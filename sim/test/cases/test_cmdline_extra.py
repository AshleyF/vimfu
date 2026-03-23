"""Test command-line Ctrl-B (beginning), Ctrl-E (end) cursor movement."""

CASES = {
    # ── Ctrl-B: Move cursor to beginning of command line ──

    "cmdline_ctrl_b_beginning": {
        "description": "Ctrl-B moves cursor to beginning of command line",
        "initial": "hello world",
        "keys": ":set number\x02\r",
    },

    # ── Ctrl-E: Move cursor to end of command line ──

    "cmdline_ctrl_e_end": {
        "description": "Ctrl-E moves cursor to end of command line",
        "initial": "hello world",
        "keys": ":set number\x02\x05\r",
    },
}
