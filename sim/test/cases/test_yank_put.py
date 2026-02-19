CASES = {
    # ── yw (yank word) then put ──────────────────────────────
    "yw_p_beginning_of_line": {
        "keys": "ywp",
        "initial": "hello world",
    },
    "yw_p_middle_of_word": {
        "keys": "llywp",
        "initial": "hello world",
    },
    "yw_P_before_cursor": {
        "keys": "ywP",
        "initial": "hello world",
    },
    "yw_p_on_last_word": {
        "keys": "wywp",
        "initial": "hello world",
    },
    "yw_p_single_char_word": {
        "keys": "wywp",
        "initial": "a b c d",
    },
    "y2w_p_yank_two_words": {
        "keys": "y2wp",
        "initial": "one two three four",
    },
    "y3w_p_yank_three_words": {
        "keys": "y3wp",
        "initial": "alpha beta gamma delta",
    },

    # ── yW (yank WORD) then put ──────────────────────────────
    "yW_p_with_punctuation": {
        "keys": "yWp",
        "initial": "hello-world foo bar",
    },
    "yW_p_mixed_punct": {
        "keys": "yWp",
        "initial": "file.txt other.doc",
    },
    "y2W_p_two_WORDS": {
        "keys": "y2Wp",
        "initial": "one-a two-b three-c",
    },

    # ── yb (yank word backward) then put ─────────────────────
    "yb_p_from_second_word": {
        "keys": "wybp",
        "initial": "hello world",
    },
    "yb_p_from_third_word": {
        "keys": "wwybp",
        "initial": "one two three",
    },
    "yb_P_before": {
        "keys": "wybP",
        "initial": "alpha beta gamma",
    },

    # ── ye (yank to end of word) then put ────────────────────
    "ye_p_start_of_word": {
        "keys": "yep",
        "initial": "hello world",
    },
    "ye_p_middle_of_word": {
        "keys": "llyep",
        "initial": "hello world",
    },
    "ye_p_on_second_word": {
        "keys": "wyep",
        "initial": "foo bar baz",
    },

    # ── y$ (yank to end of line) then put ────────────────────
    "y_dollar_p_from_start": {
        "keys": "y$p",
        "initial": "hello world",
    },
    "y_dollar_p_from_middle": {
        "keys": "wy$p",
        "initial": "hello world here",
    },
    "y_dollar_P_before": {
        "keys": "wy$P",
        "initial": "abcdef",
    },

    # ── y0 (yank to start of line) then put ──────────────────
    "y0_p_from_end": {
        "keys": "$y0p",
        "initial": "hello world",
    },
    "y0_p_from_middle": {
        "keys": "wy0p",
        "initial": "one two three",
    },

    # ── y^ (yank to first non-blank) then put ───────────────
    "y_caret_p_leading_spaces": {
        "keys": "wy^p",
        "initial": "    indented text",
    },
    "y_caret_p_tab_indent": {
        "keys": "wy^p",
        "initial": "\tindented line",
    },

    # ── yy (yank line) then put ──────────────────────────────
    "yy_p_single_line": {
        "keys": "yyp",
        "initial": "hello world",
    },
    "yy_p_first_of_two_lines": {
        "keys": "yyp",
        "initial": "first line\nsecond line",
    },
    "yy_p_last_line": {
        "keys": "jyyp",
        "initial": "first line\nsecond line",
    },
    "yy_P_above": {
        "keys": "jyyP",
        "initial": "line one\nline two\nline three",
    },
    "yy_p_middle_line": {
        "keys": "jyyp",
        "initial": "alpha\nbeta\ngamma",
    },
    "Y_p_is_same_as_yy_p": {
        "keys": "Yp",
        "initial": "hello\nworld",
    },

    # ── yy with counts ──────────────────────────────────────
    "2yy_p_two_lines": {
        "keys": "2yyp",
        "initial": "line one\nline two\nline three",
    },
    "3yy_p_three_lines": {
        "keys": "3yyp",
        "initial": "aaa\nbbb\nccc\nddd",
    },
    "2yy_P_above": {
        "keys": "j2yyP",
        "initial": "first\nsecond\nthird\nfourth",
    },
    "4yy_p_four_lines": {
        "keys": "4yyjjjp",
        "initial": "one\ntwo\nthree\nfour\nfive",
    },

    # ── yj / yk (yank current + below/above) ────────────────
    "yj_p_yank_curr_and_below": {
        "keys": "yjp",
        "initial": "alpha\nbeta\ngamma",
    },
    "yk_p_yank_curr_and_above": {
        "keys": "jykp",
        "initial": "alpha\nbeta\ngamma",
    },
    "yj_P_put_above": {
        "keys": "yjP",
        "initial": "one\ntwo\nthree",
    },
    "yk_p_from_last_line": {
        "keys": "jjykp",
        "initial": "xxx\nyyy\nzzz",
    },

    # ── yG / ygg (yank to end/start of file) ────────────────
    "yG_p_from_first_line": {
        "keys": "yGp",
        "initial": "first\nsecond\nthird",
    },
    "ygg_p_from_last_line": {
        "keys": "GyggjGp",
        "initial": "top\nmiddle\nbottom",
    },
    "yG_p_from_middle": {
        "keys": "jyGGp",
        "initial": "one\ntwo\nthree\nfour",
    },

    # ── yf{char} / yt{char} (yank through/till char) ────────
    "yf_char_p": {
        "keys": "yfop",
        "initial": "hello world",
    },
    "yf_space_p": {
        "keys": "yf p",
        "initial": "hello world stuff",
    },
    "yt_char_p": {
        "keys": "ytop",
        "initial": "hello world",
    },
    "yf_comma_p": {
        "keys": "yf,p",
        "initial": "one, two, three",
    },
    "yt_comma_p": {
        "keys": "yt,p",
        "initial": "one, two, three",
    },
    "yf_paren_p": {
        "keys": "yf)p",
        "initial": "func(arg) end",
    },

    # ── y} (yank to paragraph) ──────────────────────────────
    "y_brace_p_paragraph": {
        "keys": "y}p",
        "initial": "line one\nline two\n\nline four",
    },
    "y_brace_p_from_start": {
        "keys": "y}Gp",
        "initial": "aaa\nbbb\n\nccc\nddd",
    },

    # ── p / P with characterwise yank ────────────────────────
    "p_characterwise_end_of_line": {
        "keys": "yw$p",
        "initial": "hello world",
    },
    "P_characterwise_at_start": {
        "keys": "wyeP",
        "initial": "foo bar baz",
    },
    "p_after_ye_on_short_word": {
        "keys": "yep",
        "initial": "ab cd ef",
    },

    # ── p / P with linewise yank ─────────────────────────────
    "p_linewise_on_last_line": {
        "keys": "yyGp",
        "initial": "first\nsecond\nthird",
    },
    "P_linewise_on_first_line": {
        "keys": "GyyggP",
        "initial": "aaa\nbbb\nccc",
    },
    "p_linewise_middle": {
        "keys": "yyjp",
        "initial": "xxx\nyyy\nzzz",
    },

    # ── Multiple puts (count with p) ────────────────────────
    "2p_characterwise": {
        "keys": "yw2p",
        "initial": "hi there",
    },
    "3p_characterwise": {
        "keys": "ye3p",
        "initial": "ab cd",
    },
    "2p_linewise": {
        "keys": "yy2p",
        "initial": "hello\nworld",
    },
    "3p_linewise": {
        "keys": "yy3p",
        "initial": "test",
    },
    "2P_linewise": {
        "keys": "yy2P",
        "initial": "alpha\nbeta",
    },

    # ── Yank then move then paste (register persists) ────────
    "yank_word_move_right_paste": {
        "keys": "ywwp",
        "initial": "cat dog rat",
    },
    "yank_word_move_down_paste": {
        "keys": "ywjp",
        "initial": "hello world\nfoo bar",
    },
    "yank_line_move_down_paste": {
        "keys": "yyjjp",
        "initial": "aaa\nbbb\nccc\nddd",
    },
    "yank_word_goto_end_paste": {
        "keys": "yw$p",
        "initial": "start middle end",
    },
    "yank_ye_move_paste": {
        "keys": "yewp",
        "initial": "one two three",
    },

    # ── dd then p (move line down) ───────────────────────────
    "dd_p_move_line_down": {
        "keys": "ddp",
        "initial": "first\nsecond\nthird",
    },
    "dd_p_from_middle": {
        "keys": "jddp",
        "initial": "aaa\nbbb\nccc\nddd",
    },
    "dd_P_move_line_up": {
        "keys": "jjddP",
        "initial": "one\ntwo\nthree\nfour",
    },
    "dd_p_last_line": {
        "keys": "Gddkp",
        "initial": "xxx\nyyy\nzzz",
    },
    "2dd_p_move_two_lines": {
        "keys": "2ddp",
        "initial": "aa\nbb\ncc\ndd",
    },

    # ── x then p (swap characters) ──────────────────────────
    "xp_swap_first_two_chars": {
        "keys": "xp",
        "initial": "abcdef",
    },
    "xp_swap_in_middle": {
        "keys": "llxp",
        "initial": "abcdef",
    },
    "xp_swap_word_start": {
        "keys": "wxp",
        "initial": "hello wrold",
    },
    "xP_put_before": {
        "keys": "lxP",
        "initial": "abcd",
    },
    "2x_p_two_chars": {
        "keys": "2xp",
        "initial": "abcdef",
    },

    # ── dw then p ────────────────────────────────────────────
    "dw_p_paste_deleted_word": {
        "keys": "dwp",
        "initial": "hello world",
    },
    "dw_p_at_end": {
        "keys": "dw$p",
        "initial": "hello world stuff",
    },
    "dw_move_p": {
        "keys": "dwwp",
        "initial": "aaa bbb ccc ddd",
    },
    "d2w_p": {
        "keys": "d2wp",
        "initial": "one two three four",
    },
    "dw_j_p_paste_below": {
        "keys": "dwjp",
        "initial": "hello world\nfoo bar",
    },

    # ── Interaction: yank, delete, then p ────────────────────
    # (delete overwrites unnamed register!)
    "yank_then_delete_then_p": {
        "keys": "ywwdwp",
        "initial": "aaa bbb ccc",
    },
    "yy_then_dd_then_p": {
        "keys": "yyjddp",
        "initial": "first\nsecond\nthird",
    },
    "ye_then_x_then_p": {
        "keys": "yewxp",
        "initial": "foo bar baz",
    },
    "yw_then_dw_then_p": {
        "keys": "ywwdwp",
        "initial": "one two three four",
    },
    "yy_then_dw_then_p_charwise": {
        "keys": "yyjdwp",
        "initial": "hello\nworld today",
    },

    # ── Edge cases ───────────────────────────────────────────
    "yy_p_empty_line": {
        "keys": "yyp",
        "initial": "",
    },
    "yw_p_single_word_line": {
        "keys": "ywp",
        "initial": "word",
    },
    "yy_p_whitespace_only": {
        "keys": "yyp",
        "initial": "    ",
    },
    "p_after_yy_on_one_line_file": {
        "keys": "yyp",
        "initial": "only",
    },
    "dd_p_two_line_file": {
        "keys": "ddp",
        "initial": "first\nsecond",
    },
    "xp_single_char_line": {
        "keys": "xp",
        "initial": "a",
    },
    "yy_p_line_with_indent": {
        "keys": "yyp",
        "initial": "    indented line\nnormal line",
    },

    # ── yank + put on multiline buffers ──────────────────────
    "yy_p_multiline_buffer": {
        "keys": "jyyp",
        "initial": "one\ntwo\nthree\nfour\nfive",
    },
    "yy_3j_p_paste_far_down": {
        "keys": "yy3jp",
        "initial": "aa\nbb\ncc\ndd\nee",
    },
    "2yy_jj_p": {
        "keys": "2yyjjp",
        "initial": "alpha\nbeta\ngamma\ndelta\nepsilon",
    },
    "y_dollar_j_p_next_line": {
        "keys": "y$jp",
        "initial": "hello world\nfoo bar",
    },
    "yw_jj_p": {
        "keys": "ywjjp",
        "initial": "cat\ndog\nrat",
    },
    "dd_jj_p_move_far": {
        "keys": "ddjjp",
        "initial": "aa\nbb\ncc\ndd\nee",
    },
    "yy_G_P_paste_at_bottom": {
        "keys": "yyGP",
        "initial": "top\nmid\nbot",
    },
    "yy_gg_p_paste_at_top": {
        "keys": "Gyyggp",
        "initial": "first\nsecond\nthird",
    },
}
