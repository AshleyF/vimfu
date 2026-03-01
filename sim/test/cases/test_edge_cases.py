"""General edge case tests.

Tests tricky edge cases for existing features: % motion with nesting,
dot repeat after surround, text objects at buffer boundaries, and
operators combined with unusual motions.
"""

CASES = {
    # ══════════════════════════════════════════════════════════
    # % MOTION — NESTED / MIXED / MULTI-LINE
    # ══════════════════════════════════════════════════════════

    "percent_nested_3_levels": {
        "description": "% on outermost ( of 3-level nesting jumps to closing )",
        "keys": "%",
        "initial": "(a(b(c)))",
    },
    "percent_across_lines": {
        "description": "% on ( that spans multiple lines jumps to )",
        "keys": "%",
        "initial": "(\n  a,\n  b\n)",
    },
    "percent_d_nested_braces": {
        "description": "d% on outer { with nested {} inside",
        "keys": "f{d%",
        "initial": "x { a { b } c } y",
    },
    "percent_c_parens": {
        "description": "c% on ( replaces matched block",
        "keys": "f(c%X\x1b",
        "initial": "call(arg1, arg2) done",
    },
    "percent_y_paste_brackets": {
        "description": "y% on [ then paste — copies bracket block",
        "keys": "f[y%$p",
        "initial": "arr[idx] end",
    },
    "percent_count_50": {
        "description": "50% goes to middle of 10-line file",
        "keys": "50%",
        "initial": "line1\nline2\nline3\nline4\nline5\nline6\nline7\nline8\nline9\nline10",
    },
    "percent_on_close_brace": {
        "description": "% on } jumps back to matching {",
        "keys": "$%",
        "initial": "{hello}",
    },
    "percent_on_close_bracket": {
        "description": "% on ] jumps to matching [",
        "keys": "$%",
        "initial": "[hello]",
    },

    # ══════════════════════════════════════════════════════════
    # DOT REPEAT AFTER SURROUND WITH MOTIONS
    # ══════════════════════════════════════════════════════════

    "dot_after_ysiw_paren_w": {
        "description": "ysiw) on first word, w. on next — dot repeats surround",
        "keys": "ysiw)w.",
        "initial": "alpha beta gamma",
    },
    "dot_after_ysiw_bracket_w": {
        "description": "ysiw] then w. — repeats bracket surround",
        "keys": "ysiw]w.",
        "initial": "one two three",
    },
    "dot_after_ys_dollar_quote": {
        "description": "ys$\" wraps to EOL in quotes, j0. repeats on next line",
        "keys": "ys$\"j0.",
        "initial": "first line\nsecond line",
    },

    # ══════════════════════════════════════════════════════════
    # TEXT OBJECTS AT BUFFER BOUNDARIES
    # ══════════════════════════════════════════════════════════

    "dip_single_line": {
        "description": "dip on a single-line buffer deletes it",
        "keys": "dip",
        "initial": "only line",
    },
    "dip_at_buffer_start": {
        "description": "dip on first paragraph of multi-para buffer",
        "keys": "dip",
        "initial": "first para\nstill first\n\nsecond para",
    },
    "dip_at_buffer_end": {
        "description": "dip on last paragraph",
        "keys": "3jdip",
        "initial": "first para\n\nthird line\nfourth line",
    },
    "ci_paren_spanning_lines": {
        "description": "ci( when ( is on line 0 and ) is on last line",
        "keys": "ci(X\x1b",
        "initial": "(hello\nworld)",
    },
    "di_bracket_at_col_0": {
        "description": "di[ where [ is at col 0 on first line",
        "keys": "di[",
        "initial": "[content] more",
    },
    "di_brace_multiline": {
        "description": "di{ where { on line 0, } on last line",
        "keys": "di{",
        "initial": "{\n  body\n}",
    },
    "diw_single_char": {
        "description": "diw on a buffer that is a single character",
        "keys": "diw",
        "initial": "x",
    },
    "daw_single_word": {
        "description": "daw on a single-word buffer",
        "keys": "daw",
        "initial": "hello",
    },

    # ══════════════════════════════════════════════════════════
    # OPERATORS WITH UNUSUAL MOTIONS
    # ══════════════════════════════════════════════════════════

    "d_percent_mixed_nested": {
        "description": "d% on ( with mixed nested types inside",
        "keys": "f(d%",
        "initial": "x([{y}]) z",
    },
    "c_percent_brace_multiline": {
        "description": "c% on { spanning multiple lines",
        "keys": "f{c%NEW\x1b",
        "initial": "if {\n  body\n} end",
    },
    "d_pipe_column": {
        "description": "d10| deletes to column 10",
        "keys": "d10|",
        "initial": "abcdefghijklmnop",
    },
    "d_brace_paragraph_forward": {
        "description": "d} deletes to end of paragraph",
        "keys": "d}",
        "initial": "aaa\nbbb\n\nccc\nddd",
    },
    "gU_percent_uppercase": {
        "description": "gU% uppercases from ( to matching )",
        "keys": "f(gU%",
        "initial": "call(hello world) end",
    },
    "gu_percent_lowercase": {
        "description": "gu% lowercases from { to matching }",
        "keys": "f{gu%",
        "initial": "x{HELLO WORLD} end",
    },
    "d_2f_char": {
        "description": "d2fa deletes through second occurrence of a",
        "keys": "d2fa",
        "initial": "banana split cake",
    },
    "c_t_char_at_end": {
        "description": "ct) changes up to but not including )",
        "keys": "f(lct)X\x1b",
        "initial": "call(old) done",
    },
}
