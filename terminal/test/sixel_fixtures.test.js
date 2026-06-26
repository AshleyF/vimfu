/**
 * Decoder tests against real-world sixel files copied from
 * csdvrx/sixel-testsuite.  These are the same files xterm, mlterm,
 * foot, wezterm etc. use to verify their sixel implementations.
 *
 * For each fixture we check:
 *   - parses without throwing
 *   - reports a positive image size
 *   - emits the expected pixel count (within a small tolerance)
 *   - colour palette has been populated
 */

import { describe, test, expect } from '@jest/globals';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { SixelDecoder } from '../src/sixel.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const FX = path.join(__dirname, 'fixtures', 'sixel');

/** Strip the outer ESC P … ESC \\ envelope, leave only the body the
 *  decoder consumes (everything after the 'q' final byte). */
function unwrap(buf) {
  let body = buf.toString('latin1');
  const s = body.indexOf('\x1bP');
  if (s >= 0) body = body.slice(s + 2);
  // recompute lastIndexOf AFTER the head was removed, otherwise the
  // index points at the wrong position in the new string
  const e = body.lastIndexOf('\x1b\\');
  if (e > 0)  body = body.slice(0, e);
  return body;
}

function decodeFile(name) {
  const buf = fs.readFileSync(path.join(FX, name));
  const body = unwrap(buf);
  const dec = new SixelDecoder();
  dec.decode(body);
  return dec;
}

describe('Sixel fixtures from csdvrx/sixel-testsuite', () => {

  test('minimal-sixel.six → 14×7 image with two colors', () => {
    const d = decodeFile('minimal-sixel.six');
    expect(d.maxX).toBe(14);
    expect(d.maxY).toBe(7);
    expect(d.pixels.length).toBeGreaterThan(50);
    // Color 1 = yellow (100,100,0), color 2 = green (0,100,0).
    expect(d.palette[1]).toEqual([255, 255, 0, 255]);
    expect(d.palette[2]).toEqual([0, 255, 0, 255]);
  });

  test('go.six → 64×6 single-row gradient', () => {
    const d = decodeFile('go.six');
    expect(d.maxX).toBeGreaterThanOrEqual(60);
    expect(d.maxY).toBe(6);
    expect(d.pixels.length).toBeGreaterThan(0);
  });

  test('3-sixels.six → 93×~18 multi-color test pattern', () => {
    const d = decodeFile('3-sixels.six');
    expect(d.maxX).toBe(93);
    expect(d.maxY).toBeGreaterThanOrEqual(12);
    // 8 colours defined (#0..#7)
    let palCount = 0;
    for (let i = 0; i < 8; i++) if (d.palette[i]) palCount++;
    expect(palCount).toBe(8);
  });

  test('me.six → ~160×160 with run-length compression', () => {
    const d = decodeFile('me.six');
    expect(d.maxX).toBeGreaterThan(100);
    expect(d.maxY).toBeGreaterThan(100);
    expect(d.pixels.length).toBeGreaterThan(5000);
  });

  test('text-test.sixel → ~64×64 with raster attributes', () => {
    const d = decodeFile('text-test.sixel');
    expect(d.maxX).toBeGreaterThanOrEqual(60);
    expect(d.maxY).toBeGreaterThanOrEqual(60);
  });

  test('snake.six → 600×450 full-color photo', () => {
    const d = decodeFile('snake.six');
    expect(d.maxX).toBe(600);
    expect(d.maxY).toBe(450);
    // libsixel quantizes photos to 256 colors; we should see many of them.
    let palCount = 0;
    for (let i = 0; i < 256; i++) if (d.palette[i]) palCount++;
    expect(palCount).toBeGreaterThan(200);
    expect(d.pixels.length).toBeGreaterThan(200_000);
  });

  test('snake.six → reasonable colour distribution', () => {
    const d = decodeFile('snake.six');
    // The snake photo has greens (snake) and browns (background) and
    // some bright highlights.  Verify at least a few palette entries
    // are noticeably green-dominant or red-dominant.
    let greens = 0, reds = 0;
    for (let i = 0; i < 256; i++) {
      const c = d.palette[i];
      if (!c) continue;
      if (c[1] > 80 && c[1] > c[0] + 20 && c[1] > c[2] + 20) greens++;
      if (c[0] > 80 && c[0] > c[1] + 20 && c[0] > c[2] + 20) reds++;
    }
    expect(greens).toBeGreaterThan(5);
    expect(reds).toBeGreaterThan(2);
  });
});
