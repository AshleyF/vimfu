"""
Lesson 055: Till Character Backward

Sub-60-second lesson: Press capital T followed by a character to jump
backward to just after that character on the current line.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Till Character Backward",
    description="Press capital T followed by a character to jump backward to "
                "just after that character on the current line.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=196,
    tts_voice="echo",
    borderless=True,
    playlist="VimFu",

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Prepare workspace"),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Line("rm -f shop.py .shop.py.swp .shop.py.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*shop.py*"),
        Comment("Create demo file — magic item shop"),
        WriteFile("shop.py", """
            buy = shop("wand", 50, "rare")
            buy = shop("cape", 30, "epic")
            buy = shop("ring", 99, "myth")
        """),
        Line("clear"),
        Comment("Launch nvim before recording"),
        Line("nvim shop.py"),
        WaitForScreen("buy", timeout=10.0),
        IfScreen("swap file", "d"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Till Character Backward", duration=3.0),
        Wait(0.7),

        # --- Intro ---
        Say("Capital T searches backward but stops one short. The reverse of lowercase T.", wait=True),
        Wait(0.3),

        # --- Demo 1a: F( for contrast ---
        Say("Jump to the end of the line.", wait=False),
        Wait(0.3),
        Keys("$"),          # col 29 on ')'
        Wait(0.5),

        Say("Capital F open-paren for comparison.", wait=False),
        Wait(0.3),
        Keys("F"),
        Keys("("),          # backward to '(' at col 10
        Wait(0.6),

        Say("Capital F lands right on the paren.", wait=True),
        Wait(0.3),

        # --- Demo 1b: back to end, T( ---
        Say("Back to the end. Now capital T open-paren.", wait=False),
        Wait(0.3),
        Keys("$"),          # back to col 29
        Wait(0.3),
        Keys("T"),
        Keys("("),          # stops at col 11, one after '('
        Wait(0.6),

        Say("Stopped one past the paren. Capital T doesn't quite reach it.", wait=True),
        Wait(0.3),

        # --- Demo 2: T, on line 2 ---
        Say("Next line. Jump to the end.", wait=False),
        Wait(0.3),
        Keys("j"),
        Keys("$"),          # end of line 2
        Wait(0.3),

        Say("Capital T comma.", wait=False),
        Wait(0.3),
        Keys("T"),
        Keys(","),          # backward to one after ',' at col 21 → col 22
        Wait(0.6),

        Say("Stopped right after the comma. T always leaves one gap.", wait=True),
        Wait(0.3),

        # --- Demo 3: T( on line 3 ---
        Say("Last line. End of line. Capital T open-paren.", wait=False),
        Wait(0.3),
        Keys("j"),
        Keys("$"),          # end of line 3
        Wait(0.3),
        Keys("T"),
        Keys("("),          # backward to col 11
        Wait(0.6),

        Say("Same idea. One past the paren every time.", wait=True),
        Wait(0.3),

        # --- Wrap up ---
        Say("Lowercase F and T go forward. Capital F and T go backward. Lowercase stops before, capital stops after. Four precision tools.", wait=True),
        Wait(1.5),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f shop.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
