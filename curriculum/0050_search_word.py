"""
Lesson 050: Search Word Under Cursor

Sub-60-second lesson: Press * to search forward for the exact word
under the cursor. No typing needed.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Search Word Under Cursor",
    description="Press * to search forward for the exact word under the cursor. "
                "No typing needed — just one key.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=191,
    tts_voice="echo",
    borderless=True,
    playlist="VimFu",

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Prepare workspace"),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Line("rm -f trace.py .trace.py.swp .trace.py.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*trace.py*"),
        Comment("Create demo file"),
        WriteFile("trace.py", """
            name = "vim"
            kind = "tool"
            name = "nano"
            kind = "tool"
            name = "code"
            kind = "app"
        """),
        Line("clear"),
        Comment("Launch nvim before recording"),
        Line("nvim trace.py"),
        WaitForScreen("name", timeout=10.0),
        IfScreen("swap file", "d"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Search Word Under Cursor", duration=3.0),
        Wait(0.7),

        # --- Intro ---
        Say("Star searches for the word under your cursor. One key, no typing.", wait=True),
        Wait(0.3),

        # --- Demo 1: cursor on "name", press * ---
        Say("Cursor is on name. Press star.", wait=False),
        Wait(0.3),
        Keys("*"),          # search forward for "name" — jumps to line 2
        Wait(0.6),

        Say("Jumped to the next name. Star found every match instantly."),
        Wait(0.3),

        # --- Demo 2: press * again to cycle ---
        Say("Star again.", wait=False),
        Wait(0.3),
        Keys("*"),          # next "name" — line 4
        Wait(0.5),

        Say("Third name. Star works just like slash, but you don't type anything."),
        Wait(0.3),

        # --- Demo 3: move to a different word and * ---
        Say("Now move to kind and try star.", wait=False),
        Wait(0.3),
        Keys("j"),          # line 5: kind = "app"
        Keys("*"),          # search for "kind" — wraps to line 1
        Wait(0.6),

        Say("Found kind. Star picks up whatever word the cursor is on."),
        Wait(0.3),

        # --- Wrap up ---
        Say("Star. The fastest search in Vim. Land on a word and go."),
        Wait(1.5),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f trace.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
