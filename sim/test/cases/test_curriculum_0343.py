"""Tests for videos 0343, 0344, 0346, 0347: Ctrl-W o, HJKL, x, T."""

LINES = "alpha\nbravo\ncharlie\ndelta\necho\nfoxtrot\ngolf\nhotel\nindia\njuliet\n"

CASES = {
    # ── 0343 Ctrl-W o — close all other windows ────────────
    "ctrl_w_o_only_keeps_active": {
        "description": ":sp twice, Ctrl-W o keeps only the active window",
        "keys": ":sp\r:sp\r\x17o",
        "initial": LINES,
    },

    "ctrl_w_o_from_top_window": {
        "description": ":sp twice, Ctrl-W t then Ctrl-W o keeps only the top window",
        "keys": ":sp\r:sp\r\x17t\x17o",
        "initial": LINES,
    },

    # ── 0347 Ctrl-W T — move current window to a new tab ──
    "ctrl_w_T_window_to_new_tab": {
        "description": ":sp then Ctrl-W T moves the bottom window into a new tab",
        "keys": ":sp\r\x17T",
        "initial": LINES,
    },

    "ctrl_w_T_from_top": {
        "description": ":sp, Ctrl-W t, then Ctrl-W T moves the top window into a new tab",
        "keys": ":sp\r\x17t\x17T",
        "initial": LINES,
    },

    # ── 0346 Ctrl-W x — exchange current window with next ─
    "ctrl_w_x_exchange": {
        "description": ":sp then Ctrl-W x exchanges the two windows",
        "keys": ":sp\r\x17x",
        "initial": LINES,
    },
}

