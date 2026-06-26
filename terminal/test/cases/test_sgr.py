"""SGR (Select Graphic Rendition): colors + attributes."""

ROWS = 8
COLS = 40
ESC = "\x1b"

def csi(s): return ESC + "[" + s

# Pattern: emit a small bit of text, change attrs, emit more, reset, emit more.
def s(attr, text="X"):
    return csi(attr + "m") + text + csi("0m")

CASES = {
    # Attributes
    "sgr_reset":         s("0", "abc"),
    "sgr_bold":          s("1", "bold"),
    "sgr_dim":           s("2", "dim"),
    "sgr_italic":        s("3", "italic"),
    "sgr_underline":     s("4", "under"),
    "sgr_blink":         s("5", "blink"),
    "sgr_reverse":       s("7", "rev"),
    "sgr_strike":        s("9", "strike"),

    # Attribute off-codes
    "sgr_bold_then_off": s("1", "B") + csi("22m") + "N",
    "sgr_italic_off":    s("3", "I") + csi("23m") + "N",
    "sgr_under_off":     s("4", "U") + csi("24m") + "N",
    "sgr_reverse_off":   s("7", "R") + csi("27m") + "N",
    "sgr_strike_off":    s("9", "S") + csi("29m") + "N",

    # ANSI 16 fg
    "sgr_fg_red":        s("31", "red"),
    "sgr_fg_green":      s("32", "green"),
    "sgr_fg_blue":       s("34", "blue"),
    "sgr_fg_white":      s("37", "wht"),
    "sgr_fg_default":    csi("31m") + "R" + csi("39m") + "N",

    # ANSI 16 bg
    "sgr_bg_red":        s("41", "RED"),
    "sgr_bg_yellow":     s("43", "YEL"),
    "sgr_bg_default":    csi("44m") + "B" + csi("49m") + "N",

    # Bright (90-97 / 100-107)
    "sgr_bright_fg":     s("91", "br_r"),
    "sgr_bright_bg":     s("104", "BR_B"),

    # Combined
    "sgr_bold_red":      s("1;31", "br"),
    "sgr_under_blue_bg": s("4;44", "ub"),
    "sgr_three_combo":   s("1;3;4", "bui"),

    # 256-color
    "sgr_fg_256_42":     csi("38;5;42m") + "X" + csi("0m"),
    "sgr_bg_256_220":    csi("48;5;220m") + "X" + csi("0m"),
    "sgr_fg_256_grey":   csi("38;5;240m") + "X" + csi("0m"),

    # Truecolor (xterm/legacy semicolon form)
    "sgr_fg_truecolor":  csi("38;2;200;100;50m") + "X" + csi("0m"),
    "sgr_bg_truecolor":  csi("48;2;30;60;90m") + "X" + csi("0m"),

    # Empty SGR == 0
    "sgr_empty":         csi("31m") + "R" + csi("m") + "N",

    # Reset persists across newlines
    "sgr_across_lines":  csi("31m") + "ab\r\ncd" + csi("0m") + "ef",
}
