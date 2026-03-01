/**
 * VimFu Simulator – Controller
 *
 * Translates DOM KeyboardEvents into engine key names and feeds them
 * to the VimEngine. This is the only module that touches the DOM for
 * input handling.
 *
 * Works both in-browser (attaching to a DOM element) and headlessly
 * (call `handleKey(key)` directly from tests).
 */

import { VimEngine } from './engine.js';
import { Screen } from './screen.js';

export class Controller {
  /**
   * @param {VimEngine} engine
   * @param {Screen}    screen
   * @param {function}  onUpdate – called after each key with the new Frame
   */
  constructor(engine, screen, onUpdate = () => {}) {
    this.engine = engine;
    this.screen = screen;
    this.onUpdate = onUpdate;
    this._boundKeyDown = this._onKeyDown.bind(this);
    this._boundPaste = this._onPaste.bind(this);
    this._boundFocus = this._onFocus.bind(this);

    // Wire up clipboard write: when engine writes to "+ or "* register,
    // push the text to the system clipboard.
    this.engine._onClipboardWrite = (text) => {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).catch(() => {});
      }
    };
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
   * Programmatic key input (for tests or scripting).
   * @param {string} key
   */
  handleKey(key) {
    this.engine.feedKey(key);
    this.onUpdate(this.screen.render(this.engine));
  }

  /**
   * Feed a sequence of keys, like "iHello\x1b" where \x1b = Escape.
   * @param {string} keys – plain characters; use \x1b for Escape, \r for Enter
   */
  feedKeys(keys) {
    for (const ch of keys) {
      let key = ch;
      if (ch === '\x1b') key = 'Escape';
      else if (ch === '\r' || ch === '\n') key = 'Enter';
      else if (ch === '\x08' || ch === '\x7f') key = 'Backspace';
      this.engine.feedKey(key);
    }
    this.onUpdate(this.screen.render(this.engine));
  }

  // ── Private ──

  /** @private */
  _onKeyDown(e) {
    // Prevent browser defaults for keys we handle
    const dominated = [
      'Escape', 'Backspace', 'Enter', 'Tab',
      'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight',
    ];
    const key = this._translateKey(e);
    if (key) {
      if (dominated.includes(e.key) || (e.key.length === 1 && !e.ctrlKey && !e.altKey && !e.metaKey)) {
        e.preventDefault();
      }
      this.engine.feedKey(key);

      // After setting the + or * register, pre-read the system clipboard
      // so the data is available when the next key (p, P, etc.) arrives.
      const pendReg = this.engine._pendingRegKey;
      if ((pendReg === '+' || pendReg === '*') && navigator.clipboard && navigator.clipboard.readText) {
        navigator.clipboard.readText().then((text) => {
          this.engine.setClipboardText(text);
        }).catch(() => {});
      }

      this.onUpdate(this.screen.render(this.engine));
    }
  }

  /**
   * Handle paste events: update the + register with pasted text.
   * This catches browser Ctrl+V / Cmd+V paste events.
   * @private
   */
  _onPaste(e) {
    const text = (e.clipboardData || window.clipboardData)?.getData('text');
    if (text) {
      this.engine.setClipboardText(text);
    }
  }

  /**
   * On focus, nothing to do — clipboard is read lazily when the
   * user actually selects the + register (avoids mobile paste prompt).
   * @private
   */
  _onFocus() {
    // no-op: clipboard read moved to _onKeyDown when "+/"* is pending
  }

  /**
   * Map a DOM KeyboardEvent to the engine's key name.
   * @private
   */
  _translateKey(e) {
    // Ignore modifier-only presses
    if (['Shift', 'Control', 'Alt', 'Meta'].includes(e.key)) return null;

    // Special keys
    const specials = {
      'Escape': 'Escape',
      'Enter': 'Enter',
      'Backspace': 'Backspace',
      'ArrowUp': 'ArrowUp',
      'ArrowDown': 'ArrowDown',
      'ArrowLeft': 'ArrowLeft',
      'ArrowRight': 'ArrowRight',
    };
    if (specials[e.key]) return specials[e.key];

    // Ctrl combos
    if (e.ctrlKey && !e.altKey && !e.metaKey && /^[a-z]$/i.test(e.key)) {
      return 'Ctrl-' + e.key.toUpperCase();
    }

    // Alt/Meta combos (for completeness / mappability)
    if ((e.altKey || e.metaKey) && !e.ctrlKey && e.key.length === 1) {
      return 'Meta-' + e.key;
    }

    // Regular printable character (respect Shift via e.key)
    if (e.key.length === 1 && !e.ctrlKey && !e.altKey && !e.metaKey) {
      return e.key;
    }

    return null;
  }
}
