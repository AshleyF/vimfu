"""
Lesson 028: Go to Top of File

Sub-60-second lesson: Press gg to jump to line 1.
Instant teleport to the top of any file.
"""

import sys
from pathlib import Path

# ShellPilot DSL imports
sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Go to Top of File",
    description="Press gg to jump to line 1. "
                "Instant teleport to the top of any file.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=139,
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
        Overlay("VimFu", caption="Go to Top", duration=3.0),
        Wait(0.7),

        # --- Open file ---
        Say("Big files mean lots of scrolling.", wait=True),
        Line("nvim app.py", delay=0.05),
        WaitForScreen("import", timeout=10.0),
        IfScreen("swap file", "d"),
        Wait(0.5),

        # --- Move down to the bottom ---
        Say("Let's go to the bottom first.", wait=False),
        Wait(0.3),
        Keys("G"),       # jump to last line
        Wait(0.6),

        Say("Now we're at the end of the file."),
        Wait(0.3),

        # --- Demonstrate gg ---
        Say("Press G G to teleport to the top.", wait=False),
        Wait(0.3),
        Keys("g"),
        Keys("g"),       # jump to line 1
        Wait(0.6),

        Say("Instant. Line one."),
        Wait(0.3),

        # --- Do it again ---
        Say("No matter where you are. G G. Top of file.", wait=False),
        Wait(0.3),
        Keys("G"),       # back to bottom
        Wait(0.4),
        Keys("g"),
        Keys("g"),       # back to top
        Wait(0.6),

        Say("You'll use this all the time."),
        Wait(0.3),

        # --- Wrap up ---
        Say("G G for the top. Capital G for the bottom. That's next."),
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
