"""
Render content/parts/**/*.json topics to LaTeX (.tex) for a self-contained
book PDF. Sister renderer to render_indesign.py --- same content, same audience
filter (``book``), but emitting plain LaTeX you can compile yourself with
pdflatex / xelatex / latexmk (see ``build_pdf.py``) instead of placing
Tagged Text into Adobe InDesign.

Usage:
    python content/render_latex.py
    python content/render_latex.py --out custom/dir

Output layout (under ``content/output/latex`` by default):

    book.tex                        # master file: \\input{...} every part
    preamble.tex                    # all package + style declarations
    parts/<part>/<NN>-<slug>.tex    # per-topic body (no \\documentclass)
    parts/<part>/_part.tex          # \\part{...} + \\input every topic
    README.txt                      # build notes for the human

After rendering, run ``python content/build_pdf.py`` to compile to
``output/latex/book.pdf``.

Inline markup recognised (same vocabulary as the other renderers):
    {key:Esc}              key cap                 → \\key{Esc}
    `code`                 inline code             → \\code{code}
    **strong**             bold                    → \\textbf{...}
    *em*                   italic                  → \\textit{...}
    [label](#topic-id)     cross-ref               → \\hyperref[topic-id]{...}

Block types handled: prose, heading, tip, divider, keys, table, embed,
internals, qr, buy-prompt, example.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from lib.videos import video_for_lesson, videos_for_topic  # noqa: E402
from lib.audience import visible as _visible  # noqa: E402
from lib.qr import qr_svg as _qr_svg  # noqa: E402
from lib.redirects import (  # noqa: E402
    BOOK_SLUG, REPORT_BOOK_ISSUE_SLUG, SIM_TMUX_SLUG,
    errata_slug, part_videos_slug, redirect_url, sim_example_slug, video_slug,
)
from lib.site_config import (  # noqa: E402
    contact_email, current_edition, current_edition_label,
    current_edition_year,
)

AUDIENCE = "book"

PARTS_DIR = ROOT / "parts"
EXAMPLES_DIR = ROOT / "examples"
SCREENSHOTS_DIR = ROOT / "output" / "html" / "screenshots"  # BW + colour live here
QRCODES_DIR = ROOT / "output" / "qrcodes"
REDIRECT_QR_DIR = QRCODES_DIR / "_redirect"
DEFAULT_OUT = ROOT / "output" / "latex"


def _qr_for_slug(slug: str) -> tuple[Path, str]:
    """Return (Path-to-QR-SVG, public-URL) for a redirect ``slug``.

    Every QR in the printed book points at ``vimfubook.com/r/<slug>``
    rather than its raw target. The redirect map (see
    ``content/render_redirects.py``) lets us re-aim a printed QR years
    later when a YouTube URL or topic page moves.
    """
    REDIRECT_QR_DIR.mkdir(parents=True, exist_ok=True)
    url = redirect_url(slug)
    p = REDIRECT_QR_DIR / f"{slug}.svg"
    if not p.exists():
        p.write_text(_qr_svg(url), encoding="utf-8")
    return p, _display_url(url)


def _display_url(url: str) -> str:
    """Strip protocol + ``www.`` for the human-readable form printed beside
    a QR code. The QR itself still encodes the full URL; this is just the
    fallback caption a reader can type if they can't scan."""
    if not url:
        return url
    for prefix in ("https://", "http://"):
        if url.startswith(prefix):
            url = url[len(prefix):]
            break
    if url.startswith("www."):
        url = url[4:]
    return url


# -------- topic loading (mirrors render_indesign.py) --------------------- #

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


# -------- LaTeX escaping ------------------------------------------------- #

# Order matters: backslash first, then everything that contains it.
_TEX_REPLACEMENTS = [
    ("\\", r"\textbackslash{}"),
    ("&", r"\&"),
    ("%", r"\%"),
    ("$", r"\$"),
    ("#", r"\#"),
    ("_", r"\_"),
    ("{", r"\{"),
    ("}", r"\}"),
    ("~", r"\textasciitilde{}"),
    ("^", r"\textasciicircum{}"),
    ("<", r"\textless{}"),
    (">", r"\textgreater{}"),
    ("|", r"\textbar{}"),
]


def tex_escape(s: str) -> str:
    if s is None:
        return ""
    out = s
    for a, b in _TEX_REPLACEMENTS:
        out = out.replace(a, b)
    # Common Unicode dashes / quotes that lmodern's T1 encoding doesn't carry
    # --- convert to their TeX-idiomatic ASCII equivalents.
    out = (out
           .replace("\u2014", "---")    # em-dash
           .replace("\u2013", "--")     # en-dash
           .replace("\u2026", r"\ldots{}")  # ellipsis
           .replace("\u2018", "`")      # left single quote
           .replace("\u2019", "'")      # right single quote
           .replace("\u201C", "``")     # left double quote
           .replace("\u201D", "''"))    # right double quote
    return out


