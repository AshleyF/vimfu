/**
 * VT Parser — Paul Williams' DEC ANSI state machine.
 *
 * Reference: https://vt100.net/emu/dec_ansi_parser
 *
 * The parser walks an FSM over bytes and emits callbacks:
 *
 *   handlers.print(codepoint)
 *   handlers.execute(byte)              ← C0 control: BEL, BS, HT, LF, VT, FF, CR, SO, SI
 *   handlers.escDispatch(intermediates, final)
 *   handlers.csiDispatch(params, intermediates, final)
 *   handlers.oscDispatch(stringPayload) ← already decoded UTF-8 string
 *   handlers.dcsHook(params, intermediates, final)
 *   handlers.dcsPut(byte)
 *   handlers.dcsUnhook()
 *
 * `params` is an array of arrays of ints (subparameters are split on ':').
 * Empty params become [], a `0` default is left to the dispatcher.
 *
 * The parser owns no terminal state.  It only consumes bytes and emits
 * structured events.  Pass UTF-8 bytes via `parse(uint8array)` or a string
 * via `parseString(str)`.
 */

const MAX_PARAM = 16383;          // xterm cap
const MAX_PARAMS = 32;
const MAX_INTERMEDIATES = 2;
const MAX_OSC_LEN = 1 << 20;      // 1 MiB; enough for big OSC 8 + base64 OSC 52

const State = Object.freeze({
  GROUND: 0,
  ESCAPE: 1,
  ESCAPE_INTERMEDIATE: 2,
  CSI_ENTRY: 3,
  CSI_PARAM: 4,
  CSI_INTERMEDIATE: 5,
  CSI_IGNORE: 6,
  DCS_ENTRY: 7,
  DCS_PARAM: 8,
  DCS_INTERMEDIATE: 9,
  DCS_PASSTHROUGH: 10,
  DCS_IGNORE: 11,
  OSC_STRING: 12,
  SOS_PM_APC_STRING: 13,
  UTF8: 14,                       // not in Williams' diagram; we layer on top
});

export class Parser {
  constructor(handlers = {}) {
    this.handlers = handlers;
    this.reset();
  }

  reset() {
    this.state = State.GROUND;
    this._paramsBuf = '';
    this._params = [[]];          // params[paramIdx][subIdx]
    this._intermediates = [];
    this._oscBuf = '';
    this._dcsFinal = 0;
    this._dcsHooked = false;
    // UTF-8 multi-byte assembly
    this._utf8Need = 0;
    this._utf8Acc = 0;
    this._utf8Min = 0;
  }

  // ── Public entry points ──────────────────────────────────────────

  /** Feed a byte string (one byte per char, 0..255). */
  parseBytes(str) {
    for (let i = 0; i < str.length; i++) {
      this._feedByte(str.charCodeAt(i) & 0xff);
    }
  }

  /** Feed a JS string (will be UTF-8 encoded then parsed). */
  parseString(str) {
    const enc = new TextEncoder();
    this.parse(enc.encode(str));
  }

  /** Feed a Uint8Array. */
  parse(bytes) {
    for (let i = 0; i < bytes.length; i++) {
      this._feedByte(bytes[i]);
    }
  }

  // ── Core dispatch ────────────────────────────────────────────────

