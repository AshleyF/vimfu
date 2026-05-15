"""
Generate the static client-side redirect pages served at
``vimfubook.com/r/<slug>``.

Reads:
  * ``content/parts/**/*.json``      (topics → ``t-<id>`` redirects)
  * ``content/examples/*.json``      (examples → ``sim-ex-<id>``)
  * ``curriculum/{shorts,longs}/*``  (videos → ``v-NNNN``)
  * ``content/redirects.manual.json``(hand-curated)
  * derived per-part video pages and the ``sim-tmux`` deep link.

Writes:
  * ``content/output/html/r/<slug>/index.html`` — one tiny page per slug
    that does an instant client-side redirect (meta refresh + JS, with an
    HTML fallback link).
  * ``content/output/html/r/redirects.json`` — the resolved slug→target
    map, useful for debugging or deploying server-side redirects later.

Usage:
    python content/render_redirects.py
    python content/render_redirects.py --base-url https://staging.vimfubook.com
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib.parse import urlencode

# Ensure UTF-8 stdout on Windows (cp1252) so summary prints with "→" don't crash.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from lib.redirects import (  # noqa: E402
    DEFAULT_BASE_URL,
    BOOK_SLUG,
    REPORT_ISSUE_SLUG,
    REPORT_BOOK_ISSUE_SLUG,
    SIM_TMUX_SLUG,
    errata_slug,
    part_videos_slug,
    sim_example_slug,
    topic_slug,
    video_slug,
)
from lib.site_config import contact_email, current_edition, editions  # noqa: E402
from lib.videos import _index as _videos_index  # noqa: E402
from lib.sim_link import SIM_LINK_VERSION, practice_filename  # noqa: E402

PARTS_DIR = ROOT / "parts"
EXAMPLES_DIR = ROOT / "examples"
MANUAL_REDIRECTS = ROOT / "redirects.manual.json"
OUT_DIR = ROOT / "output" / "html" / "r"


PAGE_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Redirecting…</title>
<meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0;url={target_attr}">
<link rel="canonical" href="{target_attr}">
<style>body{{font-family:system-ui,sans-serif;max-width:36em;margin:4em auto;padding:0 1em;color:#333}}</style>
</head>
<body>
<h1>Redirecting…</h1>
<p>If you are not redirected automatically, follow this link:
<a href="{target_attr}">{target_text}</a></p>
<script>location.replace({target_json});</script>
</body>
</html>
"""


def _html_attr(s: str) -> str:
    # The href/meta value: HTML attribute escaping.
    return (s.replace("&", "&amp;").replace('"', "&quot;")
             .replace("<", "&lt;").replace(">", "&gt;"))


def _html_text(s: str) -> str:
    return _html_attr(s)


def build_map(base_url: str) -> dict[str, str]:
    """Build the full slug → target-URL map from all sources."""
    m: dict[str, str] = {}

    # --- topics ------------------------------------------------------------
    for p in sorted(PARTS_DIR.glob("*/*.json")):
        try:
            t = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        tid = t.get("id")
        if not tid:
            continue
        m[topic_slug(tid)] = f"{base_url}/{p.parent.name}/{p.stem}"

    # --- per-part videos pages --------------------------------------------
    for d in sorted({p.parent.name for p in PARTS_DIR.glob("*/*.json")}):
        m[part_videos_slug(d)] = f"{base_url}/videos/{d}"

    # --- videos ------------------------------------------------------------
    for n, v in _videos_index().items():
        if v.get("url"):
            m[video_slug(n)] = v["url"]
        else:
            # Not yet published — point at the "coming soon" page on the
            # site (it can render whatever placeholder it likes).
            m[video_slug(n)] = f"{base_url}/videos/coming-soon?lesson={n}"

    # --- example sim deep links -------------------------------------------
    for p in sorted(EXAMPLES_DIR.glob("*.json")):
        try:
            ex = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        ex_id = ex.get("id")
        if not ex_id:
            continue
        target = _example_sim_url(ex, base_url)
        if target:
            m[sim_example_slug(ex_id)] = target

    # --- tmux sim launch ---------------------------------------------------
    m[SIM_TMUX_SLUG] = f"{base_url}/sim/?" + urlencode(
        {"v": SIM_LINK_VERSION, "cmd": "tmux"}
    )

    # --- errata pages (one per known edition, plus a "latest" alias) ------
    for e in editions():
        m[errata_slug(e["slug"])] = f"{base_url}/errata/{e['slug']}/"
    m["errata"] = f"{base_url}/errata/{current_edition()}/"

    # --- "report a problem" mailto links ---------------------------------
    from urllib.parse import quote
    email = contact_email()
    m[REPORT_ISSUE_SLUG] = (
        f"mailto:{email}"
        f"?subject={quote('VimFu — issue report')}"
        f"&body={quote('Where: (page or URL)\nIssue: \n')}"
    )
    m[REPORT_BOOK_ISSUE_SLUG] = (
        f"mailto:{email}"
        f"?subject={quote('VimFu book — errata report')}"
        f"&body={quote('Page: \nLocation: \nIssue: \nSuggested correction: \n')}"
    )

    # --- hand-curated overrides (last so they always win) -----------------
    if MANUAL_REDIRECTS.exists():
        manual = json.loads(MANUAL_REDIRECTS.read_text(encoding="utf-8"))
        for k, v in manual.items():
            if k.startswith("_"):
                continue
            m[k] = v

    return m


