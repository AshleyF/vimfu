#!/usr/bin/env python3
"""
Render a VimFu book-page JSON to self-contained HTML.

Screenshots become inline SVGs (via brainstorming/render_svg.py).
Key presses become styled <kbd> badges.
Prose, tips, tables, and dividers are rendered with semantic HTML/CSS.

Usage:
    python render_page.py pages/search_and_find.json
    python render_page.py pages/search_and_find.json -o output/
"""

import json
import shutil
import sys
import re
import html as html_mod
from pathlib import Path

# ── Import SVG renderer from brainstorming/ ──────────────────
_here = Path(__file__).resolve().parent
_root = _here.parent                     # repo root (vimfu/)
sys.path.insert(0, str(_root / "brainstorming"))
from render_svg import (          # noqa: E402
    discover_palette,
    build_svg_elements,
    assemble_svg,
    color_css,
)


# ── Unified palette across multiple frames ────────────────────

def discover_unified_palette(frames, default_fg="d4d4d4", default_bg="000000"):
    """Return (fg_list, bg_list) spanning all frames."""
    fgs, bgs = {default_fg}, {default_bg}  # always include defaults
    for frame in frames:
        for line in frame["lines"]:
            for run in line["runs"]:
                fgs.add(run["fg"])
                bgs.add(run["bg"])
    return (
        sorted(fgs, key=lambda c: (c != default_fg, c)),
        sorted(bgs, key=lambda c: (c != default_bg, c)),
    )


def make_class_maps(fg_list, bg_list):
    """Return (fg_cls, bg_cls, fg_map, bg_map) dicts."""
    fg_cls = {c: f"fg{i}" for i, c in enumerate(fg_list)}
    bg_cls = {c: f"bg{i}" for i, c in enumerate(bg_list)}
    fg_map = {f"fg{i}": c for i, c in enumerate(fg_list)}
    bg_map = {f"bg{i}": c for i, c in enumerate(bg_list)}
    return fg_cls, bg_cls, fg_map, bg_map


# ── Inline key-badge markup ──────────────────────────────────

SPECIAL_KEYS = frozenset({
    "Enter", "Esc", "Space", "Tab", "Backspace",
    "Ctrl", "Shift", "Alt", "Up", "Down", "Left", "Right",
})


def render_kbd(key_text):
    """Render a key name as <kbd class="key ...">."""
    cls = " special" if key_text in SPECIAL_KEYS else ""
    return f'<kbd class="key{cls}">{html_mod.escape(key_text)}</kbd>'


def expand_inline_keys(text):
    """Replace {key:X} markers in *text* with <kbd> badges.

    Non-key text is HTML-escaped; key text is rendered via render_kbd().
    """
    parts = re.split(r"(\{key:[^}]+\})", text)
    result = []
    for part in parts:
        m = re.match(r"\{key:([^}]+)\}", part)
        if m:
            result.append(render_kbd(m.group(1)))
        else:
            result.append(html_mod.escape(part))
    return "".join(result)


# ── Block renderers ───────────────────────────────────────────

def render_heading(block):
    lvl = block["level"]
    text_html = expand_inline_keys(block["text"])
    # Slug from plain text (strip {key:} wrappers)
    plain = re.sub(r"\{key:([^}]+)\}", r"\1", block["text"])
    slug = re.sub(r"[^a-z0-9]+", "-", plain.lower()).strip("-")
    return f'<h{lvl} id="{slug}">{text_html}</h{lvl}>'


def render_prose(block):
    return f'<p>{expand_inline_keys(block["text"])}</p>'


def render_keys(block):
    """Render a key-sequence callout."""
    parts = []
    for item in block["sequence"]:
        if item.startswith("@"):
            parts.append(
                f'<span class="typed">{html_mod.escape(item[1:])}</span>'
            )
        else:
            parts.append(render_kbd(item))
    inner = '<span class="then"> → </span>'.join(parts)
    label = block.get("label", "")
    label_html = (
        f'<span class="seq-label">{html_mod.escape(label)}</span>'
        if label else ""
    )
    return f'<div class="key-sequence">{inner}{label_html}</div>'


