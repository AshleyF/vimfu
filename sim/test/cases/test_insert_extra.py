"""Extra insert mode: Ctrl-A (re-insert last), Ctrl-K (digraph - skip), completion (skip)"""

CASES = {
    # ── Insert Ctrl-A — re-insert previously inserted text ──
    "insert_ctrl_a_reinsert": {
        "keys": "ihello \x1ba\x01\x1b",
        "initial": "world\n",
    },
    # Insert Ctrl-A with multiline previous insert
    "insert_ctrl_a_multiline": {
        "keys": "iline1\rline2\x1ba\x01\x1b",
        "initial": "start\n",
    },
    # Insert Ctrl-A at end of file
    "insert_ctrl_a_at_eof": {
        "keys": "ihello\x1bGo\x01\x1b",
        "initial": "test\n",
    },
    # Insert Ctrl-A with no previous insert (should be no-op or empty)
    "insert_ctrl_a_no_prior": {
        "keys": "i\x01\x1b",
        "initial": "test\n",
    },
}
