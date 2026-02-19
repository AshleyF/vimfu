CASES = {
    # =====================================================================
    # 1. Classic Vim idioms (~20 tests)
    # =====================================================================

    # xp - swap two characters
    "xp_swap_chars": {
        "keys": "xp",
        "initial": "abcdef"
    },
    "xp_swap_middle": {
        "keys": "flxp",
        "initial": "Hello World"
    },
    # ddp - swap two lines
    "ddp_swap_lines": {
        "keys": "ddp",
        "initial": "first\nsecond\nthird"
    },
    "ddp_swap_lines_middle": {
        "keys": "jddp",
        "initial": "aaa\nbbb\nccc\nddd"
    },
    # yyp - duplicate line
    "yyp_duplicate_line": {
        "keys": "yyp",
        "initial": "Hello World"
    },
    "yyp_duplicate_middle": {
        "keys": "jyyp",
        "initial": "one\ntwo\nthree"
    },
    # yypVr= - underline with equals
    "yypVr_equals_underline": {
        "keys": "yypVr=",
        "initial": "Title"
    },
    "yypVr_dash_underline": {
        "keys": "yypVr-",
        "initial": "Chapter One"
    },
    # ea - append at end of word
    "ea_append_end_of_word": {
        "keys": "eaExtra\x1b",
        "initial": "Hello World"
    },
    "ea_append_second_word": {
        "keys": "weaSuffix\x1b",
        "initial": "foo bar baz"
    },
    # bi - insert before word
    "bi_insert_before_word": {
        "keys": "wbiPrefix\x1b",
        "initial": "foo bar baz"
    },
    # dwwP - move word forward
    "dwwP_move_word": {
        "keys": "dwwP",
        "initial": "aaa bbb ccc"
    },
    # daw - delete a word with whitespace
    "daw_delete_word": {
        "keys": "wdaw",
        "initial": "one two three"
    },
    "daw_delete_first_word": {
        "keys": "daw",
        "initial": "one two three"
    },
    # cw + new word
    "cw_change_word": {
        "keys": "cwNEW\x1b",
        "initial": "old thing here"
    },
    "cw_change_second_word": {
        "keys": "wcwREPLACED\x1b",
        "initial": "keep change this"
    },
    # dt) - delete to closing paren
    "dt_close_paren": {
        "keys": "f(ldt)",
        "initial": "func(arg1, arg2)"
    },
    # ci" - change inside quotes
    "ci_quotes": {
        "keys": "ci\"new text\x1b",
        "initial": "say \"hello world\" now"
    },
    # yiw then move then p
    "yiw_move_paste": {
        "keys": "yiwAp",
        "initial": "word"
    },
    # >>.. - indent 3 times
    "indent_dot_dot": {
        "keys": ">>..",
        "initial": "line one\nline two"
    },
    # J.. - join 3 lines
    "join_dot_dot": {
        "keys": "J..",
        "initial": "aaa\nbbb\nccc\nddd"
    },

    # =====================================================================
    # 2. Multi-step editing (~20 tests)
    # =====================================================================

    # Delete line, move down, paste
    "dd_2j_p": {
        "keys": "dd2jp",
        "initial": "one\ntwo\nthree\nfour\nfive"
    },
    # Change word, move to next, dot repeat
    "cw_dot_repeat": {
        "keys": "cwnew\x1bw.",
        "initial": "old old old"
    },
    # Delete to end, join with next
    "D_then_J": {
        "keys": "D J",
        "initial": "hello world\nnext line"
    },
    # Insert text, next line, insert more
    "insert_two_lines": {
        "keys": "iHello\x1bjA World\x1b",
        "initial": "aaa\nbbb"
    },
    # Open below, type, go up, open above
    "o_text_k_O_text": {
        "keys": "oBelow\x1bkOAbove\x1b",
        "initial": "middle"
    },
    # Search and change
    "search_and_change": {
        "keys": "/two\rcwTWO\x1b",
        "initial": "one two three"
    },
    # Yank line, go to end, paste
    "yy_G_p": {
        "keys": "yyGp",
        "initial": "first\nsecond\nthird"
    },
    # Delete inside parens, type new
    "ci_parens_new": {
        "keys": "ci(new content\x1b",
        "initial": "call(old stuff)"
    },
    # Multiple deletions
    "triple_dd": {
        "keys": "dddddd",
        "initial": "one\ntwo\nthree\nfour\nfive"
    },
    # Multiple undos after changes
    "insert_dd_undo_undo": {
        "keys": "iHello\x1bddu",
        "initial": "original"
    },
    # Delete word then append
    "dw_then_a": {
        "keys": "dwiNew \x1b",
        "initial": "old text here"
    },
    # Substitute then move and substitute again
    "s_move_s": {
        "keys": "sX\x1blsY\x1b",
        "initial": "abcdef"
    },
    # Replace char repeatedly
    "r_multiple": {
        "keys": "rXlrYlrZ",
        "initial": "abcdef"
    },
    # Change to end of line
    "C_change_to_end": {
        "keys": "fwCworld!\x1b",
        "initial": "hello whatever here"
    },
    # Delete line and open new
    "dd_O_insert": {
        "keys": "ddONew line\x1b",
        "initial": "delete me\nkeep me"
    },
    # Paste above with P
    "dd_k_P": {
        "keys": "jddkP",
        "initial": "first\nsecond\nthird"
    },
    # Yank and paste multiple times
    "yypp": {
        "keys": "yypp",
        "initial": "only line\nend"
    },
    # Join then undo
    "J_then_undo": {
        "keys": "Ju",
        "initial": "line one\nline two"
    },
    # Append at end, new line, append at end
    "A_text_o_text": {
        "keys": "A end\x1boNew line\x1b",
        "initial": "start"
    },
    # Delete to char then paste
    "dt_then_p": {
        "keys": "dt p",
        "initial": "hello world"
    },

    # =====================================================================
    # 3. Register interaction tests (~15 tests)
    # =====================================================================

    # Yank line then delete line - p puts deleted
    "yy_dd_p_register": {
        "keys": "yyjddp",
        "initial": "yanked\ndeleted\nthird"
    },
    # Yank word, delete line, p puts deleted line
    "yiw_dd_p": {
        "keys": "yiwjddp",
        "initial": "word\nkill this\nthird"
    },
    # Delete char, delete line, p puts line
    "x_dd_p": {
        "keys": "xjddp",
        "initial": "abc\ndelete me\nthird"
    },
    # yy then dw then P
    "yy_dw_P": {
        "keys": "yyjdwP",
        "initial": "full line\nsome words here"
    },
    # Multiple dd then p (last deleted)
    "multi_dd_p": {
        "keys": "ddddjp",
        "initial": "first\nsecond\nthird\nfourth"
    },
    # Yank into named register, delete, put named
    "named_reg_yank_delete_put": {
        "keys": "\"ayyjdd\"ap",
        "initial": "save me\ndelete me\nthird"
    },
    # Delete word then paste it elsewhere
    "dw_move_p": {
        "keys": "dwep",
        "initial": "move this here"
    },
    # Yank two lines then paste
    "2yy_G_p": {
        "keys": "2yyGp",
        "initial": "one\ntwo\nthree"
    },
    # Delete to end then paste
    "D_then_p": {
        "keys": "fwD$p",
        "initial": "hello world stuff"
    },
    # Yank word, change another, paste yanked
    "yiw_cw_paste": {
        "keys": "\"ayiwwcw\x12a\x1b",
        "initial": "good bad ugly"
    },
    # Multiple x then p (only last char)
    "multi_x_p": {
        "keys": "xxxp",
        "initial": "abcdef"
    },
    # dd then . then p
    "dd_dot_p": {
        "keys": "dd.p",
        "initial": "one\ntwo\nthree\nfour"
    },
    # diw then paste
    "diw_paste": {
        "keys": "diwwP",
        "initial": "cut this word"
    },
    # Yank in visual, delete elsewhere, paste yanked
    "visual_yank_named_then_dd": {
        "keys": "\"avey\"bj\"add\"bp",
        "initial": "keep\nkill\nlast"
    },
    # Char delete doesn't overwrite line yank
    "line_yank_then_x": {
        "keys": "yyjxP",
        "initial": "full line\nabc"
    },

    # =====================================================================
    # 4. Undo/redo in complex scenarios (~15 tests)
    # =====================================================================

    # Insert, delete word, undo
    "insert_dw_undo": {
        "keys": "iHello \x1bwdwu",
        "initial": "world"
    },
    # Multiple changes then multiple undos
    "multi_change_multi_undo": {
        "keys": "iA\x1boB\x1buu",
        "initial": "line"
    },
    # Change, undo, new change (redo cleared)
    "change_undo_new_change": {
        "keys": "cwfirst\x1buiwsecond\x1b",
        "initial": "original more"
    },
    # Visual delete then undo
    "visual_delete_undo": {
        "keys": "vlldu",
        "initial": "abcdef"
    },
    # Indent then undo
    "indent_undo": {
        "keys": ">>u",
        "initial": "not indented"
    },
    # Complex undo chain
    "insert_dw_undo_undo": {
        "keys": "iHello \x1bdwuu",
        "initial": "world"
    },
    # Redo after undo
    "undo_redo": {
        "keys": "dd u \x12",
        "initial": "some line\nanother"
    },
    # Multiple redo
    "multi_undo_multi_redo": {
        "keys": "dddduuu\x12\x12",
        "initial": "one\ntwo\nthree\nfour"
    },
    # Undo past visual operation
    "visual_change_undo": {
        "keys": "vlcXX\x1bu",
        "initial": "abcdef"
    },
    # Join then undo restores lines
    "join_undo": {
        "keys": "JJuu",
        "initial": "one\ntwo\nthree"
    },
    # Undo insert mode typing
    "undo_insert_typing": {
        "keys": "iHello World\x1bu",
        "initial": "original"
    },
    # Redo then undo again
    "redo_then_undo": {
        "keys": "dd u \x12 u",
        "initial": "line here\nmore"
    },
    # Undo after o (open line)
    "undo_open_line": {
        "keys": "oNew line\x1bu",
        "initial": "only"
    },
    # Undo after paste
    "paste_then_undo": {
        "keys": "yypu",
        "initial": "single"
    },
    # Complex: delete, put, undo, undo
    "dd_p_uu": {
        "keys": "ddpuu",
        "initial": "first\nsecond\nthird"
    },

    # =====================================================================
    # 5. Visual + normal interaction (~15 tests)
    # =====================================================================

    # Visual select and delete then undo
    "visual_select_delete_undo": {
        "keys": "vlllldu",
        "initial": "Hello World"
    },
    # Visual yank, move, paste
    "visual_yank_move_paste": {
        "keys": "veyw$p",
        "initial": "copy this end"
    },
    # Visual line yank, paste below
    "Vyp_visual_line": {
        "keys": "Vyjp",
        "initial": "first\nsecond\nthird"
    },
    # Visual change text
    "visual_change": {
        "keys": "wvecNEW\x1b",
        "initial": "keep change rest"
    },
    # V>> visual line indent
    "V_indent": {
        "keys": "V>",
        "initial": "indent me"
    },
    # Visual yank word then paste elsewhere
    "v_yank_paste_elsewhere": {
        "keys": "veyjwp",
        "initial": "word here and there"
    },
    # Visual delete entire line content
    "v_dollar_d": {
        "keys": "v$hd",
        "initial": "delete all this\nkeep"
    },
    # Visual line delete multiple lines
    "Vjd_multi_line": {
        "keys": "Vjd",
        "initial": "one\ntwo\nthree\nfour"
    },
    # Visual line then paste replaces
    "V_p_replace_line": {
        "keys": "yyjVp",
        "initial": "source\ntarget\nthird"
    },
    # Visual select then substitute
    "visual_then_s": {
        "keys": "vllsXYZ\x1b",
        "initial": "abcdef"
    },
    # Visual line yank then P above
    "V_yank_P_above": {
        "keys": "VyjP",
        "initial": "aaa\nbbb\nccc"
    },
    # Visual inner word delete
    "viwd_visual_inner_word": {
        "keys": "wviwd",
        "initial": "one two three"
    },
    # Visual select to end of line
    "v_end_delete": {
        "keys": "wv$d",
        "initial": "keep remove all"
    },
    # Visual block isn't tested but V then J
    "V_select_join": {
        "keys": "VjJ",
        "initial": "line one\nline two\nline three"
    },
    # Visual yank then dot repeat paste
    "visual_yank_multi_paste": {
        "keys": "veywAp",
        "initial": "hello"
    },

    # =====================================================================
    # 6. Movement after edits (~15 tests)
    # =====================================================================

    # After dd, cursor on correct line
    "dd_cursor_position": {
        "keys": "jdd",
        "initial": "one\ntwo\nthree"
    },
    # After dd last line, cursor moves up
    "dd_last_line": {
        "keys": "Gdd",
        "initial": "one\ntwo\nthree"
    },
    # After dw, cursor stays
    "dw_cursor_stays": {
        "keys": "dw",
        "initial": "first second third"
    },
    # After o ESC, cursor on new blank line
    "o_esc_cursor": {
        "keys": "o\x1b",
        "initial": "line one\nline two"
    },
    # After p (line paste), cursor on pasted line
    "p_line_paste_cursor": {
        "keys": "yyp",
        "initial": "hello\nworld"
    },
    # After cw ESC, cursor on last char
    "cw_esc_cursor": {
        "keys": "cwNew\x1b",
        "initial": "old stuff"
    },
    # Edit near end of file
    "edit_near_eof": {
        "keys": "Gdd",
        "initial": "one\ntwo"
    },
    # After J, cursor at join point
    "J_cursor_at_join": {
        "keys": "J",
        "initial": "hello\nworld"
    },
    # After A ESC cursor
    "A_esc_cursor": {
        "keys": "A!\x1b",
        "initial": "hello"
    },
    # After O ESC cursor
    "O_esc_cursor": {
        "keys": "O\x1b",
        "initial": "below"
    },
    # Cursor after multiple movements
    "movement_chain": {
        "keys": "gg$j0we",
        "initial": "first line\nsecond word here"
    },
    # After indent, cursor position
    "indent_cursor": {
        "keys": ">>",
        "initial": "text here"
    },
    # After cc, cursor on empty line
    "cc_cursor": {
        "keys": "ccNew line\x1b",
        "initial": "old line\nkept"
    },
    # After dG, cursor on last remaining
    "dG_from_middle": {
        "keys": "jdG",
        "initial": "keep\nremove\nalso remove"
    },
    # After P (put before) cursor
    "P_cursor_after_line_put": {
        "keys": "ddP",
        "initial": "first\nsecond"
    },

    # =====================================================================
    # 7. Stress/complex scenarios (~15 tests)
    # =====================================================================

    # 10 character deletions with count
    "10x_delete": {
        "keys": "10x",
        "initial": "abcdefghijklmno"
    },
    # Repeatedly change and undo
    "cw_undo_cycle": {
        "keys": "cwA\x1bucwB\x1bucwC\x1b",
        "initial": "original rest"
    },
    # Build text with multiple inserts
    "multi_insert_build": {
        "keys": "iOne \x1baTwo \x1baThree\x1b",
        "initial": ""
    },
    # Delete all lines one by one
    "delete_all_lines": {
        "keys": "dddddd",
        "initial": "one\ntwo\nthree"
    },
    # Select all and delete
    "ggVGd_select_all_delete": {
        "keys": "ggVGd",
        "initial": "one\ntwo\nthree\nfour"
    },
    # Indent then dedent restores original
    "indent_dedent_roundtrip": {
        "keys": ">><<",
        "initial": "no indent"
    },
    # Complex cursor movements
    "complex_movements": {
        "keys": "gg$j0web",
        "initial": "first line here\nsecond word line"
    },
    # Mark, edit, return to mark
    "mark_edit_return": {
        "keys": "maANew\x1b`a",
        "initial": "start here"
    },
    # ddp repeated to bubble line down
    "ddp_bubble_down": {
        "keys": "ddpddp",
        "initial": "aaa\nbbb\nccc\nddd"
    },
    # Long insert then undo
    "long_insert_undo": {
        "keys": "iThe quick brown fox\x1bu",
        "initial": "original"
    },
    # Multiple substitute chars
    "multi_substitute": {
        "keys": "sX\x1blsY\x1blsZ\x1b",
        "initial": "abcdefgh"
    },
    # Yank, paste, undo paste, paste again
    "yy_p_u_p": {
        "keys": "yypup",
        "initial": "line\nend"
    },
    # Delete to end of file then undo
    "dG_undo": {
        "keys": "jdGu",
        "initial": "keep\nremove\nalso"
    },
    # Three changes with undo between
    "interleaved_edits_undos": {
        "keys": "iA\x1buoB\x1buiC\x1b",
        "initial": "start"
    },
    # Change inside parens then append
    "ci_paren_then_append": {
        "keys": "ci(x, y\x1bA;\x1b",
        "initial": "func(a, b, c)"
    },
    # Triple yank-paste to replicate lines
    "triple_yyp": {
        "keys": "yypyypyyp",
        "initial": "original"
    },
    # Search forward then delete word
    "search_delete": {
        "keys": "/bar\rdw",
        "initial": "foo bar baz"
    },
    # Insert at multiple positions
    "I_and_A_inserts": {
        "keys": "IStart \x1bA End\x1b",
        "initial": "middle"
    },
    # Replace then dot repeat
    "replace_dot_repeat": {
        "keys": "rXl.l.",
        "initial": "abcdef"
    },
}
