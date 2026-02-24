/**
 * VimFu Simulator – Ground-Truth Comparison Tests (v2)
 *
 * Reads ground truth JSON files (per-suite or combined) and replays
 * each case through the VimFu simulator engine, comparing output.
 *
 * Usage:
 *   node test/compare_test_v2.js                          # run all suites
 *   node test/compare_test_v2.js --suite motions_basic     # run one suite
 *   node test/compare_test_v2.js --case h_basic            # run one case (searches all suites)
 *   node test/compare_test_v2.js --suite motions_basic --case h_basic
 *   node test/compare_test_v2.js --legacy                  # run old ground_truth.json too
 */

import { readFileSync, readdirSync, existsSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';
import { VimEngine } from '../src/engine.js';
import { Screen } from '../src/screen.js';

const __dirname = dirname(fileURLToPath(import.meta.url));
const LEGACY_PATH = resolve(__dirname, 'ground_truth.json');

// ── Parse args ──
const args = process.argv.slice(2);
let filterSuite = null;
let filterCase = null;
let includeLegacy = false;
let skipColors = false;
for (let i = 0; i < args.length; i++) {
  if (args[i] === '--suite' && args[i + 1]) filterSuite = args[++i];
  else if (args[i] === '--case' && args[i + 1]) filterCase = args[++i];
  else if (args[i] === '--legacy') includeLegacy = true;
  else if (args[i] === '--no-color') skipColors = true;
}

// ── Discover ground truth files ──
function loadSuites() {
  const suites = {};

  // Load per-suite files: ground_truth_<suite>.json
  const files = readdirSync(__dirname)
    .filter(f => f.startsWith('ground_truth_') && f.endsWith('.json') && f !== 'ground_truth_all.json')
    .sort();

  for (const file of files) {
    const suiteName = file.replace('ground_truth_', '').replace('.json', '');
    if (filterSuite && suiteName !== filterSuite) continue;
    const data = JSON.parse(readFileSync(resolve(__dirname, file), 'utf-8'));
    suites[suiteName] = data;
  }

  // Optionally include legacy ground_truth.json
  if (includeLegacy && existsSync(LEGACY_PATH)) {
    const data = JSON.parse(readFileSync(LEGACY_PATH, 'utf-8'));
    suites['_legacy'] = data;
  }

  return suites;
}

// ── Helpers ──
function feedKeys(engine, keys) {
  let i = 0;
  while (i < keys.length) {
    const ch = keys[i];
    let key = ch;
    if (ch === '\x1b') {
      // Check for escape sequences (arrow keys, Delete, etc.)
      if (i + 2 < keys.length && keys[i + 1] === '[') {
        const code = keys[i + 2];
        if (code === 'A') { engine.feedKey('ArrowUp'); i += 3; continue; }
        if (code === 'B') { engine.feedKey('ArrowDown'); i += 3; continue; }
        if (code === 'C') { engine.feedKey('ArrowRight'); i += 3; continue; }
        if (code === 'D') { engine.feedKey('ArrowLeft'); i += 3; continue; }
        if (code === '3' && i + 3 < keys.length && keys[i + 3] === '~') {
          engine.feedKey('Delete'); i += 4; continue;
        }
      }
      key = 'Escape';
    }
    else if (ch === '\r' || ch === '\n') key = 'Enter';
    else if (ch === '\x08' || ch === '\x7f') key = 'Backspace';
    else if (ch === '\x01') key = 'Ctrl-A';
    else if (ch === '\x02') key = 'Ctrl-B';
    else if (ch === '\x04') key = 'Ctrl-D';
    else if (ch === '\x05') key = 'Ctrl-E';
    else if (ch === '\x06') key = 'Ctrl-F';
    else if (ch === '\x07') key = 'Ctrl-G';
    else if (ch === '\x09') key = 'Tab';
    else if (ch === '\x0f') key = 'Ctrl-O';
    else if (ch === '\x12') key = 'Ctrl-R';
    else if (ch === '\x15') key = 'Ctrl-U';
    else if (ch === '\x17') key = 'Ctrl-W';
    else if (ch === '\x18') key = 'Ctrl-X';
    else if (ch === '\x19') key = 'Ctrl-Y';
    engine.feedKey(key);
    i++;
  }
}

function diffLines(expected, actual) {
  const diffs = [];
  const maxLen = Math.max(expected.length, actual.length);
  for (let i = 0; i < maxLen; i++) {
    const e = expected[i] ?? '<missing>';
    const a = actual[i] ?? '<missing>';
    if (e !== a) {
      diffs.push({ row: i, expected: JSON.stringify(e), actual: JSON.stringify(a) });
    }
  }
  return diffs;
}

/**
 * Compare runs (fg/bg colours) between ground truth and sim for text rows.
 * Returns array of {row, expected, actual} objects for mismatched rows.
 */
function diffRuns(gtFrame, simFrame, textRows) {
  const diffs = [];
  const numRows = Math.min(textRows, gtFrame.lines.length, simFrame.lines.length);
  for (let i = 0; i < numRows; i++) {
    const gtRuns = gtFrame.lines[i].runs;
    const simRuns = simFrame.lines[i].runs;
    // Compare serialised runs (fg, bg, n)
    const gtStr = gtRuns.map(r => `${r.n}:${r.fg}/${r.bg}`).join(' ');
    const simStr = simRuns.map(r => `${r.n}:${r.fg}/${r.bg}`).join(' ');
    if (gtStr !== simStr) {
      diffs.push({ row: i, expected: gtStr, actual: simStr });
    }
  }
  // Also compare status line (row textRows) and command line (row textRows+1)
  for (let i = textRows; i < Math.min(textRows + 2, gtFrame.lines.length, simFrame.lines.length); i++) {
    const gtRuns = gtFrame.lines[i].runs;
    const simRuns = simFrame.lines[i].runs;
    const gtStr = gtRuns.map(r => `${r.n}:${r.fg}/${r.bg}`).join(' ');
    const simStr = simRuns.map(r => `${r.n}:${r.fg}/${r.bg}`).join(' ');
    if (gtStr !== simStr) {
      const label = i === textRows ? 'status' : 'cmdline';
      diffs.push({ row: label, expected: gtStr, actual: simStr });
    }
  }
  return diffs;
}

// ── Run tests ──
const ROWS = 20;
const COLS = 40;

const suites = loadSuites();
if (Object.keys(suites).length === 0) {
  console.error('No ground truth files found!');
  console.error('Run: python test/nvim_ground_truth_v2.py');
  process.exit(1);
}

let totalPassed = 0;
let totalFailed = 0;
let totalSkipped = 0;
const allFailures = [];

for (const [suiteName, cases] of Object.entries(suites)) {
  const caseEntries = Object.entries(cases);
  let suitePassed = 0;
  let suiteFailed = 0;
  let suiteSkipped = 0;

  console.log(`\n${'='.repeat(60)}`);
  console.log(`Suite: ${suiteName} (${caseEntries.length} cases)`);
  console.log(`${'='.repeat(60)}`);

  for (const [name, gt] of caseEntries) {
    if (filterCase && name !== filterCase) {
      suiteSkipped++;
      continue;
    }

    if (gt.error) {
      console.log(`  SKIP  ${name} (ground truth error)`);
      suiteSkipped++;
      continue;
    }

    if (gt.skip) {
      console.log(`  SKIP  ${name} (${gt.skip})`);
      suiteSkipped++;
      continue;
    }

    // Run through sim engine
    const engine = new VimEngine({ rows: ROWS, cols: COLS });
    if (gt.initialContent) {
      engine.loadFile(gt.initialContent);
    }
    feedKeys(engine, gt.keys);

    const screen = new Screen(ROWS, COLS, 'monokai');
    const frame = screen.render(engine);
    const simTextLines = frame.lines.map(l => l.text).slice(0, ROWS - 2);

    const gtTextLines = gt.textLines;
    const textDiffs = diffLines(gtTextLines, simTextLines);

    const gtCursor = gt.cursor;
    const simCursor = frame.cursor;
    const cursorMatch = (gtCursor.row === simCursor.row && gtCursor.col === simCursor.col);

    // Compare runs/colours if ground truth has frame data
    let colorDiffs = [];
    if (!skipColors && gt.frame && gt.frame.lines && !gt.colorError) {
      colorDiffs = diffRuns(gt.frame, frame, ROWS - 2);
    }

    if (textDiffs.length === 0 && cursorMatch && colorDiffs.length === 0) {
      suitePassed++;
    } else {
      console.log(`  FAIL  ${name}`);
      const info = { suite: suiteName, name, textDiffs, cursorMatch, colorDiffs };
      if (!cursorMatch) {
        info.cursorExpected = { row: gtCursor.row, col: gtCursor.col };
        info.cursorActual = simCursor;
        console.log(`        cursor: expected (${gtCursor.row},${gtCursor.col}) got (${simCursor.row},${simCursor.col})`);
      }
      if (textDiffs.length > 0) {
        for (const d of textDiffs.slice(0, 3)) {
          console.log(`        row ${d.row}: expected ${d.expected}`);
          console.log(`                  actual   ${d.actual}`);
        }
        if (textDiffs.length > 3) {
          console.log(`        ... and ${textDiffs.length - 3} more text diffs`);
        }
      }
      if (colorDiffs.length > 0) {
        console.log(`        color mismatches:`);
        for (const d of colorDiffs.slice(0, 3)) {
          console.log(`          row ${d.row}: gt   ${d.expected}`);
          console.log(`          ${String(d.row).replace(/./g,' ')}       sim  ${d.actual}`);
        }
        if (colorDiffs.length > 3) {
          console.log(`        ... and ${colorDiffs.length - 3} more color diffs`);
        }
      }
      allFailures.push(info);
      suiteFailed++;
    }
  }

  const suiteTotal = suitePassed + suiteFailed;
  console.log(`  ${suiteName}: ${suitePassed}/${suiteTotal} passed` +
    (suiteSkipped > 0 ? `, ${suiteSkipped} skipped` : '') +
    (suiteFailed > 0 ? ` ❌ ${suiteFailed} failed` : ' ✅'));

  totalPassed += suitePassed;
  totalFailed += suiteFailed;
  totalSkipped += suiteSkipped;
}

// ── Summary ──
console.log(`\n${'='.repeat(60)}`);
console.log(`TOTAL: ${totalPassed} passed, ${totalFailed} failed, ${totalSkipped} skipped`);
console.log(`${'='.repeat(60)}`);

if (allFailures.length > 0 && allFailures.length <= 20) {
  console.log('\nFailed cases:');
  for (const f of allFailures) {
    console.log(`  ${f.suite}/${f.name}`);
  }
}

if (totalFailed > 0) process.exit(1);
