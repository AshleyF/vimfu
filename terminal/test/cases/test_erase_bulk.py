"""Erase tests at every cursor position + every ED/EL mode + with bg color."""

ROWS = 6
COLS = 16
ESC = "\x1b"

def csi(s): return ESC + "[" + s

def fill(ch="A"):
    out = csi("H")
    for r in range(ROWS):
        out += ch * COLS + "\r\n"
    return out

CASES = {}

# EL at each (row, col) position — pick a representative grid
for r in [1, 3, 6]:
    for c in [1, 8, 16]:
        for mode in [0, 1, 2]:
            CASES[f"el_r{r}_c{c}_m{mode}"] = fill() + csi(f"{r};{c}H") + csi(f"{mode}K")

# ED at each (row, col) position
for r in [1, 3, 6]:
    for c in [1, 8, 16]:
        for mode in [0, 1, 2]:
            CASES[f"ed_r{r}_c{c}_m{mode}"] = fill() + csi(f"{r};{c}H") + csi(f"{mode}J")

# Erase fills with current bg
for mode in [0, 1, 2]:
    CASES[f"ed_bg_red_m{mode}"]    = fill() + csi("3;8H") + csi("41m") + csi(f"{mode}J") + csi("0m")
    CASES[f"el_bg_yellow_m{mode}"] = fill() + csi("3;8H") + csi("43m") + csi(f"{mode}K") + csi("0m")

# Erase between writes
CASES["el_between"] = "AAAAA" + csi("K") + "BBB"
CASES["ed_between"] = "row1\r\nrow2\r\nrow3" + csi("2;2H") + csi("J")

# ECH at boundaries
CASES["ech_at_col_1"]  = fill() + csi("3;1H")  + csi("5X")
CASES["ech_at_col_8"]  = fill() + csi("3;8H")  + csi("5X")
CASES["ech_overflow"]  = fill() + csi("3;14H") + csi("10X")
CASES["ech_with_bg"]   = fill() + csi("3;5H")  + csi("41m") + csi("5X") + csi("0m")
