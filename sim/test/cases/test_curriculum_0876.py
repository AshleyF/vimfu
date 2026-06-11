"""Tests for video range 0876-0879f: :set toggle/query/fileformat features."""

CONTENT_5 = "alpha\nbeta\ngamma\ndelta\nepsilon"
CONTENT_TABS = "abc\tdef\tghi\nfoo\tbar\tbaz"
LONG_LINE = "This is a very long line that definitely exceeds forty columns and should wrap."

CASES = {
    # ── 0876 :set cursorline ─────────────────────────────────────
    "set_cursorline_on": {
        "description": ":set cursorline highlights the current line",
        "keys": ":set cursorline\r",
        "initial": CONTENT_5,
    },
    "set_cursorline_off": {
        "description": ":set nocursorline turns it off again",
        "keys": ":set cursorline\r:set nocursorline\r",
        "initial": CONTENT_5,
    },
    "set_cul_short": {
        "description": "Short form :set cul",
        "keys": ":set cul\r",
        "initial": CONTENT_5,
    },

    # ── 0877 :set option! (toggle) ───────────────────────────────
    "set_number_bang_on": {
        "description": ":set number! toggles number on (initially off)",
        "keys": ":set number!\r",
        "initial": CONTENT_5,
    },
    "set_number_bang_off": {
        "description": ":set number! toggles number off again",
        "keys": ":set number\r:set number!\r",
        "initial": CONTENT_5,
    },
    "set_cul_bang_toggle": {
        "description": ":set cursorline! toggles cursorline",
        "keys": ":set cursorline!\r",
        "initial": CONTENT_5,
    },

    # ── 0878 :set option? (query) ────────────────────────────────
    "set_number_query_off": {
        "description": ":set number? shows 'nonumber' when off",
        "keys": ":set number?\r",
        "initial": CONTENT_5,
    },
    "set_number_query_on": {
        "description": ":set number? shows 'number' after enabling",
        "keys": ":set number\r:set number?\r",
        "initial": CONTENT_5,
    },
    "set_tabstop_query": {
        "description": ":set tabstop? shows tabstop=8 (default)",
        "keys": ":set tabstop?\r",
        "initial": CONTENT_5,
    },
    "set_ts_short_query": {
        "description": "Short alias :set ts? equivalent to :set tabstop?",
        "keys": ":set ts?\r",
        "initial": CONTENT_5,
    },

    # ── 0879 :set numeric values ─────────────────────────────────
    "set_scrolloff_value": {
        "description": ":set scrolloff=3 sets numeric value",
        "keys": ":set scrolloff=3\r:set scrolloff?\r",
        "initial": CONTENT_5,
    },
    "set_tabstop_value": {
        "description": ":set tabstop=2 then query",
        "keys": ":set tabstop=2\r:set ts?\r",
        "initial": CONTENT_TABS,
    },

    # ── 0879a :set wrap / nowrap ─────────────────────────────────
    "set_nowrap_long_line": {
        "description": ":set nowrap stops line wrapping",
        "keys": ":set nowrap\r",
        "initial": LONG_LINE,
    },
    "set_wrap_back": {
        "description": ":set wrap turns wrapping back on",
        "keys": ":set nowrap\r:set wrap\r",
        "initial": LONG_LINE,
    },

    # ── 0879b :set list ──────────────────────────────────────────
    "set_list_shows_tabs": {
        "description": ":set list shows tab chars and end-of-line markers",
        "keys": ":set list\r",
        "initial": CONTENT_TABS,
    },
    "set_nolist_back": {
        "description": ":set nolist hides whitespace markers again",
        "keys": ":set list\r:set nolist\r",
        "initial": CONTENT_TABS,
    },

    # ── 0879e :set spell ─────────────────────────────────────────
    # NOTE: Spell highlight differs by dictionary content (sim ships a small
    # English wordlist; nvim uses the system spell file). We skip the visual
    # comparison for spell flagged-words and only test that :set spell? toggles
    # cleanly via a query that doesn't trigger word flagging.
    "set_spell_query_off": {
        "description": ":set spell? when disabled",
        "keys": ":set spell?\r",
        "initial": "1234567890",
    },
    "set_spell_query_on": {
        "description": ":set spell? after enabling, content has no words",
        "keys": ":set spell\r:set spell?\r",
        "initial": "1234567890",
    },

    # ── 0879f :set fileformat ────────────────────────────────────
    "set_ff_query_default": {
        "description": ":set fileformat? shows current value",
        "keys": ":set fileformat?\r",
        "initial": CONTENT_5,
    },
    "set_ff_dos": {
        "description": ":set fileformat=dos sets ff to dos",
        "keys": ":set fileformat=dos\r:set ff?\r",
        "initial": CONTENT_5,
    },
    "set_ff_unix": {
        "description": ":set ff=unix sets ff to unix",
        "keys": ":set ff=unix\r:set ff?\r",
        "initial": CONTENT_5,
    },
}
