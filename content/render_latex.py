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

# Force UTF-8 on stdout/stderr so prints with → / ✓ / … don't crash on a
# default Windows console (cp1252).
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except Exception:
        pass
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

# Single-pass char→token escaping. We MUST NOT use sequential .replace()
# here: e.g. ("\\" → r"\textbackslash{}") followed by ("{" → r"\{") would
# re-escape the braces emitted by the backslash replacement, so a literal
# `\` ends up rendering as `\{}` in the PDF. A single pass over the input
# avoids that double-escape entirely.
_TEX_CHAR_MAP = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
    "<": r"\textless{}",
    ">": r"\textgreater{}",
    "|": r"\textbar{}",
    # Unicode glyphs lmodern's T1 encoding doesn't carry → TeX equivalents.
    "\u2014": "---",          # em-dash
    "\u2013": "--",           # en-dash
    "\u2026": r"\ldots{}",    # ellipsis
    "\u2018": "`",            # left single quote
    "\u2019": "'",            # right single quote
    "\u201C": "``",           # left double quote
    "\u201D": "''",           # right double quote
}


def tex_escape(s: str) -> str:
    if s is None:
        return ""
    return "".join(_TEX_CHAR_MAP.get(c, c) for c in s)


# Verbatim fragments inside arguments are tricky; for ``\code{...}`` and
# ``\key{...}`` we escape but keep the result readable. The custom commands
# in the preamble ultimately render in monospace.
def tex_escape_inline_code(s: str) -> str:
    return tex_escape(s)


# Inline markup tokens (same as render_indesign / render_html)
_KEY_RE   = re.compile(r"\{key:([^}]+|\})\}")
_LINK_RE  = re.compile(r"\[([^\]]+)\]\(#([^)]+)\)")
_CODE_RE  = re.compile(r"`([^`]+)`")
_STRONG_RE = re.compile(r"\*\*([^*]+)\*\*")
_EM_RE    = re.compile(r"(?<!\*)\*([^*\n]+)\*(?!\*)")

_EXTLINK_RE = re.compile(r"\[([^\]]+)\]\((?!#)([^)]+)\)")

_combined = re.compile(
    r"(?P<key>\{key:(?:[^}]+|\})\})"
    r"|(?P<link>\[[^\]]+\]\(#[^)]+\))"
    r"|(?P<extlink>\[[^\]]+\]\((?!#)[^)]+\))"
    r"|(?P<code>`[^`]+`)"
    r"|(?P<strong>\*\*[^*]+\*\*)"
    r"|(?P<em>(?<!\*)\*[^*\n]+\*(?!\*))"
)


# Threshold for splitting a single \code{} fragment on path separators.
# Short fragments (e.g. \code{'fileencoding'}) stay as one pill; long
# fragments (e.g. \code{$VIMRUNTIME/plugin/netrwPlugin.vim}) get split.
_CODE_WRAP_THRESHOLD = 12


def _split_code_for_wrap(s: str) -> str:
    """Render `s` as one or more `\\code{}` pills with natural breakpoints.

    A monolithic `\\code{}` is an unbreakable atomic colorbox, so a long
    inline code run in a narrow context (table cell, tcolorbox interior)
    overflows the right margin — which on a 6x9 KDP paperback means
    crossing into the safety zone or beyond the trim.

    Strategy:
      - Whitespace in the source becomes a literal space (breakable).
      - Long fragments are further split at `/` and `\\` (path separators),
        with the separator kept on the LEFT fragment so paths read
        naturally. Path-internal breakpoints use `\\allowbreak` (no
        visible space) so the path looks unchanged when it fits on one
        line and only wraps when it must.
    """
    out: list[str] = []
    words = s.split(" ")
    for wi, word in enumerate(words):
        if not word:
            # Preserve multiple-space runs in source.
            if wi > 0:
                out.append(" ")
            continue
        if wi > 0:
            out.append(" ")
        if len(word) <= _CODE_WRAP_THRESHOLD:
            out.append(f"\\code{{{tex_escape_inline_code(word)}}}")
            continue
        parts = re.split(r"([/\\])", word)
        if len(parts) <= 1:
            out.append(f"\\code{{{tex_escape_inline_code(word)}}}")
            continue
        # Re-glue separator to preceding fragment; emit each as its own
        # \code{} pill joined by \allowbreak (zero-width breakpoint).
        glued: list[str] = []
        i = 0
        while i < len(parts):
            frag = parts[i]
            if i + 1 < len(parts) and parts[i + 1] in ("/", "\\"):
                frag = frag + parts[i + 1]
                i += 2
            else:
                i += 1
            if frag:
                glued.append(frag)
        out.append(
            "\\allowbreak{}".join(
                f"\\code{{{tex_escape_inline_code(g)}}}" for g in glued
            )
        )
    return "".join(out)


