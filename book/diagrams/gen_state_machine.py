"""Generate book/diagrams/state-machine.svg.

Hub-and-spoke diagram of Vim's seven modes. Keys render as small
rounded-rect pills (matching the book's {key:..} style); typed
commands like ``:term`` stay monospace; prose words like ``motion``
are serif italic. Diagonal arrows are drawn as parallel offset pairs
so they never cross, and their labels rotate to follow the line.
"""

from __future__ import annotations

import math
from pathlib import Path


# ----------------------------- pills + text ----------------------------- #

PILL_H = 22
PILL_PAD = 10
PILL_FONT = 13
CHAR_W = 7.6


def pill_width(text: str) -> float:
    return max(20.0, len(text) * CHAR_W + PILL_PAD)


def xml_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
    )


def pill(cx: float, cy: float, text: str) -> str:
    w = pill_width(text)
    x = cx - w / 2
    y = cy - PILL_H / 2
    return (
        f'<g class="kpill">'
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{PILL_H}" rx="5" ry="5"/>'
        f'<text x="{cx:.1f}" y="{cy + 4.5:.1f}">{xml_escape(text)}</text>'
        f'</g>'
    )


def serif_span(cx: float, cy: float, text: str, *,
               italic: bool = True, size: int = 14,
               anchor: str = "middle", fill: str = "#333") -> str:
    style = "italic" if italic else "normal"
    return (
        f'<text x="{cx:.1f}" y="{cy:.1f}" font-family="serif" '
        f'font-style="{style}" font-size="{size}" '
        f'text-anchor="{anchor}" fill="{fill}">{xml_escape(text)}</text>'
    )


def mono_span(cx: float, cy: float, text: str, *, size: int = 13,
              anchor: str = "middle", fill: str = "#000") -> str:
    return (
        f'<text x="{cx:.1f}" y="{cy:.1f}" font-family="monospace" '
        f'font-size="{size}" text-anchor="{anchor}" fill="{fill}">{xml_escape(text)}</text>'
    )


# A "token" is one of: ("pill", "i"), ("serif", "motion"), ("mono", ":term")
def render_tokens(cx: float, cy: float, tokens: list[tuple[str, str]],
                  *, gap: float = 4.0) -> str:
    """Lay out a row of tokens centred on (cx, cy)."""
    widths: list[float] = []
    for kind, txt in tokens:
        if kind == "pill":
            widths.append(pill_width(txt))
        elif kind == "serif":
            widths.append(len(txt) * 7.0)
        elif kind == "mono":
            widths.append(len(txt) * 7.6 + 4)
        else:
            widths.append(20.0)
    total = sum(widths) + gap * (len(tokens) - 1)
    out: list[str] = []
    x = cx - total / 2
    for (kind, txt), w in zip(tokens, widths):
        tcx = x + w / 2
        if kind == "pill":
            out.append(pill(tcx, cy, txt))
        elif kind == "serif":
            out.append(serif_span(tcx, cy + 4, txt, italic=True))
        elif kind == "mono":
            out.append(mono_span(tcx, cy + 4, txt))
        x += w + gap
    return "".join(out)


def rotated_tokens(cx: float, cy: float, angle_deg: float,
                   tokens: list[tuple[str, str]]) -> str:
    """Render tokens as a horizontal row, then rotate the whole group
    by ``angle_deg`` around (cx, cy)."""
    inner = render_tokens(cx, cy, tokens)
    return (
        f'<g transform="rotate({angle_deg:.2f}, {cx:.1f}, {cy:.1f})">'
        f'{inner}</g>'
    )


# ----------------------------- node boxes ----------------------------- #

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


# ----------------------------- arrows ----------------------------- #

