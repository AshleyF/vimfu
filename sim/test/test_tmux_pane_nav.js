/**
 * VimFu Simulator – Tmux Pane Navigation Tests (verified against real tmux)
 *
 * Ground truth captured from real tmux with vim-style hjkl bindings.
 * See: test/capture_tmux_pane_nav.py
 * Data: test/tmux_pane_nav_ground_truth.json
 *
 * Tests:
 *   - h/j/k/l pane navigation with various split layouts
 *   - Vertical split, horizontal split, 3-pane, 4-pane (2x2 grid)
 *   - Deep vertical splits (4 columns), deep horizontal splits (4 rows)
 *   - Complex nested splits
 *   - Last-window toggle (Ctrl-B L)
 *   - Edge case: navigate past boundary (wraps around in real tmux)
 *   - Pane geometry / border positions verified against ground truth
 *
 * Usage:
 *   node test/test_tmux_pane_nav.js
 *   node test/test_tmux_pane_nav.js --case <name>
 *   node test/test_tmux_pane_nav.js --verbose
 */

import { dirname, resolve } from 'path';
import { fileURLToPath } from 'url';
import { readFileSync } from 'fs';
import { Tmux, TmuxMode } from '../src/tmux.js';
import { SessionManager } from '../src/session.js';
import { VirtualFS } from '../src/vfs.js';

const __dirname = dirname(fileURLToPath(import.meta.url));

// ── Parse args ──
const args = process.argv.slice(2);
let filterCase = null;
let verbose = false;
for (let i = 0; i < args.length; i++) {
  if (args[i] === '--case' && args[i + 1]) filterCase = args[++i];
  else if (args[i] === '--verbose') verbose = true;
}

// ── Load ground truth ──
let groundTruth;
try {
  const gtPath = resolve(__dirname, 'tmux_pane_nav_ground_truth.json');
  groundTruth = JSON.parse(readFileSync(gtPath, 'utf-8'));
} catch {
  console.error('WARNING: No ground truth file found. Run capture_tmux_pane_nav.py first.');
  groundTruth = null;
}

// ── Helpers ──
const ROWS = 24;
const COLS = 80;

function createPaneSessionFactory(vfs) {
  return (cols, rows) => {
    const sm = new SessionManager({
      rows,
      cols,
      themeName: 'nvim_default',
      persist: false,
    });
    sm.fs = vfs;
    sm.shell.fs = vfs;
    sm.shell._insideTmux = true;
    return sm;
  };
}

function newTmux(opts = {}) {
  const vfs = opts.vfs || new VirtualFS({ persist: false });
  return new Tmux({
    rows: opts.rows || ROWS,
    cols: opts.cols || COLS,
    createPaneSession: createPaneSessionFactory(vfs),
  });
}

function feedString(target, str) {
  for (const ch of str) target.feedKey(ch);
}

function getFrameText(frame) {
  return frame.lines.map(l => l.text);
}

function getFrameRow(frame, row) {
  return frame.lines[row]?.text || '';
}

function getStatusBar(tmux) {
  const frame = tmux.renderFrame();
  return getFrameRow(frame, tmux.rows - 1);
}

function findBorderCol(frame) {
  for (let r = 0; r < frame.lines.length - 1; r++) {
    const text = frame.lines[r].text;
    for (let c = 0; c < text.length; c++) {
      if (text[c] === '│') return c;
    }
  }
  return null;
}

function findBorderRow(frame) {
  for (let r = 0; r < frame.lines.length - 1; r++) {
    if (frame.lines[r].text.includes('─')) return r;
  }
  return null;
}

function findAllBorderCols(frame) {
  const cols = new Set();
  for (let r = 0; r < frame.lines.length - 1; r++) {
    const text = frame.lines[r].text;
    for (let c = 0; c < text.length; c++) {
      if (text[c] === '│') cols.add(c);
    }
  }
  return [...cols].sort((a, b) => a - b);
}

