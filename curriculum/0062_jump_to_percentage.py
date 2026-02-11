"""
Lesson 062: Jump to Percentage

Sub-60-second lesson: 50% jumps to the middle of the file.
Any number followed by percent goes to that percentage through the file.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Jump to Percentage",
    description="50% jumps to the middle of the file. "
                "Any number followed by percent goes to that percentage through the file.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=203,
    tts_voice="echo",
    borderless=True,
    playlist="VimFu",

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Prepare workspace"),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Line("rm -f quest.py .quest.py.swp .quest.py.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*quest.py*"),
        Comment("Create demo file — RPG quest log (40 lines, scrolls off screen)"),
        WriteFile("quest.py", """
            # quest log
            quest_1 = "find the lost sword"
            quest_2 = "rescue the princess"
            quest_3 = "defeat the goblin king"
            quest_4 = "collect ten mushrooms"
            quest_5 = "explore the dark cave"
            quest_6 = "brew a healing potion"
            quest_7 = "forge the magic ring"
            quest_8 = "tame the wild dragon"
            quest_9 = "unlock the secret door"
            quest_10 = "steal the golden egg"
            quest_11 = "cross the lava bridge"
            quest_12 = "befriend the ghost"
            quest_13 = "decode the ancient map"
            quest_14 = "survive the sandstorm"
            quest_15 = "climb the frozen peak"
            quest_16 = "outsmart the sphinx"
            quest_17 = "raid the pirate ship"
            quest_18 = "tame the sea serpent"
            quest_19 = "find the hidden temple"
            quest_20 = "light the dark beacon"
            quest_21 = "calm the thunder wolf"
            quest_22 = "mend the broken crown"
            quest_23 = "open the void portal"
            quest_24 = "charm the stone giant"
            quest_25 = "ride the sky whale"
            quest_26 = "wake the sleeping god"
            quest_27 = "seal the demon rift"
            quest_28 = "win the dragon race"
            quest_29 = "trick the shadow fox"
            quest_30 = "map the crystal maze"
            quest_31 = "free the cursed knight"
            quest_32 = "brew the time elixir"
            quest_33 = "sink the ghost ship"
            quest_34 = "tame the fire hawk"
            quest_35 = "solve the moon riddle"
            quest_36 = "break the ice throne"
            quest_37 = "clear the poison swamp"
            quest_38 = "unite the lost tribes"
            quest_39 = "face the final boss"
        """),
        Line("clear"),
        Comment("Launch nvim with line numbers for percentage navigation"),
        Line("nvim -c 'set number' quest.py"),
        WaitForScreen("Top", timeout=30.0),  # file too long for screen, nvim shows "Top" not "All"
        IfScreen("swap file", "d"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Jump to Percentage", duration=3.0),
        Wait(0.7),

        # --- Intro ---
        Say("A number then percent jumps to that percentage through the file.", wait=True),
        Wait(0.3),

        # --- Demo 1: 50% → line 20 ---
        Say("Fifty percent.", wait=False),
        Wait(0.3),
        Keys("5"),
        Keys("0"),
        Keys("%", overlay="% of file"),
        Wait(0.6),

        Say("Line twenty. The screen scrolled to the middle of the file.", wait=True),
        Wait(0.3),

        # --- Demo 2: 100% → line 40 ---
        Say("One hundred percent. The very last line.", wait=False),
        Wait(0.3),
        Keys("1"),
        Keys("0"),
        Keys("0"),
        Keys("%", overlay="% of file"),
        Wait(0.6),

        Say("The final boss. Bottom of the file.", wait=True),
        Wait(0.3),

        # --- Demo 3: 75% → line 30 ---
        Say("Seventy five percent.", wait=False),
        Wait(0.3),
        Keys("7"),
        Keys("5"),
        Keys("%", overlay="% of file"),
        Wait(0.6),

        Say("Three quarters through. Trick the shadow fox.", wait=True),
        Wait(0.3),

        # --- Demo 4: 1% back to top ---
        Say("One percent goes back to the top.", wait=False),
        Wait(0.3),
        Keys("1"),
        Keys("%", overlay="% of file"),
        Wait(0.6),

        Say("Line one. Back where we started.", wait=True),
        Wait(0.3),

        # --- Wrap up ---
        Say("Number percent. Jump anywhere in a big file without knowing line numbers.", wait=True),
        Wait(1.5),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f quest.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