def arrow(x1: float, y1: float, x2: float, y2: float, *,
          shorten: float = 0.0, dashed: bool = False) -> str:
    if shorten:
        dx, dy = x2 - x1, y2 - y1
        ln = math.hypot(dx, dy) or 1
        ux, uy = dx / ln, dy / ln
        x1 += ux * shorten
        y1 += uy * shorten
        x2 -= ux * shorten
        y2 -= uy * shorten
    cls = "edgeDash" if dashed else "edge"
    marker = "url(#arrDash)" if dashed else "url(#arr)"
    return (
        f'<line class="{cls}" x1="{x1:.1f}" y1="{y1:.1f}" '
        f'x2="{x2:.1f}" y2="{y2:.1f}" marker-end="{marker}"/>'
    )


def diagonal_pair(n_attach: tuple[float, float],
                  s_attach: tuple[float, float],
                  *,
                  entry_tokens: list[tuple[str, str]],
                  exit_tokens: list[tuple[str, str]],
                  line_offset: float = 9,
                  label_offset: float = 34) -> list[str]:
    """Two parallel offset arrows between a node and its satellite, plus
    two labels rotated to follow the line direction.

    ``entry_tokens`` (N→satellite) is rendered on the visually-upper side
    of the line. ``exit_tokens`` (satellite→N) is rendered on the lower
    side. This matches the horizontal pairs: leave on top, return on
    bottom.
    """
    nx, ny = n_attach
    sx, sy = s_attach

    # Normalize the "rightward" reading direction of the line so text
    # never ends up upside down.
    if nx <= sx:
        lx, ly, rx_, ry = nx, ny, sx, sy
    else:
        lx, ly, rx_, ry = sx, sy, nx, ny
    dx, dy = rx_ - lx, ry - ly
    L = math.hypot(dx, dy) or 1
    ux, uy = dx / L, dy / L      # along the line, L -> R
    # Perpendicular pointing visually "up" on screen (negative-y side).
    # Rotating 90° CW from (ux, uy) gives (uy, -ux); that vector has
    # py = -ux which is negative whenever ux > 0, i.e. always points up.
    px, py = uy, -ux

    angle_deg = math.degrees(math.atan2(dy, dx))

    def shift(p, d):
        x, y = p
        return (x + px * d, y + py * d)

    # Entry arrow on the UPPER side (+offset along upward-pointing px,py)
    n1 = shift(n_attach, +line_offset)
    s1 = shift(s_attach, +line_offset)
    # Exit arrow on the LOWER side
    s2 = shift(s_attach, -line_offset)
    n2 = shift(n_attach, -line_offset)

    out: list[str] = []
    out.append(arrow(*n1, *s1, shorten=14))
    out.append(arrow(*s2, *n2, shorten=14))

    mx, my = (nx + sx) / 2, (ny + sy) / 2

    ex, ey = mx + px * label_offset, my + py * label_offset   # upper
    xx, xy = mx - px * label_offset, my - py * label_offset   # lower

    out.append(rotated_tokens(ex, ey, angle_deg, entry_tokens))
    out.append(rotated_tokens(xx, xy, angle_deg, exit_tokens))
    return out


def horizontal_pair(n_attach: tuple[float, float],
                    s_attach: tuple[float, float],
                    *,
                    entry_tokens: list[tuple[str, str]],
                    exit_tokens: list[tuple[str, str]],
                    line_offset: float = 12,
                    label_offset: float = 22) -> list[str]:
    """Horizontal version of diagonal_pair (same idea, angle = 0)."""
    nx, ny = n_attach
    sx, sy = s_attach
    out: list[str] = []
    # parallel offsets (vertical, since lines are horizontal)
    out.append(arrow(nx, ny - line_offset, sx, sy - line_offset, shorten=6))
    out.append(arrow(sx, sy + line_offset, nx, ny + line_offset, shorten=6))
    mx = (nx + sx) / 2
    out.append(render_tokens(mx, ny - line_offset - label_offset, entry_tokens))
    out.append(render_tokens(mx, ny + line_offset + label_offset, exit_tokens))
    return out


# ----------------------------- layout ----------------------------- #

W, H = 1100, 760

