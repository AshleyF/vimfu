/**
 * Screen — the cell grid, cursor, scroll region, alt buffer, tab stops.
 *
 * A cell is a small object so we can resize easily; the working set is the
 * visible rows × cols only (scrollback is a separate ring buffer).
 *
 * Cell shape:
 *   { ch: codepoint, w: width (1|2), fg, bg, flags }
 *
 * Flags bitfield:
 *   1 = bold, 2 = dim, 4 = italic, 8 = underline,
 *   16 = blink, 32 = reverse, 64 = invisible, 128 = strikethrough
 */

import {
  DEFAULT_FG_INDEX, DEFAULT_BG_INDEX, DEFAULT_FG_HEX, DEFAULT_BG_HEX,
  resolveColor,
} from './palette.js';

export const FLAG = Object.freeze({
  BOLD:      1 << 0,
  DIM:       1 << 1,
  ITALIC:    1 << 2,
  UNDERLINE: 1 << 3,
  BLINK:     1 << 4,
  REVERSE:   1 << 5,
  INVISIBLE: 1 << 6,
  STRIKE:    1 << 7,
});

export function defaultCell() {
  return { ch: 0x20, w: 1, fg: DEFAULT_FG_INDEX, bg: DEFAULT_BG_INDEX, flags: 0 };
}

function makeRow(cols) {
  const r = new Array(cols);
  for (let i = 0; i < cols; i++) r[i] = defaultCell();
  return r;
}

function copyCell(src, dst) {
  dst.ch = src.ch; dst.w = src.w; dst.fg = src.fg; dst.bg = src.bg; dst.flags = src.flags;
  return dst;
}

function resetCell(c) {
  c.ch = 0x20; c.w = 1; c.fg = DEFAULT_FG_INDEX; c.bg = DEFAULT_BG_INDEX; c.flags = 0;
}

function resetCellBgKeep(c, bg) {
  c.ch = 0x20; c.w = 1; c.fg = DEFAULT_FG_INDEX; c.bg = bg; c.flags = 0;
}

export class Screen {
  constructor(rows, cols, { scrollback = 1000 } = {}) {
    this.rows = rows;
    this.cols = cols;
    this.maxScrollback = scrollback;
    this._initBuffers();

    // Cursor
    this.cx = 0;
    this.cy = 0;
    this.savedCursor = null;

    // Cursor SGR (the "current attribute")
    this.curFg = DEFAULT_FG_INDEX;
    this.curBg = DEFAULT_BG_INDEX;
    this.curFlags = 0;

    // Scroll region (0-indexed, inclusive)
    this.scrollTop = 0;
    this.scrollBot = rows - 1;

    // Modes
    this.autoWrap = true;
    this.originMode = false;
    this.insertMode = false;
    this.reverseWrap = false;
    this.cursorVisible = true;
    this.bracketedPaste = false;
    this.appCursorKeys = false;
    this.appKeypad = false;
    this.mouseMode = 0;                  // 0=none, others reserved
    this.mouseProtocol = 0;
    this.altScreen = false;
    this.title = '';

    // Charsets — G0..G3 + GL/GR pointers. 'B'=ASCII, '0'=DEC special.
    this.charsets = ['B', 'B', 'B', 'B'];
    this.gl = 0;
    this.gr = 2;

    // Tab stops every 8 columns by default
    this._initTabs();
  }

  _initBuffers() {
    this._primary = [];
    this._alt = [];
    for (let r = 0; r < this.rows; r++) {
      this._primary.push(makeRow(this.cols));
      this._alt.push(makeRow(this.cols));
    }
    this.lines = this._primary;
    this.scrollback = [];                // primary-only history
  }

  _initTabs() {
    this.tabs = new Array(this.cols).fill(false);
    for (let i = 0; i < this.cols; i += 8) this.tabs[i] = true;
  }

  // ── Geometry ────────────────────────────────────────────────────

