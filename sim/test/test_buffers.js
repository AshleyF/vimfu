/**
 * VimFu Simulator – Buffer List Unit Tests
 *
 * Tests for :ls, :bn, :bp, :b N, :bd, Ctrl-^, :enew
 */

import { VimEngine } from '../src/engine.js';
import { Screen } from '../src/screen.js';

let passed = 0, failed = 0;

function feedKeys(engine, keys) {
  for (let i = 0; i < keys.length; i++) {
    let key = keys[i];
    if (key === '\x1b') key = 'Escape';
    else if (key === '\r') key = 'Enter';
    else if (key === '\x06') key = 'Ctrl-^';
    engine.feedKey(key);
  }
}

function assert(test, name, expected, actual) {
  if (expected === actual) {
    passed++;
  } else {
    console.log(`  FAIL  ${name}: expected ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}`);
    failed++;
  }
}

function assertDeep(test, name, expected, actual) {
  const es = JSON.stringify(expected), as = JSON.stringify(actual);
  if (es === as) {
    passed++;
  } else {
    console.log(`  FAIL  ${name}: expected ${es}, got ${as}`);
    failed++;
  }
}

console.log('Running buffer list unit tests...\n');

// ── Test: Initial buffer list has one entry ──
{
  const e = new VimEngine({ rows: 20, cols: 40 });
  assert('initial_buflist', 'buffer list starts with 1 entry', 1, e._bufferList.length);
  assert('initial_bufid', 'current buffer id is 1', 1, e._currentBufId);
  assert('initial_alt', 'alternate buffer is null', null, e._alternateBufId);
}

// ── Test: loadFile creates new buffer ──
{
  const e = new VimEngine({ rows: 20, cols: 40 });
  e.loadFile('hello world\n', 'file1.txt');
  assert('loadfile_count', '2 buffers after loadFile', 2, e._bufferList.length);
  assert('loadfile_id', 'current buffer id is 2', 2, e._currentBufId);
  assert('loadfile_alt', 'alternate is 1', 1, e._alternateBufId);
  assert('loadfile_name', 'fileName is file1.txt', 'file1.txt', e._fileName);
}

// ── Test: loadFile same filename reuses entry ──
{
  const e = new VimEngine({ rows: 20, cols: 40 });
  e.loadFile('hello\n', 'file1.txt');
  const id = e._currentBufId;
  e.loadFile('updated\n', 'file1.txt');
  assert('reload_count', 'still 2 buffers after reload', 2, e._bufferList.length);
  assert('reload_id', 'same buffer id', id, e._currentBufId);
}

// ── Test: :enew creates new buffer ──
{
  const e = new VimEngine({ rows: 20, cols: 40 });
  e.loadFile('hello\n', 'file1.txt');
  feedKeys(e, ':enew\r');
  assert('enew_count', '3 buffers after :enew', 3, e._bufferList.length);
  assert('enew_id', 'current is 3', 3, e._currentBufId);
  assert('enew_content', 'empty buffer', '', e.buffer.lines[0]);
}

// ── Test: :bn cycles to next buffer ──
{
  const e = new VimEngine({ rows: 20, cols: 40 });
  e.loadFile('first\n', 'first.txt');
  e.loadFile('second\n', 'second.txt');
  // Now on buffer 3 (second.txt). :bn should go to buffer 1 (initial empty)
  feedKeys(e, ':bn\r');
  assert('bn_wraps', ':bn wraps to first', 1, e._currentBufId);
  feedKeys(e, ':bn\r');
  assert('bn_next', ':bn goes to second', 2, e._currentBufId);
  assert('bn_name', 'first.txt', 'first.txt', e._fileName);
}

// ── Test: :bp cycles to previous buffer ──
{
  const e = new VimEngine({ rows: 20, cols: 40 });
  e.loadFile('first\n', 'first.txt');
  e.loadFile('second\n', 'second.txt');
  // Buffer 3 (second.txt). :bp should go to buffer 2 (first.txt)
  feedKeys(e, ':bp\r');
  assert('bp_prev', ':bp goes to prev', 2, e._currentBufId);
  assert('bp_name', 'first.txt', 'first.txt', e._fileName);
}

// ── Test: :b N switches to buffer by number ──
{
  const e = new VimEngine({ rows: 20, cols: 40 });
  e.loadFile('first\n', 'first.txt');
  e.loadFile('second\n', 'second.txt');
  feedKeys(e, ':b 2\r');
  assert('b_num', ':b 2 switches to buffer 2', 2, e._currentBufId);
  assert('b_num_name', 'first.txt', 'first.txt', e._fileName);
}

