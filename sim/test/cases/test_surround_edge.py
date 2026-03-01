"""Surround edge case tests.

Additional edge cases for nvim-surround beyond the core test_surround.py.
Covers count motions, nested same-type brackets, angle bracket changes,
aliases, no-match noops, and multi-operation sequences.
"""

CASES = {
    # ══════════════════════════════════════════════════════════
    # ys WITH COUNT MOTIONS
    # ══════════════════════════════════════════════════════════

    "ys_2w_paren": {
        "description": "ys2w) surrounds two words",
        "keys": "ys2w)",
        "initial": "one two three four",
    },
    "ys_3w_bracket": {
        "description": "ys3w] surrounds three words",
        "keys": "ys3w]",
        "initial": "alpha beta gamma delta",
    },
    "ys_2e_brace": {
        "description": "ys2e} surrounds to end of second word",
        "keys": "ys2e}",
        "initial": "foo bar baz qux",
    },
    "ys_2w_quote": {
        "description": "ys2w\" surrounds two words in quotes",
        "keys": "ys2w\"",
        "initial": "hello world today",
    },

    # ══════════════════════════════════════════════════════════
    # ds WITH NESTED SAME-TYPE BRACKETS
    # ══════════════════════════════════════════════════════════

    "ds_nested_paren_inner": {
        "description": "ds) cursor inside inner parens of ((x)) removes inner",
        "keys": "lllds)",
        "initial": "((hello))",
    },
    "ds_nested_bracket_inner": {
        "description": "ds] cursor inside inner brackets of [[x]] removes inner",
        "keys": "lllds]",
        "initial": "[[hello]]",
    },
    "ds_nested_brace_inner": {
        "description": "ds} cursor inside inner braces of {{x}} removes inner",
        "keys": "lllds}",
        "initial": "{{hello}}",
    },

    # ══════════════════════════════════════════════════════════
    # cs WITH ANGLE BRACKETS
    # ══════════════════════════════════════════════════════════

    "cs_angle_to_paren": {
        "description": "cs>) changes <x> to (x)",
        "keys": "cs>)",
        "initial": "<hello>",
    },
    "cs_angle_to_bracket": {
        "description": "cs>] changes <x> to [x]",
        "keys": "cs>]",
        "initial": "<hello>",
    },
    "cs_angle_to_quote": {
        "description": "cs>\" changes <x> to \"x\"",
        "keys": "cs>\"",
        "initial": "<hello>",
    },
    "cs_paren_to_angle": {
        "description": "cs)> changes (x) to <x>",
        "keys": "cs)>",
        "initial": "(hello)",
    },
    "cs_bracket_to_angle": {
        "description": "cs]> changes [x] to <x>",
        "keys": "cs]>",
        "initial": "[hello]",
    },

    # ══════════════════════════════════════════════════════════
    # yss ON WHITESPACE-ONLY LINE
    # ══════════════════════════════════════════════════════════

    "yss_whitespace_only": {
        "description": "yss) on line with only spaces",
        "keys": "yss)",
        "initial": "    ",
    },

    # ══════════════════════════════════════════════════════════
    # MULTIPLE SURROUND OPERATIONS IN SEQUENCE
    # ══════════════════════════════════════════════════════════

    "multi_ys_ys_two_words": {
        "description": "ysiw) then wysiw] — surround two different words",
        "keys": "ysiw)wysiw]",
        "initial": "foo bar baz",
    },
    "multi_ys_cs_ds": {
        "description": "ysiw) then cs)] then ds] — add, change, delete",
        "keys": "ysiw)cs)]ds]",
        "initial": "hello world",
    },
    "multi_ds_ds_nested": {
        "description": "ds) twice on doubly-wrapped word",
        "keys": "llds)ds)",
        "initial": "((word))",
    },

    # ══════════════════════════════════════════════════════════
    # VISUAL S WITH SINGLE CHARACTER SELECTION
    # ══════════════════════════════════════════════════════════

    "visual_S_single_char": {
        "description": "v selects one char, S) wraps just that char",
        "keys": "vS)",
        "initial": "abcdef",
    },
    "visual_S_single_char_mid": {
        "description": "v on middle char, S\" wraps just one char",
        "keys": "llvS\"",
        "initial": "abcdef",
    },

    # ══════════════════════════════════════════════════════════
    # ys WITH b/B/r/a ALIASES
    # ══════════════════════════════════════════════════════════

    "ys_iw_b_alias": {
        "description": "ysiwb wraps in parens (b = paren alias)",
        "keys": "ysiwb",
        "initial": "hello world",
    },
    "ys_iw_B_alias": {
        "description": "ysiwB wraps in braces (B = brace alias)",
        "keys": "ysiwB",
        "initial": "hello world",
    },
    "ys_iw_r_alias": {
        "description": "ysiwr wraps in brackets (r = bracket alias)",
        "keys": "ysiwr",
        "initial": "hello world",
    },
    "ys_iw_a_alias": {
        "description": "ysiwa wraps in angle brackets (a = angle alias)",
        "keys": "ysiwa",
        "initial": "hello world",
    },

    # ══════════════════════════════════════════════════════════
    # ds/cs WHEN NO MATCHING PAIR — NOOP
    # ══════════════════════════════════════════════════════════

    "ds_paren_no_match": {
        "description": "ds) when no parens around cursor — noop",
        "keys": "ds)",
        "initial": "hello world",
    },
    "ds_bracket_no_match": {
        "description": "ds] when no brackets around cursor — noop",
        "keys": "ds]",
        "initial": "hello world",
    },
    "ds_quote_no_match": {
        "description": "ds\" when no quotes around cursor — noop",
        "keys": "ds\"",
        "initial": "hello world",
    },
    "cs_paren_no_match": {
        "description": "cs)] when no parens — noop",
        "keys": "cs)]",
        "initial": "hello world",
    },

    # ══════════════════════════════════════════════════════════
    # ys WITH TEXT OBJECTS (ip, is, aW)
    # ══════════════════════════════════════════════════════════

    "ys_aW_brace": {
        "description": "ysaW} wraps a WORD in braces",
        "keys": "ysaW}",
        "initial": "foo-bar baz",
    },

    # ══════════════════════════════════════════════════════════
    # ys WITH t/T MOTIONS
    # ══════════════════════════════════════════════════════════

    "ys_t_char_paren": {
        "description": "yst.) wraps to just before the period",
        "keys": "yst.)",
        "initial": "hello. world",
    },

    # ══════════════════════════════════════════════════════════
    # DOT REPEAT WITH DIFFERENT SURROUND OPS
    # ══════════════════════════════════════════════════════════

    "dot_after_ds_quote": {
        "description": "ds\" on first quoted string, navigate then . on second",
        "keys": "ds\"f\".",
        "initial": "\"aaa\" \"bbb\" end",
    },
    "dot_after_cs_quote": {
        "description": "cs\"' on first, navigate to second, dot repeat",
        "keys": "cs\"'f\".",
        "initial": "\"foo\" \"bar\" end",
    },

    # ══════════════════════════════════════════════════════════
    # ds< (ANGLE TRIM)
    # ══════════════════════════════════════════════════════════

    "ds_open_angle_trim": {
        "description": "ds< deletes angle brackets and trims inner space",
        "keys": "ds<",
        "initial": "< hello >",
    },

    # ══════════════════════════════════════════════════════════
    # cs CROSS-TYPE: QUOTE ↔ BRACKET
    # ══════════════════════════════════════════════════════════

    "cs_quote_to_paren": {
        "description": "cs\") changes quotes to parens",
        "keys": "cs\")",
        "initial": "\"hello\"",
    },
    "cs_quote_to_bracket": {
        "description": "cs\"] changes quotes to brackets",
        "keys": "cs\"]",
        "initial": "\"hello\"",
    },
    "cs_quote_to_brace": {
        "description": "cs\"} changes quotes to braces",
        "keys": "cs\"}",
        "initial": "\"hello\"",
    },
    "cs_quote_to_angle": {
        "description": "cs\"> changes quotes to angle brackets",
        "keys": "cs\">",
        "initial": "\"hello\"",
    },
    "cs_paren_to_quote": {
        "description": "cs)\" changes parens to double quotes",
        "keys": "cs)\"",
        "initial": "(hello)",
    },
    "cs_bracket_to_quote": {
        "description": "cs]\" changes brackets to double quotes",
        "keys": "cs]\"",
        "initial": "[hello]",
    },
    "cs_brace_to_quote": {
        "description": "cs}\" changes braces to double quotes",
        "keys": "cs}\"",
        "initial": "{hello}",
    },
    "cs_paren_to_single_quote": {
        "description": "cs)' changes parens to single quotes",
        "keys": "cs)'",
        "initial": "(hello)",
    },
    "cs_bracket_to_backtick": {
        "description": "cs]` changes brackets to backticks",
        "keys": "cs]`",
        "initial": "[hello]",
    },

    # ══════════════════════════════════════════════════════════
    # cs BACKTICK AS SOURCE
    # ══════════════════════════════════════════════════════════

    "cs_backtick_to_quote": {
        "description": "cs`\" changes backticks to double quotes",
        "keys": "cs`\"",
        "initial": "`hello`",
    },
    "cs_backtick_to_single_quote": {
        "description": "cs`' changes backticks to single quotes",
        "keys": "cs`'",
        "initial": "`hello`",
    },

    # ══════════════════════════════════════════════════════════
    # cs WITH ALIASES
    # ══════════════════════════════════════════════════════════

    "cs_alias_b_to_bracket": {
        "description": "csb] uses b alias for ) as target",
        "keys": "csb]",
        "initial": "(hello)",
    },
    "cs_alias_r_to_paren": {
        "description": "csr) uses r alias for ] as target",
        "keys": "csr)",
        "initial": "[hello]",
    },
    "cs_alias_B_to_paren": {
        "description": "csB) uses B alias for } as target",
        "keys": "csB)",
        "initial": "{hello}",
    },
    "cs_alias_a_to_paren": {
        "description": "csa) uses a alias for > as target",
        "keys": "csa)",
        "initial": "<hello>",
    },

    # ══════════════════════════════════════════════════════════
    # cs WITH ARBITRARY / SYMMETRIC CHARS
    # ══════════════════════════════════════════════════════════

    "cs_quote_to_star": {
        "description": "cs\"* changes quotes to stars",
        "keys": "cs\"*",
        "initial": "\"hello\"",
    },
    "cs_star_to_quote": {
        "description": "cs*\" changes stars to double quotes",
        "keys": "cs*\"",
        "initial": "*hello*",
    },
    "cs_pipe_to_quote": {
        "description": "cs|\" changes pipes to double quotes",
        "keys": "cs|\"",
        "initial": "|hello|",
    },

    # ══════════════════════════════════════════════════════════
    # cs OPENING TARGET TRIMS (BRACE & ANGLE)
    # ══════════════════════════════════════════════════════════

    "cs_open_brace_trim": {
        "description": "cs{) trims inner space from braces then wraps in parens",
        "keys": "cs{)",
        "initial": "{ hello }",
    },
    "cs_open_angle_trim": {
        "description": "cs<) trims inner space from angles then wraps in parens",
        "keys": "cs<)",
        "initial": "< hello >",
    },

    # ══════════════════════════════════════════════════════════
    # ysiw< (ANGLE WITH SPACE)
    # ══════════════════════════════════════════════════════════

    "ys_iw_open_angle": {
        "description": "ysiw< wraps inner word in angle brackets with space",
        "keys": "ysiw<",
        "initial": "hello world",
    },

    # ══════════════════════════════════════════════════════════
    # VISUAL S — ADDITIONAL DELIMITERS
    # ══════════════════════════════════════════════════════════

    "visual_S_star": {
        "description": "viwS* wraps in stars",
        "keys": "viwS*",
        "initial": "hello world",
    },
    "visual_S_underscore": {
        "description": "viwS_ wraps in underscores",
        "keys": "viwS_",
        "initial": "hello world",
    },
    "visual_linewise_S_quote": {
        "description": "VS\" wraps line in quotes (linewise)",
        "keys": "VS\"",
        "initial": "hello world",
    },
    "visual_linewise_S_bracket": {
        "description": "VS] wraps line in brackets (linewise)",
        "keys": "VS]",
        "initial": "hello world",
    },
}