# Verbatim fragments inside arguments are tricky; for ``\code{...}`` and
# ``\key{...}`` we escape but keep the result readable. The custom commands
# in the preamble ultimately render in monospace.
def tex_escape_inline_code(s: str) -> str:
    return tex_escape(s)


# Inline markup tokens (same as render_indesign / render_html)
_KEY_RE   = re.compile(r"\{key:([^}]+)\}")
_LINK_RE  = re.compile(r"\[([^\]]+)\]\(#([^)]+)\)")
_CODE_RE  = re.compile(r"`([^`]+)`")
_STRONG_RE = re.compile(r"\*\*([^*]+)\*\*")
_EM_RE    = re.compile(r"(?<!\*)\*([^*\n]+)\*(?!\*)")

_combined = re.compile(
    r"(?P<key>\{key:[^}]+\})"
    r"|(?P<link>\[[^\]]+\]\(#[^)]+\))"
    r"|(?P<code>`[^`]+`)"
    r"|(?P<strong>\*\*[^*]+\*\*)"
    r"|(?P<em>(?<!\*)\*[^*\n]+\*(?!\*))"
)


def _index_key_entry(k: str) -> str:
    """Build an \\index entry for a key keystroke, sub-grouped under "Keys".

    Uses makeindex's `sort@display` syntax. In the display half we must
    keep raw `{` and `}` balanced from makeindex's point of view, so any
    literal `{`/`}` in the keystroke are rendered with `\\textbraceleft` /
    `\\textbraceright` instead of `\\{` / `\\}`.
    """
    # Sort key: must have balanced braces (LaTeX parses the \index argument).
    # Substitute brace/backslash with ASCII placeholders so they survive both
    # LaTeX tokenisation and makeindex sorting.
    _sort_subst = {"{": "lbrace", "}": "rbrace", "\\": "bslash"}
    sort_key = "".join(_sort_subst.get(c, ('"' + c if c in '!@|"' else c)) for c in k)
    safe_chars = []
    for c in k:
        if c == "{":
            safe_chars.append("\\textbraceleft{}")
        elif c == "}":
            safe_chars.append("\\textbraceright{}")
        elif c == "\\":
            safe_chars.append("\\textbackslash{}")
        elif c == "|":
            safe_chars.append("\\textbar{}")
        elif c in "#$%&_^~":
            safe_chars.append("\\" + c)
        else:
            safe_chars.append(c)
    display = "\\texttt{" + "".join(safe_chars) + "}"
    return f"\\index{{Keys!{sort_key}@{display}}}"


def render_inline(text: str, *, index) -> str:
    if text is None:
        return ""
    out: list[str] = []
    pos = 0
    for m in _combined.finditer(text):
        if m.start() > pos:
            out.append(tex_escape(text[pos:m.start()]))
        kind = m.lastgroup
        raw = m.group(0)
        if kind == "key":
            k = _KEY_RE.match(raw).group(1)
            out.append(f"\\key{{{tex_escape_inline_code(k)}}}{_index_key_entry(k)}")
        elif kind == "link":
            mm = _LINK_RE.match(raw)
            label, tid = mm.group(1), mm.group(2)
            # Print-style cross-reference: "label (p. NN)". The label text is
            # left as plain (non-clickable-looking) prose so the printed page
            # reads naturally; \pageref auto-tracks the actual page number.
            out.append(
                f"{tex_escape(label)}~(p.~\\pageref{{topic:{tex_escape(tid)}}})"
            )
        elif kind == "code":
            inner = _CODE_RE.match(raw).group(1)
            out.append(f"\\code{{{tex_escape_inline_code(inner)}}}")
        elif kind == "strong":
            inner = _STRONG_RE.match(raw).group(1)
            out.append(f"\\textbf{{{render_inline(inner, index=index)}}}")
        elif kind == "em":
            inner = _EM_RE.match(raw).group(1)
            out.append(f"\\textit{{{render_inline(inner, index=index)}}}")
        pos = m.end()
    if pos < len(text):
        out.append(tex_escape(text[pos:]))
    return "".join(out)


# -------- block helpers -------------------------------------------------- #

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


def emit_paragraphs(text: str, *, index) -> list[str]:
    out: list[str] = []
    for kind, chunk in split_fenced(text):
        if kind == "code":
            out.append("\\begin{codeblock}\n" + chunk.rstrip("\n") + "\n\\end{codeblock}")
        else:
            chunk = chunk.strip()
            if chunk:
                # Split on blank lines into paragraphs.
                for para in re.split(r"\n\s*\n", chunk):
                    para = para.strip()
                    if para:
                        out.append(render_inline(para, index=index) + "\n")
    return out


def screenshot_path(ex_id: str, idx: int, theme: str = "bw") -> Path | None:
    """Return absolute path of an existing screenshot, or None."""
    p = SCREENSHOTS_DIR / ex_id / f"frame_{idx:02d}.{theme}.svg"
    return p if p.exists() else None


