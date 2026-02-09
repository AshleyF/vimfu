"""
Lesson 011: Undo

Sub-60-second lesson: Press u in normal mode to undo.
Keep pressing it to undo more. Simple as that.
"""

import sys
from pathlib import Path

# ShellPilot DSL imports
sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Undo",
    description="Press u to undo in Vim. Keep pressing it to undo more. "
                "Made a mistake? Just hit u.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=52,
    tts_voice="echo",
    borderless=True,
    playlist="VimFu",

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Prepare workspace"),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Line("rm -f hello.py .hello.py.swp .hello.py.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*hello.py*"),
        Comment("Create a starter file"),
        WriteFile("hello.py", """
            print("hello")
            print("world")
            print("done")
        """),
        Line("clear"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Undo", duration=3.0),
        Wait(0.7),

        # --- Open file ---
        Say("You're going to make mistakes. That's fine.", wait=False),
        Line("nvim hello.py", delay=0.05),
        WaitForScreen("hello", timeout=10.0),
        IfScreen("swap file", "d"),
        Wait(0.5),

        Say("Here's a file with three lines. Let's break it."),

        # --- Make some destructive edits ---
        Say("Delete a line with D D.", wait=False),
        Wait(0.3),
        Keys("dd"),
        Wait(0.5),

        Say("Delete another.", wait=False),
        Wait(0.3),
        Keys("dd"),
        Wait(0.5),

        Say("Yikes. Two lines gone."),

        # --- Undo! ---
        Say("Press U to undo.", wait=False),
        Wait(0.3),
        Keys("u"),
        Wait(0.5),

        Say("One line is back."),

        Say("U again.", wait=False),
        Wait(0.3),
        Keys("u"),
        Wait(0.5),

        Say("Both lines restored. U just walks backwards through your changes."),

        # --- One more demo: undo typed text ---
        Say("It works for typing too.", wait=False),
        Wait(0.2),
        Keys("o"),
        Wait(0.3),
        Type("this is a mistake"),
        Wait(0.3),
        Escape(),
        Wait(0.3),

        Say("Undo.", wait=False),
        Wait(0.3),
        Keys("u"),
        Wait(0.5),

        Say("Gone. Press U whenever something goes wrong. "
            "You can press it as many times as you need."),
        Wait(1.5),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f hello.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
