CASES = {
    # === Basic undo with x (delete char) ===
    "undo_x_single_char": {"keys": "xu", "initial": "hello"},
    "undo_x_middle": {"keys": "llxu", "initial": "abcdef"},
    "undo_x_end_of_line": {"keys": "$xu", "initial": "world"},
    "undo_x_single_char_line": {"keys": "xu", "initial": "a\nb"},
    "undo_x_restores_cursor": {"keys": "llxu", "initial": "foobar"},
    "undo_two_x_one_undo": {"keys": "xxu", "initial": "abcdef"},
    "undo_two_x_two_undo": {"keys": "xxuu", "initial": "abcdef"},

    # === Undo with dd (delete line) ===
    "undo_dd_single_line_buffer": {"keys": "ddu", "initial": "only line"},
    "undo_dd_first_line": {"keys": "ddu", "initial": "first\nsecond\nthird"},
    "undo_dd_middle_line": {"keys": "jddu", "initial": "aaa\nbbb\nccc"},
    "undo_dd_last_line": {"keys": "Gddu", "initial": "one\ntwo\nthree"},
    "undo_dd_restores_content": {"keys": "jddu", "initial": "alpha\nbravo\ncharlie"},
    "undo_two_dd_two_undo": {"keys": "ddjdduu", "initial": "a\nb\nc\nd"},
    "undo_3dd": {"keys": "3ddu", "initial": "line1\nline2\nline3\nline4"},

    # === Undo with dw (delete word) ===
    "undo_dw_first_word": {"keys": "dwu", "initial": "hello world"},
    "undo_dw_middle": {"keys": "wdwu", "initial": "one two three"},
    "undo_dw_last_word": {"keys": "wdwu", "initial": "foo bar"},
    "undo_d2w": {"keys": "d2wu", "initial": "one two three four"},

    # === Undo after insert ===
    "undo_insert_text": {"keys": "iHI\x1bu", "initial": "hello"},
    "undo_insert_middle": {"keys": "lliFOO\x1bu", "initial": "abcd"},
    "undo_append_text": {"keys": "aXY\x1bu", "initial": "ab"},
    "undo_A_append_end": {"keys": "AEND\x1bu", "initial": "start"},
    "undo_I_insert_start": {"keys": "IBEGIN\x1bu", "initial": "end"},
    "undo_insert_multichar": {"keys": "ihello world\x1bu", "initial": ""},
    "undo_insert_empty_buffer": {"keys": "itext\x1bu", "initial": ""},

    # === Undo after o (open line) ===
    "undo_o_basic": {"keys": "onew line\x1bu", "initial": "first"},
    "undo_O_above": {"keys": "Oabove\x1bu", "initial": "below"},
    "undo_o_middle": {"keys": "jonew\x1bu", "initial": "aaa\nbbb\nccc"},
    "undo_o_empty_insert": {"keys": "o\x1bu", "initial": "hello"},

    # === Undo after p (paste) ===
    "undo_p_after_dd": {"keys": "ddpu", "initial": "first\nsecond\nthird"},
    "undo_p_after_x": {"keys": "xpu", "initial": "abcdef"},
    "undo_p_after_dw": {"keys": "dwpu", "initial": "hello world"},
    "undo_P_after_dd": {"keys": "ddPu", "initial": "aaa\nbbb"},

    # === Undo after r (replace) ===
    "undo_r_basic": {"keys": "rZu", "initial": "abcdef"},
    "undo_r_middle": {"keys": "llrXu", "initial": "foobar"},
    "undo_r_digit": {"keys": "r9u", "initial": "hello"},

    # === Undo after ~ (case toggle) ===
    "undo_tilde_basic": {"keys": "~u", "initial": "hello"},
    "undo_tilde_upper": {"keys": "~u", "initial": "Hello"},
    "undo_3_tilde": {"keys": "3~u", "initial": "hello"},
    "undo_tilde_sequence": {"keys": "~~u", "initial": "abcd"},
    "undo_tilde_sequence_two_undo": {"keys": "~~uu", "initial": "abcd"},

    # === Undo after J (join) ===
    "undo_J_basic": {"keys": "Ju", "initial": "hello\nworld"},
    "undo_J_three_lines": {"keys": "3Ju", "initial": "a\nb\nc\nd"},
    "undo_J_preserves_lines": {"keys": "Ju", "initial": "first\nsecond\nthird"},

    # === Undo after >> (indent) ===
    "undo_indent_basic": {"keys": ">>u", "initial": "hello"},
    "undo_indent_multiple": {"keys": "2>>u", "initial": "aaa\nbbb\nccc"},
    "undo_dedent_basic": {"keys": "<<u", "initial": "\thello"},

    # === Multiple undo ===
    "undo_three_changes": {"keys": "x~rZuuu", "initial": "abcdef"},
    "undo_all_back_to_original": {
        "keys": "dd>>Juuu",
        "initial": "aaa\nbbb\nccc\nddd"
    },
    "undo_five_x": {"keys": "xxxxxuuuuu", "initial": "abcdef"},
    "undo_interleaved": {"keys": "xuxu", "initial": "abcdef"},

    # === Redo (Ctrl-R) ===
    "redo_after_undo_x": {"keys": "xu\x12", "initial": "hello"},
    "redo_after_undo_dd": {"keys": "ddu\x12", "initial": "aaa\nbbb"},
    "redo_after_undo_dw": {"keys": "dwu\x12", "initial": "hello world"},
    "redo_after_undo_insert": {"keys": "ifoo\x1bu\x12", "initial": "bar"},
    "redo_after_undo_r": {"keys": "rXu\x12", "initial": "abcd"},
    "redo_after_undo_tilde": {"keys": "~u\x12", "initial": "hello"},
    "redo_after_undo_J": {"keys": "Ju\x12", "initial": "aaa\nbbb"},
    "redo_after_undo_indent": {"keys": ">>u\x12", "initial": "hello"},

    # === Redo multiple ===
    "redo_two_undos": {"keys": "xxuu\x12\x12", "initial": "abcdef"},
    "redo_three_undos": {"keys": "xxxuuu\x12\x12\x12", "initial": "abcdef"},
    "redo_partial": {"keys": "xxxuuu\x12", "initial": "abcdef"},

    # === Undo then new change clears redo ===
    "undo_new_change_clears_redo": {
        "keys": "xuiZ\x1b\x12",
        "initial": "abcdef"
    },
    "undo_new_dd_clears_redo": {
        "keys": "dduddu",
        "initial": "aaa\nbbb\nccc"
    },

    # === Count undo/redo ===
    "count_3u": {"keys": "xxx3u", "initial": "abcdef"},
    "count_2u": {"keys": "xxxx2u", "initial": "abcdefgh"},
    "count_2_redo": {"keys": "xxxuuu2\x12", "initial": "abcdef"},
    "count_3_redo": {"keys": "xxxxuuuu3\x12", "initial": "abcdefgh"},
    "count_5u_only_3_avail": {"keys": "xxx5u", "initial": "abcdef"},
    "count_5_redo_only_2_avail": {"keys": "xxuu5\x12", "initial": "abcdef"},

    # === Edge: nothing to undo/redo ===
    "undo_nothing": {"keys": "u", "initial": "hello"},
    "undo_nothing_empty": {"keys": "u", "initial": ""},
    "redo_nothing": {"keys": "\x12", "initial": "hello"},
    "redo_nothing_empty": {"keys": "\x12", "initial": ""},
    "undo_after_all_undone": {"keys": "xuu", "initial": "hello"},
    "redo_after_all_redone": {"keys": "xu\x12\x12", "initial": "hello"},

    # === Undo after visual delete ===
    "undo_visual_delete_char": {
        "keys": "vlld\x1bu",
        "initial": "abcdef"
    },
    "undo_visual_delete_word": {
        "keys": "vedu",
        "initial": "hello world"
    },
    "undo_visual_line_delete": {
        "keys": "Vdu",
        "initial": "first\nsecond\nthird"
    },
    "undo_visual_line_two": {
        "keys": "Vjdu",
        "initial": "aaa\nbbb\nccc\nddd"
    },

    # === Cursor position after undo/redo ===
    "cursor_pos_undo_dd_first": {"keys": "ddu", "initial": "aaa\nbbb\nccc"},
    "cursor_pos_undo_x_mid": {"keys": "lllxu", "initial": "abcdef"},
    "cursor_pos_undo_insert": {
        "keys": "llihello\x1bu",
        "initial": "abcdef"
    },
    "cursor_pos_redo_x": {"keys": "xu\x12", "initial": "abcdef"},
    "cursor_pos_redo_dd": {
        "keys": "jddu\x12",
        "initial": "aaa\nbbb\nccc"
    },
    "cursor_pos_redo_dw": {
        "keys": "dwu\x12",
        "initial": "hello world"
    },
    "cursor_pos_redo_insert": {
        "keys": "ifoo\x1bu\x12",
        "initial": "bar"
    },
    "cursor_pos_redo_tilde": {
        "keys": "~u\x12",
        "initial": "hello"
    },
    "cursor_pos_redo_J": {
        "keys": "Ju\x12",
        "initial": "aaa\nbbb"
    },
    "cursor_pos_redo_r": {
        "keys": "rXu\x12",
        "initial": "abcd"
    },
    "cursor_pos_redo_indent": {
        "keys": ">>u\x12",
        "initial": "hello"
    },
    "cursor_pos_redo_dedent": {
        "keys": "<<u\x12",
        "initial": "\thello"
    },
}
