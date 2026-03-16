/**
 * VimFu Simulator – Tab Pages Unit Tests
 *
 * Tests for :tabnew, :tabnext, :tabprev, :tabclose, :tabonly, gt, gT, Ctrl-W T
 */

import { VimEngine } from '../src/engine.js';
import { Screen } from '../src/screen.js';

let passed = 0, failed = 0;

function feedKeys(engine, keys) {
  for (let i = 0; i < keys.length; i++) {
    let key = keys[i];
    if (key === '\x1b') key = 'Escape';
    else if (key === '\r') key = 'Enter';
    else if (key === '\x17') key = 'Ctrl-W';
    engine.feedKey(key);
  }
}

function assert(name, expected, actual) {
  if (expected === actual) {
    passed++;
  } else {
    console.log(`  FAIL  ${name}: expected ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}`);
    failed++;
  }
}

console.log('Running tab page unit tests...\n');

// ── Test: Initial state has one tab ──
{
  const e = new VimEngine({ rows: 20, cols: 40 });
  assert('initial_tabs', 1, e.tabCount);
  assert('initial_active', 0, e._activeTab);
}

// ── Test: :tabnew creates new tab ──
{
  const e = new VimEngine({ rows: 20, cols: 40 });
  e.loadFile('hello\n', 'test.txt');
  feedKeys(e, ':tabnew\r');
  assert('tabnew_count', 2, e.tabCount);
  assert('tabnew_active', 1, e._activeTab);
  assert('tabnew_wins', 1, e._windows.length);
}

// ── Test: :tabnext moves to next tab ──
{
  const e = new VimEngine({ rows: 20, cols: 40 });
  feedKeys(e, ':tabnew\r');
  assert('tabnext_before', 1, e._activeTab);
  feedKeys(e, ':tabnext\r');
  assert('tabnext_wraps', 0, e._activeTab);
}

// ── Test: :tabprev moves to previous tab ──
{
  const e = new VimEngine({ rows: 20, cols: 40 });
  feedKeys(e, ':tabnew\r');
  feedKeys(e, ':tabprev\r');
  assert('tabprev', 0, e._activeTab);
}

// ── Test: gt cycles to next tab ──
{
  const e = new VimEngine({ rows: 20, cols: 40 });
  feedKeys(e, ':tabnew\r');
  feedKeys(e, ':tabnew\r');
  // Now on tab 2 (0-indexed). 3 tabs total.
  feedKeys(e, 'gt');
  assert('gt_next', 0, e._activeTab);
  feedKeys(e, 'gt');
  assert('gt_next2', 1, e._activeTab);
}

// ── Test: gT cycles to previous tab ──
{
  const e = new VimEngine({ rows: 20, cols: 40 });
  feedKeys(e, ':tabnew\r');
  feedKeys(e, ':tabnew\r');
  // On tab 2.
  feedKeys(e, 'gT');
  assert('gT_prev', 1, e._activeTab);
  feedKeys(e, 'gT');
  assert('gT_prev2', 0, e._activeTab);
}

// ── Test: Ngt goes to tab N ──
{
  const e = new VimEngine({ rows: 20, cols: 40 });
  feedKeys(e, ':tabnew\r');
  feedKeys(e, ':tabnew\r');
  // On tab 2. 1gt should go to tab 0.
  feedKeys(e, '1gt');
  assert('Ngt', 0, e._activeTab);
  feedKeys(e, '3gt');
  assert('3gt', 2, e._activeTab);
}

// ── Test: :tabclose closes current tab ──
{
  const e = new VimEngine({ rows: 20, cols: 40 });
  feedKeys(e, ':tabnew\r');
  feedKeys(e, ':tabnew\r');
  // 3 tabs, on tab 2.
  feedKeys(e, ':tabclose\r');
  assert('tabclose_count', 2, e.tabCount);
  assert('tabclose_active', 1, e._activeTab);
}

// ── Test: :tabclose on last tab does nothing ──
{
  const e = new VimEngine({ rows: 20, cols: 40 });
  feedKeys(e, ':tabclose\r');
  assert('tabclose_last', 1, e.tabCount);
}

// ── Test: :tabonly closes all other tabs ──
{
  const e = new VimEngine({ rows: 20, cols: 40 });
  feedKeys(e, ':tabnew\r');
  feedKeys(e, ':tabnew\r');
  feedKeys(e, ':tabonly\r');
  assert('tabonly_count', 1, e.tabCount);
  assert('tabonly_active', 0, e._activeTab);
}

// ── Test: Ctrl-W T moves window to new tab ──
{
  const e = new VimEngine({ rows: 20, cols: 40 });
  e.loadFile('hello\n', 'test.txt');
  feedKeys(e, ':sp\r'); // split: 2 windows
  assert('ctrlwt_before_wins', 2, e._windows.length);
  feedKeys(e, '\x17T'); // Ctrl-W T
  assert('ctrlwt_tabs', 2, e.tabCount);
  assert('ctrlwt_new_tab', 1, e._activeTab);
  assert('ctrlwt_new_wins', 1, e._windows.length);
}

// ── Test: Tab line rendering ──
{
  const e = new VimEngine({ rows: 20, cols: 40 });
  e.loadFile('hello\n', 'test.txt');
  feedKeys(e, ':tabnew\r');
  const screen = new Screen(20, 40, 'monokai');
  const frame = screen.render(e);
  // With 2 tabs, first line should be tab line
  const firstLine = frame.lines[0].text;
  assert('tabline_has_tabs', true, firstLine.includes('test.txt'));
  assert('tabline_total_lines', 20, frame.lines.length);
}

// ── Test: Single tab doesn't show tab line ──
{
  const e = new VimEngine({ rows: 20, cols: 40 });
  e.loadFile('hello\n', 'test.txt');
  const screen = new Screen(20, 40, 'monokai');
  const frame = screen.render(e);
  // First line should be text content, not tab line
  const firstLine = frame.lines[0].text;
  assert('no_tabline', true, firstLine.startsWith('hello'));
}

// ── Test: Tab state is preserved when switching ──
{
  const e = new VimEngine({ rows: 20, cols: 40 });
  e.loadFile('first file content\nsecond line\n', 'first.txt');
  feedKeys(e, 'j'); // cursor on line 2
  assert('tab_state_before', 1, e.cursor.row);
  feedKeys(e, ':tabnew\r');
  assert('tab_state_new', 0, e.cursor.row); // new tab starts at line 1
  // Switch back
  feedKeys(e, 'gT');
  assert('tab_state_restored', 1, e.cursor.row);
}

// ── Test: getTabLineInfo returns correct info ──
{
  const e = new VimEngine({ rows: 20, cols: 40 });
  e.loadFile('hello\n', 'test.txt');
  feedKeys(e, ':tabnew\r');
  const info = e.getTabLineInfo();
  assert('tabinfo_count', 2, info.length);
  assert('tabinfo_0_active', false, info[0].active);
  assert('tabinfo_1_active', true, info[1].active);
  assert('tabinfo_0_label', 'test.txt', info[0].label);
}

console.log(`\n${passed}/${passed + failed} passed, ${failed} failed`);
if (failed > 0) process.exit(1);
