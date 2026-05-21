"""Style-guide auto-fix pass for content/parts/*.json.

Run from the repo root:  python content\\tools\\style_audit.py

Conservative: only converts patterns that are unambiguously wrong per
content/StyleGuide.md. Prints every change it makes.

Currently handles:

1. ``{key::}{key:X}{key:Y}...`` -> ``\\`:XY...\\``` for ex commands,
   when the trailing keys are foldable (single ASCII chars or
   multi-char text that is NOT a named special key).
2. ``{key::X}`` (where the colon and the rest are inside one
   ``key{}``) -> the same backtick form.
3. Trailing pills after an existing backticked ex command:
   ``\\`:X\\`{key:Y}{key:Z}...`` -> ``\\`:XYZ...\\``` (same folding
   rules as #1).

Leaves alone:

* Standalone ``{key::}`` with no following ``{key:...}`` (legitimate
  pill for "press : to enter command-line mode").
* Sequences where the trailing item is a named special key
  (``{key:Enter}``, ``{key:Esc}``, ``{key:Tab}``, ``{key: }``,
  ``{key:Ctrl-X}``, ``{key:F2}``, ``{key:Leader}``, etc.).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTENT = ROOT / "content"

# Foldable: any single ASCII printable char (33-126).
SINGLE_CHAR_RE = re.compile(r"\{key:([!-~])\}")
# A pill body is "foldable as text" if it does NOT match any of these
# named-key patterns.
NAMED_KEYS = {
    "Enter", "Esc", "Escape", "Tab", "CR", "Space", "Backspace", "BS",
    "Leader", "LocalLeader", "Up", "Down", "Left", "Right",
    "Home", "End", "PageUp", "PageDown", "Del", "Insert", "Null",
}


def _is_named(body: str) -> bool:
    if body in NAMED_KEYS:
        return True
    if re.match(r"^(Ctrl|Alt|Shift|Cmd|Meta|Super)-", body):
        return True
    if re.match(r"^F\d{1,2}$", body):
        return True
    return False


PILL_RE = re.compile(r"\{key:([^{}]+)\}")


def _consume_foldable(text: str, j: int) -> tuple[str, int]:
    """Starting at j, greedily consume `{key:X}` pills that are
    foldable (not named special keys). Return (accumulated_body, new_j).
    """
    body = ""
    while True:
        m = PILL_RE.match(text, j)
        if not m:
            break
        inner = m.group(1)
        if _is_named(inner):
            break
        body += inner
        j = m.end()
    return body, j


def fold_ex_commands(text: str) -> tuple[str, int]:
    n = 0
    out: list[str] = []
    i = 0
    while i < len(text):
        # Case 1: {key::} followed by foldable pills.
        if text.startswith("{key::}", i):
            body, j = _consume_foldable(text, i + len("{key::}"))
            if body:
                out.append("`:" + body + "`")
                i = j
                n += 1
                continue
        # Case 2: {key::X...} with colon inside the brace.
        m = re.match(r"\{key:(:[^{}]+)\}", text[i:])
        if m and not _is_named(m.group(1)[1:]):
            extra, j = _consume_foldable(text, i + m.end())
            out.append("`" + m.group(1) + extra + "`")
            i = j if extra else i + m.end()
            n += 1
            continue
        # Case 3: an existing backticked ex command followed by
        # foldable pills.  e.g.  `:q`{key:!}   ->   `:q!`
        m = re.match(r"`(:[^`]+)`", text[i:])
        if m:
            j = i + m.end()
            extra, j2 = _consume_foldable(text, j)
            if extra:
                out.append("`" + m.group(1) + extra + "`")
                i = j2
                n += 1
                continue
            out.append(m.group(0))
            i = j
            continue
        out.append(text[i])
        i += 1
    return "".join(out), n


# Pattern for bare ex commands in prose: a ':' followed by 1+ command
# letters/digits and optional '!', not preceded by a backtick, a brace,
# or another colon.
BARE_EX_RE = re.compile(
    r"(?<![`{:.\w/-])"      # not after backtick/brace/colon/word/path char
    r"(:[a-zA-Z][a-zA-Z0-9!]{0,15})"
    r"(?=[ \t,.;:\"\)\]\n]|$|\\n)"
)
# Words that look like an ex command but aren't:
_EX_BLACKLIST = {":help", ":h"}  # `:help` *is* an ex command, keep wrapped
# Things we should NOT wrap (false positives):
_NEVER_WRAP = {":/", "::", ":-", ":)", ":(", ":D"}


def _strip_with_protected_regions(text: str):
    """Yield (kind, content) pairs where kind is 'text' or 'protected'.

    Protected regions are: fenced code blocks (```...```), inline
    backtick spans (`...`), pill braces ({key:...}), and JSON-escaped
    fences (\\n``` is the JSON encoding of a code-fence delimiter).
    Pass-through emitter so we only modify 'text' regions.
    """
    i = 0
    while i < len(text):
        # JSON-escaped fenced block: ```\n ... \n```
        if text.startswith("```", i):
            j = text.find("```", i + 3)
            if j == -1:
                yield "protected", text[i:]
                return
            yield "protected", text[i:j + 3]
            i = j + 3
            continue
        if text[i] == "`":
            j = text.find("`", i + 1)
            if j == -1:
                yield "text", text[i:]
                return
            yield "protected", text[i:j + 1]
            i = j + 1
            continue
        if text.startswith("{key:", i):
            j = text.find("}", i)
            if j == -1:
                yield "text", text[i:]
                return
            yield "protected", text[i:j + 1]
            i = j + 1
            continue
        # Plain text until the next protected marker.
        candidates = [
            text.find("```", i),
            text.find("`", i),
            text.find("{key:", i),
        ]
        candidates = [c for c in candidates if c != -1]
        end = min(candidates) if candidates else len(text)
        if end > i:
            yield "text", text[i:end]
            i = end
        else:
            # Shouldn't happen, but guard.
            yield "text", text[i]
            i += 1


def _apply_to_text_regions(text: str, transform) -> tuple[str, int]:
    parts: list[str] = []
    total = 0
    for kind, chunk in _strip_with_protected_regions(text):
        if kind == "text":
            new_chunk, n = transform(chunk)
            parts.append(new_chunk)
            total += n
        else:
            parts.append(chunk)
    return "".join(parts), total


def wrap_bare_ex(text: str) -> tuple[str, int]:
    def _do(seg: str) -> tuple[str, int]:
        n = 0

        def _sub(m: re.Match) -> str:
            nonlocal n
            cmd = m.group(1)
            if cmd in _NEVER_WRAP:
                return cmd
            n += 1
            return "`" + cmd + "`"

        return BARE_EX_RE.sub(_sub, seg), n
    return _apply_to_text_regions(text, _do)


# Bare modifier chords: Ctrl-X, Alt-X, Shift-X, etc.
BARE_CHORD_RE = re.compile(
    r"(?<![`{\w-])"
    r"((?:Ctrl|Alt|Shift|Cmd|Meta|Super)-[A-Za-z0-9])"
    r"(?![`}\w-])"
)


def wrap_bare_chords(text: str) -> tuple[str, int]:
    def _do(seg: str) -> tuple[str, int]:
        n = 0

        def _sub(m: re.Match) -> str:
            nonlocal n
            n += 1
            return "{key:" + m.group(1) + "}"

        return BARE_CHORD_RE.sub(_sub, seg), n
    return _apply_to_text_regions(text, _do)


def process_file(path: Path) -> int:
    txt = path.read_text(encoding="utf-8")
    new_txt, n1 = fold_ex_commands(txt)
    new_txt, n2 = wrap_bare_ex(new_txt)
    new_txt, n3 = wrap_bare_chords(new_txt)
    n = n1 + n2 + n3
    if n:
        path.write_text(new_txt, encoding="utf-8")
        print(f"  {path.relative_to(ROOT)}: {n1} fold(s), {n2} ex-wrap(s), {n3} chord-wrap(s)")
    return n


def main() -> int:
    total = 0
    for p in sorted((CONTENT / "parts").rglob("*.json")):
        total += process_file(p)
    print(f"Total ex-command folds: {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
