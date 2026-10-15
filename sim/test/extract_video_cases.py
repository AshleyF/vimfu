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
import shlex
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SHORTS_DIR = REPO_ROOT / "curriculum" / "shorts"
OUT_DIR = Path(__file__).resolve().parent / "cases" / "auto"

LESSON_RE = re.compile(r"^(\d{4})([a-z]*)_(.+)\.json$")
CTRL_KEY_RE = re.compile(r"^(\d*)(?:ctrl|c)[\+\-](.+)$", re.IGNORECASE)

# These lessons cross the pure-Neovim boundary used by this oracle.  They are
# retained in the generated SKIPPED inventory until equivalent SessionManager
# integration cases cover the shell/filesystem lifecycle.
ORACLE_SKIP_OVERRIDES = {
    "0002_opening_a_file": "starts in the shell; requires session oracle",
    "0008_quitting_vim": "continues after Neovim exits; requires session oracle",
    "0009_save_and_quit": "continues after Neovim exits; requires session oracle",
    "0010_quit_without_saving": "continues after Neovim exits; requires session oracle",
    "0187_the_ZZ_ZQ_keys": "exits Neovim; requires session oracle",
    "0133_navigate_windows": "nested mixed split layout is not supported by the flat window model",
    "0430l_pwd": "depends on the host working directory; requires session oracle",
    "0430d_qa": "exits Neovim; requires session oracle",
    "0430f_wqa": "exits Neovim; requires session oracle",
    "0495_mkview_loadview": "depends on persistent view files; requires session filesystem oracle",
    "0496_gx_open_url": "depends on the host URL opener and platform-specific error output",
    "0498_vimrc_init_lua": "oracle capture does not observe the sourced config before the final frame",
    "0499_help_system": "depends on Neovim runtime help files; requires runtime integration oracle",
    "0880q_quit_all": "exits Neovim; requires session oracle",
    "0880s_write_quit_all": "exits Neovim; requires session oracle",
    "0880w_pwd": "depends on the host working directory; requires session oracle",
}

# These lessons cross the Neovim/shell boundary but finish in a deterministic
# editor state that SessionManager can reproduce.  Keep this list explicit:
# arbitrary host commands are not safe or stable oracle inputs.
SESSION_ORACLE_CASES = {
    "0419_shell_command",
    "0420_repeat_shell",
    "0421_filter",
    "0814_write_to_file",
    "0880_shell_command",
    "0880a_filter_lines",
}

SESSION_EXIT_CASES = {
    "0430d_qa",
    "0430f_wqa",
}


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


def _setup_files(setup: list) -> dict[str, str]:
    """Return every deterministic file created before Neovim starts."""
    return {
        str(step["writeFile"]): str(step.get("content", ""))
        for step in setup or []
        if isinstance(step, dict) and "writeFile" in step
    }


def _launch_file_from_setup(setup: list, files: dict[str, str]) -> str | None:
    """Find the file argument from the final nvim launch command."""
    result = None
    for step in setup or []:
        if not isinstance(step, dict) or "line" not in step:
            continue
        try:
            words = shlex.split(str(step["line"]))
        except ValueError:
            continue
        indexes = [i for i, word in enumerate(words) if Path(word).name in {"vim", "nvim"}]
        if not indexes:
            continue
        args = words[indexes[-1] + 1:]
        i = 0
        candidates = []
        while i < len(args):
            if args[i] in {"-c", "--cmd", "-S", "-u"}:
                i += 2
            elif args[i].startswith("-"):
                i += 1
            else:
                candidates.append(args[i])
                i += 1
        if candidates:
            result = candidates[-1]
    if result in files:
        return result
    return next(reversed(files), None) if files else None