function findAllBorderRows(frame) {
  const rows = new Set();
  for (let r = 0; r < frame.lines.length - 1; r++) {
    const text = frame.lines[r].text;
    for (let c = 0; c < text.length; c++) {
      if ('─┬┼┤├┴'.includes(text[c])) { rows.add(r); break; }
    }
  }
  return [...rows].sort((a, b) => a - b);
}

/** Get which pane region a cursor is in given borders */
function cursorPaneRegion(cursor, borderCols, borderRows) {
  let col = 'left';
  for (const bc of borderCols) {
    if (cursor.col > bc) col = `right_of_${bc}`;
  }
  let row = 'top';
  for (const br of borderRows) {
    if (cursor.row > br) row = `below_${br}`;
  }
  return { col, row };
}

/** Check if cursor is in the left side of a vertical border */
function cursorIsLeft(cursor, borderCol) {
  return cursor.col < borderCol;
}

/** Check if cursor is above a horizontal border */
function cursorIsAbove(cursor, borderRow) {
  return cursor.row < borderRow;
}

// ── Test runner ──
const tests = {};
let passed = 0;
let failed = 0;

function assert(cond, msg) {
  if (!cond) throw new Error(msg);
}

function assertEqual(actual, expected, msg) {
  if (actual !== expected) {
    throw new Error(`${msg}: expected ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}`);
  }
}

function assertArrayEqual(actual, expected, msg) {
  const a = JSON.stringify(actual);
  const e = JSON.stringify(expected);
  if (a !== e) throw new Error(`${msg}: expected ${e}, got ${a}`);
}

// ═══════════════════════════════════════════════════════════════════
// GROUP 1: Vertical split — h/l navigation
// ═══════════════════════════════════════════════════════════════════

tests.vsplit_h_navigates_left = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B'); t.feedKey('%');
  const panes = t.activeWindow.getPanes();
  assertEqual(t.activePane, panes[1], 'starts in right pane');

  t.feedKey('Ctrl-B'); t.feedKey('h');
  assertEqual(t.activePane, panes[0], 'h moved to left pane');
};

tests.vsplit_l_navigates_right = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B'); t.feedKey('%');
  const panes = t.activeWindow.getPanes();

  t.feedKey('Ctrl-B'); t.feedKey('h');
  assertEqual(t.activePane, panes[0], 'in left pane');

  t.feedKey('Ctrl-B'); t.feedKey('l');
  assertEqual(t.activePane, panes[1], 'l moved to right pane');
};

tests.vsplit_h_then_l_roundtrip = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B'); t.feedKey('%');
  const panes = t.activeWindow.getPanes();

  t.feedKey('Ctrl-B'); t.feedKey('h');
  assertEqual(t.activePane, panes[0], 'h to left');

  t.feedKey('Ctrl-B'); t.feedKey('l');
  assertEqual(t.activePane, panes[1], 'l to right');

  t.feedKey('Ctrl-B'); t.feedKey('h');
  assertEqual(t.activePane, panes[0], 'h back to left');
};

// Verify cursor ends up in the correct pane region
tests.vsplit_h_cursor_in_left_pane = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B'); t.feedKey('%');
  t.feedKey('Ctrl-B'); t.feedKey('h');
  const frame = t.renderFrame();
  const border = findBorderCol(frame);
  assert(border !== null, 'border found');
  assert(frame.cursor.col < border, `cursor col ${frame.cursor.col} < border ${border}`);
};

tests.vsplit_l_cursor_in_right_pane = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B'); t.feedKey('%');
  t.feedKey('Ctrl-B'); t.feedKey('h');
  t.feedKey('Ctrl-B'); t.feedKey('l');
  const frame = t.renderFrame();
  const border = findBorderCol(frame);
  assert(border !== null, 'border found');
  assert(frame.cursor.col > border, `cursor col ${frame.cursor.col} > border ${border}`);
};

// ═══════════════════════════════════════════════════════════════════
// GROUP 2: Horizontal split — j/k navigation
// ═══════════════════════════════════════════════════════════════════

