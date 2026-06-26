/**
 * Canvas renderer for a Terminal screen.  Draws glyphs and the cursor
 * to a single <canvas>.  DPI-aware.  Supports:
 *
 *   - bold / italic / underline / strikethrough
 *   - default fg/bg + 256-color + truecolor (cell already resolved)
 *   - reverse video (already swapped in Screen.toFrame)
 *   - cursor styles: block / bar / underline, steady or blink
 *   - sixel images composited under the text
 */

const FONT_FAMILY = "'Cascadia Mono', 'Cascadia Code', Consolas, 'Courier New', monospace";

// Box-drawing characters → geometric line segments in normalised cell
// coordinates [0..1].  Drawing these as actual strokes (instead of
// rendering the font glyph) guarantees adjacent cells join cleanly
// regardless of how the font handles the box-drawing range.
const _C = 0.5;
const BOX_DRAW = {
  '─': [[0, _C, 1, _C]],
  '━': [[0, _C, 1, _C]],
  '│': [[_C, 0, _C, 1]],
  '┃': [[_C, 0, _C, 1]],
  '┌': [[_C, _C, 1, _C], [_C, _C, _C, 1]],
  '┐': [[0, _C, _C, _C], [_C, _C, _C, 1]],
  '└': [[_C, 0, _C, _C], [_C, _C, 1, _C]],
  '┘': [[_C, 0, _C, _C], [0, _C, _C, _C]],
  '├': [[_C, 0, _C, 1], [_C, _C, 1, _C]],
  '┤': [[_C, 0, _C, 1], [0, _C, _C, _C]],
  '┬': [[0, _C, 1, _C], [_C, _C, _C, 1]],
  '┴': [[0, _C, 1, _C], [_C, 0, _C, _C]],
  '┼': [[0, _C, 1, _C], [_C, 0, _C, 1]],
  // Double-line variants (collapse to single for simplicity)
  '═': [[0, _C, 1, _C]],
  '║': [[_C, 0, _C, 1]],
  '╔': [[_C, _C, 1, _C], [_C, _C, _C, 1]],
  '╗': [[0, _C, _C, _C], [_C, _C, _C, 1]],
  '╚': [[_C, 0, _C, _C], [_C, _C, 1, _C]],
  '╝': [[_C, 0, _C, _C], [0, _C, _C, _C]],
  '╠': [[_C, 0, _C, 1], [_C, _C, 1, _C]],
  '╣': [[_C, 0, _C, 1], [0, _C, _C, _C]],
  '╦': [[0, _C, 1, _C], [_C, _C, _C, 1]],
  '╩': [[0, _C, 1, _C], [_C, 0, _C, _C]],
  '╬': [[0, _C, 1, _C], [_C, 0, _C, 1]],
};

export const CURSOR_STYLE = Object.freeze({
  BLOCK_BLINK: 1, BLOCK_STEADY: 2,
  UNDER_BLINK: 3, UNDER_STEADY: 4,
  BAR_BLINK: 5,   BAR_STEADY: 6,
});

