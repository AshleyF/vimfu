"""
Lesson 015: The Escape Habit

Sub-60-second lesson: After every edit, press Escape.
Normal mode is your resting state. Build the reflex now.
"""

import sys
from pathlib import Path

# ShellPilot DSL imports
sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — The Escape Habit",
    description="After every edit, press Escape. Normal mode is home. "
                "Build the reflex now and never get stuck.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=56,
    tts_voice="echo",
    borderless=True,
    playlist="VimFu",

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Prepare workspace"),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Line("rm -f todo.py .todo.py.swp .todo.py.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*todo.py*"),
        Line("clear"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="The Escape Habit", duration=3.0),
        Wait(0.7),

        # --- Open empty file ---
        Say("This is the most important habit in Vim.", wait=False),
        Line("nvim todo.py", delay=0.05),
        WaitForScreen("~", timeout=10.0),
        IfScreen("swap file", "d"),
        Wait(0.5),

        Say("After every single edit, press Escape."),

        # --- Rapid fire: type, escape, type, escape ---
        Say("Watch the rhythm.", wait=False),
        Wait(0.3),

        # Edit 1
        Keys("i"),
        Wait(0.3),
        Type("# my todo list"),
        Wait(0.3),
        Escape(),
        Wait(0.5),

        # Edit 2
        Keys("o"),
        Wait(0.3),
        Type("buy milk"),
        Wait(0.3),
        Escape(),
        Wait(0.5),

        # Edit 3
        Keys("o"),
        Wait(0.3),
        Type("walk dog"),
        Wait(0.3),
        Escape(),
        Wait(0.5),

        # Edit 4
        Keys("o"),
        Wait(0.3),
        Type("learn vim"),
        Wait(0.3),
        Escape(),
        Wait(0.5),

        Say("Type. Escape. Type. Escape. Every time."),

        # --- Why it matters ---
        Say("If you're ever lost or confused, just press Escape. "
            "You'll always land in normal mode."),

        Say("It's your reset button. Your safe place. "
            "Make it a reflex and you'll never get stuck."),
        Wait(1.5),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f todo.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