  resize(rows, cols) {
    if (rows === this.rows && cols === this.cols) return;
    const oldRows = this.rows, oldCols = this.cols;

    function reshape(buf) {
      // Truncate or pad rows.
      while (buf.length > rows) buf.pop();
      while (buf.length < rows) buf.push(makeRow(cols));
      // Truncate/pad columns.
      for (const row of buf) {
        while (row.length > cols) row.pop();
        while (row.length < cols) row.push(defaultCell());
      }
    }
    reshape(this._primary);
    reshape(this._alt);

    this.rows = rows;
    this.cols = cols;
    this._initTabs();
    this.scrollTop = 0;
    this.scrollBot = rows - 1;
    if (this.cx >= cols) this.cx = cols - 1;
    if (this.cy >= rows) this.cy = rows - 1;
  }

  // ── Alt screen ──────────────────────────────────────────────────

  enterAlt() {
    if (this.altScreen) return;
    this.altScreen = true;
    this.lines = this._alt;
    this.clearScreen();
  }

  leaveAlt() {
    if (!this.altScreen) return;
    this.altScreen = false;
    this.lines = this._primary;
  }

  // ── Drawing ─────────────────────────────────────────────────────

  putChar(cp) {
    const width = charWidth(cp);
    if (width === 0) return;             // combining char — TODO compose

    // pyte rule: if cursor.x == cols on entry to draw, that's the
    // autowrap latch.  If DECAWM set → CR + LF.  Else step back so the
    // next char overwrites the last column.
    if (this.cx >= this.cols) {
      if (this.autoWrap) {
        this.cx = 0;
        this._lineFeed();
      } else {
        this.cx = Math.max(0, this.cols - width);
      }
    }

    if (this.insertMode) {
      this._shiftRight(this.cy, this.cx, width);
    }

    const row = this.lines[this.cy];
    const c = row[this.cx];
    c.ch = cp; c.w = width;
    c.fg = this.curFg; c.bg = this.curBg; c.flags = this.curFlags;

    if (width === 2 && this.cx + 1 < this.cols) {
      const c2 = row[this.cx + 1];
      c2.ch = 0; c2.w = 0;               // continuation cell
      c2.fg = this.curFg; c2.bg = this.curBg; c2.flags = this.curFlags;
    }

    // Advance cursor — pyte caps at cols (one past last printable col).
    // That is the latched state; the next putChar will wrap or overwrite.
    this.cx = Math.min(this.cx + width, this.cols);
  }

  _lineFeed() {
    if (this.cy === this.scrollBot) {
      this.scrollUp(1);
    } else if (this.cy < this.rows - 1) {
      this.cy++;
    }
  }

  _shiftRight(r, x, count) {
    const row = this.lines[r];
    count = Math.max(0, Math.min(count, this.cols - x));
    for (let i = this.cols - 1; i >= x + count; i--) {
      copyCell(row[i - count], row[i]);
    }
    for (let i = x; i < x + count && i < this.cols; i++) {
      resetCellBgKeep(row[i], this.curBg);
    }
  }

  // ── Cursor motion ───────────────────────────────────────────────

  setCursor(row, col) {
    const topRow = this.originMode ? this.scrollTop : 0;
    const botRow = this.originMode ? this.scrollBot : this.rows - 1;
    // pyte rule (origin mode): if the requested line is outside the
    // scrolling region, the command is a no-op.
    if (this.originMode) {
      const tgtRow = topRow + row;
      if (tgtRow < this.scrollTop || tgtRow > this.scrollBot) return;
      this.cy = tgtRow;
    } else {
      this.cy = clamp(row, topRow, botRow);
    }
    this.cx = clamp(col, 0, this.cols - 1);
  }

