"""Compact "text-mode" frame -> Frame JSON expander.

Hand-authoring full Frame JSON (with per-run color arrays) is brutal.
This module accepts a much simpler shape and expands it into the
canonical Frame format that frame_to_svg consumes.

Compact frame:
{
  "rows": 12,
  "cols": 40,
  "lines": [
    "speed 5",
    "range 5",
    "armor 5",
    "",
    "def cast(name):",
    "    print(\"casting\")",
    "~",
    "~",
    "spells.py [+]         1,1            All",
    ""
  ],
  "cursor": [0, 0],
  "highlights": [
    {"row": 0, "col": 6, "len": 1, "fg": "ff8700", "b": true}
  ],
  "statusRow": 8
}

- Missing rows are padded with blanks.
- Lines shorter than `cols` are space-padded.
- `~` lines (Vim's empty-buffer marker) auto-colorize with default fg.
- `statusRow` (optional) gets reverse video — black on light gray.
- `highlights` apply small color/bold overrides on top.

Outputs a Frame dict ready for frame_to_svg().
"""

from __future__ import annotations

DEFAULT_FG = "d4d4d4"
DEFAULT_BG = "000000"
TILDE_FG = "5c5cff"


def expand(compact: dict) -> dict:
    rows = compact.get("rows", 20)
    cols = compact.get("cols", 60)
    src_lines = compact.get("lines", [])
    cursor = compact.get("cursor")
    highlights = compact.get("highlights", [])
    status_row = compact.get("statusRow")
    default_fg = compact.get("defaultFg", DEFAULT_FG)
    default_bg = compact.get("defaultBg", DEFAULT_BG)

    # Pad lines to `rows`
    src_lines = list(src_lines) + [""] * max(0, rows - len(src_lines))
    src_lines = src_lines[:rows]

    # Build per-cell attributes table: cell[row][col] = (fg, bg, flags)
    cells = [
        [(default_fg, default_bg, "") for _ in range(cols)]
        for _ in range(rows)
    ]

    text_rows = []
    for r, line in enumerate(src_lines):
        # Pad / truncate to cols
        padded = (line[:cols]).ljust(cols, " ")
        text_rows.append(padded)

        # Tilde rows: classic Vim blue ~
        if padded.startswith("~") and padded[1:].strip() == "":
            cells[r][0] = (TILDE_FG, default_bg, "")

        # Status row: reverse-video
        if status_row is not None and r == status_row:
            for c in range(cols):
                cells[r][c] = (default_bg, default_fg, "")

    # Apply highlights
    for h in highlights:
        r = h["row"]
        c0 = h["col"]
        n = h.get("len", 1)
        fg = h.get("fg")
        bg = h.get("bg")
        flags = ""
        if h.get("b"): flags += "b"
        if h.get("i"): flags += "i"
        if h.get("u"): flags += "u"
        if h.get("s"): flags += "s"
        for c in range(c0, min(c0 + n, cols)):
            old_fg, old_bg, old_flags = cells[r][c]
            new_fg = fg if fg else old_fg
            new_bg = bg if bg else old_bg
            new_flags = flags if flags else old_flags
            cells[r][c] = (new_fg, new_bg, new_flags)

    # Run-length encode each row
    out_lines = []
    for r in range(rows):
        runs = []
        run_n = 0
        prev = None
        for c in range(cols):
            cur = cells[r][c]
            if cur == prev:
                run_n += 1
            else:
                if prev is not None:
                    runs.append(_make_run(run_n, *prev))
                prev = cur
                run_n = 1
        if prev is not None:
            runs.append(_make_run(run_n, *prev))
        out_lines.append({"text": text_rows[r], "runs": runs})

    cur_obj = {"row": -1, "col": -1, "visible": False}
    if cursor is not None:
        if isinstance(cursor, list):
            cur_obj = {"row": cursor[0], "col": cursor[1], "visible": True}
        else:
            cur_obj = {
                "row": cursor.get("row", 0),
                "col": cursor.get("col", 0),
                "visible": cursor.get("visible", True),
            }

    return {
        "rows": rows,
        "cols": cols,
        "cursor": cur_obj,
        "defaultFg": default_fg,
        "defaultBg": default_bg,
        "lines": out_lines,
    }


def _make_run(n, fg, bg, flags):
    run = {"n": n, "fg": fg, "bg": bg}
    if "b" in flags: run["b"] = True
    if "i" in flags: run["i"] = True
    if "u" in flags: run["u"] = True
    if "s" in flags: run["s"] = True
    return run
