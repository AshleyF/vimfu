"""
Lesson 044: The dd-p Swap Trick

Sub-60-second lesson: ddp swaps two lines by deleting and pasting.
xp swaps two adjacent characters.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — The dd-p Swap Trick",
    description="ddp swaps two lines by deleting and pasting below. "
                "xp swaps two adjacent characters.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=185,
    tts_voice="echo",
    borderless=True,
    playlist="VimFu",

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Prepare workspace"),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Line("rm -f order.py .order.py.swp .order.py.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*order.py*"),
        Comment("Create demo file"),
        WriteFile("order.py", """
            beta = 2
            alpha = 1
            delta = 3
            tset = 4
        """),
        Line("clear"),
        Comment("Launch nvim before recording"),
        Line("nvim order.py"),
        WaitForScreen("beta", timeout=10.0),
        IfScreen("swap file", "d"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="The dd-p Swap Trick", duration=3.0),
        Wait(0.7),

        # --- Intro ---
        Say("D D P is the line swap trick. Delete a line, then put it back below.", wait=True),
        Wait(0.3),

        # --- ddp demo: swap beta down, alpha comes to top ---
        Say("Beta is on line one. Let's move it down.", wait=False),
        Wait(0.3),
        Keys("d"),
        Keys("d"),       # dd — delete "beta = 2"
        Wait(0.3),
        Keys("p"),       # p — paste below "alpha = 1"
        Wait(0.6),

        Say("Alpha is first now. D D then P swapped the lines."),
        Wait(0.3),

        # --- Undo ---
        Keys("u"),       # undo p
        Keys("u"),       # undo dd
        Wait(0.3),

        # --- Mention ddP ---
        Say("Capital P would put it above instead. Same idea, opposite direction.", wait=True),
        Wait(0.3),

        # --- xp demo: fix tset → test ---
        Say("X P swaps two characters. Great for fixing typos.", wait=False),
        Wait(0.3),
        Keys("j"),       # line 1: alpha = 1
        Keys("j"),       # line 2: delta = 3
        Keys("j"),       # line 3: tset = 4
        Keys("l"),       # col 1: 's' in tset
        Keys("x"),       # delete 's'
        Wait(0.3),
        Keys("p"),       # paste 's' after 'e' → "test = 4"
        Wait(0.6),

        Say("T S E T is now test. X deletes a character, P puts it right back."),
        Wait(0.3),

        # --- Wrap up ---
        Say("D D P to swap lines. X P to swap characters. Two handy combos."),
        Wait(1.5),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f order.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
