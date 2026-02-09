"""
Lesson 001: What Is Vim?

Sub-60-second intro: Vim is a modal editor. Normal mode is your
home base — keys move and act instead of typing. Press i to insert
text, Esc to return. That's the big idea.
"""

import sys
from pathlib import Path

# ShellPilot DSL imports
sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — What Is Vim?",
    description="Vim is a modal text editor. Normal mode: keys are commands. "
                "Insert mode: keys type text. That's the big idea — and it's "
                "what makes Vim so powerful.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,   # No typos for this lesson — keep it clean
    seed=42,
    tts_voice="echo",
    borderless=True,
    playlist="VimFu",

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Cleaning up any previous files..."),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Line("rm -f hello.py .hello.py.swp .hello.py.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*hello.py*"),
        Comment("Creating a sample file with some code..."),
        WriteFile("hello.py", """
            import sys

            def greet(name):
                print(f"Hello, {name}!")
                return True

            greet("world")
        """),
        Line("clear"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="What Is Vim?", duration=4.0),
        Wait(0.7),

        # --- Open Neovim ---
        Say("Vim is a modal text editor."),
        Say("It has two main modes. Normal mode, and insert mode.", wait=False),
        Line("nvim hello.py", delay=0.05),
        WaitForScreen("import sys", timeout=10.0),
        IfScreen("swap file", "d"),

        # --- Demonstrate normal mode ---
        Say("Right now we're in normal mode."),
        Say("In normal mode, every key on your keyboard is a command.", wait=False),
        Wait(1.5),

        # --- hjkl demo: narrate each key while pressing it ---
        # Cursor starts at (0, 0) on "import sys"

        Say("For example, L moves right.", wait=False),
        Keys("l"),         # (0,1)
        Wait(0.35),
        Keys("l"),         # (0,2)
        Wait(0.35),
        Keys("l"),         # (0,3)
        Wait(0.35),
        Keys("l"),         # (0,4)
        Wait(0.5),

        Say("J moves down.", wait=False),
        Keys("j"),         # (1,0) blank line — cursor snaps to col 0
        Wait(0.4),
        Keys("j"),         # (2,4) def greet — restores col 4
        Wait(0.4),
        Keys("j"),         # (3,4)     print(...)
        Wait(0.5),

        Say("And H moves left.", wait=False),
        Keys("h"),         # (3,3)
        Wait(0.35),
        Keys("h"),         # (3,2)
        Wait(0.35),
        Keys("h"),         # (3,1)
        Wait(0.5),

        Say("K moves up.", wait=False),
        Keys("k"),         # (2,1) def greet
        Wait(0.4),
        Keys("k"),         # (1,0) blank line
        Wait(0.5),

        Say("No arrow keys needed. H J K L, right on the home row."),

        # --- Switch to insert mode on blank line 1 (won't clobber code) ---
        Say("Press I to enter insert mode. Now keys type text.", wait=False),
        Keys("i"),
        Wait(0.4),

        Type("# Vim is modal!"),
        Wait(0.3),

        # --- Back to normal mode ---
        Say("Press escape to return to normal mode.", wait=False),
        Escape(),
        Wait(0.5),

        Say("That's the whole idea. Normal mode: keys are commands. Insert mode: keys type text."),

        Say("That's Vim. A modal editor."),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Cleaning up..."),
        Line("rm -f hello.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
