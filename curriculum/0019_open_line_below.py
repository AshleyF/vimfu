"""
Lesson 019: Open Line Below

Sub-60-second lesson: Press o to create a new blank line below
the cursor and drop into insert mode. Fastest way to add a line.
"""

import sys
from pathlib import Path

# ShellPilot DSL imports
sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Open Line Below",
    description="Press o to open a new line below the cursor and "
                "enter insert mode. One key to add a line.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=60,
    tts_voice="echo",
    borderless=True,
    playlist="VimFu",

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Prepare workspace"),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Line("rm -f steps.py .steps.py.swp .steps.py.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*steps.py*"),
        Comment("Create a file with numbered steps"),
        WriteFile("steps.py", """
            step1 = "wake up"
            step3 = "code"
            step4 = "sleep"
        """),
        Line("clear"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Open Line Below", duration=3.0),
        Wait(0.7),

        # --- Open file ---
        Say("Here's a file with numbered steps.", wait=True),
        Line("nvim steps.py", delay=0.05),
        WaitForScreen("wake up", timeout=10.0),
        IfScreen("swap file", "d"),
        Wait(0.5),

        Say("We skipped step two. Let's fix that."),
        Wait(0.3),

        # --- Use o to open line below ---
        Say("Cursor is on step one. Press O to open a new line below.", wait=False),
        Wait(0.3),
        Keys("o"),
        Wait(0.5),

        Say("A blank line appears, and we're in insert mode.", wait=False),
        Wait(0.3),
        Type('step2 = "eat breakfast"'),
        Wait(0.3),
        Escape(),
        Wait(0.5),

        Say("Done. New line added right where we needed it."),
        Wait(0.3),

        # --- Add another: a step 5 ---
        Say("Let's add one more at the bottom.", wait=False),
        Wait(0.3),
        Keys("G"),
        Wait(0.3),
        Keys("o"),
        Wait(0.4),
        Type('step5 = "repeat"'),
        Wait(0.3),
        Escape(),
        Wait(0.5),

        Say("O opens below. Every time."),
        Wait(0.3),

        # --- Quick succession to show rhythm ---
        Say("You can keep going.", wait=False),
        Wait(0.3),
        Keys("o"),
        Wait(0.3),
        Type('step6 = "profit"'),
        Wait(0.3),
        Escape(),
        Wait(0.5),

        # --- Wrap up ---
        Say("Lowercase O. New line below, insert mode. "
            "One of the most-used keys in Vim."),
        Wait(1.5),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f steps.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