export class Renderer {
  constructor(canvas, { fontSize = 16, padding = 4 } = {}) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.fontSize = fontSize;
    this.padding = padding;
    this._measure();
    this._lastFrame = null;
    this._dpr = 0; this._w = 0; this._h = 0;
    this._blinkOn = true;
    setInterval(() => { this._blinkOn = !this._blinkOn; this._drawCursor(); }, 530);
    this.cursorStyle = CURSOR_STYLE.BLOCK_BLINK;
    this.sixels = [];      // [{ row, col, width, height, bitmap (Canvas) }]
    // Integer scale for sixel bitmaps so "1 sixel pixel" stays
    // visually 1 pixel (or a clean N×N block if zoomed).  Always
    // composited with imageSmoothingEnabled = false for crisp output.
    this.sixelScale = 1;
  }

  _measure() {
    this.ctx.font = `${this.fontSize}px ${FONT_FAMILY}`;
    const m = this.ctx.measureText('M');
    this.cellW = Math.max(1, Math.ceil(m.width));
    const raw = Math.ceil(this.fontSize * 1.25);
    // Constrain cell height to an integer multiple of one rendered
    // sixel band — that's 6 sixel pixels × sixelScale CSS pixels.
    // This guarantees that N character rows = M sixel bands for some
    // integer M, so sixel images tile cleanly with the text grid (3
    // bands per row at the default size, matching VT340 hardware).
    const step = 6 * Math.max(1, this.sixelScale | 0);
    this.cellH = Math.max(step, Math.round(raw / step) * step);
  }

  /** Change the font size (px) and recompute the cell grid metrics.
   *  Caller should re-draw the frame after this to repaint at the new
   *  size. */
  setFontSize(px) {
    this.fontSize = Math.max(6, Math.min(64, px | 0));
    this._measure();
  }

  /** Size the canvas to fit `rows × cols` cells. */
  fit(rows, cols) {
    const dpr = window.devicePixelRatio || 1;
    const w = this.padding * 2 + cols * this.cellW;
    const h = this.padding * 2 + rows * this.cellH;
    if (this._w !== w || this._h !== h || this._dpr !== dpr) {
      this.canvas.width = Math.round(w * dpr);
      this.canvas.height = Math.round(h * dpr);
      this.canvas.style.width = w + 'px';
      this.canvas.style.height = h + 'px';
      this._dpr = dpr; this._w = w; this._h = h;
    }
  }

  draw(frame) {
    this._lastFrame = frame;
    const { rows, cols, lines, cursor, defaultBg } = frame;
    this.fit(rows, cols);

    const ctx = this.ctx;
    ctx.setTransform(this._dpr, 0, 0, this._dpr, 0, 0);
    ctx.textBaseline = 'top';

    // Background fill
    ctx.fillStyle = '#' + defaultBg;
    ctx.fillRect(0, 0, this._w, this._h);

    // Text cells (drawn first; sixels go on top)
    for (let r = 0; r < rows; r++) {
      const line = lines[r];
      let col = 0;
      for (const run of line.runs) {
        const text = line.text.substr(col, run.n);
        this._drawRun(r, col, text, run);
        col += run.n;
      }
    }

    // Sixel images — drawn ON TOP of text (xterm/wezterm semantics).
    // Where the bitmap has opaque pixels, the image obscures whatever
    // text was underneath; where the bitmap is transparent (no sixel
    // data set), the cell text below shows through.
    for (const sx of this.sixels) this._blitSixel(sx);

    this._drawCursor();
  }

  _drawRun(r, c, text, run) {
    const ctx = this.ctx;
    const x = this.padding + c * this.cellW;
    const y = this.padding + r * this.cellH;
    const w = text.length * this.cellW;

    if (run.bg && run.bg !== this._lastFrame.defaultBg) {
      ctx.fillStyle = '#' + run.bg;
      ctx.fillRect(x, y, w, this.cellH);
    }

    let font = '';
    if (run.b) font += 'bold ';
    if (run.i) font += 'italic ';
    font += `${this.fontSize}px ${FONT_FAMILY}`;
    ctx.font = font;
    const fg = '#' + (run.fg || this._lastFrame.defaultFg);
    ctx.fillStyle = fg;

    // Draw glyph-by-glyph so we can substitute geometric segments for
    // box-drawing characters (the font's box glyphs rarely touch the
    // cell edges cleanly, so a 3×3 with `lqk / x x / mqj` ends up with
    // visible gaps).
    for (let i = 0; i < text.length; i++) {
      const ch = text[i];
      const cx = x + i * this.cellW;
      const segs = BOX_DRAW[ch];
      if (segs) {
        ctx.strokeStyle = fg;
        ctx.lineWidth = Math.max(1, Math.round(this.fontSize / 14));
        ctx.lineCap = 'butt';
        ctx.beginPath();
        for (const [x1, y1, x2, y2] of segs) {
          // Snap to half-pixel so 1-px strokes render crisply
          // (canvas anti-aliases lines drawn at integer coords).
          const px1 = Math.round(cx + x1 * this.cellW) + 0.5;
          const py1 = Math.round(y  + y1 * this.cellH) + 0.5;
          const px2 = Math.round(cx + x2 * this.cellW) + 0.5;
          const py2 = Math.round(y  + y2 * this.cellH) + 0.5;
          ctx.moveTo(px1, py1);
          ctx.lineTo(px2, py2);
        }
        ctx.stroke();
      } else if (ch !== ' ') {
        ctx.fillText(ch, cx, y + 2);
      }
    }

    if (run.u) {
      ctx.strokeStyle = fg;
      ctx.lineWidth = Math.max(1, this.fontSize / 16);
      ctx.beginPath();
      const yy = Math.round(y + this.cellH - 2) + 0.5;
      ctx.moveTo(x, yy); ctx.lineTo(x + w, yy); ctx.stroke();
    }
    if (run.s) {
      ctx.strokeStyle = fg;
      ctx.lineWidth = Math.max(1, this.fontSize / 16);
      ctx.beginPath();
      const yy = Math.round(y + this.cellH / 2) + 0.5;
      ctx.moveTo(x, yy); ctx.lineTo(x + w, yy); ctx.stroke();
    }
  }

  _drawCursor() {
    if (!this._lastFrame) return;
    const cur = this._lastFrame.cursor;
    if (!cur || !cur.visible) return;
    const blink = (this.cursorStyle === CURSOR_STYLE.BLOCK_BLINK
                || this.cursorStyle === CURSOR_STYLE.UNDER_BLINK
                || this.cursorStyle === CURSOR_STYLE.BAR_BLINK);
    if (blink && !this._blinkOn) return;

    const ctx = this.ctx;
    ctx.setTransform(this._dpr, 0, 0, this._dpr, 0, 0);
    const x = this.padding + cur.col * this.cellW;
    const y = this.padding + cur.row * this.cellH;
    ctx.fillStyle = '#' + (this._lastFrame.defaultFg || 'd4d4d4');
    switch (this.cursorStyle) {
      case CURSOR_STYLE.BLOCK_BLINK:
      case CURSOR_STYLE.BLOCK_STEADY:
        ctx.globalAlpha = 0.6;
        ctx.fillRect(x, y, this.cellW, this.cellH);
        ctx.globalAlpha = 1;
        break;
      case CURSOR_STYLE.UNDER_BLINK:
      case CURSOR_STYLE.UNDER_STEADY:
        ctx.fillRect(x, y + this.cellH - 2, this.cellW, 2);
        break;
      case CURSOR_STYLE.BAR_BLINK:
      case CURSOR_STYLE.BAR_STEADY:
        ctx.fillRect(x, y, 2, this.cellH);
        break;
    }
  }

  _blitSixel(s) {
    if (!s.bitmap) return;
    const ctx = this.ctx;

    // Switch to identity transform so we can address raw device
    // pixels directly.  This guarantees the sixel scale stays at
    // an exact integer multiplier (sixelScale × dpr), giving us
    // crisp N×N pixel blocks instead of an interpolated blur.
    const dpr = this._dpr;
    const scale = (this.sixelScale | 0) * dpr;
    const dx = Math.round((this.padding + s.col * this.cellW) * dpr);
    const dy = Math.round((this.padding + s.row * this.cellH) * dpr);
    const dw = s.bitmap.width  * scale;
    const dh = s.bitmap.height * scale;

    ctx.save();
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.imageSmoothingEnabled = false;
    ctx.drawImage(s.bitmap, 0, 0, s.bitmap.width, s.bitmap.height,
                  dx, dy, dw, dh);
    ctx.restore();

    // Restore the dpr-scaled transform so subsequent draw operations
    // (cursor, follow-up frames) keep their logical coordinates.
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }
}
