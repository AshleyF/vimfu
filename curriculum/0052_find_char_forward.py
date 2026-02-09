"""
Lesson 052: Find Character Forward

Sub-60-second lesson: Press f followed by a character to jump to
the next occurrence of that character on the current line.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Find Character Forward",
    description="Press f followed by a character to jump to the next occurrence "
                "of that character on the current line.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=193,
    tts_voice="echo",
    borderless=True,
    playlist="VimFu",

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Prepare workspace"),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Line("rm -f spawn.py .spawn.py.swp .spawn.py.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*spawn.py*"),
        Comment("Create demo file — game summoning system"),
        WriteFile("spawn.py", """
            cat = summon("whiskers", 9)
            dog = summon("barkley", 3)
            bug = summon("glitch", -1)
            npc = summon("bob", 99)
        """),
        Line("clear"),
        Comment("Launch nvim before recording"),
        Line("nvim spawn.py"),
        WaitForScreen("cat", timeout=10.0),
        IfScreen("swap file", "d"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Find Character Forward", duration=3.0),
        Wait(0.7),

        # --- Intro ---
        Say("F followed by a character jumps to it on the current line. Precision horizontal movement.", wait=True),
        Wait(0.3),

        # --- Demo 1: f on line 1 ---
        Say("Cursor is at the start. Press F W to jump to the W in whiskers.", wait=False),
        Wait(0.3),
        Keys("f"),
        Keys("w"),          # jump to 'w' in "whiskers"
        Wait(0.6),

        Say("Landed right on the W. One motion, no scrolling.", wait=True),
        Wait(0.3),

        # --- Demo 2: f again on same line ---
        Say("Press F nine to jump to the number.", wait=False),
        Wait(0.3),
        Keys("f"),
        Keys("9"),          # jump to '9' in 9)
        Wait(0.6),

        Say("Found the nine. F works with any character, letters, numbers, punctuation.", wait=True),
        Wait(0.3),

        # --- Demo 3: line 2 ---
        Say("Down to the next line.", wait=False),
        Wait(0.3),
        Keys("j"),          # line 2: dog = summon("barkley", 3) — col 25
        Keys("0"),          # back to start of line
        Wait(0.3),

        Say("F B to find barkley.", wait=False),
        Wait(0.3),
        Keys("f"),
        Keys("b"),          # jump to 'b' in "barkley" at col 14
        Wait(0.6),

        Say("There's barkley. F only searches the current line, never crosses to another.", wait=True),
        Wait(0.3),

        # --- Demo 4: line 3, f with a symbol ---
        Say("Down to the bug line. F minus.", wait=False),
        Wait(0.3),
        Keys("j"),          # line 3: bug = summon("glitch", -1) — col 14
        Wait(0.3),
        Keys("f"),
        Keys("-"),          # jump to '-' in "-1"
        Wait(0.6),

        Say("Found the minus sign. F works with letters, numbers, symbols, anything.", wait=True),
        Wait(0.3),

        # --- Wrap up ---
        Say("F plus a character. The sniper rifle of horizontal movement.", wait=True),
        Wait(1.5),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f spawn.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
