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

# Ensure UTF-8 stdout on Windows (cp1252) so summary prints with "→" don't crash.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from lib.videos import _index as _videos_index, video_for_lesson, videos_for_topic  # noqa: E402
from render_latex import _atomize_key  # noqa: E402  shared key-splitting rules
from lib.audience import visible as _visible  # noqa: E402
from lib.site_config import contact_email  # noqa: E402
from lib.sim_link import SIM_LINK_VERSION as _SIM_LINK_VERSION, practice_filename  # noqa: E402
from lib.parts import part_label as _part_label  # noqa: E402


def _report_footer(prefix: str = "") -> str:
    """Tiny shared footer with mailto + GitHub. ``prefix`` is the relative
    path back to the site root (e.g. ``""``, ``"../"``)."""
    from urllib.parse import quote
    em = contact_email()
    subj = quote("VimFu — issue report")
    return (
        '<footer class="site-footer">'
        f'Found a problem? <a href="mailto:{em}?subject={subj}">{em}</a> '
        f'· <a href="{prefix}r/github" rel="noopener">GitHub issues</a> '
        f'· <a href="{prefix}r/errata" rel="noopener">Book errata</a>'
        '</footer>'
    )

AUDIENCE = "web"

PARTS_DIR = ROOT / "parts"
EXAMPLES_DIR = ROOT / "examples"
SCREENSHOTS_DIR = ROOT / "output" / "html" / "screenshots"
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
                "visible": _visible(t, AUDIENCE),
            }
    return idx


# -------- inline markup --------------------------------------------------- #

# Order matters: do `code`, **strong**, *em* AFTER escape, BEFORE link/key
_KEY_RE   = re.compile(r"\{key:([^}]+|\})\}")
_LINK_RE  = re.compile(r"\[([^\]]+)\]\(#([^)]+)\)")
_CODE_RE  = re.compile(r"`([^`]+)`")
_STRONG_RE = re.compile(r"\*\*([^*]+)\*\*")
_EM_RE    = re.compile(r"(?<!\*)\*([^*\n]+)\*(?!\*)")

def _emit_key_pills(k: str) -> str:
    """Render a `{key:...}` payload as one or more <kbd> pills.

    Multi-character pure-ASCII runs like ``hjkl``, ``gg``, ``zz``,
    ``Ctrl-hjkl`` represent a sequence of separate keystrokes and split
    into one pill per atomic key — matching the LaTeX renderer and the
    style guide.
    """
    atoms = _atomize_key(k)
    if not atoms:
        return f'<kbd>{escape(k)}</kbd>'
    return "".join(f'<kbd>{escape(a)}</kbd>' for a in atoms)


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
        r"(?P<key>\{key:(?:[^}]+|\})\})"
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
            if (len(k) >= 3 and k.startswith(":")
                    and all(c.isalnum() or c in "_!" for c in k[1:])):
                out_parts.append(f'<code>{escape(k)}</code>')
            else:
                out_parts.append(_emit_key_pills(k))
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
                 f'src="https://www.youtube-nocookie.com/embed/{escape(vid)}?rel=0&amp;playsinline=1&amp;modestbranding=1&amp;controls=0&amp;iv_load_policy=3&amp;disablekb=1" '
                 f'title="{title}" loading="lazy" allowfullscreen '
                 f'referrerpolicy="no-referrer-when-downgrade" '
                 f'allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"></iframe>')
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
                      f'src="https://www.youtube-nocookie.com/embed/{escape(v["videoId"])}?rel=0&amp;playsinline=1&amp;modestbranding=1&amp;controls=0&amp;iv_load_policy=3&amp;disablekb=1" '
                      f'title="{escape(v["title"])}" loading="lazy" allowfullscreen '
                      f'referrerpolicy="no-referrer-when-downgrade" '
                      f'allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"></iframe>')
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


def _strip_vim_chrome(lines: list) -> list:
    """Drop trailing vim ``~`` empty-buffer markers and the status line.

    Vim renders unused buffer rows as ``~`` and the bottom row as a status
    line (e.g. ``foo.txt   1,1``). Captured compact frames include those, but
    when seeding a fresh file we only want the actual buffer contents.
    """
    out = list(lines)
    # Drop status line (last non-empty line that contains the file name + a
    # row,col indicator or large internal whitespace gap). Heuristic: a line
    # whose stripped form is mostly spaces with a trailing "N,M" token.
    if out:
        last = out[-1].rstrip()
        # Match e.g. "hi.txt                1,7" or "[No Name]   0,0-1   All"
        if re.search(r"\s\d+,\d+(-\d+)?(\s+\S+)?\s*$", last):
            out.pop()
    # Drop trailing ~-only lines (vim's empty-buffer markers).
    while out and out[-1].strip() == "~":
        out.pop()
    # Also collapse trailing blank lines.
    while out and out[-1].strip() == "":
        out.pop()
    return out


def _example_practice_query(ex: dict) -> str:
    """Build a sim deep-link query for a single example's starting buffer."""
    from urllib.parse import urlencode
    frames = (ex or {}).get("frames") or []
    if not frames:
        return ""
    compact = (frames[0].get("compact") or {})
    lines = _strip_vim_chrome(compact.get("lines") or [])
    if not lines:
        return ""
    content = "\n".join(lines) + "\n"
    return urlencode({"v": SIM_LINK_VERSION, "file": practice_filename(ex, content), "content": content})


# Single source of truth lives in ``lib/sim_link.py``. Re-exported here so
# existing call sites keep working unchanged.
SIM_LINK_VERSION = _SIM_LINK_VERSION


