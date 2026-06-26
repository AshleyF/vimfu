/**
 * Unit tests for the raw VT parser (no Screen).  These exercise the
 * state machine itself: print, execute, ESC/CSI/OSC/DCS dispatch.
 */

import { describe, test, expect } from '@jest/globals';
import { Parser } from '../src/parser.js';

function collect() {
  const events = [];
  const h = {
    print:        cp => events.push(['print', cp]),
    execute:       b => events.push(['execute', b]),
    escDispatch: (i, f) => events.push(['esc', i.slice(), f]),
    csiDispatch: (p, i, f) => events.push(['csi', p.map(g => g.slice()), i.slice(), f]),
    oscDispatch:   s => events.push(['osc', s]),
    dcsHook:    (p, i, f) => events.push(['dcsHook', p.map(g => g.slice()), i.slice(), f]),
    dcsPut:        b => events.push(['dcsPut', b]),
    dcsUnhook:    () => events.push(['dcsUnhook']),
  };
  return { events, parser: new Parser(h) };
}

describe('Parser', () => {
  test('prints plain ASCII as codepoints', () => {
    const { events, parser } = collect();
    parser.parseString('abc');
    expect(events).toEqual([['print', 0x61], ['print', 0x62], ['print', 0x63]]);
  });

  test('emits execute for C0 controls', () => {
    const { events, parser } = collect();
    parser.parseBytes('\r\n');
    expect(events).toEqual([['execute', 0x0d], ['execute', 0x0a]]);
  });

  test('dispatches plain ESC <final>', () => {
    const { events, parser } = collect();
    parser.parseBytes('\x1b7');
    expect(events).toEqual([['esc', [], 0x37]]);
  });

  test('dispatches CSI with no params', () => {
    const { events, parser } = collect();
    parser.parseBytes('\x1b[H');
    expect(events).toEqual([['csi', [[]], [], 0x48]]);
  });

  test('dispatches CSI with multiple params', () => {
    const { events, parser } = collect();
    parser.parseBytes('\x1b[3;5;7H');
    expect(events).toEqual([['csi', [[3], [5], [7]], [], 0x48]]);
  });

  test('dispatches CSI with private intermediate', () => {
    const { events, parser } = collect();
    parser.parseBytes('\x1b[?1049h');
    expect(events).toEqual([['csi', [[1049]], [0x3f], 0x68]]);
  });

  test('dispatches CSI with sub-parameters (colon)', () => {
    const { events, parser } = collect();
    parser.parseBytes('\x1b[38:2::255:128:0m');
    // params[0] = [38, 2, 0, 255, 128, 0] — '::' makes an empty param of 0
    expect(events[0][0]).toBe('csi');
    expect(events[0][1][0]).toEqual([38, 2, 0, 255, 128, 0]);
    expect(events[0][3]).toBe(0x6d);
  });

  test('dispatches OSC ; terminated by BEL', () => {
    const { events, parser } = collect();
    parser.parseBytes('\x1b]0;my title\x07');
    expect(events).toEqual([['osc', '0;my title']]);
  });

  test('dispatches OSC terminated by ST (ESC \\)', () => {
    const { events, parser } = collect();
    parser.parseBytes('\x1b]2;another\x1b\\');
    expect(events).toEqual([['osc', '2;another']]);
  });

  test('UTF-8 multi-byte assembled into one print', () => {
    const { events, parser } = collect();
    parser.parseBytes('\xe2\x86\x92');   // U+2192 →
    expect(events).toEqual([['print', 0x2192]]);
  });

  test('DCS hook/put/unhook for sixel', () => {
    const { events, parser } = collect();
    parser.parseBytes('\x1bPq#0;2;100;100;100~~~~\x1b\\');
    // First event is dcsHook with final 'q'
    expect(events[0]).toEqual(['dcsHook', [[]], [], 0x71]);
    expect(events.find(e => e[0] === 'dcsPut')[1]).toBe(0x23);     // '#'
    expect(events[events.length - 1]).toEqual(['dcsUnhook']);
  });

  test('CAN aborts an in-progress CSI', () => {
    const { events, parser } = collect();
    parser.parseBytes('\x1b[3\x18');
    expect(events).toEqual([['execute', 0x18]]);
  });

  test('SUB aborts an in-progress ESC', () => {
    const { events, parser } = collect();
    parser.parseBytes('\x1b\x1a');
    expect(events).toEqual([['execute', 0x1a]]);
  });
});
