"""Tests for video 0241: Ctrl-J (down) and Ctrl-M (Enter / first non-blank)."""

# \n in keys = Ctrl-J in compare_test_v2 mapping (see harness)
# \r = Enter = Ctrl-M

CASES = {
    "ctrl_j_moves_down": {
        "description": "Ctrl-J moves down one line (same column behavior)",
        "keys": "\n\n\n",
        "initial": "alpha\nbravo\ncharlie\ndelta\n",
    },

    "ctrl_m_first_non_blank": {
        "description": "Ctrl-M (Enter) goes to next line's first non-blank",
        "keys": "gg\r\r\r",
        "initial": "first\n    indented\nthird\n        deep\n",
    },

    "ctrl_m_count": {
        "description": "3 Ctrl-M skips 3 lines down to first non-blank",
        "keys": "gg3\r",
        "initial": "a\n    b\n        c\n    d\n",
    },

    "plus_first_non_blank": {
        "description": "+ goes to next line first non-blank (same as Ctrl-M)",
        "keys": "gg+",
        "initial": "first\n    indented\nthird\n",
    },

    "minus_first_non_blank": {
        "description": "- goes to prev line first non-blank",
        "keys": "G-",
        "initial": "first\n    indented\nthird\n",
    },

    "ctrl_j_keeps_column_logic": {
        "description": "Ctrl-J after $ on long line moves down keeping desired col",
        "keys": "$\n",
        "initial": "loooong line\nshort\n",
    },
}
