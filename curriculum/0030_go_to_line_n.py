"""
Lesson 030: Go to Line N

Sub-60-second lesson: Type :N (colon + number) or NG to jump to a specific line.
Two ways to teleport to any line number.
"""

import sys
from pathlib import Path

# ShellPilot DSL imports
sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Go to Line N",
    description="Type :N or NG to jump to a specific line number. "
                "Two ways to teleport anywhere in a file.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=161,
    tts_voice="echo",
    borderless=True,
    playlist="VimFu",

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Prepare workspace"),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Line("rm -f app.py .app.py.swp .app.py.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*app.py*"),
        Comment("Create a longer file"),
        WriteFile("app.py", """
            import os
            import sys

            def setup():
                path = os.getcwd()
                return path

            def main():
                base = setup()
                name = "vimfu"
                print(f"Running {name}")
                print(f"Path: {base}")
                return 0

            if __name__ == "__main__":
                sys.exit(main())
        """),
        Line("clear"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Go to Line N", duration=3.0),
        Wait(0.7),

        # --- Open file ---
        Say("Sometimes you know exactly which line you need.", wait=True),
        Line("nvim app.py", delay=0.05),
        WaitForScreen("import", timeout=10.0),
        IfScreen("swap file", "d"),
        Wait(0.5),

        # --- Turn on line numbers ---
        Say("First, let's turn on line numbers.", wait=False),
        Wait(0.3),
        Type(":set number"),
        Enter(),
        Wait(0.5),

        Say("Now you can see exactly where you are."),
        Wait(0.3),

        # --- Demonstrate :N ---
        Say("Type colon, then a line number.", wait=False),
        Wait(0.3),
        Type(":8"),
        Enter(),
        Wait(0.6),

        Say("Line eight. The main function."),
        Wait(0.3),

        # --- Jump to another line ---
        Say("Colon twelve.", wait=False),
        Wait(0.3),
        Type(":12"),
        Enter(),
        Wait(0.6),

        Say("Line twelve. Right to the print statement."),
        Wait(0.3),

        # --- Demonstrate NG method ---
        Say("There's an even faster way. Type the number, then shift G.", wait=False),
        Wait(0.3),
        Keys("1"),
        Keys("G"),       # 1G — jump to line 1
        Wait(0.6),

        Say("One G. Back to the top."),
        Wait(0.3),

        # --- Another NG jump ---
        Say("Five G.", wait=False),
        Wait(0.3),
        Keys("5"),
        Keys("G"),       # 5G — jump to line 5
        Wait(0.6),

        Say("Line five. Two ways to jump to any line."),
        Wait(0.3),

        # --- Wrap up ---
        Say("Colon N or N G. Pick your favorite."),
        Wait(1.5),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f app.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
