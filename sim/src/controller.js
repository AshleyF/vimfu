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
      this.onUpdate(this.screen.render(this.engine));
    }
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

    // Regular printable character (respect Shift via e.key)
    if (e.key.length === 1 && !e.ctrlKey && !e.altKey && !e.metaKey) {
      return e.key;
    }

    return null;
  }
}
