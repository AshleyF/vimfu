"""
Lesson 047: Search Backward

Sub-60-second lesson: Type ?pattern to search backward from
the cursor. It's the reverse of / (slash).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Search Backward",
    description="Type ?pattern and press Enter to search backward. "
                "It's the reverse of / (slash).",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=188,
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
        Overlay("VimFu", caption="Search Backward", duration=3.0),
        Wait(0.7),

        # --- Intro ---
        Say("Question mark searches backward. The opposite of slash.", wait=True),
        Wait(0.3),

        # --- Move to bottom first so backward search makes sense ---
        Keys("G"),          # jump to last line
        Wait(0.3),

        # --- Demo 1: search backward for "mode" ---
        Say("We're at the bottom. Let's search backward for mode.", wait=False),
        Wait(0.3),
        Keys("?"),
        Type("mode"),
        Enter(),
        Wait(0.6),

        Say("Question mark mode Enter. Jumped up to the nearest match."),
        Wait(0.3),

        # --- Demo 2: search backward for "port" ---
        Say("Search backward for port.", wait=False),
        Wait(0.3),
        Keys("?"),
        Type("port"),
        Enter(),
        Wait(0.6),

        Say("Found port just above. Question mark always searches upward."),
        Wait(0.3),

        # --- Demo 3: wraps around backward ---
        Say("Search for live. It's below us, but question mark wraps around.", wait=False),
        Wait(0.3),
        Keys("?"),
        Type("live"),
        Enter(),
        Wait(0.6),

        Say("Wrapped around backward through the bottom of the file."),
        Wait(0.3),

        # --- Wrap up ---
        Say("Slash to search forward. Question mark to search backward."),
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
