/**
 * Terminal — wires the VT parser to the screen, owning all the
 * dispatch logic for CSI / ESC / OSC / DCS sequences.
 *
 * Usage:
 *   const term = new Terminal({ rows: 24, cols: 80 });
 *   term.write("hello\r\n");
 *   const frame = term.toFrame();
 *
 * For round-trip I/O (cursor key responses, DA, DSR, mouse) hook
 * `term.onResponse = (bytes) => ...` to send bytes back to the host.
 */

import { Parser } from './parser.js';
import { Screen, FLAG } from './screen.js';
import {
  DEFAULT_FG_INDEX, DEFAULT_BG_INDEX,
  paletteIndex, parseSgrColor, setPaletteEntry, resetPalette,
} from './palette.js';

// DEC special graphics ('0' charset): 0x60..0x7e → unicode box drawing.
// Keys are the ASCII byte received; values are the rendered codepoint.
const DEC_SPECIAL = {
  0x60: 0x25c6, 0x61: 0x2592, 0x62: 0x2409, 0x63: 0x240c,
  0x64: 0x240d, 0x65: 0x240a, 0x66: 0x00b0, 0x67: 0x00b1,
  0x68: 0x2424, 0x69: 0x240b, 0x6a: 0x2518, 0x6b: 0x2510,
  0x6c: 0x250c, 0x6d: 0x2514, 0x6e: 0x253c, 0x6f: 0x23ba,
  0x70: 0x23bb, 0x71: 0x2500, 0x72: 0x23bc, 0x73: 0x23bd,
  0x74: 0x251c, 0x75: 0x2524, 0x76: 0x2534, 0x77: 0x252c,
  0x78: 0x2502, 0x79: 0x2264, 0x7a: 0x2265, 0x7b: 0x03c0,
  0x7c: 0x2260, 0x7d: 0x00a3, 0x7e: 0x00b7,
};

export class Terminal {
  constructor({ rows = 24, cols = 80, scrollback = 1000, pyteCompat = false } = {}) {
    this.screen = new Screen(rows, cols, { scrollback });
    this.pyteCompat = pyteCompat;
    this.onResponse = null;
    this.onTitle = null;
    this.onBell = null;
    this.onHyperlink = null;

    this.parser = new Parser({
      print: (cp) => this._print(cp),
      execute: (b) => this._execute(b),
      escDispatch: (i, f) => this._escDispatch(i, f),
      csiDispatch: (p, i, f) => this._csiDispatch(p, i, f),
      oscDispatch: (s) => this._oscDispatch(s),
      dcsHook: (p, i, f) => this._dcsHook(p, i, f),
      dcsPut: (b) => this._dcsPut(b),
      dcsUnhook: () => this._dcsUnhook(),
    });

    this._dcsKind = null;          // 'sixel' | null
    this._dcsBuf = '';

    this._activeHyperlink = null;  // { id, uri } currently being applied
  }

  // ── Public input ────────────────────────────────────────────────

  write(data) {
    if (typeof data === 'string') this.parser.parseString(data);
    else this.parser.parse(data);
  }

  writeBytes(byteString) {
    // 0..255 chars (each treated as raw byte) — useful for tests.
    this.parser.parseBytes(byteString);
  }

  resize(rows, cols) { this.screen.resize(rows, cols); }
  reset() {
    this.screen.reset();
    this.parser.reset();
    resetPalette();
  }

  toFrame() { return this.screen.toFrame(); }

  // ── Dispatch: print + execute ───────────────────────────────────

  _print(cp) {
    // DEL byte is ignored in ground state per VT spec / pyte behavior.
    if (cp === 0x7f) return;
    // DEC special-graphics translation: '(0' selects line-drawing glyphs.
    // In pyteCompat mode we leave the byte untranslated (so model bytes
    // match pyte's display); otherwise we map to Unicode box-drawing for
    // an honest visual render.
    if (!this.pyteCompat) {
      const cs = this.screen.charsets[this.screen.gl];
      if (cs === '0' && cp >= 0x60 && cp <= 0x7e) {
        cp = DEC_SPECIAL[cp] || cp;
      }
    }
    this.screen.putChar(cp);
  }