def render_screenshot(block, fg_cls, bg_cls, fg_map, bg_map):
    """Render a screenshot as an inline SVG with optional caption.

    Used for print/static output.  For web output, use
    ``render_screenshot_as_gif`` when the block carries a ``lesson`` key.
    """
    frame = block["frame"]
    svg = assemble_svg(frame, fg_cls, bg_cls, fg_map, bg_map)
    caption = block.get("caption", "")
    cap = (
        f"<figcaption>{html_mod.escape(caption)}</figcaption>"
        if caption else ""
    )
    return f'<figure class="screenshot">\n{svg}\n{cap}\n</figure>'


def render_screenshot_as_gif(block, images_dir: Path) -> str:
    """Render a screenshot as a demo GIF (web mode).

    The block must have a ``lesson`` key that identifies which demo GIF
    to use.  The original ``frame`` data is preserved in the JSON for
    print renderers.
    """
    lesson_num = block["lesson"]
    gif_src = _ensure_gif(lesson_num)
    if gif_src is None:
        # Fall back: caller should render as SVG instead
        return None

    images_dir.mkdir(parents=True, exist_ok=True)
    dest = images_dir / gif_src.name
    if not dest.exists() or dest.stat().st_mtime < gif_src.stat().st_mtime:
        shutil.copy2(gif_src, dest)

    rel = f"images/{dest.name}"
    caption = block.get("caption", "")
    cap_html = (
        f'<figcaption>{html_mod.escape(caption)}</figcaption>'
        if caption else ""
    )
    return (
        f'<figure class="demo">\n'
        f'<img src="{html_mod.escape(rel)}" alt="{html_mod.escape(caption)}" '
        f'loading="lazy">\n'
        f'{cap_html}\n</figure>'
    )


def render_tip(block):
    return f'<aside class="tip">{expand_inline_keys(block["text"])}</aside>'


def render_table(block):
    headers = block["headers"]
    rows = block["rows"]
    th = "".join(f"<th>{expand_inline_keys(h)}</th>" for h in headers)
    tr_list = []
    for row in rows:
        td = "".join(f"<td>{expand_inline_keys(c)}</td>" for c in row)
        tr_list.append(f"<tr>{td}</tr>")
    tbody = "\n".join(tr_list)
    return (
        f"<table>\n<thead><tr>{th}</tr></thead>\n"
        f"<tbody>\n{tbody}\n</tbody>\n</table>"
    )


def render_divider(_block):
    return '<hr class="divider">'


def render_qr(block):
    """Render a QR code block as a styled link with a QR-code emoji."""
    url = html_mod.escape(block["url"])
    caption = block.get("caption", "")
    cap_html = html_mod.escape(caption) if caption else url
    return (
        f'<div class="qr-link">'
        f'<span class="qr-icon">📱</span> '
        f'<a href="{url}" target="_blank">{cap_html}</a>'
        f'</div>'
    )


# ── Demo GIF resolver ─────────────────────────────────────

_SHORTS_DIR = _root / "curriculum" / "shorts"
_SHELLPILOT_DIR = _root / "shellpilot"


def _find_lesson_json(lesson_num: int) -> Path | None:
    """Find the lesson JSON for a given lesson number."""
    prefix = f"{lesson_num:04d}_"
    for p in sorted(_SHORTS_DIR.glob(f"{prefix}*.json")):
        return p
    return None


def _ensure_gif(lesson_num: int) -> Path | None:
    """Return the GIF path for a lesson, generating it if needed.

    The GIF pipeline lives in shellpilot/ and must run with CWD there.
    Generated files are cached in shellpilot/videos/<slug>/.
    """
    lesson_json = _find_lesson_json(lesson_num)
    if lesson_json is None:
        print(f"  [demo] WARNING: no lesson JSON for lesson {lesson_num}")
        return None

    slug = lesson_json.stem
    video_dir = _SHELLPILOT_DIR / "videos" / slug
    frames_path = video_dir / f"{slug}.frames.json"
    gif_path = video_dir / f"{slug}.frames.gif"

    if gif_path.exists():
        return gif_path

    # Generate on the fly — need CWD = shellpilot/ for relative imports
    import os
    prev_cwd = os.getcwd()
    sys.path.insert(0, str(_SHELLPILOT_DIR))
    try:
        os.chdir(_SHELLPILOT_DIR)
        from capture_frames import capture_lesson   # noqa: E402
        from gif_maker import make_gif               # noqa: E402

        if not frames_path.exists():
            print(f"  [demo] Capturing frames for lesson {lesson_num}...")
            capture_lesson(lesson_json, output=frames_path)

        doc = json.loads(frames_path.read_text(encoding="utf-8"))
        print(f"  [demo] Rendering GIF for lesson {lesson_num}...")
        make_gif(doc, gif_path, speed=2.0, font_size=48, show_keys=False)
    except Exception as exc:
        print(f"  [demo] ERROR generating GIF for lesson {lesson_num}: {exc}")
        return None
    finally:
        os.chdir(prev_cwd)

    return gif_path if gif_path.exists() else None


