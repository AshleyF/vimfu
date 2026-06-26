"""Autowrap (DECAWM), reverse wrap, line splits."""

ROWS = 6
COLS = 10
ESC = "\x1b"

def csi(s): return ESC + "[" + s

CASES = {
    "wrap_at_eol":          "ABCDEFGHIJX",      # 10 chars then X wraps to row 2
    "wrap_two_full_lines":  "0123456789ABCDEFGHIJ",
    "wrap_three_full":      "0123456789" * 3,
    "wrap_with_lf":         "0123456789\nXY",
    "no_wrap_off":          csi("?7l") + "0123456789ABC",
    "no_wrap_then_on":      csi("?7l") + "0123456789" + csi("?7h") + "ABC",
    "wrap_then_cr":         "0123456789X\rY",
    # Pending-wrap (DEC autowrap latch): writing exactly cols chars sets
    # the latch but does NOT advance to next line until the *next* print.
    "wrap_latch_then_csi":  "0123456789" + csi("3;1H") + "X",
    "wrap_then_bs":         "0123456789\x08X",
    "wrap_in_middle":       "abcde" + "FGHIJK",
    "wrap_two_then_text":   "A" * 25 + "Z",
    "wrap_with_sgr":        csi("31m") + "A" * 15 + csi("0m"),
    "wrap_at_end_of_screen": "X" * (ROWS * COLS) + "Y",
}
