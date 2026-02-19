/**
 * VimFu Simulator – Unit Tests (Jest)
 *
 * Tests the engine logic directly (no DOM, no Neovim).
 * For ground-truth comparisons against Neovim, see compare_test_v2.js.
 */

import { describe, test, expect, beforeEach } from '@jest/globals';
import { VimEngine, Mode } from '../src/engine.js';
import { Screen } from '../src/screen.js';

const ROWS = 20;
const COLS = 40;

/** Helper: create an engine and feed a key sequence. */
function run(keys, initialContent = '') {
  const engine = new VimEngine({ rows: ROWS, cols: COLS });
  if (initialContent) {
    engine.loadFile(initialContent);
  }
  for (const ch of keys) {
    let key = ch;
    if (ch === '\x1b') key = 'Escape';
    else if (ch === '\r' || ch === '\n') key = 'Enter';
    else if (ch === '\x08' || ch === '\x7f') key = 'Backspace';
    engine.feedKey(key);
  }
  return engine;
}

/** Get the text area lines (first ROWS-2 rows) from the screen. */
function textLines(engine) {
  const screen = new Screen(ROWS, COLS);
  return screen.renderText(engine).slice(0, ROWS - 2);
}

/** Get just the buffer lines (no padding). */
function bufLines(engine) {
  return [...engine.buffer.lines];
}

// ─────────────────────────────────────────
// Mode transitions
// ─────────────────────────────────────────

describe('mode transitions', () => {
  test('starts in normal mode', () => {
    const e = run('');
    expect(e.mode).toBe(Mode.NORMAL);
  });

  test('i enters insert mode', () => {
    const e = run('i');
    expect(e.mode).toBe(Mode.INSERT);
  });

  test('Escape returns to normal mode', () => {
    const e = run('i\x1b');
    expect(e.mode).toBe(Mode.NORMAL);
  });

  test('a enters insert mode', () => {
    const e = run('a', 'Hello');
    expect(e.mode).toBe(Mode.INSERT);
  });

  test('A enters insert mode at end of line', () => {
    const e = run('A', 'Hello');
    expect(e.mode).toBe(Mode.INSERT);
    expect(e.cursor.col).toBe(5);
  });

  test('I enters insert mode at first non-blank', () => {
    const e = run('I', '  Hello');
    expect(e.mode).toBe(Mode.INSERT);
    expect(e.cursor.col).toBe(2);
  });

  test('o opens line below and enters insert mode', () => {
    const e = run('o', 'Hello');
    expect(e.mode).toBe(Mode.INSERT);
    expect(e.cursor.row).toBe(1);
    expect(bufLines(e)).toEqual(['Hello', '']);
  });

  test('O opens line above and enters insert mode', () => {
    const e = run('O', 'Hello');
    expect(e.mode).toBe(Mode.INSERT);
    expect(e.cursor.row).toBe(0);
    expect(bufLines(e)).toEqual(['', 'Hello']);
  });
});

// ─────────────────────────────────────────
// Normal mode movement
// ─────────────────────────────────────────

describe('normal mode movement', () => {
  test('h moves left', () => {
    const e = run('lllh', 'Hello World');
    expect(e.cursor.col).toBe(2);
  });

  test('h does not go past column 0', () => {
    const e = run('hhhhh', 'Hello');
    expect(e.cursor.col).toBe(0);
  });

  test('l moves right', () => {
    const e = run('lll', 'Hello World');
    expect(e.cursor.col).toBe(3);
  });

  test('l stops at last character in normal mode', () => {
    const e = run('llllllllllllllllllll', 'Short');
    expect(e.cursor.col).toBe(4); // last char of "Short"
  });

  test('j moves down', () => {
    const e = run('jj', 'Line 1\nLine 2\nLine 3\nLine 4');
    expect(e.cursor.row).toBe(2);
  });

  test('j does not go past last line', () => {
    const e = run('jjjjjjjjjj', 'Line 1\nLine 2');
    expect(e.cursor.row).toBe(1);
  });

  test('k moves up', () => {
    const e = run('jjk', 'A\nB\nC');
    expect(e.cursor.row).toBe(1);
  });

  test('k does not go past row 0', () => {
    const e = run('kkkk', 'Hello');
    expect(e.cursor.row).toBe(0);
  });

  test('cursor col is clamped when moving to a shorter line', () => {
    const e = run('llllj', 'Long line\nHi');
    // Moved right 4 on "Long line", then down to "Hi" (length 2)
    // Should clamp to col 1 (last char of "Hi")
    expect(e.cursor.col).toBe(1);
  });
});

// ─────────────────────────────────────────
// Insert mode editing
// ─────────────────────────────────────────

