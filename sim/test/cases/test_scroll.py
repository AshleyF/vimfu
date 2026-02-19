THIRTYLINES = "\n".join(f"Line {i:02d} content" for i in range(1, 31))
FIFTYLINES = "\n".join(f"Line {i:02d} content" for i in range(1, 51))
EIGHTEENLINES = "\n".join(f"Line {i:02d} content" for i in range(1, 19))
NINETEENLINES = "\n".join(f"Line {i:02d} content" for i in range(1, 20))

CASES = {
    # ===== Ctrl-D (\x04) - scroll down half page =====
    "ctrl_d_basic": {
        "keys": "\x04",
        "initial": THIRTYLINES,
    },
    "ctrl_d_twice": {
        "keys": "\x04\x04",
        "initial": THIRTYLINES,
    },
    "ctrl_d_three_times": {
        "keys": "\x04\x04\x04",
        "initial": THIRTYLINES,
    },
    "ctrl_d_at_bottom": {
        "keys": "\x04\x04\x04\x04\x04\x04",
        "initial": THIRTYLINES,
    },
    "ctrl_d_short_file_fits_on_screen": {
        "keys": "\x04",
        "initial": "Line 1\nLine 2\nLine 3\nLine 4\nLine 5",
    },
    "ctrl_d_with_count_5": {
        "keys": "5\x04",
        "initial": THIRTYLINES,
    },
    "ctrl_d_with_count_3": {
        "keys": "3\x04",
        "initial": THIRTYLINES,
    },
    "ctrl_d_count_then_subsequent": {
        "keys": "5\x04\x04",
        "initial": THIRTYLINES,
    },
    "ctrl_d_from_middle_of_file": {
        "keys": "15G\x04",
        "initial": THIRTYLINES,
    },
    "ctrl_d_on_fifty_line_file": {
        "keys": "\x04",
        "initial": FIFTYLINES,
    },
    "ctrl_d_fifty_lines_multiple": {
        "keys": "\x04\x04\x04",
        "initial": FIFTYLINES,
    },

    # ===== Ctrl-U (\x15) - scroll up half page =====
    "ctrl_u_after_ctrl_d": {
        "keys": "\x04\x15",
        "initial": THIRTYLINES,
    },
    "ctrl_u_after_two_ctrl_d": {
        "keys": "\x04\x04\x15",
        "initial": THIRTYLINES,
    },
    "ctrl_u_multiple": {
        "keys": "\x04\x04\x04\x15\x15",
        "initial": THIRTYLINES,
    },
    "ctrl_u_at_top": {
        "keys": "\x15",
        "initial": THIRTYLINES,
    },
    "ctrl_u_back_to_top": {
        "keys": "\x04\x04\x15\x15\x15",
        "initial": THIRTYLINES,
    },
    "ctrl_u_with_count_5": {
        "keys": "\x04\x04" + "5\x15",
        "initial": THIRTYLINES,
    },
    "ctrl_u_with_count_3": {
        "keys": "\x04\x04" + "3\x15",
        "initial": THIRTYLINES,
    },
    "ctrl_u_count_then_subsequent": {
        "keys": "\x04\x04\x04" + "5\x15\x15",
        "initial": THIRTYLINES,
    },
    "ctrl_u_short_file": {
        "keys": "\x15",
        "initial": "Line 1\nLine 2\nLine 3",
    },

    # ===== Ctrl-F (\x06) - scroll forward full page =====
    "ctrl_f_basic": {
        "keys": "\x06",
        "initial": THIRTYLINES,
    },
    "ctrl_f_twice": {
        "keys": "\x06\x06",
        "initial": THIRTYLINES,
    },
    "ctrl_f_at_bottom": {
        "keys": "\x06\x06\x06\x06",
        "initial": THIRTYLINES,
    },
    "ctrl_f_short_file": {
        "keys": "\x06",
        "initial": "Line 1\nLine 2\nLine 3\nLine 4\nLine 5",
    },
    "ctrl_f_on_fifty_line_file": {
        "keys": "\x06",
        "initial": FIFTYLINES,
    },
    "ctrl_f_fifty_lines_twice": {
        "keys": "\x06\x06",
        "initial": FIFTYLINES,
    },
    "ctrl_f_fifty_lines_three_times": {
        "keys": "\x06\x06\x06",
        "initial": FIFTYLINES,
    },
    "ctrl_f_keeps_overlap_lines": {
        "keys": "\x06\x06\x06\x06\x06",
        "initial": FIFTYLINES,
    },

    # ===== Ctrl-B (\x02) - scroll backward full page =====
    "ctrl_b_after_ctrl_f": {
        "keys": "\x06\x02",
        "initial": THIRTYLINES,
    },
    "ctrl_b_after_two_ctrl_f": {
        "keys": "\x06\x06\x02",
        "initial": THIRTYLINES,
    },
    "ctrl_b_multiple": {
        "keys": "\x06\x06\x02\x02",
        "initial": THIRTYLINES,
    },
    "ctrl_b_at_top": {
        "keys": "\x02",
        "initial": THIRTYLINES,
    },
    "ctrl_b_back_to_top": {
        "keys": "\x06\x06\x02\x02\x02",
        "initial": THIRTYLINES,
    },
    "ctrl_b_short_file": {
        "keys": "\x02",
        "initial": "Line 1\nLine 2\nLine 3",
    },
    "ctrl_b_on_fifty_line_file": {
        "keys": "\x06\x06\x06\x02",
        "initial": FIFTYLINES,
    },

    # ===== zz - center current line on screen =====
    "zz_from_line_15": {
        "keys": "15Gzz",
        "initial": THIRTYLINES,
    },
    "zz_from_line_20": {
        "keys": "20Gzz",
        "initial": THIRTYLINES,
    },
    "zz_from_line_1": {
        "keys": "1Gzz",
        "initial": THIRTYLINES,
    },
    "zz_from_line_5": {
        "keys": "5Gzz",
        "initial": THIRTYLINES,
    },
    "zz_from_last_line": {
        "keys": "Gzz",
        "initial": THIRTYLINES,
    },
    "zz_from_line_28": {
        "keys": "28Gzz",
        "initial": THIRTYLINES,
    },
    "zz_on_short_file": {
        "keys": "3Gzz",
        "initial": "Line 1\nLine 2\nLine 3\nLine 4\nLine 5",
    },

    # ===== zt - scroll current line to top =====
    "zt_from_line_15": {
        "keys": "15Gzt",
        "initial": THIRTYLINES,
    },
    "zt_from_line_10": {
        "keys": "10Gzt",
        "initial": THIRTYLINES,
    },
    "zt_from_line_1": {
        "keys": "1Gzt",
        "initial": THIRTYLINES,
    },
    "zt_from_line_3": {
        "keys": "3Gzt",
        "initial": THIRTYLINES,
    },
    "zt_from_last_line": {
        "keys": "Gzt",
        "initial": THIRTYLINES,
    },
    "zt_from_line_25": {
        "keys": "25Gzt",
        "initial": THIRTYLINES,
    },

    # ===== zb - scroll current line to bottom =====
    "zb_from_line_15": {
        "keys": "15Gzb",
        "initial": THIRTYLINES,
    },
    "zb_from_line_20": {
        "keys": "20Gzb",
        "initial": THIRTYLINES,
    },
    "zb_from_line_1": {
        "keys": "1Gzb",
        "initial": THIRTYLINES,
    },
    "zb_from_line_5": {
        "keys": "5Gzb",
        "initial": THIRTYLINES,
    },
    "zb_from_last_line": {
        "keys": "Gzb",
        "initial": THIRTYLINES,
    },
    "zb_from_line_28": {
        "keys": "28Gzb",
        "initial": THIRTYLINES,
    },

    # ===== Ctrl-E (\x05) - scroll down one line =====
    "ctrl_e_basic": {
        "keys": "\x05",
        "initial": THIRTYLINES,
    },
    "ctrl_e_three_times": {
        "keys": "\x05\x05\x05",
        "initial": THIRTYLINES,
    },
    "ctrl_e_five_times": {
        "keys": "\x05\x05\x05\x05\x05",
        "initial": THIRTYLINES,
    },
    "ctrl_e_at_bottom": {
        "keys": "G\x05",
        "initial": THIRTYLINES,
    },
    "ctrl_e_near_bottom": {
        "keys": "25G\x05\x05\x05\x05\x05\x05\x05\x05\x05\x05",
        "initial": THIRTYLINES,
    },
    "ctrl_e_cursor_pushed_down": {
        "keys": "\x05\x05\x05\x05\x05\x05\x05\x05\x05\x05",
        "initial": THIRTYLINES,
    },
    "ctrl_e_short_file": {
        "keys": "\x05",
        "initial": "Line 1\nLine 2\nLine 3",
    },

    # ===== Ctrl-Y (\x19) - scroll up one line =====
    "ctrl_y_after_scroll_down": {
        "keys": "\x05\x05\x05\x19",
        "initial": THIRTYLINES,
    },
    "ctrl_y_multiple": {
        "keys": "\x05\x05\x05\x05\x05\x19\x19\x19",
        "initial": THIRTYLINES,
    },
    "ctrl_y_at_top": {
        "keys": "\x19",
        "initial": THIRTYLINES,
    },
    "ctrl_y_back_to_top": {
        "keys": "\x05\x05\x05\x19\x19\x19",
        "initial": THIRTYLINES,
    },
    "ctrl_y_cursor_pushed_up": {
        "keys": "G\x19\x19\x19\x19\x19\x19\x19\x19\x19\x19",
        "initial": THIRTYLINES,
    },
    "ctrl_y_short_file": {
        "keys": "\x19",
        "initial": "Line 1\nLine 2\nLine 3",
    },

    # ===== Edge cases =====
    "scroll_single_line_file_ctrl_d": {
        "keys": "\x04",
        "initial": "Only one line",
    },
    "scroll_single_line_file_ctrl_u": {
        "keys": "\x15",
        "initial": "Only one line",
    },
    "scroll_single_line_file_ctrl_f": {
        "keys": "\x06",
        "initial": "Only one line",
    },
    "scroll_single_line_file_ctrl_b": {
        "keys": "\x02",
        "initial": "Only one line",
    },
    "scroll_empty_file_ctrl_d": {
        "keys": "\x04",
        "initial": "",
    },
    "scroll_empty_file_ctrl_u": {
        "keys": "\x15",
        "initial": "",
    },
    "scroll_empty_file_ctrl_f": {
        "keys": "\x06",
        "initial": "",
    },
    "scroll_empty_file_ctrl_b": {
        "keys": "\x02",
        "initial": "",
    },
    "scroll_exactly_18_lines_ctrl_d": {
        "keys": "\x04",
        "initial": EIGHTEENLINES,
    },
    "scroll_exactly_18_lines_ctrl_f": {
        "keys": "\x06",
        "initial": EIGHTEENLINES,
    },
    "scroll_19_lines_ctrl_d": {
        "keys": "\x04",
        "initial": NINETEENLINES,
    },
    "scroll_19_lines_ctrl_f": {
        "keys": "\x06",
        "initial": NINETEENLINES,
    },
    "scroll_19_lines_ctrl_e": {
        "keys": "\x05",
        "initial": NINETEENLINES,
    },
    "scroll_zz_on_empty_file": {
        "keys": "zz",
        "initial": "",
    },
    "scroll_zt_on_empty_file": {
        "keys": "zt",
        "initial": "",
    },
    "scroll_zb_on_empty_file": {
        "keys": "zb",
        "initial": "",
    },
}
