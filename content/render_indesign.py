"""
Render content/parts/**/*.json topics to Adobe InDesign Tagged Text (.txt).

Usage:
    python content/render_indesign.py
    python content/render_indesign.py --out custom/dir

Tagged Text is the format InDesign's "Place" command imports as a fully
styled story — perfect for threaded text frames. Each output file begins
with a <ASCII-WIN>...<DefineParaStyle>...<DefineCharStyle> header that
the designer can map to real paragraph/character styles in their template
(File → Place → check "Show Import Options"; Tagged Text Import → use
"Resolve Style Conflicts → Use Publication Definition" so styles in the
.indd template win over the ones declared here).

Per-topic files land in <part>/<NN>-<slug>.txt. A "_full.txt" per part and
a top-level "_book.txt" concatenate everything for one-shot Place-into-
threaded-frames flow.

Image / video placeholders are emitted as paragraphs styled
"InlineGraphicPlaceholder" — replace each with an anchored object in
InDesign (Find/Change → GREP for the placeholder text).

Reference: https://www.adobe.com/content/dam/acom/en/devnet/indesign/sdk/cs6/scripting/InDesign_TaggedText.pdf
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
from lib.parts import part_label as _part_label  # noqa: E402

AUDIENCE = "book"

ROOT = Path(__file__).resolve().parent
PARTS_DIR = ROOT / "parts"
EXAMPLES_DIR = ROOT / "examples"
SCREENSHOTS_DIR = ROOT / "output" / "screenshots"
DEFAULT_OUT = ROOT / "output" / "indesign"


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


# -------- topic loading --------------------------------------------------- #

def load_topics():
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
    return {
        t["id"]: {"title": t.get("title", t["id"]),
                  "part_dir": t["__part_dir"],
                  "file_stem": t["__file_stem"]}
        for t in topics if t.get("id")
    }


# -------- tagged-text encoding -------------------------------------------- #

# Tagged Text uses < and > as delimiters; literal < and > in body text must be
# escaped as <0x003C> and <0x003E>. Backslash also needs escaping. We don't use
# Unicode-encoded text mode, so non-ASCII chars come through via <0xNNNN>.

def tt_escape(s: str) -> str:
    if s is None:
        return ""
    out = []
    for ch in s:
        cp = ord(ch)
        if ch == "<":
            out.append("<0x003C>")
        elif ch == ">":
            out.append("<0x003E>")
        elif ch == "\\":
            out.append("<0x005C>")
        elif cp < 0x20 and ch not in "\t":
            # strip other control chars
            continue
        elif cp <= 0x7E:
            out.append(ch)
        else:
            out.append(f"<0x{cp:04X}>")
    return "".join(out)


# Inline markup tokens
_KEY_RE   = re.compile(r"\{key:([^}]+|\})\}")
_LINK_RE  = re.compile(r"\[([^\]]+)\]\(#([^)]+)\)")
_CODE_RE  = re.compile(r"`([^`]+)`")
_STRONG_RE = re.compile(r"\*\*([^*]+)\*\*")
_EM_RE    = re.compile(r"(?<!\*)\*([^*\n]+)\*(?!\*)")

_combined = re.compile(
    r"(?P<key>\{key:(?:[^}]+|\})\})"
    r"|(?P<link>\[[^\]]+\]\(#[^)]+\))"
    r"|(?P<code>`[^`]+`)"
    r"|(?P<strong>\*\*[^*]+\*\*)"
    r"|(?P<em>(?<!\*)\*[^*\n]+\*(?!\*))"
)


def render_inline(text: str, *, index) -> str:
    """Convert inline markup into Tagged-Text character-style runs."""
    if text is None:
        return ""
    out: list[str] = []
    pos = 0
    for m in _combined.finditer(text):
        if m.start() > pos:
            out.append(tt_escape(text[pos:m.start()]))
        kind = m.lastgroup
        raw = m.group(0)
        if kind == "key":
            k = _KEY_RE.match(raw).group(1)
            out.append(f"<CharStyle:Key>{tt_escape(k)}<CharStyle:>")
        elif kind == "link":
            mm = _LINK_RE.match(raw)
            label, tid = mm.group(1), mm.group(2)
            target = index.get(tid, {}).get("title", tid)
            # Tagged Text has no real cross-doc hyperlinks; emit visible label
            # styled "Link" with a footnote-like ref the designer can wire up.
            out.append(f"<CharStyle:Link>{tt_escape(label)}<CharStyle:>")
            out.append(f"<CharStyle:LinkRef> [→ {tt_escape(target)}]<CharStyle:>")
        elif kind == "code":
            inner = _CODE_RE.match(raw).group(1)
            out.append(f"<CharStyle:Code>{tt_escape(inner)}<CharStyle:>")
        elif kind == "strong":
            inner = _STRONG_RE.match(raw).group(1)
            out.append(f"<CharStyle:Strong>{render_inline(inner, index=index)}<CharStyle:>")
        elif kind == "em":
            inner = _EM_RE.match(raw).group(1)
            out.append(f"<CharStyle:Em>{render_inline(inner, index=index)}<CharStyle:>")
        pos = m.end()
    if pos < len(text):
        out.append(tt_escape(text[pos:]))
    return "".join(out)


def para(style: str, body: str) -> str:
    return f"<ParaStyle:{style}>{body}\r"


# -------- block renderers ------------------------------------------------- #

_FENCE_RE = re.compile(r"```\s*\n?(.*?)\n?```", re.DOTALL)


def split_fenced(text: str):
    pos = 0
    for m in _FENCE_RE.finditer(text):
        if m.start() > pos:
            yield ("text", text[pos:m.start()])
        yield ("code", m.group(1))
        pos = m.end()
    if pos < len(text):
        yield ("text", text[pos:])


def emit_paragraphs(text, *, index, body_style):
    """Emit one or more <ParaStyle:...> paragraphs from text that may
    contain ```...``` fenced code blocks. Code blocks become CodeBlock
    paragraphs; other content becomes body_style paragraphs.
    """
    out = []
    for kind, chunk in split_fenced(text):
        if kind == "code":
            for line in chunk.split("\n"):
                out.append(para("CodeBlock", tt_escape(line)))
        else:
            chunk = chunk.strip()
            if chunk:
                out.append(para(body_style, render_inline(chunk, index=index)))
    return out


def render_block(b, *, index, examples) -> list[str]:
    bt = b.get("type")
    inl = lambda s: render_inline(s, index=index)
    out: list[str] = []

    if bt == "example":
        ex_id = b.get("ref")
        ex = examples.get(ex_id) if ex_id else None
        if not ex:
            out.append(para("Body", f"[example not found: {tt_escape(str(ex_id))}]"))
            return out
        out.append(para("ExampleTitle",
                        f"Worked Example: {tt_escape(ex.get('title', ex_id))}"))
        if ex.get("summary"):
            out.append(para("ExampleSummary", inl(ex["summary"])))
        for i, fr in enumerate(ex.get("frames", []), start=1):
            cap = fr.get("caption", "")
            keys = fr.get("keys", "")
            narr = fr.get("narration", "")
            # Step header: bold "Step N" + optional keys
            head_bits = [f"Step {i}"]
            if keys:
                head_bits.append(f"<CharStyle:Key>{tt_escape(keys)}<CharStyle:>")
            if cap:
                head_bits.append(inl(cap))
            out.append(para("ExampleStep", "  —  ".join(head_bits)))
            # Image placeholder pointing at the BW SVG (book = grayscale)
            svg_rel = f"../screenshots/{ex_id}/frame_{i:02d}.bw.svg"
            out.append(para("InlineGraphicPlaceholder",
                            f"[SCREENSHOT: {tt_escape(svg_rel)}]"))
            if narr:
                out.append(para("ExampleNarration", inl(narr)))
        out.append(para("Divider", "* * *"))
        return out

    if bt == "heading":
        level = int(b.get("level", 2))
        style = "Heading1" if level <= 1 else "Heading2" if level == 2 else "Heading3"
        out.append(para(style, inl(b.get("text", ""))))

    elif bt == "prose":
        out.extend(emit_paragraphs(b.get("text", ""), index=index, body_style="Body"))

    elif bt == "tip":
        out.append(para("Tip", inl(b.get("text", ""))))

    elif bt == "divider":
        out.append(para("Divider", "* * *"))

    elif bt == "keys":
        if label := b.get("label"):
            out.append(para("KeysCaption", inl(label)))
        for step in b.get("sequence", []):
            if isinstance(step, str):
                key, note = step, ""
            else:
                key = step.get("key", "")
                note = inl(step.get("note", ""))
            key_run = f"<CharStyle:Key>{tt_escape(key)}<CharStyle:>" if key else ""
            sep = "<0x0009>" if note else ""  # tab between key and note
            out.append(para("KeyRow", f"{key_run}{sep}{note}"))

    elif bt == "table":
        headers = b.get("headers", [])
        rows = b.get("rows", [])
        if headers:
            key_cols = set(b.get("keyColumns") or
                           [i for i, h in enumerate(headers)
                            if str(h).strip().lower() in ("key", "keys")])
            out.append(para("TableHeader", "<0x0009>".join(inl(h) for h in headers)))
            for row in rows:
                cells = list(row) + [""] * (len(headers) - len(row))
                rendered = []
                for i, c in enumerate(cells):
                    s = str(c)
                    if i in key_cols and s and "{key:" not in s:
                        s = "{key:" + s + "}"
                    rendered.append(inl(s))
                out.append(para("TableRow", "<0x0009>".join(rendered)))

    elif bt == "embed":
        # The book has no videos; we point readers at the QR section instead.
        # If the designer wants a "Watch online" callout, the lesson title is
        # rendered as a caption beside the placeholder.
        lesson = b.get("lesson", "")
        cap = inl(b.get("caption", ""))
        v = video_for_lesson(lesson) if lesson != "" else None
        title = (v["title"] if v else f"Lesson {lesson}")
        url = (v["url"] if v else "")
        out.append(para("InlineGraphicPlaceholder",
                        f"[VIDEO — {tt_escape(title)} — {tt_escape(url)}]"))
        if cap:
            out.append(para("Caption", cap))

    elif bt == "internals":
        title = inl(b.get("title", "Under the Hood"))
        text = b.get("text", "") or ""
        out.append(para("InternalsTitle", f"Under the Hood — {title}"))
        for chunk in text.split("\n\n"):
            chunk = chunk.rstrip()
            if not chunk:
                continue
            lines = chunk.split("\n")
            stripped = [ln.lstrip() for ln in lines]
            if all(s.startswith("• ") for s in stripped if s):
                for s in stripped:
                    if s:
                        out.append(para("InternalsBullet", inl(s[2:].strip())))
            else:
                out.extend(emit_paragraphs(chunk, index=index, body_style="InternalsBody"))

    elif bt == "anecdote":
        title = inl(b.get("title", "")) or "A Story"
        text = b.get("text", "") or ""
        out.append(para("AnecdoteTitle", title))
        for chunk in text.split("\n\n"):
            chunk = chunk.rstrip()
            if not chunk:
                continue
            out.extend(emit_paragraphs(chunk, index=index, body_style="AnecdoteBody"))

    elif bt == "qr":
        tid = b.get("topic", "")
        info = index.get(tid, {})
        label = info.get("title", tid)
        site_url = ""
        svg_hint = ""
        if info:
            part_dir = info.get("part_dir", "")
            stem = info.get("file_stem", "")
            site_url = f"https://vimfubook.com/{part_dir}/{stem}"
            svg_hint = f"output/qrcodes/{part_dir}/{stem}.svg"
        out.append(para("QRCallout",
                        f"[QR — place: {tt_escape(svg_hint)} — links to: "
                        f"{tt_escape(label)} — {tt_escape(site_url)}]"))

    elif bt == "buy-prompt":
        out.append(para("BuyPrompt", "Want the full story? Get the VimFu book."))

    else:
        out.append(para("Body", f"[unknown block: {tt_escape(str(bt))}]"))

    return out


# -------- topic body ------------------------------------------------------ #

def render_topic_body(t, index, examples) -> str:
    inl = lambda s: render_inline(s, index=index)

    out: list[str] = []
    title = t.get("title", "(untitled)")
    out.append(para("Title", inl(title)))
    if sub := t.get("subtitle"):
        out.append(para("Subtitle", inl(sub)))

    # meta line — a small designer-friendly footer-style intro
    bits = []
    if tid := t.get("id"):
        bits.append(f"<CharStyle:Code>{tt_escape(tid)}<CharStyle:>")
    if part := t.get("part"):
        bits.append(f"part: <CharStyle:Strong>{tt_escape(part)}<CharStyle:>")
    if t.get("keys"):
        bits.append("keys: " + ", ".join(
            f"<CharStyle:Key>{tt_escape(k)}<CharStyle:>" for k in t["keys"]))
    if t.get("lessons"):
        bits.append("lessons: " + ", ".join(tt_escape(str(l)) for l in t["lessons"]))
    if bits:
        out.append(para("Meta", " · ".join(bits)))

    if summary := t.get("summary"):
        out.append(para("Summary", inl(summary)))

    for b in t.get("blocks", []):
        if not _visible(b, AUDIENCE):
            continue
        if (b.get("type") == "heading" and int(b.get("level", 2)) == 1
                and b.get("text", "").strip() == title.strip()):
            continue
        out.extend(render_block(b, index=index, examples=examples))

    vids = videos_for_topic(t)
    embedded_lessons = {b.get("lesson") for b in (t.get("blocks") or [])
                        if b.get("type") == "embed" and b.get("lesson") is not None}
    vids = [v for v in vids if v["lesson"] not in embedded_lessons]
    if vids:
        out.append(para("Heading2", "Watch Online"))
        for v in vids:
            line = (f"#{v['lesson']:04d} — {v['title']}"
                    + (f" — {v['url']}" if v.get("url") else " (not yet published)"))
            out.append(para("Body", tt_escape(line)))

    if see_also := t.get("see_also"):
        labels = [index.get(tid, {}).get("title", tid) for tid in see_also]
        out.append(para("SeeAlso", "See also: " + tt_escape(", ".join(labels))))

    out.append(para("TopicBreak", ""))   # frame-break hint for designer
    return "".join(out)


# -------- header (style declarations) ------------------------------------- #

# Minimal but complete style header. Designers can override any of these in
# their .indd document — these are just defaults so the unstyled file imports
# cleanly. Font metrics intentionally bare; designer's master template wins
# when "Resolve Style Conflicts → Use Publication Definition" is selected.

PARAGRAPH_STYLES = [
    "Title", "Subtitle", "Meta", "Summary",
    "Heading1", "Heading2", "Heading3",
    "Body", "KeysCaption", "KeyRow",
    "TableHeader", "TableRow",
    "Tip", "Divider",
    "InternalsTitle", "InternalsBody", "InternalsBullet",
    "CodeBlock",
    "ExampleTitle", "ExampleSummary", "ExampleStep", "ExampleNarration",
    "InlineGraphicPlaceholder", "Caption",
    "QRCallout", "BuyPrompt",
    "SeeAlso", "TopicBreak",
]
CHARACTER_STYLES = ["Key", "Code", "Em", "Strong", "Link", "LinkRef"]


def header() -> str:
    out = ["<ASCII-WIN>", "<Version:6><FeatureSet:InDesign-Roman>"]
    for s in PARAGRAPH_STYLES:
        out.append(f"<DefineParaStyle:{s}=<Nextstyle:Body>>")
    for s in CHARACTER_STYLES:
        out.append(f"<DefineCharStyle:{s}=>")
    out.append("")  # blank to end header
    return "\r\n".join(out) + "\r\n"


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

    hdr = header()
    written = 0
    book_chunks = [hdr]

    for part_dir in sorted(parts_map.keys()):
        plist = [t for t in parts_map[part_dir] if _visible(t, AUDIENCE)]
        if not plist:
            continue
        pdir = out_dir / part_dir
        pdir.mkdir(parents=True, exist_ok=True)

        # Per-part full file
        part_label = _part_label(part_dir)
        part_chunks = [hdr, para("Heading1", tt_escape(part_label))]

        for t in plist:
            body = render_topic_body(t, index, examples)
            (pdir / f"{t['__file_stem']}.txt").write_text(
                hdr + body, encoding="utf-8")
            part_chunks.append(body)
            book_chunks.append(body)
            written += 1

        (pdir / "_full.txt").write_text("".join(part_chunks), encoding="utf-8")

    (out_dir / "_book.txt").write_text("".join(book_chunks), encoding="utf-8")

    # README for the designer
    (out_dir / "README.txt").write_text(DESIGNER_NOTES, encoding="utf-8")

    print(f"Wrote {written} topic .txt files across {len(parts_map)} parts → {out_dir}")
    print(f"  Per-part full files: <part>/_full.txt")
    print(f"  Single-story book:   _book.txt")
    return 0


DESIGNER_NOTES = """\
VimFu — InDesign Tagged Text export
====================================

