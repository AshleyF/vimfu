"""
Lesson 008: Quitting Vim

Sub-60-second lesson: Type :q and press Enter to quit.
The most famous question in programming, solved in five seconds.
"""

import sys
from pathlib import Path

# ShellPilot DSL imports
sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay


lesson = Demo(
    title="VimFu — Quitting Vim",
    description="Type :q and press Enter to quit Vim. The most famous "
                "question in programming — solved in five seconds.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=49,
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
        Line("clear"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Quitting Vim", duration=3.0),
        Wait(0.7),

        # --- The meme ---
        Say("How do you quit Vim? The most famous question in programming."),

        # --- Open nvim ---
        Say("Let's open a file.", wait=False),
        Line("nvim hello.py", delay=0.05),
        WaitForScreen("~", timeout=10.0),
        IfScreen("swap file", "d"),
        Wait(0.5),

        # --- Show the quit command ---
        Say("To quit, type colon Q.", wait=False),
        Wait(0.3),
        Type(":q"),
        Wait(0.8),

        Say("Colon opens the command line. Q means quit.", wait=False),
        Wait(0.5),

        # --- Press Enter ---
        Say("Press Enter.", wait=False),
        Enter(),
        Wait(0.8),

        # --- Back at shell ---
        Say("You're back at the shell. That's it."),

        # --- But what if you edited? ---
        Say("But what if you made changes?", wait=False),
        Line("nvim hello.py", delay=0.05),
        WaitForScreen("~", timeout=10.0),
        IfScreen("swap file", "d"),
        Wait(0.3),

        # --- Type something ---
        Keys("i"),
        Wait(0.3),
        Type("hello"),
        Wait(0.3),
        Escape(),
        Wait(0.3),

        Say("Now try colon Q.", wait=False),
        Type(":q"),
        Enter(),
        Wait(0.8),

        # --- Error message ---
        Say("Vim warns you. There are unsaved changes."),
        Wait(0.5),

        Say("We'll cover how to handle that next. "
            "For now, colon Q quits when there's nothing to lose."),
        Wait(1.5),
    ],

    teardown=[
        Comment("Force quit nvim"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f hello.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
