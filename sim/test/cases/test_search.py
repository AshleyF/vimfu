CASES = {
    # === Basic forward search ===
    "search_forward_basic": {
        "keys": "/world\r",
        "initial": "hello world",
    },
    "search_forward_second_word": {
        "keys": "/bar\r",
        "initial": "foo bar baz",
    },
    "search_forward_next_line": {
        "keys": "/two\r",
        "initial": "line one\nline two\nline three",
    },
    "search_forward_third_line": {
        "keys": "/three\r",
        "initial": "one\ntwo\nthree\nfour",
    },
    "search_forward_from_middle": {
        "keys": "j/four\r",
        "initial": "one\ntwo\nthree\nfour\nfive",
    },

    # === Search wraps around ===
    "search_wraps_to_top": {
        "keys": "G/one\r",
        "initial": "one\ntwo\nthree\nfour",
    },
    "search_wraps_from_last_line": {
        "keys": "G/first\r",
        "initial": "first\nsecond\nthird",
    },
    "search_wraps_past_match_behind": {
        "keys": "jj/aaa\r",
        "initial": "aaa\nbbb\nccc\nddd",
    },

    # === Search backward ===
    "search_backward_basic": {
        "keys": "$?hello\r",
        "initial": "hello world",
    },
    "search_backward_prev_line": {
        "keys": "j?one\r",
        "initial": "line one\nline two\nline three",
    },
    "search_backward_from_bottom": {
        "keys": "G?first\r",
        "initial": "first\nsecond\nthird\nfourth",
    },
    "search_backward_wraps_to_bottom": {
        "keys": "?four\r",
        "initial": "one\ntwo\nthree\nfour",
    },
    "search_backward_same_line": {
        "keys": "$?hel\r",
        "initial": "hello world",
    },

    # === Search not found ===
    "search_not_found_no_move": {
        "keys": "/zzzzz\r",
        "initial": "hello world\nfoo bar",
    },
    "search_backward_not_found": {
        "keys": "?zzzzz\r",
        "initial": "hello world\nfoo bar",
    },

    # === n to find next occurrence ===
    "n_finds_next": {
        "keys": "/the\rn",
        "initial": "the cat and the dog and the end",
    },
    "n_finds_next_line": {
        "keys": "/line\rn",
        "initial": "line one\nline two\nline three",
    },
    "n_wraps_around": {
        "keys": "/aa\rnn",
        "initial": "aa bb\ncc aa",
    },
    "n_multiple_times": {
        "keys": "/x\rnnn",
        "initial": "x a x b x c x d",
    },
    "n_after_backward_search": {
        "keys": "G?line\rn",
        "initial": "line one\nline two\nline three\nend",
    },

    # === N to find previous occurrence ===
    "N_finds_previous": {
        "keys": "/the\rnN",
        "initial": "the cat and the dog and the end",
    },
    "N_reverses_forward_search": {
        "keys": "/bb\rN",
        "initial": "aa bb cc bb dd bb",
    },
    "N_after_backward_search_goes_fwd": {
        "keys": "G?line\rN",
        "initial": "line one\nline two\nline three\nend",
    },
    "N_wraps_around": {
        "keys": "/aa\rN",
        "initial": "aa bb\ncc aa\ndd aa",
    },

    # === * (search word under cursor forward) ===
    "star_basic": {
        "keys": "*",
        "initial": "hello world hello end",
    },
    "star_next_line": {
        "keys": "*",
        "initial": "foo bar\nbaz foo\nqux",
    },
    "star_wraps_around": {
        "keys": "j*",
        "initial": "cat dog\ncat bird",
    },
    "star_whole_word": {
        "keys": "*",
        "initial": "the other then the end",
    },
    "star_on_second_word": {
        "keys": "w*",
        "initial": "aaa bbb ccc bbb ddd",
    },
    "star_cursor_in_middle_of_word": {
        "keys": "ll*",
        "initial": "hello world hello end",
    },
    "star_single_occurrence": {
        "keys": "*",
        "initial": "unique word here",
    },

    # === # (search word under cursor backward) ===
    "hash_basic": {
        "keys": "$b#",
        "initial": "hello world hello end",
    },
    "hash_prev_line": {
        "keys": "G#",
        "initial": "foo bar\nbaz\nfoo end",
    },
    "hash_wraps_around": {
        "keys": "#",
        "initial": "cat dog\nbird cat",
    },
    "hash_whole_word": {
        "keys": "G$b#",
        "initial": "the other then the end",
    },
    "hash_cursor_mid_word": {
        "keys": "Gll#",
        "initial": "foo bar\nfoo end",
    },

    # === Multiple occurrences with n ===
    "search_n_three_occurrences": {
        "keys": "/ab\rnn",
        "initial": "ab cd ab ef ab gh",
    },
    "search_n_across_lines": {
        "keys": "/x\rnn",
        "initial": "x one\ntwo x\nthree\nx four",
    },
    "search_n_wrap_full_cycle": {
        "keys": "/only\rn",
        "initial": "only match here",
    },

    # === Search for single character ===
    "search_single_char": {
        "keys": "/z\r",
        "initial": "abc xyz def",
    },
    "search_single_char_next": {
        "keys": "/a\rn",
        "initial": "a b c a d a",
    },

    # === Search across lines ===
    "search_lands_on_next_line": {
        "keys": "/target\r",
        "initial": "no match here\ntarget is here\nend",
    },
    "search_skips_lines": {
        "keys": "/end\r",
        "initial": "start\nmiddle\nmiddle\nend",
    },

    # === Search then n then N (direction switch) ===
    "search_n_then_N_direction": {
        "keys": "/aa\rnN",
        "initial": "aa bb aa cc aa dd",
    },
    "search_backward_n_then_N": {
        "keys": "G?aa\rnN",
        "initial": "aa bb\naa cc\naa dd\nend",
    },

    # === * on different words ===
    "star_on_short_word": {
        "keys": "*",
        "initial": "ab cd ab ef ab",
    },
    "star_on_long_word": {
        "keys": "*",
        "initial": "alpha beta alpha gamma",
    },

    # === # on different words ===
    "hash_on_short_word": {
        "keys": "G#",
        "initial": "xy end\nmore xy",
    },
    "hash_on_first_word": {
        "keys": "G$b#",
        "initial": "cat dog\nbird cat",
    },

    # === Cursor position after search ===
    "cursor_at_start_of_match": {
        "keys": "/world\r",
        "initial": "hello world",
    },
    "cursor_at_start_of_match_n": {
        "keys": "/bb\rn",
        "initial": "aa bb cc bb dd",
    },
    "cursor_after_star": {
        "keys": "*",
        "initial": "word other word end",
    },

    # === Search from middle of file ===
    "search_from_middle_forward": {
        "keys": "jj/end\r",
        "initial": "start\none\ntwo\nthree\nend",
    },
    "search_from_middle_backward": {
        "keys": "jj?start\r",
        "initial": "start\none\ntwo\nthree\nend",
    },

    # === Search in single-line buffer ===
    "search_in_single_line": {
        "keys": "/world\r",
        "initial": "hello world foo",
    },
    "search_single_line_not_found": {
        "keys": "/zzz\r",
        "initial": "hello world",
    },
    "star_in_single_line": {
        "keys": "*",
        "initial": "foo bar foo baz foo",
    },
    "n_in_single_line": {
        "keys": "/oo\rnn",
        "initial": "foo boo moo zoo",
    },

    # === Edge cases ===
    "search_first_char_of_line": {
        "keys": "j/a\r",
        "initial": "bbb\naaa\nccc",
    },
    "search_last_word_on_line": {
        "keys": "/end\r",
        "initial": "start middle end",
    },
    "star_with_n": {
        "keys": "*n",
        "initial": "foo bar\nbaz foo\nqux foo\nend",
    },
    "hash_with_n": {
        "keys": "G$b#n",
        "initial": "dog cat\ndog bird\ndog end",
    },
}
