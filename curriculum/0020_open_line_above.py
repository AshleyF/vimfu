"""
Lesson 020: Open Line Above

Sub-60-second lesson: Press shift-O to create a new blank line
ABOVE the cursor and drop into insert mode. The mirror of o.
"""

import sys
from pathlib import Path

# ShellPilot DSL imports
sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Open Line Above",
    description="Press shift-O to open a new line above the cursor and "
                "enter insert mode. The mirror of lowercase o.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=61,
    tts_voice="echo",
    borderless=True,
    playlist="VimFu",

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Prepare workspace"),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Line("rm -f recipe.py .recipe.py.swp .recipe.py.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*recipe.py*"),
        Comment("Create a file"),
        WriteFile("recipe.py", """
            flour = "2 cups"
            sugar = "1 cup"
            eggs = 3
            bake = "350F for 30 min"
        """),
        Line("clear"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Open Line Above", duration=3.0),
        Wait(0.7),

        # --- Open file ---
        Say("Lowercase O opens a line below. "
            "Shift O opens a line above.", wait=False),
        Line("nvim recipe.py", delay=0.05),
        WaitForScreen("flour", timeout=10.0),
        IfScreen("swap file", "d"),
        Wait(0.5),

        # --- Add a title above the first line ---
        Say("We need a title. Cursor is on line one.", wait=False),
        Wait(0.3),
        Keys("O"),
        Wait(0.5),

        Say("New line above. We're in insert mode.", wait=False),
        Wait(0.3),
        Type("# cake recipe"),
        Wait(0.3),
        Escape(),
        Wait(0.5),

        Say("Title added, right above where we were."),
        Wait(0.3),

        # --- Add a comment above eggs ---
        Say("Let's add a note above the eggs line.", wait=False),
        Wait(0.3),
        # Navigate to eggs line (should be line 4 now after adding title)
        Keys("j"),
        Wait(0.15),
        Keys("j"),
        Wait(0.15),
        Keys("j"),
        Wait(0.3),

        Keys("O"),
        Wait(0.4),
        Type("# wet ingredients"),
        Wait(0.3),
        Escape(),
        Wait(0.5),

        Say("Inserted above. The lines below just move down."),
        Wait(0.3),

        # --- Add a note above bake ---
        Say("One more.", wait=False),
        Wait(0.3),
        Keys("G"),
        Wait(0.3),
        Keys("O"),
        Wait(0.4),
        Type("# instructions"),
        Wait(0.3),
        Escape(),
        Wait(0.5),

        # --- Wrap up ---
        Say("Shift O. New line above, insert mode. "
            "Pair it with lowercase O and you can add lines anywhere."),
        Wait(1.5),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f recipe.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
