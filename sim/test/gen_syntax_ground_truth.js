/**
 * VimFu Simulator – Syntax Ground Truth Generator
 *
 * Opens the sample Python file in the sim at various scroll positions,
 * renders each frame, and saves the output as syntax_ground_truth.json.
 *
 * The companion test (test_syntax_screen.js) replays these exact
 * scenarios and compares frame-for-frame.
 *
 * Run:  node test/gen_syntax_ground_truth.js
 */

import { VimEngine } from '../src/engine.js';
import { Screen } from '../src/screen.js';
import { SAMPLE_PYTHON } from '../src/samples.js';
import { writeFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const OUT_PATH = resolve(__dirname, 'syntax_ground_truth.json');

const ROWS = 20;
const COLS = 40;

function makePyEngine() {
  const engine = new VimEngine({ rows: ROWS, cols: COLS });
  engine.filename = SAMPLE_PYTHON.filename;
  engine.loadFile(SAMPLE_PYTHON.content);
  return engine;
}

const lines = SAMPLE_PYTHON.content.split('\n');

// ── Define scroll scenarios ──────────────────────────────────
// Each scenario: { name, scrollTop?, keys? }
// "scrollTop" directly positions the viewport.
// "keys" feed input to the engine before rendering.

const scenarios = [
  // Top of file – imports, constants, strings
  {
    name: 'top_of_file',
    scrollTop: 0,
  },
  // Constants + string literals
  {
    name: 'constants_region',
    scrollTop: lines.findIndex(l => l.startsWith('# Constants')),
  },
  // Multi-line triple-quoted string
  {
    name: 'triple_quoted_string',
    scrollTop: lines.findIndex(l => l.includes('MULTI = """')),
  },
  // Decorator + function def
  {
    name: 'decorator_region',
    scrollTop: lines.findIndex(l => l.trimStart().startsWith('@property')),
  },
  // Class definition
  {
    name: 'class_region',
    scrollTop: lines.findIndex(l => l.startsWith('class Animal')),
  },
  // Dog class + methods
  {
    name: 'dog_class',
    scrollTop: lines.findIndex(l => l.startsWith('class Dog')),
  },
  // Generator (yield, while)
  {
    name: 'generator_fibonacci',
    scrollTop: lines.findIndex(l => l.startsWith('def fibonacci')),
  },
  // Lambda + comprehensions
  {
    name: 'lambda_region',
    scrollTop: lines.findIndex(l => l.includes('# Lambda')),
  },
  // Exception handling (try/except/finally)
  {
    name: 'exception_handling',
    scrollTop: lines.findIndex(l => l.includes('# Exception')),
  },
  // Async syntax
  {
    name: 'async_syntax',
    scrollTop: lines.findIndex(l => l.includes('# Async')),
  },
  // Walrus + match statement
  {
    name: 'walrus_match',
    scrollTop: lines.findIndex(l => l.includes('# Walrus')),
  },
  // Global / nonlocal
  {
    name: 'global_nonlocal',
    scrollTop: lines.findIndex(l => l.includes('# Global')),
  },
  // __name__ == "__main__" entry point
  {
    name: 'main_entry',
    scrollTop: lines.findIndex(l => l.includes('# Entry point')),
  },
  // Bottom of file
  {
    name: 'bottom_of_file',
    scrollTop: Math.max(0, lines.length - (ROWS - 2)),
  },
];

// ── Generate ground truth ─────────────────────────────────────
const groundTruth = {};

for (const scenario of scenarios) {
  const engine = makePyEngine();
  const screen = new Screen(ROWS, COLS, 'nvim_default');

  if (scenario.scrollTop != null) {
    engine.scrollTop = scenario.scrollTop;
  }

  const frame = screen.render(engine);

  groundTruth[scenario.name] = {
    scrollTop: scenario.scrollTop ?? null,
    keys: scenario.keys ?? null,
    cursor: { row: frame.cursor.row, col: frame.cursor.col },
    textLines: frame.lines.map(l => l.text),
    frame: {
      lines: frame.lines.map(l => ({
        text: l.text,
        runs: l.runs,
      })),
    },
  };
}

writeFileSync(OUT_PATH, JSON.stringify(groundTruth, null, 2));
console.log(`Wrote ${Object.keys(groundTruth).length} scenarios to ${OUT_PATH}`);
