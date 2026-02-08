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
    speed=0.55,
    rows=12,
    cols=40,
    humanize=0.7,
    mistakes=0.0,   # No typos for this lesson — keep it clean
    seed=42,
    tts_voice="echo",
    borderless=True,

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

        # --- Open Neovim ---
        Say("Vim is a modal text editor."),
        Say("It has two main modes. Normal mode, and insert mode.", wait=False),
        Line("nvim hello.py"),
        WaitForScreen("import sys", timeout=10.0),
        IfScreen("swap file", "d"),

        # --- Demonstrate normal mode ---
        Say("Right now we're in normal mode."),
        Say("In normal mode, every key on your keyboard is a command."),
        Say("Your whole keyboard, no modifier keys needed.", wait=False),

        Say("For example, h j k l move the cursor.", wait=False),
        Comment("Move through the Python code to show hjkl"),
        Keys("l"),         # col 2 on 'import sys'
        Wait(0.3),
        Keys("l"),         # col 3
        Wait(0.3),
        Keys("l"),         # col 4
        Wait(0.3),
        Keys("l"),         # col 5
        Wait(0.3),
        Keys("j"),         # line 2 (blank) — cursor snaps back
        Wait(0.4),
        Keys("j"),         # line 3: def greet(name):
        Wait(0.4),
        Keys("l"),         # col 2
        Wait(0.3),
        Keys("l"),         # col 3
        Wait(0.3),
        Keys("j"),         # line 4: print(...)
        Wait(0.4),
        Keys("j"),         # line 5: return True
        Wait(0.4),
        Keys("k"),         # line 4
        Wait(0.3),
        Keys("k"),         # line 3
        Wait(0.3),
        Keys("h"),         # col 2
        Wait(0.3),
        Keys("h"),         # col 1
        Wait(0.3),
        Keys("k"),         # line 2 (blank — cursor lands here for insert)
        Wait(0.4),

        Say("Arrow keys work too, but these are right on the home row."),

        # --- Switch to insert mode (cursor is on blank line 2 — safe to type) ---
        Say("Press i to enter insert mode. Now keys type text.", wait=False),
        Keys("i"),
        Wait(0.3),

        Type("# Vim is modal!"),

        # --- Back to normal mode ---
        Say("Press escape to return to normal mode.", wait=False),
        Escape(),
        Wait(0.3),

        Say("That's the whole idea. Normal mode: keys are commands."),
        Say("Insert mode: keys type text. Escape to switch back."),

        # --- Save and quit ---
        Comment("Save and quit"),
        Type(":wq"),
        Enter(),
        Wait(0.3),

        Say("That's Vim. A modal editor."),
    ],

    teardown=[
        Comment("Cleaning up..."),
        Line("rm -f hello.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
