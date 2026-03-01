"""Comprehensive surround.vim tests.

Tests nvim-surround (kylechui/nvim-surround) which is compatible with
Tim Pope's surround.vim keybindings: ds (delete), cs (change), ys (add),
and visual S (wrap selection).

Covers curriculum items 700–742.
"""

CASES = {
    # ══════════════════════════════════════════════════════════
    # ds — DELETE SURROUNDING
    # ══════════════════════════════════════════════════════════

    # ── ds" / ds' / ds` — delete quotes ─────────────────────
    "ds_double_quote": {
        "description": "ds\" removes surrounding double quotes",
        "keys": "ds\"",
        "initial": "\"hello world\"",
    },
    "ds_double_quote_cursor_middle": {
        "description": "ds\" with cursor in middle of quoted text",
        "keys": "fwds\"",
        "initial": "\"hello world\"",
    },
    "ds_single_quote": {
        "description": "ds' removes surrounding single quotes",
        "keys": "ds'",
        "initial": "'hello'",
    },
    "ds_backtick": {
        "description": "ds` removes surrounding backticks",
        "keys": "ds`",
        "initial": "`hello`",
    },
    "ds_quote_with_surrounding_text": {
        "description": "ds\" with text before and after",
        "keys": "f\"lds\"",
        "initial": "say \"hello\" now",
    },

    # ── ds) / dsb / ds( — delete parentheses ────────────────
    "ds_close_paren": {
        "description": "ds) removes parentheses",
        "keys": "ds)",
        "initial": "(hello)",
    },
    "ds_paren_alias_b": {
        "description": "dsb removes parentheses (b is alias for ))",
        "keys": "dsb",
        "initial": "(hello)",
    },
    "ds_open_paren_trims_space": {
        "description": "ds( removes parens AND trims inner space",
        "keys": "ds(",
        "initial": "( hello )",
    },
    "ds_close_paren_keeps_space": {
        "description": "ds) removes parens but keeps inner space",
        "keys": "ds)",
        "initial": "( hello )",
    },

    # ── ds] / dsr / ds[ — delete brackets ───────────────────
    "ds_close_bracket": {
        "description": "ds] removes brackets",
        "keys": "ds]",
        "initial": "[hello]",
    },
    "ds_bracket_alias_r": {
        "description": "dsr removes brackets (r is alias for ])",
        "keys": "dsr",
        "initial": "[hello]",
    },
    "ds_open_bracket_trims_space": {
        "description": "ds[ removes brackets AND trims inner space",
        "keys": "ds[",
        "initial": "[ hello ]",
    },

    # ── ds} / dsB / ds{ — delete braces ─────────────────────
    "ds_close_brace": {
        "description": "ds} removes braces",
        "keys": "ds}",
        "initial": "{hello}",
    },
    "ds_brace_alias_B": {
        "description": "dsB removes braces",
        "keys": "dsB",
        "initial": "{hello}",
    },
    "ds_open_brace_trims_space": {
        "description": "ds{ removes braces AND trims inner space",
        "keys": "ds{",
        "initial": "{ hello }",
    },

    # ── ds> / dsa — delete angle brackets ────────────────────
    "ds_close_angle": {
        "description": "ds> removes angle brackets",
        "keys": "ds>",
        "initial": "<hello>",
    },
    "ds_angle_alias_a": {
        "description": "dsa removes angle brackets",
        "keys": "dsa",
        "initial": "<hello>",
    },

    # ── ds with arbitrary punctuation ────────────────────────
    "ds_pipe": {
        "description": "ds| removes pipes",
        "keys": "ds|",
        "initial": "|hello|",
    },
    "ds_asterisk": {
        "description": "ds* removes asterisks",
        "keys": "ds*",
        "initial": "*hello*",
    },
    "ds_underscore": {
        "description": "ds_ removes underscores",
        "keys": "ds_",
        "initial": "_hello_",
    },
    "ds_slash": {
        "description": "ds/ removes slashes",
        "keys": "ds/",
        "initial": "/hello/",
    },
    "ds_tilde": {
        "description": "ds~ removes tildes",
        "keys": "ds~",
        "initial": "~hello~",
    },

    # ── ds edge cases ────────────────────────────────────────
    "ds_nested_parens_inner": {
        "description": "ds) removes innermost parens when nested",
        "keys": "fhds)",
        "initial": "((hello))",
    },
    "ds_with_surrounding_text": {
        "description": "ds) with text around the parens",
        "keys": "fhds)",
        "initial": "foo (hello) bar",
    },
    "ds_multiword_content": {
        "description": "ds\" with multiple words inside",
        "keys": "fhds\"",
        "initial": "\"hello world foo\"",
    },

    # ══════════════════════════════════════════════════════════
    # cs — CHANGE SURROUNDING
    # ══════════════════════════════════════════════════════════

    # ── cs basic quote changes ───────────────────────────────
    "cs_double_to_single": {
        "description": "cs\"' changes double to single quotes",
        "keys": "cs\"'",
        "initial": "\"hello\"",
    },
    "cs_single_to_double": {
        "description": "cs'\" changes single to double quotes",
        "keys": "cs'\"",
        "initial": "'hello'",
    },
    "cs_double_to_backtick": {
        "description": "cs\"` changes double quotes to backticks",
        "keys": "cs\"`",
        "initial": "\"hello\"",
    },

    # ── cs bracket changes ───────────────────────────────────
    "cs_bracket_to_paren": {
        "description": "cs]) changes brackets to parens",
        "keys": "cs])",
        "initial": "[hello]",
    },
    "cs_paren_to_bracket": {
        "description": "cs)[  changes parens to brackets (open = add space)",
        "keys": "cs)[",
        "initial": "(hello)",
    },
    "cs_paren_to_brace_close": {
        "description": "cs)} changes parens to braces (close = no space)",
        "keys": "cs)}",
        "initial": "(hello)",
    },
    "cs_brace_to_paren": {
        "description": "cs}) changes braces to parens",
        "keys": "cs})",
        "initial": "{hello}",
    },
    "cs_bracket_to_angle": {
        "description": "cs]> changes brackets to angle brackets",
        "keys": "cs]>",
        "initial": "[hello]",
    },

    # ── cs with space adding (opening mark as replacement) ───
    "cs_close_to_open_paren": {
        "description": "cs)( adds space inside parens",
        "keys": "cs)(",
        "initial": "(hello)",
    },
    "cs_close_to_open_brace": {
        "description": "cs){ adds space inside braces",
        "keys": "cs){",
        "initial": "(hello)",
    },
    "cs_close_to_open_bracket": {
        "description": "cs)[ adds space inside brackets",
        "keys": "cs)[",
        "initial": "(hello)",
    },

    # ── cs with space trimming (opening mark as target) ──────
    "cs_open_paren_trims_space": {
        "description": "cs(} trims inner space and changes to braces",
        "keys": "cs(}",
        "initial": "( hello )",
    },
    "cs_open_bracket_trims_space": {
        "description": "cs[) trims inner space and changes to parens",
        "keys": "cs[)",
        "initial": "[ hello ]",
    },

    # ── cs with surrounding text ─────────────────────────────
    "cs_in_context": {
        "description": "cs\"' with text around the quotes",
        "keys": "fhcs\"'",
        "initial": "say \"hello\" now",
    },
    "cs_paren_in_context": {
        "description": "cs)] with text around the parens",
        "keys": "fhcs)]",
        "initial": "call(hello) end",
    },

    # ══════════════════════════════════════════════════════════
    # ys — ADD SURROUNDING (you surround)
    # ══════════════════════════════════════════════════════════

    # ── ysiw — surround inner word ───────────────────────────
    "ys_iw_close_paren": {
        "description": "ysiw) wraps word in parens (no space)",
        "keys": "ysiw)",
        "initial": "hello world",
    },
    "ys_iw_open_paren": {
        "description": "ysiw( wraps word in parens with space",
        "keys": "ysiw(",
        "initial": "hello world",
    },
    "ys_iw_close_bracket": {
        "description": "ysiw] wraps word in brackets (no space)",
        "keys": "ysiw]",
        "initial": "hello world",
    },
    "ys_iw_open_bracket": {
        "description": "ysiw[ wraps word in brackets with space",
        "keys": "ysiw[",
        "initial": "hello world",
    },
    "ys_iw_close_brace": {
        "description": "ysiw} wraps word in braces (no space)",
        "keys": "ysiw}",
        "initial": "hello world",
    },
    "ys_iw_open_brace": {
        "description": "ysiw{ wraps word in braces with space",
        "keys": "ysiw{",
        "initial": "hello world",
    },
    "ys_iw_double_quote": {
        "description": "ysiw\" wraps word in double quotes",
        "keys": "ysiw\"",
        "initial": "hello world",
    },
    "ys_iw_single_quote": {
        "description": "ysiw' wraps word in single quotes",
        "keys": "ysiw'",
        "initial": "hello world",
    },
    "ys_iw_backtick": {
        "description": "ysiw` wraps word in backticks",
        "keys": "ysiw`",
        "initial": "hello world",
    },
    "ys_iw_angle": {
        "description": "ysiw> wraps word in angle brackets",
        "keys": "ysiw>",
        "initial": "hello world",
    },

    # ── ysiw on non-first word ───────────────────────────────
    "ys_iw_second_word": {
        "description": "ysiw) on second word",
        "keys": "wysiw)",
        "initial": "hello world today",
    },
    "ys_iw_middle_of_word": {
        "description": "ysiw) with cursor in middle of word",
        "keys": "llysiw)",
        "initial": "hello world",
    },

    # ── ysiw with arbitrary chars ────────────────────────────
    "ys_iw_pipe": {
        "description": "ysiw| wraps word in pipes",
        "keys": "ysiw|",
        "initial": "hello world",
    },
    "ys_iw_asterisk": {
        "description": "ysiw* wraps word in asterisks",
        "keys": "ysiw*",
        "initial": "hello world",
    },
    "ys_iw_underscore": {
        "description": "ysiw_ wraps word in underscores",
        "keys": "ysiw_",
        "initial": "hello world",
    },

    # ── ys with aw (a word — includes space) ─────────────────
    "ys_aw_paren": {
        "description": "ysaw) wraps a-word in parens",
        "keys": "ysaw)",
        "initial": "hello world",
    },

    # ── ys with iW/aW (WORD) ────────────────────────────────
    "ys_iW_brace": {
        "description": "ysiW} wraps WORD in braces",
        "keys": "ysiW}",
        "initial": "foo-bar baz",
    },

    # ── ys with motions ─────────────────────────────────────
    "ys_dollar_quote": {
        "description": "ys$\" wraps to end of line in quotes",
        "keys": "ys$\"",
        "initial": "hello world",
    },
    "ys_w_paren": {
        "description": "ysw) wraps from cursor to next word boundary",
        "keys": "ysw)",
        "initial": "hello world today",
    },
    "ys_e_paren": {
        "description": "yse) wraps to end of word",
        "keys": "yse)",
        "initial": "hello world today",
    },
    "ys_f_char_paren": {
        "description": "ysf.) wraps up to and including the period",
        "keys": "ysf.)",
        "initial": "hello. world",
    },

    # ── yss — surround whole line ────────────────────────────
    "yss_paren": {
        "description": "yss) wraps entire line in parens (strips leading whitespace)",
        "keys": "yss)",
        "initial": "hello world",
    },
    "yss_bracket": {
        "description": "yss] wraps entire line in brackets",
        "keys": "yss]",
        "initial": "hello world",
    },
    "yss_brace": {
        "description": "yss} wraps entire line in braces",
        "keys": "yss}",
        "initial": "hello world",
    },
    "yss_quote": {
        "description": "yss\" wraps entire line in double quotes",
        "keys": "yss\"",
        "initial": "hello world",
    },
    "yss_with_indent": {
        "description": "yss) on indented line preserves indent",
        "keys": "yss)",
        "initial": "    hello world",
    },

    # ══════════════════════════════════════════════════════════
    # VISUAL S — SURROUND SELECTION
    # ══════════════════════════════════════════════════════════

    "visual_S_paren": {
        "description": "Visual select then S) wraps in parens",
        "keys": "viwS)",
        "initial": "hello world",
    },
    "visual_S_bracket": {
        "description": "Visual select then S] wraps in brackets",
        "keys": "viwS]",
        "initial": "hello world",
    },
    "visual_S_brace": {
        "description": "Visual select then S} wraps in braces",
        "keys": "viwS}",
        "initial": "hello world",
    },
    "visual_S_double_quote": {
        "description": "Visual select then S\" wraps in double quotes",
        "keys": "viwS\"",
        "initial": "hello world",
    },
    "visual_S_single_quote": {
        "description": "Visual select then S' wraps in single quotes",
        "keys": "viwS'",
        "initial": "hello world",
    },
    "visual_S_backtick": {
        "description": "Visual select then S` wraps in backticks",
        "keys": "viwS`",
        "initial": "hello world",
    },
    "visual_S_angle": {
        "description": "Visual select then S> wraps in angle brackets",
        "keys": "viwS>",
        "initial": "hello world",
    },
    "visual_S_partial_word": {
        "description": "Visual select partial text then S)",
        "keys": "vllS)",
        "initial": "hello world",
    },
    "visual_S_multiple_words": {
        "description": "Visual select multiple words then S\"",
        "keys": "v2wS\"",
        "initial": "one two three four",
    },
    "visual_S_open_paren_space": {
        "description": "Visual S( adds space inside parens",
        "keys": "viwS(",
        "initial": "hello world",
    },
    "visual_S_pipe": {
        "description": "Visual S| wraps in pipes",
        "keys": "viwS|",
        "initial": "hello world",
    },

    # ── Visual line S ────────────────────────────────────────
    "visual_line_S_paren": {
        "description": "Visual line then S) wraps line in parens",
        "keys": "VS)",
        "initial": "hello world",
    },

    # ══════════════════════════════════════════════════════════
    # DOT REPEAT
    # ══════════════════════════════════════════════════════════

    "dot_repeat_ds": {
        "description": "ds\" then dot repeats on next occurrence",
        "keys": "ds\"j0f\"lds\"",
        "initial": "\"hello\"\n\"world\"",
    },
    "dot_repeat_ysiw": {
        "description": "ysiw) then dot on next word",
        "keys": "ysiw)w.",
        "initial": "hello world today",
    },
    "dot_repeat_cs": {
        "description": "cs\"' then dot on next occurrence",
        "keys": "cs\"'jfhcs\"'",
        "initial": "\"hello\"\n\"world\"",
    },

    # ══════════════════════════════════════════════════════════
    # UNDO / REDO
    # ══════════════════════════════════════════════════════════

    "undo_ds": {
        "description": "ds\" then undo restores quotes",
        "keys": "ds\"u",
        "initial": "\"hello\"",
    },
    "undo_cs": {
        "description": "cs\"' then undo restores original",
        "keys": "cs\"'u",
        "initial": "\"hello\"",
    },
    "undo_ys": {
        "description": "ysiw) then undo removes parens",
        "keys": "ysiw)u",
        "initial": "hello world",
    },
    "undo_visual_S": {
        "description": "visual S) then undo",
        "keys": "viwS)u",
        "initial": "hello world",
    },

    # ══════════════════════════════════════════════════════════
    # COMBINED / INTERACTION TESTS
    # ══════════════════════════════════════════════════════════

    "ds_then_ys": {
        "description": "Delete surrounding then add new ones",
        "keys": "ds\"ysiw)",
        "initial": "\"hello\" world",
    },
    "cs_then_ds": {
        "description": "Change surrounding then delete them",
        "keys": "cs\"'ds'",
        "initial": "\"hello\" world",
    },
    "ys_then_cs": {
        "description": "Add surrounding then change them",
        "keys": "ysiw)cs)]",
        "initial": "hello world",
    },
    "ys_then_ds": {
        "description": "Add surrounding then delete them",
        "keys": "ysiw)ds)",
        "initial": "hello world",
    },
    "nested_ds": {
        "description": "ds) on nested parens: inner first, then outer",
        "keys": "fhds)0fhds)",
        "initial": "((hello))",
    },
    "cs_quotes_in_multiline": {
        "description": "cs\"' on a line in a multiline buffer",
        "keys": "jfhcs\"'",
        "initial": "line one\n\"hello world\"\nline three",
    },
    "ys_iw_in_multiline": {
        "description": "ysiw) on a specific word in multiline buffer",
        "keys": "jwysiw)",
        "initial": "line one\nhello world\nline three",
    },
    "visual_S_in_multiline": {
        "description": "Visual S\" on word in multiline buffer",
        "keys": "jwviwS\"",
        "initial": "line one\nhello world\nline three",
    },

    # ══════════════════════════════════════════════════════════
    # EDGE CASES
    # ══════════════════════════════════════════════════════════

    "ds_empty_content": {
        "description": "ds\" on empty quoted string",
        "keys": "ds\"",
        "initial": "\"\"",
    },
    "ds_single_char_content": {
        "description": "ds\" with single char inside",
        "keys": "fads\"",
        "initial": "\"a\"",
    },
    "cs_empty_content": {
        "description": "cs\"' on empty quoted string",
        "keys": "cs\"'",
        "initial": "\"\"",
    },
    "ys_single_char_word": {
        "description": "ysiw) on a single-character word",
        "keys": "ysiw)",
        "initial": "a b c",
    },
    "yss_empty_line": {
        "description": "yss) on empty line",
        "keys": "yss)",
        "initial": "",
    },
    "yss_single_word": {
        "description": "yss) on single word line",
        "keys": "yss)",
        "initial": "hello",
    },
    "ds_no_match_noop": {
        "description": "ds\" when no quotes around cursor — should be no-op",
        "keys": "ds\"",
        "initial": "hello world",
    },
    "cs_no_match_noop": {
        "description": "cs\"' when no quotes around cursor — should be no-op",
        "keys": "cs\"'",
        "initial": "hello world",
    },
}
