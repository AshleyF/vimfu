"""
Lesson 010: Quit Without Saving

Sub-60-second lesson: Discard changes and bail out with :q! or ZQ.
When you've messed up and just want out.
"""

import sys
from pathlib import Path

# ShellPilot DSL imports
sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Quit Without Saving",
    description="Discard all changes with :q! or ZQ. The exclamation mark "
                "means 'I'm sure.' Everything since the last save is gone.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=51,
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
        Comment("Create a starter file so there's something to lose"),
        WriteFile("hello.py", """
            print("hello world")
        """),
        Line("clear"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Quit Without Saving", duration=3.0),
        Wait(0.7),

        # --- Open the file ---
        Say("Sometimes you make a mess and just want out.", wait=False),
        Line("nvim hello.py", delay=0.05),
        WaitForScreen("hello", timeout=10.0),
        IfScreen("swap file", "d"),
        Wait(0.5),

        Say("Here's a working file. Let's break it."),

        # --- Make destructive edits ---
        Keys("i"),
        Wait(0.3),
        Type("XXXXXXX"),
        Wait(0.3),
        Escape(),
        Wait(0.3),
        Keys("dd"),
        Wait(0.3),

        Say("Yikes. We don't want any of that."),

        # --- Try :q first to show the error ---
        Say("Colon Q won't work. Vim protects you.", wait=False),
        Wait(0.3),
        Type(":q"),
        Enter(),
        Wait(0.8),

        Say("Unsaved changes. Vim won't let you quit."),

        # --- :q! ---
        Say("Add an exclamation mark. Colon Q bang.", wait=False),
        Wait(0.3),
        Type(":q!"),
        Wait(0.8),

        Say("The bang means I'm sure. Throw it all away.", wait=False),
        Wait(0.3),
        Enter(),
        Wait(0.8),

        Say("Gone. Back to the shell. The file is untouched."),

        # --- Show the file is still fine ---
        Say("Let's check.", wait=False),
        Wait(0.2),
        Line("cat hello.py"),
        Wait(1.0),

        Say("Still perfect. Our edits were discarded."),

        # --- Method 2: ZQ ---
        Say("There's a faster way too.", wait=False),
        Line("nvim hello.py", delay=0.05),
        WaitForScreen("hello", timeout=10.0),
        IfScreen("swap file", "d"),
        Wait(0.3),

        Keys("i"),
        Wait(0.3),
        Type("OOPS"),
        Wait(0.3),
        Escape(),
        Wait(0.3),

        Say("Shift Z, Shift Q. Quit without saving, no colon needed.", wait=False),
        Wait(0.3),
        Keys("Z"),
        Wait(0.3),
        Keys("Q"),
        Wait(0.8),

        # --- Wrap up ---
        Say("Two ways out. Colon Q bang, or Z Q. "
            "Your escape hatch when things go wrong."),
        Wait(1.5),
    ],

    teardown=[
        Comment("Clean up"),
        Line("rm -f hello.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
