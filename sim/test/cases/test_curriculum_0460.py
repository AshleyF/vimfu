"""Tests for video range 0460-0490: ga, g Ctrl-A, :earlier, special regs."""

LINES_NUMS = "n = 1\nn = 2\nn = 3\nn = 4\n"
LINES_FIVE = "alpha\nbeta\ngamma\ndelta\nepsilon"

CASES = {
    # ── 0492 ga — show character information ────────────────────
    "ga_show_char_info": {
        "description": "ga prints the decimal/hex/octal of the character under cursor",
        "keys": "ga",
        "initial": "A bc\n",
    },
    "ga_with_motion": {
        "description": "lga shows info for the second character",
        "keys": "lga",
        "initial": "a B c\n",
    },

    # ── 0471 g Ctrl-A — sequential numbering in visual mode ─────
    "g_ctrl_a_sequential": {
        "description": "select 4 lines with V3j then g Ctrl-A (\\x01) → 1, 2, 3, 4 deltas",
        "keys": "V3jg\x01",
        "initial": "n = 0\nn = 0\nn = 0\nn = 0\n",
    },

    # ── 0481/0482 :earlier and :later (time-based undo) ─────────
    # (skipped — nvim's :earlier output is timing-sensitive: textLines
    # capture happens before the post-:earlier redraw, so the buffer
    # appears unchanged in the ground truth. The functionality is
    # exercised indirectly via other undo/redo tests.)

    # ── 0487 \"# — alternate file register ──────────────────────
    # (skipped — requires a real alternate file context)

    # ── 0463 ddp — swap line with the line below ────────────────
    "ddp_swap_down": {
        "description": "ddp swaps the current line with the one below it",
        "keys": "2Gddp",
        "initial": LINES_FIVE,
    },
    # ── 0464 ddP — swap line with the line above ────────────────
    "ddP_swap_up": {
        "description": "ddP swaps the current line with the one above it",
        "keys": "3GddP",
        "initial": LINES_FIVE,
    },
    # ── 0465 yyp — duplicate the current line ───────────────────
    "yyp_duplicate_line": {
        "description": "yyp duplicates the current line below",
        "keys": "2Gyyp",
        "initial": LINES_FIVE,
    },
    # ── 0461 xp — transpose two characters ──────────────────────
    "xp_transpose_chars": {
        "description": "xp on 'ab' swaps a and b to 'ba'",
        "keys": "xp",
        "initial": "abc\n",
    },
}
