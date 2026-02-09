"""
Lesson 031: Delete Character

Sub-60-second lesson: Press x to delete the character under the cursor.
The simplest delete — one character at a time.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Delete Character",
    description="Press x to delete the character under the cursor. "
                "The simplest way to delete in Vim.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=172,
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
        Comment("Create a file with a typo"),
        WriteFile("typo.py", """
            messaage = "hello"
            priint("done")
        """),
        Line("clear"),
        Comment("Launch nvim before recording"),
        Line("nvim typo.py"),
        WaitForScreen("messaage", timeout=10.0),
        IfScreen("swap file", "d"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Delete Character", duration=3.0),
        Wait(0.7),

        # --- Show the typo ---
        Say("There's a typo here. An extra A in message.", wait=True),
        Wait(0.3),

        # --- Navigate to the extra 'a' and delete ---
        Say("Move to it and press X.", wait=False),
        Wait(0.3),
        Keys("f"),
        Keys("a"),       # fa — find first 'a' in 'messaage'
        Keys("l"),       # move right to the second 'a'
        Wait(0.3),
        Keys("x"),       # delete it
        Wait(0.6),

        Say("Gone. One character deleted."),
        Wait(0.3),

        # --- Fix the second line ---
        Say("Line two has the same problem. Double I in print.", wait=False),
        Wait(0.3),
        Keys("j"),       # down to line 2: priint("done")
        Keys("0"),       # start of line
        Keys("f"),
        Keys("i"),       # fi — find first 'i'
        Keys("l"),       # move to second 'i'
        Wait(0.3),
        Keys("x"),       # delete it
        Wait(0.6),

        Say("Fixed. X deletes whatever's under the cursor."),
        Wait(0.3),

        # --- Show multiple x presses ---
        Say("You can press it multiple times too.", wait=False),
        Wait(0.3),
        Keys("g"),
        Keys("g"),       # back to top
        Keys("$"),       # end of line
        Wait(0.3),
        Keys("x"),
        Wait(0.3),
        Keys("x"),
        Wait(0.3),
        Keys("x"),
        Wait(0.5),

        Say("Each X nibbles away one character."),
        Wait(0.3),

        # --- Undo to restore ---
        Keys("u"),
        Wait(0.1),
        Keys("u"),
        Wait(0.1),
        Keys("u"),
        Wait(0.3),

        # --- Wrap up ---
        Say("X. Delete the character under the cursor."),
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
