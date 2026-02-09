"""
Lesson 054: Till Character Forward

Sub-60-second lesson: Press t followed by a character to jump to
just before the next occurrence of that character on the current line.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Till Character Forward",
    description="Press t followed by a character to jump to just before "
                "the next occurrence on the current line.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=195,
    tts_voice="echo",
    borderless=True,
    playlist="VimFu",

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Prepare workspace"),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Line("rm -f fight.py .fight.py.swp .fight.py.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*fight.py*"),
        Comment("Create demo file — boss battles"),
        WriteFile("fight.py", """
            hero = fight("dragon", 50)
            sage = fight("goblin", 10)
            king = fight("troll", 30)
        """),
        Line("clear"),
        Comment("Launch nvim before recording"),
        Line("nvim fight.py"),
        WaitForScreen("hero", timeout=10.0),
        IfScreen("swap file", "d"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Till Character Forward", duration=3.0),
        Wait(0.7),

        # --- Intro ---
        Say("T followed by a character stops just before it. Think till. Almost there, but not quite.", wait=True),
        Wait(0.3),

        # --- Demo 1a: f( for contrast ---
        Say("First, F open-paren for comparison.", wait=False),
        Wait(0.3),
        Keys("f"),
        Keys("("),          # lands ON '(' at col 12
        Wait(0.6),

        Say("F lands right on the paren.", wait=True),
        Wait(0.3),

        # --- Demo 1b: back to start, t( ---
        Say("Back to the start. Now T open-paren.", wait=False),
        Wait(0.3),
        Keys("0"),          # back to col 0
        Wait(0.3),
        Keys("t"),
        Keys("("),          # stops at col 11, one before '('
        Wait(0.6),

        Say("T stopped one short. On the T of fight, right before the paren.", wait=True),
        Wait(0.3),

        # --- Demo 2: t, on line 2 ---
        Say("Down to the next line. T comma.", wait=False),
        Wait(0.3),
        Keys("j"),          # line 2: sage = fight("goblin", 10)
        Keys("0"),
        Wait(0.3),
        Keys("t"),
        Keys(","),          # stops before first ',' on line 2
        Wait(0.6),

        Say("Stopped right before the comma. T always leaves the target untouched.", wait=True),
        Wait(0.3),

        # --- Demo 3: dt) power combo ---
        Say("Here's why T matters. Go to the last line.", wait=False),
        Wait(0.3),
        Keys("j"),          # line 3: king = fight("troll", 30)
        Keys("0"),
        Wait(0.3),

        Say("D T close-paren.", wait=False),
        Wait(0.3),
        Keys("d"),
        Keys("t"),
        Keys(")"),          # deletes from col 0 up to (not including) ')'
        Wait(0.6),

        Say("Deleted everything up to the paren. The paren stays.", wait=True),
        Wait(0.3),

        Say("Undo.", wait=False),
        Wait(0.3),
        Keys("u"),
        Wait(0.5),

        Say("T sets up surgical precision. F lands on it. T stops just before.", wait=True),
        Wait(0.3),

        # --- Wrap up ---
        Say("T. The 'almost there' motion. Perfect for delete-to and change-to combos.", wait=True),
        Wait(1.5),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f fight.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
