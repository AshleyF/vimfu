"""
Lesson 035: Delete Entire Line

Sub-60-second lesson: Press dd to delete the entire current line.
The most common delete — whole lines at once.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Delete Entire Line",
    description="Press dd to delete the entire current line. "
                "The most common delete command in Vim.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=176,
    tts_voice="echo",
    borderless=True,
    playlist="VimFu",

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Prepare workspace"),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Line("rm -f app.py .app.py.swp .app.py.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*app.py*"),
        Comment("Create a file with lines to delete"),
        WriteFile("app.py", """
            import os
            import sys
            import debug  # remove
            import log  # remove

            def main():
                run()
        """),
        Line("clear"),
        Comment("Launch nvim before recording"),
        Line("nvim app.py"),
        WaitForScreen("import os", timeout=10.0),
        IfScreen("swap file", "d"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Delete Entire Line", duration=3.0),
        Wait(0.7),

        # --- Intro ---
        Say("D D deletes the entire line. The whole thing.", wait=True),
        Wait(0.3),

        # --- Delete line 3: import debug ---
        Say("These two debug imports need to go.", wait=False),
        Wait(0.3),
        Keys("j"),       # line 2
        Keys("j"),       # line 3: import debug  # remove
        Wait(0.3),
        Keys("d"),
        Keys("d"),       # dd — delete the line
        Wait(0.6),

        Say("The whole line is gone. Everything shifted up."),
        Wait(0.3),

        # --- Delete line 3 again (now import log) ---
        Say("The next line moved up. Delete it too.", wait=False),
        Wait(0.3),
        Keys("d"),
        Keys("d"),       # dd — delete import log
        Wait(0.6),

        Say("Two lines removed. Two D D commands."),
        Wait(0.3),

        # --- Show count prefix ---
        Say("You can also use a count. Three D D deletes three lines.", wait=False),
        Wait(0.3),
        Keys("g"),
        Keys("g"),       # back to top
        Wait(0.3),
        Keys("3"),
        Keys("d"),
        Keys("d"),       # 3dd — delete 3 lines
        Wait(0.6),

        Say("Three lines in one shot."),
        Wait(0.3),

        # --- Undo all ---
        Keys("u"),
        Wait(0.2),
        Keys("u"),
        Wait(0.2),
        Keys("u"),
        Wait(0.5),

        # --- Wrap up ---
        Say("D D. Delete the line."),
        Wait(1.5),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f app.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
