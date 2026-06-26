/**
 * Demo wiring: builds the terminal, renderer, input, and hooks up the
 * feature-demo buttons + WebSocket "connect to shell" button.
 */

import { Terminal } from './terminal.js';
import { Renderer, CURSOR_STYLE } from './renderer.js';
import { KeyInput } from './input.js';
import { TerminalSocket } from './websocket.js';
import { SixelDecoder } from './sixel.js';

const DEFAULT_FONT_PX = 16;
const MIN_FONT_PX = 8;
const MAX_FONT_PX = 40;
const MIN_COLS = 20;
const MIN_ROWS = 8;

const canvas = document.getElementById('term');
const term = new Terminal({ rows: 24, cols: 80, scrollback: 2000 });
const ren = new Renderer(canvas, { fontSize: DEFAULT_FONT_PX, padding: 6 });
const ki = new KeyInput(term);

let currentFontPx = DEFAULT_FONT_PX;

function redraw() { ren.draw(term.toFrame()); }

/** Pick the largest (rows × cols) that fits inside the <main> pane at
 *  the current cell size, and apply it to the terminal + renderer. */
function fitToPane() {
  const mainEl = document.querySelector('main');
  const cs    = getComputedStyle(mainEl);
  const padX  = parseFloat(cs.paddingLeft) + parseFloat(cs.paddingRight);
  const padY  = parseFloat(cs.paddingTop)  + parseFloat(cs.paddingBottom);
  const availW = mainEl.clientWidth  - padX;
  const availH = mainEl.clientHeight - padY;
  const inner = ren.padding * 2;
  const cols = Math.max(MIN_COLS, Math.floor((availW - inner) / ren.cellW));
  const rows = Math.max(MIN_ROWS, Math.floor((availH - inner) / ren.cellH));

  if (rows !== term.screen.rows || cols !== term.screen.cols) {
    term.resize(rows, cols);
    if (sock) sock.resize(rows, cols);
  }
  redraw();
  updateStatus();
}

function setFontSize(px) {
  px = Math.max(MIN_FONT_PX, Math.min(MAX_FONT_PX, px | 0));
  if (px === currentFontPx) return;
  currentFontPx = px;
  // Sixel scale must be set *before* the renderer re-measures, since
  // cellH is constrained to a multiple of (6 × sixelScale) so sixel
  // bands tile cleanly with character rows.
  ren.sixelScale = Math.max(1, Math.round(px / DEFAULT_FONT_PX));
  ren.setFontSize(px);
  fitToPane();
}

function updateStatus() {
  const s = document.getElementById('size-info');
  if (s) {
    const bandsPerRow = ren.cellH / (6 * ren.sixelScale);
    s.textContent = `${term.screen.cols}×${term.screen.rows}  ·  ${currentFontPx}px  ·  cell ${ren.cellW}×${ren.cellH}  ·  ${bandsPerRow} sixel band${bandsPerRow !== 1 ? 's' : ''}/row`;
  }
}

// React to title changes
term.onTitle = (t) => { document.title = t ? `${t} – vt-term` : 'vt-term'; };
term.onBell  = () => { canvas.classList.add('bell'); setTimeout(() => canvas.classList.remove('bell'), 200); };

// Sixel: decode the DCS payload, place a bitmap anchored at the
// terminal cursor position, then advance the cursor past the bottom
// of the image (xterm "sixel scrolling" default behavior).
term.onSixel = (payload) => {
  try {
    const decoder = new SixelDecoder();
    decoder.decode(payload);
    const bmp = decoder.toCanvas();
    const sx = {
      row: term.screen.cy,
      col: term.screen.cx,
      width: bmp.width,
      height: bmp.height,
      bitmap: bmp,
    };
    ren.sixels.push(sx);

    // Sixel scrolling — advance cursor past image, snap to column 0.
    const rowsCovered = Math.ceil(bmp.height / ren.cellH);
    term.screen.cx = 0;
    for (let i = 0; i < rowsCovered; i++) term.screen.lf();

    console.log('[sixel] decoded', decoder.pixels.length, 'pixels',
                'into', bmp.width + 'x' + bmp.height, 'bitmap at row',
                sx.row, 'col', sx.col, '; cursor advanced',
                rowsCovered, 'rows');
  } catch (err) {
    console.error('[sixel] decode failed', err);
  }
};

