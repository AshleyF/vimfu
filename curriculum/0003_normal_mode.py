"""
Lesson 003: You're in Normal Mode

Sub-60-second lesson: Normal mode is home base. When you open Vim,
you're in normal mode. After every edit, every search, every command —
press Escape to come back. Make it a reflex.
"""

import sys
from pathlib import Path

# ShellPilot DSL imports
sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Normal Mode",
    description="Normal mode is your home base in Vim. Every key is a command — "
                "move, jump, edit, run commands. After every action, press Escape "
                "to come back. Make it a reflex.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=44,
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
        Comment("Create a sample file"),
        WriteFile("todo.py", """
            tasks = [
                "learn vim",
                "practice daily",
                "build something",
            ]

            for task in tasks:
                print(task)
        """),
        Line("clear"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Normal Mode", duration=3.0),
        Wait(0.7),

        # --- Open nvim ---
        Say("When you open Neovim, you're in normal mode.", wait=False),
        Line("nvim todo.py", delay=0.05),
        WaitForScreen("tasks", timeout=10.0),
        IfScreen("swap file", "d"),
        Wait(0.3),

        # --- Explain what normal mode means ---
        Say("Every key on the keyboard is a command. "
            "Don't memorize these. We'll learn them all later. "
            "This is just a taste."),

        # --- Show normal mode: j movement ---
        # Cursor starts at (0,0) on "tasks = ["
        Say("For example, J moves the cursor down.", wait=False),
        Keys("j"),
        Wait(0.2),
        Keys("j"),
        Wait(0.2),
        Keys("j"),
        Wait(0.2),
        Keys("j"),
        Wait(0.3),

        # --- Show normal mode: w movement ---
        Say("W jumps forward by words.", wait=False),
        Keys("w"),
        Wait(0.25),
        Keys("w"),
        Wait(0.25),
        Keys("w"),
        Wait(0.25),
        Keys("w"),
        Wait(0.3),
        Say("No arrow keys. Just single letters."),

        # --- Insert mode: add a comment at the top ---
        Say("There are commands to jump around too.", wait=False),
        Keys("gg"),
        Wait(0.3),

        Say("And commands to start typing.", wait=False),
        Keys("O"),
        Wait(0.3),
        Type("# task list"),
        Wait(0.3),

        Say("Escape brings you back to normal mode.", wait=False),
        Escape(),
        Wait(0.3),

        # --- Command-line mode: do a real command ---
        Say("There's also a command line.", wait=False),
        Wait(0.2),
        Type(":set number"),
        Enter(),
        Wait(0.3),
        Say("Line numbers. And Escape returns to normal mode.", wait=False),
        Wait(0.3),

        # --- Show escaping from command-line mode ---
        Type(":quit"),
        Wait(0.4),
        Escape(),
        Wait(0.3),
        Say("You can always abort with Escape too."),

        # --- The rule ---
        Say("The big idea: after every action, press Escape. "
            "Normal mode is your resting state. Always come back."),
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