tests.hsplit_k_navigates_up = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B'); t.feedKey('"');
  const panes = t.activeWindow.getPanes();
  assertEqual(t.activePane, panes[1], 'starts in bottom');

  t.feedKey('Ctrl-B'); t.feedKey('k');
  assertEqual(t.activePane, panes[0], 'k moved to top');
};

tests.hsplit_j_navigates_down = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B'); t.feedKey('"');
  const panes = t.activeWindow.getPanes();

  t.feedKey('Ctrl-B'); t.feedKey('k');
  assertEqual(t.activePane, panes[0], 'in top');

  t.feedKey('Ctrl-B'); t.feedKey('j');
  assertEqual(t.activePane, panes[1], 'j moved to bottom');
};

tests.hsplit_k_cursor_in_top_pane = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B'); t.feedKey('"');
  t.feedKey('Ctrl-B'); t.feedKey('k');
  const frame = t.renderFrame();
  const border = findBorderRow(frame);
  assert(border !== null, 'border found');
  assert(frame.cursor.row < border, `cursor row ${frame.cursor.row} < border ${border}`);
};

tests.hsplit_j_cursor_in_bottom_pane = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B'); t.feedKey('"');
  t.feedKey('Ctrl-B'); t.feedKey('k');
  t.feedKey('Ctrl-B'); t.feedKey('j');
  const frame = t.renderFrame();
  const border = findBorderRow(frame);
  assert(border !== null, 'border found');
  assert(frame.cursor.row > border, `cursor row ${frame.cursor.row} > border ${border}`);
};

// ═══════════════════════════════════════════════════════════════════
// GROUP 3: Three panes — left | (top-right / bottom-right)
// ═══════════════════════════════════════════════════════════════════

tests.three_panes_navigate_all = () => {
  const t = newTmux();
  // vsplit: left | right
  t.feedKey('Ctrl-B'); t.feedKey('%');
  // hsplit right: left | (top-right / bottom-right)
  t.feedKey('Ctrl-B'); t.feedKey('"');
  const panes = t.activeWindow.getPanes();
  assertEqual(panes.length, 3, '3 panes');

  // In bottom-right
  const brPane = t.activePane;

  // k -> top-right
  t.feedKey('Ctrl-B'); t.feedKey('k');
  const trPane = t.activePane;
  assert(trPane !== brPane, 'k moved away from bottom-right');

  // h -> left
  t.feedKey('Ctrl-B'); t.feedKey('h');
  const lPane = t.activePane;
  assert(lPane !== trPane, 'h moved to left');

  // l -> back to a right pane
  t.feedKey('Ctrl-B'); t.feedKey('l');
  assert(t.activePane !== lPane, 'l moved away from left');
};

tests.three_panes_geometry_matches_gt = () => {
  if (!groundTruth?.three_panes_labeled) return; // skip if no GT
  const gt = groundTruth.three_panes_labeled;
  const t = newTmux({ rows: gt.rows, cols: gt.cols });

  t.feedKey('Ctrl-B'); t.feedKey('%');
  t.feedKey('Ctrl-B'); t.feedKey('"');

  const frame = t.renderFrame();
  const simBorderCols = findAllBorderCols(frame);
  const simBorderRows = findAllBorderRows(frame);

  // GT borders
  const gtBorderCols = [];
  const gtBorderRows = [];
  for (let r = 0; r < gt.pane_lines.length; r++) {
    for (let c = 0; c < gt.pane_lines[r].length; c++) {
      if (gt.pane_lines[r][c] === '│' && !gtBorderCols.includes(c)) gtBorderCols.push(c);
      if ('─┬┼┤├┴'.includes(gt.pane_lines[r][c]) && !gtBorderRows.includes(r)) gtBorderRows.push(r);
    }
  }
  gtBorderCols.sort((a, b) => a - b);
  gtBorderRows.sort((a, b) => a - b);

  assertArrayEqual(simBorderCols, gtBorderCols, 'three_panes vertical borders match GT');
  assertArrayEqual(simBorderRows, gtBorderRows, 'three_panes horizontal borders match GT');
};