def _practice_query(t: dict, examples: dict) -> str:
    """Build the query string for the topic's "Practice in the simulator" link.

    For Vim topics, seed ``practice.txt`` with the first example's starting
    buffer (if any) and open it in nvim. For tmux topics, drop straight into
    a tmux session. For shell topics, just open the shell at a clean prompt.

    Always includes a ``v=`` cache-buster so a stale cached sim/index.html
    can't shadow the latest preload semantics.
    """
    from urllib.parse import urlencode

    # tmux part takes precedence — sim simulates tmux directly.
    part_dir = t.get("__part_dir") or ""
    if "tmux" in part_dir:
        return urlencode({"v": SIM_LINK_VERSION, "cmd": "tmux"})
    # Try to seed from the first wired example.
    for b in t.get("blocks") or []:
        if b.get("type") == "example":
            ex = examples.get(b.get("ref")) if isinstance(examples, dict) else None
            if not ex:
                continue
            frames = ex.get("frames") or []
            if not frames:
                continue
            compact = (frames[0].get("compact") or {})
            lines = _strip_vim_chrome(compact.get("lines") or [])
            if not lines:
                continue
            content = "\n".join(lines) + "\n"
            return urlencode({"v": SIM_LINK_VERSION, "file": practice_filename(ex, content), "content": content})
    return urlencode({"v": SIM_LINK_VERSION})


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
            rel = f"../screenshots/{ex_id}/frame_{i:02d}.color.svg"
            exists = (SCREENSHOTS_DIR / ex_id / f"frame_{i:02d}.color.svg").exists()
            out.append('<figure class="example-step">')
            head = [f'<span class="step-n">Step {i}</span>']
            if keys:
                head.append(_emit_key_pills(keys))
            head.append(f'<span class="step-cap">{inl(cap)}</span>')
            out.append(f'<figcaption>{" · ".join(head)}</figcaption>')
            if exists:
                out.append(f'<div class="screenshot"><img src="{escape(rel)}" alt="{escape(cap or ex_id)}"></div>')
            else:
                out.append(f'<div class="screenshot missing">[missing screenshot {ex_id}/frame_{i:02d}.color.svg — run python content/render_screenshots.py]</div>')
            if narr:
                out.append(f'<p class="narration">{inl(narr)}</p>')
            out.append('</figure>')
        # "Try it in the simulator" — preload the example's starting buffer.
        try_qs = _example_practice_query(ex)
        if try_qs:
            out.append(
                f'<p class="example-try"><a class="practice-link" '
                f'href="../sim/?{try_qs}" target="_blank" rel="noopener">'
                f'▶ Try this in the simulator</a></p>'
            )
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

    if bt == "figure":
        raw_path = (b.get("path") or "").strip()
        caption = inl(b.get("caption") or "")
        credit = inl(b.get("credit") or "")
        if not raw_path:
            return ""
        # Copy the image into the site output once, alongside the topic
        # HTML file. We use a flat /images/ subtree under docs/ to keep
        # the URL stable across re-renders.
        src = (Path(__file__).resolve().parent.parent / raw_path).resolve()
        from shutil import copyfile
        out_root = Path(__file__).resolve().parent / "output" / "html" / "images"
        out_root.mkdir(parents=True, exist_ok=True)
        dst = out_root / src.name
        try:
            if src.exists() and (not dst.exists() or src.stat().st_mtime > dst.stat().st_mtime):
                copyfile(src, dst)
        except OSError:
            pass
        href = f"../images/{src.name}"
        dim_attrs = ""
        try:
            from PIL import Image
            with Image.open(src) as im:
                dim_attrs = f' width="{im.width}" height="{im.height}"'
        except Exception:
            pass
        parts = [
            '<figure class="photo">',
            f'<img src="{escape(href)}"{dim_attrs} alt="{escape(b.get("caption") or src.stem)}">',
        ]
        if caption or credit:
            cap_html = f'<figcaption>{caption}'
            if credit:
                cap_html += f' <span class="credit">{credit}</span>'
            cap_html += '</figcaption>'
            parts.append(cap_html)
        parts.append('</figure>')
        return "\n".join(parts)

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
            key_html = _emit_key_pills(key) if key else ""
            out.append(f"<tr><td>{key_html}</td><td>{note}</td></tr>")
        out.append("</tbody></table></figure>")
        return "\n".join(out)

    if bt == "table":
        headers = b.get("headers", [])
        rows = b.get("rows", [])
        if not headers:
            return ""
        # Auto-style "Key"/"Keys" columns: if a cell doesn't already contain
        # {key:...} markup, wrap the whole cell as one. Honors an explicit
        # ``keyColumns`` list if the topic wants finer control.
        key_cols = set(b.get("keyColumns") or
                       [i for i, h in enumerate(headers)
                        if str(h).strip().lower() in ("key", "keys")])
        out = ['<table>', '<thead><tr>']
        for h in headers:
            out.append(f"<th>{inl(h)}</th>")
        out.append("</tr></thead><tbody>")
        for row in rows:
            cells = list(row) + [""] * (len(headers) - len(row))
            out.append("<tr>")
            for i, c in enumerate(cells):
                s = str(c)
                if i in key_cols and s and "{key:" not in s:
                    s = "{key:" + s + "}"
                out.append(f"<td>{inl(s)}</td>")
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
               f'<header>⚙ {title}</header>']
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

    if bt == "anecdote":
        title = inl(b.get("title", ""))
        text = b.get("text", "") or ""
        header_text = f"📖 {title}" if title else "📖 A story"
        out = ['<aside class="anecdote">',
               f'<header>{header_text}</header>']
        for para in text.split("\n\n"):
            para = para.rstrip()
            if not para:
                continue
            out.append(render_para_with_fences(para, current_part=current_part, index=index))
        out.append("</aside>")
        return "\n".join(out)

    if bt == "qr":
        slug = b.get("slug")
        caption = b.get("caption") or ""
        if slug:
            href = f"../r/{escape(str(slug))}/"
            label = caption or str(slug)
            return f'<aside class="qr"><span>→ <a href="{href}">{escape(label)}</a></span></aside>'
        url = b.get("url")
        if url:
            label = caption or url
            return f'<aside class="qr"><span>→ <a href="{escape(url)}">{escape(label)}</a></span></aside>'
        tid = b.get("topic", "")
        info = index.get(tid)
        label = info["title"] if info else tid
        href = ""
        if info:
            href = (f"../{info['part_dir']}/{info['file_stem']}.html"
                    if info["part_dir"] != current_part else f"{info['file_stem']}.html")
        link = f'<a href="{escape(href)}">{escape(label)}</a>' if href else escape(label)
        # No QR image in HTML -- readers can just click the link. QR codes are
        # generated for the printed book where scanning is the only path back
        # to the site.
        return f'<aside class="qr"><span>→ See also {link}</span></aside>'

    if bt == "buy-prompt":
        return (
            '<aside class="buy-prompt">'
            '<a class="buy-prompt-link" href="../r/book/">'
            '<img class="buy-prompt-cover" src="../cover_thumb.jpg" width="200" height="245" alt="VimFu book cover">'
            '<span class="buy-prompt-text">'
            '<span class="buy-prompt-headline">📖 Want the full story?</span>'
            '<span class="buy-prompt-cta">Get the VimFu book →</span>'
            '</span>'
            '</a>'
            '</aside>'
        )

    return f"<!-- unknown block type: {escape(str(bt))} -->"


# -------- shared head/body fragments -------------------------------------- #

# Inline FOUC-safe theme initializer. Must run before <body> renders so the
# correct theme is set immediately. Honors localStorage choice if present,
# otherwise falls back to the OS preference.
THEME_INIT_SCRIPT = """<script>
(function(){{
  try {{
    var t = localStorage.getItem('vimfu-theme');
    if (t === 'light' || t === 'dark') {{
      document.documentElement.setAttribute('data-theme', t);
    }}
  }} catch(e) {{}}
}})();
</script>"""

