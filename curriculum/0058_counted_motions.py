"""
Lesson 058: Counted Motions

Sub-60-second lesson: Prefix any motion with a number to repeat it.
5j moves down 5 lines. 3w jumps 3 words. Counts supercharge every motion.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Counted Motions",
    description="Prefix any motion with a number to repeat it. "
                "5j moves down 5 lines, 3w jumps 3 words.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=199,
    tts_voice="echo",
    borderless=True,
    playlist="VimFu",

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Prepare workspace"),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Line("rm -f dungeon.py .dungeon.py.swp .dungeon.py.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*dungeon.py*"),
        Comment("Create demo file — dungeon map"),
        WriteFile("dungeon.py", """
            # dungeon: rooms, traps, loot
            room = "entry"
            trap = False
            loot = "key"
            boss = None
            room = "vault"
            trap = True
            loot = "gold"
            boss = "dragon"
            room = "exit"
            trap = False
            loot = "gem"
            boss = None
        """),
        Line("clear"),
        Comment("Launch nvim before recording"),
        Line("nvim dungeon.py"),
        WaitForScreen("dungeon", timeout=10.0),
        IfScreen("swap file", "d"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Counted Motions", duration=3.0),
        Wait(0.7),

        # --- Intro ---
        Say("Put a number before any motion to repeat it. Counts turn one step into a leap.", wait=True),
        Wait(0.3),

        # --- Demo 1: 10l horizontal ---
        Say("Cursor is on the first line. Ten L to jump right.", wait=False),
        Wait(0.3),
        Keys("1"),
        Keys("0"),
        Keys("l"),          # right 10 chars on comment line
        Wait(0.6),

        Say("Ten characters right in one move.", wait=True),
        Wait(0.3),

        # --- Demo 2: 4j ---
        Say("Now four J to jump down four lines.", wait=False),
        Wait(0.3),
        Keys("4"),
        Keys("j"),          # row 0 → row 4
        Wait(0.6),

        Say("Four lines down. The count multiplies the motion.", wait=True),
        Wait(0.3),

        # --- Demo 3: 3w ---
        Say("Three W to jump three words forward.", wait=False),
        Wait(0.3),
        Keys("3"),
        Keys("w"),          # 3 words forward
        Wait(0.6),

        Say("Three words in one motion.", wait=True),
        Wait(0.3),

        # --- Demo 4: 6j ---
        Say("Six J to skip ahead.", wait=False),
        Wait(0.3),
        Keys("6"),
        Keys("j"),          # down 6 more lines
        Wait(0.6),

        Say("Six lines. Way faster than pressing J six times.", wait=True),
        Wait(0.3),

        # --- Demo 5: 8k back up ---
        Say("Eight K to fly back up.", wait=False),
        Wait(0.3),
        Keys("8"),
        Keys("k"),          # up 8 lines
        Wait(0.6),

        Say("Eight lines up. Counts work with J, K, W, B, L, any motion.", wait=True),
        Wait(0.3),

        # --- Wrap up ---
        Say("Number plus motion. One of the biggest multipliers in Vim.", wait=True),
        Wait(1.5),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f dungeon.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
