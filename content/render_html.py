"""
Render content/parts/**/*.json topics to navigable HTML.

Usage:
    python content/render_html.py
    python content/render_html.py --out custom/dir

Output goes to content/output/html/. Each topic becomes one .html file
inside its part folder. A single style.css ships alongside.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from html import escape
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from lib.videos import video_for_lesson, videos_for_topic  # noqa: E402

PARTS_DIR = ROOT / "parts"
EXAMPLES_DIR = ROOT / "examples"
SCREENSHOTS_DIR = ROOT / "output" / "screenshots"
QRCODES_DIR = ROOT / "output" / "qrcodes"
DEFAULT_OUT = ROOT / "output" / "html"


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


def load_screenshot(ex_id: str, n: int, theme: str) -> str | None:
    """Return the SVG content for a rendered frame, or None if missing."""
    p = SCREENSHOTS_DIR / ex_id / f"frame_{n:02d}.{theme}.svg"
    if p.exists():
        return p.read_text(encoding="utf-8")
    return None


# -------- topic loading --------------------------------------------------- #

def load_topics() -> list[dict[str, Any]]:
    topics = []
    for p in sorted(PARTS_DIR.glob("*/*.json")):
        try:
            t = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"  ! JSON error in {p.relative_to(ROOT)}: {e}", file=sys.stderr)
            continue
        t["__part_dir"] = p.parent.name
        t["__file_stem"] = p.stem
        topics.append(t)
    return topics


def build_index(topics):
    idx = {}
    for t in topics:
        if tid := t.get("id"):
            idx[tid] = {
                "part_dir": t["__part_dir"],
                "file_stem": t["__file_stem"],
                "title": t.get("title", tid),
            }
    return idx


# -------- inline markup --------------------------------------------------- #

# Order matters: do `code`, **strong**, *em* AFTER escape, BEFORE link/key
_KEY_RE   = re.compile(r"\{key:([^}]+)\}")
_LINK_RE  = re.compile(r"\[([^\]]+)\]\(#([^)]+)\)")
_CODE_RE  = re.compile(r"`([^`]+)`")
_STRONG_RE = re.compile(r"\*\*([^*]+)\*\*")
_EM_RE    = re.compile(r"(?<!\*)\*([^*\n]+)\*(?!\*)")


def render_inline(text: str, *, current_part: str, index) -> str:
    if text is None:
        return ""
    # We need to extract markup spans BEFORE escaping the rest. The simplest
    # robust path: tokenize against the patterns, escape the literal segments,
    # and emit pre-built HTML for the matched ones.
    tokens: list[tuple[str, str]] = []
    i = 0
    # combined pattern with named groups
    combined = re.compile(
        r"(?P<key>\{key:[^}]+\})"
        r"|(?P<link>\[[^\]]+\]\(#[^)]+\))"
        r"|(?P<code>`[^`]+`)"
        r"|(?P<strong>\*\*[^*]+\*\*)"
        r"|(?P<em>(?<!\*)\*[^*\n]+\*(?!\*))"
    )
    out_parts: list[str] = []
    pos = 0
    for m in combined.finditer(text):
        if m.start() > pos:
            out_parts.append(escape(text[pos:m.start()]))
        kind = m.lastgroup
        raw = m.group(0)
        if kind == "key":
            k = _KEY_RE.match(raw).group(1)
            out_parts.append(f'<kbd>{escape(k)}</kbd>')
        elif kind == "link":
            mm = _LINK_RE.match(raw)
            label, tid = mm.group(1), mm.group(2)
            info = index.get(tid)
            if not info:
                out_parts.append(f'<a href="#{escape(tid)}" class="broken">{escape(label)}</a>')
            else:
                target_part = info["part_dir"]
                target_file = info["file_stem"] + ".html"
                if target_part == current_part:
                    href = target_file
                else:
                    href = f"../{target_part}/{target_file}"
                out_parts.append(f'<a href="{escape(href)}">{escape(label)}</a>')
        elif kind == "code":
            inner = _CODE_RE.match(raw).group(1)
            out_parts.append(f'<code>{escape(inner)}</code>')
        elif kind == "strong":
            inner = _STRONG_RE.match(raw).group(1)
            # inner can have key/em — recurse on inner
            out_parts.append(f'<strong>{render_inline(inner, current_part=current_part, index=index)}</strong>')
        elif kind == "em":
            inner = _EM_RE.match(raw).group(1)
            out_parts.append(f'<em>{render_inline(inner, current_part=current_part, index=index)}</em>')
        pos = m.end()
    if pos < len(text):
        out_parts.append(escape(text[pos:]))
    return "".join(out_parts)


# -------- block renderers ------------------------------------------------- #

def _video_iframe(lesson, cap_html: str = "") -> str:
    """Render a single lesson as a YouTube iframe (or placeholder)."""
    v = video_for_lesson(lesson) if lesson is not None else None
    if v and v.get("videoId"):
        vid = v["videoId"]
        title = escape(v.get("title", f"Lesson {lesson}"))
        embed = (f'<iframe class="lesson-iframe" '
                 f'src="https://www.youtube.com/embed/{escape(vid)}" '
                 f'title="{title}" loading="lazy" allowfullscreen '
                 f'referrerpolicy="strict-origin-when-cross-origin"></iframe>')
        cap = cap_html or title
        return (f'<figure class="lesson-embed" data-lesson="{escape(str(lesson))}">'
                f'{embed}<figcaption>{cap}</figcaption></figure>')
    label = (v.get("title") if v else f"Lesson {lesson}") if lesson is not None else "(no lesson)"
    return (f'<figure class="lesson-embed" data-lesson="{escape(str(lesson))}">'
            f'<div class="placeholder">📺 {escape(label)} (not yet published)</div>'
            f'<figcaption>{cap_html}</figcaption></figure>')


def _videos_section(t: dict) -> str:
    """Auto-render the topic's lessons[] array as a "Watch" section.

    Lessons that already appear as explicit ``embed`` blocks in the topic
    body are skipped to avoid duplication.
    """
    embedded = {b.get("lesson") for b in (t.get("blocks") or [])
                if b.get("type") == "embed" and b.get("lesson") is not None}
    vids = [v for v in videos_for_topic(t) if v["lesson"] not in embedded]
    if not vids:
        return ""
    items = []
    for v in vids:
        if v.get("videoId"):
            iframe = (f'<iframe class="lesson-iframe" '
                      f'src="https://www.youtube.com/embed/{escape(v["videoId"])}" '
                      f'title="{escape(v["title"])}" loading="lazy" allowfullscreen '
                      f'referrerpolicy="strict-origin-when-cross-origin"></iframe>')
            link = (f'<a href="{escape(v["url"])}" target="_blank" rel="noopener">'
                    f'{escape(v["title"])}</a>')
            items.append(f'<li>{iframe}<span class="lesson-meta">'
                         f'#{v["lesson"]:04d} — {link}</span></li>')
        else:
            items.append(f'<li class="lesson-pending">'
                         f'<div class="placeholder">📺 #{v["lesson"]:04d} '
                         f'{escape(v["title"])} (not yet published)</div></li>')
    return ('<section class="watch"><h2>Watch</h2>'
            '<ul class="lesson-grid">' + "".join(items) + '</ul></section>')


_FENCE_RE = re.compile(r"```\s*\n?(.*?)\n?```", re.DOTALL)


def split_fenced(text: str):
    """Yield ('text', s) and ('code', s) tuples by splitting on ``` fences."""
    pos = 0
    for m in _FENCE_RE.finditer(text):
        if m.start() > pos:
            yield ("text", text[pos:m.start()])
        yield ("code", m.group(1))
        pos = m.end()
    if pos < len(text):
        yield ("text", text[pos:])


def render_para_with_fences(text, *, current_part, index, wrap_tag="p"):
    """Render a paragraph that may contain ```...``` blocks.

    Plain text becomes <wrap_tag>...</wrap_tag>; fences become <pre><code>...</code></pre>.
    """
    out = []
    for kind, chunk in split_fenced(text):
        if kind == "code":
            out.append(f"<pre><code>{escape(chunk)}</code></pre>")
        else:
            chunk = chunk.strip()
            if chunk:
                inner = render_inline(chunk, current_part=current_part, index=index)
                out.append(f"<{wrap_tag}>{inner}</{wrap_tag}>")
    return "\n".join(out)


def render_block(b, *, current_part, index, examples) -> str:
    bt = b.get("type")
    inl = lambda s: render_inline(s, current_part=current_part, index=index)

    if bt == "example":
        ex_id = b.get("ref")
        ex = examples.get(ex_id) if ex_id else None
        if not ex:
            return f"<!-- example not found: {ex_id} -->"
        out = ['<section class="example">']
        out.append(f'<h3 class="example-title">Worked example — {inl(ex.get("title", ex_id))}</h3>')
        if ex.get("summary"):
            out.append(f'<p class="example-summary">{inl(ex["summary"])}</p>')
        for i, fr in enumerate(ex.get("frames", []), start=1):
            cap = fr.get("caption", "")
            keys = fr.get("keys", "")
            narr = fr.get("narration", "")
            rel = f"../../screenshots/{ex_id}/frame_{i:02d}.color.svg"
            exists = (SCREENSHOTS_DIR / ex_id / f"frame_{i:02d}.color.svg").exists()
            out.append('<figure class="example-step">')
            head = [f'<span class="step-n">Step {i}</span>']
            if keys:
                head.append(f'<kbd>{escape(keys)}</kbd>')
            head.append(f'<span class="step-cap">{inl(cap)}</span>')
            out.append(f'<figcaption>{" · ".join(head)}</figcaption>')
            if exists:
                out.append(f'<div class="screenshot"><img src="{escape(rel)}" alt="{escape(cap or ex_id)}"></div>')
            else:
                out.append(f'<div class="screenshot missing">[missing screenshot {ex_id}/frame_{i:02d}.color.svg — run python content/render_screenshots.py]</div>')
            if narr:
                out.append(f'<p class="narration">{inl(narr)}</p>')
            out.append('</figure>')
        out.append('</section>')
        return "\n".join(out)

    if bt == "heading":
        level = max(2, min(6, int(b.get("level", 2)) + 1))  # title is h1, demote
        return f"<h{level}>{inl(b.get('text',''))}</h{level}>"

    if bt == "prose":
        return render_para_with_fences(b.get("text", ""),
                                       current_part=current_part, index=index)

    if bt == "tip":
        return f'<aside class="tip"><strong>Tip.</strong> {inl(b.get("text",""))}</aside>'

    if bt == "divider":
        return "<hr>"

    if bt == "keys":
        out = ['<figure class="keys">']
        if label := b.get("label"):
            out.append(f"<figcaption>{inl(label)}</figcaption>")
        out.append('<table><thead><tr><th>Key</th><th>Note</th></tr></thead><tbody>')
        for step in b.get("sequence", []):
            if isinstance(step, str):
                key, note = step, ""
            else:
                key = step.get("key", "")
                note = inl(step.get("note", ""))
            key_html = f"<kbd>{escape(key)}</kbd>" if key else ""
            out.append(f"<tr><td>{key_html}</td><td>{note}</td></tr>")
        out.append("</tbody></table></figure>")
        return "\n".join(out)

    if bt == "table":
        headers = b.get("headers", [])
        rows = b.get("rows", [])
        if not headers:
            return ""
        out = ['<table>', '<thead><tr>']
        for h in headers:
            out.append(f"<th>{inl(h)}</th>")
        out.append("</tr></thead><tbody>")
        for row in rows:
            cells = list(row) + [""] * (len(headers) - len(row))
            out.append("<tr>")
            for c in cells:
                out.append(f"<td>{inl(str(c))}</td>")
            out.append("</tr>")
        out.append("</tbody></table>")
        return "\n".join(out)

    if bt == "embed":
        lesson = b.get("lesson")
        cap = inl(b.get("caption", ""))
        return _video_iframe(lesson, cap)

    if bt == "internals":
        title = inl(b.get("title", "Under the Hood"))
        text = b.get("text", "") or ""
        out = ['<aside class="internals">',
               f'<header>🔧 Under the Hood — {title}</header>']
        for para in text.split("\n\n"):
            para = para.rstrip()
            if not para:
                continue
            lines = para.split("\n")
            # Detect bullet block (every line starts with "  • " or "• ")
            stripped = [ln.lstrip() for ln in lines]
            if all(s.startswith("• ") for s in stripped if s):
                out.append("<ul>")
                for s in stripped:
                    if s:
                        out.append(f"<li>{inl(s[2:].strip())}</li>")
                out.append("</ul>")
            else:
                out.append(render_para_with_fences(para, current_part=current_part, index=index))
        out.append("</aside>")
        return "\n".join(out)

    if bt == "qr":
        tid = b.get("topic", "")
        info = index.get(tid)
        label = info["title"] if info else tid
        href = ""
        qr_src = ""
        if info:
            href = (f"../{info['part_dir']}/{info['file_stem']}.html"
                    if info["part_dir"] != current_part else f"{info['file_stem']}.html")
            # Reference the precomputed QR SVG (output/qrcodes/<part>/<stem>.svg).
            qr_src = (f"../qrcodes/{info['part_dir']}/{info['file_stem']}.svg")
        link = f'<a href="{escape(href)}">{escape(label)}</a>' if href else escape(label)
        img = (f'<img class="qr-img" src="{escape(qr_src)}" alt="QR code for {escape(label)}" '
               f'width="96" height="96">' if qr_src else "")
        return (f'<aside class="qr">{img}'
                f'<span>📱 Scan or visit {link}</span></aside>')

    if bt == "buy-prompt":
        return '<aside class="buy-prompt">📖 Want the full story? <a href="#">Get the VimFu book.</a></aside>'

    return f"<!-- unknown block type: {escape(str(bt))} -->"


# -------- topic page ------------------------------------------------------ #

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title} — VimFu</title>
<link rel="stylesheet" href="{css}">
</head>
<body>
<nav class="topnav">
  <a href="{root_index}">📚 All Parts</a>
  &middot; <a href="index.html">← {part_label}</a>
</nav>
<article>
{body}
</article>
<nav class="bottomnav">
  <a href="index.html">← back to part</a>
  &middot; <a href="{root_index}">📚 all parts</a>
</nav>
</body>
</html>
"""


def render_topic_page(t, index, examples) -> str:
    current_part = t["__part_dir"]
    inl = lambda s: render_inline(s, current_part=current_part, index=index)

    title = t.get("title", "(untitled)")
    sub = t.get("subtitle", "")

    body: list[str] = [f"<h1>{inl(title)}</h1>"]
    if sub:
        body.append(f'<p class="subtitle">{inl(sub)}</p>')

    meta = []
    if tid := t.get("id"):
        meta.append(f'<code>id: {escape(tid)}</code>')
    if part := t.get("part"):
        meta.append(f'part: <strong>{escape(part)}</strong>')
    if keys := t.get("keys"):
        meta.append("keys: " + ", ".join(f"<kbd>{escape(k)}</kbd>" for k in keys))
    if lessons := t.get("lessons"):
        meta.append("lessons: " + ", ".join(escape(str(l)) for l in lessons))
    if meta:
        body.append('<p class="meta">' + " &middot; ".join(meta) + "</p>")

    if summary := t.get("summary"):
        body.append(f'<blockquote class="summary">{inl(summary)}</blockquote>')

    for b in t.get("blocks", []):
        if (b.get("type") == "heading" and int(b.get("level", 2)) == 1
                and b.get("text", "").strip() == title.strip()):
            continue
        body.append(render_block(b, current_part=current_part, index=index, examples=examples))

    if videos_html := _videos_section(t):
        body.append(videos_html)

    if see_also := t.get("see_also"):
        links = []
        for ref_id in see_also:
            info = index.get(ref_id)
            if info:
                href = (f"{info['file_stem']}.html"
                        if info["part_dir"] == current_part
                        else f"../{info['part_dir']}/{info['file_stem']}.html")
                links.append(f'<a href="{escape(href)}">{escape(info["title"])}</a>')
            else:
                links.append(f'<span class="broken">{escape(ref_id)}</span>')
        body.append('<p class="see-also"><strong>See also:</strong> ' + ", ".join(links) + "</p>")

    part_label = current_part.split("-", 1)[-1].replace("-", " ").title()
    return PAGE.format(
        title=escape(title),
        css="../style.css",
        root_index="../index.html",
        part_label=escape(part_label),
        body="\n".join(body),
    )


# -------- index pages ----------------------------------------------------- #

PART_INDEX = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>{label} — VimFu</title>
<link rel="stylesheet" href="../style.css">
</head><body>
<nav class="topnav"><a href="../index.html">📚 All Parts</a></nav>
<article>
<h1>{label}</h1>
<ol class="topic-list">
{items}
</ol>
</article>
</body></html>
"""


def render_part_index(part_dir, topics_in_part) -> str:
    items = []
    for t in topics_in_part:
        stem = t["__file_stem"]
        title = t.get("title", t.get("id", "?"))
        sub = t.get("subtitle", "")
        items.append(
            f'<li><a href="{stem}.html">{escape(title)}</a>'
            + (f" — <span class='sub'>{escape(sub)}</span>" if sub else "")
            + "</li>"
        )
    label = part_dir.split("-", 1)[-1].replace("-", " ").title()
    return PART_INDEX.format(label=escape(label), items="\n".join(items))


ROOT_INDEX = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>VimFu Content</title>
<link rel="stylesheet" href="style.css">
</head><body>
<article>
<h1>VimFu Content</h1>
<p class="meta">Auto-generated from <code>content/parts/**/*.json</code>.</p>
{sections}
</article>
</body></html>
"""


def render_root_index(parts_map) -> str:
    sections = []
    for part_dir in sorted(parts_map.keys()):
        topics = parts_map[part_dir]
        label = part_dir.split("-", 1)[-1].replace("-", " ").title()
        nn = part_dir.split("-", 1)[0]
        sections.append(f'<h2>Part {escape(nn)} — <a href="{part_dir}/index.html">{escape(label)}</a></h2>')
        sections.append("<ul>")
        for t in topics:
            stem = t["__file_stem"]
            ttl = t.get("title", t.get("id", "?"))
            sub = t.get("subtitle", "")
            sections.append(
                f'<li><a href="{part_dir}/{stem}.html">{escape(ttl)}</a>'
                + (f" — <span class='sub'>{escape(sub)}</span>" if sub else "")
                + "</li>"
            )
        sections.append("</ul>")
    return ROOT_INDEX.format(sections="\n".join(sections))


# -------- stylesheet ------------------------------------------------------ #

STYLE_CSS = """:root {
  --fg: #1a1a1a;
  --muted: #555;
  --bg: #fafafa;
  --accent: #0a6;
  --code-bg: #f0f0f0;
  --kbd-bg: #fff;
  --kbd-border: #999;
  --panel: #f6f6f0;
  --tip: #fff8d0;
  --internals: #eef2f8;
  --qr: #f0f6f0;
}
* { box-sizing: border-box; }
body {
  font: 16px/1.55 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  color: var(--fg); background: var(--bg);
  margin: 0; padding: 0;
}
article {
  max-width: 760px; margin: 0 auto; padding: 2rem 1.25rem;
}
nav.topnav, nav.bottomnav {
  max-width: 760px; margin: 0 auto; padding: 0.75rem 1.25rem;
  font-size: 0.9rem; color: var(--muted);
}
nav a { color: var(--accent); text-decoration: none; }
nav a:hover { text-decoration: underline; }

h1 { font-size: 2rem; margin: 0.4rem 0 0.2rem; }
h2 { font-size: 1.4rem; margin: 1.8rem 0 0.6rem; border-bottom: 1px solid #ddd; padding-bottom: 0.3rem; }
h3 { font-size: 1.15rem; margin: 1.4rem 0 0.4rem; }
p.subtitle { color: var(--muted); font-size: 1.1rem; margin-top: 0; font-style: italic; }
p.meta { color: var(--muted); font-size: 0.85rem; }

a { color: var(--accent); }
a.broken, span.broken { color: #a33; text-decoration: line-through dotted; }

code {
  background: var(--code-bg); padding: 1px 5px; border-radius: 3px;
  font: 0.9em ui-monospace, "Fira Code", Consolas, monospace;
}
pre {
  background: var(--code-bg); padding: 0.7rem 0.9rem; border-radius: 5px;
  overflow-x: auto; margin: 0.8rem 0;
  border-left: 3px solid var(--border);
}
pre code { background: transparent; padding: 0; font-size: 0.9rem; }
kbd {
  background: var(--kbd-bg); border: 1px solid var(--kbd-border);
  border-bottom-width: 2px; border-radius: 4px;
  padding: 0 5px; font: 0.85em ui-monospace, Consolas, monospace;
  white-space: nowrap;
}

blockquote.summary {
  border-left: 3px solid var(--accent); margin: 1rem 0;
  padding: 0.6rem 1rem; background: #f0fff8; color: #064;
  font-size: 1.05rem;
}

table {
  border-collapse: collapse; width: 100%; margin: 1rem 0;
  font-size: 0.95rem;
}
th, td { border: 1px solid #ddd; padding: 0.4rem 0.6rem; text-align: left; vertical-align: top; }
thead th { background: #efefef; }

figure.keys, figure.lesson-embed { margin: 1rem 0; }
figure.keys figcaption, figure.lesson-embed figcaption {
  font-style: italic; color: var(--muted); font-size: 0.9rem; margin-bottom: 0.4rem;
}
figure.lesson-embed iframe.lesson-iframe {
  width: 100%; aspect-ratio: 9/16; max-width: 360px; border: 0; border-radius: 6px;
  background: #000; display: block;
}
figure.lesson-embed .placeholder {
  background: #222; color: #fff; padding: 2rem; text-align: center;
  border-radius: 6px; font-size: 1.1rem;
}

aside.tip {
  background: var(--tip); border-left: 4px solid #cc0;
  padding: 0.7rem 1rem; margin: 1rem 0; border-radius: 4px;
}
aside.internals {
  background: var(--internals); border-left: 4px solid #69b;
  padding: 0.7rem 1rem; margin: 1.2rem 0; border-radius: 4px;
}
aside.internals header {
  font-weight: 600; margin-bottom: 0.4rem; color: #246;
}
aside.internals p { margin: 0.5rem 0; }
aside.internals ul { margin: 0.5rem 0; padding-left: 1.4rem; }
aside.qr {
  background: var(--qr); padding: 0.4rem 0.8rem; margin: 1rem 0;
  border-radius: 4px; font-size: 0.9rem; color: #064;
  display: flex; align-items: center; gap: 0.8rem;
}
aside.qr img.qr-img { background: #fff; padding: 4px; border-radius: 4px; }
section.watch { margin: 2rem 0; padding-top: 1rem; border-top: 1px solid #ddd; }
section.watch h2 { margin-top: 0; }
ul.lesson-grid {
  list-style: none; padding: 0; display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 1.2rem;
}
ul.lesson-grid li { display: flex; flex-direction: column; gap: 0.4rem; }
ul.lesson-grid iframe.lesson-iframe {
  width: 100%; aspect-ratio: 9/16; border: 0; border-radius: 6px;
  background: #000; display: block;
}
ul.lesson-grid .lesson-meta { font-size: 0.85rem; color: var(--muted); }
ul.lesson-grid .lesson-pending .placeholder {
  background: #f3f3f3; color: var(--muted); padding: 1.5rem 1rem;
  text-align: center; border-radius: 6px; aspect-ratio: 9/16;
  display: flex; align-items: center; justify-content: center;
}
aside.buy-prompt {
  background: #fff0e0; border: 1px dashed #c80;
  padding: 0.6rem 1rem; margin: 1.5rem 0; border-radius: 4px;
  text-align: center; font-style: italic;
}

section.example {
  margin: 1.6rem 0; padding: 1rem 1.2rem;
  background: #f5f9ff; border: 1px solid #cdd9ee; border-radius: 6px;
}
section.example h3.example-title {
  margin: 0 0 0.4rem; font-size: 1.05rem; color: #234;
  text-transform: uppercase; letter-spacing: 0.04em;
}
section.example p.example-summary {
  margin: 0 0 1rem; color: #456; font-style: italic;
}
figure.example-step {
  margin: 0.8rem 0; padding: 0.6rem; background: #fff;
  border-radius: 4px; border: 1px solid #dde6f2;
}
figure.example-step figcaption {
  font-size: 0.95rem; color: #234; margin-bottom: 0.5rem;
}
figure.example-step .step-n {
  display: inline-block; font-weight: 600; color: var(--accent);
  margin-right: 0.5rem;
}
figure.example-step .step-cap { color: #345; }
figure.example-step .screenshot {
  background: #000; border-radius: 4px; padding: 4px;
  display: flex; justify-content: center;
}
figure.example-step .screenshot img {
  width: 100%; max-width: 640px; height: auto; display: block;
}
figure.example-step .screenshot.missing {
  background: #fee; color: #900; padding: 1rem; text-align: center;
  font-family: monospace; font-size: 0.9rem;
}
figure.example-step p.narration {
  margin: 0.6rem 0 0; color: #345; font-size: 0.95rem;
}

p.see-also {
  margin-top: 2rem; padding-top: 0.8rem; border-top: 1px solid #ddd;
  font-size: 0.95rem;
}
ol.topic-list { padding-left: 1.5rem; }
ol.topic-list li { margin: 0.4rem 0; }
.sub { color: var(--muted); }
"""


# -------- main ------------------------------------------------------------ #

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    out_dir: Path = args.out
    out_dir.mkdir(parents=True, exist_ok=True)

    topics = load_topics()
    if not topics:
        print("No topics found.", file=sys.stderr); return 1
    index = build_index(topics)
    examples = load_examples()

    parts_map: dict[str, list] = {}
    for t in topics:
        parts_map.setdefault(t["__part_dir"], []).append(t)
    for k in parts_map:
        parts_map[k].sort(key=lambda x: x["__file_stem"])

    written = 0
    for part_dir, plist in parts_map.items():
        pdir = out_dir / part_dir
        pdir.mkdir(parents=True, exist_ok=True)
        for t in plist:
            (pdir / f"{t['__file_stem']}.html").write_text(
                render_topic_page(t, index, examples), encoding="utf-8")
            written += 1
        (pdir / "index.html").write_text(
            render_part_index(part_dir, plist), encoding="utf-8")

    (out_dir / "index.html").write_text(render_root_index(parts_map), encoding="utf-8")
    (out_dir / "style.css").write_text(STYLE_CSS, encoding="utf-8")

    print(f"Wrote {written} topic pages across {len(parts_map)} parts → {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
