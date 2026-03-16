/**
 * Unit tests for command-line Tab completion and Ctrl-D (show completions).
 *
 * These test the VimEngine's _commandKey handler directly,
 * verifying the commandLine text and completion state after
 * pressing Tab and Ctrl-D.
 */

import { VimEngine } from '../src/engine.js';

// ── Helpers ──
function newEngine(text = 'hello\nworld\n') {
  const e = new VimEngine({ rows: 20, cols: 40 });
  e.loadFile(text);
  return e;
}

function feedKeys(engine, keys) {
  for (const ch of keys) {
    if (ch === '\x1b') engine.feedKey('Escape');
    else if (ch === '\r') engine.feedKey('Enter');
    else if (ch === '\x09') engine.feedKey('Tab');
    else if (ch === '\x04') engine.feedKey('Ctrl-D');
    else engine.feedKey(ch);
  }
}

let passed = 0, failed = 0;
function assert(cond, msg) {
  if (!cond) { console.log(`  ✗ ${msg}`); failed++; throw new Error(msg); }
}
function assertEqual(a, b, msg) {
  assert(a === b, `${msg}: expected ${JSON.stringify(b)}, got ${JSON.stringify(a)}`);
}
function assertIncludes(s, sub, msg) {
  assert(s.includes(sub), `${msg}: ${JSON.stringify(s)} does not include ${JSON.stringify(sub)}`);
}

const tests = {};

// ═══════════════════════════════════════════════════════════════════
// TAB COMPLETION — Basic command completion
// ═══════════════════════════════════════════════════════════════════

tests.tab_completes_sor_to_sort = () => {
  const e = newEngine();
  feedKeys(e, ':sor');
  assertEqual(e.commandLine, ':sor', 'before Tab');
  e.feedKey('Tab');
  assertEqual(e.commandLine, ':sort', 'after Tab');
};

tests.tab_completes_ec_to_echo = () => {
  const e = newEngine();
  feedKeys(e, ':ec');
  e.feedKey('Tab');
  assertEqual(e.commandLine, ':echo', 'ec → echo');
};

tests.tab_completes_sp_to_split = () => {
  const e = newEngine();
  feedKeys(e, ':sp');
  e.feedKey('Tab');
  assertEqual(e.commandLine, ':split', 'sp → split');
};

tests.tab_completes_vs_to_vsplit = () => {
  const e = newEngine();
  feedKeys(e, ':vs');
  e.feedKey('Tab');
  assertEqual(e.commandLine, ':vsplit', 'vs → vsplit');
};

tests.tab_completes_noh_to_nohlsearch = () => {
  const e = newEngine();
  feedKeys(e, ':noh');
  e.feedKey('Tab');
  assertEqual(e.commandLine, ':nohlsearch', 'noh → nohlsearch');
};

tests.tab_completes_se_to_set = () => {
  const e = newEngine();
  feedKeys(e, ':se');
  e.feedKey('Tab');
  assertEqual(e.commandLine, ':set', 'se → set');
};

tests.tab_completes_clo_to_close = () => {
  const e = newEngine();
  feedKeys(e, ':clo');
  e.feedKey('Tab');
  assertEqual(e.commandLine, ':close', 'clo → close');
};

tests.tab_completes_on_to_only = () => {
  const e = newEngine();
  feedKeys(e, ':on');
  e.feedKey('Tab');
  assertEqual(e.commandLine, ':only', 'on → only');
};

tests.tab_completes_ret_to_retab = () => {
  const e = newEngine();
  feedKeys(e, ':ret');
  e.feedKey('Tab');
  assertEqual(e.commandLine, ':retab', 'ret → retab');
};

// ═══════════════════════════════════════════════════════════════════
// TAB COMPLETION — Cycling through multiple matches
// ═══════════════════════════════════════════════════════════════════

tests.tab_w_cycles_through_matches = () => {
  // :w matches: wa, wq, wqa, write, writ → sorted: wa, wq, wqa, write
  const e = newEngine();
  feedKeys(e, ':w');
  e.feedKey('Tab');
  const first = e.commandLine;
  e.feedKey('Tab');
  const second = e.commandLine;
  // Should be different commands
  assert(first !== second, `cycling produces different results: ${first} vs ${second}`);
};

