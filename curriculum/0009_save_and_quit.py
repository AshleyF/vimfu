"""
Lesson 009: Save and Quit

Sub-60-second lesson: Three ways to save and quit —
:wq, :x, and ZZ. All do the same thing.
"""

import sys
from pathlib import Path

# ShellPilot DSL imports
sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay


lesson = Demo(
    title="VimFu — Save and Quit",
    description="Three ways to save and quit: :wq, :x, and ZZ. "
                "Pick your favorite — they all work.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=50,
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
        Overlay("VimFu", caption="Save and Quit", duration=3.0),
        Wait(0.7),

        # --- Method 1: :wq ---
        Say("You know colon W saves. And colon Q quits.", wait=False),
        Line("nvim hello.py", delay=0.05),
        WaitForScreen("~", timeout=10.0),
        IfScreen("swap file", "d"),
        Wait(0.3),

        Keys("i"),
        Wait(0.3),
        Type('print("hello")'),
        Wait(0.3),
        Escape(),
        Wait(0.3),

        Say("Combine them. Colon W Q.", wait=False),
        Wait(0.3),
        Type(":wq"),
        Wait(0.8),
        Enter(),
        Wait(0.8),

        Say("Saved and quit in one command."),

        # --- Method 2: :x ---
        Say("There's a shorter way.", wait=False),
        Line("nvim hello.py", delay=0.05),
        WaitForScreen("hello", timeout=10.0),
        IfScreen("swap file", "d"),
        Wait(0.3),

        Keys("A"),
        Wait(0.3),
        Enter(),
        Type('print("world")'),
        Wait(0.3),
        Escape(),
        Wait(0.3),

        Say("Colon X. Same thing — save and quit.", wait=False),
        Wait(0.3),
        Type(":x"),
        Wait(0.8),
        Enter(),
        Wait(0.8),

        Say("Even faster."),

        # --- Method 3: ZZ ---
        Say("One more. No colon needed this time.", wait=False),
        Line("nvim hello.py", delay=0.05),
        WaitForScreen("world", timeout=10.0),
        IfScreen("swap file", "d"),
        Wait(0.3),

        Keys("o"),
        Wait(0.3),
        Type('print("done")'),
        Wait(0.3),
        Escape(),
        Wait(0.3),

        Say("Shift Z, Shift Z. Two capital Z's from normal mode.", wait=False),
        Wait(0.3),
        Keys("Z"),
        Wait(0.3),
        Keys("Z"),
        Wait(0.8),

        # --- Wrap up ---
        Say("Three ways. Colon W Q. Colon X. Or Z Z. "
            "Pick whichever feels right."),
        Wait(1.5),
    ],

    teardown=[
        Comment("Clean up"),
        Line("rm -f hello.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
