/**
 * Visual / canvas-rendering tests that go beyond the basic 17 in
 * render.pw.test.js — sweep across font sizes and verify the
 * cellH-multiple-of-(6×sixelScale) invariant + that sixel bands
 * always tile cleanly into character rows.
 */

import { test, expect } from '@playwright/test';

test.beforeEach(async ({ page }) => {
  await page.goto('/index.html', { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts && document.fonts.ready);
  await page.evaluate(() => {
    window.term.screen.cursorVisible = false;
    window.ren.draw(window.term.toFrame());
  });
});

test('cellH is always a multiple of (6 × sixelScale) at every font size', async ({ page }) => {
  await page.setViewportSize({ width: 1600, height: 1000 });
  await page.waitForTimeout(150);

  for (const px of [8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 36, 40]) {
    const result = await page.evaluate((size) => {
      window.setFontSize(size);
      return {
        font: window.ren.fontSize,
        cellH: window.ren.cellH,
        sixelScale: window.ren.sixelScale,
        step: 6 * window.ren.sixelScale,
      };
    }, px);

    expect(result.cellH % result.step).toBe(0);
    expect(result.cellH).toBeGreaterThanOrEqual(result.step);
  }
});

test('sixel band height (6×scale) divides cellH for any zoom level', async ({ page }) => {
  await page.setViewportSize({ width: 1600, height: 1000 });
  await page.waitForTimeout(150);

  // Zoom from min to max and verify the invariant at every step.
  for (let i = 0; i < 15; i++) {
    await page.click('#zoom-in');
    await page.waitForTimeout(30);
    const { cellH, scale, step } = await page.evaluate(() => ({
      cellH: window.ren.cellH,
      scale: window.ren.sixelScale,
      step: 6 * window.ren.sixelScale,
    }));
    expect(cellH % step).toBe(0);
  }
});

test('sixel bitmap remains crisp at 3x zoom (no anti-alias blur)', async ({ page }) => {
  await page.setViewportSize({ width: 1600, height: 1000 });
  await page.click('#demo-reset');
  await page.evaluate(() => {
    window.term.screen.cursorVisible = false;
  });
  // Drop a 60×6 red-only sixel band, very predictable.
  await page.evaluate(() => {
    const tilde = '~'.repeat(60);
    window.term.write('\x1bPq#1;2;100;0;0#1' + tilde + '\x1b\\');
    window.term.screen.cursorVisible = false;
    window.ren.draw(window.term.toFrame());
  });
  await page.waitForTimeout(120);

  // Zoom up — each click bumps font by 2 px.  Three clicks → 22 px →
  // sixelScale still 1; four clicks → 24 → scale = 2.  Force scale ≥ 2.
  for (let i = 0; i < 8; i++) {
    await page.click('#zoom-in');
    await page.waitForTimeout(40);
  }
  await page.evaluate(() => {
    window.term.screen.cursorVisible = false;
    window.ren.draw(window.term.toFrame());
  });

  // Sample very close to the canvas origin so we're guaranteed inside
  // the red band whatever the scale.  At scale=N the band occupies
  // [padding, padding + 6*N) device pixels.  padding=6, scale ≥ 2 →
  // band reaches y=18.  Sample at (10, 8): inside red.
  const { sixelScale, pixel } = await page.evaluate(() => {
    const c = document.getElementById('term');
    const ctx = c.getContext('2d');
    const data = ctx.getImageData(10, 8, 1, 1).data;
    return {
      sixelScale: window.ren.sixelScale,
      pixel: Array.from(data),
    };
  });

  expect(sixelScale).toBeGreaterThanOrEqual(2);
  expect(pixel[0]).toBeGreaterThan(200);   // red is on
  expect(pixel[1]).toBeLessThan(80);       // green is off
  expect(pixel[2]).toBeLessThan(80);       // blue is off
});

test('many text rows render their content without artefacts', async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 800 });
  await page.evaluate(() => {
    // Write a numbered line per row.
    const rows = window.term.screen.rows;
    for (let i = 0; i < rows; i++) {
      window.term.write(`row-${String(i).padStart(2, '0')}-test\r\n`);
    }
    window.term.screen.cursorVisible = false;
    window.ren.draw(window.term.toFrame());
  });

  const lines = await page.evaluate(() =>
    window.term.toFrame().lines.map(l => l.text.trimEnd()));

  // Each line we wrote should still be present (some early ones may
  // have scrolled off the top; check that the visible rows are
  // sequentially numbered).
  let prev = -1;
  for (const line of lines) {
    const m = line.match(/^row-(\d+)-test$/);
    if (m) {
      const n = +m[1];
      if (prev !== -1) expect(n).toBe(prev + 1);
      prev = n;
    }
  }
  expect(prev).toBeGreaterThan(0);
});

test('keyboard zoom shortcut Ctrl-= increases font', async ({ page }) => {
  await page.setViewportSize({ width: 1200, height: 700 });
  await page.waitForTimeout(150);
  const before = await page.evaluate(() => window.ren.fontSize);
  await page.keyboard.press('Control+=');
  await page.waitForTimeout(100);
  const after = await page.evaluate(() => window.ren.fontSize);
  expect(after).toBeGreaterThan(before);
});

test('keyboard zoom shortcut Ctrl-0 resets font', async ({ page }) => {
  await page.setViewportSize({ width: 1200, height: 700 });
  await page.waitForTimeout(150);
  const orig = await page.evaluate(() => window.ren.fontSize);
  await page.click('#zoom-in'); await page.waitForTimeout(50);
  await page.click('#zoom-in'); await page.waitForTimeout(50);
  await page.keyboard.press('Control+0');
  await page.waitForTimeout(100);
  const after = await page.evaluate(() => window.ren.fontSize);
  expect(after).toBe(orig);
});

test('status bar updates after auto-fit', async ({ page }) => {
  await page.setViewportSize({ width: 1600, height: 1000 });
  await page.waitForTimeout(200);
  const big = await page.locator('#size-info').textContent();
  expect(big).toMatch(/\d+×\d+/);

  await page.setViewportSize({ width: 700, height: 400 });
  await page.waitForTimeout(200);
  const small = await page.locator('#size-info').textContent();
  expect(small).toMatch(/\d+×\d+/);
  expect(small).not.toBe(big);
});
