/**
 * Unit tests for KeyInput — keyboard event → host byte sequence.
 *
 * We don't have a DOM in Node, so we hand-craft minimal mock
 * KeyboardEvent shapes that the handler reads (key, ctrlKey, altKey,
 * shiftKey, metaKey, plus a no-op preventDefault).
 */

import { describe, test, expect, beforeEach } from '@jest/globals';
import { Terminal } from '../src/terminal.js';
import { KeyInput } from '../src/input.js';

function ev(key, mods = {}) {
  return {
    key,
    ctrlKey:  !!mods.ctrl,
    altKey:   !!mods.alt,
    shiftKey: !!mods.shift,
    metaKey:  !!mods.meta,
    preventDefault() {},
  };
}

let term, ki, sent;

beforeEach(() => {
  term = new Terminal({ rows: 24, cols: 80 });
  ki = new KeyInput(term);
  sent = [];
  term.onInput = (s) => sent.push(s);
});

describe('Cursor keys', () => {
  test('arrow keys in normal mode use CSI', () => {
    ki.handle(ev('ArrowUp'));    expect(sent.pop()).toBe('\x1b[A');
    ki.handle(ev('ArrowDown'));  expect(sent.pop()).toBe('\x1b[B');
    ki.handle(ev('ArrowRight')); expect(sent.pop()).toBe('\x1b[C');
    ki.handle(ev('ArrowLeft'));  expect(sent.pop()).toBe('\x1b[D');
    ki.handle(ev('Home'));       expect(sent.pop()).toBe('\x1b[H');
    ki.handle(ev('End'));        expect(sent.pop()).toBe('\x1b[F');
  });

  test('arrow keys in application cursor mode use SS3', () => {
    term.screen.appCursorKeys = true;
    ki.handle(ev('ArrowUp'));    expect(sent.pop()).toBe('\x1bOA');
    ki.handle(ev('ArrowDown'));  expect(sent.pop()).toBe('\x1bOB');
    ki.handle(ev('ArrowRight')); expect(sent.pop()).toBe('\x1bOC');
    ki.handle(ev('ArrowLeft'));  expect(sent.pop()).toBe('\x1bOD');
    ki.handle(ev('Home'));       expect(sent.pop()).toBe('\x1bOH');
    ki.handle(ev('End'));        expect(sent.pop()).toBe('\x1bOF');
  });

  test('cursor keys with shift use CSI 1;M form', () => {
    ki.handle(ev('ArrowUp', { shift: true }));
    expect(sent.pop()).toBe('\x1b[1;2A');
    ki.handle(ev('ArrowRight', { ctrl: true }));
    expect(sent.pop()).toBe('\x1b[1;5C');
    ki.handle(ev('ArrowLeft', { alt: true, shift: true }));
    expect(sent.pop()).toBe('\x1b[1;4D');
  });

  test('PageUp/PageDown/Insert/Delete use CSI ~', () => {
    ki.handle(ev('PageUp'));   expect(sent.pop()).toBe('\x1b[5~');
    ki.handle(ev('PageDown')); expect(sent.pop()).toBe('\x1b[6~');
    ki.handle(ev('Insert'));   expect(sent.pop()).toBe('\x1b[2~');
    ki.handle(ev('Delete'));   expect(sent.pop()).toBe('\x1b[3~');
  });
});

describe('Function keys', () => {
  test('F1..F4 use SS3 in normal mode', () => {
    ki.handle(ev('F1')); expect(sent.pop()).toBe('\x1bOP');
    ki.handle(ev('F2')); expect(sent.pop()).toBe('\x1bOQ');
    ki.handle(ev('F3')); expect(sent.pop()).toBe('\x1bOR');
    ki.handle(ev('F4')); expect(sent.pop()).toBe('\x1bOS');
  });

  test('F5..F12 use CSI Ps ~ form', () => {
    ki.handle(ev('F5'));  expect(sent.pop()).toBe('\x1b[15~');
    ki.handle(ev('F6'));  expect(sent.pop()).toBe('\x1b[17~');
    ki.handle(ev('F12')); expect(sent.pop()).toBe('\x1b[24~');
  });

  test('F-keys with modifiers add the modifier code', () => {
    ki.handle(ev('F1',  { shift: true })); expect(sent.pop()).toBe('\x1b[1;2P');
    ki.handle(ev('F12', { ctrl:  true })); expect(sent.pop()).toBe('\x1b[24;5~');
  });
});

