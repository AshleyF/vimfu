"""Basic motion tests: h, j, k, l with counts, boundaries, edge cases."""

CASES = {
    # ── h (left) ──
    "h_basic": {"keys": "lh", "initial": "abcdef"},
    "h_at_col0": {"keys": "h", "initial": "abcdef"},
    "h_count_2": {"keys": "$2h", "initial": "abcdef"},
    "h_count_3": {"keys": "$3h", "initial": "abcdef"},
    "h_count_exceeds": {"keys": "ll10h", "initial": "abcdef"},
    "h_on_empty": {"keys": "h", "initial": ""},
    "h_single_char": {"keys": "h", "initial": "x"},
    "h_from_end_short_line": {"keys": "$h", "initial": "ab"},
    "h_count_1": {"keys": "$1h", "initial": "abcdef"},
    "h_count_5": {"keys": "$5h", "initial": "abcdef"},

    # ── l (right) ──
    "l_basic": {"keys": "l", "initial": "abcdef"},
    "l_at_end": {"keys": "$l", "initial": "abcdef"},
    "l_count_2": {"keys": "2l", "initial": "abcdef"},
    "l_count_3": {"keys": "3l", "initial": "abcdef"},
    "l_count_exceeds": {"keys": "20l", "initial": "abcdef"},
    "l_on_empty": {"keys": "l", "initial": ""},
    "l_single_char": {"keys": "l", "initial": "x"},
    "l_count_exact_to_end": {"keys": "4l", "initial": "abcde"},
    "l_count_1": {"keys": "1l", "initial": "abcdef"},

    # ── j (down) ──
    "j_basic": {"keys": "j", "initial": "line1\nline2\nline3"},
    "j_at_last_line": {"keys": "Gj", "initial": "line1\nline2"},
    "j_count_2": {"keys": "2j", "initial": "a\nb\nc\nd"},
    "j_count_exceeds": {"keys": "20j", "initial": "a\nb\nc"},
    "j_clamps_col": {"keys": "4lj", "initial": "Hello World\nHi"},
    "j_on_empty": {"keys": "j", "initial": ""},
    "j_single_line": {"keys": "j", "initial": "only"},
    "j_preserves_col": {"keys": "3lj", "initial": "abcdef\nabcdef"},
    "j_to_shorter_line": {"keys": "4ljj", "initial": "abcdef\nab\nabcdef"},
    "j_count_3": {"keys": "3j", "initial": "a\nb\nc\nd\ne"},
    "j_with_empty_lines": {"keys": "j", "initial": "abc\n\ndef"},
    "j_to_empty_line": {"keys": "3lj", "initial": "abcd\n\nefgh"},
    "j_past_empty_to_content": {"keys": "3l2j", "initial": "abcd\n\nefgh"},
    "j_count_1": {"keys": "1j", "initial": "a\nb\nc"},

    # ── k (up) ──
    "k_basic": {"keys": "jk", "initial": "line1\nline2"},
    "k_at_first_line": {"keys": "k", "initial": "line1\nline2"},
    "k_count_2": {"keys": "G2k", "initial": "a\nb\nc\nd"},
    "k_count_exceeds": {"keys": "G20k", "initial": "a\nb\nc"},
    "k_clamps_col": {"keys": "G4lk", "initial": "Hi\nHello World"},
    "k_on_empty": {"keys": "k", "initial": ""},
    "k_preserves_col": {"keys": "j3lk", "initial": "abcdef\nabcdef"},
    "k_to_shorter_line": {"keys": "2j4lk", "initial": "abcdef\nab\nabcdef"},
    "k_count_1": {"keys": "j1k", "initial": "a\nb\nc"},

    # ── Count multiplied movements ──
    "h_count_at_start": {"keys": "5h", "initial": "abcdef"},
    "l_count_at_end": {"keys": "$5l", "initial": "abcdef"},
    "j_count_at_bottom": {"keys": "G5j", "initial": "a\nb\nc"},
    "k_count_at_top": {"keys": "5k", "initial": "a\nb\nc"},

    # ── Column memory across movements ──
    "jk_col_memory": {"keys": "4ljjk", "initial": "abcdef\nab\nabcdef"},
    "j_col_memory_empty": {"keys": "3lj", "initial": "abcd\n"},
    "k_col_memory_empty": {"keys": "jk", "initial": "\nabcdef"},
    "jj_through_varying_lengths": {
        "keys": "5ljj",
        "initial": "abcdefgh\nab\nabcdefgh",
    },
    "jk_round_trip": {"keys": "3ljk", "initial": "abcdef\nabcdef"},

    # ── Multiple h/l in sequence ──
    "lll_sequence": {"keys": "lll", "initial": "abcdef"},
    "hhh_sequence": {"keys": "$hhh", "initial": "abcdef"},
    "lhlh_zigzag": {"keys": "lhlh", "initial": "abcdef"},
    "jjkk_zigzag": {"keys": "jjkk", "initial": "a\nb\nc\nd"},

    # ── Movement on lines with special content ──
    "l_on_spaces": {"keys": "3l", "initial": "   spaces"},
    "j_on_blank_lines": {"keys": "jj", "initial": "\n\n\nabc"},
    "l_on_tab_line": {"keys": "l", "initial": "\tabc"},
    "j_with_tabs": {"keys": "j", "initial": "\tabc\n\tdef"},

    # ── Boundary: very long line ──
    "l_long_line": {"keys": "35l", "initial": "a" + "b" * 38},
    "h_long_line": {"keys": "$35h", "initial": "a" + "b" * 38},

    # ── Boundary: many lines ──
    "j_many_lines": {
        "keys": "15j",
        "initial": "\n".join(f"line {i}" for i in range(20)),
    },
    "k_many_lines": {
        "keys": "G15k",
        "initial": "\n".join(f"line {i}" for i in range(20)),
    },
}
