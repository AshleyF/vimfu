"""
Lesson 002: Opening a File

Sub-60-second lesson: How to open a file in Neovim. Type `nvim`
followed by a filename. See what an empty buffer looks like vs.
an existing file.
"""

import sys
from pathlib import Path

# ShellPilot DSL imports
sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, Ctrl, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    speed=0.55,
    rows=12,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=43,
    tts_voice="echo",
    borderless=True,

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Prepare workspace"),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Comment("Clean up any previous files and swap files"),
        Line("rm -f hello.py .hello.py.swp .hello.py.swo"),
        Line("rm -f notes.txt .notes.txt.swp .notes.txt.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*hello.py*"),
        Line("rm -f ~/.local/state/nvim/swap/*notes.txt*"),
        Comment("Create a sample file to open later"),
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
        Overlay("VimFu", caption="Opening a File", duration=4.0),

        # --- Open a new (empty) file ---
        Say("To open a file, type Vee Eye.", wait=False),
        Type("vi"),
        Wait(1.0),
        Say("Or vim.", wait=False),
        Type("m"),
        Wait(1.0),
        Say("Or In-vim.", wait=False),
        Ctrl("a"),
        Wait(0.2),
        Type("n"),
        Wait(1.0),
        Say("Let's open a brand new file.", wait=False),
        Ctrl("e"),
        Type(" notes.txt"),
        Wait(0.3),
        Enter(),
        WaitForScreen("notes.txt", timeout=10.0),
        IfScreen("swap file", "d"),

        Wait(0.5),
        Say("This is an empty buffer. Let's type something."),
        Say("Press i for insert mode.", wait=False),
        Keys("i"),
        Wait(0.5),
        Type("Hello, Vim!"),
        Wait(0.5),
        Escape(),

        # --- Quit with a quick intro to quitting ---
        Say("To quit, type colon q.", wait=False),
        Wait(0.3),
        Type(":q"),
        Enter(),
        Wait(0.5),
        Say("It won't let us. We have unsaved changes."),
        Say("Colon q bang quits without saving.", wait=False),
        Wait(0.3),
        Type(":q!"),
        Enter(),
        WaitForScreen("$", timeout=5.0),
        Wait(0.3),

        # --- Open an existing file ---
        Say("Now let's open a file that already has content.", wait=False),
        Line("nvim hello.py", delay=0.05),
        WaitForScreen("import sys", timeout=10.0),
        IfScreen("swap file", "d"),

        Wait(0.5),
        Say("Now we can see the code inside the file."),
        Say("At the bottom is the status bar, with the filename and cursor position.", wait=False),
        Wait(1.5),

        # --- Wrap up ---
        Say("That's it. vi, vim, or nvim, then the filename."),
        Say("If the file exists, you see its contents. If not, you get an empty buffer."),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Cleaning up..."),
        Line("rm -f hello.py notes.txt"),
    ],
)


if __name__ == "__main__":
    lesson.run()
