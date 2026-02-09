"""
Lesson 029: Go to Bottom of File

Sub-60-second lesson: Press G (capital G) to jump to the last line.
The partner of gg — instant teleport to the bottom.
"""

import sys
from pathlib import Path

# ShellPilot DSL imports
sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Go to Bottom of File",
    description="Press G (capital G) to jump to the last line. "
                "The partner of gg — instant teleport to the bottom.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=150,
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
        Overlay("VimFu", caption="Go to Bottom", duration=3.0),
        Wait(0.7),

        # --- Open file ---
        Say("G G takes you to the top.", wait=True),
        Line("nvim app.py", delay=0.05),
        WaitForScreen("import", timeout=10.0),
        IfScreen("swap file", "d"),
        Wait(0.5),

        # --- Demonstrate G ---
        Say("Capital G takes you to the bottom.", wait=False),
        Wait(0.3),
        # Cursor starts at (0,0) on 'import os'
        Keys("G"),       # jump to last line
        Wait(0.6),

        Say("Last line of the file. One keypress."),
        Wait(0.3),

        # --- Bounce between top and bottom ---
        Say("G G for the top. Shift G for the bottom.", wait=False),
        Wait(0.3),
        Keys("g"),
        Keys("g"),       # back to top
        Wait(0.5),
        Keys("G"),       # back to bottom
        Wait(0.5),
        Keys("g"),
        Keys("g"),       # back to top
        Wait(0.5),
        Keys("G"),       # back to bottom
        Wait(0.5),

        Say("Top. Bottom. Top. Bottom. Instant."),
        Wait(0.3),

        # --- Wrap up ---
        Say("Shift G for the bottom. G G for the top. Memorize the pair."),
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
