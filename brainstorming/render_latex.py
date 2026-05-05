"""
Render a Frame JSON as a LaTeX/TikZ document.

Usage: python render_latex.py sample_frame.json [output.tex]

Produces a LaTeX file with a TikZ picture for each frame.
Compile with: pdflatex output.tex
"""

import json
import sys
from pathlib import Path


def hex_to_rgb(h: str):
    return int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255


def luminance(h: str) -> float:
    r, g, b = hex_to_rgb(h)
    return 0.299 * r + 0.587 * g + 0.114 * b


def is_dark(h: str) -> bool:
    return luminance(h) < 0.5


def latex_escape(s: str) -> str:
    """Escape special LaTeX characters."""
    replacements = {
        '\\': r'\textbackslash{}',
        '{': r'\{',
        '}': r'\}',
        '#': r'\#',
        '$': r'\$',
        '%': r'\%',
        '&': r'\&',
        '_': r'\_',
        '^': r'\^{}',
        '~': r'\~{}',
        '"': r"''",
    }
    result = []
    for ch in s:
        result.append(replacements.get(ch, ch))
    return "".join(result)


def render_frame_latex(frame: dict, *, bw: bool = True) -> str:
    rows = frame["rows"]
    cols = frame["cols"]
    cursor = frame["cursor"]
    default_bg = frame["defaultBg"]

    # TikZ coordinates: (col, -row) so row 0 is at top
    char_w = 0.22  # cm per character
    char_h = 0.36  # cm per line

    lines = []
    lines.append(r"\documentclass[border=5mm]{standalone}")
    lines.append(r"\usepackage[utf8]{inputenc}")
    lines.append(r"\usepackage[T1]{fontenc}")
    lines.append(r"\usepackage{tikz}")
    lines.append(r"\usepackage{inconsolata}")  # monospace font
    lines.append(r"\usetikzlibrary{calc}")
    lines.append(r"")
    lines.append(r"\begin{document}")
    lines.append(r"\begin{tikzpicture}[x=\dimexpr " + f"{char_w}" + r"cm, y=\dimexpr " + f"{char_h}" + r"cm]")
    lines.append(r"")

    # Border
    lines.append(f"  \\draw[gray, thin] (-0.1, 0.3) rectangle ({cols * char_w / char_w + 0.1}, {-(rows - 1) * char_h / char_h - 0.7});")
    lines.append(r"")

    # Background fills
    for r_idx, line in enumerate(frame["lines"]):
        col_offset = 0
        for run in line["runs"]:
            n = run["n"]
            bg = run["bg"]

            needs_fill = False
            if bw:
                if bg != default_bg:
                    needs_fill = True
            else:
                if bg != default_bg:
                    needs_fill = True

            if needs_fill:
                x1 = col_offset
                y1 = -r_idx + 0.25
                x2 = col_offset + n
                y2 = -r_idx - 0.75

                if bw:
                    lines.append(f"  \\fill[black] ({x1}, {y1}) rectangle ({x2}, {y2});")
                else:
                    cr, cg, cb = hex_to_rgb(bg)
                    lines.append(f"  \\definecolor{{bg{r_idx}_{col_offset}}}{{rgb}}{{{cr:.3f},{cg:.3f},{cb:.3f}}}")
                    lines.append(f"  \\fill[bg{r_idx}_{col_offset}] ({x1}, {y1}) rectangle ({x2}, {y2});")

            col_offset += n

    lines.append(r"")

    # Text
    for r_idx, line in enumerate(frame["lines"]):
        text = line["text"]
        col_offset = 0
        for run in line["runs"]:
            n = run["n"]
            fg = run["fg"]
            bg = run["bg"]
            bold = run.get("b", False)
            chunk = text[col_offset:col_offset + n].rstrip()

            if chunk:
                escaped = latex_escape(chunk)

                if bold:
                    escaped = f"\\textbf{{{escaped}}}"

                x = col_offset + 0.05
                y = -r_idx

                if bw:
                    if bg != default_bg:
                        # White text on filled background
                        lines.append(f"  \\node[anchor=base west, text=white, inner sep=0pt, font=\\ttfamily\\small] at ({x}, {y}) {{{escaped}}};")
                    else:
                        lines.append(f"  \\node[anchor=base west, inner sep=0pt, font=\\ttfamily\\small] at ({x}, {y}) {{{escaped}}};")
                else:
                    cr, cg, cb = hex_to_rgb(fg)
                    cname = f"fg{r_idx}_{col_offset}"
                    lines.append(f"  \\definecolor{{{cname}}}{{rgb}}{{{cr:.3f},{cg:.3f},{cb:.3f}}}")
                    lines.append(f"  \\node[anchor=base west, text={cname}, inner sep=0pt, font=\\ttfamily\\small] at ({x}, {y}) {{{escaped}}};")

            col_offset += n

    # Cursor
    if cursor.get("visible", True):
        cr_row, cc_col = cursor["row"], cursor["col"]
        x1 = cc_col
        y1 = -cr_row + 0.25
        x2 = cc_col + 1
        y2 = -cr_row - 0.75

        if bw:
            lines.append(f"  \\draw[black, very thick] ({x1}, {y1}) rectangle ({x2}, {y2});")
        else:
            lines.append(f"  \\draw[white, thick] ({x1}, {y1}) rectangle ({x2}, {y2});")

    lines.append(r"")
    lines.append(r"\end{tikzpicture}")
    lines.append(r"\end{document}")

    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python render_latex.py sample_frame.json [output.tex]")
        sys.exit(1)

    frame_path = Path(sys.argv[1])
    frame = json.loads(frame_path.read_text("utf-8"))

    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else frame_path.with_suffix(".tex")

    tex = render_frame_latex(frame, bw=True)
    out_path.write_text(tex, encoding="utf-8")
    print(f"Wrote {out_path} ({out_path.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
