/**
 * OSC dispatch — title (OSC 0/2), hyperlinks (OSC 8), palette
 * (OSC 4 / 104), and that unknown OSCs are silently ignored.
 */

import { describe, test, expect, beforeEach } from '@jest/globals';
import { Terminal } from '../src/terminal.js';
import { resolveColor, resetPalette } from '../src/palette.js';

let term;
beforeEach(() => {
  resetPalette();
  term = new Terminal({ rows: 4, cols: 20 });
});

describe('OSC 0 / OSC 2 — window title', () => {
  test('OSC 0 ; title ST sets title', () => {
    let captured = null;
    term.onTitle = (t) => { captured = t; };
    term.write('\x1b]0;my-window\x1b\\');
    expect(captured).toBe('my-window');
    expect(term.screen.title).toBe('my-window');
  });

  test('OSC 2 ; title ST sets title (window title only)', () => {
    let captured = null;
    term.onTitle = (t) => { captured = t; };
    term.write('\x1b]2;just-the-window\x07'); // BEL terminator also valid
    expect(captured).toBe('just-the-window');
  });

  test('multi-line / unicode title is preserved', () => {
    let captured = null;
    term.onTitle = (t) => { captured = t; };
    term.write('\x1b]0;hello 🐍 vim\x1b\\');
    expect(captured).toBe('hello 🐍 vim');
  });
});

describe('OSC 4 — palette set', () => {
  test('OSC 4 ; n ; rgb:RR/GG/BB sets palette entry n', () => {
    term.write('\x1b]4;42;rgb:ff/00/00\x1b\\');
    // Now SGR 38;5;42 should resolve to red
    term.write('\x1b[38;5;42m');
    const fg = term.screen.curFg;
    expect(resolveColor(fg, true)).toBe('ff0000');
  });

  test('OSC 4 ; n ; #RRGGBB also works', () => {
    term.write('\x1b]4;77;#00ff00\x1b\\');
    term.write('\x1b[38;5;77m');
    expect(resolveColor(term.screen.curFg, true)).toBe('00ff00');
  });

  test('OSC 4 supports multiple pairs in one sequence', () => {
    term.write('\x1b]4;10;rgb:11/22/33;11;rgb:aa/bb/cc\x1b\\');
    term.write('\x1b[38;5;10m');
    expect(resolveColor(term.screen.curFg, true)).toBe('112233');
    term.write('\x1b[38;5;11m');
    expect(resolveColor(term.screen.curFg, true)).toBe('aabbcc');
  });

  test('OSC 104 with no args resets the palette to defaults', () => {
    term.write('\x1b]4;0;rgb:de/ad/be\x1b\\');
    term.write('\x1b[38;5;0m');
    expect(resolveColor(term.screen.curFg, true)).toBe('deadbe');
    term.write('\x1b]104\x07');
    term.write('\x1b[38;5;0m');
    // Default palette entry 0 = black
    expect(resolveColor(term.screen.curFg, true)).toBe('000000');
  });
});

describe('OSC 8 — hyperlinks', () => {
  test('OSC 8 ; ; URI starts a hyperlink', () => {
    const events = [];
    term.onHyperlink = (uri) => events.push(uri);
    term.write('\x1b]8;;https://example.com\x1b\\');
    expect(events).toEqual(['https://example.com']);
  });

  test('OSC 8 ; ; (empty URI) ends the hyperlink', () => {
    const events = [];
    term.onHyperlink = (uri) => events.push(uri);
    term.write('\x1b]8;;https://x.example\x1b\\');
    term.write('\x1b]8;;\x1b\\');
    expect(events).toEqual(['https://x.example', null]);
  });
});

describe('Unknown OSC numbers are silently ignored', () => {
  test('OSC 999 ; whatever ST does not throw', () => {
    expect(() => term.write('\x1b]999;some payload\x1b\\')).not.toThrow();
  });
});

describe('Title can be reset by OSC 0 with empty string', () => {
  test('empty title clears', () => {
    let captured = 'something';
    term.onTitle = (t) => { captured = t; };
    term.write('\x1b]0;\x1b\\');
    expect(captured).toBe('');
  });
});