  _feedByte(b) {
    // UTF-8 continuation has highest priority — only meaningful in ground.
    if (this._utf8Need > 0 && this.state === State.GROUND) {
      if ((b & 0xc0) === 0x80) {
        this._utf8Acc = (this._utf8Acc << 6) | (b & 0x3f);
        this._utf8Need--;
        if (this._utf8Need === 0) {
          const cp = this._utf8Acc;
          if (cp >= this._utf8Min && !(cp >= 0xd800 && cp <= 0xdfff)) {
            this._print(cp);
          } else {
            this._print(0xfffd);
          }
          this._utf8Acc = 0;
        }
        return;
      } else {
        // Abandon: invalid continuation. Emit replacement, fall through.
        this._print(0xfffd);
        this._utf8Need = 0;
      }
    }

    // Anywhere transitions (highest priority after UTF-8 continuation)
    if (b === 0x18 || b === 0x1a) {       // CAN / SUB
      this._execute(b);
      this._enter(State.GROUND);
      return;
    }
    if (b === 0x1b) {                     // ESC
      // Inside a string-terminated state, ESC starts the ST sequence.
      // We finalise the current string body and then handle ESC normally;
      // a following '\\' will dispatch ST (it'll arrive in ESCAPE state
      // and that state's 0x5c handler transitions to GROUND).
      if (this.state === State.OSC_STRING) this._oscEnd();
      else if (this.state === State.DCS_PASSTHROUGH) this._dcsEnd();
      this._clear();
      this._enter(State.ESCAPE);
      return;
    }

    // 8-bit C1 control byte handling.  Only honor these when we're in
    // GROUND — inside OSC / DCS / SOS-PM-APC strings, bytes 0x80..0x9f
    // are legitimate UTF-8 continuation bytes and must pass through
    // unmolested.  (xterm and foot make the same exception.)
    if (this.state === State.GROUND) {
      if (b === 0x9b) { this._clear(); this._enter(State.CSI_ENTRY); return; }
      if (b === 0x9d) { this._clear(); this._oscBuf = ''; this._enter(State.OSC_STRING); return; }
      if (b === 0x90) { this._clear(); this._enter(State.DCS_ENTRY); return; }
      if (b === 0x98 || b === 0x9e || b === 0x9f) {
        this._enter(State.SOS_PM_APC_STRING); return;
      }
      if (b === 0x9c) {
        this._enter(State.GROUND);
        return;
      }
    } else if (b === 0x9c) {
      // C1 ST inside a string state — terminate.
      if (this.state === State.OSC_STRING) this._oscEnd();
      else if (this.state === State.DCS_PASSTHROUGH) this._dcsEnd();
      this._enter(State.GROUND);
      return;
    }

    switch (this.state) {
      case State.GROUND:           return this._ground(b);
      case State.ESCAPE:           return this._escape(b);
      case State.ESCAPE_INTERMEDIATE: return this._escapeIntermediate(b);
      case State.CSI_ENTRY:        return this._csiEntry(b);
      case State.CSI_PARAM:        return this._csiParam(b);
      case State.CSI_INTERMEDIATE: return this._csiIntermediate(b);
      case State.CSI_IGNORE:       return this._csiIgnore(b);
      case State.DCS_ENTRY:        return this._dcsEntry(b);
      case State.DCS_PARAM:        return this._dcsParam(b);
      case State.DCS_INTERMEDIATE: return this._dcsIntermediate(b);
      case State.DCS_PASSTHROUGH:  return this._dcsPassthrough(b);
      case State.DCS_IGNORE:       return; // swallow
      case State.OSC_STRING:       return this._oscString(b);
      case State.SOS_PM_APC_STRING: return; // swallow until ST
    }
  }

  _enter(state) { this.state = state; }

  _clear() {
    this._paramsBuf = '';
    this._params = [[]];
    this._intermediates = [];
  }

  // ── Print / execute ──────────────────────────────────────────────

  _print(cp) { this.handlers.print && this.handlers.print(cp); }
  _execute(b) { this.handlers.execute && this.handlers.execute(b); }

  _ground(b) {
    if (b <= 0x17 || b === 0x19 || (b >= 0x1c && b <= 0x1f)) {
      this._execute(b);
      return;
    }
    if (b <= 0x7f) {
      this._print(b);
      return;
    }
    // UTF-8 lead byte
    if ((b & 0xe0) === 0xc0)      { this._utf8Need = 1; this._utf8Acc = b & 0x1f; this._utf8Min = 0x80; }
    else if ((b & 0xf0) === 0xe0) { this._utf8Need = 2; this._utf8Acc = b & 0x0f; this._utf8Min = 0x800; }
    else if ((b & 0xf8) === 0xf0) { this._utf8Need = 3; this._utf8Acc = b & 0x07; this._utf8Min = 0x10000; }
    else                          { this._print(0xfffd); }
  }

  // ── ESC ──────────────────────────────────────────────────────────

  _escape(b) {
    if (b <= 0x17 || b === 0x19 || (b >= 0x1c && b <= 0x1f)) { this._execute(b); return; }
    if (b === 0x7f) return;
    if (b >= 0x20 && b <= 0x2f) {
      if (this._intermediates.length < MAX_INTERMEDIATES) this._intermediates.push(b);
      this._enter(State.ESCAPE_INTERMEDIATE);
      return;
    }
    if (b === 0x5b) { this._enter(State.CSI_ENTRY); return; }                 // '['
    if (b === 0x5d) { this._oscBuf = ''; this._enter(State.OSC_STRING); return; } // ']'
    if (b === 0x50) { this._enter(State.DCS_ENTRY); return; }                 // 'P'
    if (b === 0x58 || b === 0x5e || b === 0x5f) {                              // X ^ _
      this._enter(State.SOS_PM_APC_STRING); return;
    }
    if (b === 0x5c) { this._enter(State.GROUND); return; }                     // ST
    if (b >= 0x30 && b <= 0x7e) {
      this._escDispatch(b);
      this._enter(State.GROUND);
      return;
    }
  }

  _escapeIntermediate(b) {
    if (b <= 0x17 || b === 0x19 || (b >= 0x1c && b <= 0x1f)) { this._execute(b); return; }
    if (b >= 0x20 && b <= 0x2f) {
      if (this._intermediates.length < MAX_INTERMEDIATES) this._intermediates.push(b);
      return;
    }
    if (b === 0x7f) return;
    if (b >= 0x30 && b <= 0x7e) {
      this._escDispatch(b);
      this._enter(State.GROUND);
      return;
    }
  }

