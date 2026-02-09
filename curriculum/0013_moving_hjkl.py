"""
Lesson 013: Moving: h j k l

Sub-60-second lesson: h left, j down, k up, l right.
Your fingers stay on the home row.
"""

import sys
from pathlib import Path

# ShellPilot DSL imports
sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Moving: h j k l",
    description="Move the cursor with h j k l. Left, down, up, right. "
                "Your hands never leave the home row.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=54,
    tts_voice="echo",
    borderless=True,
    playlist="VimFu",

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Prepare workspace"),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Line("rm -f moves.py .moves.py.swp .moves.py.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*moves.py*"),
        Comment("Create a file with several lines"),
        WriteFile("moves.py", """
            apples = 10
            bananas = 20
            cherries = 30
            dates = 40
            elderberries = 50
        """),
        Line("clear"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Moving: h j k l", duration=3.0),
        Wait(0.7),

        # --- Open file ---
        Say("In normal mode, you move the cursor with four keys.", wait=False),
        Line("nvim moves.py", delay=0.05),
        WaitForScreen("apples", timeout=10.0),
        IfScreen("swap file", "d"),
        Wait(0.5),

        # --- j: down ---
        Say("J moves down.", wait=False),
        Wait(0.3),
        Keys("j"),
        Wait(0.3),
        Keys("j"),
        Wait(0.3),
        Keys("j"),
        Wait(0.5),

        # --- k: up ---
        Say("K moves up.", wait=False),
        Wait(0.3),
        Keys("k"),
        Wait(0.3),
        Keys("k"),
        Wait(0.5),

        # --- l: right ---
        Say("L moves right.", wait=False),
        Wait(0.3),
        Keys("l"),
        Wait(0.2),
        Keys("l"),
        Wait(0.2),
        Keys("l"),
        Wait(0.2),
        Keys("l"),
        Wait(0.2),
        Keys("l"),
        Wait(0.5),

        # --- h: left ---
        Say("H moves left.", wait=False),
        Wait(0.3),
        Keys("h"),
        Wait(0.2),
        Keys("h"),
        Wait(0.2),
        Keys("h"),
        Wait(0.5),

        # --- Explain the layout ---
        Say("H, J, K, L. All on the home row, right under your fingers."),
        Wait(0.3),

        # --- Move around freely ---
        Say("No reaching for arrow keys. Just tap and go.", wait=False),
        Wait(0.3),
        Keys("j"),
        Wait(0.15),
        Keys("j"),
        Wait(0.15),
        Keys("l"),
        Wait(0.15),
        Keys("l"),
        Wait(0.15),
        Keys("l"),
        Wait(0.15),
        Keys("k"),
        Wait(0.15),
        Keys("h"),
        Wait(0.15),
        Keys("j"),
        Wait(0.5),

        Say("H J K L. It'll feel weird for a day. Then it'll feel fast."),
        Wait(1.5),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f moves.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
