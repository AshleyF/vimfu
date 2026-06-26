"""Origin mode (DECOM) + DECSTBM interaction."""

ROWS = 8
COLS = 12
ESC = "\x1b"

def csi(s): return ESC + "[" + s

CASES = {
    # With origin mode OFF, CUP is absolute even inside a region.
    "decom_off_cup":     csi("3;6r") + csi("?6l") + csi("1;1H") + "X",
    # With origin mode ON, CUP is relative to scroll region top.
    "decom_on_cup":      csi("3;6r") + csi("?6h") + csi("1;1H") + "X",
    "decom_on_cup_3_3":  csi("3;6r") + csi("?6h") + csi("3;3H") + "X",
    # DECOM clamps cursor inside region.
    "decom_on_overflow": csi("3;6r") + csi("?6h") + csi("99;1H") + "X",
    # Toggling DECOM moves cursor to (region top, col 0).
    "decom_toggle_resets": csi("3;6r") + csi("5;5H") + csi("?6h") + "X",
    # Reset region also resets origin.
    "decom_reset_region": csi("3;6r") + csi("?6h") + csi("r") + csi("1;1H") + "X",
}
