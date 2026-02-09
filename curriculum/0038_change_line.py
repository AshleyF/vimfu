"""
Lesson 038: Change Entire Line

Sub-60-second lesson: Press cc (or S) to delete the entire line's
contents and enter insert mode. Like dd but you stay on the line.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Change Entire Line",
    description="Press cc or S to delete the entire line's contents and enter "
                "insert mode. Like dd, but you stay on the line to type.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=179,
    tts_voice="echo",
    borderless=True,
    playlist="VimFu",

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Prepare workspace"),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Line("rm -f task.py .task.py.swp .task.py.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*task.py*"),
        Comment("Create a file with lines to rewrite"),
        WriteFile("task.py", """
            x = 1
            y = 2
            z = 3
        """),
        Line("clear"),
        Comment("Launch nvim before recording"),
        Line("nvim task.py"),
        WaitForScreen("x = 1", timeout=10.0),
        IfScreen("swap file", "d"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Change Entire Line", duration=3.0),
        Wait(0.7),

        # --- Intro ---
        Say("C C clears the whole line and drops you in insert mode.", wait=True),
        Wait(0.3),

        # --- Change line 1 ---
        Say("Let's rewrite line one.", wait=False),
        Wait(0.3),
        Keys("c"),
        Keys("c"),       # cc — clear line, enter insert mode
        Wait(0.3),
        Type("name = \"vim\""),
        Wait(0.3),
        Escape(),
        Wait(0.5),

        Say("The old line is gone. The new one is in its place."),
        Wait(0.3),

        # --- Change line 2 ---
        Say("Line two.", wait=False),
        Wait(0.3),
        Keys("j"),
        Keys("c"),
        Keys("c"),       # cc — clear line, enter insert
        Wait(0.3),
        Type("version = 2"),
        Wait(0.3),
        Escape(),
        Wait(0.5),

        Say("C C wipes the content but keeps the line."),
        Wait(0.3),

        # --- Show S shortcut ---
        Say("Capital S does the same thing. One key instead of two.", wait=False),
        Wait(0.3),
        Keys("j"),
        Keys("S"),       # S — same as cc
        Wait(0.3),
        Type("active = True"),
        Wait(0.3),
        Escape(),
        Wait(0.5),

        Say("S or C C. Same result. Replace the entire line."),
        Wait(0.3),

        # --- Wrap up ---
        Say("C C. Change the whole line."),
        Wait(1.5),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f task.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
