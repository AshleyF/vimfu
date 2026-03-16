"""Display-line motions: gj, gk, g0, g$, g^, gm, gM"""

CASES = {
    # ── gj — move down one display line ──────────────────────────
    "gj_on_wrapped_line": {
        # 70-char line wraps at col 40; gj should move to col 40 (start of 2nd display line)
        "keys": "gj",
        "initial": "The quick brown fox jumps over the lazy dog and then runs away quickly\n",
    },
    "gj_short_line": {
        # Line doesn't wrap, so gj just moves to the next buffer line
        "keys": "gj",
        "initial": "short\nanother\n",
    },
    "gj_count": {
        # 2gj moves down two display lines (to col ~80 on a long wrapped line)
        "keys": "2gj",
        "initial": "The quick brown fox jumps over the lazy dog and then runs away fast across the big meadow before finally stopping to rest by the old oak tree\n",
    },

    # ── gk — move up one display line ────────────────────────────
    "gk_on_wrapped_line": {
        # gj then gk should return to the first display line
        "keys": "gjgk",
        "initial": "The quick brown fox jumps over the lazy dog and then runs away quickly\n",
    },
    "gk_count": {
        # 3gj moves to 4th display line, then 2gk moves back to 2nd display line
        "keys": "3gj2gk",
        "initial": "The quick brown fox jumps over the lazy dog and then runs away fast across the big meadow before finally stopping to rest by the old oak tree near the river bank\n",
    },

    # ── g0 — start of current display line ───────────────────────
    "g0_on_second_display_line": {
        # Navigate to 2nd display line, move right 10 chars, then g0 back to start of that display line
        "keys": "gj10lg0",
        "initial": "The quick brown fox jumps over the lazy dog and then runs away quickly\n",
    },

    # ── g$ — end of current display line ─────────────────────────
    "g_dollar_on_first_display_line": {
        # g$ on a wrapped line goes to last char of first display line (col 39)
        "keys": "g$",
        "initial": "The quick brown fox jumps over the lazy dog and then runs away quickly\n",
    },

    # ── g^ — first non-blank of current display line ────────────
    "g_caret_on_display_line": {
        # First 40 chars fill display line 1; 2nd display line starts with spaces
        # gj moves to 2nd display line, g^ skips leading spaces
        "keys": "gjg^",
        "initial": "abcdefghijklmnopqrstuvwxyz0123456789ABCD   indented part here\n",
    },

    # ── gm — middle of screen width ─────────────────────────────
    "gm_middle_of_screen": {
        # gm goes to column 20 (middle of 40-col screen)
        "keys": "gm",
        "initial": "The quick brown fox jumps over the lazy dog\n",
    },

    # ── gM — middle of text on current line ──────────────────────
    "gM_middle_of_text": {
        # gM goes to the middle character of the current buffer line
        "keys": "gM",
        "initial": "The quick brown fox jumps over the lazy dog\n",
    },
    "gM_short_line": {
        # gM on a 5-char line goes to the middle character (col 2)
        "keys": "gM",
        "initial": "hello\n",
    },

    # ── operator + display motion ────────────────────────────────
    "dgj_operator": {
        # d combined with gj deletes from cursor through next display line
        "keys": "dgj",
        "initial": "The quick brown fox jumps over the lazy dog and then runs away quickly\nsecond line\n",
    },
}
