/**
 * Ground-truth comparison test.
 *
 * For each ground_truth/<suite>.json file:
 *   - Build a fresh Terminal at (rows, cols).
 *   - Feed the same raw byte stream pyte saw.
 *   - Compare our toFrame() output to the captured one.
 *
 * A failure prints a side-by-side text + cursor diff so it's quick to
 * spot what went wrong.
 *
 * To regenerate ground truth after intentional changes to the pyte
 * expectation set: `npm run ground-truth`.
 *
 * Tests are SKIPPED (not failed) for any suite whose ground-truth file
 * is missing — that way the test suite still passes on a fresh clone
 * before someone runs `gen_ground_truth.py`.
 */

import { describe, test, expect } from '@jest/globals';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Terminal } from '../src/terminal.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const GROUND_DIR = path.join(__dirname, 'ground_truth');

function loadSuites() {
  if (!fs.existsSync(GROUND_DIR)) return [];
  return fs.readdirSync(GROUND_DIR)
    .filter(f => f.endsWith('.json'))
    .map(f => ({
      name: f.replace(/\.json$/, ''),
      path: path.join(GROUND_DIR, f),
    }));
}

/** Build a compact text picture of a frame for diff messages. */
function pictureFrame(frame) {
  const out = [];
  for (let r = 0; r < frame.rows; r++) {
    const line = frame.lines[r];
    const text = line.text.padEnd(frame.cols, ' ');
    const mark = (r === frame.cursor.row) ? '>' : ' ';
    out.push(`${mark}${String(r).padStart(2)} | ${text} |`);
  }
  const c = frame.cursor;
  out.push(`     cursor=(${c.row},${c.col}) visible=${c.visible}`);
  return out.join('\n');
}

/** Normalise a frame for comparison.  Keeps text + cursor + (light) runs. */
function normalise(frame) {
  return {
    rows: frame.rows,
    cols: frame.cols,
    cursor: { row: frame.cursor.row, col: frame.cursor.col },
    lines: frame.lines.map(line => ({
      // Strip pyte's trailing-space difference: pad both to cols.
      text: line.text.padEnd(frame.cols, ' '),
    })),
  };
}

const suites = loadSuites();

if (suites.length === 0) {
  describe('ground-truth (none generated yet)', () => {
    test.skip('run `npm run ground-truth` to generate baselines', () => {});
  });
}

for (const { name, path: filePath } of suites) {
  describe(`ground-truth: ${name}`, () => {
    const json = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    for (const [caseId, info] of Object.entries(json.cases)) {
      test(caseId, () => {
        const term = new Terminal({ rows: info.rows, cols: info.cols, pyteCompat: true });
        // Feed via TextEncoder path so multi-byte UTF-8 codepoints
        // are reassembled exactly the way they came over a real PTY.
        term.write(info.bytes);
        const got = term.toFrame();

        const a = normalise(got);
        const b = normalise(info.frame);
        try {
          expect(a).toEqual(b);
        } catch (e) {
          // Re-throw with a side-by-side picture for fast triage.
          const msg =
            `\n[case ${caseId}]\n` +
            `bytes: ${JSON.stringify(info.bytes)}\n\n` +
            `--- expected (pyte) ---\n${pictureFrame(info.frame)}\n\n` +
            `--- got (vt-term) -----\n${pictureFrame(got)}\n`;
          e.message = msg + '\n' + e.message;
          throw e;
        }
      });
    }
  });
}
