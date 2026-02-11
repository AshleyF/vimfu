"""
Lesson 063: Go to Column

Sub-60-second lesson: 20| jumps to column 20 on the current line.
A number then pipe goes straight to that column.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Go to Column",
    description="20| jumps to column 20 on the current line. "
                "A number then pipe goes straight to that column.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=204,
    tts_voice="echo",
    borderless=True,
    playlist="VimFu",

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Prepare workspace"),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Line("rm -f pixel.py .pixel.py.swp .pixel.py.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*pixel.py*"),
        Comment("Create demo file — pixel art coordinates"),
        WriteFile("pixel.py", """
            # pixel art colors
            row = "..##..##..##..##.."
            sky = "bbbbbbbbbbbbbbbbbb"
            gnd = "gggggggggggggggggg"
        """),
        Line("clear"),
        Comment("Launch nvim before recording"),
        Line("nvim pixel.py"),
        WaitForScreen("All", timeout=30.0),  # nvim status bar, not heredoc
        IfScreen("swap file", "d"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Go to Column", duration=3.0),
        Wait(0.7),

        # --- Intro ---
        Say("A number then pipe jumps to that column on the current line.", wait=True),
        Wait(0.3),

        # --- Demo 1: move to row line, 10| ---
        Say("Go to the row line. Ten pipe.", wait=False),
        Wait(0.3),
        Keys("j"),          # row line: row = "..##..."
        Wait(0.3),
        Keys("1"),
        Keys("0"),
        Keys("|"),          # column 10
        Wait(0.6),

        Say("Column ten. Right on the opening quote.", wait=True),
        Wait(0.3),

        # --- Demo 2: 1| back to start ---
        Say("One pipe goes to column one.", wait=False),
        Wait(0.3),
        Keys("1"),
        Keys("|"),          # column 1
        Wait(0.6),

        Say("Back at the start of the line. Same as zero.", wait=True),
        Wait(0.3),

        # --- Demo 3: 20| on sky line ---
        Say("Down to the sky line. Twenty pipe.", wait=False),
        Wait(0.3),
        Keys("j"),          # sky line
        Wait(0.3),
        Keys("2"),
        Keys("0"),
        Keys("|"),          # column 20
        Wait(0.6),

        Say("Column twenty. Lands right in the middle of the pixel data.", wait=True),
        Wait(0.3),

        # --- Demo 4: 30| ---
        Say("Thirty pipe.", wait=False),
        Wait(0.3),
        Keys("3"),
        Keys("0"),
        Keys("|"),          # column 30
        Wait(0.6),

        Say("Column thirty. Precise horizontal positioning.", wait=True),
        Wait(0.3),

        # --- Wrap up ---
        Say("Number pipe. Jump to any column on the current line.", wait=True),
        Wait(1.5),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f pixel.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
