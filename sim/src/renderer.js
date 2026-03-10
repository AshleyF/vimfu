/**
 * VimFu Simulator – Renderer
 *
 * Renders a Frame dict to an HTML <canvas> element with a monospaced
 * font. Also renders the cursor as a block/bar overlay.
 *
 * This is the only module that touches the DOM for output.
 */

const FONT_FAMILY = "'Cascadia Mono', Consolas, 'Courier New', monospace";

// Box-drawing characters → geometric segment definitions.
// Each entry maps to an array of [x1, y1, x2, y2] in normalised (0–1) cell coords.
// Lines are always drawn from center-to-edge or center-to-center.
const _c = 0.5; // centre
const BOX_DRAW = {
  '─': [[0, _c, 1, _c]],                          // horizontal
  '│': [[_c, 0, _c, 1]],                           // vertical
  '┌': [[_c, _c, 1, _c], [_c, _c, _c, 1]],        // top-left
  '┐': [[0, _c, _c, _c], [_c, _c, _c, 1]],        // top-right
  '└': [[_c, 0, _c, _c], [_c, _c, 1, _c]],        // bottom-left
  '┘': [[_c, 0, _c, _c], [0, _c, _c, _c]],        // bottom-right
  '├': [[_c, 0, _c, 1], [_c, _c, 1, _c]],         // left tee
  '┤': [[_c, 0, _c, 1], [0, _c, _c, _c]],         // right tee
  '┬': [[0, _c, 1, _c], [_c, _c, _c, 1]],         // top tee
  '┴': [[0, _c, 1, _c], [_c, 0, _c, _c]],         // bottom tee
  '┼': [[0, _c, 1, _c], [_c, 0, _c, 1]],          // cross
};

export class Renderer {
  /**
   * @param {HTMLCanvasElement} canvas
   * @param {object} opts
   * @param {number} [opts.fontSize=18]
   */
  constructor(canvas, { fontSize = 18 } = {}) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.fontSize = fontSize;

    // Measure character cell
    this.ctx.font = `bold ${fontSize}px ${FONT_FAMILY}`;
    const m = this.ctx.measureText('M');
    this.charW = Math.ceil(m.width);
    this.charH = Math.ceil(fontSize * 1.4);
    this.padding = 6;
    this._logicalW = 0;
    this._logicalH = 0;
    this._dpr = 0;
  }

  /**
   * Draw a complete Frame.
   * @param {object} frame – Frame dict per frame_format.md
   */
  draw(frame) {
    const { rows, cols, lines, cursor } = frame;
    const cw = this.charW;
    const ch = this.charH;
    const pad = this.padding;

    const w = pad * 2 + cols * cw;
    const h = pad * 2 + rows * ch;
    const dpr = window.devicePixelRatio || 1;

    // Resize canvas if needed (accounting for DPI scale)
    if (this._logicalW !== w || this._logicalH !== h || this._dpr !== dpr) {
      this.canvas.width = Math.round(w * dpr);
      this.canvas.height = Math.round(h * dpr);
      this.canvas.style.width = w + 'px';
      this.canvas.style.height = h + 'px';
      this._logicalW = w;
      this._logicalH = h;
      this._dpr = dpr;
    }

    const ctx = this.ctx;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.font = `bold ${this.fontSize}px ${FONT_FAMILY}`;
    ctx.textBaseline = 'top';

    // Clear canvas to the frame's default background
    const defaultBgHex = '#' + (frame.defaultBg || '000000');
    ctx.fillStyle = defaultBgHex;
    ctx.fillRect(0, 0, w, h);

    // Draw each line
    for (let r = 0; r < lines.length; r++) {
      const line = lines[r];
      const text = line.text;
      const runs = line.runs || [];
      const y = pad + r * ch;

      let col = 0;
      for (const run of runs) {
        const x = pad + col * cw;
        const runW = run.n * cw;

        // Background — skip if it matches the canvas clear color (defaultBg)
        const bg = '#' + (run.bg || '000000');
        if (bg !== defaultBgHex) {
          ctx.fillStyle = bg;
          ctx.fillRect(x, y, runW, ch);
        }

        // Foreground text
        ctx.fillStyle = '#' + (run.fg || 'd4d4d4');
        if (run.b) {
          ctx.font = `bold ${this.fontSize}px ${FONT_FAMILY}`;
        }
        for (let c = 0; c < run.n && (col + c) < text.length; c++) {
          const char = text[col + c];
          if (char === ' ') continue;
          const cx = x + c * cw;
          const segs = BOX_DRAW[char];
          if (segs) {
            // Draw box-drawing character as geometric lines
            this._drawBoxChar(ctx, segs, cx, y, cw, ch);
          } else {
            ctx.fillText(char, cx, y + 2);
          }
        }
        if (run.b) {
          ctx.font = `bold ${this.fontSize}px ${FONT_FAMILY}`;
        }
        col += run.n;
      }
    }

    // Draw cursor (dark red bg, white fg – matches Neovim Monokai config)
    if (cursor && cursor.visible) {
      const cx = pad + cursor.col * cw;
      const cy = pad + cursor.row * ch;
      if (cursor.shape === 'beam') {
        // Thin vertical bar (insert/emacs mode)
        ctx.fillStyle = '#cccccc';
        ctx.fillRect(cx, cy, 2, ch);
      } else {
        // Block cursor (default, vi-normal, vim normal)
        ctx.fillStyle = '#800000';
        ctx.fillRect(cx, cy, cw, ch);
        // Redraw the character under cursor in white
        if (cursor.row < lines.length) {
          const charUnder = lines[cursor.row].text[cursor.col] || ' ';
          ctx.fillStyle = '#ffffff';
          const segs = BOX_DRAW[charUnder];
          if (segs) {
            this._drawBoxChar(ctx, segs, cx, cy, cw, ch);
          } else {
            ctx.fillText(charUnder, cx, cy + 2);
          }
        }
      }
    }
  }

  /**
   * Draw a box-drawing character as filled rectangles.
   * Uses a 2px stroke to match the font's visual weight.
   */
  _drawBoxChar(ctx, segs, x, y, cw, ch) {
    const lw = 2; // line thickness in pixels
    const hlw = lw / 2;
    for (const [x1, y1, x2, y2] of segs) {
      const px1 = x + x1 * cw;
      const py1 = y + y1 * ch;
      const px2 = x + x2 * cw;
      const py2 = y + y2 * ch;
      if (py1 === py2) {
        // Horizontal segment
        ctx.fillRect(px1, py1 - hlw, px2 - px1, lw);
      } else {
        // Vertical segment
        ctx.fillRect(px1 - hlw, py1, lw, py2 - py1);
      }
    }
  }
}
