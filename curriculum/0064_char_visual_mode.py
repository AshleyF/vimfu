"""
Lesson 064: Character Visual Mode

Sub-60-second lesson: Press v to start selecting character by character.
Move the cursor and the selection grows. Press Escape to cancel.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Character Visual Mode",
    description="Press v to start selecting character by character. "
                "Move the cursor and the selection grows.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=205,
    tts_voice="echo",
    borderless=True,
    playlist="VimFu",

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Prepare workspace"),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Line("rm -f spell.py .spell.py.swp .spell.py.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*spell.py*"),
        Comment("Create demo file — spell book"),
        WriteFile("spell.py", """
            # spell book
            fire = "fireball"
            ice = "blizzard"
            heal = "restoration"
            dark = "shadow bolt"
        """),
        Line("clear"),
        Comment("Launch nvim before recording"),
        Line("nvim spell.py"),
        WaitForScreen("All", timeout=30.0),  # nvim status bar, not heredoc
        IfScreen("swap file", "d"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Character Visual Mode", duration=3.0),
        Wait(0.7),

        # --- Intro ---
        Say("Press V to start selecting text character by character. This is visual mode.", wait=True),
        Wait(0.3),

        # --- Demo 1: v then move right to select a word ---
        Say("Go to the fire line. Press V to start selecting.", wait=False),
        Wait(0.3),
        Keys("j"),          # fire = "fireball"
        Wait(0.3),
        Keys("v"),          # enter visual mode
        Wait(0.5),

        Say("See the highlight? Now every motion extends the selection. E to select to end of word.", wait=False),
        Wait(0.3),
        Keys("e"),          # select "fire"
        Wait(0.6),

        Say("The word fire is selected. I could delete it with D, yank it with Y, or change it.", wait=True),
        Wait(0.3),

        Say("Escape to cancel.", wait=False),
        Wait(0.3),
        Escape(),
        Wait(0.5),

        # --- Demo 2: v then w w to select more ---
        Say("Try again on the ice line. V to start, then W W to extend across words.", wait=False),
        Wait(0.3),
        Keys("j"),          # ice = "blizzard"
        Wait(0.3),
        Keys("v"),          # visual mode
        Wait(0.3),
        Keys("w"),
        Keys("w"),          # select "ice = "
        Wait(0.6),

        Say("Two words selected. The highlight follows the cursor.", wait=True),
        Wait(0.3),

        Escape(),
        Wait(0.3),

        # --- Demo 3: v then $ to select to end of line ---
        Say("On the heal line. V then dollar sign selects to the end of the line.", wait=False),
        Wait(0.3),
        Keys("j"),          # heal = "restoration"
        Wait(0.3),
        Keys("v"),          # visual mode
        Wait(0.3),
        Keys("$"),          # select to end of line
        Wait(0.6),

        Say("The entire line contents selected. Any motion works inside visual mode.", wait=True),
        Wait(0.3),

        Escape(),
        Wait(0.3),

        # --- Wrap up ---
        Say("Lowercase V. Select text, then act on it. The visual feedback makes it safe to experiment.", wait=True),
        Wait(1.5),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f spell.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
