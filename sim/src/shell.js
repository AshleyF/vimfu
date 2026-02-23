/**
 * VimFu Simulator – Shell Simulator
 *
 * A minimal ZSH/Bash-like shell that renders to the same Screen format
 * as the Vim engine. Supports a small set of built-in commands and
 * integrates with VirtualFS for file operations.
 *
 * The shell is intentionally minimal — it exists to provide context
 * for Vim demos (quitting Vim returns to the shell, typing `vim file`
 * launches the Vim engine, etc.).
 *
 * Supported commands:
 *   vim [file]     – launch vim (signals to SessionManager)
 *   vi/nvim        – aliases for vim
 *   ls             – list files
 *   cat <file>     – print file contents
 *   rm <file>      – remove a file
 *   touch <file>   – create empty file
 *   echo <text>    – print text (supports > redirect)
 *   sort <file>    – sort lines of a file (or stdin-like piped input)
 *   clear          – clear screen
 *   help           – show available commands
 */

export class ShellSim {
  /**
   * @param {object} opts
   * @param {import('./vfs.js').VirtualFS} opts.fs – virtual filesystem
   * @param {number} [opts.rows=20] – total screen rows
   * @param {number} [opts.cols=40] – screen width
   * @param {string} [opts.cwd='~/vimfu'] – display working directory
   * @param {string} [opts.user='user'] – display username
   * @param {string} [opts.hostname='vimfu'] – display hostname
   * @param {function} [opts.onLaunchVim] – callback(filename|null) when vim is invoked
   * @param {function} [opts.onLaunchTmux] – callback(args[]) when tmux is invoked
   */
  constructor({ fs, rows = 20, cols = 40, cwd = '~/vimfu', dirname = 'vimfu', user = 'user', hostname = 'vimfu', onLaunchVim = null, onLaunchTmux = null } = {}) {
    this.fs = fs;
    this.rows = rows;
    this.cols = cols;
    this.cwd = cwd;
    this.dirname = dirname;
    this.user = user;
    this.hostname = hostname;
    this.onLaunchVim = onLaunchVim;
    this.onLaunchTmux = onLaunchTmux;

    // Flag: set to true when running inside a tmux pane
    this._insideTmux = false;

    this._textRows = rows - 1; // last row is input line (no status bar in shell)

    // Screen output buffer — array of strings (scrollback)
    this._outputLines = [];

    // Current input line
    this._inputLine = '';
    this._cursorPos = 0; // position within _inputLine

    // Command history
    this._history = [];
    this._historyIdx = -1; // -1 means not browsing history
    this._savedInput = ''; // saved current input when browsing history

    // Scroll state
    this.scrollTop = 0;

    // Vi-mode line editing (set -o vi)
    this._viMode = false;    // true when vi-mode is active
    this._viNormal = false;  // true = normal mode, false = insert mode
    this._viOperator = '';   // pending operator: 'd', 'c', 'y'
    this._viPendingChar = ''; // pending char-consumer: 'r', 'f', 'F', 't', 'T'
    this._viYank = '';       // yank buffer for d/c/x/y
    this._viLastF = null;    // last f/F/t/T target: { ch, forward, till }
    this._viCount = '';      // numeric count accumulator (string of digits)
    this._viUndoStack = [];  // undo stack: array of { line, cursorPos }
    this._viLastChange = null; // dot-repeat: { keys: [...], count } — last change
    this._viRecording = [];  // keys being recorded for current change
    this._viInChange = false; // true while a change is in progress
    this._viReplaceMode = false; // R replace (overtype) mode
    this._viReplaceStart = 0;    // cursor position where R was pressed
    this._viReplaceOriginal = ''; // original text for Backspace in replace mode
    this._viSearchMode = '';     // '' | '/' | '?' — history search input
    this._viSearchBuffer = '';   // partial search pattern being typed
    this._viSearchPattern = '';  // last committed search pattern
    this._viSearchDir = 1;       // 1 = forward (/) , -1 = backward (?)

    // Status
    this._exited = false;
  }

  // ── Public API ──

  /**
   * Get the shell prompt string (zsh oh-my-zsh robbyrussell theme).
   * Format: ➜  dirname
   * Arrow (➜ + 2 spaces) = 3 chars, dirname varies, then 1 trailing space.
   * @returns {string}
   */
  get prompt() {
    return `\u279c  ${this.dirname} `;
  }

  /**
   * Length of the arrow portion of the prompt (➜ + 2 spaces).
   * Used for color runs in renderFrame.
   */
  get _promptArrowLen() {
    return 3; // ➜ (1 char) + 2 spaces
  }

  /**
   * Length of the dirname portion of the prompt.
   */
  get _promptDirLen() {
    return this.dirname.length;
  }

