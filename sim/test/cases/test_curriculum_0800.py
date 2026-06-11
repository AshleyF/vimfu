"""Tests for video range 0800-0819: ranges, line addresses, offsets."""

LINES_TEN = "line one\nline two\nline three\nline four\nline five\nline six\nline seven\nline eight\nline nine\nline ten"
LINES_FIVE = "alpha\nbeta\ngamma\ndelta\nepsilon"

CASES = {
    # ── 0804 :5 — jump to line 5 ────────────────────────────────
    "jump_to_line_5": {
        "description": ":5 moves cursor to line 5",
        "keys": ":5\r",
        "initial": LINES_TEN,
    },
    "jump_to_last_dollar": {
        "description": ":$ moves cursor to the last line",
        "keys": ":$\r",
        "initial": LINES_TEN,
    },

    # ── 0805 :.d — delete current line ──────────────────────────
    "delete_current_line": {
        "description": ":5 then :.d deletes line 5",
        "keys": ":5\r:.d\r",
        "initial": LINES_TEN,
    },
    "delete_current_plus_3": {
        "description": ":3 then :.,.+3d deletes the next 4 lines (3..6)",
        "keys": ":3\r:.,.+3d\r",
        "initial": LINES_TEN,
    },

    # ── 0806 :10,$d — delete from line 10 to end ────────────────
    "delete_from_n_to_dollar": {
        "description": ":5,$d deletes lines 5 through end",
        "keys": ":5,$d\r",
        "initial": LINES_TEN,
    },

    # ── 0807 :3,7d — explicit range delete ──────────────────────
    "delete_range_3_to_7": {
        "description": ":3,7d deletes lines 3..7",
        "keys": ":3,7d\r",
        "initial": LINES_TEN,
    },

    # ── 0808 :%d — wipe entire file ─────────────────────────────
    "delete_entire_file_percent": {
        "description": ":%d removes every line, leaving one empty line",
        "keys": ":%d\r",
        "initial": LINES_TEN,
    },

    # ── 0810 :'a,'bd — mark-based range delete ──────────────────
    "delete_mark_range": {
        "description": "set 'a on line 3 and 'b on line 7, then :'a,'bd",
        "keys": ":3\rma:7\rmb:'a,'bd\r",
        "initial": LINES_TEN,
    },

    # ── 0811 :.+2 — line-relative jump ──────────────────────────
    "jump_dot_plus_2": {
        "description": ":3 then :.+2 puts cursor on line 5",
        "keys": ":3\r:.+2\r",
        "initial": LINES_TEN,
    },

    # ── 0812 :'a,$d  /  :1,.d — combined range forms ────────────
    "delete_mark_to_dollar": {
        "description": "set 'a on line 4, then :'a,$d deletes 4..end",
        "keys": ":4\rma:'a,$d\r",
        "initial": LINES_TEN,
    },
    "delete_1_to_dot": {
        "description": ":5 then :1,.d deletes lines 1..5",
        "keys": ":5\r:1,.d\r",
        "initial": LINES_TEN,
    },

    # ── 0802 :delete (long form) ────────────────────────────────
    "delete_long_form": {
        "description": ":delete with no range deletes the current line",
        "keys": "3G:delete\r",
        "initial": LINES_FIVE,
    },
}
