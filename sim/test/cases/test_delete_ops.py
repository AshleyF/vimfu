"""Delete operator tests: d{motion}, dd, x, X, s, S, D, C with counts,
edge cases, empty lines, multi-line content, cursor positioning."""

CASES = {
    # ── dw (delete word forward) ──
    "dw_basic": {"keys": "dw", "initial": "one two three"},
    "dw_mid_line": {"keys": "wdw", "initial": "one two three"},
    "dw_last_word": {"keys": "wwdw", "initial": "one two three"},
    "dw_from_mid_word": {"keys": "lldw", "initial": "hello world"},
    "dw_single_word": {"keys": "dw", "initial": "hello"},
    "dw_with_punct": {"keys": "dw", "initial": "hello.world foo"},
    "dw_at_eol": {"keys": "$dw", "initial": "hello world"},
    "dw_across_line": {"keys": "wwdw", "initial": "one two\nthree four"},
    "dw_on_empty_line": {"keys": "dw", "initial": "\nhello"},
    "dw_count_2": {"keys": "d2w", "initial": "one two three four"},
    "dw_count_exceeds": {"keys": "d99w", "initial": "one two three"},

    # ── dW (delete WORD forward) ──
    "dW_basic": {"keys": "dW", "initial": "one two three"},
    "dW_with_punct": {"keys": "dW", "initial": "hello.world foo bar"},
    "dW_from_mid": {"keys": "lldW", "initial": "hello.world foo"},
    "dW_count_2": {"keys": "d2W", "initial": "a.b c.d e.f g.h"},

    # ── db (delete word backward) ──
    "db_basic": {"keys": "wdb", "initial": "one two three"},
    "db_from_mid_word": {"keys": "lldb", "initial": "hello world"},
    "db_at_col0": {"keys": "db", "initial": "hello world"},
    "db_count_2": {"keys": "wwd2b", "initial": "one two three four"},
    "db_across_line": {"keys": "jdb", "initial": "hello\nworld"},

    # ── dB (delete WORD backward) ──
    "dB_basic": {"keys": "wdB", "initial": "one two three"},
    "dB_with_punct": {"keys": "wdB", "initial": "one.two three"},
    "dB_count_2": {"keys": "wwd2B", "initial": "a.b c.d e.f g.h"},

    # ── de (delete to end of word, inclusive) ──
    "de_basic": {"keys": "de", "initial": "one two three"},
    "de_from_mid_word": {"keys": "llde", "initial": "hello world"},
    "de_single_word": {"keys": "de", "initial": "hello"},
    "de_with_punct": {"keys": "de", "initial": "hello.world foo"},
    "de_count_2": {"keys": "d2e", "initial": "one two three four"},

    # ── dE (delete to end of WORD, inclusive) ──
    "dE_basic": {"keys": "dE", "initial": "one two three"},
    "dE_with_punct": {"keys": "dE", "initial": "hello.world foo"},
    "dE_count_2": {"keys": "d2E", "initial": "a.b c.d e.f g.h"},

    # ── dge (delete backward to end of prev word) ──
    "dge_basic": {"keys": "wdge", "initial": "one two three"},
    "dge_at_col0": {"keys": "dge", "initial": "hello"},
    "dge_across_line": {"keys": "jdge", "initial": "hello\nworld"},

    # ── d$ (delete to end of line) ──
    "d_dollar_basic": {"keys": "d$", "initial": "hello world"},
    "d_dollar_from_mid": {"keys": "lld$", "initial": "hello world"},
    "d_dollar_multiline": {"keys": "d$", "initial": "first line\nsecond line"},
    "d_dollar_empty_line": {"keys": "jd$", "initial": "hello\n\nworld"},

    # ── d0 (delete to start of line) ──
    "d0_from_mid": {"keys": "lllld0", "initial": "hello world"},
    "d0_at_col0": {"keys": "d0", "initial": "hello world"},
    "d0_second_line": {"keys": "jlld0", "initial": "first\nsecond line\nthird"},

    # ── d^ (delete to first non-blank) ──
    "d_caret_indented": {"keys": "8ld^", "initial": "    hello world"},
    "d_caret_deep": {"keys": "wwd^", "initial": "    one two three"},
    "d_caret_no_indent": {"keys": "lld^", "initial": "hello world"},

    # ── dG (delete to end of file) ──
    "dG_from_first": {"keys": "dG", "initial": "one\ntwo\nthree\nfour"},
    "dG_from_mid": {"keys": "jdG", "initial": "one\ntwo\nthree\nfour"},
    "dG_single_line": {"keys": "dG", "initial": "hello"},

    # ── dgg (delete to start of file) ──
    "dgg_from_last": {"keys": "Gdgg", "initial": "one\ntwo\nthree\nfour"},
    "dgg_from_mid": {"keys": "jjdgg", "initial": "one\ntwo\nthree\nfour"},
    "dgg_from_first": {"keys": "dgg", "initial": "one\ntwo\nthree"},

    # ── dj (delete current + line below, linewise) ──
    "dj_basic": {"keys": "dj", "initial": "one\ntwo\nthree"},
    "dj_from_mid": {"keys": "jdj", "initial": "one\ntwo\nthree\nfour"},
    "dj_two_lines": {"keys": "dj", "initial": "one\ntwo"},
    "dj_count_2": {"keys": "d2j", "initial": "aa\nbb\ncc\ndd\nee"},

    # ── dk (delete current + line above, linewise) ──
    "dk_basic": {"keys": "jdk", "initial": "one\ntwo\nthree"},
    "dk_from_last": {"keys": "Gdk", "initial": "one\ntwo\nthree"},
    "dk_count_2": {"keys": "Gd2k", "initial": "aa\nbb\ncc\ndd\nee"},
    "dk_on_first": {"keys": "dk", "initial": "one\ntwo\nthree"},

    # ── df{char} (delete through found char, inclusive) ──
    "df_basic": {"keys": "dfo", "initial": "hello world foo"},
    "df_first_match": {"keys": "dfl", "initial": "hello world"},
    "df_space": {"keys": "df ", "initial": "hello world foo"},
    "df_no_match": {"keys": "dfz", "initial": "hello world"},
    "df_count_2": {"keys": "d2fo", "initial": "one two foo boo"},

    # ── dt{char} (delete till found char, exclusive) ──
    "dt_basic": {"keys": "dto", "initial": "hello world foo"},
    "dt_space": {"keys": "dt ", "initial": "hello world foo"},
    "dt_no_match": {"keys": "dtz", "initial": "hello world"},
    "dt_adjacent": {"keys": "dth", "initial": "ahelp"},
    "dt_count_2": {"keys": "d2to", "initial": "one two foo boo"},

    # ── dF{char} (delete backward through found char) ──
    "dF_basic": {"keys": "$dFw", "initial": "hello world"},
    "dF_no_match": {"keys": "$dFz", "initial": "hello world"},
    "dF_space": {"keys": "$dF ", "initial": "hello world foo"},

    # ── dT{char} (delete backward till found char) ──
    "dT_basic": {"keys": "$dTw", "initial": "hello world"},
    "dT_no_match": {"keys": "$dTz", "initial": "hello world"},
    "dT_space": {"keys": "$dT ", "initial": "hello world foo"},

    # ── d} (delete to next paragraph) ──
    "d_rbrace_basic": {"keys": "d}", "initial": "one\ntwo\n\nthree\nfour"},
    "d_rbrace_at_blank": {"keys": "jjd}", "initial": "one\ntwo\n\nthree\nfour"},
    "d_rbrace_last_para": {"keys": "3jd}", "initial": "one\n\nthree\nfour\nfive"},
    "d_rbrace_single": {"keys": "d}", "initial": "hello"},

    # ── d{ (delete to previous paragraph) ──
    "d_lbrace_basic": {"keys": "Gd{", "initial": "one\ntwo\n\nthree\nfour"},
    "d_lbrace_from_mid": {"keys": "jjjd{", "initial": "one\ntwo\n\nthree\nfour"},
    "d_lbrace_at_start": {"keys": "d{", "initial": "hello\nworld"},

    # ── dd (delete line) ──
    "dd_first_line": {"keys": "dd", "initial": "first\nsecond\nthird"},
    "dd_middle_line": {"keys": "jdd", "initial": "first\nsecond\nthird"},
    "dd_last_line": {"keys": "Gdd", "initial": "first\nsecond\nthird"},
    "dd_single_line": {"keys": "dd", "initial": "only line"},
    "dd_empty_buffer": {"keys": "dd", "initial": ""},
    "dd_two_lines_first": {"keys": "dd", "initial": "first\nsecond"},
    "dd_keeps_rest": {"keys": "dd", "initial": "delete me\nkeep one\nkeep two"},
    "dd_on_empty_line": {"keys": "jdd", "initial": "hello\n\nworld"},
    "dd_indented": {"keys": "jdd", "initial": "top\n    indented\nbottom"},
    "dd_last_moves_up": {"keys": "Gdd", "initial": "aaa\nbbb\nccc"},

    # ── {count}dd (delete multiple lines) ──
    "dd_count_2": {"keys": "2dd", "initial": "one\ntwo\nthree\nfour"},
    "dd_count_3": {"keys": "3dd", "initial": "one\ntwo\nthree\nfour\nfive"},
    "dd_count_exceeds": {"keys": "99dd", "initial": "one\ntwo\nthree"},
    "dd_count_exact": {"keys": "3dd", "initial": "one\ntwo\nthree"},
    "dd_count_from_last": {"keys": "G5dd", "initial": "one\ntwo\nthree\nfour"},

    # ── x (delete char under cursor) ──
    "x_basic": {"keys": "x", "initial": "hello"},
    "x_at_mid": {"keys": "llx", "initial": "abcdef"},
    "x_at_eol": {"keys": "$x", "initial": "abcdef"},
    "x_single_char": {"keys": "x", "initial": "a"},
    "x_empty_line": {"keys": "x", "initial": ""},
    "x_multiline_mid": {"keys": "jx", "initial": "abc\ndef\nghi"},
    "x_two_char_at_end": {"keys": "$x", "initial": "ab"},

    # ── {count}x (delete multiple chars) ──
    "x_count_2": {"keys": "2x", "initial": "abcdef"},
    "x_count_3": {"keys": "3x", "initial": "abcdef"},
    "x_count_exceeds": {"keys": "99x", "initial": "abcdef"},
    "x_count_3_from_mid": {"keys": "ll3x", "initial": "abcdef"},

    # ── X (delete char before cursor) ──
    "X_basic": {"keys": "lX", "initial": "abcdef"},
    "X_at_col0": {"keys": "X", "initial": "hello"},
    "X_at_eol": {"keys": "$X", "initial": "abcdef"},
    "X_empty_line": {"keys": "X", "initial": ""},
    "X_count_2": {"keys": "lll2X", "initial": "abcdef"},
    "X_count_exceeds": {"keys": "ll99X", "initial": "abcdef"},

    # ── s (substitute char: delete + insert) ──
    "s_basic": {"keys": "sX\x1b", "initial": "hello"},
    "s_at_mid": {"keys": "llsZ\x1b", "initial": "abcdef"},
    "s_at_eol": {"keys": "$sZ\x1b", "initial": "abcdef"},
    "s_single_char": {"keys": "sX\x1b", "initial": "a"},
    "s_count_2": {"keys": "2sXY\x1b", "initial": "abcdef"},
    "s_count_exceeds": {"keys": "99sX\x1b", "initial": "abc"},
    "s_on_multiline": {"keys": "jsX\x1b", "initial": "abc\ndef\nghi"},
    "s_type_multi": {"keys": "sHELLO\x1b", "initial": "xworld"},

    # ── S (substitute line: clear + insert) ──
    "S_basic": {"keys": "SNew\x1b", "initial": "old text"},
    "S_mid_line": {"keys": "jSNew\x1b", "initial": "first\nsecond\nthird"},
    "S_last_line": {"keys": "GSNew\x1b", "initial": "first\nsecond\nthird"},
    "S_single_line": {"keys": "SXYZ\x1b", "initial": "hello"},
    "S_empty_line": {"keys": "jSNew\x1b", "initial": "above\n\nbelow"},
    "S_indented": {"keys": "jSNew\x1b", "initial": "top\n    indented\nbottom"},
    "S_count_2": {"keys": "2SNew\x1b", "initial": "one\ntwo\nthree\nfour"},
    "S_type_nothing": {"keys": "S\x1b", "initial": "hello world"},

    # ── D (delete to end of line) ──
    "D_basic": {"keys": "D", "initial": "hello world"},
    "D_from_mid": {"keys": "llD", "initial": "hello world"},
    "D_at_eol": {"keys": "$D", "initial": "hello world"},
    "D_single_char": {"keys": "D", "initial": "x"},
    "D_multiline_mid": {"keys": "jllD", "initial": "first\nsecond line\nthird"},
    "D_empty_line": {"keys": "jD", "initial": "hello\n\nworld"},

    # ── C (change to end of line: delete + insert) ──
    "C_basic": {"keys": "CNew\x1b", "initial": "hello world"},
    "C_from_mid": {"keys": "llCXY\x1b", "initial": "hello world"},
    "C_at_eol": {"keys": "$CX\x1b", "initial": "hello world"},
    "C_single_char": {"keys": "CZ\x1b", "initial": "x"},
    "C_multiline_mid": {"keys": "jCNew\x1b", "initial": "first\nsecond\nthird"},
    "C_empty_line": {"keys": "jCNew\x1b", "initial": "hello\n\nworld"},
    "C_type_nothing": {"keys": "C\x1b", "initial": "hello world"},
    "C_indented": {"keys": "jllCnew\x1b", "initial": "top\n    old text\nbottom"},

    # ── d{count}{motion} combos ──
    "d3j_combo": {"keys": "d3j", "initial": "aa\nbb\ncc\ndd\nee\nff"},
    "d2j_mid": {"keys": "jd2j", "initial": "aa\nbb\ncc\ndd\nee\nff"},
    "d2k_combo": {"keys": "Gd2k", "initial": "aa\nbb\ncc\ndd\nee"},
    "d4l_combo": {"keys": "d4l", "initial": "abcdefgh"},
    "d3h_combo": {"keys": "$d3h", "initial": "abcdefgh"},
    "d2w_mid": {"keys": "wd2w", "initial": "one two three four five"},

    # ── Edge: cursor position after deletes ──
    "edge_dd_cursor_next": {"keys": "jdd", "initial": "aaa\nbbb\nccc\nddd"},
    "edge_x_eol_left": {"keys": "$x", "initial": "abcd"},
    "edge_d_dollar_back": {"keys": "lld$", "initial": "abcdef"},
    "edge_x_single_char": {"keys": "jx", "initial": "abc\nx\nefg"},
    "edge_dd_char_line": {"keys": "jdd", "initial": "abc\nx\nefg"},
    "edge_dw_one_char": {"keys": "dw", "initial": "a b c d"},
    "edge_de_one_char": {"keys": "de", "initial": "a b c d"},
}
