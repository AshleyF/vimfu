"""Tests for video range 0466-0490: star-dot pattern, gn idioms,
special registers (. : /), mapping, custom operator."""

FOO_LINES = "foo bar\nfoo baz\nfoo qux\nfoo end\n"

OLD_LINES = "old apple\nold banana\nold cherry\nold date\n"

CASES = {
    # ── 0466 Star-dot pattern: * cw...esc n. ─────────────────
    "star_cw_dot_repeat": {
        "description": "* finds foo, cw replaces with bar, n. repeats on each",
        "keys": "*cwbar\x1bn.n.n.",
        "initial": FOO_LINES,
    },

    # ── 0477 gn with dot: /pat cgn replacement esc . . . ────
    "cgn_dot_repeat": {
        "description": "/old then cgn type new esc, then . . . for each match",
        "keys": "/old\rcgnnew\x1b...",
        "initial": OLD_LINES,
    },

    # ── 0483 . register — last inserted text ─────────────────
    "dot_register_paste": {
        "description": "after inserting 'hello', \"\".p pastes from the . register",
        "keys": "ihello\x1bo\x1b\"\".p",
        "initial": "first\n",
    },

    # ── 0484 : register — last command line ─────────────────
    "colon_register_paste": {
        "description": "after :set number, \":p pastes ':set number'",
        "keys": ":set number\ro\x1b\":p",
        "initial": "first\n",
    },

    # ── 0485 / register — last search pattern ────────────────
    "slash_register_paste": {
        "description": "after /old, \"/p pastes 'old'",
        "keys": "/old\ro\x1b\"/p",
        "initial": OLD_LINES,
    },

    # ── 0476 :map Y to y$ ───────────────────────────────────
    "map_Y_to_y_dollar": {
        "description": ":nnoremap Y y$ then Y yanks to end of line, then p pastes",
        "keys": ":nnoremap Y y$\r0YA <-pasted: \x1bp",
        "initial": "hello world\nsecond\n",
    },
}
