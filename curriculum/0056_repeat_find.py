"""
Lesson 056: Repeat Find

Sub-60-second lesson: Press semicolon to repeat the last f/F/t/T
in the same direction. Hop through matches without retyping.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Repeat Find",
    description="Press semicolon to repeat the last f/F/t/T motion "
                "in the same direction.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=197,
    tts_voice="echo",
    borderless=True,
    playlist="VimFu",

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Prepare workspace"),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Line("rm -f loot.py .loot.py.swp .loot.py.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*loot.py*"),
        Comment("Create demo file — game inventory"),
        WriteFile("loot.py", """
            items = "axe, bow, cup, gem, orb"
            stats = "hp:5, mp:3, xp:0, gp:9"
            spells = "fire, ice, bolt, heal"
        """),
        Line("clear"),
        Comment("Launch nvim before recording"),
        Line("nvim loot.py"),
        WaitForScreen("items", timeout=10.0),
        IfScreen("swap file", "d"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Repeat Find", duration=3.0),
        Wait(0.7),

        # --- Intro ---
        Say("Semicolon repeats your last F or T motion. No need to type the character again.", wait=True),
        Wait(0.3),

        # --- Demo 1: f, then ; to hop through commas ---
        Say("F comma to find the first comma.", wait=False),
        Wait(0.3),
        Keys("f"),
        Keys(","),          # first ',' on line 1
        Wait(0.5),

        Say("Now semicolon.", wait=False),
        Wait(0.3),
        Keys(";"),          # next ','
        Wait(0.4),

        Say("Again.", wait=False),
        Wait(0.3),
        Keys(";"),          # next ','
        Wait(0.4),

        Say("And again.", wait=False),
        Wait(0.3),
        Keys(";"),          # last ','
        Wait(0.5),

        Say("Four commas, one F, three semicolons. Hop hop hop.", wait=True),
        Wait(0.3),

        # --- Demo 2: new find on line 2 ---
        Say("Down to the stats line. F colon.", wait=False),
        Wait(0.3),
        Keys("j"),
        Keys("0"),
        Wait(0.3),
        Keys("f"),
        Keys(":"),          # first ':' on line 2
        Wait(0.5),

        Say("Semicolon picks up the new target.", wait=False),
        Wait(0.3),
        Keys(";"),          # next ':'
        Wait(0.4),
        Keys(";"),          # next ':'
        Wait(0.4),
        Keys(";"),          # last ':'
        Wait(0.5),

        Say("Hopped through every colon. Semicolon always repeats the last find.", wait=True),
        Wait(0.3),

        # --- Demo 3: works with t too ---
        Say("Works with T too. Down one more. T comma.", wait=False),
        Wait(0.3),
        Keys("j"),
        Keys("0"),
        Wait(0.3),
        Keys("t"),
        Keys(","),          # till first ','
        Wait(0.5),

        Say("Semicolon.", wait=False),
        Wait(0.3),
        Keys(";"),          # till next ','
        Wait(0.4),
        Keys(";"),          # till next ','
        Wait(0.5),

        Say("Semicolon repeats whatever the last motion was. F, T, capital F, capital T.", wait=True),
        Wait(0.3),

        # --- Wrap up ---
        Say("Semicolon. Find once, repeat forever.", wait=True),
        Wait(1.5),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f loot.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
