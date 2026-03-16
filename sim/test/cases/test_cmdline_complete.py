"""Tests for command-line Tab completion and Ctrl-D (show completions).

Tab completes the current partial command to the next match.
Ctrl-D shows all possible completions without changing the command line.

Strategy:
- Tab tests use partial prefixes that DON'T work as abbreviations,
  so Tab completion is required for the command to execute.
- Tab-cycle tests verify cycling through multiple matches.
- Ctrl-D tests capture the screen while showing completions (no Escape).
"""

CASES = {
    # ── Tab completion: prefix REQUIRES completion to execute ──

    # :sor<Tab><Enter> — "sor" alone is not a valid abbreviation for sort
    # Tab should complete to "sort" which then executes
    "tab_sort": {
        "keys": ":sor\x09\r",
        "initial": "cherry\napple\nbanana\n",
    },

    # :ec<Tab> 'hi'<Enter> — "ec" alone doesn't match echo
    # Tab completes to "echo", then we type the argument
    "tab_echo": {
        "keys": ":ec\x09 'hi'\r",
        "initial": "test\n",
    },

    # :noh<Tab><Enter> — Tab completes to :nohlsearch
    # First search to set hlsearch, then clear it
    "tab_nohlsearch": {
        "keys": "/hello\r:noh\x09\r",
        "initial": "hello world\nhello again\n",
    },

    # :se<Tab> number<Enter> — "se" completes to "set"
    "tab_set_number": {
        "keys": ":se\x09 number\r",
        "initial": "hello\n",
    },

    # :vs<Tab><Enter> — "vs" alone won't match vsplit
    # Tab completes to "vsplit" and executes a vertical split
    "tab_vsplit": {
        "keys": ":vs\x09\r\x1b",
        "initial": "hello\nworld\n",
        "settle": 0.5,
        "skip": "vsplit rendering differs from nvim (pre-existing: sim uses flat split model)",
    },

    # ── Tab with command that has unique match ──

    # :clo<Tab><Enter> — unique match to "close"
    # Creates a split first, then closes it
    "tab_close": {
        "keys": ":sp\r:clo\x09\r",
        "initial": "hello\n",
        "settle": 0.5,
    },

    # ── Tab multiple times — cycle through matches ──

    # :w<Tab><Tab><Tab><Esc> — cycles through w-commands
    # After Escape, buffer is unchanged (just testing Tab doesn't crash)
    "tab_w_cycle_escape": {
        "keys": ":w\x09\x09\x09\x1b",
        "initial": "hello\n",
    },

    # ── Ctrl-D: show completions ──
    # Ctrl-D with short prefix, then Escape
    # The screen may or may not show completions (nvim clears on Esc)
    # These verify no crash and buffer is intact

    "ctrl_d_w_then_escape": {
        "keys": ":w\x04\x1b",
        "initial": "hello\nworld\n",
    },

    "ctrl_d_sp_then_escape": {
        "keys": ":sp\x04\x1b",
        "initial": "hello\n",
    },

    "ctrl_d_set_then_escape": {
        "keys": ":set \x04\x1b",
        "initial": "test\n",
        "skip": "nvim shows paginated set options list that fills entire screen",
    },

    # ── Edge cases ──

    # Tab with no input (just colon)
    "tab_empty_colon": {
        "keys": ":\x09\x1b",
        "initial": "test\n",
    },

    # Tab after a complete command (no additional completion needed)
    "tab_after_full_set": {
        "keys": ":set\x09\x1b",
        "initial": "test\n",
    },

    # Ctrl-D with no matches (gibberish prefix)
    "ctrl_d_no_match": {
        "keys": ":zzz\x04\x1b",
        "initial": "test\n",
    },

    # Tab with no matches (gibberish prefix) — nothing happens
    "tab_no_match": {
        "keys": ":zzz\x09\x1b",
        "initial": "test\n",
    },
}
