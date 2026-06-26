"""ESC 7 / ESC 8 (DECSC / DECRC): save & restore cursor + attributes."""

ROWS = 8
COLS = 20
ESC = "\x1b"

def csi(s): return ESC + "[" + s

CASES = {
    "decsc_pos":              csi("4;6H") + ESC + "7" + csi("2;2H") + "Y" + ESC + "8" + "X",
    "decsc_pos_again":        csi("4;6H") + ESC + "7" + csi("8;20H") + "Z" + ESC + "8" + "X",
    "decsc_preserves_sgr":    csi("31m") + ESC + "7" + csi("0m") + "A" + ESC + "8" + "B",
    "decsc_bold":             csi("1m") + ESC + "7" + csi("0m") + "A" + ESC + "8" + "B",
    "decsc_then_lf_then_rc":  csi("4;6H") + ESC + "7" + "\r\n\r\n" + ESC + "8" + "X",

    # restore without prior save → cursor at home, default attrs
    "decrc_unsaved":          ESC + "8" + "X",

    # save twice, restore once — restores to second save
    "decsc_twice":            csi("2;2H") + ESC + "7" + csi("4;4H") + ESC + "7"
                              + csi("7;15H") + "Q" + ESC + "8" + "X",
}
