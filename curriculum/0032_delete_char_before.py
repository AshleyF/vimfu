"""
Lesson 032: Delete Character Before

Sub-60-second lesson: Press X (capital) to delete the character BEFORE
the cursor — like backspace in normal mode.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Delete Character Before",
    description="Press X (Shift-x) to delete the character before the cursor. "
                "It's like backspace in normal mode.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=173,
    tts_voice="echo",
    borderless=True,
    playlist="VimFu",

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Prepare workspace"),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Line("rm -f typo.py .typo.py.swp .typo.py.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*typo.py*"),
        Comment("Create a file with double-letter typos"),
        WriteFile("typo.py", """
            prrint("hello")
            texxt = "data"
        """),
        Line("clear"),
        Comment("Launch nvim before recording"),
        Line("nvim typo.py"),
        WaitForScreen("prrint", timeout=10.0),
        IfScreen("swap file", "d"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Delete Character Before", duration=3.0),
        Wait(0.7),

        # --- Intro ---
        Say("Lowercase X deletes under the cursor. Capital X deletes before it.", wait=True),
        Wait(0.3),

        # --- Fix prrint ---
        Say("There's a double R in print. Let's fix it.", wait=False),
        Wait(0.3),
        Keys("f"),
        Keys("r"),       # fr — find first 'r' in 'prrint'
        Keys("l"),       # move right to the second 'r'
        Wait(0.3),
        Keys("X"),       # delete the 'r' before cursor
        Wait(0.6),

        Say("Capital X removed the R before the cursor."),
        Wait(0.3),

        # --- Fix texxt ---
        Say("Same fix on line two. Double X in text.", wait=False),
        Wait(0.3),
        Keys("j"),       # down to line 2: texxt = "data"
        Keys("0"),       # start of line
        Keys("f"),
        Keys("x"),       # fx — find first 'x' in 'texxt'
        Keys("l"),       # move to second 'x'
        Wait(0.3),
        Keys("X"),       # delete the 'x' before cursor
        Wait(0.6),

        Say("Fixed. Think of capital X as backspace for normal mode."),
        Wait(0.3),

        # --- Show multiple X presses ---
        Say("You can press it multiple times too.", wait=False),
        Wait(0.3),
        Keys("g"),
        Keys("g"),       # back to top
        Keys("$"),       # end of line: print("hello")
        Wait(0.3),
        Keys("X"),
        Wait(0.3),
        Keys("X"),
        Wait(0.3),
        Keys("X"),
        Wait(0.5),

        Say("Each one deletes the character before."),
        Wait(0.3),

        # --- Undo to restore ---
        Keys("u"),
        Wait(0.1),
        Keys("u"),
        Wait(0.1),
        Keys("u"),
        Wait(0.3),

        # --- Wrap up ---
        Say("Capital X. Delete the character before the cursor."),
        Wait(1.5),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f typo.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
