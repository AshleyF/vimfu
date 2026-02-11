"""
Lesson 069: Other Corner

Sub-60-second lesson: In visual mode, press o to jump the cursor
to the other end of the selection. O moves to the other corner
in block visual mode.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Other Corner",
    description="In visual mode, press o to jump the cursor to the other end "
                "of the selection. O moves to the other corner in block mode.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=210,
    tts_voice="echo",
    borderless=True,
    playlist="VimFu",

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Prepare workspace"),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Line("rm -f farm.py .farm.py.swp .farm.py.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*farm.py*"),
        Comment("Create demo file — farm inventory"),
        WriteFile("farm.py", """
            # farm inventory
            wheat = 100
            corn  = 200
            rice  = 300
            oats  = 400
            hay   = 500
        """),
        Line("clear"),
        Comment("Launch nvim before recording"),
        Line("nvim farm.py"),
        WaitForScreen("All", timeout=30.0),  # nvim status bar, not heredoc
        IfScreen("swap file", "d"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Other Corner", duration=3.0),
        Wait(0.7),

        # --- Intro ---
        Say("In visual mode, O jumps the cursor to the other end of the selection.", wait=True),
        Wait(0.3),

        # --- Demo 1: v select, then o to flip ---
        Say("Start on the wheat line. V then dollar sign to select to the end.", wait=False),
        Wait(0.3),
        Keys("j"),          # wheat = 100
        Wait(0.3),
        Keys("v"),          # character visual
        Keys("$"),          # select to end of line
        Wait(0.5),

        Say("Cursor is at the end. Press O.", wait=False),
        Wait(0.3),
        Keys("o"),          # flip to other end
        Wait(0.6),

        Say("Cursor jumped to the start of the selection. Notice that the cursor and the selection are separate. The cursor moves inside the selection without changing it.", wait=True),
        Wait(0.3),

        Say("Press O again.", wait=False),
        Wait(0.3),
        Keys("o"),          # flip back
        Wait(0.5),

        Say("Back at the end. Toggle freely.", wait=True),
        Wait(0.3),

        Escape(),
        Wait(0.3),

        # --- Demo 2: V line mode, o to flip ---
        Say("Capital V on corn, then J J to select three lines.", wait=False),
        Wait(0.3),
        Keys("j"),          # corn
        Keys("V"),          # line visual
        Keys("j"),
        Keys("j"),          # corn + rice + oats
        Wait(0.5),

        Say("Cursor is on the oats line. Press O to flip to the corn line.", wait=False),
        Wait(0.3),
        Keys("o"),          # flip to other end
        Wait(0.6),

        Say("Now extend the selection upward with K.", wait=False),
        Wait(0.3),
        Keys("k"),          # extend up to wheat
        Wait(0.6),

        Say("That is the trick. Flip ends, then extend in the other direction.", wait=True),
        Wait(0.3),

        Escape(),
        Wait(0.3),

        # --- Demo 3: block visual, O to flip corners ---
        Say("Control V for a block. Select down and right.", wait=False),
        Wait(0.3),
        Keys("g"),
        Keys("g"),
        Keys("j"),          # wheat line
        Keys("0"),          # reset to col 0 (cursor inherits col from previous demo)
        Keys("\x16"),       # Ctrl-V block visual
        Keys("j"),
        Keys("j"),          # extend down
        Keys("e"),          # extend to end of name
        Wait(0.5),

        Say("Capital O flips to the other corner on the same row.", wait=False),
        Wait(0.3),
        Keys("O"),          # flip horizontal corner (capital O in block mode)
        Wait(0.6),

        Say("Lowercase O flips vertically. Capital O flips horizontally in block mode.", wait=True),
        Wait(0.3),

        Escape(),
        Wait(0.3),

        # --- Wrap up ---
        Say("O in visual mode. Flip the cursor, then adjust the selection from either end.", wait=True),
        Wait(1.5),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f farm.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