  /**
   * Feed a single key to the shell.
   * @param {string} key – key name (same format as VimEngine)
   */
  feedKey(key) {
    if (this._exited) return;
    // Ctrl-[ is the terminal equivalent of Escape
    if (key === 'Ctrl-[') key = 'Escape';

    // ── Vi history search mode (/ or ? prompt) ──
    if (this._viSearchMode) {
      if (key === 'Enter') {
        // Commit the search
        if (this._viSearchBuffer) {
          this._viSearchPattern = this._viSearchBuffer;
          this._viSearchDir = this._viSearchMode === '/' ? -1 : 1; // / searches backward, ? searches forward in history
        }
        this._viSearchMode = '';
        this._viSearchBuffer = '';
        // Perform the search
        if (this._viSearchPattern) {
          this._viHistorySearch(this._viSearchPattern, -1);
        }
        return;
      }
      if (key === 'Escape') {
        this._viSearchMode = '';
        this._viSearchBuffer = '';
        return;
      }
      if (key === 'Backspace') {
        if (this._viSearchBuffer.length > 0) {
          this._viSearchBuffer = this._viSearchBuffer.slice(0, -1);
        } else {
          this._viSearchMode = '';
        }
        return;
      }
      if (key.length === 1) {
        this._viSearchBuffer += key;
        return;
      }
      return;
    }

    // Enter always executes, regardless of vi-mode state
    if (key === 'Enter') {
      this._viNormal = false;
      this._viReplaceMode = false;
      this._viOperator = '';
      this._viCount = '';
      this._viEndChange();
      this._execute();
      return;
    }

    // Vi-mode: dispatch to normal mode handler
    if (this._viMode && this._viNormal) {
      this._feedKeyViNormal(key);
      return;
    }

    // Vi replace mode (R): overtype characters
    if (this._viMode && this._viReplaceMode) {
      if (key === 'Escape') {
        this._viReplaceMode = false;
        this._viNormal = true;
        this._viEndChange();
        if (this._cursorPos > 0) this._cursorPos--;
        return;
      }
      if (key === 'Backspace') {
        // Restore original character if we haven't gone past replaceStart
        if (this._cursorPos > this._viReplaceStart) {
          this._cursorPos--;
          const origIdx = this._cursorPos - this._viReplaceStart;
          if (origIdx < this._viReplaceOriginal.length) {
            const origCh = this._viReplaceOriginal[origIdx];
            this._inputLine = this._inputLine.slice(0, this._cursorPos) + origCh + this._inputLine.slice(this._cursorPos + 1);
          }
        }
        if (this._viInChange) this._viRecording.push(key);
        return;
      }
      if (key.length === 1) {
        if (this._cursorPos < this._inputLine.length) {
          // Overwrite existing character
          this._inputLine = this._inputLine.slice(0, this._cursorPos) + key + this._inputLine.slice(this._cursorPos + 1);
        } else {
          // Append past end
          this._inputLine += key;
        }
        this._cursorPos++;
        if (this._viInChange) this._viRecording.push(key);
        return;
      }
      return;
    }

    // Insert mode (default emacs-style, or vi-insert)
    if (key === 'Backspace') {
      if (this._cursorPos > 0) {
        this._inputLine = this._inputLine.slice(0, this._cursorPos - 1) + this._inputLine.slice(this._cursorPos);
        this._cursorPos--;
      }
    } else if (key === 'ArrowLeft') {
      if (this._cursorPos > 0) this._cursorPos--;
    } else if (key === 'ArrowRight') {
      if (this._cursorPos < this._inputLine.length) this._cursorPos++;
    } else if (key === 'ArrowUp') {
      this._historyUp();
    } else if (key === 'ArrowDown') {
      this._historyDown();
    } else if (key === 'Home') {
      this._cursorPos = 0;
    } else if (key === 'End') {
      this._cursorPos = this._inputLine.length;
    } else if (key === 'Ctrl-C') {
      // Cancel current input
      this._appendOutput(this.prompt + this._inputLine + '^C');
      this._inputLine = '';
      this._cursorPos = 0;
      this._historyIdx = -1;
      this._viNormal = false;
      this._viReplaceMode = false;
      this._viOperator = '';
      this._viCount = '';
    } else if (key === 'Ctrl-D') {
      // On empty line: exit shell. Otherwise: delete char under cursor.
      if (this._inputLine.length === 0) {
        this._appendOutput(this.prompt + 'exit');
        this._exited = true;
        if (this._onExit) this._onExit();
      } else if (this._cursorPos < this._inputLine.length) {
        this._inputLine = this._inputLine.slice(0, this._cursorPos) + this._inputLine.slice(this._cursorPos + 1);
      }
    } else if (key === 'Delete') {
      // Forward-delete: delete char under cursor
      if (this._cursorPos < this._inputLine.length) {
        this._inputLine = this._inputLine.slice(0, this._cursorPos) + this._inputLine.slice(this._cursorPos + 1);
      }
    } else if (key === 'Ctrl-L') {
      // Clear screen
      this._outputLines = [];
      this.scrollTop = 0;
    } else if (key === 'Ctrl-A') {
      this._cursorPos = 0;
    } else if (key === 'Ctrl-E') {
      this._cursorPos = this._inputLine.length;
    } else if (key === 'Ctrl-U') {
      this._inputLine = this._inputLine.slice(this._cursorPos);
      this._cursorPos = 0;
    } else if (key === 'Ctrl-K') {
      this._inputLine = this._inputLine.slice(0, this._cursorPos);
    } else if (key === 'Ctrl-W') {
      // Delete word backward
      const before = this._inputLine.slice(0, this._cursorPos);
      const trimmed = before.replace(/\S+\s*$/, '');
      this._inputLine = trimmed + this._inputLine.slice(this._cursorPos);
      this._cursorPos = trimmed.length;
    } else if (key === 'Tab') {
      this._tabComplete();
    } else if (key === 'Escape') {
      if (this._viMode) {
        // Enter vi normal mode — cursor moves left by 1 (vim behavior)
        this._viNormal = true;
        this._viOperator = '';
        this._viPendingChar = '';
        this._viCount = '';
        this._viEndChange();
        if (this._cursorPos > 0) {
          this._cursorPos--;
        }
      }
    } else if (key.length === 1) {
      // Regular character
      this._inputLine = this._inputLine.slice(0, this._cursorPos) + key + this._inputLine.slice(this._cursorPos);
      this._cursorPos++;
      // Record for dot-repeat if in a vi change
      if (this._viInChange) this._viRecording.push(key);
    }
  }

  // ── Vi normal mode ──

