"""
Lesson 036: Change Word

Sub-60-second lesson: Press cw to delete a word and enter insert mode.
Delete + insert in one move — the change operator with word motion.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Change Word",
    description="Press cw to delete a word and enter insert mode. "
                "The change operator deletes and puts you in insert mode.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=177,
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
        Comment("Create a file with words to change"),
        WriteFile("config.py", """
            theme = "red"
            width = "small"
            label = "old"
        """),
        Line("clear"),
        Comment("Launch nvim before recording"),
        Line("nvim config.py"),
        WaitForScreen("theme", timeout=10.0),
        IfScreen("swap file", "d"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Change Word", duration=3.0),
        Wait(0.7),

        # --- Intro ---
        Say("C W deletes a word and drops you into insert mode.", wait=True),
        Wait(0.3),

        # --- Change "red" to "blue" ---
        Say("Let's change red to blue.", wait=False),
        Wait(0.3),
        Keys("f"),
        Keys("r"),       # fr — find 'r' in "red"
        Wait(0.3),
        Keys("c"),
        Keys("w"),       # cw — delete "red" and enter insert mode
        Wait(0.3),
        Type("blue"),    # type the replacement
        Wait(0.3),
        Escape(),        # back to normal mode
        Wait(0.5),

        Say("C W deleted the word and let me type the new one."),
        Wait(0.3),

        # --- Change "small" to "large" ---
        Say("Same thing on line two.", wait=False),
        Wait(0.3),
        Keys("j"),       # down to line 2
        Keys("0"),
        Keys("f"),
        Keys("s"),       # fs — find 's' in "small"
        Wait(0.3),
        Keys("c"),
        Keys("w"),       # cw — delete "small" and enter insert
        Wait(0.3),
        Type("large"),
        Wait(0.3),
        Escape(),
        Wait(0.5),

        Say("Deleted and replaced in one move."),
        Wait(0.3),

        # --- Change "old" to "new" ---
        Say("One more.", wait=False),
        Wait(0.3),
        Keys("j"),       # down to line 3
        Keys("0"),
        Keys("f"),
        Keys("o"),       # fo — find 'o' in "old"
        Wait(0.3),
        Keys("c"),
        Keys("w"),       # cw — delete "old" and enter insert
        Wait(0.3),
        Type("new"),
        Wait(0.3),
        Escape(),
        Wait(0.5),

        Say("C is the change operator. Like D for delete, but drops you in insert mode."),
        Wait(0.3),

        # --- Wrap up ---
        Say("C W. Change a word."),
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
