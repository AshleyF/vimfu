# vt-term

A standalone, canvas-based VT/xterm-compatible terminal emulator
written in pure JavaScript, plus a cross-platform Python WebSocket↔PTY
bridge for connecting a browser-resident terminal to a real shell.

Built as a sibling project to the [VimFu](../sim/) simulator — same
"ground-truth-against-pyte" testing philosophy, no shared runtime
code. Implemented from scratch on top of the Paul Williams DEC ANSI
parser state machine.

---

## Features

### Rendering
- Canvas-based, DPI-aware (1 logical CSS pixel = `devicePixelRatio` device pixels).
- 16 / 256 / 24-bit truecolor.
- Cursor styles: block / bar / underline, steady or blink.
- Bold, italic, underline, strikethrough, reverse video.
- **DEC line-drawing glyphs are stroked geometrically** (half-pixel
  snapped) — boxes always connect cleanly across cells regardless of
  font glyph quality.
- **Sixel** images with 1:1 integer-scale rendering (no blur).

### Terminal core
- Williams' state machine: ESC, CSI, OSC, DCS, SOS/PM/APC, full
  UTF-8 assembly.
- CSI: CUU/CUD/CUF/CUB/CHA/HPA/VPA/CUP/HVP, ED/EL/ECH, IL/DL/ICH/DCH,
  SU/SD, DECSTBM, REP, TBC/HTS/CBT/CHT, DA/DSR, DECSCUSR, SM/RM, SGR.
- DEC private modes: DECCKM, DECOM, DECAWM, DECTCEM, IRM, alt-buffer
  47/1047/1048/1049, bracketed paste (2004), mouse-mode parsing.
- OSC: 0/2 (title), 4 (palette set), 8 (hyperlinks), 104 (palette
  reset).
- Charsets: G0..G3 + GL/GR, DEC special graphics, ASCII.
- Cursor save/restore (DECSC/DECRC and 1048).

### Browser UI
- Auto-fits the terminal to the right-hand pane; rows × cols update
  on viewport resize and on sidebar layout changes (`ResizeObserver`).
- **Zoom controls**: `A−` / `100%` / `A+` buttons + `Ctrl-−` / `Ctrl-0`
  / `Ctrl-+` shortcuts. Cell width/height scale together with the
  font, always in whole pixels.
- **Cell height constrained to a multiple of `6 × sixelScale`** so
  sixel bands tile cleanly into character rows (matches VT340 — 3
  bands per row at default size).
- Status indicator: `cols × rows · font px · cell w×h · N bands/row`.
- Demo buttons exercise every category: color palette, SGR attrs,
  cursor styles, alt screen, DEC line drawing, line wrap, scroll
  region, sixel demos (procedural + real-world fixtures).
- Live shell mode: connect to the Python bridge over WebSocket.

### Bridge
- Cross-platform Python WebSocket↔PTY proxy.
- Windows: pywinpty (ConPTY). macOS / Linux: stdlib `pty.fork()`.
- Resize events plumbed end-to-end (TIOCSWINSZ / setwinsize).
- DSR/DA/cursor-report responses flow back to the host.

---

## Quick start

### Just the demo page (no shell)

```
cd terminal
python serve.py                       # no-cache static server on :8000
# open http://127.0.0.1:8000/index.html
```

Click around the sidebar buttons; every feature is exercised in
isolation. No shell required.

### With a real shell

```
pip install -r bridge/requirements.txt
python bridge/proxy.py --shell powershell.exe       # or bash, or cmd.exe
# In the page: leave the URL as ws://127.0.0.1:7681, click Connect
```

Other useful shells:
```
python bridge/proxy.py --shell pwsh.exe              # PowerShell 7
python bridge/proxy.py --shell "wsl.exe ~ -e bash -l"
python bridge/proxy.py --shell bash --port 9000
```

---

## Directory layout

