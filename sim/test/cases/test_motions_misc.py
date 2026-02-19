CASES = {
    # ── % with parentheses ───────────────────────────────────
    "percent_paren_open_to_close": {
        "keys": "%",
        "initial": "(hello)",
    },
    "percent_paren_close_to_open": {
        "keys": "$%",
        "initial": "(hello)",
    },
    "percent_paren_nested": {
        "keys": "%",
        "initial": "((inner))",
    },
    "percent_paren_nested_close": {
        "keys": "$%",
        "initial": "((inner))",
    },
    "percent_paren_deep_nested": {
        "keys": "%",
        "initial": "(a(b(c)))",
    },
    "percent_paren_middle_open": {
        "keys": "f(%",
        "initial": "xx(yy)zz",
    },
    "percent_paren_middle_close": {
        "keys": "f)%",
        "initial": "xx(yy)zz",
    },
    "percent_paren_multiline": {
        "keys": "%",
        "initial": "(foo\nbar\nbaz)",
    },
    "percent_paren_multiline_from_close": {
        "keys": "2j$%",
        "initial": "(foo\nbar\nbaz)",
    },
    "percent_paren_empty": {
        "keys": "%",
        "initial": "()",
    },
    "percent_paren_empty_from_close": {
        "keys": "l%",
        "initial": "()",
    },
    "percent_paren_with_spaces": {
        "keys": "%",
        "initial": "( a b c )",
    },

    # ── % with square brackets ────────────────────────────────
    "percent_bracket_open": {
        "keys": "%",
        "initial": "[hello]",
    },
    "percent_bracket_close": {
        "keys": "$%",
        "initial": "[hello]",
    },
    "percent_bracket_nested": {
        "keys": "%",
        "initial": "[[inner]]",
    },
    "percent_bracket_multiline": {
        "keys": "%",
        "initial": "[foo\nbar]",
    },
    "percent_bracket_empty": {
        "keys": "%",
        "initial": "[]",
    },

    # ── % with curly braces ──────────────────────────────────
    "percent_curly_open": {
        "keys": "%",
        "initial": "{hello}",
    },
    "percent_curly_close": {
        "keys": "$%",
        "initial": "{hello}",
    },
    "percent_curly_nested": {
        "keys": "%",
        "initial": "{{inner}}",
    },
    "percent_curly_multiline": {
        "keys": "%",
        "initial": "{foo\nbar\nbaz}",
    },
    "percent_curly_empty": {
        "keys": "%",
        "initial": "{}",
    },

    # ── % with mixed bracket types ────────────────────────────
    "percent_mixed_paren_bracket": {
        "keys": "%",
        "initial": "([foo])",
    },
    "percent_mixed_bracket_curly": {
        "keys": "%",
        "initial": "[{foo}]",
    },
    "percent_mixed_all_three": {
        "keys": "%",
        "initial": "({[x]})",
    },
    "percent_mixed_from_inner": {
        "keys": "f[%",
        "initial": "({[x]})",
    },
    "percent_mixed_from_middle_curly": {
        "keys": "f{%",
        "initial": "({[x]})",
    },

    # ── % cursor not on bracket (search forward) ─────────────
    "percent_search_forward_paren": {
        "keys": "%",
        "initial": "abc(def)ghi",
    },
    "percent_search_forward_bracket": {
        "keys": "%",
        "initial": "abc[def]ghi",
    },
    "percent_search_forward_curly": {
        "keys": "%",
        "initial": "abc{def}ghi",
    },
    "percent_search_fwd_spaces": {
        "keys": "%",
        "initial": "   (x)",
    },
    "percent_search_fwd_from_mid": {
        "keys": "l%",
        "initial": "ab(cd)ef",
    },
    "percent_search_fwd_close_first": {
        "keys": "%",
        "initial": "abc)def(ghi",
    },

    # ── % no match / edge cases ───────────────────────────────
    "percent_no_bracket_on_line": {
        "keys": "%",
        "initial": "hello world",
    },
    "percent_unmatched_open_paren": {
        "keys": "%",
        "initial": "(hello world",
    },
    "percent_unmatched_close_paren": {
        "keys": "$%",
        "initial": "hello world)",
    },
    "percent_unmatched_open_bracket": {
        "keys": "%",
        "initial": "[hello",
    },
    "percent_unmatched_open_curly": {
        "keys": "%",
        "initial": "{hello",
    },
    "percent_on_non_bracket_char": {
        "keys": "fh%",
        "initial": "x(hello)y",
    },
    "percent_single_paren": {
        "keys": "%",
        "initial": "(",
    },
    "percent_single_close_paren": {
        "keys": "%",
        "initial": ")",
    },

    # ── % multiline complex ───────────────────────────────────
    "percent_multiline_func_call": {
        "keys": "%",
        "initial": "foo(\n  bar,\n  baz\n)",
    },
    "percent_multiline_func_from_end": {
        "keys": "3j%",
        "initial": "foo(\n  bar,\n  baz\n)",
    },
    "percent_multiline_nested_func": {
        "keys": "%",
        "initial": "f(g(\n  x\n))",
    },
    "percent_multiline_curly_block": {
        "keys": "f{%",
        "initial": "if (true) {\n  body\n}",
    },
    "percent_multiline_curly_from_end": {
        "keys": "2j%",
        "initial": "if (true) {\n  body\n}",
    },
    "percent_multiline_bracket_array": {
        "keys": "f[%",
        "initial": "arr = [\n  1,\n  2\n]",
    },

    # ── % with content between brackets ───────────────────────
    "percent_paren_with_inner_text": {
        "keys": "%",
        "initial": "(abc def ghi)",
    },
    "percent_bracket_with_numbers": {
        "keys": "%",
        "initial": "[1, 2, 3]",
    },
    "percent_curly_with_assignment": {
        "keys": "%",
        "initial": "{key: value}",
    },
    "percent_nested_different_types": {
        "keys": "$%",
        "initial": "({[a]})",
    },
    "percent_code_like_expression": {
        "keys": "f(%",
        "initial": "result = func(a, b)",
    },
}
