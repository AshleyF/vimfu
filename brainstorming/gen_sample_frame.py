"""
Generate a sample Frame JSON from a hardcoded terminal state.

This simulates what we'd capture from a pyte buffer during a VimFu lesson.
It produces sample_frame.json which the renderers can consume.
"""

import json
from pathlib import Path

# Simulate the screen state from lesson 71 after "dd" deletes "power 5"
# 40 cols × 20 rows, cursor at (0,0)
COLS = 40
ROWS = 20
DEFAULT_FG = "d4d4d4"  # light gray
DEFAULT_BG = "000000"  # black

STATUS_FG = "000000"   # black text
STATUS_BG = "d4d4d4"   # gray bar

TILDE_FG = "5c5cff"    # blue tildes

lines_text = [
    "speed 5",
    "range 5",
    "armor 5",
    "",
    "def cast(name):",
    '    print(f"casting {name}")',
    '    print(f"it hits!")',
    '    print(f"nice one")',
]
# Pad to 20 rows (rows 8-17 are ~ lines, 18 is status, 19 empty)
status_line = "spells.py [+]         1,1            All"

def normal_run(n):
    """Default fg on default bg."""
    return {"n": n, "fg": DEFAULT_FG, "bg": DEFAULT_BG}

def status_run(n):
    """Status bar style (inverted)."""
    return {"n": n, "fg": STATUS_FG, "bg": STATUS_BG}

def tilde_run(n):
    """Blue tilde."""
    return {"n": n, "fg": TILDE_FG, "bg": DEFAULT_BG}

def keyword_run(n):
    """Python keyword color."""
    return {"n": n, "fg": "c586c0", "bg": DEFAULT_BG}

def func_run(n):
    """Function name color."""
    return {"n": n, "fg": "dcdcaa", "bg": DEFAULT_BG}

def string_run(n):
    """String literal color."""
    return {"n": n, "fg": "ce9178", "bg": DEFAULT_BG}

def paren_run(n):
    """Parenthesis/bracket color."""
    return {"n": n, "fg": "ffd700", "bg": DEFAULT_BG}

def param_run(n):
    """Parameter color."""
    return {"n": n, "fg": "9cdcfe", "bg": DEFAULT_BG}

frame_lines = []

# Row 0: "speed 5" (cursor here)
text = "speed 5".ljust(COLS)
frame_lines.append({"text": text, "runs": [normal_run(COLS)]})

# Row 1: "range 5"
text = "range 5".ljust(COLS)
frame_lines.append({"text": text, "runs": [normal_run(COLS)]})

# Row 2: "armor 5"
text = "armor 5".ljust(COLS)
frame_lines.append({"text": text, "runs": [normal_run(COLS)]})

# Row 3: blank
frame_lines.append({"text": " " * COLS, "runs": [normal_run(COLS)]})

# Row 4: "def cast(name):"
text = "def cast(name):".ljust(COLS)
frame_lines.append({"text": text, "runs": [
    keyword_run(3),  # "def"
    normal_run(1),   # " "
    func_run(4),     # "cast"
    paren_run(1),    # "("
    param_run(4),    # "name"
    paren_run(1),    # ")"
    normal_run(1),   # ":"
    normal_run(COLS - 15),  # padding
]})

# Row 5: '    print(f"casting {name}")'
text = '    print(f"casting {name}")'.ljust(COLS)
frame_lines.append({"text": text, "runs": [
    normal_run(4),   # indent
    func_run(5),     # "print"
    paren_run(1),    # "("
    normal_run(1),   # "f"
    string_run(17),  # '"casting {name}"'
    paren_run(1),    # ")"
    normal_run(COLS - 29),  # padding
]})

# Row 6: '    print(f"it hits!")'
text = '    print(f"it hits!")'.ljust(COLS)
frame_lines.append({"text": text, "runs": [
    normal_run(4),   # indent
    func_run(5),     # "print"
    paren_run(1),    # "("
    normal_run(1),   # "f"
    string_run(11),  # '"it hits!"'
    paren_run(1),    # ")"
    normal_run(COLS - 23),  # padding
]})

# Row 7: '    print(f"nice one")'
text = '    print(f"nice one")'.ljust(COLS)
frame_lines.append({"text": text, "runs": [
    normal_run(4),   # indent
    func_run(5),     # "print"
    paren_run(1),    # "("
    normal_run(1),   # "f"
    string_run(11),  # '"nice one"'
    paren_run(1),    # ")"
    normal_run(COLS - 23),  # padding
]})

# Rows 8-17: "~" lines
for _ in range(10):
    text = "~".ljust(COLS)
    frame_lines.append({"text": text, "runs": [
        tilde_run(1),
        normal_run(COLS - 1),
    ]})

# Row 18: status line
text = status_line.ljust(COLS)
frame_lines.append({"text": text, "runs": [status_run(COLS)]})

# Row 19: empty (command line)
frame_lines.append({"text": " " * COLS, "runs": [normal_run(COLS)]})

frame = {
    "rows": ROWS,
    "cols": COLS,
    "cursor": {"row": 0, "col": 0, "visible": True},
    "defaultFg": DEFAULT_FG,
    "defaultBg": DEFAULT_BG,
    "lines": frame_lines,
}

out = Path(__file__).parent / "sample_frame.json"
out.write_text(json.dumps(frame, indent=2), encoding="utf-8")
print(f"Wrote {out} ({out.stat().st_size:,} bytes)")

# Also create a second frame with visual selection for testing highlights
frame2_lines = list(frame_lines)  # shallow copy is fine, we replace entries

# Simulate visual selection on rows 1-2 ("range 5" and "armor 5")
for sel_row in [1, 2]:
    orig = frame_lines[sel_row]
    text = orig["text"]
    # Visual line selection: entire row is highlighted (inverted)
    frame2_lines[sel_row] = {
        "text": text,
        "runs": [{"n": COLS, "fg": DEFAULT_BG, "bg": DEFAULT_FG}]  # inverted
    }

frame2 = {
    "rows": ROWS,
    "cols": COLS,
    "cursor": {"row": 2, "col": 0, "visible": True},
    "defaultFg": DEFAULT_FG,
    "defaultBg": DEFAULT_BG,
    "lines": frame2_lines,
}

out2 = Path(__file__).parent / "sample_frame_selection.json"
out2.write_text(json.dumps(frame2, indent=2), encoding="utf-8")
print(f"Wrote {out2} ({out2.stat().st_size:,} bytes)")
