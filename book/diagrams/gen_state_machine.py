"""Generate book/diagrams/state-machine.svg.

Hub-and-spoke diagram of Vim's seven modes. Keys are rendered as small
pill-rounded rectangles (matching the {key:..} style in the book), typed
commands like ``:term`` stay in monospace, and prose words like
``motion`` and ``one command, then back to insert`` are in serif italic.
"""

from __future__ import annotations

import math
from pathlib import Path


# ---------- low-level emitters ---------- #

PILL_H = 22
PILL_PAD = 8
PILL_FONT = 13          # px
CHAR_W = 7.5            # approx monospace char width at PILL_FONT


def pill_width(text: str) -> float:
    return max(20.0, len(text) * CHAR_W + PILL_PAD)


def pill(cx: float, cy: float, text: str) -> str:
    """Return SVG for a single key-pill centred at (cx, cy)."""
    w = pill_width(text)
    x = cx - w / 2
    y = cy - PILL_H / 2
    display = (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
    )
    return (
        f'<g class="kpill">'
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{PILL_H}" rx="5" ry="5"/>'
        f'<text x="{cx:.1f}" y="{cy + 4.5:.1f}">{display}</text>'
        f'</g>'
    )


def pill_row(cx: float, cy: float, texts: list[str], gap: float = 4.0) -> str:
    """Return SVG for a horizontal run of pills, centred at (cx, cy)."""
    widths = [pill_width(t) for t in texts]
    total = sum(widths) + gap * (len(texts) - 1)
    out: list[str] = []
    x = cx - total / 2
    for t, w in zip(texts, widths):
        out.append(pill(x + w / 2, cy, t))
        x += w + gap
    return "".join(out)


def serif(cx: float, cy: float, text: str, *, italic: bool = True,
          size: int = 13, anchor: str = "middle", fill: str = "#333") -> str:
    style = "italic" if italic else "normal"
    return (
        f'<text x="{cx:.1f}" y="{cy:.1f}" font-family="serif" '
        f'font-style="{style}" font-size="{size}" '
        f'text-anchor="{anchor}" fill="{fill}">{text}</text>'
    )


def mono(cx: float, cy: float, text: str, *, size: int = 13,
         anchor: str = "middle", fill: str = "#000") -> str:
    return (
        f'<text x="{cx:.1f}" y="{cy:.1f}" font-family="monospace" '
        f'font-size="{size}" text-anchor="{anchor}" fill="{fill}">{text}</text>'
    )


def box(x: float, y: float, w: float, h: float, name: str, sub: str,
        *, big: bool = False) -> str:
    rx = 14
    cls = "normal" if big else "node"
    name_size = 28 if big else 22
    cy_name = y + h / 2 - (4 if sub else -4)
    cy_sub = y + h / 2 + 18
    parts = [
        f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" '
        f'rx="{rx}" ry="{rx}"/>',
        f'<text x="{x + w / 2:.1f}" y="{cy_name:.1f}" class="mode" '
        f'font-size="{name_size}">{name}</text>',
    ]
    if sub:
        parts.append(
            f'<text x="{x + w / 2:.1f}" y="{cy_sub:.1f}" class="sub">{sub}</text>'
        )
    return "\n  ".join(parts)


def arrow(x1: float, y1: float, x2: float, y2: float, *,
          shorten: float = 0.0, dashed: bool = False,
          curve: tuple[float, float] | None = None) -> str:
    """Return SVG for an arrow from (x1, y1) to (x2, y2).

    shorten: pull both endpoints inward by this many pixels along the line
    so the arrowhead doesn't touch the node border.
    """
    if shorten:
        dx, dy = x2 - x1, y2 - y1
        ln = math.hypot(dx, dy)
        ux, uy = dx / ln, dy / ln
        x1 += ux * shorten
        y1 += uy * shorten
        x2 -= ux * shorten
        y2 -= uy * shorten
    cls = "edgeDash" if dashed else "edge"
    marker = "url(#arrDash)" if dashed else "url(#arr)"
    if curve is not None:
        cx, cy = curve
        d = f"M {x1:.1f},{y1:.1f} Q {cx:.1f},{cy:.1f} {x2:.1f},{y2:.1f}"
        return (
            f'<path class="{cls}" d="{d}" marker-end="{marker}"/>'
        )
    return (
        f'<line class="{cls}" x1="{x1:.1f}" y1="{y1:.1f}" '
        f'x2="{x2:.1f}" y2="{y2:.1f}" marker-end="{marker}"/>'
    )


