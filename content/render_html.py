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
from lib.videos import video_for_lesson, videos_for_topic  # noqa: E402
from lib.audience import visible as _visible  # noqa: E402
from lib.site_config import contact_email  # noqa: E402


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
    return urlencode({"v": SIM_LINK_VERSION, "file": "practice.txt", "content": "\n".join(lines) + "\n"})


# Bumping this forces every browser to re-fetch /sim/ instead of using a
# cached copy. Bump whenever sim/index.html's preload semantics change.
SIM_LINK_VERSION = "3"


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
            return urlencode({"v": SIM_LINK_VERSION, "file": "practice.txt", "content": content})
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
        return '<aside class="buy-prompt">📖 Want the full story? <a href="../r/book/">Get the VimFu book.</a></aside>'

    return f"<!-- unknown block type: {escape(str(bt))} -->"


# -------- topic page ------------------------------------------------------ #

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — VimFu</title>
<link rel="icon" type="image/svg+xml" href="{root_index_dir}logo.svg">
<link rel="stylesheet" href="{css}">
</head>
<body>
<nav class="topnav">
  <a href="{root_index}">📚 All Parts</a>
  &middot; <a href="index.html">← {part_label}</a>
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
  <a href="index.html">← back to part</a>
  &middot; <a href="{root_index}">📚 all parts</a>
</nav>
{footer}
</body>
</html>
"""


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
        meta.append("Keys: " + ", ".join(f"<kbd>{escape(k)}</kbd>" for k in keys))
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

    part_label = current_part.split("-", 1)[-1].replace("-", " ").title()
    practice_qs = _practice_query(t, examples)
    prev_link, next_link, pos_label = _pager_links(current_part, t["__file_stem"], ordered or [])
    return PAGE.format(
        title=escape(title),
        css="../style.css",
        root_index="../index.html",
        root_index_dir="../",
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
<link rel="icon" type="image/svg+xml" href="../logo.svg">
<link rel="stylesheet" href="../style.css">
</head><body>
<nav class="topnav"><a href="../index.html">📚 All Parts</a></nav>
<nav class="pager pager-top">
  <span class="pager-prev">{prev_link}</span>
  <span class="pager-pos">{pos_label}</span>
  <span class="pager-next">{next_link}</span>
</nav>
<article>
<h1>{label}</h1>
<ol class="topic-list">
{items}
</ol>
</article>
<nav class="pager pager-bottom">
  <span class="pager-prev">{prev_link}</span>
  <span class="pager-pos">{pos_label}</span>
  <span class="pager-next">{next_link}</span>
</nav>
{footer}
</body></html>
"""


def render_part_index(part_dir, topics_in_part, all_parts=None) -> str:
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

    # Prev / next part links — let part-index pages chain end to end like the
    # topic pages do.
    all_parts = all_parts or []
    idx = next((i for i, p in enumerate(all_parts) if p == part_dir), None)
    prev_link = '<span class="pager-disabled">← start</span>'
    next_link = '<span class="pager-disabled">end →</span>'
    pos_label = ""
    if idx is not None:
        pos_label = f"{idx + 1} / {len(all_parts)}"
        if idx > 0:
            p = all_parts[idx - 1]
            plabel = p.split("-", 1)[-1].replace("-", " ").title()
            prev_link = f'<a class="pager-link" href="../{escape(p)}/index.html" rel="prev">← {escape(plabel)}</a>'
        if idx < len(all_parts) - 1:
            p = all_parts[idx + 1]
            plabel = p.split("-", 1)[-1].replace("-", " ").title()
            next_link = f'<a class="pager-link" href="../{escape(p)}/index.html" rel="next">{escape(plabel)} →</a>'

    return PART_INDEX.format(
        label=escape(label), items="\n".join(items),
        prev_link=prev_link, next_link=next_link, pos_label=escape(pos_label),
        footer=_report_footer(prefix="../"),
    )


ROOT_INDEX = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>VimFu &mdash; The companion site</title>
<link rel="icon" type="image/svg+xml" href="logo.svg">
<link rel="stylesheet" href="style.css">
</head><body>
<article>
<h1>VimFu</h1>
<!-- Auto-generated from content/parts/**/*.json -->
<p class="tagline">The Vim &amp; Neovim reference for programmers &mdash; companion to <a href="r/book/">the book</a>.</p>

<section class="hero">
  <p>This is the <strong>online reference</strong> half of <em>VimFu</em>. Quick to scan, deep-linkable, packed with embedded videos. Every topic in the book has a page here so you can look something up without flipping pages.</p>
  <p>The <a href="r/book/">printed book</a> goes deeper &mdash; history, internals, mental models, and worked examples for every concept. The site is the cheat sheet; the book is the why.</p>
  <p class="hero-cta">
    <a class="practice-link" href="sim/" target="_blank" rel="noopener">▶ Open the simulator</a>
    <span class="hero-aside">An in-browser Neovim + tmux for practicing anything you read here.</span>
  </p>
</section>

<h2 class="contents-heading">Contents</h2>
{sections}
</article>
{footer}
</body></html>
"""


def render_root_index(parts_map) -> str:
    sections = []
    for part_dir in sorted(parts_map.keys()):
        topics = [t for t in parts_map[part_dir] if _visible(t, AUDIENCE)]
        if not topics:
            continue
        label = part_dir.split("-", 1)[-1].replace("-", " ").title()
        nn = part_dir.split("-", 1)[0]
        sections.append(f'<!-- part {escape(nn)} ({escape(part_dir)}) -->')
        sections.append(f'<h2><a href="{part_dir}/index.html">{escape(label)}</a></h2>')
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
    return ROOT_INDEX.format(
        sections="\n".join(sections),
        footer=_report_footer(prefix=""),
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
  :root {
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
aside.buy-prompt {
  background: var(--buy-bg); border: 1px dashed var(--buy-border);
  padding: 0.6rem 1rem; margin: 1.5rem 0; border-radius: 4px;
  text-align: center; font-style: italic;
}

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

    (out_dir / "index.html").write_text(render_root_index(parts_map), encoding="utf-8")
    (out_dir / "style.css").write_text(STYLE_CSS, encoding="utf-8")

    print(f"Wrote {written} topic pages across {len(parts_map)} parts → {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
