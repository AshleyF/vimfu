"""
Render a Frame JSON as a PostScript file.

Usage: python render_ps.py sample_frame.json [output.ps]

Produces a crisp black-and-white rendering suitable for print.
"""

import json
import sys
from pathlib import Path


def hex_to_rgb(h: str):
    """Convert "rrggbb" to (r, g, b) floats 0–1."""
    return int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255


def luminance(h: str) -> float:
    """Perceived luminance of a hex color (0=black, 1=white)."""
    r, g, b = hex_to_rgb(h)
    return 0.299 * r + 0.587 * g + 0.114 * b


def is_dark(h: str) -> bool:
    return luminance(h) < 0.5


def render_frame_ps(frame: dict, *, bw: bool = True) -> str:
    """Render a single frame as a PostScript program.

    If bw=True:  pure black & white (suitable for print)
    If bw=False: full color (suitable for color PDF/screen)
    """
    rows = frame["rows"]
    cols = frame["cols"]
    cursor = frame["cursor"]
    default_fg = frame["defaultFg"]
    default_bg = frame["defaultBg"]

    # Font metrics (points)
    font_size = 11
    char_w = font_size * 0.6   # Courier at 11pt is ~6.6pt wide
    char_h = font_size * 1.25  # line height

    # Page setup
    margin_x = 72   # 1 inch
    margin_y = 72
    grid_w = cols * char_w
    grid_h = rows * char_h

    page_w = grid_w + margin_x * 2
    page_h = grid_h + margin_y * 2

    ps = []
    ps.append(f"%!PS-Adobe-3.0 EPSF-3.0")
    ps.append(f"%%BoundingBox: 0 0 {int(page_w)} {int(page_h)}")
    ps.append(f"%%Pages: 1")
    ps.append(f"%%EndComments")
    ps.append(f"")
    ps.append(f"/Courier findfont {font_size} scalefont setfont")
    ps.append(f"")

    # Helper: position of cell (col, row) in page coords
    # PostScript origin is bottom-left; row 0 is at the top
    def cell_x(c):
        return margin_x + c * char_w

    def cell_y(r):
        return page_h - margin_y - (r + 1) * char_h

    def text_y(r):
        """Baseline Y for text in row r."""
        return cell_y(r) + font_size * 0.25  # lift baseline slightly

    # --- Background pass ---
    for r, line in enumerate(frame["lines"]):
        col_offset = 0
        for run in line["runs"]:
            n = run["n"]
            bg = run["bg"]

            if bw:
                # In B&W mode: dark bg → fill black (this is "highlighted" or status bar)
                # Light bg → leave white (paper)
                if is_dark(bg) and bg != default_bg:
                    # Non-default dark bg = highlighted region
                    x = cell_x(col_offset)
                    y = cell_y(r)
                    w = n * char_w
                    ps.append(f"0 setgray")
                    ps.append(f"{x:.1f} {y:.1f} {w:.1f} {char_h:.1f} rectfill")
                elif not is_dark(bg):
                    # Light bg on normally-dark terminal = inverted (status bar etc.)
                    x = cell_x(col_offset)
                    y = cell_y(r)
                    w = n * char_w
                    ps.append(f"0 setgray")
                    ps.append(f"{x:.1f} {y:.1f} {w:.1f} {char_h:.1f} rectfill")
            else:
                # Color mode: draw actual bg color
                cr, cg, cb = hex_to_rgb(bg)
                x = cell_x(col_offset)
                y = cell_y(r)
                w = n * char_w
                ps.append(f"{cr:.3f} {cg:.3f} {cb:.3f} setrgbcolor")
                ps.append(f"{x:.1f} {y:.1f} {w:.1f} {char_h:.1f} rectfill")

            col_offset += n

    # --- Text pass ---
    for r, line in enumerate(frame["lines"]):
        text = line["text"]
        col_offset = 0
        for run in line["runs"]:
            n = run["n"]
            fg = run["fg"]
            bg = run["bg"]
            chunk = text[col_offset:col_offset + n].rstrip()

            if chunk:
                if bw:
                    # Text on highlighted/inverted bg → white text
                    if (is_dark(bg) and bg != default_bg) or (not is_dark(bg)):
                        ps.append(f"1 setgray")  # white
                    else:
                        ps.append(f"0 setgray")  # black
                else:
                    cr, cg, cb = hex_to_rgb(fg)
                    ps.append(f"{cr:.3f} {cg:.3f} {cb:.3f} setrgbcolor")

                # Escape PostScript special chars
                safe = chunk.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
                x = cell_x(col_offset)
                y = text_y(r)
                ps.append(f"{x:.1f} {y:.1f} moveto ({safe}) show")

            col_offset += n

    # --- Cursor ---
    if cursor.get("visible", True):
        cr, cc = cursor["row"], cursor["col"]
        x = cell_x(cc)
        y = cell_y(cr)

        if bw:
            # Draw cursor as a thick black rectangle outline
            ps.append(f"0 setgray")
            ps.append(f"1.5 setlinewidth")
            ps.append(f"{x:.1f} {y:.1f} {char_w:.1f} {char_h:.1f} rectstroke")
        else:
            # Draw cursor as white outline
            ps.append(f"1 1 1 setrgbcolor")
            ps.append(f"1.5 setlinewidth")
            ps.append(f"{x:.1f} {y:.1f} {char_w:.1f} {char_h:.1f} rectstroke")

    # --- Border around the whole terminal ---
    ps.append(f"0.7 setgray")
    ps.append(f"0.5 setlinewidth")
    bx = margin_x - 2
    by = cell_y(rows - 1) - 2
    bw_rect = grid_w + 4
    bh_rect = rows * char_h + 4
    ps.append(f"{bx:.1f} {by:.1f} {bw_rect:.1f} {bh_rect:.1f} rectstroke")

    ps.append(f"")
    ps.append(f"showpage")
    return "\n".join(ps)


def main():
    if len(sys.argv) < 2:
        print("Usage: python render_ps.py sample_frame.json [output.ps]")
        sys.exit(1)

    frame_path = Path(sys.argv[1])
    frame = json.loads(frame_path.read_text("utf-8"))

    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else frame_path.with_suffix(".ps")

    ps = render_frame_ps(frame, bw=True)
    out_path.write_text(ps, encoding="utf-8")
    print(f"Wrote {out_path} ({out_path.stat().st_size:,} bytes)")

    # Also generate color version
    color_path = out_path.with_stem(out_path.stem + "_color")
    ps_color = render_frame_ps(frame, bw=False)
    color_path.write_text(ps_color, encoding="utf-8")
    print(f"Wrote {color_path} ({color_path.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
