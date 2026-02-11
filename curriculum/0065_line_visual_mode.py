"""
Lesson 065: Line Visual Mode

Sub-60-second lesson: Capital V selects whole lines at a time.
Move up or down and entire lines get highlighted.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Line Visual Mode",
    description="Capital V selects whole lines at a time. "
                "Move up or down and entire lines get highlighted.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=206,
    tts_voice="echo",
    borderless=True,
    playlist="VimFu",

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Prepare workspace"),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Line("rm -f crew.py .crew.py.swp .crew.py.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*crew.py*"),
        Comment("Create demo file — spaceship crew roster"),
        WriteFile("crew.py", """
            # crew roster
            pilot = "Nova"
            medic = "Patch"
            hacker = "Glitch"
            gunner = "Boom"
            cook = "Pepper"
        """),
        Line("clear"),
        Comment("Launch nvim before recording"),
        Line("nvim crew.py"),
        WaitForScreen("All", timeout=30.0),  # nvim status bar, not heredoc
        IfScreen("swap file", "d"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Line Visual Mode", duration=3.0),
        Wait(0.7),

        # --- Intro ---
        Say("Capital V selects whole lines. Not characters, entire lines.", wait=True),
        Wait(0.3),

        # --- Demo 1: V to select one line ---
        Say("On the pilot line. Capital V.", wait=False),
        Wait(0.3),
        Keys("j"),          # pilot = "Nova"
        Wait(0.3),
        Keys("V"),          # line visual mode
        Wait(0.6),

        Say("The whole line is highlighted. Even if the cursor is in the middle.", wait=True),
        Wait(0.3),

        Escape(),
        Wait(0.3),

        # --- Demo 2: V then j j to select multiple lines ---
        Say("Capital V again, then J J to extend down.", wait=False),
        Wait(0.3),
        Keys("V"),          # line visual mode
        Wait(0.3),
        Keys("j"),          # select pilot + medic
        Keys("j"),          # select pilot + medic + hacker
        Wait(0.6),

        Say("Three whole lines selected. Perfect for deleting or moving a block of code.", wait=True),
        Wait(0.3),

        # --- Demo 2b: delete the selection ---
        Say("D to delete them all.", wait=False),
        Wait(0.3),
        Keys("d"),          # delete 3 lines
        Wait(0.6),

        Say("Three lines gone in one shot.", wait=True),
        Wait(0.3),

        # --- Undo ---
        Say("Undo.", wait=False),
        Wait(0.3),
        Keys("u"),
        Wait(0.5),

        # --- Demo 3: V then k to select upward ---
        Say("Go to the cook line. Capital V then K K to select upward.", wait=False),
        Wait(0.3),
        Keys("G"),          # last line: cook
        Wait(0.3),
        Keys("V"),          # line visual mode
        Wait(0.3),
        Keys("k"),
        Keys("k"),          # select cook + gunner + hacker
        Wait(0.6),

        Say("Three lines selected going up. Direction doesn't matter.", wait=True),
        Wait(0.3),

        Escape(),
        Wait(0.3),

        # --- Wrap up ---
        Say("Capital V for line visual mode. Select whole lines, then act.", wait=True),
        Wait(1.5),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f crew.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
