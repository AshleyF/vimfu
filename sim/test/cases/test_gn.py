"""Tests for gn and gN (search and visually select match, or operate on match)."""

CASES = {
    # ── gn — search forward, select match ──
    "gn_basic_select": {
        "keys": "/foo\rgn",
        "initial": "bar foo baz\n",
    },
    "gn_from_on_match": {
        "keys": "/foo\rgn",
        "initial": "foo bar foo\n",
    },
    "gn_delete_match": {
        "keys": "/foo\rdgn",
        "initial": "bar foo baz\n",
    },
    "gn_change_match": {
        "keys": "/foo\rcgnXYZ\x1b",
        "initial": "bar foo baz foo end\n",
    },
    "gn_dot_repeat": {
        "keys": "/foo\rcgnXYZ\x1b.",
        "initial": "foo bar foo baz\n",
    },
    "gn_wraps_around": {
        "keys": "/foo\rjjgn",
        "initial": "foo\nbar\nbaz\n",
    },

    # ── gN — search backward, select match ──
    "gN_basic_select": {
        "keys": "/foo\r$gN",
        "initial": "foo bar baz\n",
    },
    "gN_delete_match": {
        "keys": "/foo\r$dgN",
        "initial": "bar foo baz\n",
    },
}
