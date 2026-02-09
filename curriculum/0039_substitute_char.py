"""
Lesson 039: Substitute Character

Sub-60-second lesson: Press s to delete the character under the cursor
and enter insert mode. Like x + i in one keystroke.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Substitute Character",
    description="Press s to delete the character under the cursor and enter "
                "insert mode. Like x + i in one keystroke.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=180,
    tts_voice="echo",
    borderless=True,
    playlist="VimFu",

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Prepare workspace"),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Line("rm -f fix.py .fix.py.swp .fix.py.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*fix.py*"),
        Comment("Create a file with single-char typos"),
        WriteFile("fix.py", """
            het = "vim"
            cot = 42
            fog = "data"
        """),
        Line("clear"),
        Comment("Launch nvim before recording"),
        Line("nvim fix.py"),
        WaitForScreen("het", timeout=10.0),
        IfScreen("swap file", "d"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Substitute Character", duration=3.0),
        Wait(0.7),

        # --- Intro ---
        Say("Lowercase S deletes one character and enters insert mode.", wait=True),
        Wait(0.3),

        # --- Fix "het" to "let" ---
        Say("This should be let, not het.", wait=False),
        Wait(0.3),
        # Cursor at (0,0) on 'h' in 'het'
        Keys("s"),       # delete 'h', enter insert mode
        Wait(0.3),
        Type("l"),       # type 'l'
        Wait(0.3),
        Escape(),
        Wait(0.5),

        Say("S deleted the H and I typed L. One smooth move."),
        Wait(0.3),

        # --- Fix "cot" to "count" --- wait, that's more than one char
        # Fix "cot" to "cat" --- change 'o' to 'a'
        Say("Line two. Change the O to an A.", wait=False),
        Wait(0.3),
        Keys("j"),       # down to line 2: cot = 42
        Keys("l"),       # move to 'o' at position 1
        Wait(0.3),
        Keys("s"),       # delete 'o', enter insert mode
        Wait(0.3),
        Type("a"),       # type 'a'
        Wait(0.3),
        Escape(),
        Wait(0.5),

        Say("One character swapped. That's what S does."),
        Wait(0.3),

        # --- Fix "fog" to "log" ---
        Say("Last one. F to L.", wait=False),
        Wait(0.3),
        Keys("j"),       # down to line 3: fog = "data"
        Keys("0"),       # start of line
        Wait(0.3),
        Keys("s"),       # delete 'f', enter insert mode
        Wait(0.3),
        Type("l"),       # type 'l'
        Wait(0.3),
        Escape(),
        Wait(0.5),

        Say("S is like X then I. Delete and insert in one key."),
        Wait(0.3),

        # --- Wrap up ---
        Say("Lowercase S. Substitute a character."),
        Wait(1.5),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f fix.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
