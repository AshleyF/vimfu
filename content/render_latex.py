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
from lib.parts import part_label as _part_label  # noqa: E402
from lib.theses import thesis_for as _thesis_for  # noqa: E402
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


# --- QR callout pairing ----------------------------------------------------
# When two or more \qrcallout calls would otherwise stack vertically (e.g.
# the "Watch Online" section listing several video QRs, or the errata +
# report pair in the back matter), merge consecutive pairs into a single
# \qrcalloutpair so they render side by side. This is a text-level
# transform applied to the assembled LaTeX so individual emission sites
# don't need to know about pairing.

_QRCALLOUT_PREFIX = "\\qrcallout"


def _scan_brace_group(s: str, i: int) -> tuple[str, int]:
    """Return (content, idx_after_closing_brace) for the brace group at s[i]='{'.

    Handles nested braces and ignores braces that are part of a TeX escape
    sequence (``\\{``, ``\\}``, ``\\textbackslash{}``, etc.).
    """
    if s[i] != "{":
        raise ValueError(f"expected '{{' at position {i}, got {s[i]!r}")
    depth = 0
    start = i + 1
    n = len(s)
    while i < n:
        c = s[i]
        if c == "\\" and i + 1 < n:
            # Skip the next character — it's escaped, not a structural brace.
            i += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return s[start:i], i + 1
        i += 1
    raise ValueError("unbalanced braces while scanning group")


def _parse_qrcallout(s: str, start: int):
    """Parse ``\\qrcallout{a}{b}{c}{d}`` at position ``start``.

    Returns ((a, b, c, d), end_index) where end_index is one past the final
    closing brace. Returns None if the structure doesn't match.
    """
    if not s.startswith(_QRCALLOUT_PREFIX, start):
        return None
    pos = start + len(_QRCALLOUT_PREFIX)
    args: list[str] = []
    for _ in range(4):
        # Tolerate whitespace between \qrcallout and the first argument and
        # between argument groups (the emitter never inserts any, but a
        # future caller might).
        while pos < len(s) and s[pos] in " \t\r\n":
            pos += 1
        if pos >= len(s) or s[pos] != "{":
            return None
        try:
            arg, pos = _scan_brace_group(s, pos)
        except ValueError:
            return None
        args.append(arg)
    return (args[0], args[1], args[2], args[3]), pos


def pair_qrcallouts(text: str) -> str:
    """Merge adjacent ``\\qrcallout`` calls into ``\\qrcalloutpair`` calls.

    Two callouts are considered adjacent when the only characters between
    them are whitespace (spaces, tabs, newlines). Runs of three pair as
    (1,2)+single 3; runs of four pair as (1,2)+(3,4); etc.
    """
    out: list[str] = []
    pending = None  # (args, start_idx, end_idx)
    last_flushed = 0
    i = 0
    n = len(text)
    while i < n:
        j = text.find(_QRCALLOUT_PREFIX, i)
        if j < 0:
            break
        # Reject \qrcalloutpair (already paired) — advance past it.
        if text.startswith("\\qrcalloutpair", j):
            i = j + len("\\qrcalloutpair")
            continue
        # Reject false matches like \qrcalloutfoo: next char must be '{' or
        # whitespace.
        nxt = j + len(_QRCALLOUT_PREFIX)
        if nxt < n and text[nxt] not in "{ \t\r\n":
            i = nxt
            continue
        parsed = _parse_qrcallout(text, j)
        if parsed is None:
            i = j + len(_QRCALLOUT_PREFIX)
            continue
        args, end = parsed
        if pending is not None:
            p_args, p_start, p_end = pending
            gap = text[p_end:j]
            if gap.strip() == "":
                # Pair them.
                a1, b1, c1, d1 = p_args
                a2, b2, c2, d2 = args
                out.append(text[last_flushed:p_start])
                out.append(
                    "\\qrcalloutpair"
                    f"{{{a1}}}{{{b1}}}{{{c1}}}{{{d1}}}"
                    f"{{{a2}}}{{{b2}}}{{{c2}}}{{{d2}}}"
                )
                last_flushed = end
                pending = None
                i = end
                continue
            # Non-whitespace between → flush pending as-is, this becomes new pending.
            out.append(text[last_flushed:p_end])
            last_flushed = p_end
            pending = (args, j, end)
            i = end
            continue
        pending = (args, j, end)
        i = end
    out.append(text[last_flushed:])
    return "".join(out)


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
    overflows the right margin — which on a 7.5×9.25 KDP paperback means
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


_ARROW_GLYPH = {
    "Left": "\u2190",   # ←
    "Up": "\u2191",     # ↑
    "Right": "\u2192",  # →
    "Down": "\u2193",   # ↓
}


def _arrow_pill_body(name: str) -> str:
    """For a named arrow key, return the TikZ-safe body for `\\key{...}`
    that renders the Unicode arrow glyph. The glyphs live in the body
    font (Libertinus) which has them. Returns ``None`` for non-arrows.
    """
    return _ARROW_GLYPH.get(name)


