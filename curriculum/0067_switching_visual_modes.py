"""
Lesson 067: Switching Visual Modes

Sub-60-second lesson: While in visual mode, press v, V, or Ctrl-V
to switch between character, line, and block selection on the fly.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Switching Visual Modes",
    description="While in visual mode, press v, V, or Ctrl-V "
                "to switch between character, line, and block selection.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=208,
    tts_voice="echo",
    borderless=True,
    playlist="VimFu",

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Prepare workspace"),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Line("rm -f pet.py .pet.py.swp .pet.py.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*pet.py*"),
        Comment("Create demo file — pet stats"),
        WriteFile("pet.py", """
            # pet stats
            cat  = 9
            dog  = 7
            fish = 3
            bird = 5
        """),
        Line("clear"),
        Comment("Launch nvim before recording"),
        Line("nvim pet.py"),
        WaitForScreen("All", timeout=30.0),  # nvim status bar, not heredoc
        IfScreen("swap file", "d"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Switching Visual Modes", duration=3.0),
        Wait(0.7),

        # --- Intro ---
        Say("You can switch between visual modes without leaving visual mode.", wait=True),
        Wait(0.3),

        # --- Demo 1: start with v, extend, then switch to V ---
        Say("Start with lowercase V on the cat line. Select a few characters.", wait=False),
        Wait(0.3),
        Keys("j"),          # cat = 9
        Wait(0.3),
        Keys("v"),          # character visual
        Keys("e"),          # select "cat"
        Wait(0.5),

        Say("Character selection. Now press capital V to switch to line mode.", wait=False),
        Wait(0.3),
        Keys("V"),          # switch to line visual
        Wait(0.6),

        Say("Now the whole line is selected. Same starting point, different mode.", wait=True),
        Wait(0.3),

        # --- Switch to block mode ---
        Say("Control V to switch to block mode.", wait=False),
        Wait(0.3),
        Keys("\x16"),       # Ctrl-V: switch to block visual
        Wait(0.6),

        Say("Now it is a block selection. Three modes, same anchor point.", wait=True),
        Wait(0.3),

        # --- Extend the block down ---
        Say("Extend the block down with J J.", wait=False),
        Wait(0.3),
        Keys("j"),
        Keys("j"),          # extend block down through dog, fish
        Wait(0.6),

        Say("A rectangle across three lines.", wait=True),
        Wait(0.3),

        # --- Switch back to line mode ---
        Say("Capital V again. Back to line mode, now covering three lines.", wait=False),
        Wait(0.3),
        Keys("V"),          # switch to line visual
        Wait(0.6),

        Say("Three full lines selected. You can keep switching until the selection is exactly what you want.", wait=True),
        Wait(0.3),

        Escape(),
        Wait(0.3),

        # --- Wrap up ---
        Say("V, capital V, control V. Switch freely between visual modes mid-selection.", wait=True),
        Wait(1.5),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f pet.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
