"""Tests for video range 0448-0488: cmdline editing and special registers."""

LINES = "alpha beta gamma\ndelta epsilon zeta\nfoo bar baz\nfoo bar baz qux\n"
DOC = "hello world\nthe quick fox\nlazy dog runs\n"

CASES = {
    # ── 0450 Ctrl-R " (insert unnamed register into cmdline) ────
    "cmdline_ctrl_r_unnamed": {
        "description": "yank a word, then :echo \"<text>\" via Ctrl-R \" in cmdline",
        "keys": "yiw:s/alpha/\x12\"/\r",
        "initial": LINES,
    },
    "cmdline_ctrl_r_register_a": {
        "description": "yank to register a, then insert via Ctrl-R a in cmdline",
        "keys": "\"ayiw:s/alpha/\x12a/\r",
        "initial": LINES,
    },

    # ── 0451 Ctrl-R Ctrl-W (insert <cword> into cmdline) ────────
    "cmdline_ctrl_r_ctrl_w": {
        "description": "Ctrl-R Ctrl-W inserts the word under cursor into cmdline",
        "keys": ":s/\x12\x17/REPL/\r",
        "initial": "hello world\n",
    },

    # ── 0455 Up arrow history ───────────────────────────────────
    "cmdline_history_up_arrow": {
        "description": ":1 then : Up brings back :1",
        "keys": ":3\r:1\r:\x1b[A\r",
        "initial": "line one\nline two\nline three\n",
    },

    # ── 0484 \":  — last ex command in : register ───────────────
    "register_colon_last_command": {
        "description": "after :set number, \":p inserts ':set number' into buffer",
        "keys": ":set number\rgg\":p",
        "initial": "first line\n",
    },

    # ── 0485 \"/ — last search register ─────────────────────────
    "register_slash_last_search": {
        "description": "/foo then \"/p inserts 'foo' as the last search pattern",
        "keys": "/foo\rgg\"/p",
        "initial": "foo bar\nbaz\n",
    },

    # ── 0486 \"% — current filename register ────────────────────
    # (skipped — sim's filename handling differs from nvim's)

    # ── 0483 \". — last inserted text register ──────────────────
    "register_dot_last_inserted": {
        "description": "insert 'xyz', escape, \".p inserts the last inserted text",
        "keys": "ixyz\x1b\".p",
        "initial": "abc\n",
    },

    # ── Cmdline Ctrl-W: delete previous word ────────────────────
    "cmdline_ctrl_w_delete_word": {
        "description": "type then Ctrl-W deletes the last word in cmdline",
        "keys": ":s/foo/bar\x17baz/\r",
        "initial": "foo line\n",
    },
}
