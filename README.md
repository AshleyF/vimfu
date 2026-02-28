# VimFu

Learn Vim from zero to fluency — through short videos, an interactive simulator, and an online book.

## YouTube Shorts

The `curriculum/` folder contains a structured curriculum of 188 short-form video lessons covering Vim, Tmux, and shell skills. Each lesson is a JSON file that drives the automated video pipeline in `shellpilot/` — recording real Neovim/Tmux sessions with TTS narration, keystroke overlays, and auto-generated thumbnails. Videos are published to the [VimFu YouTube playlist](https://www.youtube.com/playlist?list=PLJOq0hDFOHzJfFcxZBYbSsYkHo-wR0EC_).

## Vim Simulator

A web-based Vim simulator that runs entirely in the browser. Practice normal mode, insert mode, motions, operators, text objects, registers, macros, and more — no install required.

**Try it live:** [ashleyf.github.io/vimfu/sim](https://ashleyf.github.io/vimfu/sim/)

Source is in the `sim/` folder. Tests compare simulator output against real Neovim for pixel-perfect fidelity.

## Book

An online companion book covering the full curriculum — from survival basics through advanced topics and surround.vim.

**Read it online:** [ashleyf.github.io/vimfu/book/output](https://ashleyf.github.io/vimfu/book/output/)

Source content is in `book/content/` as JSON; rendered to HTML by `book/render_page.py`.

## Keyboard Explorer

An interactive SVG keyboard that shows what every Vim key does.

**Try it live:** [ashleyf.github.io/vimfu](https://ashleyf.github.io/vimfu/)

## Project Structure

| Folder | Description |
|---|---|
| `curriculum/` | Lesson curriculum and 188 video JSON files |
| `shellpilot/` | Video recording/playback engine (PTY, TTS, GIF/MP4) |
| `sim/` | Browser-based Vim simulator |
| `book/` | Online book content and renderer |
| `archive/` | Legacy DemoGen (F# automation, retired) |
