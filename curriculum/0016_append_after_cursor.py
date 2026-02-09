"""
Lesson 016: Append After Cursor

Sub-60-second lesson: Press a to insert text AFTER the cursor.
You already know i inserts before — a is its mirror twin.
"""

import sys
from pathlib import Path

# ShellPilot DSL imports
sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Append After Cursor",
    description="Press a to insert text after the cursor. "
                "You know i inserts before — a is its mirror.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=57,
    tts_voice="echo",
    borderless=True,
    playlist="VimFu",

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Prepare workspace"),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Line("rm -f greet.py .greet.py.swp .greet.py.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*greet.py*"),
        Comment("Create a simple file"),
        WriteFile("greet.py", """
            msg = "hell"
            print(msg)
        """),
        Line("clear"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Append After Cursor", duration=3.0),
        Wait(0.7),

        # --- Open file ---
        Say("You know I inserts before the cursor.", wait=True),
        Line("nvim greet.py", delay=0.05),
        WaitForScreen("hell", timeout=10.0),
        IfScreen("swap file", "d"),
        Wait(0.5),

        # --- Show the problem: cursor on last l, i inserts before it ---
        Say("But what if you want to add text after it?", wait=False),
        Wait(0.3),
        # Move cursor to the second l in "hell" (position the cursor)
        Keys("f"),
        Keys("l"),
        Wait(0.2),
        # Now on first 'l', move to second 'l'
        Keys("l"),
        Wait(0.5),

        # --- Try i first to show the difference ---
        Say("Watch what I does here.", wait=False),
        Wait(0.3),
        Keys("i"),
        Wait(0.4),
        Type("o"),
        Wait(0.4),
        Escape(),
        Wait(0.5),

        # Now we have "helo" or something weird — undo it
        Say("That inserted before the cursor. Not what we wanted.", wait=False),
        Wait(0.3),
        Keys("u"),
        Wait(0.5),

        # --- Now use a ---
        Say("Press A instead. Lowercase A.", wait=False),
        Wait(0.3),
        # Cursor is already on the second 'l' after undo — just press a
        Keys("a"),
        Wait(0.4),

        Say("Now we're inserting after the cursor.", wait=False),
        Type("o"),
        Wait(0.4),
        Escape(),
        Wait(0.5),

        # Now "hell" → "hello"
        Say("Hello. That's what we wanted."),
        Wait(0.3),

        # --- One more demo: append to end of a word ---
        Say("A is perfect for adding to the end of words.", wait=False),
        Wait(0.3),
        # Go to line 2, position on "msg" last char
        Keys("j"),
        Wait(0.2),
        Keys("0"),
        Wait(0.2),
        Keys("f"),
        Keys("g"),
        Wait(0.3),
        Keys("a"),
        Wait(0.3),
        Type("2"),
        Wait(0.3),
        Escape(),
        Wait(0.5),

        # --- Wrap up ---
        Say("I inserts before. A appends after. Two sides of the same coin."),
        Wait(1.5),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f greet.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