// ── Test: :b name switches by name ──
{
  const e = new VimEngine({ rows: 20, cols: 40 });
  e.loadFile('first\n', 'first.txt');
  e.loadFile('second\n', 'second.txt');
  feedKeys(e, ':b first\r');
  assert('b_name', ':b first matches', 2, e._currentBufId);
}

// ── Test: :b invalid shows error ──
{
  const e = new VimEngine({ rows: 20, cols: 40 });
  feedKeys(e, ':b 999\r');
  assert('b_invalid', 'error for invalid buffer', true, e.commandLine.includes('E86'));
}

// ── Test: Ctrl-^ toggles alternate buffer ──
{
  const e = new VimEngine({ rows: 20, cols: 40 });
  e.loadFile('first\n', 'first.txt');
  e.loadFile('second\n', 'second.txt');
  // On buffer 3 (second.txt), alternate is 2 (first.txt)
  e.feedKey('Ctrl-^');
  assert('ctrl6_toggle', 'Ctrl-^ goes to alternate', 2, e._currentBufId);
  assert('ctrl6_name', 'on first.txt', 'first.txt', e._fileName);
  // Toggle back
  e.feedKey('Ctrl-^');
  assert('ctrl6_back', 'Ctrl-^ returns', 3, e._currentBufId);
  assert('ctrl6_back_name', 'on second.txt', 'second.txt', e._fileName);
}

// ── Test: Ctrl-^ with no alternate shows error ──
{
  const e = new VimEngine({ rows: 20, cols: 40 });
  e.feedKey('Ctrl-^');
  assert('ctrl6_noalt', 'error when no alternate', true, e.commandLine.includes('E23'));
}

// ── Test: :bd deletes buffer ──
{
  const e = new VimEngine({ rows: 20, cols: 40 });
  e.loadFile('first\n', 'first.txt');
  e.loadFile('second\n', 'second.txt');
  feedKeys(e, ':bd\r');
  assert('bd_count', 'buffer removed', 2, e._bufferList.length);
  assert('bd_not_third', 'buffer 3 is gone', null, e._getBufEntry(3));
}

// ── Test: :bd on last buffer clears it ──
{
  const e = new VimEngine({ rows: 20, cols: 40 });
  feedKeys(e, ':bd\r');
  assert('bd_last_count', 'still 1 buffer', 1, e._bufferList.length);
  assert('bd_last_empty', 'buffer is empty', '', e.buffer.lines[0]);
}

// ── Test: :ls shows buffer list in message prompt ──
{
  const e = new VimEngine({ rows: 20, cols: 40 });
  e.loadFile('hello\n', 'test.txt');
  feedKeys(e, ':ls\r');
  assert('ls_prompt', ':ls shows message prompt', true, e._messagePrompt !== null);
  assert('ls_lines', ':ls has 3 lines (header + 2 buffers)', 3, e._messagePrompt.lines.length);
}

// ── Test: Buffer state is preserved when switching ──
{
  const e = new VimEngine({ rows: 20, cols: 40 });
  e.loadFile('first line\nsecond line\n', 'first.txt');
  // Move cursor to line 2
  feedKeys(e, 'j');
  assert('state_before', 'cursor on line 2', 1, e.cursor.row);
  // Load another file
  e.loadFile('other file\n', 'other.txt');
  assert('state_other', 'on other file', 0, e.cursor.row);
  // Switch back to first.txt
  e.feedKey('Ctrl-^');
  assert('state_restored', 'cursor restored to line 2', 1, e.cursor.row);
  assert('state_file', 'filename restored', 'first.txt', e._fileName);
}

// ── Test: :new creates new buffer in split ──
{
  const e = new VimEngine({ rows: 20, cols: 40 });
  e.loadFile('hello\n', 'test.txt');
  const initialBufCount = e._bufferList.length;
  feedKeys(e, ':new\r');
  assert('new_bufcount', ':new adds buffer', initialBufCount + 1, e._bufferList.length);
  assert('new_wins', ':new creates split', 2, e._windows.length);
  assert('new_empty', 'new buffer is empty', '', e.buffer.lines[0]);
}

console.log(`\n${passed}/${passed + failed} passed, ${failed} failed`);
if (failed > 0) process.exit(1);