# Floating top-right toggle button. Click cycles light <-> dark and persists.
# Updates the icon to reflect the *next* state (so users see what tapping does).
THEME_TOGGLE_BUTTON = """<button id="theme-toggle" type="button" aria-label="Toggle light/dark theme" title="Toggle theme">🌓</button>
<script>
(function(){{
  var btn = document.getElementById('theme-toggle');
  if (!btn) return;
  function current(){{
    var t = document.documentElement.getAttribute('data-theme');
    if (t) return t;
    return matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }}
  function paint(){{
    btn.textContent = current() === 'dark' ? '☀' : '☾';
  }}
  paint();
  btn.addEventListener('click', function(){{
    var next = current() === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    try {{ localStorage.setItem('vimfu-theme', next); }} catch(e) {{}}
    paint();
  }});
  // React to OS preference flips while no explicit choice is set.
  matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(){{
    if (!localStorage.getItem('vimfu-theme')) paint();
  }});
}})();
</script>"""


# -------- topic page ------------------------------------------------------ #

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — VimFu</title>
<link rel="icon" type="image/png" href="{root_index_dir}icon.png">
<link rel="stylesheet" href="{css}">
THEME_INIT_PLACEHOLDER
</head>
<body>
THEME_TOGGLE_PLACEHOLDER
<nav class="topnav">
  <a href="{root_index}">📚 Contents</a>
  &middot; <a href="{root_index}#part-{part_dir}">↑ {part_label}</a>
  &middot; <a href="{root_index_dir}videos/{part_dir}/">🎬 Videos</a>
  &middot; <a class="practice-link" href="../sim/?{practice_qs}" target="_blank" rel="noopener">▶ Practice in the simulator</a>
</nav>
<nav class="pager pager-top">
  <span class="pager-prev">{prev_link}</span>
  <span class="pager-pos">{pos_label}</span>
  <span class="pager-next">{next_link}</span>
</nav>
<article>
{body}
</article>
<nav class="pager pager-bottom">
  <span class="pager-prev">{prev_link}</span>
  <span class="pager-pos">{pos_label}</span>
  <span class="pager-next">{next_link}</span>
</nav>
<nav class="bottomnav">
  <a href="{root_index}#part-{part_dir}">↑ back to {part_label}</a>
  &middot; <a href="{root_index}">📚 contents</a>
</nav>
{footer}
</body>
</html>
""".replace("THEME_INIT_PLACEHOLDER", THEME_INIT_SCRIPT).replace("THEME_TOGGLE_PLACEHOLDER", THEME_TOGGLE_BUTTON)


def _pager_links(current_part: str, current_stem: str, ordered: list[tuple[str,str,str]]) -> tuple[str,str,str]:
    """Return (prev_link_html, next_link_html, pos_label) for the topic.

    `ordered` is a flat list of (part_dir, stem, title) for every web-visible
    topic, in reading order.
    """
    idx = next((i for i, (p, s, _t) in enumerate(ordered)
                if p == current_part and s == current_stem), None)
    if idx is None:
        return ("", "", "")

    def _href(p: str, s: str) -> str:
        return f"{s}.html" if p == current_part else f"../{p}/{s}.html"

    if idx > 0:
        p, s, t = ordered[idx - 1]
        prev_html = f'<a class="pager-link" href="{escape(_href(p, s))}" rel="prev">← {escape(t)}</a>'
    else:
        prev_html = '<span class="pager-disabled">← start of book</span>'

    if idx < len(ordered) - 1:
        p, s, t = ordered[idx + 1]
        next_html = f'<a class="pager-link" href="{escape(_href(p, s))}" rel="next">{escape(t)} →</a>'
    else:
        next_html = '<span class="pager-disabled">end of book →</span>'

    pos = f"{idx + 1} / {len(ordered)}"
    return (prev_html, next_html, pos)


def render_topic_page(t, index, examples, ordered=None) -> str:
    current_part = t["__part_dir"]
    inl = lambda s: render_inline(s, current_part=current_part, index=index)

    title = t.get("title", "(untitled)")
    sub = t.get("subtitle", "")

    body: list[str] = [f"<h1>{inl(title)}</h1>"]
    if sub:
        body.append(f'<p class="subtitle">{inl(sub)}</p>')

    meta = []
    if keys := t.get("keys"):
        rendered_keys = []
        for k in keys:
            ks = str(k)
            # The keys[] array carries a mix of plain key names (`gg`, `Esc`),
            # explicit markup (`{key:Ctrl-R}`), placeholders (`{n}G`), and
            # backticked code (`` `:wq` ``). Route anything with markup through
            # render_inline so it resolves the same way prose does; wrap plain
            # names in `{key:...}` first so the splitter still atomizes them.
            if any(c in ks for c in "{`*["):
                rendered_keys.append(inl(ks))
            else:
                rendered_keys.append(_emit_key_pills(ks))
        meta.append("Keys: " + ", ".join(rendered_keys))
    if meta:
        body.append('<p class="meta">' + " &middot; ".join(meta) + "</p>")
    # Note: id, part, and lessons are intentionally not shown on the web —
    # they're internal taxonomy, not reader-facing reference material.

    if summary := t.get("summary"):
        body.append(f'<blockquote class="summary">{inl(summary)}</blockquote>')

    # Block types that are book-only per Strategy.md (web is a reference, not
    # a deep-dive): suppress QR cross-promotion asides, storytelling
    # anecdotes, and "Under the Hood" internals sidebars on the website.
    WEB_SUPPRESSED_BLOCKS = {"qr", "anecdote", "internals"}

    for b in t.get("blocks", []):
        if not _visible(b, AUDIENCE):
            continue
        if AUDIENCE == "web" and b.get("type") in WEB_SUPPRESSED_BLOCKS:
            continue
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
            if info and not info.get("visible", True):
                continue
            if info:
                href = (f"{info['file_stem']}.html"
                        if info["part_dir"] == current_part
                        else f"../{info['part_dir']}/{info['file_stem']}.html")
                links.append(f'<a href="{escape(href)}">{escape(info["title"])}</a>')
            else:
                links.append(f'<span class="broken">{escape(ref_id)}</span>')
        body.append('<p class="see-also"><strong>See also:</strong> ' + ", ".join(links) + "</p>")

    part_label = _part_label(current_part)
    practice_qs = _practice_query(t, examples)
    prev_link, next_link, pos_label = _pager_links(current_part, t["__file_stem"], ordered or [])
    return PAGE.format(
        title=escape(title),
        css="../style.css",
        root_index="../index.html",
        root_index_dir="../",
        part_dir=current_part,
        part_label=escape(part_label),
        practice_qs=practice_qs,
        prev_link=prev_link,
        next_link=next_link,
        pos_label=escape(pos_label),
        body="\n".join(body),
        footer=_report_footer(prefix="../"),
    )


# -------- index pages ----------------------------------------------------- #

PART_INDEX = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{label} — VimFu</title>
<meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0;url=../index.html#part-{part_dir}">
<link rel="canonical" href="../index.html#part-{part_dir}">
</head><body>
<p>This page has moved. <a href="../index.html#part-{part_dir}">Continue to {label} on the contents page</a>.</p>
<script>location.replace('../index.html#part-{part_dir}');</script>
</body></html>
"""


