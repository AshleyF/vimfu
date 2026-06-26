/**
 * Demo-button tests.  Drive the live demo page (index.html), click
 * each button, and verify the resulting canvas contains the expected
 * content.  Catches "demo author wrote the wrong escape codes"-class
 * bugs that the engine/renderer tests can't.
 */

import { test, expect } from '@playwright/test';

test.beforeEach(async ({ page }) => {
  await page.goto('/index.html', { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts && document.fonts.ready);
  // Hide the cursor so we don't get cursor-blink polluting pixel samples.
  await page.evaluate(() => {
    window.term.screen.cursorVisible = false;
    window.ren.draw(window.term.toFrame());
  });
});

async function clickAndSettle(page, id) {
  await page.click('#demo-reset');
  await page.waitForTimeout(50);
  // Hide cursor again after reset.
  await page.evaluate(() => {
    window.term.screen.cursorVisible = false;
    window.ren.draw(window.term.toFrame());
  });
  await page.click(`#${id}`);
  await page.waitForTimeout(150);
  await page.evaluate(() => {
    window.term.screen.cursorVisible = false;
    window.ren.draw(window.term.toFrame());
  });
}

async function screenText(page) {
  return page.evaluate(() =>
    window.term.toFrame().lines.map(l => l.text).join('\n'));
}

async function pixelAt(page, x, y) {
  return page.evaluate(({x,y}) => {
    const c = document.getElementById('term');
    const ctx = c.getContext('2d');
    return Array.from(ctx.getImageData(x, y, 1, 1).data);
  }, { x, y });
}

async function brightestIn(page, x, y, w, h) {
  return page.evaluate(({x,y,w,h}) => {
    const ctx = document.getElementById('term').getContext('2d');
    const img = ctx.getImageData(x, y, w, h).data;
    let bestR = 0, bestG = 0, bestB = 0;
    for (let i = 0; i < img.length; i += 4) {
      if (img[i]   > bestR) bestR = img[i];
      if (img[i+1] > bestG) bestG = img[i+1];
      if (img[i+2] > bestB) bestB = img[i+2];
    }
    return { r: bestR, g: bestG, b: bestB };
  }, { x, y, w, h });
}

// ──────────────────────────────────────────────────────────────────

test('demo: Hello, terminal! writes the literal text', async ({ page }) => {
  await clickAndSettle(page, 'demo-hello');
  const text = await screenText(page);
  expect(text).toMatch(/Hello, terminal!/);
});

test('demo: DEC line drawing — text inside the box is not translated', async ({ page }) => {
  await clickAndSettle(page, 'demo-boxes');
  const text = await screenText(page);
  // The "hello world" and "abcdefghijkl" lines must appear LITERALLY —
  // not as the DEC-special-graphics translations of those letters.
  expect(text).toMatch(/hello world/);
  expect(text).toMatch(/abcdefghijkl/);
  // The text MUST NOT contain any "symbol for X" Unicode glyphs from
  // the U+2400 control-symbol range, which would mean the charset
  // switch leaked into the text.
  expect(text).not.toMatch(/[\u2400-\u2426]/);
});

test('demo: DEC line drawing — corners actually paint', async ({ page }) => {
  await clickAndSettle(page, 'demo-boxes');
  // The top border row should contain horizontal line ink that spans
  // across multiple cells.  Sample a horizontal strip near the top of
  // the canvas and require white ink across the whole width.
  const ink = await page.evaluate(() => {
    const c = document.getElementById('term');
    const ctx = c.getContext('2d');
    // Find the leftmost cell border by scanning the first ~12 rows of
    // pixels for any white run.
    const img = ctx.getImageData(0, 0, c.width, 40).data;
    let lit = 0;
    for (let i = 0; i < img.length; i += 4) {
      if (img[i] > 150 && img[i+1] > 150 && img[i+2] > 150) lit++;
    }
    return lit;
  });
  expect(ink).toBeGreaterThan(50);
});

test('demo: color palette renders distinct ANSI colors', async ({ page }) => {
  await clickAndSettle(page, 'demo-colors');
  // Hunt for at least one strongly-red, strongly-green and strongly-blue
  // pixel anywhere on the canvas.
  const found = await page.evaluate(() => {
    const c = document.getElementById('term');
    const ctx = c.getContext('2d');
    const img = ctx.getImageData(0, 0, c.width, c.height).data;
    let r = false, g = false, b = false;
    for (let i = 0; i < img.length; i += 4) {
      const R = img[i], G = img[i+1], B = img[i+2];
      if (R > 180 && G < 80  && B < 80)  r = true;
      if (G > 180 && R < 80  && B < 80)  g = true;
      if (B > 180 && R < 80  && G < 80)  b = true;
    }
    return { r, g, b };
  });
  expect(found.r).toBe(true);
  expect(found.g).toBe(true);
  expect(found.b).toBe(true);
});

test('demo: SGR bold/italic/underline writes the labels', async ({ page }) => {
  await clickAndSettle(page, 'demo-sgr');
  const text = await screenText(page);
  expect(text).toMatch(/bold/);
  expect(text).toMatch(/italic/);
  expect(text).toMatch(/underline/);
  expect(text).toMatch(/reverse/);
});

test('demo: sixel tricolor flag paints distinct red/white/blue bands', async ({ page }) => {
  await clickAndSettle(page, 'demo-sixel-flag');
  // Sample three vertical strips inside the flag image.  The image is
  // at the cursor origin: roughly (padding+pad_x, padding+y).
  const r = await brightestIn(page, 8, 8, 4, 3);   // top band: red
  const w = await brightestIn(page, 8, 14, 4, 3);  // middle band: white
  const b = await brightestIn(page, 8, 20, 4, 3);  // bottom band: blue
  expect(r.r).toBeGreaterThan(150);
  expect(w.r).toBeGreaterThan(200); expect(w.g).toBeGreaterThan(200); expect(w.b).toBeGreaterThan(200);
  expect(b.b).toBeGreaterThan(150);
});

test('demo: sixel gradient paints red→green→blue stripes', async ({ page }) => {
  await clickAndSettle(page, 'demo-sixel-gradient');
  // Find at least one strong red, green and blue pixel.
  const found = await page.evaluate(() => {
    const c = document.getElementById('term');
    const ctx = c.getContext('2d');
    const img = ctx.getImageData(0, 0, 200, 30).data;
    let r = false, g = false, b = false;
    for (let i = 0; i < img.length; i += 4) {
      const R = img[i], G = img[i+1], B = img[i+2];
      if (R > 150 && G < 80  && B < 80)  r = true;
      if (G > 150 && R < 80  && B < 80)  g = true;
      if (B > 150 && R < 80  && G < 80)  b = true;
    }
    return { r, g, b };
  });
  expect(found.r).toBe(true);
  expect(found.g).toBe(true);
  expect(found.b).toBe(true);
});

test('demo: sixel sphere has a roughly-circular shaded region', async ({ page }) => {
  await clickAndSettle(page, 'demo-sixel-pattern');
  // The sphere is ~120×120 px at the top-left.  Sample a 130×130 box
  // and count lit (grey) pixels — expect "circle area ≈ πr²" within
  // an order of magnitude.
  const lit = await page.evaluate(() => {
    const c = document.getElementById('term');
    const ctx = c.getContext('2d');
    const img = ctx.getImageData(0, 0, 130, 130).data;
    let n = 0;
    for (let i = 0; i < img.length; i += 4) {
      if (img[i] > 20 || img[i+1] > 20 || img[i+2] > 20) n++;
    }
    return n;
  });
  // A circle of radius ~56 has area ≈ π·56² ≈ 9847.  Accept a wide
  // range to allow for cursor and any residual UI bits.
  expect(lit).toBeGreaterThan(5000);
  expect(lit).toBeLessThan(15000);
});

// ── Real-world sixel fixtures (csdvrx/sixel-testsuite) ────────────

test('demo: snake.six renders as a 600×450 colourful photo', async ({ page }) => {
  await clickAndSettle(page, 'demo-sixel-snake');
  // Wait for fetch + decode + render to settle.
  await page.waitForTimeout(800);
  await page.evaluate(() => {
    window.term.screen.cursorVisible = false;
    window.ren.draw(window.term.toFrame());
  });

  // The snake image is anchored at (cursor row 0, col 0).  Sample a
  // 400×300 area and require lots of distinct non-black pixels.
  const { lit, colors } = await page.evaluate(() => {
    const c = document.getElementById('term');
    const ctx = c.getContext('2d');
    const img = ctx.getImageData(0, 0, 400, 300).data;
    let n = 0;
    const seen = new Set();
    for (let i = 0; i < img.length; i += 4) {
      if (img[i] > 10 || img[i+1] > 10 || img[i+2] > 10) {
        n++;
        // Quantise to ~5-bit per channel so the set doesn't blow up
        const k = (img[i] >> 3) << 10 | (img[i+1] >> 3) << 5 | (img[i+2] >> 3);
        seen.add(k);
      }
    }
    return { lit: n, colors: seen.size };
  });
  expect(lit).toBeGreaterThan(50_000);     // lots of pixels lit
  expect(colors).toBeGreaterThan(200);     // many distinct colours
});

test('demo: 3-sixel test pattern shows three distinct colour bands', async ({ page }) => {
  await clickAndSettle(page, 'demo-sixel-3color');
  await page.waitForTimeout(300);
  await page.evaluate(() => {
    window.term.screen.cursorVisible = false;
    window.ren.draw(window.term.toFrame());
  });
  // The pattern is a small grid of 8 colours, 3 bands tall.  Within
  // a ~95×20 area we should see many distinct colours.
  const colors = await page.evaluate(() => {
    const c = document.getElementById('term');
    const ctx = c.getContext('2d');
    const img = ctx.getImageData(0, 0, 110, 30).data;
    const seen = new Set();
    for (let i = 0; i < img.length; i += 4) {
      if (img[i] > 10 || img[i+1] > 10 || img[i+2] > 10) {
        const k = (img[i] >> 3) << 10 | (img[i+1] >> 3) << 5 | (img[i+2] >> 3);
        seen.add(k);
      }
    }
    return seen.size;
  });
  expect(colors).toBeGreaterThanOrEqual(5);
});

// ── Auto-fit and zoom ───────────────────────────────────────────────

test('autofit: terminal grows when the viewport gets larger', async ({ page }) => {
  await page.setViewportSize({ width: 900, height: 500 });
  await page.waitForTimeout(150);
  const small = await page.evaluate(() => ({
    rows: window.term.screen.rows,
    cols: window.term.screen.cols,
  }));

  await page.setViewportSize({ width: 1600, height: 1000 });
  await page.waitForTimeout(200);
  const big = await page.evaluate(() => ({
    rows: window.term.screen.rows,
    cols: window.term.screen.cols,
  }));

  expect(big.rows).toBeGreaterThan(small.rows);
  expect(big.cols).toBeGreaterThan(small.cols);
});

test('autofit: terminal fills the pane within one cell of slack', async ({ page }) => {
  await page.setViewportSize({ width: 1200, height: 700 });
  await page.waitForTimeout(200);
  const m = await page.evaluate(() => {
    const main = document.querySelector('main');
    const cs = getComputedStyle(main);
    const padX = parseFloat(cs.paddingLeft) + parseFloat(cs.paddingRight);
    const padY = parseFloat(cs.paddingTop)  + parseFloat(cs.paddingBottom);
    return {
      availW: main.clientWidth  - padX,
      availH: main.clientHeight - padY,
      cellW: window.ren.cellW,
      cellH: window.ren.cellH,
      padding: window.ren.padding,
      canvasW: document.getElementById('term').clientWidth,
      canvasH: document.getElementById('term').clientHeight,
    };
  });
  // Canvas should fit within pane AND have at most one cell of unused
  // space in each axis (autofit takes the largest integer that fits).
  expect(m.canvasW).toBeLessThanOrEqual(m.availW);
  expect(m.canvasH).toBeLessThanOrEqual(m.availH);
  expect(m.availW - m.canvasW).toBeLessThan(m.cellW + 1);
  expect(m.availH - m.canvasH).toBeLessThan(m.cellH + 1);
});

test('zoom: A+ button increases cell size and reduces cols', async ({ page }) => {
  await page.setViewportSize({ width: 1200, height: 700 });
  await page.waitForTimeout(200);
  const before = await page.evaluate(() => ({
    cellW: window.ren.cellW,
    cellH: window.ren.cellH,
    cols: window.term.screen.cols,
    rows: window.term.screen.rows,
  }));
  await page.click('#zoom-in');
  await page.waitForTimeout(150);
  const after = await page.evaluate(() => ({
    cellW: window.ren.cellW,
    cellH: window.ren.cellH,
    cols: window.term.screen.cols,
    rows: window.term.screen.rows,
  }));
  expect(after.cellW).toBeGreaterThan(before.cellW);
  expect(after.cellH).toBeGreaterThan(before.cellH);
  expect(after.cols).toBeLessThan(before.cols);
  expect(after.rows).toBeLessThan(before.rows);
});

test('zoom: A- button reduces cell size and grows cols', async ({ page }) => {
  await page.setViewportSize({ width: 1200, height: 700 });
  await page.waitForTimeout(200);
  const before = await page.evaluate(() => ({
    cellW: window.ren.cellW,
    cols: window.term.screen.cols,
  }));
  await page.click('#zoom-out');
  await page.waitForTimeout(150);
  const after = await page.evaluate(() => ({
    cellW: window.ren.cellW,
    cols: window.term.screen.cols,
  }));
  expect(after.cellW).toBeLessThan(before.cellW);
  expect(after.cols).toBeGreaterThan(before.cols);
});

test('zoom: 100% button restores the default size', async ({ page }) => {
  await page.setViewportSize({ width: 1200, height: 700 });
  await page.waitForTimeout(200);
  const orig = await page.evaluate(() => window.ren.fontSize);
  // Zoom in twice, then reset
  await page.click('#zoom-in'); await page.waitForTimeout(80);
  await page.click('#zoom-in'); await page.waitForTimeout(80);
  await page.click('#zoom-reset'); await page.waitForTimeout(120);
  const after = await page.evaluate(() => window.ren.fontSize);
  expect(after).toBe(orig);
});

test('zoom: sixel integer-scales with the font (crisp pixels)', async ({ page }) => {
  await page.setViewportSize({ width: 1200, height: 700 });
  await page.waitForTimeout(200);
  // Reset, hide cursor, then drop a red sixel band.
  await page.click('#demo-reset');
  await page.evaluate(() => {
    window.term.screen.cursorVisible = false;
    window.ren.draw(window.term.toFrame());
  });
  await page.click('#demo-sixel-flag');
  await page.waitForTimeout(120);
  const before = await page.evaluate(() => ({
    scale: window.ren.sixelScale,
    px: window.ren.fontSize,
  }));

  // Zoom in twice → font ~20 px → scale should bump to 2 at some
  // point between 16 and 24 px (Math.round(px/16)).
  await page.click('#zoom-in'); await page.waitForTimeout(80);
  await page.click('#zoom-in'); await page.waitForTimeout(80);
  await page.click('#zoom-in'); await page.waitForTimeout(80);
  await page.click('#zoom-in'); await page.waitForTimeout(120);

  const after = await page.evaluate(() => ({
    scale: window.ren.sixelScale,
    px: window.ren.fontSize,
  }));
  expect(after.px).toBeGreaterThan(before.px);
  expect(after.scale).toBeGreaterThan(before.scale);
  expect(Number.isInteger(after.scale)).toBe(true);
});
