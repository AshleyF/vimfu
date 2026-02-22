/**
 * VimFu Simulator – Session Manager
 *
 * Orchestrates the relationship between the shell simulator and
 * the Vim engine. Handles:
 *   - Switching from shell → Vim (when user types `vim file`)
 *   - Switching from Vim → shell (when user does :q, :wq, ZZ, ZQ)
 *   - File I/O between VimEngine and VirtualFS (:w, :e)
 *   - Shell command execution from Vim (:! commands)
 *   - The "Press ENTER to continue" prompt after :! commands
 *
 * The SessionManager owns the active "mode" of the whole terminal:
 *   - 'shell'  → shell gets keystrokes, shell renders
 *   - 'vim'    → engine gets keystrokes, engine renders
 *   - 'shell_msg' → showing output of :! command, waiting for Enter
 */

import { VimEngine } from './engine.js';
import { ShellSim } from './shell.js';
import { VirtualFS } from './vfs.js';
import { Screen } from './screen.js';

/** @typedef {'shell' | 'vim' | 'shell_msg'} SessionMode */

export class SessionManager {
  /**
   * @param {object} opts
   * @param {number} [opts.rows=20]
   * @param {number} [opts.cols=40]
   * @param {string} [opts.themeName='nvim_default']
   * @param {boolean} [opts.persist=true] – localStorage persistence
   * @param {function} [opts.onUpdate] – callback(frame) after each key
   */
  constructor({ rows = 20, cols = 40, themeName = 'nvim_default', persist = true, onUpdate = null } = {}) {
    this.rows = rows;
    this.cols = cols;

    /** @type {SessionMode} */
    this.mode = 'shell';

    // Virtual filesystem (shared between shell and vim)
    this.fs = new VirtualFS({ persist });

    // Shell simulator
    this.shell = new ShellSim({
      fs: this.fs,
      rows,
      cols,
      onLaunchVim: (filename) => this._launchVim(filename),
    });

    // Vim engine (created on demand when vim is launched)
    /** @type {VimEngine|null} */
    this.engine = null;

    // Screen renderer (for vim mode)
    this.screen = new Screen(rows, cols, themeName);

    // Current filename open in vim
    this._vimFilename = null;

    // Undo-position-based dirty detection (saved change count)
    this._savedChangeCount = 0;

    // Shell message display (for :! output)
    this._shellMsgLines = [];

    // Callback
    this.onUpdate = onUpdate;

    // Engine event hooks — we'll monkey-patch the engine command handler
    this._engineCommandHook = null;
  }

  // ── Public API ──

  /**
   * Get the current active mode.
   * @returns {SessionMode}
   */
  getMode() {
    return this.mode;
  }

  /**
   * Feed a key to the active component (shell or vim).
   * @param {string} key
   */
  feedKey(key) {
    if (this.mode === 'shell') {
      this.shell.feedKey(key);
    } else if (this.mode === 'vim') {
      this.engine.feedKey(key);
      this._checkVimCommand();
    } else if (this.mode === 'shell_msg') {
      // Any key dismisses the shell message and returns to vim
      if (key === 'Enter' || key === 'Escape' || key.length === 1) {
        this.mode = 'vim';
      }
    }

    if (this.onUpdate) {
      this.onUpdate(this.renderFrame());
    }
  }

  /**
   * Render the current frame based on active mode.
   * @returns {object} Frame dict
   */
  renderFrame() {
    if (this.mode === 'shell') {
      return this.shell.renderFrame(this.screen.theme);
    } else if (this.mode === 'vim') {
      return this.screen.render(this.engine);
    } else if (this.mode === 'shell_msg') {
      return this._renderShellMsg();
    }
  }

  /**
   * Get the display mode label (for UI badges etc.)
   * @returns {string}
   */
  getModeLabel() {
    if (this.mode === 'shell') return 'SHELL';
    if (this.mode === 'shell_msg') return 'SHELL';
    if (this.mode === 'vim' && this.engine) {
      const vimMode = this.engine.mode;
      const labels = {
        normal: 'NORMAL', insert: 'INSERT', visual: 'VISUAL',
        visual_line: 'VISUAL LINE', replace: 'REPLACE', command: 'COMMAND',
      };
      return labels[vimMode] || vimMode.toUpperCase();
    }
    return 'SHELL';
  }