def render_part_index(part_dir, topics_in_part, all_parts=None) -> str:
    label = _part_label(part_dir)
    return PART_INDEX.format(label=escape(label), part_dir=escape(part_dir))


ROOT_INDEX = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>VimFu &mdash; Master Your Editor. Unleash Your Flow.</title>
<link rel="icon" type="image/png" href="icon.png">
<link rel="stylesheet" href="style.css">
THEME_INIT_PLACEHOLDER
</head><body>
THEME_TOGGLE_PLACEHOLDER
<article>
<h1 class="site-banner">
  <img class="banner-light" src="vimfu_light.png" width="1916" height="821" alt="VimFu — Master Your Editor. Unleash Your Flow.">
  <img class="banner-dark" src="vimfu_dark.png" width="1916" height="821" alt="" aria-hidden="true">
</h1>
<!-- Auto-generated from content/parts/**/*.json -->
<p class="tagline">The Vim &amp; Neovim reference for programmers &mdash; companion to <a href="r/book/">the book</a>.</p>

<section class="hero">
  <a class="hero-book" href="r/book/" aria-label="Get the VimFu book">
    <img class="hero-book-cover" src="cover_thumb.jpg" width="200" height="245" alt="VimFu book cover">
    <span class="hero-book-text">
      <span class="hero-book-headline">Get the VimFu book</span>
      <span class="hero-book-sub">History, internals, mental models &amp; worked examples for every concept.</span>
    </span>
  </a>
  <p>This is the <strong>online reference</strong> half of <em>VimFu</em>. Quick to scan, deep-linkable, packed with embedded videos. Every topic in the book has a page here so you can look something up without flipping pages.</p>
  <p>The site is the cheat sheet; the book is the why.</p>
  <p class="hero-cta">
    <a class="practice-link" href="sim/" target="_blank" rel="noopener">▶ Open the simulator</a>
    <a class="practice-link" href="videos/">🎬 All videos</a>
    <span class="hero-aside">An in-browser Neovim + tmux for practicing anything you read here.</span>
  </p>
</section>

<h2 class="contents-heading">Contents</h2>
{sections}
</article>
{footer}
</body></html>
""".replace("THEME_INIT_PLACEHOLDER", THEME_INIT_SCRIPT).replace("THEME_TOGGLE_PLACEHOLDER", THEME_TOGGLE_BUTTON)


def render_root_index(parts_map, index) -> str:
    sections = []
    for part_dir in sorted(parts_map.keys()):
        topics = [t for t in parts_map[part_dir] if _visible(t, AUDIENCE)]
        if not topics:
            continue
        label = _part_label(part_dir)
        nn = part_dir.split("-", 1)[0]
        sections.append(f'<!-- part {escape(nn)} ({escape(part_dir)}) -->')
        sections.append(f'<h2 id="part-{escape(part_dir)}">{escape(label)} '
                        f'<a class="part-videos-link" href="videos/{escape(part_dir)}/">🎬 videos</a></h2>')
        sections.append("<ul>")
        for t in topics:
            stem = t["__file_stem"]
            ttl = t.get("title", t.get("id", "?"))
            sub = t.get("subtitle", "")
            ttl_html = render_inline(ttl, current_part=part_dir, index=index)
            sub_html = render_inline(sub, current_part=part_dir, index=index) if sub else ""
            sections.append(
                f'<li><a href="{part_dir}/{stem}.html">{ttl_html}</a>'
                + (f" — <span class='sub'>{sub_html}</span>" if sub else "")
                + "</li>"
            )
        sections.append("</ul>")
    return ROOT_INDEX.format(
        sections="\n".join(sections),
        footer=_report_footer(prefix=""),
    )


# -------- videos pages --------------------------------------------------- #

VIDEOS_PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — VimFu Videos</title>
<link rel="icon" type="image/png" href="{prefix}icon.png">
<link rel="stylesheet" href="{prefix}style.css">
THEME_INIT_PLACEHOLDER
</head><body>
THEME_TOGGLE_PLACEHOLDER
<nav class="topnav">
  <a href="{prefix}index.html">📚 Contents</a>
  &middot; <a href="{videos_root}index.html">🎬 All videos</a>
</nav>
<article>
<h1>{title}</h1>
{intro}
{body}
</article>
{footer}
<script>
(function(){{
  var current = null;
  document.addEventListener('click', function(e){{
    var t = e.target.closest && e.target.closest('a.video-thumb[data-video-id]');
    if (!t) return;
    e.preventDefault();
    var id = t.getAttribute('data-video-id');
    var f = document.createElement('iframe');
    f.className = 'lesson-iframe';
    f.src = 'https://www.youtube-nocookie.com/embed/' + id + '?autoplay=1&rel=0&playsinline=1&modestbranding=1';
    f.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
    f.setAttribute('allowfullscreen','');
    f._origThumb = t;
    if (current && current.parentNode) {{
      current.parentNode.replaceChild(current._origThumb, current);
    }}
    t.replaceWith(f);
    current = f;
  }});
}})();
</script>
</body></html>
""".replace("THEME_INIT_PLACEHOLDER", THEME_INIT_SCRIPT).replace("THEME_TOGGLE_PLACEHOLDER", THEME_TOGGLE_BUTTON)


def _video_card(v: dict, topic_link_html: str = "") -> str:
    """Render one video as a list item (thumbnail + title + meta)."""
    disp = v.get("display_id") or (
        f"{v['lesson']:04d}" if isinstance(v.get("lesson"), int) else str(v.get("lesson", "?"))
    )
    title = escape(v["title"])
    if v.get("videoId"):
        vid = escape(v["videoId"])
        thumb = (f'<a href="{escape(v["url"])}" target="_blank" rel="noopener" '
                 f'class="video-thumb" data-video-id="{vid}" aria-label="Play video">'
                 f'<img loading="lazy" alt="" width="480" height="360" '
                 f'src="https://i.ytimg.com/vi/{vid}/hqdefault.jpg">'
                 f'<span class="video-play" aria-hidden="true">▶</span></a>')
        link = (f'<a href="{escape(v["url"])}" target="_blank" rel="noopener">'
                f'{title}</a>')
        body = f'{thumb}<div class="video-meta"><span class="video-num">#{escape(disp)}</span> {link}'
        if topic_link_html:
            body += f'<div class="video-topic">{topic_link_html}</div>'
        body += '</div>'
        return f'<li class="video-card">{body}</li>'
    body = (f'<div class="video-thumb video-thumb-pending">📺</div>'
            f'<div class="video-meta"><span class="video-num">#{escape(disp)}</span> '
            f'<span class="video-pending-title">{title}</span>'
            f'<div class="video-pending">(not yet published)</div></div>')
    return f'<li class="video-card video-card-pending">{body}</li>'


