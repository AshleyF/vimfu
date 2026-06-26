"""Tab stops: HT (basic forward tab via default 8-col stops), HTS, TBC.

Excluded (not implemented in pyte; covered in test/cases_extras/):
  CBT (CSI Z), CHT (CSI I), TBC-all-then-tab.
"""

ROWS = 4
COLS = 32
ESC = "\x1b"

def csi(s): return ESC + "[" + s

CASES = {
    # Default tab stops every 8 columns
    "tab_to_8":          "\tX",
    "tab_to_16":         "\t\tX",
    "tab_to_24":         "\t\t\tX",

    # HT from various columns
    "tab_from_3":        "abc\tX",
    "tab_from_7":        "1234567\tX",
    "tab_from_8":        "12345678\tX",

    # HTS — set tab at cursor position
    "hts_set_at_5":      "12345" + ESC + "H" + "\r\t" + "X",
    "hts_and_clear":     "12345" + ESC + "H" + csi("g") + "\r\t" + "X",
}

