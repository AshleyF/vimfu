"""
Render a Frame JSON as an HTML file.

Usage: python render_html.py sample_frame.json [output.html]

Produces an HTML page with:
  - Color rendering (screen view)
  - B&W print stylesheet (@media print)
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


def html_escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_frame_html(frame: dict) -> str:
    rows = frame["rows"]
    cols = frame["cols"]
    cursor = frame["cursor"]
    default_fg = frame["defaultFg"]
    default_bg = frame["defaultBg"]

    html_rows = []
    for r, line in enumerate(frame["lines"]):
        text = line["text"]
        col_offset = 0
        spans = []
        for run in line["runs"]:
            n = run["n"]
            fg = run["fg"]
            bg = run["bg"]
            bold = run.get("b", False)
            italic = run.get("i", False)
            underline = run.get("u", False)

            chunk = text[col_offset:col_offset + n]

            # Determine B&W classes
            bw_class = ""
            if bg != default_bg:
                if not is_dark(bg):
                    bw_class = "inv"  # status bar / inverted
                else:
                    bw_class = "hl"   # highlighted

            styles = []
            styles.append(f"color:#{fg}")
            if bg != default_bg:
                styles.append(f"background:#{bg}")
            if bold:
                styles.append("font-weight:bold")
            if italic:
                styles.append("font-style:italic")
            if underline:
                styles.append("text-decoration:underline")

            classes = []
            if bw_class:
                classes.append(bw_class)

            cls_attr = f' class="{" ".join(classes)}"' if classes else ""
            style_attr = f' style="{";".join(styles)}"'

            # Check if cursor is in this run
            if cursor.get("visible", True) and r == cursor["row"]:
                cc = cursor["col"]
                if col_offset <= cc < col_offset + n:
                    # Split run around cursor
                    pre = chunk[:cc - col_offset]
                    cur_char = chunk[cc - col_offset]
                    post = chunk[cc - col_offset + 1:]
                    if pre:
                        spans.append(f'<span{cls_attr}{style_attr}>{html_escape(pre)}</span>')
                    spans.append(f'<span class="cursor{" " + bw_class if bw_class else ""}"{style_attr}>{html_escape(cur_char)}</span>')
                    if post:
                        spans.append(f'<span{cls_attr}{style_attr}>{html_escape(post)}</span>')
                    col_offset += n
                    continue

            spans.append(f'<span{cls_attr}{style_attr}>{html_escape(chunk)}</span>')
            col_offset += n

        html_rows.append("".join(spans))

    terminal_html = "\n".join(html_rows)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>VimFu Frame</title>
<style>
  /* === Screen (color) === */
  body {{
    background: #1e1e1e;
    display: flex;
    justify-content: center;
    padding: 40px;
  }}
  .terminal {{
    background: #{default_bg};
    padding: 16px;
    border-radius: 8px;
    border: 1px solid #333;
    font-family: 'Cascadia Code', 'Consolas', 'Courier New', monospace;
    font-size: 14px;
    line-height: 1.35;
    white-space: pre;
    color: #{default_fg};
  }}
  .cursor {{
    outline: 2px solid #fff;
    outline-offset: -1px;
  }}

  /* === Print (B&W) === */
  @media print {{
    body {{
      background: white;
      padding: 0;
    }}
    .terminal {{
      background: white !important;
      border: 1px solid #000;
      border-radius: 0;
      color: #000 !important;
      padding: 12px;
    }}
    .terminal span {{
      color: #000 !important;
      background: transparent !important;
    }}
    /* Highlighted regions: inverted */
    .terminal span.hl,
    .terminal span.inv {{
      color: #fff !important;
      background: #000 !important;
    }}
    /* Cursor: thick border */
    .terminal span.cursor {{
      outline: 2.5px solid #000;
      outline-offset: -1px;
    }}
    /* Cursor inside highlight: dashed border */
    .terminal span.cursor.hl {{
      outline-style: dashed;
    }}
  }}
</style>
</head>
<body>
<pre class="terminal">{terminal_html}</pre>
</body>
</html>"""


def main():
    if len(sys.argv) < 2:
        print("Usage: python render_html.py sample_frame.json [output.html]")
        sys.exit(1)

    frame_path = Path(sys.argv[1])
    frame = json.loads(frame_path.read_text("utf-8"))

    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else frame_path.with_suffix(".html")

    html = render_frame_html(frame)
    out_path.write_text(html, encoding="utf-8")
    print(f"Wrote {out_path} ({out_path.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
