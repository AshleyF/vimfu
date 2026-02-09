"""
Lesson 018: Append at End of Line

Sub-60-second lesson: Press shift-A to jump to the end of the
line and enter insert mode. Perfect for adding semicolons,
comments, or finishing a thought.
"""

import sys
from pathlib import Path

# ShellPilot DSL imports
sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Append at End of Line",
    description="Press shift-A to jump to the end of the line and "
                "enter insert mode. Add comments, finish lines, "
                "or tack on whatever you need.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=59,
    tts_voice="echo",
    borderless=True,
    playlist="VimFu",

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Prepare workspace"),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Line("rm -f items.py .items.py.swp .items.py.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*items.py*"),
        Comment("Create a file with short lines"),
        WriteFile("items.py", """
            x = 1
            y = 2
            z = 3
            total = x + y
        """),
        Line("clear"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Append at End of Line", duration=3.0),
        Wait(0.7),

        # --- Open file ---
        Say("Sometimes you need to add something at the end of a line.", wait=True),
        Line("nvim items.py", delay=0.05),
        WaitForScreen("x = 1", timeout=10.0),
        IfScreen("swap file", "d"),
        Wait(0.5),

        # --- Position cursor at start, then shift-A ---
        Say("No matter where your cursor is, shift A takes you to the end.", wait=False),
        Wait(0.3),
        Keys("A"),
        Wait(0.4),
        Type("  # width"),
        Wait(0.3),
        Escape(),
        Wait(0.5),

        Say("Straight to the end. One key."),
        Wait(0.3),

        # --- Second line ---
        Say("Cursor's at the start this time.", wait=False),
        Wait(0.3),
        Keys("j"),
        Wait(0.2),
        Keys("0"),
        Wait(0.3),
        Say("Doesn't matter. Shift A.", wait=False),
        Wait(0.3),
        Keys("A"),
        Wait(0.4),
        Type("  # height"),
        Wait(0.3),
        Escape(),
        Wait(0.5),

        # --- Third line ---
        Say("Middle of the line. Same thing.", wait=False),
        Wait(0.3),
        Keys("j"),
        Wait(0.2),
        Keys("0"),
        Keys("w"),
        Wait(0.3),
        Keys("A"),
        Wait(0.4),
        Type("  # depth"),
        Wait(0.3),
        Escape(),
        Wait(0.5),

        # --- Fix the total line ---
        Say("Let's fix this last line.", wait=False),
        Wait(0.3),
        Keys("j"),
        Wait(0.2),
        Keys("0"),
        Wait(0.3),
        Keys("A"),
        Wait(0.4),
        Type(" + z"),
        Wait(0.3),
        Escape(),
        Wait(0.5),

        # --- Wrap up ---
        Say("Shift A. End of line, insert mode. "
            "The perfect pair with shift eye."),
        Wait(1.5),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f items.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
