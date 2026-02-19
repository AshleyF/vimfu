"""Comprehensive operator + motion phrase tests.

Tests Vim's composable grammar: every operator (d, c, y, >, <)
combined with every motion category. This catches the fundamental
issue where individual keys work but phrases (operator+motion
combinations) are broken.
"""

CASES = {
    # ================================================================
    # d + find-repeat motions (; and ,)
    # ================================================================
    "d_semicolon_basic": {
        "keys": "fa;d;",
        "initial": "banana split cake",
    },
    "d_comma_basic": {
        "keys": "$Fa,d,",
        "initial": "banana split cake",
    },
    "c_semicolon_basic": {
        "keys": "fo;c;X\x1b",
        "initial": "foo boo goo hoo",
    },
    "y_semicolon_paste": {
        "keys": "fo;y;$p",
        "initial": "foo boo goo hoo",
    },

    # ================================================================
    # d/c/y + search (/ and ?)
    # ================================================================
    "d_slash_basic": {
        "keys": "d/world\r",
        "initial": "hello world",
    },
    "d_slash_multiword": {
        "keys": "d/three\r",
        "initial": "one two three four",
    },
    "d_slash_mid_line": {
        "keys": "wd/four\r",
        "initial": "one two three four five",
    },
    "d_slash_multiline": {
        "keys": "d/gamma\r",
        "initial": "alpha beta\ngamma delta",
    },
    "d_question_basic": {
        "keys": "$d?hello\r",
        "initial": "hello world",
    },
    "c_slash_basic": {
        "keys": "c/world\rREPLACED\x1b",
        "initial": "hello world stuff",
    },
    "c_slash_multiline": {
        "keys": "c/gamma\rX\x1b",
        "initial": "alpha beta\ngamma delta",
    },
    "y_slash_paste": {
        "keys": "y/world\r$p",
        "initial": "hello world",
    },

    # ================================================================
    # d/c/y + search repeat (n and N)
    # ================================================================
    "d_n_basic": {
        "keys": "/two\rdn",
        "initial": "one two three two four",
    },
    "d_N_basic": {
        "keys": "/four\r0dN",
        "initial": "one two three four five",
    },
    "c_n_basic": {
        "keys": "/two\rcnX\x1b",
        "initial": "one two three two four",
    },
    "y_n_paste": {
        "keys": "/two\ryn$p",
        "initial": "one two three two four",
    },

    # ================================================================
    # d/c + percent (%)
    # ================================================================
    "d_percent_parens": {
        "keys": "f(d%",
        "initial": "call(arg1, arg2) done",
    },
    "d_percent_brackets": {
        "keys": "f[d%",
        "initial": "arr[0] = val",
    },
    "d_percent_braces": {
        "keys": "f{d%",
        "initial": "if {body} end",
    },
    "c_percent_parens": {
        "keys": "f(c%NEW\x1b",
        "initial": "call(old) done",
    },
    "y_percent_paste": {
        "keys": "f(y%$p",
        "initial": "call(arg) end",
    },

    # ================================================================
    # d/c + marks (' and `)
    # ================================================================
    "d_mark_tick_basic": {
        "keys": "maj0d'a",
        "initial": "one two three\nfour five six\nseven eight",
    },
    "d_mark_backtick": {
        "keys": "llma$d`a",
        "initial": "hello world",
    },
    "c_mark_tick": {
        "keys": "jma0c'aREPLACED\x1b",
        "initial": "first line\nsecond line\nthird line",
    },
    "y_mark_tick_paste": {
        "keys": "jmakky'aGp",
        "initial": "aaa\nbbb\nccc",
    },

    # ================================================================
    # d/c + line motions (+, -, Enter)
    # ================================================================
    "d_plus_basic": {
        "keys": "d+",
        "initial": "line one\nline two\nline three",
    },
    "d_minus_basic": {
        "keys": "jd-",
        "initial": "line one\nline two\nline three",
    },
    "d_enter_basic": {
        "keys": "d\r",
        "initial": "line one\nline two\nline three",
    },
    "c_plus_basic": {
        "keys": "c+REPLACED\x1b",
        "initial": "aaa\nbbb\nccc",
    },
    "d_2plus": {
        "keys": "d2+",
        "initial": "one\ntwo\nthree\nfour",
    },

    # ================================================================
    # d/c + column motion (|)
    # ================================================================
    "d_pipe_basic": {
        "keys": "$d1|",
        "initial": "hello world",
    },
    "d_pipe_mid": {
        "keys": "d5|",
        "initial": "hello world",
    },
    "c_pipe_basic": {
        "keys": "$c1|X\x1b",
        "initial": "hello world",
    },

    # ================================================================
    # d/c + underscore motion (_)
    # ================================================================
    "d_underscore_basic": {
        "keys": "d_",
        "initial": "one\ntwo\nthree",
    },
    "d_2underscore": {
        "keys": "d2_",
        "initial": "one\ntwo\nthree\nfour",
    },
    "c_underscore": {
        "keys": "c_X\x1b",
        "initial": "one\ntwo\nthree",
    },

    # ================================================================
    # d/c + screen-relative motions (H, M, L)
    # These are linewise
    # ================================================================
    "d_H_basic": {
        "keys": "jjdH",
        "initial": "one\ntwo\nthree\nfour\nfive",
    },
    "d_L_basic": {
        "keys": "dL",
        "initial": "one\ntwo\nthree\nfour\nfive",
    },
    "d_M_basic": {
        "keys": "dM",
        "initial": "one\ntwo\nthree\nfour\nfive",
    },

    # ================================================================
    # Operators with f/t to punctuation/special chars
    # (the specific user-reported ct: case)
    # ================================================================
    "ct_colon": {
        "keys": "ct:X\x1b",
        "initial": "key: value",
    },
    "ct_colon_mid": {
        "keys": "wct:NEWKEY\x1b",
        "initial": "name: age: 42",
    },
    "dt_colon": {
        "keys": "dt:",
        "initial": "key: value",
    },
    "cf_colon": {
        "keys": "cf:X\x1b",
        "initial": "key: value",
    },
    "df_colon": {
        "keys": "df:",
        "initial": "key: value",
    },
    "ct_semicolon": {
        "keys": "ct;X\x1b",
        "initial": "for (i = 0; i < n; i++)",
    },
    "dt_semicolon": {
        "keys": "dt;",
        "initial": "for (i = 0; i < n; i++)",
    },
    "ct_paren": {
        "keys": "ct)X\x1b",
        "initial": "func(arg) end",
    },
    "dt_paren": {
        "keys": "dt)",
        "initial": "func(arg) end",
    },
    "ct_bracket": {
        "keys": "ct]X\x1b",
        "initial": "arr[0] end",
    },
    "ct_brace": {
        "keys": "ct}X\x1b",
        "initial": "map{key} end",
    },
    "ct_dot": {
        "keys": "ct.X\x1b",
        "initial": "hello.world",
    },
    "dt_dot": {
        "keys": "dt.",
        "initial": "hello.world",
    },
    "ct_comma": {
        "keys": "ct,X\x1b",
        "initial": "one, two, three",
    },
    "dt_comma": {
        "keys": "dt,",
        "initial": "one, two, three",
    },
    "ct_slash": {
        "keys": "ct/X\x1b",
        "initial": "path/to/file",
    },
    "dt_slash": {
        "keys": "dt/",
        "initial": "path/to/file",
    },
    "ct_equals": {
        "keys": "ct=X\x1b",
        "initial": "name = value",
    },
    "ct_space": {
        "keys": "ct X\x1b",
        "initial": "hello world",
    },
    "ct_quote": {
        "keys": "ct'X\x1b",
        "initial": "it's a test",
    },
    "ct_dquote": {
        "keys": "ct\"X\x1b",
        "initial": 'say "hello" end',
    },
    "ct_hash": {
        "keys": "ct#X\x1b",
        "initial": "code # comment",
    },
    "ct_at": {
        "keys": "ct@X\x1b",
        "initial": "user@host.com",
    },
    "ct_pipe_char": {
        "keys": "ct|X\x1b",
        "initial": "left | right",
    },
    "ct_backslash": {
        "keys": "ct\\X\x1b",
        "initial": "path\\to\\file",
    },
    "ct_angle": {
        "keys": "ct>X\x1b",
        "initial": "tag<attr> end",
    },
    "ct_tilde": {
        "keys": "ct~X\x1b",
        "initial": "home~user end",
    },

    # backward find with operators
    "cT_colon": {
        "keys": "$cT:X\x1b",
        "initial": "key: value",
    },
    "dT_colon": {
        "keys": "$dT:",
        "initial": "key: value",
    },
    "dF_colon": {
        "keys": "$dF:",
        "initial": "key: value",
    },
    "cF_colon": {
        "keys": "$cF:X\x1b",
        "initial": "key: value",
    },

    # ================================================================
    # d/c/y + * and # (word under cursor search)
    # ================================================================
    "d_star_basic": {
        "keys": "d*",
        "initial": "foo bar foo baz",
    },
    "d_hash_basic": {
        "keys": "wd#",
        "initial": "bar foo bar baz",
    },
    "c_star_basic": {
        "keys": "c*X\x1b",
        "initial": "foo bar foo baz",
    },

    # ================================================================
    # Operator + gg (when not at top)
    # ================================================================
    "d_gg_from_middle": {
        "keys": "jjdgg",
        "initial": "one\ntwo\nthree\nfour",
    },
    "c_gg_from_bottom": {
        "keys": "Gcgg X\x1b",
        "initial": "aaa\nbbb\nccc",
    },
    "y_gg_from_bottom_paste": {
        "keys": "Gygg0p",
        "initial": "aaa\nbbb\nccc",
    },

    # ================================================================
    # Multi-key phrases: operator + count + motion
    # ================================================================
    "d2f_colon": {
        "keys": "d2f:",
        "initial": "a:b:c:d",
    },
    "c2t_comma": {
        "keys": "c2t,X\x1b",
        "initial": "one, two, three, four",
    },
    "d3w_basic": {
        "keys": "d3w",
        "initial": "one two three four five",
    },
    "c2e_basic": {
        "keys": "c2eX\x1b",
        "initial": "one two three four",
    },
    "y2w_paste": {
        "keys": "y2w$p",
        "initial": "one two three",
    },

    # ================================================================
    # Indent/dedent with motions
    # ================================================================
    "indent_j": {
        "keys": ">j",
        "initial": "one\ntwo\nthree",
    },
    "indent_brace": {
        "keys": ">}",
        "initial": "one\ntwo\n\nthree\nfour",
    },
    "dedent_j": {
        "keys": "<j",
        "initial": "        one\n        two\nthree",
        "groundTruthIssue": "cursor col=2 unexplained; our sim gives correct col=0 (firstNonBlank)",
    },
    "indent_gg": {
        "keys": "G>gg",
        "initial": "one\ntwo\nthree",
    },
    "indent_percent": {
        "keys": ">%",
        "initial": "if (\ntrue\n) end",
    },

    # ================================================================
    # Edge cases: operator + motion that doesn't move
    # ================================================================
    "d_slash_not_found": {
        "keys": "d/zzzzz\r",
        "initial": "hello world",
        "groundTruthIssue": "requires error message display (E486: Pattern not found)",
    },
    "d_f_not_found": {
        "keys": "dfZ",
        "initial": "hello world",
    },
    "c_t_not_found": {
        "keys": "ctZ",
        "initial": "hello world",
    },

    # ================================================================
    # Combined multi-step phrases (real editing scenarios)
    # ================================================================
    "ct_colon_then_type": {
        "keys": "ct:new_key\x1b",
        "initial": "old_key: value",
    },
    "df_dot_then_i": {
        "keys": "df.inew\x1b",
        "initial": "file.txt rest",
    },
    "d_slash_then_i": {
        "keys": "d/end\riSTART \x1b",
        "initial": "hello end world",
    },
    "ct_paren_replace_arg": {
        "keys": "f(lct)new_arg\x1b",
        "initial": "func(old_arg) rest",
    },
    "dt_comma_first_arg": {
        "keys": "f(ldt,",
        "initial": "func(first, second)",
    },
    "yf_dot_paste": {
        "keys": "yf.$p",
        "initial": "file.txt rest",
    },
}