  // ── Vim lifecycle ──

  /** @private – launch vim from the shell */
  _launchVim(filename) {
    this._vimFilename = filename;

    // Create a fresh engine
    this.engine = new VimEngine({ rows: this.rows, cols: this.cols });
    this.engine.filename = filename;  // for syntax highlighting

    // Load file from VFS if it exists, otherwise start empty
    if (filename && this.fs.exists(filename)) {
      const content = this.fs.read(filename);
      this.engine.loadFile(content);
    } else {
      this.engine.loadFile('');
    }
    // Track undo-position at load time for dirty detection
    this._savedChangeCount = this.engine._changeCount;

    // Set the filename in the engine's status
    this._updateVimStatus();

    this.mode = 'vim';
  }

  /** @private – check if vim executed a command that requires session action */
  _checkVimCommand() {
    if (!this.engine) return;

    // Check if the engine just processed a command
    const cmd = this.engine._lastExCommand;
    if (!cmd) return;

    // Clear the flag
    this.engine._lastExCommand = null;

    this._handleExCommand(cmd);
  }

  /** @private */
  _handleExCommand(cmd) {
    // Parse ex command
    const trimmed = cmd.trim();

    // :w[rite] [filename] – write
    if (/^w(r(i(te?)?)?)?(\s|$)/.test(trimmed)) {
      const parts = trimmed.split(/\s+/);
      const filename = parts[1] || this._vimFilename;
      if (filename) {
        this._saveFile(filename);
        if (!this._vimFilename) this._vimFilename = filename;
        this._updateVimStatus();
        // Show "written" message matching nvim: "file" NL, NB written
        const lineCount = this.engine.buffer.lineCount;
        const byteCount = this.engine.buffer.lines.join('\n').length + 1; // +1 for trailing newline
        let msg = `"${filename}" ${lineCount}L, ${byteCount}B written`;
        // Nvim truncates with < prefix when message exceeds screen width
        if (msg.length > this.cols) {
          msg = '<' + msg.slice(msg.length - this.cols + 1);
        }
        this.engine.commandLine = msg;
      } else {
        this.engine.commandLine = 'E32: No file name';
      }
      return;
    }

    // :wq [filename] or :x[it] – write and quit
    if (/^(wq|x(it?)?)(\s|$)/.test(trimmed)) {
      const parts = trimmed.split(/\s+/);
      const filename = parts[1] || this._vimFilename;
      if (filename) {
        this._saveFile(filename);
      }
      this._exitVim();
      return;
    }

    // :q[uit] – quit (fail if dirty)
    if (/^q(u(it?)?)?$/.test(trimmed)) {
      if (this._isDirty()) {
        // Real nvim shows a multi-line "Press ENTER" prompt with E37 + E162
        const fname = this._vimFilename || '[No Name]';
        const errMsg = `E37: No write since last change\nE162: No write since last change for buffer "${fname}"`;
        this.engine._messagePrompt = { error: errMsg };
        this.engine.commandLine = '';
      } else {
        this._exitVim();
      }
      return;
    }

    // :q[uit]! – force quit
    if (/^q(u(it?)?)?!$/.test(trimmed)) {
      this._exitVim();
      return;
    }

    // :e[dit] [filename] – edit file
    if (/^e(d(it?)?)?(\s|$)/.test(trimmed)) {
      const parts = trimmed.split(/\s+/);
      const filename = parts[1];
      if (filename) {
        this._vimFilename = filename;
        this.engine.filename = filename;  // update for syntax highlighting
        if (this.fs.exists(filename)) {
          this.engine.loadFile(this.fs.read(filename));
        } else {
          this.engine.loadFile('');
        }
        this._savedChangeCount = this.engine._changeCount;
        this._updateVimStatus();
      }
      return;
    }
    // :r[ead]! command — insert shell command output below cursor
    if (/^r(e(ad?)?)?!/.test(trimmed)) {
      const shellCmd = trimmed.replace(/^r(e(ad?)?)?!\s*/, '').trim();
      const lines = this._execShellForOutput(shellCmd);
      if (lines.length > 0) {
        this.engine._saveSnapshot();
        this.engine._redoStack = [];
        const row = this.engine.cursor.row;
        this.engine.buffer.lines.splice(row + 1, 0, ...lines);
        this.engine.cursor.row = row + lines.length;
        this.engine.cursor.col = 0;
        this.engine._updateDesiredCol();
        const n = lines.length;
        this.engine.commandLine = `${n} line${n !== 1 ? 's' : ''} added`;
        this.engine._stickyCommandLine = true;
      }
      return;
    }

    // :r[ead] file — insert file contents below cursor
    if (/^r(e(ad?)?)?(\s|$)/.test(trimmed)) {
      const parts = trimmed.split(/\s+/);
      const filename = parts[1];
      if (filename) {
        const contents = this.fs.read(filename);
        if (contents === null) {
          this.engine.commandLine = `E484: Can't open file ${filename}`;
          this.engine._stickyCommandLine = true;
        } else {
          this.engine._saveSnapshot();
          this.engine._redoStack = [];
          const lines = contents.split('\n');
          const row = this.engine.cursor.row;
          this.engine.buffer.lines.splice(row + 1, 0, ...lines);
          this.engine.cursor.row = row + lines.length;
          this.engine.cursor.col = 0;
          this.engine._updateDesiredCol();
          const n = lines.length;
          this.engine.commandLine = `${n} line${n !== 1 ? 's' : ''} added`;
          this.engine._stickyCommandLine = true;
        }
      } else {
        this.engine.commandLine = 'E32: No file name';
        this.engine._stickyCommandLine = true;
      }
      return;
    }
    // :! command – shell command
    if (trimmed.startsWith('!')) {
      const shellCmd = trimmed.slice(1).trim();
      this._runShellCommand(shellCmd);
      return;
    }
  }