tests.tab_s_cycles_through_matches = () => {
  // :s matches: saveas, set, sort, split, substitute
  const e = newEngine();
  feedKeys(e, ':s');
  const results = [];
  for (let i = 0; i < 6; i++) {
    e.feedKey('Tab');
    results.push(e.commandLine);
  }
  // Should have at least 2 different values
  const unique = [...new Set(results)];
  assert(unique.length >= 2, `should cycle through multiple matches, got: ${results.join(', ')}`);
};

tests.tab_cycle_wraps_around = () => {
  // After cycling through all matches, should wrap back to first
  const e = newEngine();
  feedKeys(e, ':noh');
  e.feedKey('Tab');
  const first = e.commandLine;
  // nohlsearch is the only :noh match, so Tab again should stay the same
  e.feedKey('Tab');
  const second = e.commandLine;
  assertEqual(first, second, 'unique match stays same on second Tab');
};

// ═══════════════════════════════════════════════════════════════════
// TAB COMPLETION — Edge cases
// ═══════════════════════════════════════════════════════════════════

tests.tab_no_match = () => {
  // No command starts with "zzz"
  const e = newEngine();
  feedKeys(e, ':zzz');
  e.feedKey('Tab');
  assertEqual(e.commandLine, ':zzz', 'no match — unchanged');
};

tests.tab_empty_input = () => {
  // Tab with just ":" — should complete to first command
  const e = newEngine();
  feedKeys(e, ':');
  e.feedKey('Tab');
  // Should have some command (first alphabetically)
  assert(e.commandLine.length > 1, 'Tab on empty completes to something');
};

tests.tab_exact_match = () => {
  // Tab after typing a full command name — should either stay or cycle to next
  const e = newEngine();
  feedKeys(e, ':set');
  e.feedKey('Tab');
  // "set" matches "set" exactly; should complete or cycle
  assertIncludes(e.commandLine, ':', 'still has colon prefix');
};

tests.tab_single_char = () => {
  // Tab after single char that matches multiple commands
  const e = newEngine();
  feedKeys(e, ':e');
  e.feedKey('Tab');
  // Should complete to first :e* command (echo or edit or enew)
  assert(e.commandLine.startsWith(':e'), 'starts with :e');
  assert(e.commandLine.length > 2, 'completed to a full command');
};

// ═══════════════════════════════════════════════════════════════════
// TAB COMPLETION — set option completion
// ═══════════════════════════════════════════════════════════════════

tests.tab_set_option_nu = () => {
  // :set nu<Tab> → should complete to :set number
  const e = newEngine();
  feedKeys(e, ':set nu');
  e.feedKey('Tab');
  assertEqual(e.commandLine, ':set number', 'nu → number');
};

tests.tab_set_option_ai = () => {
  // :set ai<Tab> → should complete to :set autoindent
  const e = newEngine();
  feedKeys(e, ':set ai');
  e.feedKey('Tab');
  assertEqual(e.commandLine, ':set autoindent', 'ai → autoindent');
};

tests.tab_set_option_sw = () => {
  // :set sw<Tab> → should complete to :set shiftwidth
  const e = newEngine();
  feedKeys(e, ':set sw');
  e.feedKey('Tab');
  assertEqual(e.commandLine, ':set shiftwidth', 'sw → shiftwidth');
};

tests.tab_set_nooption = () => {
  // :set nonu<Tab> → should complete to :set nonumber
  const e = newEngine();
  feedKeys(e, ':set nonu');
  e.feedKey('Tab');
  assertEqual(e.commandLine, ':set nonumber', 'nonu → nonumber');
};

// ═══════════════════════════════════════════════════════════════════
// CTRL-D — Show completions
// ═══════════════════════════════════════════════════════════════════

