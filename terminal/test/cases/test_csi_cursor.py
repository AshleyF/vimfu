"""Cursor positioning CSI commands: CUP, CUU, CUD, CUF, CUB, CHA, CNL, CPL, VPA, HVP.

Excluded (pyte does not implement them — covered in test/cases_extras/):
  HPA (CSI `), CBT (CSI Z), CHT (CSI I), SCOSC/SCORC (CSI s/u).
"""

ROWS = 10
COLS = 20
ESC = "\x1b"

def csi(s): return ESC + "[" + s

CASES = {
    # CUP — H
    "cup_origin":        csi("H"),
    "cup_3_5":           csi("3;5H") + "X",
    "cup_1_1":           csi("1;1H") + "X",
    "cup_then_text":     csi("5;10H") + "X",
    "cup_omit_col":      csi("4H") + "X",
    "cup_omit_row":      csi(";4H") + "X",
    "cup_overflow":      csi("99;99H") + "X",
    "cup_via_hvp":       csi("3;5f") + "X",

    # CUU/CUD/CUF/CUB
    "cuu_basic":         csi("5;5H") + csi("2A") + "X",
    "cud_basic":         csi("5;5H") + csi("2B") + "X",
    "cuf_basic":         csi("5;5H") + csi("3C") + "X",
    "cub_basic":         csi("5;5H") + csi("3D") + "X",
    "cuu_default_is_1":  csi("5;5H") + csi("A") + "X",
    "cud_default_is_1":  csi("5;5H") + csi("B") + "X",
    "cuf_default_is_1":  csi("5;5H") + csi("C") + "X",
    "cub_default_is_1":  csi("5;5H") + csi("D") + "X",
    "cuu_clamps_at_top": csi("2;5H") + csi("9A") + "X",
    "cud_clamps_at_bot": csi("9;5H") + csi("9B") + "X",
    "cuf_clamps_right":  csi("5;15H") + csi("99C") + "X",
    "cub_clamps_left":   csi("5;5H") + csi("99D") + "X",
    "cuu_zero_is_one":   csi("5;5H") + csi("0A") + "X",
    "cuf_count_5":       csi("5;5H") + csi("5C") + "X",

    # CHA — column absolute
    "cha_basic":         csi("5;5H") + csi("10G") + "X",
    "cha_default":       csi("5;5H") + csi("G") + "X",
    "cha_zero":          csi("5;5H") + csi("0G") + "X",
    "cha_overflow":      csi("5;5H") + csi("99G") + "X",

    # VPA — d
    "vpa_basic":         csi("5;5H") + csi("8d") + "X",
    "vpa_default":       csi("5;5H") + csi("d") + "X",
    "vpa_overflow":      csi("5;5H") + csi("99d") + "X",

    # CNL / CPL  (E / F)
    "cnl_basic":         csi("5;5H") + csi("2E") + "X",
    "cpl_basic":         csi("5;5H") + csi("2F") + "X",
    "cnl_default":       csi("5;5H") + csi("E") + "X",
    "cpl_default":       csi("5;5H") + csi("F") + "X",
    "cnl_clamps":        csi("9;5H") + csi("9E") + "X",
    "cpl_clamps":        csi("2;5H") + csi("9F") + "X",

    # DECSC/DECRC (ESC 7 / ESC 8)
    "decsc_decrc":       csi("5;5H") + ESC + "7" + csi("9;10H") + "Y" + ESC + "8" + "X",
}

