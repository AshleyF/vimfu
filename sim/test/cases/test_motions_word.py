"""Word motion tests: w, W, b, B, e, E, ge, gE with counts, punctuation,
empty lines, whitespace-only lines, tabs, boundaries, edge cases."""

CASES = {
    # ══════════════════════════════════════
    # w  (word forward)
    # ══════════════════════════════════════
    "w_basic": {"keys": "w", "initial": "one two three"},
    "w_twice": {"keys": "ww", "initial": "one two three four"},
    "w_three_times": {"keys": "www", "initial": "one two three four five"},
    "w_count_2": {"keys": "2w", "initial": "one two three four five"},
    "w_count_3": {"keys": "3w", "initial": "one two three four five"},
    "w_count_5": {"keys": "5w", "initial": "one two three four five six"},
    "w_count_exceeds": {"keys": "99w", "initial": "one two three"},
    "w_count_exact": {"keys": "4w", "initial": "a b c d e"},
    "w_single_word": {"keys": "w", "initial": "hello"},
    "w_empty_buffer": {"keys": "w", "initial": ""},
    "w_from_middle_of_word": {"keys": "llw", "initial": "hello world foo"},
    "w_from_last_char_of_word": {"keys": "4lw", "initial": "hello world"},

    # w - punctuation behavior
    "w_punct_dot": {"keys": "w", "initial": "hello.world"},
    "w_punct_dot_chain": {"keys": "www", "initial": "hello.world.foo"},
    "w_punct_dash": {"keys": "w", "initial": "foo-bar"},
    "w_punct_comma_space": {"keys": "ww", "initial": "hello, world"},
    "w_underscore_is_word_char": {"keys": "w", "initial": "foo_bar baz"},
    "w_underscore_long": {"keys": "w", "initial": "my_long_variable_name next"},
    "w_mixed_punct_and_space": {"keys": "www", "initial": "hello.world foo-bar"},
    "w_parens": {"keys": "wwww", "initial": "(foo) bar"},
    "w_brackets": {"keys": "wwww", "initial": "[foo] bar"},
    "w_braces": {"keys": "wwww", "initial": "{foo} bar"},
    "w_parens_no_space": {"keys": "www", "initial": "call(arg)"},
    "w_consecutive_punct": {"keys": "ww", "initial": "!!! hello"},
    "w_all_punct_groups": {"keys": "www", "initial": "... ### !!!"},
    "w_mixed_alnum_punct": {"keys": "www", "initial": "foo123+bar456=baz"},
    "w_only_punctuation": {"keys": "ww", "initial": "...---==="},
    "w_numbers_in_word": {"keys": "w", "initial": "abc123 def456"},
    "w_numbers_separate": {"keys": "w", "initial": "abc 123 def"},
    "w_colon_punct": {"keys": "ww", "initial": "key:value rest"},
    "w_semicolons": {"keys": "ww", "initial": "foo;bar;baz rest"},
    "w_quotes_around_word": {"keys": "www", "initial": "\"hello\" world"},
    "w_angle_brackets": {"keys": "www", "initial": "<div> content"},

    # w - whitespace
    "w_leading_spaces": {"keys": "w", "initial": "   hello world"},
    "w_trailing_spaces": {"keys": "ww", "initial": "hello world   "},
    "w_multiple_spaces": {"keys": "w", "initial": "hello    world"},
    "w_tabs_as_whitespace": {"keys": "w", "initial": "hello\tworld"},
    "w_tab_between_words": {"keys": "ww", "initial": "one\ttwo\tthree"},
    "w_mixed_tabs_spaces": {"keys": "w", "initial": "hello \t world"},
    "w_line_ending_with_space": {"keys": "ww", "initial": "hello \nworld"},

    # w - line boundaries
    "w_across_line": {"keys": "ww", "initial": "one two\nthree four"},
    "w_across_multiple_lines": {"keys": "wwww", "initial": "a b\nc d\ne f"},
    "w_across_empty_line": {"keys": "ww", "initial": "hello\n\nworld"},
    "w_across_blank_lines": {"keys": "www", "initial": "hello\n\n\nworld"},
    "w_across_many_empty_lines": {"keys": "wwww", "initial": "hello\n\n\n\nworld"},
    "w_whitespace_only_line": {"keys": "w", "initial": "hello\n   \nworld"},
    "w_end_of_line_to_next": {"keys": "$w", "initial": "abc\ndef"},
    "w_last_word_on_line": {"keys": "ww", "initial": "ab\ncd\nef"},

    # w - single char words
    "w_single_char_words": {"keys": "www", "initial": "a b c d e"},
    "w_single_char_then_long": {"keys": "ww", "initial": "x hello world"},

    # w - boundary clamping
    "w_past_end_clamp": {"keys": "wwwwwww", "initial": "a b c"},
    "w_at_end_of_buffer": {"keys": "wwwwwwwww", "initial": "one two three"},
    "w_count_large_on_short": {"keys": "50w", "initial": "hi there"},

    # ══════════════════════════════════════
    # W  (WORD forward)
    # ══════════════════════════════════════
    "W_basic": {"keys": "W", "initial": "one two three"},
    "W_twice": {"keys": "WW", "initial": "one two three four"},
    "W_count_2": {"keys": "2W", "initial": "one two three four five"},
    "W_count_3": {"keys": "3W", "initial": "one two three four five"},
    "W_count_exceeds": {"keys": "99W", "initial": "one two three"},

    # W - skips punctuation (key difference from w)
    "W_skips_dot": {"keys": "W", "initial": "hello.world foo"},
    "W_skips_dash": {"keys": "W", "initial": "foo-bar baz"},
    "W_skips_parens": {"keys": "W", "initial": "foo(bar) baz"},
    "W_skips_brackets": {"keys": "W", "initial": "[foo] baz"},
    "W_skips_complex_punct": {"keys": "W", "initial": "a.b-c!d next"},
    "W_special_chars_grouped": {"keys": "WW", "initial": "hello-world foo.bar baz"},

    # W - whitespace and lines
    "W_across_line": {"keys": "WW", "initial": "foo.bar\nbaz.qux"},
    "W_across_empty_line": {"keys": "WW", "initial": "hello\n\nworld"},
    "W_tabs": {"keys": "W", "initial": "hello\tworld"},
    "W_multiple_spaces": {"keys": "W", "initial": "hello    world"},
    "W_leading_spaces": {"keys": "W", "initial": "   hello world"},
    "W_end_of_line": {"keys": "$W", "initial": "abc\ndef"},
    "W_whitespace_only_line": {"keys": "W", "initial": "hello\n   \nworld"},

    # W vs w contrast
    "W_vs_w_dot_word": {"keys": "W", "initial": "foo.bar.baz next"},
    "W_from_middle": {"keys": "llW", "initial": "hello.world foo"},
    "W_single_char_words": {"keys": "WWW", "initial": "a b c d"},
    "W_past_end_clamp": {"keys": "WWWWWWW", "initial": "a b c"},

    # ══════════════════════════════════════
    # b  (word backward)
    # ══════════════════════════════════════
    "b_basic": {"keys": "$b", "initial": "one two three"},
    "b_twice": {"keys": "$bb", "initial": "one two three four"},
    "b_three_times": {"keys": "$bbb", "initial": "one two three four"},
    "b_count_2": {"keys": "$2b", "initial": "one two three four five"},
    "b_count_3": {"keys": "$3b", "initial": "one two three four five"},
    "b_count_exceeds": {"keys": "$99b", "initial": "one two three"},
    "b_at_start": {"keys": "b", "initial": "one two three"},
    "b_single_word": {"keys": "$b", "initial": "hello"},
    "b_empty_buffer": {"keys": "b", "initial": ""},

    # b - punctuation
    "b_punct_dot": {"keys": "$b", "initial": "hello.world"},
    "b_punct_dash": {"keys": "$b", "initial": "foo-bar"},
    "b_underscore_word": {"keys": "$b", "initial": "one foo_bar"},
    "b_parens": {"keys": "$b", "initial": "call(arg)"},
    "b_consecutive_punct": {"keys": "$b", "initial": "hello !!!"},
    "b_mixed_punct_word": {"keys": "$bb", "initial": "foo.bar baz"},
    "b_from_after_punct": {"keys": "wwb", "initial": "hello.world rest"},

    # b - whitespace
    "b_leading_spaces": {"keys": "wb", "initial": "   hello world"},
    "b_trailing_spaces": {"keys": "$b", "initial": "hello world   "},
    "b_from_middle_of_word": {"keys": "$hhb", "initial": "one twoxyz"},
    "b_multiple_spaces": {"keys": "$b", "initial": "hello    world"},

    # b - lines
    "b_across_line": {"keys": "jb", "initial": "one two\nthree four"},
    "b_across_empty_line": {"keys": "Gb", "initial": "hello\n\nworld"},
    "b_across_many_empty_lines": {"keys": "Gbbbb", "initial": "hello\n\n\n\nworld"},
    "b_whitespace_only_line": {"keys": "Gb", "initial": "hello\n   \nworld"},
    "b_start_of_line": {"keys": "jb", "initial": "end\nstart"},
    "b_on_first_word": {"keys": "b", "initial": "hello world"},

    # ══════════════════════════════════════
    # B  (WORD backward)
    # ══════════════════════════════════════
    "B_basic": {"keys": "$B", "initial": "one two three"},
    "B_twice": {"keys": "$BB", "initial": "one two three four"},
    "B_count_2": {"keys": "$2B", "initial": "one two three four five"},
    "B_count_3": {"keys": "$3B", "initial": "one two three four five"},
    "B_count_exceeds": {"keys": "$99B", "initial": "one two three"},
    "B_at_start": {"keys": "B", "initial": "one two three"},

    # B - skips punctuation
    "B_skips_dot": {"keys": "$B", "initial": "foo hello.world"},
    "B_skips_dash": {"keys": "$B", "initial": "foo bar-baz"},
    "B_skips_complex": {"keys": "$B", "initial": "foo a.b-c!d"},
    "B_skips_parens": {"keys": "$B", "initial": "foo call(arg)"},

    # B - lines
    "B_across_line": {"keys": "jB", "initial": "one two\nthree four"},
    "B_across_empty_line": {"keys": "GB", "initial": "hello\n\nworld"},
    "B_whitespace_only_line": {"keys": "GB", "initial": "hello\n   \nworld"},

    # B vs b contrast
    "B_vs_b_on_dotted": {"keys": "$B", "initial": "start foo.bar.baz"},
    "B_from_middle": {"keys": "$hhB", "initial": "one two.three"},

    # ══════════════════════════════════════
    # e  (end of word forward)
    # ══════════════════════════════════════
    "e_basic": {"keys": "e", "initial": "one two three"},
    "e_twice": {"keys": "ee", "initial": "one two three four"},
    "e_three_times": {"keys": "eee", "initial": "one two three four five"},
    "e_count_2": {"keys": "2e", "initial": "one two three four five"},
    "e_count_3": {"keys": "3e", "initial": "one two three four five"},
    "e_count_exceeds": {"keys": "99e", "initial": "one two three"},
    "e_empty_buffer": {"keys": "e", "initial": ""},

    # e - lands at end of word
    "e_single_char_words": {"keys": "eee", "initial": "a b c d e"},
    "e_at_end_already": {"keys": "ee", "initial": "one two three"},
    "e_on_last_word": {"keys": "wwe", "initial": "one two three"},
    "e_single_word": {"keys": "e", "initial": "hello"},

    # e - punctuation
    "e_punct_dot": {"keys": "e", "initial": "hello.world"},
    "e_punct_dot_chain": {"keys": "eee", "initial": "hello.world.foo"},
    "e_punct_dash": {"keys": "ee", "initial": "foo-bar baz"},
    "e_underscore_word": {"keys": "e", "initial": "foo_bar baz"},
    "e_parens": {"keys": "eee", "initial": "(foo) bar"},
    "e_consecutive_punct": {"keys": "ee", "initial": "!!! hello"},
    "e_brackets_braces": {"keys": "eeee", "initial": "[foo] {bar}"},

    # e - whitespace and lines
    "e_across_line": {"keys": "eee", "initial": "aa bb\ncc dd"},
    "e_across_empty_line": {"keys": "eee", "initial": "hello\n\nworld"},
    "e_leading_spaces": {"keys": "e", "initial": "   hello world"},
    "e_tabs": {"keys": "ee", "initial": "hello\tworld\tfoo"},
    "e_trailing_spaces": {"keys": "ee", "initial": "hello world   "},
    "e_whitespace_only_line": {"keys": "ee", "initial": "hello\n   \nworld"},

    # ══════════════════════════════════════
    # E  (end of WORD forward)
    # ══════════════════════════════════════
    "E_basic": {"keys": "E", "initial": "one two three"},
    "E_twice": {"keys": "EE", "initial": "one two three four"},
    "E_count_2": {"keys": "2E", "initial": "one two three four five"},
    "E_count_3": {"keys": "3E", "initial": "one two three four five"},
    "E_count_exceeds": {"keys": "99E", "initial": "one two three"},

    # E - skips punctuation (key difference from e)
    "E_skips_dot": {"keys": "E", "initial": "hello.world foo"},
    "E_skips_dash": {"keys": "E", "initial": "foo-bar baz"},
    "E_skips_complex": {"keys": "E", "initial": "a.b-c!d next"},
    "E_skips_parens": {"keys": "E", "initial": "foo(bar) baz"},

    # E - lines
    "E_across_line": {"keys": "EEE", "initial": "a.b c.d\ne.f g"},
    "E_across_empty_line": {"keys": "EE", "initial": "hello\n\nworld"},
    "E_whitespace_only_line": {"keys": "EE", "initial": "hello\n   \nworld"},
    "E_tabs": {"keys": "EE", "initial": "foo.bar\tbaz.qux"},

    # E vs e contrast
    "E_vs_e_dotted": {"keys": "E", "initial": "foo.bar.baz next"},
    "E_single_char_words": {"keys": "EEE", "initial": "a b c d"},

    # ══════════════════════════════════════
    # ge (end of word backward)
    # ══════════════════════════════════════
    "ge_basic": {"keys": "wge", "initial": "one two three"},
    "ge_twice": {"keys": "wwgege", "initial": "one two three four"},
    "ge_from_end": {"keys": "$ge", "initial": "one two three"},
    "ge_count_2": {"keys": "$2ge", "initial": "one two three four five"},
    "ge_count_3": {"keys": "$3ge", "initial": "one two three four five"},
    "ge_at_start": {"keys": "ge", "initial": "one two three"},
    "ge_single_word": {"keys": "$ge", "initial": "hello"},

    # ge - punctuation
    "ge_punct_dot": {"keys": "wge", "initial": "hello.world test"},
    "ge_punct_dash": {"keys": "wge", "initial": "foo-bar baz"},
    "ge_underscore": {"keys": "wge", "initial": "foo_bar baz"},
    "ge_parens": {"keys": "wwge", "initial": "(foo) bar"},
    "ge_consecutive_punct": {"keys": "wge", "initial": "!!! hello"},

    # ge - lines
    "ge_across_line": {"keys": "jge", "initial": "one two\nthree four"},
    "ge_across_empty_line": {"keys": "Gge", "initial": "hello\n\nworld"},
    "ge_from_start_of_line": {"keys": "jge", "initial": "abc def\nghi"},
    "ge_whitespace_only_line": {"keys": "Gge", "initial": "hello\n   \nworld"},

    # ge - edge cases
    "ge_single_char_words": {"keys": "wwgege", "initial": "a b c d e"},
    "ge_from_middle_of_word": {"keys": "wlge", "initial": "one two three"},
    "ge_count_exceeds": {"keys": "$99ge", "initial": "one two three"},

    # ══════════════════════════════════════
    # gE (end of WORD backward)
    # ══════════════════════════════════════
    "gE_basic": {"keys": "WgE", "initial": "one two three"},
    "gE_from_end": {"keys": "$gE", "initial": "one two.three"},
    "gE_count_2": {"keys": "$2gE", "initial": "one two three four five"},
    "gE_count_3": {"keys": "$3gE", "initial": "one two three four five"},
    "gE_at_start": {"keys": "gE", "initial": "one two three"},

    # gE - skips punctuation
    "gE_skips_dot": {"keys": "WgE", "initial": "hello.world test"},
    "gE_skips_dash": {"keys": "WgE", "initial": "foo-bar test"},
    "gE_skips_complex": {"keys": "WgE", "initial": "a.b-c!d test"},
    "gE_skips_parens": {"keys": "WgE", "initial": "foo(bar) test"},

    # gE - lines
    "gE_across_line": {"keys": "jgE", "initial": "one two\nthree four"},
    "gE_across_empty_line": {"keys": "GgE", "initial": "hello\n\nworld"},
    "gE_whitespace_only_line": {"keys": "GgE", "initial": "hello\n   \nworld"},

    # gE vs ge contrast
    "gE_vs_ge_dotted": {"keys": "$gE", "initial": "start foo.bar.baz"},
    "gE_count_exceeds": {"keys": "$99gE", "initial": "one two three"},
    "gE_from_middle": {"keys": "WlgE", "initial": "one two.three rest"},

    # ══════════════════════════════════════
    # Mixed / cross-motion tests
    # ══════════════════════════════════════
    "w_then_b_returns": {"keys": "wb", "initial": "one two three"},
    "e_then_ge_returns": {"keys": "ege", "initial": "one two three"},
    "W_then_B_returns": {"keys": "WB", "initial": "one.two three.four"},
    "E_then_gE_returns": {"keys": "EgE", "initial": "one.two three.four"},
    "w_b_w_sequence": {"keys": "wbw", "initial": "one two three"},
    "w_e_interleave": {"keys": "wewe", "initial": "one two three four five"},
    "b_ge_sequence": {"keys": "$bgeb", "initial": "one two three four"},
    "forward_back_complex": {"keys": "wwbww", "initial": "aa bb cc dd ee ff"},
    "all_fwd_motions": {"keys": "wWeE", "initial": "foo.bar baz-qux next"},
    "all_bwd_motions": {"keys": "$bBgegE", "initial": "foo.bar baz-qux next"},
}
