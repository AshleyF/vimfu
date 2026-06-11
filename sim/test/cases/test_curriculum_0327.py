"""Tests for video 0327: [p ]p put with indent adjustment."""

PYFILE = "def outer():\n    x = 10\n    y = 20\n    def inner():\n        a = 1\n        b = 2\n        return a + b\n    return x + y\n"

CASES = {
    "bracket_p_put_with_indent_after": {
        "description": "Yank line 7 (8-space indent), go to line 3, ]p adjusts indent to 4 spaces",
        "keys": "7Gyy3G]p",
        "initial": PYFILE,
    },

    "bracket_p_put_with_indent_before": {
        "description": "Yank line 7 (8-space indent), go to line 3, [p before with indent adjust",
        "keys": "7Gyy3G[p",
        "initial": PYFILE,
    },

    "regular_p_keeps_indent_for_comparison": {
        "description": "Regular p keeps original 8-space indent (no adjustment)",
        "keys": "7Gyy3Gp",
        "initial": PYFILE,
    },

    "bracket_p_when_indents_match": {
        "description": "]p with same source/target indent leaves indent alone",
        "keys": "2Gyy3G]p",
        "initial": PYFILE,
    },
}