tests.three_panes_l_from_left = () => {
  // After navigating to left pane, l should go right
  const t = newTmux();
  t.feedKey('Ctrl-B'); t.feedKey('%');
  t.feedKey('Ctrl-B'); t.feedKey('"');
  const panes = t.activeWindow.getPanes();

  // Navigate to left pane
  t.feedKey('Ctrl-B'); t.feedKey('h');
  assertEqual(t.activePane, panes[0], 'in left pane');

  // l from left
  t.feedKey('Ctrl-B'); t.feedKey('l');
  assert(t.activePane !== panes[0], 'l moved out of left pane');

  // Verify cursor is in right half
  const frame = t.renderFrame();
  const border = findBorderCol(frame);
  assert(frame.cursor.col > border, 'cursor in right side');
};

tests.three_panes_j_from_topright = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B'); t.feedKey('%');
  t.feedKey('Ctrl-B'); t.feedKey('"');
  const panes = t.activeWindow.getPanes();

  // k to top-right, then j to bottom-right
  t.feedKey('Ctrl-B'); t.feedKey('k');
  const trPane = t.activePane;
  t.feedKey('Ctrl-B'); t.feedKey('j');
  assert(t.activePane !== trPane, 'j moved down from top-right');
};

// ═══════════════════════════════════════════════════════════════════
// GROUP 4: Four panes — 2x2 grid
// ═══════════════════════════════════════════════════════════════════

tests.grid_full_circle_hjkl = () => {
  const t = newTmux();
  // Create 2x2: vsplit, hsplit right, go left, hsplit left
  t.feedKey('Ctrl-B'); t.feedKey('%');   // left | right
  t.feedKey('Ctrl-B'); t.feedKey('"');   // left | (TR / BR)
  t.feedKey('Ctrl-B'); t.feedKey('h');   // go to left
  t.feedKey('Ctrl-B'); t.feedKey('"');   // (TL / BL) | (TR / BR)

  const panes = t.activeWindow.getPanes();
  assertEqual(panes.length, 4, '4 panes in grid');

  // We should be in BL. Navigate full circle: k->TL, l->TR, j->BR, h->BL
  const blPane = t.activePane;

  t.feedKey('Ctrl-B'); t.feedKey('k');
  const tlPane = t.activePane;
  assert(tlPane !== blPane, 'k from BL moved up');

  t.feedKey('Ctrl-B'); t.feedKey('l');
  const trPane = t.activePane;
  assert(trPane !== tlPane, 'l from TL moved right');

  t.feedKey('Ctrl-B'); t.feedKey('j');
  const brPane = t.activePane;
  assert(brPane !== trPane, 'j from TR moved down');

  t.feedKey('Ctrl-B'); t.feedKey('h');
  assert(t.activePane === blPane, 'h from BR back to BL');
};

tests.grid_geometry_matches_gt = () => {
  if (!groundTruth?.grid_labeled) return;
  const gt = groundTruth.grid_labeled;
  const t = newTmux({ rows: gt.rows, cols: gt.cols });

  t.feedKey('Ctrl-B'); t.feedKey('%');
  t.feedKey('Ctrl-B'); t.feedKey('"');
  t.feedKey('Ctrl-B'); t.feedKey('h');
  t.feedKey('Ctrl-B'); t.feedKey('"');

  const frame = t.renderFrame();
  const simBorderCols = findAllBorderCols(frame);
  const simBorderRows = findAllBorderRows(frame);

  const gtBorderCols = [];
  const gtBorderRows = [];
  for (let r = 0; r < gt.pane_lines.length; r++) {
    for (let c = 0; c < gt.pane_lines[r].length; c++) {
      if (gt.pane_lines[r][c] === '│' && !gtBorderCols.includes(c)) gtBorderCols.push(c);
      if ('─┬┼┤├┴'.includes(gt.pane_lines[r][c]) && !gtBorderRows.includes(r)) gtBorderRows.push(r);
    }
  }
  gtBorderCols.sort((a, b) => a - b);
  gtBorderRows.sort((a, b) => a - b);

  assertArrayEqual(simBorderCols, gtBorderCols, 'grid vertical borders match GT');
  assertArrayEqual(simBorderRows, gtBorderRows, 'grid horizontal borders match GT');
};

