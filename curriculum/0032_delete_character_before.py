"""
Lesson 032: Delete Character Before

Sub-60-second lesson: Press X (capital X) to delete the character before
the cursor. Like backspace, but in normal mode.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Delete Character Before",
    description="Press X (capital X) to delete the character before the cursor. "
                "Like backspace, but in normal mode.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=183,
    tts_voice="echo",
    borderless=True,
    playlist="VimFu",

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Prepare workspace"),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Line("rm -f typo.py .typo.py.swp .typo.py.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*typo.py*"),
        Comment("Create a file with a typo"),
        WriteFile("typo.py", """
            priint("hello")
            priint("world")
        """),
        Line("clear"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Delete Char Before", duration=3.0),
        Wait(0.7),

        # --- Open file ---
        Say("Lowercase X deletes under the cursor.", wait=True),
        Line("nvim typo.py", delay=0.05),
        WaitForScreen("priint", timeout=10.0),
        IfScreen("swap file", "d"),
        Wait(0.5),

        # --- Navigate to the second 'i' ---
        Say("Capital X deletes before the cursor. Like backspace.", wait=False),
        Wait(0.3),
        Keys("f"),
        Keys("i"),       # find first 'i' → on first i of priint
        Keys("l"),       # move right to second 'i'
        Wait(0.3),

        # --- Demonstrate X ---
        Say("Cursor's on the second I. Shift X deletes the one before it.", wait=False),
        Wait(0.3),
        Keys("X"),       # delete the 'i' before cursor
        Wait(0.6),

        Say("The character behind the cursor is gone."),
        Wait(0.3),

        # --- Fix the second line too ---
        Say("Same fix on line two.", wait=False),
        Wait(0.3),
        Keys("j"),       # down to line 2
        Keys("0"),       # start
        Keys("f"),
        Keys("i"),       # first 'i'
        Keys("l"),       # second 'i'
        Wait(0.3),
        Keys("X"),       # delete before cursor
        Wait(0.6),

        Say("Shift X. Backspace without leaving normal mode."),
        Wait(0.3),

        # --- Wrap up ---
        Say("Lowercase X deletes forward. Shift X deletes backward."),
        Wait(1.5),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f typo.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
