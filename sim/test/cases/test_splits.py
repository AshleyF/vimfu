"""Test window splits: :sp, :vsp, Ctrl-W navigation, :close, :only."""

CASES = {
    # ── :sp creates horizontal split ──

    "split_sp_creates_split": {
        "description": ":sp creates a horizontal split showing same buffer",
        "initial": "line one\nline two\nline three\nline four\nline five",
        "keys": ":sp\r",
    },

    # ── Ctrl-W w cycles windows ──

    "split_ctrl_w_w_cycles": {
        "description": "Ctrl-W w moves to next window after :sp",
        "initial": "line one\nline two\nline three\nline four\nline five",
        "keys": ":sp\r\x17w",
    },

    # ── Ctrl-W j/k moves between windows ──

    "split_ctrl_w_j_moves_down": {
        "description": "Ctrl-W j moves to window below",
        "initial": "line one\nline two\nline three\nline four\nline five",
        "keys": ":sp\r\x17j",
    },

    "split_ctrl_w_k_moves_up": {
        "description": "Ctrl-W k moves to window above from bottom window",
        "initial": "line one\nline two\nline three\nline four\nline five",
        "keys": ":sp\r\x17j\x17k",
    },

    # ── :close closes current window ──

    "split_close_window": {
        "description": ":close closes the current split window",
        "initial": "line one\nline two\nline three\nline four\nline five",
        "keys": ":sp\r:close\r",
    },

    # ── :only closes all other windows ──

    "split_only_window": {
        "description": ":only closes all other windows",
        "initial": "line one\nline two\nline three\nline four\nline five",
        "keys": ":sp\r:only\r",
    },

    # ── Ctrl-W s creates split (same as :sp) ──

    "split_ctrl_w_s": {
        "description": "Ctrl-W s creates a horizontal split",
        "initial": "line one\nline two\nline three\nline four\nline five",
        "keys": "\x17s",
    },

    # ── Cursor moves independently in splits ──

    "split_independent_cursor": {
        "description": "Cursor in each split moves independently",
        "initial": "line one\nline two\nline three\nline four\nline five",
        "keys": ":sp\rjj\x17jj",
    },

    # ── Ctrl-W c closes window ──

    "split_ctrl_w_c_closes": {
        "description": "Ctrl-W c closes current window",
        "initial": "line one\nline two\nline three\nline four\nline five",
        "keys": ":sp\r\x17c",
    },

    # ── Edits in one window reflect in other (shared buffer) ──

    "split_shared_buffer": {
        "description": "Editing in one split shows in both (shared buffer)",
        "initial": "aaa\nbbb\nccc",
        "keys": ":sp\rddj\x17w",
    },
}
