"""Frame JSON -> standalone SVG (color or B&W).

Adapted from brainstorming/render_svg.py. Each call returns a fully
self-contained SVG string with embedded <style> — no external CSS needed.

Public API:
    frame_to_svg(frame, theme="color") -> str
    discover_palette(frame) -> (fg_list, bg_list)
"""

from __future__ import annotations

from xml.sax.saxutils import escape as xml_escape

# Cell geometry (px, viewBox coordinates)
CW = 10   # cell width
CH = 20   # cell height
FS = 16   # font-size
BL = 15   # baseline offset

NBSP = "\u00a0"


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


def _tspan(cls, col, text, extra=""):
    n = len(text)
    if n == 0:
        return None
    xs = " ".join(str((col + i) * CW) for i in range(n))
    # Each character carries its own absolute x via the xs list, so we don't
    # need NBSP padding for SVG layout. Using regular spaces keeps the PDF's
    # extracted text stream clean of U+00A0 — KDP's pre-print validation
    # flags those as non-printable characters.
    safe = xml_escape(text)
    return f'<tspan class="{cls}" x="{xs}" xml:space="preserve"{extra}>{safe}</tspan>'


def _build_elements(frame, fg_cls, bg_cls):
    rows, cols = frame["rows"], frame["cols"]
    cursor = frame.get("cursor", {})
    default_bg = frame["defaultBg"]
    W = cols * CW

    cr = cursor.get("row", -1)
    cc = cursor.get("col", -1)
    cv = cursor.get("visible", True)

    bg_rects = []
    fg_texts = []
    cur_elems = []

    bg_rects.append(
        f'<rect class="{bg_cls[default_bg]}" width="{W}" height="{rows * CH}"/>'
    )

    for r, line in enumerate(frame["lines"]):
        raw = line["text"]
        y = r * CH
        total = sum(run["n"] for run in line["runs"])
        keep = len(raw[:total].rstrip(" "))
        if keep:
            col = 0
            tspans = []
            for run in line["runs"]:
                n = run["n"]
                fg = run["fg"]
                bg = run["bg"]
                if col >= keep:
                    break
                end = min(col + n, keep)
                chunk = raw[col:end]
                if bg != default_bg:
                    bg_rects.append(
                        f'<rect class="{bg_cls[bg]}" x="{col * CW}" y="{y}"'
                        f' width="{n * CW}" height="{CH}"/>'
                    )
                extra = ""
                if run.get("b"): extra += ' font-weight="bold"'
                if run.get("i"): extra += ' font-style="italic"'
                ts = _tspan(fg_cls[fg], col, chunk, extra)
                if ts:
                    tspans.append(ts)
                col += n
            if tspans:
                fg_texts.append(f'<text y="{y + BL}">{"".join(tspans)}</text>')

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
                    if run.get("b"): cur_extra += ' font-weight="bold"'
                    if run.get("i"): cur_extra += ' font-style="italic"'
                    break
                cx += run["n"]
            cur_elems.append(
                f'<text class="cursor-text" x="{cc * CW}" y="{y + BL}"'
                f'{cur_extra}>{xml_escape(cur_c)}</text>'
            )

    return bg_rects, fg_texts, cur_elems


def _color_css(fg_map, bg_map):
    lines = []
    for cls, hx in bg_map.items():
        lines.append(f".{cls} {{ fill: #{hx}; }}")
    for cls, hx in fg_map.items():
        lines.append(f".{cls} {{ fill: #{hx}; }}")
    lines.append(".cursor { fill: #ff8700; opacity: 0.55; }")
    lines.append(".cursor-text { fill: #000; font-weight: bold; }")
    return "\n      ".join(lines)


def _bw_css(fg_map, bg_map, default_bg):
    default_bg_cls = next(c for c, h in bg_map.items() if h == default_bg)
    lines = []
    for cls in bg_map:
        if cls == default_bg_cls:
            lines.append(f".{cls} {{ fill: #ffffff; }}")
        else:
            lines.append(f".{cls} {{ fill: #cccccc; }}")
    for cls in fg_map:
        lines.append(f".{cls} {{ fill: #000000; }}")
    lines.append(".cursor { fill: #000000; opacity: 0.85; }")
    lines.append(".cursor-text { fill: #ffffff; font-weight: bold; }")
    return "\n      ".join(lines)


def frame_to_svg(frame, theme: str = "color") -> str:
    """Render a frame as a standalone SVG string with embedded styles.

    theme: "color" (full terminal palette) or "bw" (book-friendly grayscale).
    """
    rows, cols = frame["rows"], frame["cols"]
    W, H = cols * CW, rows * CH

    fg_list, bg_list = discover_palette(frame)
    fg_cls = {c: f"fg{i}" for i, c in enumerate(fg_list)}
    bg_cls = {c: f"bg{i}" for i, c in enumerate(bg_list)}
    fg_map = {f"fg{i}": c for i, c in enumerate(fg_list)}
    bg_map = {f"bg{i}": c for i, c in enumerate(bg_list)}

    bg_rects, fg_texts, cur_elems = _build_elements(frame, fg_cls, bg_cls)

    if theme == "bw":
        css = _bw_css(fg_map, bg_map, frame["defaultBg"])
    else:
        css = _color_css(fg_map, bg_map)

    NL = "\n    "
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg"',
        f'     viewBox="0 0 {W} {H}"',
        f'     font-family="\'Cascadia Code\',\'Consolas\',\'Courier New\',monospace"',
        f'     font-size="{FS}" xml:space="preserve"',
        f'     data-vimfu-theme="{theme}">',
        f'  <defs><style>',
        f'      {css}',
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