// ═══════════════════════════════════════════════════════════════════
// GROUP 5: Deep vertical splits (4 columns)
// ═══════════════════════════════════════════════════════════════════

tests.deep_vsplit_h_traverses_all = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B'); t.feedKey('%');
  t.feedKey('Ctrl-B'); t.feedKey('%');
  t.feedKey('Ctrl-B'); t.feedKey('%');
  const panes = t.activeWindow.getPanes();
  assertEqual(panes.length, 4, '4 vertical panes');

  // Should be in rightmost. Go h 3 times to leftmost.
  const startPane = t.activePane;
  const visited = [startPane];
  for (let i = 0; i < 3; i++) {
    t.feedKey('Ctrl-B'); t.feedKey('h');
    visited.push(t.activePane);
  }
  // Should have visited 4 distinct panes
  const unique = new Set(visited);
  assertEqual(unique.size, 4, 'visited all 4 panes going left');

  // Verify we're in the leftmost pane (col 0)
  assertEqual(t.activePane.left, 0, 'in leftmost pane');
};

tests.deep_vsplit_l_traverses_all = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B'); t.feedKey('%');
  t.feedKey('Ctrl-B'); t.feedKey('%');
  t.feedKey('Ctrl-B'); t.feedKey('%');
  const panes = t.activeWindow.getPanes();

  // Go all the way left first
  for (let i = 0; i < 3; i++) {
    t.feedKey('Ctrl-B'); t.feedKey('h');
  }
  assertEqual(t.activePane.left, 0, 'at leftmost');

  // Now go l 3 times to rightmost
  const visited = [t.activePane];
  for (let i = 0; i < 3; i++) {
    t.feedKey('Ctrl-B'); t.feedKey('l');
    visited.push(t.activePane);
  }
  const unique = new Set(visited);
  assertEqual(unique.size, 4, 'visited all 4 panes going right');

  // Verify we're in the rightmost pane
  const maxLeft = Math.max(...panes.map(p => p.left));
  assertEqual(t.activePane.left, maxLeft, 'in rightmost pane');
};

tests.deep_vsplit_geometry_matches_gt = () => {
  if (!groundTruth?.deep_vsplit_leftmost) return;
  const gt = groundTruth.deep_vsplit_leftmost;
  const t = newTmux({ rows: gt.rows, cols: gt.cols });

  t.feedKey('Ctrl-B'); t.feedKey('%');
  t.feedKey('Ctrl-B'); t.feedKey('%');
  t.feedKey('Ctrl-B'); t.feedKey('%');

  const frame = t.renderFrame();
  const simBorderCols = findAllBorderCols(frame);

  const gtBorderCols = [];
  for (let r = 0; r < gt.pane_lines.length; r++) {
    for (let c = 0; c < gt.pane_lines[r].length; c++) {
      if (gt.pane_lines[r][c] === '│' && !gtBorderCols.includes(c)) gtBorderCols.push(c);
    }
  }
  gtBorderCols.sort((a, b) => a - b);

  assertArrayEqual(simBorderCols, gtBorderCols, 'deep vsplit borders match GT');
};

// ═══════════════════════════════════════════════════════════════════
// GROUP 6: Deep horizontal splits (4 rows)
// ═══════════════════════════════════════════════════════════════════

