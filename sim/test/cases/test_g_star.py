"""Tests for g* and g# (search without word boundaries)."""

CASES = {
    # ── g* — search forward without word boundaries ──
    "g_star_basic": {
        "keys": "g*",
        "initial": "the theme is thick\n",
    },
    "g_star_partial_match": {
        "keys": "g*",
        "initial": "cat catfish scatter\n",
    },
    "g_star_wraps_around": {
        "keys": "jg*",
        "initial": "foobar\nfoo baz\nfoo_bar\n",
    },
    "g_star_count": {
        "keys": "2g*",
        "initial": "ab abc abcd ab\n",
    },
    "g_star_vs_star": {
        # * would match only whole word 'the'; g* also matches 'theme', 'other'
        "keys": "g*n",
        "initial": "the theme other\n",
    },

    # ── g# — search backward without word boundaries ──
    "g_hash_basic": {
        "keys": "$bg#",
        "initial": "the theme thick the\n",
    },
    "g_hash_partial": {
        "keys": "$bg#",
        "initial": "catfish cat scatter\n",
    },
    "g_hash_wraps": {
        "keys": "g#",
        "initial": "foobar\nfoo baz\nfoo_bar\n",
    },
}
