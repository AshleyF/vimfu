"""Test additional Ctrl-W window commands: W, p, t, b, r, R, x, n, H/J/K/L, <, >, |."""

CASES = {
    # ── Ctrl-W W: Cycle backwards ──

    "ctrlw_W_cycles_backward": {
        "description": "Ctrl-W W moves to previous window (wrap around)",
        "initial": "line one\nline two\nline three\nline four\nline five",
        "keys": ":sp\r\x17W",
    },

    "ctrlw_W_wraps_from_first": {
        "description": "Ctrl-W W wraps from first window to last",
        "initial": "line one\nline two\nline three\nline four\nline five",
        "keys": ":sp\r\x17j\x17W",
    },

    # ── Ctrl-W p: Previous (last accessed) window ──

    "ctrlw_p_goes_to_last_accessed": {
        "description": "Ctrl-W p goes back to the last accessed window",
        "initial": "line one\nline two\nline three\nline four\nline five",
        "keys": ":sp\r\x17j\x17p",
    },

    # ── Ctrl-W t: Move to top window ──

    "ctrlw_t_goes_to_top": {
        "description": "Ctrl-W t moves to the top window",
        "initial": "line one\nline two\nline three\nline four\nline five",
        "keys": ":sp\r\x17j\x17t",
    },

    # ── Ctrl-W b: Move to bottom window ──

    "ctrlw_b_goes_to_bottom": {
        "description": "Ctrl-W b moves to the bottom window",
        "initial": "line one\nline two\nline three\nline four\nline five",
        "keys": ":sp\r\x17b",
    },

    # ── Ctrl-W r: Rotate windows downward ──

    "ctrlw_r_rotates_down": {
        "description": "Ctrl-W r rotates windows downward",
        "initial": "aaa\nbbb\nccc\nddd\neee\nfff",
        "keys": ":sp\rjj\x17r",
    },

    # ── Ctrl-W R: Rotate windows upward ──

    "ctrlw_R_rotates_up": {
        "description": "Ctrl-W R rotates windows upward",
        "initial": "aaa\nbbb\nccc\nddd\neee\nfff",
        "keys": ":sp\rjj\x17R",
    },

    # ── Ctrl-W x: Exchange windows ──

    "ctrlw_x_exchanges": {
        "description": "Ctrl-W x exchanges current window with next",
        "initial": "aaa\nbbb\nccc\nddd\neee\nfff",
        "keys": ":sp\rjj\x17x",
    },

    # ── Ctrl-W n: New window with empty buffer ──

    "ctrlw_n_new_window": {
        "description": "Ctrl-W n opens a new window with an empty buffer",
        "initial": "hello world\nsecond line",
        "keys": "\x17n",
    },
}
