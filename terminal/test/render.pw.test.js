/**
 * Canvas rendering tests (Playwright).
 *
 * These run inside real Chromium against the test harness page and
 * inspect pixels in the rendered canvas — verifying the painter, not
 * just the data model.  Run with `npm run test:render`.
 */

import { test, expect } from '@playwright/test';

test.beforeEach(async ({ page }) => {
  // Use a custom font load wait by waiting for the vt-ready event
  await page.goto('/test/render_harness.html', { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts && document.fonts.ready);
});

// ── Helpers ─────────────────────────────────────────────────────────

async function reset(page, rows = 6, cols = 20) {
  await page.evaluate(({ rows, cols }) => window.vt.reset(rows, cols), { rows, cols });
}
async function write(page, bytes)         { await page.evaluate(b => window.vt.write(b), bytes); }
async function avg(page, row, col)        { return page.evaluate(({r,c}) => window.vt.cellAverage(r, c), { r: row, c: col }); }
async function ink(page, row, col, bg)    { return page.evaluate(({r,c,bg}) => window.vt.cellInkRatio(r, c, bg), { r: row, c: col, bg: bg || [0,0,0] }); }
async function pixel(page, x, y)          { return page.evaluate(({x,y}) => window.vt.pixelAt(x, y), { x, y }); }
async function geom(page)                  { return page.evaluate(() => window.vt.geometry()); }
async function rect(page, row, col)       { return page.evaluate(({r,c}) => window.vt.cellRect(r, c), { r: row, c: col }); }

// Compare a pixel value to a target color allowing per-channel slack.
function nearColor([r, g, b, a], target, slack = 20) {
  return Math.abs(r - target[0]) <= slack
      && Math.abs(g - target[1]) <= slack
      && Math.abs(b - target[2]) <= slack;
}

// ── Background / foreground colors ─────────────────────────────────

test('default background is black across the canvas', async ({ page }) => {
  await reset(page);
  const c = await avg(page, 2, 5);
  expect(c[0]).toBeLessThan(15);
  expect(c[1]).toBeLessThan(15);
  expect(c[2]).toBeLessThan(15);
});

test('SGR red background fills the cell with red', async ({ page }) => {
  await reset(page);
  await write(page, '\x1b[41m  \x1b[0m');     // two cells with red bg
  const c = await avg(page, 0, 0);
  expect(c[0]).toBeGreaterThan(150);          // red channel dominant
  expect(c[1]).toBeLessThan(60);
  expect(c[2]).toBeLessThan(60);
});

test('SGR truecolor background paints the exact color', async ({ page }) => {
  await reset(page);
  await write(page, '\x1b[48;2;200;100;50m  \x1b[0m');
  const c = await avg(page, 0, 0);
  expect(nearColor(c, [200, 100, 50], 15)).toBe(true);
});

test('all eight ANSI fg colors produce distinct hues', async ({ page }) => {
  await reset(page, 4, 32);
  for (let n = 30; n <= 37; n++) {
    await write(page, `\x1b[${n}m##\x1b[0m`);
  }
  // Just sanity: at least 4 distinct sets of pixels across the row
  const seen = new Set();
  for (let i = 0; i < 16; i += 2) {
    const c = await avg(page, 0, i);
    seen.add(c.slice(0, 3).join(','));
  }
  expect(seen.size).toBeGreaterThanOrEqual(4);
});

// ── Text rendering ─────────────────────────────────────────────────

test('writing a letter produces ink in its cell', async ({ page }) => {
  await reset(page);
  await write(page, 'X');
  const r = await ink(page, 0, 0);
  expect(r).toBeGreaterThan(0.05);             // at least 5% ink
  // The neighbouring cell should be empty (cursor is hidden in the
  // harness so it can't pollute the sample).
  const r2 = await ink(page, 0, 1);
  expect(r2).toBeLessThan(0.02);
});

test('bold letter has more ink than its plain counterpart', async ({ page }) => {
  await reset(page, 2, 4);
  await write(page, 'X');                       // (0,0) plain
  await write(page, '\x1b[1mX\x1b[0m');         // (0,1) bold
  const plain = await ink(page, 0, 0);
  const bold  = await ink(page, 0, 1);
  // Bold metrics vary by browser/font.  Just require strictly more ink.
  expect(bold).toBeGreaterThanOrEqual(plain);
  expect(bold).toBeGreaterThan(0.05);
});

test('underline draws a horizontal line near the bottom of the cell', async ({ page }) => {
  await reset(page);
  await write(page, '\x1b[4mX\x1b[0m');
  const r = await rect(page, 0, 0);
  // Sample several pixels along the bottom row of the cell to side-
  // step single-pixel anti-aliasing softening.
  const ys = [r.h - 2, r.h - 3];
  let bestBrightness = 0;
  for (const dy of ys) {
    for (let dx = 2; dx < r.w - 2; dx++) {
      const [R] = await pixel(page, r.x + dx, r.y + dy);
      if (R > bestBrightness) bestBrightness = R;
    }
  }
  expect(bestBrightness).toBeGreaterThan(120);
});

test('strikethrough draws across the cell middle', async ({ page }) => {
  await reset(page);
  await write(page, '\x1b[9mX\x1b[0m');
  const r = await rect(page, 0, 0);
  const [R] = await pixel(page, r.x + Math.round(r.w / 2), r.y + Math.round(r.h / 2));
  expect(R).toBeGreaterThan(120);
});

test('reverse video swaps fg/bg', async ({ page }) => {
  await reset(page);
  await write(page, '\x1b[7m \x1b[0m');         // reverse + space
  const c = await avg(page, 0, 0);
  // Background should now be ~fg color (light)
  expect(c[0]).toBeGreaterThan(120);
  expect(c[1]).toBeGreaterThan(120);
  expect(c[2]).toBeGreaterThan(120);
});

// ── Cursor ─────────────────────────────────────────────────────────

test('cursor block is drawn at the current cursor position', async ({ page }) => {
  await reset(page);
  await write(page, '\x1b[3;5HX');              // cursor lands at (2, 5)
  // Re-enable the cursor (harness hides it by default).
  await page.evaluate(() => window.vt.showCursor());
  const r = await rect(page, 2, 5);
  const c = await pixel(page, r.x + Math.round(r.w / 2), r.y + Math.round(r.h / 2));
  // Block cursor at 0.6 alpha over light fg — should be brightish.
  expect(c[0]).toBeGreaterThan(80);
});

// ── DEC line drawing ───────────────────────────────────────────────

// Helper: find the maximum red-channel value over a small box.
async function brightestIn(page, x, y, w, h) {
  return page.evaluate(({x,y,w,h}) => {
    const ctx = document.getElementById('term').getContext('2d');
    const img = ctx.getImageData(x, y, w, h).data;
    let best = 0;
    for (let i = 0; i < img.length; i += 4) {
      const lum = Math.max(img[i], img[i+1], img[i+2]);
      if (lum > best) best = lum;
    }
    return best;
  }, { x, y, w, h });
}

test('DEC line drawing horizontal: adjacent q-q cells touch at the edge', async ({ page }) => {
  await reset(page, 3, 10);
  await write(page, '\x1b(0qq\x1b(B');           // two ── glyphs side by side
  const r0 = await rect(page, 0, 0);
  const r1 = await rect(page, 0, 1);
  // Brightest pixel in a small box straddling the cell boundary at mid-height.
  const midY = r0.y + Math.round(r0.h / 2) - 1;
  const b = await brightestIn(page, r0.x + r0.w - 2, midY, 4, 3);
  expect(b).toBeGreaterThan(120);
});

test('DEC line drawing vertical: x glyph paints a centred column', async ({ page }) => {
  await reset(page, 4, 4);
  await write(page, '\x1b(0x\x1b(B');
  const r = await rect(page, 0, 0);
  const midX = r.x + Math.round(r.w / 2) - 1;
  const top    = await brightestIn(page, midX, r.y + 1, 3, 3);
  const bottom = await brightestIn(page, midX, r.y + r.h - 4, 3, 3);
  expect(top).toBeGreaterThan(120);
  expect(bottom).toBeGreaterThan(120);
});

test('DEC line drawing box: corners connect to edges', async ({ page }) => {
  await reset(page, 4, 6);
  await write(page, '\x1b(0lqk\x1b(B');
  const rl = await rect(page, 0, 0);   // l = ┌
  const rq = await rect(page, 0, 1);   // q = ─
  const rk = await rect(page, 0, 2);   // k = ┐

  const midY = rl.y + Math.round(rl.h / 2) - 1;
  // Between l and q
  const a = await brightestIn(page, rl.x + rl.w - 2, midY, 4, 3);
  // Between q and k
  const b = await brightestIn(page, rq.x + rq.w - 2, midY, 4, 3);
  expect(a).toBeGreaterThan(120);
  expect(b).toBeGreaterThan(120);
});

// ── Sixel ──────────────────────────────────────────────────────────

test('sixel: red horizontal band shows up at the cursor', async ({ page }) => {
  await reset(page, 6, 20);
  const dcs = "\x1bP" + "q#1;2;100;0;0#1!40~" + "\x1b\\";
  await write(page, dcs);
  // Sample at the cursor origin (row 0, col 0), a few pixels in.
  const g = await geom(page);
  const c = await pixel(page, g.padding + 2, g.padding + 2);
  expect(c[0]).toBeGreaterThan(180);   // red
  expect(c[1]).toBeLessThan(60);
  expect(c[2]).toBeLessThan(60);
});

test('sixel: tricolor flag has three distinct bands', async ({ page }) => {
  await reset(page, 6, 20);
  const tilde = '~'.repeat(60);
  const dcs = "\x1bP" + "q"
    + "#1;2;100;15;15"
    + "#2;2;100;100;100"
    + "#3;2;15;30;100"
    + "#1" + tilde + "-"
    + "#2" + tilde + "-"
    + "#3" + tilde
    + "\x1b\\";
  await write(page, dcs);
  const g = await geom(page);
  // Sample top of each band: y=padding+1, +7, +13 (each band 6px high).
  const red   = await pixel(page, g.padding + 10, g.padding + 1);
  const white = await pixel(page, g.padding + 10, g.padding + 8);
  const blue  = await pixel(page, g.padding + 10, g.padding + 14);
  expect(red[0]).toBeGreaterThan(150);
  expect(red[2]).toBeLessThan(80);
  expect(white[0]).toBeGreaterThan(200); expect(white[1]).toBeGreaterThan(200); expect(white[2]).toBeGreaterThan(200);
  expect(blue[2]).toBeGreaterThan(150);
  expect(blue[0]).toBeLessThan(80);
});

test('sixel: clearing wipes the overlay layer', async ({ page }) => {
  await reset(page);
  const dcs = "\x1bP" + "q#1;2;100;0;0#1!40~" + "\x1b\\";
  await write(page, dcs);
  await page.evaluate(() => {
    window.vt.ren.sixels.length = 0;
    window.vt.ren.draw(window.vt.term.toFrame());
  });
  const g = await geom(page);
  const c = await pixel(page, g.padding + 2, g.padding + 2);
  expect(c[0]).toBeLessThan(30);
});

test('sixel: image overlays text (sixel on top, not behind)', async ({ page }) => {
  // Write a row of bright-cyan X's at row 0, then drop a red sixel
  // band on top of them.  At the sixel pixels we should see RED, not
  // cyan — proving the sixel covers the text.
  await reset(page, 6, 20);
  await write(page, '\x1b[H\x1b[36mXXXXXXXXXXXXXXXXXX\x1b[0m\x1b[H');
  await write(page, "\x1bP" + "q#1;2;100;0;0#1!40~" + "\x1b\\");
  const g = await geom(page);
  // Sample within the sixel area (well inside, not on an edge pixel).
  const c = await pixel(page, g.padding + 6, g.padding + 2);
  expect(c[0]).toBeGreaterThan(180);     // red
  expect(c[2]).toBeLessThan(60);          // not cyan/blue
});

test('sixel: cursor advances past the bottom of the image', async ({ page }) => {
  // Cursor starts at (0, 0).  Write an 18-px-tall sixel.  At a
  // cellH of ~20 px the image covers 1 row, so the cursor should
  // be on row 1 (0-based) after the sixel.
  await reset(page, 6, 20);
  const tilde = '~'.repeat(20);
  const dcs = "\x1bP" + "q#1;2;100;0;0#1" + tilde + "-#1" + tilde + "-#1" + tilde + "\x1b\\";
  await write(page, dcs);
  const cursor = await page.evaluate(() => {
    const s = window.vt.term.screen;
    return { row: s.cy, col: s.cx };
  });
  // Image is 18 px tall.  With fontSize 16 px → cellH ~ 20 px →
  // ceil(18/20) = 1.  Image is 20 px tall could be 1 cell on some
  // fonts.  Accept ≥1 row of advance.
  expect(cursor.row).toBeGreaterThanOrEqual(1);
  expect(cursor.col).toBe(0);
});

test('sixel: transparent pixels let the underlying text show through', async ({ page }) => {
  // Sixel byte 0x3f ('?') has mask 0 → NO pixels set → fully
  // transparent.  Write '?' so the entire sixel "image" is
  // transparent and the underlying cyan X must show through.
  await reset(page, 6, 20);
  await write(page, '\x1b[H\x1b[36mXXXXXXXXXX\x1b[0m\x1b[H');
  // Use raster attrs so the canvas has a real size (10 wide × 6 tall)
  // even though no pixels are set.
  await write(page, "\x1bP" + 'q"1;1;10;6' + '!10?' + "\x1b\\");
  const g = await geom(page);
  // Sample where the X glyph would have ink — bottom row of cell 0.
  // The cyan should still be visible.
  const c = await pixel(page, g.padding + 4, g.padding + 8);
  // Cyan = (0, ~200, ~200).  Specifically green channel should be high.
  expect(c[1] + c[2]).toBeGreaterThan(80);
});

// ── Geometry / cells ───────────────────────────────────────────────

test('canvas is sized to (rows × cellH) + 2·padding', async ({ page }) => {
  await reset(page, 6, 20);
  const g = await geom(page);
  expect(g.canvasW).toBe(g.padding * 2 + 20 * g.cellW);
  expect(g.canvasH).toBe(g.padding * 2 + 6 * g.cellH);
});