  cursorUp(n)    { this.cy = Math.max(this._top(), this.cy - n); }
  cursorDown(n)  { this.cy = Math.min(this._bot(), this.cy + n); }
  cursorLeft(n) {
    // pyte rule: if cursor was at the autowrap latch (cx == cols), step
    // back off the latch first, *then* apply the count.
    if (this.cx >= this.cols) this.cx = this.cols - 1;
    this.cx = Math.max(0, this.cx - n);
  }
  cursorRight(n) { this.cx = Math.min(this.cols - 1, this.cx + n); }
  cursorCol(n)   { this.cx = clamp(n, 0, this.cols - 1); }
  cursorRow(n)   {
    const target = this.originMode ? this.scrollTop + n : n;
    if (this.originMode && (target < this.scrollTop || target > this.scrollBot)) return;
    this.cy = clamp(target, 0, this.rows - 1);
  }

  _top() { return this.cy >= this.scrollTop ? this.scrollTop : 0; }
  _bot() { return this.cy <= this.scrollBot ? this.scrollBot : this.rows - 1; }

  saveCursor() {
    this.savedCursor = {
      x: this.cx, y: this.cy,
      fg: this.curFg, bg: this.curBg, flags: this.curFlags,
      originMode: this.originMode,
      charsets: this.charsets.slice(), gl: this.gl, gr: this.gr,
      autoWrap: this.autoWrap,
    };
  }

  restoreCursor() {
    if (!this.savedCursor) {
      this.cx = 0; this.cy = 0; this.curFg = DEFAULT_FG_INDEX;
      this.curBg = DEFAULT_BG_INDEX; this.curFlags = 0;
      return;
    }
    const s = this.savedCursor;
    this.cx = clamp(s.x, 0, this.cols - 1);
    this.cy = clamp(s.y, 0, this.rows - 1);
    this.curFg = s.fg; this.curBg = s.bg; this.curFlags = s.flags;
    this.originMode = s.originMode;
    this.charsets = s.charsets.slice(); this.gl = s.gl; this.gr = s.gr;
    this.autoWrap = s.autoWrap;
  }

  // ── C0 ────────────────────────────────────────────────────────────

  bs()  {
    if (this.cx >= this.cols) this.cx = this.cols - 1;
    if (this.cx > 0) this.cx--;
  }
  cr()  { this.cx = 0; }
  lf()  { this._lineFeed(); }
  ri()  { // reverse index
    if (this.cy === this.scrollTop) this.scrollDown(1);
    else if (this.cy > 0) this.cy--;
  }
  ind() { this._lineFeed(); }
  nel() { this.cr(); this._lineFeed(); }
  tab() {
    if (this.cx >= this.cols - 1) return;
    let x = this.cx + 1;
    while (x < this.cols - 1 && !this.tabs[x]) x++;
    this.cx = x;
  }
  cbt(n) {
    let x = this.cx;
    for (let k = 0; k < n; k++) {
      x--;
      while (x > 0 && !this.tabs[x]) x--;
    }
    this.cx = Math.max(0, x);
  }
  cht(n) {
    for (let k = 0; k < n; k++) this.tab();
  }

  // ── Erase ───────────────────────────────────────────────────────

  eraseInLine(mode) {
    const row = this.lines[this.cy];
    const bg = this.curBg;
    if (mode === 0)      for (let i = this.cx; i < this.cols; i++) resetCellBgKeep(row[i], bg);
    else if (mode === 1) for (let i = 0; i <= this.cx && i < this.cols; i++) resetCellBgKeep(row[i], bg);
    else if (mode === 2) for (let i = 0; i < this.cols; i++) resetCellBgKeep(row[i], bg);
  }

  eraseInDisplay(mode) {
    const bg = this.curBg;
    if (mode === 0) {
      this.eraseInLine(0);
      for (let r = this.cy + 1; r < this.rows; r++)
        for (let i = 0; i < this.cols; i++) resetCellBgKeep(this.lines[r][i], bg);
    } else if (mode === 1) {
      for (let r = 0; r < this.cy; r++)
        for (let i = 0; i < this.cols; i++) resetCellBgKeep(this.lines[r][i], bg);
      this.eraseInLine(1);
    } else if (mode === 2 || mode === 3) {
      this.clearScreen();
      if (mode === 3) this.scrollback = [];
    }
  }

