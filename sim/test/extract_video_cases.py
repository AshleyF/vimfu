"""
Extract a fidelity test CASE from a VimFu video JSON.

Produces one test_curriculum_auto_<RANGE>.py file under
sim/test/cases/auto/ containing a CASES dict in the same shape used
by the existing test suite, with one entry per video.

Usage:
    python sim/test/extract_video_cases.py 0876 0895
        # extracts all videos whose numeric ID falls in [0876, 0895]
        # to sim/test/cases/auto/test_curriculum_auto_0876_to_0895.py

The translation rules from video JSON `steps[]` to a raw key string
mirror shellpilot/player.py so the captured ground truth matches
what the recorded video actually shows:

    "escape" / "enter"          -> \x1b / \r
    {"type": "..."}             -> literal text
    {"keys": "..."}             -> literal text (with "ctrl+x" etc.
                                   recognised and lowered to a
                                   control byte just like player.py)
    {"keys": "escape|enter|tab"}-> \x1b / \r / \t
    {"ex": "..."}               -> ":" + ex + "\r"
    {"ctrl": "x"}               -> control byte
    {"backspace": N}            -> "\x7f" * N

Steps ignored (purely narration / pacing): say, comment, wait,
pause, overlay, ifScreen, waitForScreen, writeFile (only used in
setup), line (only used in setup).

Videos that exercise features the sim can't reproduce are emitted
with a SKIP comment and excluded from CASES. Reasons:

    - :!cmd      shell escape — sim can't run arbitrary shells
    - :term      terminal buffer
    - :edit X    multi-file workflows the harness doesn't support
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SHORTS_DIR = REPO_ROOT / "curriculum" / "shorts"
OUT_DIR = Path(__file__).resolve().parent / "cases" / "auto"

LESSON_RE = re.compile(r"^(\d{4})([a-z]*)_(.+)\.json$")
CTRL_KEY_RE = re.compile(r"^(\d*)(?:ctrl|c)[\+\-](.+)$", re.IGNORECASE)


def _ctrl_byte(letter: str) -> str:
    """Translate a single key letter into the matching control byte.
    Supports A-Z, @, [, \\, ], ^, _ (matches Vim's notation)."""
    c = letter.upper()
    if c == "@":
        return "\x00"
    if c == "[":
        return "\x1b"
    if c == "\\":
        return "\x1c"
    if c == "]":
        return "\x1d"
    if c == "^":
        return "\x1e"
    if c == "_":
        return "\x1f"
    if "A" <= c <= "Z":
        return chr(ord(c) - 64)
    return ""


def _ranges_overlap(name: str, lo: int, hi: int) -> bool:
    m = LESSON_RE.match(name)
    if not m:
        return False
    n = int(m.group(1))
    return lo <= n <= hi


def _initial_from_setup(setup: list) -> str:
    """The last writeFile in setup is the file nvim opens; its
    content seeds the test buffer. If no writeFile, return empty."""
    content = ""
    for step in setup or []:
        if isinstance(step, dict) and "writeFile" in step:
            content = step["content"]
    return content


_RANGE_PREFIX_RE = re.compile(r"^[%$.\d,;'+\-/?\s<>]*$")


def _is_blocking_ex(cmd: str) -> str | None:
    """Return a skip reason if the ex command can't run in the sim.

    Detects ``:!cmd`` and ``:<range>!cmd`` shell-escape forms while
    leaving forced-command modifiers (``:q!`` / ``:delmarks!``), the
    ``:set option!`` toggle, and substitute delimiters (``:s!a!b!``)
    alone — those still execute purely inside vim."""
    c = cmd.lstrip(":")
    if "!" in c:
        head_before_bang = c.split("!", 1)[0]
        # The first '!' is a shell escape iff everything before it
        # is a (possibly empty) range expression — digits, ranges,
        # %, $, ., '.', ',', ';', whitespace.
        if _RANGE_PREFIX_RE.match(head_before_bang):
            return "shell escape (:!)"
    head = c.strip().split()[0] if c.strip() else ""
    if head in {"term", "terminal"}:
        return ":term"
    return None


def _emit_key_step(step, keys: list[str], skip: list[str]) -> None:
    if isinstance(step, str):
        if step == "escape":
            keys.append("\x1b")
        elif step == "enter":
            keys.append("\r")
        return

    if not isinstance(step, dict):
        return

    # Check the primary step type FIRST. `overlay`, `wait` etc. can
    # ride along as metadata on a real input step (e.g. `type` with
    # an overlay caption); we must not treat them as a reason to
    # skip the whole step.
    if "type" in step:
        t = step["type"]
        reason = _is_blocking_ex(t)
        if reason:
            skip.append(reason)
            return
        keys.append(t)
        return

    if "ex" in step:
        e = step["ex"]
        reason = _is_blocking_ex(":" + e)
        if reason:
            skip.append(reason)
            return
        keys.append(":" + e + "\r")
        return

    if "keys" in step:
        kv = step["keys"]
        if kv == "escape":
            keys.append("\x1b")
            return
        if kv == "enter":
            keys.append("\r")
            return
        if kv == "tab":
            keys.append("\t")
            return
        m = CTRL_KEY_RE.match(kv) if isinstance(kv, str) else None
        if m:
            count, letter = m.group(1), m.group(2)
            cb = _ctrl_byte(letter)
            if cb:
                keys.append(count + cb)
                return
        keys.append(kv)
        return

    if "ctrl" in step:
        cb = _ctrl_byte(step["ctrl"])
        if cb:
            keys.append(cb)
        return

    if "backspace" in step:
        n = int(step["backspace"])
        keys.append("\x7f" * n)
        return

    # Pure narration / pacing / setup-only — produce no keys.
    return


def extract_case(video_path: Path) -> dict:
    data = json.loads(video_path.read_text(encoding="utf-8"))
    keys: list[str] = []
    skip: list[str] = []
    # Tag-based skip: tmux / shell lessons exercise programs we don't
    # simulate. Mark the whole video as skipped so it doesn't pollute
    # the sim-vs-nvim fidelity pass rate.
    tags = data.get("tags", []) or []
    if "tmux" in tags:
        skip.append("tmux lesson (not vim)")
    elif "shell" in tags:
        skip.append("shell lesson (not vim)")
    for step in data.get("steps", []):
        _emit_key_step(step, keys, skip)
    initial = _initial_from_setup(data.get("setup", []))
    return {
        "stem": video_path.stem,
        "title": data.get("title", video_path.stem),
        "description": data.get("description", ""),
        "initial": initial,
        "keys": "".join(keys),
        "skip_reasons": sorted(set(skip)),
    }


def collect(lo: int, hi: int) -> list[dict]:
    out: list[dict] = []
    for p in sorted(SHORTS_DIR.glob("*.json")):
        if _ranges_overlap(p.name, lo, hi):
            out.append(extract_case(p))
    return out


def render_module(cases: list[dict]) -> str:
    """Render a Python source file holding CASES (skipped videos
    appear only in a SKIPPED dict for visibility)."""
    lines = [
        '"""',
        f"AUTO-GENERATED by extract_video_cases.py. Do not edit by hand.",
        '"""',
        '',
        'CASES = {',
    ]
    skipped: dict[str, list[str]] = {}
    for c in cases:
        if c["skip_reasons"]:
            skipped[c["stem"]] = c["skip_reasons"]
            continue
        # repr() handles all the escape-byte cases (\x1b etc.) safely
        lines.append(f'    {c["stem"]!r}: {{')
        desc = c["title"].split("—", 1)[-1].strip() if "—" in c["title"] else c["title"]
        lines.append(f'        "description": {desc!r},')
        lines.append(f'        "keys": {c["keys"]!r},')
        lines.append(f'        "initial": {c["initial"]!r},')
        lines.append('    },')
    lines.append('}')
    if skipped:
        lines.append('')
        lines.append('SKIPPED = {')
        for stem, reasons in sorted(skipped.items()):
            lines.append(f'    {stem!r}: {reasons!r},')
        lines.append('}')
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("lo", type=int, help="lower bound (inclusive), e.g. 876")
    ap.add_argument("hi", type=int, help="upper bound (inclusive), e.g. 895")
    ap.add_argument("--out", type=Path, default=None,
                    help="output file (default: auto/test_curriculum_auto_<lo>_to_<hi>.py)")
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = args.out or (
        OUT_DIR / f"test_curriculum_auto_{args.lo:04d}_to_{args.hi:04d}.py"
    )

    cases = collect(args.lo, args.hi)
    if not cases:
        print(f"ERROR: no videos found in [{args.lo:04d}, {args.hi:04d}]")
        sys.exit(1)

    out_path.write_text(render_module(cases), encoding="utf-8")
    total = len(cases)
    skipped = sum(1 for c in cases if c["skip_reasons"])
    kept = total - skipped
    print(f"Wrote {out_path}")
    print(f"  {total} videos found, {kept} CASES emitted, {skipped} skipped.")
    if skipped:
        print("  Skipped:")
        for c in cases:
            if c["skip_reasons"]:
                print(f"    {c['stem']}: {', '.join(c['skip_reasons'])}")


if __name__ == "__main__":
    main()