def _atomize_key(s: str) -> list[str]:
    """Split a key string into atomic keystrokes for body rendering and
    index emission.

    Multi-character alpha sequences like ``hjkl`` or ``gg`` become one
    element per character. A modifier chord whose suffix is multi-alpha
    like ``Ctrl-hjkl`` becomes ``[Ctrl-h, Ctrl-j, Ctrl-k, Ctrl-l]``.
    Space-separated tokens (``Ctrl-W Ctrl-W``) are recursed on. Named
    keys (``Esc``, ``Tab``, ``Left``), F-keys, ``<...>`` angle-bracket
    forms, and short tokens stay atomic.
    """
    if not s:
        return []
    if " " in s:
        words = s.split(" ")
        if not all(words):
            return [s]
        if "".join(words) in _NAMED_KEYS:
            return [s]
        out: list[str] = []
        for w in words:
            out.extend(_atomize_key(w))
        return out
    if s in _NAMED_KEYS:
        return [s]
    if _FNKEY_RE.match(s):
        return [s]
    if s.startswith("<") and s.endswith(">"):
        return [s]
    m = _MODIFIER_RE.match(s)
    if m:
        prefix = s[:m.end()]
        rest = s[m.end():]
        # Suffix that's itself a named key (``Space``, ``Esc``, ``Up``)
        # or wrapped in angle brackets (``<C-W>``) is one atomic chord,
        # not a sequence of separate per-character chords.
        if rest in _NAMED_KEYS or _FNKEY_RE.match(rest):
            return [s]
        if rest.startswith("<") and rest.endswith(">"):
            return [s]
        if len(rest) >= 2 and rest.isascii() and all(c > " " for c in rest):
            return [prefix + c for c in rest]
        return [s]
    if (
        len(s) >= 2
        and s.isascii()
        and all(c > " " for c in s)
    ):
        # Multi-character sequences like ``hjkl``, ``gg``, ``:wq``,
        # ``'a``, ``[c``, ``gU`` are each *a sequence of separate
        # keystrokes*, not one key labelled with the whole string. Split
        # them so body pills show one cap per keystroke and the index
        # gets one entry per atomic key.
        return list(s)
    return [s]


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
    keystrokes, not a single key labelled "hjkl". Modifier chords whose
    suffix is multi-alpha (``Ctrl-hjkl``) are similarly expanded into
    one chord per letter.
    """
    atoms = _atomize_key(s)
    if not atoms:
        body = "\u2423"
        return f"\\key{{{tex_escape_inline_code(body)}}}"

    def _render_atom(a: str) -> str:
        # Single named arrow → Unicode glyph in the pill.
        m = _MODIFIER_RE.match(a)
        if m:
            prefix = a[:m.end()]
            rest = a[m.end():]
            glyph = _arrow_pill_body(rest)
            if glyph is not None:
                return (
                    f"\\key{{{tex_escape_inline_code(prefix)}"
                    f"{glyph}}}"
                )
            # ``Ctrl- `` (literal space suffix) renders the space with
            # the visible-space glyph so the chord doesn't appear as a
            # bare ``Ctrl-`` pill in the index/body.
            body = prefix + rest.replace(" ", chr(0x2423))
            return f"\\key{{{tex_escape_inline_code(body)}}}"
        glyph = _arrow_pill_body(a)
        if glyph is not None:
            return f"\\key{{{glyph}}}"
        if not a:
            return f"\\key{{{tex_escape_inline_code(chr(0x2423))}}}"
        body = a.replace(" ", chr(0x2423))
        return f"\\key{{{tex_escape_inline_code(body)}}}"

    # Decide spacing between atoms. Atoms split out of a single string
    # (``hjkl`` → 4 pills) read as one continuous chord and render
    # touching. Atoms separated by a literal space in the source
    # (``Ctrl-W Ctrl-W``) get a real space so TeX has a breakpoint.
    words = s.split(" ")
    if len(words) <= 1:
        return "".join(_render_atom(a) for a in atoms)
    # Reconstruct: group atoms per word, join word-groups with " ".
    groups: list[str] = []
    for w in words:
        if not w:
            continue
        wa = _atomize_key(w)
        groups.append("".join(_render_atom(a) for a in wa))
    return " ".join(groups)


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
    "Ctrl", "Alt", "Shift", "Cmd", "Meta", "Super",
    "CapsLock", "NumLock", "ScrollLock",
    "PrtSc", "PrintScreen", "SysRq", "Pause", "Break",
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
    """Build one or more \\index entries (concatenated) for a key
    keystroke, sub-grouped under "Keys".

    Returns an empty string for non-key tokens (e.g. literal text like
    "foo" / "bar" inside example commands) so the index stays focused on
    real Vim keys.

    The key string is *atomized* first — ``hjkl`` produces four entries
    (``h``, ``j``, ``k``, ``l``), ``Ctrl-hjkl`` produces four ``Ctrl-X``
    entries — so the index stays consistent with the per-pill body
    rendering. Without this, every multi-keystroke chord like ``gg``,
    ``ZZ``, ``Ctrl-WW`` would clutter the index with bogus compound
    "keys" that aren't real Vim keys, while still being absent from the
    individual-letter entries readers actually want to look up.

    Uses makeindex's `sort@display` syntax. In the display half we must
    keep raw `{` and `}` balanced from makeindex's point of view, so any
    literal `{`/`}` in the keystroke are rendered with `\\textbraceleft` /
    `\\textbraceright` instead of `\\{` / `\\}`.
    """
    if not _is_vim_key(k):
        return ""
    atoms = _atomize_key(k)
    if not atoms:
        return ""
    out: list[str] = []
    for atom in atoms:
        entry = _index_key_atom_entry(atom)
        if entry:
            out.append(entry)
    return "".join(out)


def _index_key_atom_entry(k: str) -> str:
    """Emit a single ``\\index{Keys!sort@display}`` entry for one atomic
    keystroke. Internal helper for `_index_key_entry`.
    """
    if not k:
        return ""
    k_for_sort = "".join(c for c in k if c >= " ")
    # Arrow glyphs collapse to their English names so ``{key:↑}`` and
    # ``{key:Up}`` index together. Likewise the visible-space glyph
    # collapses to the literal name "Space" so a Ctrl-Space chord
    # sorts as Ctrl-Space rather than Ctrl-␣.
    _glyph_to_name = {
        "\u2190": "Left", "\u2191": "Up",
        "\u2192": "Right", "\u2193": "Down",
        "\u2423": "Space",
    }
    k_for_sort = "".join(_glyph_to_name.get(c, c) for c in k_for_sort)

    # Group prefix so the index reads top-to-bottom in a natural order:
    #   A letters · B digits · C symbols · D named keys · E F-keys ·
    #   F modifier chords.
    # Letter prefixes (not digits) because makeindex's default sort
    # tends to fold leading digits and produces inconsistent ordering.
    mod_m = _MODIFIER_RE.match(k_for_sort)
    if mod_m:
        group = "F"
        within = k_for_sort
    elif _FNKEY_RE.match(k_for_sort):
        group = "E"
        within = k_for_sort
    elif k_for_sort in _NAMED_KEYS:
        group = "D"
        within = k_for_sort
    else:
        first = k_for_sort[:1]
        if first.isalpha():
            group = "A"
            within = first.lower() + ("U" if first.isupper() else "L") + k_for_sort[1:]
        elif first.isdigit():
            group = "B"
            within = k_for_sort
        else:
            group = "C"
            within = f"{ord(first):03d}" + k_for_sort[1:]

    # makeindex-safe encoding of the within-group key: quote `!@|"` and
    # collapse special chars to ASCII names so the .ind file doesn't
    # try to emit accents (\^x) or unbalanced braces in the sort half.
    _sort_subst = {
        "{": "lbrace", "}": "rbrace", "\\": "bslash",
        "^": "caret", "~": "tilde", "|": "bar",
        "#": "hash", "%": "percent", "$": "dollar",
        "_": "underscore", "&": "amp",
    }
    sort_key = group + "".join(
        _sort_subst.get(c, ('"' + c if c in '!@|"' else c))
        for c in within
    )

    def _esc(c: str) -> str:
        if c == "{": return "\\textbraceleft{}"
        if c == "}": return "\\textbraceright{}"
        if c == "\\": return "\\textbackslash{}"
        if c == "|": return "\\textbar{}"
        if c == "^": return "\\textasciicircum{}"
        if c == "~": return "\\textasciitilde{}"
        if c in "#$%&_": return "\\" + c
        if c < " ": return "\u2423"
        # makeindex treats unescaped `"`, `!`, `@`, `|` as special even
        # inside the display argument. `"` quotes the next char (so `{"}`
        # means literal `}` and the inner `{` ends up unmatched, which
        # blows up makeindex with "premature LFD"). Double the quote and
        # prefix the others so makeindex passes them through verbatim.
        if c == '"': return '""'
        if c in "!@|": return '"' + c
        return c

    # Modifier chord with arrow suffix → Unicode arrow glyph.
    m = _MODIFIER_RE.match(k)
    if m:
        prefix = k[:m.end()]
        rest = k[m.end():]
        glyph = _arrow_pill_body(rest)
        if glyph is not None:
            body = "".join(_esc(c) for c in prefix) + glyph
            display = "\\protect\\key{" + body + "}"
            return f"\\index{{Keys!{sort_key}@{display}}}"
    # Bare arrow name → Unicode arrow glyph.
    glyph = _arrow_pill_body(k)
    if glyph is not None:
        display = "\\protect\\key{" + glyph + "}"
        return f"\\index{{Keys!{sort_key}@{display}}}"

    parts = k.split(" ")
    if not k or any(p == "" for p in parts):
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


def _extract_key_index_entries(text: str) -> list[str]:
    """Return a list of ``\\index{Keys!...}`` lines for every ``{key:X}``
    pill in *text*. Used by heading-like blocks (``\\section*``,
    ``\\begin{internals}{...}``, etc.) so we can emit the index entries
    *outside* the fragile title argument. Inside a fragile arg, LaTeX
    strips our ``\\protect`` from ``\\protect\\key{...}`` while writing the
    title to .aux, which produces a duplicate ``\\key {X}`` entry in the
    index — every key indexed from a heading would appear twice.
    """
    if not text:
        return []
    entries: list[str] = []
    for m in _KEY_RE.finditer(_collapse_long_key_runs(text)):
        e = _index_key_entry(m.group(1))
        if e:
            entries.append(e)
    return entries


_LONG_KEY_RUN_RE = re.compile(r"(?:\{key:[^{}\s]\} ?){4,}")


def _collapse_long_key_runs(text: str) -> str:
    """Collapse a long string of single-char `{key:X}` markers into a
    single backtick-quoted code span.

    Author shortcut: many topics encode a literal Ex-mode command as
    ``{key::}{key:s}{key:e}{key:t} {key:s}{key:p}{key:e}{key:l}{key:l}``
    so each char gets its own pill. That looks awful: a row of 8+
    single-letter boxes for what is really a single command the user
    types. When that happens, fold the whole run into ``\\code{...}``
    so it renders as one ttfamily code block instead.

    We only collapse runs that look like *typed text* on the command
    line. The signal for "typed text" is BOTH:

      * the run starts with one of the command-line-entering keys
        ``:``, ``/``, ``?``, or ``!``, AND
      * the run contains at least one multi-character word (so
        ``:set spell`` collapses, but a chord list like
        ``{key:/} {key:?} {key:n} {key:N}`` — all single-character
        pills — does not).

    Pure normal-mode chord lists like ``{key:h} {key:j} {key:k}
    {key:l}`` (the "remap to hjkl" row in the tmux table) or
    ``gUiw``, ``"ayy``, ``ddkP``, ``+yiw`` keep rendering as a row
    of touching key pills.
    """
    def repl(m: re.Match) -> str:
        chunk = m.group(0)
        chars: list[str] = []
        for piece in re.finditer(r"\{key:([^{}])\}( ?)", chunk):
            chars.append(piece.group(1))
            if piece.group(2):
                chars.append(piece.group(2))
        joined = "".join(chars).rstrip()
        starts_cmdline = bool(joined) and joined[0] in ":/?!"
        has_multichar_word = any(len(w) >= 2 for w in joined.split())
        if not (starts_cmdline and has_multichar_word):
            return chunk  # leave chord list as individual pills
        return "`" + joined + "`"
    return _LONG_KEY_RUN_RE.sub(repl, text)


def _smart_quotes(s: str, *, prev_char: str = "") -> str:
    """Convert ASCII " and ' in prose to typographic curly quotes.

    Heuristic: an ASCII double or single quote opens (left-curly) when
    the preceding character is whitespace, opening punctuation, or
    start-of-string; otherwise it closes (right-curly). For single
    quotes, an alphanumeric preceding character forces the closing
    form so contractions (don't, it's) render as right-curly
    apostrophes.

    ``prev_char`` is the character before this segment in the
    surrounding text — passed in by render_inline so that a quote at
    the very start of a prose chunk knows what was before it across
    markup boundaries.
    """
    out: list[str] = []
    prev = prev_char
    n = len(s)
    # Common leading-apostrophe contractions that should render with a
    # closing curly (right single quote) even though they sit at a word
    # boundary: 'tis, 'twas, 'em, 'n', 'cause, 'round, 'nough, etc.
    _LEADING_APOS = ("tis", "twas", "em", "cause", "round", "nough", "bout", "ere", "neath")
    i = 0
    while i < n:
        c = s[i]
        if c == '"':
            if not prev or prev.isspace() or prev in "([{<-/\u2013\u2014":
                out.append("\u201C")
            else:
                out.append("\u201D")
        elif c == "'":
            # Detect leading-apostrophe contraction or decade ('90s)
            at_word_boundary = (not prev) or prev.isspace() or prev in "([{<-/\u2013\u2014"
            leading_special = False
            if at_word_boundary and i + 1 < n:
                nxt = s[i + 1]
                if nxt.isdigit():
                    leading_special = True
                else:
                    tail = s[i + 1 : i + 8].lower()
                    for w in _LEADING_APOS:
                        if tail.startswith(w):
                            after = s[i + 1 + len(w)] if i + 1 + len(w) < n else " "
                            if not after.isalpha():
                                leading_special = True
                                break
            if leading_special:
                out.append("\u2019")
            elif prev and prev.isalnum():
                out.append("\u2019")
            elif at_word_boundary:
                # An opening quote can't be immediately followed by
                # whitespace, terminal punctuation, or end-of-string —
                # in that case it's actually a closing quote that just
                # happens to sit after a space (e.g. `'quick '`).
                nxt2 = s[i + 1] if i + 1 < n else ""
                if (not nxt2) or nxt2.isspace() or nxt2 in ".,;:!?)]}>":
                    out.append("\u2019")
                else:
                    out.append("\u2018")
            else:
                out.append("\u2019")
        else:
            out.append(c)
        prev = c
        i += 1
    return "".join(out)


def render_inline(text: str, *, index, with_key_index: bool = True, plain_keys: bool = False) -> str:
    if text is None:
        return ""
    text = _collapse_long_key_runs(text)
    out: list[str] = []
    pos = 0
    # Track the last raw character emitted (before tex_escape) so that
    # _smart_quotes can make correct open/close decisions for a quote
    # that begins a prose segment immediately after markup like a
    # closing italic or a key pill.
    last_char = ""
    for m in _combined.finditer(text):
        if m.start() > pos:
            seg = text[pos:m.start()]
            out.append(tex_escape(_smart_quotes(seg, prev_char=last_char)))
            last_char = seg[-1] if seg else last_char
        kind = m.lastgroup
        raw = m.group(0)
        if kind == "key":
            k = _KEY_RE.match(raw).group(1)
            idx = _index_key_entry(k) if with_key_index else ""
            # Ex-commands like `{key::terminal}` were authored as key pills
            # but should render as inline monospace code (per the style
            # guide, multi-character typed strings are code, not keys).
            # Detect them defensively: starts with `:` followed by 2+
            # alpha chars (a real `:` key alone, or `:1` etc. is left alone).
            if (len(k) >= 3 and k.startswith(":")
                    and all(c.isalnum() or c in "_!" for c in k[1:])):
                out.append(f"\\code{{{tex_escape_inline_code(k)}}}{idx}")
            elif plain_keys:
                out.append(f"\\texttt{{{tex_escape_inline_code(k)}}}{idx}")
            else:
                out.append(f"{_split_key_for_wrap(k)}{idx}")
            # Glue trailing punctuation to the pill so a line break can't
            # separate them — \key{} ends with \allowbreak, which would
            # otherwise let "{key:D}, on the other hand" wrap the comma
            # alone onto the next line.
            nxt = text[m.end():m.end() + 1]
            if nxt in ",.:;!?":
                out.append("\\nobreak{}")
            last_char = " "  # treat markup as a word boundary
        elif kind == "link":
            mm = _LINK_RE.match(raw)
            label, tid = mm.group(1), mm.group(2)
            # If the markdown label is just a backticked internal slug
            # matching the link target's topic id, replace it with that
            # topic's real title — otherwise readers see opaque slugs
            # like "basic-editing.replace-mode" in print.
            stripped = label.strip("`")
            if stripped == tid and tid in index:
                label = index[tid].get("title", label)
            out.append(
                f"{tex_escape(label)}~(p.~\\pageref{{topic:{tex_escape(tid)}}})"
            )
            last_char = ")"
        elif kind == "extlink":
            mm = _EXTLINK_RE.match(raw)
            out.append(render_inline(mm.group(1), index=index))
            last_char = " "
        elif kind == "code":
            inner = _CODE_RE.match(raw).group(1)
            if plain_keys:
                out.append(f"\\texttt{{{tex_escape_inline_code(inner)}}}")
            else:
                out.append(_split_code_for_wrap(inner))
            last_char = " "
        elif kind == "strong":
            inner = _STRONG_RE.match(raw).group(1)
            out.append(f"\\textbf{{{render_inline(inner, index=index)}}}")
            last_char = inner[-1] if inner else last_char
        elif kind == "em":
            inner = _EM_RE.match(raw).group(1)
            # Pull a trailing punctuation char into the italic span so
            # the kerning between the italic glyph and the punctuation
            # doesn't fight the upright baseline.
            tail = ""
            end = m.end()
            if end < len(text) and text[end] in ",.:;!?\u2014\u2013":
                tail = text[end]
                pos = end + 1
            else:
                pos = end
            out.append(f"\\textit{{{render_inline(inner + tail, index=index)}}}")
            last_char = tail if tail else (inner[-1] if inner else last_char)
            continue
        pos = m.end()
    if pos < len(text):
        seg = text[pos:]
        out.append(tex_escape(_smart_quotes(seg, prev_char=last_char)))
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
        raw_ex_title = ex.get("title", ex_id)
        out.extend(_extract_key_index_entries(raw_ex_title))
        out.append("\\begin{example}{" + render_inline(raw_ex_title, index=index, with_key_index=False) + "}")
        if ex.get("summary"):
            out.append("\\examplesummary{" + inl(ex["summary"]) + "}")
        for i, fr in enumerate(ex.get("frames", []), start=1):
            cap = fr.get("caption", "")
            keys = fr.get("keys", "")
            narr = fr.get("narration", "")
            # Many example captions were authored as "<keys> — <description>",
            # which duplicates the key chord already shown as pills in the
            # step header. Strip that leading "<keys> —" (or em-dash variants)
            # so the head reads "Step N — {keys} — description" instead of
            # "Step N — {keys} — keys — description".
            #
            # Captions usually open with the keys as pill markup like
            # "{key:i} — ...". We extract any leading {key:...} pills, join
            # their inner names (ignoring whitespace), and compare against the
            # normalized keys string. If they match, drop those pills plus the
            # following separator.
            if keys and cap:
                _pill_re = re.compile(r"^\{key:([^}]*)\}\s*")
                rest = cap.lstrip()
                extracted: list[str] = []
                while True:
                    m = _pill_re.match(rest)
                    if not m:
                        break
                    extracted.append(m.group(1))
                    rest = rest[m.end():]
                if extracted and "".join(extracted).replace(" ", "") == keys.replace(" ", ""):
                    rest = rest.lstrip()
                    for sep in (" \u2014 ", " \u2013 ", " - ", "\u2014 ", "\u2013 ", "- ",
                                "\u2014", "\u2013", "-", ", "):
                        if rest.startswith(sep):
                            rest = rest[len(sep):].lstrip()
                            break
                    cap = rest
                else:
                    # Fall back to the old raw-string match for captions that
                    # spell out the keys literally (no pill markup).
                    stripped = cap.lstrip()
                    for sep in (" \u2014 ", " \u2013 ", " - ", "\u2014", "\u2013", "-"):
                        prefix = keys + sep
                        if stripped.startswith(prefix):
                            cap = stripped[len(prefix):].lstrip()
                            break
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
                    f"\\par\\textit{{[missing screenshot {tex_escape(ex_id)}/frame\\_{i:02d}.bw.svg --- "
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
            + "}{\\linkicon}{Try this in the simulator}{" + tex_escape(qr_url) + "}"
        )
        out.append("\\end{example}")
        return out

    if bt == "heading":
        level = int(b.get("level", 2))
        cmd = "section" if level <= 1 else "subsection" if level == 2 else "subsubsection"
        raw_title = b.get("text", "")
        # Render the visible title with key indexing OFF, then emit the
        # `\index{Keys!...}` calls AFTER the heading. Index calls inside
        # `\section*{...}` get re-written by LaTeX as the title is moved
        # into .aux/running-headers, and the inner `\protect\key{...}`
        # loses its protection — producing a duplicate `\key {X}`
        # variant for every key (see _extract_key_index_entries).
        title_tex = render_inline(raw_title, index=index, with_key_index=False)
        out.append(f"\\{cmd}*{{{title_tex}}}")
        out.extend(_extract_key_index_entries(raw_title))

    elif bt == "prose":
        out.extend(emit_paragraphs(b.get("text", ""), index=index))

    elif bt == "tip":
        out.append("\\begin{tipbox}\n" + inl(b.get("text", "")) + "\n\\end{tipbox}")

    elif bt == "divider":
        out.append("\\begin{center}\\rule{0.4\\linewidth}{0.4pt}\\end{center}")

    elif bt == "figure":
        # Inline photograph / illustration with caption + credit. Path is
        # repo-relative (e.g. "content/images/ADM-3A.png"); we resolve it
        # against the project root so latex_path produces a path relative
        # to the output dir.
        raw_path = (b.get("path") or "").strip()
        if raw_path:
            img = ROOT.parent / raw_path if not Path(raw_path).is_absolute() else Path(raw_path)
            if img.exists():
                width = b.get("width") or "0.8"
                caption = b.get("caption") or ""
                credit = b.get("credit") or ""
                out.append(
                    "\\photofigure{" + latex_path(img) + "}{"
                    + str(width) + "}{"
                    + inl(caption) + "}{"
                    + inl(credit) + "}"
                )
            else:
                out.append(
                    "\\par\\textit{[missing figure: "
                    + tex_escape(raw_path) + "]}"
                )

    elif bt == "_keys_panel":
        items = b.get("items", [])
        kt_lines: list[str] = ["\\begin{keypanel}", "\\begin{keytable}"]
        for item in items:
            sequence = item.get("sequence", [])
            label = item.get("label", "")
            key_runs: list[str] = []
            for step in sequence:
                if isinstance(step, str):
                    k = step
                    note = ""
                else:
                    k = step.get("key", "")
                    note = step.get("note", "")
                if not k:
                    continue
                key_runs.append(_split_key_for_wrap(k) + _index_key_entry(k))
                if note:
                    # Per-step notes are rare in this path, but keep them
                    # attached so we don't drop information.
                    label = (label + " " if label else "") + inl(note)
            run = "\\,".join(key_runs)
            kt_lines.append(f"  {run} & {inl(label)} \\\\")
        kt_lines.append("\\end{keytable}")
        kt_lines.append("\\end{keypanel}")
        out.append("\n".join(kt_lines))

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
            kt_lines: list[str] = ["\\begin{keytable}"]
            for key, note in pairs:
                key_run = _split_key_for_wrap(key) if key else ""
                if key:
                    key_run += _index_key_entry(key)
                kt_lines.append(f"  {key_run} & {note} \\\\")
            kt_lines.append("\\end{keytable}")
            # Emit as one block so the outer "\n\n" join doesn't insert
            # blank lines between rows (which trigger \parskip and push
            # the key cell down relative to the note cell).
            out.append("\n".join(kt_lines))

    elif bt == "table":
        headers = b.get("headers", [])
        rows = b.get("rows", [])
        if headers:
            explicit_key_cols = set(b.get("keyColumns") or [])
            # Legacy auto-detect: columns headed exactly "Key" / "Keys"
            # always count as key columns.
            for i, h in enumerate(headers):
                if str(h).strip().lower() in ("key", "keys"):
                    explicit_key_cols.add(i)
            n = len(headers)

            # Measure the longest visible content per column. Strip our
            # content markup (`{key:..}`, `**bold**`, `*em*`, backtick
            # code) so widths reflect rendered text length.
            def _visible_len(s: str) -> int:
                t = re.sub(r"\{key:([^}]+)\}", r"\1", str(s))
                t = re.sub(r"\*\*([^*]+)\*\*", r"\1", t)
                t = re.sub(r"\*([^*]+)\*", r"\1", t)
                t = re.sub(r"`([^`]+)`", r"\1", t)
                return len(t)

            def _has_key_markup(s: str) -> bool:
                return "{key:" in str(s)

            col_max = [
                max(
                    [_visible_len(headers[i])]
                    + [_visible_len(row[i]) if i < len(row) else 0
                       for row in rows]
                )
                for i in range(n)
            ]
            col_has_keys = [
                any(_has_key_markup(row[i]) for row in rows if i < len(row))
                or _has_key_markup(headers[i])
                for i in range(n)
            ]

            # A column is "narrow" (fixed-width, sized to its longest
            # content) if any of these are true:
            #   * it is explicitly listed in keyColumns / header == "Key(s)"
            #   * any of its cells contain {key:...} key-pill markup
            #     AND the longest cell is short enough to fit without
            #     wrapping (≤ KEY_NARROW_LIMIT chars). Tables that list
            #     many keys per cell ("Examples", "Variants") have long
            #     key-rich cells that need to wrap as prose does, so we
            #     leave them as X columns despite the key markup.
            #   * its longest visible content fits in ~22 characters,
            #     which is short enough that letting tabularx wrap it
            #     across multiple lines would just waste vertical space.
            # Everything else becomes a tabularx X column that absorbs
            # the remaining horizontal space and wraps prose naturally.
            NARROW_CHAR_LIMIT = 22
            KEY_NARROW_LIMIT = 18
            narrow_cols = set(explicit_key_cols)
            for i in range(n):
                if col_has_keys[i] and col_max[i] <= KEY_NARROW_LIMIT:
                    narrow_cols.add(i)
                elif (not col_has_keys[i]) and col_max[i] <= NARROW_CHAR_LIMIT:
                    narrow_cols.add(i)

            # If every column ended up narrow, demote the widest one to
            # X so the table doesn't sit awkwardly half-empty on the
            # page (and so longtable rules still apply for paging).
            if narrow_cols == set(range(n)) and n > 1:
                widest = max(range(n), key=lambda i: col_max[i])
                narrow_cols.discard(widest)

            def _col_em(i: int) -> float:
                # ~0.7em per visible char + 1em slack for cell padding.
                # Columns containing {key:...} pills need extra slack
                # because each pill adds horizontal padding around the
                # ttfamily char (border + fboxsep). Clamp to 3..16em so
                # a freak long cell doesn't push the prose column off
                # the page.
                longest = col_max[i]
                if col_has_keys[i]:
                    em = longest * 0.95 + 1.5
                else:
                    em = longest * 0.7 + 1.0
                return max(3.0, min(16.0, em))

            # Compute every narrow column's width, then make sure their
            # total leaves enough room for the prose X column to actually
            # absorb width and wrap text. Our body text width is roughly
            # 30em on the KDP trim, so cap total narrow width at 22em
            # (leaves ~8em for the X column at minimum). If we're over,
            # scale every narrow column down proportionally.
            narrow_em = {i: _col_em(i) for i in narrow_cols}
            has_x = any(i not in narrow_cols for i in range(n))
            if has_x:
                MAX_NARROW_TOTAL = 22.0
                total = sum(narrow_em.values())
                if total > MAX_NARROW_TOTAL:
                    factor = MAX_NARROW_TOTAL / total
                    narrow_em = {i: max(3.0, w * factor)
                                 for i, w in narrow_em.items()}

            cols = []
            # When 2+ columns would become X (prose-wrapping) columns,
            # weight each by its longest cell so a wordier column gets
            # more horizontal share than a short one. Single-X tables
            # behave exactly as before (plain X). Weights are clamped
            # to [0.5, 1.5] of the equal share so a freak-long cell in
            # one column can't starve its peers to unreadable widths,
            # then re-normalised so the sum equals the X-column count
            # (tabularx requirement: sum of \hsize weights == # X cols).
            x_cols = [i for i in range(n) if i not in narrow_cols]
            x_weight: dict[int, float] = {}
            if len(x_cols) >= 2:
                raw = [max(col_max[i], 1) for i in x_cols]
                total = sum(raw)
                n_x = len(x_cols)
                weights = [r / total * n_x for r in raw]
                weights = [max(0.5, min(1.5, w)) for w in weights]
                wsum = sum(weights)
                weights = [w / wsum * n_x for w in weights]
                x_weight = {i: w for i, w in zip(x_cols, weights)}

            for i in range(n):
                if i in narrow_cols:
                    cols.append(
                        "@{}>{\\strut\\raggedright\\sloppy\\arraybackslash}"
                        f"p{{{narrow_em[i]:.1f}em}}@{{}}"
                    )
                elif i in x_weight:
                    cols.append(
                        f"@{{\\hspace{{1em}}}}Y{{{x_weight[i]:.3f}}}"
                    )
                else:
                    cols.append(
                        "@{\\hspace{1em}}>{\\strut\\raggedright\\sloppy"
                        "\\arraybackslash}X"
                    )

            # If there is NO X column (every column is narrow), fall
            # back to a plain longtable so we don't ask tabularx to
            # handle a row with no expanding column.
            spec = "".join(cols)
            table_lines: list[str] = []
            if has_x:
                table_lines.append(
                    "\\par\\begin{tabularx}{\\linewidth}{" + spec + "}"
                )
            else:
                table_lines.append("\\par\\begin{longtable}{" + spec + "}")
            table_lines.append(" & ".join(f"\\textbf{{{inl(h)}}}" for h in headers) + " \\\\")
            table_lines.append("\\hline")
            for row in rows:
                cells = list(row) + [""] * (n - len(row))
                rendered = []
                for i, c in enumerate(cells):
                    s = str(c)
                    # Cells in explicit "Key"/"Keys" columns get the
                    # {key:...} wrapper added implicitly. Other narrow
                    # columns (Command/Motion/Operator/etc.) already
                    # carry their own key markup in the source. Skip
                    # cells that already contain {key:...} markup OR
                    # backticked monospace (e.g. `:undolist`, `:earlier 5m`):
                    # those are typed commands, not key chords.
                    if (i in explicit_key_cols and s
                            and "{key:" not in s
                            and "`" not in s):
                        s = "{key:" + s + "}"
                    rendered.append(inl(s))
                table_lines.append(" & ".join(rendered) + " \\\\")
            table_lines.append("\\end{tabularx}" if has_x else "\\end{longtable}")
            # Emit the whole table as ONE block so the outer block-join
            # ("\n\n") doesn't insert blank lines between rows -- blank
            # lines inside longtable/tabularx trigger \parskip and
            # disturb the row baselines (keys appear shifted below their
            # description text).
            out.append("\n".join(table_lines))

    elif bt == "embed":
        lesson = b.get("lesson", "")
        v = video_for_lesson(lesson) if lesson != "" else None
        # Prefer book_title (which may contain {key:...} pill markup) over
        # the YouTube-facing title so we can render keys as pills in print.
        if v and v.get("book_title"):
            title_tex = inl(v["book_title"])
        elif v:
            title_tex = tex_escape(v["title"])
        else:
            title_tex = tex_escape(f"Lesson {lesson}")
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
                + "}{\\playicon}{" + title_tex + "}{" + tex_escape(qr_url) + "}"
            )
        else:
            out.append("\\begin{videocallout}")
            out.append(f"\\playicon\\iconsep {title_tex}")
            out.append("\\end{videocallout}")

    elif bt == "internals":
        raw_title = b.get("title", "Under the Hood")
        title = render_inline(raw_title, index=index, with_key_index=False)
        text = b.get("text", "") or ""
        out.extend(_extract_key_index_entries(raw_title))
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
        raw_title = b.get("title", "")
        title = render_inline(raw_title, index=index, with_key_index=False)
        text = b.get("text", "") or ""
        title_arg = title if title else ""
        out.extend(_extract_key_index_entries(raw_title))
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
                + "}{\\linkicon}{" + cap + "}{" + tex_escape(qr_url) + "}"
            )
        return out

    elif bt == "buy-prompt":
        # The PDF *is* the book — drop these callouts entirely.
        return out

    else:
        out.append(f"\\par\\textit{{[unknown block: {tex_escape(str(bt))}]}}")

    return out


# -------- topic body ----------------------------------------------------- #

def render_topic_body(t, index, examples, *, thesis: str | None = None) -> str:
    inl = lambda s: render_inline(s, index=index)
    out: list[str] = []

    title = t.get("title", "(untitled)")
    tid = t.get("id", t["__file_stem"])
    # Chapter title: pills in the body heading AND in the typeset TOC.
    # PDF bookmarks (hyperref) can't render TikZ \key{} pills, so we use
    # \texorpdfstring to give the bookmark a plain-monospace fallback
    # while the TOC still gets real pills.
    body_title = render_inline(title, index=index, with_key_index=False, plain_keys=False)
    toc_title  = render_inline(title, index=index, with_key_index=False, plain_keys=False)
    pdf_title  = render_inline(title, index=index, with_key_index=False, plain_keys=True)
    short_title = f"\\texorpdfstring{{{toc_title}}}{{{pdf_title}}}"
    out.append(f"\\chapter[{short_title}]{{{body_title}}}\\label{{topic:{tex_escape(tid)}}}")
    if thesis:
        out.append("\\partthesis{" + render_inline(thesis, index=index) + "}")
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
            + "}{\\linkicon}{Spin up tmux in the simulator}{" + tex_escape(qr_url) + "}"
        )

    # Normalize title and level-1 heading text by stripping {key:...}
    # wrappers so titles authored with key-markup like "{key:*}, {key:cw}"
    # still match a body heading authored as plain "*, cw, …".
    _norm_title = re.sub(r"\{key:([^}]+)\}", r"\1", title).strip()

    # Inline `{"type":"keys"}` blocks duplicate the Reference table that
    # appears at the end of most topics. Drop them in the print book when
    # a table is present, so the same keys aren't summarised three times
    # (prose, mid-topic key blocks, end-of-topic Reference table). When a
    # topic has no table, the `keys` blocks ARE the summary — keep them.
    _blocks_src = list(t.get("blocks", []))
    _has_ref_table = any(b.get("type") == "table" for b in _blocks_src)
    raw_blocks = [b for b in _blocks_src
                  if _visible(b, AUDIENCE)
                  and not (_has_ref_table and b.get("type") == "keys")]

    for b in raw_blocks:
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
                    + "}{\\playicon}{" + title + "}{" + tex_escape(qr_url) + "}"
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
\documentclass[10pt,twoside,openany]{book}

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
\setmonofont{Libertinus Mono}[Scale=0.93, FakeBold=1.3]
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
\makeindex[title=Index, columns=2, intoc, noautomatic]
\usepackage{longtable}
\usepackage{tabularx}
\usepackage{ltablex} % longtable + tabularx: X columns that page-break
\keepXColumns       % preserve X behaviour inside tabularx after ltablex hijacks it
\usepackage{array}  % \arraybackslash, advanced column specs
% Weighted X column: Y{w} acts like an X column but absorbs the
% leftover width in proportion to w. When a table has multiple
% X-style columns, weighting each by its content length stops the
% wordier column from wrapping while its peer sits half-empty.
% Sum of weights across Y/X columns must equal their count (handled
% by the renderer, see _column_spec in render_latex.py).
\newcolumntype{Y}[1]{>{\hsize=#1\hsize\linewidth=\hsize\strut\raggedright\sloppy\arraybackslash}X}
\usepackage{amssymb}  % \checkmark, used by newunicodechar mapping below
\usepackage{newunicodechar}
% Libertinus Serif lacks the U+2713 CHECK MARK glyph. Without a mapping,
% XeLaTeX silently emits a missing-glyph placeholder that downstream PDF
% consumers (e.g. KDP's pre-print validation) flag as a non-printable
% character. Map it to the math \checkmark, which renders cleanly.
\newunicodechar{✓}{\ensuremath{\checkmark}}
\usepackage{fontawesome5}
% Icons used in place of repetitive labels:
%   \playicon       — a small film-reel icon next to video QR titles,
%                     reading as "this QR points to a video".
%   \linkicon       — a small arrow next to non-video QR titles
%                     ("Try it in the simulator", "Errata", etc.) —
%                     reading as "scan and follow this link".
%   \internalsicon  — a small gear used as the title prefix on "Under the Hood"
%                     callout boxes, replacing the old "Under the Hood --- "
%                     literal text. The gear reads as "internals / mechanics".
% \iconsep adds slightly more breathing room than \  between the icon and
% the title text so the icon doesn't look glued to the first letter.
\newcommand{\iconsep}{\hspace{0.35em}}
\newcommand{\playicon}{\faFilm}
\newcommand{\linkicon}{\faArrowRight}
\newcommand{\internalsicon}{\faCog}
\usepackage{fvextra}
\usepackage[most]{tcolorbox}
\usepackage{enumitem}
\usepackage{needspace}
\usepackage{etoolbox}
% \calloutneedspace ensures at least this much vertical space before a
% breakable callout box starts. Prevents the title from sitting alone
% at the bottom of a page while the body wraps to the next.
\newcommand{\calloutneedspace}{\par\needspace{8\baselineskip}}
% \partthesis: a short italic paragraph printed under the chapter title
% on the first topic of each part. Sets the stage for the part.
\newcommand{\partthesis}[1]{%
  \par\medskip
  \begingroup
    \leftskip=1.5em \rightskip=1.5em
    \itshape\large
    \noindent #1\par
  \endgroup
  \par\bigskip
}
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
\setlength{\cftbeforepartskip}{8pt plus 1pt}
\setlength{\cftbeforechapskip}{2pt plus 0.5pt}
\setlength{\cftbeforesecskip}{0pt}
\setlength{\cftbeforesubsecskip}{0pt}
% Tighter line spacing inside the TOC itself.
\AtBeginDocument{\addtocontents{toc}{\protect\linespread{0.92}\protect\selectfont}}
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
\newcommand{\code}[1]{\allowbreak\texttt{#1}\allowbreak}

% --- Block code -------------------------------------------------------------
% breaklines/breakanywhere: long lines (e.g. the text-objects
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
  left=10pt,right=8pt,top=6pt,bottom=6pt,
  lines before break=3,
  fontupper={\setlength{\parskip}{0.5\baselineskip}\setlength{\parindent}{0pt}}}

% --- Internals callout ------------------------------------------------------
\newtcolorbox{internals}[1]{enhanced,breakable,colback=internalsbg,colframe=internalsbg,
  coltext=internalsfg,arc=2pt,boxrule=0pt,leftrule=3pt,
  borderline west={2pt}{0pt}{internalsborder},
  left=10pt,right=8pt,top=6pt,bottom=6pt,
  lines before break=3,
  fontupper={\setlength{\parskip}{0.5\baselineskip}\setlength{\parindent}{0pt}},
  title={\internalsicon\iconsep\textbf{#1}},coltitle=internalsfg,fonttitle=\bfseries,
  attach title to upper={\par\medskip}}

% --- Anecdote / personal story callout --------------------------------------
% Warmer styling than internals; italic body, tan/amber accent.
\newtcolorbox{anecdote}[1]{enhanced,breakable,colback=anecdotebg,colframe=anecdotebg,
  coltext=anecdotefg,arc=2pt,boxrule=0pt,leftrule=3pt,
  borderline west={2pt}{0pt}{anecdoteborder},
  left=10pt,right=8pt,top=6pt,bottom=6pt,
  lines before break=3,
  fontupper={\itshape\setlength{\parskip}{0.5\baselineskip}\setlength{\parindent}{0pt}},
  title={\textbf{\upshape #1}},coltitle=anecdotefg,fonttitle=\bfseries,
  attach title to upper={\par\medskip}}

% --- Worked example callout -------------------------------------------------
\newtcolorbox{example}[1]{enhanced,breakable,colback=examplebg,colframe=exampleborder,
  arc=2pt,boxrule=0.5pt,
  left=10pt,right=8pt,top=6pt,bottom=6pt,
  lines before break=3,
  fontupper={\setlength{\parskip}{0.5\baselineskip}\setlength{\parindent}{0pt}},
  title={\textbf{Worked Example: #1}},coltitle=black,fonttitle=\bfseries,
  attach title to upper={\par\medskip}}
\newcommand{\examplesummary}[1]{\par\textit{#1}\par\medskip}
\newcommand{\examplestep}[1]{\par\medskip\noindent #1\par}
\newcommand{\examplenarration}[1]{\par\small #1\normalsize\par}
% Screenshot in an example: thin gray border so the white SVG background
% doesn't bleed into the page.
\newcommand{\examplefigure}[1]{%
  \par\medskip\begin{center}%
    {\setlength{\fboxrule}{0.4pt}\setlength{\fboxsep}{0pt}%
     \color{figureborder}\fbox{\color{black}\includegraphics[width=0.55\linewidth]{#1}}}%
  \end{center}\par}

% \photofigure{<path>}{<width-frac>}{<caption>}{<credit>}
% Inline photograph or illustration with a caption and a smaller credit
% line. Width is given as a fraction of \linewidth (e.g. "0.8"). The
% credit is rendered in a small italic font on a separate line below the
% caption so the source attribution is always visible but doesn't
% compete with the caption text.
\newcommand{\photofigure}[4]{%
  \par\medskip\begin{center}%
    {\setlength{\fboxrule}{0.6pt}\setlength{\fboxsep}{0pt}%
     \color{figureborder}\fbox{\color{black}\includegraphics[width=#2\linewidth]{#1}}}%
    \par\smallskip
    {\small\itshape #3}%
    \ifx\relax#4\relax\else\par\smallskip{\footnotesize #4}\fi
  \end{center}\par\medskip}

% --- Key-row table ----------------------------------------------------------
% \keycolwidth pins the width of the "key" column across every key/table
% block so consecutive tables on a page line up vertically. Width chosen
% to fit common combos like "Ctrl+W Ctrl+W" rendered as keycaps.
\newlength{\keycolwidth}
\setlength{\keycolwidth}{7.5em}
% Both columns are top-aligned p{} so that when the note column wraps
% to multiple lines the key chord sits at the top of the row (lined up
% with the first line of the note) rather than drifting toward the
% vertical center. The leading \strut on each row gives both first
% lines the same height so a single-line note baseline matches a
% keycap baseline.
\newenvironment{keytable}{%
  \par\medskip\begin{tabular}{@{}>{\strut\centering\arraybackslash}p{\keycolwidth}@{\hspace{1em}}>{\strut}p{\dimexpr\linewidth-\keycolwidth-2.6em\relax}@{}}}{%
  \end{tabular}\par\medskip}

% --- Keys reference panel ---------------------------------------------------
% Light gray callout wrapping a series of `{"type":"keys"}` blocks so a
% sequence like {i — insert before}, {a — append after}, ... visually
% separates from the surrounding prose instead of reading as more body
% paragraphs.
\definecolor{keypanelbg}{HTML}{F4F4F4}
\definecolor{keypanelborder}{HTML}{C8C8C8}
\newtcolorbox{keypanel}{enhanced,breakable,colback=keypanelbg,colframe=keypanelborder,
  arc=2pt,boxrule=0.5pt,
  left=10pt,right=8pt,top=6pt,bottom=6pt,
  fontupper={\setlength{\parskip}{0pt}\setlength{\parindent}{0pt}}}
\BeforeBeginEnvironment{keypanel}{\calloutneedspace}

% --- Video callout ----------------------------------------------------------
\newtcolorbox{videocallout}{enhanced,colback=accentcolor!5,colframe=accentcolor!50,
  arc=2pt,boxrule=0.5pt,
  left=10pt,right=8pt,top=6pt,bottom=6pt}
\BeforeBeginEnvironment{tipbox}{\calloutneedspace}
\BeforeBeginEnvironment{internals}{\calloutneedspace}
\BeforeBeginEnvironment{anecdote}{\calloutneedspace}
\BeforeBeginEnvironment{example}{\calloutneedspace}
\BeforeBeginEnvironment{videocallout}{\calloutneedspace}
% --- QR callout -------------------------------------------------------------
% URL is shown as plain text (not a clickable link) — a printed page can't
% be clicked, and the QR code beside it is the real "scan to follow"
% mechanism. URL drops to \scriptsize: it's only a fallback for readers
% who can't scan, and the smaller size keeps the callout calm.
%
% Args: {qr image path}{icon (e.g. \playicon) or empty}{title text}{url}.
% Icon is passed separately so we can measure its width and indent the
% URL to align with the first character of the TITLE TEXT (not the icon).
% [c]+[t] minipage alignment puts the title's first baseline on the QR's
% vertical center; the URL hangs below.
\newlength{\qriconw}
\newcommand{\qrcallout}[4]{%
  \calloutneedspace
  \par\medskip\noindent\begin{minipage}[c]{0.12\linewidth}%
    \includegraphics[width=\linewidth]{#1}%
  \end{minipage}\hfill\begin{minipage}[t]{0.84\linewidth}%
    \settowidth{\qriconw}{\sffamily\bfseries\ifx\relax#2\relax\else#2\iconsep\fi}%
    {\sffamily\bfseries\ifx\relax#2\relax\else#2\iconsep\fi#3}\par
    \smallskip\hspace*{\qriconw}{\scriptsize\sffamily #4}%
  \end{minipage}\par\medskip}

% --- Paired QR callouts ------------------------------------------------------
% Two callouts in two columns, used when the Python renderer detects that
% multiple \qrcallout calls would otherwise stack vertically (e.g. several
% video QRs in the same "Watch Online" section). The QR images stay the
% same physical size as in the single version (0.12\linewidth -> 0.25 of a
% half-column of 0.48\linewidth) so they scan identically. Title/URL fonts
% drop one size each (\small / \scriptsize) to fit the narrower column.
% Args: {q1}{i1}{t1}{u1}{q2}{i2}{t2}{u2} — same icon-separated form as
% the single \qrcallout so the URL hangs below the title text.
\newcommand{\qrcalloutpair}[8]{%
  \calloutneedspace
  \par\medskip\noindent
  \begin{minipage}[t]{0.48\linewidth}%
    \begin{minipage}[c]{0.25\linewidth}%
      \includegraphics[width=\linewidth]{#1}%
    \end{minipage}\hfill\begin{minipage}[t]{0.71\linewidth}%
      \settowidth{\qriconw}{\sffamily\bfseries\small\ifx\relax#2\relax\else#2\iconsep\fi}%
      {\sffamily\bfseries\small\ifx\relax#2\relax\else#2\iconsep\fi#3}\par
      \smallskip\hspace*{\qriconw}{\scriptsize\sffamily #4}%
    \end{minipage}%
  \end{minipage}\hspace{0.04\linewidth}%
  \begin{minipage}[t]{0.48\linewidth}%
    \begin{minipage}[c]{0.25\linewidth}%
      \includegraphics[width=\linewidth]{#5}%
    \end{minipage}\hfill\begin{minipage}[t]{0.71\linewidth}%
      \settowidth{\qriconw}{\sffamily\bfseries\small\ifx\relax#6\relax\else#6\iconsep\fi}%
      {\sffamily\bfseries\small\ifx\relax#6\relax\else#6\iconsep\fi#7}\par
      \smallskip\hspace*{\qriconw}{\scriptsize\sffamily #8}%
    \end{minipage}%
  \end{minipage}%
  \par\medskip}

% Slightly tighter chapter heading.
% Chapter heading: ``block`` (not ``hang``) so very long titles wrap onto
% the next line inside the text block instead of running off the right
% margin. Smaller font (LARGE, not Huge) so even unwrapped titles fit on
% a 7.5×9.25 page. \raggedright in the title body lets LaTeX break wherever it
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
% Redefine \frontmatter/\backmatter so they don't force a blank verso
% (book.cls uses \cleardoublepage). The book builds with
% \documentclass[...,openany], so \clearpage is sufficient and avoids
% the stranded-blank pages reported by readers.
%
% \mainmatter intentionally uses \cleardoublepage: mainmatter page 1
% must land on a recto (right-hand page) so LaTeX's odd/even = recto/verso
% assignment matches the PDF page parity that KDP uses for its
% gutter-margin check. An odd-length frontmatter would otherwise invert
% every page-parity downstream and KDP would flag the entire mainmatter
% as having insufficient inner margin.
\makeatletter
\renewcommand\frontmatter{\clearpage\@mainmatterfalse\pagenumbering{roman}}
\renewcommand\mainmatter{\cleardoublepage\@mainmattertrue\pagenumbering{arabic}}
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

% \illustratedpartqr{<title>}{<image>}{<qr image>}{<qr url>}
% Same as \illustratedpart but also drops a small "Watch the videos
% for this part" QR below the illustration. The QR is centered with
% the URL directly below it (no separate label / icon — the heading
% already names the QR's purpose). URL uses \scriptsize sans so it
% reads as a quiet fallback for readers who can't scan.
\newcommand{\illustratedpartqr}[4]{%
  \clearpage
  \refstepcounter{part}%
  \addcontentsline{toc}{part}{#1}%
  \phantomsection\pdfbookmark[0]{#1}{part.#1}%
  \thispagestyle{empty}%
  \null\vspace*{1em}%
  \begin{center}{\sffamily\Huge\bfseries #1\par}\end{center}
  \vfill
  \begin{center}%
    \includegraphics[width=\linewidth,
      height=0.55\textheight,keepaspectratio]{#2}%
  \end{center}
  \vfill
  \begin{center}%
    {\small\itshape Watch the videos for this part\par}%
    \vspace{0.5em}%
    \includegraphics[width=0.12\linewidth]{#3}\par
    \vspace{0.4em}%
    {\scriptsize\sffamily #4\par}%
  \end{center}
  \vspace*{1em}%
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

        part_label = _part_label(part_dir)
        part_slug = part_dir.split("-", 1)[-1]
        illus = ROOT.parent / "book" / "illustrations" / f"{part_slug}.png"
        # Pre-compute the per-part videos QR so we can either embed it on
        # the part-title page (illustrated parts) or emit a standalone
        # trailer page (non-illustrated parts, e.g. Appendices).
        qr_path, qr_url = _qr_for_slug(part_videos_slug(part_dir))
        if illus.exists():
            # Single-page part: title + illustration + small per-part
            # videos QR all on the same recto.
            part_lines: list[str] = [
                f"\\illustratedpartqr{{{tex_escape(part_label)}}}"
                f"{{{latex_path(illus)}}}"
                f"{{{latex_path(qr_path)}}}"
                f"{{{tex_escape(qr_url)}}}\n"
            ]
        else:
            part_lines = [f"\\part{{{tex_escape(part_label)}}}\n"]

        for idx, t in enumerate(plist):
            tk = _thesis_for(part_dir) if idx == 0 else None
            body = render_topic_body(t, index, examples, thesis=tk)
            body = pair_qrcallouts(body)
            (pdir / f"{t['__file_stem']}.tex").write_text(body, encoding="utf-8")
            part_lines.append(
                f"\\input{{parts/{part_dir}/{t['__file_stem']}}}"
            )
            written += 1

        # Per-part trailer: only for parts without an illustration (the
        # illustrated path already embedded the videos QR on the title
        # page). Currently this means Appendices only.
        if not illus.exists():
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
                + "}{\\linkicon}{Videos: " + tex_escape(part_label) + "}{"
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
        + "}{\\linkicon}{Errata for this edition (" + tex_escape(edition_label) + ")}{"
        + tex_escape(errata_qr_url) + "}"
    )
    report_qr_callout = (
        "\\qrcallout{" + latex_path(report_qr_path)
        + "}{\\linkicon}{Report a problem (email)}{"
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
        + "}{\\linkicon}{Try it: open vimfubook.com}{}"
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
        # should appear physically BEFORE the table of contents — but it is
        # NOT listed in the TOC. The TOC opens facing the start of "About
        # the QR codes" (TOC begins on a right-hand page, About sits on
        # the facing left-hand page), so listing it would be redundant —
        # the reader is literally looking at it while reading the TOC.
        "\\chapter*{About the QR codes}\n"
        "This book stands on its own---you can read it cover to cover "
        "without ever picking up a phone. It also has a companion website, "
        "{\\sffamily vimfubook.com}, that hosts a short screen-recorded "
        "video for every technique in the book and a browser-based Vim "
        "simulator where you can practice everything you read about "
        "directly on the web page---no installation, no signup, no setup. "
        "QR codes throughout the book let you jump straight to that "
        "material from wherever you are reading.\n\n"
        "There are three kinds of QR codes you will see:\n\n"
        "\\begin{itemize}\n"
        "\\item \\textbf{Videos.} Each part of the book ends with a QR that "
        "opens the collection of videos for that part. Inline video "
        "callouts (the boxed ones marked with \\playicon) point at one "
        "specific clip when a single demo is worth pausing for.\n"
        "\\item \\textbf{Worked examples.} Many topics include a worked "
        "example with a QR beside it. Scan it and the simulator opens with "
        "\\emph{that exact example preloaded}, so you can try the keystrokes "
        "yourself instead of just reading about them.\n"
        "\\item \\textbf{The simulator and the website.} A handful of QRs "
        "send you to the live simulator itself, the errata page for this "
        "edition, or other reference material on the site.\n"
        "\\end{itemize}\n\n"
        + sample_qr_callout + "\n"
        "\\clearpage\n"
        "\\tableofcontents\n"
        "% --- Epigraph (fills the verso between TOC and mainmatter) ---\n"
        "\\clearpage\n"
        "\\thispagestyle{empty}\n"
        "\\null\\vfill\n"
        "\\begin{center}\n"
        "  {\\upshape\\sffamily\\large\\char\"266B\\,\\char\"266A\\,\\char\"266B}\\hspace{0.8em}\\textit{\\large Everybody was Vim-fu fighting}\\par\n"
        "  \\vspace{0.4em}\n"
        "  \\textit{\\large Those keys were fast as lightning}\\hspace{0.8em}{\\upshape\\sffamily\\large\\char\"266A}\\par\n"
        "  \\vspace{1.2em}\n"
        "  {\\footnotesize ---with apologies to Carl Douglas\\par}\n"
        "\\end{center}\n"
        "\\vfill\\vfill\n"
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
    book_tex = pair_qrcallouts(book_tex)
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

