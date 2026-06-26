# AGENTS.md — vt-term

Architectural notes for AI agents working in `terminal/`. This file
is intentionally dense; it assumes you already read the user-facing
[README.md](README.md).

## TL;DR for any change

1. **Don't change the data model invariants** (see `## Invariants`)
   without updating both the Jest tests **and** the Playwright
   rendering tests.
2. **Run both test layers** before declaring done:
   ```
   npm test         # 589 jest tests (engine)
   npm run test:render   # 43 playwright tests (canvas pixels)
   ```
3. **If you regenerate ground truth**, expect *only* the JSON files
   in `test/ground_truth/` to change. If they do change for a case
   you didn't intend to touch, you broke something else.
4. **Pyte is the oracle, but not for everything** — see `## Pyte
   divergence`. Don't try to match pyte for sequences it doesn't
   implement; use direct Jest assertions instead.

---

## Module map and data flow

```
                ┌────────────────┐
  user keys ─►  │  KeyInput      │  src/input.js
                │                │   - cursor app/normal mode
                │                │   - F1..F12 + modifiers
                │                │   - bracketed paste
                └─────┬──────────┘
                      │ term.onInput(seq)
                      ▼
                ┌────────────────┐
                │  WebSocket     │  src/websocket.js
                │  client        │   - JSON control frames out
                │                │   - binary frames in
                └─────┬──────────┘
                      │ host bytes (Uint8Array)
                      ▼
                ┌────────────────┐
                │  Parser        │  src/parser.js
                │  (Williams)    │   - emits print/execute/csi/esc/osc/dcs
                │                │   - UTF-8-clean inside string states
                └─────┬──────────┘
                      │ callbacks (per byte / per dispatch)
                      ▼
                ┌────────────────┐
                │  Terminal      │  src/terminal.js
                │                │   - SGR (calls palette helpers)
                │                │   - CSI / OSC / DCS dispatch
                │                │   - DEC private modes
                │                │   - DEC special graphics translation
                └─────┬──────────┘
                      │ screen mutations
                      ▼
                ┌────────────────┐
                │  Screen        │  src/screen.js
                │                │   - 2D cell grid (primary + alt)
                │                │   - scroll region, tabs, charsets
                │                │   - cursor with autowrap latch (cx==cols)
                │                │   - scrollback ring (primary only)
                │                │   - toFrame() → renderer-agnostic dict
                └─────┬──────────┘
                      │ frame dict (text + runs + cursor + defaults)
                      ▼
                ┌────────────────┐
                │  Renderer      │  src/renderer.js
                │                │   - canvas, DPR-scaled transform
                │                │   - geometric box-drawing
                │                │   - sixel overlay (integer-scale)
                │                │   - cursor styles + blink
                └────────────────┘

Side channels:
  Terminal → onSixel(payload)   → sixel.js → renderer.sixels
  Terminal → onTitle / onBell / onHyperlink / onResponse
```

---

## Source-file reference

### `src/parser.js`

