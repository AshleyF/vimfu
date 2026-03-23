"""Test insert mode Ctrl-V (literal char) and Ctrl-G u (break undo sequence)."""

CASES = {
    # ── Ctrl-V: Insert literal character ──

    "insert_ctrl_v_escape": {
        "description": "Ctrl-V Escape inserts literal ^[ (Escape character)",
        "initial": "hello",
        "keys": "A\x16\x1b\x1b",
    },

    "insert_ctrl_v_ctrl_a": {
        "description": "Ctrl-V Ctrl-A inserts literal ^A",
        "initial": "hello",
        "keys": "A\x16\x01\x1b",
    },

    # ── Ctrl-G u: Break undo sequence ──

    "insert_ctrl_g_u_break_undo": {
        "description": "Ctrl-G u breaks undo so subsequent typing is a separate undo step",
        "initial": "hello",
        "keys": "Afoo\x07ubar\x1buu",
    },
}