def _build_lesson_backlinks(parts_map: dict) -> dict[int, tuple[str, str, str]]:
    """Map lesson# → (part_dir, topic_stem, topic_title) of the first topic
    that references it."""
    back: dict[int, tuple[str, str, str]] = {}
    for part_dir in sorted(parts_map.keys()):
        for t in parts_map[part_dir]:
            if not _visible(t, AUDIENCE):
                continue
            stem = t["__file_stem"]
            ttl = t.get("title", stem)
            for n in (t.get("lessons") or []):
                try:
                    n = int(n)
                except (TypeError, ValueError):
                    continue
                back.setdefault(n, (part_dir, stem, ttl))
    return back


def render_part_videos_page(part_dir: str, lessons: list[int],
                            backlinks: dict) -> str:
    label = _part_label(part_dir)
    vids = []
    for n in lessons:
        v = video_for_lesson(n)
        if v is None:
            continue
        vids.append(v)
    # Stable order by lesson number.
    vids.sort(key=lambda v: v["display_id"])
    items = []
    for v in vids:
        bl = backlinks.get(v["lesson"])
        topic_html = ""
        if bl:
            pd, stem, ttl = bl
            topic_html = (f'from <a href="../../{escape(pd)}/{escape(stem)}.html">'
                          f'{escape(ttl)}</a>')
        items.append(_video_card(v, topic_html))
    if items:
        body = '<ul class="video-grid">' + "".join(items) + '</ul>'
    else:
        body = '<p class="muted">No videos for this part yet.</p>'
    intro = (f'<p class="tagline">Every video referenced from the '
             f'<em>{escape(label)}</em> part of the book. '
             f'See also the <a href="../index.html">complete video index</a>.</p>')
    return VIDEOS_PAGE.format(
        title=f"{escape(label)} videos",
        prefix="../../",
        videos_root="../",
        intro=intro,
        body=body,
        footer=_report_footer(prefix="../../"),
    )


def render_master_videos_page(parts_map: dict, backlinks: dict) -> str:
    idx = _videos_index()
    # Numeric lessons referenced from topic JSONs.
    by_part: dict[str, list] = {}
    for part_dir in sorted(parts_map.keys()):
        for t in parts_map[part_dir]:
            if not _visible(t, AUDIENCE):
                continue
            for n in (t.get("lessons") or []):
                try:
                    n = int(n)
                except (TypeError, ValueError):
                    continue
                if n in idx:
                    by_part.setdefault(part_dir, []).append(n)
    # Letter-suffixed sub-lessons (e.g. 0430a, 0531b) follow their numeric
    # parent's part assignment if the parent is referenced anywhere.
    parent_part: dict[int, str] = {}
    for part_dir, lst in by_part.items():
        for n in lst:
            parent_part.setdefault(n, part_dir)
    for key, v in idx.items():
        if isinstance(key, str) and v.get("suffix"):
            pd = parent_part.get(v["num"])
            if pd:
                by_part.setdefault(pd, []).append(key)
    assigned = {n for lst in by_part.values() for n in lst}
    orphans = [k for k in idx.keys() if k not in assigned]

    def _sortkey(k):
        return idx[k]["display_id"]

    sections = []
    for part_dir in sorted(by_part.keys()):
        label = _part_label(part_dir)
        lessons = sorted(set(by_part[part_dir]), key=_sortkey)
        sections.append(f'<h2 id="part-{escape(part_dir)}">'
                        f'<a href="{escape(part_dir)}/index.html">{escape(label)}</a> '
                        f'<span class="part-count">({len(lessons)})</span></h2>')
        items = []
        for n in lessons:
            v = idx[n]
            bl = backlinks.get(n) or (
                backlinks.get(v["num"]) if isinstance(n, str) and v.get("suffix") else None
            )
            topic_html = ""
            if bl:
                pd, stem, ttl = bl
                topic_html = (f'from <a href="../{escape(pd)}/{escape(stem)}.html">'
                              f'{escape(ttl)}</a>')
            items.append(_video_card(v, topic_html))
        sections.append('<ul class="video-grid">' + "".join(items) + '</ul>')

    if orphans:
        orphans = sorted(orphans, key=_sortkey)
        pub_o = [n for n in orphans if idx[n]["published"]]
        unpub_o = [n for n in orphans if not idx[n]["published"]]
        sections.append('<h2 id="unassigned">More videos '
                        f'<span class="part-count">({len(orphans)})</span></h2>')
        sections.append('<p class="muted">Videos that aren\'t yet linked from a '
                        'specific chapter — but they\'re here, watchable, and '
                        'searchable.</p>')
        if pub_o:
            sections.append('<h3>Published</h3>')
            sections.append('<ul class="video-grid">' +
                            "".join(_video_card(idx[n]) for n in pub_o) +
                            '</ul>')
        if unpub_o:
            sections.append('<h3>In production</h3>')
            sections.append('<ul class="video-grid">' +
                            "".join(_video_card(idx[n]) for n in unpub_o) +
                            '</ul>')

    total = len(idx)
    published = sum(1 for v in idx.values() if v["published"])
    intro = (f'<p class="tagline">All {total} VimFu videos &mdash; '
             f'{published} published, {total - published} in production. '
             f'Grouped by the part of the book that references them.</p>')
    return VIDEOS_PAGE.format(
        title="All Videos",
        prefix="../",
        videos_root="",
        intro=intro,
        body="\n".join(sections),
        footer=_report_footer(prefix="../"),
    )


# -------- stylesheet ------------------------------------------------------ #