describe('Control + special bytes', () => {
  test('Enter sends CR', () => {
    ki.handle(ev('Enter')); expect(sent.pop()).toBe('\r');
  });
  test('Backspace sends DEL by default, BS with Ctrl', () => {
    ki.handle(ev('Backspace'));               expect(sent.pop()).toBe('\x7f');
    ki.handle(ev('Backspace', { ctrl:true })); expect(sent.pop()).toBe('\x08');
  });
  test('Tab and Shift-Tab', () => {
    ki.handle(ev('Tab'));                expect(sent.pop()).toBe('\t');
    ki.handle(ev('Tab', { shift:true })); expect(sent.pop()).toBe('\x1b[Z');
  });
  test('Escape sends ESC', () => {
    ki.handle(ev('Escape')); expect(sent.pop()).toBe('\x1b');
  });
});

describe('Ctrl-letter → C0 control', () => {
  test('Ctrl-A through Ctrl-Z', () => {
    for (let i = 0; i < 26; i++) {
      const ch = String.fromCharCode(0x61 + i);
      ki.handle(ev(ch, { ctrl: true }));
      expect(sent.pop()).toBe(String.fromCharCode(i + 1));
    }
  });
  test('Ctrl-@ → NUL, Ctrl-[ → ESC, Ctrl-\\ → FS, Ctrl-] → GS, Ctrl-^ → RS, Ctrl-_ → US', () => {
    ki.handle(ev('@', { ctrl: true }));  expect(sent.pop()).toBe('\x00');
    ki.handle(ev('[', { ctrl: true }));  expect(sent.pop()).toBe('\x1b');
    ki.handle(ev('\\',{ ctrl: true }));  expect(sent.pop()).toBe('\x1c');
    ki.handle(ev(']', { ctrl: true }));  expect(sent.pop()).toBe('\x1d');
    ki.handle(ev('^', { ctrl: true }));  expect(sent.pop()).toBe('\x1e');
    ki.handle(ev('_', { ctrl: true }));  expect(sent.pop()).toBe('\x1f');
  });
});

describe('Alt-prefix', () => {
  test('Alt-letter sends ESC + letter', () => {
    ki.handle(ev('a', { alt: true })); expect(sent.pop()).toBe('\x1ba');
    ki.handle(ev('x', { alt: true })); expect(sent.pop()).toBe('\x1bx');
  });
});

describe('Plain printable', () => {
  test('letters send their codepoint', () => {
    ki.handle(ev('a')); expect(sent.pop()).toBe('a');
    ki.handle(ev('Z')); expect(sent.pop()).toBe('Z');
    ki.handle(ev(' ')); expect(sent.pop()).toBe(' ');
  });
});

describe('Bracketed paste', () => {
  test('paste sends raw text when bracketed-paste mode is off', () => {
    const e = {
      clipboardData: { getData: () => 'hello' },
      preventDefault() {},
    };
    ki.paste(e);
    expect(sent.pop()).toBe('hello');
  });

  test('paste wraps in ESC[200~ … ESC[201~ when mode is on', () => {
    term.screen.bracketedPaste = true;
    const e = {
      clipboardData: { getData: () => 'pasted' },
      preventDefault() {},
    };
    ki.paste(e);
    expect(sent.pop()).toBe('\x1b[200~pasted\x1b[201~');
  });
});