  eraseChars(n) {
    const row = this.lines[this.cy];
    const bg = this.curBg;
    for (let i = this.cx; i < this.cx + n && i < this.cols; i++) resetCellBgKeep(row[i], bg);
  }

  insertChars(n) { this._shiftRight(this.cy, this.cx, n); }

  deleteChars(n) {
    const row = this.lines[this.cy];
    const bg = this.curBg;
    n = Math.max(0, Math.min(n, this.cols - this.cx));
    for (let i = this.cx; i + n < this.cols; i++) copyCell(row[i + n], row[i]);
    for (let i = Math.max(this.cx, this.cols - n); i < this.cols; i++) resetCellBgKeep(row[i], bg);
  }

  insertLines(n) {
    if (this.cy < this.scrollTop || this.cy > this.scrollBot) return;
    for (let k = 0; k < n; k++) {
      const row = this.lines.splice(this.scrollBot, 1)[0];
      for (let i = 0; i < this.cols; i++) resetCellBgKeep(row[i], this.curBg);
      this.lines.splice(this.cy, 0, row);
    }
    this.cx = 0;
  }

  deleteLines(n) {
    if (this.cy < this.scrollTop || this.cy > this.scrollBot) return;
    for (let k = 0; k < n; k++) {
      const row = this.lines.splice(this.cy, 1)[0];
      for (let i = 0; i < this.cols; i++) resetCellBgKeep(row[i], this.curBg);
      this.lines.splice(this.scrollBot, 0, row);
    }
    this.cx = 0;
  }

  scrollUp(n) {
    for (let k = 0; k < n; k++) {
      const row = this.lines.splice(this.scrollTop, 1)[0];
      // Save to scrollback only when scroll region is the full screen
      // and we're on the primary buffer.
      if (!this.altScreen && this.scrollTop === 0 && this.scrollBot === this.rows - 1) {
        this.scrollback.push(row.map(c => ({ ...c })));
        if (this.scrollback.length > this.maxScrollback) this.scrollback.shift();
      }
      for (let i = 0; i < this.cols; i++) resetCellBgKeep(row[i], this.curBg);
      this.lines.splice(this.scrollBot, 0, row);
    }
  }

  scrollDown(n) {
    for (let k = 0; k < n; k++) {
      const row = this.lines.splice(this.scrollBot, 1)[0];
      for (let i = 0; i < this.cols; i++) resetCellBgKeep(row[i], this.curBg);
      this.lines.splice(this.scrollTop, 0, row);
    }
  }

  // ── Clear / reset ───────────────────────────────────────────────

  clearScreen() {
    for (let r = 0; r < this.rows; r++)
      for (let i = 0; i < this.cols; i++) resetCellBgKeep(this.lines[r][i], this.curBg);
  }

  reset() {
    this.curFg = DEFAULT_FG_INDEX;
    this.curBg = DEFAULT_BG_INDEX;
    this.curFlags = 0;
    this.cx = 0; this.cy = 0;
    this.scrollTop = 0; this.scrollBot = this.rows - 1;
    this.autoWrap = true; this.originMode = false; this.insertMode = false;
    this.cursorVisible = true; this.bracketedPaste = false;
    this.appCursorKeys = false; this.appKeypad = false;
    this.altScreen = false; this.lines = this._primary;
    this.charsets = ['B','B','B','B']; this.gl = 0; this.gr = 2;
    this.savedCursor = null;
    this._initTabs();
    this.clearScreen();
  }

  // ── Tab stops ───────────────────────────────────────────────────

  setTabAtCursor() { this.tabs[this.cx] = true; }
  clearTab(mode) {
    if (mode === 0) this.tabs[this.cx] = false;
    else if (mode === 3) this.tabs.fill(false);
  }

