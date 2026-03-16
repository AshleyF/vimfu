/**
 * VimFu Simulator – Spell Checking Unit Tests
 *
 * Tests for :set spell, ]s, [s, z=, zg, zw, zug, zuw
 */

import { VimEngine } from '../src/engine.js';
import { Screen } from '../src/screen.js';

let passed = 0, failed = 0;

function feedKeys(engine, keys) {
  for (let i = 0; i < keys.length; i++) {
    let key = keys[i];
    if (key === '\x1b') key = 'Escape';
    else if (key === '\r') key = 'Enter';
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

console.log('Running spell checking unit tests...\n');

// ── Test: spell is off by default ──
{
  const e = new VimEngine({ rows: 20, cols: 40 });
  assert('spell_off', false, e._settings.spell);
}

// ── Test: :set spell enables spell checking ──
{
  const e = new VimEngine({ rows: 20, cols: 40 });
  feedKeys(e, ':set spell\r');
  assert('spell_on', true, e._settings.spell);
}

// ── Test: :set nospell disables spell checking ──
{
  const e = new VimEngine({ rows: 20, cols: 40 });
  feedKeys(e, ':set spell\r');
  feedKeys(e, ':set nospell\r');
  assert('spell_off2', false, e._settings.spell);
}

// ── Test: _isSpellBad detects misspelled words ──
{
  const e = new VimEngine({ rows: 20, cols: 40 });
  feedKeys(e, ':set spell\r');
  assert('bad_word', true, e._isSpellBad('xyzzyplugh'));
  assert('good_word', false, e._isSpellBad('the'));
  assert('good_word2', false, e._isSpellBad('function'));
}

// ── Test: ]s moves to next misspelled word ──
{
  const e = new VimEngine({ rows: 20, cols: 40 });
  e.loadFile('the xyzzyplugh is here\n', 'test.txt');
  feedKeys(e, ':set spell\r');
  feedKeys(e, ']s');
  assert('next_spell_col', 4, e.cursor.col); // 'xyzzyplugh' starts at col 4
  assert('next_spell_row', 0, e.cursor.row);
}

// ── Test: [s moves to previous misspelled word ──
{
  const e = new VimEngine({ rows: 20, cols: 40 });
  e.loadFile('the xyzzyplugh is foobarqux\n', 'test.txt');
  feedKeys(e, ':set spell\r');
  feedKeys(e, '$[s');
  assert('prev_spell_col', 18, e.cursor.col); // 'foobarqux' at col 18
}

// ── Test: zg adds word to good list ──
{
  const e = new VimEngine({ rows: 20, cols: 40 });
  e.loadFile('xyzzyplugh\n', 'test.txt');
  feedKeys(e, ':set spell\r');
  assert('before_zg', true, e._isSpellBad('xyzzyplugh'));
  feedKeys(e, 'zg');
  assert('after_zg', false, e._isSpellBad('xyzzyplugh'));
  assert('in_good_list', true, e._spellGoodWords.has('xyzzyplugh'));
}

// ── Test: zw marks word as bad ──
{
  const e = new VimEngine({ rows: 20, cols: 40 });
  e.loadFile('hello\n', 'test.txt');
  feedKeys(e, ':set spell\r');
  assert('before_zw', false, e._isSpellBad('hello'));
  feedKeys(e, 'zw');
  assert('after_zw', true, e._isSpellBad('hello'));
}

// ── Test: zug undoes zg ──
{
  const e = new VimEngine({ rows: 20, cols: 40 });
  e.loadFile('xyzzyplugh\n', 'test.txt');
  feedKeys(e, ':set spell\r');
  feedKeys(e, 'zg'); // add to good list
  assert('zg_good', false, e._isSpellBad('xyzzyplugh'));
  feedKeys(e, 'zug'); // undo
  assert('zug_bad', true, e._isSpellBad('xyzzyplugh'));
}

// ── Test: zuw undoes zw ──
{
  const e = new VimEngine({ rows: 20, cols: 40 });
  e.loadFile('hello\n', 'test.txt');
  feedKeys(e, ':set spell\r');
  feedKeys(e, 'zw');
  assert('zw_bad', true, e._isSpellBad('hello'));
  feedKeys(e, 'zuw');
  assert('zuw_good', false, e._isSpellBad('hello'));
}

// ── Test: z= shows suggestions for misspelled word ──
{
  const e = new VimEngine({ rows: 20, cols: 40 });
  e.loadFile('helo\n', 'test.txt');
  feedKeys(e, ':set spell\r');
  feedKeys(e, 'z=');
  assert('z=_prompt', true, e._messagePrompt !== null);
}

// ── Test: ]s wraps around buffer ──
{
  const e = new VimEngine({ rows: 20, cols: 40 });
  e.loadFile('xyzzyplugh is on the line\nall good here\n', 'test.txt');
  feedKeys(e, ':set spell\r');
  feedKeys(e, 'j'); // go to line 2
  feedKeys(e, ']s'); // should wrap to line 1
  assert('wrap_spell_row', 0, e.cursor.row);
  assert('wrap_spell_col', 0, e.cursor.col);
}

// ── Test: Spell highlighting in rendered frame ──
{
  const e = new VimEngine({ rows: 20, cols: 40 });
  e.loadFile('the xyzzyplugh is here\n', 'test.txt');
  feedKeys(e, ':set spell\r');
  const screen = new Screen(20, 40, 'monokai');
  const frame = screen.render(e);
  // The first line should have different colors for 'xyzzyplugh'
  const line0Runs = frame.lines[0].runs;
  // Should have more than 1 run (spell error should create separate run)
  assert('spell_render_runs', true, line0Runs.length > 1);
}

// ── Test: No spell errors on good words ──
{
  const e = new VimEngine({ rows: 20, cols: 40 });
  e.loadFile('the cat sat on the mat\n', 'test.txt');
  feedKeys(e, ':set spell\r');
  // All common words — should have no spell errors
  assert('no_errors_cat', false, e._isSpellBad('cat'));
  assert('no_errors_sat', false, e._isSpellBad('sat'));
  assert('no_errors_mat', false, e._isSpellBad('mat'));
}

console.log(`\n${passed}/${passed + failed} passed, ${failed} failed`);
if (failed > 0) process.exit(1);
