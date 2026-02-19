CASES = {
    # === ~ (tilde) toggle single char ===
    "tilde_lower_to_upper": {"keys": "~", "initial": "hello"},
    "tilde_upper_to_lower": {"keys": "~", "initial": "Hello"},
    "tilde_digit_no_change": {"keys": "~", "initial": "123"},
    "tilde_space_no_change": {"keys": "~", "initial": " hello"},
    "tilde_punctuation_no_change": {"keys": "~", "initial": "!abc"},
    "tilde_advances_cursor": {"keys": "~~", "initial": "abcd"},
    "tilde_three_chars": {"keys": "~~~", "initial": "Hello"},
    "tilde_end_of_line": {"keys": "$~", "initial": "abcde"},
    "tilde_on_empty_line": {"keys": "~", "initial": ""},
    "tilde_single_char_line": {"keys": "~", "initial": "a"},
    "tilde_at_eol_stays": {"keys": "$~", "initial": "ab"},
    "tilde_mixed_case": {"keys": "~~~~~", "initial": "HeLLo"},
    "tilde_middle_of_line": {"keys": "ll~", "initial": "abcde"},
    "tilde_all_upper": {"keys": "~~~~~", "initial": "ABCDE"},
    "tilde_all_lower": {"keys": "~~~~~", "initial": "abcde"},
    "tilde_multiline_first": {"keys": "~", "initial": "abc\ndef"},
    "tilde_does_not_cross_line": {"keys": "$~~", "initial": "ab\ncd"},

    # === ~ with count ===
    "tilde_count_3": {"keys": "3~", "initial": "hello world"},
    "tilde_count_5": {"keys": "5~", "initial": "Hello World"},
    "tilde_count_exceeds_line": {"keys": "10~", "initial": "abc"},
    "tilde_count_1": {"keys": "1~", "initial": "xyz"},
    "tilde_count_on_spaces": {"keys": "5~", "initial": "a b c"},
    "tilde_count_at_mid": {"keys": "ll3~", "initial": "abcdef"},
    "tilde_count_whole_line": {"keys": "6~", "initial": "FoObAr"},

    # === g~ (toggle case over motion) ===
    "g_tilde_w": {"keys": "g~w", "initial": "hello world"},
    "g_tilde_e": {"keys": "g~e", "initial": "hello world"},
    "g_tilde_dollar": {"keys": "g~$", "initial": "Hello World"},
    "g_tilde_0": {"keys": "llg~0", "initial": "Hello"},
    "g_tilde_W": {"keys": "g~W", "initial": "hello-world foo"},
    "g_tilde_b": {"keys": "wg~b", "initial": "hello world"},
    "g_tilde_iw": {"keys": "g~iw", "initial": "hello world"},
    "g_tilde_aw": {"keys": "g~aw", "initial": "hello world"},
    "g_tilde_j_linewise": {"keys": "g~j", "initial": "Hello\nWorld\nFoo"},
    "g_tilde_k_linewise": {"keys": "jg~k", "initial": "Hello\nWorld\nFoo"},
    "g_tilde_2w": {"keys": "g~2w", "initial": "aaa bbb ccc"},
    "g_tilde_dollar_mid": {"keys": "llg~$", "initial": "abcDEF"},
    "g_tilde_gg_from_bottom": {
        "keys": "Gg~gg",
        "initial": "aaa\nbbb\nccc"
    },
    "g_tilde_G_from_top": {
        "keys": "g~G",
        "initial": "AAA\nBBB\nCCC"
    },
    "g_tilde_iw_middle": {
        "keys": "wg~iw",
        "initial": "foo BAR baz"
    },
    "g_tilde_empty_line": {"keys": "g~$", "initial": ""},

    # === gu (lowercase over motion) ===
    "gu_w_basic": {"keys": "guw", "initial": "HELLO world"},
    "gu_e_basic": {"keys": "gue", "initial": "HELLO world"},
    "gu_dollar": {"keys": "gu$", "initial": "HELLO WORLD"},
    "gu_0": {"keys": "llgu0", "initial": "HELLO"},
    "gu_iw": {"keys": "guiw", "initial": "HELLO world"},
    "gu_aw": {"keys": "guaw", "initial": "HELLO world"},
    "gu_2w": {"keys": "gu2w", "initial": "AAA BBB CCC"},
    "gu_j_linewise": {"keys": "guj", "initial": "HELLO\nWORLD\nfoo"},
    "gu_k_linewise": {"keys": "jguk", "initial": "HELLO\nWORLD\nfoo"},
    "gu_G_to_end": {"keys": "guG", "initial": "AAA\nBBB\nCCC"},
    "gu_gg_from_end": {"keys": "Ggugg", "initial": "AAA\nBBB\nCCC"},
    "guu_whole_line": {"keys": "guu", "initial": "HELLO WORLD"},
    "guu_mixed": {"keys": "guu", "initial": "HeLLo WoRLd"},
    "guu_already_lower": {"keys": "guu", "initial": "hello"},
    "guu_second_line": {"keys": "jguu", "initial": "AAA\nBBB\nCCC"},
    "gu_dollar_mid": {"keys": "llgu$", "initial": "abCDEF"},
    "gu_iw_middle": {"keys": "wguiw", "initial": "foo BAR baz"},
    "gu_empty_line": {"keys": "gu$", "initial": ""},

    # === gU (uppercase over motion) ===
    "gU_w_basic": {"keys": "gUw", "initial": "hello world"},
    "gU_e_basic": {"keys": "gUe", "initial": "hello world"},
    "gU_dollar": {"keys": "gU$", "initial": "hello world"},
    "gU_0": {"keys": "llgU0", "initial": "hello"},
    "gU_iw": {"keys": "gUiw", "initial": "hello world"},
    "gU_aw": {"keys": "gUaw", "initial": "hello world"},
    "gU_2w": {"keys": "gU2w", "initial": "aaa bbb ccc"},
    "gU_j_linewise": {"keys": "gUj", "initial": "hello\nworld\nfoo"},
    "gU_k_linewise": {"keys": "jgUk", "initial": "hello\nworld\nfoo"},
    "gU_G_to_end": {"keys": "gUG", "initial": "aaa\nbbb\nccc"},
    "gU_gg_from_end": {"keys": "GgUgg", "initial": "aaa\nbbb\nccc"},
    "gUU_whole_line": {"keys": "gUU", "initial": "hello world"},
    "gUU_mixed": {"keys": "gUU", "initial": "HeLLo WoRLd"},
    "gUU_already_upper": {"keys": "gUU", "initial": "HELLO"},
    "gUU_second_line": {"keys": "jgUU", "initial": "aaa\nbbb\nccc"},
    "gU_dollar_mid": {"keys": "llgU$", "initial": "ABcdef"},
    "gU_iw_middle": {"keys": "wgUiw", "initial": "FOO bar BAZ"},
    "gU_empty_line": {"keys": "gU$", "initial": ""},

    # === Visual mode case operations (small sample) ===
    "visual_tilde_word": {
        "keys": "ve~",
        "initial": "hello"
    },
    "visual_u_lowercase": {
        "keys": "veu",
        "initial": "HELLO"
    },
    "visual_U_uppercase": {
        "keys": "veU",
        "initial": "hello"
    },
    "visual_tilde_selection": {
        "keys": "wve~",
        "initial": "aaa BBB ccc"
    },
    "visual_u_partial": {
        "keys": "llv$u",
        "initial": "ABCDEF"
    },
    "visual_U_partial": {
        "keys": "llv$U",
        "initial": "abcdef"
    },
    "visual_line_tilde": {
        "keys": "V~",
        "initial": "Hello World"
    },
    "visual_line_u": {
        "keys": "Vu",
        "initial": "HELLO WORLD"
    },
    "visual_line_U": {
        "keys": "VU",
        "initial": "hello world"
    },
}
