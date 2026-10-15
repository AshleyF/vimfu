# Content Migration

Historical note: early VimFu book prose lived under `book/content/` and
was rendered by `book/render_page.py`. That era is over.

**Canonical source today:** `content/parts/**/*.json` (plus
`content/example_defs/`, theses, and the content renderers). See
`AGENTS.md` and `content/StyleGuide.md`.

This file stays as a short quarantine marker so agents do not re-open
the prototype tree for authoring. Delete it once `book/content/` itself
is removed from the repo.

---

## Do not author here

| Path | Status |
|------|--------|
| `book/content/*.json` | **Legacy / do-not-author.** Early prototype chapters. Topics for foundations/survival/basic-editing already live under `content/parts/`. Mine only if you need leftover prose, then leave the files alone. |
| `book/render_page.py` | **Legacy.** Site/book rendering is `content/render_html.py`, `content/deploy_site.py`, `content/render_latex.py`, `content/build_pdf.py`. |
| `book/output/*` | **Legacy generated artifacts.** Ignore. |

When leftover mining is finished:

```
git rm -r book/content/
git rm book/render_page.py
```

Keep `book/marketing/`, `book/illustrations/`, and related print assets —
those are still live.

## Kept (separate, ongoing jobs)

| Path | Why keep |
|------|----------|
| `curriculum/shorts/*.json` | Per-lesson video source of truth |
| `sim/` | Simulator + oracle tests |
| `shellpilot/` | Capture / record pipeline |
| `docs/` | Published site (generated; preserve list in `deploy_site.py`) |
