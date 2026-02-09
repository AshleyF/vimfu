"""
Lesson 017: Insert at Start of Line

Sub-60-second lesson: Press shift-I to jump to the first
non-blank character and enter insert mode. Great for adding
prefixes or comments.
"""

import sys
from pathlib import Path

# ShellPilot DSL imports
sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Insert at Start of Line",
    description="Press shift-I to jump to the start of the line and "
                "enter insert mode. Perfect for adding comments or prefixes.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=58,
    tts_voice="echo",
    borderless=True,
    playlist="VimFu",

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Prepare workspace"),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Line("rm -f config.py .config.py.swp .config.py.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*config.py*"),
        Comment("Create a file with indented lines"),
        WriteFile("config.py", """
            host = "localhost"
            port = 8080
            debug = True
            name = "app"
        """),
        Line("clear"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Insert at Start of Line", duration=3.0),
        Wait(0.7),

        # --- Open file ---
        Say("Lowercase eye inserts where the cursor is.", wait=False),
        Line("nvim config.py", delay=0.05),
        WaitForScreen("host", timeout=10.0),
        IfScreen("swap file", "d"),
        Wait(0.5),

        # --- Move cursor to middle of a line ---
        Say("But what if you want to type at the beginning of the line?", wait=False),
        Wait(0.3),
        # Move cursor into the middle of the line
        Keys("f"),
        Keys("l"),
        Wait(0.5),

        # --- Shift-I jumps to start ---
        Say("Shift eye. It jumps to the start and enters insert mode.", wait=False),
        Wait(0.3),
        Keys("I"),
        Wait(0.5),
        Type("# "),
        Wait(0.3),
        Say("Escape to go back to normal mode.", wait=False),
        Escape(),
        Wait(0.5),

        Say("We just commented out that line. From anywhere on it."),
        Wait(0.3),

        # --- Do it again on another line ---
        Say("Let's do another. Move down a couple lines.", wait=False),
        Wait(0.3),
        Keys("j"),
        Wait(0.2),
        Keys("j"),
        Wait(0.2),
        # Cursor somewhere on "debug = True"
        Keys("$"),
        Wait(0.3),
        Say("Cursor is at the end. Shift eye.", wait=False),
        Wait(0.3),
        Keys("I"),
        Wait(0.4),
        Type("# "),
        Wait(0.3),
        Say("And Escape.", wait=False),
        Escape(),
        Wait(0.5),

        Say("Straight to the start. No matter where you were."),
        Wait(0.3),

        # --- One more for rhythm ---
        Say("One more.", wait=False),
        Wait(0.3),
        Keys("j"),
        Wait(0.3),
        Keys("I"),
        Wait(0.4),
        Type("# "),
        Wait(0.3),
        Say("Escape.", wait=False),
        Escape(),
        Wait(0.5),

        # --- Wrap up ---
        Say("Shift eye. Jump to the beginning, start typing. "
            "The opposite of shift A, which we'll see next."),
        Wait(1.5),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f config.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
