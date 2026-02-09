"""
Lesson 021: Word Forward

Sub-60-second lesson: Press w to jump to the start of the next word.
The fastest way to move through code word by word.
"""

import sys
from pathlib import Path

# ShellPilot DSL imports
sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Word Forward",
    description="Press w to jump to the start of the next word. "
                "Move through code quickly without holding arrow keys.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=62,
    tts_voice="echo",
    borderless=True,
    playlist="VimFu",

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Prepare workspace"),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Line("rm -f words.py .words.py.swp .words.py.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*words.py*"),
        Comment("Create a file with some code"),
        WriteFile("words.py", """
            name = "vim master"
            level = 42
            print(name, level)
        """),
        Line("clear"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Word Forward", duration=3.0),
        Wait(0.7),

        # --- Open file ---
        Say("Moving one character at a time is slow.", wait=True),
        Line("nvim words.py", delay=0.05),
        WaitForScreen("vim master", timeout=10.0),
        IfScreen("swap file", "d"),
        Wait(0.5),

        # --- Demonstrate w ---
        Say("Press W to jump to the next word.", wait=False),
        Wait(0.3),
        # Cursor starts at column 0 on line 1: 'n' of 'name'
        Keys("w"),
        Wait(0.4),
        Keys("w"),
        Wait(0.4),
        Keys("w"),
        Wait(0.4),
        Keys("w"),
        Wait(0.5),

        Say("Each W hops to the start of the next word."),
        Wait(0.3),

        # --- Keep going across lines ---
        Say("It wraps to the next line too.", wait=False),
        Wait(0.3),
        Keys("w"),
        Wait(0.4),
        Keys("w"),
        Wait(0.4),
        Keys("w"),
        Wait(0.4),
        Keys("w"),
        Wait(0.5),

        Say("Word by word. Way faster than H L L L L."),
        Wait(0.3),

        # --- Go back to top and race through ---
        Say("Watch how fast you can move.", wait=False),
        Wait(0.3),
        Keys("g"),
        Keys("g"),
        Keys("0"),
        Wait(0.3),
        Keys("w"),
        Wait(0.2),
        Keys("w"),
        Wait(0.2),
        Keys("w"),
        Wait(0.2),
        Keys("w"),
        Wait(0.2),
        Keys("w"),
        Wait(0.2),
        Keys("w"),
        Wait(0.2),
        Keys("w"),
        Wait(0.2),
        Keys("w"),
        Wait(0.2),
        Keys("w"),
        Wait(0.2),
        Keys("w"),
        Wait(0.5),

        # --- Wrap up ---
        Say("W for word forward. Your first speed boost."),
        Wait(1.5),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f words.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