// Keyboard
canvas.tabIndex = 0;
// Initial focus: do it both immediately and after first frame paints,
// since some browsers ignore focus calls during initial parsing.
canvas.focus();
window.addEventListener('load', () => canvas.focus());
// If the user clicks anywhere on the page chrome, snap focus back so
// keystrokes always land in the terminal.
document.addEventListener('click', (e) => {
  // Don't steal focus from inputs (e.g. the WS URL field).
  if (e.target.tagName === 'INPUT' || e.target.tagName === 'BUTTON') return;
  canvas.focus();
});
canvas.addEventListener('keydown', (e) => { ki.handle(e); redraw(); });
canvas.addEventListener('paste',   (e) => { ki.paste(e); redraw(); });

// Echo locally when not connected
term.onInput = (s) => {
  if (sock) { sock.send(s); return; }
  // Local echo: most useful for the "press keys, see output" demo.
  // Convert CR to CRLF so Enter actually wraps to a new line.
  const echoed = s.replace(/\r/g, '\r\n');
  term.write(echoed);
  redraw();
};

// ── Demo buttons ──────────────────────────────────────────────────

function btn(id, fn) { document.getElementById(id).addEventListener('click', () => { fn(); redraw(); canvas.focus(); }); }

btn('demo-reset', () => { term.reset(); ren.sixels.length = 0; });
btn('demo-hello', () => term.write('Hello, terminal!\r\n'));
btn('demo-colors', () => {
  let out = '\r\n  ANSI 16:\r\n';
  for (let i = 0; i < 16; i++) {
    out += `\x1b[48;5;${i}m  ${i.toString().padStart(2)}  \x1b[0m`;
    if (i === 7) out += '\r\n';
  }
  out += '\r\n\r\n  256-color cube:\r\n';
  for (let r = 0; r < 6; r++) {
    out += '  ';
    for (let g = 0; g < 6; g++) {
      for (let b = 0; b < 6; b++) {
        const idx = 16 + r * 36 + g * 6 + b;
        out += `\x1b[48;5;${idx}m  \x1b[0m`;
      }
      out += ' ';
    }
    out += '\r\n';
  }
  out += '\r\n  Greys:\r\n  ';
  for (let i = 232; i < 256; i++) out += `\x1b[48;5;${i}m  \x1b[0m`;
  out += '\r\n\r\n  Truecolor gradient:\r\n  ';
  for (let i = 0; i < 60; i++) {
    const r = Math.round(255 * i / 59), b = 255 - r;
    out += `\x1b[48;2;${r};0;${b}m \x1b[0m`;
  }
  out += '\r\n';
  term.write(out);
});

btn('demo-sgr', () => {
  term.write(
    '\r\n  \x1b[1mbold\x1b[0m  \x1b[3mitalic\x1b[0m  \x1b[4munderline\x1b[0m  ' +
    '\x1b[9mstrike\x1b[0m  \x1b[7mreverse\x1b[0m  \x1b[1;33;44mbold-yellow-on-blue\x1b[0m\r\n'
  );
});

btn('demo-cursor', () => {
  // Cycle styles
  const order = [
    CURSOR_STYLE.BLOCK_BLINK, CURSOR_STYLE.BLOCK_STEADY,
    CURSOR_STYLE.UNDER_BLINK, CURSOR_STYLE.UNDER_STEADY,
    CURSOR_STYLE.BAR_BLINK,   CURSOR_STYLE.BAR_STEADY,
  ];
  const cur = ren.cursorStyle;
  const idx = order.indexOf(cur);
  ren.cursorStyle = order[(idx + 1) % order.length];
});

btn('demo-alt', () => {
  term.write('\x1b[?1049h');     // enter alt
  term.write('\x1b[H\x1b[2J');   // clear
  term.write('  This is the alternate screen.\r\n');
  term.write('  Click "Leave alt screen" to return.\r\n');
});

btn('demo-leave-alt', () => term.write('\x1b[?1049l'));

btn('demo-boxes', () => {
  // DEC line drawing.  We have to switch *back* to ASCII (\x1b(B)
  // before any plain text, otherwise letters get translated as DEC
  // special graphics glyphs (h→␤, e→␊, l→┌, …) which look like tiny
  // "NL/LF/CR" subscript labels in most fonts.
  const G = '\x1b(0';   // select DEC special graphics for G0
  const A = '\x1b(B';   // back to ASCII
  term.write('\r\n');
  // Top border: ┌──────────────┐
  term.write(G + 'l' + 'q'.repeat(14) + 'k' + A + '\r\n');
  // Middle row with text inside the bars
  term.write(G + 'x' + A + ' hello world  ' + G + 'x' + A + '\r\n');
  // Cross divider: ├──────────────┤
  term.write(G + 't' + 'q'.repeat(14) + 'u' + A + '\r\n');
  // Another text row
  term.write(G + 'x' + A + ' abcdefghijkl ' + G + 'x' + A + '\r\n');
  // Bottom border: └──────────────┘
  term.write(G + 'm' + 'q'.repeat(14) + 'j' + A + '\r\n');
});