def _split_key_for_wrap(s: str) -> str:
    """Render `s` as one or more `\\key{}` caps with breakpoints.

    `\\key{...}` wraps content in a TikZ node — a single atomic hbox. A long
    argument like ``@nvim hello.txt`` can't break mid-pill, so in narrow
    contexts (keytable cells, the gutter side of a two-column layout) it
    runs off the right margin.

    Whitespace in the source becomes a real space between separate pills,
    giving TeX an obvious breakpoint without changing how the page looks
    when the line fits.

    Multi-letter alpha-only tokens like ``hjkl`` or ``gg`` are split
    into per-character pills — those represent a sequence of separate
    keystrokes, not a single key labelled "hjkl".
    """
    words = s.split(" ")
    # If any split segment is empty, the spaces aren't pill-separators
    # — render the whole token as one pill with `␣` (U+2423) for each
    # literal space so the space character is visible.
    if not s or any(p == "" for p in words):
        body = (s.replace(" ", "\u2423") if s else "\u2423")
        return f"\\key{{{tex_escape_inline_code(body)}}}"
    if len(words) > 1:
        pills: list[str] = []
        for w in words:
            if not w:
                continue
            pills.append(_split_key_for_wrap(w))
        return " ".join(pills)
    # Single token: see if it's a sequence of plain letters that should
    # render as separate pills. Skip named keys ("Esc", "Tab"), modifier
    # chords ("Ctrl-W"), angle-bracket forms ("<C-W>"), and any token
    # containing punctuation (":wq", "//", "g~").
    if (
        len(s) >= 2
        and s.isascii()
        and s.isalpha()
        and s not in _NAMED_KEYS
        and not _FNKEY_RE.match(s)
        and not _MODIFIER_RE.match(s)
    ):
        pills = [f"\\key{{{tex_escape_inline_code(c)}}}" for c in s]
        # Thin space between adjacent pills so they read as a sequence
        # but stay visually tight.
        return "\\,".join(pills)
    return f"\\key{{{tex_escape_inline_code(s)}}}"


# A whitelist for what counts as an actual Vim key worth indexing under
# "Keys" in the book index. Without this, every `{key:foo}` markup (used
# for typed text like "foo"/"bar" inside example commands) generates a
# bogus "Keys!foo" index entry. We keep the index focused on real keys.
_NAMED_KEYS = {
    "Esc", "Enter", "Return", "Tab", "Space", "BS", "Backspace",
    "CR", "NL", "Nul", "Bar", "Bslash", "Lt", "Gt",
    "Up", "Down", "Left", "Right",
    "Home", "End", "PageUp", "PageDown", "PgUp", "PgDn",
    "Del", "Delete", "Ins", "Insert", "Help", "Undo",
    "Leader", "LocalLeader",
}
_FNKEY_RE = re.compile(r"^F\d{1,2}$")
_MODIFIER_RE = re.compile(
    r"^(?:Ctrl|Alt|Shift|Cmd|Meta|Super)-", re.IGNORECASE
)


def _is_vim_key(k: str) -> bool:
    """Return True if `k` looks like an actual Vim key worth indexing."""
    if not k:
        return False
    # Short tokens (single char like `g`, two-char like `gg`, `:w`, `//`).
    if len(k) <= 2:
        return True
    if k in _NAMED_KEYS:
        return True
    if _FNKEY_RE.match(k):
        return True
    if _MODIFIER_RE.match(k):
        return True
    if k.startswith("<") and k.endswith(">"):
        return True
    # Modifier combos separated by space, e.g. "Ctrl-W Ctrl-W".
    if " " in k and all(
        (not p) or _is_vim_key(p) for p in k.split(" ")
    ):
        return True
    return False