  _escDispatch(final) {
    if (this.handlers.escDispatch) {
      this.handlers.escDispatch(this._intermediates.slice(), final);
    }
  }

  // ── CSI ──────────────────────────────────────────────────────────

  _csiEntry(b) {
    if (b <= 0x17 || b === 0x19 || (b >= 0x1c && b <= 0x1f)) { this._execute(b); return; }
    if (b === 0x7f) return;
    if (b >= 0x30 && b <= 0x39) { this._paramBegin(b); this._enter(State.CSI_PARAM); return; }
    if (b === 0x3b || b === 0x3a) { this._paramBegin(b); this._enter(State.CSI_PARAM); return; }
    if (b >= 0x3c && b <= 0x3f) {
      // Private-use marker (<=>?). Stash in intermediates so dispatcher sees it.
      if (this._intermediates.length < MAX_INTERMEDIATES) this._intermediates.push(b);
      this._enter(State.CSI_PARAM);
      return;
    }
    if (b >= 0x20 && b <= 0x2f) {
      if (this._intermediates.length < MAX_INTERMEDIATES) this._intermediates.push(b);
      this._enter(State.CSI_INTERMEDIATE);
      return;
    }
    if (b >= 0x40 && b <= 0x7e) {
      this._csiDispatch(b);
      this._enter(State.GROUND);
      return;
    }
  }

  _csiParam(b) {
    if (b <= 0x17 || b === 0x19 || (b >= 0x1c && b <= 0x1f)) { this._execute(b); return; }
    if (b === 0x7f) return;
    if (b >= 0x30 && b <= 0x39) { this._paramDigit(b); return; }
    if (b === 0x3b) { this._paramNext(); return; }
    if (b === 0x3a) { this._paramSubNext(); return; }
    if (b >= 0x3c && b <= 0x3f) { this._enter(State.CSI_IGNORE); return; }
    if (b >= 0x20 && b <= 0x2f) {
      if (this._intermediates.length < MAX_INTERMEDIATES) this._intermediates.push(b);
      this._enter(State.CSI_INTERMEDIATE);
      return;
    }
    if (b >= 0x40 && b <= 0x7e) {
      this._csiDispatch(b);
      this._enter(State.GROUND);
      return;
    }
  }

  _csiIntermediate(b) {
    if (b <= 0x17 || b === 0x19 || (b >= 0x1c && b <= 0x1f)) { this._execute(b); return; }
    if (b === 0x7f) return;
    if (b >= 0x20 && b <= 0x2f) {
      if (this._intermediates.length < MAX_INTERMEDIATES) this._intermediates.push(b);
      return;
    }
    if (b >= 0x30 && b <= 0x3f) { this._enter(State.CSI_IGNORE); return; }
    if (b >= 0x40 && b <= 0x7e) {
      this._csiDispatch(b);
      this._enter(State.GROUND);
      return;
    }
  }

  _csiIgnore(b) {
    if (b <= 0x17 || b === 0x19 || (b >= 0x1c && b <= 0x1f)) { this._execute(b); return; }
    if (b >= 0x40 && b <= 0x7e) { this._enter(State.GROUND); return; }
  }

  _paramBegin(b) {
    this._paramsBuf = '';
    this._params = [[]];
    if (b === 0x3b) { this._paramNext(); return; }
    if (b === 0x3a) { this._paramSubNext(); return; }
    this._paramDigit(b);
  }

  _paramDigit(b) {
    this._paramsBuf += String.fromCharCode(b);
  }

  _flushParam() {
    const last = this._params[this._params.length - 1];
    if (this._paramsBuf.length > 0) {
      let v = parseInt(this._paramsBuf, 10);
      if (!Number.isFinite(v)) v = 0;
      if (v > MAX_PARAM) v = MAX_PARAM;
      last.push(v);
    } else if (last.length > 0) {
      // Empty SUB-param between two ':' or before final → defaults to 0
      // (per ISO 8613-6).  Empty PARAM (whole group never had a digit)
      // stays as an empty array.
      last.push(0);
    }
    this._paramsBuf = '';
  }

  _paramNext() {
    this._flushParam();
    if (this._params.length < MAX_PARAMS) this._params.push([]);
  }

  _paramSubNext() {
    this._flushParam();
    // continue accumulating into the current paramIdx (subparam separator ':')
  }

  _csiDispatch(final) {
    this._flushParam();
    if (this.handlers.csiDispatch) {
      this.handlers.csiDispatch(this._params, this._intermediates.slice(), final);
    }
  }

