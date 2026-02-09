"""
Lesson 014: Why Not Arrow Keys?

Sub-60-second lesson: Arrow keys work in Vim, but they move
your hands off the home row. h j k l keeps you faster.
"""

import sys
from pathlib import Path

# ShellPilot DSL imports
sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Why Not Arrow Keys?",
    description="Arrow keys work in Vim, but they pull your hands off "
                "the home row. Train yourself to use h j k l instead.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=55,
    tts_voice="echo",
    borderless=True,
    playlist="VimFu",

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Prepare workspace"),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Line("rm -f moves.py .moves.py.swp .moves.py.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*moves.py*"),
        Comment("Create a file with several lines"),
        WriteFile("moves.py", """
            apples = 10
            bananas = 20
            cherries = 30
            dates = 40
        """),
        Line("clear"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Why Not Arrow Keys?", duration=3.0),
        Wait(0.7),

        # --- Open file ---
        Say("Arrow keys work in Vim. Let's prove it.", wait=False),
        Line("nvim moves.py", delay=0.05),
        WaitForScreen("apples", timeout=10.0),
        IfScreen("swap file", "d"),
        Wait(0.5),

        # --- Demo arrow keys ---
        Say("Down, down, right, right, up.", wait=False),
        Wait(0.3),
        Keys("\x1b[B"),  # Down arrow
        Wait(0.3),
        Keys("\x1b[B"),  # Down
        Wait(0.3),
        Keys("\x1b[C"),  # Right
        Wait(0.3),
        Keys("\x1b[C"),  # Right
        Wait(0.3),
        Keys("\x1b[A"),  # Up
        Wait(0.5),

        Say("They work fine. So why not use them?"),

        Say("Because your right hand has to leave the home row. "
            "Every time you reach for an arrow key, you lose your position."),

        # --- Now with h j k l ---
        Say("With H J K L, your fingers never move.", wait=False),
        Wait(0.3),
        Keys("j"),
        Wait(0.2),
        Keys("j"),
        Wait(0.2),
        Keys("l"),
        Wait(0.2),
        Keys("l"),
        Wait(0.2),
        Keys("k"),
        Wait(0.5),

        Say("Same moves. Faster. No reaching."),

        # --- The point ---
        Say("Arrow keys are a crutch. H J K L is a habit. "
            "Start building it now."),
        Wait(1.5),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f moves.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