Implements [Paul Williams' DEC ANSI state machine](https://vt100.net/emu/dec_ansi_parser).
Pure functional over bytes; emits structured events to handler
callbacks. **Owns no terminal state.**

Public API: `new Parser(handlers)`, `parse(bytes)`, `parseString(s)`,
`parseBytes(byteStr)`, `reset()`.

Key implementation notes:
- The state machine matches Williams' diagram exactly **except for
  one deliberate deviation**: 8-bit C1 controls (0x80–0x9F) are only
  honored in `GROUND`. Inside `OSC_STRING`, `DCS_PASSTHROUGH`, or
  `SOS_PM_APC_STRING` they're treated as data bytes. This is required
  for UTF-8-safe OSC payloads (continuation bytes 0x80–0xBF would
  otherwise trigger random C1 state transitions). xterm and foot do
  the same.
- Multi-byte UTF-8 is assembled in `_feedByte` before the FSM sees
  the byte — only in `GROUND` state. Inside `OSC_STRING` we hold raw
  bytes in `_oscBuf` (Latin-1) and TextDecoder them on `_oscEnd` if
  any high bytes were seen. This is critical for emoji in OSC titles.
- Empty CSI parameters: an empty whole param-group is `[]` (no `0`
  filler); an empty sub-param between two `:` separators emits `0`
  (ISO 8613-6).
- `MAX_PARAMS = 32`, `MAX_INTERMEDIATES = 2`, `MAX_OSC_LEN = 1 MiB`,
  `MAX_PARAM = 16383` (xterm cap).

Callback shape:
```js
new Parser({
  print:        (codepoint) => {},
  execute:      (byte) => {},
  escDispatch:  (intermediates: number[], final: number) => {},
  csiDispatch:  (params: number[][], intermediates: number[], final: number) => {},
  oscDispatch:  (payload: string) => {},   // already UTF-8 decoded
  dcsHook:      (params, intermediates, final) => {},
  dcsPut:       (byte) => {},
  dcsUnhook:    () => {},
});
```

`params` is an array of arrays: each outer entry is a parameter,
each inner entry is a sub-parameter (split on `:`). Most commands
only look at `params[i][0]`.

### `src/screen.js`

The cell grid. **Renderer-agnostic.** Has no notion of pixels.

Cell shape:
```js
{ ch: codepoint, w: width (1|2), fg, bg, flags }
```

Width-2 cells are followed by a continuation cell with `w === 0`.
The `flags` bitfield: `FLAG.BOLD | DIM | ITALIC | UNDERLINE | BLINK
| REVERSE | INVISIBLE | STRIKE`.

Colours are integers:
- `< 0`: special — `DEFAULT_FG_INDEX = -1`, `DEFAULT_BG_INDEX = -2`.
- `0..255`: 256-color palette index.
- `TRUE_FLAG | rgb24`: truecolor (high bit set).

`toFrame()` walks the visible buffer and emits the renderer-agnostic
frame dict:
```js
{
  rows, cols,
  cursor: { row, col, visible },
  defaultFg, defaultBg,                        // 6-char hex
  lines: [ { text, runs: [{n, fg, bg, b?, i?, u?, s?}] } ],
}
```

Run merging: consecutive cells with the same `(fg, bg, flags)` are
emitted as one run. Reverse video swaps fg/bg in the frame, not in
the model. Padding spaces are emitted on the right to make `text`
exactly `cols` wide (matches pyte).

### `src/palette.js`

ANSI 16 / xterm 256 / truecolor resolution. Mutable runtime palette
for OSC 4. Exports `resolveColor(value, isFg)` → 6-char hex string
(no `#`), `parseSgrColor(params, idx)` for `38/48; …` extended SGR.

### `src/terminal.js`

Wires `Parser` to `Screen` and owns all dispatch logic.

Public API:
- `new Terminal({ rows, cols, scrollback, pyteCompat })`
- `write(data)`, `writeBytes(byteStr)`, `resize(rows, cols)`, `reset()`
- `toFrame()` — delegates to screen.
- Callbacks: `onResponse, onTitle, onBell, onHyperlink, onSixel`.

`pyteCompat: true` disables DEC special-graphics translation in
`_print` so model bytes match pyte exactly (used by ground-truth
tests). All other behaviour is identical.

Common gotchas when editing this file:
- `_csiDispatch` is a big switch on `final` byte. If you add a new
  case, *return* — many cases fall through bugs if you don't.
- DECSCUSR (`CSI Ps SP q`) has intermediate `0x20`; it must be
  handled **inside** the `case 0x71:` block (early return otherwise
  skips it).
- DEC private modes are dispatched separately via `_decSet`; ANSI
  modes via `_smRm`. Don't mix.
- Cursor-position-style commands (`CUP/HVP`) and column commands
  (`CHA/HPA`) take 1-based parameters from the wire and convert to
  0-based internally with `arg(i, default) - 1`.

### `src/sixel.js`

DCS sixel decoder. Reads payload bytes (excluding the `\x1bP` and
`\x1b\\` envelope), emits an HTMLCanvasElement (or OffscreenCanvas
in Node).

Supported:
- Color definitions `#N;2;r;g;b` (RGB 0..100) and `#N;1;h;l;s` (HLS).
- Run-length `!N<sixel>`.
- Graphics CR `$` (overlay next colour at same band).
- Graphics LF `-` (advance band).
- Raster attrs `"Pan;Pad;Ph;Pv`.
- DCS header `Ps1` for pixel aspect: 0,1,5,6→2:1; 2→5:1; 3,4→3:1;
  7,8,9→1:1. Raster attrs override Ps1.
- VT340 16-color default palette.

**Defensive**: an `\x1b` byte mid-stream is treated as early
termination. Without this, a caller that forgets to strip `\x1b\\`
could feed the `\` (0x5c) byte to the decoder, which is in the sixel
data range and would corrupt the image.

### `src/renderer.js`

Canvas painter. **DPR-aware.**

```
canvas.width  = cssWidth  × dpr     (device pixels)
canvas.style.width  = cssWidth      (CSS pixels)
ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
```

So most drawing happens in *logical CSS pixels*, the canvas
internally scales up to device pixels. Text gets crisp anti-aliasing
at full device resolution.

**Box-drawing (`BOX_DRAW` table)**: every codepoint we know how to
draw geometrically (single + double, all crosses, tees, corners) is
stroked with half-pixel-snapped coordinates and `lineWidth >= 1`. The
font glyph is NOT drawn — guarantees clean cell-edge joins.

**Sixel compositing (`_blitSixel`)**: temporarily resets the canvas
transform to identity so we can blit at exact device-pixel positions
with integer-only scaling. `imageSmoothingEnabled = false` → crisp
N×N pixel blocks at any zoom. Restores `setTransform(dpr,…)` after.

```js
scale = sixelScale × dpr                  // device px per sixel px
dx, dy = (padding + col×cellW, padding + row×cellH) × dpr
dw, dh = bitmap.width × scale, bitmap.height × scale
```

`sixels` is a plain array of `{row, col, bitmap}`. The terminal owns
nothing here — `main.js` pushes onto it from `term.onSixel`.

### `src/input.js`

`KeyboardEvent` → host bytes. Reads the terminal's mode flags
(`appCursorKeys`, `bracketedPaste`) to encode appropriately.

Modifier-code encoding follows xterm:
`mod = 1 + shift + 2*alt + 4*ctrl + 8*meta`.

Special handling:
- `Backspace`: DEL (`\x7f`) by default, BS (`\x08`) with Ctrl. xterm
  default.
- `Tab`/`Shift-Tab`: `\t` / `\x1b[Z`.
- Ctrl-letter → control byte (subtract 0x60).
- Alt-letter → `ESC` + letter.

### `src/main.js`

Demo wiring + auto-fit + zoom + WebSocket connect. Not a library.

Key state:
- `currentFontPx` — single source of truth for zoom level.
- `ren.sixelScale` — derived from `currentFontPx / DEFAULT_FONT_PX`.
- `sock` — the WebSocket, lazily created.

Order matters in `setFontSize`:
```js
ren.sixelScale = ...;     // FIRST — _measure uses this
ren.setFontSize(px);      // re-measures with new step
fitToPane();              // then resize buffer + redraw
```

`fitToPane()` is called from a `ResizeObserver` on `<main>` and from
`window.onresize`. It computes the largest `(rows, cols)` that fit
the pane, resizes the terminal, and updates the status indicator.

### `bridge/proxy.py`

Plain `asyncio` + `websockets` server.

Class hierarchy:
```
PtyBase   (abstract)
├─ WindowsPty   (pywinpty)
└─ UnixPty      (stdlib pty + fcntl)
```

Each session spawns a reader thread (PTY reads are blocking in
pywinpty) and uses `loop.call_soon_threadsafe` to push chunks into
an asyncio Queue. Two coroutines pump that queue out the WebSocket
and feed input back into the PTY.

Wire protocol — client → server (JSON text frames):
```json
{"type":"input",  "data":"…"}
{"type":"resize", "rows":24,"cols":80}
```
Server → client: raw binary frames (PTY output), plus
`{"type":"exit","code":N}` when the child dies.

### `serve.py`

Trivial static file server with `Cache-Control: no-store` so a
browser reload always picks up edited modules. The default `python
-m http.server` does not do this and caused real confusion early on
when JS file changes weren't visible without a hard refresh.

---

## Invariants

Don't break these without updating tests.

### Parser

- **Inside `OSC_STRING`, `DCS_PASSTHROUGH`, `SOS_PM_APC_STRING`**: 8-bit
  C1 controls (0x80–0x9F) are *data*, not state changes. Only 0x1B
  (ESC) and 0x9C (C1 ST) terminate string states.
- **`_csiDispatch` and `_dcsHookStart`** emit raw param arrays. Empty
  param groups stay `[]`; sub-param defaults to `0` only between
  explicit `:` separators.
- **`reset()`** must restore every field set in the constructor.

### Screen

- **Autowrap latch is `cx === cols`**, not a separate boolean. This
  matches pyte and xterm semantics; many tests sample `cursor.col`
  and expect `cols` (one past the right edge) when at the latch.
- **`cursorLeft` / `bs`** must step off the latch first (subtract 1
  from `cx` if it equals `cols`) *then* apply the count. pyte does
  this; not doing it breaks readline editing.
- **`setCursor` under `originMode`** must no-op if the target row is
  outside the scroll region. Otherwise programs that use origin mode
  get scrolling artefacts. Matches pyte's `cursor_position` source.
- **`enterAlt`** clears the alt buffer but does NOT move the cursor.
  1049 saves the cursor; 47 / 1047 do not.
- **`toFrame()`** emits exactly `cols` chars per line (pad with
  spaces) so the frame dict matches pyte's `display`.

### Terminal

- **DECSTBM with no args** (`CSI r`) resets the scroll region but
  does NOT move the cursor. pyte behaviour; many ground-truth tests
  rely on it.
- **DEC private mode 6 (DECOM)** homes the cursor on set/reset to
  region-top. Per VT520 + pyte.
- **`ESC c` (RIS)** must reset palette, charsets, modes, cursor,
  buffers, and call `parser.reset()`. Easy to forget the parser.

### Renderer

- **Sixel compositing** must reset transform to identity, disable
  smoothing, blit at integer-scaled positions, then restore the
  dpr-scaled transform. Anything else makes sixels blurry at high
  DPR or high zoom.
- **`cellH` is always a multiple of `6 × sixelScale`** so sixel
  bands tile cleanly into character rows. `_measure()` enforces this.

---

## Pyte divergence

We have a Jest ground-truth comparison against pyte for ~493
sequences. The following pyte limitations are worked around by
removing the divergent cases from the pyte oracle and adding direct
Jest assertions instead.

| Sequence       | Pyte                           | vt-term         |
| -------------- | ------------------------------ | --------------- |
| `CSI s` / `u`  | Not implemented                | SCOSC / SCORC   |
| `CSI Ps S`     | Not implemented                | SU              |
| `CSI Ps T`     | Not implemented                | SD              |
| `CSI Ps I`     | Not implemented                | CHT             |
| `CSI Ps Z`     | Not implemented                | CBT             |
| `CSI Ps \``    | Not implemented                | HPA             |
| `CSI Ps b`     | Not implemented                | REP             |
| `?47/1047/1048/1049` | No-op                    | Full alt-buffer |
| `ESC ( 0`      | Untranslated in display        | Translated      |
| `DL` with sparse buffer | Source row sparse → dest unchanged | Always overwrite |

**Rule of thumb**: when writing a new ground-truth test, if pyte's
result doesn't match what xterm would do, *drop the case from the
pyte oracle* and add a direct Jest assertion in the relevant unit
test file (`modes.test.js`, `alt_screen.test.js`, etc.).

---

## Test strategy in detail

### Where each kind of test lives

| Concern                            | Test file                       | Layer       |
| ---------------------------------- | ------------------------------- | ----------- |
| Parser state machine               | `test/parser.test.js`           | Jest        |
| Engine behaviour vs pyte           | `test/terminal.test.js`         | Jest + pyte |
| Sixel decoder (synthetic)          | `test/sixel.test.js`            | Jest        |
| Sixel decoder (real fixtures)      | `test/sixel_fixtures.test.js`   | Jest        |
| Keyboard encoding                  | `test/input.test.js`            | Jest        |
| OSC callbacks                      | `test/osc.test.js`              | Jest        |
| Private/ANSI modes (pyte-divergent)| `test/modes.test.js`            | Jest        |
| Alt screen isolation               | `test/alt_screen.test.js`       | Jest        |
| Screen resize                      | `test/resize.test.js`           | Jest        |
| Canvas pixel correctness           | `test/render.pw.test.js`        | Playwright  |
| End-to-end demo buttons            | `test/demo.pw.test.js`          | Playwright  |
| Cellh/zoom invariants              | `test/bulk_render.pw.test.js`   | Playwright  |

### Adding a new ground-truth case

1. Pick the relevant suite in `test/cases/test_*.py` (or add a new
   one). Each `CASES[id] = "raw byte stream"`.
2. `python test/gen_ground_truth.py` rewrites the JSON for changed
   suites.
3. `npm test` runs the comparison.

If your test fails because pyte and our impl disagree:
- Probe pyte directly with `python -c "import pyte; ..."` to
  understand its semantics.
- Decide whose behaviour is "right" (usually xterm, occasionally
  pyte).
- If we're wrong, fix it. If pyte's wrong, **remove the case from
  the .py file** and add a direct Jest test in the matching
  divergence file.

### Adding a Playwright pixel test

1. Use `test/render_harness.html` for low-level isolated tests
   (uses `window.vt` API).
2. Use the live `index.html` (via `clickAndSettle`) for end-to-end
   demo button tests.
3. Always hide the cursor before sampling pixels:
   ```js
   await page.evaluate(() => {
     window.term.screen.cursorVisible = false;
     window.ren.draw(window.term.toFrame());
   });
   ```
4. For canvas sampling, prefer `cellInkRatio` or `brightestIn` (max
   over a small box) over single-pixel sampling — anti-aliasing.

### Adding a new sixel fixture

1. Drop the `.six` file into `test/fixtures/sixel/`.
2. Add an entry to `test/sixel_fixtures.test.js` asserting the
   decoded dimensions / pixel count.
3. Optionally add a demo button in `index.html` + `main.js` and an
   end-to-end test in `test/demo.pw.test.js`.

---

## Common pitfalls

1. **Empty CSI params**: `CSI H` is `[[]]` (one empty group), not
   `[[0]]`. Many CSI defaults are `1`, not `0` — handle via
   `arg(i, 1)` helper in `_csiDispatch`.

2. **UTF-8 in OSC payloads**: if you touch the parser's string-state
   handling, run `test/osc.test.js`'s `multi-line / unicode title`
   case. Easy to break.

3. **Sixel + cursor advance**: each sixel implicitly advances the
   cursor (xterm "sixel scrolling"). `main.js`'s `term.onSixel`
   handler does this. If you remove it, all sixel demos will
   stack on top of each other.

4. **DPR + sixel scaling**: sixels are rendered at
   `sixelScale × dpr` device pixels per sixel pixel. Always with
   `imageSmoothingEnabled = false`. The transform reset → blit →
   transform restore sequence in `_blitSixel` is the *correct
   order*; don't simplify it.

5. **Ground-truth test names**: case IDs are part of the test
   identity. Renaming a case is a destructive change for `git diff`
   on the JSON.

6. **Pyte version**: tests pass against `pyte` 0.8.x (whatever ships
   with `pip install pyte`). If you upgrade pyte and behaviour
   shifts, ground truth needs regenerating.

7. **Sparse buffers in pyte**: pyte stores rows as a sparse `{col:
   cell}` dict and treats missing cells as default. Several edge
   cases (especially DL with empty source rows, ICH at edge) have
   pyte returning "no change" where we sensibly clear; see the
   `pyte-divergent` notes in `test/cases/test_insert_delete_bulk.py`.

8. **Don't add capture/zoom/highdpi `.mjs` scripts to git unless
   they're useful long-term** — they're development aids and live
   in `test/` next to the real tests. Treat them as scratch unless
   they earn their keep.

---

## Useful one-liners

```powershell
# Probe what pyte does for a sequence (Windows PowerShell)
python -c "import pyte; s=pyte.Screen(20,4); st=pyte.Stream(s); st.feed('\x1b[5;3HX'); print(s.cursor.x, s.cursor.y); print(s.display)"

# Decode a .six file via our decoder and dump stats
node --experimental-vm-modules -e "import('fs').then(async f=>{const{SixelDecoder}=await import('./src/sixel.js');const buf=f.readFileSync('test/fixtures/sixel/snake.six');let b=buf.toString('latin1');b=b.slice(b.indexOf('\x1bP')+2,b.lastIndexOf('\x1b\\\\'));const d=new SixelDecoder();d.decode(b);console.log(d.maxX+'x'+d.maxY,'pixels='+d.pixels.length)})"

# Run a single ground-truth case
python test/gen_ground_truth.py --suite csi_cursor --case cup_3_5

# Run a single jest test
npm test -- -t "DECSCUSR"

# Capture all demo screenshots
npm run capture
```

---

## Future work

Roughly in priority order:

1. **Mouse encoding (send side)** — parser already accepts the
   DECSET codes; `KeyInput` needs to emit `CSI M …` or `CSI < …`
   sequences.
2. **DECCOLM (132-column mode)** — currently ignored.
3. **Scrollback rendering** — model holds it, renderer doesn't paint
   it; add wheel/PageUp scroll into scrollback.
4. **Sixel images that scroll with text** — currently anchored in
   place; on real xterm they're tied to the underlying cells.
5. **Image protocols** — Kitty graphics, iTerm2 inline images. The
   DCS/OSC dispatcher hooks are in place; just need decoders.
6. **OSC 52 clipboard** — read/write via `navigator.clipboard`.
7. **Hand-written goldens** for the pyte-divergent sequences (CBT,
   CHT, HPA, SU, SD, etc.) so we can lock down expected output
   independently of pyte.

When implementing any of these, keep the two-layer testing pattern:
direct Jest assertions for engine behaviour, Playwright canvas
pixels for visible behaviour.
