"""Tests for :p[rint], :nu[mber], :reg with args, :jumps from 0846-0852."""

LINES_TEN = "line one\nline two\nline three\nline four\nline five\nline six\nline seven\nline eight\nline nine\nline ten"
LINES_FIVE = "alpha\nbeta\ngamma\ndelta\nepsilon"

CASES = {
    # ── 0847 :3p — print line 3 ─────────────────────────────────
    "print_single_line": {
        "description": ":3p prints line 3 of the buffer to the command area",
        "keys": ":3p\r",
        "initial": LINES_TEN,
    },
    "print_range_lines": {
        "description": ":5,8p prints lines 5..8",
        "keys": ":5,8p\r",
        "initial": LINES_TEN,
    },

    # ── 0848 :4nu — print line 4 with line number ───────────────
    "number_single_line": {
        "description": ":4nu prints line 4 prefixed with its line number",
        "keys": ":4nu\r",
        "initial": LINES_TEN,
    },
    "number_range_lines": {
        "description": ":2,5nu prints lines 2-5 with line numbers",
        "keys": ":2,5nu\r",
        "initial": LINES_TEN,
    },

    # ── 0846 :reg a — show specific register ────────────────────
    "reg_specific_a": {
        "description": "after yanking to a, :reg a shows only that register",
        "keys": "\"ayy:reg a\r",
        "initial": LINES_FIVE,
    },
    "reg_specific_multi": {
        "description": ":reg ab shows registers a and b",
        "keys": "\"ayyj\"byy:reg ab\r",
        "initial": LINES_FIVE,
    },
}
