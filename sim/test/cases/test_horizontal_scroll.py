"""Tests for horizontal scroll (nowrap mode).

When :set nowrap is active, long lines are NOT wrapped. Instead,
the viewport has a horizontal scroll offset (scrollLeft).

z-commands:
  zs — scroll so cursor column is at left of screen
  ze — scroll so cursor column is at right of screen
  zh — scroll N columns right (text moves left)
  zl — scroll N columns left (text moves right)
  zH — scroll half-screen width right
  zL — scroll half-screen width left

The screen is 40 columns wide. Lines longer than 40 chars get truncated
at the right edge (no wrapping).
"""

# A long line for testing (60+ chars)
LONG_LINE = "abcdefghij" * 7  # 70 chars: abcdefghij repeated 7 times
LONG_INITIAL = LONG_LINE + "\nshort\n"

# Multi-line with varying lengths
MULTI_LONG = (
    "The quick brown fox jumps over the lazy dog and keeps running far away\n"
    "short\n"
    "Another very long line that definitely exceeds forty columns by a lot!\n"
)

CASES = {
    # ── Basic nowrap rendering ──

    # With nowrap, long line should be truncated at 40 cols (not wrapped)
    "nowrap_truncates_long_line": {
        "keys": ":set nowrap\r",
        "initial": LONG_INITIAL,
    },

    # With wrap (default), long line should wrap to multiple screen rows
    "wrap_wraps_long_line": {
        "keys": "",
        "initial": LONG_INITIAL,
    },

    # ── Cursor at end of long line in nowrap ──

    # Move to end of long line — screen should scroll right
    "nowrap_cursor_at_end": {
        "keys": ":set nowrap\r$",
        "initial": LONG_INITIAL,
    },

    # ── zl — scroll left (text shifts left, revealing right side) ──

    "zl_scroll_left": {
        "keys": ":set nowrap\r10zl",
        "initial": LONG_INITIAL,
    },

    "zl_scroll_left_20": {
        "keys": ":set nowrap\r20zl",
        "initial": LONG_INITIAL,
    },

    # ── zh — scroll right (text shifts right, revealing left side) ──

    "zh_scroll_right_after_zl": {
        "keys": ":set nowrap\r20zl5zh",
        "initial": LONG_INITIAL,
    },

    "zh_at_zero_noop": {
        "keys": ":set nowrap\r5zh",
        "initial": LONG_INITIAL,
    },

    # ── zL — scroll half-screen left ──

    "zL_half_screen": {
        "keys": ":set nowrap\rzL",
        "initial": LONG_INITIAL,
    },

    # ── zH — scroll half-screen right ──

    "zH_after_zL": {
        "keys": ":set nowrap\rzLzH",
        "initial": LONG_INITIAL,
    },

    # ── zs — cursor column at left edge of screen ──

    "zs_cursor_at_col_20": {
        "keys": ":set nowrap\r20lzs",
        "initial": LONG_INITIAL,
    },

    # ── ze — cursor column at right edge of screen ──

    "ze_cursor_at_col_20": {
        "keys": ":set nowrap\r20lze",
        "initial": LONG_INITIAL,
    },

    # ── $ then zs in nowrap ──

    "zs_at_end_of_line": {
        "keys": ":set nowrap\r$zs",
        "initial": LONG_INITIAL,
    },

    # ── Cursor movement auto-scrolls ──

    # Move right past the screen edge — should auto-scroll
    "auto_scroll_right": {
        "keys": ":set nowrap\r45l",
        "initial": LONG_INITIAL,
    },

    # Move cursor left with h — should auto-scroll back
    "auto_scroll_left": {
        "keys": ":set nowrap\r45l40h",
        "initial": LONG_INITIAL,
    },

    # ── Short lines with horizontal scroll ──

    # Short line with scroll offset — should show empty past end
    "short_line_with_scroll": {
        "keys": ":set nowrap\r20zl",
        "initial": "short\nhi\n",
    },

    # ── Multi-line nowrap ──

    "multi_line_nowrap": {
        "keys": ":set nowrap\r",
        "initial": MULTI_LONG,
    },

    # ── Number gutter with nowrap ──

    "nowrap_with_number": {
        "keys": ":set nowrap\r:set number\r$",
        "initial": LONG_INITIAL,
    },
}
