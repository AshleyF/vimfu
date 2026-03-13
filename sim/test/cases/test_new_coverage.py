"""Tests for new coverage areas.

Covers: ga, Ctrl-G, @: (repeat last ex), visual put, :sort,
backspace/space wrapping, Ctrl-[ exits, D with count.
"""

CASES = {
    # ================================================================
    # ga — show ASCII value
    # ================================================================
    "ga_basic": {
        "description": "ga shows ASCII value of char under cursor",
        "keys": "ga",
        "initial": "Hello",
    },
    "ga_space": {
        "description": "ga on a space character",
        "keys": "lllllga",
        "initial": "Hello World",
    },

    # ================================================================
    # Ctrl-G — file info
    # ================================================================
    "ctrl_g_basic": {
        "description": "Ctrl-G shows file info",
        "keys": "\x07",
        "initial": "hello\nworld",
    },
    "ctrl_g_multiline": {
        "description": "Ctrl-G on multiline file after moving down",
        "keys": "jj\x07",
        "initial": "one\ntwo\nthree\nfour\nfive",
    },

    # ================================================================
    # @: — repeat last ex command
    # ================================================================
    "at_colon_repeat_goto": {
        "description": "@: repeats :3 goto after initial :3",
        "keys": ":3\rgg@:",
        "initial": "one\ntwo\nthree\nfour\nfive",
    },
    "at_colon_with_no_ex": {
        "description": "@: with no previous ex command shows E30 error",
        "keys": "@:",
        "initial": "hello",
    },

    # ================================================================
    # Visual put
    # ================================================================
    "v_p_replace_charwise": {
        "description": "visual put replaces selection (charwise)",
        "keys": "yiwwvep",
        "initial": "hello world",
    },
    "v_p_replace_shorter": {
        "description": "visual put with shorter replacement",
        "keys": "yiwflv$p",
        "initial": "ab longword",
    },

    # ================================================================
    # :sort
    # ================================================================
    "v_colon_sort": {
        "description": ":sort in visual range",
        "keys": "Vjj:sort\r",
        "initial": "cherry\napple\nbanana",
    },

    # ================================================================
    # Backspace / Space wrapping in normal mode
    # ================================================================
    "backspace_wrap_normal": {
        "description": "Backspace at col 0 wraps to previous line end",
        "keys": "j\x08",
        "initial": "hello\nworld",
    },
    "backspace_at_start": {
        "description": "Backspace at (0,0) stays put",
        "keys": "\x08",
        "initial": "hello",
    },
    "space_wrap_normal": {
        "description": "Space at end of line wraps to next line",
        "keys": "$ ",
        "initial": "hi\nthere",
    },
    "space_at_end": {
        "description": "Space at end of last line stays put",
        "keys": "$ ",
        "initial": "hello",
    },

    # ================================================================
    # Ctrl-[ exits modes (same as Escape)
    # ================================================================
    "ctrl_bracket_exits_insert": {
        "description": "Ctrl-[ exits insert mode",
        "keys": "iHello\x1b",
    },
    "ctrl_bracket_exits_visual": {
        "description": "Ctrl-[ exits visual mode",
        "keys": "vll\x1b",
        "initial": "hello",
    },

    # ================================================================
    # D with count
    # ================================================================
    "D_count_2": {
        "description": "2D deletes rest of line + next line",
        "keys": "2D",
        "initial": "aaa\nbbb\nccc",
    },
    "D_count_3_mid": {
        "description": "3D from col 1 deletes rest + 2 lines",
        "keys": "l3D",
        "initial": "aaa\nbbb\nccc\nddd\neee",
    },
    "D_count_exceeds": {
        "description": "10D with only 3 lines deletes all from cursor",
        "keys": "10D",
        "initial": "aaa\nbbb\nccc",
    },
}
