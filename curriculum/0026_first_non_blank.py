"""
Lesson 026: First Non-Blank

Sub-60-second lesson: Press ^ (caret) to jump to the first non-whitespace
character on the line. Smarter than 0 when code is indented.
"""

import sys
from pathlib import Path

# ShellPilot DSL imports
sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — First Non-Blank",
    description="Press ^ (caret) to jump to the first non-whitespace character. "
                "Smarter than 0 for indented code.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=117,
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
        Comment("Create a file with indented code"),
        WriteFile("greet.py", """
            def greet(name):
                msg = f"Hello {name}"
                print(msg)
        """),
        Line("clear"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="First Non-Blank", duration=3.0),
        Wait(0.7),

        # --- Open file ---
        Say("Zero goes to column zero. But with indented code, that's a space.", wait=True),
        Line("nvim greet.py", delay=0.05),
        WaitForScreen("greet", timeout=10.0),
        IfScreen("swap file", "d"),
        Wait(0.5),

        # --- Show 0 on an indented line ---
        Keys("j"),       # down to line 2: "    msg = ..."
        Keys("$"),       # end of line
        Wait(0.3),
        Keys("0"),       # column 0 — lands on the space
        Wait(0.5),

        Say("See? Cursor's on a space. Not very useful.", wait=True),
        Wait(0.3),

        # --- Now show ^ ---
        Keys("$"),       # go back to end of line
        Wait(0.3),
        Say("Caret jumps to the first real character.", wait=False),
        Wait(0.3),
        Keys("^"),       # first non-blank — lands on 'm' of 'msg'
        Wait(0.6),

        Say("Skips the spaces. Lands right on the code."),
        Wait(0.3),

        # --- Try on line 3 ---
        Say("Works on every indented line.", wait=False),
        Wait(0.3),
        Keys("j"),       # down to "    print(msg)"
        Keys("$"),       # end of line
        Wait(0.3),
        Keys("^"),       # first non-blank — lands on 'p' of 'print'
        Wait(0.6),

        # --- Back to line 1 to show it's same as 0 when no indent ---
        Keys("g"),
        Keys("g"),       # back to line 1: "def greet(name):"
        Keys("$"),       # end of line
        Wait(0.3),
        Say("On a line with no indent, caret and zero do the same thing.", wait=False),
        Wait(0.3),
        Keys("^"),       # lands on 'd' of 'def' — same as column 0
        Wait(0.6),

        # --- Wrap up ---
        Say("Caret for the first real character. Zero for column zero."),
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
