"""Tests for video range 0317-0327: bracket motions ([ and ] commands)."""

CODE = (
    "function outer() {\n"
    "    if (a) {\n"
    "        do_one();\n"
    "    }\n"
    "    while (b) {\n"
    "        do_two();\n"
    "    }\n"
    "}\n"
    "\n"
    "function next() {\n"
    "    return 42;\n"
    "}\n"
)

PARENS = (
    "alpha (one, two,\n"
    "      (three, four)\n"
    "      five) end\n"
)

PREP = (
    "#include <stdio.h>\n"
    "#ifdef DEBUG\n"
    "  int x = 1;\n"
    "#endif\n"
    "int main(void) {\n"
    "    return 0;\n"
    "}\n"
)

CCOMMENT = (
    "int a = 1;\n"
    "/* first comment */\n"
    "int b = 2;\n"
    "/* second\n"
    "   block */\n"
    "int c = 3;\n"
)

CASES = {
    # ── 0317 [( ]) — unmatched parens ──────────────────────────
    # Cursor inside nested parens; [( goes to enclosing unmatched (
    "bracket_paren_simple": {
        "description": "[( finds unmatched ( from inside nested parens",
        "keys": "3Gfn[(",
        "initial": PARENS,
    },
    "bracket_paren_forward": {
        "description": "]) finds unmatched ) from inside nested parens",
        "keys": "1Gfa])",
        "initial": PARENS,
    },

    # ── 0318 [{ ]} — unmatched braces ──────────────────────────
    "bracket_brace_back": {
        "description": "[{ jumps to enclosing open brace",
        "keys": "3G[{",
        "initial": CODE,
    },
    "bracket_brace_forward": {
        "description": "]} jumps to enclosing close brace",
        "keys": "3G]}",
        "initial": CODE,
    },

    # ── 0319 [[ ]] — sections (col-0 '{') ──────────────────────
    "bracket_section_forward": {
        "description": "]] jumps to next col-0 '{'",
        "keys": "1G]]",
        "initial": CODE,
    },
    "bracket_section_back": {
        "description": "[[ jumps to prev col-0 '{'",
        "keys": "11G[[",
        "initial": CODE,
    },

    # ── 0320 [] ][ — section ends (col-0 '}') ──────────────────
    "bracket_section_end_forward": {
        "description": "][ jumps to next col-0 '}'",
        "keys": "1G][",
        "initial": CODE,
    },
    "bracket_section_end_back": {
        "description": "[] jumps to prev col-0 '}'",
        "keys": "12G[]",
        "initial": CODE,
    },

    # ── 0321 [m ]m — methods ('{') ─────────────────────────────
    "bracket_method_forward": {
        "description": "]m jumps to next '{'",
        "keys": "1G]m",
        "initial": CODE,
    },
    "bracket_method_back": {
        "description": "[m jumps to previous '{'",
        "keys": "11G[m",
        "initial": CODE,
    },

    # ── 0324 [# ]# — preprocessor #if / #endif ─────────────────
    "bracket_hash_back": {
        "description": "[# jumps to previous #if/#ifdef",
        "keys": "3G[#",
        "initial": PREP,
    },
    "bracket_hash_forward": {
        "description": "]# jumps to next #endif",
        "keys": "2G]#",
        "initial": PREP,
    },

    # ── 0325 [* ]* — C comment (/* ... */) ─────────────────────
    "bracket_star_back": {
        "description": "[* jumps to previous /*",
        "keys": "6G[*",
        "initial": CCOMMENT,
    },
    "bracket_star_forward": {
        "description": "]* jumps to next */",
        "keys": "1G]*",
        "initial": CCOMMENT,
    },

    # ── 0326 ['  ]' — navigate lowercase marks ──────────────────
    "bracket_quote_forward": {
        "description": "]' jumps to next lowercase mark",
        "keys": "1Gmaj2jmbgg]'",
        "initial": CODE,
    },
    "bracket_quote_back": {
        "description": "['  jumps to previous lowercase mark",
        "keys": "1Gmaj2jmbG['",
        "initial": CODE,
    },
}
