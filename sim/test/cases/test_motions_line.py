"""
MOTIONS_LINE: 0, ^, $, g_, +, Enter, -, _, |, G, gg
with counts, empty lines, whitespace, tabs, boundary conditions.
"""

CASES = {
    # ══════════════════════════════════════
    # 0 — go to first column
    # ══════════════════════════════════════
    "zero_from_middle": {"keys": "4l0", "initial": "abcdefgh"},
    "zero_already_at_col0": {"keys": "0", "initial": "abcdefgh"},
    "zero_single_char": {"keys": "0", "initial": "x"},
    "zero_on_empty_line": {"keys": "j0", "initial": "abc\n\ndef"},
    "zero_on_indented_line": {"keys": "j4l0", "initial": "abc\n    hello"},
    "zero_on_tab_indented": {"keys": "j2l0", "initial": "abc\n\thello"},
    "zero_whitespace_only_line": {"keys": "j$0", "initial": "abc\n     "},

    # ══════════════════════════════════════
    # ^ — first non-blank character
    # ══════════════════════════════════════
    "caret_no_indent": {"keys": "4l^", "initial": "abcdefgh"},
    "caret_spaces_indent": {"keys": "$^", "initial": "    hello world"},
    "caret_tab_indent": {"keys": "$^", "initial": "\thello world"},
    "caret_mixed_indent": {"keys": "$^", "initial": " \t hello world"},
    "caret_already_at_first_nonblank": {"keys": "4l^", "initial": "    hello"},
    "caret_from_before_indent": {"keys": "^", "initial": "    hello"},
    "caret_single_char_no_indent": {"keys": "^", "initial": "x"},
    "caret_single_char_with_indent": {"keys": "$^", "initial": "   x"},
    "caret_whitespace_only": {"keys": "$^", "initial": "      "},
    "caret_second_line_indented": {"keys": "j$^", "initial": "top\n    indented"},
    "caret_tab_and_spaces": {"keys": "$^", "initial": "\t  code here"},
    "caret_on_empty_line": {"keys": "j^", "initial": "abc\n\ndef"},

    # ══════════════════════════════════════
    # $ — end of line (last character)
    # ══════════════════════════════════════
    "dollar_from_start": {"keys": "$", "initial": "abcdefgh"},
    "dollar_already_at_end": {"keys": "$$", "initial": "abcdefgh"},
    "dollar_single_char": {"keys": "$", "initial": "x"},
    "dollar_with_trailing_spaces": {"keys": "$", "initial": "hello   "},
    "dollar_second_line": {"keys": "j$", "initial": "short\nlonger line here"},
    "dollar_on_empty_line": {"keys": "j$", "initial": "abc\n\ndef"},
    "dollar_count_2": {"keys": "2$", "initial": "line one\nline two\nline three"},
    "dollar_count_3": {"keys": "3$", "initial": "aa\nbb\ncc\ndd"},
    "dollar_count_exceeds": {"keys": "10$", "initial": "aa\nbb\ncc"},
    "dollar_whitespace_only_line": {"keys": "j$", "initial": "abc\n     "},

    # ══════════════════════════════════════
    # g_ — last non-blank character
    # ══════════════════════════════════════
    "g_under_no_trailing": {"keys": "g_", "initial": "abcdefgh"},
    "g_under_trailing_spaces": {"keys": "g_", "initial": "hello   "},
    "g_under_trailing_mixed": {"keys": "g_", "initial": "hello \t "},
    "g_under_from_middle": {"keys": "3lg_", "initial": "abcdef   "},
    "g_under_indented_trailing": {"keys": "g_", "initial": "   hello   "},
    "g_under_single_char_trailing": {"keys": "g_", "initial": "x   "},
    "g_under_whitespace_only": {"keys": "g_", "initial": "      "},
    "g_under_second_line": {"keys": "jg_", "initial": "top\nhello   "},
    "g_under_on_empty_line": {"keys": "jg_", "initial": "abc\n\ndef"},
    "g_under_count_2": {"keys": "2g_", "initial": "aaa\nbbb   \nccc"},
    "g_under_count_3": {"keys": "3g_", "initial": "aa\nbb\ncc   \ndd"},

    # ══════════════════════════════════════
    # + — first non-blank of next line
    # ══════════════════════════════════════
    "plus_basic": {"keys": "+", "initial": "hello\nworld"},
    "plus_to_indented": {"keys": "+", "initial": "hello\n    world"},
    "plus_to_tab_indented": {"keys": "+", "initial": "hello\n\tworld"},
    "plus_from_middle_of_line": {"keys": "3l+", "initial": "hello\n  world"},
    "plus_to_whitespace_only": {"keys": "+", "initial": "hello\n     "},
    "plus_count_2": {"keys": "2+", "initial": "aaa\nbbb\n  ccc"},
    "plus_count_3": {"keys": "3+", "initial": "aa\nbb\ncc\n   dd"},
    "plus_at_last_line": {"keys": "G+", "initial": "aaa\nbbb"},
    "plus_to_empty_line": {"keys": "+", "initial": "abc\n\ndef"},
    "plus_count_exceeds": {"keys": "10+", "initial": "aa\nbb\ncc"},
    "plus_varying_indent": {
        "keys": "2+",
        "initial": "zero\n  two\n\tfour\n      six",
    },

    # ══════════════════════════════════════
    # Enter (\r) — same as + (first non-blank next line)
    # ══════════════════════════════════════
    "enter_basic": {"keys": "\r", "initial": "hello\nworld"},
    "enter_to_indented": {"keys": "\r", "initial": "hello\n    world"},
    "enter_count_2": {"keys": "2\r", "initial": "aa\nbb\n  cc"},
    "enter_at_last_line": {"keys": "G\r", "initial": "aaa\nbbb"},

    # ══════════════════════════════════════
    # - — first non-blank of previous line
    # ══════════════════════════════════════
    "minus_basic": {"keys": "j-", "initial": "hello\nworld"},
    "minus_to_indented": {"keys": "j-", "initial": "    hello\nworld"},
    "minus_from_middle_of_line": {"keys": "j3l-", "initial": "  hello\nworld"},
    "minus_at_first_line": {"keys": "-", "initial": "hello\nworld"},
    "minus_count_2": {"keys": "2j2-", "initial": "aa\n  bb\n    cc"},
    "minus_count_3": {"keys": "G3-", "initial": "  aa\nbb\ncc\ndd"},
    "minus_to_empty_line": {"keys": "2j-", "initial": "hello\n\nworld"},
    "minus_count_exceeds": {"keys": "j10-", "initial": "aa\nbb\ncc"},
    "minus_varying_indent": {
        "keys": "G2-",
        "initial": "zero\n  two\n\tfour\n    six",
    },

    # ══════════════════════════════════════
    # _ — first non-blank of [count-1] lines down
    # ══════════════════════════════════════
    "underscore_no_count": {"keys": "3l_", "initial": "   hello world"},
    "underscore_count_1": {"keys": "3l1_", "initial": "   hello world"},
    "underscore_count_2": {"keys": "2_", "initial": "aaa\n  bbb\nccc"},
    "underscore_count_3": {"keys": "3_", "initial": "aaa\nbbb\n   ccc\nddd"},
    "underscore_indented_start": {"keys": "_", "initial": "    hello"},
    "underscore_on_empty_line": {"keys": "j_", "initial": "abc\n\ndef"},
    "underscore_to_empty_line": {"keys": "2_", "initial": "abc\n\ndef"},
    "underscore_count_exceeds": {"keys": "20_", "initial": "aa\nbb\ncc"},
    "underscore_already_at_nonblank": {"keys": "_", "initial": "hello"},
    "underscore_whitespace_only": {"keys": "_", "initial": "     "},

    # ══════════════════════════════════════
    # | — go to screen column [count]
    # ══════════════════════════════════════
    "pipe_col_1": {"keys": "4l1|", "initial": "abcdefghij"},
    "pipe_col_5": {"keys": "5|", "initial": "abcdefghij"},
    "pipe_col_10": {"keys": "10|", "initial": "abcdefghij"},
    "pipe_no_count": {"keys": "4l|", "initial": "abcdefghij"},
    "pipe_exceeds_line_len": {"keys": "30|", "initial": "abcdef"},
    "pipe_col_1_already_there": {"keys": "1|", "initial": "abcdefghij"},
    "pipe_col_last_char": {"keys": "6|", "initial": "abcdef"},
    "pipe_single_char_line": {"keys": "5|", "initial": "x"},
    "pipe_empty_line": {"keys": "j5|", "initial": "abc\n\ndef"},
    "pipe_on_indented": {"keys": "8|", "initial": "    hello world"},
    "pipe_with_tabs": {"keys": "9|", "initial": "\thello"},
    "pipe_from_end": {"keys": "$3|", "initial": "abcdefgh"},

    # ══════════════════════════════════════
    # G — go to line [count] or last line
    # ══════════════════════════════════════
    "G_no_count": {
        "keys": "G",
        "initial": "line one\nline two\nline three",
    },
    "G_to_line_1": {
        "keys": "jj1G",
        "initial": "first\nsecond\nthird",
    },
    "G_to_line_2": {
        "keys": "2G",
        "initial": "first\nsecond\nthird",
    },
    "G_to_line_3": {
        "keys": "3G",
        "initial": "first\n  second\n    third",
    },
    "G_to_last_explicit": {
        "keys": "3G",
        "initial": "aa\nbb\ncc",
    },
    "G_count_exceeds": {
        "keys": "99G",
        "initial": "aa\nbb\ncc",
    },
    "G_single_line": {"keys": "G", "initial": "only"},
    "G_to_indented_line": {
        "keys": "3G",
        "initial": "aa\nbb\n    cc\ndd",
    },
    "G_to_empty_line": {
        "keys": "2G",
        "initial": "aa\n\ncc",
    },
    "G_on_empty_buffer": {"keys": "G", "initial": ""},
    "G_from_middle_col": {
        "keys": "3lG",
        "initial": "hello\nworld\n  end",
    },
    "G_many_lines": {
        "keys": "5G",
        "initial": "a\nb\nc\nd\n  e\nf\ng\nh",
    },

    # ══════════════════════════════════════
    # gg — go to line [count] or first line
    # ══════════════════════════════════════
    "gg_no_count": {
        "keys": "Ggg",
        "initial": "first\nsecond\nthird",
    },
    "gg_to_line_1": {
        "keys": "G1gg",
        "initial": "first\nsecond\nthird",
    },
    "gg_to_line_2": {
        "keys": "2gg",
        "initial": "first\nsecond\nthird",
    },
    "gg_to_line_3": {
        "keys": "3gg",
        "initial": "first\nsecond\n    third",
    },
    "gg_count_exceeds": {
        "keys": "99gg",
        "initial": "aa\nbb\ncc",
    },
    "gg_single_line": {"keys": "gg", "initial": "only"},
    "gg_already_at_first": {
        "keys": "gg",
        "initial": "first\nsecond",
    },
    "gg_to_indented_first": {
        "keys": "Ggg",
        "initial": "    first\nsecond\nthird",
    },
    "gg_to_empty_line": {
        "keys": "3gg",
        "initial": "aa\nbb\n\ndd",
    },
    "gg_on_empty_buffer": {"keys": "gg", "initial": ""},
    "gg_from_middle_col": {
        "keys": "j3lgg",
        "initial": "  hello\nworld",
    },
    "gg_many_lines": {
        "keys": "G4gg",
        "initial": "a\nb\nc\n   d\ne\nf",
    },
}