  /**
   * Handle a key in vi normal mode.
   * Supports motions, operators (d/c/y), and mode-switching keys.
   * @private
   */
  _feedKeyViNormal(key) {
    const line = this._inputLine;
    const pos = this._cursorPos;
    const maxPos = Math.max(0, line.length - 1);
    const op = this._viOperator;
    const pending = this._viPendingChar;

    // ── Pending single-char consumers (must be checked FIRST) ──

    if (pending === 'r') {
      if (key.length === 1 && line.length > 0) {
        const cnt = Math.min(this._viGetCount(), line.length - pos);
        this._viSaveUndo();
        this._inputLine = line.slice(0, pos) + key.repeat(cnt) + line.slice(pos + cnt);
        this._cursorPos = pos + cnt - 1;
        this._viEndChange();
      }
      this._viPendingChar = '';
      this._viCount = '';
      return;
    }

    if (pending === 'f' || pending === 'F' || pending === 't' || pending === 'T') {
      if (key.length === 1) {
        const forward = (pending === 'f' || pending === 't');
        const till = (pending === 't' || pending === 'T');
        this._viLastF = { ch: key, forward, till };
        let target = null;
        if (forward) {
          const idx = line.indexOf(key, pos + 1);
          if (idx !== -1) target = till ? idx - 1 : idx;
        } else {
          const idx = line.lastIndexOf(key, pos - 1);
          if (idx !== -1) target = till ? idx + 1 : idx;
        }
        if (target !== null && target >= 0 && target < line.length) {
          if (op) {
            // operator + f/F/t/T motion
            const from = Math.min(pos, target);
            const to = Math.max(pos, target) + 1; // f/t motions are inclusive with operators
            this._viSaveUndo();
            this._viYank = line.slice(from, to);
            if (op === 'd' || op === 'c') {
              this._inputLine = line.slice(0, from) + line.slice(to);
              this._cursorPos = from;
            }
            this._viOperator = '';
            if (op === 'c') { this._viNormal = false; this._viBeginChange(['c', pending, key]); }
            else { this._clampViCursor(); this._viEndChange(); }
          } else {
            this._cursorPos = target;
          }
        }
      }
      this._viPendingChar = '';
      this._viCount = '';
      return;
    }

    // ── Escape cancels pending operator ──
    if (key === 'Escape') {
      this._viOperator = '';
      this._viPendingChar = '';
      this._viCount = '';
      return;
    }

    // ── Numeric count accumulation ──
    if (/[1-9]/.test(key) || (key === '0' && this._viCount !== '')) {
      // '0' alone is a motion (start of line), so only accumulate if already have digits
      this._viCount += key;
      return;
    }

    // ── Mode-switch keys (only without pending operator) ──
    if (!op) {
      if (key === 'i') {
        this._viNormal = false;
        this._viCount = '';
        this._viBeginChange(['i']);
        return;
      }
      if (key === 'I') {
        this._viNormal = false;
        this._cursorPos = 0;
        this._viCount = '';
        this._viBeginChange(['I']);
        return;
      }
      if (key === 'a') {
        this._viNormal = false;
        this._cursorPos = Math.min(pos + 1, line.length);
        this._viCount = '';
        this._viBeginChange(['a']);
        return;
      }
      if (key === 'A') {
        this._viNormal = false;
        this._cursorPos = line.length;
        this._viCount = '';
        this._viBeginChange(['A']);
        return;
      }
      if (key === 's') {
        // substitute: delete count chars under cursor, enter insert
        const cnt = Math.min(this._viGetCount(), line.length - pos);
        this._viSaveUndo();
        if (line.length > 0) {
          this._viYank = line.slice(pos, pos + cnt);
          this._inputLine = line.slice(0, pos) + line.slice(pos + cnt);
        }
        this._viNormal = false;
        this._viCount = '';
        this._viBeginChange(['s']);
        return;
      }
      if (key === 'S') {
        // substitute whole line
        this._viSaveUndo();
        this._viYank = line;
        this._inputLine = '';
        this._cursorPos = 0;
        this._viNormal = false;
        this._viCount = '';
        this._viBeginChange(['S']);
        return;
      }
      if (key === 'C') {
        // change to end of line
        this._viSaveUndo();
        this._viYank = line.slice(pos);
        this._inputLine = line.slice(0, pos);
        this._viNormal = false;
        this._viCount = '';
        this._viBeginChange(['C']);
        return;
      }
      if (key === 'D') {
        // delete to end of line
        this._viSaveUndo();
        this._viYank = line.slice(pos);
        this._inputLine = line.slice(0, pos);
        this._clampViCursor();
        this._viCount = '';
        return;
      }
      if (key === 'R') {
        // Enter replace (overtype) mode
        this._viSaveUndo();
        this._viNormal = false;
        this._viReplaceMode = true;
        this._viReplaceStart = pos;
        this._viReplaceOriginal = line.slice(pos);
        this._viCount = '';
        this._viBeginChange(['R']);
        return;
      }
      if (key === 'u') {
        // Undo
        this._viUndo();
        this._viCount = '';
        return;
      }
      if (key === '.') {
        // Dot repeat — replay last change
        this._viDotRepeat();
        this._viCount = '';
        return;
      }
      if (key === '#') {
        // Comment out line and execute (bash vi-mode)
        this._viSaveUndo();
        this._inputLine = '#' + line;
        this._cursorPos = 0;
        this._viNormal = false;
        this._viCount = '';
        // Execute immediately
        this._viEndChange();
        this._execute();
        return;
      }
    }

    // ── Operator keys ──
    if (key === 'd' || key === 'c' || key === 'y') {
      if (op === key) {
        // dd / cc / yy — operate on entire line
        this._viSaveUndo();
        this._viYank = line;
        if (key === 'd' || key === 'c') {
          this._inputLine = '';
          this._cursorPos = 0;
        }
        this._viOperator = '';
        this._viCount = '';
        if (key === 'c') { this._viNormal = false; this._viBeginChange([key, key]); }
        return;
      }
      this._viOperator = key;
      return;
    }

    // ── f/F/t/T/r: set up pending char consumer ──
    if (key === 'f' || key === 'F' || key === 't' || key === 'T') {
      this._viPendingChar = key;
      return;
    }
    if (!op && key === 'r') {
      this._viPendingChar = 'r';
      return;
    }

    // ── History search: / and ? ──
    if (!op && (key === '/' || key === '?')) {
      this._viSearchMode = key;
      this._viSearchBuffer = '';
      this._viCount = '';
      return;
    }

    // ── G: jump to specific history entry ──
    if (!op && key === 'G') {
      const cnt = this._viCount;
      this._viCount = '';
      if (cnt === '') {
        // G without count = oldest history entry (like real bash)
        if (this._history.length > 0) {
          this._historyIdx = 0;
          this._inputLine = this._history[0];
          this._cursorPos = this._inputLine.length;
          this._clampViCursor();
        }
      } else {
        const n = parseInt(cnt, 10);
        if (n >= 1 && n <= this._history.length) {
          this._historyIdx = n - 1;
          this._inputLine = this._history[n - 1];
          this._cursorPos = this._inputLine.length;
          this._clampViCursor();
        }
      }
      return;
    }

    // ── Resolve motion ──
    const count = this._viGetCount();
    const motion = this._viResolveMotion(key, pos, line);
    if (motion !== null) {
      // Apply count to motions by repeating
      let target = motion.target;
      let inclusive = motion.inclusive;
      if (count > 1 && !op) {
        // For pure motions, repeat the motion count times
        let p = pos;
        for (let i = 0; i < count; i++) {
          const m = this._viResolveMotion(key, p, line);
          if (!m || m.target === p) break;
          p = m.target;
          inclusive = m.inclusive;
        }
        target = p;
      } else if (count > 1 && op) {
        // For operator+motion, repeat motion count times
        let p = pos;
        for (let i = 0; i < count; i++) {
          const m = this._viResolveMotion(key, p, this._inputLine);
          if (!m || m.target === p) break;
          p = m.target;
          inclusive = m.inclusive;
        }
        target = p;
      }

      if (op) {
        // Vim quirk: cw/cW acts like ce/cE (don't eat trailing whitespace)
        let from = Math.min(pos, target);
        let to = Math.max(pos, target);
        if (op === 'c' && (key === 'w' || key === 'W')) {
          // Change-word: only delete to end of current word, not trailing space
          let p = pos;
          for (let i = 0; i < count; i++) {
            const eMotion = this._viResolveMotion(key === 'w' ? 'e' : 'E', p, this._inputLine);
            if (!eMotion || eMotion.target === p) break;
            p = eMotion.target;
          }
          to = p;
          inclusive = true;
        }
        if (inclusive) to++;
        else if (from === to) to++; // at least 1 char
        this._viSaveUndo();
        const deleted = line.slice(from, to);
        this._viYank = deleted;
        if (op === 'd' || op === 'c') {
          this._inputLine = line.slice(0, from) + line.slice(to);
          this._cursorPos = from;
        } else if (op === 'y') {
          // yank only — don't delete
        }
        this._viOperator = '';
        this._viCount = '';
        if (op === 'c') {
          this._viNormal = false;
          this._viBeginChange([op, ...(count > 1 ? [String(count)] : []), key]);
        } else {
          this._clampViCursor();
        }
      } else {
        // Pure motion — just move
        this._cursorPos = Math.min(target, maxPos);
        this._viCount = '';
      }
      return;
    }

    // ── Non-motion action keys (only without pending operator) ──
    if (!op) {
      if (key === 'x') {
        const cnt = Math.min(this._viGetCount(), line.length - pos);
        if (line.length > 0 && pos < line.length) {
          this._viSaveUndo();
          this._viYank = line.slice(pos, pos + cnt);
          this._inputLine = line.slice(0, pos) + line.slice(pos + cnt);
          this._clampViCursor();
        }
        this._viCount = '';
        return;
      }
      if (key === 'X') {
        const cnt = Math.min(this._viGetCount(), pos);
        if (pos > 0) {
          this._viSaveUndo();
          this._viYank = line.slice(pos - cnt, pos);
          this._inputLine = line.slice(0, pos - cnt) + line.slice(pos);
          this._cursorPos = pos - cnt;
        }
        this._viCount = '';
        return;
      }
      if (key === 'p') {
        if (this._viYank) {
          this._viSaveUndo();
          const cnt = this._viGetCount();
          const text = this._viYank.repeat(cnt);
          const after = pos + 1;
          this._inputLine = line.slice(0, after) + text + line.slice(after);
          this._cursorPos = after + text.length - 1;
        }
        this._viCount = '';
        return;
      }
      if (key === 'P') {
        if (this._viYank) {
          this._viSaveUndo();
          const cnt = this._viGetCount();
          const text = this._viYank.repeat(cnt);
          this._inputLine = line.slice(0, pos) + text + line.slice(pos);
          this._cursorPos = pos + text.length - 1;
        }
        this._viCount = '';
        return;
      }
      if (key === '~') {
        const cnt = Math.min(this._viGetCount(), line.length - pos);
        if (line.length > 0 && pos < line.length) {
          this._viSaveUndo();
          let segment = '';
          for (let i = 0; i < cnt; i++) {
            const ch = line[pos + i];
            segment += ch === ch.toLowerCase() ? ch.toUpperCase() : ch.toLowerCase();
          }
          this._inputLine = line.slice(0, pos) + segment + line.slice(pos + cnt);
          this._cursorPos = Math.min(pos + cnt, this._inputLine.length - 1);
        }
        this._viCount = '';
        return;
      }
      // ArrowUp / ArrowDown for history even in normal mode
      if (key === 'ArrowUp' || key === 'k') {
        this._historyUp();
        this._clampViCursor();
        this._viCount = '';
        return;
      }
      if (key === 'ArrowDown' || key === 'j') {
        this._historyDown();
        this._clampViCursor();
        this._viCount = '';
        return;
      }
      // n / N — repeat history search
      if (key === 'n') {
        if (this._viSearchPattern) {
          this._viHistorySearch(this._viSearchPattern, -1);
        }
        this._viCount = '';
        return;
      }
      if (key === 'N') {
        if (this._viSearchPattern) {
          this._viHistorySearch(this._viSearchPattern, 1);
        }
        this._viCount = '';
        return;
      }
      // ; and , repeat last f/F/t/T
      if (key === ';' || key === ',') {
        if (this._viLastF) {
          const forward = key === ';' ? this._viLastF.forward : !this._viLastF.forward;
          const till = this._viLastF.till;
          const ch = this._viLastF.ch;
          let target = null;
          if (forward) {
            const idx = line.indexOf(ch, pos + 1);
            if (idx !== -1) target = till ? idx - 1 : idx;
          } else {
            const idx = line.lastIndexOf(ch, pos - 1);
            if (idx !== -1) target = till ? idx + 1 : idx;
          }
          if (target !== null && target >= 0 && target < line.length) {
            this._cursorPos = target;
          }
        }
        this._viCount = '';
        return;
      }
    }

    // Unknown key in normal mode — ignore
    this._viOperator = '';
    this._viPendingChar = '';
    this._viCount = '';
  }