```
terminal/
  README.md
  AGENTS.md                 ← detailed architecture for AI agents
  package.json
  jest.config.js
  playwright.config.js
  serve.py                  ← static file server with no-cache headers
  index.html                ← demo page

  src/
    parser.js               ← Paul Williams' DEC ANSI state machine
    screen.js               ← cell grid, scroll region, alt buffer, scrollback
    palette.js              ← 16/256/truecolor; OSC 4 palette mutation
    terminal.js             ← parser↔screen glue; SGR, modes, OSC, DCS
    renderer.js             ← canvas: glyphs, cursor styles, box-drawing,
                              integer-scale sixel compositing
    input.js                ← KeyboardEvent → host bytes
    sixel.js                ← DCS Pq decoder with Ps1 + raster attrs
    websocket.js            ← WS client (binary + JSON control frames)
    main.js                 ← demo + zoom + auto-fit + live shell wiring

  bridge/
    proxy.py                ← cross-platform WS↔PTY proxy
    requirements.txt
    README.md

  test/
    cases/test_*.py         ← raw-byte test cases by category
    fixtures/sixel/*.six    ← real-world sixel files from csdvrx/sixel-testsuite
    ground_truth/*.json     ← per-suite pyte frame dicts (regenerable)
    gen_ground_truth.py     ← feeds cases through pyte → writes JSON
    capture_demos.js        ← visual capture script (Playwright)
    render_harness.html     ← Playwright-driven mini page

    parser.test.js          ← FSM unit tests
    terminal.test.js        ← ground-truth comparison against pyte
    sixel.test.js           ← sixel decoder unit tests
    sixel_fixtures.test.js  ← decoder vs real-world .six files
    input.test.js           ← keyboard encoding
    osc.test.js             ← title/palette/hyperlink callbacks
    modes.test.js           ← DEC private + ANSI modes
    alt_screen.test.js      ← alt-buffer isolation, save/restore
    resize.test.js          ← screen resize correctness

    render.pw.test.js       ← canvas-pixel rendering tests
    demo.pw.test.js         ← end-to-end demo button tests
    bulk_render.pw.test.js  ← cellH invariants, zoom, status, etc.
```

---

## Testing

Two distinct layers.

### Layer 1 — Engine (Jest)

Same test pattern as the VimFu Vim simulator: a Python ground-truth
generator runs raw byte streams through `pyte.Screen` and writes the
resulting frame dicts to JSON. A jest test feeds the same bytes
through our terminal and compares.

```
npm install
python test/gen_ground_truth.py
npm test
```

Coverage:
- **493 ground-truth cases vs pyte** (basic, csi_cursor, sgr, erase,
  scroll, wrap, insert/delete, save_restore, origin, tabs, plus
  bulk suites for cursor/sgr/erase/wrap/insert).
- **Parser FSM**: 13 direct tests of the state machine
  (ground/escape/CSI/OSC/DCS).
- **Sixel decoder**: 11 synthetic + 7 real-world fixture tests
  (smallest sixel, gradient, 3-color, 160×160 portrait, 600×450
  photo from csdvrx/sixel-testsuite).
- **Input encoding**: 17 tests covering cursor keys (normal + app
  mode), F1–F12 with modifiers, Ctrl-letters, Alt-prefix, bracketed
  paste.
- **OSC callbacks**: 11 tests for title (0/2), palette (4/104),
  hyperlinks (8), Unicode payloads.
- **Modes**: 18 tests for DECCKM, DECTCEM, DECAWM, IRM, bracketed
  paste, DECOM, DECSCUSR, DA, DSR, RIS.
- **Alt screen**: 9 tests for 47/1047/1048/1049 isolation.
- **Resize**: 8 tests for screen reshape, cursor clamping, alt-buffer
  parity.

Where pyte is incomplete (CBT, CHT, HPA, REP, SU/SD, alt-buffer
modes, DEC line-drawing translation, SCOSC/SCORC) we use hand-written
unit tests instead — those areas are still covered, just not via the
pyte oracle.

### Layer 2 — Rendering (Playwright)

A headless Chromium instance drives a minimal harness page and
inspects actual canvas pixels.

```
npx playwright install chromium
npm run test:render
```

Coverage:
- **Low-level rendering**: 24 tests including default bg, SGR colours,
  truecolor bg, ink density, bold weight, underline / strike pixels,
  reverse video, DEC line drawing edge-to-edge connectivity, cursor
  block, sixel overlay (image on top of text, transparent pixels let
  text show through), sixel cursor advance, canvas geometry.
