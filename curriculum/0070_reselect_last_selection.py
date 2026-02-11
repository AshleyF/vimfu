"""
Lesson 070: Reselect Last Selection

Sub-60-second lesson: gv re-highlights the previous visual selection.
Handy for acting on the same region again.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Reselect Last Selection",
    description="gv re-highlights the previous visual selection. "
                "Handy for acting on the same region again.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=211,
    tts_voice="echo",
    borderless=True,
    playlist="VimFu",

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Prepare workspace"),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Line("rm -f menu.py .menu.py.swp .menu.py.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*menu.py*"),
        Comment("Create demo file — pizza menu"),
        WriteFile("menu.py", """
            # pizza menu
            cheese = 8
            pepperoni = 10
            veggie = 9
            supreme = 12
            hawaiian = 11
        """),
        Line("clear"),
        Comment("Launch nvim before recording"),
        Line("nvim menu.py"),
        WaitForScreen("All", timeout=30.0),  # nvim status bar, not heredoc
        IfScreen("swap file", "d"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Reselect Last Selection", duration=3.0),
        Wait(0.7),

        # --- Intro ---
        Say("G V re-highlights your last visual selection. Same region, instantly.", wait=True),
        Wait(0.3),

        # --- Demo 1: select lines, indent, then gv to do a DIFFERENT action ---
        Say("Select the middle three pizzas. Capital V, then J J.", wait=False),
        Wait(0.3),
        Keys("2"),
        Keys("j"),          # pepperoni line
        Keys("V"),          # line visual
        Keys("j"),
        Keys("j"),          # pepperoni + veggie + supreme
        Wait(0.5),

        Say("Greater than to indent.", wait=False),
        Wait(0.3),
        Keys(">"),          # indent selection — selection disappears
        Wait(0.6),

        Say("Indented, but now I want to delete those same lines. G V to reselect.", wait=False),
        Wait(0.3),
        Keys("g"),
        Keys("v"),          # reselect last selection
        Wait(0.6),

        Say("Same three lines, re-highlighted. D to delete.", wait=False),
        Wait(0.3),
        Keys("d"),          # delete the selection
        Wait(0.6),

        Say("Gone. G V let me do a second, different action on the same region.", wait=True),
        Wait(0.3),

        # --- Undo both ---
        Say("Undo twice to bring them back.", wait=False),
        Keys("u"),
        Wait(0.3),
        Keys("u"),
        Wait(0.5),

        # --- Demo 2: select a word, escape, move away, gv to come back ---
        Say("Works for character selections too. V E to select cheese.", wait=False),
        Wait(0.3),
        Keys("g"),
        Keys("g"),
        Keys("j"),          # cheese line
        Keys("v"),          # character visual
        Keys("e"),          # select "cheese"
        Wait(0.5),

        Say("Escape. Move somewhere else.", wait=False),
        Wait(0.3),
        Escape(),
        Wait(0.3),
        Keys("3"),
        Keys("j"),          # move away
        Wait(0.5),

        Say("G V. Right back on cheese, no matter where the cursor was.", wait=True),
        Wait(0.3),
        Keys("g"),
        Keys("v"),          # reselect cheese
        Wait(0.6),

        Escape(),
        Wait(0.3),

        # --- Wrap up ---
        Say("G V. Reselect to apply a different action, or jump back to where you were.", wait=True),
        Wait(1.5),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f menu.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
