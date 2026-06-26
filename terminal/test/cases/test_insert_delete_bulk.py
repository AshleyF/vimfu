"""Insert/delete bulk: ICH/DCH/ECH/IL/DL with various counts."""

ROWS = 8
COLS = 16
ESC = "\x1b"

def csi(s): return ESC + "[" + s

def fill_grid():
    out = csi("H")
    for r in range(ROWS):
        out += f"row{r:02d}-{r:02d}{r:02d}{r:02d}{r:02d}".ljust(COLS)[:COLS] + "\r\n"
    return out

CASES = {}

# ICH counts 1..8 at cursor (3,5)
for n in range(1, 9):
    CASES[f"ich_{n}"] = fill_grid() + csi("4;6H") + csi(f"{n}@")

# DCH counts 1..8 at cursor (3,5)
for n in range(1, 9):
    CASES[f"dch_{n}"] = fill_grid() + csi("4;6H") + csi(f"{n}P")

# ECH counts 1..8 at cursor (3,5)
for n in range(1, 9):
    CASES[f"ech_{n}"] = fill_grid() + csi("4;6H") + csi(f"{n}X")

# IL counts 1..6 at row 3
for n in range(1, 7):
    CASES[f"il_{n}"] = fill_grid() + csi("4;1H") + csi(f"{n}L")

# DL counts 1..6 at row 3 (skip 3, 4 — pyte has a sparse-buffer quirk
# when the moved-up source row is empty: it leaves the destination row
# unchanged instead of blanking it; real terminals overwrite.)
for n in (1, 2, 5, 6):
    CASES[f"dl_{n}"] = fill_grid() + csi("4;1H") + csi(f"{n}M")

# IL/DL in scroll region
CASES["il_in_region_2_5"] = fill_grid() + csi("3;6r") + csi("4;1H") + csi("2L")
CASES["dl_in_region_2_5"] = fill_grid() + csi("3;6r") + csi("4;1H") + csi("2M")

# ICH/DCH past end of line
CASES["ich_at_end"]  = fill_grid() + csi("2;14H") + csi("4@")
CASES["dch_at_end"]  = fill_grid() + csi("2;14H") + csi("4P")
CASES["ich_at_col_1"] = fill_grid() + csi("2;1H") + csi("3@")
CASES["dch_at_col_1"] = fill_grid() + csi("2;1H") + csi("3P")

# IRM (insert mode) writes
CASES["irm_insert_abc"]   = fill_grid() + csi("2;3H") + csi("4h") + "ABC" + csi("4l")
CASES["irm_off_overwrite"] = fill_grid() + csi("2;3H") + "ABC"
