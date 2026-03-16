"""Tests for z-scroll variants: z. z+ z- z^."""

CASES = {
    # ── z. — center cursor line, cursor to first non-blank ──
    "z_dot_center": {
        "keys": "10jz.",
        "initial": "line0\nline1\nline2\nline3\nline4\nline5\nline6\nline7\nline8\nline9\nline10\nline11\nline12\nline13\nline14\nline15\nline16\nline17\nline18\nline19\n",
    },

    # ── z<CR> — cursor line to top, cursor to first non-blank ──
    "z_enter_top": {
        "keys": "10jz\r",
        "initial": "line0\nline1\nline2\nline3\nline4\nline5\nline6\nline7\nline8\nline9\nline10\nline11\nline12\nline13\nline14\nline15\nline16\nline17\nline18\nline19\n",
    },

    # ── z- — cursor line to bottom, cursor to first non-blank ──
    "z_minus_bottom": {
        "keys": "10jz-",
        "initial": "line0\nline1\nline2\nline3\nline4\nline5\nline6\nline7\nline8\nline9\nline10\nline11\nline12\nline13\nline14\nline15\nline16\nline17\nline18\nline19\n",
    },
}
