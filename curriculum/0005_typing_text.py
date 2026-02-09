"""
Lesson 005: Typing Text

Sub-60-second lesson: Once you're in insert mode, just type.
Backspace, Enter, Tab — everything works like a normal editor.
No surprises.
"""

import sys
from pathlib import Path

# ShellPilot DSL imports
sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, Backspace, IfScreen, WaitForScreen, Overlay


lesson = Demo(
    title="VimFu — Typing Text",
    description="In insert mode, Vim works like any other editor. Type, "
                "press Enter for new lines, Backspace to delete. "
                "No tricks — just type.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=46,
    tts_voice="echo",
    borderless=True,
    playlist="VimFu",

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Prepare workspace"),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Line("rm -f notes.txt .notes.txt.swp .notes.txt.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*notes.txt*"),
        Line("clear"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Typing Text", duration=3.0),
        Wait(0.7),

        # --- Open empty file and enter insert mode ---
        Say("When you open a file, you're in normal mode.", wait=False),
        Line("nvim notes.txt", delay=0.05),
        WaitForScreen("~", timeout=10.0),
        IfScreen("swap file", "d"),
        Wait(0.3),

        Say("Press I to enter insert mode.", wait=False),
        Keys("i"),
        Wait(0.5),

        Say("Now what? Just type. It works like any other editor.", wait=False),
        Wait(0.5),

        # --- Type a few lines naturally ---
        Type("Shopping list"),
        Wait(0.3),

        # --- Enter for new lines ---
        Say("Enter makes a new line.", wait=False),
        Enter(),
        Wait(0.3),
        Type("eggs"),
        Enter(),
        Type("milk"),
        Enter(),
        Type("bread"),
        Wait(0.5),

        # --- Backspace to fix bread → butter ---
        # "bread" — delete "read" (4 chars), leaving "b", then type "utter"
        Say("Backspace deletes backwards.", wait=False),
        Wait(0.3),
        Backspace(),
        Wait(0.15),
        Backspace(),
        Wait(0.15),
        Backspace(),
        Wait(0.15),
        Backspace(),
        Wait(0.3),
        Type("utter"),
        Wait(0.5),

        # --- Tab works ---
        Say("Enter, then Tab indents.", wait=False),
        Enter(),
        Keys("\t"),
        Type("salted"),
        Wait(0.5),

        # --- Wrap up ---
        Say("No surprises. In insert mode, your keyboard works normally."),

        Say("When you're done, Escape back to normal mode.", wait=False),
        Wait(0.3),
        Escape(),
        Wait(1.5),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f notes.txt"),
    ],
)


if __name__ == "__main__":
    lesson.run()
