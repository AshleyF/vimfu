"""
Render a Frame JSON as SVG with semantic CSS classes.

Scans all runs to discover unique foreground/background colors,
assigns numbered class names (bg0, bg1, …, fg0, fg1, …), and
emits SVG with those classes — zero inline colors.

Outputs:
  {stem}.svg               bare SVG with embedded fallback style
  {stem}_svg_color.html    HTML with original terminal colors
  {stem}_svg_bw.html       HTML with stark B&W theme

Usage:
  python render_svg.py sample_frame.json
  python render_svg.py sample_frame_selection.json
"""

import json
import sys
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

# ── Cell geometry (px in viewBox coordinates) ────────────────────
CW = 10   # cell width
CH = 20   # cell height
FS = 16   # font-size
BL = 15   # baseline offset from cell top  (y + BL)


# ── Palette discovery ────────────────────────────────────────────

def discover_palette(frame):
    """Return (fg_list, bg_list) — unique hex colors, default first."""
    fgs, bgs = set(), set()
    for line in frame["lines"]:
        for run in line["runs"]:
            fgs.add(run["fg"])
            bgs.add(run["bg"])
    dfg, dbg = frame["defaultFg"], frame["defaultBg"]
    return (
        sorted(fgs, key=lambda c: (c != dfg, c)),
        sorted(bgs, key=lambda c: (c != dbg, c)),
    )


# ── SVG construction ─────────────────────────────────────────────

NBSP = "\u00a0"          # non-breaking space — never collapsed by HTML5


def _tspan(cls, col, text, extra=""):
    """Build a <tspan> with per-glyph ``x`` positions.

    Regular spaces are replaced with U+00A0 (non-breaking space) so
    that HTML5's inline-SVG whitespace normalisation cannot collapse
    them and desynchronise the glyph ↔ x-value mapping.
    """
    n = len(text)
    if n == 0:
        return None
    xs = " ".join(str((col + i) * CW) for i in range(n))
    safe = xml_escape(text.replace(" ", NBSP))
    return f'<tspan class="{cls}" x="{xs}"{extra}>{safe}</tspan>'


def build_svg_elements(frame, fg_cls, bg_cls):
    """Return (bg_rects, fg_texts, cur_elems) lists of SVG markup.

    Each screen row becomes ONE <text> element.  Each colour run is a
    child <tspan> that carries its own per-glyph ``x`` position list.
    Spaces inside tspan text are emitted as U+00A0 so the HTML parser
    cannot collapse them.

    The cursor is a pure overlay (rect + text) painted last.
    """
    rows, cols = frame["rows"], frame["cols"]
    cursor = frame.get("cursor", {})
    default_bg = frame["defaultBg"]
    W = cols * CW

    cr = cursor.get("row", -1)
    cc = cursor.get("col", -1)
    cv = cursor.get("visible", True)

    bg_rects = []
    fg_texts = []   # one <text> string per non-empty row
    cur_elems = []

    # Full-screen default background
    bg_rects.append(
        f'<rect class="{bg_cls[default_bg]}" width="{W}" height="{rows * CH}"/>'
    )

    for r, line in enumerate(frame["lines"]):
        raw = line["text"]
        y = r * CH

        # Determine rightmost non-space column (line-level trim)
        total = sum(run["n"] for run in line["runs"])
        keep = len(raw[:total].rstrip(" "))
        if keep == 0:
            # Entirely blank row — emit nothing for foreground, but
            # still check for cursor below.
            pass
        else:
            col = 0
            tspans = []
            for run in line["runs"]:
                n  = run["n"]
                fg = run["fg"]
                bg = run["bg"]

                if col >= keep:
                    break
                end = min(col + n, keep)
                chunk = raw[col:end]

                # Non-default bg rect (full run width, not trimmed)
                if bg != default_bg:
                    bg_rects.append(
                        f'<rect class="{bg_cls[bg]}" x="{col * CW}" y="{y}"'
                        f' width="{n * CW}" height="{CH}"/>'
                    )

                extra = ""
                if run.get("b", False):
                    extra += ' font-weight="bold"'
                if run.get("i", False):
                    extra += ' font-style="italic"'

                ts = _tspan(fg_cls[fg], col, chunk, extra)
                if ts:
                    tspans.append(ts)
                col += n

            if tspans:
                fg_texts.append(
                    f'<text y="{y + BL}">{"".join(tspans)}</text>'
                )

        # Cursor overlay (rect + text, painted on top of everything)
        if cv and r == cr and 0 <= cc < len(raw):
            cur_elems.append(
                f'<rect class="cursor" x="{cc * CW}" y="{y}"'
                f' width="{CW}" height="{CH}"/>'
            )
            cur_c = raw[cc]
            cur_extra = ""
            cx = 0
            for run in line["runs"]:
                if cx <= cc < cx + run["n"]:
                    if run.get("b"):
                        cur_extra += ' font-weight="bold"'
                    if run.get("i"):
                        cur_extra += ' font-style="italic"'
                    break
                cx += run["n"]
            cur_elems.append(
                f'<text class="cursor-text" x="{cc * CW}" y="{y + BL}"'
                f'{cur_extra}>{xml_escape(cur_c)}</text>'
            )

    return bg_rects, fg_texts, cur_elems