  /**
   * Resolve a vi motion key to a target position.
   * Returns { target, inclusive } or null if not a motion.
   * @private
   */
  _viResolveMotion(key, pos, line) {
    const len = line.length;
    if (key === 'h' || key === 'ArrowLeft') {
      return { target: Math.max(0, pos - 1), inclusive: false };
    }
    if (key === 'l' || key === 'ArrowRight' || key === ' ') {
      return { target: Math.min(pos + 1, Math.max(0, len - 1)), inclusive: false };
    }
    if (key === '0' || key === 'Home') {
      return { target: 0, inclusive: false };
    }
    if (key === '$' || key === 'End') {
      return { target: Math.max(0, len - 1), inclusive: true };
    }
    if (key === '^' || key === '_') {
      // First non-whitespace
      const m = line.match(/\S/);
      return { target: m ? m.index : 0, inclusive: false };
    }
    if (key === 'w') {
      // Next word start
      let i = pos;
      // Skip current word chars
      if (i < len && /\w/.test(line[i])) {
        while (i < len && /\w/.test(line[i])) i++;
      } else if (i < len && /[^\w\s]/.test(line[i])) {
        while (i < len && /[^\w\s]/.test(line[i])) i++;
      } else {
        i++;
      }
      // Skip whitespace
      while (i < len && /\s/.test(line[i])) i++;
      return { target: i, inclusive: false };
    }
    if (key === 'W') {
      // Next WORD start (whitespace-delimited)
      let i = pos;
      while (i < len && !/\s/.test(line[i])) i++;
      while (i < len && /\s/.test(line[i])) i++;
      return { target: i, inclusive: false };
    }
    if (key === 'b') {
      // Previous word start
      let i = pos;
      if (i > 0) i--;
      while (i > 0 && /\s/.test(line[i])) i--;
      if (/\w/.test(line[i])) {
        while (i > 0 && /\w/.test(line[i - 1])) i--;
      } else if (/[^\w\s]/.test(line[i])) {
        while (i > 0 && /[^\w\s]/.test(line[i - 1])) i--;
      }
      return { target: i, inclusive: false };
    }
    if (key === 'B') {
      // Previous WORD start
      let i = pos;
      if (i > 0) i--;
      while (i > 0 && /\s/.test(line[i])) i--;
      while (i > 0 && !/\s/.test(line[i - 1])) i--;
      return { target: i, inclusive: false };
    }
    if (key === 'e') {
      // End of word
      let i = pos;
      if (i < len - 1) i++;
      while (i < len - 1 && /\s/.test(line[i])) i++;
      if (/\w/.test(line[i])) {
        while (i < len - 1 && /\w/.test(line[i + 1])) i++;
      } else if (/[^\w\s]/.test(line[i])) {
        while (i < len - 1 && /[^\w\s]/.test(line[i + 1])) i++;
      }
      return { target: i, inclusive: true };
    }
    if (key === 'E') {
      // End of WORD
      let i = pos;
      if (i < len - 1) i++;
      while (i < len - 1 && /\s/.test(line[i])) i++;
      while (i < len - 1 && !/\s/.test(line[i + 1])) i++;
      return { target: i, inclusive: true };
    }
    return null;
  }

