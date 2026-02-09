"""
Lesson 048: Next Match

Sub-60-second lesson: After a search, press n to jump to the next
match in the same direction.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Next Match",
    description="After a search, press n to jump to the next match "
                "in the same direction.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=189,
    tts_voice="echo",
    borderless=True,
    playlist="VimFu",

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Prepare workspace"),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Line("rm -f words.py .words.py.swp .words.py.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*words.py*"),
        Comment("Create demo file"),
        WriteFile("words.py", """
            cat = "meow"
            dog = "woof"
            cat = "purr"
            dog = "bark"
            cat = "hiss"
            dog = "howl"
        """),
        Line("clear"),
        Comment("Launch nvim before recording"),
        Line("nvim words.py"),
        WaitForScreen("cat", timeout=10.0),
        IfScreen("swap file", "d"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Next Match", duration=3.0),
        Wait(0.7),

        # --- Intro ---
        Say("After a search, N jumps to the next match. No need to type the pattern again.", wait=True),
        Wait(0.3),

        # --- Search for "cat" ---
        Say("Let's search for cat.", wait=False),
        Wait(0.3),
        Keys("/"),
        Type("cat"),
        Enter(),            # lands on line 2 (next cat forward from line 0)
        Wait(0.5),

        Say("Found a cat. There are three in this file."),
        Wait(0.3),

        # --- Press n to cycle through matches ---
        Say("Press N to jump to the next one.", wait=False),
        Wait(0.3),
        Keys("n"),          # next cat — line 4
        Wait(0.5),

        Say("There's the next cat."),
        Wait(0.3),

        # --- n wraps around ---
        Say("N again. Watch it wrap back to the top.", wait=False),
        Wait(0.3),
        Keys("n"),          # wraps to line 0
        Wait(0.6),

        Say("Wrapped around. N cycles through every match in the file."),
        Wait(0.3),

        # --- Wrap up ---
        Say("Search once with slash. Then N, N, N to hop through every match."),
        Wait(1.5),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f words.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