  _execute(b) {
    switch (b) {
      case 0x07: if (this.onBell) this.onBell(); return;       // BEL
      case 0x08: this.screen.bs(); return;                      // BS
      case 0x09: this.screen.tab(); return;                     // HT
      case 0x0a:                                                // LF
      case 0x0b:                                                // VT
      case 0x0c: this.screen.lf(); return;                      // FF
      case 0x0d: this.screen.cr(); return;                      // CR
      case 0x0e: this.screen.gl = 1; return;                    // SO (LS1)
      case 0x0f: this.screen.gl = 0; return;                    // SI (LS0)
      case 0x85: this.screen.nel(); return;                     // NEL
      default: return;
    }
  }

  // ── Dispatch: ESC ───────────────────────────────────────────────

  _escDispatch(intermediates, final) {
    const i0 = intermediates[0];

    // No-intermediate ESC sequences
    if (intermediates.length === 0) {
      switch (final) {
        case 0x37: this.screen.saveCursor(); return;        // ESC 7 DECSC
        case 0x38: this.screen.restoreCursor(); return;     // ESC 8 DECRC
        case 0x44: this.screen.ind(); return;               // ESC D IND
        case 0x45: this.screen.nel(); return;               // ESC E NEL
        case 0x48: this.screen.setTabAtCursor(); return;    // ESC H HTS
        case 0x4d: this.screen.ri(); return;                // ESC M RI
        case 0x4e: return;                                  // ESC N SS2 (ignored)
        case 0x4f: return;                                  // ESC O SS3 (ignored)
        case 0x63: this.reset(); return;                    // ESC c RIS
        case 0x3d: this.screen.appKeypad = true; return;    // ESC = DECKPAM
        case 0x3e: this.screen.appKeypad = false; return;   // ESC > DECKPNM
        case 0x6e: this.screen.gl = 2; return;              // ESC n LS2
        case 0x6f: this.screen.gl = 3; return;              // ESC o LS3
        case 0x7c: this.screen.gr = 3; return;              // ESC | LS3R
        case 0x7d: this.screen.gr = 2; return;              // ESC } LS2R
        case 0x7e: this.screen.gr = 1; return;              // ESC ~ LS1R
      }
      return;
    }

    // SCS — Select Character Set: ESC ( B / ESC ) B / ESC * B / ESC + B
    if (i0 === 0x28 || i0 === 0x29 || i0 === 0x2a || i0 === 0x2b) {
      const slot = i0 - 0x28; // 0..3
      const charset = String.fromCharCode(final);
      this.screen.charsets[slot] = charset;
      return;
    }

    // ESC # 8 — DECALN screen alignment test (fills with 'E')
    if (i0 === 0x23 && final === 0x38) {
      const s = this.screen;
      for (let r = 0; r < s.rows; r++)
        for (let c = 0; c < s.cols; c++) {
          const cell = s.lines[r][c];
          cell.ch = 0x45; cell.w = 1;
          cell.fg = DEFAULT_FG_INDEX; cell.bg = DEFAULT_BG_INDEX; cell.flags = 0;
        }
      s.cx = 0; s.cy = 0;
      return;
    }
  }

  // ── Dispatch: CSI ──────────────────────────────────────────────

