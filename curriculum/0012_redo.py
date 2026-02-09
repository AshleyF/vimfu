"""
Lesson 012: Redo

Sub-60-second lesson: Press Ctrl-R to redo what you just undid.
Undo went too far? Ctrl-R brings it back.
"""

import sys
from pathlib import Path

# ShellPilot DSL imports
sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, Ctrl, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Redo",
    description="Press Ctrl-R to redo in Vim. Went too far with undo? "
                "Ctrl-R brings your changes back.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=53,
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
        Comment("Create a starter file"),
        WriteFile("hello.py", """
            print("hello")
            print("world")
        """),
        Line("clear"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Redo", duration=3.0),
        Wait(0.7),

        # --- Open file ---
        Say("You know U undoes your last change.", wait=False),
        Line("nvim hello.py", delay=0.05),
        WaitForScreen("hello", timeout=10.0),
        IfScreen("swap file", "d"),
        Wait(0.5),

        # --- Make a change then undo it ---
        Say("Let's add a line.", wait=False),
        Wait(0.2),
        Keys("o"),
        Wait(0.3),
        Type('print("new line")'),
        Wait(0.3),
        Escape(),
        Wait(0.5),

        Say("Now undo it.", wait=False),
        Wait(0.3),
        Keys("u"),
        Wait(0.5),

        Say("Gone. But what if we wanted that line back?"),

        # --- Redo ---
        Say("Control R. Redo.", wait=False),
        Wait(0.3),
        Ctrl("r"),
        Wait(0.5),

        Say("It's back. Redo reverses the undo."),

        # --- Show the back-and-forth ---
        Say("You can go back and forth.", wait=False),
        Wait(0.3),
        Keys("u"),
        Wait(0.4),
        Say("Undo.", wait=False),
        Wait(0.3),
        Ctrl("r"),
        Wait(0.4),
        Say("Redo.", wait=False),
        Wait(0.3),
        Keys("u"),
        Wait(0.4),
        Ctrl("r"),
        Wait(0.5),

        Say("U to undo. Control R to redo. Simple."),
        Wait(1.5),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f hello.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
