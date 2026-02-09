"""
Lesson 033: Delete Word

Sub-60-second lesson: Press dw to delete from the cursor to the start
of the next word. Your first operator + motion combo.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Delete Word",
    description="Press dw to delete from the cursor to the start of the next word. "
                "The d operator combined with the w motion.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=174,
    tts_voice="echo",
    borderless=True,
    playlist="VimFu",

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Prepare workspace"),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Line("rm -f config.py .config.py.swp .config.py.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*config.py*"),
        Comment("Create a file with extra words to delete"),
        WriteFile("config.py", """
            color = "dark blue"
            shape = "very large"
            title = "old legacy"
        """),
        Line("clear"),
        Comment("Launch nvim before recording"),
        Line("nvim config.py"),
        WaitForScreen("color", timeout=10.0),
        IfScreen("swap file", "d"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Delete Word", duration=3.0),
        Wait(0.7),

        # --- Intro ---
        Say("D W deletes from the cursor to the next word.", wait=True),
        Wait(0.3),

        # --- Delete "dark " from line 1 ---
        Say("This should say blue, not dark blue.", wait=False),
        Wait(0.3),
        Keys("f"),
        Keys("d"),       # fd — find 'd' in 'dark'
        Wait(0.3),
        Keys("d"),
        Keys("w"),       # dw — deletes "dark "
        Wait(0.6),

        Say("Gone. D is the delete operator. W is the word motion."),
        Wait(0.3),

        # --- Delete "very " from line 2 ---
        Say("Same idea on line two.", wait=False),
        Wait(0.3),
        Keys("j"),       # down — cursor col 9 lands right on 'v' in 'very'
        Wait(0.3),
        Keys("d"),
        Keys("w"),       # dw — deletes "very "
        Wait(0.6),

        Say("D W again. The word and the space after it are gone."),
        Wait(0.3),

        # --- Delete "old " from line 3 ---
        Say("One more.", wait=False),
        Wait(0.3),
        Keys("j"),       # down — cursor col 9 lands right on 'o' in 'old'
        Wait(0.3),
        Keys("d"),
        Keys("w"),       # dw — deletes "old "
        Wait(0.6),

        Say("Three words deleted. Same two keys every time."),
        Wait(0.3),

        # --- Undo all ---
        Keys("u"),
        Wait(0.1),
        Keys("u"),
        Wait(0.1),
        Keys("u"),
        Wait(0.5),

        # --- Wrap up ---
        Say("D W. Delete a word."),
        Wait(1.5),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f config.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