  _csiDispatch(params, intermediates, final) {
    // Private prefix '?' lives in intermediates per our parser.
    const isPrivate = intermediates.some(b => b === 0x3f);
    const isGt      = intermediates.some(b => b === 0x3e);

    const first = (i, def = 0) => {
      const g = params[i];
      const v = g && g.length > 0 ? g[0] : 0;
      return v === 0 && def !== undefined && (g === undefined || g.length === 0) ? def : v;
    };
    const arg = (i, def) => {
      const g = params[i];
      if (!g || g.length === 0 || g[0] === 0) return def;
      return g[0];
    };
    const argZero = (i, def = 0) => {
      const g = params[i];
      if (!g || g.length === 0) return def;
      return g[0];
    };

    const s = this.screen;

    if (isPrivate) {
      // DEC private mode set/reset (?-prefixed)
      if (final === 0x68) return this._decSet(params, true);   // h
      if (final === 0x6c) return this._decSet(params, false);  // l
    }

    switch (final) {
      case 0x40: s.insertChars(arg(0, 1)); return;                // @ ICH
      case 0x41: s.cursorUp(arg(0, 1)); return;                   // A CUU
      case 0x42: s.cursorDown(arg(0, 1)); return;                 // B CUD
      case 0x43: s.cursorRight(arg(0, 1)); return;                // C CUF
      case 0x44: s.cursorLeft(arg(0, 1)); return;                 // D CUB
      case 0x45: s.cursorDown(arg(0, 1)); s.cx = 0; return;       // E CNL
      case 0x46: s.cursorUp(arg(0, 1)); s.cx = 0; return;         // F CPL
      case 0x47: s.cursorCol(arg(0, 1) - 1); return;              // G CHA
      case 0x48: {                                                  // H CUP
        const r = arg(0, 1) - 1, c = arg(1, 1) - 1;
        s.setCursor(r, c); return;
      }
      case 0x49: s.cht(arg(0, 1)); return;                        // I CHT
      case 0x4a: s.eraseInDisplay(argZero(0, 0)); return;         // J ED
      case 0x4b: s.eraseInLine(argZero(0, 0)); return;            // K EL
      case 0x4c: s.insertLines(arg(0, 1)); return;                // L IL
      case 0x4d: s.deleteLines(arg(0, 1)); return;                // M DL
      case 0x50: s.deleteChars(arg(0, 1)); return;                // P DCH
      case 0x53: s.scrollUp(arg(0, 1)); return;                   // S SU
      case 0x54: s.scrollDown(arg(0, 1)); return;                 // T SD
      case 0x58: s.eraseChars(arg(0, 1)); return;                 // X ECH
      case 0x5a: s.cbt(arg(0, 1)); return;                        // Z CBT
      case 0x60: s.cursorCol(arg(0, 1) - 1); return;              // ` HPA
      case 0x61: s.cursorRight(arg(0, 1)); return;                // a HPR
      case 0x62: {                                                  // b REP
        // Repeat last printable. We don't track last cp; approximate
        // by reading the cell to the left of the cursor.
        const n = arg(0, 1);
        const row = s.lines[s.cy];
        let x = s.cx - 1;
        if (s.wrapPending) x = s.cols - 1;
        if (x < 0) return;
        const cp = row[x].ch || 0x20;
        for (let k = 0; k < n; k++) s.putChar(cp);
        return;
      }
      case 0x63: {                                                  // c DA
        if (isGt) {
          // Secondary DA → xterm patch 95 (XTerm)
          this._respond('\x1b[>0;95;0c');
        } else {
          // Primary DA → VT102 with: 1=132-col, 2=printer, 6=selective erase,
          // 9=natl-replacement, 15=tech-chars, 22=ANSI color, 29=ANSI text.
          this._respond('\x1b[?62;22c');
        }
        return;
      }
      case 0x64: s.cursorRow(arg(0, 1) - 1); return;              // d VPA
      case 0x65: s.cursorDown(arg(0, 1)); return;                 // e VPR
      case 0x66: {                                                  // f HVP
        const r = arg(0, 1) - 1, c = arg(1, 1) - 1;
        s.setCursor(r, c); return;
      }
      case 0x67: {                                                  // g TBC
        s.clearTab(argZero(0, 0)); return;
      }
      case 0x68: return this._smRm(params, true);                  // h SM
      case 0x6c: return this._smRm(params, false);                 // l RM
      case 0x6d: return this._sgr(params);                         // m SGR
      case 0x6e: {                                                  // n DSR
        const code = argZero(0, 0);
        if (code === 5) this._respond('\x1b[0n');
        else if (code === 6) this._respond(`\x1b[${s.cy + 1};${s.cx + 1}R`);
        return;
      }
      case 0x71: {                                                  // q DECSCUSR (with intermediate ' ') or ignored
        if (intermediates.includes(0x20)) {
          this._cursorStyle = argZero(0, 0);
        }
        return;
      }
      case 0x72: {                                                  // r DECSTBM
        // pyte: with no params, reset region AND don't move cursor.
        const g0 = params[0], g1 = params[1];
        const noArgs = (!g0 || g0.length === 0) && (!g1 || g1.length === 0);
        if (noArgs) {
          s.scrollTop = 0; s.scrollBot = s.rows - 1;
          return;
        }
        const top = arg(0, 1) - 1;
        const bot = arg(1, s.rows) - 1;
        if (top < bot && bot < s.rows) {
          s.scrollTop = top; s.scrollBot = bot;
          s.setCursor(0, 0);
        }
        return;
      }
      case 0x73: s.saveCursor(); return;                          // s SCOSC
      case 0x74: return;                                          // t XTWINOPS — ignore
      case 0x75: s.restoreCursor(); return;                       // u SCORC
    }
  }

