# VimFu

Learn Vim from zero to fluency — through short videos, an interactive
simulator, and a book/site built from one content graph.

**Site:** [vimfubook.com](https://vimfubook.com)

## YouTube Shorts

The `curriculum/` folder holds a structured curriculum of short-form
video lessons covering Vim, tmux, and shell skills. Each lesson is a
JSON file that drives the automated video pipeline in `shellpilot/` —
recording real Neovim/`tmux` sessions with TTS narration, keystroke
overlays, and auto-generated thumbnails.

## Vim Simulator

A web-based Vim simulator that runs entirely in the browser. Practice
*normal mode*, *insert mode*, motions, operators, text objects,
registers, macros, and more — no install required.

**Try it live:** [vimfubook.com/sim](https://vimfubook.com/sim/)

Source is in the `sim/` folder. Tests compare simulator output against
real Neovim for fidelity.

## Book and website

The **canonical source** is `content/parts/**/*.json`. From there we
render the website (`content/deploy_site.py` → `docs/`), the PDF book
(`content/build_pdf.py`), InDesign Tagged Text, and SVG screenshots of
worked examples.

**Read it online:** [vimfubook.com](https://vimfubook.com)

Do **not** author in `book/content/` — that tree is a legacy prototype.
See `AGENTS.md` and `content/StyleGuide.md` before editing prose.

## Keyboard Explorer

An interactive SVG keyboard that shows what every Vim key does (shipped
with the site).

## Project structure

| Folder | Description |
|---|---|
| `content/` | **Source of truth** — topics, examples, style guide, renderers |
| `docs/` | Published GitHub Pages site (generated; see `deploy_site.py`) |
| `curriculum/` | Video curriculum / short lesson JSON |
| `shellpilot/` | Video recording/playback engine (PTY, TTS, GIF/MP4) |
| `sim/` | Browser-based Vim simulator |
| `book/` | Marketing/cover, illustrations; `book/content/` is **legacy** |
| `archive/` | Legacy DemoGen (F# automation, retired) |

## Agent / author entry points

- `AGENTS.md` — how to work in this repo
- `content/StyleGuide.md` — prose/key/mode markup contract (read before any prose edit)
- `content/README.md` — content system layout and build commands
