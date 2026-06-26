/**
 * Unit tests for the sixel decoder.
 */

import { describe, test, expect } from '@jest/globals';
import { SixelDecoder } from '../src/sixel.js';

// Polyfill OffscreenCanvas-free fallback by stubbing in a tiny canvas-
// like object.  toCanvas() is GUI-side; the tests here only validate
// pixel emission.
describe('SixelDecoder', () => {
  test('decodes a single-pixel red dot', () => {
    const d = new SixelDecoder();
    // Define color 1 as pure red (RGB 100/0/0), then plot mask 0x01
    // (top pixel only).
    d.decode('q#1;2;100;0;0#1@');   // '@' = 0x40 → mask 0x01
    expect(d.pixels.length).toBe(1);
    const [x, y, r, g, b, a] = d.pixels[0];
    expect([x, y]).toEqual([0, 0]);
    expect([r, g, b, a]).toEqual([255, 0, 0, 255]);
  });

  test('decodes a vertical green column (all six pixels)', () => {
    const d = new SixelDecoder();
    d.decode('q#2;2;0;100;0#2~');   // '~' = 0x7e → mask 0x3f
    expect(d.pixels.length).toBe(6);
    for (let i = 0; i < 6; i++) {
      const [x, y] = d.pixels[i];
      expect(x).toBe(0);
      expect(y).toBe(i);
    }
    expect(d.maxX).toBe(1);
    expect(d.maxY).toBe(6);
  });

  test('repeat operator !N produces N copies', () => {
    const d = new SixelDecoder();
    d.decode('q#3;2;0;0;100#3!10~');
    // 10 columns × 6 rows = 60 pixels
    expect(d.pixels.length).toBe(60);
    expect(d.maxX).toBe(10);
    expect(d.maxY).toBe(6);
  });

  test('carriage return ($) resets x', () => {
    const d = new SixelDecoder();
    d.decode('q#4;2;100;100;0#4!5~$#4@');
    // Five-wide stripe, then back to x=0, place one pixel
    // (the @ writes the *top* pixel at x=0, overwriting an existing).
    // pixels list has 30 + 1 = 31 entries (some overlap at 0,0).
    expect(d.pixels.length).toBe(31);
  });

  test('newline (-) drops y by 6 and resets x', () => {
    const d = new SixelDecoder();
    d.decode('q#5;2;0;100;100#5~-#5~');
    expect(d.maxY).toBe(12);
    expect(d.pixels.length).toBe(12);
    expect(d.pixels.some(p => p[1] >= 6)).toBe(true);
  });

  test('multiple colors in one pass', () => {
    const d = new SixelDecoder();
    d.decode('q#1;2;100;0;0#2;2;0;100;0#1@#2A');
    expect(d.pixels.length).toBe(2);
    // First pixel: color 1 (red) at (0, 0)
    expect(d.pixels[0].slice(2)).toEqual([255, 0, 0, 255]);
    // Second pixel: color 2 (green) at (1, 0)
    expect(d.pixels[1].slice(2)).toEqual([0, 255, 0, 255]);
  });

  test('raster attributes set image bounds', () => {
    const d = new SixelDecoder();
    d.decode('q"1;1;40;30');
    expect(d.maxX).toBeGreaterThanOrEqual(40);
    expect(d.maxY).toBeGreaterThanOrEqual(30);
  });

  test('Ps1 header param 7 means 1:1 pixel aspect (square)', () => {
    const d = new SixelDecoder();
    // Ps1=7  Ps2=1 (transparent bg)
    d.decode('7;1q');
    expect(d.aspectNum).toBe(1);
    expect(d.aspectDen).toBe(1);
  });

  test('Ps1 header param 0 means 2:1 pixel aspect (VT240 default)', () => {
    const d = new SixelDecoder();
    d.decode('0q');
    expect(d.aspectNum).toBe(2);
    expect(d.aspectDen).toBe(1);
  });

  test('Ps1 header param 2 means 5:1 pixel aspect', () => {
    const d = new SixelDecoder();
    d.decode('2q');
    expect(d.aspectNum).toBe(5);
    expect(d.aspectDen).toBe(1);
  });

  test('raster attributes override the Ps1 default aspect', () => {
    const d = new SixelDecoder();
    // Ps1=0 → 2:1, but raster attrs say 1:1
    d.decode('0q"1;1;20;10');
    expect(d.aspectNum).toBe(1);
    expect(d.aspectDen).toBe(1);
  });
});
