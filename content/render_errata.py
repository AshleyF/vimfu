"""
Generate per-edition errata pages.

Each printed edition of VimFu carries a QR pointing at
``vimfubook.com/r/errata-<edition>``. This script writes the page that
QR redirects to: a static HTML page listing every known correction for
that edition, plus instructions for reporting new ones.

Authoring
---------
Errata live in ``content/errata/<edition>.json``::

    {
      "edition": "1e",
      "label":   "First Edition",
      "entries": [
        {
          "page": 123,
          "location": "Chapter 7 — Operators & Text Objects",
          "issue":      "Says ``daw`` deletes a WORD; should be ``daW``.",
          "correction": "``daW`` (capital W) deletes a whitespace-delimited WORD.",
          "reported_by": "anon",
          "fixed_in":    "2e"
        }
      ]
    }

Output
------
``content/output/html/errata/<edition>/index.html``

When a new edition ships, add it to ``site.config.json`` and create a
new ``content/errata/<edition>.json``. Old editions stay generated
forever so any printed QR keeps working.

Usage::

    python content/render_errata.py
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from lib.site_config import (  # noqa: E402
    contact_email, current_edition, editions, site_base_url,
)

ERRATA_DIR = ROOT / "errata"
OUT_DIR = ROOT / "output" / "html" / "errata"


def _h(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


PAGE_CSS = """body{font-family:system-ui,-apple-system,sans-serif;max-width:42em;
margin:3em auto;padding:0 1em;color:#222;line-height:1.55}
h1{margin-bottom:0.2em}.subtitle{color:#666;margin-top:0}
.entry{border-left:3px solid #888;padding:0.4em 0 0.4em 1em;margin:1em 0;background:#fafafa}
.entry .meta{font-size:0.9em;color:#555}
.entry .issue{margin:0.4em 0}
.entry .correction{margin:0.4em 0;color:#063}
.empty{padding:1em;background:#f4f4f4;border-radius:4px}
.report{padding:1em;background:#eef;border-radius:4px;margin-top:2em}
code{background:#f0f0f0;padding:1px 4px;border-radius:3px}
.tag{display:inline-block;background:#222;color:#fff;font-size:0.7em;
padding:1px 6px;border-radius:3px;margin-left:6px;vertical-align:1px}"""


def render_page(edition_meta: dict, entries: list[dict],
                is_current: bool, current_label: str) -> str:
    label = edition_meta.get("label", edition_meta.get("slug", ""))
    year = edition_meta.get("year", "")
    out: list[str] = []
    out.append("<!doctype html><html lang=en><head><meta charset=utf-8>")
    out.append(f"<title>Errata — VimFu, {_h(label)}</title>")
    out.append(f"<style>{PAGE_CSS}</style></head><body>")

    out.append(f"<h1>Errata <span class=tag>{_h(label)}</span></h1>")
    sub = f"Corrections for VimFu, {label}"
    if year:
        sub += f" ({year})"
    out.append(f"<p class=subtitle>{_h(sub)}.</p>")

    if not is_current:
        out.append(
            "<p><strong>Heads up:</strong> a newer edition of VimFu is "
            f"available — <em>{_h(current_label)}</em>. The latest "
            "edition incorporates every correction listed below. "
            f"<a href='{site_base_url()}/r/book'>Get the latest edition →</a></p>"
        )

    if not entries:
        out.append(
            "<div class=empty><strong>No errors reported yet.</strong><br>"
            "If you spot a typo, broken link, missing key, or anything "
            "incorrect in your copy of the book, please tell us — see below.</div>"
        )
    else:
        out.append(f"<h2>Known issues ({len(entries)})</h2>")
        for e in entries:
            page = e.get("page")
            loc = e.get("location", "")
            issue = e.get("issue", "")
            corr = e.get("correction", "")
            fixed = e.get("fixed_in", "")
            who = e.get("reported_by", "")
            out.append("<div class=entry>")
            meta_bits = []
            if page is not None:
                meta_bits.append(f"<strong>p.\u00a0{_h(str(page))}</strong>")
            if loc:
                meta_bits.append(_h(loc))
            if fixed:
                meta_bits.append(f"fixed in {_h(fixed)}")
            if who:
                meta_bits.append(f"reported by {_h(who)}")
            if meta_bits:
                out.append(f"<div class=meta>{' · '.join(meta_bits)}</div>")
            if issue:
                out.append(f"<div class=issue><strong>Issue:</strong> {_h(issue)}</div>")
            if corr:
                out.append(f"<div class=correction><strong>Correction:</strong> {_h(corr)}</div>")
            out.append("</div>")

    email = contact_email()
    subj = f"VimFu {label} errata report"
    body = (f"Page: \nLocation: \nIssue: \nSuggested correction: \n\n"
            f"(Edition: {label})")
    from urllib.parse import quote
    mailto = f"mailto:{email}?subject={quote(subj)}&body={quote(body)}"
    out.append("<div class=report>")
    out.append("<h2>Report a problem</h2>")
    out.append(
        "<p>Found something wrong? Drop us a line — please include the "
        "page number and a quote of the affected text so we can find it "
        "quickly.</p>"
    )
    out.append(
        f"<p><strong>Email:</strong> "
        f"<a href='{_h(mailto)}'><code>{_h(email)}</code></a></p>"
    )
    out.append(
        "<p>Or open an issue on GitHub: "
        f"<a href='{site_base_url()}/r/github'>{site_base_url()}/r/github</a></p>"
    )
    out.append("</div></body></html>")
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT_DIR)
    args = ap.parse_args()

    cur = current_edition()
    cur_label = next((e["label"] for e in editions() if e["slug"] == cur), cur)
    n = 0
    for e in editions():
        slug = e["slug"]
        ed_dir = args.out / slug
        ed_dir.mkdir(parents=True, exist_ok=True)
        data_path = ERRATA_DIR / f"{slug}.json"
        entries: list[dict] = []
        if data_path.exists():
            try:
                doc = json.loads(data_path.read_text(encoding="utf-8"))
                entries = doc.get("entries") or []
            except Exception as ex:
                print(f"  ! errata json error in {data_path.name}: {ex}",
                      file=sys.stderr)
        html = render_page(e, entries, is_current=(slug == cur),
                           current_label=cur_label)
        (ed_dir / "index.html").write_text(html, encoding="utf-8")
        n += 1

    # Also write a top-level redirect at /errata/ that points to the latest.
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "index.html").write_text(
        f"<!doctype html><meta http-equiv=refresh content='0;url={cur}/'>"
        f"<a href='{cur}/'>Latest errata →</a>",
        encoding="utf-8",
    )

    print(f"Wrote {n} errata page(s) → {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