def render_demo(block, images_dir: Path) -> str:
    """Render a demo block as an <img> referencing the lesson GIF."""
    lesson_num = block["lesson"]
    gif_src = _ensure_gif(lesson_num)
    if gif_src is None:
        return f'<!-- demo: GIF not available for lesson {lesson_num} -->'

    # Copy GIF into images/ next to the HTML output
    images_dir.mkdir(parents=True, exist_ok=True)
    dest = images_dir / gif_src.name
    if not dest.exists() or dest.stat().st_mtime < gif_src.stat().st_mtime:
        shutil.copy2(gif_src, dest)

    rel = f"images/{dest.name}"
    caption = block.get("caption", "")
    cap_html = (
        f'<figcaption>{html_mod.escape(caption)}</figcaption>'
        if caption else ""
    )
    return (
        f'<figure class="demo">\n'
        f'<img src="{html_mod.escape(rel)}" alt="{html_mod.escape(caption)}" '
        f'loading="lazy">\n'
        f'{cap_html}\n</figure>'
    )


_RENDERERS = {
    "heading":    render_heading,
    "prose":      render_prose,
    "keys":       render_keys,
    "tip":        render_tip,
    "table":      render_table,
    "divider":    render_divider,
    "qr":         render_qr,
    # "screenshot" handled specially (needs palette args)
    # "demo" handled specially (needs images_dir)
}


def render_block(block, fg_cls, bg_cls, fg_map, bg_map, *,
                 images_dir: Path | None = None):
    t = block["type"]
    if t == "screenshot":
        # Web mode: if the screenshot has a lesson reference, show the GIF
        if "lesson" in block and images_dir is not None:
            gif_html = render_screenshot_as_gif(block, images_dir)
            if gif_html is not None:
                return gif_html
        # Fallback / print mode: render as inline SVG
        return render_screenshot(block, fg_cls, bg_cls, fg_map, bg_map)
    if t == "demo":
        return render_demo(block, images_dir) if images_dir else \
            f'<!-- demo: no images_dir set -->'
    fn = _RENDERERS.get(t)
    if fn:
        return fn(block)
    return f"<!-- unknown block type: {t} -->"


# ── Page CSS ──────────────────────────────────────────────────

