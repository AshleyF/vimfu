/**
 * Sixel decoder — DCS Pa;Pb;Pc q ... ST
 *
 * Sixel encodes 6 vertical pixels per character.  Each data byte
 * 0x3f..0x7e represents a column of 6 pixels (byte - 0x3f gives a
 * 6-bit mask, LSB = top pixel).
 *
 * ## Cell-to-sixel relationship (what the spec says, and doesn't)
 *
 * The sixel format is pixel-graphics; the *only* dimensional facts
 * baked into the spec are:
 *   1. Six pixels per data byte (vertically), one band high.
 *   2. **Pixel aspect ratio** is configurable in two places:
 *        - DCS header param Ps1:
 *            0,1,5,6 → 2:1 (height:width)   [VT240 default]
 *            2       → 5:1
 *            3,4     → 3:1
 *            7,8,9   → 1:1 (square)         [libsixel default]
 *        - Raster attributes `"Pan;Pad;Ph;Pv` (override Ps1):
 *            Pan/Pad = height/width pixel aspect; Ph/Pv = image size.
 *
 * The spec **does NOT** define "a sixel band is half a character cell".
 * Cell size is a property of the terminal/font, separate from the
 * sixel data.  Historically the VT340 had 10×20-pixel character cells
 * and 1:1 sixel pixels, so 1 sixel band (6 px) ≈ 30% of a cell row,
 * i.e. ~3 bands per character row.  Modern terminals (xterm, foot,
 * wezterm, libsixel) render square pixels by default.
 *
 * ## Control characters inside the payload
 *
 *   #N            — select color N (palette index)
 *   #N;Pu;Px;Py;Pz — define color N
 *                     Pu=1 → HLS (hue 0..360, lightness 0..100, sat 0..100)
 *                     Pu=2 → RGB (r,g,b each 0..100)
 *   !Ns           — repeat sixel byte s N times
 *   $             — graphics carriage return (x ← 0)
 *   -             — graphics newline (y ← y+6, x ← 0)
 *   "Pan;Pad;Ph;Pv — raster attributes (pixel aspect + image size hint)
 *
 * Returns ImageData/Canvas with the decoded image.
 */

const _SIXEL_MIN = 0x3f;
const _SIXEL_MAX = 0x7e;

// Default VT340 16-color palette (per DEC docs).  Entries given as
// RGB 0..255.  These are the standard saturated colours that programs
// commonly assume even without an explicit colour definition.
const VT340_PALETTE = [
  [  0,   0,   0],  // 0: black
  [ 51,  51, 204],  // 1: blue
  [204,  51,  51],  // 2: red
  [ 51, 204,  51],  // 3: green
  [204,  51, 204],  // 4: magenta
  [ 51, 204, 204],  // 5: cyan
  [204, 204,  51],  // 6: yellow
  [120, 120, 120],  // 7: grey 50%
  [ 51,  51,  51],  // 8: grey 20%
  [102, 102, 153],  // 9: bright blue
  [153, 102, 102],  // 10: bright red
  [102, 153, 102],  // 11: bright green
  [153, 102, 153],  // 12: bright magenta
  [102, 153, 153],  // 13: bright cyan
  [153, 153, 102],  // 14: bright yellow
  [204, 204, 204],  // 15: grey 80%
];

function hlsToRgb(h, l, s) {
  // DEC sixel HLS: H 0..360, L 0..100, S 0..100.  DEC's H=0 is BLUE
  // (not red like CSS HSL).  Convert by rotating hue by +120°.
  const hh = ((h + 240) % 360) / 360;
  const ll = l / 100;
  const ss = s / 100;
  if (ss === 0) {
    const v = Math.round(ll * 255);
    return [v, v, v];
  }
  const q = ll < 0.5 ? ll * (1 + ss) : ll + ss - ll * ss;
  const p = 2 * ll - q;
  const hue2 = (t) => {
    if (t < 0) t += 1;
    if (t > 1) t -= 1;
    if (t < 1/6) return p + (q - p) * 6 * t;
    if (t < 1/2) return q;
    if (t < 2/3) return p + (q - p) * (2/3 - t) * 6;
    return p;
  };
  return [
    Math.round(hue2(hh + 1/3) * 255),
    Math.round(hue2(hh) * 255),
    Math.round(hue2(hh - 1/3) * 255),
  ];
}

