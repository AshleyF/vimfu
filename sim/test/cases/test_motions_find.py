CASES = {
    # =====================================================================
    # f{char} - find char forward (inclusive, lands ON the char)
    # =====================================================================
    "f_basic": {
        "keys": "fa",
        "initial": "hello world and more",
    },
    "f_first_char_of_word": {
        "keys": "fw",
        "initial": "hello world",
    },
    "f_last_char_on_line": {
        "keys": "fe",
        "initial": "abcde",
    },
    "f_finds_second_occurrence_skips_first": {
        "keys": "fl",
        "initial": "hello world",
    },
    "f_with_count_2": {
        "keys": "2fo",
        "initial": "one two four open",
    },
    "f_with_count_3": {
        "keys": "3fo",
        "initial": "one two four open onto",
    },
    "f_char_not_found": {
        "keys": "fz",
        "initial": "hello world",
    },
    "f_find_space": {
        "keys": "f ",
        "initial": "hello world",
    },
    "f_find_punctuation": {
        "keys": "f.",
        "initial": "hello world. done",
    },
    "f_find_digit": {
        "keys": "f3",
        "initial": "abc123def",
    },
    "f_find_comma": {
        "keys": "f,",
        "initial": "one, two, three",
    },
    "f_at_end_of_line_not_found": {
        "keys": "$fx",
        "initial": "abcdef",
    },
    "f_skip_char_under_cursor": {
        "keys": "fh",
        "initial": "hello haha",
    },
    "f_adjacent_duplicate_chars": {
        "keys": "fb",
        "initial": "aabbbcc",
    },
    "f_count_exceeds_occurrences": {
        "keys": "5fo",
        "initial": "one two",
    },
    "f_from_middle_of_line": {
        "keys": "llllfe",
        "initial": "abcdefgh",
    },
    "f_single_char_line": {
        "keys": "fa",
        "initial": "a",
    },
    "f_find_bang": {
        "keys": "f!",
        "initial": "hello! world!",
    },
    "f_find_hash": {
        "keys": "f#",
        "initial": "item #1 is here",
    },
    "f_find_tab_char": {
        "keys": "f\t",
        "initial": "hello\tworld",
    },

    # =====================================================================
    # F{char} - find char backward (inclusive, lands ON the char)
    # =====================================================================
    "F_basic": {
        "keys": "$Fh",
        "initial": "hello world",
    },
    "F_finds_nearest_backward": {
        "keys": "$Fo",
        "initial": "one two four",
    },
    "F_with_count_2": {
        "keys": "$2Fo",
        "initial": "one two four",
    },
    "F_char_not_found": {
        "keys": "$Fz",
        "initial": "hello world",
    },
    "F_at_column_0_not_found": {
        "keys": "Fa",
        "initial": "abcdef",
    },
    "F_find_space_backward": {
        "keys": "$F ",
        "initial": "hello world",
    },
    "F_find_punctuation_backward": {
        "keys": "$F.",
        "initial": "a.b.c.d",
    },
    "F_adjacent_duplicates_backward": {
        "keys": "$Fb",
        "initial": "aabbbcc",
    },
    "F_from_middle_backward": {
        "keys": "llllFa",
        "initial": "abcadef",
    },
    "F_count_exceeds_occurrences": {
        "keys": "$5Fa",
        "initial": "apple",
    },
    "F_single_char_line": {
        "keys": "Fa",
        "initial": "a",
    },
    "F_find_digit_backward": {
        "keys": "$F1",
        "initial": "a1b2c3d",
    },

    # =====================================================================
    # t{char} - till char forward (exclusive, lands BEFORE the char)
    # =====================================================================
    "t_basic": {
        "keys": "tw",
        "initial": "hello world",
    },
    "t_vs_f_difference": {
        "keys": "td",
        "initial": "abcdef",
    },
    "t_with_count_2": {
        "keys": "2to",
        "initial": "one two four open",
    },
    "t_char_not_found": {
        "keys": "tz",
        "initial": "hello world",
    },
    "t_target_adjacent_no_move": {
        "keys": "tb",
        "initial": "abcdef",
    },
    "t_find_space": {
        "keys": "t ",
        "initial": "hello world",
    },
    "t_find_punctuation": {
        "keys": "t.",
        "initial": "hello world. done",
    },
    "t_at_end_of_line": {
        "keys": "$tx",
        "initial": "abcdef",
    },
    "t_adjacent_duplicates": {
        "keys": "tc",
        "initial": "aabbbcc",
    },
    "t_count_exceeds_occurrences": {
        "keys": "5to",
        "initial": "one two",
    },
    "t_from_middle": {
        "keys": "lllth",
        "initial": "abcdefgh",
    },
    "t_single_char_no_move": {
        "keys": "ta",
        "initial": "a",
    },
    "t_find_digit": {
        "keys": "t5",
        "initial": "abc5def",
    },
    "t_skip_current_position": {
        "keys": "lte",
        "initial": "abcde",
    },

    # =====================================================================
    # T{char} - till char backward (exclusive, lands AFTER the char)
    # =====================================================================
    "T_basic": {
        "keys": "$Th",
        "initial": "hello world",
    },
    "T_with_count_2": {
        "keys": "$2To",
        "initial": "one two four open",
    },
    "T_char_not_found": {
        "keys": "$Tz",
        "initial": "hello world",
    },
    "T_target_adjacent_no_move": {
        "keys": "$Te",
        "initial": "abcdef",
    },
    "T_at_column_0_not_found": {
        "keys": "Ta",
        "initial": "abcdef",
    },
    "T_find_space_backward": {
        "keys": "$T ",
        "initial": "hello world",
    },
    "T_adjacent_duplicates_backward": {
        "keys": "$Tb",
        "initial": "aabbbcc",
    },
    "T_from_middle": {
        "keys": "llllTa",
        "initial": "abcadefg",
    },
    "T_count_exceeds_occurrences": {
        "keys": "$5Ta",
        "initial": "apple",
    },
    "T_find_digit_backward": {
        "keys": "$T2",
        "initial": "a1b2c3d",
    },

    # =====================================================================
    # ; - repeat last f/F/t/T in same direction
    # =====================================================================
    "semicolon_after_f": {
        "keys": "fo;",
        "initial": "one two four open",
    },
    "semicolon_after_f_twice": {
        "keys": "fo;;",
        "initial": "one two four open onto",
    },
    "semicolon_after_F": {
        "keys": "$Fo;",
        "initial": "one two four open",
    },
    "semicolon_after_t": {
        "keys": "to;",
        "initial": "one two four open",
    },
    "semicolon_after_T": {
        "keys": "$To;",
        "initial": "one two four open",
    },
    "semicolon_with_count": {
        "keys": "fo2;",
        "initial": "one two four open onto over",
    },
    "semicolon_no_previous_find": {
        "keys": ";",
        "initial": "hello world",
    },
    "semicolon_no_more_matches": {
        "keys": "fo;;;",
        "initial": "one two",
    },
    "semicolon_after_f_space": {
        "keys": "f ;",
        "initial": "one two three four",
    },
    "semicolon_after_t_works_like_t": {
        "keys": "to;",
        "initial": "hello old opera",
    },
    "semicolon_multiple_after_f": {
        "keys": "fa;;;",
        "initial": "abracadabra magic",
    },

    # =====================================================================
    # , - repeat last f/F/t/T in opposite direction
    # =====================================================================
    "comma_after_f": {
        "keys": "fo;,",
        "initial": "one two four open",
    },
    "comma_after_F": {
        "keys": "$Fo;,",
        "initial": "one two four open",
    },
    "comma_after_t": {
        "keys": "to;,",
        "initial": "one two four open",
    },
    "comma_after_T": {
        "keys": "$To;,",
        "initial": "one two four open",
    },
    "comma_with_count": {
        "keys": "$Fo,2,",
        "initial": "one two four open onto",
    },
    "comma_no_previous_find": {
        "keys": ",",
        "initial": "hello world",
    },
    "comma_reverses_f_to_F": {
        "keys": "fo;;,",
        "initial": "one two four open onto",
    },
    "comma_reverses_F_to_f": {
        "keys": "$Fo,,",
        "initial": "one two four open onto",
    },
    "comma_no_match_in_reverse": {
        "keys": "fo,",
        "initial": "one two",
    },

    # =====================================================================
    # Mixed sequences: f/t then ; and , combinations
    # =====================================================================
    "f_semicolon_comma_sequence": {
        "keys": "fe;;,",
        "initial": "eagle eye entered evenly",
    },
    "t_semicolon_comma_sequence": {
        "keys": "te;;,",
        "initial": "eagle eye entered evenly",
    },
    "f_then_multiple_semicolons": {
        "keys": "fa;;;;",
        "initial": "a cat ran a lap and nap",
    },
    "F_then_comma_forward": {
        "keys": "$Fa,",
        "initial": "a cat ran a lap",
    },
    "f_comma_at_start_no_move": {
        "keys": "fx,",
        "initial": "abcxdef",
    },
    "f_semicolon_then_comma_back": {
        "keys": "fl;;,,",
        "initial": "hello silly llama",
    },

    # =====================================================================
    # Edge cases and special scenarios
    # =====================================================================
    "f_on_empty_line": {
        "keys": "jfa",
        "initial": "abc\n\ndef",
    },
    "f_does_not_cross_lines": {
        "keys": "fd",
        "initial": "abc\ndef",
    },
    "F_does_not_cross_lines": {
        "keys": "jFa",
        "initial": "abc\ndef",
    },
    "t_does_not_cross_lines": {
        "keys": "td",
        "initial": "abc\ndef",
    },
    "T_does_not_cross_lines": {
        "keys": "jTa",
        "initial": "abc\ndef",
    },
    "f_same_char_repeated_line": {
        "keys": "fa",
        "initial": "aaaaaaa",
    },
    "f_count_on_repeated_chars": {
        "keys": "3fa",
        "initial": "aaaaaaa",
    },
    "t_on_repeated_chars": {
        "keys": "ta",
        "initial": "aaaaaaa",
    },
    "F_on_repeated_chars": {
        "keys": "$Fa",
        "initial": "aaaaaaa",
    },
    "T_on_repeated_chars": {
        "keys": "$Ta",
        "initial": "aaaaaaa",
    },
    "semicolon_after_t_repeated_chars": {
        "keys": "ta;;",
        "initial": "aaaaaaa",
    },
    "f_underscore": {
        "keys": "f_",
        "initial": "hello_world_test",
    },
    "f_bracket": {
        "keys": "f(",
        "initial": "func(arg1, arg2)",
    },
    "f_closing_bracket": {
        "keys": "f)",
        "initial": "func(arg1, arg2)",
    },
    "f_quote": {
        "keys": "f\"",
        "initial": "say \"hello\" now",
    },
    "t_quote": {
        "keys": "t'",
        "initial": "it's a test",
    },
    "f_at_penultimate_char": {
        "keys": "$hff",
        "initial": "abcdef",
    },
    "t_at_penultimate_finds_last": {
        "keys": "lllltf",
        "initial": "abcdef",
    },
    "f_with_multiline_initial": {
        "keys": "jfx",
        "initial": "first line\nsecond x line",
    },
    "F_with_multiline_initial": {
        "keys": "j$Fs",
        "initial": "first line\nsecond x line",
    },
    "semicolon_preserves_t_semantics": {
        "keys": "te;",
        "initial": "one eye entered",
    },
    "comma_preserves_t_semantics": {
        "keys": "$Te,",
        "initial": "one eye entered",
    },
    "f_cursor_stays_on_not_found_count": {
        "keys": "lll3fx",
        "initial": "abcxdexf",
    },
}
