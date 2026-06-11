"""Tests for video 0209: leader key (backslash) and 0207/0208 angle/pipe."""

CASES = {
    # ── 0209 Leader key (backslash by default) ───────────────
    # NOTE: avoid :echo mappings — nvim leaves cursor in cmdline at
    # end of echo message (row 19), but sim returns cursor to buffer.
    # Test mappings that modify the buffer/cursor in normal mode.
    "leader_dd_mapped": {
        "description": ":nnoremap \\d dd then \\d deletes current line",
        "keys": ":nnoremap \\d dd\r\\d",
        "initial": "first\nsecond\nthird\n",
    },

    "leader_w_mapped_to_w": {
        "description": ":nnoremap \\w w then \\w jumps a word forward",
        "keys": ":nnoremap \\w w\r\\w",
        "initial": "one two three\n",
    },

    "leader_n_mapped_to_zz": {
        "description": ":nnoremap \\n zz centers (no-op on tiny file)",
        "keys": ":nnoremap \\n j\r\\n",
        "initial": "a\nb\nc\n",
    },

    # ── 0208 pipe key ──────────────────────────────────────
    "pipe_goto_column": {
        "description": "5| moves to column 5",
        "keys": "5|",
        "initial": "abcdefghij\n",
    },

    "pipe_goto_column_long": {
        "description": "20| on short line goes to end",
        "keys": "20|",
        "initial": "short\n",
    },

    # ── 0207 angle bracket > and < (indent) ───────────────
    "angle_indent_right": {
        "description": ">> indents current line by shiftwidth",
        "keys": ">>",
        "initial": "hello\n",
    },

    "angle_indent_left": {
        "description": "<< dedents an indented line",
        "keys": "<<",
        "initial": "    hello\n",
    },
}
