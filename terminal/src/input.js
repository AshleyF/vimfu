/**
 * Keyboard input → bytes for a VT/xterm host.
 *
 * Public API:
 *   const ki = new KeyInput(term);
 *   element.addEventListener('keydown', e => ki.handle(e));
 *   element.addEventListener('paste',  e => ki.paste(e));
 *
 * The handler returns the byte sequence (string) it would have sent,
 * and (by default) also fires `term.write(...)` if `term.echo` is true
 * or calls `term.onInput(seq)` if defined.  For a live PTY you usually
 * just want `term.onInput = (s) => ws.send(...)`.
 */

function csi(s) { return '\x1b[' + s; }
function ss3(s) { return '\x1bO' + s; }

// Modifier code per xterm: 1 + (shift) + 2*(alt) + 4*(ctrl) + 8*(meta)
function modCode(e) {
  let m = 0;
  if (e.shiftKey) m += 1;
  if (e.altKey)   m += 2;
  if (e.ctrlKey)  m += 4;
  if (e.metaKey)  m += 8;
  return m === 0 ? 0 : m + 1;
}

// Cursor keys: app mode uses SS3, normal mode uses CSI.  With any
// modifier, both modes use CSI 1 ; M letter.
function cursor(letter, app, mods) {
  if (mods) return csi(`1;${mods}${letter}`);
  return app ? ss3(letter) : csi(letter);
}

// Function keys F1..F12.  F1-F4 use SS3 P/Q/R/S in xterm; F5+ use CSI Ps ~.
// With modifiers: CSI 1;m P  for F1..F4, CSI n;m~ for F5+.
function funcKey(n, mods) {
  if (n <= 4) {
    const ltr = ['P', 'Q', 'R', 'S'][n - 1];
    if (mods) return csi(`1;${mods}${ltr}`);
    return ss3(ltr);
  }
  const codes = { 5: 15, 6: 17, 7: 18, 8: 19, 9: 20, 10: 21, 11: 23, 12: 24 };
  const code = codes[n];
  if (mods) return csi(`${code};${mods}~`);
  return csi(`${code}~`);
}

export class KeyInput {
  constructor(term) {
    this.term = term;
    this.echo = false;
  }

  _send(seq) {
    if (!seq) return;
    if (this.echo) this.term.write(seq);
    if (this.term.onInput) this.term.onInput(seq);
  }

  handle(e) {
    const app = this.term.screen.appCursorKeys;
    const mods = modCode(e);

    // Named keys first
    switch (e.key) {
      case 'ArrowUp':    this._send(cursor('A', app, mods)); e.preventDefault(); return;
      case 'ArrowDown':  this._send(cursor('B', app, mods)); e.preventDefault(); return;
      case 'ArrowRight': this._send(cursor('C', app, mods)); e.preventDefault(); return;
      case 'ArrowLeft':  this._send(cursor('D', app, mods)); e.preventDefault(); return;
      case 'Home':       this._send(cursor('H', app, mods)); e.preventDefault(); return;
      case 'End':        this._send(cursor('F', app, mods)); e.preventDefault(); return;
      case 'PageUp':     this._send(mods ? csi(`5;${mods}~`) : csi('5~')); e.preventDefault(); return;
      case 'PageDown':   this._send(mods ? csi(`6;${mods}~`) : csi('6~')); e.preventDefault(); return;
      case 'Insert':     this._send(mods ? csi(`2;${mods}~`) : csi('2~')); e.preventDefault(); return;
      case 'Delete':     this._send(mods ? csi(`3;${mods}~`) : csi('3~')); e.preventDefault(); return;
      case 'Enter':      this._send('\r'); e.preventDefault(); return;
      case 'Backspace':  this._send(e.ctrlKey ? '\x08' : '\x7f'); e.preventDefault(); return;
      case 'Tab':        this._send(e.shiftKey ? csi('Z') : '\t'); e.preventDefault(); return;
      case 'Escape':     this._send('\x1b'); e.preventDefault(); return;
    }

    if (e.key.startsWith('F') && /^F\d+$/.test(e.key)) {
      const n = parseInt(e.key.slice(1), 10);
      if (n >= 1 && n <= 12) {
        this._send(funcKey(n, mods));
        e.preventDefault();
        return;
      }
    }

    // Printable
    if (e.key.length === 1) {
      let out = e.key;
      if (e.ctrlKey && !e.metaKey) {
        // Ctrl-letter → control byte
        const code = e.key.toLowerCase().charCodeAt(0);
        if (code >= 97 && code <= 122)       out = String.fromCharCode(code - 96);
        else if (e.key === ' ' || e.key === '@') out = '\x00';
        else if (e.key === '[')              out = '\x1b';
        else if (e.key === '\\')             out = '\x1c';
        else if (e.key === ']')              out = '\x1d';
        else if (e.key === '^')              out = '\x1e';
        else if (e.key === '_' || e.key === '?') out = '\x1f';
        else out = '';
        if (out) { this._send(out); e.preventDefault(); }
        return;
      }
      if (e.altKey && !e.metaKey) {
        // Alt-prefix: send ESC + char
        this._send('\x1b' + out);
        e.preventDefault();
        return;
      }
      this._send(out);
      e.preventDefault();
      return;
    }
  }

  paste(e) {
    const text = (e.clipboardData || window.clipboardData).getData('text');
    if (!text) return;
    if (this.term.screen.bracketedPaste) {
      this._send('\x1b[200~' + text + '\x1b[201~');
    } else {
      this._send(text);
    }
    e.preventDefault();
  }
}
