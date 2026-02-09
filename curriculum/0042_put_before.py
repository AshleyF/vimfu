"""
Lesson 042: Put (Paste) Before

Sub-60-second lesson: Press P (capital) to paste before the cursor.
For yanked lines, P pastes above the current line.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Put Before",
    description="Press P (capital) to paste before the cursor. For yanked lines, "
                "P pastes above the current line.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=183,
    tts_voice="echo",
    borderless=True,
    playlist="VimFu",

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Prepare workspace"),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Line("rm -f tasks.py .tasks.py.swp .tasks.py.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*tasks.py*"),
        Comment("Create demo file"),
        WriteFile("tasks.py", """
            alpha = 1
            gamma = 3
        """),
        Line("clear"),
        Comment("Launch nvim before recording"),
        Line("nvim tasks.py"),
        WaitForScreen("alpha", timeout=10.0),
        IfScreen("swap file", "d"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Put Before", duration=3.0),
        Wait(0.7),

        # --- Intro ---
        Say("Lowercase P pastes after. Capital P pastes before.", wait=True),
        Wait(0.3),

        # --- Yank line 2 and paste above with P ---
        Say("Let's yank line two and put it above.", wait=False),
        Wait(0.3),
        Keys("j"),       # down to line 2: gamma = 3
        Keys("y"),
        Keys("y"),       # yy — yank line 2
        Wait(0.3),
        Keys("P"),       # P — paste above current line
        Wait(0.6),

        Say("Capital P pasted it above. The line appeared before, not after."),
        Wait(0.3),

        # --- Undo, show dd + P to move line up ---
        Keys("u"),
        Wait(0.3),
        Say("D D then capital P puts it right back where it was.", wait=False),
        Wait(0.3),
        Keys("d"),
        Keys("d"),       # dd — cut line 2 (gamma = 3)
        Wait(0.4),
        Keys("P"),       # P — paste above current line (puts gamma back on top)
        Wait(0.6),

        Say("The line moved up. Capital P puts above."),
        Wait(0.3),

        # --- Undo, show character P ---
        Keys("u"),
        Wait(0.1),
        Keys("u"),
        Wait(0.3),
        Keys("g"),
        Keys("g"),       # back to top
        Say("For characters, capital P pastes before the cursor.", wait=False),
        Wait(0.3),
        Keys("x"),       # cut 'a'
        Wait(0.3),
        Keys("P"),       # paste before cursor — 'a' goes back to position 0
        Wait(0.6),

        Say("Lowercase P after. Capital P before. That's the only difference."),
        Wait(0.3),

        # --- Wrap up ---
        Say("Capital P. Put before."),
        Wait(1.5),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f tasks.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