These are Adobe InDesign Tagged Text (.txt) files. They are structured rich
text that imports directly into a threaded text frame.

How to import:
    1. In InDesign, draw your master text frame (or thread several frames).
    2. With the cursor in the frame: File -> Place...
    3. Select _book.txt (or a per-part _full.txt, or a single topic .txt).
    4. Check "Show Import Options".
    5. In the Tagged Text Import Options dialog:
        - Use Typographer's Quotes: ON
        - Resolve Text Style Conflicts: USE PUBLICATION DEFINITION
          (so the styles in your .indd template win over the bare defaults
           declared in the file's header).
    6. Click OK; the styled text flows into your threaded frames.

Paragraph styles you should define in the template:
    Title          - chapter / topic title
    Subtitle       - tagline under the title
    Meta           - small id/keys/lessons line
    Summary        - the lead paragraph (set apart visually)
    Heading1/2/3   - in-topic section headings
    Body           - body paragraph default
    Tip            - call-out for short tips
    KeysCaption    - label above a keys table
    KeyRow         - one row of a keys walkthrough (key + note)
    TableHeader    - header row of a key-reference table
    TableRow       - data row (tabs separate cells)
    InternalsTitle - "Under the Hood" headline
    InternalsBody  - body inside Under the Hood
    InternalsBullet- bullet inside Under the Hood
    InlineGraphicPlaceholder - paragraph holding a [VIDEO PLACEHOLDER...]
                               token; replace with an anchored picture frame
    Caption        - caption under an image / video frame
    QRCallout      - the [QR PLACEHOLDER] line; replace with anchored QR PNG
    BuyPrompt      - the soft "buy the book" line at end of every topic
    SeeAlso        - cross-reference list at end of topic
    TopicBreak     - empty paragraph; useful for "Start in Next Frame"
                     break setting between topics
    Divider        - "* * *" separator

Character styles:
    Key            - inline key cap (kbd-style)
    Code           - inline monospace
    Em             - italic
    Strong         - bold
    Link           - cross-reference label (target shown in LinkRef after)
    LinkRef        - the "(-> Target Title)" reference text

Replacing placeholders:
    The export uses tokens like:
        [VIDEO PLACEHOLDER - Lesson 247]
        [QR PLACEHOLDER - links to: Target Title (target.id)]
    To wire them up:
        Edit -> Find/Change -> GREP -> "\\[VIDEO PLACEHOLDER[^\\]]+\\]"
        Replace with an anchored object containing the YouTube thumbnail
        or the QR PNG. (Designer task; can also be scripted with
        ExtendScript/UXP.)
"""


if __name__ == "__main__":
    raise SystemExit(main())