def _index_key_entry(k: str) -> str:
    """Build an \\index entry for a key keystroke, sub-grouped under "Keys".

    Returns an empty string for non-key tokens (e.g. literal text like
    "foo" / "bar" inside example commands) so the index stays focused on
    real Vim keys.

    Uses makeindex's `sort@display` syntax. In the display half we must
    keep raw `{` and `}` balanced from makeindex's point of view, so any
    literal `{`/`}` in the keystroke are rendered with `\\textbraceleft` /
    `\\textbraceright` instead of `\\{` / `\\}`.
    """
    if not _is_vim_key(k):
        return ""
    # Strip control characters (newline, tab, …) from the sort key so they
    # don't end up sorting next to NULs in makeindex's output.
    k_for_sort = "".join(c for c in k if c >= " ")
    # Sort key: must have balanced braces (LaTeX parses the \index argument).
    # Substitute brace/backslash/caret/tilde/etc with ASCII placeholders so
    # they sort sensibly *and* don't survive into the rendered index page
    # as combining accents (\^x / \~x).
    _sort_subst = {
        "{": "lbrace", "}": "rbrace", "\\": "bslash",
        "^": "caret", "~": "tilde", "|": "bar",
        "#": "hash", "%": "percent", "$": "dollar",
        "_": "underscore", "&": "amp",
    }
    sort_key = "".join(
        _sort_subst.get(c, ('"' + c if c in '!@|"' else c))
        for c in k_for_sort
    )
    # Escape each char for inside \key{...}; split on spaces so multi-key
    # sequences (e.g. "Ctrl-W Ctrl-W") render as separate pills with a
    # visible gap, instead of one long unbreakable pill.
    def _esc(c: str) -> str:
        if c == "{": return "\\textbraceleft{}"
        if c == "}": return "\\textbraceright{}"
        if c == "\\": return "\\textbackslash{}"
        if c == "|": return "\\textbar{}"
        if c == "^": return "\\textasciicircum{}"
        if c == "~": return "\\textasciitilde{}"
        if c in "#$%&_": return "\\" + c
        # NUL/Tab/etc. don't have a renderable glyph; if such a char
        # ever sneaks into a key string, substitute the visible-space
        # symbol so the index entry shows SOMETHING rather than a blank
        # pill that points readers at a page number with no caption.
        if c < " ": return "\u2423"
        return c

    # Render display half. Spaces are usually a separator between distinct
    # keystrokes ("Ctrl-W Ctrl-W"), but they can also BE the keystroke
    # (the Space bar) or part of a chord ("Ctrl- " = Ctrl-Space). If any
    # split segment is empty, the spaces aren't separators — render the
    # whole token as a single pill with `\textvisiblespace` for spaces.
    parts = k.split(" ")
    if not k or any(p == "" for p in parts):
        # Single pill: replace every literal space with the visible-space
        # glyph ␣ so the index entry isn't an empty box.
        body = "".join(
            "\u2423" if c == " " else _esc(c)
            for c in (k if k else "\u2423")
        )
        display = "\\protect\\key{" + body + "}"
    else:
        pills: list[str] = []
        for word in parts:
            pills.append("\\protect\\key{" + "".join(_esc(c) for c in word) + "}")
        display = " ".join(pills)
    return f"\\index{{Keys!{sort_key}@{display}}}"


_LONG_KEY_RUN_RE = re.compile(r"(?:\{key:[^{}\s]\} ?){4,}")


def _collapse_long_key_runs(text: str) -> str:
    """Collapse a long string of single-char `{key:X}` markers into a
    single backtick-quoted code span.

    Author shortcut: many topics encode a literal Ex-mode command as
    `{key::}{key:s}{key:e}{key:t} {key:s}{key:p}{key:e}{key:l}{key:l}`
    so each char gets its own pill. That looks awful: a row of 8+
    single-letter boxes for what is really a single command the user
    types. When we see 4 or more single-char key tokens in a row
    (allowing one literal space between them, as the author would
    insert), fold the whole run into ``\\code{...}`` so it renders as
    one ttfamily code block instead.

    Shorter runs are left alone — ``{key:g}{key:g}`` stays as two
    pills; ``{key:c}{key:i}{key:p}`` stays as three pills (those read
    fine as discrete keystrokes).
    """
    def repl(m: re.Match) -> str:
        chunk = m.group(0)
        chars: list[str] = []
        for piece in re.finditer(r"\{key:([^{}])\}( ?)", chunk):
            chars.append(piece.group(1))
            if piece.group(2):
                chars.append(piece.group(2))
        return "`" + "".join(chars).rstrip() + "`"
    return _LONG_KEY_RUN_RE.sub(repl, text)