  /**
   * Clamp cursor to valid vi-normal-mode range (0..len-1).
   * @private
   */
  _clampViCursor() {
    const maxPos = Math.max(0, this._inputLine.length - 1);
    if (this._cursorPos > maxPos) this._cursorPos = maxPos;
    if (this._cursorPos < 0) this._cursorPos = 0;
  }

  /**
   * Get the numeric count (default 1) and reset the accumulator.
   * @private
   */
  _viGetCount() {
    const n = this._viCount ? parseInt(this._viCount, 10) : 1;
    return Math.max(1, n);
  }

  /**
   * Save current line state to undo stack.
   * @private
   */
  _viSaveUndo() {
    this._viUndoStack.push({ line: this._inputLine, cursorPos: this._cursorPos });
    // Cap undo stack at 100 entries
    if (this._viUndoStack.length > 100) this._viUndoStack.shift();
  }

  /**
   * Undo: restore last saved state.
   * @private
   */
  _viUndo() {
    if (this._viUndoStack.length > 0) {
      const state = this._viUndoStack.pop();
      this._inputLine = state.line;
      this._cursorPos = state.cursorPos;
      this._clampViCursor();
    }
  }

  /**
   * Begin recording keys for a change (for dot-repeat).
   * @private
   */
  _viBeginChange(prefixKeys) {
    this._viInChange = true;
    this._viRecording = [...prefixKeys];
  }

  /**
   * End the current change recording and save for dot-repeat.
   * @private
   */
  _viEndChange() {
    if (this._viInChange) {
      this._viLastChange = { keys: [...this._viRecording] };
      this._viInChange = false;
      this._viRecording = [];
    }
  }

  /**
   * Dot-repeat: replay the last recorded change.
   * @private
   */
  _viDotRepeat() {
    if (!this._viLastChange) return;
    this._viSaveUndo();
    const keys = this._viLastChange.keys;
    // Replay all the keys that made up the last change
    for (const k of keys) {
      this.feedKey(k);
    }
    // End in normal mode
    if (!this._viNormal) {
      this.feedKey('Escape');
    }
  }

  /**
   * Search through command history for a pattern.
   * dir: -1 = search backward (older), 1 = search forward (newer)
   * @private
   */
  _viHistorySearch(pattern, dir) {
    if (this._history.length === 0) return;
    let startIdx;
    if (this._historyIdx === -1) {
      this._savedInput = this._inputLine;
      startIdx = dir < 0 ? this._history.length - 1 : 0;
    } else {
      startIdx = this._historyIdx + dir;
    }

    try {
      const re = new RegExp(pattern);
      let idx = startIdx;
      while (idx >= 0 && idx < this._history.length) {
        if (re.test(this._history[idx])) {
          this._historyIdx = idx;
          this._inputLine = this._history[idx];
          this._cursorPos = this._inputLine.length;
          this._clampViCursor();
          return;
        }
        idx += dir;
      }
    } catch {
      // Invalid regex — try plain substring match
      let idx = startIdx;
      while (idx >= 0 && idx < this._history.length) {
        if (this._history[idx].includes(pattern)) {
          this._historyIdx = idx;
          this._inputLine = this._history[idx];
          this._cursorPos = this._inputLine.length;
          this._clampViCursor();
          return;
        }
        idx += dir;
      }
    }
  }

  /**
   * Get the current screen state as an array of text lines.
   * Each line is exactly this.cols characters (padded with spaces).
   * The last row contains the prompt + current input.
   *
   * @returns {{ lines: string[], cursor: {row: number, col: number} }}
   */
  getScreen() {
    const lines = [];
    const totalOutput = this._outputLines.length;
    // Total content = output lines + 1 prompt line
    const totalContent = totalOutput + 1;

    if (totalContent <= this.rows) {
      // ── Content fits on screen — no scrolling ──
      // Output lines at top, prompt right after, blanks fill the rest.
      for (let r = 0; r < totalOutput; r++) {
        lines.push(this._pad(this._outputLines[r]));
      }
      // Prompt line immediately after output
      const promptStr = this.prompt;
      const inputDisplay = promptStr + this._inputLine;
      lines.push(this._pad(inputDisplay));
      const promptRow = totalOutput;
      // Blank rows to fill remaining screen
      for (let r = totalContent; r < this.rows; r++) {
        lines.push(' '.repeat(this.cols));
      }
      let cursorCol = Math.min(promptStr.length + this._cursorPos, this.cols - 1);
      // If in search mode, override last row to show search prompt
      if (this._viSearchMode) {
        const searchLine = this._viSearchMode + this._viSearchBuffer;
        // Replace the last used row (or add a new row if blank rows exist)
        const searchRow = Math.min(promptRow + 1, this.rows - 1);
        lines[searchRow] = this._pad(searchLine);
        cursorCol = searchLine.length;
        return { lines, cursor: { row: searchRow, col: cursorCol } };
      }
      return { lines, cursor: { row: promptRow, col: cursorCol } };
    } else {
      // ── Content overflows — scroll so prompt is on last row ──
      const visibleOutputRows = this.rows - 1;
      const maxScroll = Math.max(0, totalOutput - visibleOutputRows);
      this.scrollTop = Math.min(this.scrollTop, maxScroll);
      const startLine = this.scrollTop;
      for (let r = 0; r < visibleOutputRows; r++) {
        const lineIdx = startLine + r;
        if (lineIdx < totalOutput) {
          lines.push(this._pad(this._outputLines[lineIdx]));
        } else {
          lines.push(' '.repeat(this.cols));
        }
      }
      // Prompt on last row
      const promptStr = this.prompt;
      const inputDisplay = promptStr + this._inputLine;
      lines.push(this._pad(inputDisplay));
      const cursorCol = Math.min(promptStr.length + this._cursorPos, this.cols - 1);
      return { lines, cursor: { row: this.rows - 1, col: cursorCol } };
    }
  }

