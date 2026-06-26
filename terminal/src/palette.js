/**
 * Palette — ANSI 16, xterm 256, truecolor (0xRRGGBB) → '#rrggbb'.
 *
 * Defaults match xterm:
 *   defaultFg = #d4d4d4 (light grey)
 *   defaultBg = #000000 (black)
 *
 * Colour state on a cell is stored as a 32-bit signed int with the
 * following encoding (matches what most JS terminals do, easy to test):
 *
 *   value <  0          → default (special marker)
 *   value < 256         → palette index (0..15 = ANSI, 16..255 = 256-cube)
 *   value >= 0x10000000 → truecolor, RGB packed in low 24 bits
 *
 * Use `isDefault/isPalette/isTrue` to introspect.
 */

export const DEFAULT_FG_INDEX = -1;
export const DEFAULT_BG_INDEX = -2;
const TRUE_FLAG = 0x10000000;

// xterm 16-color palette (matches pyte defaults + xterm "modern")
// NOTE: capture_frames.py in shellpilot also uses these; keep in sync.
const ANSI_16 = [
  '000000', 'cd0000', '00cd00', 'cdcd00',
  '0000ee', 'cd00cd', '00cdcd', 'e5e5e5',
  '7f7f7f', 'ff0000', '00ff00', 'ffff00',
  '5c5cff', 'ff00ff', '00ffff', 'ffffff',
];

// Build 256-color palette: 16 ANSI + 216 RGB cube + 24 greys.
function build256() {
  const out = new Array(256);
  for (let i = 0; i < 16; i++) out[i] = ANSI_16[i];
  for (let i = 0; i < 216; i++) {
    const r = Math.floor(i / 36) % 6;
    const g = Math.floor(i / 6) % 6;
    const b = i % 6;
    const conv = c => (c === 0 ? 0 : 55 + c * 40);
    out[16 + i] = hex2(conv(r)) + hex2(conv(g)) + hex2(conv(b));
  }
  for (let i = 0; i < 24; i++) {
    const v = 8 + i * 10;
    out[232 + i] = hex2(v) + hex2(v) + hex2(v);
  }
  return out;
}

function hex2(n) { return n.toString(16).padStart(2, '0'); }

export const PALETTE_256 = build256();

export const DEFAULT_FG_HEX = 'd4d4d4';
export const DEFAULT_BG_HEX = '000000';

// Mutable runtime palette (OSC 4 can change it).
const runtimePalette = PALETTE_256.slice();

export function resetPalette() {
  for (let i = 0; i < 256; i++) runtimePalette[i] = PALETTE_256[i];
}

export function setPaletteEntry(idx, hex) {
  if (idx >= 0 && idx < 256) runtimePalette[idx] = hex;
}

export function getPaletteEntry(idx) {
  return runtimePalette[idx];
}

// ── Encoding helpers ───────────────────────────────────────────────

export function paletteIndex(i)  { return i & 0xff; }
export function trueRGB(r, g, b) { return TRUE_FLAG | ((r & 0xff) << 16) | ((g & 0xff) << 8) | (b & 0xff); }

export function isDefault(v) { return v === DEFAULT_FG_INDEX || v === DEFAULT_BG_INDEX; }
export function isTrue(v)    { return (v & TRUE_FLAG) !== 0; }
export function isPalette(v) { return v >= 0 && v < 256; }

/** Resolve to '#rrggbb'-style hex (no leading '#') for a cell colour. */
export function resolveColor(v, isFg) {
  if (v === DEFAULT_FG_INDEX) return DEFAULT_FG_HEX;
  if (v === DEFAULT_BG_INDEX) return DEFAULT_BG_HEX;
  if (v < 0) return isFg ? DEFAULT_FG_HEX : DEFAULT_BG_HEX;
  if (isTrue(v)) {
    const r = (v >> 16) & 0xff, g = (v >> 8) & 0xff, b = v & 0xff;
    return hex2(r) + hex2(g) + hex2(b);
  }
  return runtimePalette[v & 0xff];
}

// ── SGR colour-parameter consumer ──────────────────────────────────
//
// Handles `38;5;n`, `38;2;r;g;b`, and ISO-8613-6 sub-parameter forms
// (`38:2::r:g:b` already arrives as one param-group with subparams).
//
// Returns { value, advance } where `advance` is the number of *param groups*
// consumed (caller should skip).
export function parseSgrColor(params, idx) {
  const group = params[idx];
  if (!group || group.length === 0) return null;

  // Sub-param form: e.g. params[idx] = [38, 5, 1] or [38, 2, , r, g, b]
  if (group.length >= 2) {
    const sel = group[1];
    if (sel === 5) {
      const n = group[2] | 0;
      return { value: paletteIndex(n), advance: 1 };
    }
    if (sel === 2) {
      // ISO form: [38, 2, ?colorspace, r, g, b] OR [38, 2, r, g, b]
      let r, g, b;
      if (group.length >= 6) { r = group[3]|0; g = group[4]|0; b = group[5]|0; }
      else                   { r = group[2]|0; g = group[3]|0; b = group[4]|0; }
      return { value: trueRGB(r, g, b), advance: 1 };
    }
    return { value: null, advance: 1 };
  }

  // Legacy semicolon form: [38] [5] [n]   or   [38] [2] [r] [g] [b]
  const sel = (params[idx + 1] && params[idx + 1][0]) | 0;
  if (sel === 5) {
    const n = (params[idx + 2] && params[idx + 2][0]) | 0;
    return { value: paletteIndex(n), advance: 3 };
  }
  if (sel === 2) {
    const r = (params[idx + 2] && params[idx + 2][0]) | 0;
    const g = (params[idx + 3] && params[idx + 3][0]) | 0;
    const b = (params[idx + 4] && params[idx + 4][0]) | 0;
    return { value: trueRGB(r, g, b), advance: 5 };
  }
  return { value: null, advance: 1 };
}
