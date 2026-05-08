"""
Render content/parts/**/*.json topics to navigable Markdown.

Usage:
    python content/render_markdown.py
    python content/render_markdown.py --out custom/dir

Output goes to content/output/markdown/ by default. Each topic becomes one
.md file named <NN>-<topic-id-slug>.md inside its part folder. An index.md
at the top links into every part; each part folder has its own index.md.

Inline markup understood:
    {key:X}        -> `X` (with leading "Key " for multi-char keys)
    [text](#id)    -> [text](path/to/topic.md)  -- topic-id cross-refs
    `code`, *em*, **strong**  -- pass through (markdown already supports)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from lib.videos import video_for_lesson, videos_for_topic  # noqa: E402
from lib.audience import visible as _visible  # noqa: E402

AUDIENCE = "all"

PARTS_DIR = ROOT / "parts"
EXAMPLES_DIR = ROOT / "examples"
SCREENSHOTS_DIR = ROOT / "output" / "screenshots"
DEFAULT_OUT = ROOT / "output" / "markdown"


def load_examples() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for p in EXAMPLES_DIR.glob("*.json"):
        try:
            ex = json.loads(p.read_text("utf-8"))
            if "id" in ex:
                out[ex["id"]] = ex
        except Exception:
            pass
    return out


# -------- topic loading & cross-ref index --------------------------------- #

def load_topics() -> list[dict[str, Any]]:
    topics = []
    for json_path in sorted(PARTS_DIR.glob("*/*.json")):
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"  ! JSON error in {json_path.relative_to(ROOT)}: {e}", file=sys.stderr)
            continue
        data["__src"] = json_path
        data["__part_dir"] = json_path.parent.name        # e.g. "07-operators-textobjects"
        data["__file_stem"] = json_path.stem              # e.g. "06-grammar"
        topics.append(data)
    return topics


def build_index(topics: list[dict[str, Any]]) -> dict[str, dict[str, str]]:
    """Map topic id -> {part_dir, file_stem, title}."""
    idx = {}
    for t in topics:
        tid = t.get("id")
        if not tid:
            continue
        if tid in idx:
            print(f"  ! duplicate topic id: {tid}", file=sys.stderr)
        idx[tid] = {
            "part_dir": t["__part_dir"],
            "file_stem": t["__file_stem"],
            "title": t.get("title", tid),
        }
    return idx


# -------- inline markup ---------------------------------------------------- #

_KEY_RE = re.compile(r"\{key:([^}]+)\}")
_LINK_RE = re.compile(r"\[([^\]]+)\]\(#([^)]+)\)")


def render_key(match: re.Match[str]) -> str:
    k = match.group(1)
    # Pure markdown: code-span the key. Multi-char modifiers stay together.
    return f"`{k}`"


def render_inline(text: str, *, current_part: str, index: dict[str, dict[str, str]]) -> str:
    """Convert custom inline markup. Idempotent for unknown stuff."""
    if text is None:
        return ""
    # 1. {key:X} -> `X`
    text = _KEY_RE.sub(render_key, text)

    # 2. [label](#topic.id) -> [label](relative/path.md)
    def link_sub(m: re.Match[str]) -> str:
        label, tid = m.group(1), m.group(2)
        info = index.get(tid)
        if not info:
            return f"[{label}](#{tid})"   # leave broken refs visible
        target_part = info["part_dir"]
        target_file = info["file_stem"] + ".md"
        if target_part == current_part:
            href = target_file
        else:
            href = f"../{target_part}/{target_file}"
        return f"[{label}]({href})"
    text = _LINK_RE.sub(link_sub, text)
    return text


# -------- block renderers -------------------------------------------------- #

def render_block(b: dict[str, Any], *, current_part: str, index, examples: dict[str, dict]) -> str:
    bt = b.get("type")
    inl = lambda s: render_inline(s, current_part=current_part, index=index)

    if bt == "example":
        ex_id = b.get("ref")
        ex = examples.get(ex_id) if ex_id else None
        if not ex:
            return f"<!-- example not found: {ex_id} -->"
        out: list[str] = []
        out.append("---")
        out.append(f"### Worked example — {inl(ex.get('title', ex_id))}")
        if ex.get("summary"):
            out.append(f"> {inl(ex['summary'])}")
            out.append("")
        # Path from content/output/markdown/<part>/topic.md
        # to content/output/screenshots/<id>/frame_NN.color.svg
        for i, fr in enumerate(ex.get("frames", []), start=1):
            rel = f"../../screenshots/{ex_id}/frame_{i:02d}.color.svg"
            cap = fr.get("caption", "")
            keys = fr.get("keys", "")
            heading_bits = [f"**Step {i}**"]
            if keys:
                heading_bits.append(f"keys: `{keys}`")
            if cap:
                heading_bits.append(inl(cap))
            out.append(" — ".join(heading_bits))
            out.append("")
            out.append(f"![{cap or ex_id + ' frame ' + str(i)}]({rel})")
            out.append("")
            narr = fr.get("narration", "")
            if narr:
                out.append(f"> {inl(narr)}")
                out.append("")
        out.append("---")
        return "\n".join(out)

    if bt == "heading":
        level = int(b.get("level", 2))
        return f"{'#' * level} {inl(b.get('text', ''))}"

    if bt == "prose":
        return inl(b.get("text", ""))

    if bt == "tip":
        return f"> **Tip.** {inl(b.get('text', ''))}"

    if bt == "divider":
        return "---"

    if bt == "keys":
        out = []
        label = b.get("label")
        if label:
            out.append(f"**{inl(label)}**")
            out.append("")
        out.append("| Key | Note |")
        out.append("|---|---|")
        for step in b.get("sequence", []):
            if isinstance(step, str):
                key, note = step, ""
            else:
                key = step.get("key", "")
                note = inl(step.get("note", ""))
            key_md = f"`{key}`" if key else ""
            out.append(f"| {key_md} | {note} |")
        return "\n".join(out)

    if bt == "table":
        headers = b.get("headers", [])
        rows = b.get("rows", [])
        if not headers:
            return ""
        key_cols = set(b.get("keyColumns") or
                       [i for i, h in enumerate(headers)
                        if str(h).strip().lower() in ("key", "keys")])
        out = ["| " + " | ".join(inl(h) for h in headers) + " |"]
        out.append("|" + "|".join(["---"] * len(headers)) + "|")
        for row in rows:
            cells = []
            for i, c in enumerate(row):
                s = str(c)
                if i in key_cols and s and "{key:" not in s:
                    s = "{key:" + s + "}"
                cells.append(inl(s))
            # pad short rows
            while len(cells) < len(headers):
                cells.append("")
            out.append("| " + " | ".join(cells) + " |")
        return "\n".join(out)

    if bt == "embed":
        lesson = b.get("lesson")
        cap = inl(b.get("caption", ""))
        v = video_for_lesson(lesson) if lesson is not None else None
        if v and v.get("videoId"):
            url = v["url"]
            title = v["title"]
            label = cap or title
            return f"> 📺 **[{label}]({url})** — Lesson {lesson}"
        return f"> 📺 **Lesson {lesson}** — {cap} *(not yet published)*"

    if bt == "internals":
        title = inl(b.get("title", "Under the Hood"))
        text = inl(b.get("text", ""))
        # convert internal "  • " bullets to real markdown bullets
        # paragraphs are split on blank line
        out = [f"> **🔧 Under the Hood — {title}**", ">"]
        for para in text.split("\n\n"):
            para = para.rstrip()
            if not para:
                continue
            for line in para.split("\n"):
                stripped = line.lstrip()
                if stripped.startswith("• "):
                    out.append(f"> - {stripped[2:].strip()}")
                else:
                    out.append(f"> {line}")
            out.append(">")
        # drop trailing ">"
        while out and out[-1] == ">":
            out.pop()
        return "\n".join(out)

    if bt == "qr":
        tid = b.get("topic", "")
        info = index.get(tid)
        label = info["title"] if info else tid
        return f"_📱 QR → **{label}** (web)_"

    if bt == "buy-prompt":
        return "_📖 Want the full story? Get the VimFu book._"

    # unknown -> raw json comment so we notice
    return f"<!-- unknown block type: {bt} -->"


# -------- topic renderer --------------------------------------------------- #

def render_topic(t: dict[str, Any], index, examples: dict[str, dict]) -> str:
    current_part = t["__part_dir"]
    inl = lambda s: render_inline(s, current_part=current_part, index=index)

    out: list[str] = []

    title = t.get("title", "(untitled)")
    out.append(f"# {inl(title)}")
    sub = t.get("subtitle")
    if sub:
        out.append(f"*{inl(sub)}*")
    out.append("")

    # frontmatter-ish summary line
    meta_bits = []
    if t.get("id"):
        meta_bits.append(f"`id: {t['id']}`")
    if t.get("part"):
        meta_bits.append(f"part: **{t['part']}**")
    keys = t.get("keys") or []
    if keys:
        meta_bits.append("keys: " + ", ".join(f"`{k}`" for k in keys))
    lessons = t.get("lessons") or []
    if lessons:
        meta_bits.append("lessons: " + ", ".join(str(l) for l in lessons))
    if meta_bits:
        out.append(" · ".join(meta_bits))
        out.append("")

    summary = t.get("summary")
    if summary:
        out.append(f"> {inl(summary)}")
        out.append("")

    for b in t.get("blocks", []):
        if not _visible(b, AUDIENCE):
            continue
        # Skip a leading H1 that just repeats the title.
        if (b.get("type") == "heading" and int(b.get("level", 2)) == 1
                and b.get("text", "").strip() == title.strip()):
            continue
        rendered = render_block(b, current_part=current_part, index=index, examples=examples)
        if rendered:
            out.append(rendered)
            out.append("")

    vids = videos_for_topic(t)
    embedded_lessons = {b.get("lesson") for b in (t.get("blocks") or [])
                        if b.get("type") == "embed" and b.get("lesson") is not None}
    vids = [v for v in vids if v["lesson"] not in embedded_lessons]
    if vids:
        out.append("## Watch")
        out.append("")
        for v in vids:
            if v.get("videoId"):
                out.append(f"- 📺 **[{v['title']}]({v['url']})** — Lesson {v['lesson']:04d}")
            else:
                out.append(f"- 📺 *Lesson {v['lesson']:04d} — {v['title']} (not yet published)*")
        out.append("")

    see_also = t.get("see_also") or []
    if see_also:
        out.append("---")
        out.append("**See also:** " + ", ".join(
            inl(f"[{index.get(tid, {}).get('title', tid)}](#{tid})")
            for tid in see_also
        ))
        out.append("")

    # nav back to part index
    out.append("---")
    out.append("[← back to part](index.md) · [📚 all parts](../index.md)")
    out.append("")

    return "\n".join(out)


# -------- index pages ------------------------------------------------------ #

def render_part_index(part_dir: str, topics_in_part: list[dict[str, Any]]) -> str:
    out = [f"# {part_dir.split('-', 1)[-1].replace('-', ' ').title()}", ""]
    out.append("| # | Topic | ID |")
    out.append("|---|---|---|")
    for t in topics_in_part:
        stem = t["__file_stem"]
        title = t.get("title", t.get("id", "?"))
        tid = t.get("id", "")
        nn = stem.split("-", 1)[0]
        out.append(f"| {nn} | [{title}]({stem}.md) | `{tid}` |")
    out.append("")
    out.append("[📚 all parts](../index.md)")
    out.append("")
    return "\n".join(out)


def render_root_index(parts_map: dict[str, list[dict[str, Any]]]) -> str:
    out = ["# VimFu Content — Markdown Preview", "",
           "_Auto-generated from `content/parts/**/*.json`. Don't edit by hand._", ""]
    for part_dir in sorted(parts_map.keys()):
        topics = parts_map[part_dir]
        title = part_dir.split('-', 1)[-1].replace('-', ' ').title()
        nn = part_dir.split('-', 1)[0]
        out.append(f"## Part {nn} — [{title}]({part_dir}/index.md)")
        out.append("")
        for t in topics:
            stem = t["__file_stem"]
            ttitle = t.get("title", t.get("id", "?"))
            sub = t.get("subtitle", "")
            out.append(f"- [{ttitle}]({part_dir}/{stem}.md)" + (f" — {sub}" if sub else ""))
        out.append("")
    return "\n".join(out)


# -------- main ------------------------------------------------------------- #

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()

    out_dir: Path = args.out
    out_dir.mkdir(parents=True, exist_ok=True)

    topics = load_topics()
    if not topics:
        print("No topics found.", file=sys.stderr)
        return 1
    index = build_index(topics)
    examples = load_examples()

    # group by part
    parts_map: dict[str, list[dict[str, Any]]] = {}
    for t in topics:
        parts_map.setdefault(t["__part_dir"], []).append(t)
    for k in parts_map:
        parts_map[k].sort(key=lambda x: x["__file_stem"])

    # write topic files + part indexes
    written = 0
    for part_dir, plist in parts_map.items():
        plist = [t for t in plist if _visible(t, AUDIENCE)]
        if not plist:
            continue
        pdir = out_dir / part_dir
        pdir.mkdir(parents=True, exist_ok=True)
        for t in plist:
            md = render_topic(t, index, examples)
            (pdir / f"{t['__file_stem']}.md").write_text(md, encoding="utf-8")
            written += 1
        (pdir / "index.md").write_text(render_part_index(part_dir, plist), encoding="utf-8")

    # root index
    (out_dir / "index.md").write_text(render_root_index(parts_map), encoding="utf-8")

    print(f"Wrote {written} topics across {len(parts_map)} parts → {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