  /** @private – save current vim buffer to VFS */
  _saveFile(filename) {
    const content = this.engine.buffer.lines.join('\n');
    this.fs.write(filename, content);
    this._savedChangeCount = this.engine._changeCount;
  }

  /** @private – check if vim buffer differs from last save */
  _isDirty() {
    if (!this.engine) return false;
    return this.engine._changeCount !== this._savedChangeCount;
  }

  /** @private – exit vim and return to shell */
  _exitVim() {
    this.mode = 'shell';
    this.engine = null;
    this._vimFilename = null;
    this._savedChangeCount = 0;
  }

  /** @private – update vim status line with filename */
  _updateVimStatus() {
    // The engine generates its own status line, but we could
    // override it here if needed. For now, we let it be.
  }

  // ── :! shell command support ──

  /** @private – execute a shell command and return output lines */
  _execShellForOutput(cmd) {
    const lines = [];
    const args = this._tokenize(cmd);
    if (args.length === 0) return lines;

    const command = args[0];
    const rest = args.slice(1);

    switch (command) {
      case 'ls': {
        const files = this.fs.ls();
        if (files.length > 0) lines.push(files.join('  '));
        break;
      }
      case 'cat': {
        for (const name of rest) {
          const contents = this.fs.read(name);
          if (contents === null) {
            lines.push(`cat: ${name}: No such file or directory`);
          } else {
            lines.push(...contents.split('\n'));
          }
        }
        break;
      }
      case 'pwd':
        lines.push(this.shell.cwd);
        break;
      case 'echo':
        lines.push(rest.join(' '));
        break;
      case 'date': {
        const d = new Date();
        const days = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
        const mons = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
        const tzM = d.toString().match(/\(([^)]+)\)/);
        let tz = '';
        if (tzM) tz = tzM[1].includes(' ') ? tzM[1].split(' ').map(w => w[0]).join('') : tzM[1];
        lines.push(`${days[d.getDay()]} ${mons[d.getMonth()]} ${String(d.getDate()).padStart(2,' ')} ${d.toTimeString().split(' ')[0]} ${tz} ${d.getFullYear()}`);
        break;
      }
      case 'rm': {
        for (const name of rest) {
          if (!this.fs.rm(name)) {
            lines.push(`rm: cannot remove '${name}': No such file or directory`);
          }
        }
        break;
      }
      case 'sort': {
        if (rest.length === 0) {
          lines.push('sort: missing file operand');
        } else {
          let reverse = false, numeric = false, unique = false;
          const files = [];
          for (const arg of rest) {
            if (arg.startsWith('-')) {
              for (const ch of arg.slice(1)) {
                if (ch === 'r') reverse = true;
                else if (ch === 'n') numeric = true;
                else if (ch === 'u') unique = true;
              }
            } else files.push(arg);
          }
          for (const name of files) {
            const contents = this.fs.read(name);
            if (contents === null) {
              lines.push(`sort: cannot read: ${name}: No such file or directory`);
            } else {
              let sorted = contents.split('\n');
              if (sorted.length > 0 && sorted[sorted.length - 1] === '') sorted.pop();
              if (numeric) sorted.sort((a, b) => (parseFloat(a) || 0) - (parseFloat(b) || 0));
              else sorted.sort();
              if (reverse) sorted.reverse();
              if (unique) sorted = [...new Set(sorted)];
              lines.push(...sorted);
            }
          }
        }
        break;
      }
      default:
        lines.push(`zsh: command not found: ${command}`);
        break;
    }

