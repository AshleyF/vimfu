"""Bulk wrap tests — every wrap-related edge case at different widths."""

ROWS = 6
COLS = 10
ESC = "\x1b"

def csi(s): return ESC + "[" + s

CASES = {}

# Write exactly N chars for N in 1..3*COLS
for n in [1, 5, 9, 10, 11, 15, 19, 20, 21, 29, 30]:
    CASES[f"write_{n:02d}_chars"] = "X" * n

# Wrap with various continuations
CASES["wrap_then_cr"]            = "X" * 10 + "\rABC"
CASES["wrap_then_cr_lf"]         = "X" * 10 + "\r\nABC"
CASES["wrap_then_lf"]            = "X" * 10 + "\nABC"
CASES["wrap_then_bs_then_chr"]   = "X" * 10 + "\bY"
CASES["wrap_then_bs_three"]      = "X" * 10 + "\b\b\bY"
CASES["wrap_then_cuf"]           = "X" * 10 + csi("3C") + "Y"
CASES["wrap_then_cub"]           = "X" * 10 + csi("3D") + "Y"
CASES["wrap_then_cuu"]           = "X" * 10 + csi("1A") + "Y"
CASES["wrap_then_cud"]           = "X" * 10 + csi("1B") + "Y"
CASES["wrap_then_cup"]           = "X" * 10 + csi("3;3H") + "Y"

# Disable autowrap
CASES["no_autowrap_15_chars"]    = csi("?7l") + "X" * 15
CASES["no_autowrap_then_re"]     = csi("?7l") + "X" * 12 + csi("?7h") + "Y" * 12

# Wrap multiple rows then erase
CASES["wrap_full_screen_clear"]  = "X" * (ROWS * COLS) + csi("H") + csi("2J")
CASES["wrap_full_screen_ed_1"]   = "X" * (ROWS * COLS) + csi("3;5H") + csi("1J")
CASES["wrap_full_screen_ed_2"]   = "X" * (ROWS * COLS) + csi("3;5H") + csi("2J")
