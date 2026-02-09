"""
Lesson 053: Find Character Backward

Sub-60-second lesson: Press capital F followed by a character to jump
backward to it on the current line.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Find Character Backward",
    description="Press capital F followed by a character to jump backward to "
                "the previous occurrence of that character on the current line.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=194,
    tts_voice="echo",
    borderless=True,
    playlist="VimFu",

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Prepare workspace"),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Line("rm -f brew.py .brew.py.swp .brew.py.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*brew.py*"),
        Comment("Create demo file — potion brewing"),
        WriteFile("brew.py", """
            heal = mix("ruby", "moss", 3)
            burn = mix("lava", "coal", 7)
            cure = mix("sage", "mint", 2)
            zap  = mix("bolt", "dust", 5)
        """),
        Line("clear"),
        Comment("Launch nvim before recording"),
        Line("nvim brew.py"),
        WaitForScreen("heal", timeout=10.0),
        IfScreen("swap file", "d"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Find Character Backward", duration=3.0),
        Wait(0.7),

        # --- Intro ---
        Say("Capital F searches backward on the current line. The reverse of lowercase F.", wait=True),
        Wait(0.3),

        # --- Demo 1: $ to end, Fm backward ---
        Say("Let's go to the end of the line.", wait=False),
        Wait(0.3),
        Keys("$"),          # end of line 1: col 28 on ')'
        Wait(0.5),

        Say("Capital F M.", wait=False),
        Wait(0.3),
        Keys("F"),
        Keys("m"),          # backward to 'm' in "moss" at col 20
        Wait(0.6),

        Say("Jumped backward to moss. Capital F finds the previous match.", wait=True),
        Wait(0.3),

        # --- Demo 2: Fr backward on same line ---
        Say("Capital F R.", wait=False),
        Wait(0.3),
        Keys("F"),
        Keys("r"),          # backward to 'r' in "ruby" at col 12
        Wait(0.6),

        Say("Further back to ruby. Same line, keeps going backward.", wait=True),
        Wait(0.3),

        # --- Demo 3: line 2, Fl twice ---
        Say("Next line. Go to the end.", wait=False),
        Wait(0.3),
        Keys("j"),          # line 2
        Keys("$"),          # end of line 2: col 28
        Wait(0.5),

        Say("Capital F L.", wait=False),
        Wait(0.3),
        Keys("F"),
        Keys("l"),          # backward to 'l' in "coal" at col 23
        Wait(0.6),

        Say("Found the L in coal. Again.", wait=False),
        Wait(0.3),
        Keys("F"),
        Keys("l"),          # backward to 'l' in "lava" at col 12
        Wait(0.6),

        Say("Back to lava. Capital F hops backward through every match on the line.", wait=True),
        Wait(0.3),

        # --- Wrap up ---
        Say("Lowercase F goes forward, capital F goes backward. Same line, opposite direction.", wait=True),
        Wait(1.5),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f brew.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
