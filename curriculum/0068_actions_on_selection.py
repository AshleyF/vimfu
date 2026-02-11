"""
Lesson 068: Actions on Selection

Sub-60-second lesson: In visual mode, press d to delete, c to change,
y to yank, > to indent, or < to unindent the selection.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Actions on Selection",
    description="In visual mode, press d to delete, c to change, "
                "y to yank, angle bracket to indent or unindent.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=209,
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
        Comment("Create demo file — loot table"),
        WriteFile("loot.py", """
            # loot table
            sword = 10
            shield = 5
            potion = 20
            scroll = 8
            gem = 50
        """),
        Line("clear"),
        Comment("Launch nvim before recording"),
        Line("nvim loot.py"),
        WaitForScreen("All", timeout=30.0),  # nvim status bar, not heredoc
        IfScreen("swap file", "d"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Actions on Selection", duration=3.0),
        Wait(0.7),

        # --- Intro ---
        Say("Once you have a visual selection, one key acts on it. D deletes, Y yanks, greater than indents.", wait=True),
        Wait(0.3),

        # --- Demo 1: V j d to delete two lines ---
        Say("Select the sword and shield lines with capital V then J.", wait=False),
        Wait(0.3),
        Keys("j"),          # sword = 10
        Keys("V"),          # line visual
        Keys("j"),          # extend to shield
        Wait(0.5),

        Say("D to delete.", wait=False),
        Wait(0.3),
        Keys("d"),          # delete both lines
        Wait(0.6),

        Say("Both lines gone.", wait=True),
        Wait(0.3),

        Say("Undo.", wait=False),
        Keys("u"),
        Wait(0.5),

        # --- Demo 2: V j j > to indent ---
        Say("Select three lines. Capital V, then J J.", wait=False),
        Wait(0.3),
        Keys("2"),
        Keys("j"),          # potion line
        Keys("V"),          # line visual
        Keys("j"),
        Keys("j"),          # extend to gem
        Wait(0.5),

        Say("Greater than to indent.", wait=False),
        Wait(0.3),
        Keys(">"),          # indent selection
        Wait(0.6),

        Say("All three lines shifted right.", wait=True),
        Wait(0.3),

        Say("Undo.", wait=False),
        Keys("u"),
        Wait(0.5),

        # --- Demo 3: v e y p to yank and paste ---
        Say("Select a word with V E on the sword line.", wait=False),
        Wait(0.3),
        Keys("g"),
        Keys("g"),
        Keys("j"),          # sword line
        Keys("v"),          # character visual
        Keys("e"),          # select "sword"
        Wait(0.5),

        Say("Y to yank it.", wait=False),
        Wait(0.3),
        Keys("y"),          # yank selection
        Wait(0.3),

        Say("Go to the end of the file and paste.", wait=False),
        Wait(0.3),
        Keys("G"),          # last line
        Keys("o"),          # open line below
        Type("best = "),
        Escape(),
        Keys("p"),          # paste "sword"
        Wait(0.6),

        Say("Yanked from visual mode, pasted right where we needed it.", wait=True),
        Wait(0.3),

        Keys("u"),          # undo the paste
        Wait(0.2),
        Keys("u"),          # undo the new line
        Wait(0.3),

        # --- Wrap up ---
        Say("Select, then act. D, C, Y, greater than, less than. Visual mode makes it obvious what you are editing.", wait=True),
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
