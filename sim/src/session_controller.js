/**
 * VimFu Simulator – Session Controller
 *
 * Like Controller, but routes keyboard events through a SessionManager
 * instead of directly to the engine. This handles the full shell↔vim
 * lifecycle including Ctrl key combos needed by the shell.
 *
 * The existing Controller class is left intact for standalone vim-only
 * usage and tests.
 */

import { SessionManager } from './session.js';

export class SessionController {
  /**
   * @param {SessionManager} session
   * @param {function} [onUpdate] – called after each key with the new Frame
   */
  constructor(session, onUpdate = () => {}) {
    this.session = session;
    this.onUpdate = onUpdate;
    this._boundKeyDown = this._onKeyDown.bind(this);
    this._boundPaste = this._onPaste.bind(this);
    this._boundFocus = this._onFocus.bind(this);
  }

  /**
   * Attach keyboard listener to a DOM element.
   * @param {HTMLElement} el
   */
  attach(el) {
    el.addEventListener('keydown', this._boundKeyDown);
    el.addEventListener('paste', this._boundPaste);
    el.addEventListener('focus', this._boundFocus);
  }

  /**
   * Detach keyboard listener.
   * @param {HTMLElement} el
   */
  detach(el) {
    el.removeEventListener('keydown', this._boundKeyDown);
    el.removeEventListener('paste', this._boundPaste);
    el.removeEventListener('focus', this._boundFocus);
  }

  /**
   * Programmatic key input.
   * @param {string} key
   */
  handleKey(key) {
    this.session.feedKey(key);
    this.onUpdate(this.session.renderFrame());
  }

  /**
   * Feed a sequence of keys.
   * @param {string} keys
   */
  feedKeys(keys) {
    for (const ch of keys) {
      let key = ch;
      if (ch === '\x1b') key = 'Escape';
      else if (ch === '\r' || ch === '\n') key = 'Enter';
      else if (ch === '\x08' || ch === '\x7f') key = 'Backspace';
      this.session.feedKey(key);
    }
    this.onUpdate(this.session.renderFrame());
  }

  // ── Private ──

  /**
   * Get the active VimEngine (if we're in vim mode).
   * @private
   * @returns {import('./engine.js').VimEngine|null}
   */
  _getEngine() {
    return this.session.mode === 'vim' ? this.session.engine : null;
  }

  /**
   * Wire up the clipboard-write callback on the engine so that
   * writing to "+ or "* pushes text to the system clipboard.
   * Called every time a new engine appears (i.e. when vim launches).
   * @private
   */
  _wireClipboard(engine) {
    if (!engine || engine._clipboardWired) return;
    engine._onClipboardWrite = (text) => {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).catch(() => {});
      }
    };
    engine._clipboardWired = true;
  }

  /**
   * Pre-read the system clipboard into the engine's + register
   * so it's ready for synchronous paste.
   * @private
   */
  _preReadClipboard() {
    const engine = this._getEngine();
    if (!engine) return;
    if (navigator.clipboard && navigator.clipboard.readText) {
      navigator.clipboard.readText().then((text) => {
        if (text != null) engine.setClipboardText(text);
      }).catch(() => {});
    }
  }

  /** @private */
  _onKeyDown(e) {
    const key = this._translateKey(e);
    if (key) {
      // Prevent browser defaults
      const dominated = [
        'Escape', 'Backspace', 'Enter', 'Tab',
        'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight',
      ];
      if (
        dominated.includes(e.key) ||
        (e.key.length === 1 && !e.altKey && !e.metaKey) ||
        (e.ctrlKey && /^[a-z]$/i.test(e.key)) ||
        ((e.altKey || e.metaKey) && !e.ctrlKey && e.key.length === 1)
      ) {
        e.preventDefault();
      }

      // Wire clipboard on engine if not yet done
      const engine = this._getEngine();
      if (engine) this._wireClipboard(engine);

      this.session.feedKey(key);

      // After setting the + or * register, pre-read the system clipboard
      // so the data is available when the next key (p, P, etc.) arrives.
      if (engine) {
        const pendReg = engine._pendingRegKey;
        if (pendReg === '+' || pendReg === '*') {
          this._preReadClipboard();
        }
      }

      this.onUpdate(this.session.renderFrame());
    }
  }

  /**
   * Handle paste events: update the + register with pasted text.
   * @private
   */
  _onPaste(e) {
    const text = (e.clipboardData || window.clipboardData)?.getData('text');
    if (text) {
      const engine = this._getEngine();
      if (engine) engine.setClipboardText(text);
    }
  }

  /**
   * On focus, wire clipboard callbacks but don't eagerly read —
   * that triggers a paste-permission prompt on mobile.
   * @private
   */
  _onFocus() {
    const engine = this._getEngine();
    if (engine) {
      this._wireClipboard(engine);
    }
  }

  /**
   * Map a DOM KeyboardEvent to a key name that both the shell and
   * engine understand.
   * @private
   */
  _translateKey(e) {
    // Ignore modifier-only presses
    if (['Shift', 'Control', 'Alt', 'Meta'].includes(e.key)) return null;

    // Ctrl combos — needed by both shell (Ctrl-C/L/A/E/U/K/W)
    // and engine (Ctrl-R/D/U/F/B/G)
    if (e.ctrlKey && !e.altKey && !e.metaKey && /^[a-z]$/i.test(e.key)) {
      return 'Ctrl-' + e.key.toUpperCase();
    }

    // Ctrl + arrow keys (for tmux resize)
    if (e.ctrlKey && !e.altKey && !e.metaKey && e.key.startsWith('Arrow')) {
      const dir = e.key.slice(5); // 'ArrowLeft' → 'Left'
      return 'Ctrl-' + dir;
    }

    // Alt/Meta combos (for completeness / mappability)
    if ((e.altKey || e.metaKey) && !e.ctrlKey && e.key.length === 1) {
      return 'Meta-' + e.key;
    }

    // Special keys
    const specials = {
      'Escape': 'Escape',
      'Enter': 'Enter',
      'Backspace': 'Backspace',
      'ArrowUp': 'ArrowUp',
      'ArrowDown': 'ArrowDown',
      'ArrowLeft': 'ArrowLeft',
      'ArrowRight': 'ArrowRight',
      'Tab': 'Tab',
    };
    if (specials[e.key]) return specials[e.key];

    // Regular printable character (respect Shift via e.key)
    if (e.key.length === 1 && !e.ctrlKey && !e.altKey && !e.metaKey) {
      return e.key;
    }

    return null;
  }
}
