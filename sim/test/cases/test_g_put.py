"""Tests for gp and gP (put and leave cursor after pasted text)."""

CASES = {
    # ── gp — put after, cursor after pasted text ──
    "gp_char_single_line": {
        "keys": "yiwwgp",
        "initial": "hello world\n",
    },
    "gp_char_end_of_line": {
        "keys": "yiw$gp",
        "initial": "hello world\n",
    },
    "gp_line_paste": {
        "keys": "yyGgp",
        "initial": "first\nsecond\nthird\n",
    },
    "gp_line_paste_count": {
        "keys": "yy2gp",
        "initial": "alpha\nbeta\n",
    },

    # ── gP — put before, cursor after pasted text ──
    "gP_char_single_line": {
        "keys": "yiwwgP",
        "initial": "hello world\n",
    },
    "gP_line_paste": {
        "keys": "yyGgP",
        "initial": "first\nsecond\nthird\n",
    },
    "gP_line_paste_count": {
        "keys": "yy2gP",
        "initial": "alpha\nbeta\n",
    },
}