def latex_path(p: Path) -> str:
    """Return the path of an asset RELATIVE TO the latex output dir
    (which is where book.tex lives), with forward slashes for LaTeX, and
    WITHOUT the ``.svg`` extension so ``\\includegraphics`` picks up the
    pre-converted ``.pdf`` sibling that ``build_pdf.py`` produces."""
    rel = os.path.relpath(p, DEFAULT_OUT).replace("\\", "/")
    if rel.lower().endswith(".svg"):
        rel = rel[:-4]
    return rel


# -------- block rendering ------------------------------------------------ #

def render_block(b, *, index, examples) -> list[str]:
    bt = b.get("type")
    inl = lambda s: render_inline(s, index=index)
    out: list[str] = []

    if bt == "example":
        ex_id = b.get("ref")
        ex = examples.get(ex_id) if ex_id else None
        if not ex:
            out.append(f"\\par\\textit{{[example not found: {tex_escape(str(ex_id))}]}}")
            return out
        out.append("\\begin{example}{" + tex_escape(ex.get("title", ex_id)) + "}")
        if ex.get("summary"):
            out.append("\\examplesummary{" + inl(ex["summary"]) + "}")
        for i, fr in enumerate(ex.get("frames", []), start=1):
            cap = fr.get("caption", "")
            keys = fr.get("keys", "")
            narr = fr.get("narration", "")
            head_bits = [f"\\textbf{{Step {i}}}"]
            if keys:
                head_bits.append(f"\\key{{{tex_escape_inline_code(keys)}}}")
            if cap:
                head_bits.append(inl(cap))
            out.append("\\examplestep{" + " \\,---\\, ".join(head_bits) + "}")
            sp = screenshot_path(ex_id, i, theme="bw")
            if sp is not None:
                out.append("\\examplefigure{" + latex_path(sp) + "}")
            else:
                out.append(
                    f"\\par\\textit{{[missing screenshot {tex_escape(ex_id)}/frame_{i:02d}.bw.svg --- "
                    "run \\texttt{python content/render\\_screenshots.py}]}"
                )
            if narr:
                out.append("\\examplenarration{" + inl(narr) + "}")
        # "Try this in the simulator" QR: scan to load the example's starting
        # buffer in the live web simulator. URL goes through the redirect
        # service so a deployed book can be re-aimed later.
        qr_p, qr_url = _qr_for_slug(sim_example_slug(ex_id))
        out.append(
            "\\qrcallout{" + latex_path(qr_p)
            + "}{Try this in the simulator}{" + tex_escape(qr_url) + "}"
        )
        out.append("\\end{example}")
        return out

    if bt == "heading":
        level = int(b.get("level", 2))
        cmd = "section" if level <= 1 else "subsection" if level == 2 else "subsubsection"
        out.append(f"\\{cmd}*{{{inl(b.get('text', ''))}}}")

    elif bt == "prose":
        out.extend(emit_paragraphs(b.get("text", ""), index=index))

    elif bt == "tip":
        out.append("\\begin{tipbox}\n" + inl(b.get("text", "")) + "\n\\end{tipbox}")

    elif bt == "divider":
        out.append("\\begin{center}\\rule{0.4\\linewidth}{0.4pt}\\end{center}")

    elif bt == "keys":
        if label := b.get("label"):
            out.append("\\par\\textbf{" + inl(label) + "}")
        out.append("\\begin{keytable}")
        for step in b.get("sequence", []):
            if isinstance(step, str):
                key, note = step, ""
            else:
                key = step.get("key", "")
                note = inl(step.get("note", ""))
            key_run = f"\\key{{{tex_escape_inline_code(key)}}}" if key else ""
            if key:
                key_run += _index_key_entry(key)
            out.append(f"  {key_run} & {note} \\\\")
        out.append("\\end{keytable}")

    elif bt == "table":
        headers = b.get("headers", [])
        rows = b.get("rows", [])
        if headers:
            key_cols = set(b.get("keyColumns") or
                           [i for i, h in enumerate(headers)
                            if str(h).strip().lower() in ("key", "keys")])
            n = len(headers)
            # Pin key columns to \keycolwidth so this table aligns with any
            # \begin{keytable} (or other key-column tables) stacked above or
            # below it. Non-key columns stay auto-width.
            non_key_count = max(1, n - len(key_cols))
            cols = []
            for i in range(n):
                if i in key_cols:
                    cols.append("p{\\keycolwidth}")
                else:
                    cols.append(
                        "p{\\dimexpr(\\linewidth-\\keycolwidth*"
                        f"{len(key_cols)})/{non_key_count}-1.2em\\relax}}"
                    )
            spec = "@{}" + "".join(cols) + "@{}"
            out.append("\\par\\begin{longtable}{" + spec + "}")
            out.append(" & ".join(f"\\textbf{{{inl(h)}}}" for h in headers) + " \\\\")
            out.append("\\hline")
            for row in rows:
                cells = list(row) + [""] * (n - len(row))
                rendered = []
                for i, c in enumerate(cells):
                    s = str(c)
                    if i in key_cols and s and "{key:" not in s:
                        s = "{key:" + s + "}"
                    rendered.append(inl(s))
                out.append(" & ".join(rendered) + " \\\\")
            out.append("\\end{longtable}")

    elif bt == "embed":
        lesson = b.get("lesson", "")
        v = video_for_lesson(lesson) if lesson != "" else None
        title = (v["title"] if v else f"Lesson {lesson}")
        # In a print book a video link is useless without a QR. We always
        # encode the redirect URL (vimfubook.com/r/v-NNNN) — the redirect
        # map handles "not yet published" with a coming-soon page, so we
        # don't need a separate fallback path here. We deliberately drop
        # the inline caption: it's almost always the same words as the
        # video title, and the QR title already says "Watch: <title>".
        if isinstance(lesson, int) or (isinstance(lesson, str) and str(lesson).strip().isdigit()):
            qr_p, qr_url = _qr_for_slug(video_slug(int(lesson)))
            out.append(
                "\\qrcallout{" + latex_path(qr_p)
                + "}{Watch: " + tex_escape(title) + "}{" + tex_escape(qr_url) + "}"
            )
        else:
            out.append("\\begin{videocallout}")
            out.append(f"\\textbf{{Watch:}} {tex_escape(title)}")
            out.append("\\end{videocallout}")

    elif bt == "internals":
        title = inl(b.get("title", "Under the Hood"))
        text = b.get("text", "") or ""
        out.append("\\begin{internals}{" + title + "}")
        for chunk in text.split("\n\n"):
            chunk = chunk.rstrip()
            if not chunk:
                continue
            lines = chunk.split("\n")
            stripped = [ln.lstrip() for ln in lines]
            if all(s.startswith("• ") for s in stripped if s):
                out.append("\\begin{itemize}")
                for s in stripped:
                    if s:
                        out.append("  \\item " + inl(s[2:].strip()))
                out.append("\\end{itemize}")
            else:
                out.extend(emit_paragraphs(chunk, index=index))
        out.append("\\end{internals}")

    elif bt == "qr":
        # Per-topic QR codes are website-only — they would point readers at
        # a duplicate of the very page they're reading. The print book uses
        # a single per-part QR (rendered at the end of each part) that
        # points to the videos collection for that part instead.
        return out

    elif bt == "buy-prompt":
        # The PDF *is* the book — drop these callouts entirely.
        return out

    else:
        out.append(f"\\par\\textit{{[unknown block: {tex_escape(str(bt))}]}}")

    return out


