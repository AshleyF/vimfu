"""
Lesson 066: Block Visual Mode

Sub-60-second lesson: Ctrl-V selects a rectangular block (columns).
Move the cursor and a box of text gets highlighted.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Block Visual Mode",
    description="Ctrl-V selects a rectangular block of text. "
                "Move the cursor and a box gets highlighted.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=207,
    tts_voice="echo",
    borderless=True,
    playlist="VimFu",

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Prepare workspace"),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Line("rm -f grid.py .grid.py.swp .grid.py.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*grid.py*"),
        Comment("Create demo file — aligned data grid"),
        WriteFile("grid.py", """
            # score board
            alice  = 100
            bob    = 200
            carol  = 300
            dave   = 400
            eve    = 500
        """),
        Line("clear"),
        Comment("Launch nvim before recording"),
        Line("nvim grid.py"),
        WaitForScreen("All", timeout=30.0),  # nvim status bar, not heredoc
        IfScreen("swap file", "d"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Block Visual Mode", duration=3.0),
        Wait(0.7),

        # --- Intro ---
        Say("Control V starts block visual mode. It selects a rectangle, not lines or characters.", wait=True),
        Wait(0.3),

        # --- Demo 1: select a column of names ---
        Say("Go to the alice line. Control V to start the block.", wait=False),
        Wait(0.3),
        Keys("j"),          # alice = 100
        Wait(0.3),
        Keys("\x16"),       # Ctrl-V: block visual mode
        Wait(0.5),

        Say("Now J four times to extend down through all the names.", wait=False),
        Wait(0.3),
        Keys("j"),
        Keys("j"),
        Keys("j"),
        Keys("j"),          # extend down to eve
        Wait(0.6),

        Say("A thin column selected. Now E to widen it across the names.", wait=False),
        Wait(0.3),
        Keys("e"),          # extend to end of each name
        Wait(0.6),

        Say("A perfect rectangle. Five names in a block. No other mode can do this.", wait=True),
        Wait(0.3),

        Escape(),
        Wait(0.3),

        # --- Demo 2: select the numbers column ---
        Say("Now select just the numbers. Go to the first score.", wait=False),
        Wait(0.3),
        Keys("g"),
        Keys("g"),          # top
        Keys("j"),          # alice line
        Keys("$"),          # end of line: on "0" of 100
        Wait(0.3),

        Say("Control V, then J four times.", wait=False),
        Wait(0.3),
        Keys("\x16"),       # Ctrl-V
        Keys("j"),
        Keys("j"),
        Keys("j"),
        Keys("j"),          # extend down
        Wait(0.6),

        Say("Just the last digit of each score. A column selection.", wait=True),
        Wait(0.3),

        # --- Delete the block ---
        Say("D to delete the column.", wait=False),
        Wait(0.3),
        Keys("d"),          # delete the block
        Wait(0.6),

        Say("Only that column is gone. The rest of the lines stay intact.", wait=True),
        Wait(0.3),

        Keys("u"),          # undo
        Wait(0.3),

        # --- Wrap up ---
        Say("Control V. Block visual mode. Select rectangles, edit columns.", wait=True),
        Wait(1.5),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f grid.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
