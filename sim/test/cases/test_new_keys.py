"""Tests for newly implemented keys.

Covers: Delete (normal), Q (replay macro), Ctrl-W/Ctrl-U (insert),
insert mode Delete/arrows, Ctrl-A/Ctrl-X, () sentence motions, gd.

Note: Ctrl-H/Ctrl-J are the same byte sequences as Backspace/Enter in
terminals, so they're tested implicitly by existing tests. Ctrl-G and ga
produce environment-specific command-line output, so they're tested via
unit tests rather than ground truth comparison.
"""

CASES = {
    # ================================================================
    # Delete key in normal mode (alias for x)
    # ================================================================
    "delete_key_normal_basic": {
        "description": "Delete key deletes char under cursor like x",
        "keys": "\x1b[3~",
        "initial": "abcde",
    },
    "delete_key_normal_end_of_line": {
        "description": "Delete key at end of line",
        "keys": "$\x1b[3~",
        "initial": "abcde",
    },

    # ================================================================
    # Q - replay last macro
    # ================================================================
    "Q_replay_last_macro": {
        "description": "Q replays last recorded macro",
        "keys": "qaiX\x1bqjQ",
        "initial": "aaa\nbbb\nccc",
    },
    "Q_with_count": {
        "description": "3Q replays macro 3 times",
        "keys": "qax\x1bqj3Q",
        "initial": "aaa\nbbbbbbb\nccc",
    },
    "Q_no_macro_recorded": {
        "description": "Q with no macro recorded (nvim enters ex-mode, we no-op)",
        "keys": "Q",
        "initial": "hello",
        "skip": "nvim enters ex-mode which we don't implement",
    },

    # ================================================================
    # Insert mode Ctrl-W (delete word backward)
    # ================================================================
    "insert_ctrl_w_basic": {
        "description": "Ctrl-W deletes word backward in insert",
        "keys": "A\x17\x1b",
        "initial": "hello world",
    },
    "insert_ctrl_w_multiple_words": {
        "description": "Two Ctrl-W deletes two words",
        "keys": "A\x17\x17\x1b",
        "initial": "one two three",
    },
    "insert_ctrl_w_at_start": {
        "description": "Ctrl-W at start of line joins with previous",
        "keys": "jI\x17\x1b",
        "initial": "hello\nworld",
    },
    "insert_ctrl_w_with_spaces": {
        "description": "Ctrl-W skips trailing spaces then deletes word",
        "keys": "A\x17\x1b",
        "initial": "hello   ",
    },
    "insert_ctrl_w_single_word": {
        "description": "Ctrl-W on single word deletes it",
        "keys": "A\x17\x1b",
        "initial": "hello",
    },

    # ================================================================
    # Insert mode Ctrl-U (delete to start of line)
    # ================================================================
    "insert_ctrl_u_basic": {
        "description": "Ctrl-U deletes to start of line in insert",
        "keys": "A\x15\x1b",
        "initial": "hello world",
    },
    "insert_ctrl_u_mid_line": {
        "description": "Ctrl-U from middle of line",
        "keys": "llli\x15\x1b",
        "initial": "abcde",
    },
    "insert_ctrl_u_at_start": {
        "description": "Ctrl-U at start of line joins with previous",
        "keys": "jI\x15\x1b",
        "initial": "hello\nworld",
    },

    # ================================================================
    # Insert mode Delete key (forward delete)
    # ================================================================
    "insert_delete_basic": {
        "description": "Delete key in insert mode forward-deletes",
        "keys": "i\x1b[3~\x1b",
        "initial": "abcde",
    },
    "insert_delete_at_end": {
        "description": "Delete key at end of line joins with next",
        "keys": "A\x1b[3~\x1b",
        "initial": "abc\ndef",
    },

    # ================================================================
    # Insert mode arrow keys
    # ================================================================
    "insert_arrow_left": {
        "description": "Left arrow moves cursor in insert mode",
        "keys": "A\x1b[D\x1b[Dx\x1b",
        "initial": "abcde",
    },
    "insert_arrow_right": {
        "description": "Right arrow moves cursor in insert mode",
        "keys": "i\x1b[C\x1b[Cx\x1b",
        "initial": "abcde",
    },
    "insert_arrow_up": {
        "description": "Up arrow moves cursor up in insert mode",
        "keys": "jA\x1b[Ax\x1b",
        "initial": "abcdef\nghijkl",
    },
    "insert_arrow_down": {
        "description": "Down arrow moves cursor down in insert mode",
        "keys": "A\x1b[Bx\x1b",
        "initial": "abcdef\nghijkl",
    },

    # ================================================================
    # Ctrl-A / Ctrl-X (increment / decrement)
    # ================================================================
    "ctrl_a_basic": {
        "description": "Ctrl-A increments number at cursor",
        "keys": "w\x01",
        "initial": "val 42 end",
    },
    "ctrl_a_with_count": {
        "description": "5 Ctrl-A increments by 5",
        "keys": "w5\x01",
        "initial": "val 10 end",
    },
    "ctrl_x_basic": {
        "description": "Ctrl-X decrements number",
        "keys": "w\x18",
        "initial": "val 10 end",
    },
    "ctrl_x_to_negative": {
        "description": "Ctrl-X decrements past zero to negative",
        "keys": "w\x18",
        "initial": "val 0 end",
    },
    "ctrl_a_negative": {
        "description": "Ctrl-A increments negative number",
        "keys": "w\x01",
        "initial": "val -5 end",
    },
    "ctrl_a_cursor_before_number": {
        "description": "Ctrl-A finds next number on line",
        "keys": "\x01",
        "initial": "abc 99",
    },
    "ctrl_a_dot_repeat": {
        "description": "Ctrl-A then . repeats increment",
        "keys": "w\x01.",
        "initial": "val 10 end",
    },
    "ctrl_x_dot_repeat": {
        "description": "Ctrl-X then . repeats decrement",
        "keys": "w\x18.",
        "initial": "val 10 end",
    },
    "ctrl_a_on_zero": {
        "description": "Ctrl-A on 0 becomes 1",
        "keys": "\x01",
        "initial": "0",
    },
    "ctrl_a_multidigit": {
        "description": "Ctrl-A on multi-digit number",
        "keys": "\x01",
        "initial": "999",
    },

    # ================================================================
    # () sentence motions
    # ================================================================
    "paren_right_basic": {
        "description": ") moves to next sentence",
        "keys": ")",
        "initial": "Hello world.  Next sentence here.",
    },
    "paren_right_across_lines": {
        "description": ") moves to next sentence across lines",
        "keys": ")",
        "initial": "First sentence.\nSecond sentence.",
    },
    "paren_left_basic": {
        "description": "( from end goes to sentence start",
        "keys": "$(",
        "initial": "Hello world.  Next sentence here.",
    },
    "paren_left_to_start": {
        "description": "( at first sentence goes to start of buffer",
        "keys": "(",
        "initial": "Hello world.  Next sentence here.",
    },
    "paren_right_with_count": {
        "description": "2) skips two sentences",
        "keys": "2)",
        "initial": "First.  Second.  Third.",
    },
    "paren_right_blank_line": {
        "description": ") treats blank line as sentence boundary",
        "keys": ")",
        "initial": "First paragraph.\n\nSecond paragraph.",
    },
    "paren_left_blank_line": {
        "description": "( treats blank line as sentence boundary",
        "keys": "G(",
        "initial": "First paragraph.\n\nSecond paragraph.",
    },
    "d_paren_right": {
        "description": "d) deletes to next sentence",
        "keys": "d)",
        "initial": "Hello world.  Next sentence here.",
    },

    # ================================================================
    # gd (go to local declaration)
    # ================================================================
    "gd_basic": {
        "description": "gd jumps to first occurrence of word under cursor",
        "keys": "jjwgd",
        "initial": "x = 10\ny = 20\nz = x + y",
    },
    "gd_already_at_first": {
        "description": "gd on first occurrence stays",
        "keys": "gd",
        "initial": "foo = 1\nbar = foo",
    },
    "gd_different_word": {
        "description": "gd on different word",
        "keys": "j$gd",
        "initial": "hello world\nfoo hello",
    },
}
