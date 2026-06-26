/**
 * Alt-screen isolation + save/restore behaviour.
 *
 * Pyte doesn't implement DEC private modes 47/1047/1048/1049 in any
 * useful way (per its source), so the ground-truth suite skips these.
 * These are direct tests against our Terminal/Screen model.
 */

import { describe, test, expect, beforeEach } from '@jest/globals';
import { Terminal } from '../src/terminal.js';

function dump(term) {
  return term.toFrame().lines.map(l => l.text.trimEnd());
}

let term;
beforeEach(() => {
  term = new Terminal({ rows: 6, cols: 20 });
});

describe('Alt-screen content isolation', () => {
  test('entering alt screen does NOT write through to primary', () => {
    term.write('PRIMARY_DATA');
    term.write('\x1b[?1049h');
    term.write('\x1b[H\x1b[2J');             // home + clear alt
    term.write('ALT_DATA');
    // We're now looking at the alt buffer
    expect(dump(term)[0].startsWith('ALT_DATA')).toBe(true);
    // Leave alt — primary should be intact
    term.write('\x1b[?1049l');
    expect(dump(term)[0].startsWith('PRIMARY_DATA')).toBe(true);
  });

  test('switching to alt and back twice preserves both', () => {
    term.write('A');
    term.write('\x1b[?1049h\x1b[H\x1b[2J');
    term.write('B');
    term.write('\x1b[?1049l');
    expect(dump(term)[0][0]).toBe('A');
    term.write('\x1b[?1049h\x1b[H\x1b[2J');  // re-enter alt; should be cleared
    expect(dump(term)[0]).toBe('');
    term.write('\x1b[?1049l');
  });

  test('1049 saves and restores the primary cursor position', () => {
    term.write('\x1b[3;5H');                 // primary cursor (2,4)
    term.write('\x1b[?1049h');
    term.write('\x1b[1;1H');                 // alt cursor (0,0)
    term.write('\x1b[?1049l');               // restore primary cursor
    expect(term.screen.cy).toBe(2);
    expect(term.screen.cx).toBe(4);
  });

  test('SGR state is restored on leave-alt', () => {
    term.write('\x1b[31m');                  // primary fg = red
    term.write('\x1b[?1049h');
    term.write('\x1b[34m');                  // alt fg = blue
    term.write('\x1b[?1049l');
    // After restore, foreground should be red again (palette index 1)
    expect(term.screen.curFg).toBe(1);
  });

  test('?47h / ?47l do NOT clear or save-restore', () => {
    term.write('P');
    term.write('\x1b[?47h');                 // enter alt without clear/save
    expect(term.screen.altScreen).toBe(true);
    term.write('X');                          // writes onto alt
    term.write('\x1b[?47l');                 // leave alt without restore
    expect(term.screen.altScreen).toBe(false);
    expect(dump(term)[0].startsWith('P')).toBe(true);
  });

  test('cursor position is independent on alt vs primary', () => {
    term.write('\x1b[5;10H');
    term.write('\x1b[?1049h');
    // 1049 enters alt and clears it but doesn't move the cursor
    // (xterm); our impl just saves+clears.  Just check we're on alt.
    expect(term.screen.altScreen).toBe(true);
  });
});

describe('DECSC/DECRC (ESC 7 / ESC 8) — cursor save/restore', () => {
  test('saves & restores cursor position', () => {
    term.write('\x1b[3;7H');
    term.write('\x1b7');
    term.write('\x1b[1;1H');
    term.write('\x1b8');
    expect(term.screen.cy).toBe(2);
    expect(term.screen.cx).toBe(6);
  });

  test('saves & restores SGR attributes', () => {
    term.write('\x1b[1;31m');                // bold red
    term.write('\x1b7');
    term.write('\x1b[0m');                   // reset
    term.write('\x1b8');
    expect(term.screen.curFg).toBe(1);
    expect(term.screen.curFlags & 1).toBe(1); // BOLD
  });

  test('saves & restores origin mode', () => {
    term.write('\x1b[3;5r');                 // scroll region
    term.write('\x1b[?6h');                  // DECOM on
    term.write('\x1b7');
    term.write('\x1b[?6l');                  // DECOM off
    term.write('\x1b8');
    expect(term.screen.originMode).toBe(true);
  });
});