  /**
   * Render a Frame dict matching the Screen.render() format.
   * This allows the same Renderer to draw both shell and vim.
   *
   * @param {object} theme – theme object with color properties
   * @returns {object} Frame dict
   */
  renderFrame(theme) {
    const t = theme;
    const { lines: textLines, cursor } = this.getScreen();
    const frameLines = [];
    const bg = t.normalBg || '14161b';
    const fg = t.normalFg || 'e0e2ea';
    // Real zsh oh-my-zsh prompt colors: green arrow, cyan dirname
    const arrowFg = '00ff00';
    const dirFg = '00ffff';
    const arrowLen = this._promptArrowLen;
    const dirLen = this._promptDirLen;
    const promptStr = this.prompt;

    for (let r = 0; r < textLines.length; r++) {
      const text = textLines[r];
      const isInputLine = (r === cursor.row);
      // Check if this output line starts with the prompt (echoed command)
      const hasPrompt = isInputLine || text.startsWith(promptStr);

      if (hasPrompt && arrowLen + dirLen < this.cols) {
        // Color: green arrow, cyan dirname, default rest
        const runs = [];
        runs.push({ n: arrowLen, fg: arrowFg, bg, b: true });
        runs.push({ n: dirLen, fg: dirFg, bg, b: true });
        const rest = this.cols - arrowLen - dirLen;
        if (rest > 0) runs.push({ n: rest, fg, bg });
        frameLines.push({ text, runs });
      } else {
        // Regular output line
        frameLines.push({
          text,
          runs: [{ n: this.cols, fg, bg }],
        });
      }
    }

    // Cursor shape: block in vi-normal and replace mode, beam in insert/emacs
    const cursorShape = (this._viMode && (this._viNormal || this._viReplaceMode)) ? 'block' : 'beam';

    return {
      rows: this.rows,
      cols: this.cols,
      cursor: { row: cursor.row, col: cursor.col, visible: true, shape: cursorShape },
      defaultFg: t.normalFg || 'e0e2ea',
      defaultBg: t.normalBg || '14161b',
      lines: frameLines,
    };
  }

  // ── Command execution ──

  /** @private */
  _execute() {
    const fullLine = this.prompt + this._inputLine;
    this._appendOutput(fullLine);

    const raw = this._inputLine.trim();
    this._inputLine = '';
    this._cursorPos = 0;

    if (raw) {
      this._history.push(raw);
      this._historyIdx = -1;
      this._runCommand(raw);
    }
  }

  /** @private */
  _runCommand(raw) {
    // Simple tokenization (handles quotes minimally)
    const args = this._tokenize(raw);
    if (args.length === 0) return;

    const cmd = args[0];
    const rest = args.slice(1);

    switch (cmd) {
      case 'vi':
      case 'vim':
      case 'nvim':
        this._cmdVim(rest);
        break;
      case 'ls':
        this._cmdLs(rest);
        break;
      case 'cat':
        this._cmdCat(rest);
        break;
      case 'rm':
        this._cmdRm(rest);
        break;
      case 'touch':
        this._cmdTouch(rest);
        break;
      case 'echo':
        this._cmdEcho(rest, raw);
        break;
      case 'sort':
        this._cmdSort(rest);
        break;
      case 'wc':
        this._cmdWc(rest);
        break;

      case 'grep':
        this._cmdGrep(rest);
        break;
      case 'cp':
        this._cmdCp(rest);
        break;
      case 'mv':
        this._cmdMv(rest);
        break;
      case 'history':
        this._cmdHistory();
        break;

      case 'exit':
        this._exited = true;
        break;
      case 'tmux':
        this._cmdTmux(rest);
        break;

      case 'set':
        this._cmdSet(rest);
        break;
      case 'date':
        this._appendOutput(ShellSim._formatDate(new Date()));
        break;
      case 'clear':
        this._outputLines = [];
        this.scrollTop = 0;
        break;
      case 'help':
        this._cmdHelp();
        break;
      default:
        this._appendOutput(`zsh: command not found: ${cmd}`);
        break;
    }
  }

  // ── Built-in commands ──

  /** @private */
  _cmdVim(args) {
    const filename = args[0] || null;
    if (this.onLaunchVim) {
      this.onLaunchVim(filename);
    }
  }

  /** @private */
  _cmdTmux(args) {
    if (this._insideTmux) {
      this._appendOutput('sessions should be nested with care, unset $TMUX to force');
      return;
    }
    if (this.onLaunchTmux) {
      this.onLaunchTmux(args);
    } else {
      this._appendOutput('zsh: command not found: tmux');
    }
  }

  /** @private */
  _cmdLs(args) {
    const files = this.fs.ls();
    if (files.length === 0) return; // empty — no output like real ls
    // Simple column layout
    this._appendOutput(files.join('  '));
  }

  /** @private */
  _cmdCat(args) {
    if (args.length === 0) {
      // cat with no args: just return (real cat reads stdin, but we skip that)
      return;
    }
    for (const name of args) {
      const contents = this.fs.read(name);
      if (contents === null) {
        this._appendOutput(`cat: ${name}: No such file or directory`);
      } else {
        // Output each line
        const lines = contents.split('\n');
        for (const line of lines) {
          this._appendOutput(line);
        }
      }
    }
  }

  /** @private */
  _cmdRm(args) {
    for (const name of args) {
      if (!this.fs.rm(name)) {
        this._appendOutput(`rm: cannot remove '${name}': No such file or directory`);
      }
    }
  }

  /** @private */
  _cmdTouch(args) {
    for (const name of args) {
      if (!this.fs.exists(name)) {
        this.fs.write(name, '');
      }
    }
  }