# -------- topic body ----------------------------------------------------- #

def render_topic_body(t, index, examples) -> str:
    inl = lambda s: render_inline(s, index=index)
    out: list[str] = []

    title = t.get("title", "(untitled)")
    tid = t.get("id", t["__file_stem"])
    out.append(f"\\chapter{{{inl(title)}}}\\label{{topic:{tex_escape(tid)}}}")
    # Index every key the topic claims to be about (keys[] array on the JSON
    # frontmatter). We deliberately do NOT index the chapter title itself --
    # that would just duplicate the table of contents. The index is for
    # *terms* (keys, modes, concepts) found inside the body.
    for k in (t.get("keys") or []):
        out.append(_index_key_entry(str(k)))

    if sub := t.get("subtitle"):
        out.append("\\par\\textit{" + inl(sub) + "}\\par\\medskip")

    bits = []
    if t.get("id"):
        bits.append(f"\\code{{{tex_escape_inline_code(t['id'])}}}")
    if part := t.get("part"):
        bits.append("part: \\textbf{" + tex_escape(part) + "}")
    if t.get("keys"):
        bits.append("keys: " + ", ".join(
            f"\\key{{{tex_escape_inline_code(k)}}}" for k in t["keys"]))
    if t.get("lessons"):
        bits.append("lessons: " + ", ".join(tex_escape(str(l)) for l in t["lessons"]))
    if bits:
        out.append("\\par\\small{" + " \\,$\\cdot$\\, ".join(bits) + "}\\par\\medskip\\normalsize")

    if summary := t.get("summary"):
        out.append("\\par\\noindent " + inl(summary) + "\\par\\medskip")

    # tmux topics get a "Spin up tmux in the simulator" QR right under the
    # summary — the print page can't show pane splits the way a live tmux
    # session can, so we route readers to the live sim instead.
    if "tmux" in (t.get("__part_dir") or ""):
        qr_p, qr_url = _qr_for_slug(SIM_TMUX_SLUG)
        out.append(
            "\\qrcallout{" + latex_path(qr_p)
            + "}{Spin up tmux in the simulator}{" + tex_escape(qr_url) + "}"
        )

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
        out.append("\\section*{Watch Online}")
        out.append(
            "\\noindent\\small Scan to watch the supporting videos for this "
            "topic.\\normalsize\\par\\medskip"
        )
        for v in vids:
            lesson_n = v.get("lesson")
            title = tex_escape(v.get("title") or f"Lesson {lesson_n}")
            if v.get("published") and lesson_n is not None:
                qr_p, qr_url = _qr_for_slug(video_slug(int(lesson_n)))
                out.append(
                    "\\qrcallout{" + latex_path(qr_p)
                    + "}{Watch: " + title + "}{" + tex_escape(qr_url) + "}"
                )
            else:
                out.append(f"\\par\\noindent\\textit{{{title}}} (coming soon)")

    if see_also := t.get("see_also"):
        labels = []
        for stid in see_also:
            label = index.get(stid, {}).get("title", stid)
            labels.append(
                f"{tex_escape(label)}~(p.~\\pageref{{topic:{tex_escape(stid)}}})"
            )
        out.append("\\par\\medskip\\noindent\\textit{See also:} " + ", ".join(labels))

    return "\n\n".join(out) + "\n"


