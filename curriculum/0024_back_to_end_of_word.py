"""
Lesson 024: Back to End of Word

Sub-60-second lesson: Press ge to jump backward to the end of the previous word.
The mirror of e — combines g and e into a two-key motion.
"""

import sys
from pathlib import Path

# ShellPilot DSL imports
sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Back to End of Word",
    description="Press ge to jump backward to the end of the previous word. "
                "The reverse of e — a two-key motion.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=95,
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
        Overlay("VimFu", caption="Back to End of Word", duration=3.0),
        Wait(0.7),

        # --- Open file and position at end of file ---
        Say("E goes forward to the end of a word.", wait=True),
        Line("nvim words.py", delay=0.05),
        WaitForScreen("vim master", timeout=10.0),
        IfScreen("swap file", "d"),
        Wait(0.5),

        # Position at start of line 3 so we have room to go backward
        Keys("G"),       # last line: print(name, level)
        Keys("$"),       # end of line
        Wait(0.3),

        # --- Demonstrate ge ---
        Say("G E goes backward to the end of the previous word.", wait=False),
        Wait(0.3),
        Keys("g"),
        Keys("e"),       # ) → end of "level"
        Wait(0.5),
        Keys("g"),
        Keys("e"),       # end of "level" → comma
        Wait(0.5),
        Keys("g"),
        Keys("e"),       # comma → end of "name"
        Wait(0.5),
        Keys("g"),
        Keys("e"),       # end of "name" → (
        Wait(0.5),

        Say("Each G E hops backward to a word ending."),
        Wait(0.3),

        # --- Keep going across lines ---
        Say("It wraps to the previous line too.", wait=False),
        Wait(0.3),
        Keys("g"),
        Keys("e"),       # ( → end of word on previous line
        Wait(0.5),
        Keys("g"),
        Keys("e"),
        Wait(0.5),
        Keys("g"),
        Keys("e"),
        Wait(0.5),

        Say("B lands on the start. G E lands on the end."),
        Wait(0.3),

        # --- Quick summary of the four word motions ---
        Say("Now you have all four. W, B, E, G E."),
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
