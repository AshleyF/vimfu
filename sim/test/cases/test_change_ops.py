"""Change operator tests: c{motion}, cc, C, s, S, r, R with counts,
edge cases, empty lines, multi-line content, cursor positioning.
Change ops delete text AND enter insert mode; tests type replacement
text then \x1b to return to normal mode."""

CASES = {
    # ── cw (change word – acts like ce, does NOT include trailing space!) ──
    "cw_basic": {"keys": "cwNEW\x1b", "initial": "one two three"},
    "cw_mid_line": {"keys": "wcwNEW\x1b", "initial": "one two three"},
    "cw_last_word": {"keys": "wwcwNEW\x1b", "initial": "one two three"},
    "cw_from_mid_word": {"keys": "llcwNEW\x1b", "initial": "hello world"},
    "cw_single_word": {"keys": "cwNEW\x1b", "initial": "hello"},
    "cw_with_punct": {"keys": "cwNEW\x1b", "initial": "hello.world foo"},
    "cw_at_eol": {"keys": "$cwX\x1b", "initial": "hello world"},
    "cw_preserves_space": {"keys": "cwX\x1b", "initial": "one two three"},
    "cw_empty_replacement": {"keys": "cw\x1b", "initial": "one two three"},
    "cw_on_space": {"keys": "lcwX\x1b", "initial": "a b c"},
    "cw_count_2": {"keys": "c2wNEW\x1b", "initial": "one two three four"},
    "cw_count_2_alt": {"keys": "2cwNEW\x1b", "initial": "one two three four"},
    "cw_count_3": {"keys": "c3wNEW\x1b", "initial": "one two three four five"},

    # ── cW (change WORD forward) ──
    "cW_basic": {"keys": "cWNEW\x1b", "initial": "one two three"},
    "cW_with_punct": {"keys": "cWNEW\x1b", "initial": "hello.world foo bar"},
    "cW_from_mid": {"keys": "llcWNEW\x1b", "initial": "hello.world foo"},
    "cW_count_2": {"keys": "c2WNEW\x1b", "initial": "a.b c.d e.f g.h"},
    "cW_last_WORD": {"keys": "wwcWNEW\x1b", "initial": "aa bb.cc dd"},

    # ── cb (change word backward) ──
    "cb_basic": {"keys": "wcbNEW\x1b", "initial": "one two three"},
    "cb_from_mid_word": {"keys": "llcbNEW\x1b", "initial": "hello world"},
    "cb_at_col0": {"keys": "cbNEW\x1b", "initial": "hello world"},
    "cb_count_2": {"keys": "wwc2bNEW\x1b", "initial": "one two three four"},
    "cb_across_line": {"keys": "jcbNEW\x1b", "initial": "hello\nworld"},

    # ── cB (change WORD backward) ──
    "cB_basic": {"keys": "wcBNEW\x1b", "initial": "one two three"},
    "cB_with_punct": {"keys": "wcBNEW\x1b", "initial": "one.two three"},
    "cB_count_2": {"keys": "wwc2BNEW\x1b", "initial": "a.b c.d e.f g.h"},

    # ── ce (change to end of word, inclusive) ──
    "ce_basic": {"keys": "ceNEW\x1b", "initial": "one two three"},
    "ce_from_mid_word": {"keys": "llceNEW\x1b", "initial": "hello world"},
    "ce_single_word": {"keys": "ceNEW\x1b", "initial": "hello"},
    "ce_with_punct": {"keys": "ceNEW\x1b", "initial": "hello.world foo"},
    "ce_count_2": {"keys": "c2eNEW\x1b", "initial": "one two three four"},
    "ce_at_end_of_word": {"keys": "wlllceNEW\x1b", "initial": "one four three"},

    # ── cE (change to end of WORD, inclusive) ──
    "cE_basic": {"keys": "cENEW\x1b", "initial": "one two three"},
    "cE_with_punct": {"keys": "cENEW\x1b", "initial": "hello.world foo"},
    "cE_count_2": {"keys": "c2ENEW\x1b", "initial": "a.b c.d e.f g.h"},
    "cE_from_mid": {"keys": "llcENEW\x1b", "initial": "abc.def ghi"},

    # ── c$ (change to end of line) ──
    "c_dollar_basic": {"keys": "c$NEW\x1b", "initial": "hello world"},
    "c_dollar_from_mid": {"keys": "llc$NEW\x1b", "initial": "hello world"},
    "c_dollar_multiline": {"keys": "c$NEW\x1b", "initial": "first line\nsecond line"},
    "c_dollar_empty_line": {"keys": "jc$NEW\x1b", "initial": "hello\n\nworld"},
    "c_dollar_single_char": {"keys": "c$X\x1b", "initial": "z"},

    # ── c0 (change to start of line) ──
    "c0_from_mid": {"keys": "llllc0NEW\x1b", "initial": "hello world"},
    "c0_at_col0": {"keys": "c0X\x1b", "initial": "hello world"},
    "c0_second_line": {"keys": "jllc0NEW\x1b", "initial": "first\nsecond line\nthird"},

    # ── c^ (change to first non-blank) ──
    "c_caret_indented": {"keys": "8lc^X\x1b", "initial": "    hello world"},
    "c_caret_deep": {"keys": "wwc^X\x1b", "initial": "    one two three"},
    "c_caret_no_indent": {"keys": "llc^X\x1b", "initial": "hello world"},

    # ── cG (change to end of file, linewise) ──
    "cG_from_first": {"keys": "cGNEW\x1b", "initial": "one\ntwo\nthree\nfour"},
    "cG_from_mid": {"keys": "jcGNEW\x1b", "initial": "one\ntwo\nthree\nfour"},
    "cG_single_line": {"keys": "cGNEW\x1b", "initial": "hello"},

    # ── cgg (change to start of file, linewise) ──
    "cgg_from_last": {"keys": "GcggNEW\x1b", "initial": "one\ntwo\nthree\nfour"},
    "cgg_from_mid": {"keys": "jjcggNEW\x1b", "initial": "one\ntwo\nthree\nfour"},
    "cgg_from_first": {"keys": "cggNEW\x1b", "initial": "one\ntwo\nthree"},

    # ── cj (change current + line below, linewise) ──
    "cj_basic": {"keys": "cjNEW\x1b", "initial": "one\ntwo\nthree"},
    "cj_from_mid": {"keys": "jcjNEW\x1b", "initial": "one\ntwo\nthree\nfour"},
    "cj_two_lines": {"keys": "cjNEW\x1b", "initial": "one\ntwo"},
    "cj_count_2": {"keys": "c2jNEW\x1b", "initial": "aa\nbb\ncc\ndd\nee"},

    # ── ck (change current + line above, linewise) ──
    "ck_basic": {"keys": "jckNEW\x1b", "initial": "one\ntwo\nthree"},
    "ck_from_last": {"keys": "GckNEW\x1b", "initial": "one\ntwo\nthree"},
    "ck_count_2": {"keys": "Gc2kNEW\x1b", "initial": "aa\nbb\ncc\ndd\nee"},

    # ── cf{char} (change through found char, inclusive) ──
    "cf_basic": {"keys": "cfoNEW\x1b", "initial": "hello world foo"},
    "cf_first_match": {"keys": "cflNEW\x1b", "initial": "hello world"},
    "cf_space": {"keys": "cf NEW\x1b", "initial": "hello world foo"},
    "cf_no_match": {"keys": "cfzNEW\x1b", "initial": "hello world"},
    "cf_count_2": {"keys": "c2foNEW\x1b", "initial": "one two foo boo"},

    # ── ct{char} (change till found char, exclusive) ──
    "ct_basic": {"keys": "ctoNEW\x1b", "initial": "hello world foo"},
    "ct_space": {"keys": "ct NEW\x1b", "initial": "hello world foo"},
    "ct_no_match": {"keys": "ctzNEW\x1b", "initial": "hello world"},
    "ct_adjacent": {"keys": "cthNEW\x1b", "initial": "ahelp"},
    "ct_count_2": {"keys": "c2toNEW\x1b", "initial": "one two foo boo"},

    # ── cF{char} (change backward through found char) ──
    "cF_basic": {"keys": "$cFwNEW\x1b", "initial": "hello world"},
    "cF_no_match": {"keys": "$cFzNEW\x1b", "initial": "hello world"},
    "cF_space": {"keys": "$cF NEW\x1b", "initial": "hello world foo"},

    # ── cT{char} (change backward till found char) ──
    "cT_basic": {"keys": "$cTwNEW\x1b", "initial": "hello world"},
    "cT_no_match": {"keys": "$cTzNEW\x1b", "initial": "hello world"},
    "cT_space": {"keys": "$cT NEW\x1b", "initial": "hello world foo"},

    # ── c} (change to next paragraph) ──
    "c_rbrace_basic": {"keys": "c}NEW\x1b", "initial": "one\ntwo\n\nthree\nfour"},
    "c_rbrace_at_blank": {"keys": "jjc}NEW\x1b", "initial": "one\ntwo\n\nthree\nfour"},
    "c_rbrace_single": {"keys": "c}NEW\x1b", "initial": "hello"},

    # ── c{ (change to previous paragraph) ──
    "c_lbrace_basic": {"keys": "Gc{NEW\x1b", "initial": "one\ntwo\n\nthree\nfour"},
    "c_lbrace_from_mid": {"keys": "jjjc{NEW\x1b", "initial": "one\ntwo\n\nthree\nfour"},
    "c_lbrace_at_start": {"keys": "c{NEW\x1b", "initial": "hello\nworld"},

    # ── cc (change entire line) ──
    "cc_first_line": {"keys": "ccNEW\x1b", "initial": "first\nsecond\nthird"},
    "cc_middle_line": {"keys": "jccNEW\x1b", "initial": "first\nsecond\nthird"},
    "cc_last_line": {"keys": "GccNEW\x1b", "initial": "first\nsecond\nthird"},
    "cc_single_line": {"keys": "ccNEW\x1b", "initial": "only line"},
    "cc_empty_buffer": {"keys": "ccNEW\x1b", "initial": ""},
    "cc_on_empty_line": {"keys": "jccNEW\x1b", "initial": "hello\n\nworld"},
    "cc_indented": {"keys": "jccNEW\x1b", "initial": "top\n    indented\nbottom"},
    "cc_type_nothing": {"keys": "cc\x1b", "initial": "hello world"},
    "cc_long_line": {"keys": "ccX\x1b", "initial": "this is a longer line of text"},

    # ── {count}cc (change multiple lines) ──
    "cc_count_2": {"keys": "2ccNEW\x1b", "initial": "one\ntwo\nthree\nfour"},
    "cc_count_3": {"keys": "3ccNEW\x1b", "initial": "one\ntwo\nthree\nfour\nfive"},
    "cc_count_exceeds": {"keys": "99ccNEW\x1b", "initial": "one\ntwo\nthree"},
    "cc_count_from_mid": {"keys": "j2ccNEW\x1b", "initial": "one\ntwo\nthree\nfour\nfive"},

    # ── S (substitute line, same as cc) ──
    "S_basic_change": {"keys": "SNEW\x1b", "initial": "old text here"},
    "S_mid_line": {"keys": "jSNEW\x1b", "initial": "first\nsecond\nthird"},
    "S_empty_line": {"keys": "jSNEW\x1b", "initial": "above\n\nbelow"},
    "S_count_2": {"keys": "2SNEW\x1b", "initial": "one\ntwo\nthree\nfour"},

    # ── C (change to end of line, same as c$) ──
    "C_basic_change": {"keys": "CNEW\x1b", "initial": "hello world"},
    "C_from_mid": {"keys": "llCNEW\x1b", "initial": "hello world"},
    "C_at_eol": {"keys": "$CX\x1b", "initial": "hello world"},
    "C_single_char": {"keys": "CZ\x1b", "initial": "x"},
    "C_multiline": {"keys": "jCNEW\x1b", "initial": "first\nsecond\nthird"},
    "C_empty_line": {"keys": "jCNEW\x1b", "initial": "hello\n\nworld"},
    "C_type_nothing": {"keys": "C\x1b", "initial": "hello world"},

    # ── r{char} (replace single character) ──
    "r_basic": {"keys": "ra", "initial": "hello"},
    "r_mid_word": {"keys": "llrx", "initial": "hello"},
    "r_at_eol": {"keys": "$rz", "initial": "hello"},
    "r_first_char": {"keys": "rX", "initial": "abc"},
    "r_with_space": {"keys": "r ", "initial": "hello"},
    "r_digit": {"keys": "r5", "initial": "hello"},
    "r_punct": {"keys": "r!", "initial": "hello"},
    "r_on_space": {"keys": "lrx", "initial": "a b c"},
    "r_single_char_line": {"keys": "rx", "initial": "a"},
    "r_second_line": {"keys": "jrx", "initial": "abc\ndef\nghi"},
    "r_multiline_mid": {"keys": "jllrX", "initial": "abc\ndefgh\nijk"},

    # ── {count}r{char} (replace multiple chars) ──
    "r_count_2": {"keys": "2ra", "initial": "hello"},
    "r_count_3": {"keys": "3rx", "initial": "abcdef"},
    "r_count_5": {"keys": "5r.", "initial": "abcdefgh"},
    "r_count_from_mid": {"keys": "ll3rx", "initial": "abcdefgh"},
    "r_count_exact_line": {"keys": "5rx", "initial": "abcde"},
    "r_count_exceeds": {"keys": "99rx", "initial": "hello"},
    "r_count_exceeds_short": {"keys": "4rx", "initial": "abc"},
    "r_count_1": {"keys": "1rx", "initial": "hello"},

    # ── R (replace mode) ──
    "R_basic": {"keys": "RABC\x1b", "initial": "hello world"},
    "R_overwrite_mid": {"keys": "llRXYZ\x1b", "initial": "abcdefgh"},
    "R_single_char": {"keys": "RX\x1b", "initial": "hello"},
    "R_type_full_line": {"keys": "RNEW TEXT\x1b", "initial": "old stuff"},
    "R_extend_past_eol": {"keys": "lllllRXYZ\x1b", "initial": "hello"},
    "R_on_short_line": {"keys": "RABCDEF\x1b", "initial": "ab"},
    "R_empty_line": {"keys": "RABC\x1b", "initial": ""},
    "R_second_line": {"keys": "jRXYZ\x1b", "initial": "abc\ndef\nghi"},
    "R_type_nothing": {"keys": "R\x1b", "initial": "hello"},
    "R_from_mid_to_end": {"keys": "lllRXYZW\x1b", "initial": "abcdef"},
    "R_overwrite_all": {"keys": "RNEWLINE\x1b", "initial": "oldline"},

    # ── R with backspace (restores original char) ──
    "R_backspace_restore": {"keys": "RAB\x08\x08\x1b", "initial": "hello"},
    "R_backspace_mid": {"keys": "llRA\x08\x1b", "initial": "abcdef"},
    "R_backspace_then_type": {"keys": "RA\x08X\x1b", "initial": "hello"},
    "R_multi_backspace": {"keys": "RABC\x08\x08\x08\x1b", "initial": "hello"},
    "R_backspace_past_start": {"keys": "RAB\x08\x08\x08\x1b", "initial": "hello"},
    "R_backspace_at_extend": {"keys": "lllllRABC\x08\x1b", "initial": "hello"},

    # ── c with counts: {count}c{motion} and c{count}{motion} ──
    "count_2cw": {"keys": "2cwNEW\x1b", "initial": "one two three four"},
    "count_c2w": {"keys": "c2wNEW\x1b", "initial": "one two three four"},
    "count_c3j": {"keys": "c3jNEW\x1b", "initial": "aa\nbb\ncc\ndd\nee\nff"},
    "count_3cc": {"keys": "3ccNEW\x1b", "initial": "aa\nbb\ncc\ndd\nee"},
    "count_2ce": {"keys": "2ceNEW\x1b", "initial": "one two three four"},
    "count_c2e": {"keys": "c2eNEW\x1b", "initial": "one two three four"},
    "count_2cb": {"keys": "wwc2bNEW\x1b", "initial": "aa bb cc dd"},
    "count_c3l": {"keys": "c3lNEW\x1b", "initial": "abcdefgh"},
    "count_c2h": {"keys": "lllc2hNEW\x1b", "initial": "abcdefgh"},

    # ── Edge cases and special scenarios ──
    "edge_cw_single_char_word": {"keys": "cwX\x1b", "initial": "a b c d"},
    "edge_cc_preserves_neighbors": {"keys": "jccNEW\x1b", "initial": "aaa\nbbb\nccc\nddd"},
    "edge_cw_across_line": {"keys": "wwcwNEW\x1b", "initial": "one two\nthree four"},
    "edge_c_dollar_at_eol": {"keys": "$c$X\x1b", "initial": "hello world"},
    "edge_cw_whitespace_only": {"keys": "cwX\x1b", "initial": "   hello"},
    "edge_cc_blank_to_text": {"keys": "jccNEW\x1b", "initial": "top\n\nbottom"},
    "edge_cw_eol_last_word": {"keys": "wcwNEW\x1b", "initial": "aa bb"},
    "edge_ce_vs_cw_same": {"keys": "ceNEW\x1b", "initial": "one two three"},
}
