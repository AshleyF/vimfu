// One-off: prove the sixel overlay now sits *on top of* text.
import { chromium } from '@playwright/test';
import path from 'node:path';
import fs from 'node:fs';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(__dirname, 'screenshots');
fs.mkdirSync(OUT, { recursive: true });

const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 600, height: 200 }, deviceScaleFactor: 1 });
const page = await ctx.newPage();
await page.goto('http://127.0.0.1:8000/index.html', { waitUntil: 'networkidle' });
await page.evaluate(() => document.fonts && document.fonts.ready);

await page.click('#demo-reset');
await page.waitForTimeout(50);

// Fill the area with cyan text first.
await page.evaluate(() => {
  window.term.write('\x1b[H');
  for (let r = 0; r < 4; r++) {
    window.term.write('\x1b[33mTEXT BEHIND THE SIXEL ' + '\x1b[0m\r\n');
  }
  window.term.write('\x1b[H');
  // Drop a red sixel band on top
  const tilde = '~'.repeat(80);
  window.term.write('\x1bPq#1;2;100;0;0#1' + tilde + '-#1' + tilde + '\x1b\\');
  window.ren.draw(window.term.toFrame());
});
await page.waitForTimeout(150);
await page.locator('#term').screenshot({ path: path.join(OUT, 'overlay-test.png') });
await browser.close();
console.log('wrote', path.relative(process.cwd(), path.join(OUT, 'overlay-test.png')));
