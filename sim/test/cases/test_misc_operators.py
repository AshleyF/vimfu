"""Misc operators: = (indent), & g& (repeat :s), gq gw (format), g? (rot13)"""

CASES = {
    # == auto-indent (C-style: indent after {, unindent at })
    "indent_current_line": {
        "keys": "j==",
        "initial": "if (true) {\nhello\n}\n",
    },
    "indent_range_with_j": {
        "keys": "j=j",
        "initial": "if (true) {\nhello\nworld\n}\n",
    },
    "indent_visual": {
        "keys": "jVj=",
        "initial": "if (true) {\nhello\nworld\n}\n",
    },
    "indent_brace_unindent": {
        "keys": "=G",
        "initial": "if (true) {\nhello\nworld\n}\n",
    },

    # & repeat last substitution on current line
    "ampersand_repeat_sub": {
        "keys": ":s/foo/bar/\rj&",
        "initial": "foo baz\nfoo qux\n",
    },
    "ampersand_no_prior_sub": {
        "keys": "&",
        "initial": "hello\n",
    },

    # g& repeat last substitution on all lines (like :%s//~/&)
    "g_ampersand_global": {
        "keys": ":s/foo/bar/\rg&",
        "initial": "foo one\nfoo two\nfoo three\n",
    },

    # gq format (with default textwidth=0, gq joins lines in the range)
    "gq_join_lines": {
        "keys": "gqj",
        "initial": "hello\nworld\n",
    },
    "gqq_current_line": {
        "keys": "gqq",
        "initial": "  hello  \n",
    },

    # gw format (like gq but cursor stays)
    "gw_format": {
        "keys": "gwj",
        "initial": "hello\nworld\n",
    },

    # g? rot13
    "g_question_line": {
        "keys": "g?g?",
        "initial": "hello\n",
    },
    "g_question_word": {
        "keys": "g?w",
        "initial": "hello world\n",
    },
    "g_question_visual": {
        "keys": "veg?",
        "initial": "hello world\n",
    },
    "g_question_rot13_roundtrip": {
        "keys": "g?g?g?g?",
        "initial": "hello\n",
    },
}
