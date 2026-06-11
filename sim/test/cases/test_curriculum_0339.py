"""Tests for videos 0334-0339: Ctrl-W window navigation."""

LINES = "alpha\nbravo\ncharlie\ndelta\necho\nfoxtrot\ngolf\nhotel\nindia\njuliet\n"

CASES = {
    # ── 0339 Ctrl-W t — go to top (first) window ───────────
    "ctrl_w_t_top_window": {
        "description": ":sp twice, Ctrl-W t jumps to top window",
        "keys": ":sp\r:sp\r\x17t",
        "initial": LINES,
    },

    # ── 0339 Ctrl-W b — go to bottom (last) window ─────────
    "ctrl_w_b_bottom_window": {
        "description": ":sp twice, Ctrl-W t then Ctrl-W b jumps to bottom",
        "keys": ":sp\r:sp\r\x17t\x17b",
        "initial": LINES,
    },

    # ── 0338 Ctrl-W W — backwards cycle ────────────────────
    "ctrl_w_W_backwards": {
        "description": ":sp twice, Ctrl-W W cycles backwards from window 0",
        "keys": ":sp\r:sp\r\x17W",
        "initial": LINES,
    },

    # ── Ctrl-W r — rotate windows ──────────────────────────
    "ctrl_w_r_rotate": {
        "description": ":sp then Ctrl-W r rotates windows downward",
        "keys": ":sp\r\x17r",
        "initial": LINES,
    },
}
