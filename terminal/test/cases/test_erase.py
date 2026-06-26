"""Erase commands: ED, EL, ECH."""

ROWS = 6
COLS = 20
ESC = "\x1b"

def csi(s): return ESC + "[" + s

# Fill some content first, then erase.
def fill(text="ABCDEFGHIJKLMNOPQRST"):
    out = csi("H")
    for _ in range(ROWS):
        out += text + "\r\n"
    return out + csi("3;10H")   # place cursor row 3 col 10

CASES = {
    # ED — Erase in Display
    "ed_after_cursor":   fill() + csi("0J"),
    "ed_before_cursor":  fill() + csi("1J"),
    "ed_all":            fill() + csi("2J"),
    "ed_default_is_0":   fill() + csi("J"),

    # EL — Erase in Line
    "el_after_cursor":   fill() + csi("0K"),
    "el_before_cursor":  fill() + csi("1K"),
    "el_whole_line":     fill() + csi("2K"),
    "el_default_is_0":   fill() + csi("K"),

    # ECH — Erase N characters
    "ech_3":             fill() + csi("3X"),
    "ech_default_1":     fill() + csi("X"),
    "ech_overflow":      fill() + csi("99X"),

    # Erase preserves cursor SGR for new cells
    "ed_with_red_bg":    fill() + csi("41m") + csi("2J"),
    "el_with_yellow_bg": fill() + csi("43m") + csi("2K"),

    # ED 3 also clears scrollback (treat same as 2 in our small view)
    "ed_3_scrollback":   fill() + csi("3J"),
}