  // ── DECSET / DECRST (?-prefixed) ────────────────────────────────

  _decSet(params, set) {
    const s = this.screen;
    for (const group of params) {
      const code = group[0] | 0;
      switch (code) {
        case 1:   s.appCursorKeys = set; break;                       // DECCKM
        case 3:   /* DECCOLM — column switch; not implemented */ break;
        case 5:   /* DECSCNM reverse video */ break;
        case 6:                                                       // DECOM
          s.originMode = set;
          // Per VT520 + pyte: DECOM set/reset homes the cursor (which
          // means region-top when origin mode is now ON).
          s.setCursor(0, 0);
          break;
        case 7:   s.autoWrap = set; break;                            // DECAWM
        case 8:   /* DECARM autorepeat */ break;
        case 12:  /* cursor blink */ this._cursorBlink = set; break;
        case 25:  s.cursorVisible = set; break;                       // DECTCEM
        case 45:  s.reverseWrap = set; break;                         // xterm reverse wrap
        case 47: case 1047:
          if (set) s.enterAlt(); else s.leaveAlt(); break;
        case 1048:
          if (set) s.saveCursor(); else s.restoreCursor(); break;
        case 1049:
          if (set) { s.saveCursor(); s.enterAlt(); s.clearScreen(); }
          else     { s.leaveAlt(); s.restoreCursor(); }
          break;
        case 2004: s.bracketedPaste = set; break;
        case 1000: case 1002: case 1003: case 1005: case 1006: case 1015:
          s.mouseMode = set ? code : 0; break;
        default: /* unknown — ignore */ break;
      }
    }
  }

  // ── SM / RM (ANSI, no '?') ──────────────────────────────────────

  _smRm(params, set) {
    for (const group of params) {
      const code = group[0] | 0;
      switch (code) {
        case 2:  /* KAM — keyboard action mode */ break;
        case 4:  this.screen.insertMode = set; break;       // IRM
        case 12: /* SRM — send/receive */ break;
        case 20: /* LNM — line feed/new line */ break;
      }
    }
  }

  // ── SGR ────────────────────────────────────────────────────────

  _sgr(params) {
    const s = this.screen;
    if (params.length === 1 && params[0].length === 0) {
      // CSI m with no params = CSI 0 m (reset)
      s.curFg = DEFAULT_FG_INDEX; s.curBg = DEFAULT_BG_INDEX; s.curFlags = 0;
      return;
    }
    for (let i = 0; i < params.length; i++) {
      const group = params[i];
      const v = group.length > 0 ? group[0] : 0;
      switch (true) {
        case v === 0:
          s.curFg = DEFAULT_FG_INDEX; s.curBg = DEFAULT_BG_INDEX; s.curFlags = 0; break;
        case v === 1:  s.curFlags |= FLAG.BOLD; break;
        case v === 2:  s.curFlags |= FLAG.DIM; break;
        case v === 3:  s.curFlags |= FLAG.ITALIC; break;
        case v === 4:  s.curFlags |= FLAG.UNDERLINE; break;
        case v === 5:  s.curFlags |= FLAG.BLINK; break;
        case v === 6:  s.curFlags |= FLAG.BLINK; break;
        case v === 7:  s.curFlags |= FLAG.REVERSE; break;
        case v === 8:  s.curFlags |= FLAG.INVISIBLE; break;
        case v === 9:  s.curFlags |= FLAG.STRIKE; break;
        case v === 21: s.curFlags &= ~FLAG.BOLD; break; // double underline; treat as bold-off
        case v === 22: s.curFlags &= ~(FLAG.BOLD | FLAG.DIM); break;
        case v === 23: s.curFlags &= ~FLAG.ITALIC; break;
        case v === 24: s.curFlags &= ~FLAG.UNDERLINE; break;
        case v === 25: s.curFlags &= ~FLAG.BLINK; break;
        case v === 27: s.curFlags &= ~FLAG.REVERSE; break;
        case v === 28: s.curFlags &= ~FLAG.INVISIBLE; break;
        case v === 29: s.curFlags &= ~FLAG.STRIKE; break;

        case v >= 30 && v <= 37: s.curFg = paletteIndex(v - 30); break;
        case v === 38: {
          const r = parseSgrColor(params, i);
          if (r && r.value !== null) s.curFg = r.value;
          i += r ? r.advance : 1;
          break;
        }
        case v === 39: s.curFg = DEFAULT_FG_INDEX; break;
        case v >= 40 && v <= 47: s.curBg = paletteIndex(v - 40); break;
        case v === 48: {
          const r = parseSgrColor(params, i);
          if (r && r.value !== null) s.curBg = r.value;
          i += r ? r.advance : 1;
          break;
        }
        case v === 49: s.curBg = DEFAULT_BG_INDEX; break;
        case v >= 90 && v <= 97:  s.curFg = paletteIndex(v - 90 + 8); break;
        case v >= 100 && v <= 107: s.curBg = paletteIndex(v - 100 + 8); break;
      }
    }
  }

