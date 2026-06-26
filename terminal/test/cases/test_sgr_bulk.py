"""Large generated SGR coverage: every 8-color fg/bg, bright variants,
common attribute combos, 256-color cube sampling, truecolor edge cases."""

ROWS = 4
COLS = 60
ESC = "\x1b"

def csi(s): return ESC + "[" + s

CASES = {}

# Every fg color 30..37
for n in range(30, 38):
    CASES[f"fg_{n}"] = csi(f"{n}m") + "X" + csi("0m") + "Y"

# Every bg color 40..47
for n in range(40, 48):
    CASES[f"bg_{n}"] = csi(f"{n}m") + "X" + csi("0m") + "Y"

# Every bright fg 90..97
for n in range(90, 98):
    CASES[f"fg_bright_{n}"] = csi(f"{n}m") + "X" + csi("0m") + "Y"

# Every bright bg 100..107
for n in range(100, 108):
    CASES[f"bg_bright_{n}"] = csi(f"{n}m") + "X" + csi("0m") + "Y"

# 256-color sampling across the cube and greyscale
for n in [0, 7, 8, 15, 16, 21, 42, 100, 196, 220, 231, 232, 244, 255]:
    CASES[f"fg_256_{n:03d}"] = csi(f"38;5;{n}m") + "X" + csi("0m") + "Y"
    CASES[f"bg_256_{n:03d}"] = csi(f"48;5;{n}m") + "X" + csi("0m") + "Y"

# Truecolor edge cases (pure black/white + primary corners)
for r, g, b in [(0,0,0), (255,255,255), (255,0,0), (0,255,0), (0,0,255),
                (127,127,127), (12,34,56), (200,100,50)]:
    CASES[f"fg_true_{r}_{g}_{b}"] = csi(f"38;2;{r};{g};{b}m") + "X" + csi("0m") + "Y"
    CASES[f"bg_true_{r}_{g}_{b}"] = csi(f"48;2;{r};{g};{b}m") + "X" + csi("0m") + "Y"

# All "off" codes after their on-counterpart
for on, off, label in [
    (1, 22, "bold"),
    (3, 23, "italic"),
    (4, 24, "underline"),
    (7, 27, "reverse"),
    (9, 29, "strike"),
]:
    CASES[f"on_off_{label}"] = csi(f"{on}m") + "A" + csi(f"{off}m") + "B" + csi("0m") + "C"

# Combined attrs (many at once)
CASES["combo_bold_italic_under"] = csi("1;3;4m") + "X" + csi("0m") + "Y"
CASES["combo_bold_under_red"]    = csi("1;4;31m") + "X" + csi("0m") + "Y"
CASES["combo_reverse_yellow"]    = csi("7;33m") + "X" + csi("0m") + "Y"
CASES["combo_all_attrs"]         = csi("1;3;4;5;7;9m") + "X" + csi("0m") + "Y"

# fg + bg in one sequence
CASES["fg_red_bg_blue"]   = csi("31;44m") + "X" + csi("0m") + "Y"
CASES["fg_256_bg_256"]    = csi("38;5;82;48;5;236m") + "X" + csi("0m") + "Y"
CASES["fg_true_bg_true"]  = csi("38;2;100;200;50;48;2;30;30;60m") + "X" + csi("0m") + "Y"

# 39/49 to reset only fg or only bg
CASES["fg_default"] = csi("31m") + "A" + csi("39m") + "B" + csi("0m")
CASES["bg_default"] = csi("44m") + "A" + csi("49m") + "B" + csi("0m")

# SGR sticks across newlines and erases keep the bg
CASES["sgr_persists_lf"] = csi("31m") + "abc\r\ndef" + csi("0m")
CASES["sgr_with_erase"]  = "X" * 20 + csi("41m") + csi("2K") + csi("0m")

# Empty SGR == reset
CASES["empty_is_reset"] = csi("31m") + "A" + csi("m") + "B"
