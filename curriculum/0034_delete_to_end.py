"""
Lesson 034: Delete to End of Line

Sub-60-second lesson: Press D to delete from the cursor to the end
of the line. Same as d$ — the delete operator with the end-of-line motion.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Delete to End of Line",
    description="Press D to delete from the cursor to the end of the line. "
                "Same as d$ — delete operator plus the end-of-line motion.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=175,
    tts_voice="echo",
    borderless=True,
    playlist="VimFu",

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Prepare workspace"),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Line("rm -f notes.py .notes.py.swp .notes.py.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*notes.py*"),
        Comment("Create a file with trailing comments to delete"),
        WriteFile("notes.py", """
            name = "vim"  # TODO fix
            port = 8080  # remove this
            host = "local"  # old note
        """),
        Line("clear"),
        Comment("Launch nvim before recording"),
        Line("nvim notes.py"),
        WaitForScreen("name", timeout=10.0),
        IfScreen("swap file", "d"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Delete to End of Line", duration=3.0),
        Wait(0.7),

        # --- Intro ---
        Say("Capital D deletes everything from the cursor to the end of the line.", wait=True),
        Wait(0.3),

        # --- Delete trailing comment from line 1 ---
        Say("These trailing comments need to go.", wait=False),
        Wait(0.3),
        Keys("f"),
        Keys("#"),       # f# — find the '#' comment
        Wait(0.3),
        Keys("D"),       # delete from # to end of line
        Wait(0.6),

        Say("Everything from the hash to the end. Gone."),
        Wait(0.3),

        # --- Delete trailing comment from line 2 ---
        Say("Same on line two.", wait=False),
        Wait(0.3),
        Keys("j"),       # down to line 2
        Keys("0"),       # start of line
        Keys("f"),
        Keys("#"),       # f# — find the '#' comment
        Wait(0.3),
        Keys("D"),       # delete from # to end of line
        Wait(0.6),

        Say("One key. Everything after the cursor is deleted."),
        Wait(0.3),

        # --- Delete trailing comment from line 3 ---
        Say("One more.", wait=False),
        Wait(0.3),
        Keys("j"),       # down to line 3
        Keys("0"),       # start of line
        Keys("f"),
        Keys("#"),       # f# — find the '#' comment
        Wait(0.3),
        Keys("D"),       # delete from # to end of line
        Wait(0.6),

        Say("D is the same as d dollar sign. Delete to end of line."),
        Wait(0.3),

        # --- Undo all ---
        Keys("u"),
        Wait(0.1),
        Keys("u"),
        Wait(0.1),
        Keys("u"),
        Wait(0.5),

        # --- Wrap up ---
        Say("Capital D. Delete to the end of the line."),
        Wait(1.5),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f notes.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
