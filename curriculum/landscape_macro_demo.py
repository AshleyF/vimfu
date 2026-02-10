"""
Landscape Demo: Recording and Playing Macros in Vim

A longer-form tutorial (1920x1080 landscape) walking through a real-world
refactoring task using Vim macros. We add a logging line to six functions
by recording a macro once and replaying it five times.

Target audience: complete Vim beginners. Every single keystroke is explained.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))

from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile


lesson = Demo(
    title="VimFu — Recording Macros",
    description="Learn how to record a Vim macro to automate repetitive edits. "
                "We add a logging line to six functions by recording once and replaying five times.",
    speed=0.55,
    rows=24,
    cols=80,
    humanize=0.7,
    mistakes=0.0,
    seed=400,
    tts_voice="echo",
    borderless=True,
    playlist="",
    target_width=1920,
    target_height=1080,

    setup=[
        Comment("Set TERM for proper color support in Neovim"),
        Line("export TERM=xterm-256color"),
        Comment("Prepare workspace"),
        Line("mkdir -p ~/vimfu && cd ~/vimfu"),
        Line("rm -f server.py .server.py.swp .server.py.swo"),
        Line("rm -f ~/.local/state/nvim/swap/*server.py*"),
        Comment("Create the demo file — a little API server with functions that need logging"),
        WriteFile("server.py", """
import logging

logger = logging.getLogger(__name__)


def get_users(db):
    users = db.query("SELECT * FROM users")
    return users


def create_user(db, name, email):
    db.execute("INSERT INTO users VALUES (?, ?)", (name, email))
    return {"status": "created"}


def delete_user(db, user_id):
    db.execute("DELETE FROM users WHERE id = ?", (user_id,))
    return {"status": "deleted"}


def update_email(db, user_id, new_email):
    db.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))
    return {"status": "updated"}


def list_orders(db, user_id):
    orders = db.query("SELECT * FROM orders WHERE user_id = ?", (user_id,))
    return orders


def cancel_order(db, order_id):
    db.execute("UPDATE orders SET status = 'cancelled' WHERE id = ?", (order_id,))
    return {"status": "cancelled"}
