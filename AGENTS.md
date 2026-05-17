# Agent Instructions

VimFu is one source of truth (the JSON topic files in `content/parts/`)
rendered to a website, a book, intermediate markdown, InDesign Tagged
Text, and SVG screenshots. Treat the JSON as canonical.

## Style guide — read first

Before editing any prose, table, heading, title, caption, or example
in the book or website, **read [`content/StyleGuide.md`](content/StyleGuide.md)**.
It is the authoritative reference for:

- Keys (boxed pills) vs commands (monospace) vs plain prose.
- Mode names (always lowercase italic, e.g. *normal mode*).
- Italic punctuation (punctuation goes inside the italic span).
- Key-sequence spacing (touching, no literal spaces between pills in
  one sequence).
- Placeholder templates (`f{c}`, `c{motion}`, `/{pattern}`).
- Lowercase Unix command names (`vi`, `ed`, `ex`, `nvim`, `tmux`).
- Chapter/heading titles use `{key:...}` markup, never plain text.

If you observe an inconsistency that the style guide doesn't yet
cover, add a rule for it to `StyleGuide.md` *before* the fix lands —
the guide is meant to grow with every new convention discovered.

## Build commands

- **PDF book:** `python content\build_pdf.py` (uses `xelatex` via
  MiKTeX; takes ~5 min). On Windows ensure Inkscape is on PATH:
  `$env:PATH += ';C:\Program Files\Inkscape\bin'`.
- **Website:** `python content\deploy_site.py --skip-sim` (~30 s).
- **Screenshots:** `python content\render_screenshots.py` — run if
  `content/output/html/screenshots/` has been wiped.

## Repository layout (highlights)

- `content/parts/<part>/<topic>.json` — topic source files.
- `content/render_latex.py` — book renderer.
- `content/lib/parts.py` — part display labels.
- `content/StyleGuide.md` — style rules.
- `book/illustrations/<part>.png` — chapter-opener illustrations.
- `docs/` — published website (overwritten by `deploy_site.py`; see
  `PRESERVE` set there for files that survive deploys).
- `curriculum/`, `shellpilot/`, `sim/` — adjacent tooling, not the
  book content itself.

## Conventions

- Use Windows-style paths (`\`) on Windows.
- Commits include `Co-authored-by: Copilot
  <223556219+Copilot@users.noreply.github.com>`.
- Don't create planning markdown files unless asked. Use the session
  workspace for ephemeral notes.