btn('demo-wrap', () => {
  term.write('\r\nLong line: ');
  for (let i = 0; i < 10; i++) term.write('abcdefghij');
  term.write('\r\n');
});

btn('demo-scroll-region', () => {
  term.write('\x1b[H\x1b[2J');
  for (let i = 1; i <= term.screen.rows; i++) term.write(`line ${i}\r\n`);
  term.write('\x1b[5;15r');   // scroll region rows 5..15
  term.write('\x1b[5H');       // go to row 5
  for (let i = 0; i < 20; i++) term.write(`scrolled ${i}\r\n`);
  term.write('\x1b[r');         // reset region
});

// ── Sixel demos ────────────────────────────────────────────────────

function dcs(payload) { return '\x1bP' + payload + '\x1b\\'; }

btn('demo-sixel-flag', () => {
  // Three horizontal bands: red, white, blue.  Width 60, height 18 (3 bands of 6).
  // Use the standard 6 colors per the VT340 palette + a custom white.
  // #N;2;r;g;b defines RGB (each 0..100).
  // Sixel data char = 0x3f + 6-bit column mask; ~ = all 6 pixels on.
  const W = 60;
  const tilde = '~'.repeat(W);                       // all six rows on
  let s = 'q';
  s += '#1;2;100;15;15';      // color 1 = red
  s += '#2;2;100;100;100';    // color 2 = white
  s += '#3;2;15;30;100';      // color 3 = blue
  s += '#1' + tilde + '-';   // red band
  s += '#2' + tilde + '-';   // white band
  s += '#3' + tilde;          // blue band
  term.write(dcs(s));
  term.write('\r\n');
});

btn('demo-sixel-gradient', () => {
  // 36 colored vertical stripes across a single band.
  let s = 'q';
  for (let i = 0; i < 36; i++) {
    const r = Math.round(100 * Math.max(0, 1 - Math.abs(i - 6) / 10));
    const g = Math.round(100 * Math.max(0, 1 - Math.abs(i - 18) / 10));
    const b = Math.round(100 * Math.max(0, 1 - Math.abs(i - 30) / 10));
    s += `#${i + 10};2;${r};${g};${b}`;
  }
  // Three bands tall for visibility (18 px high).
  for (let band = 0; band < 3; band++) {
    for (let i = 0; i < 36; i++) {
      s += `#${i + 10}!4~`;     // 4 cols wide, all 6 pixels on
    }
    s += '-';
  }
  term.write(dcs(s));
  term.write('\r\n');
});

btn('demo-sixel-pattern', () => {
  // Clean smooth-shaded sphere — 120 wide × 120 tall (20 sixel bands).
  // We use 64 distinct gray-shade colors so the sphere looks lit.
  const W = 120, H = 120;
  const BANDS = H / 6;
  const cxF = W / 2, cyF = H / 2, R = W / 2 - 4;

  let s = 'q"1;1;' + W + ';' + H;
  // Palette: 64 grey levels in colors 16..79
  for (let i = 0; i < 64; i++) {
    const v = Math.round(i / 63 * 100);   // 0..100 (sixel scale)
    s += `#${16 + i};2;${v};${v};${v}`;
  }
  // For each (band, color), build a vertical-mask string of W chars.
  // We bucket pixels by colour so we can emit all the column data for
  // one colour with one `#N`-then-data block per band.
  for (let band = 0; band < BANDS; band++) {
    // colorIdx → array of 6-bit masks (one per column)
    const byColor = new Map();
    for (let col = 0; col < W; col++) {
      for (let row = 0; row < 6; row++) {
        const y = band * 6 + row;
        const dx = col - cxF, dy = y - cyF;
        const d  = Math.sqrt(dx * dx + dy * dy);
        if (d > R) continue;
        // Lighting: surface normal of sphere with light from upper-left.
        const z = Math.sqrt(Math.max(0, R * R - d * d));
        const nx = dx / R, ny = dy / R, nz = z / R;
        const lx = -0.5, ly = -0.6, lz = 0.6;
        const len = Math.sqrt(lx*lx + ly*ly + lz*lz);
        let dot  = (nx*lx + ny*ly + nz*lz) / len;
        if (dot < 0) dot = 0;
        const idx = 16 + Math.min(63, Math.max(0, Math.round(dot * 63)));
        let masks = byColor.get(idx);
        if (!masks) { masks = new Array(W).fill(0); byColor.set(idx, masks); }
        masks[col] |= (1 << row);
      }
    }
    // Emit each colour's contribution for this band, using $ to rewind
    // x between colours.  Use ! repeat to compress runs.
    let first = true;
    for (const [color, masks] of byColor) {
      if (!first) s += '$';   // graphics CR — overlay next colour in same band
      first = false;
      s += `#${color}`;
      let i = 0;
      while (i < W) {
        let run = 1;
        while (i + run < W && masks[i + run] === masks[i]) run++;
        const ch = String.fromCharCode(0x3f + masks[i]);
        if (run > 3) s += `!${run}${ch}`;
        else         s += ch.repeat(run);
        i += run;
      }
    }
    s += '-';   // graphics LF — advance to next band
  }
  term.write(dcs(s));
  term.write('\r\n');
});

