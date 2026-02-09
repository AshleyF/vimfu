"""
Lesson 049: Previous Match

Sub-60-second lesson: After a search, press N (capital) to jump
to the previous match — the opposite direction of n.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Previous Match",
    description="After a search, press capital N to jump to the previous match. "
                "It goes the opposite direction of n.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=190,
    tts_voice="echo",
    borderless=True,
    playlist="VimFu",

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Prepare workspace"),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Line("rm -f words.py .words.py.swp .words.py.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*words.py*"),
        Comment("Create demo file"),
        WriteFile("words.py", """
            cat = "meow"
            dog = "woof"
            cat = "purr"
            dog = "bark"
            cat = "hiss"
            dog = "howl"
        """),
        Line("clear"),
        Comment("Launch nvim before recording"),
        Line("nvim words.py"),
        WaitForScreen("cat", timeout=10.0),
        IfScreen("swap file", "d"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Previous Match", duration=3.0),
        Wait(0.7),

        # --- Intro ---
        Say("Capital N goes to the previous match. The opposite of lowercase N.", wait=True),
        Wait(0.3),

        # --- First, search for "dog" and use n to go forward ---
        Say("Let's search for dog and go forward with N.", wait=False),
        Wait(0.3),
        Keys("/"),
        Type("dog"),
        Enter(),            # line 1: dog = "woof"
        Wait(0.4),
        Keys("n"),          # line 3: dog = "bark"
        Wait(0.4),
        Keys("n"),          # line 5: dog = "howl"
        Wait(0.5),

        Say("We're on the last dog. Now let's go backward."),
        Wait(0.3),

        # --- Capital N to go backward ---
        Say("Capital N. Previous match.", wait=False),
        Wait(0.3),
        Keys("N"),          # line 3: dog = "bark"
        Wait(0.5),

        Say("Jumped back one match."),
        Wait(0.3),

        Say("Capital N again.", wait=False),
        Wait(0.3),
        Keys("N"),          # line 1: dog = "woof"
        Wait(0.5),

        Say("Back to the first dog. Capital N reverses the search direction."),
        Wait(0.3),

        # --- Wrap up ---
        Say("Lowercase N goes forward. Capital N goes backward. Easy."),
        Wait(1.5),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f words.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