  /** @private */
  _cmdEcho(args, raw) {
    // Check for append redirect: echo text >> file
    const appendIdx = args.indexOf('>>');
    if (appendIdx >= 0) {
      const text = args.slice(0, appendIdx).join(' ');
      const filename = args[appendIdx + 1];
      if (filename) {
        const existing = this.fs.read(filename) || '';
        this.fs.write(filename, existing + (existing ? '\n' : '') + this._unquote(text));
      } else {
        this._appendOutput('zsh: parse error near `\\n\'');
      }
      return;
    }
    // Check for redirect: echo text > file
    const redirectIdx = args.indexOf('>');
    if (redirectIdx >= 0) {
      const text = args.slice(0, redirectIdx).join(' ');
      const filename = args[redirectIdx + 1];
      if (filename) {
        this.fs.write(filename, this._unquote(text));
      } else {
        this._appendOutput('zsh: parse error near `\\n\'');
      }
    } else {
      const text = args.join(' ');
      this._appendOutput(this._unquote(text));
    }
  }

  /** @private */
  _cmdSort(args) {
    // Flags
    let reverse = false;
    let numeric = false;
    let unique = false;
    const files = [];
    for (const arg of args) {
      if (arg === '-r' || arg === '--reverse') reverse = true;
      else if (arg === '-n' || arg === '--numeric-sort') numeric = true;
      else if (arg === '-u' || arg === '--unique') unique = true;
      else if (arg.startsWith('-') && arg.length > 1) {
        // Combined flags like -rn
        for (const ch of arg.slice(1)) {
          if (ch === 'r') reverse = true;
          else if (ch === 'n') numeric = true;
          else if (ch === 'u') unique = true;
          else {
            this._appendOutput(`sort: invalid option -- '${ch}'`);
            return;
          }
        }
      } else {
        files.push(arg);
      }
    }
    if (files.length === 0) {
      this._appendOutput('sort: missing file operand');
      return;
    }
    for (const name of files) {
      const contents = this.fs.read(name);
      if (contents === null) {
        this._appendOutput(`sort: cannot read: ${name}: No such file or directory`);
        continue;
      }
      let lines = contents.split('\n');
      // Remove trailing empty line from final newline
      if (lines.length > 0 && lines[lines.length - 1] === '') lines.pop();
      if (numeric) {
        lines.sort((a, b) => {
          const na = parseFloat(a) || 0;
          const nb = parseFloat(b) || 0;
          return na - nb;
        });
      } else {
        lines.sort();
      }
      if (reverse) lines.reverse();
      if (unique) lines = [...new Set(lines)];
      for (const line of lines) {
        this._appendOutput(line);
      }
    }
  }

  /** @private */
  _cmdWc(args) {
    const flags = [];
    const files = [];
    for (const arg of args) {
      if (arg.startsWith('-') && arg.length > 1) {
        for (const ch of arg.slice(1)) {
          if ('lwc'.includes(ch)) flags.push(ch);
          else {
            this._appendOutput(`wc: invalid option -- '${ch}'`);
            return;
          }
        }
      } else {
        files.push(arg);
      }
    }
    if (files.length === 0) {
      this._appendOutput('wc: missing file operand');
      return;
    }
    const showAll = flags.length === 0;
    const showLines = showAll || flags.includes('l');
    const showWords = showAll || flags.includes('w');
    const showBytes = showAll || flags.includes('c');
    for (const name of files) {
      const contents = this.fs.read(name);
      if (contents === null) {
        this._appendOutput(`wc: ${name}: No such file or directory`);
        continue;
      }
      const lines = contents === '' ? 0 : contents.split('\n').length;
      const words = contents === '' ? 0 : contents.split(/\s+/).filter(w => w).length;
      const bytes = contents.length;
      const parts = [];
      if (showLines) parts.push(String(lines).padStart(8));
      if (showWords) parts.push(String(words).padStart(8));
      if (showBytes) parts.push(String(bytes).padStart(8));
      parts.push(` ${name}`);
      this._appendOutput(parts.join(''));
    }
  }



  /** @private */
  _cmdGrep(args) {
    let ignoreCase = false;
    let showLineNums = false;
    let countOnly = false;
    const positional = [];
    for (const arg of args) {
      if (arg.startsWith('-') && arg.length > 1 && !/^\d/.test(arg.slice(1))) {
        for (const ch of arg.slice(1)) {
          if (ch === 'i') ignoreCase = true;
          else if (ch === 'n') showLineNums = true;
          else if (ch === 'c') countOnly = true;
          else {
            this._appendOutput(`grep: invalid option -- '${ch}'`);
            return;
          }
        }
      } else {
        positional.push(arg);
      }
    }
    if (positional.length < 2) {
      this._appendOutput('Usage: grep [options] pattern file');
      return;
    }
    const pattern = positional[0];
    const files = positional.slice(1);
    let re;
    try {
      re = new RegExp(pattern, ignoreCase ? 'i' : '');
    } catch (e) {
      this._appendOutput(`grep: invalid regex: ${pattern}`);
      return;
    }
    for (const name of files) {
      const contents = this.fs.read(name);
      if (contents === null) {
        this._appendOutput(`grep: ${name}: No such file or directory`);
        continue;
      }
      const lines = contents.split('\n');
      let count = 0;
      const prefix = files.length > 1 ? `${name}:` : '';
      for (let i = 0; i < lines.length; i++) {
        if (re.test(lines[i])) {
          count++;
          if (!countOnly) {
            const lineNum = showLineNums ? `${i + 1}:` : '';
            this._appendOutput(`${prefix}${lineNum}${lines[i]}`);
          }
        }
      }
      if (countOnly) {
        this._appendOutput(`${prefix}${count}`);
      }
    }
  }

  /** @private */
  _cmdCp(args) {
    if (args.length < 2) {
      this._appendOutput('cp: missing file operand');
      return;
    }
    const src = args[0];
    const dst = args[1];
    const contents = this.fs.read(src);
    if (contents === null) {
      this._appendOutput(`cp: cannot stat '${src}': No such file or directory`);
      return;
    }
    this.fs.write(dst, contents);
  }

  /** @private */
  _cmdMv(args) {
    if (args.length < 2) {
      this._appendOutput('mv: missing file operand');
      return;
    }
    const src = args[0];
    const dst = args[1];
    const contents = this.fs.read(src);
    if (contents === null) {
      this._appendOutput(`mv: cannot stat '${src}': No such file or directory`);
      return;
    }
    this.fs.write(dst, contents);
    this.fs.rm(src);
  }

  /** @private */
  _cmdHistory() {
    for (let i = 0; i < this._history.length; i++) {
      const num = String(i + 1).padStart(5);
      this._appendOutput(`${num}  ${this._history[i]}`);
    }
  }