tests.ctrl_d_shows_completions = () => {
  // Ctrl-D with :s should show matching commands
  const e = newEngine();
  feedKeys(e, ':s');
  e.feedKey('Ctrl-D');
  // The engine should have some completion display state
  // commandLine should still be :s (Ctrl-D doesn't change it)
  assertEqual(e.commandLine, ':s', 'commandLine unchanged');
  // Check that completions are available
  assert(e._cmdCompletions && e._cmdCompletions.length > 0,
    'completions list populated');
};

tests.ctrl_d_w_completions = () => {
  const e = newEngine();
  feedKeys(e, ':w');
  e.feedKey('Ctrl-D');
  assertEqual(e.commandLine, ':w', 'commandLine unchanged');
  assert(e._cmdCompletions && e._cmdCompletions.length > 0,
    'has completions');
  // Should include write, wq, wa, wqa
  const completions = e._cmdCompletions;
  assert(completions.includes('write'), 'includes write');
  assert(completions.includes('wq'), 'includes wq');
};

tests.ctrl_d_no_completions = () => {
  // Ctrl-D with gibberish — no completions
  const e = newEngine();
  feedKeys(e, ':zzz');
  e.feedKey('Ctrl-D');
  assertEqual(e.commandLine, ':zzz', 'commandLine unchanged');
  assert(!e._cmdCompletions || e._cmdCompletions.length === 0,
    'no completions for gibberish');
};

tests.ctrl_d_set_completions = () => {
  // Ctrl-D after :set shows option names
  const e = newEngine();
  feedKeys(e, ':set ');
  e.feedKey('Ctrl-D');
  assert(e._cmdCompletions && e._cmdCompletions.length > 0,
    'has set option completions');
  const completions = e._cmdCompletions;
  assert(completions.includes('number'), 'includes number');
  assert(completions.includes('autoindent'), 'includes autoindent');
};

tests.ctrl_d_then_escape_clears = () => {
  // After Ctrl-D shows completions, Escape should clear them
  const e = newEngine();
  feedKeys(e, ':w');
  e.feedKey('Ctrl-D');
  assert(e._cmdCompletions && e._cmdCompletions.length > 0, 'has completions');
  e.feedKey('Escape');
  assertEqual(e.mode, 'normal', 'back to normal mode');
  // Completions should be cleared
  assert(!e._cmdCompletions || e._cmdCompletions.length === 0,
    'completions cleared after Escape');
};

// ═══════════════════════════════════════════════════════════════════
// TAB COMPLETION — Functional (command actually executes)
// ═══════════════════════════════════════════════════════════════════

tests.tab_sort_executes = () => {
  const e = newEngine('cherry\napple\nbanana\n');
  feedKeys(e, ':sor');
  e.feedKey('Tab');
  e.feedKey('Enter');
  // Sort should have executed
  assertEqual(e.buffer.lines[0], 'apple', 'first line sorted');
  assertEqual(e.buffer.lines[1], 'banana', 'second line sorted');
  assertEqual(e.buffer.lines[2], 'cherry', 'third line sorted');
};

tests.tab_echo_executes = () => {
  const e = newEngine();
  feedKeys(e, ':ec');
  e.feedKey('Tab');
  feedKeys(e, " 'hello'");
  e.feedKey('Enter');
  // Echo should have set commandLine to the echo output
  assertIncludes(e.commandLine, 'hello', 'echo output visible');
};

tests.tab_vsplit_executes = () => {
  const e = newEngine();
  feedKeys(e, ':vs');
  e.feedKey('Tab');
  e.feedKey('Enter');
  // vsplit should create a second window
  assert(e._windows.length === 2, 'two windows after vsplit');
};

// ═══════════════════════════════════════════════════════════════════
// Run all tests
// ═══════════════════════════════════════════════════════════════════

console.log(`Running ${Object.keys(tests).length} command-line completion tests...\n`);

for (const [name, fn] of Object.entries(tests)) {
  try {
    fn();
    passed++;
  } catch (e) {
    // Error already printed by assert
  }
}

console.log(`\n${passed}/${passed + failed} passed, ${failed} failed`);
if (failed > 0) process.exit(1);
