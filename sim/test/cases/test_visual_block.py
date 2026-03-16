"""Visual block mode (Ctrl-V)"""

CASES = {
    # ── Basic selection and delete ──
    "block_delete_square": {
        "keys": "\x16jld",
        "initial": "abcdef\nghijkl\nmnopqr\n",
    },
    "block_delete_dollar": {
        "keys": "\x16j$d",
        "initial": "abcdef\nghijkl\nmnopqr\n",
    },

    # ── Block insert (I) ──
    "block_insert_prefix": {
        "keys": "\x16jjI#\x1b",
        "initial": "line one\nline two\nline three\n",
    },
    "block_insert_multiple_chars": {
        "keys": "\x16jjI// \x1b",
        "initial": "line one\nline two\nline three\n",
    },

    # ── Block append (A) ──
    "block_append": {
        "keys": "\x16jj$A;\x1b",
        "initial": "line one\nline two\nline three\n",
    },

    # ── Block change (c) ──
    "block_change": {
        "keys": "\x16jllcXY\x1b",
        "initial": "abcdef\nghijkl\nmnopqr\n",
    },

    # ── Block yank and put ──
    "block_yank_put": {
        "keys": "\x16jly$p",
        "initial": "abcdef\nghijkl\nmnopqr\n",
    },

    # ── Block replace (r) ──
    "block_replace": {
        "keys": "\x16jllrX",
        "initial": "abcdef\nghijkl\nmnopqr\n",
    },

    # ── Block shift ──
    "block_shift_right": {
        "keys": "\x16jj>",
        "initial": "aaa\nbbb\nccc\n",
    },

    # ── Switching between visual modes ──
    "switch_to_block_from_visual": {
        "keys": "vjj\x16",
        "initial": "abc\ndef\nghi\n",
    },
    "switch_to_visual_from_block": {
        "keys": "\x16jjv",
        "initial": "abc\ndef\nghi\n",
    },

    # ── Block with movement ──
    "block_select_with_w": {
        "keys": "\x16jwd",
        "initial": "hello world\nhello world\nhello world\n",
    },

    # ── Count with block ──
    "block_delete_3j": {
        "keys": "\x163jld",
        "initial": "abcd\nefgh\nijkl\nmnop\nqrst\n",
    },
}
