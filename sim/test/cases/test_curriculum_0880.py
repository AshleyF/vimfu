"""
Test suite for curriculum-driven feature coverage from the 0880 series of
VimFu shorts (shell commands, buffers, tabs, splits, marks management,
substitute with backreferences, etc.).

Many of these features were already implemented but lacked direct test
coverage tied to the actual ways the videos demonstrate them.
"""

FIVE = "alpha\nbeta\ngamma\ndelta\nepsilon"
TEN = "\n".join(f"line {i}" for i in range(1, 11))
PROSE = "hello world\nfoo bar\nbaz quux"
WORDS = "alice bob\ncarol dave\neve frank"

CASES = {
    # ── :s captured groups (0880aa) ──────────────────────────────
    "sub_capture_swap": {
        "description": ":s/\\(w\\)\\s\\(w\\)/\\2 \\1/ swaps two words via capture groups",
        "keys": ":%s/\\(\\w\\+\\) \\(\\w\\+\\)/\\2, \\1/\r",
        "initial": WORDS,
    },
    "sub_capture_single_group": {
        "description": "Single capture group reordering",
        "keys": ":%s/\\(\\w\\+\\)/[\\1]/g\r",
        "initial": "abc def",
    },
    "sub_capture_three": {
        "description": "Three capture groups",
        "keys": ":%s/\\(\\w\\+\\) \\(\\w\\+\\) \\(\\w\\+\\)/\\3 \\2 \\1/\r",
        "initial": "one two three",
    },

    # ── :s & backreference (0880z) ───────────────────────────────
    "sub_amp_wrap": {
        "description": "& in replacement = full match; wrap each word in brackets",
        "keys": ":%s/\\w\\+/[&]/g\r",
        "initial": "abc def",
    },
    "sub_amp_prefix": {
        "description": "& prefixed by ' - ' on every line",
        "keys": ":%s/.*/ - &/\r",
        "initial": PROSE,
    },

    # ── :s alternate delimiters (0880y) ──────────────────────────
    "sub_alt_hash_delim": {
        "description": "Use # as alt delimiter to avoid escaping /",
        "keys": ":%s#/usr/local#/opt#g\r",
        "initial": "/usr/local/bin\n/usr/local/lib",
    },
    "sub_alt_bang_delim": {
        "description": "Use ! as alt delimiter",
        "keys": ":%s!/usr/local!/opt!g\r",
        "initial": "/usr/local/bin\n/usr/local/lib",
    },
    "sub_alt_at_delim": {
        "description": "Use @ as alt delimiter",
        "keys": ":%s@foo@bar@g\r",
        "initial": "foo and foo and bar",
    },

    # ── :file — show file info (0880x) ───────────────────────────
    "file_info_unmodified": {
        "description": ":file shows current file info on cmdline",
        "keys": ":file\r",
        "initial": FIVE,
    },
    "file_info_after_modify": {
        "description": ":file shows [Modified] after editing",
        "keys": "i!\x1b:file\r",
        "initial": FIVE,
    },

    # ── :pwd (0880w) ─────────────────────────────────────────────
    "pwd_basic": {
        "description": ":pwd prints current dir",
        "keys": ":pwd\r",
        "initial": FIVE,
    },

    # ── :ls — list buffers (0880b) ───────────────────────────────
    "ls_single_buffer": {
        "description": ":ls shows the single open buffer",
        "keys": ":ls\r",
        "initial": FIVE,
    },
    "buffers_single": {
        "description": ":buffers same as :ls",
        "keys": ":buffers\r",
        "initial": FIVE,
    },
    "ls_after_enew": {
        "description": ":ls shows two buffers after :enew",
        "keys": ":enew\r:ls\r",
        "initial": FIVE,
    },

    # ── :bn / :bp / :bd (0880c, 0880e) ───────────────────────────
    "bn_with_enew": {
        "description": "After :enew, :bn cycles back to original",
        "keys": ":enew\r:bn\r",
        "initial": FIVE,
    },
    "bp_with_enew": {
        "description": "After :enew, :bp cycles to previous",
        "keys": ":enew\r:bp\r",
        "initial": FIVE,
    },
    "bd_after_enew": {
        "description": ":bd deletes the new empty buffer",
        "keys": ":enew\r:bd\r",
        "initial": FIVE,
    },

    # ── Ctrl-^ alternate buffer (0880g) ──────────────────────────
    "alternate_ctrl_caret_after_enew": {
        "description": "Ctrl-^ swaps back to alternate buffer after :enew",
        "keys": ":enew\r\x1e",
        "initial": FIVE,
    },

    # ── :tabnew / gt / gT / :tabc / :tabo (0880h-k) ──────────────
    "tabnew_basic": {
        "description": ":tabnew opens an empty tab; tabline appears",
        "keys": ":tabnew\r",
        "initial": FIVE,
    },
    "tabnew_then_gT": {
        "description": "gT goes back to the previous (first) tab",
        "keys": ":tabnew\rgT",
        "initial": FIVE,
    },
    "tabnew_then_gt_cycles": {
        "description": "gt from last tab cycles to first",
        "keys": ":tabnew\rgt",
        "initial": FIVE,
    },
    "tabnext_explicit": {
        "description": ":tabn explicit",
        "keys": ":tabnew\r:tabn\r",
        "initial": FIVE,
    },
    "tabprev_explicit": {
        "description": ":tabp explicit",
        "keys": ":tabnew\r:tabp\r",
        "initial": FIVE,
    },
    "tabclose_returns_to_one": {
        "description": ":tabc closes current tab",
        "keys": ":tabnew\r:tabc\r",
        "initial": FIVE,
    },
    "tabonly_closes_others": {
        "description": ":tabo closes other tabs",
        "keys": ":tabnew\r:tabnew\r:tabo\r",
        "initial": FIVE,
    },

    # ── Ctrl-W T — move window to new tab (0880l) ────────────────
    "ctrl_w_T_window_to_tab": {
        "description": ":sp then Ctrl-W T moves split into its own tab",
        "keys": ":sp\r\x17T",
        "initial": FIVE,
    },

    # ── :new — new empty window (0880o) ──────────────────────────
    "new_window_basic": {
        "description": ":new creates a new horizontal split with empty buffer",
        "keys": ":new\r",
        "initial": FIVE,
    },

    # ── :wa / :xa / :qa (0880q-s) ────────────────────────────────
    # NOTE: :qa would exit nvim — keep test single :wa
    "wa_unmodified": {
        "description": ":wa with nothing modified is a no-op",
        "keys": ":wa\r",
        "initial": FIVE,
    },

    # ── :sort (0880-series uses too) ─────────────────────────────
    # Already covered by other suites, but let's add a basic case
    "sort_basic": {
        "description": ":sort sorts all lines alphabetically",
        "keys": ":sort\r",
        "initial": "delta\nbeta\nalpha\ngamma",
    },
    "sort_reverse": {
        "description": ":sort! sorts descending",
        "keys": ":sort!\r",
        "initial": "alpha\nbeta\ngamma\ndelta",
    },
    "sort_unique": {
        "description": ":sort u removes duplicates",
        "keys": ":sort u\r",
        "initial": "alpha\nbeta\nalpha\ngamma\nbeta",
    },
    "sort_numeric": {
        "description": ":sort n sorts numerically",
        "keys": ":sort n\r",
        "initial": "10\n2\n1\n20",
    },
}