STYLE_CSS = """:root {
  --fg: #1a1a1a;
  --muted: #555;
  --bg: #fafafa;
  --bg-elev: #ffffff;
  --accent: #800000;
  --accent-hover: #a00000;
  --accent-soft: #fbe8e8;
  --accent-border: #e6c0c0;
  --code-bg: #f0f0f0;
  --kbd-bg: #fff;
  --kbd-border: #999;
  --kbd-fg: #1a1a1a;
  --panel: #f6f6f0;
  --tip-bg: #fff8d0;
  --tip-border: #cc0;
  --internals-bg: #eef2f8;
  --internals-border: #69b;
  --internals-fg: #246;
  --anecdote-bg: #fbf6ec;
  --anecdote-border: #a8884a;
  --anecdote-fg: #6a4a14;
  --qr-bg: #f6efef;
  --qr-fg: #4a1414;
  --buy-bg: #fff0e0;
  --buy-border: #c80;
  --example-bg: #fbf5f5;
  --example-border: #e6c0c0;
  --example-fg: #4a1414;
  --rule: #e5e5e5;
  --rule-strong: #ddd;
  --table-head: #efefef;
  --summary-bg: #fbf2f2;
  --summary-fg: #4a1414;
  --pager-hover-bg: #fbe8e8;
  --pager-hover-border: #e6c0c0;
  --broken: #a33;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --fg: #e6e6e6;
    --muted: #9aa0a6;
    --bg: #14161b;
    --bg-elev: #1c1f26;
    --accent: #e07070;
    --accent-hover: #ff8c8c;
    --accent-soft: #2a1818;
    --accent-border: #5a2828;
    --code-bg: #22262d;
    --kbd-bg: #2a2e36;
    --kbd-border: #555;
    --kbd-fg: #e6e6e6;
    --panel: #1c1f26;
    --tip-bg: #2c2a18;
    --tip-border: #b8a83a;
    --internals-bg: #18222e;
    --internals-border: #4a7aa0;
    --internals-fg: #aac6e0;
    --anecdote-bg: #2a2418;
    --anecdote-border: #a8884a;
    --anecdote-fg: #d8c08a;
    --qr-bg: #2a1818;
    --qr-fg: #d8a0a0;
    --buy-bg: #2c2418;
    --buy-border: #a87830;
    --example-bg: #1f1818;
    --example-border: #5a2828;
    --example-fg: #d8a0a0;
    --rule: #2a2e36;
    --rule-strong: #3a3e46;
    --table-head: #22262d;
    --summary-bg: #2a1818;
    --summary-fg: #e8b8b8;
    --pager-hover-bg: #2a1818;
    --pager-hover-border: #5a2828;
    --broken: #d88;
  }
}
:root[data-theme="dark"] {
  --fg: #e6e6e6;
  --muted: #9aa0a6;
  --bg: #14161b;
  --bg-elev: #1c1f26;
  --accent: #e07070;
  --accent-hover: #ff8c8c;
  --accent-soft: #2a1818;
  --accent-border: #5a2828;
  --code-bg: #22262d;
  --kbd-bg: #2a2e36;
  --kbd-border: #555;
  --kbd-fg: #e6e6e6;
  --panel: #1c1f26;
  --tip-bg: #2c2a18;
  --tip-border: #b8a83a;
  --internals-bg: #18222e;
  --internals-border: #4a7aa0;
  --internals-fg: #aac6e0;
  --anecdote-bg: #2a2418;
  --anecdote-border: #a8884a;
  --anecdote-fg: #d8c08a;
  --qr-bg: #2a1818;
  --qr-fg: #d8a0a0;
  --buy-bg: #2c2418;
  --buy-border: #a87830;
  --example-bg: #1f1818;
  --example-border: #5a2828;
  --example-fg: #d8a0a0;
  --rule: #2a2e36;
  --rule-strong: #3a3e46;
  --table-head: #22262d;
  --summary-bg: #2a1818;
  --summary-fg: #e8b8b8;
  --pager-hover-bg: #2a1818;
  --pager-hover-border: #5a2828;
  --broken: #d88;
}
button#theme-toggle {
  position: fixed; top: 10px; right: 10px; z-index: 1000;
  width: 36px; height: 36px; padding: 0;
  border: 1px solid var(--rule-strong); border-radius: 50%;
  background: var(--bg-elev); color: var(--fg);
  font-size: 1.05rem; line-height: 1; cursor: pointer;
  box-shadow: 0 1px 3px rgba(0,0,0,0.15);
  transition: transform 0.15s ease, background 0.2s ease;
}
button#theme-toggle:hover {
  background: var(--accent-soft); border-color: var(--accent-border);
  transform: scale(1.05);
}
button#theme-toggle:focus-visible {
  outline: 2px solid var(--accent); outline-offset: 2px;
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

a.practice-link {
  display: inline-block; background: var(--accent); color: #fff;
  padding: 4px 14px; border-radius: 4px; font-weight: 600;
  text-decoration: none;
}
a.practice-link:hover { background: var(--accent-hover); text-decoration: none; }
p.example-try {
  margin: 0.6rem 0 0; text-align: right; font-size: 0.92rem;
}
p.tagline {
  color: var(--muted); font-size: 1.1rem; margin: -0.4rem 0 1.6rem;
  font-style: italic;
}
section.hero {
  background: var(--accent-soft); border: 1px solid var(--accent-border);
  padding: 1rem 1.2rem; border-radius: 6px; margin: 0 0 2rem;
}
section.hero p { margin: 0.6rem 0; }
section.hero p:first-child { margin-top: 0; }
section.hero p:last-child { margin-bottom: 0; }
p.hero-cta { margin-top: 1rem !important; display: flex; align-items: center; gap: 0.8rem; flex-wrap: wrap; }
p.hero-cta .hero-aside { color: var(--muted); font-size: 0.92rem; }
h2.contents-heading { margin-top: 1.5rem; }
nav.pager {
  max-width: 760px; margin: 0.5rem auto; padding: 0.6rem 1.25rem;
  display: grid; grid-template-columns: 1fr auto 1fr;
  align-items: center; gap: 0.8rem;
  font-size: 0.92rem;
  border-top: 1px solid var(--rule); border-bottom: 1px solid var(--rule);
}
nav.pager .pager-prev { text-align: left; }
nav.pager .pager-next { text-align: right; }
nav.pager .pager-pos  { color: var(--muted); font-variant-numeric: tabular-nums; }
nav.pager .pager-link {
  display: inline-block; padding: 4px 10px; border-radius: 4px;
  text-decoration: none; color: var(--accent);
  border: 1px solid transparent;
}
nav.pager .pager-link:hover { background: var(--pager-hover-bg); border-color: var(--pager-hover-border); text-decoration: none; }
nav.pager .pager-disabled { color: var(--muted); opacity: 0.5; font-style: italic; }
nav.pager.pager-bottom { margin-top: 2rem; }

footer.site-footer {
  margin: 3rem 0 1rem;
  padding: 0.8rem 0 0;
  border-top: 1px solid var(--rule);
  color: var(--muted);
  font-size: 0.85rem;
  text-align: center;
}
footer.site-footer a { color: var(--muted); }

h1 { font-size: 2rem; margin: 0.4rem 0 0.2rem; }
h2 { font-size: 1.4rem; margin: 1.8rem 0 0.6rem; border-bottom: 1px solid var(--rule-strong); padding-bottom: 0.3rem; }
h3 { font-size: 1.15rem; margin: 1.4rem 0 0.4rem; }
p.subtitle { color: var(--muted); font-size: 1.1rem; margin-top: 0; font-style: italic; }
p.booktitle-sub { color: var(--muted); font-size: 1.25rem; margin: 0 0 0.8rem; font-style: italic; font-weight: 500; letter-spacing: 0.01em; }
.site-banner { margin: 0 0 0.6rem; padding: 0; line-height: 0; font-size: 0; }
.site-banner img { display: block; width: 100%; max-width: 720px; height: auto; margin: 0 auto; }
.site-banner .banner-dark { display: none; }
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) .site-banner .banner-light { display: none; }
  :root:not([data-theme="light"]) .site-banner .banner-dark  { display: block; }
}
:root[data-theme="dark"] .site-banner .banner-light { display: none; }
:root[data-theme="dark"] .site-banner .banner-dark  { display: block; }
:root[data-theme="light"] .site-banner .banner-light { display: block; }
:root[data-theme="light"] .site-banner .banner-dark  { display: none; }
p.meta { color: var(--muted); font-size: 0.9rem; }

a { color: var(--accent); }
a:hover { color: var(--accent-hover); }
a.broken, span.broken { color: var(--broken); text-decoration: line-through dotted; }

code {
  background: var(--code-bg); padding: 1px 5px; border-radius: 3px;
  font: 0.9em ui-monospace, "Fira Code", Consolas, monospace;
}
pre {
  background: var(--code-bg); padding: 0.7rem 0.9rem; border-radius: 5px;
  overflow-x: auto; margin: 0.8rem 0;
  border-left: 3px solid var(--rule-strong);
}
pre code { background: transparent; padding: 0; font-size: 0.9rem; }
kbd {
  background: var(--kbd-bg); border: 1px solid var(--kbd-border);
  border-bottom-width: 2px; border-radius: 4px;
  padding: 0 5px; font: 0.85em ui-monospace, Consolas, monospace;
  color: var(--kbd-fg);
  white-space: nowrap;
}
/* Keycaps that appear inside a link or heading inherit the link/heading color
   instead of the high-contrast white-on-gray default — this keeps the title
   visually unified rather than spotted with neutral chips. */
a kbd, h1 kbd, h2 kbd, h3 kbd, h4 kbd, .subtitle kbd {
  background: transparent; color: inherit;
  border-color: currentColor;
  border-bottom-width: 1px;
  text-decoration: none;
}
a kbd { display: inline-block; text-decoration: none; }
a:hover kbd { color: inherit; }

blockquote.summary {
  border-left: 3px solid var(--accent); margin: 1rem 0;
  padding: 0.6rem 1rem; background: var(--summary-bg); color: var(--summary-fg);
  font-size: 1.05rem;
}

table {
  border-collapse: collapse; width: 100%; margin: 1rem 0;
  font-size: 0.95rem;
}
th, td { border: 1px solid var(--rule-strong); padding: 0.4rem 0.6rem; text-align: left; vertical-align: top; }
thead th { background: var(--table-head); }

figure.keys, figure.lesson-embed { margin: 1rem 0; }
figure.keys figcaption, figure.lesson-embed figcaption {
  font-style: italic; color: var(--muted); font-size: 0.9rem; margin-bottom: 0.4rem;
}
figure.photo {
  margin: 1.4rem auto; text-align: center; max-width: 100%;
}
figure.photo img {
  max-width: 100%; height: auto; border: 1px solid var(--rule-strong);
  border-radius: 4px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
figure.photo figcaption {
  font-style: italic; color: var(--muted); font-size: 0.9rem;
  margin-top: 0.5rem;
}
figure.photo .credit {
  font-style: normal; font-size: 0.8rem; color: var(--muted);
}
figure.photo .credit::before { content: "— "; }
figure.lesson-embed iframe.lesson-iframe {
  width: 100%; aspect-ratio: 1/1; max-width: 480px; border: 0; border-radius: 6px;
  background: #000; display: block;
}
figure.lesson-embed .placeholder {
  background: #222; color: #fff; padding: 2rem; text-align: center;
  border-radius: 6px; font-size: 1.1rem;
}

aside.tip {
  background: var(--tip-bg); border-left: 4px solid var(--tip-border);
  padding: 0.7rem 1rem; margin: 1rem 0; border-radius: 4px;
}
aside.internals {
  background: var(--internals-bg); border-left: 4px solid var(--internals-border);
  padding: 0.7rem 1rem; margin: 1.2rem 0; border-radius: 4px;
}
aside.internals header {
  font-weight: 600; margin-bottom: 0.4rem; color: var(--internals-fg);
}
aside.internals p { margin: 0.5rem 0; }
aside.internals ul { margin: 0.5rem 0; padding-left: 1.4rem; }
aside.anecdote {
  background: var(--anecdote-bg); border-left: 4px solid var(--anecdote-border);
  padding: 0.7rem 1rem; margin: 1.2rem 0; border-radius: 4px;
  font-style: italic;
}
aside.anecdote header {
  font-weight: 600; margin-bottom: 0.4rem; color: var(--anecdote-fg);
  font-style: normal;
}
aside.anecdote p { margin: 0.5rem 0; }
aside.qr {
  background: var(--qr-bg); padding: 0.4rem 0.8rem; margin: 1rem 0;
  border-radius: 4px; font-size: 0.9rem; color: var(--qr-fg);
  display: flex; align-items: center; gap: 0.8rem;
}
aside.qr img.qr-img { background: #fff; padding: 4px; border-radius: 4px; }
section.watch { margin: 2rem 0; padding-top: 1rem; border-top: 1px solid var(--rule-strong); }
section.watch h2 { margin-top: 0; }
ul.lesson-grid {
  list-style: none; padding: 0; display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 1.2rem;
}
ul.lesson-grid li { display: flex; flex-direction: column; gap: 0.4rem; }
ul.lesson-grid iframe.lesson-iframe {
  width: 100%; aspect-ratio: 1/1; border: 0; border-radius: 6px;
  background: #000; display: block;
}
ul.lesson-grid .lesson-meta { font-size: 0.85rem; color: var(--muted); }
ul.lesson-grid .lesson-pending .placeholder {
  background: var(--code-bg); color: var(--muted); padding: 1.5rem 1rem;
  text-align: center; border-radius: 6px; aspect-ratio: 1/1;
  display: flex; align-items: center; justify-content: center;
}
ul.video-grid {
  list-style: none; padding: 0; margin: 1rem 0 2rem;
  display: grid; gap: 1rem;
  grid-template-columns: repeat(2, 1fr);
}
@media (max-width: 520px) {
  ul.video-grid { grid-template-columns: 1fr; }
}
li.video-card { display: flex; flex-direction: column; gap: 0.4rem; }
li.video-card a.video-thumb {
  display: block; line-height: 0; position: relative;
  border-radius: 4px; overflow: hidden;
}
li.video-card a.video-thumb img {
  width: 100%; aspect-ratio: 1/1; object-fit: cover; border-radius: 4px;
  background: var(--code-bg);
}
li.video-card a.video-thumb .video-play {
  position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
  width: 48px; height: 48px; border-radius: 50%;
  background: rgba(0,0,0,0.65); color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.3rem; padding-left: 4px;
  transition: background 0.15s;
  pointer-events: none;
}
li.video-card a.video-thumb:hover .video-play,
li.video-card a.video-thumb:focus-visible .video-play {
  background: rgba(220,30,30,0.9);
}
li.video-card iframe.lesson-iframe {
  width: 100%; aspect-ratio: 1/1; border: 0; border-radius: 4px;
  background: #000;
}
li.video-card .video-thumb-pending {
  aspect-ratio: 1/1; background: var(--code-bg); color: var(--muted);
  display: flex; align-items: center; justify-content: center; font-size: 2rem;
  border-radius: 4px;
}
li.video-card .video-meta { font-size: 0.9rem; line-height: 1.3; }
li.video-card .video-num {
  font-family: monospace; color: var(--muted); font-size: 0.8rem;
  margin-right: 0.3rem;
}
li.video-card .video-topic, li.video-card .video-pending {
  font-size: 0.8rem; color: var(--muted); margin-top: 0.2rem;
}
li.video-card-pending .video-pending-title { color: var(--muted); }
.part-count { font-weight: normal; color: var(--muted); font-size: 0.85em; }
.part-videos-link {
  font-size: 0.7em; font-weight: normal; color: var(--muted);
  margin-left: 0.4em; text-decoration: none;
}
.part-videos-link:hover { color: var(--accent); text-decoration: underline; }
aside.buy-prompt {
  background: var(--buy-bg); border: 1px dashed var(--buy-border);
  padding: 0.6rem 1rem; margin: 1.5rem 0; border-radius: 4px;
}
aside.buy-prompt a.buy-prompt-link {
  display: flex; align-items: center; gap: 0.9rem;
  color: var(--fg); text-decoration: none;
}
aside.buy-prompt a.buy-prompt-link:hover .buy-prompt-cta { text-decoration: underline; }
aside.buy-prompt .buy-prompt-cover {
  width: 56px; height: auto; flex-shrink: 0; border-radius: 2px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.25);
  border: 1px solid var(--rule);
}
aside.buy-prompt .buy-prompt-text { display: flex; flex-direction: column; gap: 0.1rem; }
aside.buy-prompt .buy-prompt-headline { font-style: italic; color: var(--muted); font-size: 0.95rem; }
aside.buy-prompt .buy-prompt-cta { font-weight: 600; color: var(--accent); font-size: 1.02rem; }

a.hero-book {
  display: flex; align-items: center; gap: 1rem; text-decoration: none;
  background: var(--bg-elev); border: 1px solid var(--accent-border);
  border-radius: 6px; padding: 0.7rem 1rem; margin: 0 0 1rem;
  color: var(--fg);
}
a.hero-book:hover { background: var(--accent-soft); text-decoration: none; }
a.hero-book .hero-book-cover {
  width: 76px; height: auto; flex-shrink: 0; border-radius: 3px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.3);
  border: 1px solid var(--rule);
}
a.hero-book .hero-book-text { display: flex; flex-direction: column; gap: 0.2rem; }
a.hero-book .hero-book-headline { font-weight: 700; font-size: 1.15rem; color: var(--accent); }
a.hero-book .hero-book-sub { color: var(--muted); font-size: 0.92rem; }

section.example {
  margin: 1.6rem 0; padding: 1rem 1.2rem;
  background: var(--example-bg); border: 1px solid var(--example-border); border-radius: 6px;
}
section.example h3.example-title {
  margin: 0 0 0.4rem; font-size: 1.05rem; color: var(--example-fg);
  text-transform: uppercase; letter-spacing: 0.04em;
}
section.example p.example-summary {
  margin: 0 0 1rem; color: var(--example-fg); font-style: italic; opacity: 0.85;
}
figure.example-step {
  margin: 0.8rem 0; padding: 0.6rem; background: var(--bg-elev);
  border-radius: 4px; border: 1px solid var(--example-border);
}
figure.example-step figcaption {
  font-size: 0.95rem; color: var(--fg); margin-bottom: 0.5rem;
}
figure.example-step .step-n {
  display: inline-block; font-weight: 600; color: var(--accent);
  margin-right: 0.5rem;
}
figure.example-step .step-cap { color: var(--fg); }
figure.example-step .screenshot {
  background: #000; border-radius: 4px; padding: 4px;
  display: flex; justify-content: flex-start;
}
figure.example-step .screenshot img {
  width: 100%; max-width: 380px; height: auto; display: block;
}
figure.example-step .screenshot.missing {
  background: var(--accent-soft); color: var(--broken); padding: 1rem; text-align: center;
  font-family: monospace; font-size: 0.9rem;
}
figure.example-step p.narration {
  margin: 0.6rem 0 0; color: var(--muted); font-size: 0.95rem;
}

p.see-also {
  margin-top: 2rem; padding-top: 0.8rem; border-top: 1px solid var(--rule-strong);
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

    # Build a flat web-visible reading order (part_dir, stem, title) for
    # the prev/next pager. Filter audience BEFORE flattening so book-only
    # topics don't appear in the website's pagination.
    ordered: list[tuple[str, str, str]] = []
    for part_dir in sorted(parts_map.keys()):
        for t in parts_map[part_dir]:
            if _visible(t, AUDIENCE):
                ordered.append((part_dir, t["__file_stem"], t.get("title", t["__file_stem"])))

    written = 0
    visible_parts = [p for p in sorted(parts_map.keys())
                     if any(_visible(t, AUDIENCE) for t in parts_map[p])]
    for part_dir, plist in parts_map.items():
        plist = [t for t in plist if _visible(t, AUDIENCE)]
        if not plist:
            continue
        pdir = out_dir / part_dir
        pdir.mkdir(parents=True, exist_ok=True)
        for t in plist:
            (pdir / f"{t['__file_stem']}.html").write_text(
                render_topic_page(t, index, examples, ordered=ordered), encoding="utf-8")
            written += 1
        (pdir / "index.html").write_text(
            render_part_index(part_dir, plist, all_parts=visible_parts), encoding="utf-8")

    (out_dir / "index.html").write_text(render_root_index(parts_map, index), encoding="utf-8")
    (out_dir / "style.css").write_text(STYLE_CSS, encoding="utf-8")

    # Per-part and master video pages at /videos/...
    backlinks = _build_lesson_backlinks(parts_map)
    idx_all = _videos_index()
    # Map: part_dir -> list of lesson keys (ints + suffixed sublessons that
    # inherit their numeric parent's part).
    part_lessons: dict[str, list] = {}
    parent_part: dict[int, str] = {}
    for part_dir, plist in parts_map.items():
        for t in plist:
            if not _visible(t, AUDIENCE):
                continue
            for n in (t.get("lessons") or []):
                try:
                    ni = int(n)
                except (TypeError, ValueError):
                    continue
                part_lessons.setdefault(part_dir, []).append(ni)
                parent_part.setdefault(ni, part_dir)
    for key, v in idx_all.items():
        if isinstance(key, str) and v.get("suffix"):
            pd = parent_part.get(v["num"])
            if pd:
                part_lessons.setdefault(pd, []).append(key)

    videos_dir = out_dir / "videos"
    videos_dir.mkdir(parents=True, exist_ok=True)
    for part_dir in parts_map.keys():
        lessons = part_lessons.get(part_dir, [])
        pvdir = videos_dir / part_dir
        pvdir.mkdir(parents=True, exist_ok=True)
        (pvdir / "index.html").write_text(
            render_part_videos_page(part_dir, list(dict.fromkeys(lessons)), backlinks),
            encoding="utf-8")
    (videos_dir / "index.html").write_text(
        render_master_videos_page(parts_map, backlinks), encoding="utf-8")

    print(f"Wrote {written} topic pages across {len(parts_map)} parts → {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
