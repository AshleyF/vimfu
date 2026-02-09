"""
Lesson 004: Entering Insert Mode

Sub-60-second lesson: Press i to enter insert mode. Now your keys
type text instead of running commands. When you're done, press
Escape to go back to normal mode.
"""

import sys
from pathlib import Path

# ShellPilot DSL imports
sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Insert Mode",
    description="Press i to enter insert mode. Your keys now type text instead "
                "of running commands. Press Escape to go back to normal mode. "
                "That's how you write code in Vim.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=45,
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
        Overlay("VimFu", caption="Insert Mode", duration=3.0),
        Wait(0.7),

        # --- Open an EMPTY file (new buffer — just tildes) ---
        Say("You know that normal mode is home base.", wait=False),
        Line("nvim hello.py", delay=0.05),
        WaitForScreen("~", timeout=10.0),
        IfScreen("swap file", "d"),
        Wait(0.3),

        # --- Show keys don't type in normal mode ---
        Say("But you can't type text in normal mode.", wait=False),
        Wait(0.5),
        Keys("j"),
        Wait(0.3),
        Keys("k"),
        Wait(0.3),
        Say("Keys are commands. Nothing appears on screen."),

        # --- Enter insert mode ---
        Say("To type text, press I.", wait=False),
        Wait(0.3),
        Keys("i"),
        Wait(0.5),

        Say("See INSERT at the bottom? Now keys type text.", wait=False),
        Wait(0.8),

        # --- Type two lines of code ---
        # Cursor is at (0,0) on empty buffer. Type first line, Enter, second line.
        Type('name = "world"'),
        Wait(0.3),
        Enter(),
        Type("print(name)"),
        Wait(0.5),

        # --- Escape back ---
        # After typing print(name), cursor is after ')'.
        # Escape moves cursor left one — now ON ')'.
        Say("Press Escape to return to normal mode.", wait=False),
        Wait(0.3),
        Escape(),
        Wait(0.5),

        Say("INSERT is gone. We're back."),

        # --- Second round: insert before cursor ---
        # Cursor is ON ')' in print(name).
        # Press i → insert BEFORE ')' → type ', "!"' → print(name, "!")
        Say("One more time. I to insert.", wait=False),
        Wait(0.3),
        Keys("i"),
        Wait(0.4),
        Type(', "!"'),
        Wait(0.3),
        Say("Escape to return.", wait=False),
        Escape(),
        Wait(0.5),

        # --- Wrap up ---
        Say("I to type. Escape to stop. That's the rhythm."),
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
