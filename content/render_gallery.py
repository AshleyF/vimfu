"""
Render a single screenshot gallery page listing every example with all its
frames inline. Useful for at-a-glance verification that screenshots render.

Output: content/output/html/screenshots.html
"""

from __future__ import annotations

import json
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXAMPLES_DIR = ROOT / "examples"
SCREENSHOTS_DIR = ROOT / "output" / "screenshots"
OUT = ROOT / "output" / "html" / "screenshots.html"


def main() -> int:
    if not SCREENSHOTS_DIR.exists():
        print("No screenshots dir — run render_screenshots.py first.", file=sys.stderr)
        return 1
    examples = []
    for p in sorted(EXAMPLES_DIR.glob("*.json")):
        try:
            ex = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        examples.append(ex)

    sections = []
    total_frames = 0
    for ex in examples:
        eid = ex["id"]
        title = ex.get("title", eid)
        summary = ex.get("summary", "")
        topic = ex.get("topic", "")
        frames_html = []
        n_frames = len(ex.get("frames", []))
        for i, fr in enumerate(ex.get("frames", []), start=1):
            cap = fr.get("caption", "")
            keys = fr.get("keys", "")
            rel = f"screenshots/{eid}/frame_{i:02d}.color.svg"
            exists = (SCREENSHOTS_DIR / eid / f"frame_{i:02d}.color.svg").exists()
            badge = f"<kbd>{escape(keys)}</kbd> " if keys else ""
            if exists:
                total_frames += 1
                frames_html.append(
                    f'<figure class="frame">'
                    f'<img src="{escape(rel)}" alt="{escape(cap)}">'
                    f'<figcaption>Step {i} · {badge}{escape(cap)}</figcaption>'
                    f'</figure>'
                )
            else:
                frames_html.append(
                    f'<figure class="frame missing">'
                    f'[missing {eid}/frame_{i:02d}.color.svg]'
                    f'<figcaption>Step {i} · {escape(cap)}</figcaption>'
                    f'</figure>'
                )
        sections.append(
            f'<section id="{escape(eid)}">'
            f'<h2>{escape(title)} <small>({escape(eid)})</small></h2>'
            f'<p class="meta">topic: <code>{escape(topic)}</code> · {n_frames} frame(s)</p>'
            f'<p class="summary">{escape(summary)}</p>'
            f'<div class="frames">{"".join(frames_html)}</div>'
            f'</section>'
        )

    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>VimFu screenshot gallery</title>
<style>
  body {{ font-family: system-ui, sans-serif; max-width: 1100px; margin: 2rem auto; padding: 0 1rem; color: #234; }}
  header {{ border-bottom: 2px solid #234; margin-bottom: 1.5rem; padding-bottom: 0.5rem; }}
  header h1 {{ margin: 0; }}
  header p {{ margin: 0.25rem 0; color: #678; }}
  section {{ margin: 2rem 0; padding: 1rem; background: #f8fafc; border: 1px solid #d8e0ee; border-radius: 6px; }}
  section h2 {{ margin: 0 0 0.4rem; font-size: 1.2rem; }}
  section h2 small {{ color: #678; font-weight: normal; font-family: monospace; font-size: 0.9rem; }}
  p.meta {{ font-size: 0.85rem; color: #678; margin: 0.25rem 0; }}
  p.summary {{ margin: 0.5rem 0 1rem; font-style: italic; color: #345; }}
  div.frames {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(360px, 1fr)); gap: 1rem; }}
  figure.frame {{ margin: 0; padding: 0.4rem; background: #fff; border: 1px solid #dde6f2; border-radius: 4px; }}
  figure.frame img {{ width: 100%; height: auto; display: block; background: #000; border-radius: 4px; }}
  figure.frame figcaption {{ margin-top: 0.4rem; font-size: 0.85rem; color: #345; }}
  figure.frame.missing {{ background: #fee; color: #900; padding: 1rem; text-align: center; font-family: monospace; }}
  kbd {{ padding: 1px 6px; border: 1px solid #aaa; border-radius: 3px; background: #fafafa; font-family: monospace; font-size: 0.85rem; }}
  nav.toc {{ columns: 3; column-gap: 1.5rem; font-size: 0.9rem; }}
  nav.toc a {{ display: block; padding: 0.1rem 0; color: #045; text-decoration: none; }}
  nav.toc a:hover {{ text-decoration: underline; }}
</style>
</head><body>
<header>
  <h1>VimFu screenshot gallery</h1>
  <p>{len(examples)} example(s) · {total_frames} frame(s) on disk</p>
  <p><a href="index.html">← back to topics</a></p>
</header>
<nav class="toc">
{"".join(f'<a href="#{escape(e["id"])}">{escape(e.get("title", e["id"]))}</a>' for e in examples)}
</nav>
{"".join(sections)}
</body></html>
"""
    OUT.write_text(page, encoding="utf-8")
    print(f"Wrote gallery -> {OUT}")
    print(f"  {len(examples)} example(s), {total_frames} frame(s) referenced")
    return 0


if __name__ == "__main__":
    sys.exit(main())
