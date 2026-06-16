"""Scan shellpilot video logs for the 'recording started before setup
completed' bug — where the screen snapshot at [RECORDING_START] still
shows setup-command text instead of the post-setup app state.

We only flag commands that are unambiguously setup-only and should never
appear in a real demo (mkdir / export / find / rm). Tmux demos legitimately
start at a shell prompt with a tmux command visible, so a bare prompt
isn't enough on its own.

Run from anywhere::

    python shellpilot/scan_early_recordings.py
"""
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
VROOT = REPO_ROOT / "videos"

# Setup-only tokens — these should never appear on the first recorded
# frame. They're commands the JSON `setup` block runs before recording
# starts to prepare the workspace. If they're still visible, the
# recording started too early.
SETUP_ONLY_TOKENS = (
    "mkdir -p ~/vimfu",
    "export TERM=xterm",
    "find ~/.local",
    "rm -f ",
)


def main() -> None:
    suspects: list[tuple[str, list[str]]] = []
    total = 0
    for d in sorted(p for p in VROOT.iterdir() if p.is_dir()):
        log = d / f"{d.name}.log"
        if not log.exists():
            continue
        total += 1
        text = log.read_text(encoding="utf-8", errors="replace")
        m = re.search(
            r"\[RECORDING_START\] Screen state at recording start:(.*?)\[",
            text, re.S,
        )
        if not m:
            continue
        snap = m.group(1)
        flags = sorted({t.strip() for t in SETUP_ONLY_TOKENS if t in snap})
        if flags:
            suspects.append((d.name, flags))
    print(f"Scanned {total} logs; {len(suspects)} suspect.")
    for name, flags in suspects:
        joined = ", ".join(flags)
        print(f"  {name}  ->  {joined}")


if __name__ == "__main__":
    main()

