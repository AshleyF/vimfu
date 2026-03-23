"""Test g<Tab> (last accessed tab), gf/gF (goto file), and bracket [z ]z [/ ]/ [# ]# [* ]* commands."""

CASES = {
    # ── Bracket [z / ]z: fold boundaries ──

    "bracket_open_z_fold_start": {
        "description": "[z moves to start of current open fold",
        "initial": "aaa\nbbb\nccc\nddd\neee\nfff",
        "keys": "zf4jjj[z",
    },

    "bracket_close_z_fold_end": {
        "description": "]z moves to end of current open fold",
        "initial": "aaa\nbbb\nccc\nddd\neee\nfff",
        "keys": "zf4jzo[z]z",
    },

    # ── Bracket [/ ]/ and [* ]*: C comment boundaries ──

    "bracket_open_slash_prev_comment": {
        "description": "[/ goes to start of previous C comment",
        "initial": "code\n/* this is\na comment */\nmore code",
        "keys": "jj[/",
    },

    "bracket_close_slash_next_comment": {
        "description": "]/ goes to end of next C comment",
        "initial": "code\n/* this is\na comment */\nmore code",
        "keys": "]/",
    },

    "bracket_open_star_prev_comment": {
        "description": "[* goes to start of previous /* comment",
        "initial": "code\n/* this is\na comment */\nmore code",
        "keys": "jj[*",
    },

    "bracket_close_star_next_comment": {
        "description": "]* goes to end of next */ comment",
        "initial": "code\n/* this is\na comment */\nmore code",
        "keys": "]*",
    },

    # ── Bracket [# ]#: preprocessor ifdef ──

    "bracket_open_hash_prev_ifdef": {
        "description": "[# goes to previous unmatched #if/#ifdef",
        "initial": "#ifdef FOO\ncode\n#endif",
        "keys": "j[#",
    },

    "bracket_close_hash_next_endif": {
        "description": "]# goes to next unmatched #endif",
        "initial": "#ifdef FOO\ncode\n#endif",
        "keys": "]#",
    },
}
