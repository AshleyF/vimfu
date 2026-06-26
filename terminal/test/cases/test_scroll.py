"""Scrolling region, DECSTBM, IL, DL.

Excluded (not implemented in pyte; in test/cases_extras/):
  SU (CSI S), SD (CSI T).
"""

ROWS = 10
COLS = 12
ESC = "\x1b"

def csi(s): return ESC + "[" + s

def fill_lines():
    out = csi("H")
    for i in range(ROWS):
        out += f"line {i:02d}" + "\r\n"
    return out

CASES = {
    # DECSTBM
    "stbm_default":         fill_lines() + csi("r"),
    "stbm_2_5":             fill_lines() + csi("2;5r") + csi("H") + "X",
    "stbm_then_lf_scrolls": fill_lines() + csi("2;5r") + csi("5;1H") + "\n",

    # IL / DL
    "il_basic":  fill_lines() + csi("3;1H") + csi("L"),
    "il_3":      fill_lines() + csi("3;1H") + csi("3L"),
    "dl_basic":  fill_lines() + csi("3;1H") + csi("M"),
    "dl_3":      fill_lines() + csi("3;1H") + csi("3M"),

    # IL/DL respect scroll region
    "il_in_region":  fill_lines() + csi("3;7r") + csi("4;1H") + csi("2L"),
    "dl_in_region":  fill_lines() + csi("3;7r") + csi("4;1H") + csi("2M"),

    # Newline at scroll boundary scrolls only the region
    "lf_at_region_end": fill_lines() + csi("3;7r") + csi("7;1H") + "\n",

    # Reverse index at top of region scrolls down
    "ri_at_region_top": fill_lines() + csi("3;7r") + csi("3;1H") + ESC + "M",
}