def render_inline(text: str, *, index, with_key_index: bool = True, plain_keys: bool = False) -> str:
    if text is None:
        return ""
    text = _collapse_long_key_runs(text)
    out: list[str] = []
    pos = 0
    for m in _combined.finditer(text):
        if m.start() > pos:
            out.append(tex_escape(text[pos:m.start()]))
        kind = m.lastgroup
        raw = m.group(0)
        if kind == "key":
            k = _KEY_RE.match(raw).group(1)
            idx = _index_key_entry(k) if with_key_index else ""
            if plain_keys:
                out.append(f"\\texttt{{{tex_escape_inline_code(k)}}}{idx}")
            else:
                out.append(f"{_split_key_for_wrap(k)}{idx}")
        elif kind == "link":
            mm = _LINK_RE.match(raw)
            label, tid = mm.group(1), mm.group(2)
            # Print-style cross-reference: "label (p. NN)". The label text is
            # left as plain (non-clickable-looking) prose so the printed page
            # reads naturally; \pageref auto-tracks the actual page number.
            out.append(
                f"{tex_escape(label)}~(p.~\\pageref{{topic:{tex_escape(tid)}}})"
            )
        elif kind == "extlink":
            # External Markdown link like `[label](https://…)`. The print
            # book routes all live URLs through QR codes elsewhere; for
            # inline prose we just emit the label, dropping the URL so the
            # page doesn't show literal Markdown syntax.
            mm = _EXTLINK_RE.match(raw)
            out.append(render_inline(mm.group(1), index=index))
        elif kind == "code":
            inner = _CODE_RE.match(raw).group(1)
            # Break unbreakable \code{...} runs into per-fragment pills so
            # they can wrap in narrow contexts (table cells, tcolorbox
            # interiors) instead of overflowing the page / KDP safe area.
            # Split on spaces first; then for any still-long fragment,
            # split on path separators (/ and \), keeping the separator
            # attached to the LEFT fragment so paths read naturally.
            out.append(_split_code_for_wrap(inner))
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
                head_bits.append(_split_key_for_wrap(keys))
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
        label = b.get("label")
        sequence = b.get("sequence", [])
        # Decompose to (key, note) pairs.
        pairs = []
        for step in sequence:
            if isinstance(step, str):
                pairs.append((step, ""))
            else:
                pairs.append((step.get("key", ""), inl(step.get("note", ""))))
        has_notes = any(n for _, n in pairs)
        if not has_notes and pairs:
            # No per-step notes — collapse into a single inline run so a
            # sequence like ["r", "x"] or ["3", "r", "-"] reads as one
            # line of pills (with the label as a lead-in), instead of
            # exploding into a row per keystroke.
            key_runs = []
            for k, _ in pairs:
                if not k:
                    continue
                idx = _index_key_entry(k)
                key_runs.append(f"{_split_key_for_wrap(k)}{idx}")
            run = "\\,".join(key_runs)  # thin space between pills
            if label:
                out.append(
                    "\\par\\noindent " + inl(label) + ":\\enspace " + run
                    + "\\par\\medskip"
                )
            else:
                out.append("\\par\\noindent " + run + "\\par\\medskip")
        else:
            if label:
                out.append("\\par\\textbf{" + inl(label) + "}")
            out.append("\\begin{keytable}")
            for key, note in pairs:
                key_run = _split_key_for_wrap(key) if key else ""
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

            # Estimate how wide each key column needs to be (in em) so we
            # don't waste page width on a fixed-size key column. Non-key
            # columns become tabularx X columns: they absorb the rest of
            # \linewidth and wrap their (typically prose) content.
            def _visible_len(s: str) -> int:
                # Strip our content markup so widths reflect rendered text,
                # not raw `{key:...}` / `**bold**` / `_em_` etc. \key pills
                # have a few points of horizontal padding so we round up.
                t = re.sub(r"\{key:([^}]+)\}", r"\1", str(s))
                t = re.sub(r"\*\*([^*]+)\*\*", r"\1", t)
                t = re.sub(r"`([^`]+)`", r"\1", t)
                return len(t)

            key_col_widths = {}
            for i in key_cols:
                longest = max(
                    [_visible_len(headers[i])]
                    + [_visible_len(row[i]) if i < len(row) else 0
                       for row in rows]
                )
                # ~0.7em per char (ttfamily + pill padding); clamp 3..14em.
                em = max(3.0, min(14.0, longest * 0.7 + 1.0))
                key_col_widths[i] = em

            cols = []
            for i in range(n):
                if i in key_cols:
                    cols.append(
                        "@{}>{\\raggedright\\sloppy\\arraybackslash}"
                        f"p{{{key_col_widths[i]:.1f}em}}@{{}}"
                    )
                else:
                    cols.append(
                        "@{\\hspace{1em}}>{\\raggedright\\sloppy"
                        "\\arraybackslash}X"
                    )
            # If there is NO X column (all columns are keys), fall back to
            # a plain longtable so we don't ask tabularx to handle a row
            # with no expanding column.
            has_x = any(i not in key_cols for i in range(n))
            spec = "".join(cols)
            if has_x:
                out.append(
                    "\\par\\begin{tabularx}{\\linewidth}{" + spec + "}"
                )
            else:
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
            out.append("\\end{tabularx}" if has_x else "\\end{longtable}")

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

    elif bt == "anecdote":
        title = inl(b.get("title", ""))
        text = b.get("text", "") or ""
        title_arg = title if title else ""
        out.append("\\begin{anecdote}{" + title_arg + "}")
        for chunk in text.split("\n\n"):
            chunk = chunk.rstrip()
            if not chunk:
                continue
            out.extend(emit_paragraphs(chunk, index=index))
        out.append("\\end{anecdote}")

    elif bt == "qr":
        # Per-topic QR codes (those that only specify a `topic` id) are
        # website-only — they would point readers at a duplicate of the
        # page they're reading. But an explicit `slug` (or one-off `url`)
        # is different: it points at external content the reader can't
        # reach from the current page. Emit a real QR for those.
        slug = b.get("slug")
        caption = b.get("caption") or ""
        if slug:
            qr_p, qr_url = _qr_for_slug(str(slug))
            cap = tex_escape(caption) if caption else "Scan to open"
            out.append(
                "\\qrcallout{" + latex_path(qr_p)
                + "}{" + cap + "}{" + tex_escape(qr_url) + "}"
            )
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
    # Chapter title: render keys as plain-text (\texttt) rather than TikZ
    # pills. TikZ \key{} inside \chapter{...} blows up hyperref's PDF
    # bookmark generation ("TeX capacity exceeded - parameter stack size")
    # because the title also goes into the .toc, .aux, running headers,
    # AND PDF bookmark strings. Body-level <h1> headings authored inside
    # blocks still get full key pills.
    out.append(f"\\chapter{{{render_inline(title, index=index, with_key_index=False, plain_keys=True)}}}\\label{{topic:{tex_escape(tid)}}}")
    # Index every key the topic claims to be about (keys[] array on the JSON
    # frontmatter). We deliberately do NOT index the chapter title itself --
    # that would just duplicate the table of contents. The index is for
    # *terms* (keys, modes, concepts) found inside the body.
    for k in (t.get("keys") or []):
        out.append(_index_key_entry(str(k)))

    if sub := t.get("subtitle"):
        out.append("\\par\\textit{" + inl(sub) + "}\\par\\medskip")

    # NOTE: We deliberately do NOT emit a metadata line here (topic id,
    # part, keys list, lesson numbers). Those fields are useful on the
    # website (cross-references, lesson links) but look like internal
    # designations leaking into the print book. The "keys" covered in a
    # topic still get indexed via _index_key_entry() above, so the back
    # of book has them; here we go straight from subtitle to summary.

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

    # Normalize title and level-1 heading text by stripping {key:...}
    # wrappers so titles authored with key-markup like "{key:*}, {key:cw}"
    # still match a body heading authored as plain "*, cw, …".
    _norm_title = re.sub(r"\{key:([^}]+)\}", r"\1", title).strip()

    for b in t.get("blocks", []):
        if not _visible(b, AUDIENCE):
            continue
        if b.get("type") == "heading" and int(b.get("level", 2)) == 1:
            heading_text = re.sub(r"\{key:([^}]+)\}", r"\1",
                                  b.get("text", "")).strip()
            if heading_text == _norm_title:
                continue
        out.extend(render_block(b, index=index, examples=examples))

    vids = videos_for_topic(t)
    embedded_lessons = {b.get("lesson") for b in (t.get("blocks") or [])
                        if b.get("type") == "embed" and b.get("lesson") is not None}
    vids = [v for v in vids if v["lesson"] not in embedded_lessons]
    if vids:
        # Hide videos that aren't actually published yet. Two signals indicate
        # "not yet available": missing `published` flag, or a title that
        # literally announces "(coming soon)". Either one is treated as
        # invisible in the print book — readers don't need placeholders.
        def _hidden(v):
            t = (v.get("title") or "")
            if not v.get("published"):
                return True
            if "(coming soon)" in t.lower():
                return True
            return False
        vids = [v for v in vids if not _hidden(v)]
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
                # Defensive: should never reach here given the filter above.
                continue

    if see_also := t.get("see_also"):
        labels = []
        for stid in see_also:
            label = index.get(stid, {}).get("title", stid)
            # Titles may contain `{key:X}` markup which must render as
            # actual pills (or plain text), not literal braces. We turn
            # off key indexing so cross-references don't fabricate index
            # entries for keys that aren't actually used on this page.
            label_tex = render_inline(label, index=index,
                                      with_key_index=False)
            labels.append(
                f"{label_tex}~(p.~\\pageref{{topic:{tex_escape(stid)}}})"
            )
        out.append("\\par\\medskip\\noindent\\textit{See also:} " + ", ".join(labels))

    return "\n\n".join(out) + "\n"


