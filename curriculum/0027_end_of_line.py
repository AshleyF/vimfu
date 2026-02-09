"""
Lesson 027: End of Line

Sub-60-second lesson: Press $ (dollar sign) to jump to the last character
on the line. The opposite of 0.
"""

import sys
from pathlib import Path

# ShellPilot DSL imports
sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — End of Line",
    description="Press $ to jump to the last character on the line. "
                "The opposite of 0 — instant jump to the end.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=128,
    tts_voice="echo",
    borderless=True,
    playlist="VimFu",

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Prepare workspace"),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Line("rm -f greet.py .greet.py.swp .greet.py.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*greet.py*"),
        Comment("Create a file with some code"),
        WriteFile("greet.py", """
            def greet(name):
                msg = f"Hello {name}"
                print(msg)
        """),
        Line("clear"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="End of Line", duration=3.0),
        Wait(0.7),

        # --- Open file ---
        Say("Zero goes to the start of the line.", wait=True),
        Line("nvim greet.py", delay=0.05),
        WaitForScreen("greet", timeout=10.0),
        IfScreen("swap file", "d"),
        Wait(0.5),

        # --- Demonstrate $ on line 1 ---
        Say("Dollar sign goes to the end.", wait=False),
        Wait(0.3),
        # Cursor starts at (0,0) on 'def greet(name):'
        Keys("$"),       # end of line → ':'
        Wait(0.6),

        Say("Instant jump to the last character."),
        Wait(0.3),

        # --- Try on each line ---
        Say("Works on every line.", wait=False),
        Wait(0.3),
        Keys("j"),       # down to line 2
        Keys("0"),       # start of line
        Wait(0.2),
        Keys("$"),       # end of line
        Wait(0.5),

        Keys("j"),       # down to line 3
        Keys("0"),       # start of line
        Wait(0.2),
        Keys("$"),       # end of line
        Wait(0.5),

        Say("No matter how long the line is."),
        Wait(0.3),

        # --- Show 0 and $ as a pair ---
        Say("Zero and dollar. Start and end. Like bookends.", wait=False),
        Wait(0.3),
        Keys("g"),
        Keys("g"),       # back to line 1
        Keys("$"),       # end
        Wait(0.4),
        Keys("0"),       # start
        Wait(0.4),
        Keys("$"),       # end
        Wait(0.4),
        Keys("0"),       # start
        Wait(0.5),

        # --- Wrap up ---
        Say("Dollar sign for end of line. Pair it with zero."),
        Wait(1.5),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f greet.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
