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
import { Tmux } from './tmux.js';

/** @typedef {'shell' | 'vim' | 'shell_msg' | 'tmux'} SessionMode */

export class SessionManager {
  /**
   * @param {object} opts
   * @param {number} [opts.rows=20]
   * @param {number} [opts.cols=40]
   * @param {string} [opts.themeName='monokai']
   * @param {boolean} [opts.persist=true] – localStorage persistence
   * @param {function} [opts.onUpdate] – callback(frame) after each key
   */
  constructor({ rows = 20, cols = 40, themeName = 'monokai', persist = true, onUpdate = null } = {}) {
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
      onLaunchTmux: (args) => this._launchTmux(args),
    });
    this.shell._isTopLevel = true;

    // Vim engine (created on demand when vim is launched)
    /** @type {VimEngine|null} */
    this.engine = null;

    // Screen renderer (for vim mode)
    this.screen = new Screen(rows, cols, themeName);
    this._themeName = themeName;

    // Tmux instance (created on demand when tmux is launched)
    /** @type {Tmux|null} */
    this._tmux = null;

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
      if (key === 'Tab' && this._vimCmdTabComplete()) {
        // Tab completion handled
      } else {
        // Clear tab cycle state when leaving command mode
        if (key === 'Escape' || key === 'Enter') {
          this._tabCycleState = null;
        }
        this.engine.feedKey(key);
        this._checkVimCommand();
      }
    } else if (this.mode === 'shell_msg') {
      // Only Enter or : dismisses the message (matches nvim "Press ENTER" behavior)
      if (key === 'Enter' || key === 'Escape') {
        this.mode = 'vim';
      } else if (key === ':') {
        // ':' dismisses and enters command mode (nvim behavior)
        this.mode = 'vim';
        this.engine.feedKey(':');
      }
    } else if (this.mode === 'tmux') {
      this._tmux.feedKey(key);
      // Check if tmux detached or exited
      if (this._tmux.detached) {
        this.mode = 'shell';
        if (this._tmux.exited) {
          // All panes/windows closed — real tmux prints "[exited]"
          this.shell._appendOutput('[exited]');
          // Destroy the tmux instance so next `tmux` creates a fresh one
          this._tmux = null;
        } else {
          // User detached (Ctrl-B d) — session is still alive
          this.shell._appendOutput('[detached (from session ' + this._tmux.activeSession?.name + ')]');
        }
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
    } else if (this.mode === 'tmux') {
      return this._tmux.renderFrame();
    }
  }

  /**
   * Get the display mode label (for UI badges etc.)
   * @returns {string}
   */
  getModeLabel() {
    if (this.mode === 'shell') return 'SHELL';
    if (this.mode === 'shell_msg') return 'SHELL';
    if (this.mode === 'tmux') return 'TMUX';
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

  // ── Tmux lifecycle ──

  /** @private – launch tmux from the shell */
  _launchTmux(args) {
    // If tmux is already running and user typed `tmux attach`, reattach
    if (this._tmux && args.length > 0 && (args[0] === 'attach' || args[0] === 'a')) {
      this._tmux.detached = false;
      this.mode = 'tmux';
      return;
    }

    // `tmux ls` — list sessions without entering tmux
    if (args.length > 0 && (args[0] === 'ls' || args[0] === 'list-sessions')) {
      if (this._tmux) {
        const lines = this._tmux.sessions.map((s, i) =>
          `${s.name}: ${s.windows.length} windows${i === this._tmux._activeSessionIndex ? ' (attached)' : ''}`
        );
        for (const line of lines) this.shell._appendOutput(line);
      } else {
        this.shell._appendOutput('no server running on /tmp/tmux-1000/default');
      }
      return;
    }

    // Create or reuse tmux instance
    if (!this._tmux) {
      const fs = this.fs;
      const themeName = this._themeName;
      this._tmux = new Tmux({
        rows: this.rows,
        cols: this.cols,
        createPaneSession: (cols, rows) => {
          const sm = new SessionManager({
            rows,
            cols,
            themeName,
            persist: false,
          });
          // Share the VFS
          sm.fs = fs;
          sm.shell.fs = fs;
          // Mark as inside tmux (prevents nested tmux)
          sm.shell._insideTmux = true;
          // Pane shells are NOT top-level — allow exit to close the pane
          sm.shell._isTopLevel = false;
          return sm;
        },
      });
    } else {
      // Reattach existing tmux
      this._tmux.detached = false;
    }

    this.mode = 'tmux';
  }

  // ── Vim lifecycle ──

  /** @private – launch vim from the shell */
  _launchVim(filename) {
    this._vimFilename = filename;

    // Create a fresh engine
    this.engine = new VimEngine({ rows: this.rows, cols: this.cols });
    this.engine.filename = filename;  // for syntax highlighting

    // Sync engine text rows with screen layout
    // (vim in tmux uses laststatus=1: no status line, so rows-1 for text)
    if (!this.screen.showStatusLine) {
      this.engine._textRows = this.rows - 1;
    }

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

    // Set the initial file message on the command line (like real vim)
    if (!this.screen.showStatusLine && filename) {
      const isNew = !this.fs.exists(filename);
      if (isNew) {
        this.engine.commandLine = `"${filename}" [New]`;
      } else {
        const lineCount = this.engine.buffer.lineCount;
        const charCount = this.engine.buffer.lines.join('\n').length;
        this.engine.commandLine = `"${filename}" ${lineCount}L, ${charCount}C`;
      }
      this.engine._stickyCommandLine = true;
    }

    this.mode = 'vim';
  }

  /**
   * @private – tab-complete filenames in vim command-line mode.
   * Handles :e, :r, :w, :sav commands.
   * @returns {boolean} true if completion was handled
   */
  _vimCmdTabComplete() {
    if (this.engine.mode !== 'command') return false;
    if (this.engine.commandLine[0] !== ':') return false;

    const input = this.engine._searchInput;
    // Match ex commands that take a filename argument
    const m = input.match(/^(e(?:d(?:it?)?)?|r(?:e(?:ad?)?)?|w(?:r(?:i(?:te?)?)?)?|sav(?:e(?:as?)?)?)(\s+(.*))?$/);
    if (!m) return false;

    const exCmd = m[1];
    const partial = m[3] || '';

    // Check if we're continuing a previous Tab cycle
    const st = this._tabCycleState;
    if (st && st.exCmd === exCmd && st.matches.includes(partial)) {
      // We're cycling — advance to next match
      st.index = (st.index + 1) % st.matches.length;
      const pick = st.matches[st.index];
      this.engine._searchInput = exCmd + ' ' + pick;
      this.engine.commandLine = ':' + exCmd + ' ' + pick;
      return true;
    }

    const files = this.fs.ls().sort();
    const matches = partial ? files.filter(f => f.startsWith(partial)) : files;
    if (matches.length === 0) { this._tabCycleState = null; return true; }

    // Match nvim wildmode=full: first Tab picks first match, subsequent Tabs cycle
    this._tabCycleState = { exCmd, matches, index: 0 };
    const pick = matches[0];
    this.engine._searchInput = exCmd + ' ' + pick;
    this.engine.commandLine = ':' + exCmd + ' ' + pick;
    return true;
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
      const isX = trimmed.startsWith('x');
      const filename = parts[1] || this._vimFilename;
      if (!filename) {
        this.engine.commandLine = 'E32: No file name';
        this.engine._stickyCommandLine = true;
        return;
      }
      // :x only writes if buffer is dirty; :wq always writes
      if (!isX || this._isDirty()) {
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

    // :e[dit]! – force re-edit (reload from VFS, discarding changes)
    if (/^e(d(it?)?)?!(\s|$)/.test(trimmed)) {
      const parts = trimmed.split(/\s+/);
      const filename = parts[1] || this._vimFilename;
      if (filename) {
        this._vimFilename = filename;
        this.engine.filename = filename;
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

    // :e[dit] [filename] – edit file
    if (/^e(d(it?)?)?(\s|$)/.test(trimmed)) {
      const parts = trimmed.split(/\s+/);
      const filename = parts[1] || this._vimFilename;
      if (filename) {
        if (parts[1] && !this._vimFilename) {
          // New file — set as current
          this._vimFilename = filename;
        } else if (parts[1]) {
          this._vimFilename = filename;
        }
        this.engine.filename = filename;  // update for syntax highlighting
        if (this.fs.exists(filename)) {
          this.engine.loadFile(this.fs.read(filename));
        } else {
          this.engine.loadFile('');
        }
        this._savedChangeCount = this.engine._changeCount;
        this._updateVimStatus();
      } else {
        this.engine.commandLine = 'E32: No file name';
        this.engine._stickyCommandLine = true;
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
        this.engine.cursor.row = row + 1;
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
          // Strip trailing empty element from file's final newline
          if (lines.length > 1 && lines[lines.length - 1] === '') lines.pop();
          const row = this.engine.cursor.row;
          this.engine.buffer.lines.splice(row + 1, 0, ...lines);
          // Nvim places cursor on first inserted line
          this.engine.cursor.row = row + 1;
          this.engine.cursor.col = 0;
          this.engine._updateDesiredCol();
          const n = lines.length;
          this.engine.commandLine = `${n} line${n !== 1 ? 's' : ''} added`;
          this.engine._stickyCommandLine = true;
          // Update syntax highlighting to match the read file's type.
          // In real Vim, :r doesn't change filetype, but in the simulator
          // it's more useful to highlight the content that was just loaded.
          this._vimFilename = filename;
          this.engine.filename = filename;
        }
      } else {
        this.engine.commandLine = 'E32: No file name';
        this.engine._stickyCommandLine = true;
      }
      return;
    }
    // :{range}!cmd — filter lines through shell command
    // This handles both:
    //   1. Commands from !{motion} operator (engine sets _filterRange + '!cmd')
    //   2. Direct ex commands like :%!sort, :1,5!sort, :.!cmd
    {
      let filterSr = null, filterEr = null, shellCmd = null;

      if (this.engine._filterRange) {
        // From !{motion} operator — range already computed
        const { sr, er } = this.engine._filterRange;
        this.engine._filterRange = null;
        filterSr = sr;
        filterEr = er;
        // The command string is the pre-filled range+!cmd, extract just the shell command
        const bangIdx = trimmed.indexOf('!');
        if (bangIdx >= 0) shellCmd = trimmed.slice(bangIdx + 1).trim();
        else if (trimmed.startsWith('!')) shellCmd = trimmed.slice(1).trim();
      } else {
        // Parse range from the command string using engine's parser
        const parsed = this.engine._parseExRange(trimmed);
        if (parsed.hasRange && parsed.rest.startsWith('!')) {
          filterSr = parsed.sr;
          filterEr = parsed.er;
          shellCmd = parsed.rest.slice(1).trim();
        }
      }

      if (filterSr !== null && filterEr !== null && shellCmd) {
        const inputLines = [];
        for (let r = filterSr; r <= filterEr; r++) {
          inputLines.push(this.engine.buffer.lines[r]);
        }
        const stdin = inputLines.join('\n');
        const output = this._execShellForOutput(shellCmd, stdin);
        // Replace lines with output
        this.engine._saveSnapshot();
        this.engine._redoStack = [];
        this.engine.buffer.lines.splice(filterSr, filterEr - filterSr + 1, ...output);
        if (this.engine.buffer.lines.length === 0) this.engine.buffer.lines.push('');
        // Position cursor at first filtered line, first non-blank
        this.engine.cursor.row = Math.min(filterSr, this.engine.buffer.lineCount - 1);
        this.engine.cursor.col = this.engine._firstNonBlank(this.engine.cursor.row);
        this.engine._clampCursor();
        this.engine._updateDesiredCol();
        const nOld = filterEr - filterSr + 1;
        const nNew = output.length;
        if (nNew !== nOld) {
          this.engine.commandLine = `${nNew} fewer line${nNew !== 1 ? 's' : ''}; ${nOld} line${nOld !== 1 ? 's' : ''} filtered`;
        } else {
          this.engine.commandLine = `${nNew} line${nNew !== 1 ? 's' : ''} filtered`;
        }
        this.engine._stickyCommandLine = true;
        return;
      }
    }
    // :! command – shell command
    if (trimmed.startsWith('!')) {
      const shellCmd = trimmed.slice(1).trim();
      this._runShellCommand(shellCmd);
      return;
    }

    // :sav[eas] filename – save as new filename
    if (/^sav(e(as?)?)?(\ |$)/.test(trimmed)) {
      const parts = trimmed.split(/\s+/);
      const filename = parts[1];
      if (filename) {
        this._saveFile(filename);
        this._vimFilename = filename;
        this.engine.filename = filename;
        this._updateVimStatus();
        const lineCount = this.engine.buffer.lineCount;
        const byteCount = this.engine.buffer.lines.join('\n').length + 1;
        let msg = `"${filename}" ${lineCount}L, ${byteCount}B written`;
        if (msg.length > this.cols) {
          msg = '<' + msg.slice(msg.length - this.cols + 1);
        }
        this.engine.commandLine = msg;
      } else {
        this.engine.commandLine = 'E32: No file name';
        this.engine._stickyCommandLine = true;
      }
      return;
    }

    // :N – jump to line number
    if (/^\d+$/.test(trimmed)) {
      const lineNum = parseInt(trimmed, 10);
      const maxLine = this.engine.buffer.lineCount - 1;
      this.engine.cursor.row = Math.max(0, Math.min(lineNum - 1, maxLine));
      this.engine.cursor.col = 0;
      this.engine._updateDesiredCol();
      this.engine._ensureCursorVisible();
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

  /**
   * Resize the terminal grid.  Propagates to shell, screen, engine, and tmux.
   * @param {number} rows
   * @param {number} cols
   */
  resize(rows, cols) {
    if (rows === this.rows && cols === this.cols) return;
    this.rows = rows;
    this.cols = cols;
    this.shell.rows = rows;
    this.shell.cols = cols;
    this.shell._textRows = rows - 1;
    this.screen.rows = rows;
    this.screen.cols = cols;
    if (this.engine) {
      this.engine.rows = rows;
      this.engine.cols = cols;
      this.engine._textRows = rows - (this.screen.showStatusLine ? 2 : 1);
      // Re-clamp scroll / cursor
      this.engine._ensureCursorVisible();
    }
    if (this._tmux) {
      this._tmux.rows = rows;
      this._tmux.cols = cols;
      this._tmux._paneRows = rows - 1;
      // Resize all windows + panes
      for (const sess of this._tmux.sessions) {
        sess.rows = rows;
        sess.cols = cols;
        for (const win of sess.windows) {
          win.rows = rows;
          win.cols = cols;
          win.layout.computeLayout(0, 0, cols, rows);
        }
      }
    }
  }

  /** @private – update vim status line with filename */
  _updateVimStatus() {
    // The engine generates its own status line, but we could
    // override it here if needed. For now, we let it be.
  }

  // ── :! shell command support ──

  /** @private – execute a shell command and return output lines */
  _execShellForOutput(cmd, stdin = null) {
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
        if (rest.length === 0 && stdin !== null) {
          // cat with stdin: pass through
          lines.push(...stdin.split('\n'));
        } else {
          for (const name of rest) {
            const contents = this.fs.read(name);
            if (contents === null) {
              lines.push(`cat: ${name}: No such file or directory`);
            } else {
              lines.push(...contents.split('\n'));
            }
          }
        }
        break;
      }

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
      case 'touch': {
        for (const name of rest) {
          if (!this.fs.exists(name)) {
            this.fs.write(name, '');
          }
        }
        break;
      }
      case 'cp': {
        if (rest.length < 2) {
          lines.push('cp: missing file operand');
        } else {
          const contents = this.fs.read(rest[0]);
          if (contents === null) {
            lines.push(`cp: cannot stat '${rest[0]}': No such file or directory`);
          } else {
            this.fs.write(rest[1], contents);
          }
        }
        break;
      }
      case 'mv': {
        if (rest.length < 2) {
          lines.push('mv: missing file operand');
        } else {
          const contents = this.fs.read(rest[0]);
          if (contents === null) {
            lines.push(`mv: cannot stat '${rest[0]}': No such file or directory`);
          } else {
            this.fs.write(rest[1], contents);
            this.fs.rm(rest[0]);
          }
        }
        break;
      }
      case 'wc': {
        const flags = [];
        const files = [];
        for (const arg of rest) {
          if (arg.startsWith('-') && arg.length > 1) {
            for (const ch of arg.slice(1)) flags.push(ch);
          } else files.push(arg);
        }
        if (files.length === 0) {
          lines.push('wc: missing file operand');
        } else {
          const showAll = flags.length === 0;
          const showLines = showAll || flags.includes('l');
          const showWords = showAll || flags.includes('w');
          const showBytes = showAll || flags.includes('c');
          for (const name of files) {
            const contents = this.fs.read(name);
            if (contents === null) {
              lines.push(`wc: ${name}: No such file or directory`);
            } else {
              const l = contents === '' ? 0 : contents.split('\n').length;
              const w = contents === '' ? 0 : contents.split(/\s+/).filter(s => s).length;
              const b = contents.length;
              const parts = [];
              if (showLines) parts.push(String(l).padStart(8));
              if (showWords) parts.push(String(w).padStart(8));
              if (showBytes) parts.push(String(b).padStart(8));
              parts.push(` ${name}`);
              lines.push(parts.join(''));
            }
          }
        }
        break;
      }


      case 'grep': {
        let ignoreCase = false, showNums = false, countOnly = false;
        const positional = [];
        for (const arg of rest) {
          if (arg.startsWith('-') && arg.length > 1) {
            for (const ch of arg.slice(1)) {
              if (ch === 'i') ignoreCase = true;
              else if (ch === 'n') showNums = true;
              else if (ch === 'c') countOnly = true;
            }
          } else positional.push(arg);
        }
        if (positional.length < 1) {
          lines.push('Usage: grep [options] pattern file');
        } else if (positional.length === 1 && stdin !== null) {
          // grep pattern from stdin
          let re;
          try { re = new RegExp(positional[0], ignoreCase ? 'i' : ''); }
          catch (e) { lines.push(`grep: invalid regex: ${positional[0]}`); break; }
          const flines = stdin.split('\n');
          let count = 0;
          for (let i = 0; i < flines.length; i++) {
            if (re.test(flines[i])) {
              count++;
              if (!countOnly) {
                const ln = showNums ? `${i + 1}:` : '';
                lines.push(`${ln}${flines[i]}`);
              }
            }
          }
          if (countOnly) lines.push(`${count}`);
        } else if (positional.length < 2) {
          lines.push('Usage: grep [options] pattern file');
        } else {
          let re;
          try { re = new RegExp(positional[0], ignoreCase ? 'i' : ''); }
          catch (e) { lines.push(`grep: invalid regex: ${positional[0]}`); break; }
          const gfiles = positional.slice(1);
          for (const name of gfiles) {
            const contents = this.fs.read(name);
            if (contents === null) {
              lines.push(`grep: ${name}: No such file or directory`);
            } else {
              const flines = contents.split('\n');
              let count = 0;
              const prefix = gfiles.length > 1 ? `${name}:` : '';
              for (let i = 0; i < flines.length; i++) {
                if (re.test(flines[i])) {
                  count++;
                  if (!countOnly) {
                    const ln = showNums ? `${i + 1}:` : '';
                    lines.push(`${prefix}${ln}${flines[i]}`);
                  }
                }
              }
              if (countOnly) lines.push(`${prefix}${count}`);
            }
          }
        }
        break;
      }

      case 'history': {
        const hist = this.shell._history;
        for (let i = 0; i < hist.length; i++) {
          lines.push(`${String(i + 1).padStart(5)}  ${hist[i]}`);
        }
        break;
      }
      case 'sort': {
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
        if (files.length === 0 && stdin !== null) {
          // sort from stdin
          let sorted = stdin.split('\n');
          if (sorted.length > 0 && sorted[sorted.length - 1] === '') sorted.pop();
          if (numeric) sorted.sort((a, b) => (parseFloat(a) || 0) - (parseFloat(b) || 0));
          else sorted.sort();
          if (reverse) sorted.reverse();
          if (unique) sorted = [...new Set(sorted)];
          lines.push(...sorted);
        } else if (files.length === 0) {
          lines.push('sort: missing file operand');
        } else {
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

      case 'uniq': {
        // Remove consecutive duplicate lines
        let inputLines;
        if (rest.length === 0 && stdin !== null) {
          inputLines = stdin.split('\n');
        } else if (rest.length > 0) {
          const contents = this.fs.read(rest[0]);
          if (contents === null) {
            lines.push(`uniq: ${rest[0]}: No such file or directory`);
            break;
          }
          inputLines = contents.split('\n');
        } else {
          lines.push('uniq: missing operand');
          break;
        }
        if (inputLines.length > 0 && inputLines[inputLines.length - 1] === '') inputLines.pop();
        const result = [];
        for (let i = 0; i < inputLines.length; i++) {
          if (i === 0 || inputLines[i] !== inputLines[i - 1]) {
            result.push(inputLines[i]);
          }
        }
        lines.push(...result);
        break;
      }

      case 'tr': {
        // tr 'set1' 'set2' — translate characters
        if (rest.length < 2) {
          lines.push('tr: missing operand');
        } else {
          const set1 = this._expandTrSet(rest[0]);
          const set2 = this._expandTrSet(rest[1]);
          const input = stdin !== null ? stdin : '';
          let output = '';
          for (const ch of input) {
            const idx = set1.indexOf(ch);
            if (idx >= 0 && idx < set2.length) {
              output += set2[idx];
            } else if (idx >= 0) {
              output += set2[set2.length - 1] || ch;
            } else {
              output += ch;
            }
          }
          lines.push(...output.split('\n'));
        }
        break;
      }

      case 'rev': {
        // Reverse each line
        let inputLines;
        if (rest.length === 0 && stdin !== null) {
          inputLines = stdin.split('\n');
        } else if (rest.length > 0) {
          const contents = this.fs.read(rest[0]);
          if (contents === null) {
            lines.push(`rev: ${rest[0]}: No such file or directory`);
            break;
          }
          inputLines = contents.split('\n');
        } else {
          inputLines = [];
        }
        for (const line of inputLines) {
          lines.push(line.split('').reverse().join(''));
        }
        break;
      }

      case 'tac': {
        // Reverse line order
        let inputLines;
        if (rest.length === 0 && stdin !== null) {
          inputLines = stdin.split('\n');
        } else if (rest.length > 0) {
          const contents = this.fs.read(rest[0]);
          if (contents === null) {
            lines.push(`tac: ${rest[0]}: No such file or directory`);
            break;
          }
          inputLines = contents.split('\n');
        } else {
          inputLines = [];
        }
        if (inputLines.length > 0 && inputLines[inputLines.length - 1] === '') inputLines.pop();
        lines.push(...inputLines.reverse());
        break;
      }

      case 'head': {
        // head -n N — first N lines (default 10)
        let n = 10;
        const files = [];
        for (let i = 0; i < rest.length; i++) {
          if (rest[i] === '-n' && i + 1 < rest.length) {
            n = parseInt(rest[i + 1], 10) || 10;
            i++;
          } else if (rest[i].startsWith('-') && rest[i] !== '-') {
            // -N shorthand
            const num = parseInt(rest[i].slice(1), 10);
            if (!isNaN(num)) n = num;
          } else {
            files.push(rest[i]);
          }
        }
        let inputLines;
        if (files.length === 0 && stdin !== null) {
          inputLines = stdin.split('\n');
        } else if (files.length > 0) {
          const contents = this.fs.read(files[0]);
          if (contents === null) {
            lines.push(`head: ${files[0]}: No such file or directory`);
            break;
          }
          inputLines = contents.split('\n');
        } else {
          break;
        }
        lines.push(...inputLines.slice(0, n));
        break;
      }

      case 'tail': {
        // tail -n N — last N lines (default 10)
        let n = 10;
        const files = [];
        for (let i = 0; i < rest.length; i++) {
          if (rest[i] === '-n' && i + 1 < rest.length) {
            n = parseInt(rest[i + 1], 10) || 10;
            i++;
          } else if (rest[i].startsWith('-') && rest[i] !== '-') {
            const num = parseInt(rest[i].slice(1), 10);
            if (!isNaN(num)) n = num;
          } else {
            files.push(rest[i]);
          }
        }
        let inputLines;
        if (files.length === 0 && stdin !== null) {
          inputLines = stdin.split('\n');
        } else if (files.length > 0) {
          const contents = this.fs.read(files[0]);
          if (contents === null) {
            lines.push(`tail: ${files[0]}: No such file or directory`);
            break;
          }
          inputLines = contents.split('\n');
        } else {
          break;
        }
        if (inputLines.length > 0 && inputLines[inputLines.length - 1] === '') inputLines.pop();
        lines.push(...inputLines.slice(-n));
        break;
      }

      case 'sed': {
        // Basic sed 's/pat/rep/[flags]' support
        let inputLines;
        // Collect flags and positional args
        const sedFlags = [];
        const sedPositional = [];
        for (const arg of rest) {
          if (arg.startsWith('-') && arg.length > 1) {
            sedFlags.push(arg);
          } else {
            sedPositional.push(arg);
          }
        }
        const sedExpr = sedPositional[0] || '';
        const sedFiles = sedPositional.slice(1);
        if (sedFiles.length === 0 && stdin !== null) {
          inputLines = stdin.split('\n');
        } else if (sedFiles.length > 0) {
          const contents = this.fs.read(sedFiles[0]);
          if (contents === null) {
            lines.push(`sed: ${sedFiles[0]}: No such file or directory`);
            break;
          }
          inputLines = contents.split('\n');
        } else {
          inputLines = [];
        }
        // Parse s/pat/rep/flags
        const sedMatch = sedExpr.match(/^s(.)(.+?)\1(.*?)\1([gi]*)$/);
        if (sedMatch) {
          const [, , pat, rep, flags] = sedMatch;
          const isGlobal = flags.includes('g');
          const isIcase = flags.includes('i');
          let re;
          try {
            re = new RegExp(pat, (isGlobal ? 'g' : '') + (isIcase ? 'i' : ''));
          } catch (e) {
            lines.push(`sed: invalid regex: ${pat}`);
            break;
          }
          for (const line of inputLines) {
            lines.push(line.replace(re, rep));
          }
        } else {
          // Unsupported sed expression — pass through
          lines.push(...inputLines);
        }
        break;
      }

      default:
        lines.push(`zsh: command not found: ${command}`);
        break;
    }

    return lines;
  }

  /** @private – expand tr character set ranges like a-z */
  _expandTrSet(s) {
    let result = '';
    for (let i = 0; i < s.length; i++) {
      if (i + 2 < s.length && s[i + 1] === '-') {
        const start = s.charCodeAt(i);
        const end = s.charCodeAt(i + 2);
        for (let c = start; c <= end; c++) {
          result += String.fromCharCode(c);
        }
        i += 2;
      } else {
        result += s[i];
      }
    }
    return result;
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