PAGE_CSS = """\
/* ── Reset & base ───────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: 'Georgia', 'Times New Roman', serif;
  line-height: 1.7;
  max-width: 720px;
  margin: 0 auto;
  padding: 2.5rem 1.5rem;
  color: #222;
  background: #fafaf8;
}

/* ── Headings ───────────────────────────────────────────── */
h1 {
  font-size: 2rem;
  margin: 0 0 0.3rem;
  color: #1a1a1a;
  border-bottom: 2px solid #ddd;
  padding-bottom: 0.4rem;
}
h2 {
  font-size: 1.5rem;
  margin: 2.2rem 0 0.6rem;
  color: #2a2a2a;
}
h3 {
  font-size: 1.15rem;
  margin: 1.6rem 0 0.4rem;
  color: #333;
}
.subtitle {
  font-size: 1.1rem;
  color: #666;
  margin-bottom: 2rem;
  font-style: italic;
}

/* ── Prose ──────────────────────────────────────────────── */
p { margin: 0.6em 0; }

/* ── Key badges ─────────────────────────────────────────── */
kbd.key {
  display: inline-block;
  padding: 1px 7px;
  font-family: 'Cascadia Code', 'Consolas', 'Courier New', monospace;
  font-size: 0.88em;
  background: #f4f0ec;
  border: 1px solid #c8c0b8;
  border-radius: 4px;
  box-shadow: 0 2px 0 #d5cec6;
  color: #333;
  white-space: nowrap;
  vertical-align: baseline;
  line-height: 1.4;
}
kbd.key.special {
  background: #e8e0f0;
  border-color: #b8a0d0;
  box-shadow: 0 2px 0 #c0b0d8;
}

/* ── Key-sequence row ───────────────────────────────────── */
.key-sequence {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0;
  margin: 0.8em 0;
  padding: 0.7em 1em;
  background: #f5f3f0;
  border: 1px solid #e0dcd6;
  border-radius: 6px;
}
.key-sequence .then {
  color: #999;
  margin: 0 0.3em;
  font-size: 0.9em;
}
.key-sequence .typed {
  font-family: 'Cascadia Code', 'Consolas', monospace;
  color: #b45309;
  font-weight: 600;
  letter-spacing: 0.03em;
}
.key-sequence .seq-label {
  margin-left: auto;
  font-style: italic;
  color: #888;
  font-size: 0.85em;
  padding-left: 1em;
}

/* ── Screenshots ────────────────────────────────────────── */
figure.screenshot {
  margin: 1.5em 0;
  text-align: center;
}
figure.screenshot svg {
  display: block;
  margin: 0 auto;
  width: 100%;
  max-width: 560px;
  border: 2px solid #444;
  border-radius: 6px;
}
figcaption {
  font-size: 0.85em;
  color: #777;
  margin-top: 0.4em;
  font-style: italic;
}

/* ── Demo GIFs ──────────────────────────────────────────── */
figure.demo {
  margin: 1.5em 0;
  text-align: center;
}
figure.demo img {
  display: block;
  margin: 0 auto;
  width: 100%;
  max-width: 560px;
  border: 2px solid #444;
  border-radius: 6px;
}

/* ── Tip aside ──────────────────────────────────────────── */
aside.tip {
  margin: 1em 0;
  padding: 0.8em 1.2em;
  background: #f0f6ff;
  border-left: 4px solid #4a90d9;
  border-radius: 0 6px 6px 0;
  font-size: 0.95em;
}
aside.tip::before { content: "💡 "; }

/* ── Table ──────────────────────────────────────────────── */
table {
  width: 100%;
  border-collapse: collapse;
  margin: 1em 0;
  font-size: 0.95em;
}
th, td {
  padding: 6px 12px;
  border: 1px solid #ddd;
  text-align: left;
}
th {
  background: #f0ede8;
  font-weight: 600;
}
td:first-child {
  font-family: 'Cascadia Code', 'Consolas', monospace;
  white-space: nowrap;
}

/* ── Divider ────────────────────────────────────────────── */
hr.divider { border: none; border-top: 1px solid #ddd; margin: 2rem 0; }

/* ── QR code link ───────────────────────────────────────── */
.qr-link {
  margin: 0.6em 0;
  padding: 0.5em 1em;
  background: #f8f5ff;
  border: 1px solid #e0d8f0;
  border-radius: 6px;
  font-size: 0.9em;
}
.qr-link .qr-icon { font-size: 1.1em; }
.qr-link a {
  color: #5b3ea5;
  text-decoration: none;
  font-weight: 500;
}
.qr-link a:hover { text-decoration: underline; }

/* ── Navigation bar ─────────────────────────────────────── */
nav.book-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.8em 0;
  border-top: 1px solid #ddd;
  border-bottom: 1px solid #ddd;
  margin: 1.5rem 0;
  font-size: 0.9em;
}
nav.book-nav a {
  color: #5b3ea5;
  text-decoration: none;
  font-weight: 500;
}
nav.book-nav a:hover { text-decoration: underline; }
nav.book-nav .nav-prev,
nav.book-nav .nav-next { flex: 1; }
nav.book-nav .nav-prev { text-align: left; }
nav.book-nav .nav-next { text-align: right; }
nav.book-nav .nav-toc  { text-align: center; }
nav.book-nav .nav-prev::before { content: "← "; }
nav.book-nav .nav-next::after  { content: " →"; }
nav.book-nav .disabled {
  color: #ccc;
  pointer-events: none;
}
"""


