# Test cases for newly implemented features:
#   - Uppercase append registers ("A-"Z)
#   - Numbered registers ("0-"9)
#   - Small delete register ("-)
#   - Black hole register ("_)
#   - Last search register ("/)
#   - Special marks ('. `. '' `` '< '>)
#   - ignorecase / smartcase
#   - scrolloff
#   - :substitute
#   - expandtab / tabstop / shiftwidth
#   - autoindent
#   - cursorline

FIVELINES = "\n".join(f"Line {i:02d} content" for i in range(1, 6))
TENLINES = "\n".join(f"Line {i:02d} content" for i in range(1, 11))
TWENTYLINES = "\n".join(f"Line {i:02d} content" for i in range(1, 21))
THIRTYLINES = "\n".join(f"Line {i:02d} content" for i in range(1, 31))

CASES = {

    # ═══════════════════════════════════════════════════════════
    # UPPERCASE APPEND REGISTERS
    # ═══════════════════════════════════════════════════════════

    "reg_uppercase_append_basic": {
        "keys": '"ayiw' + 'w"Ayiw' + '"ap',
        "initial": "hello world end",
    },
    "reg_uppercase_append_line": {
        "keys": '"ayy' + 'j"Ayy' + '"ap',
        "initial": "alpha\nbeta\ngamma",
    },
    "reg_uppercase_append_dd": {
        "keys": '"add' + '"Add' + '"ap',
        "initial": "first\nsecond\nthird\nfourth",
    },
    "reg_uppercase_append_three_times": {
        "keys": '"ayiw' + 'w"Ayiw' + 'w"Ayiw' + '"ap',
        "initial": "aaa bbb ccc end",
    },
    "reg_uppercase_creates_if_empty": {
        "keys": '"Byiw' + '"bp',
        "initial": "hello world",
    },

    # ═══════════════════════════════════════════════════════════
    # NUMBERED REGISTERS
    # ═══════════════════════════════════════════════════════════

    # "0 holds last yank
    "reg_0_holds_yank": {
        "keys": 'yiw' + '"0p',
        "initial": "hello world",
    },
    "reg_0_after_yy": {
        "keys": 'yy' + '"0p',
        "initial": "hello world",
    },
    "reg_0_not_overwritten_by_delete": {
        "keys": 'yiw' + 'wdiw' + '"0p',
        "initial": "hello world end",
    },
    "reg_0_updated_on_second_yank": {
        "keys": 'yiw' + 'wyiw' + '"0p',
        "initial": "hello world end",
    },

    # "1-"9 hold delete history
    "reg_1_holds_last_line_delete": {
        "keys": 'dd' + '"1p',
        "initial": "first\nsecond\nthird",
    },
    "reg_1_shifts_to_2": {
        "keys": 'dd' + 'dd' + '"2p',
        "initial": "aaa\nbbb\nccc\nddd",
    },
    "reg_1_2_after_two_deletes": {
        "keys": 'dd' + 'dd' + '"1p' + '"2p',
        "initial": "aaa\nbbb\nccc\nddd",
    },

    # Small deletes don't go to numbered registers
    "reg_small_delete_not_in_1": {
        "keys": 'dw' + '"1p',
        "initial": "hello world end",
    },

    # ═══════════════════════════════════════════════════════════
    # SMALL DELETE REGISTER
    # ═══════════════════════════════════════════════════════════

    "reg_small_delete_basic": {
        "keys": 'dw' + '"_p',  # delete word, black hole paste, just to clear
        "initial": "hello world",
    },
    "reg_minus_after_dw": {
        "keys": 'dw' + '"-p',
        "initial": "hello world end",
    },
    "reg_minus_after_x": {
        "keys": 'x' + '"-p',
        "initial": "hello world",
    },
    "reg_minus_after_dl": {
        "keys": 'dl' + '"-p',
        "initial": "abcdef",
    },
    "reg_minus_not_after_dd": {
        # dd is a line delete, should go to "1 not "-
        "keys": 'dw' + 'dd' + '"-p',
        "initial": "hello world\nsecond line\nthird line",
    },

    # ═══════════════════════════════════════════════════════════
    # BLACK HOLE REGISTER
    # ═══════════════════════════════════════════════════════════

    "reg_blackhole_delete_no_overwrite": {
        "keys": 'yiw' + '"_diw' + 'p',
        "initial": "hello world end",
    },
    "reg_blackhole_dd_preserves_unnamed": {
        "keys": 'yy' + 'j"_dd' + 'p',
        "initial": "keep\ndelete\nend",
    },
    "reg_blackhole_paste_empty": {
        "keys": '"_p',
        "initial": "hello world",
    },
    "reg_blackhole_change_no_overwrite": {
        "keys": 'yiw' + 'w"_ciwnew\x1b' + 'p',
        "initial": "hello world end",
    },

    # ═══════════════════════════════════════════════════════════
    # LAST SEARCH REGISTER
    # ═══════════════════════════════════════════════════════════

    "reg_search_after_forward": {
        "keys": "/world\r" + ':put "/\r',
        "initial": "hello world",
    },
    # We verify indirectly: search then use n to confirm
    "reg_search_pattern_set": {
        "keys": "/world\r" + "n",
        "initial": "hello world\nfoo world\nbar",
    },

    # ═══════════════════════════════════════════════════════════
    # SPECIAL MARKS
    # ═══════════════════════════════════════════════════════════

    # `. — jump to last change position
    "mark_dot_after_insert": {
        "keys": "iHELLO\x1b" + "gg" + "`.",
        "initial": "line one\nline two\nline three",
    },
    "mark_dot_after_dd": {
        "keys": "jdd" + "G" + "`.",
        "initial": "line one\nline two\nline three\nline four",
    },
    "mark_apostrophe_dot_goes_to_bol": {
        "keys": "jlllx" + "G" + "'.",
        "initial": "line one\nline two\nline three\nline four",
    },

    # '' / `` — jump to position before last jump
    "mark_backtick_backtick_after_G": {
        "keys": "G" + "``",
        "initial": FIVELINES,
    },
    "mark_apostrophe_apostrophe_after_G": {
        "keys": "G" + "''",
        "initial": FIVELINES,
    },
    "mark_backtick_backtick_after_gg": {
        "keys": "G" + "gg" + "``",
        "initial": FIVELINES,
    },
    "mark_doubletick_after_search": {
        "keys": "ll" + "/Line 04\r" + "``",
        "initial": FIVELINES,
    },

    # '< / '> — visual selection bounds
    "mark_lt_gt_after_visual": {
        "keys": "jVj\x1b" + "'<",
        "initial": FIVELINES,
    },
    "mark_gt_after_visual": {
        "keys": "jVj\x1b" + "'>",
        "initial": FIVELINES,
    },
    "mark_lt_after_char_visual": {
        "keys": "wvee\x1b" + "'<",
        "initial": "hello world today",
    },

    # ═══════════════════════════════════════════════════════════
    # IGNORECASE / SMARTCASE
    # ═══════════════════════════════════════════════════════════

    "search_ignorecase_off": {
        "keys": "/hello\r",
        "initial": "Hello World\nhello world",
    },
    "search_ignorecase_on": {
        "keys": ":set ignorecase\r" + "/hello\r",
        "initial": "Hello World\nhello world",
    },
    "search_ignorecase_shortform": {
        "keys": ":set ic\r" + "/hello\r",
        "initial": "Hello World\nhello world",
    },
    "search_smartcase_lowercase": {
        "keys": ":set ignorecase\r:set smartcase\r" + "/hello\r",
        "initial": "Hello World\nhello world",
    },
    "search_smartcase_uppercase": {
        "keys": ":set ignorecase\r:set smartcase\r" + "/Hello\r",
        "initial": "Hello World\nhello world",
    },
    "search_ic_n_wraps": {
        "keys": ":set ic\r" + "/HELLO\r" + "n",
        "initial": "Hello world\nhello world\nHELLO WORLD",
    },
    "search_noignorecase": {
        "keys": ":set ic\r" + ":set noic\r" + "/hello\r",
        "initial": "Hello World\nhello world",
    },

    # ═══════════════════════════════════════════════════════════
    # SCROLLOFF
    # ═══════════════════════════════════════════════════════════

    "scrolloff_basic": {
        "keys": ":set scrolloff=3\r" + "14j",
        "initial": TWENTYLINES,
    },
    "scrolloff_up": {
        "keys": ":set scrolloff=3\r" + "G" + "14k",
        "initial": TWENTYLINES,
    },
    "scrolloff_so_shortform": {
        "keys": ":set so=5\r" + "12j",
        "initial": TWENTYLINES,
    },
    "scrolloff_0_default": {
        # Default scrolloff=0, cursor can go to top/bottom edge
        "keys": "17j",
        "initial": TWENTYLINES,
    },
    "scrolloff_high_value": {
        "keys": ":set so=999\r" + "5j",
        "initial": TWENTYLINES,
    },

    # ═══════════════════════════════════════════════════════════
    # :SUBSTITUTE
    # ═══════════════════════════════════════════════════════════

    "sub_basic": {
        "keys": ":s/hello/world\r",
        "initial": "hello there hello",
    },
    "sub_global": {
        "keys": ":s/hello/world/g\r",
        "initial": "hello there hello",
    },
    "sub_percent_range": {
        "keys": ":%s/foo/bar/g\r",
        "initial": "foo one\nfoo two\nfoo three",
    },
    "sub_visual_range": {
        "keys": "jVj:s/line/row/g\r",
        "initial": "line one\nline two\nline three\nline four",
    },
    "sub_not_found": {
        "keys": ":s/xyz/abc\r",
        "initial": "hello world",
    },
    "sub_case_insensitive_flag": {
        "keys": ":s/hello/world/gi\r",
        "initial": "HELLO there Hello",
    },
    "sub_sets_search_pattern": {
        # After :s, n should find the next match
        "keys": ":s/hello/world\r" + "n",
        "initial": "hello there hello",
    },
    "sub_regex_pattern": {
        "keys": ":%s/[0-9]\\+/NUM/g\r",
        "initial": "item 42 and item 7",
    },
    "sub_empty_replacement": {
        "keys": ":%s/foo//g\r",
        "initial": "foo bar foo baz",
    },
    "sub_single_line": {
        "keys": ":s/a/b\r",
        "initial": "aaa bbb aaa",
    },
    "sub_alternate_delimiter": {
        "keys": ":s#hello#world\r",
        "initial": "hello there",
    },
    "sub_with_ignorecase_setting": {
        "keys": ":set ic\r" + ":s/hello/world/g\r",
        "initial": "Hello hello HELLO",
    },
    "sub_with_smartcase": {
        "keys": ":set ic\r:set scs\r" + ":s/Hello/world/g\r",
        "initial": "Hello hello HELLO",
    },
    "sub_escaped_delimiter": {
        "keys": ":s/he\\/lo/world\r",
        "initial": "he/lo there",
    },

    # ═══════════════════════════════════════════════════════════
    # EXPANDTAB / TABSTOP / SHIFTWIDTH
    # ═══════════════════════════════════════════════════════════

    "indent_default_sw8": {
        "keys": ">>",
        "initial": "hello world",
    },
    "indent_sw4": {
        "keys": ":set sw=4\r" + ">>",
        "initial": "hello world",
    },
    "indent_sw2": {
        "keys": ":set sw=2\r" + ">>",
        "initial": "hello world",
    },
    "indent_expandtab": {
        "keys": ":set expandtab\r:set sw=4\r" + ">>",
        "initial": "hello world",
    },
    "indent_et_sw2": {
        "keys": ":set et\r:set sw=2\r" + ">>",
        "initial": "hello world",
    },
    "dedent_sw4": {
        "keys": ":set sw=4\r" + "<<",
        "initial": "    hello world",
    },
    "dedent_et_sw4": {
        "keys": ":set et\r:set sw=4\r" + "<<",
        "initial": "    hello world",
    },
    "indent_twice_sw4": {
        "keys": ":set sw=4\r" + ">>>>",
        "initial": "hello",
    },
    "dedent_not_below_zero": {
        "keys": ":set sw=4\r" + "<<",
        "initial": "  hi",
    },
    "indent_sw4_et_visual": {
        "keys": ":set sw=4\r:set et\r" + "Vj>",
        "initial": "line one\nline two\nline three",
    },

    # ═══════════════════════════════════════════════════════════
    # AUTOINDENT
    # ═══════════════════════════════════════════════════════════

    "autoindent_o_inherits": {
        "keys": ":set ai\r" + "oNEW\x1b",
        "initial": "    indented line",
    },
    "autoindent_O_inherits": {
        "keys": ":set ai\r" + "ONEW\x1b",
        "initial": "    indented line",
    },
    "autoindent_off_o_no_indent": {
        "keys": ":set noai\r" + "oNEW\x1b",
        "initial": "    indented line",
    },
    "autoindent_off_O_no_indent": {
        "keys": ":set noai\r" + "ONEW\x1b",
        "initial": "    indented line",
    },
    "autoindent_o_with_tabs": {
        "keys": ":set ai\r" + "oNEW\x1b",
        "initial": "\tindented line",
    },

    # ═══════════════════════════════════════════════════════════
    # CURSORLINE
    # ═══════════════════════════════════════════════════════════

    "cursorline_on": {
        "keys": ":set cursorline\r",
        "initial": "line one\nline two\nline three",
    },
    "cursorline_off": {
        "keys": ":set cursorline\r:set nocursorline\r",
        "initial": "line one\nline two\nline three",
    },
    "cursorline_moves_with_cursor": {
        "keys": ":set cul\r" + "jj",
        "initial": "line one\nline two\nline three\nline four",
    },
    "cursorline_with_number": {
        "keys": ":set cul\r:set nu\r",
        "initial": "line one\nline two\nline three",
    },

    # ═══════════════════════════════════════════════════════════
    # SET COMMAND ENHANCEMENTS
    # ═══════════════════════════════════════════════════════════

    "set_tabstop_4": {
        "keys": ":set ts=4\r",
        "initial": "\thello\t\tworld",
    },
    "set_shiftwidth_2": {
        "keys": ":set sw=2\r" + ">>",
        "initial": "hello",
    },
    "set_multiple_options": {
        "keys": ":set nu ic sw=4\r",
        "initial": "hello\nworld",
    },

    # ═══════════════════════════════════════════════════════════
    # COMBINED / INTEGRATION
    # ═══════════════════════════════════════════════════════════

    "reg_0_then_named_put": {
        # Yank, delete, paste from "0 (yank), then unnamed (delete)
        "keys": 'yiw' + 'wdiw' + '"0P' + 'p',
        "initial": "hello world end",
    },
    "blackhole_during_macro": {
        "keys": 'yiw' + 'qa"_diwq' + 'p',
        "initial": "hello world end",
    },
    "sub_then_n_search": {
        "keys": ":%s/foo/bar\r" + "jn",
        "initial": "foo one\nfoo two\nfoo three",
    },
    "mark_dot_after_sub": {
        "keys": ":s/hello/world\r" + "G`.",
        "initial": "hello there\nsecond\nthird",
    },
    "ignorecase_star_search": {
        "keys": ":set ic\r" + "*",
        "initial": "hello world\nHELLO there\nhello again",
    },
    "scrolloff_with_search": {
        "keys": ":set so=3\r" + "/Line 18\r",
        "initial": TWENTYLINES,
    },
}