describe('insert mode editing', () => {
  test('typing inserts characters', () => {
    const e = run('iHello\x1b');
    expect(bufLines(e)).toEqual(['Hello']);
  });

  test('typing multiple words', () => {
    const e = run('iHello World\x1b');
    expect(bufLines(e)).toEqual(['Hello World']);
  });

  test('Enter splits line', () => {
    const e = run('iHello\rWorld\x1b');
    expect(bufLines(e)).toEqual(['Hello', 'World']);
  });

  test('Backspace deletes character', () => {
    const e = run('iHello\x08\x08\x1b');
    expect(bufLines(e)).toEqual(['Hel']);
  });

  test('Backspace at start of line joins with previous', () => {
    const e = run('ji\x08\x1b', 'Line 1\nLine 2');
    expect(bufLines(e)).toEqual(['Line 1Line 2']);
  });

  test('Backspace at start of first line does nothing', () => {
    const e = run('i\x08\x1b', 'Hello');
    expect(bufLines(e)).toEqual(['Hello']);
  });

  test('insert in middle of text', () => {
    const e = run('lliXY\x1b', 'Hello');
    expect(bufLines(e)).toEqual(['HeXYllo']);
  });

  test('append after cursor', () => {
    const e = run('aXY\x1b', 'Hello');
    expect(bufLines(e)).toEqual(['HXYello']);
  });

  test('append at end of line', () => {
    const e = run('AXY\x1b', 'Hello');
    expect(bufLines(e)).toEqual(['HelloXY']);
  });

  test('open below and type', () => {
    const e = run('onew line\x1b', 'First line');
    expect(bufLines(e)).toEqual(['First line', 'new line']);
  });

  test('open above and type', () => {
    const e = run('Onew line\x1b', 'First line');
    expect(bufLines(e)).toEqual(['new line', 'First line']);
  });
});

// ─────────────────────────────────────────
// x (delete character in normal mode)
// ─────────────────────────────────────────

describe('x delete', () => {
  test('x deletes character at cursor', () => {
    const e = run('x', 'Hello');
    expect(bufLines(e)).toEqual(['ello']);
  });

  test('x in middle of line', () => {
    const e = run('llx', 'Hello');
    expect(bufLines(e)).toEqual(['Helo']);
  });

  test('multiple x', () => {
    const e = run('xxx', 'Hello');
    expect(bufLines(e)).toEqual(['lo']);
  });

  test('x on empty line does nothing', () => {
    const e = run('x');
    expect(bufLines(e)).toEqual(['']);
  });

  test('x clamps cursor when at end', () => {
    const e = run('llllx', 'Hello');
    // cursor at col 4 ('o'), delete it → "Hell", cursor clamps to col 3
    expect(bufLines(e)).toEqual(['Hell']);
    expect(e.cursor.col).toBe(3);
  });
});

// ─────────────────────────────────────────
// Cursor position after Escape
// ─────────────────────────────────────────

describe('cursor after Escape', () => {
  test('cursor moves back one column', () => {
    const e = run('iHello\x1b');
    expect(e.cursor.col).toBe(4); // was at 5, back to 4
  });

  test('cursor stays at 0 if already there', () => {
    const e = run('i\x1b', 'Hello');
    expect(e.cursor.col).toBe(0);
  });
});

// ─────────────────────────────────────────
// Screen rendering
// ─────────────────────────────────────────

describe('screen rendering', () => {
  test('produces correct number of rows', () => {
    const engine = run('', 'Hello');
    const screen = new Screen(ROWS, COLS);
    const frame = screen.render(engine);
    expect(frame.lines.length).toBe(ROWS);
    expect(frame.rows).toBe(ROWS);
    expect(frame.cols).toBe(COLS);
  });

  test('first line shows buffer content', () => {
    const engine = run('', 'Hello World');
    const screen = new Screen(ROWS, COLS);
    const lines = screen.renderText(engine);
    expect(lines[0]).toBe('Hello World' + ' '.repeat(COLS - 11));
  });

  test('empty lines past buffer show tilde', () => {
    const engine = run('', 'Only one line');
    const screen = new Screen(ROWS, COLS);
    const lines = screen.renderText(engine);
    // Line 1 (second text row) should start with '~'
    expect(lines[1][0]).toBe('~');
  });

  test('cursor position in frame', () => {
    const engine = run('ll', 'Hello');
    const screen = new Screen(ROWS, COLS);
    const frame = screen.render(engine);
    expect(frame.cursor.row).toBe(0);
    expect(frame.cursor.col).toBe(2);
  });

  test('frame has correct format fields', () => {
    const engine = run('', 'Hello');
    const screen = new Screen(ROWS, COLS);
    const frame = screen.render(engine);
    expect(frame).toHaveProperty('rows');
    expect(frame).toHaveProperty('cols');
    expect(frame).toHaveProperty('cursor');
    expect(frame).toHaveProperty('defaultFg');
    expect(frame).toHaveProperty('defaultBg');
    expect(frame).toHaveProperty('lines');
    expect(frame.cursor).toHaveProperty('row');
    expect(frame.cursor).toHaveProperty('col');
    expect(frame.cursor).toHaveProperty('visible');
    for (const line of frame.lines) {
      expect(line).toHaveProperty('text');
      expect(line).toHaveProperty('runs');
    }
  });
});

// ─────────────────────────────────────────
// Scrolling
// ─────────────────────────────────────────

describe('scrolling', () => {
  test('cursor moving past viewport scrolls down', () => {
    // 20 rows total, 18 text rows → buffer needs > 18 lines
    const lines = Array.from({ length: 30 }, (_, i) => `Line ${i + 1}`);
    const engine = run('j'.repeat(25), lines.join('\n'));
    // Should have scrolled
    expect(engine.scrollTop).toBeGreaterThan(0);
    expect(engine.cursor.row).toBe(25);
  });

  test('cursor moving up scrolls back', () => {
    const lines = Array.from({ length: 30 }, (_, i) => `Line ${i + 1}`);
    const keys = 'j'.repeat(25) + 'k'.repeat(25);
    const engine = run(keys, lines.join('\n'));
    expect(engine.scrollTop).toBe(0);
    expect(engine.cursor.row).toBe(0);
  });
});
