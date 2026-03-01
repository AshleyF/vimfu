"""MatchParen highlighting tests.

Tests that the simulator highlights matching brackets when the cursor
is on a bracket character.  Neovim's matchparen plugin highlights both
the bracket under the cursor and its matching partner in MatchParen color
(monokai: f92672 pink foreground).
"""

CASES = {
    # ══════════════════════════════════════════════════════════
    # CURSOR ON OPENING BRACKET
    # ══════════════════════════════════════════════════════════

    "mp_open_paren_at_start": {
        "description": "Cursor on ( at col 0 highlights ( and matching )",
        "keys": "",
        "initial": "(hello)",
    },
    "mp_open_bracket_at_start": {
        "description": "Cursor on [ at col 0 highlights [ and ]",
        "keys": "",
        "initial": "[hello]",
    },
    "mp_open_brace_at_start": {
        "description": "Cursor on { at col 0 highlights { and }",
        "keys": "",
        "initial": "{hello}",
    },

    # ══════════════════════════════════════════════════════════
    # CURSOR ON CLOSING BRACKET
    # ══════════════════════════════════════════════════════════

    "mp_close_paren_at_end": {
        "description": "Cursor on ) highlights ) and matching (",
        "keys": "$",
        "initial": "(hello)",
    },
    "mp_close_bracket_at_end": {
        "description": "Cursor on ] highlights ] and [",
        "keys": "$",
        "initial": "[hello]",
    },
    "mp_close_brace_at_end": {
        "description": "Cursor on } highlights } and {",
        "keys": "$",
        "initial": "{hello}",
    },

    # ══════════════════════════════════════════════════════════
    # EMPTY BRACKETS
    # ══════════════════════════════════════════════════════════

    "mp_empty_parens_on_open": {
        "description": "Cursor on ( of empty () — both highlighted",
        "keys": "",
        "initial": "()",
    },
    "mp_empty_parens_on_close": {
        "description": "Cursor on ) of empty ()",
        "keys": "l",
        "initial": "()",
    },

    # ══════════════════════════════════════════════════════════
    # NESTED BRACKETS
    # ══════════════════════════════════════════════════════════

    "mp_nested_on_inner_open": {
        "description": "Cursor on inner ( of ((inner)) highlights inner pair",
        "keys": "l",
        "initial": "((inner))",
    },
    "mp_nested_on_outer_open": {
        "description": "Cursor on outer ( of ((inner))",
        "keys": "",
        "initial": "((inner))",
    },
    "mp_nested_on_outer_close": {
        "description": "Cursor on outer ) of ((inner))",
        "keys": "$",
        "initial": "((inner))",
    },
    "mp_deeply_nested": {
        "description": "Three levels deep — cursor on innermost (",
        "keys": "ll",
        "initial": "(([x]))",
    },

    # ══════════════════════════════════════════════════════════
    # MULTI-LINE BRACKET MATCHING
    # ══════════════════════════════════════════════════════════

    "mp_multiline_paren_open": {
        "description": "( on line 0, ) on line 2 — cursor on (",
        "keys": "f(",
        "initial": "foo(\n  bar\n)",
    },
    "mp_multiline_paren_close": {
        "description": "( on line 0, ) on line 2 — cursor on )",
        "keys": "2j",
        "initial": "foo(\n  bar\n)",
    },
    "mp_multiline_brace": {
        "description": "{ on line 0, } on line 2 — cursor on {",
        "keys": "f{",
        "initial": "if (x) {\n  body\n}",
    },

    # ══════════════════════════════════════════════════════════
    # UNMATCHED BRACKETS — NO HIGHLIGHT
    # ══════════════════════════════════════════════════════════

    "mp_unmatched_open_paren": {
        "description": "Unmatched ( — no matching ), no highlight on any bracket",
        "keys": "",
        "initial": "(hello world",
    },
    "mp_unmatched_close_paren": {
        "description": "Unmatched ) — no matching (",
        "keys": "$",
        "initial": "hello world)",
    },

    # ══════════════════════════════════════════════════════════
    # CURSOR NOT ON BRACKET — NO HIGHLIGHT
    # ══════════════════════════════════════════════════════════

    "mp_cursor_on_letter": {
        "description": "Cursor on 'h' — no bracket under cursor, no highlight",
        "keys": "l",
        "initial": "(hello)",
    },
    "mp_no_brackets_in_buffer": {
        "description": "No brackets anywhere — no highlight",
        "keys": "",
        "initial": "hello world",
    },

    # ══════════════════════════════════════════════════════════
    # MIXED BRACKET TYPES
    # ══════════════════════════════════════════════════════════

    "mp_mixed_on_paren": {
        "description": "Mixed ([{x}]) — cursor on outer ( highlights matching )",
        "keys": "",
        "initial": "([{x}])",
    },
    "mp_mixed_on_bracket": {
        "description": "Mixed ([{x}]) — cursor on [ highlights matching ]",
        "keys": "l",
        "initial": "([{x}])",
    },
    "mp_mixed_on_brace": {
        "description": "Mixed ([{x}]) — cursor on { highlights matching }",
        "keys": "ll",
        "initial": "([{x}])",
    },

    # ══════════════════════════════════════════════════════════
    # BRACKETS IN MIDDLE OF LINE
    # ══════════════════════════════════════════════════════════

    "mp_paren_mid_line": {
        "description": "Cursor moved to ( in middle of text",
        "keys": "f(",
        "initial": "call foo(arg) end",
    },
    "mp_bracket_mid_line": {
        "description": "Cursor on [ in middle of text",
        "keys": "f[",
        "initial": "arr[idx] = val",
    },

    # ══════════════════════════════════════════════════════════
    # AFTER SURROUND OPERATION
    # ══════════════════════════════════════════════════════════

    "mp_after_ysiw_paren": {
        "description": "After ysiw), cursor on ( — both brackets highlighted",
        "keys": "ysiw)",
        "initial": "hello world",
    },
}
