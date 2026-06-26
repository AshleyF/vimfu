// Render colour-palette + text at dpr=2 to verify high-DPI text and
// sixel pixels both come out crisp.
import { chromium } from '@playwright/test';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(__dirname, 'screenshots');

const browser = await chromium.launch();
const ctx = await browser.newContext({
  viewport: { width: 1200, height: 800 },
  deviceScaleFactor: 2,
});
const page = await ctx.newPage();
await page.goto('http://127.0.0.1:8000/index.html', { waitUntil: 'networkidle' });
await page.evaluate(() => document.fonts && document.fonts.ready);
await page.evaluate(() => {
  window.term.screen.cursorVisible = false;
  window.ren.draw(window.term.toFrame());
});
await page.click('#demo-colors');
await page.waitForTimeout(300);
await page.evaluate(() => {
  window.term.screen.cursorVisible = false;
  window.ren.draw(window.term.toFrame());
});

const reported = await page.evaluate(() => ({
  dpr: window.devicePixelRatio,
  canvasW: document.getElementById('term').width,
  canvasH: document.getElementById('term').height,
  cssW: parseFloat(document.getElementById('term').style.width),
  cssH: parseFloat(document.getElementById('term').style.height),
}));
console.log('dpr=' + reported.dpr,
            'canvas pixels=' + reported.canvasW + 'x' + reported.canvasH,
            'css=' + reported.cssW + 'x' + reported.cssH);

await page.locator('#term').screenshot({ path: path.join(OUT, 'highdpi-text.png') });
await browser.close();
console.log('done');
