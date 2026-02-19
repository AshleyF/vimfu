CASES = {
    # ══════════════════════════════════════════════════════════
    # WORD TEXT OBJECTS  (iw / aw)
    # ══════════════════════════════════════════════════════════

    # ── diw (delete inner word) ──────────────────────────────
    "diw_start_of_word": {
        "keys": "diw",
        "initial": "hello world",
    },
    "diw_middle_of_word": {
        "keys": "lldiw",
        "initial": "hello world",
    },
    "diw_on_second_word": {
        "keys": "wdiw",
        "initial": "hello world today",
    },
    "diw_single_word": {
        "keys": "diw",
        "initial": "hello",
    },
    "diw_on_space_between_words": {
        "keys": "fwldiw",
        "initial": "aaa    bbb",
    },
    "diw_last_word_on_line": {
        "keys": "wdiw",
        "initial": "foo bar",
    },
    "diw_word_with_trailing_punct": {
        "keys": "diw",
        "initial": "hello, world",
    },

    # ── daw (delete a word) ──────────────────────────────────
    "daw_first_word": {
        "keys": "daw",
        "initial": "hello world",
    },
    "daw_middle_word": {
        "keys": "wdaw",
        "initial": "one two three",
    },
    "daw_last_word": {
        "keys": "wwdaw",
        "initial": "one two three",
    },
    "daw_single_word": {
        "keys": "daw",
        "initial": "hello",
    },
    "daw_on_space": {
        "keys": "f daw",
        "initial": "aaa bbb ccc",
    },
    "daw_word_at_start_multiword": {
        "keys": "daw",
        "initial": "alpha beta gamma delta",
    },

    # ── ciw (change inner word) ──────────────────────────────
    "ciw_replace_word": {
        "keys": "ciwNEW\x1b",
        "initial": "hello world",
    },
    "ciw_middle_word": {
        "keys": "wciwXX\x1b",
        "initial": "one two three",
    },
    "ciw_single_char_word": {
        "keys": "wciwZZ\x1b",
        "initial": "a b c",
    },
    "ciw_last_word": {
        "keys": "wciwend\x1b",
        "initial": "start finish",
    },

    # ── caw (change a word) ──────────────────────────────────
    "caw_first_word": {
        "keys": "cawNEW \x1b",
        "initial": "old text here",
    },
    "caw_middle_word": {
        "keys": "wcawMID\x1b",
        "initial": "one two three",
    },
    "caw_last_word": {
        "keys": "wwcawEND\x1b",
        "initial": "one two three",
    },

    # ── yiw then p ──────────────────────────────────────────
    "yiw_p_first_word": {
        "keys": "yiwwp",
        "initial": "hello world",
    },
    "yiw_p_second_word": {
        "keys": "wyiwp",
        "initial": "foo bar baz",
    },
    "yaw_p": {
        "keys": "yawwp",
        "initial": "hello world end",
    },

    # ══════════════════════════════════════════════════════════
    # DOUBLE QUOTE TEXT OBJECTS  (i" / a")
    # ══════════════════════════════════════════════════════════

    # ── di" (delete inner double-quoted string) ──────────────
    'di_dquote_simple': {
        "keys": 'di"',
        "initial": 'say "hello" end',
    },
    'di_dquote_cursor_inside': {
        "keys": 'f"ldi"',
        "initial": 'x "content" y',
    },
    'di_dquote_cursor_before': {
        "keys": 'di"',
        "initial": '"hello world"',
    },
    'di_dquote_empty_quotes': {
        "keys": 'di"',
        "initial": 'before "" after',
    },
    'di_dquote_with_spaces': {
        "keys": 'di"',
        "initial": '"hello world foo" end',
    },

    # ── da" (delete a double-quoted string) ──────────────────
    'da_dquote_simple': {
        "keys": 'da"',
        "initial": 'say "hello" end',
    },
    'da_dquote_whole_line': {
        "keys": 'da"',
        "initial": '"entire"',
    },
    'da_dquote_cursor_inside': {
        "keys": 'f"lda"',
        "initial": 'x "stuff" y',
    },
    'da_dquote_empty_quotes': {
        "keys": 'da"',
        "initial": 'x "" y',
    },

    # ── ci" (change inner quoted) ────────────────────────────
    'ci_dquote_replace': {
        "keys": 'ci"NEW\x1b',
        "initial": 'say "hello" end',
    },
    'ci_dquote_empty_quotes': {
        "keys": 'ci"text\x1b',
        "initial": 'x "" y',
    },
    'ci_dquote_long_content': {
        "keys": 'ci"short\x1b',
        "initial": '"very long content here" done',
    },

    # ══════════════════════════════════════════════════════════
    # SINGLE QUOTE TEXT OBJECTS  (i' / a')
    # ══════════════════════════════════════════════════════════

    "di_squote_simple": {
        "keys": "di'",
        "initial": "say 'hello' end",
    },
    "da_squote_simple": {
        "keys": "da'",
        "initial": "say 'hello' end",
    },
    "ci_squote_replace": {
        "keys": "ci'NEW\x1b",
        "initial": "say 'old' end",
    },
    "di_squote_cursor_inside": {
        "keys": "f'ldi'",
        "initial": "x 'content' y",
    },
    "da_squote_empty": {
        "keys": "da'",
        "initial": "x '' y",
    },
    "di_squote_empty": {
        "keys": "di'",
        "initial": "x '' y",
    },

    # ══════════════════════════════════════════════════════════
    # PAREN TEXT OBJECTS  (i( / a( / ib / ab)
    # ══════════════════════════════════════════════════════════

    # ── di( / di) / dib ──────────────────────────────────────
    "di_paren_simple": {
        "keys": "di(",
        "initial": "func(arg) end",
    },
    "di_paren_alt_close": {
        "keys": "di)",
        "initial": "func(arg) end",
    },
    "dib_same_as_di_paren": {
        "keys": "dib",
        "initial": "func(arg) end",
    },
    "di_paren_multiple_args": {
        "keys": "di(",
        "initial": "f(a, b, c) end",
    },
    "di_paren_cursor_inside": {
        "keys": "f(ldi(",
        "initial": "call(inner) rest",
    },
    "di_paren_empty": {
        "keys": "di(",
        "initial": "func() end",
    },
    "di_paren_nested_outer": {
        "keys": "di(",
        "initial": "f((inner)) end",
    },
    "di_paren_cursor_on_open": {
        "keys": "f(di(",
        "initial": "foo(bar) baz",
    },
    "di_paren_cursor_on_close": {
        "keys": "f)di)",
        "initial": "foo(bar) baz",
    },

    # ── da( / da) / dab ──────────────────────────────────────
    "da_paren_simple": {
        "keys": "da(",
        "initial": "func(arg) end",
    },
    "da_paren_alt_close": {
        "keys": "da)",
        "initial": "func(arg) end",
    },
    "dab_same_as_da_paren": {
        "keys": "dab",
        "initial": "func(arg) end",
    },
    "da_paren_multiple_args": {
        "keys": "da(",
        "initial": "f(x, y) end",
    },
    "da_paren_empty": {
        "keys": "da(",
        "initial": "func() rest",
    },
    "da_paren_whole_line": {
        "keys": "da(",
        "initial": "(everything)",
    },

    # ── ci( / ci) ────────────────────────────────────────────
    "ci_paren_replace": {
        "keys": "ci(NEW\x1b",
        "initial": "func(old) end",
    },
    "ci_paren_empty_parens": {
        "keys": "ci(text\x1b",
        "initial": "func() end",
    },
    "ci_paren_multi_arg": {
        "keys": "ci(x\x1b",
        "initial": "f(a, b, c) done",
    },

    # ── Multiline parens ─────────────────────────────────────
    "di_paren_multiline": {
        "keys": "di(",
        "initial": "func(\n  arg1,\n  arg2\n) end",
    },
    "da_paren_multiline": {
        "keys": "da(",
        "initial": "f(\n  x,\n  y\n) done",
    },
    "ci_paren_multiline": {
        "keys": "ci(z\x1b",
        "initial": "g(\n  old\n) rest",
    },

    # ══════════════════════════════════════════════════════════
    # BRACKET TEXT OBJECTS  (i[ / a[)
    # ══════════════════════════════════════════════════════════

    "di_bracket_simple": {
        "keys": "di[",
        "initial": "arr[0] end",
    },
    "di_bracket_alt": {
        "keys": "di]",
        "initial": "arr[idx] end",
    },
    "da_bracket_simple": {
        "keys": "da[",
        "initial": "arr[0] end",
    },
    "da_bracket_alt": {
        "keys": "da]",
        "initial": "arr[idx] end",
    },
    "di_bracket_multiple": {
        "keys": "di[",
        "initial": "x[1, 2, 3] done",
    },
    "da_bracket_empty": {
        "keys": "da[",
        "initial": "arr[] rest",
    },
    "di_bracket_empty": {
        "keys": "di[",
        "initial": "arr[] rest",
    },
    "ci_bracket_replace": {
        "keys": "ci[NEW\x1b",
        "initial": "a[old] end",
    },
    "di_bracket_multiline": {
        "keys": "di[",
        "initial": "x[\n  a,\n  b\n] end",
    },
    "da_bracket_multiline": {
        "keys": "da[",
        "initial": "x[\n  a,\n  b\n] end",
    },

    # ══════════════════════════════════════════════════════════
    # BRACE TEXT OBJECTS  (i{ / a{ / iB / aB)
    # ══════════════════════════════════════════════════════════

    "di_brace_simple": {
        "keys": "di{",
        "initial": "x{body} end",
    },
    "di_brace_alt": {
        "keys": "di}",
        "initial": "x{body} end",
    },
    "diB_same_as_di_brace": {
        "keys": "diB",
        "initial": "x{body} end",
    },
    "da_brace_simple": {
        "keys": "da{",
        "initial": "x{body} end",
    },
    "da_brace_alt": {
        "keys": "da}",
        "initial": "x{body} end",
    },
    "daB_same_as_da_brace": {
        "keys": "daB",
        "initial": "x{body} end",
    },
    "di_brace_empty": {
        "keys": "di{",
        "initial": "x{} end",
    },
    "da_brace_empty": {
        "keys": "da{",
        "initial": "x{} end",
    },
    "ci_brace_replace": {
        "keys": "ci{NEW\x1b",
        "initial": "x{old} end",
    },
    "ci_brace_multiline": {
        "keys": "ci{z\x1b",
        "initial": "if {\n  code\n} end",
    },
    "di_brace_multiline": {
        "keys": "di{",
        "initial": "fn {\n  body;\n  more;\n} end",
    },
    "da_brace_multiline": {
        "keys": "da{",
        "initial": "fn {\n  body;\n} end",
    },
    "di_brace_cursor_inside": {
        "keys": "f{ldi{",
        "initial": "a{hello}b",
    },

    # ══════════════════════════════════════════════════════════
    # ANGLE BRACKET TEXT OBJECTS  (i< / a<)
    # ══════════════════════════════════════════════════════════

    "di_angle_simple": {
        "keys": "di<",
        "initial": "x<tag> end",
    },
    "di_angle_alt": {
        "keys": "di>",
        "initial": "x<tag> end",
    },
    "da_angle_simple": {
        "keys": "da<",
        "initial": "x<tag> end",
    },
    "da_angle_alt": {
        "keys": "da>",
        "initial": "x<tag> end",
    },
    "di_angle_empty": {
        "keys": "di<",
        "initial": "x<> end",
    },
    "da_angle_empty": {
        "keys": "da<",
        "initial": "x<> end",
    },
    "ci_angle_replace": {
        "keys": "ci<NEW\x1b",
        "initial": "x<old> end",
    },
    "di_angle_with_attrs": {
        "keys": "di<",
        "initial": '<div class="a"> end',
    },
    "da_angle_with_attrs": {
        "keys": "da<",
        "initial": '<div class="a"> end',
    },
    "di_angle_multiline": {
        "keys": "di<",
        "initial": "x<\n  inner\n> end",
    },

    # ══════════════════════════════════════════════════════════
    # NESTED BRACKETS
    # ══════════════════════════════════════════════════════════

    "di_paren_nested_inner": {
        "keys": "f(ldi(",
        "initial": "f((inner)) end",
    },
    "da_paren_nested_outer": {
        "keys": "da(",
        "initial": "f((inner)) end",
    },
    "di_brace_nested": {
        "keys": "f{ldi{",
        "initial": "x{{inner}} end",
    },
    "di_bracket_nested": {
        "keys": "f[ldi[",
        "initial": "a[[inner]] end",
    },
    "ci_paren_nested_inner": {
        "keys": "f(lci(X\x1b",
        "initial": "f((deep)) end",
    },

    # ══════════════════════════════════════════════════════════
    # CURSOR POSITION EDGE CASES
    # ══════════════════════════════════════════════════════════

    "di_paren_cursor_before_open": {
        "keys": "di(",
        "initial": "x(content) end",
    },
    "diw_at_end_of_line": {
        "keys": "$diw",
        "initial": "hello world",
    },
    "daw_at_end_of_line": {
        "keys": "$daw",
        "initial": "hello world",
    },
    "diw_with_leading_spaces": {
        "keys": "wdiw",
        "initial": "   hello world",
    },
    "daw_only_word_on_line": {
        "keys": "daw",
        "initial": " hello ",
    },
    'di_dquote_cursor_on_quote': {
        "keys": 'f"di"',
        "initial": 'say "hello" end',
    },
    "di_paren_cursor_deep_inside": {
        "keys": "fadi(",
        "initial": "func(abcdef) end",
    },

    # ══════════════════════════════════════════════════════════
    # MIXED OPERATORS WITH TEXT OBJECTS
    # ══════════════════════════════════════════════════════════

    "yi_paren_then_p": {
        "keys": "yi(Ep",
        "initial": "f(content) end",
    },
    "ya_paren_then_p": {
        "keys": "ya($p",
        "initial": "f(stuff) end",
    },
    'yi_dquote_then_p': {
        "keys": 'yi"Ep',
        "initial": '"hello" end',
    },
    "yi_bracket_then_p": {
        "keys": "yi[Ep",
        "initial": "a[val] end",
    },
    "yi_brace_then_p": {
        "keys": "yi{Ep",
        "initial": "x{data} end",
    },
    "yiw_then_P": {
        "keys": "yiwwP",
        "initial": "aaa bbb ccc",
    },
    "yaw_then_p": {
        "keys": "yaw$p",
        "initial": "one two three",
    },

    # ══════════════════════════════════════════════════════════
    # WORD TEXT OBJECTS ON SPECIAL CHARS
    # ══════════════════════════════════════════════════════════

    "diw_on_punctuation": {
        "keys": "f,diw",
        "initial": "hello, world",
    },
    "daw_on_punctuation": {
        "keys": "f,daw",
        "initial": "hello, world",
    },
    "diw_on_number": {
        "keys": "wdiw",
        "initial": "item 42 end",
    },
    "diw_underscore_word": {
        "keys": "diw",
        "initial": "my_var = 10",
    },
    "ciw_hyphenated": {
        "keys": "ciwNEW\x1b",
        "initial": "foo-bar baz",
    },
}
