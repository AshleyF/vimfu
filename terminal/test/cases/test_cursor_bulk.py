"""Comprehensive cursor motion: every CUU/CUD/CUF/CUB count from 1..15,
boundary cases, edge-of-screen CUP, off-region clamping."""

ROWS = 10
COLS = 20
ESC = "\x1b"

def csi(s): return ESC + "[" + s

CASES = {}

# CUU/CUD/CUF/CUB with counts 1..15 from a centered position
for n in range(1, 16):
    CASES[f"cuu_{n}"] = csi("8;10H") + csi(f"{n}A") + "X"
    CASES[f"cud_{n}"] = csi("3;10H") + csi(f"{n}B") + "X"
    CASES[f"cuf_{n}"] = csi("5;5H")  + csi(f"{n}C") + "X"
    CASES[f"cub_{n}"] = csi("5;15H") + csi(f"{n}D") + "X"

# CUP to every corner
CASES["cup_top_left"]     = csi("1;1H")  + "X"
CASES["cup_top_right"]    = csi(f"1;{COLS}H")  + "X"
CASES["cup_bottom_left"]  = csi(f"{ROWS};1H") + "X"
CASES["cup_bottom_right"] = csi(f"{ROWS};{COLS}H") + "X"

# CUP middle
CASES["cup_center"] = csi(f"{ROWS//2};{COLS//2}H") + "X"

# CUP with 0,0 defaults to 1,1
CASES["cup_0_0"] = csi("0;0H") + "X"

# Cursor motion past 0,0 (clamps)
CASES["cuu_from_0_0"]  = csi("1;1H") + csi("5A") + "X"
CASES["cub_from_0_0"]  = csi("1;1H") + csi("5D") + "X"
CASES["cud_to_bottom"] = csi("1;1H") + csi("99B") + "X"
CASES["cuf_to_right"]  = csi("1;1H") + csi("99C") + "X"

# CUP then advancing by writes
CASES["cup_then_3_chars"] = csi("5;5H") + "ABC"

# CR / LF position effects
CASES["cr_then_x"]      = "ABC" + "\r" + "X"
CASES["lf_then_x"]      = "ABC" + "\n" + "X"  # cursor stays at col 3, lf advances row
CASES["crlf_then_x"]    = "ABC" + "\r\n" + "X"

# CNL/CPL counts
for n in range(1, 6):
    CASES[f"cnl_{n}"] = csi("5;5H") + csi(f"{n}E") + "X"
    CASES[f"cpl_{n}"] = csi("5;5H") + csi(f"{n}F") + "X"

# VPA counts
for r in (1, 2, 5, 8, 10):
    CASES[f"vpa_{r}"] = csi("5;5H") + csi(f"{r}d") + "X"

# CHA counts
for c in (1, 5, 10, 15, 20):
    CASES[f"cha_{c}"] = csi("5;5H") + csi(f"{c}G") + "X"

# HVP equivalent to CUP
CASES["hvp_3_3"] = csi("3;3f") + "X"
CASES["hvp_omit"] = csi("f") + "X"