    return lines;
  }

  /** @private */
  _runShellCommand(cmd) {
    const lines = this._execShellForOutput(cmd);
    // Show output + "Press ENTER" prompt
    this._shellMsgLines = lines;
    this.mode = 'shell_msg';
  }

  /** @private – render the :! command output screen */
  _renderShellMsg() {
    const t = this.screen.theme;
    const frameLines = [];
    const textRows = this.rows;

    // Fill with output lines, then "Press ENTER..." at the bottom
    const msgLines = [...this._shellMsgLines];
    msgLines.push('');
    msgLines.push('Press ENTER or type command to continue');

    for (let r = 0; r < textRows; r++) {
      if (r < msgLines.length) {
        const text = this._pad(msgLines[r]);
        // "Press ENTER" line gets special color
        const isPrompt = msgLines[r].startsWith('Press ENTER');
        frameLines.push({
          text,
          runs: [{
            n: this.cols,
            fg: isPrompt ? (t.promptFg || '8cf8f7') : (t.normalFg || 'e0e2ea'),
            bg: t.normalBg || '14161b',
          }],
        });
      } else {
        frameLines.push({
          text: ' '.repeat(this.cols),
          runs: [{ n: this.cols, fg: t.normalFg || 'e0e2ea', bg: t.normalBg || '14161b' }],
        });
      }
    }

    return {
      rows: this.rows,
      cols: this.cols,
      cursor: { row: Math.min(msgLines.length - 1, this.rows - 1), col: this.cols - 1, visible: true },
      defaultFg: t.normalFg || 'e0e2ea',
      defaultBg: t.normalBg || '14161b',
      lines: frameLines,
    };
  }

  /** @private */
  _pad(s) {
    if (s.length >= this.cols) return s.slice(0, this.cols);
    return s + ' '.repeat(this.cols - s.length);
  }

  /** @private – same tokenizer as shell */
  _tokenize(input) {
    const tokens = [];
    let current = '';
    let inSingle = false;
    let inDouble = false;
    for (let i = 0; i < input.length; i++) {
      const ch = input[i];
      if (ch === "'" && !inDouble) { inSingle = !inSingle; }
      else if (ch === '"' && !inSingle) { inDouble = !inDouble; }
      else if (ch === ' ' && !inSingle && !inDouble) {
        if (current) { tokens.push(current); current = ''; }
      } else { current += ch; }
    }
    if (current) tokens.push(current);
    return tokens;
  }
}