# -------- preamble ------------------------------------------------------- #

PREAMBLE = r"""% Auto-generated by content/render_latex.py --- do not edit by hand.
\documentclass[11pt,oneside]{book}

\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{fontspec}
% Book-style typography: classic-feel serif body with a clean sans for headings.
% Libertinus is shipped with MiKTeX/TeX Live and is designed as a unified family
% (serif/sans/mono share metrics), giving us a polished, book-like look.
\setmainfont{Libertinus Serif}
\setsansfont{Libertinus Sans}
\setmonofont{Libertinus Mono}
\usepackage[paperwidth=6in,paperheight=9in,margin=0.6in,bindingoffset=0.25in]{geometry}
\usepackage{microtype}
\usepackage{xcolor}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage{imakeidx}
\makeindex[title=Index, columns=2, intoc]
\usepackage{longtable}
\usepackage{fancyvrb}
\usepackage[most]{tcolorbox}
\usepackage{enumitem}
\usepackage{titlesec}
\usepackage{tocloft}
% Numbered parts with Arabic numerals (no Roman); unnumbered chapters/sections
% (titles only -- the TOC carries the page numbers).
\renewcommand{\thepart}{\arabic{part}}
\setcounter{secnumdepth}{-1}
% Widen the TOC page-number column so 3-digit numbers don't collide with titles.
% Chapters/sections aren't numbered, so collapse their number-column gap to 0.
% No numbering anywhere -- titles only. Parts, chapters, sections all unnumbered.
\setcounter{secnumdepth}{-2}
% TOC: collapse all number columns and indent chapters under parts to show
% hierarchy without numbers.
\setlength{\cftchapnumwidth}{0pt}
\setlength{\cftsecnumwidth}{0pt}
\setlength{\cftsubsecnumwidth}{0pt}
\setlength{\cftchapindent}{1.2em}
\setlength{\cftsecindent}{2.4em}
\setlength{\cftsubsecindent}{3.6em}
\cftsetpnumwidth{3em}
\cftsetrmarg{3.5em}
% Render TOC entries in sans, matching the headings in the body.
\renewcommand{\cftpartfont}{\sffamily\bfseries}
\renewcommand{\cftchapfont}{\sffamily}
\renewcommand{\cftsecfont}{\sffamily}
\renewcommand{\cftsubsecfont}{\sffamily}
\renewcommand{\cftpartpagefont}{\sffamily\bfseries}
\renewcommand{\cftchappagefont}{\sffamily}
\renewcommand{\cftsecpagefont}{\sffamily}
\renewcommand{\cftsubsecpagefont}{\sffamily}
% Sans "Contents" heading.
\renewcommand{\cfttoctitlefont}{\sffamily\Huge\bfseries}
% Tighter leading inside chapters; keep visible breathing room before each
% new chapter so the structure reads at a glance.
\setlength{\cftbeforepartskip}{14pt plus 1pt}
\setlength{\cftbeforechapskip}{6pt plus 1pt}
\setlength{\cftbeforesecskip}{1pt}
\setlength{\cftbeforesubsecskip}{1pt}

% Modern typography: single-spacing after periods (no Victorian double-spacing),
% suppress orphans/widows, ragged bottom for even leading.
\frenchspacing
\clubpenalty=10000
\widowpenalty=10000
\displaywidowpenalty=10000
\raggedbottom

\definecolor{accentcolor}{HTML}{2A2A2A}
\definecolor{tipbg}{HTML}{F0F0F0}
\definecolor{tipfg}{HTML}{1A1A1A}
\definecolor{tipborder}{HTML}{6B6B6B}
\definecolor{internalsbg}{HTML}{F0F0F0}
\definecolor{internalsfg}{HTML}{1A1A1A}
\definecolor{internalsborder}{HTML}{4A4A4A}
\definecolor{examplebg}{HTML}{F8F8F8}
\definecolor{exampleborder}{HTML}{B8B8B8}
\definecolor{keybg}{HTML}{F4F4F4}
\definecolor{keyfg}{HTML}{1A1A1A}
\definecolor{keyborder}{HTML}{888888}
\definecolor{codebg}{HTML}{F0F0F0}
\definecolor{figureborder}{HTML}{888888}

\hypersetup{
  colorlinks=true,
  linkcolor=black,
  urlcolor=black,
  citecolor=black,
  pdftitle={VimFu --- The Book},
  pdfauthor={VimFu},
}

% --- Inline key cap ----------------------------------------------------------
% Light keycap: subtle gray fill matching inline code, rounded border, dark
% text. Uniform height via \strut; minimum width so single letters look
% square. Multi-char caps (Esc, Ctrl) widen naturally.
\newlength{\keyminwidth}
\setlength{\keyminwidth}{1.6ex}
\newcommand{\key}[1]{%
  \tikz[baseline=(K.base)]{%
    \node[inner xsep=3pt, inner ysep=1pt,
          minimum width=\keyminwidth, minimum height=1.9ex,
          draw=keyborder, line width=0.5pt,
          fill=keybg, text=keyfg,
          rounded corners=2pt,
          font=\ttfamily\footnotesize]
      (K) {\strut #1};%
  }%
}

% --- Inline code ------------------------------------------------------------
\newcommand{\code}[1]{\colorbox{codebg}{\texttt{#1}}}

% --- Block code -------------------------------------------------------------
\DefineVerbatimEnvironment{codeblock}{Verbatim}{frame=single,framerule=0pt,
  rulecolor=\color{codebg},fontsize=\small,xleftmargin=4pt,xrightmargin=4pt,
  formatcom=\color{black}}

% --- Tip box ----------------------------------------------------------------
\newtcolorbox{tipbox}{enhanced,breakable,colback=tipbg,colframe=tipbg,coltext=tipfg,
  arc=2pt,boxrule=0pt,leftrule=3pt,
  borderline west={2pt}{0pt}{tipborder},
  left=10pt,right=8pt,top=6pt,bottom=6pt}

% --- Internals callout ------------------------------------------------------
\newtcolorbox{internals}[1]{enhanced,breakable,colback=internalsbg,colframe=internalsbg,
  coltext=internalsfg,arc=2pt,boxrule=0pt,leftrule=3pt,
  borderline west={2pt}{0pt}{internalsborder},
  left=10pt,right=8pt,top=6pt,bottom=6pt,
  title={\textbf{Under the Hood --- #1}},coltitle=internalsfg,fonttitle=\bfseries,
  attach title to upper={\par\medskip}}

% --- Worked example callout -------------------------------------------------
\newtcolorbox{example}[1]{enhanced,breakable,colback=examplebg,colframe=exampleborder,
  arc=2pt,boxrule=0.5pt,
  left=10pt,right=8pt,top=6pt,bottom=6pt,
  title={\textbf{Worked Example: #1}},coltitle=black,fonttitle=\bfseries,
  attach title to upper={\par\medskip}}
\newcommand{\examplesummary}[1]{\par\textit{#1}\par\medskip}
\newcommand{\examplestep}[1]{\par\medskip\noindent #1\par}
\newcommand{\examplenarration}[1]{\par\small #1\normalsize\par}
% Screenshot in an example: thin gray border so the white SVG background
% doesn't bleed into the page.
\newcommand{\examplefigure}[1]{%
  \par\medskip\begin{center}%
    \fcolorbox{figureborder}{white}{\includegraphics[width=0.65\linewidth]{#1}}%
  \end{center}\par}

% --- Key-row table ----------------------------------------------------------
% \keycolwidth pins the width of the "key" column across every key/table
% block so consecutive tables on a page line up vertically. Width chosen
% to fit common combos like "Ctrl+W Ctrl+W" rendered as keycaps.
\newlength{\keycolwidth}
\setlength{\keycolwidth}{7.5em}
\newenvironment{keytable}{%
  \par\medskip\begin{tabular}{@{}p{\keycolwidth}@{\hspace{1em}}p{\dimexpr\linewidth-\keycolwidth-2.6em\relax}@{}}}{%
  \end{tabular}\par\medskip}

% --- Video callout ----------------------------------------------------------
\newtcolorbox{videocallout}{enhanced,colback=accentcolor!5,colframe=accentcolor!50,
  arc=2pt,boxrule=0.5pt,
  left=10pt,right=8pt,top=6pt,bottom=6pt}
% --- QR callout -------------------------------------------------------------
% URL is shown as plain monospace text (not a clickable link) — a printed
% page can't be clicked, and the QR code beside it is the real "scan to
% follow" mechanism.
\newcommand{\qrcallout}[3]{%
  \par\medskip\noindent\begin{minipage}[c]{0.18\linewidth}%
    \includegraphics[width=\linewidth]{#1}%
  \end{minipage}\hfill\begin{minipage}[c]{0.78\linewidth}%
    {\sffamily\bfseries #2}\par\smallskip{\footnotesize\sffamily #3}%
  \end{minipage}\par\medskip}

% Slightly tighter chapter heading.
% Chapter heading: ``block`` (not ``hang``) so very long titles wrap onto
% the next line inside the text block instead of running off the right
% margin. Smaller font (LARGE, not Huge) so even unwrapped titles fit on
% a 6x9 page. \raggedright in the title body lets LaTeX break wherever it
% needs to instead of trying to justify a single oversize word.
\titleformat{\chapter}[block]
  {\sffamily\LARGE\bfseries\raggedright}
  {\thechapter\hspace{0.6em}}{0pt}{}
\titlespacing*{\chapter}{0pt}{-12pt}{14pt}
% Section / subsection headings get the same treatment for consistency.
\titleformat{\section}[block]
  {\sffamily\Large\bfseries\raggedright}{\thesection\hspace{0.5em}}{0pt}{}
\titleformat{\subsection}[block]
  {\sffamily\large\bfseries\raggedright}{\thesubsection\hspace{0.5em}}{0pt}{}
% Part page: just the title, no "Part N" label, in sans.
\titleformat{\part}[display]
  {\sffamily\Huge\bfseries\centering}{}{0pt}{}

% TikZ for the \key{} cap — load before the \key{} definition above wouldn't
% help (forward reference), so put the load-and-providecommand-fallback here.
\usepackage{tikz}
\providecommand{\key}[1]{\fbox{\texttt{#1}}}
"""