# Node rectangles  (x, y, w, h, name, sub)
NORMAL = (430, 340, 240, 90, "normal",            "resting state")
INSERT = (890, 350, 180, 60, "insert",            "typing text")
VISUAL = (30,  350, 180, 60, "visual",            "char / line / block")
OPPEND = (60,  90,  280, 60, "operator-pending",  "awaiting a motion")
CMDLIN = (760, 90,  280, 60, "command-line",      ": / ? line")
REPLAC = (90,  610, 220, 60, "replace",           "overtype")
TERMIN = (790, 610, 220, 60, "terminal",          "shell inside vim")


def attach(box_def, side, frac=0.5):
    x, y, w, h = box_def[0], box_def[1], box_def[2], box_def[3]
    if side == "right":  return (x + w, y + h * frac)
    if side == "left":   return (x,     y + h * frac)
    if side == "top":    return (x + w * frac, y)
    if side == "bottom": return (x + w * frac, y + h)
    raise ValueError(side)


# ----------------------------- emit ----------------------------- #

def build() -> str:
    parts: list[str] = [
        f'<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {W} {H}" font-family="serif">',
        '''
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
          d="M 670 440 C 740 490, 860 490, 920 435"/>
    <path id="ctrlOLabelPath"
          d="M 670 425 C 740 475, 860 475, 920 420"/>
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
''',
    ]

    # nodes
    for b, big in [(NORMAL, True), (INSERT, False), (VISUAL, False),
                   (OPPEND, False), (CMDLIN, False), (REPLAC, False),
                   (TERMIN, False)]:
        parts.append("  " + box(*b, big=big))

    # ---- horizontal pairs ----

    parts += horizontal_pair(
        attach(NORMAL, "right"), attach(INSERT, "left"),
        entry_tokens=[("pill", k) for k in ["i", "a", "o", "I", "A", "O", "c"]],
        exit_tokens=[("pill", "Esc")],
    )
    parts += horizontal_pair(
        attach(NORMAL, "left"), attach(VISUAL, "right"),
        entry_tokens=[("pill", k) for k in ["v", "V", "Ctrl-V"]],
        exit_tokens=[("pill", "Esc")],
    )

    # ---- diagonal pairs ----

    # Normal <-> Operator-pending (upper-left)
    parts += diagonal_pair(
        attach(NORMAL, "top", frac=0.20),
        attach(OPPEND, "bottom", frac=0.80),
        entry_tokens=[("pill", k) for k in ["d", "c", "y", ">", "<", "="]],
        exit_tokens=[("serif", "motion"), ("serif", "/"), ("pill", "Esc")],
    )

    # Normal <-> Command-line (upper-right)
    parts += diagonal_pair(
        attach(NORMAL, "top", frac=0.80),
        attach(CMDLIN, "bottom", frac=0.20),
        entry_tokens=[("pill", k) for k in [":", "/", "?"]],
        exit_tokens=[("pill", "Enter"), ("serif", "/"), ("pill", "Esc")],
    )

    # Normal <-> Replace (lower-left)
    parts += diagonal_pair(
        attach(NORMAL, "bottom", frac=0.20),
        attach(REPLAC, "top", frac=0.80),
        entry_tokens=[("pill", "R")],
        exit_tokens=[("pill", "Esc")],
    )

    # Normal <-> Terminal (lower-right)
    parts += diagonal_pair(
        attach(NORMAL, "bottom", frac=0.80),
        attach(TERMIN, "top", frac=0.20),
        entry_tokens=[("mono", ":term")],
        exit_tokens=[("pill", "Ctrl-\\"), ("pill", "Ctrl-N")],
    )

    # ---- Ctrl-O dashed curve ----
    parts.append(
        '<use href="#ctrlOPath" class="edgeDash" marker-end="url(#arrDash)"/>'
    )
    # Label following an offset path lifted above the visible curve.
    parts.append(
        '<text font-size="12" fill="#555">'
        '<textPath href="#ctrlOLabelPath" startOffset="50%" text-anchor="middle">'
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
