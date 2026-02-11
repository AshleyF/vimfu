"""
Lesson 061: Go to Line by Count

Sub-60-second lesson: 42G jumps to line 42. Same as :42 Enter.
A count before G goes straight to that line number.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Go to Line by Count",
    description="42G jumps to line 42. Same as :42 Enter. "
                "A count before G goes straight to that line number.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=202,
    tts_voice="echo",
    borderless=True,
    playlist="VimFu",

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Prepare workspace"),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Line("rm -f tower.py .tower.py.swp .tower.py.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*tower.py*"),
        Comment("Create demo file — tower defense config with many lines"),
        WriteFile("tower.py", """
            # tower defense config
            wave_1 = "goblins"
            wave_2 = "orcs"
            wave_3 = "trolls"
            wave_4 = "dragons"
            wave_5 = "demons"
            gold = 500
            tower_a = "archer"
            tower_b = "mage"
            tower_c = "cannon"
            tower_d = "frost"
            boss = "lich king"
            hp = 9999
            loot = "legendary sword"
        """),
        Line("clear"),
        Comment("Launch nvim with line numbers — essential for a line-navigation lesson"),
        Line("nvim -c 'set number' tower.py"),
        WaitForScreen("All", timeout=30.0),        # nvim status bar, not heredoc
        IfScreen("swap file", "d"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Go to Line by Count", duration=3.0),
        Wait(0.7),

        # --- Intro ---
        Say("A number before capital G jumps straight to that line.", wait=True),
        Wait(0.3),

        # --- Demo 1: 7G ---
        Say("Seven capital G.", wait=False),
        Wait(0.3),
        Keys("7"),
        Keys("G", overlay="go to line"),  # with count, G = go to line (not file end)
        Wait(0.6),

        Say("Line seven. The gold line. Instant jump.", wait=True),
        Wait(0.3),

        # --- Demo 2: 12G ---
        Say("Twelve capital G.", wait=False),
        Wait(0.3),
        Keys("1"),
        Keys("2"),
        Keys("G", overlay="go to line"),  # with count, G = go to line (not file end)
        Wait(0.6),

        Say("Line twelve. The boss. No scrolling, no counting lines.", wait=True),
        Wait(0.3),

        # --- Demo 3: :5 Enter (colon method) ---
        Say("You can also type colon five Enter.", wait=False),
        Wait(0.3),
        Type(":5"),
        Enter(),            # jump to line 5: wave_4 = "dragons"
        Wait(0.6),

        Say("Same result, different syntax. Both take you to line five.", wait=True),
        Wait(0.3),

        # --- Demo 4: 1G back to top ---
        Say("One capital G goes to line one. Same as G G.", wait=False),
        Wait(0.3),
        Keys("1"),
        Keys("G", overlay="go to line"),  # with count, G = go to line
        Wait(0.6),

        Say("Back at the top.", wait=True),
        Wait(0.3),

        # --- Wrap up ---
        Say("Number capital G. Jump to any line in the file instantly.", wait=True),
        Wait(1.5),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f tower.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
