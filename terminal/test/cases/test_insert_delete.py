"""Character-level insert/delete: ICH, DCH, IRM (CSI 4 h/l)."""

ROWS = 4
COLS = 16
ESC = "\x1b"

def csi(s): return ESC + "[" + s

def prefill():
    return "ABCDEFGHIJKLMNOP" + csi("1;5H")  # cursor on 'E'

CASES = {
    # ICH — insert N blank cells, shift right (off the edge)
    "ich_default_1": prefill() + csi("@"),
    "ich_3":         prefill() + csi("3@"),
    "ich_overflow":  prefill() + csi("99@"),

    # DCH — delete N cells, shift left
    "dch_default_1": prefill() + csi("P"),
    "dch_3":         prefill() + csi("3P"),
    "dch_overflow":  prefill() + csi("99P"),

    # IRM — insert mode (CSI 4 h)
    "irm_off":       prefill() + "Z",                       # overwrite
    "irm_on":        prefill() + csi("4h") + "Z",           # insert
    "irm_on_off":    prefill() + csi("4h") + "Z" + csi("4l") + "Y",

    # SGR carried with inserted/deleted cells (bg sweeps through)
    "ich_with_bg":   prefill() + csi("41m") + csi("3@") + csi("0m"),
    "dch_with_bg":   prefill() + csi("41m") + csi("3P") + csi("0m"),
}