# ---------- layout ---------- #

W, H = 1100, 760

# Node rectangles  (x, y, w, h, name, sub)
NORMAL = (430, 340, 240, 90, "normal",         "resting state")
INSERT = (890, 350, 180, 60, "insert",         "typing text")
VISUAL = (30,  350, 180, 60, "visual",         "char / line / block")
OPPEND = (60,  90,  280, 60, "operator-pending","awaiting a motion")
CMDLIN = (760, 90,  280, 60, "command-line",   ": / ? line")
REPLAC = (90,  610, 220, 60, "replace",        "overtype")
TERMIN = (790, 610, 220, 60, "terminal",       "shell inside vim")


def cx(b): return b[0] + b[2] / 2
def cy(b): return b[1] + b[3] / 2
def right(b): return (b[0] + b[2], cy(b))
def left(b):  return (b[0], cy(b))
def top(b):   return (cx(b), b[1])
def bot(b):   return (cx(b), b[1] + b[3])


# ---------- emit ---------- #

def build() -> str:
    parts: list[str] = []
    parts.append(
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {W} {H}" font-family="serif">'
    )
    parts.append('''
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="8" markerHeight="8" orient="auto">
      <path d="M0,0 L10,5 L0,10 z" fill="#222"/>
    </marker>
    <marker id="arrDash" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="8" markerHeight="8" orient="auto">
      <path d="M0,0 L10,5 L0,10 z" fill="#666"/>
    </marker>
    <path id="ctrlOPath"
          d="M 670 445 C 740 530, 850 530, 915 415"/>
  </defs>

  <style>
    .node    { fill: #fff; stroke: #222; stroke-width: 2; }
    .normal  { fill: #f3f3f3; stroke: #000; stroke-width: 3; }
    .mode    { font-style: italic; fill: #000; text-anchor: middle; }
    .sub     { font-size: 12px; fill: #555; text-anchor: middle; font-style: italic; }
    .edge    { fill: none; stroke: #222; stroke-width: 1.5; }
    .edgeDash{ fill: none; stroke: #666; stroke-width: 1.2; stroke-dasharray: 5 4; }
    .kpill rect { fill: #fafafa; stroke: #444; stroke-width: 1; }
    .kpill text { font-family: monospace; font-size: 13px; fill: #000; text-anchor: middle; }
  </style>
''')

    # nodes
    for b, big in [(NORMAL, True), (INSERT, False), (VISUAL, False),
                   (OPPEND, False), (CMDLIN, False), (REPLAC, False),
                   (TERMIN, False)]:
        parts.append("  " + box(*b, big=big))

    # ---- horizontal edges (Normal <-> Insert, Normal <-> Visual) ----

    # Normal -> Insert (upper of pair)
    nx, _ = right(NORMAL)
    ix, _ = left(INSERT)
    parts.append(arrow(nx, cy(NORMAL) - 12, ix, cy(INSERT) - 12, shorten=4))
    # entry keys above
    parts.append(pill_row((nx + ix) / 2, cy(NORMAL) - 32,
                          ["i", "a", "o", "I", "A", "O", "c"]))

    # Insert -> Normal (lower of pair)
    parts.append(arrow(ix, cy(INSERT) + 12, nx, cy(NORMAL) + 12, shorten=4))
    parts.append(pill((nx + ix) / 2, cy(NORMAL) + 32, "Esc"))

    # Normal -> Visual (upper of pair)
    nl, _ = left(NORMAL)
    vr, _ = right(VISUAL)
    parts.append(arrow(nl, cy(NORMAL) - 12, vr, cy(VISUAL) - 12, shorten=4))
    parts.append(pill_row((nl + vr) / 2, cy(NORMAL) - 32,
                          ["v", "V", "Ctrl-V"]))

    # Visual -> Normal
    parts.append(arrow(vr, cy(VISUAL) + 12, nl, cy(NORMAL) + 12, shorten=4))
    parts.append(pill((nl + vr) / 2, cy(NORMAL) + 32, "Esc"))

    # ---- diagonal edges, with HORIZONTAL labels off to the side ----

    # Normal <-> Operator-pending (upper-left)
    nx1, ny1 = NORMAL[0] + 30, NORMAL[1]                   # top-left-ish of Normal
    ox1, oy1 = OPPEND[0] + OPPEND[2] - 40, OPPEND[1] + OPPEND[3]  # bot-right of Op-pending
    parts.append(arrow(nx1 - 5, ny1, ox1 + 5, oy1, shorten=6))   # N -> OP
    parts.append(arrow(ox1 - 5, oy1, nx1 + 5, ny1, shorten=6))   # OP -> N
    # entry pills - placed in the upper portion of the gap
    parts.append(pill_row(165, 200,
                          ["d", "c", "y", ">", "<", "="]))
    # exit label: motion (serif italic) / Esc pill
    parts.append(serif(150, 268, "motion", italic=True, size=14, anchor="end"))
    parts.append(serif(157, 268, "/", italic=False, size=14, anchor="middle"))
    parts.append(pill(190, 263, "Esc"))

    # Normal <-> Command-line (upper-right)
    nx2, ny2 = NORMAL[0] + NORMAL[2] - 30, NORMAL[1]
    cx1, cy1 = CMDLIN[0] + 40, CMDLIN[1] + CMDLIN[3]
    parts.append(arrow(nx2 + 5, ny2, cx1 - 5, cy1, shorten=6))   # N -> Cmd
    parts.append(arrow(cx1 + 5, cy1, nx2 - 5, ny2, shorten=6))   # Cmd -> N
    parts.append(pill_row(935, 200, [":", "/", "?"]))
    parts.append(pill(917, 263, "Enter"))
    parts.append(serif(950, 268, "/", italic=False, size=14, anchor="middle"))
    parts.append(pill(975, 263, "Esc"))

    # Normal <-> Replace (lower-left)
    nx3, ny3 = NORMAL[0] + 30, NORMAL[1] + NORMAL[3]
    rx1, ry1 = REPLAC[0] + REPLAC[2] - 40, REPLAC[1]
    parts.append(arrow(nx3 - 5, ny3, rx1 + 5, ry1, shorten=6))   # N -> R
    parts.append(arrow(rx1 - 5, ry1, nx3 + 5, ny3, shorten=6))   # R -> N
    parts.append(pill(180, 500, "R"))
    parts.append(pill(225, 560, "Esc"))

    # Normal <-> Terminal (lower-right)
    nx4, ny4 = NORMAL[0] + NORMAL[2] - 30, NORMAL[1] + NORMAL[3]
    tx1, ty1 = TERMIN[0] + 40, TERMIN[1]
    parts.append(arrow(nx4 + 5, ny4, tx1 - 5, ty1, shorten=6))   # N -> T
    parts.append(arrow(tx1 + 5, ty1, nx4 - 5, ny4, shorten=6))   # T -> N
    parts.append(mono(925, 505, ":term"))                        # typed command
    parts.append(pill(885, 560, "Ctrl-\\"))
    parts.append(pill(945, 560, "Ctrl-N"))

    # ---- Ctrl-O dashed curve (insert -> normal -> back to insert) ----
    parts.append('<use href="#ctrlOPath" class="edgeDash" marker-end="url(#arrDash)"/>')

    # Label following the curve (left-to-right so it reads correctly).
    parts.append(
        '<text font-size="12" fill="#555">'
        '<textPath href="#ctrlOPath" startOffset="50%" text-anchor="middle">'
        '<tspan font-family="monospace" fill="#000">Ctrl-O</tspan>'
        '<tspan font-family="serif" font-style="italic">'
        '  — one command, then back'
        '</tspan>'
        '</textPath>'
        '</text>'
    )

    parts.append('</svg>\n')
    return "\n".join(parts)


def main() -> None:
    out = Path(__file__).resolve().parent / "state-machine.svg"
    out.write_text(build(), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
