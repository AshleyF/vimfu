"""
Lesson 059: Counted Deletes

Sub-60-second lesson: Put a count before delete to multiply it.
3dd deletes 3 lines. 2dw deletes 2 words.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Counted Deletes",
    description="Put a count before delete to multiply it. "
                "3dd deletes 3 lines, 2dw deletes 2 words.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=200,
    tts_voice="echo",
    borderless=True,
    playlist="VimFu",

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Prepare workspace"),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Line("rm -f robot.py .robot.py.swp .robot.py.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*robot.py*"),
        Comment("Create demo file — robot config with junk"),
        WriteFile("robot.py", """
            # robot config
            power = 100
            bug = "glitch"
            bug = "crash"
            bug = "lag"
            speed = 50
            junk = None
            junk = None
            armor = 75
        """),
        Line("clear"),
        Comment("Launch nvim before recording"),
        Line("nvim robot.py"),
        WaitForScreen("robot", timeout=10.0),
        IfScreen("swap file", "d"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Counted Deletes", duration=3.0),
        Wait(0.7),

        # --- Intro ---
        Say("Put a count before delete to multiply it. Clean up code in bulk.", wait=True),
        Wait(0.3),

        # --- Demo 1: 3dd to delete bug lines ---
        Say("Three bug lines need to go. Move to the first one.", wait=False),
        Wait(0.3),
        Keys("2"),
        Keys("j"),          # row 2: bug = "glitch"
        Wait(0.5),

        Say("Three D D.", wait=False),
        Wait(0.3),
        Keys("3"),
        Keys("d"),
        Keys("d"),          # delete 3 lines (rows 2-4)
        Wait(0.6),

        Say("All three bug lines gone in one move.", wait=True),
        Wait(0.3),

        # --- Demo 2: 2dd to delete junk lines ---
        Say("Two junk lines below. Move down.", wait=False),
        Wait(0.3),
        Keys("j"),          # now on junk = None (shifted after 3dd)
        Wait(0.3),

        Say("Two D D.", wait=False),
        Wait(0.3),
        Keys("2"),
        Keys("d"),
        Keys("d"),          # delete 2 lines
        Wait(0.6),

        Say("Both junk lines deleted. The file is clean.", wait=True),
        Wait(0.3),

        # --- Undo to restore ---
        Say("Undo twice to bring it all back.", wait=False),
        Wait(0.3),
        Keys("u"),
        Wait(0.4),
        Keys("u"),
        Wait(0.5),

        Say("Good as new.", wait=True),
        Wait(0.3),

        # --- Demo 3: 2dw to delete words ---
        Say("Counts work with D W too. Go to the power line.", wait=False),
        Wait(0.3),
        Keys("g"),
        Keys("g"),          # top of file
        Keys("j"),          # row 1: power = 100
        Wait(0.5),

        Say("Two D W deletes two words.", wait=False),
        Wait(0.3),
        Keys("2"),
        Keys("d"),
        Keys("w"),          # delete "power " and "= "
        Wait(0.6),

        Say("Two words gone. Just the value left.", wait=True),
        Wait(0.3),

        Say("Undo.", wait=False),
        Wait(0.3),
        Keys("u"),
        Wait(0.5),

        # --- Wrap up ---
        Say("Count plus delete. Three D D, two D W. Surgical bulk removal.", wait=True),
        Wait(1.5),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f robot.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