def fallback_css(fg_map, bg_map, default_bg_cls):
    """Minimal embedded CSS so the bare .svg is viewable standalone."""
    lines = []
    for cls in bg_map:
        fill = "#111" if cls == default_bg_cls else "#555"
        lines.append(f".{cls} {{ fill: {fill}; }}")
    for cls in fg_map:
        lines.append(f".{cls} {{ fill: #ccc; }}")
    lines.append(".cursor { fill: #800000; }")
    lines.append(".cursor-text { fill: #fff; }")
    return "\n      ".join(lines)


def assemble_svg(frame, fg_cls, bg_cls, fg_map, bg_map):
    """Return complete SVG string."""
    rows, cols = frame["rows"], frame["cols"]
    W, H = cols * CW, rows * CH
    bg_rects, fg_texts, cur_elems = build_svg_elements(frame, fg_cls, bg_cls)

    default_bg_cls = bg_cls[frame["defaultBg"]]
    fb = fallback_css(fg_map, bg_map, default_bg_cls)

    NL = "\n    "  # indent helper

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg"',
        f'     viewBox="0 0 {W} {H}"',
        f'     font-family="\'Cascadia Code\',\'Consolas\',\'Courier New\',monospace"',
        f'     font-size="{FS}" xml:space="preserve">',
        f'  <defs><style>',
        f'      /* Fallback for standalone .svg viewing */',
        f'      {fb}',
        f'  </style></defs>',
        f'  <g class="backgrounds">',
        f'    {NL.join(bg_rects)}',
        f'  </g>',
        f'  <g class="foreground">',
        f'    {NL.join(fg_texts)}',
        f'  </g>',
    ]

    if cur_elems:
        parts += [
            f'  <g class="cursors">',
            f'    {NL.join(cur_elems)}',
            f'  </g>',
        ]

    parts.append('</svg>')
    return "\n".join(parts)


# ── CSS generators ────────────────────────────────────────────────

def color_css(fg_map, bg_map):
    """CSS mapping classes → original terminal hex colors."""
    lines = ["/* Color theme — original terminal colors */"]
    for cls, hx in bg_map.items():
        lines.append(f"svg .{cls} {{ fill: #{hx}; }}")
    for cls, hx in fg_map.items():
        lines.append(f"svg .{cls} {{ fill: #{hx}; }}")
    lines.append("svg .cursor { fill: #800000; }")
    lines.append("svg .cursor-text { fill: #fff; }")
    return "\n".join(lines)


