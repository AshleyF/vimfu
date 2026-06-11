"""Tests for video range 0860-0866: :global / :v inverse and subcommands."""

LINES_WITH_TODO = "first line\nTODO: fix this\nthird line\nTODO: refactor\nfifth line"
LINES_WITH_BLANK = "alpha\n\nbeta\n\ngamma\n\ndelta"
LINES_IMPORTS = "def main():\n    pass\n\nimport os\nimport sys\nfrom typing import List\n\nclass C:\n    pass"
LINES_TODOS_TRIM = "  TODO: a\nplain\n  TODO: b\nanother\n  TODO: c"
LINES_KEEP_DROP = "keep one\ndrop one\nkeep two\ndrop two\nkeep three"
LOG_LINES = "INFO: ok\nERROR: bad\nINFO: ok\nERROR: worse\nINFO: done"

CASES = {
    # ── 0860 :g/TODO/d ───────────────────────────────────────────
    "global_delete_todo": {
        "description": ":g/TODO/d deletes every line matching TODO",
        "keys": ":g/TODO/d\r",
        "initial": LINES_WITH_TODO,
    },

    # ── 0861 :g/^$/d ─────────────────────────────────────────────
    "global_delete_blank_lines": {
        "description": ":g/^$/d removes all empty lines",
        "keys": ":g/^$/d\r",
        "initial": LINES_WITH_BLANK,
    },

    # ── 0862 :g/^import/m 0 ──────────────────────────────────────
    "global_move_imports_to_top": {
        "description": ":g/^import/m 0 moves every import line to the top of file",
        "keys": ":g/^import/m 0\r",
        "initial": LINES_IMPORTS,
    },

    # ── 0863 :g/TODO/norm 0x ─────────────────────────────────────
    "global_norm_strip_first_char": {
        "description": ":g/TODO/norm 0x strips the first char of each TODO line",
        "keys": ":g/TODO/norm 0x\r",
        "initial": LINES_TODOS_TRIM,
    },

    # ── 0864 :g/class/+1s/old/new/g  — substitute on line after match
    "global_substitute_offset": {
        "description": ":g/foo/s/a/A/g — substitute on every matching line",
        "keys": ":g/keep/s/keep/KEEP/g\r",
        "initial": LINES_KEEP_DROP,
    },

    # ── 0865 :v/keep/d  — inverse: delete lines NOT matching ─────
    "inverse_global_delete_non_keep": {
        "description": ":v/keep/d removes any line that doesn't have 'keep'",
        "keys": ":v/keep/d\r",
        "initial": LINES_KEEP_DROP,
    },

    # ── 0866 :v/ERROR/d  — keep only ERROR lines ─────────────────
    "inverse_global_keep_errors": {
        "description": ":v/ERROR/d keeps just the lines containing 'ERROR'",
        "keys": ":v/ERROR/d\r",
        "initial": LOG_LINES,
    },
}
