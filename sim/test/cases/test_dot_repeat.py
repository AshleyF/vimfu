CASES = {
    # === Dot after x (delete char under cursor) ===
    "dot_after_x_deletes_another_char": {
        "keys": "x.",
        "initial": "abcdef",
    },
    "dot_after_x_three_times": {
        "keys": "x...",
        "initial": "abcdefgh",
    },
    "dot_after_x_at_end_of_line": {
        "keys": "$x.",
        "initial": "abcdef",
    },
    "dot_after_x_on_single_char_line": {
        "keys": "x.",
        "initial": "ab\ncd",
    },
    "dot_after_x_multiline": {
        "keys": "xj.",
        "initial": "abcdef\nghijkl",
    },

    # === Dot after dd (delete line) ===
    "dot_after_dd_deletes_another_line": {
        "keys": "dd.",
        "initial": "line one\nline two\nline three\nline four",
    },
    "dot_after_dd_three_lines": {
        "keys": "dd..",
        "initial": "aaa\nbbb\nccc\nddd\neee",
    },
    "dot_after_dd_until_one_line_left": {
        "keys": "dd..",
        "initial": "first\nsecond\nthird\nfourth",
    },

    # === Dot after dw (delete word) ===
    "dot_after_dw": {
        "keys": "dw.",
        "initial": "one two three four",
    },
    "dot_after_dw_three_times": {
        "keys": "dw..",
        "initial": "alpha beta gamma delta epsilon",
    },
    "dot_after_dw_at_line_start": {
        "keys": "dw.",
        "initial": "foo bar baz qux",
    },

    # === Dot after d$ (delete to end of line) ===
    "dot_after_d_dollar_next_line": {
        "keys": "d$j.",
        "initial": "hello world\nfoo bar baz\nkeep this",
    },
    "dot_after_d_dollar_from_middle": {
        "keys": "wd$j.",
        "initial": "aaa bbb ccc\nddd eee fff\nggg",
    },

    # === Dot after D (delete to end of line) ===
    "dot_after_D_next_line": {
        "keys": "Dj.",
        "initial": "hello world\nfoo bar baz\nstay",
    },
    "dot_after_D_from_middle": {
        "keys": "wDj.",
        "initial": "one two three\nfour five six\nseven",
    },

    # === Dot after de (delete to end of word) ===
    "dot_after_de": {
        "keys": "de.",
        "initial": "alpha beta gamma delta",
    },
    "dot_after_de_twice": {
        "keys": "de..",
        "initial": "aaa bbb ccc ddd eee",
    },

    # === Dot after db (delete to beginning of word) ===
    "dot_after_db": {
        "keys": "wwdb.",
        "initial": "one two three four five",
    },

    # === Dot after df{char} ===
    "dot_after_df_char": {
        "keys": "dfa.",
        "initial": "abcda fgh a xyz",
    },
    "dot_after_df_comma": {
        "keys": "df,.",
        "initial": "a,b,c,d,e",
    },

    # === Dot after dt{char} ===
    "dot_after_dt_char": {
        "keys": "dta.",
        "initial": "xxxa yyyazzz",
    },
    "dot_after_dt_space": {
        "keys": "dt .",
        "initial": "hello world foo bar",
    },

    # === Dot after cw + text + Escape ===
    "dot_after_cw_text": {
        "keys": "cwNEW\x1bw.",
        "initial": "old old old old",
    },
    "dot_after_cw_text_three_times": {
        "keys": "cwX\x1bw.w.",
        "initial": "aaa bbb ccc ddd eee",
    },
    "dot_after_cw_longer_text": {
        "keys": "cwHELLO\x1bw.",
        "initial": "hi hi hi",
    },
    "dot_after_cw_shorter_text": {
        "keys": "cwx\x1bw.",
        "initial": "longword longword longword",
    },

    # === Dot after cc + text + Escape ===
    "dot_after_cc_text": {
        "keys": "ccnew line\x1bj.",
        "initial": "old line one\nold line two\nold line three",
    },
    "dot_after_cc_empty": {
        "keys": "cc\x1bj.",
        "initial": "aaa\nbbb\nccc",
    },

    # === Dot after C + text + Escape ===
    "dot_after_C_text": {
        "keys": "wCend\x1bj.",
        "initial": "start middle\nstart middle\nkeep",
    },
    "dot_after_C_from_beginning": {
        "keys": "Creplaced\x1bj.",
        "initial": "first line\nsecond line\nthird",
    },

    # === Dot after s + text + Escape ===
    "dot_after_s_text": {
        "keys": "sX\x1bl.",
        "initial": "abcdef",
    },
    "dot_after_s_multichar_insert": {
        "keys": "s[]\x1bl.",
        "initial": "abcdef",
    },

    # === Dot after S + text + Escape ===
    "dot_after_S_text": {
        "keys": "Snew\x1bj.",
        "initial": "old one\nold two\nold three",
    },

    # === Dot after r{char} ===
    "dot_after_r_char": {
        "keys": "rXl.",
        "initial": "abcdef",
    },
    "dot_after_r_char_multiline": {
        "keys": "rZjl.",
        "initial": "abcdef\nghijkl",
    },
    "dot_after_r_char_three_times": {
        "keys": "r_l.l.",
        "initial": "abcdef",
    },

    # === Dot after ~ (toggle case) ===
    "dot_after_tilde": {
        "keys": "~.",
        "initial": "abcdef",
    },
    "dot_after_tilde_three_times": {
        "keys": "~..",
        "initial": "abcdef",
    },
    "dot_after_tilde_uppercase": {
        "keys": "~.",
        "initial": "ABCDEF",
    },

    # === Dot after >> (indent) ===
    "dot_after_indent": {
        "keys": ">>j.",
        "initial": "line one\nline two\nline three",
    },
    "dot_after_indent_twice": {
        "keys": ">>j.j.",
        "initial": "aaa\nbbb\nccc\nddd",
    },
    "dot_after_double_indent": {
        "keys": ">>>>.",
        "initial": "hello\nworld",
    },

    # === Dot after << (dedent) ===
    "dot_after_dedent": {
        "keys": "<<j.",
        "initial": "\t\tline one\n\t\tline two\n\t\tline three",
    },
    "dot_after_dedent_on_unindented": {
        "keys": "<<j.",
        "initial": "no indent\n\tsome indent\nno indent",
    },

    # === Dot after J (join lines) ===
    "dot_after_J": {
        "keys": "J.",
        "initial": "aaa\nbbb\nccc\nddd",
    },
    "dot_after_J_three_times": {
        "keys": "J..",
        "initial": "one\ntwo\nthree\nfour\nfive",
    },

    # === Dot after i + text + Escape ===
    "dot_after_i_text": {
        "keys": "iHI \x1b.",
        "initial": "world",
    },
    "dot_after_i_text_multiline": {
        "keys": "iINS\x1bj.",
        "initial": "aaa\nbbb",
    },

    # === Dot after a + text + Escape ===
    "dot_after_a_text": {
        "keys": "aXX\x1b.",
        "initial": "abcdef",
    },
    "dot_after_a_text_at_end": {
        "keys": "$a!\x1b.",
        "initial": "hello",
    },

    # === Dot after o + text + Escape ===
    "dot_after_o_text": {
        "keys": "onew\x1b.",
        "initial": "first\nlast",
    },
    "dot_after_o_text_at_bottom": {
        "keys": "Goend\x1b.",
        "initial": "top\nmiddle",
    },

    # === Dot after O + text + Escape ===
    "dot_after_O_text": {
        "keys": "Oabove\x1b.",
        "initial": "below\nmore below",
    },
    "dot_after_O_on_last_line": {
        "keys": "GOinserted\x1b.",
        "initial": "first\nsecond\nthird",
    },

    # === Dot after I + text + Escape ===
    "dot_after_I_text": {
        "keys": "I>> \x1bj.",
        "initial": "hello\nworld\nfoo",
    },
    "dot_after_I_text_indented": {
        "keys": "I# \x1bj.",
        "initial": "\tfoo\n\tbar\n\tbaz",
    },

    # === Dot after A + text + Escape ===
    "dot_after_A_text": {
        "keys": "A!\x1bj.",
        "initial": "hello\nworld\nfoo",
    },
    "dot_after_A_text_multi": {
        "keys": "A;;\x1bj.j.",
        "initial": "aaa\nbbb\nccc\nddd",
    },

    # === Dot after p (put/paste) ===
    "dot_after_p": {
        "keys": "yywp.",
        "initial": "word rest of line",
    },
    "dot_after_p_line": {
        "keys": "ddp.",
        "initial": "first\nsecond\nthird\nfourth",
    },
    "dot_after_p_char": {
        "keys": "xlp.",
        "initial": "abcdef",
    },

    # === Dot after P (put before) ===
    "dot_after_P": {
        "keys": "ywP.",
        "initial": "hello world",
    },
    "dot_after_P_line": {
        "keys": "ddP.",
        "initial": "aaa\nbbb\nccc",
    },

    # === Dot with count (count replaces original) ===
    "dot_with_count_replaces_dd": {
        "keys": "2dd3.",
        "initial": "L1\nL2\nL3\nL4\nL5\nL6\nL7\nL8",
    },
    "dot_with_count_replaces_x": {
        "keys": "2x3.",
        "initial": "abcdefghij",
    },
    "dot_with_count_replaces_dw": {
        "keys": "dw2.",
        "initial": "aa bb cc dd ee ff gg",
    },
    "dot_with_count_3_after_x": {
        "keys": "x3.",
        "initial": "abcdefgh",
    },

    # === Multiple dots in sequence ===
    "multiple_dots_x_four": {
        "keys": "x...",
        "initial": "abcdefgh",
    },
    "multiple_dots_dd_three": {
        "keys": "dd..",
        "initial": "L1\nL2\nL3\nL4\nL5",
    },
    "multiple_dots_dw": {
        "keys": "dw..",
        "initial": "one two three four five",
    },

    # === Dot after undo ===
    "dot_after_undo_redo_change": {
        "keys": "x\x1bu.",
        "initial": "abcdef",
    },
    "dot_after_undo_dd": {
        "keys": "ddu.",
        "initial": "aaa\nbbb\nccc",
    },
    "dot_after_undo_cw": {
        "keys": "cwNEW\x1bu.",
        "initial": "old word here",
    },

    # === Dot does NOT repeat motions or yanks ===
    "dot_does_not_repeat_yank_yy": {
        "keys": "yy.p",
        "initial": "line one\nline two",
    },
    "dot_does_not_repeat_yank_yw": {
        "keys": "yw.P",
        "initial": "hello world",
    },

    # === Dot after visual mode operation ===
    "dot_after_visual_delete_word": {
        "keys": "vwd.",
        "initial": "alpha beta gamma delta",
    },
    "dot_after_visual_delete_chars": {
        "keys": "vlld.",
        "initial": "abcdefghijkl",
    },
    "dot_after_visual_line_delete": {
        "keys": "Vd.",
        "initial": "one\ntwo\nthree\nfour\nfive",
    },
    "dot_after_visual_case_toggle": {
        "keys": "vll~w.",
        "initial": "abcdef ghijkl",
    },

    # === Dot after count change ===
    "dot_after_3x": {
        "keys": "3x.",
        "initial": "abcdefghijkl",
    },
    "dot_after_2dd": {
        "keys": "2dd.",
        "initial": "L1\nL2\nL3\nL4\nL5\nL6",
    },
    "dot_after_2dw": {
        "keys": "2dw.",
        "initial": "aa bb cc dd ee ff",
    },
    "dot_after_3s_text": {
        "keys": "3sXYZ\x1b.",
        "initial": "abcdefghijkl",
    },

    # === Moving between dots ===
    "move_between_dots_dw_w": {
        "keys": "dww.w.",
        "initial": "a1 a2 a3 a4 a5 a6 a7",
    },
    "move_between_dots_x_l": {
        "keys": "xl.l.",
        "initial": "abcdefghij",
    },
    "move_between_dots_dd_j_skipping": {
        "keys": "ddj.j.",
        "initial": "L1\nL2\nL3\nL4\nL5\nL6\nL7",
    },

    # === Additional edge cases ===
    "dot_on_empty_buffer": {
        "keys": "dd.",
        "initial": "only\nline",
    },
    "dot_after_rx_at_eol": {
        "keys": "$rZ0.",
        "initial": "abcdef",
    },
    "dot_repeat_cw_different_word_length": {
        "keys": "cwXX\x1bw.",
        "initial": "short longerword end",
    },
    "dot_after_indent_multiple_lines": {
        "keys": ">>j.j.",
        "initial": "aaa\nbbb\nccc\nddd",
    },
    "dot_after_J_trailing_spaces": {
        "keys": "J.",
        "initial": "hello\nworld\nfoo",
    },
    "dot_after_delete_last_char": {
        "keys": "$x.",
        "initial": "abcd",
    },
    "dot_after_dw_at_eol": {
        "keys": "$dw.",
        "initial": "hello world\nfoo bar",
    },
    "dot_after_cc_indent_preserved": {
        "keys": "ccnew\x1bj.",
        "initial": "\told one\n\told two\n\told three",
    },
    "dot_after_S_indent_preserved": {
        "keys": "Snew\x1bj.",
        "initial": "\told one\n\told two\n\told three",
    },
    "dot_after_c_dollar_text": {
        "keys": "wC!!!\x1bj.",
        "initial": "keep this\nkeep that\nkeep more",
    },
    "dot_after_2cc_text": {
        "keys": "2cctwoline\x1b.",
        "initial": "L1\nL2\nL3\nL4\nL5\nL6",
    },
    "dot_after_d_iw": {
        "keys": "wdiw.",
        "initial": "aaa bbb ccc ddd",
    },
}
