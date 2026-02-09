"""
Lesson 007: Saving Your File

Sub-60-second lesson: Type :w and press Enter to save your file.
The colon enters command-line mode, w means "write."
"""

import sys
from pathlib import Path

# ShellPilot DSL imports
sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay


lesson = Demo(
    title="VimFu — Saving Your File",
    description="Type :w and press Enter to save. The colon opens the "
                "command line, w means write. That's it — your file is saved.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=48,
    tts_voice="echo",
    borderless=True,
    playlist="VimFu",

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Prepare workspace"),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Line("rm -f hello.py .hello.py.swp .hello.py.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*hello.py*"),
        Line("clear"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Saving Your File", duration=3.0),
        Wait(0.7),

        # --- Open a new file and write some code ---
        Say("Let's create a file and save it.", wait=True),
        Line("nvim hello.py", delay=0.05),
        WaitForScreen("~", timeout=10.0),
        IfScreen("swap file", "d"),
        Wait(0.3),

        # --- Type some code ---
        Keys("i"),
        Wait(0.3),
        Type('print("hello world")'),
        Wait(0.3),
        Escape(),
        Wait(0.5),

        # --- Explain the save command ---
        Say("To save, type colon W.", wait=False),
        Wait(0.3),
        Type(":w"),
        Wait(0.5),

        Say("See the command at the bottom? Colon opens the command line. W means write.", wait=False),
        Wait(0.8),

        # --- Press Enter to execute ---
        Say("Press Enter.", wait=False),
        Enter(),
        Wait(0.8),

        Say("Saved. Look at the bottom. It confirms the file was written."),

        # --- Make another edit and save again ---
        Say("Let's edit and save again.", wait=False),
        Wait(0.2),
        Keys("o"),
        Wait(0.3),
        Type('print("saved!")'),
        Wait(0.3),
        Escape(),
        Wait(0.3),

        Say("Colon W, Enter.", wait=False),
        Type(":w"),
        Enter(),
        Wait(0.8),

        Say("That's it. Colon W saves your file. You'll type it a hundred times a day."),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f hello.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
