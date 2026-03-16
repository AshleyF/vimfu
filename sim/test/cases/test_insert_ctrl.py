"""Tests for insert-mode Ctrl-O, Ctrl-T, Ctrl-D, Ctrl-E, Ctrl-Y."""

CASES = {
    # ── Ctrl-O — execute one normal command then return to insert ──
    "ctrl_o_motion": {
        "keys": "iHello \x0fA World\x1b",
        "initial": "\n",
    },
    "ctrl_o_word_forward": {
        "keys": "i\x0fwINSERT\x1b",
        "initial": "hello world\n",
    },
    "ctrl_o_delete_word": {
        "keys": "ea\x0fdwDone\x1b",
        "initial": "good bad end\n",
    },
    "ctrl_o_goto_line": {
        "keys": "i\x0fGBottom\x1b",
        "initial": "first\nsecond\nthird\n",
    },

    # ── Ctrl-T — indent current line in insert mode ──
    "ctrl_t_basic": {
        "keys": "i\x14",
        "initial": "hello\n",
    },
    "ctrl_t_twice": {
        "keys": "i\x14\x14",
        "initial": "hello\n",
    },
    "ctrl_t_with_expandtab": {
        "keys": ":set expandtab\r:set shiftwidth=4\riworld\x14\x1b",
        "initial": "hello\n",
    },

    # ── Ctrl-D — unindent current line in insert mode ──
    "ctrl_d_basic": {
        "keys": "i\x04",
        "initial": "\thello\n",
    },
    "ctrl_d_with_expandtab": {
        "keys": ":set expandtab\r:set shiftwidth=4\ri\x04\x1b",
        "initial": "    hello\n",
    },
    "ctrl_d_no_indent": {
        "keys": "i\x04",
        "initial": "hello\n",
    },

    # ── Ctrl-E — insert character from line below ──
    "ctrl_e_basic": {
        "keys": "A\x05\x1b",
        "initial": "abc\nxyz\n",
    },
    "ctrl_e_multiple": {
        "keys": "A\x05\x05\x05\x1b",
        "initial": "\nworld\n",
    },
    "ctrl_e_no_line_below": {
        "keys": "A\x05\x1b",
        "initial": "hello\n",
    },

    # ── Ctrl-Y — insert character from line above ──
    "ctrl_y_basic": {
        "keys": "jA\x19\x1b",
        "initial": "abcdef\nxy\n",
    },
    "ctrl_y_multiple": {
        "keys": "jI\x19\x19\x19\x1b",
        "initial": "hello\n\n",
    },
    "ctrl_y_no_line_above": {
        "keys": "A\x19\x1b",
        "initial": "hello\n",
    },
}
