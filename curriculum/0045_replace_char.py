"""
Lesson 045: Replace a Character

Sub-60-second lesson: Press r followed by a character to replace
the character under the cursor — without entering insert mode.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Replace a Character",
    description="Press r followed by a character to replace the character "
                "under the cursor without entering insert mode.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=186,
    tts_voice="echo",
    borderless=True,
    playlist="VimFu",

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Prepare workspace"),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Line("rm -f typo.py .typo.py.swp .typo.py.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*typo.py*"),
        Comment("Create demo file"),
        WriteFile("typo.py", """
            tag = "dork"
            count = 9090
            flag = Trua
        """),
        Line("clear"),
        Comment("Launch nvim before recording"),
        Line("nvim typo.py"),
        WaitForScreen("mode", timeout=10.0),
        IfScreen("swap file", "d"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Replace a Character", duration=3.0),
        Wait(0.7),

        # --- Intro ---
        Say("R replaces one character. You stay in normal mode.", wait=True),
        Wait(0.3),

        # --- Demo 1: fix "dork" → "dark" (replace 'o' with 'a') ---
        Say("This says dork. Should be dark.", wait=False),
        Wait(0.3),
        Keys("f"),
        Keys("o"),       # fo — jump to 'o' in "dork" (col 8)
        Keys("r"),
        Keys("a"),       # ra — replace 'o' with 'a' → "dark"
        Wait(0.6),

        Say("R A. One key to replace, one key for the new character."),
        Wait(0.3),

        # --- Demo 2: fix 9090 → 8080 (col 8 aligns with first '9') ---
        Say("Now the count. Nine zero nine zero should be eight zero eight zero.", wait=False),
        Wait(0.3),
        Keys("j"),       # line 2: count = 9090 — cursor lands on col 8 = first '9'
        Keys("r"),
        Keys("8"),       # r8 — replace first '9' with '8'
        Wait(0.4),
        Keys("l"),       # col 9: '0'
        Keys("l"),       # col 10: second '9'
        Keys("r"),
        Keys("8"),       # r8 — replace second '9' → 8080
        Wait(0.6),

        Say("Two quick fixes. Still in normal mode the whole time."),
        Wait(0.3),

        # --- Demo 3: fix "Trua" → "True" (col 10 aligns with 'a') ---
        Say("One more. Trua should be True.", wait=False),
        Wait(0.3),
        Keys("j"),       # line 3: flag = Trua — cursor lands on col 10 = 'a'
        Keys("r"),
        Keys("e"),       # re — replace 'a' with 'e' → "True"
        Wait(0.6),

        Say("R E. Fixed. No insert mode needed."),
        Wait(0.3),

        # --- Wrap up ---
        Say("R plus any character. Quick single-character fix."),
        Wait(1.5),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f typo.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