# -------- preamble ------------------------------------------------------- #

PREAMBLE = r"""% Auto-generated by content/render_latex.py --- do not edit by hand.
% twoside: mirror inner/outer margins so the spine-side (inner) margin
% alternates correctly between odd and even pages. Required for a properly
% bound print book (e.g. KDP paperback).
% openany: don't force chapters onto right-hand (recto) pages with blank
% versos between them. The book has many short chapters; forcing recto-start
% would inflate the page count noticeably with little reader benefit.
\documentclass[11pt,twoside,openany]{book}

\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{fontspec}
% Force xelatex to emit /ActualText markup for every glyph so extracted text
% (KDP preflight, accessibility tools, copy/paste) sees the real Unicode
% regardless of the font's ToUnicode CMap. Libertinus's CMap maps several
% glyph IDs to C0 control chars (U+0007, U+0009, U+001A, U+001B, U+001D) for
% stylistic/ligature glyphs xdvipdfmx couldn't reverse-map; without
% ActualText, KDP strips those pages with "non-printable markup removed".
\XeTeXgenerateactualtext=1
% Book-style typography: classic-feel serif body with a clean sans for headings.
% Libertinus is shipped with MiKTeX/TeX Live and is designed as a unified family
% (serif/sans/mono share metrics), giving us a polished, book-like look.
\setmainfont{Libertinus Serif}
\setsansfont{Libertinus Sans}
\setmonofont{Libertinus Mono}
% KDP paperback 7.5x9.25, ~301-500 page bucket at this larger trim:
% inside >= 0.625", outside/top/bottom >= 0.25". We use generous values.
%   inner  (spine side):    0.875"
%   outer (fore edge):      0.625"
%   top / bottom:           0.75"
% bindingoffset is intentionally omitted: with twoside + inner/outer geometry,
% the inner margin already provides the spine allowance and mirrors correctly.
\usepackage[
  paperwidth=7.5in, paperheight=9.25in,
  inner=0.875in, outer=0.625in,
  top=0.75in, bottom=0.75in,
  headsep=14pt, footskip=28pt
]{geometry}
\usepackage{microtype}
\usepackage{xcolor}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage{imakeidx}
\makeindex[title=Index, columns=2, intoc]
\usepackage{longtable}
\usepackage{tabularx}
\usepackage{ltablex} % longtable + tabularx: X columns that page-break
\keepXColumns       % preserve X behaviour inside tabularx after ltablex hijacks it
\usepackage{array}  % \arraybackslash, advanced column specs
\usepackage{amssymb}  % \checkmark, used by newunicodechar mapping below
\usepackage{newunicodechar}
% Libertinus Serif lacks the U+2713 CHECK MARK glyph. Without a mapping,
% XeLaTeX silently emits a missing-glyph placeholder that downstream PDF
% consumers (e.g. KDP's pre-print validation) flag as a non-printable
% character. Map it to the math \checkmark, which renders cleanly.
\newunicodechar{✓}{\ensuremath{\checkmark}}
\usepackage{fvextra}
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
% Dotted leader lines between TOC entry text and page number. Default
% LaTeX gives chapters no leader at all; here every level gets light
% dots so the reader's eye can follow across the wider trim size.
\renewcommand{\cftpartleader}{\cftdotfill{\cftdotsep}}
\renewcommand{\cftchapleader}{\cftdotfill{\cftdotsep}}
\renewcommand{\cftsecleader}{\cftdotfill{\cftdotsep}}
\renewcommand{\cftsubsecleader}{\cftdotfill{\cftdotsep}}
\renewcommand{\cftdotsep}{2}

% Modern typography: single-spacing after periods (no Victorian double-spacing),
% suppress orphans/widows, ragged bottom for even leading.
\frenchspacing
\clubpenalty=10000
\widowpenalty=10000
\displaywidowpenalty=10000
\raggedbottom

\definecolor{accentcolor}{HTML}{2A2A2A}
% Unified grayscale palette for callouts (black-and-white book).
\definecolor{tipbg}{HTML}{F2F2F2}
\definecolor{tipfg}{HTML}{1A1A1A}
\definecolor{tipborder}{HTML}{6B6B6B}
\definecolor{internalsbg}{HTML}{F2F2F2}
\definecolor{internalsfg}{HTML}{1A1A1A}
\definecolor{internalsborder}{HTML}{4A4A4A}
% Anecdote was warm/yellow; flattened to gray for B&W print.
\definecolor{anecdotebg}{HTML}{F2F2F2}
\definecolor{anecdotefg}{HTML}{1A1A1A}
\definecolor{anecdoteborder}{HTML}{6B6B6B}
\definecolor{examplebg}{HTML}{F8F8F8}
\definecolor{exampleborder}{HTML}{B8B8B8}
% Key pills: white fill so they always pop against any gray callout bg.
\definecolor{keybg}{HTML}{FFFFFF}
\definecolor{keyfg}{HTML}{1A1A1A}
\definecolor{keyborder}{HTML}{666666}
% Inline-code bg slightly darker than callout bg so \code{...} on a callout
% still has a visible bg pill (otherwise it disappears into the callout).
\definecolor{codebg}{HTML}{E6E6E6}
\definecolor{figureborder}{HTML}{888888}

\hypersetup{
  colorlinks=true,
  linkcolor=black,
  urlcolor=black,
  citecolor=black,
  pdftitle={VimFu --- Master Your Editor. Unleash Your Flow.},
  pdfauthor={VimFu},
}

% --- Inline key cap ----------------------------------------------------------
% Light keycap: subtle gray fill matching inline code, rounded border, dark
% text. Uniform height via \strut; minimum width so single letters look
% square. Multi-char caps (Esc, Ctrl) widen naturally.
\newlength{\keyminwidth}
\setlength{\keyminwidth}{1.6ex}
\DeclareRobustCommand{\key}[1]{%
  \allowbreak\tikz[baseline=(K.base)]{%
    \node[inner xsep=3pt, inner ysep=1pt,
          minimum width=\keyminwidth, minimum height=1.9ex,
          draw=keyborder, line width=0.5pt,
          fill=keybg, text=keyfg,
          rounded corners=2pt,
          font=\ttfamily\footnotesize]
      (K) {\strut #1};%
  }\allowbreak%
}

% --- Inline code ------------------------------------------------------------
% \allowbreak so inline code (e.g. \code{'fileencoding'}, file paths, command
% snippets) can break at word boundaries inside narrow contexts (tcolorboxes,
% table cells) instead of overflowing the margin.
\newcommand{\code}[1]{\allowbreak\colorbox{codebg}{\texttt{#1}}\allowbreak}

% --- Block code -------------------------------------------------------------
% breaklines/breakanywhere: long lines (e.g. the operators-textobjects
% grammar formula) must wrap inside narrow tcolorbox callouts instead of
% overflowing the right edge into the gutter.
\DefineVerbatimEnvironment{codeblock}{Verbatim}{frame=single,framerule=0pt,
  rulecolor=\color{codebg},fontsize=\small,xleftmargin=4pt,xrightmargin=4pt,
  breaklines=true,breakanywhere=true,breaksymbolleft={\tiny\ensuremath{\hookrightarrow}},
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

% --- Anecdote / personal story callout --------------------------------------
% Warmer styling than internals; italic body, tan/amber accent.
\newtcolorbox{anecdote}[1]{enhanced,breakable,colback=anecdotebg,colframe=anecdotebg,
  coltext=anecdotefg,arc=2pt,boxrule=0pt,leftrule=3pt,
  borderline west={2pt}{0pt}{anecdoteborder},
  left=10pt,right=8pt,top=6pt,bottom=6pt,
  fontupper=\itshape,
  title={\textbf{\upshape #1}},coltitle=anecdotefg,fonttitle=\bfseries,
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

% \illustratedpart{<title>}{<image path>} replaces \part{<title>} for the
% parts that have a hand-drawn illustration. Standard \part puts the
% title on its own page and \newpages anything that follows, which left
% the illustration stranded on the next page. This macro emits a single
% part page that holds BOTH the title and the image, then clears to the
% next content page.
% Redefine \frontmatter/\mainmatter/\backmatter so they don't force a
% blank verso (book.cls uses \cleardoublepage). The book builds with
% \documentclass[...,openany], so \clearpage is sufficient and avoids
% the stranded-blank pages reported by readers.
\makeatletter
\renewcommand\frontmatter{\clearpage\@mainmatterfalse\pagenumbering{roman}}
\renewcommand\mainmatter{\clearpage\@mainmattertrue\pagenumbering{arabic}}
\renewcommand\backmatter{\clearpage\@mainmatterfalse}
\makeatother

\newcommand{\illustratedpart}[2]{%
  \clearpage
  \refstepcounter{part}%
  \addcontentsline{toc}{part}{#1}%
  \phantomsection\pdfbookmark[0]{#1}{part.#1}%
  \thispagestyle{empty}%
  \null\vspace*{1em}%
  \begin{center}
    {\sffamily\Huge\bfseries #1\par}
    \vspace{1.6em}
    \includegraphics[width=\linewidth,
      height=0.62\textheight,keepaspectratio]{#2}\par
  \end{center}
  \vfill
  \clearpage
}

% \partillustration{<path>} drops a centered illustration above the part
% title. Used on parts that have a hand-drawn image in
% book/illustrations/<slug>.png. Width is capped at \linewidth and
% height at half the text height so the part title always fits below.
\newcommand{\partillustration}[1]{%
  \par\vspace*{0pt}\begingroup
    \centering\includegraphics[width=\linewidth,
      height=0.45\textheight,keepaspectratio]{#1}\par
  \endgroup\vspace{1.5em}%
}

% TikZ for the \key{} cap — load before the \key{} definition above wouldn't
% help (forward reference), so put the load-and-providecommand-fallback here.
\usepackage{tikz}
% Slim the \fbox around \key{...} so end-of-line keys are less likely to
% overshoot the right margin. Defaults are \fboxsep=3pt, \fboxrule=0.4pt.
\setlength{\fboxsep}{2pt}
\setlength{\fboxrule}{0.4pt}
% \allowbreak on both sides lets TeX wrap sequences like \key{Up}/\key{Down}/
% \key{Left}/\key{Right} across lines in narrow table cells instead of
% running off into the margin.
\providecommand{\key}[1]{\allowbreak\fbox{\texttt{#1}}\allowbreak}

% Line-breaking safety net. \emergencystretch lets TeX add a bit of extra
% inter-word glue on otherwise-impossible lines, eliminating most of the
% small overfull-hboxes that would poke into the margin (and into KDP's
% safety zone). Hide the visual indicator that TeX draws for residual
% overfulls in the final PDF.
\setlength{\emergencystretch}{3em}
\hbadness=10000
\hfuzz=2pt
\overfullrule=0pt
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
        part_slug = part_dir.split("-", 1)[-1]
        illus = ROOT.parent / "book" / "illustrations" / f"{part_slug}.png"
        if illus.exists():
            # Single-page part: title + illustration on the same recto.
            part_lines: list[str] = [
                f"\\illustratedpart{{{tex_escape(part_label)}}}"
                f"{{{latex_path(illus)}}}\n"
            ]
        else:
            part_lines = [f"\\part{{{tex_escape(part_label)}}}\n"]

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
        part_lines.append("\\clearpage")
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

    title_illus = ROOT.parent / "book" / "illustrations" / "title.png"
    _copyright_year = edition_year or ""
    _copyright_line = (
        f"Copyright \\textcopyright{{}} {tex_escape(str(_copyright_year))} Ashley Feniello. All rights reserved."
        if _copyright_year
        else "Copyright \\textcopyright{} Ashley Feniello. All rights reserved."
    )
    if title_illus.exists():
        title_block = (
            "\\begin{titlepage}\n"
            "\\sffamily\\centering\n"
            "\\vspace*{2em}\n"
            "{\\Huge\\bfseries VimFu\\par}\n"
            "\\vspace{0.6em}\n"
            "{\\Large\\itshape Master Your Editor. Unleash Your Flow.\\par}\n"
            "\\vspace{1.6em}\n"
            f"\\includegraphics[width=\\linewidth,"
            f"height=0.6\\textheight,keepaspectratio]{{{latex_path(title_illus)}}}\\par\n"
            "\\vfill\n"
            f"{{\\large {tex_escape(edition_string)}\\par}}\n"
            "\\vspace{0.4em}\n"
            f"{{\\small {_copyright_line}\\par}}\n"
            "\\vspace{1em}\n"
            "\\end{titlepage}\n"
        )
    else:
        title_block = (
            "\\title{\\sffamily\\bfseries VimFu\\texorpdfstring{\\\\[0.4em]{\\Large\\mdseries\\itshape Master Your Editor.\\\\Unleash Your Flow.}}{}}\n"
            "\\author{}\n"
            f"\\date{{\\sffamily {tex_escape(edition_string)}\\\\[0.4em]{{\\small {_copyright_line}}}}}\n"
            "\\maketitle\n"
        )

    book_tex = (
        "\\input{preamble}\n"
        "\\begin{document}\n"
        "\\frontmatter\n"
        + title_block +
        # The "About the QR codes" chapter is part of the front matter and
        # should appear physically BEFORE the table of contents (and thus be
        # listed at the top of the TOC, as a front-matter peer of "Contents"
        # itself). Emitting it after \tableofcontents put it after the TOC
        # both physically and visually — and made it look like a peer to the
        # numbered parts. \addcontentsline still routes the entry into the
        # generated .toc on the next pass.
        "\\chapter*{About the QR codes}\n"
        "\\addcontentsline{toc}{chapter}{About the QR codes}\n"
        "This book stands on its own---you can read it cover to cover without "
        "ever picking up a phone. Where it earns its place beside the website "
        "is in the videos and the live simulator: short screen-recorded demos "
        "that show every technique in motion, and a browser-based Vim "
        "playground where you can practice without leaving the page. We "
        "can't print either of those on paper, so QR codes throughout the "
        "book---not just at the end of each part---let you jump straight to "
        "them on {\\sffamily vimfubook.com}.\n\n"
        "There are three kinds of QR codes you will see:\n\n"
        "\\begin{itemize}\n"
        "\\item \\textbf{Videos.} Each part of the book ends with a QR that "
        "opens the collection of videos for that part. Inline embeds (the "
        "boxed \\textit{Watch} callouts) point at one specific clip when a "
        "single demo is worth pausing for.\n"
        "\\item \\textbf{Worked examples.} Many topics include a worked "
        "example with a QR beside it. Scan it and the simulator opens with "
        "\\emph{that exact example preloaded}, so you can try the keystrokes "
        "yourself instead of just reading them.\n"
        "\\item \\textbf{The simulator and the website.} A handful of QRs "
        "send you to the live simulator itself, the errata page for this "
        "edition, or other reference material on the site.\n"
        "\\end{itemize}\n\n"
        "Cross-references between topics appear as \\textit{(p.~NN)} so you "
        "can flip to them directly---there's a full alphabetical index in "
        "the back of the book as well.\n\n"
        "Every QR in this book points at a short, stable URL on the domain "
        "{\\sffamily vimfubook.com} (under the {\\sffamily /r/} prefix)---a "
        "redirect we own. That means if a video moves or a page is "
        "restructured we can re-aim the link without ever invalidating a "
        "printed code.\n\n"
        "\\noindent\\textbf{Try one now---this code opens the website:}"
        "\\par\\medskip\n"
        + sample_qr_callout + "\n"
        "\\clearpage\n"
        "\\tableofcontents\n"
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

