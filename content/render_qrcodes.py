"""
Generate one QR-code SVG per topic, encoding its public website URL.

Usage:
    python content/render_qrcodes.py
    python content/render_qrcodes.py --base-url https://staging.vimfubook.com

Output goes to ``content/output/qrcodes/<part_dir>/<file_stem>.svg``.
The InDesign book renderer references these from ``qr`` blocks; the
website renderer can also embed the same SVGs as inline scan-codes.

Why per-topic and not per-block: every topic ends with a ``qr`` block
pointing at the site URL, so generating one SVG per topic is sufficient.
A topic that wants additional QR codes (e.g. a deep link to a sub-anchor)
can be handled later by extending the ``qr`` block schema with a
``url`` override.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from lib.qr import qr_svg, topic_url, DEFAULT_BASE_URL  # noqa: E402

PARTS_DIR = ROOT / "parts"
OUT_DIR = ROOT / "output" / "qrcodes"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default=DEFAULT_BASE_URL,
                    help=f"Base URL for the site. Default: {DEFAULT_BASE_URL}")
    ap.add_argument("--out", type=Path, default=OUT_DIR,
                    help="Output directory.")
    args = ap.parse_args()

    n_written = 0
    for p in sorted(PARTS_DIR.glob("*/*.json")):
        try:
            t = json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"  ! JSON error in {p.relative_to(ROOT)}: {e}", file=sys.stderr)
            continue
        t["__part_dir"] = p.parent.name
        t["__file_stem"] = p.stem
        url = topic_url(t, base_url=args.base_url)
        svg = qr_svg(url)
        out_path = args.out / p.parent.name / f"{p.stem}.svg"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(svg, encoding="utf-8")
        n_written += 1

    # Also write a manifest so renderers can sanity-check.
    manifest = {
        "base_url": args.base_url,
        "count": n_written,
    }
    (args.out / "_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"Wrote {n_written} QR SVG(s) -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
