"""
Lesson 023: End of Word

Sub-60-second lesson: Press e to jump to the end of the current/next word.
Like w, but lands on the last character instead of the first.
"""

import sys
from pathlib import Path

# ShellPilot DSL imports
sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — End of Word",
    description="Press e to jump to the end of the current or next word. "
                "Like w but lands on the last character.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=84,
    tts_voice="echo",
    borderless=True,
    playlist="VimFu",

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Prepare workspace"),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Line("rm -f words.py .words.py.swp .words.py.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*words.py*"),
        Comment("Create a file with some code"),
        WriteFile("words.py", """
            name = "vim master"
            level = 42
            print(name, level)
        """),
        Line("clear"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="End of Word", duration=3.0),
        Wait(0.7),

        # --- Open file ---
        Say("W jumps to the start of the next word.", wait=True),
        Line("nvim words.py", delay=0.05),
        WaitForScreen("vim master", timeout=10.0),
        IfScreen("swap file", "d"),
        Wait(0.5),

        # --- Demonstrate e ---
        Say("E jumps to the end instead.", wait=False),
        Wait(0.3),
        # Cursor starts at (0,0) 'n' of 'name'
        Keys("e"),       # end of 'name' → col 3
        Wait(0.4),
        Keys("e"),       # end of '=' → col 5
        Wait(0.4),
        Keys("e"),       # end of '"vim' → col 10  (quotes are punctuation word)
        Wait(0.4),
        Keys("e"),       # end of next word
        Wait(0.5),

        Say("Each E lands on the last letter of a word."),
        Wait(0.3),

        # --- Compare with w ---
        Say("W lands on the first letter. E lands on the last.", wait=False),
        Wait(0.3),
        Keys("e"),
        Wait(0.4),
        Keys("e"),
        Wait(0.4),
        Keys("e"),
        Wait(0.4),
        Keys("e"),
        Wait(0.5),

        Say("It wraps across lines, just like W."),
        Wait(0.3),

        # --- Race through ---
        Say("Watch the cursor hop to each word ending.", wait=False),
        Wait(0.3),
        Keys("g"),
        Keys("g"),
        Keys("0"),
        Wait(0.3),
        Keys("e"),
        Wait(0.15),
        Keys("e"),
        Wait(0.15),
        Keys("e"),
        Wait(0.15),
        Keys("e"),
        Wait(0.15),
        Keys("e"),
        Wait(0.15),
        Keys("e"),
        Wait(0.15),
        Keys("e"),
        Wait(0.15),
        Keys("e"),
        Wait(0.15),
        Keys("e"),
        Wait(0.15),
        Keys("e"),
        Wait(0.5),

        # --- Wrap up ---
        Say("E for end of word. Pair it with W and B."),
        Wait(1.5),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f words.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
