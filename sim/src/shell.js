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
 *   pwd            – print working directory
 *   clear          – clear screen
 *   exit / quit    – (no-op in browser, could signal parent)
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
   */
  constructor({ fs, rows = 20, cols = 40, cwd = '~/vimfu', dirname = 'vimfu', user = 'user', hostname = 'vimfu', onLaunchVim = null } = {}) {
    this.fs = fs;
    this.rows = rows;
    this.cols = cols;
    this.cwd = cwd;
    this.dirname = dirname;
    this.user = user;
    this.hostname = hostname;
    this.onLaunchVim = onLaunchVim;

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

    if (key === 'Enter') {
      this._execute();
    } else if (key === 'Backspace') {
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
      // Ignore in shell
    } else if (key.length === 1) {
      // Regular character
      this._inputLine = this._inputLine.slice(0, this._cursorPos) + key + this._inputLine.slice(this._cursorPos);
      this._cursorPos++;
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
      const cursorCol = Math.min(promptStr.length + this._cursorPos, this.cols - 1);
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

    return {
      rows: this.rows,
      cols: this.cols,
      cursor: { row: cursor.row, col: cursor.col, visible: true },
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
      case 'pwd':
        this._appendOutput(this.cwd);
        break;
      case 'clear':
        this._outputLines = [];
        this.scrollTop = 0;
        break;
      case 'help':
        this._cmdHelp();
        break;
      case 'exit':
      case 'quit':
        this._appendOutput('logout');
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
  _cmdHelp() {
    const cmds = [
      'Available commands:',
      '  vim [file]    Open file in Vim',
      '  nvim [file]   Open file in Vim',
      '  ls            List files',
      '  cat <file>    Display file contents',
      '  rm <file>     Remove a file',
      '  touch <file>  Create empty file',
      '  echo <text>   Print text (supports > redirect)',
      '  pwd           Print working directory',
      '  clear         Clear screen',
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

    // Complete filenames
    const matches = this.fs.ls().filter(f => f.startsWith(partial));
    if (matches.length === 1) {
      const completed = matches[0];
      const rest = completed.slice(partial.length);
      this._inputLine = before + rest + this._inputLine.slice(this._cursorPos);
      this._cursorPos += rest.length;
    } else if (matches.length > 1) {
      // Show matches
      this._appendOutput(this.prompt + this._inputLine);
      this._appendOutput(matches.join('  '));
    }
  }

  // ── Helpers ──

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