tests.deep_hsplit_k_traverses_all = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B'); t.feedKey('"');
  t.feedKey('Ctrl-B'); t.feedKey('"');
  t.feedKey('Ctrl-B'); t.feedKey('"');
  const panes = t.activeWindow.getPanes();
  assertEqual(panes.length, 4, '4 horizontal panes');

  // Should be in bottommost. Go k 3 times.
  const visited = [t.activePane];
  for (let i = 0; i < 3; i++) {
    t.feedKey('Ctrl-B'); t.feedKey('k');
    visited.push(t.activePane);
  }
  const unique = new Set(visited);
  assertEqual(unique.size, 4, 'visited all 4 panes going up');
  assertEqual(t.activePane.top, 0, 'in topmost pane');
};

tests.deep_hsplit_j_traverses_all = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B'); t.feedKey('"');
  t.feedKey('Ctrl-B'); t.feedKey('"');
  t.feedKey('Ctrl-B'); t.feedKey('"');
  const panes = t.activeWindow.getPanes();

  // Go all the way up first
  for (let i = 0; i < 3; i++) {
    t.feedKey('Ctrl-B'); t.feedKey('k');
  }
  assertEqual(t.activePane.top, 0, 'at topmost');

  // Now go j 3 times
  const visited = [t.activePane];
  for (let i = 0; i < 3; i++) {
    t.feedKey('Ctrl-B'); t.feedKey('j');
    visited.push(t.activePane);
  }
  const unique = new Set(visited);
  assertEqual(unique.size, 4, 'visited all 4 panes going down');

  const maxTop = Math.max(...panes.map(p => p.top));
  assertEqual(t.activePane.top, maxTop, 'in bottommost pane');
};

tests.deep_hsplit_geometry_matches_gt = () => {
  if (!groundTruth?.deep_hsplit_top) return;
  const gt = groundTruth.deep_hsplit_top;
  const t = newTmux({ rows: gt.rows, cols: gt.cols });

  t.feedKey('Ctrl-B'); t.feedKey('"');
  t.feedKey('Ctrl-B'); t.feedKey('"');
  t.feedKey('Ctrl-B'); t.feedKey('"');

  const frame = t.renderFrame();
  const simBorderRows = findAllBorderRows(frame);

  const gtBorderRows = [];
  for (let r = 0; r < gt.pane_lines.length; r++) {
    for (let c = 0; c < gt.pane_lines[r].length; c++) {
      if ('─┬┼┤├┴'.includes(gt.pane_lines[r][c]) && !gtBorderRows.includes(r)) {
        gtBorderRows.push(r);
        break;
      }
    }
  }
  gtBorderRows.sort((a, b) => a - b);

  assertArrayEqual(simBorderRows, gtBorderRows, 'deep hsplit borders match GT');
};

// ═══════════════════════════════════════════════════════════════════
// GROUP 7: Complex nested splits
// ═══════════════════════════════════════════════════════════════════

tests.nested_splits_navigate = () => {
  const t = newTmux();
  // vsplit: L | R
  t.feedKey('Ctrl-B'); t.feedKey('%');
  // h to go left
  t.feedKey('Ctrl-B'); t.feedKey('h');
  // hsplit left: TL / BL | R
  t.feedKey('Ctrl-B'); t.feedKey('"');
  // vsplit bottom-left: TL / (BL-L | BL-R) | R
  t.feedKey('Ctrl-B'); t.feedKey('%');

  const panes = t.activeWindow.getPanes();
  assertEqual(panes.length, 4, '4 panes in nested layout');

  // We're in BL-R. Navigate to each pane.
  const blrPane = t.activePane;

  // h -> BL-L
  t.feedKey('Ctrl-B'); t.feedKey('h');
  const bllPane = t.activePane;
  assert(bllPane !== blrPane, 'h from BLR moved left');

  // k -> TL
  t.feedKey('Ctrl-B'); t.feedKey('k');
  const tlPane = t.activePane;
  assert(tlPane !== bllPane, 'k from BLL moved up');

  // l -> R (should cross main vertical border)
  t.feedKey('Ctrl-B'); t.feedKey('l');
  const rPane = t.activePane;
  assert(rPane !== tlPane, 'l from TL moved right');

  // Verify R pane is on the right side
  const frame = t.renderFrame();
  const borders = findAllBorderCols(frame);
  assert(rPane.left > borders[0], 'R pane is on right side');
};

