"""
Lesson 040: Yank (Copy) a Line

Sub-60-second lesson: Press yy to copy (yank) the current line.
Then use p to paste it. Vim calls copy "yank."
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Yank a Line",
    description="Press yy to copy (yank) the current line. Then p to paste. "
                "In Vim, copy is called yank.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=181,
    tts_voice="echo",
    borderless=True,
    playlist="VimFu",

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Prepare workspace"),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Line("rm -f items.py .items.py.swp .items.py.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*items.py*"),
        Comment("Create a short file"),
        WriteFile("items.py", """
            name = "vim"
            version = 2
        """),
        Line("clear"),
        Comment("Launch nvim before recording"),
        Line("nvim items.py"),
        WaitForScreen("name", timeout=10.0),
        IfScreen("swap file", "d"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Yank a Line", duration=3.0),
        Wait(0.7),

        # --- Intro ---
        Say("In Vim, copy is called yank. Y Y yanks the current line.", wait=True),
        Wait(0.3),

        # --- Yank line 1 ---
        Say("Let's copy this first line.", wait=False),
        Wait(0.3),
        Keys("y"),
        Keys("y"),       # yy — yank the current line
        Wait(0.6),

        Say("It looks like nothing happened. But the line is copied."),
        Wait(0.3),

        # --- Paste with p ---
        Say("Press P to paste it below.", wait=False),
        Wait(0.3),
        Keys("p"),       # paste below current line
        Wait(0.6),

        Say("There it is. A copy of line one, pasted below."),
        Wait(0.3),

        # --- Paste again ---
        Say("Press P again. It pastes again.", wait=False),
        Wait(0.3),
        Keys("p"),       # paste again
        Wait(0.6),

        Say("Yank once, paste as many times as you want."),
        Wait(0.3),

        # --- Undo pastes ---
        Keys("u"),
        Wait(0.1),
        Keys("u"),
        Wait(0.3),

        # --- Yank line 2 and paste ---
        Say("Let's yank line two instead.", wait=False),
        Wait(0.3),
        Keys("j"),       # down to line 2: version = 2
        Keys("y"),
        Keys("y"),       # yy — yank line 2
        Wait(0.3),
        Keys("p"),       # paste below
        Wait(0.6),

        Say("Copied and pasted. Y Y to yank. P to put."),
        Wait(0.3),

        # --- Undo ---
        Keys("u"),
        Wait(0.3),

        # --- Wrap up ---
        Say("Y Y. Yank a line."),
        Wait(1.5),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f items.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
