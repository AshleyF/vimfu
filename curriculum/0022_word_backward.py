"""
Lesson 022: Word Backward

Sub-60-second lesson: Press b to jump to the start of the previous word.
The mirror of w — move backward through code word by word.
"""

import sys
from pathlib import Path

# ShellPilot DSL imports
sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Word Backward",
    description="Press b to jump to the start of the previous word. "
                "Move backward through code without holding arrow keys.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=73,
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
        Comment("Create a file with some code"),
        WriteFile("words.py", """
            name = "vim master"
            level = 42
            print(name, level)
        """),
        Line("clear"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Word Backward", duration=3.0),
        Wait(0.7),

        # --- Open file and position cursor at end of last line ---
        Say("W moves forward. But what about going back?", wait=True),
        Line("nvim words.py", delay=0.05),
        WaitForScreen("vim master", timeout=10.0),
        IfScreen("swap file", "d"),
        Wait(0.5),

        # Move to end of last line: print(name, level)
        Keys("G"),       # last line (col preserved at 0)
        Keys("$"),       # end of line → cursor on )
        Wait(0.3),

        # --- Demonstrate b through line 3 ---
        Say("Press B to jump to the previous word.", wait=False),
        Wait(0.3),
        Keys("b"),       # ) → level
        Wait(0.4),
        Keys("b"),       # level → ,
        Wait(0.4),
        Keys("b"),       # , → name
        Wait(0.4),
        Keys("b"),       # name → (
        Wait(0.4),
        Keys("b"),       # ( → print
        Wait(0.5),

        Say("Each B hops backward one word at a time."),
        Wait(0.3),

        # --- Keep going across lines ---
        Say("It wraps to the previous line too.", wait=False),
        Wait(0.3),
        Keys("b"),       # print → 42 (wraps to line 2)
        Wait(0.4),
        Keys("b"),       # 42 → =
        Wait(0.4),
        Keys("b"),       # = → level
        Wait(0.5),

        Say("Word by word. Back through the code."),
        Wait(0.3),

        # --- Race from bottom to top ---
        Say("Watch how fast you can move.", wait=False),
        Wait(0.3),
        Keys("G"),       # last line
        Keys("$"),       # end of line
        Wait(0.3),
        Keys("b"),
        Wait(0.15),
        Keys("b"),
        Wait(0.15),
        Keys("b"),
        Wait(0.15),
        Keys("b"),
        Wait(0.15),
        Keys("b"),
        Wait(0.15),
        Keys("b"),
        Wait(0.15),
        Keys("b"),
        Wait(0.15),
        Keys("b"),
        Wait(0.15),
        Keys("b"),
        Wait(0.15),
        Keys("b"),
        Wait(0.15),
        Keys("b"),
        Wait(0.15),
        Keys("b"),
        Wait(0.15),
        Keys("b"),
        Wait(0.15),
        Keys("b"),
        Wait(0.5),

        # --- Wrap up ---
        Say("B for back. W forward, B backward."),
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
