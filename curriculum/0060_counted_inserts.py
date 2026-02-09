"""
Lesson 060: Counted Inserts

Sub-60-second lesson: A count before insert mode repeats your text.
5i- then Escape gives five dashes. 3o adds three identical lines.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Counted Inserts",
    description="A count before insert mode repeats your text. "
                "5i- then Escape gives five dashes. 3o adds three lines.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=201,
    tts_voice="echo",
    borderless=True,
    playlist="VimFu",

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Prepare workspace"),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Line("rm -f ship.py .ship.py.swp .ship.py.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*ship.py*"),
        Comment("Create demo file — spaceship parts"),
        WriteFile("ship.py", """
            # spaceship parts

            engine = 1
            shield = 1
            laser = 1
        """),
        Line("clear"),
        Comment("Launch nvim before recording"),
        Line("nvim ship.py"),
        WaitForScreen("spaceship", timeout=10.0),
        IfScreen("swap file", "d"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Counted Inserts", duration=3.0),
        Wait(0.7),

        # --- Intro ---
        Say("A count before I repeats your insert. The multiplier for insert mode.", wait=True),
        Wait(0.3),

        # --- Demo 1: 20i- Esc on blank line ---
        Say("This blank line needs a separator. Twenty I dash Escape.", wait=False),
        Wait(0.3),
        Keys("j"),          # row 1: blank line
        Wait(0.3),
        Keys("2"),
        Keys("0"),
        Keys("i"),          # insert mode with count 20
        Keys("-"),           # type a dash
        Escape(),           # Escape — 20 dashes appear
        Wait(0.6),

        Say("Twenty dashes. One keystroke, twenty characters. Vim repeated the dash twenty times.", wait=True),
        Wait(0.3),

        # --- Undo ---
        Say("Undo.", wait=False),
        Wait(0.3),
        Keys("u"),
        Wait(0.5),

        # --- Demo 2: 3o to add 3 lines ---
        Say("Now three O. It opens three new lines and enters insert mode.", wait=False),
        Wait(0.3),
        Keys("G"),          # last line: laser = 1
        Wait(0.3),
        Keys("3"),
        Keys("o"),          # open line below, insert mode, count 3
        Type("fuel = 0"),   # type on the new line
        Escape(),           # Escape — text appears on 3 lines
        Wait(0.6),

        Say("Three identical lines. Type once, Vim copies it three times.", wait=True),
        Wait(0.3),

        # --- Undo ---
        Say("Undo.", wait=False),
        Wait(0.3),
        Keys("u"),
        Wait(0.5),

        # --- Demo 3: 5i* for quick decoration ---
        Say("One more. Five I star Escape.", wait=False),
        Wait(0.3),
        Keys("g"),
        Keys("g"),          # top of file
        Keys("j"),          # row 1: blank line
        Wait(0.3),
        Keys("5"),
        Keys("i"),
        Keys("*"),
        Escape(),           # 5 stars
        Wait(0.6),

        Say("Five stars. Works with any character, any count.", wait=True),
        Wait(0.3),

        Keys("u"),          # undo
        Wait(0.3),

        # --- Wrap up ---
        Say("Count, I, type, Escape. Build patterns instantly.", wait=True),
        Wait(1.5),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f ship.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