- **Demo-button end-to-end**: 12 tests that click each demo button
  and verify the canvas contents — catches "demo author wrote the
  wrong bytes" regressions.
- **Bulk & invariants**: 7 tests sweeping font size 8..40 verifying
  cellH-multiple-of-(6×sixelScale), keyboard zoom shortcuts, status
  bar updates, multi-row writes, crisp sixel at high zoom.

### One-shot scripts

```
npm run capture                    # snapshot every demo button → test/screenshots/
node test/zoom_check.mjs           # snake at 1× and 2× zoom on dpr=2
node test/highdpi_check.mjs        # color demo at dpr=2
node test/overlay_check.mjs        # sixel overlapping text
```

### Run everything

```
npm run test:all                   # jest + playwright
```

---

## Testing strategy notes

`pyte` is a wonderful library but it diverges from xterm/spec in
several specific places. Where it disagrees, we side with xterm/spec
and document the divergence:

| Sequence            | What pyte does            | What we do                   |
| ------------------- | ------------------------- | ---------------------------- |
| `CSI s` / `CSI u`   | not implemented           | SCOSC / SCORC                |
| `CSI Ps S` / `T`    | not implemented           | SU / SD                      |
| `CSI Ps I` / `Z`    | not implemented           | CHT / CBT                    |
| `CSI Ps \``         | not implemented           | HPA                          |
| `CSI Ps b`          | not implemented           | REP                          |
| `?47h`/`?1047h`/`?1048h`/`?1049h` | accepted but no-op | full alt-screen behaviour |
| `ESC ( 0` DEC graphics | not translated in display | translated to box-drawing glyphs (default), opt-out via `pyteCompat: true` |
| Sparse-row `DL` on empty rows | leaves dest unchanged | overwrites (real-terminal behaviour) |

Cases that exercise the above are tested with direct Jest assertions
against our Terminal model instead of via the pyte oracle.

---

## Status

| area                       | state |
| -------------------------- | ----- |
| VT parser FSM              | ✅ Williams; UTF-8-clean inside string states |
| Screen model               | ✅ cells, attrs, alt buffer, scroll region, scrollback, tabs |
| Palette                    | ✅ 16, 256, truecolor, OSC 4, ISO 8613-6 |
| Terminal core              | ✅ common CSI + SGR + DECSET/RST + OSC 0/2/4/8 |
| Canvas renderer            | ✅ glyphs, cursor styles + blink, geometric box-drawing, integer-scale sixels, high-DPI |
| Keyboard input             | ✅ cursor app/normal, F1..F12, modifiers, bracketed paste |
| WS↔PTY bridge              | ✅ Windows (pywinpty) + Unix (pty); end-to-end verified |
| Sixel decoder              | ✅ RGB + HLS, `!` repeat, `$` CR, `-` LF, Ps1 + raster attrs |
| Auto-fit + zoom            | ✅ ResizeObserver + Ctrl-+ / Ctrl-− / Ctrl-0 + buttons |
| Ground-truth gen           | ✅ pyte-based, 493 cases |
| **Engine tests (Jest)**    | ✅ **589 passing** |
| **Rendering tests (PW)**   | ✅ **43 passing** |
| **Total**                  | ✅ **632 / 632** |
| Mouse encoding             | parsed only (DECSET); send-side not implemented |
| Scrollback view            | model holds it; renderer doesn't paint it yet |
| DECCOLM (132-col)          | not implemented |

---

## Acknowledgements

- Real-world sixel test fixtures from
  [csdvrx/sixel-testsuite](https://github.com/csdvrx/sixel-testsuite).
- DEC ANSI parser state machine: Paul Williams,
  [vt100.net/emu/dec_ansi_parser](https://vt100.net/emu/dec_ansi_parser).
- VT340 / VT240 reference behaviour from the DEC VT420 Video
  Terminal Programmer Reference Manual.
- Sister project: [VimFu Vim simulator](../sim/) — same testing
  philosophy, different scope.

See **[AGENTS.md](AGENTS.md)** for the deeper architectural notes
written for AI agents working on this codebase.