"""),
        Line("clear"),
        Comment("Launch nvim before recording"),
        Line("nvim server.py"),
        WaitForScreen("get_users", timeout=10.0),
        IfScreen("swap file", "d"),
    ],

    steps=[
        # --- Title card ---
        Overlay("VimFu", caption="Recording Macros", duration=4.0),
        Wait(1.0),

        # ====================================================================
        # PART 1: Introduction
        # ====================================================================
        Say("Today we're learning one of Vim's most powerful features. Macros. "
            "A macro lets you record a sequence of keystrokes and replay them instantly. "
            "They're perfect for repetitive edits.", wait=True),
        Wait(0.5),

        Say("Here's the scenario. We've got a Python file with six API functions. "
            "The boss wants a logging line added at the top of every function. "
            "We could do it by hand six times — or we could be smart about it.", wait=True),
        Wait(0.5),

        # --- Orient the viewer ---
        Say("At the top we've got the logging import, then the first few functions — "
            "get users, create user, delete user, update email.", wait=True),
        Wait(0.3),

        Say("There are two more below the screen. Control F scrolls down one full page.", wait=False),
        Wait(0.3),
        Keys("\x06"),       # Ctrl-F to page down
        Wait(0.8),

        Say("List orders and cancel order. Six functions total, and every one needs a logging line.", wait=True),
        Wait(0.3),

        Say("G G takes us back to the top of the file.", wait=False),
        Wait(0.3),
        Keys("g"),
        Keys("g"),
        Wait(0.5),

        # ====================================================================
        # PART 2: Do the first function by hand (teach basic editing)
        # ====================================================================
        Say("Let me do the first one by hand, so you can see the basic edits. "
            "Then we'll record a macro for the rest.", wait=True),
        Wait(0.5),

        # --- Navigate to first function ---
        Say("I'll use slash to search. Slash puts Vim into search mode. Watch the bottom of the screen.", wait=True),
        Wait(0.3),
        Keys("/"),
        Wait(0.5),

        Say("I type def get, then press Enter to jump there.", wait=False),
        Wait(0.3),
        Type("def get"),
        Wait(0.3),
        Enter(),
        Wait(0.5),

        Say("The cursor jumped right to the def line. Slash search is one of the fastest ways to move around in Vim.", wait=True),
        Wait(0.5),

        # --- Open a line below ---
        Say("Now I need to create a new line under this def line and start typing. "
            "In Vim, lowercase O does exactly that. It opens a new line below and puts you in insert mode.", wait=True),
        Wait(0.3),

        Say("Watch — I press O.", wait=False),
        Wait(0.3),
        Keys("o"),          # open line below
        Wait(0.5),

        Say("See? A new blank line appeared and the cursor is there, ready to type. "
            "We're in insert mode now — anything I type goes directly into the file.", wait=True),
        Wait(0.5),

        # --- Type the logging line ---
        Say("I'll type the logging line. Vim already indented for us, so I just type the call.", wait=False),
        Wait(0.3),
        Type('logger.info("calling get_users")'),
        Wait(0.6),

        Say("Done. Logger dot info, calling get users. That's exactly what we want.", wait=True),
        Wait(0.5),

        # --- Escape back to normal mode ---
        Say("Now I press Escape to leave insert mode and go back to normal mode. "
            "In Vim you're always either in normal mode, where keys are commands, "
            "or insert mode, where keys type text. Escape switches you back to normal.", wait=True),
        Wait(0.3),
        Escape(),
        Wait(0.5),

        Say("First function — done. But we've got five more to go. "
            "Doing this by hand five more times would be tedious. Let's use a macro.", wait=True),
        Wait(0.8),

        # ====================================================================
        # PART 3: Record the macro on the second function
        # ====================================================================
        Say("Here's the idea. I'm going to record every keystroke I make while editing the second function. "
            "Then I can replay those exact keystrokes on functions three, four, five, and six.", wait=True),
        Wait(0.5),

        # --- Navigate to second function ---
        Say("First, let me jump to the second function. Slash, def create.", wait=False),
        Wait(0.3),
        Keys("/"),
        Type("def create"),
        Enter(),
        Wait(0.5),

        Say("Cursor is on the d of def create user. Perfect starting position.", wait=True),
        Wait(0.5),

        # === START RECORDING ===
        Say("To start recording a macro, I press Q followed by a letter. "
            "The letter is the name of the register where the macro will be stored. "
            "I'll use the letter A. So — Q, A.", wait=True),
        Wait(0.5),
        Keys("q"),
        Keys("a", overlay="register a"),
        Wait(0.5),

        Say("Look at the bottom left of the screen. It says recording at A. "
            "From this moment on, every single keystroke is being captured.", wait=True),
        Wait(0.8),

        # --- Step 1: Yank the function name ---
        Say("Now here's the clever part. Instead of typing the function name by hand, "
            "I'm going to copy it from the def line. That way this macro will work on any function, "
            "not just create user.", wait=True),
        Wait(0.5),

        Say("The cursor is on the D of def. I press W — lowercase W — to move forward one word. "
            "That lands the cursor right on the function name.", wait=True),
        Wait(0.3),
        Keys("w"),
        Wait(0.5),

        Say("Now the cursor is on the C of create user. I'll copy this function name. "
            "In Vim, copying is called yanking. I press Y W — yank word.", wait=True),
        Wait(0.3),

        Keys("y"),
        Keys("w"),
        Wait(0.5),

        Say("Notice I didn't have to select anything first. In most editors you'd highlight the text "
            "and then copy. In Vim, Y plus a motion yanks directly — no selection step needed.", wait=True),
        Wait(0.3),

        Say("Create underscore user is now yanked and sitting in a register, ready to paste.", wait=True),
        Wait(0.5),

        # --- Step 2: Open line below ---
        Say("Now O to open a new line below and enter insert mode.", wait=False),
        Wait(0.3),
        Keys("o"),
        Wait(0.4),

        # --- Step 3: Type the logging template ---
        Say("Vim auto-indented for us. I'll type the full logging line, but leave "
            "a gap where the function name goes — then paste it in.", wait=True),
        Wait(0.3),

        Type('logger.info("calling ")'),
        Wait(0.5),

        # --- Step 4: Escape and paste the function name ---
        Say("Escape to go back to normal mode.", wait=False),
        Wait(0.3),
        Escape(),
        Wait(0.4),

        Say("The cursor is on the closing parenthesis. I press H to move left.", wait=False),
        Wait(0.3),
        Keys("h"),
        Wait(0.4),

        Say("Now I'm on the closing quote — right where I want to paste.", wait=True),
        Wait(0.3),

        Say("Now capital P — paste before. This inserts the yanked function name "
            "right before the quote.", wait=True),
        Wait(0.3),
        Keys("P"),
        Wait(0.6),

        Say("Look at that — create underscore user was pasted right into the string. "
            "We yanked it from the def line and pasted it here — and every keystroke "
            "is being recorded into the macro.", wait=True),
        Wait(0.4),

        # --- Step 5: Jump to the next function ---
        Say("One last thing before we stop recording. I'll search for the next def line. "
            "That way the macro includes the navigation — so when we replay it, "
            "the cursor is already in position and we can just replay again immediately.", wait=True),
        Wait(0.3),

        Say("Slash, def, space, Enter.", wait=False),
        Wait(0.3),
        Keys("/"),
        Type("def "),
        Enter(),
        Wait(0.5),

        Say("The cursor is now on delete user — the next function in line.", wait=True),
        Wait(0.3),

        # === STOP RECORDING ===
        Say("And now I press Q to stop recording.", wait=True),
        Wait(0.3),
        Keys("q"),
        Wait(0.5),

        Say("That's it. The macro is saved. It contains: W to jump to the function name, "
            "Y W to yank the word, O to open a new line, type the logging template, "
            "Escape, H, capital P to paste the function name in, "
            "then slash def to jump to the next function. Let's see it in action.", wait=True),
        Wait(0.8),

        # ====================================================================
        # PART 4: Replay the macro
        # ====================================================================
        Say("To replay a macro, I press at sign followed by the register letter. At, A.", wait=True),
        Wait(0.5),
        Keys("@"),
        Keys("a", overlay="register a"),
        Wait(1.2),

        Say("Boom. Delete user got its logging line, and the cursor jumped to update email — "
            "ready for the next replay. All in an instant.", wait=True),
        Wait(0.5),

        # --- Introduce @@ shortcut ---
        Say("Here's a shortcut. Instead of at A, I can press at, at — two at signs. "
            "That replays whatever macro you ran last.", wait=True),
        Wait(0.3),
        Keys("@"),
        Keys("@"),
        Wait(1.2),

        Say("Update email — done. Cursor's on list orders. Two functions left.", wait=True),
        Wait(0.5),

        # --- Introduce count prefix ---
        Say("And here's one more trick. I can put a count in front — "
            "two at at runs the macro twice in a row.", wait=True),
        Wait(0.3),
        Keys("2"),
        Keys("@"),
        Keys("@"),
        Wait(1.5),

        Say("List orders and cancel order — both done. All six functions now have logging.", wait=True),
        Wait(0.8),

        # ====================================================================
        # PART 5: Show the result
        # ====================================================================
        Say("Notice the search wrapped back to the top of the file — there are no more defs below. "
            "So we can already see the first few functions and their new log lines.", wait=True),
        Wait(0.8),

        Say("Get users — has its log line. Create user — yep. Delete user — got it.", wait=True),
        Wait(0.5),

        # Scroll down to see the rest — Ctrl+F for full page forward
        Say("Control F scrolls down one full screen. Let me check the rest.", wait=False),
        Wait(0.3),
        Keys("\x06"),       # Ctrl-F to page down
        Wait(1.0),

        Say("Update email, list orders, cancel order — every single one. Each logging line has "
            "the correct function name because the macro yanked it from the def line.", wait=True),
        Wait(0.8),

        # ====================================================================
        # PART 6: Recap
        # ====================================================================
        Say("Quick recap. Q followed by a letter starts recording into that register. "
            "You do your edit. Q again stops recording. "
            "At sign plus the letter replays it. At at replays the last macro. "
            "And you can put a count in front to replay multiple times.", wait=True),
        Wait(0.5),

        Say("The secret to a good macro is making it generic. We didn't hardcode the function name — "
            "we yanked it. We didn't count lines — we searched for the next def. "
            "That's what made it work on every function automatically.", wait=True),
        Wait(0.5),

        Say("Macros are one of Vim's real superpowers. Once you see a repetitive pattern, "
            "record a macro and let Vim do the heavy lifting. Thanks for watching.", wait=True),
        Wait(2.0),
    ],

    teardown=[
        Comment("Quit nvim without saving"),
        Escape(),
        Type(":q!"),
        Enter(),
        Comment("Clean up"),
        Line("rm -f server.py"),
    ],
)

if __name__ == "__main__":
    lesson.run()
