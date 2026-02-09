"""
Lesson 051: Search Word Backward

Sub-60-second lesson: Press # to search backward for the exact word
under the cursor. The reverse of *.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Search Word Backward",
    description="Press # to search backward for the exact word under the cursor. "
                "The reverse of *.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=192,
    tts_voice="echo",
    borderless=True,
    playlist="VimFu",

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Prepare workspace"),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Line("rm -f cats.py .cats.py.swp .cats.py.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*cats.py*"),
        Comment("Create demo file — cat mood tracker"),
        WriteFile("cats.py", """
            mood = "hungry"
            naps = 5
            mood = "playful"
            naps = 2
            mood = "grumpy"
            naps = 9
            mood = "zoomies"
            naps = 0
            mood = "sleepy"
            naps = 12
        """),
        Line("clear"),
        Comment("Launch nvim before recording"),
        Line("nvim cats.py"),
        WaitForScreen("mood", timeout=10.0),
        IfScreen("swap file", "d"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Search Word Backward", duration=3.0),
        Wait(0.7),

        # --- Intro ---
        Say("Hash searches backward for the word under your cursor. The reverse of star.", wait=True),
        Wait(0.3),

        # --- Demo 1: Jump to bottom, # on "naps" ---
        Say("Here's a cat mood tracker. Let's jump to the bottom.", wait=False),
        Wait(0.3),
        Keys("G"),          # last line: naps = 12
        Wait(0.5),

        Say("Cursor is on naps. Press hash.", wait=False),
        Wait(0.3),
        Keys("#"),          # backward to line 8: naps = 0
        Wait(0.6),

        Say("Jumped backward to the previous naps.", wait=True),
        Wait(0.3),

        # --- Demo 2: keep pressing # ---
        Say("Hash again.", wait=False),
        Wait(0.3),
        Keys("#"),          # backward to line 6: naps = 9
        Wait(0.5),

        Say("Another hop backward. And again.", wait=False),
        Wait(0.3),
        Keys("#"),          # backward to line 4: naps = 2
        Wait(0.5),

        Say("Every naps in the file, going backward.", wait=True),
        Wait(0.3),

        Say("One more.", wait=False),
        Wait(0.3),
        Keys("#"),          # backward to line 2: naps = 5
        Wait(0.5),

        Say("All the way back to line two.", wait=True),
        Wait(0.3),

        # --- Demo 3: switch to a different word ---
        Say("Now go up to mood.", wait=False),
        Wait(0.3),
        Keys("k"),          # line 1: mood = "hungry"
        Wait(0.3),

        Say("Press hash on mood.", wait=False),
        Wait(0.3),
        Keys("#"),          # wraps to line 9: mood = "sleepy"
        Wait(0.6),

        Say("Wrapped to the last mood in the file. Hash always goes backward, even past the top.", wait=True),
        Wait(0.3),

        # --- Wrap up ---
        Say("Hash. One key, backward search. Star forward, hash back.", wait=True),
        Wait(1.5),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f cats.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