PART_QR_DIR = QRCODES_DIR / "_parts"
SIM_QR_DIR = QRCODES_DIR / "_sim"


# -------- main ----------------------------------------------------------- #

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
    parts_dir = out_dir / "parts"
    parts_dir.mkdir(exist_ok=True)

    # preamble
    (out_dir / "preamble.tex").write_text(PREAMBLE, encoding="utf-8")

    book_parts: list[str] = []
    for part_dir in sorted(parts_map.keys()):
        plist = [t for t in parts_map[part_dir] if _visible(t, AUDIENCE)]
        if not plist:
            continue
        pdir = parts_dir / part_dir
        pdir.mkdir(parents=True, exist_ok=True)

        part_label = part_dir.split("-", 1)[-1].replace("-", " ").title()
        part_lines: list[str] = [f"\\part{{{tex_escape(part_label)}}}\n"]

        for t in plist:
            body = render_topic_body(t, index, examples)
            (pdir / f"{t['__file_stem']}.tex").write_text(body, encoding="utf-8")
            part_lines.append(
                f"\\input{{parts/{part_dir}/{t['__file_stem']}}}"
            )
            written += 1

        # Per-part trailer: one QR pointing at the videos collection for this
        # part on the website. Encoded via the redirect service so we can
        # re-aim the deployed book if URLs change.
        qr_path, qr_url = _qr_for_slug(part_videos_slug(part_dir))
        part_lines.append("")
        part_lines.append("\\cleardoublepage")
        part_lines.append("\\section*{Watch the videos for this part}")
        part_lines.append(
            "\\noindent Scan to open the video collection that accompanies "
            f"this part of the book---short demos that show the keystrokes in "
            "motion. (See \\textit{About the QR codes} in the front matter for "
            "the full story.)\\par\\medskip"
        )
        part_lines.append(
            "\\qrcallout{" + latex_path(qr_path)
            + "}{Videos: " + tex_escape(part_label) + "}{"
            + tex_escape(qr_url) + "}"
        )

        (pdir / "_part.tex").write_text("\n".join(part_lines) + "\n", encoding="utf-8")
        book_parts.append(f"\\input{{parts/{part_dir}/_part}}")

    # --- Errata QRs (rendered into both front matter and back matter) ----
    edition = current_edition()
    edition_label = current_edition_label()
    edition_year = current_edition_year()
    errata_qr_path, errata_qr_url = _qr_for_slug(errata_slug(edition))
    report_qr_path, report_qr_url = _qr_for_slug(REPORT_BOOK_ISSUE_SLUG)
    edition_string = edition_label + (f", {edition_year}" if edition_year else "")
    errata_qr_callout = (
        "\\qrcallout{" + latex_path(errata_qr_path)
        + "}{Errata for this edition (" + tex_escape(edition_label) + ")}{"
        + tex_escape(errata_qr_url) + "}"
    )
    report_qr_callout = (
        "\\qrcallout{" + latex_path(report_qr_path)
        + "}{Report a problem (email)}{"
        + tex_escape(report_qr_url) + "}"
    )
    # Sample QR for the "About the QR codes" front-matter chapter -- gives the
    # reader something to scan immediately so they know how it works. This one
    # bypasses the /r/ redirect and points straight at the site root: a
    # redirect for "open vimfubook.com" is meaningless (if the domain itself
    # ever moves, every redirect on it is broken anyway).
    REDIRECT_QR_DIR.mkdir(parents=True, exist_ok=True)
    _site_url_full = "https://vimfubook.com/"
    sample_qr_path = REDIRECT_QR_DIR / "_site-direct.svg"
    if not sample_qr_path.exists():
        sample_qr_path.write_text(_qr_svg(_site_url_full), encoding="utf-8")
    sample_qr_callout = (
        "\\qrcallout{" + latex_path(sample_qr_path)
        + "}{Try it: open vimfubook.com}{}"
    )

    book_tex = (
        "\\input{preamble}\n"
        "\\begin{document}\n"
        "\\frontmatter\n"
        "\\title{\\sffamily\\bfseries VimFu}\n"
        "\\author{}\n"
        f"\\date{{\\sffamily {tex_escape(edition_string)}}}\n"
        "\\maketitle\n"
        "\\tableofcontents\n"
        "\\chapter*{About the QR codes}\n"
        "\\addcontentsline{toc}{chapter}{About the QR codes}\n"
        "This book stands on its own---you can read it cover to cover without "
        "ever picking up a phone. Where it earns its place beside the website "
        "is in the videos: short, screen-recorded demos that show every "
        "technique in motion. We can't print video on paper, so each part of "
        "the book ends with a single QR code that opens the collection of "
        "videos for that part on \\texttt{vimfubook.com}. Scan it when you "
        "want to see the keystrokes happen live; otherwise, keep reading.\n\n"
        "Inline embeds (the boxed \\textit{Watch} callouts) point at one "
        "specific clip when a single demo is worth pausing for. Cross-"
        "references to other topics appear as \\textit{(p.~NN)} so you can "
        "flip to them directly---there's a full alphabetical index in the "
        "back of the book as well.\n\n"
        "Every QR in this book points at a short, stable URL on the "
        "domain \\texttt{vimfubook.com} (under the \\texttt{/r/} prefix)---"
        "a redirect we own. That means if a "
        "video moves or a page is restructured we can re-aim the link "
        "without ever invalidating a printed code.\n\n"
        "\\noindent\\textbf{Try one now---this code opens the website:}"
        "\\par\\medskip\n"
        + sample_qr_callout + "\n"
        "\\mainmatter\n"
        + "\n".join(book_parts) + "\n"
        "\\backmatter\n"
        "% --- Errata & corrections ---\n"
        "\\chapter*{Errata \\& corrections}\n"
        "\\addcontentsline{toc}{chapter}{Errata \\& corrections}\n"
        "Books are software too---and software has bugs. We maintain a live "
        f"list of every known error in \\textit{{{tex_escape(edition_label)}}}"
        " on the website. If you spot a typo, a wrong key, a broken example, "
        "an unclear sentence, or anything else worth fixing, please tell us. "
        "Confirmed corrections appear on the errata page and roll into the "
        "next edition.\n\n"
        "\\noindent\\textbf{See known errors for this edition:}\\par\\medskip\n"
        + errata_qr_callout + "\n\n"
        "\\noindent\\textbf{Report a new error:}\\par\\medskip\n"
        + report_qr_callout + "\n\n"
        "Or email us directly at \\texttt{" + tex_escape(contact_email())
        + "}. Please include the page number and a short quote of the "
        "affected text so we can find it quickly.\n\n"
        "\\printindex\n"
        "\\end{document}\n"
    )
    (out_dir / "book.tex").write_text(book_tex, encoding="utf-8")

    (out_dir / "README.txt").write_text(BUILD_NOTES, encoding="utf-8")

    print(f"Wrote {written} topic .tex files across {len(parts_map)} parts → {out_dir}")
    print("  Master:    book.tex")
    print("  Per-part:  parts/<part>/_part.tex")
    print("  Build to PDF: python content/build_pdf.py")
    return 0


BUILD_NOTES = """\
VimFu --- LaTeX export
====================

These are LaTeX (.tex) files. Compile to PDF with:

    python content/build_pdf.py

Or manually with latexmk:

    cd output/latex && latexmk -pdf book.tex

Requirements (install once):
  - A LaTeX distribution (TeX Live, MiKTeX, MacTeX) --- pdflatex/xelatex/latexmk.
  - Inkscape on your PATH --- required by the `svg` package to convert the
    screenshot/QR SVGs into PDF on demand. (Comment out `\\usepackage{svg}`
    in preamble.tex and replace `\\includesvg` with `\\includegraphics` if
    you want to pre-convert the SVGs yourself.)
  - The standard CTAN packages used by preamble.tex: tcolorbox, tikz,
    longtable, hyperref, geometry, microtype, lmodern, enumitem, titlesec,
    fancyvrb, svg, graphicx.

Layout:
    book.tex                       master, \\input every part
    preamble.tex                   document class, packages, custom commands
    parts/<part>/<topic>.tex       individual topic body
    parts/<part>/_part.tex         \\part{} + \\input every topic
"""


if __name__ == "__main__":
    sys.exit(main())

