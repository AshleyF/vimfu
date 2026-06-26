/**
 * Screen resize behaviour.  Pyte's resize semantics are different
 * from ours (it doesn't preserve content the same way), so these
 * are unit tests against our own Screen model.
 */

import { describe, test, expect, beforeEach } from '@jest/globals';
import { Screen } from '../src/screen.js';
import { Terminal } from '../src/terminal.js';

describe('Screen.resize', () => {
  test('growing keeps existing content in place', () => {
    const s = new Screen(4, 10);
    'hello'.split('').forEach(c => s.putChar(c.charCodeAt(0)));
    s.resize(8, 20);
    expect(s.rows).toBe(8);
    expect(s.cols).toBe(20);
    const row0 = s.toFrame().lines[0].text;
    expect(row0.startsWith('hello')).toBe(true);
  });

  test('shrinking truncates rightmost columns', () => {
    const s = new Screen(2, 10);
    'abcdefghij'.split('').forEach(c => s.putChar(c.charCodeAt(0)));
    s.resize(2, 5);
    expect(s.cols).toBe(5);
    expect(s.toFrame().lines[0].text).toBe('abcde');
  });

  test('shrinking rows truncates bottom rows', () => {
    const s = new Screen(6, 10);
    for (let r = 0; r < 6; r++) {
      s.setCursor(r, 0);
      ('row' + r).split('').forEach(c => s.putChar(c.charCodeAt(0)));
    }
    s.resize(3, 10);
    expect(s.rows).toBe(3);
    expect(s.toFrame().lines[0].text.startsWith('row0')).toBe(true);
    expect(s.toFrame().lines[2].text.startsWith('row2')).toBe(true);
  });

  test('cursor is clamped within new bounds', () => {
    const s = new Screen(10, 20);
    s.setCursor(8, 15);
    s.resize(5, 10);
    expect(s.cy).toBeLessThan(5);
    expect(s.cx).toBeLessThan(10);
  });

  test('scroll region resets to full screen on resize', () => {
    const s = new Screen(10, 20);
    s.scrollTop = 2;
    s.scrollBot = 7;
    s.resize(15, 25);
    expect(s.scrollTop).toBe(0);
    expect(s.scrollBot).toBe(14);
  });

  test('resize is a no-op when dimensions are unchanged', () => {
    const s = new Screen(8, 16);
    'X'.split('').forEach(c => s.putChar(c.charCodeAt(0)));
    const before = s.toFrame();
    s.resize(8, 16);
    expect(s.toFrame()).toEqual(before);
  });

  test('resize preserves alt screen contents independently of primary', () => {
    const s = new Screen(6, 10);
    s.putChar('P'.charCodeAt(0));
    s.enterAlt();
    s.setCursor(0, 0);
    s.putChar('A'.charCodeAt(0));
    s.resize(8, 20);
    // Still on alt
    expect(s.altScreen).toBe(true);
    expect(s.toFrame().lines[0].text[0]).toBe('A');
    s.leaveAlt();
    expect(s.toFrame().lines[0].text[0]).toBe('P');
  });
});

describe('Terminal.resize', () => {
  test('after resize, cursor reports do not break', () => {
    const term = new Terminal({ rows: 24, cols: 80 });
    const replies = [];
    term.onResponse = (s) => replies.push(s);
    term.resize(10, 40);
    term.write('\x1b[5;5H');
    term.write('\x1b[6n');         // CPR
    expect(replies.pop()).toBe('\x1b[5;5R');
  });
});