# ── Full-page assembly ────────────────────────────────────────

def _render_nav(nav: dict | None) -> str:
    """Return a <nav> bar HTML string, or empty string if *nav* is None."""
    if nav is None:
        return ""
    prev_link = (
        f'<a href="{html_mod.escape(nav["prev"]["href"])}">{html_mod.escape(nav["prev"]["title"])}</a>'
        if nav.get("prev") else '<span class="disabled">Previous</span>'
    )
    next_link = (
        f'<a href="{html_mod.escape(nav["next"]["href"])}">{html_mod.escape(nav["next"]["title"])}</a>'
        if nav.get("next") else '<span class="disabled">Next</span>'
    )
    toc_link = f'<a href="{html_mod.escape(nav["toc"])}">{html_mod.escape(nav.get("toc_label", "Table of Contents"))}</a>'
    return (
        f'<nav class="book-nav">\n'
        f'  <span class="nav-prev">{prev_link}</span>\n'
        f'  <span class="nav-toc">{toc_link}</span>\n'
        f'  <span class="nav-next">{next_link}</span>\n'
        f'</nav>'
    )


def render_page(page, *, images_dir: Path | None = None,
                nav: dict | None = None):
    """Render a page dict → complete self-contained HTML string.

    *images_dir* — directory where demo GIFs will be copied.  If ``None``,
    demo blocks are skipped with a comment.
    *nav* — optional navigation dict with keys ``prev``, ``next``, ``toc``.
            ``prev``/``next`` are ``{"href": "...", "title": "..."}`` or None.
            ``toc`` is the relative URL to the table-of-contents page.
    """

    # Collect every frame for a unified SVG palette
    frames = [b["frame"] for b in page["content"] if b["type"] == "screenshot"]
    if frames:
        dfg = frames[0].get("defaultFg", "d4d4d4")
        dbg = frames[0].get("defaultBg", "000000")
        fg_list, bg_list = discover_unified_palette(frames, dfg, dbg)
        fg_cls, bg_cls, fg_map, bg_map = make_class_maps(fg_list, bg_list)
        svg_css = color_css(fg_map, bg_map)
    else:
        fg_cls = bg_cls = fg_map = bg_map = {}
        svg_css = ""

    # Render blocks
    blocks_html = []
    for block in page["content"]:
        blocks_html.append(
            render_block(block, fg_cls, bg_cls, fg_map, bg_map,
                         images_dir=images_dir)
        )
    body = "\n\n".join(blocks_html)

    title = html_mod.escape(page["title"])
    subtitle = page.get("subtitle", "")
    sub_html = (
        f'<p class="subtitle">{html_mod.escape(subtitle)}</p>'
        if subtitle else ""
    )

    nav_html = _render_nav(nav)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title} — VimFu</title>
<style>
{PAGE_CSS}
/* ── SVG colour theme ─────────────────────────────────── */
{svg_css}
</style>
</head>
<body>
{nav_html}
{sub_html}
{body}
{nav_html}
</body>
</html>"""


# ── CLI ───────────────────────────────────────────────────────

# ── Table of Contents generator ────────────────────────────

# Canonical ordering of content files for TOC + navigation.
# front_matter is first, then chapters in order.
_CONTENT_DIR = _here / "content"


def _discover_pages() -> list[Path]:
    """Return content JSON files in book order."""
    pages: list[Path] = []
    # front_matter always first
    fm = _CONTENT_DIR / "front_matter.json"
    if fm.exists():
        pages.append(fm)
    # chapters sorted by filename (ch01_, ch02_, ...)
    for p in sorted(_CONTENT_DIR.glob("ch*.json")):
        pages.append(p)
    # appendices
    for p in sorted(_CONTENT_DIR.glob("app_*.json")):
        pages.append(p)
    return pages


def render_toc(pages_meta: list[dict]) -> str:
    """Render a Table of Contents HTML page.

    *pages_meta* is a list of dicts with keys ``stem``, ``title``, ``subtitle``.
    """
    items = []
    for pm in pages_meta:
        href = f"{pm['stem']}.html"
        title = html_mod.escape(pm["title"])
        sub = pm.get("subtitle", "")
        sub_html = f' <span class="toc-subtitle">— {html_mod.escape(sub)}</span>' if sub else ""
        items.append(f'<li><a href="{href}">{title}</a>{sub_html}</li>')
    toc_list = "\n".join(items)

    toc_css = PAGE_CSS + """