def _example_sim_url(ex: dict, base_url: str) -> str | None:
    frames = ex.get("frames") or []
    if not frames:
        return None
    compact = (frames[0].get("compact") or {})
    raw = compact.get("lines") or []
    lines = [ln for ln in raw if ln.strip() not in ("~",)]
    if lines and "  " in lines[-1] and ("," in lines[-1] or "%" in lines[-1]):
        lines = lines[:-1]
    if not lines:
        return None
    content = "\n".join(lines) + "\n"
    qs = urlencode({
        "v": SIM_LINK_VERSION,
        "file": practice_filename(ex, content),
        "content": content,
    })
    return f"{base_url}/sim/?{qs}"


def write_pages(m: dict[str, str], out_dir: Path) -> int:
    """Write a redirect page for every slug AND its short id.

    QR codes printed in the book encode the SHORT-id form
    (``vimfubook.com/r/0079``) — see ``redirect_url()`` in
    ``lib/redirects.py``. The slug-form (``/r/vimspeak``) is the
    developer-facing identifier and is also useful for typed URLs.
    Both must resolve to the same target on the deployed site.
    """
    from lib.redirect_ids import id_for_slug  # local import to avoid cycles
    out_dir.mkdir(parents=True, exist_ok=True)
    n = 0
    written: set[str] = set()
    for slug, target in m.items():
        html = PAGE_TEMPLATE.format(
            target_attr=_html_attr(target),
            target_text=_html_text(target),
            target_json=json.dumps(target),
        )
        paths = [slug]
        try:
            short = id_for_slug(slug)
        except Exception:
            short = None
        if short and short != slug:
            paths.append(short)
        for path in paths:
            if path in written:
                continue
            d = out_dir / path
            d.mkdir(parents=True, exist_ok=True)
            (d / "index.html").write_text(html, encoding="utf-8")
            written.add(path)
            n += 1
    (out_dir / "redirects.json").write_text(
        json.dumps(m, indent=2, sort_keys=True), encoding="utf-8"
    )
    return n


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default=DEFAULT_BASE_URL,
                    help=f"Base URL for the site (default: {DEFAULT_BASE_URL}).")
    ap.add_argument("--out", type=Path, default=OUT_DIR,
                    help="Output directory (default: content/output/html/r).")
    args = ap.parse_args()

    m = build_map(args.base_url.rstrip("/"))
    n = write_pages(m, args.out)
    by_kind: dict[str, int] = {}
    for slug in m:
        prefix = slug.split("-", 1)[0] if "-" in slug else slug
        by_kind[prefix] = by_kind.get(prefix, 0) + 1
    print(f"Wrote {n} redirect pages → {args.out}")
    for k, c in sorted(by_kind.items()):
        print(f"  {k:>10}: {c}")
    print(f"  Map: {args.out / 'redirects.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