export class SixelDecoder {
  constructor() { this.reset(); }

  reset() {
    this.palette = new Array(256);
    for (let i = 0; i < 16; i++) this.palette[i] = VT340_PALETTE[i].concat(255);
    this.curColor = 0;
    this.x = 0;
    this.bandY = 0;        // top pixel row of current sixel band
    this.maxX = 0;
    this.maxY = 0;
    this.aspectNum = 1;
    this.aspectDen = 1;
    this.bgIndex = 0;
    this.transparentBg = true;
    this.pixels = [];      // flat array of [x, y, r, g, b, a]
  }

  /** Decode a sixel DCS payload (everything between the final 'q' and ST). */
  decode(payload) {
    // Strip leading params Pa;Pb;Pc up through 'q' if it slipped in.
    let body = payload;
    const qIdx = body.indexOf('q');
    if (qIdx !== -1 && qIdx < 8) {
      // Header params: Ps1 ; Ps2 ; Ps3 q
      //   Ps1 = pixel aspect ratio (height : width).  DEC table:
      //         0,1,5,6 → 2:1   2 → 5:1   3,4 → 3:1   7,8,9 → 1:1
      //   Ps2 = background-color behaviour
      //         1 = leave existing pixels (transparent bg)
      //         0,2 = clear to background
      //   Ps3 = horizontal grid (1/90 inch units, historical — ignored)
      const header = body.slice(0, qIdx).split(';').map(s => parseInt(s, 10));
      const ps1 = header[0];
      if (Number.isFinite(ps1)) {
        // Map Ps1 → default Pan/Pad. The `"Pan;Pad…` raster attrs
        // (handled in the body) take precedence if present.
        const ASPECT_TABLE = {
          0: [2, 1], 1: [2, 1], 2: [5, 1], 3: [3, 1], 4: [3, 1],
          5: [2, 1], 6: [2, 1], 7: [1, 1], 8: [1, 1], 9: [1, 1],
        };
        const ratio = ASPECT_TABLE[ps1] || [1, 1];
        this.aspectNum = ratio[0];
        this.aspectDen = ratio[1];
      }
      if (header.length >= 2 && header[1] === 1) this.transparentBg = true;
      else if (header.length >= 2) this.transparentBg = false;
      body = body.slice(qIdx + 1);
    }

    const n = body.length;
    let i = 0;

    while (i < n) {
      const ch = body.charCodeAt(i);

      // Defensive: an ESC byte inside the body means "we ran into the
      // string terminator early" (caller didn't strip it).  Bail out
      // before the following ST byte (likely '\\') gets misread as a
      // sixel data char (0x5c is in the 0x3f..0x7e range).
      if (ch === 0x1b) break;

      if (ch >= _SIXEL_MIN && ch <= _SIXEL_MAX) {
        this._writeSixel(ch - _SIXEL_MIN);
        i++;
        continue;
      }

      if (ch === 0x21) {                           // '!' repeat
        i++;
        let count = 0;
        while (i < n && body.charCodeAt(i) >= 0x30 && body.charCodeAt(i) <= 0x39) {
          count = count * 10 + body.charCodeAt(i) - 0x30; i++;
        }
        if (count < 1) count = 1;
        if (i < n) {
          const sx = body.charCodeAt(i);
          if (sx >= _SIXEL_MIN && sx <= _SIXEL_MAX) {
            const bits = sx - _SIXEL_MIN;
            for (let r = 0; r < count; r++) this._writeSixel(bits);
            i++;
          }
        }
        continue;
      }

      if (ch === 0x24) { this.x = 0; i++; continue; }     // '$'
      if (ch === 0x2d) { this.x = 0; this.bandY += 6; i++; continue; } // '-'

      if (ch === 0x23) {                           // '#' color
        i++;
        const params = [];
        let v = '', sawDigit = false;
        while (i < n) {
          const c = body.charCodeAt(i);
          if (c >= 0x30 && c <= 0x39) { v += body[i]; sawDigit = true; i++; }
          else if (c === 0x3b)         { params.push(parseInt(v, 10) || 0); v = ''; i++; }
          else                          break;
        }
        if (sawDigit || v.length > 0) params.push(parseInt(v, 10) || 0);
        const idx = params[0] | 0;
        if (params.length >= 5) {
          const mode = params[1];
          if (mode === 2) {
            // RGB 0..100
            const r = Math.round((params[2] | 0) * 2.55);
            const g = Math.round((params[3] | 0) * 2.55);
            const b = Math.round((params[4] | 0) * 2.55);
            this.palette[idx] = [r, g, b, 255];
          } else if (mode === 1) {
            const [r, g, b] = hlsToRgb(params[2] | 0, params[3] | 0, params[4] | 0);
            this.palette[idx] = [r, g, b, 255];
          }
        }
        this.curColor = idx;
        continue;
      }

      if (ch === 0x22) {                           // '"' raster attributes
        i++;
        const params = [];
        let v = '';
        while (i < n) {
          const c = body.charCodeAt(i);
          if (c >= 0x30 && c <= 0x39) { v += body[i]; i++; }
          else if (c === 0x3b)         { params.push(parseInt(v, 10) || 0); v = ''; i++; }
          else                          break;
        }
        if (v) params.push(parseInt(v, 10) || 0);
        if (params.length >= 2) {
          this.aspectNum = params[0] || 1;
          this.aspectDen = params[1] || 1;
        }
        if (params.length >= 4) {
          this.maxX = Math.max(this.maxX, params[2] || 0);
          this.maxY = Math.max(this.maxY, params[3] || 0);
        }
        continue;
      }

      // Whitespace / unknown — skip
      i++;
    }
  }

