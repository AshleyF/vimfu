"""Tests for video range 0840-0859: print and info-display commands.

Separate from test_curriculum_0840 because these commands write only to
the command line (no buffer mutation), and the existing suite focuses on
buffer changes.
"""

LINES_TEN = "line one\nline two\nline three\nline four\nline five\nline six\nline seven\nline eight\nline nine\nline ten"

CASES = {
    # ── 0849 := — print buffer line count ───────────────────────
    "equals_buffer_linecount": {
        "description": ":= shows the number of lines in the buffer",
        "keys": ":=\r",
        "initial": LINES_TEN,
    },

    # ── 0850 :.= — current line, :$= — last line ─────────────────
    "dot_equals_current_line": {
        "description": ":.= shows the current line number",
        "keys": "4G:.=\r",
        "initial": LINES_TEN,
    },
    "dollar_equals_last_line": {
        "description": ":$= shows the last (final) line number",
        "keys": ":$=\r",
        "initial": LINES_TEN,
    },
}
