// Visual proof: zoom in on the snake and verify the bitmap stays
// crisp (no blur) and grows as N×N integer multiples.
import { chromium } from '@playwright/test';
import path from 'node:path';
import fs from 'node:fs';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(__dirname, 'screenshots');
fs.mkdirSync(OUT, { recursive: true });

const browser = await chromium.launch();
const ctx = await browser.newContext({
  viewport: { width: 1600, height: 1000 },
  deviceScaleFactor: 2,        // simulate a Retina display
});
const page = await ctx.newPage();
await page.goto('http://127.0.0.1:8000/index.html', { waitUntil: 'networkidle' });
await page.evaluate(() => document.fonts && document.fonts.ready);
await page.evaluate(() => {
  window.term.screen.cursorVisible = false;
  window.ren.draw(window.term.toFrame());
});

// Snake at default zoom (sixelScale=1, dpr=2).
await page.click('#demo-sixel-snake');
await page.waitForTimeout(1500);
await page.locator('#term').screenshot({ path: path.join(OUT, 'snake-zoom-1x-dpr2.png') });
console.log('1× zoom, dpr=2:', await page.evaluate(() =>
  'fontSize=' + window.ren.fontSize +
  '  sixelScale=' + window.ren.sixelScale +
  '  cell=' + window.ren.cellW + 'x' + window.ren.cellH));

// Zoom in 4 times → 24 px font → sixelScale ≈ round(24/16) = 2.
for (let i = 0; i < 4; i++) {
  await page.click('#zoom-in');
  await page.waitForTimeout(80);
}
// Re-render the snake from the original sixel data — sixels added
// to ren.sixels keep their original bitmap, so the blit just scales.
await page.evaluate(() => window.ren.draw(window.term.toFrame()));
await page.waitForTimeout(150);
await page.locator('#term').screenshot({ path: path.join(OUT, 'snake-zoom-2x-dpr2.png') });
console.log('2× zoom, dpr=2:', await page.evaluate(() =>
  'fontSize=' + window.ren.fontSize +
  '  sixelScale=' + window.ren.sixelScale +
  '  cell=' + window.ren.cellW + 'x' + window.ren.cellH));

await browser.close();
console.log('done');
