"""Tests for video range 0820-0839: file I/O, registers w/ args, :pu, sort iu."""

LINES_NUMBERED = "line 1\nline 2\nline 3\nline 4\nline 5\nline 6\nline 7\nline 8"
LINES_FIVE = "alpha\nbeta\ngamma\ndelta\nepsilon"
LINES_SORT_MIXED = "Banana\napple\nCHERRY\nbanana\nApple"
LINES_JOIN = "first\nsecond\nthird\nfourth"

CASES = {
    # ── 0825 :3d a — delete line 3 into register a ──────────────
    "ex_delete_to_register": {
        "description": ":3d a deletes line 3 and stores it in register a",
        "keys": ":3d a\r:reg a\r",
        "initial": LINES_NUMBERED,
    },

    # ── 0826 :2,4y — yank range to unnamed register ─────────────
    "ex_yank_range": {
        "description": ":2,4y yanks lines 2-4 into the unnamed register",
        "keys": ":2,4y\r:reg \"\r",
        "initial": LINES_NUMBERED,
    },

    # ── 0827 :2,3y a — yank range to register a ─────────────────
    "ex_yank_range_to_register": {
        "description": ":2,3y a yanks lines 2-3 into register a",
        "keys": ":2,3y a\r:reg a\r",
        "initial": LINES_NUMBERED,
    },

    # ── 0832 :pu a — put register a after current line ───────────
    "ex_put_register_after": {
        "description": "yank to a, jump to line 3, :pu a inserts after line 3",
        "keys": "\"ayyG:3\r:pu a\r",
        "initial": LINES_FIVE,
    },
    "ex_put_register_before": {
        "description": ":pu! a inserts register a before the current line",
        "keys": "\"ayyG:3\r:pu! a\r",
        "initial": LINES_FIVE,
    },

    # ── 0830 :t$ — copy current line to end ─────────────────────
    "ex_copy_to_end_t_dollar": {
        "description": ":t$ duplicates current line at the end of the file",
        "keys": "2G:t$\r",
        "initial": LINES_FIVE,
    },

    # ── 0831 :2,3j  /  :2,3j!  — join with/without space ────────
    "ex_join_range": {
        "description": ":2,3j joins lines 2-3 with a single space between",
        "keys": ":2,3j\r",
        "initial": LINES_JOIN,
    },
    "ex_join_range_bang": {
        "description": ":2,3j! joins lines 2-3 without inserting any space",
        "keys": ":2,3j!\r",
        "initial": LINES_JOIN,
    },

    # ── 0834 :%sort! — reverse sort ─────────────────────────────
    "sort_reverse": {
        "description": ":%sort! produces descending order",
        "keys": ":%sort!\r",
        "initial": LINES_FIVE,
    },

    # ── 0835 :%sort iu — case-insensitive unique ────────────────
    "sort_iu_case_insensitive_unique": {
        "description": ":%sort iu deduplicates case-insensitively (per stored memory)",
        "keys": ":%sort iu\r",
        "initial": LINES_SORT_MIXED,
    },

    # ── 0820 :e! — revert to saved on disk ──────────────────────
    # (skipped — requires actual file on disk; ground truth runs with
    # /tmp file but sim can't read disk in the same way)

    # ── 0838 :s/foo/bar/gi — ignore case substitute ─────────────
    "substitute_ignore_case_flag": {
        "description": ":s/foo/bar/gi substitutes regardless of case",
        "keys": ":s/foo/bar/gi\r",
        "initial": "Foo foo FOO fOo other\n",
    },
}
