CASES = {
    # ==========================================
    # Visual character mode (v) - Enter/Exit
    # ==========================================
    "v_escape_cancels": {
        "keys": "v\x1b",
        "initial": "hello world"
    },
    "v_v_cancels": {
        "keys": "vv",
        "initial": "hello world"
    },

    # ==========================================
    # Visual char - Selection with h/l/j/k
    # ==========================================
    "v_l_select_right": {
        "keys": "vlld",
        "initial": "abcdef"
    },
    "v_h_select_left": {
        "keys": "$vhhd",
        "initial": "abcdef"
    },
    "v_j_select_down": {
        "keys": "vjd",
        "initial": "line one\nline two\nline three"
    },
    "v_k_select_up": {
        "keys": "jvkd",
        "initial": "line one\nline two\nline three"
    },
    "v_j_multiple_lines": {
        "keys": "vjjd",
        "initial": "aaa\nbbb\nccc\nddd"
    },

    # ==========================================
    # Visual char - Word motions
    # ==========================================
    "v_w_select_word": {
        "keys": "vwd",
        "initial": "hello world foo"
    },
    "v_W_select_WORD": {
        "keys": "vWd",
        "initial": "hello-world foo bar"
    },
    "v_b_select_back_word": {
        "keys": "wvbd",
        "initial": "hello world foo"
    },
    "v_B_select_back_WORD": {
        "keys": "wvBd",
        "initial": "hello-world foo"
    },
    "v_e_select_end_of_word": {
        "keys": "ved",
        "initial": "hello world foo"
    },
    "v_E_select_end_of_WORD": {
        "keys": "vEd",
        "initial": "hello-world foo"
    },
    "v_2w_select_two_words": {
        "keys": "v2wd",
        "initial": "one two three four"
    },
    "v_3e_select_three_word_ends": {
        "keys": "v3ed",
        "initial": "one two three four five"
    },

    # ==========================================
    # Visual char - Line motions ($, 0, ^, g_)
    # ==========================================
    "v_dollar_select_to_eol": {
        "keys": "v$d",
        "initial": "hello world"
    },
    "v_0_select_to_bol": {
        "keys": "$v0d",
        "initial": "hello world"
    },
    "v_caret_select_to_first_nonblank": {
        "keys": "$v^d",
        "initial": "   hello world"
    },
    "v_g_underscore_select_to_last_nonblank": {
        "keys": "vg_d",
        "initial": "hello world"
    },
    "v_dollar_from_middle": {
        "keys": "wwv$d",
        "initial": "one two three four"
    },
    "v_0_from_middle": {
        "keys": "wv0d",
        "initial": "one two three"
    },

    # ==========================================
    # Visual char - Find motions (f/t/F/T)
    # ==========================================
    "v_f_char_select": {
        "keys": "vfod",
        "initial": "hello world"
    },
    "v_t_char_select": {
        "keys": "vtod",
        "initial": "hello world"
    },
    "v_F_char_select": {
        "keys": "$vFod",
        "initial": "hello world"
    },
    "v_T_char_select": {
        "keys": "$vTod",
        "initial": "hello world"
    },
    "v_f_select_to_comma": {
        "keys": "vf,d",
        "initial": "one, two, three"
    },

    # ==========================================
    # Visual char - File motions (gg, G)
    # ==========================================
    "v_gg_select_to_top": {
        "keys": "jjvggd",
        "initial": "aaa\nbbb\nccc\nddd"
    },
    "v_G_select_to_bottom": {
        "keys": "vGd",
        "initial": "aaa\nbbb\nccc\nddd"
    },
    "v_G_from_middle": {
        "keys": "jvGd",
        "initial": "aaa\nbbb\nccc\nddd"
    },

    # ==========================================
    # Visual char - Paragraph motions
    # ==========================================
    "v_close_brace_select_paragraph": {
        "keys": "v}d",
        "initial": "aaa\nbbb\n\nccc\nddd"
    },
    "v_open_brace_select_paragraph_back": {
        "keys": "Gv{d",
        "initial": "aaa\nbbb\n\nccc\nddd"
    },

    # ==========================================
    # Visual char - Text objects (iw, aw)
    # ==========================================
    "v_iw_select_inner_word": {
        "keys": "wviwd",
        "initial": "hello world foo"
    },
    "v_aw_select_a_word": {
        "keys": "wvawd",
        "initial": "hello world foo"
    },
    "v_iw_on_first_word": {
        "keys": "viwd",
        "initial": "hello world"
    },
    "v_aw_on_last_word": {
        "keys": "wvawd",
        "initial": "hello world"
    },

    # ==========================================
    # Visual char - Bracket/quote text objects
    # ==========================================
    "v_i_paren_select": {
        "keys": "f+vi(d",
        "initial": "foo(a+b)"
    },
    "v_a_paren_select": {
        "keys": "f+va(d",
        "initial": "foo(a+b) bar"
    },
    "v_i_quote_select": {
        "keys": 'f+vi"d',
        "initial": 'foo "a+b" bar'
    },
    "v_a_quote_select": {
        "keys": 'f+va"d',
        "initial": 'foo "a+b" bar'
    },
    "v_i_bracket_select": {
        "keys": "f+vi[d",
        "initial": "foo[a+b] bar"
    },
    "v_a_bracket_select": {
        "keys": "f+va[d",
        "initial": "foo[a+b] bar"
    },
    "v_i_brace_select": {
        "keys": "f+vi{d",
        "initial": "foo{a+b} bar"
    },
    "v_a_brace_select": {
        "keys": "f+va{d",
        "initial": "foo{a+b} bar"
    },
    "v_i_single_quote_select": {
        "keys": "f+vi'd",
        "initial": "foo 'a+b' bar"
    },

    # ==========================================
    # Visual char - Operations: delete (d, x)
    # ==========================================
    "v_select_d_delete": {
        "keys": "vllld",
        "initial": "abcdefgh"
    },
    "v_select_x_delete": {
        "keys": "vlllx",
        "initial": "abcdefgh"
    },
    "v_select_word_d": {
        "keys": "vwd",
        "initial": "hello world again"
    },
    "v_select_multiline_d": {
        "keys": "vjjd",
        "initial": "aaa\nbbb\nccc\nddd"
    },
    "v_select_to_eol_d": {
        "keys": "wv$d",
        "initial": "one two three"
    },

    # ==========================================
    # Visual char - Operations: change (c, s)
    # ==========================================
    "v_select_c_change": {
        "keys": "vllcXYZ\x1b",
        "initial": "abcdef"
    },
    "v_select_s_substitute": {
        "keys": "vllsXYZ\x1b",
        "initial": "abcdef"
    },
    "v_select_word_c": {
        "keys": "vecNEW\x1b",
        "initial": "hello world"
    },
    "v_select_multiline_c": {
        "keys": "vjcrepl\x1b",
        "initial": "first\nsecond\nthird"
    },

    # ==========================================
    # Visual char - Operations: yank and paste
    # ==========================================
    "v_yank_paste": {
        "keys": "velyp",
        "initial": "hello world"
    },
    "v_yank_word_paste_elsewhere": {
        "keys": "vey$p",
        "initial": "hello world"
    },
    "v_yank_multiline_paste": {
        "keys": "vjy}p",
        "initial": "aaa\nbbb\n\nccc"
    },

    # ==========================================
    # Visual char - Case toggle (~, u, U)
    # ==========================================
    "v_tilde_toggle_case": {
        "keys": "vll~",
        "initial": "Hello World"
    },
    "v_u_lowercase": {
        "keys": "vllu",
        "initial": "HELLO WORLD"
    },
    "v_U_uppercase": {
        "keys": "vllU",
        "initial": "hello world"
    },
    "v_tilde_whole_line": {
        "keys": "v$~",
        "initial": "Hello World"
    },
    "v_u_whole_word": {
        "keys": "veu",
        "initial": "ABCDEF"
    },
    "v_U_whole_word": {
        "keys": "veU",
        "initial": "abcdef"
    },
    "v_tilde_multiline": {
        "keys": "vj~",
        "initial": "Hello\nWorld"
    },

    # ==========================================
    # Visual char - Indent / Dedent (>, <)
    # ==========================================
    "v_indent_selection": {
        "keys": "vj>",
        "initial": "aaa\nbbb\nccc"
    },
    "v_dedent_selection": {
        "keys": "vj<",
        "initial": "\taaa\n\tbbb\nccc"
    },
    "v_indent_single_line": {
        "keys": "v$>",
        "initial": "hello"
    },
    "v_indent_three_lines": {
        "keys": "vjj>",
        "initial": "aaa\nbbb\nccc\nddd"
    },

    # ==========================================
    # Visual char - Join (J)
    # ==========================================
    "v_J_join_two_lines": {
        "keys": "vjJ",
        "initial": "hello\nworld"
    },
    "v_J_join_three_lines": {
        "keys": "vjjJ",
        "initial": "aaa\nbbb\nccc\nddd"
    },

    # ==========================================
    # Visual char - Replace (r)
    # ==========================================
    "v_r_replace_selection": {
        "keys": "vllrx",
        "initial": "abcdef"
    },
    "v_r_replace_word": {
        "keys": "ver-",
        "initial": "hello world"
    },
    "v_r_replace_multiline": {
        "keys": "vjr*",
        "initial": "aaa\nbbb\nccc"
    },

    # ==========================================
    # Visual char - o (swap ends)
    # ==========================================
    "v_o_swap_and_extend": {
        "keys": "vlllolld",
        "initial": "abcdefghij"
    },
    "v_o_swap_cursor": {
        "keys": "vllod",
        "initial": "abcdef"
    },

    # ==========================================
    # Visual line mode (V) - Entering
    # ==========================================
    "V_selects_whole_line": {
        "keys": "Vd",
        "initial": "hello world\nsecond line"
    },

    # ==========================================
    # Visual line - Selection with j/k
    # ==========================================
    "V_j_select_two_lines": {
        "keys": "Vjd",
        "initial": "aaa\nbbb\nccc"
    },
    "V_k_select_up": {
        "keys": "jVkd",
        "initial": "aaa\nbbb\nccc"
    },
    "V_jj_select_three_lines": {
        "keys": "Vjjd",
        "initial": "aaa\nbbb\nccc\nddd"
    },
    "V_jjj_select_four_lines": {
        "keys": "Vjjjd",
        "initial": "aaa\nbbb\nccc\nddd\neee"
    },

    # ==========================================
    # Visual line - File motions (gg, G)
    # ==========================================
    "V_gg_select_to_top": {
        "keys": "jjVggd",
        "initial": "aaa\nbbb\nccc\nddd"
    },
    "V_G_select_to_bottom": {
        "keys": "VGd",
        "initial": "aaa\nbbb\nccc\nddd"
    },
    "V_G_from_middle": {
        "keys": "jVGd",
        "initial": "aaa\nbbb\nccc\nddd"
    },

    # ==========================================
    # Visual line - Delete (d)
    # ==========================================
    "V_d_delete_single_line": {
        "keys": "Vd",
        "initial": "aaa\nbbb\nccc"
    },
    "V_d_delete_first_line": {
        "keys": "Vd",
        "initial": "first\nsecond\nthird"
    },
    "V_d_delete_middle_line": {
        "keys": "jVd",
        "initial": "first\nsecond\nthird"
    },
    "V_d_delete_last_line": {
        "keys": "GVd",
        "initial": "first\nsecond\nthird"
    },
    "V_2j_d_delete_three_lines": {
        "keys": "V2jd",
        "initial": "aaa\nbbb\nccc\nddd\neee"
    },

    # ==========================================
    # Visual line - Change (c)
    # ==========================================
    "V_c_change_line": {
        "keys": "Vcnew text\x1b",
        "initial": "old text\nsecond line"
    },
    "V_j_c_change_two_lines": {
        "keys": "Vjcreplacement\x1b",
        "initial": "aaa\nbbb\nccc"
    },

    # ==========================================
    # Visual line - Yank and paste (y, p)
    # ==========================================
    "V_y_p_yank_paste_line": {
        "keys": "Vyp",
        "initial": "aaa\nbbb\nccc"
    },
    "V_jy_p_yank_paste_two_lines": {
        "keys": "Vjyjp",
        "initial": "aaa\nbbb\nccc"
    },
    "V_3j_y_p_yank_paste_four_lines": {
        "keys": "V3jyGp",
        "initial": "aaa\nbbb\nccc\nddd\neee"
    },

    # ==========================================
    # Visual line - Indent / Dedent
    # ==========================================
    "V_indent_single_line": {
        "keys": "V>",
        "initial": "hello\nworld"
    },
    "V_indent_two_lines": {
        "keys": "Vj>",
        "initial": "aaa\nbbb\nccc"
    },
    "V_dedent_single_line": {
        "keys": "V<",
        "initial": "\thello\nworld"
    },
    "V_dedent_two_lines": {
        "keys": "Vj<",
        "initial": "\taaa\n\tbbb\nccc"
    },

    # ==========================================
    # Visual line - Join (J)
    # ==========================================
    "V_j_J_join_two_lines": {
        "keys": "VjJ",
        "initial": "hello\nworld\nfoo"
    },
    "V_jj_J_join_three_lines": {
        "keys": "VjjJ",
        "initial": "aaa\nbbb\nccc\nddd"
    },

    # ==========================================
    # Visual line - Case operations
    # ==========================================
    "V_tilde_toggle_case_line": {
        "keys": "V~",
        "initial": "Hello World\nsecond"
    },
    "V_U_uppercase_line": {
        "keys": "VU",
        "initial": "hello world\nsecond"
    },
    "V_u_lowercase_line": {
        "keys": "Vu",
        "initial": "HELLO WORLD\nsecond"
    },
    "V_j_tilde_two_lines": {
        "keys": "Vj~",
        "initial": "Hello\nWorld\nfoo"
    },
    "V_j_U_uppercase_two_lines": {
        "keys": "VjU",
        "initial": "hello\nworld\nfoo"
    },
    "V_j_u_lowercase_two_lines": {
        "keys": "Vju",
        "initial": "HELLO\nWORLD\nfoo"
    },

    # ==========================================
    # Visual line - Replace (r)
    # ==========================================
    "V_r_replace_line": {
        "keys": "Vrx",
        "initial": "hello\nworld"
    },
    "V_j_r_replace_two_lines": {
        "keys": "Vjr-",
        "initial": "aaa\nbbb\nccc"
    },

    # ==========================================
    # Counts with visual mode
    # ==========================================
    "v_2l_select_two_right": {
        "keys": "v2ld",
        "initial": "abcdef"
    },
    "v_3l_select_three_right": {
        "keys": "v3ld",
        "initial": "abcdefgh"
    },
    "v_2w_select_two_words": {
        "keys": "v2wd",
        "initial": "one two three four"
    },
    "v_3w_select_three_words": {
        "keys": "v3wd",
        "initial": "one two three four five"
    },
    "v_2j_select_two_down": {
        "keys": "v2jd",
        "initial": "aaa\nbbb\nccc\nddd"
    },
    "V_2j_select_three_lines": {
        "keys": "V2jd",
        "initial": "aaa\nbbb\nccc\nddd\neee"
    },
    "V_3j_select_four_lines": {
        "keys": "V3jd",
        "initial": "aaa\nbbb\nccc\nddd\neee\nfff"
    },
    "v_2e_select_two_word_ends": {
        "keys": "v2ed",
        "initial": "one two three four"
    },
    "v_2b_select_two_words_back": {
        "keys": "wwv2bd",
        "initial": "one two three four"
    },

    # ==========================================
    # Switching modes (v <-> V)
    # ==========================================
    "v_then_V_switch_to_linewise": {
        "keys": "vllVd",
        "initial": "hello world\nsecond"
    },
    "V_then_v_switch_to_charwise": {
        "keys": "Vvlld",
        "initial": "hello world\nsecond"
    },
    "v_escape_back_to_normal": {
        "keys": "vll\x1bx",
        "initial": "abcdef"
    },
    "V_escape_back_to_normal": {
        "keys": "V\x1bx",
        "initial": "hello world"
    },

    # ==========================================
    # Edge cases
    # ==========================================
    "v_on_empty_line": {
        "keys": "jvd",
        "initial": "hello\n\nworld"
    },
    "v_on_single_char": {
        "keys": "vd",
        "initial": "a\nsecond"
    },
    "v_across_empty_lines": {
        "keys": "vjjd",
        "initial": "hello\n\nworld"
    },
    "v_on_last_line": {
        "keys": "Gvd",
        "initial": "aaa\nbbb\nccc"
    },
    "v_delete_entire_line_content": {
        "keys": "0v$d",
        "initial": "hello\nworld"
    },
    "V_on_single_line_buffer_d": {
        "keys": "Vd",
        "initial": "only line"
    },
    "V_delete_all_lines": {
        "keys": "VGd",
        "initial": "aaa\nbbb\nccc"
    },
    "v_single_char_line": {
        "keys": "vd",
        "initial": "x"
    },
    "v_select_last_char_of_line": {
        "keys": "$vd",
        "initial": "abcde\nfgh"
    },
    "V_on_empty_line": {
        "keys": "jVd",
        "initial": "hello\n\nworld"
    },
    "v_select_across_short_and_long": {
        "keys": "vjd",
        "initial": "short\na much longer line here"
    },
    "v_select_across_long_and_short": {
        "keys": "vjd",
        "initial": "a much longer line here\nshort"
    },

    # ==========================================
    # Visual char - misc motions & combos
    # ==========================================
    "v_percent_match_paren": {
        "keys": "v%d",
        "initial": "(hello world)"
    },
    "v_dollar_multiline": {
        "keys": "v$jd",
        "initial": "aaa\nbbb\nccc"
    },
    "v_select_d_then_insert": {
        "keys": "vedireplace\x1b",
        "initial": "hello world"
    },
    "v_select_yank_paste_inline": {
        "keys": "vely$p",
        "initial": "abcdef"
    },
    "v_select_entire_short_line": {
        "keys": "0v$d",
        "initial": "ab\ncd"
    },

    # ==========================================
    # Visual line - misc combos
    # ==========================================
    "V_y_paste_below_last_line": {
        "keys": "VyGp",
        "initial": "first\nsecond\nthird"
    },
    "V_d_only_middle": {
        "keys": "jVd",
        "initial": "first\nsecond\nthird"
    },
    "V_j_c_new_text": {
        "keys": "VjcNEW\x1b",
        "initial": "aaa\nbbb\nccc\nddd"
    },

    # ==========================================
    # More text objects in visual
    # ==========================================
    "v_iw_middle_of_word": {
        "keys": "lviwd",
        "initial": "hello world"
    },
    "v_aw_with_trailing_space": {
        "keys": "vawd",
        "initial": "hello world bar"
    },
    "v_i_paren_nested": {
        "keys": "fxvi(d",
        "initial": "a(b(x)c)d"
    },
    "v_a_paren_with_space": {
        "keys": "fxva(d",
        "initial": "fn( x ) end"
    },
    "v_i_curly_brace": {
        "keys": "fxvi{d",
        "initial": "if {x} then"
    },

    # ==========================================
    # Additional operations for coverage
    # ==========================================
    "v_d_first_two_chars": {
        "keys": "vld",
        "initial": "abcdef"
    },
    "v_d_last_two_chars": {
        "keys": "$hvld",
        "initial": "abcdef"
    },
    "v_c_single_char": {
        "keys": "vcZ\x1b",
        "initial": "abcdef"
    },
    "V_r_replace_with_space": {
        "keys": "Vr ",
        "initial": "hello\nworld"
    },
    "v_select_word_yank_paste_after": {
        "keys": "veyep",
        "initial": "hello world"
    },
    "V_yank_paste_multiple": {
        "keys": "Vyjjp",
        "initial": "aaa\nbbb\nccc\nddd"
    },
    "v_tilde_single_char": {
        "keys": "v~",
        "initial": "hello"
    },
    "v_U_single_char": {
        "keys": "vU",
        "initial": "hello"
    },
    "v_u_single_char": {
        "keys": "vu",
        "initial": "Hello"
    },
    "v_r_single_char": {
        "keys": "vrx",
        "initial": "abcdef"
    },
    "V_d_two_of_five_lines": {
        "keys": "jVjd",
        "initial": "one\ntwo\nthree\nfour\nfive"
    },
    "V_c_last_line": {
        "keys": "GVcnew last\x1b",
        "initial": "aaa\nbbb\nccc"
    },
    "v_J_join_from_middle": {
        "keys": "wvjJ",
        "initial": "hello world\nfoo bar\nbaz"
    },
    "v_indent_already_indented": {
        "keys": "vj>",
        "initial": "\taaa\n\tbbb\nccc"
    },
    "V_indent_already_indented": {
        "keys": "Vj>",
        "initial": "\taaa\n\tbbb\nccc"
    },
    "v_2j_c_change_multiline": {
        "keys": "v2jcX\x1b",
        "initial": "aaa\nbbb\nccc\nddd"
    },
    "V_2j_J_join_three_lines": {
        "keys": "V2jJ",
        "initial": "aaa\nbbb\nccc\nddd"
    },
    "v_select_line_and_change": {
        "keys": "v$cNEW\x1b",
        "initial": "old content\nkeep this"
    },
    "V_select_and_replace_all": {
        "keys": "VGrz",
        "initial": "aaa\nbbb\nccc"
    },
}