def bw_css(fg_map, bg_map, default_bg):
    """Stark B&W: white text on black, one gray for highlights, another for cursor."""
    default_bg_cls = next(c for c, h in bg_map.items() if h == default_bg)
    lines = ["/* Stark B&W theme */"]
    for cls, hx in bg_map.items():
        if cls == default_bg_cls:
            lines.append(f"svg .{cls} {{ fill: #000; }}  /* default bg */")
        else:
            lines.append(f"svg .{cls} {{ fill: #444; }}  /* was #{hx} → highlight / statusbar */")
    for cls, hx in fg_map.items():
        lines.append(f"svg .{cls} {{ fill: #fff; }}  /* was #{hx} */")
    lines.append("svg .cursor { fill: #800000; }")
    lines.append("svg .cursor-text { fill: #fff; }")
    return "\n".join(lines)


# ── HTML wrapper ──────────────────────────────────────────────────

def palette_note(fg_map, bg_map):
    """Human-readable color map for HTML comments."""
    parts = ["Background classes:"]
    for c, h in bg_map.items():
        parts.append(f"  .{c} = #{h}")
    parts.append("Foreground classes:")
    for c, h in fg_map.items():
        parts.append(f"  .{c} = #{h}")
    return "\n".join(parts)


def wrap_html(title, svg, css, note, page_bg, frame_border, heading_color):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
body {{
  margin: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: {page_bg};
  font-family: system-ui, sans-serif;
}}
h1 {{
  font-size: 14px;
  font-weight: 400;
  color: {heading_color};
  letter-spacing: 0.05em;
  text-transform: uppercase;
}}
.frame {{
  border: 2px solid {frame_border};
  border-radius: 6px;
  overflow: hidden;
  line-height: 0;
}}
svg {{ display: block; width: 640px; }}
/* ── Theme ──────────────────────────────────────────── */
{css}
</style>
</head>
<body>
<h1>{title}</h1>
<!--
{note}
-->
<div class="frame">
{svg}
</div>
</body>
</html>"""


# ── Main ──────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python render_svg.py <frame.json>")
        sys.exit(1)

    src = Path(sys.argv[1])
    frame = json.loads(src.read_text("utf-8"))
    stem = src.stem

    # Discover palette
    fg_list, bg_list = discover_palette(frame)
    fg_cls = {c: f"fg{i}" for i, c in enumerate(fg_list)}
    bg_cls = {c: f"bg{i}" for i, c in enumerate(bg_list)}
    fg_map = {f"fg{i}": c for i, c in enumerate(fg_list)}
    bg_map = {f"bg{i}": c for i, c in enumerate(bg_list)}

    n_total = len(bg_list) + len(fg_list)
    print(f"Palette: {len(bg_list)} bg + {len(fg_list)} fg = {n_total} unique colors")
    for cls, hx in bg_map.items():
        tag = " (default)" if hx == frame["defaultBg"] else ""
        print(f"  .{cls} = #{hx}{tag}")
    for cls, hx in fg_map.items():
        tag = " (default)" if hx == frame["defaultFg"] else ""
        print(f"  .{cls} = #{hx}{tag}")

    # Build SVG
    svg = assemble_svg(frame, fg_cls, bg_cls, fg_map, bg_map)

    # ── Write bare SVG ───────────────────────────────────────
    svg_path = src.with_suffix(".svg")
    svg_path.write_text(svg, encoding="utf-8")
    print(f"\nWrote {svg_path} ({svg_path.stat().st_size:,} bytes)")

    # ── Write color HTML ─────────────────────────────────────
    note = palette_note(fg_map, bg_map)
    cc = color_css(fg_map, bg_map)
    color_html = wrap_html(
        "VimFu Frame — Color", svg, cc, note,
        page_bg="#1e1e1e", frame_border="#555", heading_color="#888",
    )
    cp = src.parent / f"{stem}_svg_color.html"
    cp.write_text(color_html, encoding="utf-8")
    print(f"Wrote {cp} ({cp.stat().st_size:,} bytes)")

    # ── Write B&W HTML ───────────────────────────────────────
    bc = bw_css(fg_map, bg_map, frame["defaultBg"])
    bw_html = wrap_html(
        "VimFu Frame — Stark B&W", svg, bc, note,
        page_bg="#fff", frame_border="#000", heading_color="#666",
    )
    bp = src.parent / f"{stem}_svg_bw.html"
    bp.write_text(bw_html, encoding="utf-8")
    print(f"Wrote {bp} ({bp.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