  // ── OSC ──────────────────────────────────────────────────────────

  _oscString(b) {
    if (b === 0x07) { this._oscEnd(); this._enter(State.GROUND); return; } // BEL
    if (b === 0x1b) {
      // Will arrive via Anywhere → ESCAPE. Anywhere already handled, so this is
      // only reached if we're still in OSC_STRING and the byte is in the
      // 0x00..0x06, 0x08..0x17, 0x19, 0x1c..0x1f range.  ESC handled above.
      // Actually 0x1b is handled by Anywhere — but for safety:
      this._oscEnd();
      this._clear();
      this._enter(State.ESCAPE);
      return;
    }
    if (b < 0x20 && b !== 0x09) {
      // C0 (except TAB) terminates string in xterm — drop and stay; some
      // implementations require ST. We just ignore the byte.
      return;
    }
    if (this._oscBuf.length < MAX_OSC_LEN) {
      this._oscBuf += String.fromCharCode(b);
    }
  }

  _oscEnd() {
    if (this.handlers.oscDispatch) {
      // OSC payload may be UTF-8 if any bytes are >0x7f. Decode it.
      let s = this._oscBuf;
      if (/[\u0080-\u00ff]/.test(s)) {
        // Re-interpret as bytes → UTF-8
        const bytes = new Uint8Array(s.length);
        for (let i = 0; i < s.length; i++) bytes[i] = s.charCodeAt(i) & 0xff;
        s = new TextDecoder('utf-8', { fatal: false }).decode(bytes);
      }
      this.handlers.oscDispatch(s);
    }
    this._oscBuf = '';
  }

  // ── DCS ──────────────────────────────────────────────────────────

  _dcsEntry(b) {
    if (b <= 0x17 || b === 0x19 || (b >= 0x1c && b <= 0x1f)) return;
    if (b === 0x7f) return;
    if (b >= 0x30 && b <= 0x39) { this._paramBegin(b); this._enter(State.DCS_PARAM); return; }
    if (b === 0x3b || b === 0x3a) { this._paramBegin(b); this._enter(State.DCS_PARAM); return; }
    if (b >= 0x3c && b <= 0x3f) {
      if (this._intermediates.length < MAX_INTERMEDIATES) this._intermediates.push(b);
      this._enter(State.DCS_PARAM);
      return;
    }
    if (b >= 0x20 && b <= 0x2f) {
      if (this._intermediates.length < MAX_INTERMEDIATES) this._intermediates.push(b);
      this._enter(State.DCS_INTERMEDIATE);
      return;
    }
    if (b >= 0x40 && b <= 0x7e) { this._dcsHookStart(b); return; }
  }

  _dcsParam(b) {
    if (b <= 0x17 || b === 0x19 || (b >= 0x1c && b <= 0x1f)) return;
    if (b === 0x7f) return;
    if (b >= 0x30 && b <= 0x39) { this._paramDigit(b); return; }
    if (b === 0x3b) { this._paramNext(); return; }
    if (b === 0x3a) { this._paramSubNext(); return; }
    if (b >= 0x3c && b <= 0x3f) { this._enter(State.DCS_IGNORE); return; }
    if (b >= 0x20 && b <= 0x2f) {
      if (this._intermediates.length < MAX_INTERMEDIATES) this._intermediates.push(b);
      this._enter(State.DCS_INTERMEDIATE);
      return;
    }
    if (b >= 0x40 && b <= 0x7e) { this._dcsHookStart(b); return; }
  }

  _dcsIntermediate(b) {
    if (b <= 0x17 || b === 0x19 || (b >= 0x1c && b <= 0x1f)) return;
    if (b === 0x7f) return;
    if (b >= 0x20 && b <= 0x2f) {
      if (this._intermediates.length < MAX_INTERMEDIATES) this._intermediates.push(b);
      return;
    }
    if (b >= 0x30 && b <= 0x3f) { this._enter(State.DCS_IGNORE); return; }
    if (b >= 0x40 && b <= 0x7e) { this._dcsHookStart(b); return; }
  }

  _dcsHookStart(final) {
    this._flushParam();
    this._dcsFinal = final;
    this._dcsHooked = true;
    if (this.handlers.dcsHook) {
      this.handlers.dcsHook(this._params, this._intermediates.slice(), final);
    }
    this._enter(State.DCS_PASSTHROUGH);
  }

  _dcsPassthrough(b) {
    // Any C0 except ESC is passed through; ESC handled by Anywhere.
    if (b === 0x7f) return;
    if (this.handlers.dcsPut) this.handlers.dcsPut(b);
  }

  _dcsEnd() {
    if (this._dcsHooked) {
      this._dcsHooked = false;
      if (this.handlers.dcsUnhook) this.handlers.dcsUnhook();
    }
  }
}

Parser.State = State;
