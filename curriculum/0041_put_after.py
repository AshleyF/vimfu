"""
Lesson 041: Put (Paste) After

Sub-60-second lesson: Press p to paste after the cursor.
For yanked lines, p pastes below the current line.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Put After",
    description="Press p to paste after the cursor. For yanked lines, "
                "p pastes below the current line.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=182,
    tts_voice="echo",
    borderless=True,
    playlist="VimFu",

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Prepare workspace"),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Line("rm -f tasks.py .tasks.py.swp .tasks.py.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*tasks.py*"),
        Comment("Create demo file"),
        WriteFile("tasks.py", """
            alpha = 1
            gamma = 3
        """),
        Line("clear"),
        Comment("Launch nvim before recording"),
        Line("nvim tasks.py"),
        WaitForScreen("alpha", timeout=10.0),
        IfScreen("swap file", "d"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Put After", duration=3.0),
        Wait(0.7),

        # --- Intro ---
        Say("Last time we yanked a line. Now let's paste it.", wait=True),
        Wait(0.3),

        # --- Yank line 1 and paste below ---
        Say("Y Y copies the line. P puts it below.", wait=False),
        Wait(0.3),
        Keys("y"),
        Keys("y"),       # yy — yank line 1
        Wait(0.3),
        Keys("p"),       # p — paste below
        Wait(0.6),

        Say("A copy of line one appeared below it."),
        Wait(0.3),

        # --- Undo, then show dd + p ---
        Keys("u"),
        Wait(0.3),
        Say("P also works with deleted text. D D cuts a line. P puts it back.", wait=False),
        Wait(0.3),
        Keys("d"),
        Keys("d"),       # dd — cut line 1 (alpha = 1)
        Wait(0.4),
        Keys("p"),       # p — paste below current line
        Wait(0.6),

        Say("We moved the line down. Delete and put. That's a move."),
        Wait(0.3),

        # --- Undo, show character paste ---
        Keys("u"),
        Wait(0.1),
        Keys("u"),
        Wait(0.3),
        Say("It works for characters too. X cuts a character. P pastes it after.", wait=False),
        Wait(0.3),
        Keys("x"),       # cut 'a' from 'alpha'
        Wait(0.3),
        Keys("p"),       # paste 'a' after cursor
        Wait(0.6),

        Say("P always pastes after. After the cursor, or below the line."),
        Wait(0.3),

        # --- Wrap up ---
        Say("P. Put after."),
        Wait(1.5),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f tasks.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