tests.nested_geometry_matches_gt = () => {
  if (!groundTruth?.nested_labeled) return;
  const gt = groundTruth.nested_labeled;
  const t = newTmux({ rows: gt.rows, cols: gt.cols });

  t.feedKey('Ctrl-B'); t.feedKey('%');
  t.feedKey('Ctrl-B'); t.feedKey('h');
  t.feedKey('Ctrl-B'); t.feedKey('"');
  t.feedKey('Ctrl-B'); t.feedKey('%');

  const frame = t.renderFrame();
  const simBorderCols = findAllBorderCols(frame);

  const gtBorderCols = [];
  for (let r = 0; r < gt.pane_lines.length; r++) {
    for (let c = 0; c < gt.pane_lines[r].length; c++) {
      if (gt.pane_lines[r][c] === '│' && !gtBorderCols.includes(c)) gtBorderCols.push(c);
    }
  }
  gtBorderCols.sort((a, b) => a - b);

  assertArrayEqual(simBorderCols, gtBorderCols, 'nested borders match GT');
};

// ═══════════════════════════════════════════════════════════════════
// GROUP 8: Last window (Ctrl-B L)
// ═══════════════════════════════════════════════════════════════════

tests.last_window_toggle = () => {
  const t = newTmux();
  const sess = t.activeSession;

  // Create window 1
  t.feedKey('Ctrl-B'); t.feedKey('c');
  assertEqual(sess.activeWindowIndex, 1, 'in window 1');

  // L -> last window (0)
  t.feedKey('Ctrl-B'); t.feedKey('L');
  assertEqual(sess.activeWindowIndex, 0, 'L toggled to window 0');

  // L again -> back to window 1
  t.feedKey('Ctrl-B'); t.feedKey('L');
  assertEqual(sess.activeWindowIndex, 1, 'L toggled back to window 1');
};

tests.last_window_status_bar = () => {
  if (!groundTruth?.lastwin_toggle_back) return;
  const gt = groundTruth.lastwin_toggle_back;

  const t = newTmux({ rows: gt.rows, cols: gt.cols });
  t.feedKey('Ctrl-B'); t.feedKey('c');
  t.feedKey('Ctrl-B'); t.feedKey('L');

  const status = getStatusBar(t);
  // Should show window 0 as active (with *)
  const windowParts = status.match(/\d+:zsh[*-]/g) || [];
  const activeWin = windowParts.find(w => w.includes('*'));
  assert(activeWin?.startsWith('0:'), `active window should be 0, got: ${activeWin}`);
};

// Verify lowercase l still does pane nav, not last window
tests.lowercase_l_is_pane_nav_not_last_window = () => {
  const t = newTmux();
  // Create window 1
  t.feedKey('Ctrl-B'); t.feedKey('c');
  assertEqual(t.activeSession.activeWindowIndex, 1, 'in window 1');

  // vsplit in window 1
  t.feedKey('Ctrl-B'); t.feedKey('%');
  const panes = t.activeWindow.getPanes();
  assertEqual(panes.length, 2, '2 panes');
  assertEqual(t.activePane, panes[1], 'in right pane');

  // lowercase l should navigate pane, NOT switch windows
  t.feedKey('Ctrl-B'); t.feedKey('h');
  assertEqual(t.activePane, panes[0], 'h to left');
  t.feedKey('Ctrl-B'); t.feedKey('l');
  assertEqual(t.activePane, panes[1], 'l to right (pane nav, not window switch)');
  assertEqual(t.activeSession.activeWindowIndex, 1, 'still in window 1');
};

// ═══════════════════════════════════════════════════════════════════
// GROUP 9: Edge cases — wrapping
// ═══════════════════════════════════════════════════════════════════