/* ── Table of Contents ──────────────────────────────────── */
ul.toc {
  list-style: none;
  padding: 0;
}
ul.toc li {
  margin: 0.6em 0;
  font-size: 1.1em;
}
ul.toc li a {
  color: #5b3ea5;
  text-decoration: none;
  font-weight: 600;
}
ul.toc li a:hover { text-decoration: underline; }
.toc-subtitle {
  font-weight: 400;
  color: #888;
  font-style: italic;
  font-size: 0.9em;
}
"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>VimFu — Table of Contents</title>
<style>
{toc_css}
</style>
</head>
<body>
<h1>VimFu</h1>
<p class="subtitle">Master the Vim Editing Language</p>
<h2>Table of Contents</h2>
<ul class="toc">
{toc_list}
</ul>
</body>
</html>"""


# ── CLI ───────────────────────────────────────────────────────

def main():
    import argparse
    ap = argparse.ArgumentParser(description="Render VimFu book page → HTML")
    ap.add_argument("input", nargs="?", default=None,
                    help="Page JSON file (omit to build all pages + TOC)")
    ap.add_argument("-o", "--output-dir", default=None,
                    help="Output directory (default: book/output/)")
    args = ap.parse_args()

    if args.input:
        # ── Single-page mode (original behaviour) ──
        src = Path(args.input)
        page = json.loads(src.read_text("utf-8"))
        out_dir = Path(args.output_dir) if args.output_dir else src.parent
        out_dir.mkdir(parents=True, exist_ok=True)
        images_dir = out_dir / "images"
        result = render_page(page, images_dir=images_dir)
        out_path = out_dir / f"{src.stem}.html"
        out_path.write_text(result, encoding="utf-8")
        print(f"Wrote {out_path}  ({out_path.stat().st_size:,} bytes)")
        return

    # ── Full-book mode: build all pages + TOC ──
    page_files = _discover_pages()
    if not page_files:
        print("No content files found in book/content/")
        return

    out_dir = Path(args.output_dir) if args.output_dir else (_here / "output")
    out_dir.mkdir(parents=True, exist_ok=True)
    images_dir = out_dir / "images"

    # Load all page metadata
    pages_data = []
    for pf in page_files:
        page = json.loads(pf.read_text("utf-8"))
        pages_data.append({"path": pf, "page": page, "stem": pf.stem})

    pages_meta = [
        {"stem": pd["stem"], "title": pd["page"]["title"],
         "subtitle": pd["page"].get("subtitle", "")}
        for pd in pages_data
    ]

    # Render each page with navigation
    for i, pd in enumerate(pages_data):
        prev_info = (
            {"href": f"{pages_data[i-1]['stem']}.html",
             "title": pages_data[i-1]["page"]["title"]}
            if i > 0 else None
        )
        next_info = (
            {"href": f"{pages_data[i+1]['stem']}.html",
             "title": pages_data[i+1]["page"]["title"]}
            if i < len(pages_data) - 1 else None
        )
        nav = {
            "prev": prev_info,
            "next": next_info,
            "toc": "index.html",
            "toc_label": "Table of Contents",
        }
        result = render_page(pd["page"], images_dir=images_dir, nav=nav)
        out_path = out_dir / f"{pd['stem']}.html"
        out_path.write_text(result, encoding="utf-8")
        print(f"Wrote {out_path}  ({out_path.stat().st_size:,} bytes)")

    # Render TOC
    toc_html = render_toc(pages_meta)
    toc_path = out_dir / "index.html"
    toc_path.write_text(toc_html, encoding="utf-8")
    print(f"Wrote {toc_path}  ({toc_path.stat().st_size:,} bytes)")
    print(f"\nDone — {len(pages_data)} pages + TOC")


if __name__ == "__main__":
    main()