  _writeSixel(bits) {
    const color = this.palette[this.curColor] || [255, 255, 255, 255];
    for (let b = 0; b < 6; b++) {
      if (bits & (1 << b)) {
        const px = this.x;
        const py = this.bandY + b;
        this.pixels.push([px, py, color[0], color[1], color[2], color[3]]);
        if (px + 1 > this.maxX) this.maxX = px + 1;
        if (py + 1 > this.maxY) this.maxY = py + 1;
      }
    }
    this.x++;
    if (this.x > this.maxX) this.maxX = this.x;
  }

  /** Render the decoded pixels onto a fresh canvas (returned). */
  toCanvas() {
    const w = Math.max(1, this.maxX);
    const h = Math.max(1, this.maxY);
    const yScale = Math.max(1, Math.round(this.aspectNum / this.aspectDen));

    // Always use a regular <canvas> element — OffscreenCanvas is not
    // universally supported and drawImage() with one occasionally
    // misbehaves across browsers.  A detached HTMLCanvasElement works
    // everywhere and drawImage handles it identically.
    const cnv = (typeof document !== 'undefined')
      ? document.createElement('canvas')
      : new OffscreenCanvas(w, h * yScale);
    cnv.width  = w;
    cnv.height = h * yScale;

    const ctx = cnv.getContext('2d');
    if (!ctx) return cnv;

    if (!this.transparentBg) {
      const bg = this.palette[this.bgIndex] || [0, 0, 0, 255];
      ctx.fillStyle = `rgba(${bg[0]},${bg[1]},${bg[2]},${bg[3] / 255})`;
      ctx.fillRect(0, 0, w, h * yScale);
    }

    const img = ctx.createImageData(w, h);
    for (const [px, py, r, g, b, a] of this.pixels) {
      if (px < 0 || px >= w || py < 0 || py >= h) continue;
      const idx = (py * w + px) * 4;
      img.data[idx]     = r;
      img.data[idx + 1] = g;
      img.data[idx + 2] = b;
      img.data[idx + 3] = a;
    }

    if (yScale === 1) {
      ctx.putImageData(img, 0, 0);
    } else {
      // Stretch vertically to honor pixel aspect.
      const tmp = (typeof document !== 'undefined')
        ? document.createElement('canvas')
        : new OffscreenCanvas(w, h);
      tmp.width = w; tmp.height = h;
      tmp.getContext('2d').putImageData(img, 0, 0);
      ctx.imageSmoothingEnabled = false;
      ctx.drawImage(tmp, 0, 0, w, h, 0, 0, w, h * yScale);
    }
    return cnv;
  }
}

/** Convenience: decode a payload and return a canvas. */
export function decodeSixel(payload) {
  const dec = new SixelDecoder();
  dec.decode(payload);
  return dec.toCanvas();
}