  // ── OSC ────────────────────────────────────────────────────────

  _oscDispatch(payload) {
    // OSC is "Ps ; Pt".  Ps is the command number (digits up to first ';').
    const semi = payload.indexOf(';');
    const psStr = semi === -1 ? payload : payload.slice(0, semi);
    const pt    = semi === -1 ? '' : payload.slice(semi + 1);
    const ps    = parseInt(psStr, 10);

    switch (ps) {
      case 0: case 2:
        this.screen.title = pt;
        if (this.onTitle) this.onTitle(pt);
        return;
      case 4: {
        // OSC 4 ; index ; spec  (or pairs)
        const parts = pt.split(';');
        for (let k = 0; k + 1 < parts.length; k += 2) {
          const idx = parseInt(parts[k], 10);
          const hex = parseColorSpec(parts[k + 1]);
          if (!Number.isNaN(idx) && hex) setPaletteEntry(idx, hex);
        }
        return;
      }
      case 8: {
        // OSC 8 ; params ; URI    (empty URI ends the hyperlink)
        const idx = pt.indexOf(';');
        const uri = idx === -1 ? pt : pt.slice(idx + 1);
        this._activeHyperlink = uri ? { uri } : null;
        if (this.onHyperlink) this.onHyperlink(uri || null);
        return;
      }
      case 10: case 11: case 12: {
        // Set/query default fg/bg/cursor — ignored for now.
        return;
      }
      case 52: /* clipboard */ return;
      case 104: resetPalette(); return;
      case 110: case 111: case 112: /* reset fg/bg/cursor color */ return;
      default: return;
    }
  }

  // ── DCS ────────────────────────────────────────────────────────

  _dcsHook(params, intermediates, final) {
    // Sixel: final 'q' (0x71).
    if (final === 0x71) {
      this._dcsKind = 'sixel';
      this._dcsBuf = '';
      return;
    }
    this._dcsKind = null;
  }

  _dcsPut(b) {
    if (this._dcsKind === 'sixel') this._dcsBuf += String.fromCharCode(b);
  }

  _dcsUnhook() {
    if (this._dcsKind === 'sixel' && this.onSixel) this.onSixel(this._dcsBuf);
    this._dcsKind = null;
    this._dcsBuf = '';
  }

  // ── Response helper ────────────────────────────────────────────

  _respond(s) { if (this.onResponse) this.onResponse(s); }
}

// Parse OSC 4 / 10 colour spec.  Supports rgb:RR/GG/BB, rgb:RRRR/GGGG/BBBB
// and #RRGGBB / #RRRRGGGGBBBB.
function parseColorSpec(spec) {
  if (!spec) return null;
  spec = spec.trim();
  if (spec.startsWith('#')) {
    const h = spec.slice(1);
    if (h.length === 6) return h.toLowerCase();
    if (h.length === 12) return (h.slice(0, 2) + h.slice(4, 6) + h.slice(8, 10)).toLowerCase();
  }
  if (spec.toLowerCase().startsWith('rgb:')) {
    const parts = spec.slice(4).split('/');
    if (parts.length === 3) {
      const conv = p => p.length === 2 ? p : p.slice(0, 2);
      return (conv(parts[0]) + conv(parts[1]) + conv(parts[2])).toLowerCase();
    }
  }
  return null;
}
