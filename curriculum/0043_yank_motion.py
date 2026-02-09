"""
Lesson 043: Yank a Motion

Sub-60-second lesson: Use yw to yank a word, y$ to yank to end of line.
The y operator works with any motion, just like d and c.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Yank a Motion",
    description="Use yw to yank a word, y$ to yank to end of line. "
                "The y operator works with any motion, just like d and c.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=184,
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
        Comment("Create demo file"),
        WriteFile("notes.py", """
            name = "vim"
            kind = "editor"
        """),
        Line("clear"),
        Comment("Launch nvim before recording"),
        Line("nvim notes.py"),
        WaitForScreen("name", timeout=10.0),
        IfScreen("swap file", "d"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Yank a Motion", duration=3.0),
        Wait(0.7),

        # --- Intro ---
        Say("Y Y yanks a whole line. But you can yank smaller pieces too.", wait=True),
        Wait(0.3),

        # --- yw demo: yank "name" then paste it ---
        Say("Y W yanks a word.", wait=False),
        Wait(0.3),
        Keys("y"),
        Keys("w"),       # yw — yank "name "
        Wait(0.4),
        Keys("j"),       # down to line 2: kind = "editor"
        Keys("P"),       # paste before cursor
        Wait(0.6),

        Say("We yanked the word name and pasted it on line two."),
        Wait(0.3),

        # --- Undo ---
        Keys("u"),
        Wait(0.3),

        # --- y$ demo: yank to end of line ---
        Say("Y dollar sign yanks to the end of the line.", wait=False),
        Wait(0.3),
        Keys("g"),
        Keys("g"),       # back to top: name = "vim"
        Keys("y"),
        Keys("$"),       # y$ — yank to end of line: name = "vim"
        Wait(0.4),

        Keys("j"),       # line 2: kind = "editor"
        Keys("$"),       # end of line
        Keys("p"),       # paste after
        Wait(0.6),

        Say("Yanked to end of line. There it is, pasted at the end."),
        Wait(0.3),

        # --- Undo ---
        Keys("u"),
        Wait(0.3),

        # --- Wrap up ---
        Say("Y plus any motion. Y W for a word. Y dollar for the rest of the line."),
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
