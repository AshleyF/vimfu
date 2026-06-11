"""Tests for video range 0840-0859: substitute variants, ex modify cmds, :norm."""

LINES_XY = "x x x\nx y\ny y y\nx x y y\nx\ny"
LINES_INDENT = "alpha\nbeta\ngamma\ndelta\nepsilon"
LINES_LIST = "item 1\nitem 2\nitem 3\nitem 4"
LINES_ABCDE = "alpha\nbeta\ngamma\ndelta\nepsilon\nfoo\nbar\nbaz"

CASES = {
    # ── 0843 :3,6s/x/y/g — substitute with explicit line range ──
    "substitute_range": {
        "description": ":3,6s/x/y/g substitutes only within lines 3-6",
        "keys": ":3,6s/x/y/g\r",
        "initial": LINES_XY,
    },
    "substitute_range_dot_dollar": {
        "description": ":.,$s/x/Y/g substitutes from current line to end",
        "keys": "2G:.,$s/x/Y/g\r",
        "initial": LINES_XY,
    },

    # ── 0844 :noh — clear search highlight ──────────────────────
    "noh_clears_highlight": {
        "description": "/foo then :noh — hlsearch is off",
        "keys": "/x\r:noh\r",
        "initial": LINES_XY,
    },
    "nohlsearch_long_form": {
        "description": ":nohlsearch (full word) also clears highlight",
        "keys": "/y\r:nohlsearch\r",
        "initial": LINES_XY,
    },

    # ── 0853 :2> — indent single line via ex ────────────────────
    "ex_indent_single": {
        "description": ":2> indents line 2 by one shiftwidth",
        "keys": ":2>\r",
        "initial": LINES_INDENT,
    },
    "ex_indent_range": {
        "description": ":3,4> indents lines 3-4",
        "keys": ":3,4>\r",
        "initial": LINES_INDENT,
    },

    # ── 0854 :2,4< — dedent single line via ex ──────────────────
    "ex_dedent_range": {
        "description": ":2,4< dedents lines 2-4",
        "keys": ":%>\r:2,4<\r",
        "initial": LINES_INDENT,
    },

    # ── 0856 :3,5>> / :3<<< — multi-level shifts ────────────────
    "ex_indent_double": {
        "description": ":3,5>> indents lines 3-5 by 2 shiftwidths",
        "keys": ":3,5>>\r",
        "initial": LINES_INDENT,
    },
    "ex_dedent_triple": {
        "description": ":3<<< dedents line 3 by 3 shiftwidths",
        "keys": ":%>\r:%>\r:%>\r:3<<<\r",
        "initial": LINES_INDENT,
    },

    # ── 0857 :%norm A; — append ';' to every line ───────────────
    "percent_norm_append": {
        "description": ":%norm A; appends ; to every line",
        "keys": ":%norm A;\r",
        "initial": LINES_LIST,
    },

    # ── 0858 :%norm I# — insert '# ' at start of every line ─────
    "percent_norm_insert_prefix": {
        "description": ":%norm I# inserts '# ' at start of every line",
        "keys": ":%norm I# \r",
        "initial": LINES_LIST,
    },

    # ── 0859 :3,5norm A! — append '!' to lines 3-5 only ─────────
    "range_norm_append": {
        "description": ":3,5norm A! appends ! only to lines 3-5",
        "keys": ":3,5norm A!\r",
        "initial": LINES_ABCDE,
    },

    # ── Visual + ex range substitute (0842) ────────────────────
    "visual_substitute": {
        "description": "select lines, then :s with auto '<,'> range",
        "keys": "Vjj:s/item/fruit/g\r",
        "initial": LINES_LIST,
    },
}
