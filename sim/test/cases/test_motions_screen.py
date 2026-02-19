CASES = {
    # ── H - top of screen ────────────────────────────────────
    "H_basic_short_file": {
        "keys": "H",
        "initial": "aaa\nbbb\nccc\nddd\neee",
    },
    "H_from_bottom_of_short_file": {
        "keys": "GH",
        "initial": "aaa\nbbb\nccc\nddd\neee",
    },
    "H_single_line": {
        "keys": "H",
        "initial": "hello world",
    },
    "H_from_middle_short": {
        "keys": "3jH",
        "initial": "aaa\nbbb\nccc\nddd\neee\nfff",
    },
    "H_indented_first_line": {
        "keys": "jH",
        "initial": "    indented\nnormal\nthird",
    },
    "H_tab_indented": {
        "keys": "jH",
        "initial": "\tindented\nnormal\nthird",
    },
    "H_exactly_18_lines": {
        "keys": "GH",
        "initial": "L01\nL02\nL03\nL04\nL05\nL06\nL07\nL08\nL09\nL10\nL11\nL12\nL13\nL14\nL15\nL16\nL17\nL18",
    },
    "H_empty_buffer": {
        "keys": "H",
        "initial": "",
    },
    "H_two_lines": {
        "keys": "jH",
        "initial": "first\nsecond",
    },

    # ── H with count ─────────────────────────────────────────
    "H_count_2": {
        "keys": "G2H",
        "initial": "aaa\nbbb\nccc\nddd\neee\nfff",
    },
    "H_count_3": {
        "keys": "G3H",
        "initial": "aaa\nbbb\nccc\nddd\neee\nfff",
    },
    "H_count_5": {
        "keys": "G5H",
        "initial": "L01\nL02\nL03\nL04\nL05\nL06\nL07\nL08\nL09\nL10",
    },
    "H_count_exceeds_lines": {
        "keys": "10H",
        "initial": "aaa\nbbb\nccc",
    },
    "H_count_1_same_as_H": {
        "keys": "G1H",
        "initial": "aaa\nbbb\nccc\nddd\neee",
    },
    "H_count_2_indented": {
        "keys": "G2H",
        "initial": "aaa\n    indented\nccc\nddd\neee",
    },
    "H_count_with_18_lines": {
        "keys": "G5H",
        "initial": "L01\nL02\nL03\nL04\nL05\nL06\nL07\nL08\nL09\nL10\nL11\nL12\nL13\nL14\nL15\nL16\nL17\nL18",
    },
    "H_count_to_last_visible": {
        "keys": "18H",
        "initial": "L01\nL02\nL03\nL04\nL05\nL06\nL07\nL08\nL09\nL10\nL11\nL12\nL13\nL14\nL15\nL16\nL17\nL18",
    },

    # ── M - middle of screen ─────────────────────────────────
    "M_basic_short_file": {
        "keys": "M",
        "initial": "aaa\nbbb\nccc\nddd\neee",
    },
    "M_from_bottom": {
        "keys": "GM",
        "initial": "aaa\nbbb\nccc\nddd\neee",
    },
    "M_single_line": {
        "keys": "M",
        "initial": "hello",
    },
    "M_two_lines": {
        "keys": "M",
        "initial": "first\nsecond",
    },
    "M_three_lines": {
        "keys": "M",
        "initial": "aaa\nbbb\nccc",
    },
    "M_four_lines": {
        "keys": "M",
        "initial": "aaa\nbbb\nccc\nddd",
    },
    "M_five_lines": {
        "keys": "M",
        "initial": "aaa\nbbb\nccc\nddd\neee",
    },
    "M_six_lines": {
        "keys": "jM",
        "initial": "aaa\nbbb\nccc\nddd\neee\nfff",
    },
    "M_seven_lines": {
        "keys": "M",
        "initial": "aa\nbb\ncc\ndd\nee\nff\ngg",
    },
    "M_exactly_18_lines": {
        "keys": "M",
        "initial": "L01\nL02\nL03\nL04\nL05\nL06\nL07\nL08\nL09\nL10\nL11\nL12\nL13\nL14\nL15\nL16\nL17\nL18",
    },
    "M_indented_middle": {
        "keys": "M",
        "initial": "aaa\nbbb\n    middle\nddd\neee",
    },
    "M_empty_buffer": {
        "keys": "M",
        "initial": "",
    },
    "M_10_lines": {
        "keys": "M",
        "initial": "L01\nL02\nL03\nL04\nL05\nL06\nL07\nL08\nL09\nL10",
    },
    "M_tab_indented_middle": {
        "keys": "M",
        "initial": "aaa\nbbb\n\tindented\nddd\neee",
    },

    # ── L - bottom of screen ─────────────────────────────────
    "L_basic_short_file": {
        "keys": "L",
        "initial": "aaa\nbbb\nccc\nddd\neee",
    },
    "L_from_top": {
        "keys": "L",
        "initial": "aaa\nbbb\nccc\nddd\neee\nfff",
    },
    "L_single_line": {
        "keys": "L",
        "initial": "hello",
    },
    "L_two_lines": {
        "keys": "L",
        "initial": "first\nsecond",
    },
    "L_exactly_18_lines": {
        "keys": "L",
        "initial": "L01\nL02\nL03\nL04\nL05\nL06\nL07\nL08\nL09\nL10\nL11\nL12\nL13\nL14\nL15\nL16\nL17\nL18",
    },
    "L_indented_last_line": {
        "keys": "L",
        "initial": "aaa\nbbb\nccc\n    indented",
    },
    "L_empty_buffer": {
        "keys": "L",
        "initial": "",
    },
    "L_tab_indented_last": {
        "keys": "L",
        "initial": "aaa\nbbb\n\ttabbed",
    },

    # ── L with count ─────────────────────────────────────────
    "L_count_2": {
        "keys": "2L",
        "initial": "aaa\nbbb\nccc\nddd\neee\nfff",
    },
    "L_count_3": {
        "keys": "3L",
        "initial": "aaa\nbbb\nccc\nddd\neee\nfff",
    },
    "L_count_5": {
        "keys": "5L",
        "initial": "L01\nL02\nL03\nL04\nL05\nL06\nL07\nL08\nL09\nL10",
    },
    "L_count_exceeds_lines": {
        "keys": "10L",
        "initial": "aaa\nbbb\nccc",
    },
    "L_count_1_same_as_L": {
        "keys": "1L",
        "initial": "aaa\nbbb\nccc\nddd\neee",
    },
    "L_count_2_indented": {
        "keys": "2L",
        "initial": "aaa\nbbb\nccc\n    indented\neee",
    },
    "L_count_with_18_lines": {
        "keys": "5L",
        "initial": "L01\nL02\nL03\nL04\nL05\nL06\nL07\nL08\nL09\nL10\nL11\nL12\nL13\nL14\nL15\nL16\nL17\nL18",
    },
    "L_count_to_top": {
        "keys": "18L",
        "initial": "L01\nL02\nL03\nL04\nL05\nL06\nL07\nL08\nL09\nL10\nL11\nL12\nL13\nL14\nL15\nL16\nL17\nL18",
    },

    # ── Combined H/M/L ────────────────────────────────────────
    "H_then_L": {
        "keys": "HL",
        "initial": "aaa\nbbb\nccc\nddd\neee\nfff",
    },
    "L_then_H": {
        "keys": "LH",
        "initial": "aaa\nbbb\nccc\nddd\neee\nfff",
    },
    "H_then_M": {
        "keys": "HM",
        "initial": "aaa\nbbb\nccc\nddd\neee\nfff",
    },
    "M_then_L": {
        "keys": "ML",
        "initial": "aaa\nbbb\nccc\nddd\neee\nfff",
    },
    "L_then_M_then_H": {
        "keys": "LMH",
        "initial": "aaa\nbbb\nccc\nddd\neee\nfff\nggg",
    },
    "H_M_L_indented_lines": {
        "keys": "HML",
        "initial": "  aa\n  bb\n  cc\n  dd\n  ee",
    },
    "H_M_L_mixed_indent": {
        "keys": "LMH",
        "initial": "    top\n  mid1\n      mid2\n\tbottom",
    },
}