  // ── Frame dict (for tests + offline renderers) ──────────────────

  toFrame() {
    const lines = [];
    for (let r = 0; r < this.rows; r++) {
      const row = this.lines[r];
      const chars = [];
      const runs = [];
      let prev = null;
      let runLen = 0;

      const emit = () => {
        if (!prev) return;
        const run = { n: runLen, fg: prev.fg, bg: prev.bg };
        if (prev.flags & FLAG.BOLD)      run.b = true;
        if (prev.flags & FLAG.ITALIC)    run.i = true;
        if (prev.flags & FLAG.UNDERLINE) run.u = true;
        if (prev.flags & FLAG.STRIKE)    run.s = true;
        runs.push(run);
      };

      for (let i = 0; i < this.cols; i++) {
        const c = row[i];
        if (c.w === 0) continue;          // skip continuation half
        const ch = c.ch === 0 ? 0x20 : c.ch;
        chars.push(String.fromCodePoint(ch));
        if (c.w === 2) i++; // skip the continuation cell next loop

        let fg = resolveColor(c.fg, true);
        let bg = resolveColor(c.bg, false);
        if (c.flags & FLAG.REVERSE) { const t = fg; fg = bg; bg = t; }
        const key = { fg, bg, flags: c.flags & (FLAG.BOLD|FLAG.ITALIC|FLAG.UNDERLINE|FLAG.STRIKE) };

        if (prev && prev.fg === key.fg && prev.bg === key.bg && prev.flags === key.flags) {
          runLen++;
        } else {
          emit();
          prev = key; runLen = 1;
        }
      }
      emit();

      // Pad text out to `cols` so frame dims match pyte (which always
      // emits cols-wide rows).  Padding inherits last run's bg.
      while (chars.length < this.cols) chars.push(' ');

      lines.push({ text: chars.join(''), runs });
    }

    // When the autowrap latch is set, the cursor logically sits "one
    // past the last column" — pyte and xterm both report it that way.
    const curCol = this.cx;

    return {
      rows: this.rows,
      cols: this.cols,
      cursor: { row: this.cy, col: curCol, visible: this.cursorVisible },
      defaultFg: DEFAULT_FG_HEX,
      defaultBg: DEFAULT_BG_HEX,
      lines,
    };
  }
}

// Minimal east-asian width: returns 2 for CJK wide ranges, 0 for
// combining marks, 1 otherwise.  Sufficient for most box-drawing,
// emoji combiners are not handled.
export function charWidth(cp) {
  if (cp === 0) return 1;
  if (cp < 0x20) return 0;
  if (cp >= 0x300 && cp <= 0x36f) return 0;             // combining diacritical marks
  if (cp >= 0x1100 && cp <= 0x115f) return 2;           // Hangul Jamo
  if (cp >= 0x2e80 && cp <= 0x303e) return 2;
  if (cp >= 0x3041 && cp <= 0x33ff) return 2;
  if (cp >= 0x3400 && cp <= 0x4dbf) return 2;
  if (cp >= 0x4e00 && cp <= 0x9fff) return 2;
  if (cp >= 0xa000 && cp <= 0xa4cf) return 2;
  if (cp >= 0xac00 && cp <= 0xd7a3) return 2;
  if (cp >= 0xf900 && cp <= 0xfaff) return 2;
  if (cp >= 0xfe30 && cp <= 0xfe4f) return 2;
  if (cp >= 0xff00 && cp <= 0xff60) return 2;
  if (cp >= 0xffe0 && cp <= 0xffe6) return 2;
  if (cp >= 0x20000 && cp <= 0x2fffd) return 2;
  if (cp >= 0x30000 && cp <= 0x3fffd) return 2;
  return 1;
}

function clamp(v, lo, hi) { return v < lo ? lo : v > hi ? hi : v; }
