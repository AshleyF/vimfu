"""Normal mode Ctrl-key synonyms and misc small features"""

CASES = {
    # Ctrl-H = h (move left)
    "ctrl_h_left": {
        "keys": "l\x08",
        "initial": "hello\n",
    },
    # Ctrl-N = j (move down)
    "ctrl_n_down": {
        "keys": "\x0e",
        "initial": "line1\nline2\n",
    },
    # Ctrl-P = k (move up)
    "ctrl_p_up": {
        "keys": "j\x10",
        "initial": "line1\nline2\n",
    },
    # Ctrl-J = j (move down)
    "ctrl_j_down": {
        "keys": "\x0a",
        "initial": "line1\nline2\n",
    },
    # Ctrl-M = Enter (next line first non-blank)
    "ctrl_m_next_line": {
        "keys": "\r",
        "initial": "  hello\n  world\n",
    },
    # Ctrl-L clears command line
    "ctrl_l_clears": {
        "keys": ":set number\r\x0c",
        "initial": "test\n",
    },
    # Ctrl-C cancels pending operator
    "ctrl_c_cancels": {
        "keys": "d\x03",
        "initial": "hello\nworld\n",
    },
    # Ctrl-C in insert mode (leave insert)
    "ctrl_c_insert": {
        "keys": "ihello\x03",
        "initial": "world\n",
    },
    # go (byte offset)
    "go_byte_offset": {
        "keys": "8go",
        "initial": "hello\nworld\n",
    },
}
