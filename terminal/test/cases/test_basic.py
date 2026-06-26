"""Basic printing + C0 control characters: CR, LF, BS, TAB, plain text."""

ROWS = 10
COLS = 20

ESC = "\x1b"
BEL = "\x07"
BS  = "\x08"
HT  = "\x09"
LF  = "\x0a"
CR  = "\x0d"

CASES = {
    "plain_text":         "hello",
    "two_words":          "hello world",
    "cr_lf":              "abc\r\ndef",
    "lf_only":            "abc\ndef",
    "cr_only":            "abc\rXY",
    "bs_basic":           "abc\x08X",
    "bs_at_col_0":        "\x08X",
    "bs_many":            "abc\x08\x08\x08X",
    "tab_basic":          "a\tb",
    "tab_from_col_0":     "\tx",
    "tab_aligned":        "abcdefgh\tX",
    "tab_at_col_7":       "1234567\tX",
    "tab_past_eol":       "abc\t\t\t\tX",
    "bs_after_wrap":      "x" * 19 + "y" + "\x08z",
    "cr_in_middle":       "abcdef\rXY",
    "empty":              "",
    "single_char":        "A",
    "two_lines":          "first\r\nsecond",
    "three_lines":        "a\r\nb\r\nc",
    "trailing_lf":        "abc\n",
    "trailing_cr":        "abc\r",
    "form_feed":          "abc\x0cdef",
    "vert_tab":           "abc\x0bdef",
    "bell_ignored":       "ab" + BEL + "cd",
    "mix_bs_and_print":   "hello\x08\x08\x08XYZ",
    "delete_char_byte":   "abc\x7fd",   # DEL is no-op in ground state
    "null_ignored":       "a\x00b",
    "high_ascii":         "x\xb1y",     # latin-1 ± (UTF-8 lead)
    "utf8_2byte":         "x\u00e9y",   # é
    "utf8_3byte":         "x\u2192y",   # →
    "many_lines":         "\r\n".join(f"L{i}" for i in range(8)),
}
