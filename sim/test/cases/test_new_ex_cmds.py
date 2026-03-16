"""
Test suite for newly added Ex commands and features:
  :retab[!] [N]    — convert tabs to/from spaces
  :qa[!]           — quit all
  :wa              — write all
  :new             — new buffer in split
  :enew[!]         — edit new unnamed buffer
  :pwd             — show current directory
  :f[ile]          — show file info
  :delm[arks]      — delete marks
  :undol[ist]      — show undo info
  :set wrap/incsearch/list/splitbelow/splitright
  gD               — go to global declaration
  g8               — show hex of char
  K                — keyword lookup
"""

FIVELINES = "\n".join(f"Line {i:02d} content" for i in range(1, 6))
TENLINES = "\n".join(f"Line {i:02d} content" for i in range(1, 11))
ALPHA = "alpha\nbeta\ngamma\ndelta\nepsilon"
TABBED = "\tline one\n\t\tline two\n\tline three"
MIXED_INDENT = "    line one\n\t\tline two\n    line three"

CASES = {
    # ═══════════════════════════════════════════════════════════════
    #  :retab — convert tabs to spaces
    # ═══════════════════════════════════════════════════════════════

    "retab_basic": {
        "keys": ":set expandtab\r:retab\r",
        "initial": TABBED,
    },
    "retab_with_tabstop": {
        "keys": ":set expandtab\r:set ts=4\r:retab\r",
        "initial": TABBED,
    },
    "retab_bang": {
        "keys": ":retab!\r",
        "initial": TABBED,
    },
    "retab_with_N": {
        "keys": ":set expandtab\r:retab 2\r",
        "initial": TABBED,
    },
    "retab_range": {
        "keys": ":set expandtab\r:1,2retab\r",
        "initial": TABBED,
    },
    "retab_abbrev": {
        "keys": ":set expandtab\r:ret\r",
        "initial": TABBED,
    },

    # ═══════════════════════════════════════════════════════════════
    #  :set wrap/nowrap, incsearch, list, splitbelow, splitright
    # ═══════════════════════════════════════════════════════════════

    "set_wrap": {
        "keys": ":set nowrap\r",
        "initial": FIVELINES,
    },
    "set_wrap_toggle": {
        "keys": ":set nowrap\r:set wrap\r",
        "initial": FIVELINES,
    },
    "set_incsearch": {
        "keys": ":set incsearch\r",
        "initial": FIVELINES,
    },
    "set_is_short": {
        "keys": ":set is\r",
        "initial": FIVELINES,
    },
    "set_noincsearch": {
        "keys": ":set is\r:set nois\r",
        "initial": FIVELINES,
    },
    "set_list": {
        "keys": ":set list\r",
        "initial": FIVELINES,
    },
    "set_nolist": {
        "keys": ":set list\r:set nolist\r",
        "initial": FIVELINES,
    },
    "set_splitbelow": {
        "keys": ":set splitbelow\r",
        "initial": FIVELINES,
    },
    "set_sb_short": {
        "keys": ":set sb\r",
        "initial": FIVELINES,
    },
    "set_splitright": {
        "keys": ":set splitright\r",
        "initial": FIVELINES,
    },
    "set_spr_short": {
        "keys": ":set spr\r",
        "initial": FIVELINES,
    },

    # ═══════════════════════════════════════════════════════════════
    #  :delm[arks] — delete marks
    # ═══════════════════════════════════════════════════════════════

    "delmarks_single": {
        "keys": "ma2jmb:delmarks a\r`b",
        "initial": FIVELINES,
    },
    "delmarks_multiple": {
        "keys": "ma2jmb4jmc:delmarks ab\r",
        "initial": FIVELINES,
    },
    "delmarks_bang": {
        "keys": "ma2jmb4jmc:delmarks!\r",
        "initial": FIVELINES,
    },

    # ═══════════════════════════════════════════════════════════════
    #  gD — go to global declaration
    # ═══════════════════════════════════════════════════════════════

    "gD_basic": {
        "keys": "4jfagD",
        "initial": "alpha = 1\nbeta = 2\ngamma = 3\ndelta = 4\nalpha = 5",
    },
    "gD_on_first_occurrence": {
        "keys": "gD",
        "initial": "hello world\nhello again\nhello more",
    },

    # ═══════════════════════════════════════════════════════════════
    #  g8 — show hex of character
    # ═══════════════════════════════════════════════════════════════

    "g8_letter_a": {
        "keys": "g8",
        "initial": "abc",
    },
    "g8_letter_A": {
        "keys": "flg8",
        "initial": "Hello",
    },

    # ═══════════════════════════════════════════════════════════════
    #  K — keyword lookup (NOT testable against nvim — opens man page)
    #  :qa! — NOT testable against nvim — exits the process
    #  :undolist — format differs between nvim and sim
    # These are unit-tested only.
    # ═══════════════════════════════════════════════════════════════

    # ═══════════════════════════════════════════════════════════════
    #  :enew — new empty buffer
    # ═══════════════════════════════════════════════════════════════

    "enew_basic": {
        "keys": ":enew\r",
        "initial": FIVELINES,
    },
    "enew_abbrev": {
        "keys": ":ene\r",
        "initial": FIVELINES,
    },
}
