CASES = {
    # ==========================================
    # i - insert before cursor
    # ==========================================
    "i_on_empty_line": {
        "keys": "iHello\x1b",
        "initial": "",
    },
    "i_at_start_of_line": {
        "keys": "iHello \x1b",
        "initial": "world",
    },
    "i_at_end_of_line": {
        "keys": "$iX\x1b",
        "initial": "abcde",
    },
    "i_in_middle_of_line": {
        "keys": "lliINSERT\x1b",
        "initial": "abcde",
    },
    "i_on_line_with_leading_spaces": {
        "keys": "iX\x1b",
        "initial": "    indented",
    },
    "i_on_line_with_tabs": {
        "keys": "iX\x1b",
        "initial": "\ttabbed text",
    },
    "i_multiline_first_line": {
        "keys": "iSTART\x1b",
        "initial": "line one\nline two\nline three",
    },
    "i_multiline_second_line": {
        "keys": "jiMID\x1b",
        "initial": "line one\nline two\nline three",
    },
    "i_type_multiple_chars": {
        "keys": "iHello World 123\x1b",
        "initial": "",
    },
    "i_type_spaces": {
        "keys": "i   \x1b",
        "initial": "text",
    },
    "i_type_single_char": {
        "keys": "iX\x1b",
        "initial": "abc",
    },

    # ==========================================
    # I - insert at first non-blank
    # ==========================================
    "I_on_empty_line": {
        "keys": "IHello\x1b",
        "initial": "",
    },
    "I_at_start_no_indent": {
        "keys": "IPrefix: \x1b",
        "initial": "some text here",
    },
    "I_with_leading_spaces": {
        "keys": "ISTART\x1b",
        "initial": "    indented line",
    },
    "I_with_leading_tabs": {
        "keys": "ISTART\x1b",
        "initial": "\tindented line",
    },
    "I_with_mixed_whitespace": {
        "keys": "IX\x1b",
        "initial": "  \t  mixed indent",
    },
    "I_cursor_in_middle": {
        "keys": "llllIBEGIN\x1b",
        "initial": "    hello world",
    },
    "I_cursor_at_end": {
        "keys": "$IFRONT\x1b",
        "initial": "    text here",
    },
    "I_on_blank_line_spaces": {
        "keys": "IX\x1b",
        "initial": "    ",
    },
    "I_multiline_second_line": {
        "keys": "jISTART\x1b",
        "initial": "first\n    second\nthird",
    },

    # ==========================================
    # a - append after cursor
    # ==========================================
    "a_on_empty_line": {
        "keys": "aHello\x1b",
        "initial": "",
    },
    "a_at_start_of_line": {
        "keys": "aX\x1b",
        "initial": "abcde",
    },
    "a_at_end_of_line": {
        "keys": "$aEND\x1b",
        "initial": "abcde",
    },
    "a_in_middle_of_line": {
        "keys": "llaINS\x1b",
        "initial": "abcde",
    },
    "a_on_line_with_leading_spaces": {
        "keys": "aX\x1b",
        "initial": "    indented",
    },
    "a_on_line_with_tabs": {
        "keys": "aX\x1b",
        "initial": "\ttabbed",
    },
    "a_multiline_first_line": {
        "keys": "aAPP\x1b",
        "initial": "line one\nline two\nline three",
    },
    "a_multiline_second_line": {
        "keys": "jaAPP\x1b",
        "initial": "line one\nline two\nline three",
    },
    "a_type_multiple_chars": {
        "keys": "aHello World\x1b",
        "initial": "X",
    },
    "a_type_spaces": {
        "keys": "a   \x1b",
        "initial": "text",
    },
    "a_single_char_line": {
        "keys": "aY\x1b",
        "initial": "X",
    },

    # ==========================================
    # A - append at end of line
    # ==========================================
    "A_on_empty_line": {
        "keys": "AHello\x1b",
        "initial": "",
    },
    "A_at_start_of_line": {
        "keys": "A END\x1b",
        "initial": "text",
    },
    "A_cursor_in_middle": {
        "keys": "A!!!\x1b",
        "initial": "hello world",
    },
    "A_with_leading_spaces": {
        "keys": "A END\x1b",
        "initial": "    indented",
    },
    "A_with_tabs": {
        "keys": "A END\x1b",
        "initial": "\ttabbed",
    },
    "A_multiline_second_line": {
        "keys": "jA END\x1b",
        "initial": "first\nsecond\nthird",
    },
    "A_on_blank_line_spaces": {
        "keys": "Atext\x1b",
        "initial": "    ",
    },
    "A_type_multiple_chars": {
        "keys": "A appended stuff\x1b",
        "initial": "start",
    },

    # ==========================================
    # o - open line below
    # ==========================================
    "o_on_empty_line": {
        "keys": "obelow\x1b",
        "initial": "",
    },
    "o_single_line": {
        "keys": "onew line\x1b",
        "initial": "first line",
    },
    "o_first_of_multiline": {
        "keys": "oinserted\x1b",
        "initial": "line one\nline two\nline three",
    },
    "o_middle_of_multiline": {
        "keys": "joinserted\x1b",
        "initial": "line one\nline two\nline three",
    },
    "o_last_of_multiline": {
        "keys": "jjoinserted\x1b",
        "initial": "line one\nline two\nline three",
    },
    "o_with_leading_spaces": {
        "keys": "onew\x1b",
        "initial": "    indented",
    },
    "o_type_multiple_chars": {
        "keys": "oHello World\x1b",
        "initial": "above",
    },
    "o_empty_line_enter": {
        "keys": "o\x1b",
        "initial": "text",
    },
    "o_on_line_with_tabs": {
        "keys": "onew\x1b",
        "initial": "\ttabbed line",
    },

    # ==========================================
    # O - open line above
    # ==========================================
    "O_on_empty_line": {
        "keys": "Oabove\x1b",
        "initial": "",
    },
    "O_single_line": {
        "keys": "Onew line\x1b",
        "initial": "original",
    },
    "O_first_of_multiline": {
        "keys": "Oinserted\x1b",
        "initial": "line one\nline two\nline three",
    },
    "O_middle_of_multiline": {
        "keys": "jOinserted\x1b",
        "initial": "line one\nline two\nline three",
    },
    "O_last_of_multiline": {
        "keys": "jjOinserted\x1b",
        "initial": "line one\nline two\nline three",
    },
    "O_with_leading_spaces": {
        "keys": "Onew\x1b",
        "initial": "    indented",
    },
    "O_type_multiple_chars": {
        "keys": "OHello World\x1b",
        "initial": "below",
    },
    "O_empty_line_only": {
        "keys": "O\x1b",
        "initial": "text",
    },

    # ==========================================
    # Count prefix with insert commands
    # ==========================================
    "count_3i_text": {
        "keys": "3iHa\x1b",
        "initial": "",
    },
    "count_2i_word": {
        "keys": "2iab\x1b",
        "initial": "",
    },
    "count_5i_single_char": {
        "keys": "5iX\x1b",
        "initial": "",
    },
    "count_3i_with_existing": {
        "keys": "3iHa\x1b",
        "initial": "END",
    },
    "count_2I_at_front": {
        "keys": "2IHa\x1b",
        "initial": "    text",
    },
    "count_3a_after_cursor": {
        "keys": "3axy\x1b",
        "initial": "abc",
    },
    "count_2A_at_end": {
        "keys": "2A!\x1b",
        "initial": "hello",
    },
    "count_3o_lines_below": {
        "keys": "3onew\x1b",
        "initial": "top",
    },
    "count_2O_lines_above": {
        "keys": "2Onew\x1b",
        "initial": "bottom",
    },
    "count_1i_no_effect": {
        "keys": "1iX\x1b",
        "initial": "abc",
    },
    "count_3i_with_space": {
        "keys": "3i- \x1b",
        "initial": "",
    },

    # ==========================================
    # Backspace (\x08) in insert mode
    # ==========================================
    "bs_delete_last_typed": {
        "keys": "iabc\x08\x1b",
        "initial": "",
    },
    "bs_delete_all_typed": {
        "keys": "ia\x08\x1b",
        "initial": "text",
    },
    "bs_multiple_deletes": {
        "keys": "iabcde\x08\x08\x08\x1b",
        "initial": "",
    },
    "bs_at_start_of_first_line": {
        "keys": "i\x08\x1b",
        "initial": "hello",
    },
    "bs_join_with_previous_line": {
        "keys": "ji\x08\x1b",
        "initial": "first\nsecond",
    },
    "bs_after_enter": {
        "keys": "ifoo\r\x08\x1b",
        "initial": "",
    },
    "bs_delete_past_insert_point": {
        "keys": "lli\x08\x1b",
        "initial": "abcde",
    },
    "bs_delete_multiple_past_insert": {
        "keys": "llli\x08\x08\x1b",
        "initial": "abcde",
    },
    "bs_after_a_command": {
        "keys": "laXY\x08\x1b",
        "initial": "abc",
    },
    "bs_empty_line_join_up": {
        "keys": "jji\x08\x1b",
        "initial": "first\n\nthird",
    },
    "bs_o_then_backspace": {
        "keys": "o\x08\x1b",
        "initial": "line one",
    },
    "bs_type_and_delete_all": {
        "keys": "iHello\x08\x08\x08\x08\x08\x1b",
        "initial": "X",
    },
    "bs_on_tab_char": {
        "keys": "A\x08\x1b",
        "initial": "\ttext",
    },

    # ==========================================
    # Enter (\r) in insert mode
    # ==========================================
    "enter_split_line_middle": {
        "keys": "llli\r\x1b",
        "initial": "abcdef",
    },
    "enter_at_start_of_line": {
        "keys": "i\r\x1b",
        "initial": "hello",
    },
    "enter_at_end_of_line": {
        "keys": "A\r\x1b",
        "initial": "hello",
    },
    "enter_type_before_and_after": {
        "keys": "ifoo\rbar\x1b",
        "initial": "",
    },
    "enter_multiple_blank_lines": {
        "keys": "i\r\r\r\x1b",
        "initial": "text",
    },
    "enter_on_empty_line": {
        "keys": "i\r\x1b",
        "initial": "",
    },
    "enter_after_o": {
        "keys": "ofirst\rsecond\x1b",
        "initial": "above",
    },
    "enter_in_middle_of_multiline": {
        "keys": "jllli\r\x1b",
        "initial": "line one\nabcdef\nline three",
    },
    "enter_multiple_with_text": {
        "keys": "ione\rtwo\rthree\x1b",
        "initial": "",
    },
    "enter_at_end_then_type": {
        "keys": "A\rnew line\x1b",
        "initial": "first",
    },

    # ==========================================
    # Cursor position after Escape
    # ==========================================
    "esc_after_i_moves_back": {
        "keys": "iab\x1b",
        "initial": "XY",
    },
    "esc_after_i_at_col0": {
        "keys": "i\x1b",
        "initial": "hello",
    },
    "esc_after_a_on_last_char": {
        "keys": "$aZ\x1b",
        "initial": "abc",
    },
    "esc_after_a_mid_line": {
        "keys": "laZ\x1b",
        "initial": "abcde",
    },
    "esc_after_o_with_text": {
        "keys": "oXYZ\x1b",
        "initial": "above",
    },
    "esc_after_O_with_text": {
        "keys": "OXYZ\x1b",
        "initial": "below",
    },
    "esc_after_I_with_text": {
        "keys": "IXYZ\x1b",
        "initial": "    hello",
    },
    "esc_after_A_with_text": {
        "keys": "AXYZ\x1b",
        "initial": "hello",
    },
    "esc_immediately_after_i": {
        "keys": "lli\x1b",
        "initial": "abcde",
    },
    "esc_immediately_after_a": {
        "keys": "lla\x1b",
        "initial": "abcde",
    },
    "esc_immediately_after_o": {
        "keys": "o\x1b",
        "initial": "hello",
    },
    "esc_immediately_after_O": {
        "keys": "O\x1b",
        "initial": "hello",
    },

    # ==========================================
    # Edge cases and combinations
    # ==========================================
    "i_then_esc_then_i_again": {
        "keys": "iAB\x1biCD\x1b",
        "initial": "XY",
    },
    "a_then_esc_then_a_again": {
        "keys": "aAB\x1baCD\x1b",
        "initial": "XY",
    },
    "i_then_esc_then_a": {
        "keys": "iX\x1baY\x1b",
        "initial": "abc",
    },
    "o_then_esc_then_o": {
        "keys": "ofirst\x1bosecond\x1b",
        "initial": "top",
    },
    "O_then_esc_then_O": {
        "keys": "Ofirst\x1bOsecond\x1b",
        "initial": "bottom",
    },
    "i_long_text": {
        "keys": "iThe quick brown fox jumps\x1b",
        "initial": "",
    },
    "a_on_empty_then_text": {
        "keys": "aHello World\x1b",
        "initial": "",
    },
    "i_special_chars": {
        "keys": "i!@#$%\x1b",
        "initial": "text",
    },
    "i_digits": {
        "keys": "i12345\x1b",
        "initial": "abc",
    },
    "i_mixed_text_and_bs": {
        "keys": "iHelo\x08lo\x1b",
        "initial": "",
    },
    "a_mixed_text_and_bs": {
        "keys": "aXYZ\x08\x08AB\x1b",
        "initial": "M",
    },
    "i_enter_then_bs": {
        "keys": "i\r\x08\x1b",
        "initial": "hello",
    },
    "count_3i_with_enter": {
        "keys": "3ia\r\x1b",
        "initial": "",
    },
    "o_on_last_line_of_buffer": {
        "keys": "GonewLast\x1b",
        "initial": "line one\nline two\nline three",
    },
    "O_on_first_line_of_buffer": {
        "keys": "OnewFirst\x1b",
        "initial": "line one\nline two\nline three",
    },
    "i_after_dollar": {
        "keys": "$iX\x1b",
        "initial": "hello",
    },
    "a_at_position_zero": {
        "keys": "0aX\x1b",
        "initial": "hello",
    },
    "I_after_dollar": {
        "keys": "$IFRONT\x1b",
        "initial": "hello",
    },
    "A_from_position_zero": {
        "keys": "0AEND\x1b",
        "initial": "hello",
    },

    # ==========================================
    # gi - insert at last insert position
    # ==========================================
    "gi_basic": {
        "keys": "iHello\x1bgggi World\x1b",
        "initial": "line one\nline two",
    },
    "gi_after_append": {
        "keys": "AEND\x1bjjgi MORE\x1b",
        "initial": "first\nsecond\nthird",
    },
    "gi_after_o_open_below": {
        "keys": "onew line\x1bgggi extra\x1b",
        "initial": "first\nlast",
    },
    "gi_no_previous_insert": {
        "keys": "gi",
        "initial": "hello",
    },
    "gi_after_insert_middle": {
        "keys": "lliMID\x1bgggiADD\x1b",
        "initial": "abcde",
    },
    "gi_after_cw": {
        "keys": "cwNEW\x1bgggiMORE\x1b",
        "initial": "old text here",
    },
    "gi_after_s_substitute": {
        "keys": "llsX\x1bgggiY\x1b",
        "initial": "abcde",
    },
    "gi_preserves_col_past_eol": {
        "keys": "ALONG\x1bjgiX\x1b",
        "initial": "aaa\nb",
    },

    # ==========================================
    # gI - insert at column 0
    # ==========================================
    "gI_basic": {
        "keys": "gISTART\x1b",
        "initial": "    indented",
    },
    "gI_on_empty_line": {
        "keys": "gItext\x1b",
        "initial": "",
    },
    "gI_multiline": {
        "keys": "jgIFRONT\x1b",
        "initial": "line one\n    line two",
    },
}
