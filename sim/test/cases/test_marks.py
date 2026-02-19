CASES = {
    # === Basic mark set and jump with ' (line) ===
    "mark_a_jump_back_apostrophe": {
        "keys": "majj'a",
        "initial": "line one\nline two\nline three\nline four",
    },
    "mark_a_jump_from_bottom": {
        "keys": "maG'a",
        "initial": "first\nsecond\nthird\nfourth\nfifth",
    },
    "mark_a_jump_from_top": {
        "keys": "Gma0gg'a",
        "initial": "aaa\nbbb\nccc\nddd",
    },
    "mark_a_same_line": {
        "keys": "maw'a",
        "initial": "hello world foo bar",
    },

    # === Basic mark set and jump with ` (exact position) ===
    "mark_a_jump_back_backtick": {
        "keys": "ma3j`a",
        "initial": "line one\nline two\nline three\nline four",
    },
    "mark_a_backtick_preserves_column": {
        "keys": "llmajj`a",
        "initial": "abcdef\nghijkl\nmnopqr",
    },
    "mark_a_backtick_at_col_5": {
        "keys": "4lmajj`a",
        "initial": "abcdefgh\nxxxxxxxx\nyyyyyyyy",
    },
    "mark_a_backtick_at_col_0": {
        "keys": "majj`a",
        "initial": "first\nsecond\nthird",
    },

    # === ' vs ` difference: first non-blank vs exact col ===
    "apostrophe_goes_to_first_nonblank": {
        "keys": "llmajj'a",
        "initial": "  hello\nworld\n  there",
    },
    "backtick_goes_to_exact_column": {
        "keys": "llmajj`a",
        "initial": "  hello\nworld\n  there",
    },
    "apostrophe_indented_line": {
        "keys": "wmajj'a",
        "initial": "\thello world\nfoo bar\nbaz qux",
    },
    "backtick_indented_line": {
        "keys": "wmajj`a",
        "initial": "\thello world\nfoo bar\nbaz qux",
    },
    "apostrophe_deep_indent": {
        "keys": "3lmajj'a",
        "initial": "\t\tdeep\nshallow\nend",
    },
    "backtick_deep_indent": {
        "keys": "3lmajj`a",
        "initial": "\t\tdeep\nshallow\nend",
    },
    "apostrophe_vs_backtick_spaces": {
        "keys": "5lmaG'a",
        "initial": "     spaced out\nlast",
    },
    "backtick_vs_apostrophe_spaces": {
        "keys": "5lmaG`a",
        "initial": "     spaced out\nlast",
    },

    # === Multiple marks at different positions ===
    "two_marks_a_and_b": {
        "keys": "majjmb'a",
        "initial": "aaa\nbbb\nccc\nddd",
    },
    "two_marks_jump_to_b": {
        "keys": "majjmbgg'b",
        "initial": "aaa\nbbb\nccc\nddd",
    },
    "three_marks_a_b_c": {
        "keys": "majjmbjjmcgg'c",
        "initial": "L1\nL2\nL3\nL4\nL5",
    },
    "three_marks_jump_middle": {
        "keys": "majjmbjjmcgg'b",
        "initial": "L1\nL2\nL3\nL4\nL5",
    },
    "marks_different_columns": {
        "keys": "lmajjllmbgg`b",
        "initial": "abcdef\nghijkl\nmnopqr",
    },
    "marks_different_columns_jump_a": {
        "keys": "lmajjllmbgg`a",
        "initial": "abcdef\nghijkl\nmnopqr",
    },

    # === Jump between marks ===
    "jump_between_two_marks": {
        "keys": "maGmb'a'b",
        "initial": "top\nmiddle\nbottom",
    },
    "jump_back_and_forth": {
        "keys": "majjmb'a'b'a",
        "initial": "one\ntwo\nthree\nfour",
    },
    "jump_three_marks_cycle": {
        "keys": "majjmbjjmc'a'b'c",
        "initial": "L1\nL2\nL3\nL4\nL5",
    },

    # === Mark on first line, last line, middle ===
    "mark_on_first_line": {
        "keys": "maG'a",
        "initial": "first\nsecond\nthird\nfourth",
    },
    "mark_on_last_line": {
        "keys": "Gmagg'a",
        "initial": "first\nsecond\nthird\nfourth",
    },
    "mark_on_middle_line": {
        "keys": "jjmagg'a",
        "initial": "L1\nL2\nL3\nL4\nL5",
    },

    # === Mark on empty line ===
    "mark_on_empty_line": {
        "keys": "jmaG'a",
        "initial": "content\n\nmore content",
    },
    "mark_on_empty_line_backtick": {
        "keys": "jmaG`a",
        "initial": "content\n\nmore content",
    },
    "mark_on_blank_line_with_spaces": {
        "keys": "jmajj'a",
        "initial": "aaa\n   \nbbb\nccc",
    },

    # === Overwrite a mark ===
    "overwrite_mark_a": {
        "keys": "majjmagg'a",
        "initial": "L1\nL2\nL3\nL4",
    },
    "overwrite_mark_a_different_col": {
        "keys": "lmajjllmagg`a",
        "initial": "abcdef\nghijkl\nmnopqr",
    },
    "overwrite_mark_twice": {
        "keys": "majjmajjmagg'a",
        "initial": "L1\nL2\nL3\nL4\nL5",
    },

    # === Delete with mark: d'a ===
    "delete_to_mark_line_up": {
        "keys": "majjd'a",
        "initial": "L1\nL2\nL3\nL4\nL5",
    },
    "delete_to_mark_line_down": {
        "keys": "jjmaggd'a",
        "initial": "L1\nL2\nL3\nL4\nL5",
    },
    "delete_to_mark_same_line": {
        "keys": "mad'a",
        "initial": "single line\nanother",
    },
    "delete_to_mark_adjacent_lines": {
        "keys": "majd'a",
        "initial": "aaa\nbbb\nccc\nddd",
    },
    "delete_to_mark_multiple_lines_up": {
        "keys": "ma3jd'a",
        "initial": "L1\nL2\nL3\nL4\nL5",
    },

    # === Delete with mark: d`a ===
    "delete_to_mark_exact_pos_up": {
        "keys": "llmajjd`a",
        "initial": "abcdef\nghijkl\nmnopqr",
    },
    "delete_to_mark_exact_pos_down": {
        "keys": "jjllmaggd`a",
        "initial": "abcdef\nghijkl\nmnopqr",
    },
    "delete_to_mark_exact_same_line": {
        "keys": "ma$d`a",
        "initial": "hello world",
    },
    "delete_to_mark_backtick_forward": {
        "keys": "llma0d`a",
        "initial": "abcdefgh",
    },

    # === Yank with mark: y'a then p ===
    "yank_to_mark_line_put": {
        "keys": "majjy'aGp",
        "initial": "L1\nL2\nL3\nL4",
    },
    "yank_to_mark_backtick_put": {
        "keys": "llmawwy`a$p",
        "initial": "abcdefghij",
    },
    "yank_to_mark_multiline_put": {
        "keys": "ma2jy'aGp",
        "initial": "aaa\nbbb\nccc\nddd",
    },

    # === Change with mark: c'a ===
    "change_to_mark_line": {
        "keys": "majjc'aREPLACED\x1b",
        "initial": "L1\nL2\nL3\nL4\nL5",
    },
    "change_to_mark_line_down": {
        "keys": "jjmaggc'aXX\x1b",
        "initial": "L1\nL2\nL3\nL4",
    },

    # === Marks at various columns ===
    "mark_at_column_0": {
        "keys": "0majj`a",
        "initial": "abcdef\nghijkl",
    },
    "mark_at_column_5": {
        "keys": "4lmajj`a",
        "initial": "abcdefgh\nxxxxxxxx",
    },
    "mark_at_last_column": {
        "keys": "$majj`a",
        "initial": "abcdef\nghijkl",
    },
    "mark_at_column_mid": {
        "keys": "wwmajj`a",
        "initial": "one two three four\nxxxxxxxxxxxxxxxxxx",
    },

    # === Marks survive cursor movement ===
    "mark_survives_movement": {
        "keys": "llmajj$hhkww`a",
        "initial": "abcdef\nghijkl\nmnopqr",
    },
    "mark_survives_gg_G": {
        "keys": "jjlmaGgg`a",
        "initial": "aaa\nbbb\nccc\nddd",
    },

    # === Multiple mark letters ===
    "mark_z": {
        "keys": "mzjj'z",
        "initial": "alpha\nbeta\ngamma\ndelta",
    },
    "mark_m": {
        "keys": "jmm0gg'm",
        "initial": "aaa\nbbb\nccc",
    },
    "marks_a_through_d": {
        "keys": "majmbj2lmcjmd'a'b'c'd",
        "initial": "L1\nL2\nL3\nL4\nL5",
    },

    # === Edge cases ===
    "mark_on_single_line_buffer": {
        "keys": "llma$`a",
        "initial": "only line",
    },
    "mark_first_char": {
        "keys": "0maG`a",
        "initial": "hello\nworld",
    },
    "mark_after_word_motion": {
        "keys": "wwmagg`a",
        "initial": "aaa bbb ccc ddd",
    },
    "apostrophe_on_line_with_tabs": {
        "keys": "wma3j'a",
        "initial": "\t\thello\nfoo\nbar\nbaz",
    },
    "backtick_column_beyond_short_line": {
        "keys": "4lmaG`a",
        "initial": "abcdefgh\nab",
    },
    "delete_mark_range_three_lines": {
        "keys": "maGd'a",
        "initial": "L1\nL2\nL3\nL4\nL5",
    },
}
