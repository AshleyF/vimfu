"""
Lesson 037: Change to End of Line

Sub-60-second lesson: Press C to delete from the cursor to the end
of the line and enter insert mode. Same as c$ — change + end-of-line.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Change to End of Line",
    description="Press C to delete from the cursor to the end of the line "
                "and enter insert mode. Same as c$ — change + end-of-line.",
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=178,
    tts_voice="echo",
    borderless=True,
    playlist="VimFu",

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Prepare workspace"),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Line("rm -f urls.py .urls.py.swp .urls.py.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*urls.py*"),
        Comment("Create a file with values to replace"),
        WriteFile("urls.py", """
            host = "http://old-server"
            port = "9999"
            path = "/api/v1/old"
        """),
        Line("clear"),
        Comment("Launch nvim before recording"),
        Line("nvim urls.py"),
        WaitForScreen("host", timeout=10.0),
        IfScreen("swap file", "d"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Change to End of Line", duration=3.0),
        Wait(0.7),

        # --- Intro ---
        Say("Capital C deletes to the end and puts you in insert mode.", wait=True),
        Wait(0.3),

        # --- Change host value ---
        Say("Let's replace this whole URL.", wait=False),
        Wait(0.3),
        Keys("f"),
        Keys("h"),       # fh — find 'h' in "http..."
        Wait(0.3),
        Keys("C"),       # C — delete to end, enter insert
        Wait(0.3),
        Type("https://new-server\""),
        Wait(0.3),
        Escape(),
        Wait(0.5),

        Say("Everything after the cursor was replaced."),
        Wait(0.3),

        # --- Change port value ---
        Say("Change the port too.", wait=False),
        Wait(0.3),
        Keys("j"),       # down to line 2: port = "9999"
        Keys("0"),
        Keys("f"),
        Keys("9"),       # f9 — find '9' in "9999"
        Wait(0.3),
        Keys("C"),       # C — delete to end, enter insert
        Wait(0.3),
        Type("8080\""),
        Wait(0.3),
        Escape(),
        Wait(0.5),

        Say("C is D plus insert mode. Delete to end, then type."),
        Wait(0.3),

        # --- Change path value ---
        Say("One more.", wait=False),
        Wait(0.3),
        Keys("j"),       # down to line 3: path = "/api/v1/old"
        Keys("0"),
        Keys("f"),
        Keys("/"),       # f/ — find first '/'
        Wait(0.3),
        Keys("C"),       # C — delete to end, enter insert
        Wait(0.3),
        Type("/api/v2/new\""),
        Wait(0.3),
        Escape(),
        Wait(0.5),

        # --- Wrap up ---
        Say("Capital C. Change to the end of the line."),
        Wait(1.5),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f urls.py"),
    ],
)


if __name__ == "__main__":
    lesson.run()