tests.edge_h_at_leftmost_wraps = () => {
  // Real tmux: select-pane -L wraps around
  const t = newTmux();
  t.feedKey('Ctrl-B'); t.feedKey('%');
  const panes = t.activeWindow.getPanes();

  // Go to left pane
  t.feedKey('Ctrl-B'); t.feedKey('h');
  assertEqual(t.activePane, panes[0], 'in left pane');

  // h again: should wrap to right pane (real tmux behavior)
  t.feedKey('Ctrl-B'); t.feedKey('h');
  assertEqual(t.activePane, panes[1], 'h at leftmost wraps to right pane');
};

tests.edge_l_at_rightmost_wraps = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B'); t.feedKey('%');
  const panes = t.activeWindow.getPanes();

  // Already in right pane
  assertEqual(t.activePane, panes[1], 'in right pane');

  // l again: should wrap to left
  t.feedKey('Ctrl-B'); t.feedKey('l');
  assertEqual(t.activePane, panes[0], 'l at rightmost wraps to left pane');
};

tests.edge_k_at_topmost_wraps = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B'); t.feedKey('"');
  const panes = t.activeWindow.getPanes();

  // Go to top
  t.feedKey('Ctrl-B'); t.feedKey('k');
  assertEqual(t.activePane, panes[0], 'in top pane');

  // k again: should wrap to bottom
  t.feedKey('Ctrl-B'); t.feedKey('k');
  assertEqual(t.activePane, panes[1], 'k at topmost wraps to bottom');
};

tests.edge_j_at_bottommost_wraps = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B'); t.feedKey('"');
  const panes = t.activeWindow.getPanes();

  // Already in bottom
  assertEqual(t.activePane, panes[1], 'in bottom pane');

  // j: should wrap to top
  t.feedKey('Ctrl-B'); t.feedKey('j');
  assertEqual(t.activePane, panes[0], 'j at bottommost wraps to top');
};

// ═══════════════════════════════════════════════════════════════════
// GROUP 10: Arrow keys still work too
// ═══════════════════════════════════════════════════════════════════

tests.arrows_and_hjkl_equivalent = () => {
  const t1 = newTmux();
  const t2 = newTmux();

  // Same layout in both
  t1.feedKey('Ctrl-B'); t1.feedKey('%');
  t2.feedKey('Ctrl-B'); t2.feedKey('%');

  // Navigate with arrows in t1, hjkl in t2
  t1.feedKey('Ctrl-B'); t1.feedKey('ArrowLeft');
  t2.feedKey('Ctrl-B'); t2.feedKey('h');

  const p1 = t1.activeWindow.getPanes();
  const p2 = t2.activeWindow.getPanes();
  assertEqual(p1.indexOf(t1.activePane), p2.indexOf(t2.activePane), 'arrow and h equivalent');

  t1.feedKey('Ctrl-B'); t1.feedKey('ArrowRight');
  t2.feedKey('Ctrl-B'); t2.feedKey('l');
  assertEqual(p1.indexOf(t1.activePane), p2.indexOf(t2.activePane), 'arrow and l equivalent');
};


// ═══════════════════════════════════════════════════════════════════
// Test Runner
// ═══════════════════════════════════════════════════════════════════

const testNames = Object.keys(tests);
const toRun = filterCase ? testNames.filter(n => n === filterCase) : testNames;

console.log(`\nRunning ${toRun.length} tmux pane navigation tests...\n`);

for (const name of toRun) {
  try {
    tests[name]();
    passed++;
    if (verbose) console.log(`  ✅ ${name}`);
  } catch (e) {
    failed++;
    console.log(`  ❌ ${name}: ${e.message}`);
    if (verbose) console.log(`     ${e.stack?.split('\n')[1]?.trim()}`);
  }
}

console.log(`\n${passed}/${toRun.length} passed, ${failed} failed\n`);
process.exit(failed > 0 ? 1 : 0);
