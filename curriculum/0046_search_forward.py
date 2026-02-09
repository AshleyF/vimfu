"""
Lesson 046: Search Forward

Sub-60-second lesson: Type /pattern to search forward for text.
Press Enter to jump to the first match.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Search Forward",
    description="Type /pattern and press Enter to search forward for text. "
                "The cursor jumps to the first match.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=187,
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
        Comment("Create demo file"),
        WriteFile("config.py", """
            host = "local"
            port = 8080
            mode = "debug"
            flag = True
            host = "cloud"
            port = 9090
            mode = "live"
            flag = False
        """),
        Line("clear"),
        Comment("Launch nvim before recording"),
        Line("nvim config.py"),
        WaitForScreen("host", timeout=10.0),
        IfScreen("swap file", "d"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Search Forward", duration=3.0),
        Wait(0.7),

        # --- Intro ---
        Say("Slash searches forward. Type a pattern and press Enter.", wait=True),
        Wait(0.3),

        # --- Demo 1: search for "mode" ---
        Say("Let's find mode.", wait=False),
        Wait(0.3),
        Keys("/"),          # enter search mode
        Type("mode"),       # type search pattern
        Enter(),            # jump to first match
        Wait(0.6),

        Say("Slash mode Enter. Cursor jumped right to it."),
        Wait(0.3),

        # --- Demo 2: search for "flag" ---
        Say("Now let's search for flag.", wait=False),
        Wait(0.3),
        Keys("/"),
        Type("flag"),
        Enter(),
        Wait(0.6),

        Say("Jumped to flag on the next line."),
        Wait(0.3),

        # --- Demo 3: search wraps around ---
        Say("Now search for local. It's above us, but slash wraps around.", wait=False),
        Wait(0.3),
        Keys("/"),
        Type("local"),
        Enter(),
        Wait(0.6),

        Say("Wrapped back to line one. Search always loops around the file."),
        Wait(0.3),

        # --- Wrap up ---
        Say("Slash, type your pattern, Enter. The fastest way to jump anywhere."),
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
