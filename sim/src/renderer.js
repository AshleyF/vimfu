/**
 * VimFu Simulator – Renderer
 *
 * Renders a Frame dict to an HTML <canvas> element with a monospaced
 * font. Also renders the cursor as a block/bar overlay.
 *
 * This is the only module that touches the DOM for output.
 */

const FONT_FAMILY = "'Cascadia Mono', Consolas, 'Courier New', monospace";

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
    this.ctx.font = `${fontSize}px ${FONT_FAMILY}`;
    const m = this.ctx.measureText('M');
    this.charW = Math.ceil(m.width);
    this.charH = Math.ceil(fontSize * 1.4);
    this.padding = 6;
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

    // Resize canvas if needed
    if (this.canvas.width !== w || this.canvas.height !== h) {
      this.canvas.width = w;
      this.canvas.height = h;
    }

    const ctx = this.ctx;
    ctx.font = `${this.fontSize}px ${FONT_FAMILY}`;
    ctx.textBaseline = 'top';

    // Clear
    ctx.fillStyle = '#' + (frame.defaultBg || '000000');
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

        // Background
        const bg = '#' + (run.bg || '000000');
        if (bg !== '#000000') {
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
          if (char !== ' ') {
            ctx.fillText(char, x + c * cw, y + 2);
          }
        }
        if (run.b) {
          ctx.font = `${this.fontSize}px ${FONT_FAMILY}`;
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
          ctx.fillText(charUnder, cx, cy + 2);
        }
      }
    }
  }
}
