"""
Lesson 025: Start of Line

Sub-60-second lesson: Press 0 to jump to column zero — the very first character.
No matter where you are on the line, 0 snaps you to the left edge.
"""

import sys
from pathlib import Path

# ShellPilot DSL imports
sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Start of Line",
    description="Press 0 to jump to column zero. "
                "Snaps to the very first character on the line.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=106,
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
        Overlay("VimFu", caption="Start of Line", duration=3.0),
        Wait(0.7),

        # --- Open file ---
        Say("Sometimes you just need to get to the beginning of a line.", wait=True),
        Line("nvim greet.py", delay=0.05),
        WaitForScreen("greet", timeout=10.0),
        IfScreen("swap file", "d"),
        Wait(0.5),

        # --- Move to somewhere in the middle of line 1 ---
        Keys("w"),       # jump a few words in
        Wait(0.2),
        Keys("w"),
        Wait(0.2),
        Keys("w"),
        Wait(0.3),

        # --- Demonstrate 0 ---
        Say("Press zero. Instant jump to column zero.", wait=False),
        Wait(0.3),
        Keys("0"),
        Wait(0.6),

        Say("No matter where you are. Zero snaps you to the left edge."),
        Wait(0.3),

        # --- Try on an indented line ---
        Say("Let's try an indented line.", wait=False),
        Wait(0.3),
        Keys("j"),       # down to line 2: "    msg = ..."
        Keys("$"),       # end of line
        Wait(0.3),
        Keys("0"),       # back to column 0 — the space before "msg"
        Wait(0.6),

        Say("Zero goes all the way to column zero. Even before the indent."),
        Wait(0.3),

        # --- Another indented line ---
        Keys("j"),       # down to line 3: "    print(msg)"
        Keys("$"),       # end of line
        Wait(0.3),
        Keys("0"),
        Wait(0.6),

        Say("Every time. Column zero."),
        Wait(0.3),

        # --- Wrap up ---
        Say("Zero for column zero. Even before the indent."),
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
