/**
 * Tests for DEC private modes + ANSI modes that change observable
 * terminal state (cursor, input mode, wrap, paste, etc.).
 */

import { describe, test, expect, beforeEach } from '@jest/globals';
import { Terminal } from '../src/terminal.js';

let term;
beforeEach(() => { term = new Terminal({ rows: 6, cols: 20 }); });

describe('DECCKM (?1) — application cursor keys', () => {
  test('default is normal mode', () => {
    expect(term.screen.appCursorKeys).toBe(false);
  });
  test('set turns on, reset turns off', () => {
    term.write('\x1b[?1h');
    expect(term.screen.appCursorKeys).toBe(true);
    term.write('\x1b[?1l');
    expect(term.screen.appCursorKeys).toBe(false);
  });
});

describe('DECTCEM (?25) — cursor visibility', () => {
  test('default is visible', () => {
    expect(term.screen.cursorVisible).toBe(true);
    expect(term.toFrame().cursor.visible).toBe(true);
  });
  test('?25l hides, ?25h shows', () => {
    term.write('\x1b[?25l');
    expect(term.toFrame().cursor.visible).toBe(false);
    term.write('\x1b[?25h');
    expect(term.toFrame().cursor.visible).toBe(true);
  });
});

describe('DECAWM (?7) — autowrap', () => {
  test('default is on', () => {
    expect(term.screen.autoWrap).toBe(true);
  });
  test('disabling stops wrap at right margin', () => {
    term.write('\x1b[?7l');
    term.write('X'.repeat(30));        // way past cols=20
    // All 'X' should clamp at the rightmost column rather than wrap.
    const f = term.toFrame();
    // Row 0 has filled-then-clamped behaviour; row 1 should be empty.
    expect(f.lines[1].text.trim()).toBe('');
  });
  test('re-enabling allows wrap again', () => {
    term.write('\x1b[?7l');
    term.write('X'.repeat(25));
    term.write('\x1b[?7h');
    term.write('Y'.repeat(5));
    // The Y's should now wrap to row 1
    expect(term.toFrame().lines[1].text.startsWith('Y')).toBe(true);
  });
});

describe('IRM (CSI 4 h/l) — insert mode', () => {
  test('default is off (overwrite)', () => {
    expect(term.screen.insertMode).toBe(false);
  });
  test('set shifts existing cells right when printing', () => {
    term.write('ABCDEF\x1b[1;1H');
    term.write('\x1b[4h');
    term.write('!');
    expect(term.toFrame().lines[0].text.startsWith('!ABCDEF')).toBe(true);
  });
  test('reset restores overwrite', () => {
    term.write('ABCDEF\x1b[1;1H');
    term.write('\x1b[4l');
    term.write('!');
    expect(term.toFrame().lines[0].text.startsWith('!BCDEF')).toBe(true);
  });
});

describe('Bracketed paste (?2004)', () => {
  test('default is off', () => {
    expect(term.screen.bracketedPaste).toBe(false);
  });
  test('?2004h enables, ?2004l disables', () => {
    term.write('\x1b[?2004h');
    expect(term.screen.bracketedPaste).toBe(true);
    term.write('\x1b[?2004l');
    expect(term.screen.bracketedPaste).toBe(false);
  });
});

describe('DECOM (?6) — origin mode', () => {
  test('default is off; CUP is absolute', () => {
    term.write('\x1b[3;6r');                  // region rows 2..5 (0-based)
    term.write('\x1b[1;1H');
    expect(term.screen.cy).toBe(0);
    expect(term.screen.cx).toBe(0);
  });
  test('on, CUP is relative to scroll region top', () => {
    term.write('\x1b[3;6r');
    term.write('\x1b[?6h');
    term.write('\x1b[1;1H');
    expect(term.screen.cy).toBe(2);           // region top row
    expect(term.screen.cx).toBe(0);
  });
});

describe('DECSCUSR (CSI Ps SP q) — cursor style', () => {
  test('terminal records the requested cursor style number', () => {
    term.write('\x1b[5 q');
    expect(term._cursorStyle).toBe(5);
    term.write('\x1b[2 q');
    expect(term._cursorStyle).toBe(2);
  });
});

describe('DA (CSI c) — device attributes', () => {
  test('primary DA replies with VT102 / colour-capable identification', () => {
    const replies = [];
    term.onResponse = (s) => replies.push(s);
    term.write('\x1b[c');
    expect(replies.pop()).toBe('\x1b[?62;22c');
  });
  test('secondary DA replies with terminal type', () => {
    const replies = [];
    term.onResponse = (s) => replies.push(s);
    term.write('\x1b[>c');
    expect(replies.pop()).toBe('\x1b[>0;95;0c');
  });
});

describe('DSR (CSI n) — device status', () => {
  test('DSR 5 reports OK', () => {
    const replies = [];
    term.onResponse = (s) => replies.push(s);
    term.write('\x1b[5n');
    expect(replies.pop()).toBe('\x1b[0n');
  });
  test('DSR 6 reports cursor position (1-based)', () => {
    const replies = [];
    term.onResponse = (s) => replies.push(s);
    term.write('\x1b[3;5H');
    term.write('\x1b[6n');
    expect(replies.pop()).toBe('\x1b[3;5R');
  });
});

describe('RIS (ESC c) — full reset', () => {
  test('reset clears screen and restores defaults', () => {
    term.write('\x1b[31m');
    term.write('hello');
    term.write('\x1b[?7l');
    term.write('\x1bc');
    expect(term.screen.curFg).toBe(-1);       // default fg
    expect(term.screen.autoWrap).toBe(true);
    expect(term.toFrame().lines[0].text.trim()).toBe('');
    expect(term.screen.cx).toBe(0);
    expect(term.screen.cy).toBe(0);
  });
});