  /** @private */
  _cmdSet(args) {
    if (args.length === 2 && args[0] === '-o' && args[1] === 'vi') {
      this._viMode = true;
      this._viNormal = false; // start in insert mode
      this._viReplaceMode = false;
      this._viUndoStack = [];
      this._viLastChange = null;
      this._viCount = '';
      this._viSearchPattern = '';
    } else if (args.length === 2 && args[0] === '-o' && args[1] === 'emacs') {
      this._viMode = false;
      this._viNormal = false;
      this._viReplaceMode = false;
    } else if (args.length >= 2 && args[0] === '-o') {
      this._appendOutput(`set: no such option: ${args[1]}`);
    } else if (args.length === 0) {
      // Show current settings
      this._appendOutput(`editing-mode ${this._viMode ? 'vi' : 'emacs'}`);
    } else {
      this._appendOutput(`set: usage: set -o [vi|emacs]`);
    }
  }

  /** @private */
  _cmdHelp() {
    const cmds = [
      'Available commands:',
      '  nvim [file]   Open file in Neovim (also: vim, vi)',
      '  ls            List files',
      '  cat <file>    Display file contents',
      '  rm <file>     Remove a file',
      '  touch <file>  Create empty file',
      '  cp <s> <d>    Copy a file',
      '  mv <s> <d>    Move/rename a file',
      '  echo <text>   Print text (> and >> redirect)',
      '  wc <file>     Count lines, words, bytes',
      '  grep <p> <f>  Search for pattern in file',
      '  sort <file>   Sort lines of a file (-r -n -u)',
      '  history       Show command history',
      '  tmux          Start terminal multiplexer (attach, ls)',
      '  set -o vi     Enable vi-mode editing (set -o emacs to disable)',
      '  date          Print current date and time',
      '  clear         Clear screen',
      '  exit          Exit shell',
      '  help          Show this help',
    ];
    for (const line of cmds) {
      this._appendOutput(line);
    }
  }

  // ── History ──

  /** @private */
  _historyUp() {
    if (this._history.length === 0) return;
    if (this._historyIdx === -1) {
      this._savedInput = this._inputLine;
      this._historyIdx = this._history.length - 1;
    } else if (this._historyIdx > 0) {
      this._historyIdx--;
    }
    this._inputLine = this._history[this._historyIdx];
    this._cursorPos = this._inputLine.length;
  }

  /** @private */
  _historyDown() {
    if (this._historyIdx === -1) return;
    if (this._historyIdx < this._history.length - 1) {
      this._historyIdx++;
      this._inputLine = this._history[this._historyIdx];
    } else {
      this._historyIdx = -1;
      this._inputLine = this._savedInput;
    }
    this._cursorPos = this._inputLine.length;
  }

  // ── Tab completion ──

  /** @private */
  _tabComplete() {
    const before = this._inputLine.slice(0, this._cursorPos);
    const parts = before.split(/\s+/);
    const partial = parts[parts.length - 1] || '';

    if (!partial) return;

    // If on the first word, complete command names; otherwise complete filenames
    const isFirstWord = parts.length === 1 || (parts.length === 2 && parts[0] === '');
    let matches;
    if (isFirstWord) {
      const commands = [
        'vim', 'vi', 'nvim', 'ls', 'cat', 'rm', 'touch', 'cp', 'mv',
        'echo', 'wc', 'grep', 'sort', 'history',
        'set', 'date', 'clear', 'exit', 'help', 'tmux',
      ];
      matches = commands.filter(c => c.startsWith(partial));
    } else {
      matches = this.fs.ls().filter(f => f.startsWith(partial));
    }

    if (matches.length === 1) {
      const completed = matches[0];
      const rest = completed.slice(partial.length);
      // Add trailing space after completed command name
      const suffix = isFirstWord ? rest + ' ' : rest;
      this._inputLine = before + suffix + this._inputLine.slice(this._cursorPos);
      this._cursorPos += suffix.length;
    } else if (matches.length > 1) {
      // Show matches
      this._appendOutput(this.prompt + this._inputLine);
      this._appendOutput(matches.join('  '));
    }
  }

  // ── Helpers ──

  /**
   * Format a Date like Unix `date` command.
   * e.g. "Sat Feb 21 21:24:56 PST 2026"
   */
  static _formatDate(d) {
    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const day = days[d.getDay()];
    const mon = months[d.getMonth()];
    const dd = String(d.getDate()).padStart(2, ' ');
    const time = d.toTimeString().split(' ')[0]; // HH:MM:SS
    // Extract short timezone name from toString(), e.g. "PST"
    const tzMatch = d.toString().match(/\(([^)]+)\)/);
    let tz = '';
    if (tzMatch) {
      // Abbreviate e.g. "Pacific Standard Time" → "PST"
      const full = tzMatch[1];
      tz = full.includes(' ') ? full.split(' ').map(w => w[0]).join('') : full;
    }
    const year = d.getFullYear();
    return `${day} ${mon} ${dd} ${time} ${tz} ${year}`;
  }

  /** @private – pad or truncate a string to this.cols */
  _pad(s) {
    if (s.length >= this.cols) return s.slice(0, this.cols);
    return s + ' '.repeat(this.cols - s.length);
  }

  /** @private – add a line to the output buffer */
  _appendOutput(line) {
    // Word-wrap long lines
    if (line.length <= this.cols) {
      this._outputLines.push(line);
    } else {
      for (let i = 0; i < line.length; i += this.cols) {
        this._outputLines.push(line.slice(i, i + this.cols));
      }
    }
    // Auto-scroll: when output + prompt exceeds screen, scroll to show end
    const visibleOutputRows = this.rows - 1;
    const maxScroll = Math.max(0, this._outputLines.length - visibleOutputRows);
    this.scrollTop = maxScroll;
  }

  /** @private – simple tokenizer that respects single/double quotes */
  _tokenize(input) {
    const tokens = [];
    let current = '';
    let inSingle = false;
    let inDouble = false;

    for (let i = 0; i < input.length; i++) {
      const ch = input[i];
      if (ch === "'" && !inDouble) {
        inSingle = !inSingle;
      } else if (ch === '"' && !inSingle) {
        inDouble = !inDouble;
      } else if (ch === ' ' && !inSingle && !inDouble) {
        if (current) {
          tokens.push(current);
          current = '';
        }
      } else {
        current += ch;
      }
    }
    if (current) tokens.push(current);
    return tokens;
  }

  /** @private – remove surrounding quotes from a string */
  _unquote(s) {
    if ((s.startsWith("'") && s.endsWith("'")) || (s.startsWith('"') && s.endsWith('"'))) {
      return s.slice(1, -1);
    }
    return s;
  }
}
