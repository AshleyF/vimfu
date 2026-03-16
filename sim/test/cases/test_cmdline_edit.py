"""Tests for command-line editing: Ctrl-U, Ctrl-W, Up/Down history."""

CASES = {
    # ── Ctrl-U — clear command line then type new command ──
    "cmdline_ctrl_u_retype": {
        "keys": ":set number\x152\r",
        "initial": "line one\nline two\nline three\n",
    },

    # ── Ctrl-W — delete word backward on command line ──
    "cmdline_ctrl_w_then_enter": {
        "keys": ":%s/foo/bar/g\x17\x17baz/g\r",
        "initial": "foo test foo\n",
    },

    # ── Up/Down history ──
    "cmdline_history_up": {
        "keys": ":2\r:\x1b[A\r",
        "initial": "line one\nline two\nline three\n",
    },
    "cmdline_history_two": {
        "keys": ":3\r:1\r:\x1b[A\x1b[A\r",
        "initial": "line one\nline two\nline three\n",
    },
}
