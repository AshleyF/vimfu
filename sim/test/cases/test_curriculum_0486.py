"""Tests for video range 0486-0488: %, #, and = registers."""

CASES = {
    # ── 0486 % register: Ctrl-R % inserts current filename ────
    "percent_register_ctrl_r": {
        "description": "A space Ctrl-R % inserts current filename at end of line",
        "keys": "A \x12%\x1b",
        "initial": "hello world\n",
    },

    # ── Same but with multiple lines ──────────────────────────
    "percent_register_at_line_end_multiline": {
        "description": "j A Ctrl-R % inserts filename at end of line 2",
        "keys": "jA \x12%\x1b",
        "initial": "first line\nsecond line\nthird line\n",
    },

    # ── 0486 alternate: in middle of line via i ───────────────
    "percent_register_insert_at_start": {
        "description": "I Ctrl-R % space Esc inserts filename at start",
        "keys": "I\x12% \x1b",
        "initial": "data here\n",
    },
}
