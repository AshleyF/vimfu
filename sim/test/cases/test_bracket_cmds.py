"""Tests for bracket commands: [( ]) [{ ]} [[ ]] [] ][."""

CASES = {
    # ── [( — go to previous unmatched ( ──
    "bracket_open_paren": {
        "keys": "f+[(", 
        "initial": "(a + b) * c\n",
    },
    "bracket_open_paren_nested": {
        "keys": "fz[(",
        "initial": "(foo (bar (baz) z) end)\n",
    },
    "bracket_open_paren_multiline": {
        "keys": "j[(",
        "initial": "(\n  hello\n)\n",
    },

    # ── ]) — go to next unmatched ) ──
    "bracket_close_paren": {
        "keys": "])",
        "initial": "(hello world)\n",
    },
    "bracket_close_paren_nested": {
        "keys": "fa])",
        "initial": "(foo (bar) baz)\n",
    },

    # ── [{ — go to previous unmatched { ──
    "bracket_open_brace": {
        "keys": "jf+[{",
        "initial": "{\n  a + b\n}\n",
    },

    # ── ]} — go to next unmatched } ──
    "bracket_close_brace": {
        "keys": "]}",
        "initial": "{ hello }\n",
    },

    # ── [[ — go to previous { in column 0 (section start) ──
    "bracket_section_back": {
        "keys": "3j[[",
        "initial": "{\n  one\n}\n{\n  two\n}\n",
    },

    # ── ]] — go to next { in column 0 (section start) ──
    "bracket_section_forward": {
        "keys": "]]",
        "initial": "{\n  one\n}\n{\n  two\n}\n",
    },

    # ── [] — go to previous } in column 0 (section end) ──
    "bracket_section_end_back": {
        "keys": "5j[]",
        "initial": "{\n  one\n}\n{\n  two\n}\n",
    },

    # ── ][ — go to next } in column 0 (section end) ──
    "bracket_section_end_forward": {
        "keys": "][",
        "initial": "{\n  one\n}\n{\n  two\n}\n",
    },

    # ── Operators with bracket motions ──
    "d_bracket_close_paren": {
        "keys": "d])",
        "initial": "(hello world)\n",
    },
    "d_bracket_open_paren": {
        "keys": "f+d[(",
        "initial": "(a + b)\n",
    },
}