btn('demo-sixel-clear', () => {
  ren.sixels.length = 0;
});

// ── Load a real-world sixel fixture from disk ────────────────────

async function loadFixture(filename) {
  const resp = await fetch(`test/fixtures/sixel/${filename}`);
  if (!resp.ok) { console.error('fetch failed:', resp.status); return; }
  const buf = new Uint8Array(await resp.arrayBuffer());
  // The .six files contain the full ESC P … ESC \ envelope; just
  // hand them straight to the terminal and let the parser do its job.
  term.write(buf);
}

btn('demo-sixel-snake', () => loadFixture('snake.six').then(redraw));
btn('demo-sixel-me',    () => loadFixture('me.six').then(redraw));
btn('demo-sixel-3color',() => loadFixture('3-sixels.six').then(redraw));

// ── Zoom controls ──────────────────────────────────────────────────

btn('zoom-in',    () => setFontSize(currentFontPx + 2));
btn('zoom-out',   () => setFontSize(currentFontPx - 2));
btn('zoom-reset', () => setFontSize(DEFAULT_FONT_PX));

// Keyboard shortcuts (Ctrl-+, Ctrl--, Ctrl-0).  We capture these
// before they reach the canvas key handler so they never get sent
// to the connected shell.  Some browsers also intercept these for
// page-zoom; we preventDefault to override.
document.addEventListener('keydown', (e) => {
  if (!(e.ctrlKey || e.metaKey) || e.altKey || e.shiftKey) return;
  if (e.key === '=' || e.key === '+') {
    setFontSize(currentFontPx + 2); e.preventDefault();
  } else if (e.key === '-' || e.key === '_') {
    setFontSize(currentFontPx - 2); e.preventDefault();
  } else if (e.key === '0') {
    setFontSize(DEFAULT_FONT_PX); e.preventDefault();
  }
}, true);

// ── WebSocket connect ──────────────────────────────────────────────

let sock = null;
const connectBtn = document.getElementById('connect');
const statusEl = document.getElementById('status');

function setStatus(s, cls) {
  statusEl.textContent = s;
  statusEl.className = 'status ' + (cls || '');
}

connectBtn.addEventListener('click', () => {
  if (sock) { sock.close(); sock = null; setStatus('disconnected', 'off'); connectBtn.textContent = 'Connect'; canvas.focus(); return; }
  const url = document.getElementById('ws-url').value || 'ws://localhost:7681';
  setStatus('connecting…', 'pending');
  sock = new TerminalSocket(url);
  sock.onOpen = () => {
    setStatus('connected', 'on');
    connectBtn.textContent = 'Disconnect';
    sock.resize(term.screen.rows, term.screen.cols);
    canvas.focus();
  };
  sock.onClose = () => { setStatus('disconnected', 'off'); connectBtn.textContent = 'Connect'; };
  sock.onData = (bytes) => { term.write(bytes); redraw(); };
  sock.onExit = (code) => { term.write(`\r\n[shell exited ${code}]\r\n`); redraw(); };
});

// Wire the host-response back over the socket (DSR, DA, cursor reports)
term.onResponse = (s) => { if (sock) sock.send(s); };

// ── Auto-fit to the <main> pane ────────────────────────────────────

// Watch for any pane resize (window or layout change).  Using
// ResizeObserver instead of just `resize` so changes to the sidebar
// width or font metrics are picked up too.
const _ro = new ResizeObserver(() => fitToPane());
_ro.observe(document.querySelector('main'));
window.addEventListener('resize', fitToPane);

// Initial fit + paint
fitToPane();

// Periodic redraw (cursor blink already self-paints, but other state
// changes from async data won't until we redraw).  Cheap.
setInterval(redraw, 100);

// Expose for console hacking
window.term = term;
window.ren  = ren;
window.setFontSize = setFontSize;
