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
  }

  /**
   * Attach keyboard listener to a DOM element.
   * @param {HTMLElement} el
   */
  attach(el) {
    el.addEventListener('keydown', this._boundKeyDown);
  }

  /**
   * Detach keyboard listener.
   * @param {HTMLElement} el
   */
  detach(el) {
    el.removeEventListener('keydown', this._boundKeyDown);
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
        (e.ctrlKey && /^[a-z]$/i.test(e.key))
      ) {
        e.preventDefault();
      }
      this.session.feedKey(key);
      this.onUpdate(this.session.renderFrame());
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
