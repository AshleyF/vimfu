"""
Lesson 006: Back to Normal Mode

Sub-60-second lesson: Press Escape to leave insert mode and return
to normal mode. Make it a reflex — after every edit, hit Escape.
"""

import sys
from pathlib import Path

# ShellPilot DSL imports
sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Back to Normal Mode",
    description="Press Escape to leave insert mode. Always. After every "
                "edit, hit Escape to return to normal mode. "
                "Make it a reflex.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=47,
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
        Comment("Create a starter file"),
        WriteFile("todo.py", """
            tasks = []
            print(tasks)
        """),
        Line("clear"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Back to Normal Mode", duration=3.0),
        Wait(0.7),

        # --- Open file ---
        Say("You know how to enter insert mode with I.", wait=True),
        Line("nvim todo.py", delay=0.05),
        WaitForScreen("tasks", timeout=10.0),
        IfScreen("swap file", "d"),
        Wait(0.5),

        # --- First edit cycle: i, type, Escape ---
        Say("Type something. Then press Escape.", wait=False),
        Keys("i"),
        Wait(0.3),
        Type("# my todo list"),
        Enter(),
        Wait(0.3),
        Escape(),
        Wait(0.5),

        Say("INSERT is gone. You're back in normal mode."),

        # --- Show that Escape is safe: press it extra times ---
        Say("Escape is always safe. Press it twice if you're not sure.", wait=False),
        Wait(0.3),
        Escape(),
        Wait(0.2),
        Escape(),
        Wait(0.5),

        Say("Nothing bad happens. You just stay in normal mode."),

        # --- Second edit cycle: use A to append at end of line ---
        # Cursor is on line 1 (# my todo list). j j → print(tasks)
        Say("There are other ways into insert mode too. "
            "Shift A appends at the end of a line.", wait=False),
        Wait(0.2),
        Keys("j"),
        Wait(0.15),
        Keys("j"),
        Wait(0.15),
        Keys("j"),
        Wait(0.3),
        Keys("A"),
        Wait(0.4),
        Type("  # show tasks"),
        Wait(0.3),
        Escape(),
        Wait(0.5),

        Say("Same rule. When you're done, Escape."),

        # --- Third cycle: one more quick rep ---
        Say("One more. Shift O to open a line above.", wait=False),
        Wait(0.2),
        Keys("gg"),
        Wait(0.2),
        Keys("O"),
        Wait(0.3),
        Type("# vim practice"),
        Wait(0.3),
        Escape(),
        Wait(0.5),

        # --- The rule ---
        Say("That's the habit. After every edit, Escape. "
            "Normal mode is home. Always come back."),
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