def _nvim_launch_from_setup(setup: list) -> dict | None:
    """Preserve multi-file launch semantics that affect visible state."""
    result = None
    for step in setup or []:
        if not isinstance(step, dict) or "line" not in step:
            continue
        try:
            words = shlex.split(str(step["line"]))
        except ValueError:
            continue
        indexes = [i for i, word in enumerate(words) if Path(word).name in {"vim", "nvim"}]
        if not indexes:
            continue
        args = words[indexes[-1] + 1:]
        layout = None
        files: list[str] = []
        i = 0
        while i < len(args):
            arg = args[i]
            if arg in {"-o", "-O", "-p"}:
                layout = {"-o": "horizontal", "-O": "vertical", "-p": "tabs"}[arg]
                i += 1
            elif arg == "-d":
                layout = "diff"
                i += 1
            elif arg in {"-c", "--cmd", "-S", "-u"}:
                i += 2
            elif arg.startswith("-"):
                i += 1
            else:
                files.append(arg)
                i += 1
        result = {"layout": layout, "files": files}
    return result


_NVIM_C_COMMAND_RE = re.compile(r"(?:^|\s)-c\s+(['\"])(.*?)\1")


def _nvim_prelude_from_setup(setup: list) -> str:
    """Preserve ``nvim -c '...'`` launch configuration as Ex keystrokes.

    The fidelity harness starts its own pinned Neovim instance, so silently
    dropping launch-time options creates an oracle gap: the captured editor is
    not the editor used by the video.  Replaying the commands immediately after
    startup is equivalent for the option/plugin setup used by the curriculum.
    """
    commands: list[str] = []
    for step in setup or []:
        if not isinstance(step, dict) or "line" not in step:
            continue
        line = str(step["line"])
        if not re.search(r"(?:^|\s)(?:n?vim)(?:\s|$)", line):
            continue
        for match in _NVIM_C_COMMAND_RE.finditer(line):
            commands.append(":" + match.group(2) + "\r")
    return "".join(commands)


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
    if re.match(r"^(?:r(?:ead)?|w(?:rite)?)\s+!", c.strip()):
        return "shell command through Ex; requires session oracle"
    if head in {"term", "terminal"}:
        return ":term"
    return None


def _emit_key_step(
    step, keys: list[str], skip: list[str], *, allow_shell: bool = False
) -> None:
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
        if reason and not allow_shell:
            skip.append(reason)
            return
        keys.append(t)
        return

    if "ex" in step:
        e = step["ex"]
        command = e if e.startswith(":") else ":" + e
        reason = _is_blocking_ex(command)
        if reason and not allow_shell:
            skip.append(reason)
            return
        keys.append(command + "\r")
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
    setup = data.get("setup", [])
    keys: list[str] = [_nvim_prelude_from_setup(setup)]
    skip: list[str] = []
    setup_files = _setup_files(setup)
    launch_file = _launch_file_from_setup(setup, setup_files)
    launch = _nvim_launch_from_setup(setup)
    expects_exit = video_path.stem in SESSION_EXIT_CASES
    requires_session = video_path.stem in SESSION_ORACLE_CASES or expects_exit
    # Tag-based skip: tmux / shell lessons exercise programs we don't
    # simulate. Mark the whole video as skipped so it doesn't pollute
    # the sim-vs-nvim fidelity pass rate.
    tags = data.get("tags", []) or []
    if "tmux" in tags:
        skip.append("tmux lesson (not vim)")
    elif "shell" in tags and not requires_session:
        skip.append("shell lesson (not vim)")
    if video_path.stem in ORACLE_SKIP_OVERRIDES and not expects_exit:
        skip.append(ORACLE_SKIP_OVERRIDES[video_path.stem])
    for step in data.get("steps", []):
        _emit_key_step(step, keys, skip, allow_shell=requires_session)
    initial = setup_files.get(launch_file, _initial_from_setup(setup))
    return {
        "stem": video_path.stem,
        "title": data.get("title", video_path.stem),
        "description": data.get("description", ""),
        "initial": initial,
        "file_name": launch_file,
        "setup_files": setup_files,
        "launch": launch,
        "requires_session": requires_session,
        "expects_exit": expects_exit,
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
        if c["requires_session"]:
            lines.append('        "requiresSession": True,')
        if c["expects_exit"]:
            lines.append('        "expectsExit": True,')
        if len(c["setup_files"]) > 1:
            lines.append(f'        "fileName": {c["file_name"]!r},')
            lines.append(f'        "setupFiles": {c["setup_files"]!r},')
            if c["launch"]:
                lines.append(f'        "launch": {c["launch"]!r},')
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
