"""
Lesson 057: Repeat Find Reverse

Sub-60-second lesson: Press comma to repeat the last f/F/t/T in the
opposite direction. Went too far? Comma brings you back.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Repeat Find Reverse",
    description="Press comma to repeat the last f/F/t/T in the opposite "
                "direction. Semicolon goes forward, comma goes back.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=198,
    tts_voice="echo",
    borderless=True,
    playlist="VimFu",

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Prepare workspace"),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Line("rm -f paths.py .paths.py.swp .paths.py.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*paths.py*"),
        Comment("Create demo file — Unix paths"),
        WriteFile("paths.py", """
            path = "/usr/bin/vim/share/doc"
            home = "/home/user/.config/nvim"
        """),
        Line("clear"),
        Comment("Launch nvim before recording"),
        Line("nvim paths.py"),
        WaitForScreen("path", timeout=10.0),
        IfScreen("swap file", "d"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Repeat Find Reverse", duration=3.0),
        Wait(0.7),

        # --- Intro ---
        Say("Comma reverses the last find. If semicolon goes forward, comma brings you back.", wait=True),
        Wait(0.3),

        # --- Demo 1: f/ then ; forward, then , backward ---
        Say("F slash to find the first slash.", wait=False),
        Wait(0.3),
        Keys("f"),
        Keys("/"),          # first '/' at col 8
        Wait(0.5),

        Say("Semicolon to hop forward through the slashes.", wait=False),
        Wait(0.3),
        Keys(";"),          # col 12
        Wait(0.3),
        Keys(";"),          # col 16
        Wait(0.3),
        Keys(";"),          # col 20
        Wait(0.5),

        Say("Three hops forward. Now comma to reverse.", wait=False),
        Wait(0.3),
        Keys(","),          # back to col 16
        Wait(0.4),

        Say("Back one.", wait=False),
        Wait(0.3),
        Keys(","),          # back to col 12
        Wait(0.4),

        Say("Back again. Comma walks backward through the same matches.", wait=True),
        Wait(0.3),

        # --- Demo 2: line 2, show the same pattern ---
        Say("Next line. F slash, then semicolon, semicolon.", wait=False),
        Wait(0.3),
        Keys("j"),
        Keys("0"),
        Wait(0.3),
        Keys("f"),
        Keys("/"),          # first '/' at col 8
        Wait(0.3),
        Keys(";"),          # col 13
        Wait(0.3),
        Keys(";"),          # col 18
        Wait(0.5),

        Say("Too far. Comma.", wait=False),
        Wait(0.3),
        Keys(","),          # back to col 13
        Wait(0.5),

        Say("Right where we wanted. Comma is the undo for semicolon.", wait=True),
        Wait(0.3),

        # --- Wrap up ---
        Say("Semicolon forward, comma backward. Find once, navigate forever.", wait=True),
        Wait(1.5),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f paths.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
