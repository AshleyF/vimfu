/**
 * Drive the live demo page with Playwright, click each demo button,
 * and dump a PNG of the canvas after each click.  This lets me
 * actually *see* what the user sees and validate rendering bugs.
 *
 * Run with:  node test/capture_demos.js
 * Writes:    test/screenshots/<id>.png
 */

import { chromium } from '@playwright/test';
import path from 'node:path';
import fs from 'node:fs';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const OUT_DIR = path.join(__dirname, 'screenshots');
fs.mkdirSync(OUT_DIR, { recursive: true });

const URL_BASE = process.env.VT_URL || 'http://127.0.0.1:8000';

const BUTTONS = [
  'demo-hello',
  'demo-colors',
  'demo-sgr',
  'demo-boxes',
  'demo-wrap',
  'demo-scroll-region',
  'demo-sixel-flag',
  'demo-sixel-gradient',
  'demo-sixel-pattern',
  'demo-sixel-snake',
  'demo-sixel-me',
  'demo-sixel-3color',
];

(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({
    viewport: { width: 1280, height: 800 },
    deviceScaleFactor: 1,
  });
  const page = await ctx.newPage();

  console.log(`[capture] opening ${URL_BASE}/index.html`);
  await page.goto(`${URL_BASE}/index.html`, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts && document.fonts.ready);

  // Baseline empty-screen snapshot
  await page.locator('#term').screenshot({
    path: path.join(OUT_DIR, '00-baseline.png'),
  });

  for (const id of BUTTONS) {
    // Reset before each demo so they don't pile up.
    await page.click('#demo-reset');
    await page.waitForTimeout(120);
    await page.click(`#${id}`);
    // The sixel fixtures fetch from disk asynchronously, so give them
    // time to land before capturing.
    await page.waitForTimeout(id.includes('snake') ? 1500 : 400);
    const out = path.join(OUT_DIR, `${id}.png`);
    await page.locator('#term').screenshot({ path: out });
    console.log(`  ${id} → ${path.relative(process.cwd(), out)}`);
  }

  // Whole-page screenshot at a couple of sizes, to verify the auto-fit
  // logic and the "actual terminal area" outline behaviour.
  for (const [w, h] of [[1280, 800], [1600, 1000], [900, 500]]) {
    await page.setViewportSize({ width: w, height: h });
    await page.waitForTimeout(200);
    await page.click('#demo-reset');
    await page.click('#demo-hello');
    await page.waitForTimeout(120);
    const out = path.join(OUT_DIR, `autofit-${w}x${h}.png`);
    await page.screenshot({ path: out });
    console.log(`  autofit ${w}x${h} → ${path.relative(process.cwd(), out)}`);
  }

  await browser.close();
  console.log('[capture] done');
})();
