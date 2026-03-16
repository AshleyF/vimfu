/**
 * VimFu Simulator – VimEngine
 *
 * Core model: buffer + cursor + mode + command dispatch.
 * Pure logic — no DOM, no rendering. Fully testable via Node.
 *
 * Comprehensive feature set covering curriculum lessons 1-85+:
 *   Normal: h j k l  w W b B e E ge gE  0 ^ $  gg G
 *           f F t T ; ,  % { } ( )  H M L
 *           x X Delete  s  r  ~  J gJ  dd D  cc C S
 *           dw d$ d{motion}  cw c$ c{motion}
 *           yy Y  yw y$ y{motion}  p P
 *           >> <<  >{motion} <{motion}
 *           . (dot)  u (undo)  Ctrl-R (redo)
 *           / ? n N * #  (search)
 *           v V (visual)  counts  text objects
 *           Ctrl-A (increment)  Ctrl-X (decrement)
 *           Ctrl-G (file info)  ga (ASCII value)
 *           Ctrl-O / Ctrl-I (jump list)
 *           g; / g, (change list)  gd (local declaration)
 *           Q (replay last macro)
 *   Insert: printable, Enter, Backspace, Escape, Ctrl-H, Ctrl-J,
 *           Ctrl-W (word delete), Ctrl-U (line delete),
 *           Delete, Arrow keys, Ctrl-R (register paste)
 *   Replace: R (overtype)
 *   Command: :w :q :wq :q! :42  :set number/relativenumber
 */

import { Buffer } from './buffer.js';
import { DICTIONARY } from './dictionary.js';

/** @enum {string} */
export const Mode = {
  NORMAL: 'normal',
  INSERT: 'insert',
  VISUAL: 'visual',
  VISUAL_LINE: 'visual_line',
  VISUAL_BLOCK: 'visual_block',
  REPLACE: 'replace',
  COMMAND: 'command',
};

export class VimEngine {
  constructor({ rows = 20, cols = 40, lines = [''] } = {}) {
    this.rows = rows;
    this.cols = cols;
    this.buffer = new Buffer(lines);
    this.cursor = { row: 0, col: 0 };
    this.mode = Mode.NORMAL;
    this.scrollTop = 0;
    this.scrollLeft = 0; // horizontal scroll offset (buffer column of left edge)
    this.statusLine = '';
    this.commandLine = '';
    this.filename = null;   // set by SessionManager for syntax highlighting
    this._textRows = rows - 2;

    // Fold state
    this._folds = [];  // Array of { startRow, endRow, closed: true/false }

    // Window management (splits)
    this._windows = [];
    this._activeWin = 0;

    // Pending state
    this._pendingCtrlW = false;
    this._pendingCount = '';
    this._pendingOp = '';
    this._pendingG = false;
    this._pendingZ = false;
    this._pendingZu = false;
    this._pendingCapZ = false;
    this._pendingF = '';
    this._pendingR = false;
    this._pendingM = false;
    this._pendingQ = false;
    this._pendingAt = false;
    this._pendingQuote = false;
    this._pendingBacktick = false;
    this._pendingTextObjType = null;
    this._pendingBracket = '';
    this._opStartPos = null;
    this._motionInclusive = false;
    this._motionLinewise = false;
    this._motionExclusive = false;
    this._insertCount = 1;
    this._insertOneShot = false; // Ctrl-O: execute one normal command, then return to insert
    this._scrollHalf = 0; // sticky scroll amount for Ctrl-D/Ctrl-U

    // Operator saved across async-like sequences (e.g. d/pattern<CR>)
    this._pendingOpForSearch = '';
    this._opStartPosForSearch = null;

    // Registers
    this._unnamedReg = '';
    this._regType = 'char'; // 'char' or 'line'
    this._namedRegs = {};   // {a-z, +, *}: { text, type }
    this._numberedRegs = new Array(10).fill(null); // "0-"9: {text, type} or null
    this._smallDeleteReg = null; // "-: {text, type} for deletes < 1 line
    this._pendingRegKey = ''; // pending " register prefix
    this._pendingCtrlR = false; // pending Ctrl-R in insert mode
    this._cmdPendingCtrlR = false; // pending Ctrl-R in command mode
    this._lastMessage = ''; // last displayed message (for g<)
    /** @type {((text: string) => void) | null} */
    this._onClipboardWrite = null; // callback when + or * register is written

    // File name (for "% register in :di)
    this._fileName = null;

    // Search
    this._searchPattern = '';
    this._searchForward = true;
    this._searchInput = '';
    this._showCurSearch = false; // true only after user-initiated search navigation
    this._curSearchPos = null; // {row, col} of the match for CurSearch highlight
    this._hlsearchActive = true; // false after :noh, true again on next search

    // Message prompt ("Press ENTER or type command to continue")
    this._messagePrompt = null; // null or { error: 'E486: ...' }

    // Sticky command line: preserves error/info messages for one frame
    this._stickyCommandLine = false;
    this._commandLineLineNrLen = 0; // for :nu/:# line number coloring

    // Last insert position (for gi)
    this._lastInsertPos = null;

    // Last inserted text (for ". register)
    this._lastInsertedText = '';

    // Line undo save (for U command)
    this._lineUndoSave = null;

    // Find on line
    this._lastFind = null;

    // Visual mode
    this._visualStart = { row: 0, col: 0 };
    this._visualExclusive = false; // true when last visual motion was exclusive (e.g. ), ()
    this._visualBlockDollar = false; // true when $ was pressed in visual_block mode
    this._blockInsertState = null; // {mode, topRow, bottomRow, leftCol, rightCol, dollar, editRow, insertCol, origLine}
    this._lastVisual = null; // {mode, start: {row, col}, end: {row, col}} for gv

    // Dot repeat
    this._lastChange = null;
    this._recording = false;
    this._recordedKeys = [];
    this._dotPrefix = []; // keys to prepend to recorded keys for dot repeat

    // Undo / Redo
    this._undoStack = [];
    this._redoStack = [];
    this._changeCount = 0; // tracks undo-position for dirty detection
    this._changeList = [];
    this._changeListPos = -1;
    this._saveSnapshot();
    this._changeCount = 0; // reset after initial snapshot

    // Marks
    this._marks = {};

    // Macros
    this._macroRegisters = {};     // {a-z}: array of key strings
    this._macroRecording = '';     // '' = not recording, else register letter
    this._macroKeys = [];          // keys captured during recording
    this._lastMacroRegister = '';  // for @@ (replay last played)
    this._lastRecordedRegister = '';  // for Q (replay last recorded)
    this._macroPlaying = false;    // true while replaying a macro
    this._macroAborted = false;     // set true when motion fails during macro

    // Jump list (for Ctrl-O / Ctrl-I)
    this._jumpList = [];
    this._jumpListPos = -1;
    this._lastJumpPos = null; // for '' / `` marks (position before last jump)

    // Ex command hook — set by _executeCommand when it processes :w/:q etc.
    // SessionManager reads and clears this after each feedKey.
    this._lastExCommand = null;

    // Echo message (persists across feedKeys until mode change)
    this._echoMessage = null;

    // Visual command range — set when : is pressed in visual mode
    this._visualCmdRange = null;

    // Surround (nvim-surround plugin)
    this._pendingSurround = '';      // 'ds', 'cs', 'ys', or ''
    this._surroundTarget = '';       // for cs: the target char (first char after cs)
    this._ysRange = null;            // for ys: {sr, sc, er, ec} waiting for surround char
    this._pendingVisualSurround = null; // for visual S: {sr, sc, er, ec, wasLinewise}
    this._pendingTagInput = null;    // tag input mode: { buffer, context, ...data }

    // Desired column for vertical movement
    this._desiredCol = 0;

    // Command-line history
    this._cmdHistory = [];
    this._cmdHistoryPos = -1;

    // Command-line Tab completion state
    this._cmdCompletions = [];     // current list of matching completions
    this._cmdCompletionIdx = -1;   // index into _cmdCompletions (-1 = not cycling)
    this._cmdCompletionBase = '';  // the original prefix before first Tab

    // Settings (:set)
    this._settings = {
      number: false,       // :set number / :set nonumber
      relativenumber: false, // :set relativenumber / :set norelativenumber
      ignorecase: false,   // :set ignorecase / :set noignorecase (ic/noic)
      smartcase: false,    // :set smartcase / :set nosmartcase (scs/noscs)
      scrolloff: 0,        // :set scrolloff=N (so)
      expandtab: false,    // :set expandtab / :set noexpandtab (et/noet)
      tabstop: 8,          // :set tabstop=N (ts)
      shiftwidth: 8,       // :set shiftwidth=N (sw)
      autoindent: true,   // :set autoindent / :set noautoindent (ai/noai) — nvim default is on
      cursorline: false,   // :set cursorline / :set nocursorline (cul/nocul)
      hlsearch: true,      // :set hlsearch / :set nohlsearch (hls/nohls)
      fileformat: 'dos',   // :set fileformat=dos/unix (ff)
      wrap: true,          // :set wrap / :set nowrap
      incsearch: false,    // :set incsearch / :set noincsearch (is/nois)
      list: false,         // :set list / :set nolist
      splitbelow: false,   // :set splitbelow / :set nosplitbelow (sb/nosb)
      splitright: false,   // :set splitright / :set nosplitright (spr/nospr)
      spell: false,        // :set spell / :set nospell
    };

    // Spell checking
    this._spellGoodWords = new Set(); // words added with zg
    this._spellBadWords = new Set();  // words marked bad with zw

    this._updateStatus();

    // Initialize default window (must be after all other state init)
    this._windows = [{
      buffer: this.buffer,
      cursor: { ...this.cursor },
      scrollTop: this.scrollTop,
      scrollLeft: this.scrollLeft,
      folds: this._folds,
      _desiredCol: 0,
    }];
    this._activeWin = 0;

    // ── Buffer list ──
    this._nextBufId = 1;
    this._bufferList = []; // {id, buffer, fileName, cursor, scrollTop, scrollLeft, undoStack, redoStack, changeCount, marks, folds, desiredCol, jumpList, jumpListPos, changeList, changeListPos}
    this._currentBufId = this._registerBuffer(this.buffer, this._fileName);
    this._alternateBufId = null;

    // ── Tab pages ──
    this._tabs = [{ windows: this._windows, activeWin: this._activeWin }];
    this._activeTab = 0;
  }

  // ── Public API ──

  loadFile(text, fileName) {
    // Register in buffer list (save old state BEFORE replacing this.buffer)
    if (this._bufferList && this._currentBufId != null) {
      this._saveCurrentBufState();
      this._alternateBufId = this._currentBufId;
    }
    const lines = text.split('\n');
    this._fileName = fileName || null;
    if (lines.length > 1 && lines[lines.length - 1] === '') lines.pop();
    this.buffer = new Buffer(lines);
    // Neovim opens files with cursor at the first non-blank character
    const fnb = this._firstNonBlank(0);
    this.cursor = { row: 0, col: fnb };
    // Set desiredCol to the virtual column of the first non-blank
    this._desiredCol = this._virtColAt(0, fnb);
    this.scrollTop = 0;
    this.scrollLeft = 0;
    this._undoStack = [];
    this._redoStack = [];
    this._changeCount = 0;
    this._lineUndoSave = null;  // reset for new file
    this._jumpList = [];
    this._jumpListPos = -1;
    // Nvim records the file-open cursor position as the initial jumplist entry
    this._jumpList.push({ row: 0, col: fnb });
    this._jumpListPos = 1; // points past the initial entry (current position)
    this._changeList = [];
    this._changeListPos = -1;
    this._marks = {};
    this._folds = [];
    this._saveSnapshot();
    this._changeCount = 0; // reset after initial snapshot
    // Clear change list — loading a file is not a "change"
    this._changeList = [];
    this._changeListPos = -1;
    // Register new buffer or reuse existing
    if (this._bufferList) {
      // Check if we already have a buffer for this fileName
      let existingEntry = null;
      if (fileName) {
        existingEntry = this._bufferList.find(e => e.fileName === fileName);
      }
      if (existingEntry) {
        // Re-use existing entry (reload content)
        existingEntry.buffer = this.buffer;
        existingEntry.cursor = { ...this.cursor };
        existingEntry.scrollTop = 0;
        existingEntry.scrollLeft = 0;
        existingEntry.undoStack = this._undoStack;
        existingEntry.redoStack = this._redoStack;
        existingEntry.changeCount = 0;
        existingEntry.marks = {};
        existingEntry.folds = [];
        this._currentBufId = existingEntry.id;
      } else {
        this._currentBufId = this._registerBuffer(this.buffer, fileName);
      }
    }
    this._updateStatus();
  }

  /** First non-blank column of a string (static helper, no buffer dependency) */
  _firstNonBlankOfLine(line) {
    const m = line.match(/\S/);
    return m ? m.index : 0;
  }

  feedKey(key) {
    // Ctrl-[ is the terminal equivalent of Escape
    if (key === 'Ctrl-[') key = 'Escape';

    // If in message prompt mode, any key dismisses it
    if (this._messagePrompt) {
      this._messagePrompt = null;
      this.commandLine = '';
      this._updateStatus();
      return;
    }

    // Clear sticky command line from previous feedKey
    if (this._stickyCommandLine) {
      this._stickyCommandLine = false;
      this._commandLineLineNrLen = 0;
      this._errorCmdLineCursor = false;
      this.commandLine = '';
    }

    // Capture keys into macro register (but not keys generated by macro playback)
    if (this._macroRecording && !this._macroPlaying) {
      this._macroKeys.push(key);
    }

    if (this.mode === Mode.COMMAND) this._commandKey(key);
    else if (this.mode === Mode.NORMAL) {
      this._normalKey(key);
      // Ctrl-O one-shot: return to insert mode after one normal command
      if (this._insertOneShot) {
        if (this.mode !== Mode.NORMAL) {
          // Command switched to another mode (insert, visual, etc.) — cancel one-shot
          this._insertOneShot = false;
        } else if (!this._pendingOp && !this._pendingG && !this._pendingZ && !this._pendingCapZ
            && !this._pendingF && !this._pendingR && !this._pendingM && !this._pendingQ
            && !this._pendingAt && !this._pendingQuote && !this._pendingBacktick
            && !this._pendingDblQuote && !this._pendingSurround && !this._ysRange
            && !this._pendingCount && !this._pendingTextObjType && !this._pendingCtrlW) {
          // Normal command completed with no pending state — return to insert
          this._insertOneShot = false;
          this.mode = Mode.INSERT;
          this.commandLine = '-- INSERT --';
        }
        // else: still pending (e.g. operator-pending like d waiting for motion) — stay in normal
      }
    }
    else if (this.mode === Mode.INSERT) this._insertKey(key);
    else if (this.mode === Mode.VISUAL || this.mode === Mode.VISUAL_LINE || this.mode === Mode.VISUAL_BLOCK) this._visualKey(key);
    else if (this.mode === Mode.REPLACE) this._replaceKey(key);
    // Clear line undo save when cursor moves to a different row
    if (this._lineUndoSave && this._lineUndoSave.row !== this.cursor.row) {
      this._lineUndoSave = null;
    }
    // Clear echo message when mode changes or new messages appear
    if (this._echoMessage != null) {
      if (this._stickyCommandLine || this._messagePrompt || this.mode !== Mode.NORMAL) {
        this._echoMessage = null;
      }
    }
    // If cursor landed inside a closed fold, snap to fold start
    this._adjustCursorForFolds();
    this._clampCursor();
    this._ensureCursorVisible();
    this._adjustHorizontalScroll();
    this._updateStatus();
  }

  // ── Snapshot / Undo / Redo ──

  _saveSnapshot(cursorOverride) {
    // During macro playback, suppress intermediate snapshots
    // (the single pre-playback snapshot handles undo for the whole macro)
    if (this._macroPlaying) return;
    this._changeCount++;
    // Track original line content for U (undo line)
    if (this._lineUndoSave === null || this._lineUndoSave.row !== this.cursor.row) {
      this._lineUndoSave = { row: this.cursor.row, text: this.buffer.lines[this.cursor.row] };
    }
    // Record position in change list
    this._changeList.push({ row: this.cursor.row, col: this.cursor.col });
    if (this._changeList.length > 100) this._changeList.shift();
    this._changeListPos = this._changeList.length;
    this._undoStack.push({
      lines: [...this.buffer.lines],
      cursor: cursorOverride ? { ...cursorOverride } : { ...this.cursor },
      scrollTop: this.scrollTop,
    });
    if (this._undoStack.length > 100) this._undoStack.shift();
  }

  _undo() {
    if (this._undoStack.length <= 1) return;
    this._changeCount--;
    // Pop the most recent pre-change snapshot
    const snap = this._undoStack.pop();
    // Push current state to redo stack.
    // redoCursor: the original pre-change cursor (from the undo snapshot).
    // In Vim, redo positions cursor at the start of the change.
    // undoCursor: also the original pre-change cursor, so that if redo
    // pushes back to undo, the cursor is correct for a subsequent undo.
    const redoEntry = {
      lines: [...this.buffer.lines],
      cursor: { ...this.cursor },
      scrollTop: this.scrollTop,
      redoCursor: snap.redoCursor || { ...snap.cursor },
      undoCursor: { ...snap.cursor },
    };
    this._redoStack.push(redoEntry);
    // Restore pre-change state
    this.buffer = new Buffer([...snap.lines]);
    this.cursor = { ...snap.cursor };
    this.scrollTop = snap.scrollTop;
  }

  _redo() {
    if (this._redoStack.length === 0) return;
    this._changeCount++;
    const snap = this._redoStack.pop();
    const redoCursor = { ...snap.redoCursor };
    // Push current state back onto undo stack.
    // Use undoCursor (the original pre-change cursor) if available.
    this._undoStack.push({
      lines: [...this.buffer.lines],
      cursor: snap.undoCursor ? { ...snap.undoCursor } : { ...this.cursor },
      scrollTop: this.scrollTop,
      redoCursor: { ...snap.redoCursor },
    });
    // Restore buffer content from redo entry.
    this.buffer = new Buffer([...snap.lines]);
    this.scrollTop = snap.scrollTop;
    // Use the computed redo cursor position
    this.cursor = redoCursor;
    // Clamp cursor to valid position in the new buffer
    this.cursor.row = Math.min(this.cursor.row, this.buffer.lineCount - 1);
    this.cursor.col = Math.min(this.cursor.col, Math.max(0, this.buffer.lineLength(this.cursor.row) - 1));
  }

  _saveForDot(key) {
    if (this._recording) this._recordedKeys.push(key);
  }

  _startRecording() {
    this._recording = true;
    this._recordedKeys = [];
  }

  _stopRecording() {
    if (this._recording) {
      this._recording = false;
      this._lastChange = [...this._dotPrefix, ...this._recordedKeys];
      this._dotPrefix = [];
    }
  }

  // ── Count helpers ──

  _getCount(defaultVal = 1) {
    const n = this._pendingCount ? parseInt(this._pendingCount, 10) : defaultVal;
    this._pendingCount = '';
    return n;
  }

  _hasCount() { return this._pendingCount !== ''; }

  /**
   * Save text to registers after a delete, change, or yank.
   * @param {string} text
   * @param {'char'|'line'} type
   * @param {'delete'|'yank'} [op='delete'] – whether this is a delete/change or a yank
   */
  _setReg(text, type, op = 'delete') {
    const reg = this._pendingRegKey;
    this._pendingRegKey = '';

    // Black hole register: discard everything
    if (reg === '_') return;

    // Always update unnamed register
    this._unnamedReg = text;
    this._regType = type;

    if (reg) {
      // Uppercase register: append to the lowercase register
      if (reg >= 'A' && reg <= 'Z') {
        const lower = reg.toLowerCase();
        const existing = this._namedRegs[lower];
        if (existing) {
          const sep = (existing.type === 'line' || type === 'line') ? '\n' : '';
          this._namedRegs[lower] = { text: existing.text + sep + text, type: type === 'line' || existing.type === 'line' ? 'line' : 'char' };
        } else {
          this._namedRegs[lower] = { text, type };
        }
      } else {
        this._namedRegs[reg] = { text, type };
      }
      // Notify controller when writing to clipboard registers
      if ((reg === '+' || reg === '*') && this._onClipboardWrite) {
        this._onClipboardWrite(text);
      }
    }

    // Numbered register logic (only when no explicit named register was given)
    if (!reg || (reg >= 'A' && reg <= 'Z')) {
      if (op === 'yank') {
        // "0 always gets the most recent yank
        this._numberedRegs[0] = { text, type };
      } else {
        // delete/change: if linewise OR multiline, shift "1-"9 and store in "1
        const isMultiline = text.includes('\n');
        if (type === 'line' || isMultiline) {
          for (let i = 9; i >= 2; i--) this._numberedRegs[i] = this._numberedRegs[i - 1];
          this._numberedRegs[1] = { text, type };
        } else {
          // Small delete (less than one line) → "- register
          this._smallDeleteReg = { text, type };
        }
      }
    }
  }

  /** Get text and type from the current register (named or unnamed) */
  _getReg() {
    const reg = this._pendingRegKey;
    this._pendingRegKey = '';
    if (reg) {
      // Black hole register
      if (reg === '_') return { text: '', type: 'char' };
      // Numbered registers
      if (reg >= '0' && reg <= '9') {
        const r = this._numberedRegs[parseInt(reg)];
        return r ? r : { text: '', type: 'char' };
      }
      // Small delete register
      if (reg === '-') {
        return this._smallDeleteReg ? this._smallDeleteReg : { text: '', type: 'char' };
      }
      // Last search register
      if (reg === '/') {
        return { text: this._searchPattern || '', type: 'char' };
      }
      // Last inserted text register
      if (reg === '.') {
        return { text: this._lastInsertedText || '', type: 'char' };
      }
      // Last ex command register
      if (reg === ':') {
        return { text: this._lastExCommand || '', type: 'char' };
      }
      // Uppercase register reads from lowercase
      const key = (reg >= 'A' && reg <= 'Z') ? reg.toLowerCase() : reg;
      const r = this._namedRegs[key];
      return r ? r : { text: '', type: 'char' };
    }
    return { text: this._unnamedReg, type: this._regType };
  }

  /**
   * Set the clipboard ("+) register from external data (e.g. browser clipboard).
   * Also mirrors into the "* register.
   * @param {string} text
   * @param {'char'|'line'} [type='char']
   */
  setClipboardText(text, type = 'char') {
    this._namedRegs['+'] = { text, type };
    this._namedRegs['*'] = { text, type };
  }

  // ── Normal mode ──

  _normalKey(key) {
    // q stops macro recording (before any other dispatch)
    if (this._macroRecording && key === 'q' && !this._pendingOp && !this._pendingF && !this._pendingR && !this._pendingG && !this._pendingZ && !this._pendingCapZ && !this._pendingM && !this._pendingQuote && !this._pendingBacktick && !this._pendingTextObjType && !this._pendingBracket && !this._pendingCtrlW) {
      // Remove the trailing 'q' we just captured
      this._macroKeys.pop();
      this._macroRegisters[this._macroRecording] = [...this._macroKeys];
      this._lastMacroRegister = this._macroRecording; // for @@
      this._lastRecordedRegister = this._macroRecording; // for Q
      this._macroRecording = '';
      this._macroKeys = [];
      this._pendingCount = '';
      return;
    }

    // Pending q (waiting for register letter to start recording)
    if (this._pendingQ) {
      this._pendingQ = false;
      if (key.length === 1 && key >= 'a' && key <= 'z') {
        this._macroRecording = key;
        this._macroKeys = [];
      }
      this._pendingCount = '';
      return;
    }

    // Pending @ (waiting for register letter to play macro)
    if (this._pendingAt) {
      this._pendingAt = false;
      // @: — repeat last ex command
      if (key === ':') {
        if (this._lastExCommand) {
          const count = this._getCount();
          for (let i = 0; i < count; i++) {
            // Simulate :<cmd><Enter> by feeding keys
            this.feedKey(':');
            for (const ch of this._lastExCommand) this.feedKey(ch);
            this.feedKey('Enter');
          }
        } else {
          this._messagePrompt = { error: 'E30: No previous command line' };
          this.commandLine = '';
        }
        this._pendingCount = '';
        return;
      }
      let reg = null;
      if (key === '@') {
        // @@ = replay last macro
        reg = this._lastMacroRegister;
      } else if (key.length === 1 && key >= 'a' && key <= 'z') {
        reg = key;
      }
      if (reg && this._macroRegisters[reg]) {
        this._lastMacroRegister = reg;
        const count = this._getCount();
        const keys = this._macroRegisters[reg];
        // Save one snapshot for undo grouping (macro = single undo unit)
        this._saveSnapshot();
        this._redoStack = [];
        const wasPlaying = this._macroPlaying;
        this._macroPlaying = true;
        this._macroAborted = false;
        for (let c = 0; c < count && !this._macroAborted; c++) {
          for (const k of keys) {
            if (this._macroAborted) break;
            this.feedKey(k);
          }
        }
        this._macroPlaying = wasPlaying;
        this._macroAborted = false;
      }
      this._pendingCount = '';
      return;
    }

    // Pending " (register selection)
    if (this._pendingDblQuote) {
      this._pendingDblQuote = false;
      if (key.length === 1 && (/^[a-zA-Z0-9]$/.test(key) || '+-*_/".:'.includes(key))) {
        this._pendingRegKey = key;
      }
      // After setting register, fall through to normal processing
      // (the next key like d, y, p etc. will use the register)
      return;
    }

    // Pending tag input mode (collecting tag name for surround operations)
    if (this._pendingTagInput) {
      if (key === 'Escape') { this._pendingTagInput = null; this._pendingCount = ''; return; }
      if (key === 'Enter') {
        const tagName = this._pendingTagInput.buffer.trim();
        if (!tagName) { this._pendingTagInput = null; this._pendingCount = ''; return; }
        const ctx = this._pendingTagInput;
        this._pendingTagInput = null;
        if (ctx.context === 'ys') {
          this._saveSnapshot();
          this._doSurroundAdd(ctx.range.sr, ctx.range.sc, ctx.range.er, ctx.range.ec,
            null, !ctx.range.noTrim, `<${tagName}>`, `</${tagName.split(/\s/)[0]}>`);
          const dotKeys = ctx.range.dotKeys
            ? [...ctx.range.dotKeys, 't', ...tagName.split(''), 'Enter']
            : ['y', 's', 't', ...tagName.split(''), 'Enter'];
          this._lastChange = dotKeys;
          this._redoStack = [];
        } else if (ctx.context === 'cs') {
          this._saveSnapshot();
          const ok = this._doSurroundChangeTag(ctx.target, tagName);
          if (ok) {
            this._lastChange = ['c', 's', ctx.target, 't', ...tagName.split(''), 'Enter'];
            this._redoStack = [];
          }
        } else if (ctx.context === 'S') {
          const vs = ctx.vs;
          const savedCursor = { ...this.cursor };
          this.cursor = { row: vs.sr, col: vs.sc };
          this._saveSnapshot();
          this.cursor = savedCursor;
          if (vs.wasLinewise) {
            const open = `<${tagName}>`;
            const close = `</${tagName.split(/\s/)[0]}>`;
            this.buffer.lines.splice(vs.er + 1, 0, close);
            this.buffer.lines.splice(vs.sr, 0, open);
            this.cursor.row = vs.sr; this.cursor.col = 0;
          } else {
            this._doSurroundAdd(vs.sr, vs.sc, vs.er, vs.ec,
              null, true, `<${tagName}>`, `</${tagName.split(/\s/)[0]}>`);
          }
          this.mode = Mode.NORMAL; this.commandLine = '';
          this._redoStack = [];
        }
        this._pendingCount = '';
        return;
      }
      if (key === 'Backspace' || key === 'Ctrl-H') {
        this._pendingTagInput.buffer = this._pendingTagInput.buffer.slice(0, -1);
        return;
      }
      if (key.length === 1) {
        this._pendingTagInput.buffer += key;
        return;
      }
      return;
    }

    // Pending ys surround char (we have the range, waiting for the wrap char)
    if (this._ysRange) {
      if (key === 'Escape') {
        this._ysRange = null; this._pendingCount = ''; return;
      }
      if (key === 't') {
        // Tag surround: enter tag input mode
        this._pendingTagInput = { buffer: '', context: 'ys', range: this._ysRange };
        this._ysRange = null;
        return;
      }
      const range = this._ysRange;
      this._ysRange = null;
      this._saveSnapshot();
      this._doSurroundAdd(range.sr, range.sc, range.er, range.ec, key, !range.noTrim);
      this._lastChange = range.dotKeys ? [...range.dotKeys, key] : ['y', 's', key];
      this._redoStack = [];
      this._pendingCount = '';
      return;
    }

    // Pending ds (waiting for target char)
    if (this._pendingSurround === 'ds') {
      this._pendingSurround = '';
      if (key === 'Escape') { this._pendingCount = ''; return; }
      if (key === 't') {
        // Delete surrounding tag
        this._saveSnapshot();
        const ok = this._doSurroundDeleteTag();
        if (ok) {
          this._lastChange = ['d', 's', 't'];
          this._redoStack = [];
        }
        this._pendingCount = '';
        return;
      }
      this._saveSnapshot();
      const ok = this._doSurroundDelete(key);
      if (ok) {
        this._lastChange = ['d', 's', key];
        this._redoStack = [];
      }
      this._pendingCount = '';
      return;
    }

    // Pending cs — waiting for target char
    if (this._pendingSurround === 'cs' && !this._surroundTarget) {
      if (key === 'Escape') {
        this._pendingSurround = ''; this._pendingCount = ''; return;
      }
      this._surroundTarget = key;
      return;
    }

    // Pending cs — have target, waiting for replacement char
    if (this._pendingSurround === 'cs' && this._surroundTarget) {
      const target = this._surroundTarget;
      this._pendingSurround = ''; this._surroundTarget = '';
      if (key === 'Escape') { this._pendingCount = ''; return; }
      if (target === 't') {
        // Tag target: always enter tag input for replacement
        this._pendingTagInput = { buffer: key === 't' ? '' : key, context: 'cs', target: 't' };
        if (key === 't') {
          // 't' as replacement char also means tag input, start with empty buffer
        }
        return;
      }
      if (key === 't') {
        // Non-tag target, but replacement is tag: enter tag input mode
        this._pendingTagInput = { buffer: '', context: 'cs', target };
        return;
      }
      this._saveSnapshot();
      const ok = this._doSurroundChange(target, key);
      if (ok) {
        this._lastChange = ['c', 's', target, key];
        this._redoStack = [];
      }
      this._pendingCount = '';
      return;
    }

    // Pending r
    if (this._pendingR) {
      this._pendingR = false;
      if (key === 'Enter') {
        // r<Enter>: replace character(s) with a newline (split line)
        this._saveSnapshot();
        this._startRecording();
        this._saveForDot('r'); this._saveForDot(key);
        const count = this._getCount();
        const line = this.buffer.lines[this.cursor.row];
        if (this.cursor.col + count - 1 < line.length) {
          const before = line.slice(0, this.cursor.col);
          const after = line.slice(this.cursor.col + count);
          this.buffer.lines[this.cursor.row] = before;
          this.buffer.lines.splice(this.cursor.row + 1, 0, after);
          this.cursor.row++;
          this.cursor.col = 0;
        }
        this._stopRecording();
        this._redoStack = [];
      } else if (key.length === 1 && key !== 'Escape') {
        this._saveSnapshot();
        this._startRecording();
        this._saveForDot('r'); this._saveForDot(key);
        const count = this._getCount();
        const line = this.buffer.lines[this.cursor.row];
        if (this.cursor.col + count - 1 < line.length) {
          let newLine = line.slice(0, this.cursor.col);
          for (let i = 0; i < count; i++) newLine += key;
          newLine += line.slice(this.cursor.col + count);
          this.buffer.lines[this.cursor.row] = newLine;
          this.cursor.col = this.cursor.col + count - 1;
        }
        this._stopRecording();
        this._redoStack = [];
      }
      this._pendingCount = '';
      return;
    }

    // Pending f/F/t/T
    if (this._pendingF) {
      const type = this._pendingF;
      this._pendingF = '';
      // Accept 'Tab' as literal '\t' for f/F/t/T
      const findChar = key === 'Tab' ? '\t' : key;
      if ((findChar.length === 1 || key === 'Tab') && key !== 'Escape') {
        this._lastFind = { type, char: findChar };
        const count = this._getCount();
        const savedCol = this.cursor.col;
        let failed = false;
        if (type === 't' || type === 'T') {
          // For t/T with count, use f/F for intermediate steps
          const fType = type === 't' ? 'f' : 'F';
          for (let i = 0; i < count - 1; i++) {
            const before = this.cursor.col;
            this._doFind(fType, findChar);
            if (this.cursor.col === before) { failed = true; break; }
          }
          if (!failed) {
            // For the final step, use t/T. Consider it successful if
            // the underlying f/F would find the character (even if t/T lands on same col)
            const before = this.cursor.col;
            const fTypeFinal = type === 't' ? 'f' : 'F';
            const testCol = this.cursor.col;
            this._doFind(fTypeFinal, findChar);
            const found = this.cursor.col !== testCol;
            if (found) {
              // Character was found. Apply t/T adjustment
              if (type === 't') this.cursor.col -= 1;
              else this.cursor.col += 1;
            } else {
              failed = true;
            }
          }
        } else {
          for (let i = 0; i < count; i++) {
            const before = this.cursor.col;
            this._doFind(type, findChar);
            if (this.cursor.col === before) { failed = true; break; }
          }
        }
        const moved = !failed && this.cursor.col !== savedCol;
        if (!moved && failed) {
          this.cursor.col = savedCol;  // restore if find failed
        }
        if (this._pendingOp) {
          if (this._pendingOp === 'ys') {
            // ys + f/F/t/T: capture range for surround
            if (moved || (!failed && (type === 't' || type === 'T'))) {
              const ysStartPos = { ...this._opStartPos };
              const endPos = { ...this.cursor };
              let sr, sc, er, ec;
              if (endPos.row < ysStartPos.row || (endPos.row === ysStartPos.row && endPos.col < ysStartPos.col)) {
                sr = endPos.row; sc = endPos.col; er = ysStartPos.row; ec = ysStartPos.col;
              } else {
                sr = ysStartPos.row; sc = ysStartPos.col; er = endPos.row; ec = endPos.col;
              }
              // f/t are inclusive (include found char); for backward F/T, don't include the start pos char
              const isForward = endPos.row > ysStartPos.row || (endPos.row === ysStartPos.row && endPos.col >= ysStartPos.col);
              if (isForward) ec++;
              this.cursor = { ...ysStartPos };
              this._ysRange = { sr, sc, er, ec, dotKeys: ['y', 's', type, key] };
            }
            this._pendingOp = '';
          } else if (moved || (!failed && (type === 't' || type === 'T'))) {
            this._motionInclusive = true;  // f/F/t/T are inclusive for operators
            const opChar = this._pendingOp;
            const dotKeys = [opChar, type, key];
            if (opChar === 'c') {
              this._dotPrefix = dotKeys;
            }
            this._executeOperator(this._opStartPos, { row: this.cursor.row, col: this.cursor.col });
            if (opChar !== 'c' && opChar !== 'y') {
              this._lastChange = dotKeys;
            }
          } else {
            // Find failed, cancel operator
            this.cursor.col = this._opStartPos.col;
          }
          this._pendingOp = '';
        } else {
          // Update desiredCol for standalone find motions
          this._updateDesiredCol();
        }
      } else {
        this._pendingOp = '';
        this._pendingCount = '';
      }
      return;
    }

    // Pending m
    if (this._pendingM) {
      this._pendingM = false;
      if (key.length === 1 && key >= 'a' && key <= 'z')
        this._marks[key] = { row: this.cursor.row, col: this.cursor.col };
      this._pendingCount = '';
      return;
    }

    // Pending ' (mark line)
    if (this._pendingQuote) {
      this._pendingQuote = false;
      const mark = this._resolveMark(key);
      if (mark) {
        const sr = this.cursor.row, sc = this.cursor.col;
        this.cursor.row = Math.min(mark.row, this.buffer.lineCount - 1);
        this.cursor.col = this._firstNonBlank(this.cursor.row);
        if (this._pendingOp) {
          this._motionLinewise = true;
          this._motionInclusive = false;
          // Linewise mark motions always execute (even on same line, like cc/dd)
          this._executeOperator(this._opStartPos, { ...this.cursor });
          this._pendingOp = '';
        }
      } else if (this._pendingOp) {
        this._pendingOp = '';
      }
      this._pendingCount = '';
      return;
    }

    // Pending ` (mark exact)
    if (this._pendingBacktick) {
      this._pendingBacktick = false;
      const mark = this._resolveMark(key);
      if (mark) {
        const sr = this.cursor.row, sc = this.cursor.col;
        this.cursor.row = Math.min(mark.row, this.buffer.lineCount - 1);
        this.cursor.col = mark.col;
        // Clamp col to line length
        const maxCol = Math.max(0, this.buffer.lineLength(this.cursor.row) - 1);
        if (this.cursor.col > maxCol) this.cursor.col = maxCol;
        if (this._pendingOp) {
          this._motionInclusive = false;
          this._motionLinewise = false;
          if (this.cursor.row !== sr || this.cursor.col !== sc) {
            this._executeOperator(this._opStartPos, { ...this.cursor });
          }
          this._pendingOp = '';
        }
      } else if (this._pendingOp) {
        this._pendingOp = '';
      }
      this._pendingCount = '';
      return;
    }

    // Pending Ctrl-W (window command)
    if (this._pendingCtrlW) {
      this._pendingCtrlW = false;
      this._handleCtrlW(key);
      this._pendingCount = '';
      return;
    }

    // Pending z
    if (this._pendingZ) {
      this._pendingZ = false;
      this._handleZ(key);
      this._pendingCount = '';
      return;
    }

    // Pending zu (zug/zuw)
    if (this._pendingZu) {
      this._handleZ(key); // _handleZ checks _pendingZu internally
      this._pendingCount = '';
      return;
    }

    // Pending Z (capital) – ZZ or ZQ
    if (this._pendingCapZ) {
      this._pendingCapZ = false;
      if (key === 'Z') {
        this._lastExCommand = 'wq';
      } else if (key === 'Q') {
        this._lastExCommand = 'q!';
      }
      this._pendingCount = '';
      return;
    }

    // Pending [ or ] bracket command
    if (this._pendingBracket) {
      const bracket = this._pendingBracket;
      this._pendingBracket = '';
      if (key === 'Escape') { this._pendingOp = ''; this._pendingCount = ''; return; }
      const startPos = this._opStartPos || { ...this.cursor };
      this._handleBracketCommand(bracket, key);
      if (this._pendingOp) {
        const moved = (this.cursor.row !== startPos.row || this.cursor.col !== startPos.col);
        if (moved) {
          this._motionInclusive = false;
          this._motionLinewise = false;
          this._executeOperator(startPos, { ...this.cursor });
        }
        this._pendingOp = '';
      }
      this._pendingCount = '';
      return;
    }

    // Pending g
    if (this._pendingG) {
      this._pendingG = false;
      this._handleG(key);
      return;
    }

    // Count accumulation
    if ((key >= '1' && key <= '9') || (key === '0' && this._pendingCount !== '')) {
      this._pendingCount += key;
      return;
    }

    // Operator pending: text object (di, da, ci, ca, yi, ya)
    if (this._pendingTextObjType) {
      const objType = this._pendingTextObjType;
      this._pendingTextObjType = null;
      const opChar = this._pendingOp;
      // ys + text object: capture range, wait for surround char
      if (opChar === 'ys') {
        const range = this._getTextObject(objType, key);
        if (range) {
          const dotKeys = ['y', 's', objType, key];
          let sr = range.startRow, sc = range.startCol, er = range.endRow, ec = range.endCol;
          // Trim trailing whitespace from range (nvim-surround trims before wrapping)
          if (sr === er) {
            const line = this.buffer.lines[sr];
            while (ec > sc && (line[ec - 1] === ' ' || line[ec - 1] === '\t')) ec--;
          } else {
            const eline = this.buffer.lines[er];
            while (ec > 0 && (eline[ec - 1] === ' ' || eline[ec - 1] === '\t')) ec--;
          }
          this._ysRange = { sr, sc, er, ec, dotKeys };
        }
        this._pendingOp = '';
        this._pendingCount = '';
        return;
      }
      const range = this._getTextObject(objType, key);
      if (range) {
        const dotKeys = [opChar, objType, key];
        if (opChar === 'c') {
          this._dotPrefix = dotKeys;
        }
        this._executeOperatorRange(range);
        // For non-insert operators (d, >, <, etc), save _lastChange directly
        if (opChar !== 'c' && opChar !== 'y') {
          this._lastChange = dotKeys;
        }
      }
      this._pendingOp = '';
      this._pendingCount = '';
      return;
    }

    // Operator pending: second key
    if (this._pendingOp) {
      // Surround: ys, ds, cs intercepts
      if (key === 's' && (this._pendingOp === 'y' || this._pendingOp === 'd' || this._pendingOp === 'c')) {
        if (this._pendingOp === 'y') {
          // ys — enter surround-add mode (need motion + surround char)
          this._pendingOp = 'ys';
          this._opStartPos = { ...this.cursor };
          return;
        } else if (this._pendingOp === 'd') {
          // ds — enter surround-delete mode (need target char)
          this._pendingSurround = 'ds';
          this._pendingOp = ''; this._pendingCount = '';
          return;
        } else if (this._pendingOp === 'c') {
          // cs — enter surround-change mode (need target + replacement)
          this._pendingSurround = 'cs';
          this._pendingOp = ''; this._pendingCount = '';
          return;
        }
      }
      // ys operator: handle yss (surround whole line) and motions
      if (this._pendingOp === 'ys') {
        if (key === 's') {
          // yss — surround whole line
          const row = this.cursor.row;
          const line = this.buffer.lines[row];
          const m = line.match(/\S/);
          const fnb = m ? m.index : 0; // all-whitespace: wrap from col 0
          const end = line.length;
          this._ysRange = { sr: row, sc: fnb, er: row, ec: end, dotKeys: ['y', 's', 's'], noTrim: true };
          this._pendingOp = ''; this._pendingCount = '';
          return;
        }
        // Text object trigger (i or a)
        if (key === 'i' || key === 'a') {
          this._pendingTextObjType = key;
          return;
        }
        // Operator + g prefix
        if (key === 'g') { this._pendingG = true; return; }
        // Operator + f/F/t/T
        if (key === 'f' || key === 'F' || key === 't' || key === 'T') {
          this._pendingF = key;
          this._motionInclusive = (key === 'f' || key === 'F');
          return;
        }
        // Handle motion to get range, then wait for surround char
        this._motionInclusive = false;
        this._motionLinewise = false;
        this._motionExclusive = false;
        const ysStartPos = { ...this.cursor };
        const motionCountStr = this._pendingCount;
        const moved = this._doMotion(key);
        if (moved || this._motionInclusive) {
          let sr, sc, er, ec;
          const endPos = { ...this.cursor };
          // Normalize range (start <= end)
          if (endPos.row < ysStartPos.row || (endPos.row === ysStartPos.row && endPos.col < ysStartPos.col)) {
            sr = endPos.row; sc = endPos.col; er = ysStartPos.row; ec = ysStartPos.col;
          } else {
            sr = ysStartPos.row; sc = ysStartPos.col; er = endPos.row; ec = endPos.col;
          }
          // If word motion overshot to start of next line, clamp to end of start line
          if (er > sr && ec === 0 && (key === 'w' || key === 'W')) {
            er = sr;
            ec = this.buffer.lines[sr].length;
          }
          // For inclusive motions (e, $, f), include the endpoint char
          if (this._motionInclusive) ec++;
          // Restore cursor to start for ys
          this.cursor = { ...ysStartPos };
          const dotKeys = ['y', 's'];
          if (motionCountStr) for (const ch of motionCountStr) dotKeys.push(ch);
          dotKeys.push(key);
          // Trim trailing whitespace from range (nvim-surround trims before wrapping)
          if (sr === er) {
            const line = this.buffer.lines[sr];
            while (ec > sc && (line[ec - 1] === ' ' || line[ec - 1] === '\t')) ec--;
          } else {
            const eline = this.buffer.lines[er];
            while (ec > 0 && (eline[ec - 1] === ' ' || eline[ec - 1] === '\t')) ec--;
          }
          this._ysRange = { sr, sc, er, ec, dotKeys };
        }
        this._pendingOp = ''; this._pendingCount = '';
        return;
      }
      // !! — filter current line(s) through shell command
      if (this._pendingOp === '!' && key === '!') {
        const count = this._getCount();
        const sr = this.cursor.row;
        const er = Math.min(sr + count - 1, this.buffer.lineCount - 1);
        let rangeStr;
        if (count === 1) {
          rangeStr = '.';
        } else {
          rangeStr = '.,.+' + (count - 1);
        }
        this._filterRange = { sr, er };
        this.mode = Mode.COMMAND;
        this._searchInput = rangeStr + '!';
        this.commandLine = ':' + rangeStr + '!';
        this._pendingOp = '';
        this._pendingCount = '';
        return;
      }
      // Double operator = line op (dd, cc, yy, >>, <<)
      if (key === this._pendingOp[this._pendingOp.length - 1]) {
        const countStr = this._pendingCount;
        const count = this._getCount();
        const opChar = this._pendingOp[this._pendingOp.length - 1];
        // Build the dot key sequence
        const dotKeys = [];
        if (countStr) for (const ch of countStr) dotKeys.push(ch);
        dotKeys.push(opChar, opChar);
        if (opChar === 'c') {
          // cc enters insert mode — set prefix for _stopRecording
          this._dotPrefix = dotKeys;
        }
        this._doLineOperation(this._pendingOp, count);
        // Save for dot (not for yy - yank is not a change)
        // For cc, _stopRecording in insert-mode Escape will handle it
        if (opChar !== 'y' && opChar !== 'c') {
          this._lastChange = dotKeys;
        }
        this._pendingOp = '';
        return;
      }
      // Text object trigger (i or a)
      if (key === 'i' || key === 'a') {
        this._pendingTextObjType = key;
        this._pendingTextObjKeyForDot = key;
        return;
      }
      // Operator + g prefix
      if (key === 'g') {
        this._pendingG = true;
        return;
      }
      // Operator + motion
      this._opStartPos = { row: this.cursor.row, col: this.cursor.col };
      // Special handling for f/F/t/T in operator-pending
      if (key === 'f' || key === 'F' || key === 't' || key === 'T') {
        this._pendingF = key;
        this._motionInclusive = (key === 'f' || key === 'F');
        this._pendingMotionKeyForDot = key;
        return;
      }
      // Marks in operator-pending: wait for mark key
      if (key === "'") {
        this._pendingQuote = true;
        return;
      }
      if (key === '`') {
        this._pendingBacktick = true;
        return;
      }
      // Bracket commands in operator-pending: [( ]) [{ ]} [[ ]] [] ][
      if (key === '[' || key === ']') {
        this._pendingBracket = key;
        return;
      }
      // Search in operator-pending: save operator state, enter command mode
      if (key === '/' || key === '?') {
        this._pendingOpForSearch = this._pendingOp;
        this._opStartPosForSearch = { ...this._opStartPos };
        this._pendingOp = '';
        this.mode = Mode.COMMAND;
        this._searchForward = (key === '/');
        this._searchInput = '';
        this.commandLine = key;
        return;
      }
      // cw/cW special case: when cursor is on a non-blank, change to end of
      // current word (like ce/cE) rather than using w/W motion.  We compute
      // the word end manually because `e` from the last char of a word jumps
      // to the end of the *next* word, which would change too much.
      let actualKey = key;
      let cwSpecial = false;
      const curLine = this.buffer.lines[this.cursor.row] || '';
      const curCh = curLine[this.cursor.col];
      if ((this._pendingOp === 'c') && (key === 'w' || key === 'W')) {
        if (curCh && curCh !== ' ' && curCh !== '\t') {
          cwSpecial = true;  // handle below after motion
          // Still use e/E motion for the multi-count case, but we need
          // to clip to word boundary for count=1
          actualKey = (key === 'w') ? 'e' : 'E';
        }
      }
      this._motionInclusive = false;
      this._motionLinewise = false;
      this._motionExclusive = false;
      const opChar = this._pendingOp;
      // Capture count string before motion consumes it
      const motionCountStr = this._pendingCount;
      const cwStartRow = this.cursor.row;
      const cwStartCol = this.cursor.col;
      const cwCount = motionCountStr ? parseInt(motionCountStr, 10) : 1;
      const moved = this._doMotion(actualKey);
      // For cw/cW special case with count=1: if the e/E motion crossed
      // whitespace (the end position is in a different word than the start),
      // clip to end of the original word so we don't eat trailing whitespace
      // or the next word.  With count>1, e/E already gives the right endpoint.
      if (cwSpecial && moved && cwCount === 1) {
        const line = this.buffer.lines[cwStartRow];
        // Find end of current word from the start position
        let endCol = cwStartCol;
        const bigWord = (key === 'W');
        if (bigWord) {
          while (endCol + 1 < line.length && line[endCol + 1] !== ' ' && line[endCol + 1] !== '\t') endCol++;
        } else {
          if (this._isWordChar(line[cwStartCol])) {
            while (endCol + 1 < line.length && this._isWordChar(line[endCol + 1])) endCol++;
          } else {
            while (endCol + 1 < line.length && !this._isWordChar(line[endCol + 1]) && line[endCol + 1] !== ' ' && line[endCol + 1] !== '\t') endCol++;
          }
        }
        // If the motion went beyond the word boundary (onto next word),
        // clip to end of current word
        if (this.cursor.row > cwStartRow || this.cursor.col > endCol) {
          this.cursor.row = cwStartRow;
          this.cursor.col = endCol;
        }
      }
      // Operator with inclusive motion that didn't move: still operates on
      // current character (e.g. ce at end of last word, c$ on single char,
      // y$ at end of line, d$ at end of line).
      // c operator with positional motion (0, ^) that didn't move: enters
      // insert mode without deleting (zero-width change).
      // Other operators or backward motions that fail: no-op.
      const inclusiveNoMove = !moved && !this._motionLinewise && this._motionInclusive;
      const cPositionalNoMove = opChar === 'c' && !moved && !this._motionLinewise &&
        (actualKey === '0' || actualKey === '^');
      if (moved || this._motionLinewise || inclusiveNoMove || cPositionalNoMove) {
        let opEndPos = { row: this.cursor.row, col: this.cursor.col };
        // dw/dW special case: when w/W crosses a line boundary, 
        // only delete to end of the original line (not across lines)
        if (opChar === 'd' && (key === 'w' || key === 'W') && this.cursor.row > this._opStartPos.row) {
          // Delete from opStart to end of line (linewise for the original line)
          // Special: if opStart line is empty, delete just the empty line
          if (this.buffer.lines[this._opStartPos.row].length === 0) {
            this._motionLinewise = true;
            opEndPos = { row: this._opStartPos.row, col: 0 };
          } else {
            opEndPos = { row: this._opStartPos.row, col: this.buffer.lines[this._opStartPos.row].length };
          }
        }
        // Build dot prefix for operator+motion (e.g. 'c', '2', 'w' or 'd', 'w')
        const dotKeys = [];
        dotKeys.push(opChar);
        if (motionCountStr) for (const ch of motionCountStr) dotKeys.push(ch);
        dotKeys.push(key);
        if (opChar === 'c') {
          // c enters insert mode - set prefix for _stopRecording
          this._dotPrefix = dotKeys;
        }
        this._executeOperator(this._opStartPos, opEndPos);
        // For non-insert operators (d, >, <, etc), save _lastChange directly
        if (opChar !== 'c' && opChar !== 'y') {
          this._lastChange = dotKeys;
        }
      }
      this._pendingOp = '';
      this._pendingCount = '';
      return;
    }

    switch (key) {
      // Movement
      case 'Ctrl-H':
      case 'h': case 'ArrowLeft': {
        const count = this._getCount();
        for (let i = 0; i < count; i++) { if (this.cursor.col > 0) this.cursor.col--; }
        this._updateDesiredCol();
        break;
      }
      case 'Backspace': {
        const count = this._getCount();
        for (let i = 0; i < count; i++) {
          if (this.cursor.col > 0) {
            this.cursor.col--;
          } else if (this.cursor.row > 0) {
            this.cursor.row--;
            this.cursor.col = this._maxCol();
          }
        }
        this._updateDesiredCol();
        break;
      }
      case 'l': case 'ArrowRight': {
        const count = this._getCount();
        for (let i = 0; i < count; i++) {
          if (this.cursor.col < this._maxCol()) this.cursor.col++;
        }
        this._updateDesiredCol();
        break;
      }
      case ' ': {
        const count = this._getCount();
        for (let i = 0; i < count; i++) {
          if (this.cursor.col < this._maxCol()) {
            this.cursor.col++;
          } else if (this.cursor.row < this.buffer.lineCount - 1) {
            this.cursor.row++;
            this.cursor.col = 0;
          }
        }
        this._updateDesiredCol();
        break;
      }
      case 'Ctrl-N':
      case 'Ctrl-J':
      case 'j': case 'ArrowDown': {
        const count = this._getCount();
        const beforeRow = this.cursor.row;
        for (let i = 0; i < count; i++) {
          if (this.cursor.row < this.buffer.lineCount - 1) {
            // Skip closed folds: if on fold start, jump past fold end
            const cf = this.getClosedFoldAt(this.cursor.row);
            if (cf) {
              this.cursor.row = Math.min(cf.endRow + 1, this.buffer.lineCount - 1);
            } else {
              this.cursor.row++;
            }
          }
        }
        if (this._macroPlaying && this.cursor.row === beforeRow) this._macroAborted = true;
        this._applyDesiredCol();
        break;
      }
      case 'Ctrl-P':
      case 'k': case 'ArrowUp': {
        const count = this._getCount();
        const beforeRow = this.cursor.row;
        for (let i = 0; i < count; i++) {
          if (this.cursor.row > 0) {
            this.cursor.row--;
            // Skip closed folds: if landed inside a fold, jump to fold start
            const hf = this.getFoldHidingRow(this.cursor.row);
            if (hf) this.cursor.row = hf.startRow;
          }
        }
        this._applyDesiredCol();
        break;
      }

      // Word motions
      case 'w': { const c = this._getCount(); for (let i = 0; i < c; i++) this._moveWordForward(false); this._updateDesiredCol(); break; }
      case 'W': { const c = this._getCount(); for (let i = 0; i < c; i++) this._moveWordForward(true); this._updateDesiredCol(); break; }
      case 'b': { const c = this._getCount(); for (let i = 0; i < c; i++) this._moveWordBackward(false); this._updateDesiredCol(); break; }
      case 'B': { const c = this._getCount(); for (let i = 0; i < c; i++) this._moveWordBackward(true); this._updateDesiredCol(); break; }
      case 'e': { const c = this._getCount(); for (let i = 0; i < c; i++) this._moveWordEnd(false); this._updateDesiredCol(); break; }
      case 'E': { const c = this._getCount(); for (let i = 0; i < c; i++) this._moveWordEnd(true); this._updateDesiredCol(); break; }

      // Line motions
      case '0': this.cursor.col = 0; this._desiredCol = 0; break;
      case '^': this.cursor.col = this._firstNonBlank(this.cursor.row); this._updateDesiredCol(); break;
      case '$': {
        const count = this._getCount();
        if (count > 1) this.cursor.row = Math.min(this.cursor.row + count - 1, this.buffer.lineCount - 1);
        this.cursor.col = this._maxCol();
        this._desiredCol = Infinity;
        break;
      }
      case '_': {
        const count = this._getCount();
        this.cursor.row = Math.min(this.cursor.row + count - 1, this.buffer.lineCount - 1);
        this.cursor.col = this._firstNonBlank(this.cursor.row);
        this._updateDesiredCol();
        break;
      }

      // File motions
      case 'G': {
        this._addJumpEntry();
        if (this._hasCount()) {
          const n = this._getCount();
          this.cursor.row = Math.max(0, Math.min(n - 1, this.buffer.lineCount - 1));
          this.cursor.col = 0;
          this._updateDesiredCol();
        } else {
          this.cursor.row = this.buffer.lineCount - 1;
          this._applyDesiredCol();
        }
        break;
      }
      case 'g': this._pendingG = true; return;
      case 'z': this._pendingZ = true; return;
      case 'Z': this._pendingCapZ = true; return;

      // f F t T
      case 'f': case 'F': case 't': case 'T':
        this._pendingF = key; return;

      // ; ,
      case ';': {
        if (this._lastFind) {
          const c = this._getCount();
          this._doFindRepeat(this._lastFind.type, this._lastFind.char, c);
        }
        break;
      }
      case ',': {
        if (this._lastFind) {
          const c = this._getCount();
          const rev = { f: 'F', F: 'f', t: 'T', T: 't' }[this._lastFind.type];
          this._doFindRepeat(rev, this._lastFind.char, c);
        }
        break;
      }

      // % (match bracket or percentage)
      case '%': {
        if (!this._hasCount()) { this._doMatchBracket(); }
        else {
          const pct = this._getCount();
          const target = Math.max(0, Math.min(Math.round((pct / 100) * this.buffer.lineCount) - 1, this.buffer.lineCount - 1));
          this.cursor.row = target;
          this.cursor.col = this._firstNonBlank(this.cursor.row);
        }
        this._updateDesiredCol();
        break;
      }

      // Paragraph
      case '{': { const c = this._getCount(); const saved = { row: this.cursor.row, col: this.cursor.col }; let ok = true; for (let i = 0; i < c; i++) { if (!this._moveParagraphBackward()) { ok = false; break; } } if (!ok) { this.cursor.row = saved.row; this.cursor.col = saved.col; } this._updateDesiredCol(); break; }
      case '}': { const c = this._getCount(); const saved = { row: this.cursor.row, col: this.cursor.col }; let ok = true; for (let i = 0; i < c; i++) { if (!this._moveParagraphForward()) { ok = false; break; } } if (!ok) { this.cursor.row = saved.row; this.cursor.col = saved.col; } this._updateDesiredCol(); break; }

      // Screen motions
      case 'H': {
        const c = this._getCount() - 1;
        this.cursor.row = Math.min(this.scrollTop + c, this.buffer.lineCount - 1);
        this.cursor.col = this._byteColForVirtCol(this.cursor.row, this._desiredCol);
        break;
      }
      case 'M': {
        const visible = Math.min(this._textRows, this.buffer.lineCount - this.scrollTop);
        this.cursor.row = this.scrollTop + Math.floor((visible - 1) / 2);
        this.cursor.col = this._byteColForVirtCol(this.cursor.row, this._desiredCol);
        break;
      }
      case 'L': {
        const c = this._getCount() - 1;
        const lastVis = this.scrollTop + Math.min(this._textRows, this.buffer.lineCount - this.scrollTop) - 1;
        this.cursor.row = Math.max(this.scrollTop, lastVis - c);
        this.cursor.col = this._byteColForVirtCol(this.cursor.row, this._desiredCol);
        break;
      }

      // + - Enter
      case 'Ctrl-M':
      case '+': case 'Enter': {
        const c = this._getCount();
        this.cursor.row = Math.min(this.cursor.row + c, this.buffer.lineCount - 1);
        this.cursor.col = this._firstNonBlank(this.cursor.row);
        this._updateDesiredCol();
        break;
      }
      case '-': {
        const c = this._getCount();
        this.cursor.row = Math.max(this.cursor.row - c, 0);
        this.cursor.col = this._firstNonBlank(this.cursor.row);
        this._updateDesiredCol();
        break;
      }

      // | (go to column)
      case '|': {
        const c = this._getCount() - 1;  // virtual column (0-indexed)
        this.cursor.col = this._byteColForVirtCol(this.cursor.row, c);
        this._updateDesiredCol();
        break;
      }

      // ── Editing ──
      case 'Delete':
      case 'x': {
        const countStr = this._pendingCount;
        const count = this._getCount();
        if (this.buffer.lineLength(this.cursor.row) === 0) break;
        this._saveSnapshot();
        if (countStr) this._dotPrefix = [...countStr];
        this._startRecording(); this._saveForDot('x');
        let del = '';
        for (let i = 0; i < count; i++) {
          if (this.cursor.col < this.buffer.lineLength(this.cursor.row)) {
            del += this.buffer.charAt(this.cursor.row, this.cursor.col);
            this.buffer.deleteChar(this.cursor.row, this.cursor.col);
          }
        }
        if (del) { this._setReg(del, 'char'); }
        this._stopRecording(); this._redoStack = [];
        // Clamp cursor to valid position after delete, then update desiredCol
        if (this.cursor.col > 0 && this.cursor.col >= this.buffer.lineLength(this.cursor.row)) {
          this.cursor.col = Math.max(0, this.buffer.lineLength(this.cursor.row) - 1);
        }
        this._updateDesiredCol();
        break;
      }
      case 'X': {
        const countStr = this._pendingCount;
        const count = this._getCount();
        this._saveSnapshot();
        if (countStr) this._dotPrefix = [...countStr];
        this._startRecording(); this._saveForDot('X');
        let del = '';
        for (let i = 0; i < count; i++) {
          if (this.cursor.col > 0) {
            this.cursor.col--;
            del = this.buffer.charAt(this.cursor.row, this.cursor.col) + del;
            this.buffer.deleteChar(this.cursor.row, this.cursor.col);
          }
        }
        if (del) { this._setReg(del, 'char'); }
        this._stopRecording(); this._redoStack = [];
        this._updateDesiredCol();
        break;
      }
      case 's': {
        const countStr = this._pendingCount;
        const count = this._getCount();
        this._saveSnapshot();
        if (countStr) this._dotPrefix = [...countStr];
        this._startRecording(); this._saveForDot('s');
        let del = '';
        for (let i = 0; i < count; i++) {
          if (this.cursor.col < this.buffer.lineLength(this.cursor.row)) {
            del += this.buffer.charAt(this.cursor.row, this.cursor.col);
            this.buffer.deleteChar(this.cursor.row, this.cursor.col);
          }
        }
        if (del) { this._setReg(del, 'char'); }
        this.mode = Mode.INSERT;
        this.commandLine = '-- INSERT --';
        break;
      }
      case 'S': {
        const sCount = this._getCount();
        this._insertCount = 1; // S count is for lines, not insert repeat
        this._saveSnapshot();
        this._startRecording(); this._saveForDot('S');
        // S with count: delete sCount lines, replace with empty line (like cc)
        const sSr = this.cursor.row;
        const sEr = Math.min(sSr + sCount - 1, this.buffer.lineCount - 1);
        // Preserve leading whitespace from first line
        const sLine = this.buffer.lines[sSr];
        const sIndent = sLine.match(/^\s*/)[0];
        let sYank = '';
        for (let r = sSr; r <= sEr; r++) sYank += (r > sSr ? '\n' : '') + this.buffer.lines[r];
        this._setReg(sYank, 'line');
        this.buffer.lines.splice(sSr, sEr - sSr + 1, sIndent);
        this.cursor.row = sSr;
        this.cursor.col = sIndent.length;
        this.mode = Mode.INSERT; this.commandLine = '-- INSERT --';
        this._redoStack = [];
        break;
      }
      case 'r': this._pendingR = true; return;
      case 'R':
        this._saveSnapshot();
        this._startRecording(); this._saveForDot('R');
        this.mode = Mode.REPLACE;
        this.commandLine = '-- REPLACE --';
        // Save replace mode start position and original chars for backspace
        this._replaceStartCol = this.cursor.col;
        this._replaceOrigChars = []; // stack of {col, char|null} entries
        break;

      // ~ (toggle case)
      case '~': {
        const count = this._getCount();
        if (this.buffer.lineLength(this.cursor.row) === 0) break;
        this._saveSnapshot();
        this._startRecording(); this._saveForDot('~');
        for (let i = 0; i < count; i++) {
          if (this.cursor.col < this.buffer.lineLength(this.cursor.row)) {
            const ch = this.buffer.charAt(this.cursor.row, this.cursor.col);
            const tog = ch === ch.toUpperCase() ? ch.toLowerCase() : ch.toUpperCase();
            this.buffer.lines[this.cursor.row] = this.buffer.lines[this.cursor.row].slice(0, this.cursor.col) + tog + this.buffer.lines[this.cursor.row].slice(this.cursor.col + 1);
            if (this.cursor.col < this.buffer.lineLength(this.cursor.row) - 1) {
              this.cursor.col++;
            } else {
              break; // Reached end of line, stop toggling
            }
          }
        }
        this._stopRecording(); this._redoStack = [];
        this._updateDesiredCol();
        break;
      }

      // J (join)
      case 'J': {
        const count = Math.max(2, this._getCount());
        const numJoins = count - 1;  // nJ joins n lines = n-1 joins
        this._saveSnapshot();
        this._startRecording(); this._saveForDot('J');
        for (let i = 0; i < numJoins; i++) {
          if (this.cursor.row < this.buffer.lineCount - 1) {
            const cur = this.buffer.lines[this.cursor.row];
            const next = this.buffer.lines[this.cursor.row + 1];
            const trimmed = next.replace(/^\s+/, '');
            const joinCol = cur.length;
            // Vim rules for adding space:
            // - Don't add space if current line is empty
            // - Don't add space if next line (after stripping indent) is empty
            // - Don't add space if next line starts with ')'
            // - Don't add space if current line ends with whitespace
            const nextFirstChar = trimmed.length > 0 ? trimmed[0] : '';
            const curEndsWithSpace = cur.length > 0 && (cur[cur.length - 1] === ' ' || cur[cur.length - 1] === '\t');
            let joined;
            if (cur.length === 0 || trimmed.length === 0 || nextFirstChar === ')' || curEndsWithSpace) {
              joined = cur + trimmed;
            } else {
              joined = cur + ' ' + trimmed;
            }
            this.buffer.lines[this.cursor.row] = joined;
            this.buffer.lines.splice(this.cursor.row + 1, 1);
            this.cursor.col = joinCol;
          }
        }
        this._stopRecording(); this._redoStack = [];
        this._updateDesiredCol();
        break;
      }

      // K — keyword lookup
      case 'K': {
        const word = this._wordUnderCursor();
        if (word) {
          this.commandLine = 'E149: Sorry, no help for ' + word;
          this._stickyCommandLine = true;
        }
        break;
      }

      // Operators
      case 'd': this._pendingOp = 'd'; this._opStartPos = { ...this.cursor }; return;
      case 'c': this._pendingOp = 'c'; this._opStartPos = { ...this.cursor }; return;
      case 'y': this._pendingOp = 'y'; this._opStartPos = { ...this.cursor }; return;
      case '>': this._pendingOp = '>'; this._opStartPos = { ...this.cursor }; return;
      case '<': this._pendingOp = '<'; this._opStartPos = { ...this.cursor }; return;
      case '=': this._pendingOp = '='; this._opStartPos = { ...this.cursor }; return;
      case '!': this._pendingOp = '!'; this._opStartPos = { ...this.cursor }; return;

      // & (repeat last :s on current line)
      case '&': {
        if (this._lastSubstitution) {
          const { pattern, replacement } = this._lastSubstitution;
          let jsPattern = this._vimPatternToJs(pattern);
          let jsReplacement = replacement
            .replace(/\\&/g, '\x00AMP')
            .replace(/\$/g, '$$$$')
            .replace(/&/g, '$$&')
            .replace(/\x00AMP/g, '&')
            .replace(/\\([1-9])/g, '$$$1');
          let caseFlag = this._searchCaseFlag();
          let regex;
          try { regex = new RegExp(jsPattern, caseFlag); } catch {
            this.commandLine = 'E486: Pattern not found: ' + pattern;
            this._stickyCommandLine = true;
            break;
          }
          const r = this.cursor.row;
          const before = this.buffer.lines[r];
          const after = before.replace(regex, jsReplacement);
          if (after !== before) {
            this._saveSnapshot();
            this.buffer.lines[r] = after;
            this.cursor.col = this._firstNonBlank(r);
            this._redoStack = [];
          }
          this.commandLine = ':&&';
          this._stickyCommandLine = true;
        } else {
          this._messagePrompt = { error: 'E33: No previous substitute regular expression' };
          this.commandLine = '';
        }
        break;
      }

      // D C Y
      case 'D': {
        this._saveSnapshot();
        this._startRecording(); this._saveForDot('D');
        const count = this._getCount();
        const line = this.buffer.lines[this.cursor.row];
        if (count > 1) {
          // 2D = delete to EOL on current line + (count-1) subsequent full lines
          const lastRow = Math.min(this.cursor.row + count - 1, this.buffer.lineCount - 1);
          let y = line.slice(this.cursor.col);
          for (let r = this.cursor.row + 1; r <= lastRow; r++) y += '\n' + this.buffer.lines[r];
          this._setReg(y, 'char');
          this.buffer.lines.splice(this.cursor.row + 1, lastRow - this.cursor.row);
          this.buffer.lines[this.cursor.row] = line.slice(0, this.cursor.col);
          // If the line became empty and there are more lines, remove it (matches nvim)
          if (this.buffer.lines[this.cursor.row] === '' && this.buffer.lineCount > 1) {
            this.buffer.lines.splice(this.cursor.row, 1);
            if (this.cursor.row >= this.buffer.lineCount) {
              this.cursor.row = this.buffer.lineCount - 1;
            }
          }
        } else {
          this._setReg(line.slice(this.cursor.col), 'char');
          this.buffer.lines[this.cursor.row] = line.slice(0, this.cursor.col);
        }
        this.cursor.col = Math.max(0, this.cursor.col - 1);
        this._stopRecording(); this._redoStack = [];
        this._updateDesiredCol();
        break;
      }
      case 'C': {
        this._saveSnapshot();
        this._startRecording(); this._saveForDot('C');
        const line = this.buffer.lines[this.cursor.row];
        this._setReg(line.slice(this.cursor.col), 'char');
        this.buffer.lines[this.cursor.row] = line.slice(0, this.cursor.col);
        this.mode = Mode.INSERT;
        this.commandLine = '-- INSERT --';
        break;
      }
      case 'Y': {
        const count = this._getCount();
        const line = this.buffer.lines[this.cursor.row];
        this._setReg(line.slice(this.cursor.col), 'char', 'yank');
        break;
      }

      // p P
      case 'p': {
        const count = this._getCount();
        const explicitReg = this._pendingRegKey;
        const reg = this._getReg();
        if (explicitReg && !reg.text && explicitReg !== '_') {
          this.commandLine = 'E353: Nothing in register ' + explicitReg;
          this._stickyCommandLine = true;
          break;
        }
        this._saveSnapshot();
        this._startRecording(); this._saveForDot('p');
        for (let i = 0; i < count; i++) this._putAfter(reg);
        // For linewise paste with count, cursor goes to first pasted line
        if (reg.type === 'line' && count > 1) {
          this.cursor.row -= (count - 1);
          this.cursor.col = this._firstNonBlank(this.cursor.row);
        }
        this._stopRecording(); this._redoStack = [];
        break;
      }
      case 'P': {
        const count = this._getCount();
        const explicitReg = this._pendingRegKey;
        const reg = this._getReg();
        if (explicitReg && !reg.text && explicitReg !== '_') {
          this.commandLine = 'E353: Nothing in register ' + explicitReg;
          this._stickyCommandLine = true;
          break;
        }
        this._saveSnapshot();
        this._startRecording(); this._saveForDot('P');
        for (let i = 0; i < count; i++) this._putBefore(reg);
        // For linewise paste with count, cursor goes to first pasted line
        if (reg.type === 'line' && count > 1) {
          this.cursor.row -= (count - 1);
          this.cursor.col = this._firstNonBlank(this.cursor.row);
        }
        this._stopRecording(); this._redoStack = [];
        break;
      }

      // Enter insert mode
      case 'i':
        this._insertCount = this._getCount();
        this._saveSnapshot(); this._startRecording(); this._saveForDot('i');
        this.mode = Mode.INSERT; this.commandLine = '-- INSERT --';
        break;
      case 'I': {
        this._insertCount = this._getCount();
        this._saveSnapshot(); this._startRecording(); this._saveForDot('I');
        const ILine = this.buffer.lines[this.cursor.row];
        const Ifnb = ILine.match(/\S/);
        // I goes to first non-blank; on all-whitespace line, go to end
        this.cursor.col = Ifnb ? Ifnb.index : ILine.length;
        this.mode = Mode.INSERT; this.commandLine = '-- INSERT --';
        break;
      }
      case 'a':
        this._insertCount = this._getCount();
        this._startRecording(); this._saveForDot('a');
        if (this.buffer.lineLength(this.cursor.row) > 0) this.cursor.col++;
        this._saveSnapshot();
        this.mode = Mode.INSERT; this.commandLine = '-- INSERT --';
        break;
      case 'A':
        this._insertCount = this._getCount();
        this._startRecording(); this._saveForDot('A');
        this.cursor.col = this.buffer.lineLength(this.cursor.row);
        this._saveSnapshot();
        this.mode = Mode.INSERT; this.commandLine = '-- INSERT --';
        break;
      case 'o': {
        this._insertCount = this._getCount();
        this._saveSnapshot(); this._startRecording(); this._saveForDot('o');
        const oIndent = this._settings.autoindent ? this.buffer.lines[this.cursor.row].match(/^[ \t]*/)[0] : '';
        this.buffer.insertLineAfter(this.cursor.row);
        this.cursor.row++;
        this.buffer.lines[this.cursor.row] = oIndent;
        this.cursor.col = oIndent.length;
        this.mode = Mode.INSERT; this.commandLine = '-- INSERT --';
        break;
      }
      case 'O': {
        this._insertCount = this._getCount();
        this._saveSnapshot(); this._startRecording(); this._saveForDot('O');
        const OIndent = this._settings.autoindent ? this.buffer.lines[this.cursor.row].match(/^[ \t]*/)[0] : '';
        this.buffer.insertLineBefore(this.cursor.row);
        this.buffer.lines[this.cursor.row] = OIndent;
        this.cursor.col = OIndent.length;
        this.mode = Mode.INSERT; this.commandLine = '-- INSERT --';
        break;
      }

      // Undo/Redo
      case 'u': { const c = this._getCount(); for (let i = 0; i < c; i++) this._undo(); if (this._showCurSearch) this._updateCurSearchPos(); break; }
      case 'Ctrl-R': { const c = this._getCount(); for (let i = 0; i < c; i++) this._redo(); if (this._showCurSearch) this._updateCurSearchPos(); break; }
      case 'U': {
        // Undo all changes on current line
        if (this._lineUndoSave && this._lineUndoSave.row === this.cursor.row) {
          this._saveSnapshot();
          this.buffer.lines[this.cursor.row] = this._lineUndoSave.text;
          this.cursor.col = Math.min(this.cursor.col, Math.max(0, this.buffer.lineLength(this.cursor.row) - 1));
          this._redoStack = [];
        }
        break;
      }

      // Dot repeat
      case '.': {
        if (this._lastChange) {
          const dotCountStr = this._pendingCount;
          this._pendingCount = '';
          const saved = [...this._lastChange];
          let replay;
          if (dotCountStr) {
            // Count replaces original count: 3. after 2dd → 3dd
            // Skip leading digits in saved, prepend new count
            let i = 0;
            while (i < saved.length && saved[i] >= '0' && saved[i] <= '9') i++;
            replay = [...dotCountStr].concat(saved.slice(i));
          } else {
            replay = saved;
          }
          for (const k of replay) this.feedKey(k);
          this._lastChange = saved;
        }
        break;
      }

      // Visual mode
      case 'v':
        this.mode = Mode.VISUAL;
        this._visualStart = { ...this.cursor };
        this.commandLine = '-- VISUAL --';
        break;
      case 'V':
        this.mode = Mode.VISUAL_LINE;
        this._visualStart = { ...this.cursor };
        this.commandLine = '-- VISUAL LINE --';
        break;
      case 'Ctrl-V':
        this.mode = Mode.VISUAL_BLOCK;
        this._visualStart = { ...this.cursor };
        this._visualBlockDollar = false;
        this.commandLine = '-- VISUAL BLOCK --';
        break;

      // Search
      case '/':
        this.mode = Mode.COMMAND;
        this._searchForward = true;
        this._searchInput = '';
        this.commandLine = '/';
        return;
      case '?':
        this.mode = Mode.COMMAND;
        this._searchForward = false;
        this._searchInput = '';
        this.commandLine = '?';
        return;
      case 'n': { this._addJumpEntry(); const c = this._getCount(); let found = false; for (let i = 0; i < c; i++) found = this._searchNext(this._searchForward); if (!found && this._searchPattern) { this.commandLine = 'E486: Pattern not found: ' + this._searchPattern; this._stickyCommandLine = true; } this._showCurSearch = true; this._hlsearchActive = true; break; }
      case 'N': { this._addJumpEntry(); const c = this._getCount(); let found = false; for (let i = 0; i < c; i++) found = this._searchNext(!this._searchForward); if (!found && this._searchPattern) { this.commandLine = 'E486: Pattern not found: ' + this._searchPattern; this._stickyCommandLine = true; } this._showCurSearch = true; this._hlsearchActive = true; break; }
      case '*': {
        const w = this._wordUnderCursor();
        if (w) { this._addJumpEntry(); this._searchPattern = '\\b' + w + '\\b'; this._searchForward = true; this._searchNext(true); this._showCurSearch = true; this._hlsearchActive = true; }
        break;
      }
      case '#': {
        const w = this._wordUnderCursor();
        if (w) { this._addJumpEntry(); this._searchPattern = '\\b' + w + '\\b'; this._searchForward = false; this._searchNext(false); this._showCurSearch = true; this._hlsearchActive = true; }
        break;
      }

      // Scrolling
      case 'Ctrl-D': {
        if (this._hasCount()) this._scrollHalf = this._getCount();
        const c = this._scrollHalf || Math.floor(this._textRows / 2);
        this.cursor.row = Math.min(this.cursor.row + c, this.buffer.lineCount - 1);
        this.scrollTop = Math.min(this.scrollTop + c, Math.max(0, this.buffer.lineCount - this._textRows));
        this.cursor.col = this._firstNonBlank(this.cursor.row);
        this._updateDesiredCol();
        break;
      }
      case 'Ctrl-U': {
        if (this._hasCount()) this._scrollHalf = this._getCount();
        const c = this._scrollHalf || Math.floor(this._textRows / 2);
        this.cursor.row = Math.max(this.cursor.row - c, 0);
        this.scrollTop = Math.max(this.scrollTop - c, 0);
        this.cursor.col = this._firstNonBlank(this.cursor.row);
        this._updateDesiredCol();
        break;
      }
      case 'Ctrl-F': {
        const c = this._getCount();
        const scroll = (this._textRows - 2) * c;
        const oldBottom = this.scrollTop + this._textRows - 1;
        const maxST = Math.max(0, this.buffer.lineCount - 1);
        if (oldBottom >= this.buffer.lineCount - 1) {
          // Last line already visible — jump to show last line at top
          this.scrollTop = maxST;
        } else {
          this.scrollTop = Math.min(this.scrollTop + scroll, maxST);
        }
        this.cursor.row = Math.min(this.scrollTop, this.buffer.lineCount - 1);
        this.cursor.col = this._firstNonBlank(this.cursor.row);
        this._updateDesiredCol();
        break;
      }
      case 'Ctrl-B': {
        const c = this._getCount();
        const scroll = this._textRows * c;
        const oldST = this.scrollTop;
        this.scrollTop = Math.max(this.scrollTop - scroll, 0);
        if (this.scrollTop === 0 && oldST === 0) break;
        this.cursor.row = Math.min(this.scrollTop + this._textRows - 1, this.buffer.lineCount - 1);
        this.cursor.col = this._firstNonBlank(this.cursor.row);
        this._updateDesiredCol();
        break;
      }
      case 'Ctrl-E': {
        const c = this._getCount();
        const maxST = Math.max(0, this.buffer.lineCount - 1);
        this.scrollTop = Math.min(this.scrollTop + c, maxST);
        if (this.cursor.row < this.scrollTop) {
          this.cursor.row = this.scrollTop;
          this._applyDesiredCol();
        }
        break;
      }
      case 'Ctrl-Y': {
        const c = this._getCount();
        this.scrollTop = Math.max(this.scrollTop - c, 0);
        if (this.cursor.row >= this.scrollTop + this._textRows) {
          this.cursor.row = this.scrollTop + this._textRows - 1;
          this._applyDesiredCol();
        }
        break;
      }

      // Marks
      case 'm': this._pendingM = true; return;
      case '\'': this._pendingQuote = true; return;
      case '`': this._pendingBacktick = true; return;

      // Macros
      case 'q': this._pendingQ = true; return;
      case '@': this._pendingAt = true; return;

      // Register selection
      case '"': this._pendingDblQuote = true; return;

      // Q = replay last recorded macro
      case 'Q': {
        if (this._lastRecordedRegister && this._macroRegisters[this._lastRecordedRegister]) {
          const reg = this._lastRecordedRegister;
          const count = this._getCount();
          const keys = this._macroRegisters[reg];
          this._saveSnapshot();
          this._redoStack = [];
          const wasPlaying = this._macroPlaying;
          this._macroPlaying = true;
          this._macroAborted = false;
          for (let c = 0; c < count && !this._macroAborted; c++) {
            for (const k of keys) {
              if (this._macroAborted) break;
              this.feedKey(k);
            }
          }
          this._macroPlaying = wasPlaying;
          this._macroAborted = false;
        } else {
          this._messagePrompt = { error: "E354: Invalid register name: '^@'" };
        }
        this._pendingCount = '';
        break;
      }

      case 'Ctrl-L':
        this.commandLine = '';
        this._stickyCommandLine = false;
        break;
      case 'Ctrl-W':
        this._pendingCtrlW = true;
        return;
      case 'Ctrl-C':
        // Cancel any pending operation
        this._pendingOp = '';
        this._pendingCount = '';
        this._pendingG = false;
        this._pendingZ = false;
        this._pendingCtrlW = false;
        this._pendingSurround = '';
        this._surroundTarget = '';
        this._pendingR = false;
        this._pendingBracket = '';
        this._pendingTagInput = null;
        this._pendingDblQuote = false;
        this.commandLine = '';
        this._stickyCommandLine = false;
        break;

      // File info
      case 'Ctrl-G': {
        const name = this.filename || '[No Name]';
        const total = this.buffer.lineCount;
        let bytes = 0;
        for (let i = 0; i < total; i++) bytes += this.buffer.lines[i].length + (i < total - 1 ? 1 : 0);
        this._messagePrompt = { info: `"${name}" ${total}L, ${bytes}B` };
        this.commandLine = '';
        this._pendingCount = '';
        break;
      }

      // Alternate buffer (Ctrl-^ / Ctrl-6)
      case 'Ctrl-^':
      case 'Ctrl-6': {
        if (this._alternateBufId != null) {
          this._switchToBuffer(this._alternateBufId);
        } else {
          this.commandLine = 'E23: No alternate file';
          this._stickyCommandLine = true;
        }
        this._pendingCount = '';
        break;
      }

      // Increment / Decrement number
      case 'Ctrl-A': {
        const countStr = this._pendingCount;
        const count = this._getCount();
        this._saveSnapshot();
        if (countStr) this._dotPrefix = [...countStr];
        this._startRecording(); this._saveForDot('Ctrl-A');
        this._incrementNumber(count);
        this._stopRecording(); this._redoStack = [];
        break;
      }
      case 'Ctrl-X': {
        const countStr = this._pendingCount;
        const count = this._getCount();
        this._saveSnapshot();
        if (countStr) this._dotPrefix = [...countStr];
        this._startRecording(); this._saveForDot('Ctrl-X');
        this._incrementNumber(-count);
        this._stopRecording(); this._redoStack = [];
        break;
      }

      // Jump list
      case 'Ctrl-O': {
        if (this._jumpList.length > 0 && this._jumpListPos > 0) {
          if (this._jumpListPos >= this._jumpList.length) {
            // Save current position before jumping back.
            // Same-line dedup: if last entry is on same row, update col (nvim setpcmark).
            const last = this._jumpList[this._jumpList.length - 1];
            if (last.row === this.cursor.row) {
              last.col = this.cursor.col;
            } else {
              this._jumpList.push({ row: this.cursor.row, col: this.cursor.col });
            }
            this._jumpListPos = this._jumpList.length - 1;
          }
          if (this._jumpListPos > 0) {
            this._jumpListPos--;
            const entry = this._jumpList[this._jumpListPos];
            this.cursor.row = Math.min(entry.row, this.buffer.lineCount - 1);
            this.cursor.col = Math.min(entry.col, this._maxCol());
            this._updateDesiredCol();
          }
        }
        this._pendingCount = '';
        break;
      }
      case 'Tab':
      case 'Ctrl-I': {
        if (this._jumpListPos < this._jumpList.length - 1) {
          this._jumpListPos++;
          const entry = this._jumpList[this._jumpListPos];
          this.cursor.row = Math.min(entry.row, this.buffer.lineCount - 1);
          this.cursor.col = Math.min(entry.col, this._maxCol());
          this._updateDesiredCol();
        }
        this._pendingCount = '';
        break;
      }

      // Sentence motions
      case ')': {
        const c = this._getCount();
        for (let i = 0; i < c; i++) this._moveSentenceForward();
        this._updateDesiredCol();
        break;
      }
      case '(': {
        const c = this._getCount();
        for (let i = 0; i < c; i++) this._moveSentenceBackward();
        this._updateDesiredCol();
        break;
      }

      // Bracket commands
      case '[':
      case ']':
        this._pendingBracket = key;
        this._opStartPos = { ...this.cursor };
        return;

      // Command mode
      case ':':
        this.mode = Mode.COMMAND;
        this._searchInput = '';
        this.commandLine = ':';
        return;

      default:
        this._pendingCount = '';
        break;
    }
  }

  // ── g prefix ──

  _handleG(key) {
    switch (key) {
      case 'g': {
        if (this._pendingOp) {
          // gg as motion for operator (e.g. dgg) - linewise
          const startPos = this._opStartPos;
          if (this._hasCount()) {
            const n = this._getCount();
            this.cursor.row = Math.max(0, Math.min(n - 1, this.buffer.lineCount - 1));
          } else {
            this.cursor.row = 0;
          }
          this.cursor.col = 0;
          this._motionLinewise = true;
          this._executeOperator(startPos, { ...this.cursor });
          this._pendingOp = '';
          break;
        }
        this._addJumpEntry();
        if (this._hasCount()) {
          const n = this._getCount();
          this.cursor.row = Math.max(0, Math.min(n - 1, this.buffer.lineCount - 1));
          this.cursor.col = 0;
          this._updateDesiredCol();
        } else {
          this.cursor.row = 0;
          this._applyDesiredCol();
        }
        this._pendingCount = '';
        break;
      }
      case '_': {
        // g_ = go to last non-blank character on line
        const count = this._getCount();
        if (count > 1) {
          this.cursor.row = Math.min(this.cursor.row + count - 1, this.buffer.lineCount - 1);
        }
        this.cursor.col = this._lastNonBlank(this.cursor.row);
        this._updateDesiredCol();
        if (this._pendingOp) {
          this._motionInclusive = true;
          this._executeOperator(this._opStartPos, { ...this.cursor });
          this._pendingOp = '';
        }
        this._pendingCount = '';
        break;
      }
      case 'e': {
        const c = this._getCount();
        const geStart = { row: this.cursor.row, col: this.cursor.col };
        for (let i = 0; i < c; i++) this._moveWordEndBackward(false);
        this._updateDesiredCol();
        if (this._pendingOp) {
          // Only operate if ge actually moved
          if (this.cursor.row !== geStart.row || this.cursor.col !== geStart.col) {
            // ge is backward inclusive: delete from ge destination to cursor (inclusive of both ends)
            const adjStart = { row: this._opStartPos.row, col: this._opStartPos.col + 1 };
            this._executeOperator(adjStart, { ...this.cursor });
          }
          this._pendingOp = '';
        }
        break;
      }
      case 'E': {
        const c = this._getCount();
        const gEStart = { row: this.cursor.row, col: this.cursor.col };
        for (let i = 0; i < c; i++) this._moveWordEndBackward(true);
        this._updateDesiredCol();
        if (this._pendingOp) {
          if (this.cursor.row !== gEStart.row || this.cursor.col !== gEStart.col) {
            const adjStart = { row: this._opStartPos.row, col: this._opStartPos.col + 1 };
            this._executeOperator(adjStart, { ...this.cursor });
          }
          this._pendingOp = '';
        }
        break;
      }
      case 'J': {
        const c = Math.max(2, this._getCount()) - 1; // NgJ joins N lines = N-1 joins
        this._saveSnapshot();
        this._startRecording(); this._saveForDot('g'); this._saveForDot('J');
        for (let i = 0; i < c; i++) {
          if (this.cursor.row < this.buffer.lineCount - 1) {
            const cur = this.buffer.lines[this.cursor.row];
            const next = this.buffer.lines[this.cursor.row + 1];
            const joinCol = cur.length;
            this.buffer.lines[this.cursor.row] = cur + next;
            this.buffer.lines.splice(this.cursor.row + 1, 1);
            this.cursor.col = joinCol;
          }
        }
        this._stopRecording(); this._redoStack = [];
        this._updateDesiredCol();
        break;
      }
      case 'u': {
        this._pendingOp = 'gu';
        this._opStartPos = { ...this.cursor };
        break;
      }
      case 'U': {
        this._pendingOp = 'gU';
        this._opStartPos = { ...this.cursor };
        break;
      }
      case '~': {
        this._pendingOp = 'g~';
        this._opStartPos = { ...this.cursor };
        break;
      }
      case 'o': {
        // go — go to byte offset N
        const targetByte = this._getCount() - 1; // 1-based to 0-based
        const eolSize = this._settings.fileformat === 'dos' ? 2 : 1;
        let bytePos = 0;
        for (let r = 0; r < this.buffer.lineCount; r++) {
          const lineLen = this.buffer.lines[r].length + eolSize; // +eolSize for line ending
          if (bytePos + lineLen > targetByte) {
            this.cursor.row = r;
            this.cursor.col = Math.min(targetByte - bytePos, this.buffer.lines[r].length - 1);
            this.cursor.col = Math.max(0, this.cursor.col);
            break;
          }
          bytePos += lineLen;
        }
        this._updateDesiredCol();
        this._pendingCount = '';
        break;
      }
      case 'v': {
        // gv — reselect last visual selection
        if (this._lastVisual) {
          this.mode = this._lastVisual.mode;
          this._visualStart = { ...this._lastVisual.start };
          this.cursor = { ...this._lastVisual.end };
          this.commandLine = this.mode === Mode.VISUAL_LINE ? '-- VISUAL LINE --' : '-- VISUAL --';
        }
        break;
      }
      case 'i':
        this._saveSnapshot(); this._startRecording();
        if (this._lastInsertPos) {
          this.cursor.row = Math.min(this._lastInsertPos.row, this.buffer.lineCount - 1);
          this.cursor.col = Math.min(this._lastInsertPos.col, this.buffer.lines[this.cursor.row].length);
        }
        this.mode = Mode.INSERT; this.commandLine = '-- INSERT --';
        break;
      case 'I':
        this._saveSnapshot(); this._startRecording();
        this.cursor.col = 0;
        this.mode = Mode.INSERT; this.commandLine = '-- INSERT --';
        break;
      case 'a': {
        // ga — show ASCII value of char under cursor
        const line = this.buffer.lines[this.cursor.row];
        let gaMsg;
        if (line.length === 0) {
          gaMsg = 'NUL';
        } else {
          const ch = line[this.cursor.col] || line[line.length - 1];
          const code = ch.charCodeAt(0);
          const dec = code;
          const hex = code.toString(16);
          const oct = code.toString(8);
          const display = code < 32 ? '^' + String.fromCharCode(code + 64) : ch;
          gaMsg = `<${display}>  ${dec},  Hex ${hex.padStart(2, '0')},  Oct ${oct.padStart(3, '0')}`;
        }
        // nvim shows "Press ENTER" (overlay) for chars with digraph info
        // (space, control chars, DEL, high bytes); regular printable chars
        // (0x21–0x7E) display inline in the cmdline.
        const gaCode = (line.length > 0) ? (line[this.cursor.col] || line[line.length - 1]).charCodeAt(0) : 0;
        if (gaCode >= 0x21 && gaCode <= 0x7E) {
          this.commandLine = gaMsg;
          this._stickyCommandLine = true;
        } else {
          this._messagePrompt = { info: gaMsg };
          this.commandLine = '';
        }
        this._pendingCount = '';
        break;
      }
      case 'd': {
        // gd — go to local declaration of word under cursor
        // If cursor is not on a word char, search forward for the next word
        let w = this._wordUnderCursor();
        if (!w) {
          const line = this.buffer.lines[this.cursor.row];
          let c = this.cursor.col;
          while (c < line.length && !this._isWordChar(line[c])) c++;
          if (c < line.length) {
            let e = c;
            while (e < line.length && this._isWordChar(line[e])) e++;
            w = line.slice(c, e);
          }
        }
        if (w) {
          // Set search pattern and highlighting (like nvim)
          const escaped = w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
          this._searchPattern = '\\b' + escaped + '\\b';
          this._showCurSearch = true;
          this._hlsearchActive = true;
          // Search from top of buffer for the first occurrence
          const re = new RegExp('\\b' + escaped + '\\b');
          for (let r = 0; r < this.buffer.lineCount; r++) {
            const m = this.buffer.lines[r].match(re);
            if (m) {
              this._addJumpEntry();
              this.cursor.row = r;
              this.cursor.col = m.index;
              this._curSearchPos = { row: r, col: m.index };
              this._updateDesiredCol();
              break;
            }
          }
        }
        this._pendingCount = '';
        break;
      }
      case ';': {
        // g; — go to older position in change list
        if (this._changeList.length === 0) {
          this.commandLine = 'E664: changelist is empty';
          this._stickyCommandLine = true;
        } else if (this._changeListPos > 0) {
          this._changeListPos--;
          const entry = this._changeList[this._changeListPos];
          this.cursor.row = Math.min(entry.row, this.buffer.lineCount - 1);
          this.cursor.col = Math.min(entry.col, this._maxCol());
          this._updateDesiredCol();
        } else {
          this.commandLine = 'E662: At start of changelist';
          this._stickyCommandLine = true;
        }
        this._pendingCount = '';
        break;
      }
      case ',': {
        // g, — go to newer position in change list
        if (this._changeList.length > 0 && this._changeListPos < this._changeList.length - 1) {
          this._changeListPos++;
          const entry = this._changeList[this._changeListPos];
          this.cursor.row = Math.min(entry.row, this.buffer.lineCount - 1);
          this.cursor.col = Math.min(entry.col, this._maxCol());
          this._updateDesiredCol();
        }
        this._pendingCount = '';
        break;
      }
      case '*': {
        // g* — search word under cursor forward (no word boundaries)
        const w = this._wordUnderCursor();
        if (w) {
          this._addJumpEntry();
          const escaped = w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
          this._searchPattern = escaped;
          this._searchForward = true;
          const c = this._getCount();
          for (let i = 0; i < c; i++) this._searchNext(true);
          this._showCurSearch = true;
          this._hlsearchActive = true;
        }
        break;
      }
      case '#': {
        // g# — search word under cursor backward (no word boundaries)
        const w = this._wordUnderCursor();
        if (w) {
          this._addJumpEntry();
          const escaped = w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
          this._searchPattern = escaped;
          this._searchForward = false;
          const c = this._getCount();
          for (let i = 0; i < c; i++) this._searchNext(false);
          this._showCurSearch = true;
          this._hlsearchActive = true;
        }
        break;
      }
      case 'p': {
        // gp — put after, cursor after pasted text
        const count = this._getCount();
        const explicitReg = this._pendingRegKey;
        const reg = this._getReg();
        if (explicitReg && !reg.text && explicitReg !== '_') {
          this.commandLine = 'E353: Nothing in register ' + explicitReg;
          this._stickyCommandLine = true;
          break;
        }
        this._saveSnapshot();
        this._startRecording(); this._saveForDot('g'); this._saveForDot('p');
        for (let i = 0; i < count; i++) this._putAfter(reg);
        // Move cursor after pasted text
        if (reg.type === 'line') {
          // For linewise: cursor goes to line after last pasted line
          const pastedLines = reg.text.split('\n').length * count;
          // After _putAfter for linewise, cursor is on first pasted line (row was incremented)
          // We need to go to the line after the last pasted line
          const lastPastedRow = this.cursor.row + pastedLines - 1;
          if (lastPastedRow < this.buffer.lineCount - 1) {
            this.cursor.row = lastPastedRow + 1;
          } else {
            this.cursor.row = this.buffer.lineCount - 1;
          }
          this.cursor.col = this._firstNonBlank(this.cursor.row);
        } else {
          // For charwise: cursor is already on last char of pasted text after _putAfter;
          // move one position forward (after the pasted text)
          this.cursor.col = Math.min(this.cursor.col + 1, this.buffer.lineLength(this.cursor.row) > 0 ? this.buffer.lineLength(this.cursor.row) - 1 : 0);
        }
        this._updateDesiredCol();
        this._stopRecording(); this._redoStack = [];
        break;
      }
      case 'P': {
        // gP — put before, cursor after pasted text
        const count = this._getCount();
        const explicitReg = this._pendingRegKey;
        const reg = this._getReg();
        if (explicitReg && !reg.text && explicitReg !== '_') {
          this.commandLine = 'E353: Nothing in register ' + explicitReg;
          this._stickyCommandLine = true;
          break;
        }
        this._saveSnapshot();
        this._startRecording(); this._saveForDot('g'); this._saveForDot('P');
        for (let i = 0; i < count; i++) this._putBefore(reg);
        // Move cursor after pasted text
        if (reg.type === 'line') {
          // For linewise: cursor goes to line after last pasted line
          const pastedLines = reg.text.split('\n').length * count;
          const lastPastedRow = this.cursor.row + pastedLines - 1;
          if (lastPastedRow < this.buffer.lineCount - 1) {
            this.cursor.row = lastPastedRow + 1;
          } else {
            this.cursor.row = this.buffer.lineCount - 1;
          }
          this.cursor.col = this._firstNonBlank(this.cursor.row);
        } else {
          // For charwise: move one past end of pasted text
          this.cursor.col = Math.min(this.cursor.col + 1, this.buffer.lineLength(this.cursor.row) > 0 ? this.buffer.lineLength(this.cursor.row) - 1 : 0);
        }
        this._updateDesiredCol();
        this._stopRecording(); this._redoStack = [];
        break;
      }
      case 'n': {
        // gn — search forward and select match (or operate on match)
        if (!this._searchPattern) break;
        const match = this._findSearchMatch(true);
        if (!match) break;
        if (this._pendingOp) {
          // Operator-pending: operate on the match range
          const opChar = this._pendingOp;
          const startPos = { row: match.row, col: match.col };
          const endPos = { row: match.row, col: match.col + match.len - 1 };
          this._motionInclusive = true;
          this._motionLinewise = false;
          this.cursor = { ...endPos };
          const dotKeys = [opChar, 'g', 'n'];
          if (opChar === 'c') {
            this._dotPrefix = dotKeys;
          }
          this._executeOperator(startPos, endPos);
          if (opChar !== 'c' && opChar !== 'y') {
            this._lastChange = dotKeys;
          }
          this._pendingOp = '';
          this._showCurSearch = false;
          this._curSearchPos = null;
        } else {
          // Normal mode: visually select the match
          this.mode = Mode.VISUAL;
          this._visualStart = { row: match.row, col: match.col };
          this.cursor.row = match.row;
          this.cursor.col = match.col + match.len - 1;
          this.commandLine = '-- VISUAL --';
          this._showCurSearch = true;
          this._curSearchPos = { row: match.row, col: match.col };
        }
        this._hlsearchActive = true;
        break;
      }
      case 'N': {
        // gN — search backward and select match (or operate on match)
        if (!this._searchPattern) break;
        const match = this._findSearchMatch(false);
        if (!match) break;
        if (this._pendingOp) {
          // Operator-pending: operate on the match range
          const opChar = this._pendingOp;
          const startPos = { row: match.row, col: match.col };
          const endPos = { row: match.row, col: match.col + match.len - 1 };
          this._motionInclusive = true;
          this._motionLinewise = false;
          this.cursor = { ...endPos };
          const dotKeys = [opChar, 'g', 'N'];
          if (opChar === 'c') {
            this._dotPrefix = dotKeys;
          }
          this._executeOperator(startPos, endPos);
          if (opChar !== 'c' && opChar !== 'y') {
            this._lastChange = dotKeys;
          }
          this._pendingOp = '';
          this._showCurSearch = false;
          this._curSearchPos = null;
        } else {
          // Normal mode: visually select the match
          this.mode = Mode.VISUAL;
          this._visualStart = { row: match.row, col: match.col + match.len - 1 };
          this.cursor.row = match.row;
          this.cursor.col = match.col;
          this.commandLine = '-- VISUAL --';
          this._showCurSearch = true;
          this._curSearchPos = { row: match.row, col: match.col };
        }
        this._hlsearchActive = true;
        break;
      }
      // ── Display-line motions ──

      case 'j': {
        // gj — move down one display line
        const count = this._getCount();
        if (this._pendingOp) {
          // Operator-pending: gj is an exclusive motion (unlike j which is linewise)
          const startPos = this._opStartPos;
          for (let i = 0; i < count; i++) {
            const info = this._displayLineInfo(this.cursor.row, this.cursor.col);
            if (info.displayRow < info.totalDisplayRows - 1) {
              // Move to next display row within same buffer line
              this.cursor.col = this._bufColForDisplayCol(this.cursor.row, info.displayRow + 1,
                Math.min(this._desiredCol, this._getTextCols() - 1));
            } else if (this.cursor.row < this.buffer.lineCount - 1) {
              // Move to first display row of next buffer line
              this.cursor.row++;
              this.cursor.col = this._bufColForDisplayCol(this.cursor.row, 0,
                Math.min(this._desiredCol, this._getTextCols() - 1));
            }
          }
          this._executeOperator(startPos, { ...this.cursor });
          this._pendingOp = '';
        } else {
          for (let i = 0; i < count; i++) {
            const info = this._displayLineInfo(this.cursor.row, this.cursor.col);
            if (info.displayRow < info.totalDisplayRows - 1) {
              // Move to next display row within same buffer line
              this.cursor.col = this._bufColForDisplayCol(this.cursor.row, info.displayRow + 1,
                Math.min(this._desiredCol, this._getTextCols() - 1));
            } else if (this.cursor.row < this.buffer.lineCount - 1) {
              // Move to first display row of next buffer line
              this.cursor.row++;
              this.cursor.col = this._bufColForDisplayCol(this.cursor.row, 0,
                Math.min(this._desiredCol, this._getTextCols() - 1));
            }
          }
        }
        // Don't update desiredCol — gj preserves it like j
        this._pendingCount = '';
        break;
      }
      case 'k': {
        // gk — move up one display line
        const count = this._getCount();
        if (this._pendingOp) {
          // Operator-pending: gk is an exclusive motion (unlike k which is linewise)
          const startPos = this._opStartPos;
          for (let i = 0; i < count; i++) {
            const info = this._displayLineInfo(this.cursor.row, this.cursor.col);
            if (info.displayRow > 0) {
              // Move to previous display row within same buffer line
              this.cursor.col = this._bufColForDisplayCol(this.cursor.row, info.displayRow - 1,
                Math.min(this._desiredCol, this._getTextCols() - 1));
            } else if (this.cursor.row > 0) {
              // Move to last display row of previous buffer line
              this.cursor.row--;
              const prevInfo = this._displayLineInfo(this.cursor.row, this.buffer.lineLength(this.cursor.row));
              this.cursor.col = this._bufColForDisplayCol(this.cursor.row, prevInfo.totalDisplayRows - 1,
                Math.min(this._desiredCol, this._getTextCols() - 1));
            }
          }
          this._executeOperator(startPos, { ...this.cursor });
          this._pendingOp = '';
        } else {
          for (let i = 0; i < count; i++) {
            const info = this._displayLineInfo(this.cursor.row, this.cursor.col);
            if (info.displayRow > 0) {
              // Move to previous display row within same buffer line
              this.cursor.col = this._bufColForDisplayCol(this.cursor.row, info.displayRow - 1,
                Math.min(this._desiredCol, this._getTextCols() - 1));
            } else if (this.cursor.row > 0) {
              // Move to last display row of previous buffer line
              this.cursor.row--;
              const prevInfo = this._displayLineInfo(this.cursor.row, this.buffer.lineLength(this.cursor.row));
              this.cursor.col = this._bufColForDisplayCol(this.cursor.row, prevInfo.totalDisplayRows - 1,
                Math.min(this._desiredCol, this._getTextCols() - 1));
            }
          }
        }
        // Don't update desiredCol — gk preserves it like k
        this._pendingCount = '';
        break;
      }
      case 'Ctrl-A':
      case 'Ctrl-X': {
        // g Ctrl-A / g Ctrl-X — sequential increment/decrement in visual mode
        if (this.mode === Mode.VISUAL || this.mode === Mode.VISUAL_LINE || this.mode === Mode.VISUAL_BLOCK) {
          this._lastVisual = { mode: this.mode, start: { ...this._visualStart }, end: { ...this.cursor } };
          const sr = Math.min(this._visualStart.row, this.cursor.row);
          const er = Math.max(this._visualStart.row, this.cursor.row);
          const savedCursor = { ...this.cursor };
          this.cursor = { row: sr, col: 0 };
          this._saveSnapshot();
          this.cursor = savedCursor;
          const sign = (key === 'Ctrl-A') ? 1 : -1;
          let seq = 1;
          for (let r = sr; r <= er; r++) {
            const line = this.buffer.lines[r];
            const re = /-?\d+/g;
            const m = re.exec(line);
            if (m) {
              const s = m.index;
              const e = s + m[0].length - 1;
              const num = parseInt(m[0], 10) + sign * seq;
              const newText = num.toString();
              this.buffer.lines[r] = line.slice(0, s) + newText + line.slice(e + 1);
            }
            seq++;
          }
          const lineCount = er - sr + 1;
          this.cursor.row = sr;
          this.cursor.col = 0;
          this.mode = Mode.NORMAL;
          if (lineCount >= 2) {
            this.commandLine = lineCount + ' lines changed';
            this._stickyCommandLine = true;
          } else {
            this.commandLine = '';
          }
          this._redoStack = [];
        }
        this._pendingCount = '';
        break;
      }
      case '0': {
        // g0 — move to start of current display line
        const info = this._displayLineInfo(this.cursor.row, this.cursor.col);
        this.cursor.col = info.displayLineStart;
        this._updateDesiredCol();
        if (this._pendingOp) {
          this._executeOperator(this._opStartPos, { ...this.cursor });
          this._pendingOp = '';
        }
        this._pendingCount = '';
        break;
      }
      case '$': {
        // g$ — move to end of current display line
        const info = this._displayLineInfo(this.cursor.row, this.cursor.col);
        this.cursor.col = info.displayLineEnd;
        this._updateDesiredCol();
        if (this._pendingOp) {
          this._motionInclusive = true;
          this._executeOperator(this._opStartPos, { ...this.cursor });
          this._pendingOp = '';
        }
        this._pendingCount = '';
        break;
      }
      case '^': {
        // g^ — move to first non-blank of current display line
        const info = this._displayLineInfo(this.cursor.row, this.cursor.col);
        const raw = this.buffer.lines[this.cursor.row] || '';
        // Find first non-blank character at or after displayLineStart
        let col = info.displayLineStart;
        while (col <= info.displayLineEnd && col < raw.length &&
               (raw[col] === ' ' || raw[col] === '\t')) {
          col++;
        }
        // If all chars in this display line are blank, stay at displayLineStart
        if (col > info.displayLineEnd) col = info.displayLineStart;
        this.cursor.col = col;
        this._updateDesiredCol();
        if (this._pendingOp) {
          this._executeOperator(this._opStartPos, { ...this.cursor });
          this._pendingOp = '';
        }
        this._pendingCount = '';
        break;
      }
      case 'm': {
        // gm — move to middle of screen width
        // Moves cursor to the character at screen column textCols/2
        // (middle of the screen, not middle of the text)
        const textCols = this._getTextCols();
        const info = this._displayLineInfo(this.cursor.row, this.cursor.col);
        const midScreenCol = Math.floor(textCols / 2);
        this.cursor.col = this._bufColForDisplayCol(this.cursor.row, info.displayRow, midScreenCol);
        // Clamp to end of line
        const maxC = this.buffer.lineLength(this.cursor.row) > 0 ? this.buffer.lineLength(this.cursor.row) - 1 : 0;
        if (this.cursor.col > maxC) this.cursor.col = maxC;
        this._updateDesiredCol();
        if (this._pendingOp) {
          this._motionInclusive = true;
          this._executeOperator(this._opStartPos, { ...this.cursor });
          this._pendingOp = '';
        }
        this._pendingCount = '';
        break;
      }
      case 'M': {
        // gM — move to middle of actual text on the line
        // For a line of length L, go to floor((L-1)/2)
        const lineLen = this.buffer.lineLength(this.cursor.row);
        if (lineLen === 0) {
          this.cursor.col = 0;
        } else {
          this.cursor.col = Math.floor((lineLen - 1) / 2);
        }
        this._updateDesiredCol();
        if (this._pendingOp) {
          this._motionInclusive = true;
          this._executeOperator(this._opStartPos, { ...this.cursor });
          this._pendingOp = '';
        }
        this._pendingCount = '';
        break;
      }

      case '?': {
        // g? — rot13 operator
        if (this.mode === Mode.VISUAL || this.mode === Mode.VISUAL_LINE) {
          // Visual mode: apply rot13 to selection immediately
          this._lastVisual = { mode: this.mode, start: { ...this._visualStart }, end: { ...this.cursor } };
          let sr, sc, er, ec;
          if (this.mode === Mode.VISUAL_LINE) {
            sr = Math.min(this._visualStart.row, this.cursor.row);
            er = Math.max(this._visualStart.row, this.cursor.row);
            sc = 0; ec = this.buffer.lineLength(er);
          } else {
            if (this._visualStart.row < this.cursor.row || (this._visualStart.row === this.cursor.row && this._visualStart.col <= this.cursor.col)) {
              sr = this._visualStart.row; sc = this._visualStart.col;
              er = this.cursor.row; ec = this.cursor.col;
            } else {
              sr = this.cursor.row; sc = this.cursor.col;
              er = this._visualStart.row; ec = this._visualStart.col;
            }
          }
          const savedCursor = { ...this.cursor };
          this.cursor = { row: sr, col: sc };
          this._saveSnapshot();
          this.cursor = savedCursor;
          if (this.mode === Mode.VISUAL_LINE) {
            for (let r = sr; r <= er; r++) this.buffer.lines[r] = this._rot13(this.buffer.lines[r]);
          } else {
            for (let r = sr; r <= er; r++) {
              const line = this.buffer.lines[r];
              const s = (r === sr) ? sc : 0;
              const e = (r === er) ? ec : line.length - 1;
              this.buffer.lines[r] = line.slice(0, s) + this._rot13(line.slice(s, e + 1)) + line.slice(e + 1);
            }
          }
          this.mode = Mode.NORMAL; this.commandLine = '';
          this.cursor.row = sr; this.cursor.col = sc;
          this._redoStack = [];
          this._updateDesiredCol();
        } else if (this._pendingOp === 'g?') {
          // g?g? — current line
          this._doLineOperation('g?', this._getCount());
          this._pendingOp = '';
        } else {
          this._pendingOp = 'g?';
          this._opStartPos = { ...this.cursor };
        }
        break;
      }
      case 'q': {
        // gq — format operator
        if (this._pendingOp === 'gq') {
          // gqgq — current line
          this._doLineOperation('gq', this._getCount());
          this._pendingOp = '';
        } else {
          this._pendingOp = 'gq';
          this._opStartPos = { ...this.cursor };
        }
        break;
      }
      case 'w': {
        // gw — format operator (cursor stays)
        if (this._pendingOp === 'gw') {
          // gwgw — current line
          this._doLineOperation('gw', this._getCount());
          this._pendingOp = '';
        } else if (this._pendingOp) {
          // operator + gw motion: w is the motion
          const c = this._getCount();
          for (let i = 0; i < c; i++) this._moveWordForward(false);
          this._updateDesiredCol();
          this._executeOperator(this._opStartPos, { ...this.cursor });
          this._pendingOp = '';
        } else {
          this._pendingOp = 'gw';
          this._opStartPos = { ...this.cursor };
        }
        break;
      }
      case 'D': {
        // gD — go to first occurrence of word under cursor in file (global declaration)
        let w2 = this._wordUnderCursor();
        if (!w2) {
          const line = this.buffer.lines[this.cursor.row];
          let c = this.cursor.col;
          while (c < line.length && !this._isWordChar(line[c])) c++;
          if (c < line.length) {
            let e = c;
            while (e < line.length && this._isWordChar(line[e])) e++;
            w2 = line.slice(c, e);
          }
        }
        if (w2) {
          const escaped = w2.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
          this._searchPattern = '\\b' + escaped + '\\b';
          this._showCurSearch = true;
          this._hlsearchActive = true;
          const re = new RegExp('\\b' + escaped + '\\b');
          for (let r = 0; r < this.buffer.lineCount; r++) {
            const m = this.buffer.lines[r].match(re);
            if (m) {
              this._addJumpEntry();
              this.cursor.row = r;
              this.cursor.col = m.index;
              this._curSearchPos = { row: r, col: m.index };
              this._updateDesiredCol();
              break;
            }
          }
        }
        this._pendingCount = '';
        break;
      }
      case '8': {
        // g8 — show hex of character under cursor
        const line = this.buffer.lines[this.cursor.row];
        if (this.cursor.col < line.length) {
          const ch = line[this.cursor.col];
          const hex = ch.charCodeAt(0).toString(16);
          this.commandLine = hex;
          this._stickyCommandLine = true;
        }
        this._pendingCount = '';
        break;
      }
      case '<': {
        // g< — redisplay last message output
        if (this._lastMessage) {
          this.commandLine = this._lastMessage;
          this._stickyCommandLine = true;
        }
        this._pendingCount = '';
        break;
      }
      case '&': {
        // g& — repeat last :s on all lines
        if (this._lastSubstitution) {
          const { pattern, replacement } = this._lastSubstitution;
          let jsPattern = this._vimPatternToJs(pattern);
          let jsReplacement = replacement
            .replace(/\\&/g, '\x00AMP')
            .replace(/\$/g, '$$$$')
            .replace(/&/g, '$$&')
            .replace(/\x00AMP/g, '&')
            .replace(/\\([1-9])/g, '$$$1');
          let caseFlag = this._searchCaseFlag();
          let regex;
          try { regex = new RegExp(jsPattern, caseFlag); } catch {
            this.commandLine = 'E486: Pattern not found: ' + pattern;
            this._stickyCommandLine = true;
            break;
          }
          this._saveSnapshot({ row: 0, col: 0 });
          this._redoStack = [];
          let totalSubs = 0, lastSubRow = 0;
          for (let r = 0; r < this.buffer.lineCount; r++) {
            const before = this.buffer.lines[r];
            const after = before.replace(regex, jsReplacement);
            if (after !== before) { this.buffer.lines[r] = after; totalSubs++; lastSubRow = r; }
          }
          if (totalSubs > 0) {
            this.cursor.row = lastSubRow;
            this.cursor.col = this._firstNonBlank(lastSubRow);
          }
          this.commandLine = ':s/' + pattern + '/' + replacement + '/';
          this._stickyCommandLine = true;
        } else {
          this._messagePrompt = { error: 'E33: No previous substitute regular expression' };
          this.commandLine = '';
        }
        this._pendingCount = '';
        break;
      }

      // gt — next tab page (with count: go to tab N)
      case 't': {
        if (this._hasCount()) {
          const n = this._getCount();
          // gt with count: go to tab page N (1-based)
          const idx = Math.max(0, Math.min(n - 1, this._tabs.length - 1));
          this._switchToTab(idx);
        } else {
          // Next tab (wrapping)
          const nextIdx = (this._activeTab + 1) % this._tabs.length;
          this._switchToTab(nextIdx);
        }
        this._pendingCount = '';
        break;
      }

      // gT — previous tab page
      case 'T': {
        const count = this._hasCount() ? this._getCount() : 1;
        const prevIdx = ((this._activeTab - count) % this._tabs.length + this._tabs.length) % this._tabs.length;
        this._switchToTab(prevIdx);
        this._pendingCount = '';
        break;
      }

      default:
        this._pendingCount = '';
        break;
    }
  }

  // ── Buffer list helpers ──

  /**
   * Register a buffer in the buffer list. Returns the assigned buffer id.
   */
  _registerBuffer(buffer, fileName) {
    // Check if this buffer is already registered
    for (const entry of this._bufferList) {
      if (entry.buffer === buffer) return entry.id;
    }
    const id = this._nextBufId++;
    this._bufferList.push({
      id,
      buffer,
      fileName: fileName || null,
      cursor: { row: 0, col: 0 },
      scrollTop: 0,
      scrollLeft: 0,
      undoStack: [],
      redoStack: [],
      changeCount: 0,
      marks: {},
      folds: [],
      desiredCol: 0,
      jumpList: [],
      jumpListPos: -1,
      changeList: [],
      changeListPos: -1,
    });
    return id;
  }

  /**
   * Find a buffer entry by id.
   */
  _getBufEntry(id) {
    return this._bufferList.find(e => e.id === id) || null;
  }

  /**
   * Save current engine state into the buffer list entry for _currentBufId.
   */
  _saveCurrentBufState() {
    const entry = this._getBufEntry(this._currentBufId);
    if (!entry) return;
    entry.buffer = this.buffer;
    entry.fileName = this._fileName;
    entry.cursor = { ...this.cursor };
    entry.scrollTop = this.scrollTop;
    entry.scrollLeft = this.scrollLeft;
    entry.undoStack = this._undoStack;
    entry.redoStack = this._redoStack;
    entry.changeCount = this._changeCount;
    entry.marks = this._marks;
    entry.folds = this._folds;
    entry.desiredCol = this._desiredCol;
    entry.jumpList = this._jumpList;
    entry.jumpListPos = this._jumpListPos;
    entry.changeList = this._changeList;
    entry.changeListPos = this._changeListPos;
  }

  /**
   * Switch to a buffer by id. Saves current state and restores the target buffer's state.
   */
  _switchToBuffer(id) {
    if (id === this._currentBufId) return;
    const entry = this._getBufEntry(id);
    if (!entry) return;
    // Save current buffer state
    this._saveCurrentBufState();
    // Set alternate buffer
    this._alternateBufId = this._currentBufId;
    this._currentBufId = id;
    // Restore target buffer state
    this.buffer = entry.buffer;
    this._fileName = entry.fileName;
    this.cursor = { ...entry.cursor };
    this.scrollTop = entry.scrollTop;
    this.scrollLeft = entry.scrollLeft;
    this._undoStack = entry.undoStack;
    this._redoStack = entry.redoStack;
    this._changeCount = entry.changeCount;
    this._marks = entry.marks;
    this._folds = entry.folds;
    this._desiredCol = entry.desiredCol;
    this._jumpList = entry.jumpList;
    this._jumpListPos = entry.jumpListPos;
    this._changeList = entry.changeList;
    this._changeListPos = entry.changeListPos;
    // Update active window
    this._windows[this._activeWin].buffer = this.buffer;
    this._windows[this._activeWin].cursor = { ...this.cursor };
    this._windows[this._activeWin].scrollTop = this.scrollTop;
    this._windows[this._activeWin].scrollLeft = this.scrollLeft;
    this._windows[this._activeWin].folds = this._folds;
    this._windows[this._activeWin]._desiredCol = this._desiredCol;
    // Reset mode to normal
    if (this.mode !== Mode.NORMAL) {
      this.mode = Mode.NORMAL;
    }
    // Clamp cursor
    this._clampCursor();
    this._updateStatus();
  }

  // ── z prefix ──

  _handleZ(key) {
    // Handle pending zu (for zug/zuw)
    if (this._pendingZu) {
      this._pendingZu = false;
      if (key === 'g') {
        // zug — undo zg (remove word from good list)
        const w = this._getWordAtCursor();
        if (w) {
          this._spellGoodWords.delete(w.word.toLowerCase());
          this.commandLine = '';
        }
      } else if (key === 'w') {
        // zuw — undo zw (remove word from bad list)
        const w = this._getWordAtCursor();
        if (w) {
          this._spellBadWords.delete(w.word.toLowerCase());
          this.commandLine = '';
        }
      }
      return;
    }

    const maxST = Math.max(0, this.buffer.lineCount - 1);
    switch (key) {
      case 'z': case '.':
        this.scrollTop = Math.max(0, Math.min(this.cursor.row - Math.floor((this._textRows - 1) / 2), maxST));
        this.cursor.col = this._firstNonBlank(this.cursor.row);
        this._updateDesiredCol();
        break;
      case 't': case 'Enter':
        this.scrollTop = Math.max(0, Math.min(this.cursor.row, maxST));
        this.cursor.col = this._firstNonBlank(this.cursor.row);
        this._updateDesiredCol();
        break;
      case 'b': case '-':
        this.scrollTop = Math.max(0, Math.min(this.cursor.row - this._textRows + 1, maxST));
        this.cursor.col = this._firstNonBlank(this.cursor.row);
        this._updateDesiredCol();
        break;
      case '+': {
        // z+ — line below window to top, first non-blank
        const textRows = this.rows - 1; // status line
        let bottomRow = this.scrollTop;
        for (let i = 0; i < textRows && bottomRow < this.buffer.lineCount - 1; bottomRow++) {
          i++;
        }
        const newTop = Math.min(bottomRow, this.buffer.lineCount - 1);
        this.scrollTop = newTop;
        this.cursor.row = newTop;
        this.cursor.col = this._firstNonBlank(this.cursor.row);
        this._updateDesiredCol();
        break;
      }
      case '^': {
        // z^ — line above window to bottom, first non-blank
        const textRows = this.rows - 1;
        const lineAbove = Math.max(0, this.scrollTop - 1);
        const newTop = Math.max(0, lineAbove - textRows + 1);
        this.scrollTop = newTop;
        this.cursor.row = lineAbove;
        this.cursor.col = this._firstNonBlank(this.cursor.row);
        this._updateDesiredCol();
        break;
      }
      case 'f':
        // zf is an operator - set pending and wait for motion
        this._pendingOp = 'zf';
        this._opStartPos = { ...this.cursor };
        return;
      case 'o': {
        const fold = this._findFoldAt(this.cursor.row);
        if (fold) fold.closed = false;
        break;
      }
      case 'O': {
        const folds = this._findAllFoldsAt(this.cursor.row);
        for (const f of folds) f.closed = false;
        break;
      }
      case 'c': {
        const fold = this._findFoldAt(this.cursor.row);
        if (fold) fold.closed = true;
        break;
      }
      case 'C': {
        const folds = this._findAllFoldsAt(this.cursor.row);
        for (const f of folds) f.closed = true;
        break;
      }
      case 'd': {
        const fold = this._findFoldAt(this.cursor.row);
        if (fold) {
          const idx = this._folds.indexOf(fold);
          if (idx >= 0) this._folds.splice(idx, 1);
        }
        break;
      }
      case 'D': {
        const folds = this._findAllFoldsAt(this.cursor.row);
        for (const f of folds) {
          const idx = this._folds.indexOf(f);
          if (idx >= 0) this._folds.splice(idx, 1);
        }
        break;
      }
      case 'E':
        this._folds = [];
        break;
      case 'R':
        for (const f of this._folds) f.closed = false;
        break;
      case 'M':
        for (const f of this._folds) f.closed = true;
        break;
      case 'a': {
        const fold = this._findFoldAt(this.cursor.row);
        if (fold) fold.closed = !fold.closed;
        break;
      }
      case 'A': {
        const folds = this._findAllFoldsAt(this.cursor.row);
        const anyOpen = folds.some(f => !f.closed);
        for (const f of folds) f.closed = anyOpen;
        break;
      }
      case 'j': {
        // Move to next fold start
        let nextFold = null;
        for (const f of this._folds) {
          if (f.startRow > this.cursor.row) {
            if (!nextFold || f.startRow < nextFold.startRow) nextFold = f;
          }
        }
        if (nextFold) {
          this.cursor.row = nextFold.startRow;
          this.cursor.col = this._firstNonBlank(this.cursor.row);
          this._updateDesiredCol();
        }
        break;
      }
      case 'k': {
        // Move to previous fold end
        let prevFold = null;
        for (const f of this._folds) {
          if (f.endRow < this.cursor.row) {
            if (!prevFold || f.endRow > prevFold.endRow) prevFold = f;
          }
        }
        if (prevFold) {
          this.cursor.row = prevFold.startRow;
          this.cursor.col = this._firstNonBlank(this.cursor.row);
          this._updateDesiredCol();
        }
        break;
      }

      // ── Horizontal scroll (nowrap only) ──

      case 'l': {
        // zl — scroll screen right by N columns
        if (!this._settings.wrap) {
          const count = this._getCount(1);
          this.scrollLeft += count;
          // Clamp cursor to stay on-screen (left edge)
          const lineLen = this.buffer.lines[this.cursor.row].length;
          if (this.cursor.col < this.scrollLeft) {
            this.cursor.col = Math.min(this.scrollLeft, Math.max(lineLen - 1, 0));
          }
          // If line is short, clamp scrollLeft so cursor stays visible
          if (this.cursor.col < this.scrollLeft) {
            this.scrollLeft = this.cursor.col;
          }
          this._updateDesiredCol();
        }
        break;
      }
      case 'h': {
        // zh — scroll screen left by N columns
        if (!this._settings.wrap) {
          const count = this._getCount(1);
          this.scrollLeft = Math.max(0, this.scrollLeft - count);
          this._updateDesiredCol();
        }
        break;
      }
      case 'L': {
        // zL — scroll half screen right
        if (!this._settings.wrap) {
          const half = Math.floor(this._computeTextCols() / 2);
          this.scrollLeft += half;
          const lineLen = this.buffer.lines[this.cursor.row].length;
          if (this.cursor.col < this.scrollLeft) {
            this.cursor.col = Math.min(this.scrollLeft, Math.max(lineLen - 1, 0));
          }
          if (this.cursor.col < this.scrollLeft) {
            this.scrollLeft = this.cursor.col;
          }
          this._updateDesiredCol();
        }
        break;
      }
      case 'H': {
        // zH — scroll half screen left
        if (!this._settings.wrap) {
          const half = Math.floor(this._computeTextCols() / 2);
          this.scrollLeft = Math.max(0, this.scrollLeft - half);
          this._updateDesiredCol();
        }
        break;
      }
      case 's': {
        // zs — scroll so cursor column is at left edge
        if (!this._settings.wrap) {
          this.scrollLeft = this._virtColAt(this.cursor.row, this.cursor.col);
        }
        break;
      }
      case 'e': {
        // ze — scroll so cursor column is at right edge
        if (!this._settings.wrap) {
          const textCols = this._computeTextCols();
          this.scrollLeft = Math.max(0, this.cursor.col - textCols + 1);
        }
        break;
      }

      // ── Spell commands ──

      case '=': {
        // z= — show spelling suggestions for word under cursor
        if (this._settings.spell) {
          const w = this._getWordAtCursor();
          if (w && this._isSpellBad(w.word)) {
            const suggestions = this._spellSuggest(w.word);
            if (suggestions.length > 0) {
              const normalFg = 'd4d4d4', normalBg = '000000';
              const cols = this.cols;
              const mkLine = (text, runs) => ({ text, runs });
              const promptLines = [];
              promptLines.push(mkLine(('Change "' + w.word + '" to:' + ' '.repeat(cols)).slice(0, cols),
                [{ n: cols, fg: normalFg, bg: normalBg }]));
              for (let i = 0; i < suggestions.length; i++) {
                const numStr = String(i + 1);
                const lineText = (' ' + numStr + ' "' + suggestions[i] + '"' + ' '.repeat(cols)).slice(0, cols);
                promptLines.push(mkLine(lineText, [{ n: cols, fg: normalFg, bg: normalBg }]));
              }
              this._messagePrompt = { lines: promptLines };
            } else {
              this.commandLine = 'Sorry, no strggestions';
              this._stickyCommandLine = true;
            }
          }
        }
        break;
      }
      case 'g': {
        // zg — add word under cursor to good words list
        if (this._settings.spell) {
          const w = this._getWordAtCursor();
          if (w) {
            this._spellGoodWords.add(w.word.toLowerCase());
            this._spellBadWords.delete(w.word.toLowerCase());
            this.commandLine = '';
          }
        }
        break;
      }
      case 'w': {
        // zw — mark word under cursor as bad (wrong)
        if (this._settings.spell) {
          const w = this._getWordAtCursor();
          if (w) {
            this._spellBadWords.add(w.word.toLowerCase());
            this._spellGoodWords.delete(w.word.toLowerCase());
            this.commandLine = '';
          }
        }
        break;
      }
      case 'u': {
        // zu — pending for zug/zuw
        this._pendingZu = true;
        return; // don't fall through to end
      }
    }
  }

  // ── Window split helpers ──

  _saveWindowState() {
    const w = this._windows[this._activeWin];
    if (!w) return;
    w.cursor = { ...this.cursor };
    w.scrollTop = this.scrollTop;
    w.scrollLeft = this.scrollLeft;
    w.folds = this._folds;
    w._desiredCol = this._desiredCol;
    w.buffer = this.buffer;
  }

  _restoreWindowState() {
    const w = this._windows[this._activeWin];
    if (!w) return;
    this.buffer = w.buffer;
    this.cursor = { ...w.cursor };
    this.scrollTop = w.scrollTop;
    this.scrollLeft = w.scrollLeft || 0;
    this._folds = w.folds;
    this._desiredCol = w._desiredCol || 0;
  }

  _switchToWindow(idx) {
    if (idx < 0 || idx >= this._windows.length || idx === this._activeWin) return;
    this._saveWindowState();
    this._activeWin = idx;
    this._restoreWindowState();
  }

  _doSplit() {
    this._saveWindowState();
    const cur = this._windows[this._activeWin];
    const newWin = {
      buffer: cur.buffer,
      cursor: { ...cur.cursor },
      scrollTop: cur.scrollTop,
      folds: cur.folds.map(f => ({ ...f })),
      _desiredCol: cur._desiredCol || 0,
    };
    // Insert new window at current position (new on top, old shifts down)
    this._windows.splice(this._activeWin, 0, newWin);
    // activeWin now points to the new window (top)
    this._restoreWindowState();
  }

  _doCloseWindow() {
    if (this._windows.length <= 1) return; // Can't close last window
    this._windows.splice(this._activeWin, 1);
    if (this._activeWin >= this._windows.length) {
      this._activeWin = this._windows.length - 1;
    }
    this._restoreWindowState();
  }

  _doOnlyWindow() {
    if (this._windows.length <= 1) return;
    this._saveWindowState();
    const cur = this._windows[this._activeWin];
    this._windows = [cur];
    this._activeWin = 0;
    this._restoreWindowState();
  }

  // ── Tab page helpers ──

  /**
   * Save the current tab's state (windows + activeWin).
   */
  _saveTabState() {
    this._saveWindowState();
    this._tabs[this._activeTab] = {
      windows: this._windows,
      activeWin: this._activeWin,
    };
  }

  /**
   * Restore a tab's state.
   */
  _restoreTabState() {
    const tab = this._tabs[this._activeTab];
    this._windows = tab.windows;
    this._activeWin = tab.activeWin;
    this._restoreWindowState();
  }

  /**
   * Switch to a tab by index.
   */
  _switchToTab(idx) {
    if (idx < 0 || idx >= this._tabs.length || idx === this._activeTab) return;
    this._saveTabState();
    this._activeTab = idx;
    this._restoreTabState();
  }

  /**
   * Create a new tab with an empty buffer.
   */
  _doTabNew() {
    this._saveTabState();
    // Save current buffer state
    this._saveCurrentBufState();
    this._alternateBufId = this._currentBufId;
    // Create new empty buffer
    this.buffer = new Buffer(['']);
    this.cursor = { row: 0, col: 0 };
    this.scrollTop = 0;
    this.scrollLeft = 0;
    this._fileName = null;
    this._undoStack = [];
    this._redoStack = [];
    this._changeCount = 0;
    this._marks = {};
    this._folds = [];
    this._desiredCol = 0;
    this._currentBufId = this._registerBuffer(this.buffer, null);
    // New tab with a single window showing the new buffer
    const newWin = {
      buffer: this.buffer,
      cursor: { ...this.cursor },
      scrollTop: 0,
      scrollLeft: 0,
      folds: [],
      _desiredCol: 0,
    };
    this._tabs.splice(this._activeTab + 1, 0, { windows: [newWin], activeWin: 0 });
    this._activeTab++;
    this._windows = this._tabs[this._activeTab].windows;
    this._activeWin = 0;
  }

  /**
   * Close the current tab. If it's the last tab, do nothing (Vim shows E784).
   */
  _doTabClose() {
    if (this._tabs.length <= 1) return;
    this._tabs.splice(this._activeTab, 1);
    if (this._activeTab >= this._tabs.length) {
      this._activeTab = this._tabs.length - 1;
    }
    this._restoreTabState();
  }

  /**
   * Close all other tabs.
   */
  _doTabOnly() {
    if (this._tabs.length <= 1) return;
    this._saveTabState();
    this._tabs = [this._tabs[this._activeTab]];
    this._activeTab = 0;
  }

  /**
   * Get the number of tab pages.
   */
  get tabCount() {
    return this._tabs.length;
  }

  /**
   * Get info for rendering the tab line.
   * Returns array of { label, active } for each tab.
   */
  getTabLineInfo() {
    return this._tabs.map((tab, i) => {
      // Find the active window's filename in this tab
      const win = tab.windows[tab.activeWin] || tab.windows[0];
      let label;
      if (win && win.buffer) {
        // Find filename for this buffer from buffer list
        const entry = this._bufferList.find(e => e.buffer === win.buffer);
        if (entry && entry.fileName) {
          // Just the basename
          const parts = entry.fileName.replace(/\\/g, '/').split('/');
          label = parts[parts.length - 1];
        } else if (i === this._activeTab && this._fileName) {
          const parts = this._fileName.replace(/\\/g, '/').split('/');
          label = parts[parts.length - 1];
        } else {
          label = '[No Name]';
        }
      } else {
        label = '[No Name]';
      }
      return { label, active: i === this._activeTab };
    });
  }

  // ── Ctrl-W (window) prefix ──

  _handleCtrlW(key) {
    switch (key) {
      case 's': case 'Ctrl-S':
        this._doSplit();
        break;
      case 'v': case 'Ctrl-V':
        // For now, vertical split behaves same as horizontal (flat model)
        this._doSplit();
        break;
      case 'w': case 'Ctrl-W':
        // Cycle to next window
        if (this._windows.length > 1) {
          const next = (this._activeWin + 1) % this._windows.length;
          this._switchToWindow(next);
        }
        break;
      case 'j': case 'Ctrl-J': case 'ArrowDown':
        // Move to window below
        if (this._activeWin < this._windows.length - 1) {
          this._switchToWindow(this._activeWin + 1);
        }
        break;
      case 'k': case 'Ctrl-K': case 'ArrowUp':
        // Move to window above
        if (this._activeWin > 0) {
          this._switchToWindow(this._activeWin - 1);
        }
        break;
      case 'h': case 'Ctrl-H': case 'ArrowLeft':
        // Move to window left (same as up for horizontal-only splits)
        if (this._activeWin > 0) {
          this._switchToWindow(this._activeWin - 1);
        }
        break;
      case 'l': case 'Ctrl-L': case 'ArrowRight':
        // Move to window right (same as down for horizontal-only splits)
        if (this._activeWin < this._windows.length - 1) {
          this._switchToWindow(this._activeWin + 1);
        }
        break;
      case 'c': case 'q':
        // Close current window
        this._doCloseWindow();
        break;
      case 'o':
        // Only: close all other windows
        this._doOnlyWindow();
        break;
      case '=':
        // Equalize window sizes (handled by renderer)
        break;
      case '_':
        // Maximize current window height (handled by renderer)
        break;
      case '+':
        // Increase window height (no-op for now)
        break;
      case '-':
        // Decrease window height (no-op for now)
        break;
      case 'T':
        // Ctrl-W T — move current window to a new tab
        if (this._windows.length > 1) {
          this._saveWindowState();
          const win = this._windows.splice(this._activeWin, 1)[0];
          if (this._activeWin >= this._windows.length) {
            this._activeWin = this._windows.length - 1;
          }
          // Save current tab state (without the removed window)
          this._tabs[this._activeTab].windows = this._windows;
          this._tabs[this._activeTab].activeWin = this._activeWin;
          // Create new tab with the removed window
          this._tabs.splice(this._activeTab + 1, 0, { windows: [win], activeWin: 0 });
          this._activeTab++;
          this._windows = this._tabs[this._activeTab].windows;
          this._activeWin = 0;
          this._restoreWindowState();
        }
        break;
      default:
        break;
    }
  }

  // ── Fold helpers ──

  // Find the innermost fold containing the given row
  _findFoldAt(row) {
    let best = null;
    for (const f of this._folds) {
      if (row >= f.startRow && row <= f.endRow) {
        if (!best || (f.endRow - f.startRow) < (best.endRow - best.startRow)) {
          best = f;
        }
      }
    }
    return best;
  }

  // Find all folds containing the given row
  _findAllFoldsAt(row) {
    return this._folds.filter(f => row >= f.startRow && row <= f.endRow);
  }

  // Get the closed fold that hides this row (if any)
  // Returns the fold if row is inside a closed fold AND row !== fold.startRow
  // (the fold start line is always visible)
  getFoldHidingRow(row) {
    for (const f of this._folds) {
      if (f.closed && row > f.startRow && row <= f.endRow) {
        return f;
      }
    }
    return null;
  }

  // Get the closed fold starting at this row (if any)
  getClosedFoldAt(row) {
    for (const f of this._folds) {
      if (f.closed && f.startRow === row) {
        return f;
      }
    }
    return null;
  }

  // Get the next visible row in the given direction (1=down, -1=up)
  _nextVisibleRow(row, direction) {
    let r = row + direction;
    while (r >= 0 && r < this.buffer.lineCount) {
      if (!this.getFoldHidingRow(r)) return r;
      r += direction;
    }
    return row; // Can't move
  }

  // If cursor is inside a closed fold (not on the start line), move to fold start
  _adjustCursorForFolds() {
    const fold = this.getFoldHidingRow(this.cursor.row);
    if (fold) {
      this.cursor.row = fold.startRow;
      this.cursor.col = this._firstNonBlank(this.cursor.row);
      this._updateDesiredCol();
    }
  }

  // ── Command (Ex) mode ──

  // Canonical list of all Ex commands the simulator supports (sorted).
  // Used for Tab completion and Ctrl-D.
  static _EX_COMMANDS = [
    'bdelete', 'bnext', 'bprevious', 'buffer', 'buffers',
    'changes', 'close', 'copy', 'delete', 'delmarks', 'display',
    'echo', 'edit', 'enew', 'file', 'files', 'global',
    'join', 'jumps', 'ls', 'marks', 'move', 'new',
    'nohlsearch', 'normal', 'number', 'only',
    'print', 'put', 'pwd',
    'qa', 'quit',
    'read', 'registers', 'retab',
    'saveas', 'set', 'sort', 'split', 'substitute',
    'tabclose', 'tabedit', 'tabnew', 'tabnext', 'tabonly', 'tabprevious',
    'undolist', 'vglobal', 'vsplit',
    'wa', 'wq', 'wqa', 'write',
    'xa', 'xit', 'yank',
  ];

  // All :set option names (sorted).
  static _SET_OPTIONS = [
    'autoindent', 'cursorline', 'expandtab', 'fileformat',
    'hlsearch', 'ignorecase', 'incsearch', 'list',
    'number', 'relativenumber', 'scrolloff', 'shiftwidth',
    'smartcase', 'spell', 'splitbelow', 'splitright', 'tabstop', 'wrap',
  ];

  // Short-form aliases for :set options → canonical names
  static _SET_ALIASES = {
    ai: 'autoindent', cul: 'cursorline', et: 'expandtab', ff: 'fileformat',
    hls: 'hlsearch', ic: 'ignorecase', is: 'incsearch',
    nu: 'number', rnu: 'relativenumber', so: 'scrolloff', sw: 'shiftwidth',
    scs: 'smartcase', sb: 'splitbelow', spr: 'splitright', ts: 'tabstop',
  };

  /**
   * Get completions for a command-line prefix.
   * Returns sorted list of full command/option names matching the prefix.
   */
  _getCompletions(input) {
    // Trim leading whitespace from input (after the : prefix)
    const trimmed = input.trimStart();

    // Check if this is a :set subcommand — complete option names
    const setMatch = trimmed.match(/^set?\s+(no)?(.*)$/);
    if (setMatch) {
      const noPrefix = setMatch[1] || '';
      const partial = setMatch[2];
      // Match against option names and aliases
      const matches = [];
      for (const opt of VimEngine._SET_OPTIONS) {
        if (opt.startsWith(partial)) {
          matches.push(noPrefix + opt);
        }
      }
      for (const [alias, opt] of Object.entries(VimEngine._SET_ALIASES)) {
        if (alias.startsWith(partial) && !matches.includes(noPrefix + opt)) {
          matches.push(noPrefix + opt);
        }
      }
      matches.sort();
      return { matches, replaceFrom: trimmed.indexOf(noPrefix + partial), context: 'set' };
    }

    // Complete Ex command names
    const matches = VimEngine._EX_COMMANDS.filter(c => c.startsWith(trimmed));
    return { matches, replaceFrom: 0, context: 'command' };
  }

  /**
   * Handle Tab in command mode: cycle through completions.
   */
  _cmdTabComplete() {
    const prefix = this.commandLine[0]; // ':' or '/' or '?'
    if (prefix !== ':') return; // only complete : commands

    // If not currently cycling, start a new completion
    if (this._cmdCompletionIdx < 0) {
      this._cmdCompletionBase = this._searchInput;
      const { matches, context } = this._getCompletions(this._searchInput);
      this._cmdCompletions = matches;
      if (matches.length === 0) return;
      this._cmdCompletionIdx = 0;
    } else {
      // Cycle to next
      this._cmdCompletionIdx = (this._cmdCompletionIdx + 1) % this._cmdCompletions.length;
    }

    // Apply the completion
    const match = this._cmdCompletions[this._cmdCompletionIdx];
    const base = this._cmdCompletionBase;
    const { context } = this._getCompletions(base);

    if (context === 'set') {
      // Replace just the option part after "set "
      const setMatch = base.match(/^(set?\s+)/);
      const setPrefix = setMatch ? setMatch[1] : 'set ';
      this._searchInput = setPrefix + match;
    } else {
      this._searchInput = match;
    }
    this.commandLine = prefix + this._searchInput;
  }

  /**
   * Reset Tab completion state (called when input changes).
   */
  _resetTabCompletion() {
    this._cmdCompletionIdx = -1;
    this._cmdCompletions = [];
    this._cmdCompletionBase = '';
  }

  _commandKey(key) {
    if (key === 'Escape') {
      this.mode = Mode.NORMAL; this.commandLine = '';
      this._pendingOpForSearch = '';
      this._opStartPosForSearch = null;
      this._visualCmdRange = null;
      this._filterRange = null;
      this._cmdHistoryPos = -1;
      this._resetTabCompletion();
      return;
    }
    if (key === 'Enter' || key === 'Ctrl-J' || key === 'Ctrl-M') { this._resetTabCompletion(); this._executeCommand(); return; }
    if (key === 'Tab') {
      // Tab completion — only for : commands, not / or ? search
      if (this.commandLine[0] === ':') {
        this._cmdTabComplete();
      }
      return;
    }
    if (key === 'Ctrl-D') {
      // Show completions — populate _cmdCompletions without changing commandLine
      if (this.commandLine[0] === ':') {
        const { matches } = this._getCompletions(this._searchInput);
        this._cmdCompletions = matches;
      }
      return;
    }
    if (key === 'Backspace') {
      this._resetTabCompletion();
      if (this._searchInput.length > 0) {
        this._searchInput = this._searchInput.slice(0, -1);
        this.commandLine = this.commandLine[0] + this._searchInput;
      } else {
        this.mode = Mode.NORMAL; this.commandLine = '';
        this._visualCmdRange = null;
        this._filterRange = null;
        this._cmdHistoryPos = -1;
      }
      return;
    }
    if (key === 'Ctrl-U') {
      this._resetTabCompletion();
      this._searchInput = '';
      this.commandLine = this.commandLine[0];
      return;
    }
    if (key === 'Ctrl-W') {
      this._resetTabCompletion();
      // Delete word backward: strip trailing whitespace, then strip one word
      // Vim word: keyword chars (a-z, A-Z, 0-9, _) or non-keyword non-whitespace chars
      let s = this._searchInput;
      // Strip trailing whitespace first
      s = s.replace(/\s+$/, '');
      if (s.length > 0) {
        const last = s[s.length - 1];
        if (/\w/.test(last)) {
          // keyword chars
          s = s.replace(/\w+$/, '');
        } else {
          // non-keyword non-whitespace chars
          s = s.replace(/[^\w\s]+$/, '');
        }
      }
      this._searchInput = s;
      this.commandLine = this.commandLine[0] + this._searchInput;
      return;
    }
    if (key === 'ArrowUp') {
      const prefix = this.commandLine[0];
      if (this._cmdHistory.length === 0) return;
      if (this._cmdHistoryPos < 0) {
        this._cmdHistorySaved = this._searchInput;
        this._cmdHistoryPos = this._cmdHistory.length - 1;
      } else if (this._cmdHistoryPos > 0) {
        this._cmdHistoryPos--;
      } else {
        return;
      }
      this._searchInput = this._cmdHistory[this._cmdHistoryPos];
      this.commandLine = prefix + this._searchInput;
      return;
    }
    if (key === 'ArrowDown') {
      const prefix = this.commandLine[0];
      if (this._cmdHistoryPos < 0) return;
      if (this._cmdHistoryPos < this._cmdHistory.length - 1) {
        this._cmdHistoryPos++;
        this._searchInput = this._cmdHistory[this._cmdHistoryPos];
      } else {
        this._cmdHistoryPos = -1;
        this._searchInput = this._cmdHistorySaved || '';
      }
      this.commandLine = prefix + this._searchInput;
      return;
    }
    if (this._cmdPendingCtrlR) {
      this._cmdPendingCtrlR = false;
      let regText = '';
      if (/^[a-zA-Z0-9]$/.test(key) || '+-*_/"'.includes(key)) {
        this._pendingRegKey = (key === '"') ? '' : key;
        if (key === '"') {
          regText = this._unnamedReg || '';
        } else {
          const r = this._getReg();
          regText = r.text || '';
        }
      } else if (key === '/') {
        regText = this._searchPattern || '';
      } else if (key === ':') {
        regText = this._lastExCommand || '';
      } else if (key === '%') {
        regText = this._fileName || '';
      }
      if (regText) {
        // Insert register contents into command/search input (strip newlines)
        const clean = regText.replace(/\n/g, '');
        this._searchInput += clean;
        this.commandLine = this.commandLine[0] + this._searchInput;
      }
      return;
    }
    if (key === 'Ctrl-R') {
      this._cmdPendingCtrlR = true;
      return;
    }
    if (key.length === 1) {
      this._resetTabCompletion();
      this._searchInput += key;
      this.commandLine = this.commandLine[0] + this._searchInput;
    }
  }

  // ── Ex command helpers ──

  /**
   * Parse a single ex address starting at position `pos` in string `cmd`.
   * Returns { line: number (0-based), pos: number } or null.
   */
  _parseExAddr(cmd, pos) {
    if (pos >= cmd.length) return null;
    let line = null;
    const ch = cmd[pos];

    if (ch === '.') {
      line = this.cursor.row;
      pos++;
    } else if (ch === '$') {
      line = this.buffer.lineCount - 1;
      pos++;
    } else if (ch === "'" && pos + 1 < cmd.length) {
      const mk = cmd[pos + 1];
      pos += 2;
      if (mk === '<' && this._visualCmdRange) {
        line = this._visualCmdRange.start;
      } else if (mk === '>' && this._visualCmdRange) {
        line = this._visualCmdRange.end;
      } else {
        const resolved = this._resolveMark(mk);
        if (resolved) line = resolved.row;
        else return null;
      }
    } else if (ch >= '0' && ch <= '9') {
      let num = '';
      while (pos < cmd.length && cmd[pos] >= '0' && cmd[pos] <= '9') {
        num += cmd[pos]; pos++;
      }
      line = parseInt(num, 10) - 1; // 1-based to 0-based
    } else if (ch === '+' || ch === '-') {
      // Bare +N or -N means current line with offset
      line = this.cursor.row;
    } else {
      return null;
    }

    // Parse +N/-N offsets (can be chained)
    while (pos < cmd.length && (cmd[pos] === '+' || cmd[pos] === '-')) {
      const sign = cmd[pos] === '+' ? 1 : -1;
      pos++;
      let offset = '';
      while (pos < cmd.length && cmd[pos] >= '0' && cmd[pos] <= '9') {
        offset += cmd[pos]; pos++;
      }
      line += sign * (offset ? parseInt(offset, 10) : 1);
    }

    // Clamp — allow -1 for "before first line" (address 0 in ex commands)
    line = Math.max(-1, Math.min(line, this.buffer.lineCount - 1));
    return { line, pos };
  }

  /**
   * Parse the range prefix from an ex command string.
   * Returns { sr, er, hasRange, rest }.
   */
  _parseExRange(cmd) {
    // Special case: % means entire file
    if (cmd.startsWith('%')) {
      return {
        sr: 0, er: this.buffer.lineCount - 1, hasRange: true,
        rest: cmd.slice(1)
      };
    }

    // Special case: '<,'> (visual range)
    if (cmd.startsWith("'<,'>")) {
      if (this._visualCmdRange) {
        const sr = this._visualCmdRange.start;
        const er = this._visualCmdRange.end;
        return { sr, er, hasRange: true, rest: cmd.slice(5) };
      }
      return { sr: this.cursor.row, er: this.cursor.row, hasRange: false, rest: cmd.slice(5) };
    }

    // Try to parse first address
    const first = this._parseExAddr(cmd, 0);
    if (!first) {
      return { sr: this.cursor.row, er: this.cursor.row, hasRange: false, rest: cmd };
    }

    // Check for comma (range)
    if (first.pos < cmd.length && cmd[first.pos] === ',') {
      const second = this._parseExAddr(cmd, first.pos + 1);
      if (second) {
        return { sr: Math.max(0, first.line), er: Math.max(0, second.line), hasRange: true, rest: cmd.slice(second.pos) };
      }
      // Comma but no second address: use end of file
      return { sr: Math.max(0, first.line), er: this.buffer.lineCount - 1, hasRange: true, rest: cmd.slice(first.pos + 1) };
    }

    // Single address
    return { sr: Math.max(0, first.line), er: Math.max(0, first.line), hasRange: true, rest: cmd.slice(first.pos) };
  }

  /** :d[elete] [register] — delete lines in range */
  _exDelete(sr, er, regName) {
    this._saveSnapshot({ row: sr, col: 0 });
    this._redoStack = [];
    const count = er - sr + 1;
    const deleted = this.buffer.lines.splice(sr, count);
    if (this.buffer.lines.length === 0) this.buffer.lines.push('');
    const text = deleted.join('\n');
    if (regName) this._pendingRegKey = regName;
    this._setReg(text, 'line', 'delete');
    this.cursor.row = Math.min(sr, this.buffer.lineCount - 1);
    this.cursor.col = this._firstNonBlank(this.cursor.row);
    this._updateDesiredCol();
    if (count >= 2) {
      this.commandLine = count + ' fewer lines';
      this._stickyCommandLine = true;
    } else {
      this.commandLine = '';
    }
  }

  /** :y[ank] [register] — yank lines in range without modifying buffer */
  _exYank(sr, er, regName) {
    const count = er - sr + 1;
    const text = this.buffer.lines.slice(sr, er + 1).join('\n');
    if (regName) this._pendingRegKey = regName;
    this._setReg(text, 'line', 'yank');
    // :yank does NOT move the cursor
    if (count >= 2) {
      this.commandLine = count + ' lines yanked';
      this._stickyCommandLine = true;
    } else {
      this.commandLine = '';
    }
  }

  /** :m[ove] {address} — move lines from range to after address */
  _exMove(sr, er, dest) {
    this._saveSnapshot({ row: sr, col: 0 });
    this._redoStack = [];
    const count = er - sr + 1;
    const moved = this.buffer.lines.splice(sr, count);
    // Adjust dest for the removed lines
    if (dest > er) dest -= count;
    else if (dest >= sr && dest <= er) dest = sr - 1;
    // Insert after dest (dest is 0-based line; insert after it)
    const insertAt = dest + 1;
    this.buffer.lines.splice(insertAt, 0, ...moved);
    this.cursor.row = insertAt + count - 1;
    this.cursor.col = this._firstNonBlank(this.cursor.row);
    this._updateDesiredCol();
    this.commandLine = '';
  }

  /** :co[py]/:t {address} — copy lines from range to after address */
  _exCopy(sr, er, dest) {
    this._saveSnapshot({ row: dest + 1, col: 0 });
    this._redoStack = [];
    const count = er - sr + 1;
    const copied = this.buffer.lines.slice(sr, er + 1);
    const insertAt = dest + 1;
    this.buffer.lines.splice(insertAt, 0, ...copied);
    this.cursor.row = insertAt + count - 1;
    this.cursor.col = this._firstNonBlank(this.cursor.row);
    this._updateDesiredCol();
    this.commandLine = '';
  }

  /** :j[oin][!] — join lines in range */
  _exJoin(sr, er, bang) {
    this._saveSnapshot({ row: sr, col: 0 });
    this._redoStack = [];
    // If single line (no range given), join with next line
    if (sr === er) er = sr + 1;
    if (sr >= er || er >= this.buffer.lineCount) return;
    let result = this.buffer.lines[sr];
    for (let i = sr + 1; i <= er; i++) {
      const next = this.buffer.lines[i];
      if (bang) {
        result += next;
      } else {
        const trimmed = next.replace(/^\s+/, '');
        if (result.length > 0 && trimmed.length > 0) {
          result += ' ' + trimmed;
        } else {
          result += trimmed;
        }
      }
    }
    this.buffer.lines.splice(sr, er - sr + 1, result);
    this.cursor.row = sr;
    this.cursor.col = this._firstNonBlank(sr);
    this._updateDesiredCol();
    this.commandLine = '';
  }

  /** :norm[al][!] {keys} — execute normal-mode keys on each line in range */
  _exNormal(sr, er, keys) {
    this._saveSnapshot({ row: sr, col: 0 });
    this._redoStack = [];
    const wasPlaying = this._macroPlaying;
    this._macroPlaying = true;
    const iterCount = er - sr + 1;
    let row = sr;
    for (let i = 0; i < iterCount; i++) {
      if (this.buffer.lineCount === 0) break;
      // Clamp row to valid range (when lines have been deleted, row may exceed buffer)
      if (row >= this.buffer.lineCount) row = this.buffer.lineCount - 1;
      this.cursor.row = row;
      this.cursor.col = 0;
      this.mode = Mode.NORMAL;
      for (const ch of keys) {
        this.feedKey(ch);
      }
      if (this.mode !== Mode.NORMAL) this.feedKey('Escape');
      // Always advance row by 1 — nvim uses fixed iteration count
      row++;
    }
    this._macroPlaying = wasPlaying;
    this.mode = Mode.NORMAL;
    this.commandLine = '';
  }

  /** :g[lobal]/{pattern}/{cmd} and :v[global]/{pattern}/{cmd} */
  _exGlobal(sr, er, pattern, subcmd, invert) {
    // Snapshot is saved after finding matches (to set cursor at first match)

    // Build regex
    let jsPattern = this._vimPatternToJs(pattern);
    let caseFlag = this._searchCaseFlag();
    let regex;
    try { regex = new RegExp(jsPattern, caseFlag); } catch {
      this.commandLine = 'E486: Pattern not found: ' + pattern;
      this._stickyCommandLine = true;
      return;
    }

    // Set search pattern for highlighting
    this._searchPattern = pattern;
    this._hlsearchActive = true;
    this._showCurSearch = true;

    // Collect matching line indices
    const matches = [];
    for (let r = sr; r <= er; r++) {
      const hit = regex.test(this.buffer.lines[r]);
      if (invert ? !hit : hit) matches.push(r);
    }

    if (matches.length === 0) {
      this.commandLine = 'E486: Pattern not found: ' + pattern;
      this._stickyCommandLine = true;
      return;
    }

    // Save snapshot with cursor at first match position
    this._saveSnapshot({ row: matches[0], col: 0 });
    this._redoStack = [];

    const trimmedSub = subcmd.trim();

    // :g/.../d — delete matching lines (process bottom to top)
    if (/^d(e(l(e(te?)?)?)?)?(\s.*)?$/.test(trimmedSub)) {
      for (let i = matches.length - 1; i >= 0; i--) {
        this.buffer.lines.splice(matches[i], 1);
      }
      if (this.buffer.lines.length === 0) this.buffer.lines.push('');
      // Cursor: approximate position of the last original match
      const lastMatch = matches[matches.length - 1];
      const deletionsBefore = matches.length - 1; // matches before the last one
      let newPos = lastMatch - deletionsBefore;
      newPos = Math.max(0, Math.min(newPos, this.buffer.lineCount - 1));
      this.cursor.row = newPos;
      this.cursor.col = this._firstNonBlank(this.cursor.row);
      this._updateDesiredCol();
      // Set CurSearch: only if cursor is exactly at the start of a match
      this._setCurSearchAtCursor();
      this.commandLine = '';
      return;
    }

    // :g/.../norm {keys}
    const normMatch = trimmedSub.match(/^norm(?:a(?:l)?)?!?\s+(.+)$/);
    if (normMatch) {
      const keys = normMatch[1];
      const wasPlaying = this._macroPlaying;
      this._macroPlaying = true;
      // Process from top to bottom, adjusting for line count changes
      let offset = 0;
      for (let i = 0; i < matches.length; i++) {
        const row = matches[i] + offset;
        if (row >= this.buffer.lineCount) break;
        const beforeCount = this.buffer.lineCount;
        this.cursor.row = row;
        this.cursor.col = 0;
        this.mode = Mode.NORMAL;
        for (const ch of keys) {
          this.feedKey(ch);
        }
        if (this.mode !== Mode.NORMAL) this.feedKey('Escape');
        offset += this.buffer.lineCount - beforeCount;
      }
      this._macroPlaying = wasPlaying;
      this.mode = Mode.NORMAL;
      // Set CurSearch: only if cursor is exactly at the start of a match
      this._setCurSearchAtCursor();
      this.commandLine = '';
      return;
    }

    this.commandLine = '';
  }

  _executeCommand() {
    const prefix = this.commandLine[0];
    const cmd = this._searchInput.replace(/^\s+/, ''); // trim leading whitespace only
    this.mode = Mode.NORMAL;

    // Push to command history
    if (cmd) {
      this._cmdHistory.push(cmd);
    }
    this._cmdHistoryPos = -1;

    if (prefix === '/' || prefix === '?') {
      if (cmd) {
        this._addJumpEntry();
        const beforeRow = this.cursor.row, beforeCol = this.cursor.col;
        this._searchPattern = cmd;
        this._searchForward = (prefix === '/');
        const found = this._searchNext(this._searchForward);

        if (!found) {
          // E486: Pattern not found — show error in command line or full prompt
          const errMsg = 'E486: Pattern not found: ' + cmd;
          if (errMsg.length >= 30) {
            // Long error message: show full "Press ENTER" prompt
            this._messagePrompt = { error: errMsg };
          } else {
            // Short error message: show in command line only
            this.commandLine = errMsg;
            this._stickyCommandLine = true;
          }
          // Cancel any pending operator
          this._pendingOpForSearch = '';
          this._opStartPosForSearch = null;
          return;
        }

        // Complete pending operator+search (e.g. d/pattern<CR>)
        if (this._pendingOpForSearch) {
          const searchOp = this._pendingOpForSearch;
          const moved = (this.cursor.row !== beforeRow || this.cursor.col !== beforeCol);
          if (moved) {
            this._pendingOp = searchOp;
            this._opStartPos = this._opStartPosForSearch;
            this._motionInclusive = false;
            this._motionLinewise = false;
            this._motionExclusive = false;
            this._showCurSearch = true;
            this._hlsearchActive = true;
            this._executeOperator(this._opStartPos, { ...this.cursor });
            this._pendingOp = '';
          }
          this._pendingOpForSearch = '';
          this._opStartPosForSearch = null;
          // Show CurSearch for the current match position
          this._showCurSearch = true;
          this._hlsearchActive = true;
        } else {
          this._showCurSearch = true; // normal search navigation
          this._hlsearchActive = true;
          this._updateDesiredCol();
        }
      } else {
        // Empty search — cancel any pending operator
        this._pendingOpForSearch = '';
        this._opStartPosForSearch = null;
      }
      this.commandLine = '';
      return;
    }

    // Store every : command for @: replay
    this._lastExCommand = cmd;

    // If _filterRange is set and the user typed something after the pre-filled range+!,
    // pass through as _lastExCommand so the session can handle the filter
    if (this._filterRange && cmd.includes('!')) {
      this._lastExCommand = cmd;
      this.commandLine = '';
      return;
    }

    // Detect :{range}!cmd (filter through shell) — pass to session
    // This catches %!sort, 1,5!sort, .,.+3!sort, '<,'>!sort, etc.
    {
      const parsed = this._parseExRange(cmd);
      if (parsed.hasRange && parsed.rest.startsWith('!')) {
        this._lastExCommand = cmd;
        this.commandLine = '';
        return;
      }
    }

    // : commands — file/quit operations (with nvim-style abbreviations)
    // :w[rite], :wq, :x[it], :q[uit], :q[uit]!, :e[dit], :r[ead], :!
    // Set _lastExCommand so SessionManager can intercept; clear commandLine.
    if (/^(w(r(i(te?)?)?)?|wq|x(it?)?|q(u(it?)?)?!?|qa!?|wa!?|wqa!?|xa!?|sav(e(as?)?)?)(\s|$)/.test(cmd) || /^e(d(it?)?)?!?(\s|$)/.test(cmd) || /^r(e(ad?)?)?!/.test(cmd) || /^r(e(ad?)?)?(\s|$)/.test(cmd) || cmd.startsWith('!')) {
      this._lastExCommand = cmd;
      this.commandLine = '';
      return;
    }

    // :sp[lit] — horizontal split
    if (/^sp(l(it?)?)?(\s|$)/.test(cmd)) {
      this._doSplit();
      this.commandLine = '';
      return;
    }

    // :vsp[lit] — vertical split (uses same horizontal model for now)
    if (/^vs(p(l(it?)?)?)?(\s|$)/.test(cmd)) {
      this._doSplit();
      this.commandLine = '';
      return;
    }

    // :new — new empty buffer in split
    if (/^new(\s|$)/.test(cmd)) {
      this._doSplit();
      // Save current buffer state, register new buffer
      this._saveCurrentBufState();
      this._alternateBufId = this._currentBufId;
      // Clear the active window's buffer
      this.buffer = new Buffer(['']);
      this.cursor = { row: 0, col: 0 };
      this.scrollTop = 0;
      this.scrollLeft = 0;
      this._fileName = null;
      this._undoStack = [];
      this._redoStack = [];
      this._changeCount = 0;
      this._marks = {};
      this._folds = [];
      this._currentBufId = this._registerBuffer(this.buffer, null);
      this._saveWindowState();
      this.commandLine = '';
      return;
    }

    // :enew[!] — edit new unnamed buffer
    if (/^ene(w!?)?(\s|$)/.test(cmd)) {
      // Save current buffer state before creating new
      this._saveCurrentBufState();
      this._alternateBufId = this._currentBufId;
      this.buffer = new Buffer(['']);
      this.cursor = { row: 0, col: 0 };
      this.scrollTop = 0;
      this.scrollLeft = 0;
      this._fileName = null;
      this._undoStack = [];
      this._redoStack = [];
      this._changeCount = 0;
      this._marks = {};
      this._folds = [];
      this._currentBufId = this._registerBuffer(this.buffer, null);
      this.commandLine = '';
      return;
    }

    // :ls / :buffers — list all buffers
    if (/^(ls|buffers?|files?)(\s|$)/.test(cmd)) {
      this._saveCurrentBufState();
      const normalFg = 'd4d4d4', normalBg = '000000', dirFg = '66d9ef';
      const cols = this.cols;
      const mkLine = (text, runs) => ({ text, runs });
      const promptLines = [];

      // Header
      promptLines.push(mkLine(':' + cmd + ' '.repeat(cols - cmd.length - 1), [{ n: cols, fg: normalFg, bg: normalBg }]));

      for (const entry of this._bufferList) {
        const isCurrent = entry.id === this._currentBufId;
        const isAlternate = entry.id === this._alternateBufId;
        const flags = (isCurrent ? '%' : (isAlternate ? '#' : ' '))
                    + (isCurrent ? 'a' : ' ')
                    + (entry.changeCount > 0 ? '+' : ' ');
        const name = entry.fileName ? '"' + entry.fileName + '"' : '"[No Name]"';
        const lineNum = isCurrent ? (this.cursor.row + 1) : (entry.cursor.row + 1);
        const prefix = String(entry.id).padStart(3) + ' ' + flags + '   ' + name;
        const suffix = 'line ' + lineNum;
        const gap = Math.max(1, cols - prefix.length - suffix.length);
        const lineText = (prefix + ' '.repeat(gap) + suffix).slice(0, cols);
        const padded = lineText.length < cols ? lineText + ' '.repeat(cols - lineText.length) : lineText;
        promptLines.push(mkLine(padded, [{ n: cols, fg: normalFg, bg: normalBg }]));
      }

      this._messagePrompt = { lines: promptLines };
      this.commandLine = '';
      return;
    }

    // :bn[ext] / :bnext — switch to next buffer
    if (/^bn(e(xt?)?)?(\s|$)/.test(cmd)) {
      const count = 1;
      const idx = this._bufferList.findIndex(e => e.id === this._currentBufId);
      if (idx >= 0 && this._bufferList.length > 1) {
        const nextIdx = (idx + count) % this._bufferList.length;
        this._switchToBuffer(this._bufferList[nextIdx].id);
      }
      this.commandLine = '';
      return;
    }

    // :bp[revious] / :bprev — switch to previous buffer
    if (/^bp(r(e(v(i(o(us?)?)?)?)?)?)?(\s|$)/.test(cmd)) {
      const count = 1;
      const idx = this._bufferList.findIndex(e => e.id === this._currentBufId);
      if (idx >= 0 && this._bufferList.length > 1) {
        const prevIdx = (idx - count + this._bufferList.length) % this._bufferList.length;
        this._switchToBuffer(this._bufferList[prevIdx].id);
      }
      this.commandLine = '';
      return;
    }

    // :b[uffer] N — switch to buffer N
    // :b[uffer] name — switch to buffer by name
    if (/^b(u(f(f(er?)?)?)?)?(\s|$)/.test(cmd)) {
      const parts = cmd.split(/\s+/);
      const arg = parts[1];
      if (arg) {
        const num = parseInt(arg, 10);
        if (!isNaN(num)) {
          // Switch by buffer number
          const entry = this._getBufEntry(num);
          if (entry) {
            this._switchToBuffer(entry.id);
          } else {
            this.commandLine = 'E86: Buffer ' + num + ' does not exist';
            this._stickyCommandLine = true;
          }
        } else {
          // Switch by name (partial match)
          const matches = this._bufferList.filter(e =>
            e.fileName && e.fileName.includes(arg));
          if (matches.length === 1) {
            this._switchToBuffer(matches[0].id);
          } else if (matches.length > 1) {
            this.commandLine = 'E93: More than one match for ' + arg;
            this._stickyCommandLine = true;
          } else {
            this.commandLine = 'E94: No matching buffer for ' + arg;
            this._stickyCommandLine = true;
          }
        }
      }
      this.commandLine = this.commandLine || '';
      return;
    }

    // :bd[elete][!] — delete buffer
    if (/^bd(e(l(e(te?)?)?)?)?!?(\s|$)/.test(cmd)) {
      const force = cmd.includes('!');
      if (!force && this._changeCount > 0) {
        this.commandLine = 'E89: No write since last change (add ! to override)';
        this._stickyCommandLine = true;
        return;
      }
      if (this._bufferList.length <= 1) {
        // Last buffer — just clear it
        this.buffer = new Buffer(['']);
        this.cursor = { row: 0, col: 0 };
        this.scrollTop = 0;
        this.scrollLeft = 0;
        this._fileName = null;
        this._undoStack = [];
        this._redoStack = [];
        this._changeCount = 0;
        const entry = this._getBufEntry(this._currentBufId);
        if (entry) {
          entry.buffer = this.buffer;
          entry.fileName = null;
          entry.changeCount = 0;
        }
      } else {
        // Remove current buffer and switch to next
        const idx = this._bufferList.findIndex(e => e.id === this._currentBufId);
        const removedId = this._currentBufId;
        this._bufferList.splice(idx, 1);
        // Switch to next (or previous if last)
        const nextIdx = Math.min(idx, this._bufferList.length - 1);
        this._currentBufId = this._bufferList[nextIdx].id;
        // Restore the new current buffer
        const entry = this._getBufEntry(this._currentBufId);
        this.buffer = entry.buffer;
        this._fileName = entry.fileName;
        this.cursor = { ...entry.cursor };
        this.scrollTop = entry.scrollTop;
        this.scrollLeft = entry.scrollLeft;
        this._undoStack = entry.undoStack;
        this._redoStack = entry.redoStack;
        this._changeCount = entry.changeCount;
        this._marks = entry.marks;
        this._folds = entry.folds;
        this._desiredCol = entry.desiredCol;
        // Fix alternate if it was the deleted buffer
        if (this._alternateBufId === removedId) {
          this._alternateBufId = null;
        }
      }
      this.commandLine = '';
      return;
    }

    // :clo[se] — close current window
    if (/^clo(se?)?$/.test(cmd)) {
      this._doCloseWindow();
      this.commandLine = '';
      return;
    }

    // :on[ly] — close all other windows
    if (/^on(ly?)?$/.test(cmd)) {
      this._doOnlyWindow();
      this.commandLine = '';
      return;
    }

    // :tabnew / :tabe[dit] — open a new tab page
    if (/^tabnew(\s|$)/.test(cmd) || /^tabe(d(it?)?)?(\s|$)/.test(cmd)) {
      this._doTabNew();
      this.commandLine = '';
      return;
    }

    // :tabn[ext] — go to next tab page
    if (/^tabn(e(xt?)?)?(\s|$)/.test(cmd)) {
      const parts = cmd.split(/\s+/);
      const arg = parts[1] ? parseInt(parts[1], 10) : 0;
      if (arg > 0) {
        const idx = Math.max(0, Math.min(arg - 1, this._tabs.length - 1));
        this._switchToTab(idx);
      } else {
        const nextIdx = (this._activeTab + 1) % this._tabs.length;
        this._switchToTab(nextIdx);
      }
      this.commandLine = '';
      return;
    }

    // :tabp[revious] / :tabN[ext] — go to previous tab page
    if (/^tabp(r(e(v(i(o(us?)?)?)?)?)?)?(\s|$)/.test(cmd) || /^tabN(e(xt?)?)?(\s|$)/.test(cmd)) {
      const prevIdx = ((this._activeTab - 1) % this._tabs.length + this._tabs.length) % this._tabs.length;
      this._switchToTab(prevIdx);
      this.commandLine = '';
      return;
    }

    // :tabc[lose] — close current tab page
    if (/^tabc(l(o(se?)?)?)?(\s|$)/.test(cmd)) {
      this._doTabClose();
      this.commandLine = '';
      return;
    }

    // :tabo[nly] — close all other tab pages
    if (/^tabo(n(ly?)?)?(\s|$)/.test(cmd)) {
      this._doTabOnly();
      this.commandLine = '';
      return;
    }

    // :pwd — display current directory
    if (cmd === 'pwd') {
      this.commandLine = '/home/user';
      this._stickyCommandLine = true;
      return;
    }

    // :echo — display expression result
    if (/^echo(\s|$)/.test(cmd)) {
      const arg = cmd.slice(4).trim();
      let result = '';
      if (arg.startsWith("'") && arg.endsWith("'") && arg.length >= 2) {
        result = arg.slice(1, -1);
      } else if (arg.startsWith('"') && arg.endsWith('"') && arg.length >= 2) {
        result = arg.slice(1, -1);
      } else {
        result = arg;
      }
      this.commandLine = result;
      this._echoMessage = result;
      return;
    }

    // :noh[lsearch] — clear search highlighting (keeps pattern for n/N)
    if (/^noh(l(s(e(a(r(c(h)?)?)?)?)?)?)?$/.test(cmd)) {
      this._hlsearchActive = false;
      this._showCurSearch = false;
      this._curSearchPos = null;
      this.commandLine = '';
      return;
    }

    // :set commands
    if (/^set?\s/.test(cmd) || cmd === 'set') {
      this._executeSet(cmd);
      this.commandLine = '';
      return;
    }

    // ── Parse range and dispatch ex commands ──
    const parsed = this._parseExRange(cmd);
    let { sr, er, hasRange } = parsed;
    const rest = parsed.rest.trimStart();

    // Clear visual range now that the parser consumed it
    this._visualCmdRange = null;

    // :marks — display marks list
    if (/^marks?\s*$/.test(rest)) {
      // Build structured lines for the message prompt with proper color runs.
      // Colors from monokai theme (verified against nvim ground truth):
      const normalFg = 'd4d4d4', normalBg = '000000', dirFg = '66d9ef';
      const cols = this.cols;
      const mkLine = (text, runs) => ({ text, runs });
      const mkFullLine = (text) => mkLine(text, [{ n: cols, fg: normalFg, bg: normalBg }]);
      const mkDataLine = (prefix, lineText) => {
        // prefix is 15 chars (mark + line + col + space), lineText is the buffer text
        const textLen = Math.min(lineText.length, cols - 15);
        const padLen = cols - 15 - textLen;
        const fullText = prefix + lineText.slice(0, cols - 15) + ' '.repeat(padLen);
        const runs = [
          { n: 15, fg: normalFg, bg: normalBg },
        ];
        if (textLen > 0) runs.push({ n: textLen, fg: dirFg, bg: normalBg });
        if (padLen > 0) runs.push({ n: padLen, fg: normalFg, bg: normalBg });
        return mkLine(fullText, runs);
      };

      const promptLines = [];
      // :marks header (full-width single run)
      promptLines.push(mkFullLine(':marks' + ' '.repeat(cols - 6)));
      // Column header: "mark line  col file/text" — monokai yellow e6db74 + bold
      const hdrFg = 'e6db74';
      const hdr = 'mark line  col file/text';
      promptLines.push(mkLine(hdr + ' '.repeat(cols - hdr.length), [
        { n: hdr.length, fg: hdrFg, bg: normalBg, b: true },
        { n: cols - hdr.length, fg: normalFg, bg: normalBg },
      ]));

      const fmtPrefix = (ch, row, col) => {
        return ' ' + ch + String(row + 1).padStart(7) + String(col).padStart(5) + ' ';
      };
      const getLineText = (row) => (row < this.buffer.lineCount) ? this.buffer.lines[row] : '';

      // ' — last jump position (defaults to line 1, col 0)
      const jp = this._lastJumpPos || { row: 0, col: 0 };
      promptLines.push(mkDataLine(fmtPrefix("'", jp.row, jp.col), getLineText(jp.row)));
      // User marks a-z
      const markKeys = Object.keys(this._marks).sort();
      for (const mk of markKeys) {
        const m = this._marks[mk];
        promptLines.push(mkDataLine(fmtPrefix(mk, m.row, m.col), getLineText(m.row)));
      }
      // " — last position when exiting file
      promptLines.push(mkDataLine(fmtPrefix('"', jp.row, jp.col), getLineText(jp.row)));
      // [ — start of buffer
      promptLines.push(mkDataLine(fmtPrefix('[', 0, 0), getLineText(0)));
      // ] — end of buffer
      const lastRow = this.buffer.lineCount - 1;
      promptLines.push(mkDataLine(fmtPrefix(']', lastRow, 0), getLineText(lastRow)));

      this._messagePrompt = { lines: promptLines };
      this.commandLine = '';
      return;
    }

    // :f[ile] — show file info
    if (/^f(i(le?)?)?\s*$/.test(rest)) {
      const name = this._fileName || '[No Name]';
      const mod = this._changeCount > 0 ? ' [Modified]' : '';
      const lines = this.buffer.lineCount;
      this.commandLine = '"' + name + '"' + mod + ' ' + lines + ' line' + (lines !== 1 ? 's' : '');
      this._stickyCommandLine = true;
      return;
    }

    // :delm[arks] {marks} or :delm[arks]!
    {
      const delmMatch = rest.match(/^delm(a(r(ks?)?)?)?\s*(.*)/);
      if (delmMatch) {
        const arg = delmMatch[4].trim();
        if (arg === '!') {
          // Delete all lowercase marks
          this._marks = {};
        } else {
          // Delete specified marks
          for (const ch of arg) {
            if (/[a-z]/.test(ch)) {
              delete this._marks[ch];
            }
          }
        }
        this.commandLine = '';
        return;
      }
    }

    // :undol[ist] — show undo info
    if (/^undol(i(st?)?)?\s*$/.test(rest)) {
      const numEntries = this._undoStack.length;
      this.commandLine = 'number of changes: ' + numEntries;
      this._stickyCommandLine = true;
      return;
    }

    // :reg[isters] / :di[splay]
    if (/^(reg(i(s(t(e(rs?)?)?)?)?)?|di(s(p(l(a(y)?)?)?)?)?)\s*$/.test(rest)) {
      // Structured lines with monokai colors (verified against nvim ground truth):
      //   Header "Type Name Content" → monokai yellow e6db74 + bold
      //   Data rows (type, "name, content) → Normal d4d4d4
      //   ^J newline markers in content    → SpecialKey f92672 (magenta/pink)
      const normalFg = 'd4d4d4', normalBg = '000000', specialKeyFg = 'f92672';
      const cols = this.cols;
      const pad = (s) => s.length < cols ? s + ' '.repeat(cols - s.length) : s.slice(0, cols);
      const mkLine = (text, runs) => ({ text, runs });

      // Build a register data line.  rawText may contain \n displayed as ^J.
      // prefix ("  c  ""   ") and text content are Normal;  ^J markers are SpecialKey (dim gray).
      const mkRegLine = (prefix, rawText) => {
        const parts = rawText.split('\n');
        const displayContent = parts.join('^J');
        const fullRaw = prefix + displayContent;
        const fullText = fullRaw.length < cols
          ? fullRaw + ' '.repeat(cols - fullRaw.length)
          : fullRaw.slice(0, cols);
        const runs = [];
        let pos = 0;
        // Prefix in Normal
        const pLen = Math.min(prefix.length, cols);
        if (pLen > 0) { runs.push({ n: pLen, fg: normalFg, bg: normalBg }); pos += pLen; }
        // Content parts with ^J in SpecialKey (dim gray 4f5258)
        for (let j = 0; j < parts.length && pos < cols; j++) {
          if (j > 0 && pos < cols) {
            const n = Math.min(2, cols - pos);
            runs.push({ n, fg: specialKeyFg, bg: normalBg });
            pos += n;
          }
          if (pos < cols && parts[j].length > 0) {
            const n = Math.min(parts[j].length, cols - pos);
            runs.push({ n, fg: normalFg, bg: normalBg });
            pos += n;
          }
        }
        // Trailing padding
        if (pos < cols) { runs.push({ n: cols - pos, fg: normalFg, bg: normalBg }); }
        return mkLine(fullText, runs);
      };

      const promptLines = [];
      // Echo line (shows the command as typed)
      const mkFullLine = (text) => mkLine(text, [{ n: cols, fg: normalFg, bg: normalBg }]);
      const echoCmd = ':' + rest.trim();
      promptLines.push(mkFullLine(pad(echoCmd)));
      // Header line — monokai yellow e6db74 + bold
      const hdrFg = 'e6db74';
      const hdr = 'Type Name Content';
      promptLines.push(mkLine(pad(hdr), [
        { n: Math.min(hdr.length, cols), fg: hdrFg, bg: normalBg, b: true },
        ...(hdr.length < cols ? [{ n: cols - hdr.length, fg: normalFg, bg: normalBg }] : []),
      ]));
      // Unnamed register
      if (this._unnamedReg) {
        const t = this._regType === 'line' ? 'l' : 'c';
        const regText = this._unnamedReg + (this._regType === 'line' ? '\n' : '');
        promptLines.push(mkRegLine('  ' + t + '  ""   ', regText));
      }
      // Numbered registers 0-9
      for (let i = 0; i <= 9; i++) {
        const r = this._numberedRegs[i];
        if (r && r.text) {
          const t = r.type === 'line' ? 'l' : 'c';
          const regText = r.text + (r.type === 'line' ? '\n' : '');
          promptLines.push(mkRegLine('  ' + t + '  "' + i + '   ', regText));
        }
      }
      // Small delete register
      if (this._smallDeleteReg && this._smallDeleteReg.text) {
        const t = this._smallDeleteReg.type === 'line' ? 'l' : 'c';
        const regText = this._smallDeleteReg.text + (this._smallDeleteReg.type === 'line' ? '\n' : '');
        promptLines.push(mkRegLine('  ' + t + '  "-   ', regText));
      }
      // Named registers a-z
      const namedKeys = Object.keys(this._namedRegs).sort();
      for (const k of namedKeys) {
        const r = this._namedRegs[k];
        if (r && r.text) {
          const t = r.type === 'line' ? 'l' : 'c';
          const regText = r.text + (r.type === 'line' ? '\n' : '');
          promptLines.push(mkRegLine('  ' + t + '  "' + k + '   ', regText));
        }
      }
      // Clipboard registers "* and "+ (always shown as empty characterwise)
      promptLines.push(mkRegLine('  c  "*   ', ''));
      promptLines.push(mkRegLine('  c  "+   ', ''));
      // Current file name register "%
      if (this._fileName) {
        promptLines.push(mkRegLine('  c  "%   ', this._fileName));
      }
      // Last search register
      if (this._searchPattern) {
        promptLines.push(mkRegLine('  c  "/   ', this._searchPattern));
      }
      this._messagePrompt = { lines: promptLines };
      this.commandLine = '';
      return;
    }

    // :norm[al][!] {keys}
    {
      const normMatch = rest.match(/^norm(?:a(?:l)?)?!?\s+(.+)$/);
      if (normMatch) {
        this._exNormal(sr, er, normMatch[1]);
        return;
      }
    }

    // :g[lobal]/{pattern}/{cmd}
    {
      const gMatch = rest.match(/^g(?:l(?:o(?:b(?:a(?:l)?)?)?)?)?(!?)([\/:!#])(.*)/);
      if (gMatch) {
        const invert = !!gMatch[1]; // g! is inverted
        const delim = gMatch[2];
        const body = gMatch[3];
        // :g without range defaults to entire file
        const gsr = hasRange ? sr : 0;
        const ger = hasRange ? er : this.buffer.lineCount - 1;
        // Parse pattern and subcmd separated by delim
        let pattern = '', subcmd = '';
        let inPat = true;
        for (let i = 0; i < body.length; i++) {
          if (body[i] === '\\' && i + 1 < body.length && inPat) {
            pattern += body[i] + body[i + 1]; i++; continue;
          }
          if (body[i] === delim && inPat) { inPat = false; continue; }
          if (inPat) pattern += body[i]; else subcmd += body[i];
        }
        if (pattern) {
          this._exGlobal(gsr, ger, pattern, subcmd, invert);
        }
        this.commandLine = '';
        return;
      }
    }

    // :v[global]/{pattern}/{cmd}
    {
      const vMatch = rest.match(/^v(?:g(?:l(?:o(?:b(?:a(?:l)?)?)?)?)?)?(!?)([\/:!#])(.*)/);
      if (vMatch) {
        const delim = vMatch[2];
        const body = vMatch[3];
        // :v without range defaults to entire file
        const vsr = hasRange ? sr : 0;
        const ver = hasRange ? er : this.buffer.lineCount - 1;
        let pattern = '', subcmd = '';
        let inPat = true;
        for (let i = 0; i < body.length; i++) {
          if (body[i] === '\\' && i + 1 < body.length && inPat) {
            pattern += body[i] + body[i + 1]; i++; continue;
          }
          if (body[i] === delim && inPat) { inPat = false; continue; }
          if (inPat) pattern += body[i]; else subcmd += body[i];
        }
        if (pattern) {
          this._exGlobal(vsr, ver, pattern, subcmd, true);
        }
        this.commandLine = '';
        return;
      }
    }

    // :s[ubstitute] with delimiter — full substitution
    {
      const subMatch = rest.match(/^s(?:u(?:b(?:s(?:t(?:i(?:t(?:u(?:te?)?)?)?)?)?)?)?)?([\/:!#])(.*)/);
      if (subMatch) {
        const delim = subMatch[1];
        const body = subMatch[2];
        // Parse: pattern<delim>replacement<delim>[flags]
        let pattern = '', replacement = '', flagStr = '';
        let part = 0; // 0=pattern, 1=replacement, 2=flags
        for (let i = 0; i < body.length; i++) {
          if (body[i] === '\\' && i + 1 < body.length) {
            const target = part === 0 ? 'pattern' : part === 1 ? 'replacement' : 'flags';
            if (target === 'pattern') pattern += body[i] + body[i + 1];
            else if (target === 'replacement') replacement += body[i] + body[i + 1];
            else flagStr += body[i] + body[i + 1];
            i++; continue;
          }
          if (body[i] === delim) { part++; continue; }
          if (part === 0) pattern += body[i];
          else if (part === 1) replacement += body[i];
          else flagStr += body[i];
        }
        if (!pattern) { this.commandLine = ''; return; }

        // Parse flags
        let globalFlag = false, icFlag = false, confirmFlag = false, countOnly = false;
        for (const ch of flagStr) {
          if (ch === 'g') globalFlag = true;
          else if (ch === 'i') icFlag = true;
          else if (ch === 'c') confirmFlag = true;
          else if (ch === 'n') countOnly = true;
        }

        // Store last substitution for bare :s repeat
        this._lastSubstitution = { pattern, replacement, flags: flagStr };

        // Set search pattern for n/N/highlighting
        this._searchPattern = pattern;
        this._hlsearchActive = true;
        this._showCurSearch = true;

        // Translate vim "magic" regex to JavaScript regex
        let jsPattern = this._vimPatternToJs(pattern);

        // Handle & in replacement: vim's & means "whole match" → JS $&
        // But \& is a literal & in vim → keep as &
        // Order matters: escape $ first, then convert &, so $& won't be double-escaped
        let jsReplacement = replacement
          .replace(/\\&/g, '\x00AMP')       // protect literal \&
          .replace(/\$/g, '$$$$')            // escape bare $ (vim $ is literal, JS $ is special)
          .replace(/&/g, '$$&')              // vim & → JS $& ($$& in .replace = literal $ + &)
          .replace(/\x00AMP/g, '&')          // restore literal &
          .replace(/\\([1-9])/g, '$$$1');    // vim \1-\9 → JS $1-$9

        // Build regex
        let caseFlag = icFlag ? 'i' : this._searchCaseFlag();
        let regex;
        try { regex = new RegExp(jsPattern, (globalFlag ? 'g' : '') + caseFlag); } catch {
          this.commandLine = 'E486: Pattern not found: ' + pattern;
          this._stickyCommandLine = true;
          return;
        }

        // Count-only mode (n flag)
        if (countOnly) {
          let matchCount = 0, lineCount = 0;
          for (let r = sr; r <= er; r++) {
            const line = this.buffer.lines[r];
            const re = new RegExp(jsPattern, 'g' + caseFlag);
            const m = line.match(re);
            if (m) { matchCount += m.length; lineCount++; }
          }
          this.commandLine = matchCount + ' match' + (matchCount !== 1 ? 'es' : '') + ' on ' + lineCount + ' line' + (lineCount !== 1 ? 's' : '');
          this._stickyCommandLine = true;
          this._updateCurSearchPos();
          return;
        }

        // Perform substitutions
        this._saveSnapshot({ row: sr, col: 0 });
        this._redoStack = [];
        let totalSubs = 0;
        let lastSubRow = sr;
        for (let r = sr; r <= er; r++) {
          const before = this.buffer.lines[r];
          const after = before.replace(regex, jsReplacement);
          if (after !== before) {
            this.buffer.lines[r] = after;
            totalSubs++;
            lastSubRow = r;
          }
        }

        if (totalSubs === 0) {
          this.commandLine = 'E486: Pattern not found: ' + pattern;
          this._stickyCommandLine = true;
        } else {
          this.cursor.row = lastSubRow;
          this.cursor.col = this._firstNonBlank(lastSubRow);
          this.commandLine = totalSubs + ' substitution' + (totalSubs > 1 ? 's' : '') + ' on ' + (er - sr + 1) + ' line' + ((er - sr + 1) > 1 ? 's' : '');
          this._stickyCommandLine = true;
        }
        this._showCurSearch = false;
        this._curSearchPos = null;
        return;
      }
    }

    // Bare :s — repeat last substitution on current line (or range)
    if (/^s(u(b(s(t(i(t(u(te?)?)?)?)?)?)?)?)?$/.test(rest)) {
      if (this._lastSubstitution) {
        const { pattern, replacement, flags } = this._lastSubstitution;
        this._searchPattern = pattern;
        this._hlsearchActive = true;
        this._showCurSearch = true;

        let jsPattern = pattern
          .replace(/\\\+/g, '+')
          .replace(/\\\?/g, '?')
          .replace(/\\\(/g, '(')
          .replace(/\\\)/g, ')')
          .replace(/\\\|/g, '|')
          .replace(/\\\{/g, '{')
          .replace(/\\\}/g, '}');
        let jsReplacement = replacement
          .replace(/\\&/g, '\x00AMP')
          .replace(/\$/g, '$$$$')
          .replace(/&/g, '$$&')
          .replace(/\x00AMP/g, '&');
        let globalFlag = flags.includes('g');
        let icFlag = flags.includes('i');
        let caseFlag = icFlag ? 'i' : this._searchCaseFlag();
        let regex;
        try { regex = new RegExp(jsPattern, (globalFlag ? 'g' : '') + caseFlag); } catch {
          this.commandLine = 'E486: Pattern not found: ' + pattern;
          this._stickyCommandLine = true;
          return;
        }
        this._saveSnapshot({ row: sr, col: 0 });
        this._redoStack = [];
        let totalSubs = 0, lastSubRow = sr;
        for (let r = sr; r <= er; r++) {
          const before = this.buffer.lines[r];
          const after = before.replace(regex, jsReplacement);
          if (after !== before) { this.buffer.lines[r] = after; totalSubs++; lastSubRow = r; }
        }
        if (totalSubs === 0) {
          this.commandLine = 'E486: Pattern not found: ' + pattern;
          this._stickyCommandLine = true;
        } else {
          this.cursor.row = lastSubRow;
          this.cursor.col = this._firstNonBlank(lastSubRow);
          this.commandLine = totalSubs + ' substitution' + (totalSubs > 1 ? 's' : '') + ' on ' + (er - sr + 1) + ' line' + ((er - sr + 1) > 1 ? 's' : '');
          this._stickyCommandLine = true;
        }
        this._showCurSearch = false;
        this._curSearchPos = null;
      }
      return;
    }

    // :sort[!] [flags]
    {
      const sortMatch = rest.match(/^sort(!)?\s*(.*)?$/);
      if (sortMatch) {
        const bang = !!sortMatch[1];
        const flags = (sortMatch[2] || '').trim();
        let reverse = bang;
        let numeric = false;
        let unique = false;
        let ignoreCase = false;
        for (const ch of flags) {
          if (ch === 'n') numeric = true;
          else if (ch === 'i') ignoreCase = true;
          else if (ch === 'u') unique = true;
        }
        // If no explicit range was given, sort entire file
        if (!hasRange) { sr = 0; er = this.buffer.lineCount - 1; }
        const slice = this.buffer.lines.slice(sr, er + 1);
        if (numeric) {
          slice.sort((a, b) => {
            const na = parseFloat(a) || 0;
            const nb = parseFloat(b) || 0;
            return na - nb;
          });
        } else if (ignoreCase) {
          slice.sort((a, b) => a.toLowerCase().localeCompare(b.toLowerCase()));
        } else {
          slice.sort();
        }
        if (reverse) slice.reverse();
        if (unique) {
          const seen = new Set();
          const deduped = [];
          for (const line of slice) {
            const key = ignoreCase ? line.toLowerCase() : line;
            if (!seen.has(key)) { seen.add(key); deduped.push(line); }
          }
          slice.length = 0;
          slice.push(...deduped);
        }
        this._saveSnapshot({ row: sr, col: 0 });
        this._redoStack = [];
        this.buffer.lines.splice(sr, er - sr + 1, ...slice);
        this.cursor.row = sr;
        this.cursor.col = this._firstNonBlank(sr);
        this._updateDesiredCol();
        const count = slice.length;
        this.commandLine = `${count} line${count !== 1 ? 's' : ''} sorted`;
        this._stickyCommandLine = true;
        return;
      }
    }

    // :retab[!] [N]
    {
      const retabMatch = rest.match(/^ret(ab?)?(!)?\s*(\d+)?\s*$/);
      if (retabMatch) {
        const bang = !!retabMatch[2];
        const oldTs = this._settings.tabstop;
        const newTs = retabMatch[3] ? parseInt(retabMatch[3], 10) : oldTs;
        if (retabMatch[3]) this._settings.tabstop = newTs;
        this._saveSnapshot();
        this._redoStack = [];
        const rsr = hasRange ? sr : 0;
        const rer = hasRange ? er : this.buffer.lineCount - 1;
        if (this._settings.expandtab || bang) {
          // Convert tabs to spaces using the OLD tabstop for visual width
          for (let r = rsr; r <= rer; r++) {
            this.buffer.lines[r] = this.buffer.lines[r].replace(/\t/g, ' '.repeat(oldTs));
          }
        } else {
          // Convert spaces to tabs using new tabstop
          for (let r = rsr; r <= rer; r++) {
            const line = this.buffer.lines[r];
            const match = line.match(/^( +)/);
            if (match) {
              const leading = match[1];
              const tabCount = Math.floor(leading.length / newTs);
              const remainder = leading.length % newTs;
              this.buffer.lines[r] = '\t'.repeat(tabCount) + ' '.repeat(remainder) + line.slice(leading.length);
            }
          }
        }
        // Place cursor on first non-blank of current line (like nvim)
        const line = this.buffer.lines[this.cursor.row];
        const fnb = line.search(/\S/);
        this.cursor.col = fnb >= 0 ? fnb : 0;
        this.commandLine = '';
        return;
      }
    }

    // :j[oin][!]
    {
      const joinMatch = rest.match(/^j(o(i(n)?)?)?(!)?\s*$/);
      if (joinMatch) {
        const bang = !!joinMatch[4];
        // If no range given, default to joining current line with next
        if (!hasRange) er = sr;
        this._exJoin(sr, er, bang);
        return;
      }
    }

    // :d[elete] [register]
    {
      const delMatch = rest.match(/^d(e(l(e(te?)?)?)?)?\s*([a-zA-Z])?\s*$/);
      if (delMatch) {
        const regName = delMatch[5] || '';
        this._exDelete(sr, er, regName);
        return;
      }
    }

    // :y[ank] [register]
    {
      const yankMatch = rest.match(/^y(a(n(k)?)?)?\s*([a-zA-Z])?\s*$/);
      if (yankMatch) {
        const regName = yankMatch[4] || '';
        this._exYank(sr, er, regName);
        return;
      }
    }

    // :m[ove] {address} — MUST come after :marks check
    {
      const moveMatch = rest.match(/^m(o(ve?)?)?\s*(.*)/);
      if (moveMatch) {
        const addrStr = moveMatch[3].trim();
        const addrParsed = this._parseExAddr(addrStr, 0);
        if (addrParsed) {
          this._exMove(sr, er, addrParsed.line);
        }
        this.commandLine = '';
        return;
      }
    }

    // :co[py]/:t {address}
    {
      const copyMatch = rest.match(/^(?:co(?:py?)?|t)\s*(.*)/);
      if (copyMatch) {
        const addrStr = copyMatch[1].trim();
        const addrParsed = this._parseExAddr(addrStr, 0);
        if (addrParsed) {
          this._exCopy(sr, er, addrParsed.line);
        }
        this.commandLine = '';
        return;
      }
    }

    // :pu[t][!] [register] — paste register content as new lines
    {
      const putMatch = rest.match(/^pu(t)?(!)?\s*(.*)$/);
      if (putMatch) {
        const bang = !!putMatch[2];
        const regArg = putMatch[3].trim();
        let regName = '';
        let reg;
        if (regArg.length >= 1) {
          regName = regArg[0];
          this._pendingRegKey = regName;
          reg = this._getReg();
        } else {
          regName = '"';
          reg = { text: this._unnamedReg, type: this._regType };
        }
        const text = reg.text || '';
        if (!text) {
          this.commandLine = 'E353: Nothing in register ' + regName;
          this._stickyCommandLine = true;
          return;
        }
        this._saveSnapshot();
        this._redoStack = [];
        const lines = text.split('\n');
        if (lines.length > 0 && lines[lines.length - 1] === '' && text.endsWith('\n')) {
          lines.pop();
        }
        // If a range/line address was given, use sr as target line
        const targetRow = hasRange ? sr : this.cursor.row;
        if (bang) {
          this.buffer.lines.splice(targetRow, 0, ...lines);
          this.cursor.row = targetRow + lines.length - 1;
          this.cursor.col = this._firstNonBlank(this.cursor.row);
        } else {
          this.buffer.lines.splice(targetRow + 1, 0, ...lines);
          this.cursor.row = targetRow + lines.length;
          this.cursor.col = this._firstNonBlank(this.cursor.row);
        }
        this._updateDesiredCol();
        this.commandLine = '';
        return;
      }
    }

    // :[range]> — shift lines right (indent)
    {
      const shiftRightMatch = rest.match(/^(>+)\s*$/);
      if (shiftRightMatch) {
        const count = shiftRightMatch[1].length; // >> means shift twice
        if (!hasRange) { sr = this.cursor.row; er = this.cursor.row; }
        this._saveSnapshot({ row: sr, col: 0 });
        this._redoStack = [];
        for (let i = 0; i < count; i++) {
          for (let r = sr; r <= er; r++) this._shiftLineRight(r);
        }
        this.cursor.row = er;
        this.cursor.col = this._firstNonBlank(er);
        this._updateDesiredCol();
        this.commandLine = '';
        return;
      }
    }

    // :[range]< — shift lines left (unindent)
    {
      const shiftLeftMatch = rest.match(/^(<+)\s*$/);
      if (shiftLeftMatch) {
        const count = shiftLeftMatch[1].length; // << means shift twice
        if (!hasRange) { sr = this.cursor.row; er = this.cursor.row; }
        this._saveSnapshot({ row: sr, col: 0 });
        this._redoStack = [];
        for (let i = 0; i < count; i++) {
          for (let r = sr; r <= er; r++) this._shiftLineLeft(r);
        }
        this.cursor.row = er;
        this.cursor.col = this._firstNonBlank(er);
        this._updateDesiredCol();
        this.commandLine = '';
        return;
      }
    }

    // := — print total number of lines; :.= — print current line number
    if (rest === '=') {
      if (hasRange) {
        this.commandLine = String(er + 1);
      } else {
        this.commandLine = String(this.buffer.lineCount);
      }
      this._stickyCommandLine = true;
      return;
    }

    // :p[rint] / :nu[mber] / :# — display lines
    {
      const printMatch = rest.match(/^(p(r(i(nt?)?)?)?|nu(m(b(e(r)?)?)?)?|#)\s*$/);
      if (printMatch) {
        if (!hasRange) { sr = this.cursor.row; er = this.cursor.row; }
        const isNumber = rest.startsWith('nu') || rest === '#';
        const numWidth = Math.max(3, String(this.buffer.lineCount).length);
        // Move cursor to last line in range
        this.cursor.row = er;
        this.cursor.col = this._firstNonBlank(er);
        this._updateDesiredCol();
        if (sr === er) {
          // Single line: show in command line (like neovim)
          let line;
          if (isNumber) {
            line = String(sr + 1).padStart(numWidth) + ' ' + this.buffer.lines[sr];
            this._commandLineLineNrLen = numWidth + 1; // include space after number
          } else {
            line = this.buffer.lines[sr];
          }
          this.commandLine = line;
          this._stickyCommandLine = true;
        } else {
          // Multi-line: show in message prompt with proper colors
          const normalFg = 'd4d4d4', normalBg = '000000', lineNrFg = 'd4d4d4';
          const cols = 40; // standard screen width
          const promptLines = [];
          for (let r = sr; r <= er; r++) {
            if (isNumber) {
              const numStr = String(r + 1).padStart(numWidth);
              const lineText = this.buffer.lines[r];
              const full = numStr + ' ' + lineText;
              const padded = full.length < cols ? full + ' '.repeat(cols - full.length) : full.slice(0, cols);
              const nrLen = numWidth + 1; // line number + space separator
              const restLen = cols - nrLen;
              const runs = [];
              runs.push({ n: nrLen, fg: lineNrFg, bg: normalBg });
              if (restLen > 0) runs.push({ n: restLen, fg: normalFg, bg: normalBg });
              promptLines.push({ text: padded, runs });
            } else {
              const lineText = this.buffer.lines[r];
              const padded = lineText.length < cols ? lineText + ' '.repeat(cols - lineText.length) : lineText.slice(0, cols);
              promptLines.push({ text: padded, runs: [{ n: cols, fg: normalFg, bg: normalBg }] });
            }
          }
          this._messagePrompt = { lines: promptLines };
          this.commandLine = '';
        }
        return;
      }
    }

    // :ju[mps] — display jump list
    if (/^ju(m(ps?)?)?\s*$/.test(rest)) {
      // Build structured lines with monokai colors (verified against nvim ground truth):
      //   Header " jump line  col file/text" → monokai yellow e6db74 + bold
      //   Data prefix (marker, num, line, col) → Normal d4d4d4
      //   Data text (file/text)               → Directory/blue 66d9ef (current buf)
      const normalFg = 'd4d4d4', normalBg = '000000', dirFg = '66d9ef';
      const cols = this.cols;
      const pad = (s) => s.length < cols ? s + ' '.repeat(cols - s.length) : s.slice(0, cols);
      const mkLine = (text, runs) => ({ text, runs });
      const mkDataLine = (prefix, lineText) => {
        const prefixLen = prefix.length;
        const textLen = Math.min(lineText.length, Math.max(0, cols - prefixLen));
        const padLen = Math.max(0, cols - prefixLen - textLen);
        const fullText = prefix + lineText.slice(0, Math.max(0, cols - prefixLen)) + ' '.repeat(padLen);
        const runs = [{ n: Math.min(prefixLen, cols), fg: normalFg, bg: normalBg }];
        if (textLen > 0) runs.push({ n: textLen, fg: dirFg, bg: normalBg });
        if (padLen > 0) runs.push({ n: padLen, fg: normalFg, bg: normalBg });
        return mkLine(fullText, runs);
      };

      const promptLines = [];
      // Echo line (shows the command as typed)
      const mkFullLine = (text) => mkLine(text, [{ n: cols, fg: normalFg, bg: normalBg }]);
      const echoCmd = ':' + rest.trim();
      promptLines.push(mkFullLine(pad(echoCmd)));
      // Header line — monokai yellow e6db74 + bold
      const hdr = ' jump line  col file/text';
      promptLines.push(mkLine(pad(hdr), [
        { n: Math.min(hdr.length, cols), fg: 'e6db74', bg: normalBg, b: true },
        ...(hdr.length < cols ? [{ n: cols - hdr.length, fg: normalFg, bg: normalBg }] : []),
      ]));

      const list = this._jumpList;
      const pos = this._jumpListPos;
      for (let i = 0; i < list.length; i++) {
        const e = list[i];
        const jumpNum = list.length - i;
        const marker = (i === pos) ? '>' : ' ';
        const lineText = (e.row < this.buffer.lineCount) ? this.buffer.lines[e.row] : '';
        const prefix = marker + String(jumpNum).padStart(3) + String(e.row + 1).padStart(6) + String(e.col).padStart(5) + ' ';
        promptLines.push(mkDataLine(prefix, lineText));
      }
      // Current position (>) at bottom — nvim shows just ">" with no data
      if (pos >= list.length) {
        promptLines.push(mkLine(pad('>'), [{ n: cols, fg: normalFg, bg: normalBg }]));
      }
      if (list.length === 0) {
        promptLines.push(mkLine(pad('>'), [{ n: cols, fg: normalFg, bg: normalBg }]));
      }
      this._messagePrompt = { lines: promptLines };
      this.commandLine = '';
      return;
    }

    // :changes — display change list
    if (/^changes?\s*$/.test(rest)) {
      // Build structured lines with monokai colors (verified against nvim ground truth):
      //   Header "change line  col text" → monokai yellow e6db74 + bold
      //   Data prefix (marker, num, line, col) → Normal d4d4d4
      //   Data text content                    → Directory/blue 66d9ef (current buf)
      const normalFg = 'd4d4d4', normalBg = '000000', dirFg = '66d9ef';
      const cols = this.cols;
      const pad = (s) => s.length < cols ? s + ' '.repeat(cols - s.length) : s.slice(0, cols);
      const mkLine = (text, runs) => ({ text, runs });
      const mkDataLine = (prefix, lineText) => {
        const prefixLen = prefix.length;
        const textLen = Math.min(lineText.length, Math.max(0, cols - prefixLen));
        const padLen = Math.max(0, cols - prefixLen - textLen);
        const fullText = prefix + lineText.slice(0, Math.max(0, cols - prefixLen)) + ' '.repeat(padLen);
        const runs = [{ n: Math.min(prefixLen, cols), fg: normalFg, bg: normalBg }];
        if (textLen > 0) runs.push({ n: textLen, fg: dirFg, bg: normalBg });
        if (padLen > 0) runs.push({ n: padLen, fg: normalFg, bg: normalBg });
        return mkLine(fullText, runs);
      };

      const promptLines = [];
      // Echo line (shows the command as typed)
      const mkFullLine = (text) => mkLine(text, [{ n: cols, fg: normalFg, bg: normalBg }]);
      const echoCmd = ':' + rest.trim();
      promptLines.push(mkFullLine(pad(echoCmd)));
      // Header line — monokai yellow e6db74 + bold
      const hdr = 'change line  col text';
      promptLines.push(mkLine(pad(hdr), [
        { n: Math.min(hdr.length, cols), fg: 'e6db74', bg: normalBg, b: true },
        ...(hdr.length < cols ? [{ n: cols - hdr.length, fg: normalFg, bg: normalBg }] : []),
      ]));

      const list = this._changeList;
      const pos = this._changeListPos;
      for (let i = 0; i < list.length; i++) {
        const e = list[i];
        const changeNum = list.length - i;
        const marker = (i === pos) ? '>' : ' ';
        const lineText = (e.row < this.buffer.lineCount) ? this.buffer.lines[e.row] : '';
        const prefix = marker + String(changeNum).padStart(4) + String(e.row + 1).padStart(6) + String(e.col).padStart(5) + ' ';
        promptLines.push(mkDataLine(prefix, lineText));
      }
      // Current position at bottom if pos >= list.length
      if (pos >= list.length) {
        const prefix = '>' + String(0).padStart(4) + String(this.cursor.row + 1).padStart(6) + String(this.cursor.col).padStart(5) + ' ';
        promptLines.push(mkDataLine(prefix, ''));
      }
      if (list.length === 0) {
        // Just the header, no data
      }
      this._messagePrompt = { lines: promptLines };
      this.commandLine = '';
      return;
    }

    // No command after range — goto line (if range was given or bare number/$ in original cmd)
    if (hasRange && rest === '') {
      const targetLine = er;
      this.cursor.row = targetLine;
      this.cursor.col = this._firstNonBlank(this.cursor.row);
      // Neovim-style scroll: center when jump distance is large
      const half = Math.floor((this._textRows - 1) / 2);
      if (this.cursor.row < this.scrollTop) {
        const dist = this.scrollTop - this.cursor.row;
        if (dist >= half) {
          this.scrollTop = Math.max(0, this.cursor.row - half);
        } else {
          this.scrollTop = this.cursor.row;
        }
      } else if (this.cursor.row >= this.scrollTop + this._textRows) {
        const dist = this.cursor.row - (this.scrollTop + this._textRows - 1);
        if (dist >= half) {
          const maxST = Math.max(0, this.buffer.lineCount - this._textRows);
          this.scrollTop = Math.min(this.cursor.row - half, maxST);
        } else {
          this.scrollTop = this.cursor.row - this._textRows + 1;
        }
      }
      this.commandLine = '';
      return;
    }

    // Unknown command — show error
    if (rest) {
      this._messagePrompt = { error: 'E492: Not an editor command: ' + cmd };
    }
    this.commandLine = '';
  }

  /** Handle :set commands */
  _executeSet(cmd) {
    // Parse: "set option" or "set nooption" or "set option=value"
    const args = cmd.replace(/^set?\s*/, '').split(/\s+/);
    // Short-form aliases → canonical names
    const shortAliases = {
      nu: 'number', rnu: 'relativenumber',
      ic: 'ignorecase', scs: 'smartcase',
      et: 'expandtab', ai: 'autoindent',
      cul: 'cursorline', hls: 'hlsearch',
      ts: 'tabstop', sw: 'shiftwidth', so: 'scrolloff',
      is: 'incsearch', sb: 'splitbelow', spr: 'splitright',
    };
    for (const arg of args) {
      if (!arg) continue;

      // Handle numeric settings: option=value
      const eqMatch = arg.match(/^(\w+)=(\d+)$/);
      if (eqMatch) {
        const optName = shortAliases[eqMatch[1]] || eqMatch[1];
        if (optName in this._settings && typeof this._settings[optName] === 'number') {
          this._settings[optName] = parseInt(eqMatch[2], 10);
        }
        continue;
      }

      // Boolean options: :set nooption
      const noMatch = arg.match(/^no(.+)$/);
      if (noMatch) {
        const raw = noMatch[1];
        const opt = shortAliases[raw] || raw;
        if (opt in this._settings && typeof this._settings[opt] === 'boolean') {
          this._settings[opt] = false;
        }
        continue;
      }

      // Boolean enable (short or long form)
      const opt = shortAliases[arg] || arg;
      if (opt in this._settings && typeof this._settings[opt] === 'boolean') {
        this._settings[opt] = true;
        continue;
      }
    }
    // Sync hlsearch active state with setting
    this._hlsearchActive = this._settings.hlsearch;
  }

  // ── Insert mode ──

  _insertKey(key) {
    // Pending Ctrl-R: next key is register name, paste register contents
    if (this._pendingCtrlR) {
      this._pendingCtrlR = false;
      this._saveForDot(key);
      let regText = '';
      // Use _getReg logic for consistency: set _pendingRegKey then call _getReg
      if (/^[a-zA-Z0-9]$/.test(key) || '+-*_/"'.includes(key)) {
        this._pendingRegKey = key === '"' ? '' : key;
        if (key === '"') {
          regText = this._unnamedReg || '';
        } else {
          const r = this._getReg();
          regText = r.text || '';
        }
      }
      if (regText) {
        const lines = regText.split('\n');
        for (let i = 0; i < lines.length; i++) {
          if (i > 0) {
            this.buffer.splitLine(this.cursor.row, this.cursor.col);
            this.cursor.row++; this.cursor.col = 0;
          }
          for (const ch of lines[i]) {
            this.buffer.insertChar(this.cursor.row, this.cursor.col, ch);
            this.cursor.col++;
          }
        }
      }
      return;
    }
    this._saveForDot(key);
    switch (key) {
      case 'Ctrl-A': {
        // Re-insert previously inserted text
        if (this._lastInsertedText) {
          for (const ch of this._lastInsertedText) {
            if (ch === '\n') {
              // Split line
              const line = this.buffer.lines[this.cursor.row];
              const before = line.slice(0, this.cursor.col);
              const after = line.slice(this.cursor.col);
              this.buffer.lines[this.cursor.row] = before;
              this.buffer.lines.splice(this.cursor.row + 1, 0, after);
              this.cursor.row++;
              this.cursor.col = 0;
            } else {
              // Insert character
              const line = this.buffer.lines[this.cursor.row];
              this.buffer.lines[this.cursor.row] = line.slice(0, this.cursor.col) + ch + line.slice(this.cursor.col);
              this.cursor.col++;
            }
          }
        } else {
          this._insertError = 'E29: No inserted text yet';
        }
        break;
      }
      case 'Ctrl-C':
      case 'Escape': {
        // Handle count-prefix insert (e.g. 3iHa<Esc> -> HaHaHa)
        if (this._insertCount > 1) {
          // The recorded keys include [insertCmd, typed keys..., Escape]
          // Skip the first key (insert cmd like 'i','a','I','A','o','O','s','S','c','C')
          // and skip 'Escape' at the end
          const insertCmd = this._recordedKeys[0];
          const recorded = this._recordedKeys.slice(1); // skip insert cmd
          const needsNewline = (insertCmd === 'o' || insertCmd === 'O');
          for (let rep = 1; rep < this._insertCount; rep++) {
            if (needsNewline) {
              // For o/O, each repeat starts on a new line
              this._insertKeyDirect('Enter');
            }
            for (const rk of recorded) {
              if (rk === 'Escape') continue;
              this._insertKeyDirect(rk);
            }
          }
          this._insertCount = 1;
        }
        // Compute last inserted text for ". register
        {
          let insText = '';
          for (let ri = 1; ri < this._recordedKeys.length; ri++) {
            const k = this._recordedKeys[ri];
            if (k === 'Escape') continue;
            if (k === 'Ctrl-R') { ri++; continue; } // skip register name
            if (k === 'Enter' || k === 'Ctrl-J') { insText += '\n'; continue; }
            if (k === 'Backspace' || k === 'Ctrl-H') {
              if (insText.length > 0) insText = insText.slice(0, -1);
              continue;
            }
            if (k.length === 1 && k >= ' ') insText += k;
          }
          this._lastInsertedText = insText;
        }
        // Save cursor position before adjusting for gi
        this._lastInsertPos = { row: this.cursor.row, col: this.cursor.col };
        // Update change list with the position after editing (for `. mark)
        if (this._changeList.length > 0) {
          const endCol = Math.max(0, this.cursor.col - 1);
          this._changeList[this._changeList.length - 1] = { row: this.cursor.row, col: endCol };
        }
        this.mode = Mode.NORMAL;
        // Preserve error messages (e.g. E29) set during insert mode
        if (this._insertError) {
          this.commandLine = this._insertError;
          this._insertError = null;
          this._stickyCommandLine = true;
          this._errorCmdLineCursor = true;
        } else {
          this.commandLine = '';
        }
        if (this.cursor.col > 0) this.cursor.col--;
        this._stopRecording(); this._redoStack = [];

        // Handle block insert state (visual block I/A/c): apply typed text to all rows
        if (this._blockInsertState) {
          const bs = this._blockInsertState;
          this._blockInsertState = null;
          const newLine = this.buffer.lines[bs.editRow];
          const lenDiff = newLine.length - bs.origLine.length;
          const typedText = lenDiff > 0 ? newLine.slice(bs.insertCol, bs.insertCol + lenDiff) : '';
          if (typedText.length > 0) {
            for (let r = bs.topRow; r <= bs.bottomRow; r++) {
              if (r === bs.editRow) continue;
              const line = this.buffer.lines[r];
              if (bs.mode === 'I') {
                // Insert at leftCol
                const padded = line.length < bs.leftCol ? line + ' '.repeat(bs.leftCol - line.length) : line;
                this.buffer.lines[r] = padded.slice(0, bs.leftCol) + typedText + padded.slice(bs.leftCol);
              } else if (bs.mode === 'A') {
                if (bs.dollar) {
                  // Append at end of line
                  this.buffer.lines[r] = line + typedText;
                } else {
                  // Insert at rightCol + 1
                  const insertAt = bs.rightCol + 1;
                  const padded = line.length < insertAt ? line + ' '.repeat(insertAt - line.length) : line;
                  this.buffer.lines[r] = padded.slice(0, insertAt) + typedText + padded.slice(insertAt);
                }
              } else if (bs.mode === 'c') {
                // Block columns already deleted; insert typed text at leftCol
                const padded = line.length < bs.leftCol ? line + ' '.repeat(bs.leftCol - line.length) : line;
                this.buffer.lines[r] = padded.slice(0, bs.leftCol) + typedText + padded.slice(bs.leftCol);
              }
            }
          }
          // For I and A, cursor goes to (topRow, leftCol); for c, stays at normal Esc position
          if (bs.mode === 'I' || bs.mode === 'A') {
            this.cursor.row = bs.topRow;
            this.cursor.col = bs.leftCol;
          }
        }

        this._updateDesiredCol();
        // Update CurSearch position after text changes from insert mode
        if (this._showCurSearch) this._updateCurSearchPos();
        break;
      }
      case 'Ctrl-J':
      case 'Enter':
        this.buffer.splitLine(this.cursor.row, this.cursor.col);
        this.cursor.row++; this.cursor.col = 0;
        break;
      case 'Ctrl-H':
      case 'Backspace': {
        const pos = this.buffer.deleteCharBefore(this.cursor.row, this.cursor.col);
        this.cursor.row = pos.row; this.cursor.col = pos.col;
        break;
      }
      case 'Delete': {
        // Forward-delete: delete char at cursor
        if (this.cursor.col < this.buffer.lineLength(this.cursor.row)) {
          this.buffer.deleteChar(this.cursor.row, this.cursor.col);
        } else if (this.cursor.row < this.buffer.lineCount - 1) {
          // At end of line: join with next line
          const cur = this.buffer.lines[this.cursor.row];
          const next = this.buffer.lines[this.cursor.row + 1];
          this.buffer.lines[this.cursor.row] = cur + next;
          this.buffer.lines.splice(this.cursor.row + 1, 1);
        }
        break;
      }
      case 'Ctrl-W': {
        // Delete word backward
        if (this.cursor.col === 0 && this.cursor.row > 0) {
          // At start of line: join with previous line
          const prevLen = this.buffer.lines[this.cursor.row - 1].length;
          const cur = this.buffer.lines[this.cursor.row];
          this.buffer.lines[this.cursor.row - 1] += cur;
          this.buffer.lines.splice(this.cursor.row, 1);
          this.cursor.row--;
          this.cursor.col = prevLen;
        } else if (this.cursor.col > 0) {
          const line = this.buffer.lines[this.cursor.row];
          let c = this.cursor.col;
          // Skip whitespace
          while (c > 0 && (line[c - 1] === ' ' || line[c - 1] === '\t')) c--;
          // Delete word characters or non-word non-space characters
          if (c > 0 && this._isWordChar(line[c - 1])) {
            while (c > 0 && this._isWordChar(line[c - 1])) c--;
          } else {
            while (c > 0 && !this._isWordChar(line[c - 1]) && line[c - 1] !== ' ' && line[c - 1] !== '\t') c--;
          }
          this.buffer.lines[this.cursor.row] = line.slice(0, c) + line.slice(this.cursor.col);
          this.cursor.col = c;
        }
        break;
      }
      case 'Ctrl-U': {
        // Delete to start of line
        if (this.cursor.col > 0) {
          const line = this.buffer.lines[this.cursor.row];
          this.buffer.lines[this.cursor.row] = line.slice(this.cursor.col);
          this.cursor.col = 0;
        } else if (this.cursor.row > 0) {
          // At col 0: join with previous line
          const prevLen = this.buffer.lines[this.cursor.row - 1].length;
          const cur = this.buffer.lines[this.cursor.row];
          this.buffer.lines[this.cursor.row - 1] += cur;
          this.buffer.lines.splice(this.cursor.row, 1);
          this.cursor.row--;
          this.cursor.col = prevLen;
        }
        break;
      }
      case 'ArrowLeft':
        if (this.cursor.col > 0) this.cursor.col--;
        this._insertCount = 1; // Arrow keys cancel count-insert replay
        break;
      case 'ArrowRight':
        if (this.cursor.col < this.buffer.lineLength(this.cursor.row)) this.cursor.col++;
        this._insertCount = 1;
        break;
      case 'ArrowUp':
        if (this.cursor.row > 0) {
          this.cursor.row--;
          this.cursor.col = Math.min(this.cursor.col, this.buffer.lineLength(this.cursor.row));
        }
        this._insertCount = 1;
        break;
      case 'ArrowDown':
        if (this.cursor.row < this.buffer.lineCount - 1) {
          this.cursor.row++;
          this.cursor.col = Math.min(this.cursor.col, this.buffer.lineLength(this.cursor.row));
        }
        this._insertCount = 1;
        break;
      case 'Ctrl-O': {
        // Execute one normal-mode command, then return to insert
        this._insertOneShot = true;
        this.mode = Mode.NORMAL;
        this.commandLine = '-- (insert) --';
        return;
      }
      case 'Ctrl-T': {
        // Indent current line by one shiftwidth
        const lineBeforeT = this.buffer.lines[this.cursor.row];
        const oldLenT = lineBeforeT.length;
        this._shiftLineRight(this.cursor.row);
        // Adjust cursor position by the actual change in line length
        const lineAfterT = this.buffer.lines[this.cursor.row];
        const addedT = lineAfterT.length - oldLenT;
        this.cursor.col = Math.min(this.cursor.col + addedT, lineAfterT.length);
        break;
      }
      case 'Ctrl-D': {
        // Unindent current line by one shiftwidth
        const lineBefore = this.buffer.lines[this.cursor.row];
        const oldLen = lineBefore.length;
        this._shiftLineLeft(this.cursor.row);
        const lineAfterD = this.buffer.lines[this.cursor.row];
        const removed = oldLen - lineAfterD.length;
        this.cursor.col = Math.max(0, this.cursor.col - removed);
        break;
      }
      case 'Ctrl-E': {
        // Insert character from line below at current column
        const belowRow = this.cursor.row + 1;
        if (belowRow < this.buffer.lineCount) {
          const belowLine = this.buffer.lines[belowRow];
          if (this.cursor.col < belowLine.length) {
            const ch = belowLine[this.cursor.col];
            this.buffer.insertChar(this.cursor.row, this.cursor.col, ch);
            this.cursor.col++;
          }
        }
        break;
      }
      case 'Ctrl-Y': {
        // Insert character from line above at current column
        const aboveRow = this.cursor.row - 1;
        if (aboveRow >= 0) {
          const aboveLine = this.buffer.lines[aboveRow];
          if (this.cursor.col < aboveLine.length) {
            const ch = aboveLine[this.cursor.col];
            this.buffer.insertChar(this.cursor.row, this.cursor.col, ch);
            this.cursor.col++;
          }
        }
        break;
      }
      case 'Ctrl-R': // Ctrl-R: paste from register
        this._pendingCtrlR = true;
        return; // don't fall through
      default:
        if (key.length === 1 && key >= ' ') {
          this.buffer.insertChar(this.cursor.row, this.cursor.col, key);
          this.cursor.col++;
        }
        break;
    }
  }

  // ── Replace mode ──

  /** Direct insert key handling (no recording) - used for count-insert replay */
  _insertKeyDirect(key) {
    switch (key) {
      case 'Ctrl-J':
      case 'Enter':
        this.buffer.splitLine(this.cursor.row, this.cursor.col);
        this.cursor.row++; this.cursor.col = 0;
        break;
      case 'Ctrl-H':
      case 'Backspace': {
        const pos = this.buffer.deleteCharBefore(this.cursor.row, this.cursor.col);
        this.cursor.row = pos.row; this.cursor.col = pos.col;
        break;
      }
      case 'Delete':
        if (this.cursor.col < this.buffer.lineLength(this.cursor.row)) {
          this.buffer.deleteChar(this.cursor.row, this.cursor.col);
        } else if (this.cursor.row < this.buffer.lineCount - 1) {
          const cur = this.buffer.lines[this.cursor.row];
          const next = this.buffer.lines[this.cursor.row + 1];
          this.buffer.lines[this.cursor.row] = cur + next;
          this.buffer.lines.splice(this.cursor.row + 1, 1);
        }
        break;
      case 'Ctrl-W': {
        if (this.cursor.col === 0 && this.cursor.row > 0) {
          const prevLen = this.buffer.lines[this.cursor.row - 1].length;
          const cur = this.buffer.lines[this.cursor.row];
          this.buffer.lines[this.cursor.row - 1] += cur;
          this.buffer.lines.splice(this.cursor.row, 1);
          this.cursor.row--;
          this.cursor.col = prevLen;
        } else if (this.cursor.col > 0) {
          const line = this.buffer.lines[this.cursor.row];
          let c = this.cursor.col;
          while (c > 0 && (line[c - 1] === ' ' || line[c - 1] === '\t')) c--;
          if (c > 0 && this._isWordChar(line[c - 1])) {
            while (c > 0 && this._isWordChar(line[c - 1])) c--;
          } else {
            while (c > 0 && !this._isWordChar(line[c - 1]) && line[c - 1] !== ' ' && line[c - 1] !== '\t') c--;
          }
          this.buffer.lines[this.cursor.row] = line.slice(0, c) + line.slice(this.cursor.col);
          this.cursor.col = c;
        }
        break;
      }
      case 'Ctrl-U': {
        if (this.cursor.col > 0) {
          const line = this.buffer.lines[this.cursor.row];
          this.buffer.lines[this.cursor.row] = line.slice(this.cursor.col);
          this.cursor.col = 0;
        } else if (this.cursor.row > 0) {
          const prevLen = this.buffer.lines[this.cursor.row - 1].length;
          const cur = this.buffer.lines[this.cursor.row];
          this.buffer.lines[this.cursor.row - 1] += cur;
          this.buffer.lines.splice(this.cursor.row, 1);
          this.cursor.row--;
          this.cursor.col = prevLen;
        }
        break;
      }
      case 'ArrowLeft':
        if (this.cursor.col > 0) this.cursor.col--;
        break;
      case 'ArrowRight':
        if (this.cursor.col < this.buffer.lineLength(this.cursor.row)) this.cursor.col++;
        break;
      case 'ArrowUp':
        if (this.cursor.row > 0) {
          this.cursor.row--;
          this.cursor.col = Math.min(this.cursor.col, this.buffer.lineLength(this.cursor.row));
        }
        break;
      case 'ArrowDown':
        if (this.cursor.row < this.buffer.lineCount - 1) {
          this.cursor.row++;
          this.cursor.col = Math.min(this.cursor.col, this.buffer.lineLength(this.cursor.row));
        }
        break;
      default:
        if (key.length === 1 && key >= ' ') {
          this.buffer.insertChar(this.cursor.row, this.cursor.col, key);
          this.cursor.col++;
        }
        break;
    }
  }

  _replaceKey(key) {
    this._saveForDot(key);
    if (key === 'Escape') {
      this.mode = Mode.NORMAL; this.commandLine = '';
      if (this.cursor.col > 0) this.cursor.col--;
      this._stopRecording(); this._redoStack = [];
      this._updateDesiredCol();
      return;
    }
    if (key === 'Enter' || key === 'Ctrl-J') {
      this.buffer.splitLine(this.cursor.row, this.cursor.col);
      this.cursor.row++; this.cursor.col = 0;
      return;
    }
    if (key === 'Backspace' || key === 'Ctrl-H') {
      // Cannot backspace before replace mode start position
      if (this.cursor.col <= this._replaceStartCol) return;
      this.cursor.col--;
      // Restore original character or remove appended character
      if (this._replaceOrigChars && this._replaceOrigChars.length > 0) {
        const entry = this._replaceOrigChars.pop();
        if (entry.ch === null) {
          // Was appended (past original line length) — delete it
          const line = this.buffer.lines[this.cursor.row];
          this.buffer.lines[this.cursor.row] = line.slice(0, this.cursor.col) + line.slice(this.cursor.col + 1);
        } else {
          // Was overwritten — restore original character
          const line = this.buffer.lines[this.cursor.row];
          this.buffer.lines[this.cursor.row] = line.slice(0, this.cursor.col) + entry.ch + line.slice(this.cursor.col + 1);
        }
      }
      return;
    }
    if (key.length === 1 && key >= ' ') {
      const line = this.buffer.lines[this.cursor.row];
      if (this.cursor.col < line.length) {
        // Overwriting existing char — save original for backspace restore
        if (this._replaceOrigChars) {
          this._replaceOrigChars.push({ ch: line[this.cursor.col] });
        }
        this.buffer.lines[this.cursor.row] = line.slice(0, this.cursor.col) + key + line.slice(this.cursor.col + 1);
      } else {
        // Appending past end — save null marker for backspace delete
        if (this._replaceOrigChars) {
          this._replaceOrigChars.push({ ch: null });
        }
        this.buffer.insertChar(this.cursor.row, this.cursor.col, key);
      }
      this.cursor.col++;
    }
  }

  // ── Visual mode ──

  _visualKey(key) {
    if ((key >= '1' && key <= '9') || (key === '0' && this._pendingCount !== '')) {
      this._pendingCount += key; return;
    }

    // Pending visual r: replace selection with character
    if (this._pendingVisualR) {
      this._pendingVisualR = false;
      this._doVisualReplace(key);
      this._pendingCount = ''; return;
    }

    // Pending visual surround: S was pressed, waiting for surround char
    if (this._pendingVisualSurround) {
      const vs = this._pendingVisualSurround;
      this._pendingVisualSurround = null;
      if (key === 'Escape') {
        this.mode = Mode.NORMAL; this.commandLine = '';
        this._pendingCount = ''; return;
      }
      if (key === 't') {
        // Tag surround: enter tag input mode
        this._pendingTagInput = { buffer: '', context: 'S', vs };
        this.mode = Mode.NORMAL;
        this.commandLine = '';
        return;
      }
      const savedCursor = { ...this.cursor };
      this.cursor = { row: vs.sr, col: vs.sc };
      this._saveSnapshot();
      this.cursor = savedCursor;
      if (vs.wasLinewise) {
        // Linewise visual S: place surround on separate lines
        let { open, close } = this._getSurroundPair(key);
        // For linewise mode, strip padding spaces from open/close (e.g. '( ' → '(')
        open = open.trim();
        close = close.trim();
        // Insert closing delimiter line after selected lines
        this.buffer.lines.splice(vs.er + 1, 0, close);
        // Insert opening delimiter line before selected lines
        this.buffer.lines.splice(vs.sr, 0, open);
        this.cursor.row = vs.sr; this.cursor.col = 0;
      } else {
        this._doSurroundAdd(vs.sr, vs.sc, vs.er, vs.ec, key);
      }
      this.mode = Mode.NORMAL; this.commandLine = '';
      this._redoStack = [];
      this._pendingCount = ''; return;
    }

    // Pending text object type (i/a)
    if (this._pendingTextObjType) {
      const objType = this._pendingTextObjType;
      this._pendingTextObjType = null;
      const range = this._getTextObject(objType, key);
      if (range) {
        // Expand visual selection to cover the text object range
        this._visualStart = { row: range.startRow, col: range.startCol };
        this.cursor.row = range.endRow;
        this.cursor.col = range.endCol - 1;
        if (this.cursor.col < 0) this.cursor.col = 0;
      }
      this._pendingCount = ''; return;
    }

    // Pending find on line (f/F/t/T)
    if (this._pendingF) {
      const type = this._pendingF;
      this._pendingF = '';
      const findChar = key === 'Tab' ? '\t' : key;
      const c = this._getCount();
      this._doFindRepeat(type, findChar, c);
      this._pendingCount = ''; return;
    }

    // Pending g prefix
    if (this._pendingG) {
      this._pendingG = false;
      this._handleG(key);
      this._pendingCount = ''; return;
    }

    // Pending z prefix
    if (this._pendingZ) {
      this._pendingZ = false;
      if (key === 'f') {
        // zf in visual mode: create fold from selection
        this._lastVisual = { mode: this.mode, start: { ...this._visualStart }, end: { ...this.cursor } };
        const sr = Math.min(this._visualStart.row, this.cursor.row);
        const er = Math.max(this._visualStart.row, this.cursor.row);
        if (sr < er) {
          this._folds.push({ startRow: sr, endRow: er, closed: true });
          this._folds.sort((a, b) => a.startRow - b.startRow);
        }
        this.cursor.row = sr;
        this.cursor.col = this._firstNonBlank(sr);
        this._updateDesiredCol();
        this.mode = Mode.NORMAL;
        this.commandLine = '';
      }
      this._pendingCount = '';
      return;
    }

    // Pending register selection ("x)
    if (this._pendingDblQuote) {
      this._pendingDblQuote = false;
      if (key.length === 1 && (/^[a-zA-Z0-9]$/.test(key) || '+-*_/".:'.includes(key))) {
        this._pendingRegKey = key;
      }
      return;
    }

    if (key === '"') {
      this._pendingDblQuote = true;
      return;
    }

    if (key === 'z') {
      this._pendingZ = true;
      return;
    }

    if (key === '!') {
      // Visual mode !: enter command mode with filter for visual range
      this._lastVisual = { mode: this.mode, start: { ...this._visualStart }, end: { ...this.cursor } };
      const sr = Math.min(this._visualStart.row, this.cursor.row);
      const er = Math.max(this._visualStart.row, this.cursor.row);
      this._visualCmdRange = {
        start: sr, end: er,
        visMode: this.mode,
        visStart: { ...this._visualStart },
        visEnd: { ...this.cursor },
      };
      this._filterRange = { sr, er };
      this.mode = Mode.COMMAND;
      this._searchInput = "'<,'>!";
      this.commandLine = ":'<,'>!";
      this._pendingCount = ''; return;
    }

    if (key === ':') {
      // Enter command mode with visual range prefix
      this._lastVisual = { mode: this.mode, start: { ...this._visualStart }, end: { ...this.cursor } };
      const sr = Math.min(this._visualStart.row, this.cursor.row);
      const er = Math.max(this._visualStart.row, this.cursor.row);
      this._visualCmdRange = {
        start: sr, end: er,
        visMode: this.mode,              // 'visual' or 'visual_line'
        visStart: { ...this._visualStart },
        visEnd: { ...this.cursor },
      };
      this.mode = Mode.COMMAND;
      this._searchInput = "'<,'>";
      this.commandLine = ":'<,'>";
      this._pendingCount = ''; return;
    }
    if (key === 'Escape') {
      this._lastVisual = { mode: this.mode, start: { ...this._visualStart }, end: { ...this.cursor } };
      this.mode = Mode.NORMAL; this.commandLine = '';
      this._pendingCount = ''; return;
    }
    if (key === 'v') {
      if (this.mode === Mode.VISUAL) {
        this._lastVisual = { mode: this.mode, start: { ...this._visualStart }, end: { ...this.cursor } };
        this.mode = Mode.NORMAL; this.commandLine = '';
      } else { this.mode = Mode.VISUAL; this._visualBlockDollar = false; this.commandLine = '-- VISUAL --'; }
      this._pendingCount = ''; return;
    }
    if (key === 'V') {
      if (this.mode === Mode.VISUAL_LINE) {
        this._lastVisual = { mode: this.mode, start: { ...this._visualStart }, end: { ...this.cursor } };
        this.mode = Mode.NORMAL; this.commandLine = '';
      } else { this.mode = Mode.VISUAL_LINE; this._visualBlockDollar = false; this.commandLine = '-- VISUAL LINE --'; }
      this._pendingCount = ''; return;
    }
    if (key === 'Ctrl-V') {
      if (this.mode === Mode.VISUAL_BLOCK) {
        this._lastVisual = { mode: this.mode, start: { ...this._visualStart }, end: { ...this.cursor } };
        this.mode = Mode.NORMAL; this.commandLine = '';
      } else { this.mode = Mode.VISUAL_BLOCK; this._visualBlockDollar = false; this.commandLine = '-- VISUAL BLOCK --'; }
      this._pendingCount = ''; return;
    }
    if (key === 'o' || key === 'O') {
      if (this.mode === Mode.VISUAL_BLOCK && key === 'O') {
        // In visual_block, O swaps horizontal position only
        const tmpCol = this._visualStart.col;
        this._visualStart.col = this.cursor.col;
        this.cursor.col = tmpCol;
      } else {
        const t = { ...this._visualStart };
        this._visualStart = { ...this.cursor };
        this.cursor = t;
      }
      this._pendingCount = ''; return;
    }

    // Pending bracket command in visual mode
    if (this._pendingBracket) {
      const bracket = this._pendingBracket;
      this._pendingBracket = '';
      if (key !== 'Escape') {
        this._handleBracketCommand(bracket, key);
      }
      this._pendingCount = ''; return;
    }

    // Bracket command prefix in visual mode
    if (key === '[' || key === ']') {
      this._pendingBracket = key;
      return;
    }

    // Text object prefixes
    if (key === 'i' || key === 'a') {
      this._pendingTextObjType = key;
      return;
    }

    // Find on line
    if (key === 'f' || key === 'F' || key === 't' || key === 'T') {
      this._pendingF = key;
      return;
    }

    // g prefix
    if (key === 'g') {
      this._pendingG = true;
      return;
    }

    // Visual surround: S key triggers surround
    if (key === 'S') {
      this._lastVisual = { mode: this.mode, start: { ...this._visualStart }, end: { ...this.cursor } };
      const wasLinewise = (this.mode === Mode.VISUAL_LINE);
      let sr, sc, er, ec;
      if (wasLinewise) {
        sr = Math.min(this._visualStart.row, this.cursor.row);
        er = Math.max(this._visualStart.row, this.cursor.row);
        sc = 0; ec = this.buffer.lineLength(er);
      } else {
        if (this._visualStart.row < this.cursor.row || (this._visualStart.row === this.cursor.row && this._visualStart.col <= this.cursor.col)) {
          sr = this._visualStart.row; sc = this._visualStart.col;
          er = this.cursor.row; ec = this.cursor.col + 1;
        } else {
          sr = this.cursor.row; sc = this.cursor.col;
          er = this._visualStart.row; ec = this._visualStart.col + 1;
        }
      }
      this._pendingVisualSurround = { sr, sc, er, ec, wasLinewise };
      return;
    }

    // Actions
    const actionKeys = new Set(['d','c','y','>','<','~','U','u','J','p','x','s','r','Delete','=']);

    // Visual Block: I/A for block insert/append
    if (this.mode === Mode.VISUAL_BLOCK && (key === 'I' || key === 'A')) {
      this._doVisualBlockInsert(key);
      this._pendingCount = '';
      return;
    }

    // Visual Block: route block actions to dedicated handler
    if (this.mode === Mode.VISUAL_BLOCK && actionKeys.has(key)) {
      this._doVisualBlockAction(key);
      this._pendingCount = '';
      return;
    }

    if (actionKeys.has(key)) {
      this._doVisualAction(key);
      this._pendingCount = '';
      return;
    }

    // Motions
    this._doMotion(key);
    // Sentence motions are exclusive — in visual mode, the cursor char is not highlighted
    const exclusiveVisualMotions = new Set([')', '(']);
    this._visualExclusive = exclusiveVisualMotions.has(key);
    // Track _visualBlockDollar for visual_block $ motion
    if (this.mode === Mode.VISUAL_BLOCK) {
      if (key === '$') {
        this._visualBlockDollar = true;
      } else if (key !== 'j' && key !== 'k' && key !== 'ArrowDown' && key !== 'ArrowUp'
          && key !== 'G' && key !== 'H' && key !== 'M' && key !== 'L') {
        this._visualBlockDollar = false;
      }
    }
  }

  _doVisualAction(key) {
    // Save last visual selection for gv
    this._lastVisual = { mode: this.mode, start: { ...this._visualStart }, end: { ...this.cursor } };
    let sr, sc, er, ec;
    const wasLinewise = (this.mode === Mode.VISUAL_LINE);
    if (this.mode === Mode.VISUAL_LINE) {
      sr = Math.min(this._visualStart.row, this.cursor.row);
      er = Math.max(this._visualStart.row, this.cursor.row);
      sc = 0; ec = this.buffer.lineLength(er);
    } else {
      if (this._visualStart.row < this.cursor.row || (this._visualStart.row === this.cursor.row && this._visualStart.col <= this.cursor.col)) {
        sr = this._visualStart.row; sc = this._visualStart.col;
        er = this.cursor.row; ec = this.cursor.col;
      } else {
        sr = this.cursor.row; sc = this.cursor.col;
        er = this._visualStart.row; ec = this._visualStart.col;
      }
    }
    // Save snapshot with cursor at the start of the visual selection.
    // Vim's undo restores cursor to the beginning of the changed region.
    const savedCursor = { ...this.cursor };
    this.cursor = { row: sr, col: sc };
    this._saveSnapshot();
    this.cursor = savedCursor;

    switch (key) {
      case 'd': case 'x': case 'Delete': {
        if (this.mode === Mode.VISUAL_LINE) {
          let y = ''; for (let r = sr; r <= er; r++) y += (r > sr ? '\n' : '') + this.buffer.lines[r];
          this._setReg(y, 'line');
          const savedCol = this.cursor.col;
          this.buffer.lines.splice(sr, er - sr + 1);
          if (this.buffer.lines.length === 0) this.buffer.lines = [''];
          this.cursor.row = Math.min(sr, this.buffer.lineCount - 1);
          this.cursor.col = Math.min(savedCol, Math.max(0, this.buffer.lineLength(this.cursor.row) - 1));
        } else if (sc === 0 && sr !== er && ec >= this.buffer.lineLength(er) - 1) {
          // Multi-line: charwise selection covering full line content on all lines → linewise
          let y = ''; for (let r = sr; r <= er; r++) y += (r > sr ? '\n' : '') + this.buffer.lines[r];
          this._setReg(y, 'line');
          this.buffer.lines.splice(sr, er - sr + 1);
          if (this.buffer.lines.length === 0) this.buffer.lines = [''];
          this.cursor.row = Math.min(sr, this.buffer.lineCount - 1);
          this.cursor.col = this._firstNonBlank(this.cursor.row);
        } else if (sc === 0 && sr === er && ec >= this.buffer.lineLength(er) && this.buffer.lineCount > 1) {
          // Single line: v$ past end of line → linewise delete (includes newline)
          let y = this.buffer.lines[sr];
          this._setReg(y, 'line');
          this.buffer.lines.splice(sr, 1);
          if (this.buffer.lines.length === 0) this.buffer.lines = [''];
          this.cursor.row = Math.min(sr, this.buffer.lineCount - 1);
          this.cursor.col = this._firstNonBlank(this.cursor.row);
        } else {
          this._setReg(this._extractRange(sr, sc, er, ec), 'char');
          this._deleteRange(sr, sc, er, ec);
          this.cursor.row = sr; this.cursor.col = sc;
        }
        this._updateDesiredCol();
        this.mode = Mode.NORMAL; this.commandLine = '';
        this._redoStack = [];
        break;
      }
      case 'c': case 's': {
        if (this.mode === Mode.VISUAL_LINE) {
          let y = ''; for (let r = sr; r <= er; r++) y += (r > sr ? '\n' : '') + this.buffer.lines[r];
          this._setReg(y, 'line');
          this.buffer.lines.splice(sr, er - sr + 1, '');
          this.cursor.row = sr; this.cursor.col = 0;
        } else if (sc === 0 && ec >= this.buffer.lineLength(er) && sr === er && sr < this.buffer.lineCount - 1) {
          // v$ on a non-last line: selection includes newline, merge with next line
          const y = this.buffer.lines[sr] + '\n';
          this._setReg(y, 'char');
          // Merge: remove current line text and newline, joining with next line
          this.buffer.lines[sr] = this.buffer.lines[sr + 1];
          this.buffer.lines.splice(sr + 1, 1);
          this.cursor.row = sr; this.cursor.col = 0;
        } else if (sc === 0 && ec >= this.buffer.lineLength(er) && sr !== er) {
          // Multi-line charwise covering full lines: promote to linewise change
          let y = ''; for (let r = sr; r <= er; r++) y += (r > sr ? '\n' : '') + this.buffer.lines[r];
          this._setReg(y, 'line');
          this.buffer.lines.splice(sr, er - sr + 1, '');
          this.cursor.row = sr; this.cursor.col = 0;
        } else {
          this._setReg(this._extractRange(sr, sc, er, ec), 'char');
          this._deleteRange(sr, sc, er, ec);
          this.cursor.row = sr; this.cursor.col = sc;
        }
        this._updateDesiredCol();
        this._startRecording();
        this.mode = Mode.INSERT; this.commandLine = '-- INSERT --';
        this._redoStack = [];
        break;
      }
      case 'y': {
        if (this.mode === Mode.VISUAL_LINE) {
          let y = ''; for (let r = sr; r <= er; r++) y += (r > sr ? '\n' : '') + this.buffer.lines[r];
          this._setReg(y, 'line', 'yank');
        } else {
          this._setReg(this._extractRange(sr, sc, er, ec), 'char', 'yank');
        }
        this.mode = Mode.NORMAL; this.commandLine = '';
        this.cursor.row = sr; this.cursor.col = sc;
        break;
      }
      case '>': {
        const savedCol = this._desiredCol;
        for (let r = sr; r <= er; r++) this._shiftLineRight(r);
        this.mode = Mode.NORMAL; this.commandLine = '';
        this.cursor.row = sr; this.cursor.col = this._byteColForVirtCol(sr, savedCol);
        this._desiredCol = this._virtColEnd(sr, this.cursor.col);
        this._redoStack = [];
        break;
      }
      case '<': {
        const savedCol = this._desiredCol;
        for (let r = sr; r <= er; r++) this._shiftLineLeft(r);
        this.mode = Mode.NORMAL; this.commandLine = '';
        this.cursor.row = sr; this.cursor.col = this._byteColForVirtCol(sr, savedCol);
        this._desiredCol = this._virtColEnd(sr, this.cursor.col);
        this._redoStack = [];
        break;
      }
      case '~': {
        for (let r = sr; r <= er; r++) {
          const line = this.buffer.lines[r];
          const s = (r === sr && this.mode === Mode.VISUAL) ? sc : 0;
          const e = (r === er && this.mode === Mode.VISUAL) ? ec : line.length - 1;
          let nl = '';
          for (let c = 0; c < line.length; c++) {
            if (c >= s && c <= e) {
              const ch = line[c];
              nl += ch === ch.toUpperCase() ? ch.toLowerCase() : ch.toUpperCase();
            } else nl += line[c];
          }
          this.buffer.lines[r] = nl;
        }
        this.mode = Mode.NORMAL; this.commandLine = '';
        this.cursor.row = sr; this.cursor.col = sc;
        this._redoStack = [];
        break;
      }
      case 'U': {
        for (let r = sr; r <= er; r++) {
          const line = this.buffer.lines[r];
          const s = (r === sr && this.mode === Mode.VISUAL) ? sc : 0;
          const e = (r === er && this.mode === Mode.VISUAL) ? ec : line.length - 1;
          let nl = '';
          for (let c = 0; c < line.length; c++) {
            nl += (c >= s && c <= e) ? line[c].toUpperCase() : line[c];
          }
          this.buffer.lines[r] = nl;
        }
        this.mode = Mode.NORMAL; this.commandLine = '';
        this.cursor.row = sr; this.cursor.col = sc;
        this._redoStack = [];
        break;
      }
      case 'u': {
        for (let r = sr; r <= er; r++) {
          const line = this.buffer.lines[r];
          const s = (r === sr && this.mode === Mode.VISUAL) ? sc : 0;
          const e = (r === er && this.mode === Mode.VISUAL) ? ec : line.length - 1;
          let nl = '';
          for (let c = 0; c < line.length; c++) {
            nl += (c >= s && c <= e) ? line[c].toLowerCase() : line[c];
          }
          this.buffer.lines[r] = nl;
        }
        this.mode = Mode.NORMAL; this.commandLine = '';
        this.cursor.row = sr; this.cursor.col = sc;
        this._redoStack = [];
        break;
      }
      case '=': {
        this._cindent(sr, er);
        this.mode = Mode.NORMAL; this.commandLine = '';
        this.cursor.row = sr;
        this.cursor.col = 0;
        const lineCount = er - sr + 1;
        if (lineCount > 2) {
          this.commandLine = lineCount + ' lines indented';
          this._stickyCommandLine = true;
        }
        this._updateDesiredCol();
        this._redoStack = [];
        break;
      }
      case 'J': {
        let joinCol = 0;
        for (let r = sr; r < er; r++) {
          const cur = this.buffer.lines[sr];
          const next = this.buffer.lines[sr + 1];
          const trimmed = next.replace(/^\s+/, '');
          joinCol = cur.length;
          const nextFirstChar = trimmed.length > 0 ? trimmed[0] : '';
          const curEndsWithSpace = cur.length > 0 && (cur[cur.length - 1] === ' ' || cur[cur.length - 1] === '\t');
          let joined;
          if (cur.length === 0 || trimmed.length === 0 || nextFirstChar === ')' || curEndsWithSpace) {
            joined = cur + trimmed;
          } else {
            joined = cur + ' ' + trimmed;
          }
          this.buffer.lines[sr] = joined;
          this.buffer.lines.splice(sr + 1, 1);
        }
        this.mode = Mode.NORMAL; this.commandLine = '';
        this.cursor.row = sr; this.cursor.col = joinCol;
        this._updateDesiredCol();
        this._redoStack = [];
        break;
      }
      case 'p': {
        if (this.mode === Mode.VISUAL_LINE) {
          this.buffer.lines.splice(sr, er - sr + 1);
          if (this.buffer.lines.length === 0) this.buffer.lines = [''];
          this.cursor.row = Math.min(sr, this.buffer.lineCount - 1);
          if (this._regType === 'line') {
            const pl = this._unnamedReg.split('\n');
            this.buffer.lines.splice(sr, 0, ...pl);
          } else {
            this.buffer.lines.splice(sr, 0, this._unnamedReg);
          }
        } else {
          this._deleteRange(sr, sc, er, ec);
          this.cursor.row = sr; this.cursor.col = sc;
          const text = this._unnamedReg;
          if (text) {
            const before = this.buffer.lines[sr].slice(0, sc);
            const after = this.buffer.lines[sr].slice(sc);
            const pl = text.split('\n');
            if (pl.length === 1) {
              this.buffer.lines[sr] = before + text + after;
              this.cursor.col = sc + text.length - 1;
            } else {
              this.buffer.lines[sr] = before + pl[0];
              for (let i = 1; i < pl.length - 1; i++) this.buffer.lines.splice(sr + i, 0, pl[i]);
              const li = sr + pl.length - 1;
              this.buffer.lines.splice(li, 0, pl[pl.length - 1] + after);
              this.cursor.row = li;
              this.cursor.col = pl[pl.length - 1].length - 1;
            }
          }
        }
        this.mode = Mode.NORMAL; this.commandLine = '';
        this._redoStack = [];
        break;
      }
      case 'r': {
        this._pendingVisualR = true;
        return; // wait for replacement character
      }
    }

    // Set _lastChange for dot repeat of visual operations (not for y, r, p)
    const nonDotVisualOps = new Set(['y', 'r', 'p']);
    if (!nonDotVisualOps.has(key)) {
      const dotKeys = [];
      if (wasLinewise) {
        dotKeys.push('V');
        const lineCount = er - sr + 1;
        if (lineCount > 1) {
          for (const ch of String(lineCount - 1)) dotKeys.push(ch);
          dotKeys.push('j');
        }
      } else {
        dotKeys.push('v');
        if (sr === er) {
          // Single line charwise
          const extent = ec - sc;
          if (extent > 0) {
            for (const ch of String(extent)) dotKeys.push(ch);
            dotKeys.push('l');
          }
        } else {
          // Multi-line charwise: use number of lines
          for (const ch of String(er - sr)) dotKeys.push(ch);
          dotKeys.push('j');
        }
      }
      if (key === 'c' || key === 's') {
        this._dotPrefix = dotKeys.concat([key]);
      } else {
        dotKeys.push(key);
        this._lastChange = dotKeys;
      }
    }
  }

  _doVisualReplace(ch) {
    let sr, sc, er, ec;
    if (this.mode === Mode.VISUAL_BLOCK) {
      // Block replace
      const topRow = Math.min(this._visualStart.row, this.cursor.row);
      const bottomRow = Math.max(this._visualStart.row, this.cursor.row);
      const leftCol = Math.min(this._visualStart.col, this.cursor.col);
      const rightCol = Math.max(this._visualStart.col, this.cursor.col);
      this._saveSnapshot();
      for (let r = topRow; r <= bottomRow; r++) {
        const line = this.buffer.lines[r];
        const rc = Math.min(rightCol, line.length - 1);
        let nl = '';
        for (let c = 0; c < line.length; c++) {
          nl += (c >= leftCol && c <= rc) ? ch : line[c];
        }
        this.buffer.lines[r] = nl;
      }
      this.cursor.row = topRow; this.cursor.col = leftCol;
      this._updateDesiredCol();
      this.mode = Mode.NORMAL; this.commandLine = '';
      this._redoStack = [];
      return;
    }
    if (this.mode === Mode.VISUAL_LINE) {
      sr = Math.min(this._visualStart.row, this.cursor.row);
      er = Math.max(this._visualStart.row, this.cursor.row);
      sc = 0; ec = this.buffer.lineLength(er);
    } else {
      if (this._visualStart.row < this.cursor.row || (this._visualStart.row === this.cursor.row && this._visualStart.col <= this.cursor.col)) {
        sr = this._visualStart.row; sc = this._visualStart.col;
        er = this.cursor.row; ec = this.cursor.col;
      } else {
        sr = this.cursor.row; sc = this.cursor.col;
        er = this._visualStart.row; ec = this._visualStart.col;
      }
    }
    this._saveSnapshot();
    for (let r = sr; r <= er; r++) {
      const line = this.buffer.lines[r];
      const s = (this.mode === Mode.VISUAL_LINE) ? 0 : (r === sr ? sc : 0);
      const e = (this.mode === Mode.VISUAL_LINE) ? line.length - 1 : (r === er ? ec : line.length - 1);
      let nl = '';
      for (let c = 0; c < line.length; c++) {
        nl += (c >= s && c <= e) ? ch : line[c];
      }
      this.buffer.lines[r] = nl;
    }
    this.cursor.row = sr; this.cursor.col = sc;
    this._updateDesiredCol();
    this.mode = Mode.NORMAL; this.commandLine = '';
    this._redoStack = [];
  }

  // ── Visual Block helpers ──

  /** Compute the block selection rectangle from visualStart and cursor */
  _getBlockRect() {
    const topRow = Math.min(this._visualStart.row, this.cursor.row);
    const bottomRow = Math.max(this._visualStart.row, this.cursor.row);
    const leftCol = Math.min(this._visualStart.col, this.cursor.col);
    const rightCol = Math.max(this._visualStart.col, this.cursor.col);
    return { topRow, bottomRow, leftCol, rightCol, dollar: this._visualBlockDollar };
  }

  /** Block I/A: enter insert mode for block insert or append */
  _doVisualBlockInsert(key) {
    this._lastVisual = { mode: this.mode, start: { ...this._visualStart }, end: { ...this.cursor } };
    const { topRow, bottomRow, leftCol, rightCol, dollar } = this._getBlockRect();

    // Save snapshot with cursor at top-left
    const savedCursor = { ...this.cursor };
    this.cursor = { row: topRow, col: leftCol };
    this._saveSnapshot();

    let insertCol;
    if (key === 'I') {
      // Insert at left column of block on top row
      insertCol = leftCol;
    } else {
      // A: append after right column (or end of line with $)
      if (dollar) {
        insertCol = this.buffer.lineLength(topRow);
      } else {
        insertCol = rightCol + 1;
        // Pad line if needed
        const line = this.buffer.lines[topRow];
        if (line.length < insertCol) {
          this.buffer.lines[topRow] = line + ' '.repeat(insertCol - line.length);
        }
      }
    }

    const origLine = this.buffer.lines[topRow];
    this.cursor = { row: topRow, col: insertCol };

    this._blockInsertState = {
      mode: key, // 'I' or 'A'
      topRow, bottomRow, leftCol, rightCol, dollar,
      editRow: topRow,
      insertCol,
      origLine,
    };

    this._startRecording();
    this.mode = Mode.INSERT; this.commandLine = '-- INSERT --';
    this._redoStack = [];
  }

  /** Block d/c/y/>/</p action */
  _doVisualBlockAction(key) {
    this._lastVisual = { mode: this.mode, start: { ...this._visualStart }, end: { ...this.cursor } };
    const { topRow, bottomRow, leftCol, rightCol, dollar } = this._getBlockRect();

    // Save snapshot with cursor at top-left
    const savedCursor = { ...this.cursor };
    this.cursor = { row: topRow, col: leftCol };
    this._saveSnapshot();
    this.cursor = savedCursor;

    switch (key) {
      case 'd': case 'x': case 'Delete': {
        // Yank block text, then delete
        const blockLines = [];
        for (let r = topRow; r <= bottomRow; r++) {
          const line = this.buffer.lines[r];
          const rc = dollar ? line.length : Math.min(rightCol + 1, line.length);
          blockLines.push(line.slice(leftCol, rc));
        }
        this._setReg(blockLines.join('\n'), 'block');
        // Delete block columns
        for (let r = topRow; r <= bottomRow; r++) {
          const line = this.buffer.lines[r];
          const rc = dollar ? line.length : Math.min(rightCol + 1, line.length);
          this.buffer.lines[r] = line.slice(0, leftCol) + line.slice(rc);
        }
        this.cursor.row = topRow;
        this.cursor.col = Math.min(leftCol, Math.max(0, this.buffer.lineLength(topRow) - 1));
        this._updateDesiredCol();
        this.mode = Mode.NORMAL; this.commandLine = '';
        this._redoStack = [];
        break;
      }
      case 'c': case 's': {
        // Yank block, delete from all rows, enter insert on top row
        const blockLines = [];
        for (let r = topRow; r <= bottomRow; r++) {
          const line = this.buffer.lines[r];
          const rc = dollar ? line.length : Math.min(rightCol + 1, line.length);
          blockLines.push(line.slice(leftCol, rc));
        }
        this._setReg(blockLines.join('\n'), 'block');
        // Delete block columns from all rows
        for (let r = topRow; r <= bottomRow; r++) {
          const line = this.buffer.lines[r];
          const rc = dollar ? line.length : Math.min(rightCol + 1, line.length);
          this.buffer.lines[r] = line.slice(0, leftCol) + line.slice(rc);
        }
        const origLine = this.buffer.lines[topRow];
        this.cursor = { row: topRow, col: leftCol };

        this._blockInsertState = {
          mode: 'c',
          topRow, bottomRow, leftCol, rightCol, dollar,
          editRow: topRow,
          insertCol: leftCol,
          origLine,
        };

        this._startRecording();
        this.mode = Mode.INSERT; this.commandLine = '-- INSERT --';
        this._redoStack = [];
        break;
      }
      case 'y': {
        const blockLines = [];
        for (let r = topRow; r <= bottomRow; r++) {
          const line = this.buffer.lines[r];
          const rc = dollar ? line.length : Math.min(rightCol + 1, line.length);
          blockLines.push(line.slice(leftCol, rc));
        }
        this._setReg(blockLines.join('\n'), 'block', 'yank');
        this.cursor.row = topRow; this.cursor.col = leftCol;
        this.mode = Mode.NORMAL; this.commandLine = '';
        break;
      }
      case '>': {
        const savedCol = this._desiredCol;
        for (let r = topRow; r <= bottomRow; r++) this._shiftLineRight(r);
        this.mode = Mode.NORMAL;
        this.cursor.row = topRow;
        this.cursor.col = this._byteColForVirtCol(topRow, savedCol);
        this._desiredCol = this._virtColEnd(topRow, this.cursor.col);
        this._redoStack = [];
        // Show shift message for 2+ lines
        const lineCount = bottomRow - topRow + 1;
        if (lineCount >= 2) {
          this.commandLine = lineCount + ' lines >ed 1 time';
          this._stickyCommandLine = true;
        } else {
          this.commandLine = '';
        }
        break;
      }
      case '<': {
        const savedColL = this._desiredCol;
        for (let r = topRow; r <= bottomRow; r++) this._shiftLineLeft(r);
        this.mode = Mode.NORMAL;
        this.cursor.row = topRow;
        this.cursor.col = this._byteColForVirtCol(topRow, savedColL);
        this._desiredCol = this._virtColEnd(topRow, this.cursor.col);
        this._redoStack = [];
        const lineCountL = bottomRow - topRow + 1;
        if (lineCountL >= 2) {
          this.commandLine = lineCountL + ' lines <ed 1 time';
          this._stickyCommandLine = true;
        } else {
          this.commandLine = '';
        }
        break;
      }
      case 'p': {
        const reg = this._getReg();
        const text = reg.text || this._unnamedReg;
        const type = reg.type || this._regType;
        if (!text) { this.mode = Mode.NORMAL; this.commandLine = ''; break; }
        // Delete block first
        for (let r = topRow; r <= bottomRow; r++) {
          const line = this.buffer.lines[r];
          const rc = dollar ? line.length : Math.min(rightCol + 1, line.length);
          this.buffer.lines[r] = line.slice(0, leftCol) + line.slice(rc);
        }
        // Paste: insert register text at leftCol on each block row
        const pasteLines = text.split('\n');
        for (let i = 0; i < pasteLines.length; i++) {
          const r = topRow + i;
          if (r >= this.buffer.lineCount) this.buffer.lines.push('');
          const line = this.buffer.lines[r];
          const padded = line.length < leftCol ? line + ' '.repeat(leftCol - line.length) : line;
          this.buffer.lines[r] = padded.slice(0, leftCol) + pasteLines[i] + padded.slice(leftCol);
        }
        this.cursor.row = topRow; this.cursor.col = leftCol;
        this._updateDesiredCol();
        this.mode = Mode.NORMAL; this.commandLine = '';
        this._redoStack = [];
        break;
      }
      case '~': {
        for (let r = topRow; r <= bottomRow; r++) {
          const line = this.buffer.lines[r];
          const rc = dollar ? line.length - 1 : Math.min(rightCol, line.length - 1);
          let nl = '';
          for (let c = 0; c < line.length; c++) {
            if (c >= leftCol && c <= rc) {
              const ch = line[c];
              nl += ch === ch.toUpperCase() ? ch.toLowerCase() : ch.toUpperCase();
            } else nl += line[c];
          }
          this.buffer.lines[r] = nl;
        }
        this.cursor.row = topRow; this.cursor.col = leftCol;
        this.mode = Mode.NORMAL; this.commandLine = '';
        this._redoStack = [];
        break;
      }
      default:
        // For unhandled block keys, fall through to normal visual action
        this.cursor = savedCursor;
        this._doVisualAction(key);
        break;
    }
  }

  // ── Motion execution ──

  _doMotion(key) {
    const sr = this.cursor.row, sc = this.cursor.col;
    // Classify motion inclusivity for operator-pending mode
    const inclusiveMotions = new Set(['e', 'E', '$', 'G', '%', 'H', 'M', 'L', ';', ',']);
    this._motionInclusive = inclusiveMotions.has(key);
    switch (key) {
      case 'h': case 'ArrowLeft': case 'Backspace': {
        const c = this._getCount();
        for (let i = 0; i < c; i++) { if (this.cursor.col > 0) this.cursor.col--; }
        this._updateDesiredCol();
        break;
      }
      case 'l': case 'ArrowRight': case ' ': {
        const c = this._getCount();
        for (let i = 0; i < c; i++) { if (this.cursor.col < this._maxCol()) this.cursor.col++; }
        this._updateDesiredCol();
        break;
      }
      case 'j': case 'ArrowDown': {
        const c = this._getCount();
        const startRow = this.cursor.row;
        for (let i = 0; i < c; i++) { if (this.cursor.row < this.buffer.lineCount - 1) this.cursor.row++; }
        this._applyDesiredCol();
        if (this.cursor.row !== startRow) this._motionLinewise = true;
        break;
      }
      case 'k': case 'ArrowUp': {
        const c = this._getCount();
        const startRow = this.cursor.row;
        for (let i = 0; i < c; i++) { if (this.cursor.row > 0) this.cursor.row--; }
        this._applyDesiredCol();
        if (this.cursor.row !== startRow) this._motionLinewise = true;
        break;
      }
      case 'w': { const c = this._getCount(); for (let i = 0; i < c; i++) this._moveWordForward(false); this._updateDesiredCol(); break; }
      case 'W': { const c = this._getCount(); for (let i = 0; i < c; i++) this._moveWordForward(true); this._updateDesiredCol(); break; }
      case 'b': { const c = this._getCount(); for (let i = 0; i < c; i++) this._moveWordBackward(false); this._updateDesiredCol(); break; }
      case 'B': { const c = this._getCount(); for (let i = 0; i < c; i++) this._moveWordBackward(true); this._updateDesiredCol(); break; }
      case 'e': { const c = this._getCount(); for (let i = 0; i < c; i++) this._moveWordEnd(false); this._updateDesiredCol(); break; }
      case 'E': { const c = this._getCount(); for (let i = 0; i < c; i++) this._moveWordEnd(true); this._updateDesiredCol(); break; }
      case '0': this.cursor.col = 0; this._desiredCol = 0; break;
      case '^': this.cursor.col = this._firstNonBlank(this.cursor.row); this._updateDesiredCol(); break;
      case '$': {
        const c = this._getCount();
        if (c > 1) this.cursor.row = Math.min(this.cursor.row + c - 1, this.buffer.lineCount - 1);
        // In visual mode, $ goes one past the last char (like insert mode)
        if (this.mode === Mode.VISUAL || this.mode === Mode.VISUAL_LINE || this.mode === Mode.VISUAL_BLOCK) {
          this.cursor.col = this.buffer.lineLength(this.cursor.row);
        } else {
          this.cursor.col = this._maxCol();
        }
        this._desiredCol = Infinity;
        break;
      }
      case 'G': {
        if (this._hasCount()) {
          const n = this._getCount();
          this.cursor.row = Math.max(0, Math.min(n - 1, this.buffer.lineCount - 1));
          this.cursor.col = 0;
        } else {
          this.cursor.row = this.buffer.lineCount - 1;
          this._applyDesiredCol();
        }
        this._updateDesiredCol();
        this._motionLinewise = true;
        break;
      }
      case '{': {
        const c = this._getCount();
        const saved = { row: this.cursor.row, col: this.cursor.col };
        let ok = true;
        for (let i = 0; i < c; i++) { if (!this._moveParagraphBackward()) { ok = false; break; } }
        if (!ok) { this.cursor.row = saved.row; this.cursor.col = saved.col; }
        this._updateDesiredCol();
        this._motionLinewise = true;
        this._motionExclusive = true; // paragraph motions are exclusive linewise
        break;
      }
      case '}': {
        const c = this._getCount();
        const saved = { row: this.cursor.row, col: this.cursor.col };
        let ok = true;
        for (let i = 0; i < c; i++) { if (!this._moveParagraphForward()) { ok = false; break; } }
        if (!ok) { this.cursor.row = saved.row; this.cursor.col = saved.col; }
        this._updateDesiredCol();
        this._motionLinewise = true;
        this._motionExclusive = true; // paragraph motions are exclusive linewise
        break;
      }
      case '%': if (!this._hasCount()) this._doMatchBracket(); break;
      case 'H': {
        const c = this._getCount() - 1;
        this.cursor.row = Math.min(this.scrollTop + c, this.buffer.lineCount - 1);
        this.cursor.col = this._byteColForVirtCol(this.cursor.row, this._desiredCol);
        this._motionLinewise = true;
        break;
      }
      case 'M': {
        const vis = Math.min(this._textRows, this.buffer.lineCount - this.scrollTop);
        this.cursor.row = this.scrollTop + Math.floor((vis - 1) / 2);
        this.cursor.col = this._byteColForVirtCol(this.cursor.row, this._desiredCol);
        this._motionLinewise = true;
        break;
      }
      case 'L': {
        const c = this._getCount() - 1;
        const lv = this.scrollTop + Math.min(this._textRows, this.buffer.lineCount - this.scrollTop) - 1;
        this.cursor.row = Math.max(this.scrollTop, lv - c);
        this.cursor.col = this._byteColForVirtCol(this.cursor.row, this._desiredCol);
        this._motionLinewise = true;
        break;
      }
      case ';': {
        if (this._lastFind) {
          const c = this._getCount();
          this._doFindRepeat(this._lastFind.type, this._lastFind.char, c);
          // If find failed (cursor didn't move), clear inclusive flag so operator doesn't fire
          if (this.cursor.row === sr && this.cursor.col === sc) this._motionInclusive = false;
        }
        break;
      }
      case ',': {
        if (this._lastFind) {
          const c = this._getCount();
          const rev = { f: 'F', F: 'f', t: 'T', T: 't' }[this._lastFind.type];
          this._doFindRepeat(rev, this._lastFind.char, c);
          // If find failed (cursor didn't move), clear inclusive flag so operator doesn't fire
          if (this.cursor.row === sr && this.cursor.col === sc) this._motionInclusive = false;
        }
        break;
      }
      // ── Search motions ──
      case 'n': {
        const c = this._getCount();
        for (let i = 0; i < c; i++) this._searchNext(this._searchForward);
        this._showCurSearch = true;
        this._hlsearchActive = true;
        break;
      }
      case 'N': {
        const c = this._getCount();
        for (let i = 0; i < c; i++) this._searchNext(!this._searchForward);
        this._showCurSearch = true;
        this._hlsearchActive = true;
        break;
      }
      case '*': {
        const w = this._wordUnderCursor();
        if (w) { this._searchPattern = '\\b' + w + '\\b'; this._searchForward = true; this._searchNext(true); this._showCurSearch = true; this._hlsearchActive = true; }
        break;
      }
      case '#': {
        const w = this._wordUnderCursor();
        if (w) { this._searchPattern = '\\b' + w + '\\b'; this._searchForward = false; this._searchNext(false); this._showCurSearch = true; this._hlsearchActive = true; }
        break;
      }
      // ── Line motions ──
      case '+': case 'Enter': {
        const c = this._getCount();
        this.cursor.row = Math.min(this.cursor.row + c, this.buffer.lineCount - 1);
        this.cursor.col = this._firstNonBlank(this.cursor.row);
        this._updateDesiredCol();
        this._motionLinewise = true;
        break;
      }
      case '-': {
        const c = this._getCount();
        this.cursor.row = Math.max(this.cursor.row - c, 0);
        this.cursor.col = this._firstNonBlank(this.cursor.row);
        this._updateDesiredCol();
        this._motionLinewise = true;
        break;
      }
      case '_': {
        const c = this._getCount();
        this.cursor.row = Math.min(this.cursor.row + c - 1, this.buffer.lineCount - 1);
        this.cursor.col = this._firstNonBlank(this.cursor.row);
        this._updateDesiredCol();
        this._motionLinewise = true;
        break;
      }
      // g_ = last non-blank on line
      case 'g_': {
        const c = this._getCount();
        if (c > 1) this.cursor.row = Math.min(this.cursor.row + c - 1, this.buffer.lineCount - 1);
        this.cursor.col = this._lastNonBlank(this.cursor.row);
        this._updateDesiredCol();
        this._motionInclusive = true;
        break;
      }
      // ── Column motion ──
      case '|': {
        const c = this._getCount() - 1;  // virtual column (0-indexed)
        this.cursor.col = this._byteColForVirtCol(this.cursor.row, c);
        this._updateDesiredCol();
        break;
      }
      // ── Sentence motions ──
      case ')': {
        const c = this._getCount();
        for (let i = 0; i < c; i++) this._moveSentenceForward();
        this._updateDesiredCol();
        break;
      }
      case '(': {
        const c = this._getCount();
        for (let i = 0; i < c; i++) this._moveSentenceBackward();
        this._updateDesiredCol();
        break;
      }
      default: return false;
    }
    return (this.cursor.row !== sr || this.cursor.col !== sc);
  }

  // ── Operator execution ──

  _executeOperator(startPos, endPos) {
    const op = this._pendingOp;
    let sr = startPos.row, sc = startPos.col;
    let er = endPos.row, ec = endPos.col;
    let isLinewise = this._motionLinewise;
    // Detect backward motion (endPos is before startPos)
    const backward = (er < sr || (er === sr && ec < sc));
    if (backward) [sr, sc, er, ec] = [er, ec, sr, sc];

    // zf operator: create fold from startRow to endRow
    if (op === 'zf') {
      const foldSr = Math.min(startPos.row, endPos.row);
      const foldEr = Math.max(startPos.row, endPos.row);
      if (foldSr < foldEr) {  // Need at least 2 lines
        this._folds.push({ startRow: foldSr, endRow: foldEr, closed: true });
        // Sort folds by startRow
        this._folds.sort((a, b) => a.startRow - b.startRow);
      }
      this.cursor.row = foldSr;
      this.cursor.col = this._firstNonBlank(foldSr);
      this._updateDesiredCol();
      this._motionLinewise = false;
      this._motionInclusive = false;
      this._motionExclusive = false;
      return;
    }

    // ! operator: enter command mode with range pre-filled for shell filter
    if (op === '!') {
      // Always line-wise for ! operator
      const lineSr = Math.min(startPos.row, endPos.row);
      const lineEr = Math.max(startPos.row, endPos.row);
      let rangeStr;
      if (lineSr === lineEr) {
        rangeStr = '.';
      } else {
        rangeStr = '.,.+' + (lineEr - lineSr);
      }
      this._filterRange = { sr: lineSr, er: lineEr };
      this.mode = Mode.COMMAND;
      this._searchInput = rangeStr + '!';
      this.commandLine = ':' + rangeStr + '!';
      this._motionLinewise = false;
      this._motionInclusive = false;
      this._motionExclusive = false;
      return;
    }

    // Vim rule: exclusive motion ending at column 0 adjusts to inclusive
    // end of previous line (`:help exclusive`)
    if (!isLinewise && !this._motionInclusive && ec === 0 && er > sr) {
      er--;
      ec = this.buffer.lineLength(er) > 0 ? this.buffer.lineLength(er) - 1 : 0;
      this._motionInclusive = true;
      // Further Vim rule (`:help exclusive-linewise`): if the adjusted range
      // now starts at column 0 and ends at end of a line, promote to linewise.
      // This applies for d/c operators but not for y (yw charwise yank).
      if (sc === 0 && ec >= (this.buffer.lineLength(er) > 0 ? this.buffer.lineLength(er) - 1 : 0)
          && op !== 'y') {
        isLinewise = true;
        this._motionLinewise = true;
      }
    }

    // For exclusive linewise motions (e.g., d}, d{), exclude the endpoint row
    // For forward d}: exclude the motion endpoint (the blank line), unless at EOF
    // For backward d{: always exclude the operator start position (the line we started on)
    if (isLinewise && this._motionExclusive) {
      if (backward) {
        // d{: exclude the operator start position (er after swap = where cursor was)
        er--;
      } else {
        // d}: exclude the motion endpoint (er = blank line or EOF)
        // But if motion hit end of file, include it
        if (er < this.buffer.lineCount - 1) {
          er--;
        }
      }
      if (sr > er) {
        // For 'c' operator, zero-width exclusive range = enter insert mode
        if (op === 'c') {
          this.cursor.row = this._opStartPos.row;
          this.cursor.col = this._opStartPos.col;
          this._saveSnapshot();
          this._startRecording();
          this.mode = Mode.INSERT; this.commandLine = '-- INSERT --';
          this._redoStack = [];
        }
        this._motionLinewise = false;
        this._motionInclusive = false;
        this._motionExclusive = false;
        return;
      }
    }

    // For inclusive motions, advance ec by 1 to make slice work
    // But for backward inclusive motions, ec is the original cursor position
    // and should be excluded (Vim behavior: backward inclusive = [motionDest, cursorPos))
    const inclusive = this._motionInclusive;
    let ecSlice;
    if (isLinewise) {
      ecSlice = ec;
    } else if (inclusive && !backward) {
      ecSlice = ec + 1;
    } else if (inclusive && backward) {
      ecSlice = ec; // backward inclusive: exclude the original cursor position
    } else {
      ecSlice = ec;
    }

    // Save snapshot with cursor at the operator start position (where the
    // command was initiated, e.g. where 'd' was pressed).  The motion may
    // have moved this.cursor already, but Vim's undo restores cursor to the
    // start of the changed region.
    const savedCursor = { ...this.cursor };
    this.cursor = { ...this._opStartPos };
    this._saveSnapshot();
    this.cursor = savedCursor;

    switch (op) {
      case 'd': {
        if (isLinewise) {
          let y = ''; for (let r = sr; r <= er; r++) y += (r > sr ? '\n' : '') + this.buffer.lines[r];
          this._setReg(y, 'line');
          this.buffer.lines.splice(sr, er - sr + 1);
          if (this.buffer.lines.length === 0) this.buffer.lines = [''];
          this.cursor.row = Math.min(sr, this.buffer.lineCount - 1);
          this.cursor.col = this._firstNonBlank(this.cursor.row);
        } else if (sr === er) {
          this._setReg(this.buffer.lines[sr].slice(sc, ecSlice), 'char');
          this.buffer.lines[sr] = this.buffer.lines[sr].slice(0, sc) + this.buffer.lines[sr].slice(ecSlice);
          this.cursor.row = sr; this.cursor.col = Math.min(sc, Math.max(0, this.buffer.lines[sr].length - 1));
        } else {
          // Cross-line charwise delete
          let y = this.buffer.lines[sr].slice(sc);
          for (let r = sr + 1; r < er; r++) y += '\n' + this.buffer.lines[r];
          y += '\n' + this.buffer.lines[er].slice(0, ecSlice);
          this._setReg(y, 'char');
          const newLine = this.buffer.lines[sr].slice(0, sc) + this.buffer.lines[er].slice(ecSlice);
          this.buffer.lines.splice(sr, er - sr + 1, newLine);
          this.cursor.row = sr; this.cursor.col = Math.min(sc, Math.max(0, this.buffer.lines[sr].length - 1));
        }
        this._startRecording(); this._stopRecording();
        this._redoStack = [];
        break;
      }
      case 'c': {
        if (isLinewise) {
          let y = ''; for (let r = sr; r <= er; r++) y += (r > sr ? '\n' : '') + this.buffer.lines[r];
          this._setReg(y, 'line');
          this.buffer.lines.splice(sr, er - sr + 1, '');
          this.cursor.row = sr; this.cursor.col = 0;
        } else if (sr === er) {
          this._setReg(this.buffer.lines[sr].slice(sc, ecSlice), 'char');
          this.buffer.lines[sr] = this.buffer.lines[sr].slice(0, sc) + this.buffer.lines[sr].slice(ecSlice);
          this.cursor.row = sr; this.cursor.col = sc;
        } else {
          // Cross-line charwise change
          let y = this.buffer.lines[sr].slice(sc);
          for (let r = sr + 1; r < er; r++) y += '\n' + this.buffer.lines[r];
          y += '\n' + this.buffer.lines[er].slice(0, ecSlice);
          this._setReg(y, 'char');
          const newLine = this.buffer.lines[sr].slice(0, sc) + this.buffer.lines[er].slice(ecSlice);
          this.buffer.lines.splice(sr, er - sr + 1, newLine);
          this.cursor.row = sr; this.cursor.col = sc;
        }
        this._startRecording();
        this.mode = Mode.INSERT; this.commandLine = '-- INSERT --';
        this._redoStack = [];
        break;
      }
      case 'y': {
        if (isLinewise) {
          let y = ''; for (let r = sr; r <= er; r++) y += (r > sr ? '\n' : '') + this.buffer.lines[r];
          this._setReg(y, 'line', 'yank');
        } else {
          this._setReg(this.buffer.lines[sr].slice(sc, ecSlice), 'char', 'yank');
        }
        this.cursor.row = sr; this.cursor.col = sc;
        break;
      }
      case '>': {
        const savedCol = this._desiredCol;
        for (let r = sr; r <= er; r++) this._shiftLineRight(r);
        this.cursor.row = sr; this.cursor.col = this._byteColForVirtCol(sr, savedCol);
        this._desiredCol = this._virtColEnd(sr, this.cursor.col);
        this._redoStack = [];
        break;
      }
      case '<': {
        const savedCol = this._desiredCol;
        for (let r = sr; r <= er; r++) this._shiftLineLeft(r);
        this.cursor.row = sr; this.cursor.col = this._byteColForVirtCol(sr, savedCol);
        this._desiredCol = this._virtColEnd(sr, this.cursor.col);
        this._redoStack = [];
        break;
      }
      case 'gu': {
        if (isLinewise) { for (let r = sr; r <= er; r++) this.buffer.lines[r] = this.buffer.lines[r].toLowerCase(); }
        else { const l = this.buffer.lines[sr]; this.buffer.lines[sr] = l.slice(0, sc) + l.slice(sc, ecSlice).toLowerCase() + l.slice(ecSlice); }
        this.cursor.row = sr; this.cursor.col = sc; this._redoStack = [];
        break;
      }
      case 'gU': {
        if (isLinewise) { for (let r = sr; r <= er; r++) this.buffer.lines[r] = this.buffer.lines[r].toUpperCase(); }
        else { const l = this.buffer.lines[sr]; this.buffer.lines[sr] = l.slice(0, sc) + l.slice(sc, ecSlice).toUpperCase() + l.slice(ecSlice); }
        this.cursor.row = sr; this.cursor.col = sc; this._redoStack = [];
        break;
      }
      case 'g~': {
        const toggle = s => [...s].map(c => c === c.toUpperCase() ? c.toLowerCase() : c.toUpperCase()).join('');
        if (isLinewise) { for (let r = sr; r <= er; r++) this.buffer.lines[r] = toggle(this.buffer.lines[r]); }
        else { const l = this.buffer.lines[sr]; this.buffer.lines[sr] = l.slice(0, sc) + toggle(l.slice(sc, ecSlice)) + l.slice(ecSlice); }
        this.cursor.row = sr; this.cursor.col = sc; this._redoStack = [];
        break;
      }
      case '=': {
        this._cindent(sr, er);
        this.cursor.row = sr;
        this.cursor.col = 0;
        const lineCount = er - sr + 1;
        if (lineCount > 2) {
          this.commandLine = lineCount + ' lines indented';
          this._stickyCommandLine = true;
        }
        this._redoStack = [];
        break;
      }
      case 'g?': {
        if (isLinewise) {
          for (let r = sr; r <= er; r++) this.buffer.lines[r] = this._rot13(this.buffer.lines[r]);
        } else {
          const l = this.buffer.lines[sr];
          this.buffer.lines[sr] = l.slice(0, sc) + this._rot13(l.slice(sc, ecSlice)) + l.slice(ecSlice);
        }
        this.cursor.row = sr; this.cursor.col = sc; this._redoStack = [];
        break;
      }
      case 'gq': {
        if (sr === er) {
          // Single line: no-op, just move cursor to first non-blank
          this.cursor.row = sr;
          this.cursor.col = this._firstNonBlank(sr);
        } else {
          // Join lines in range: concatenate with spaces
          let joined = this.buffer.lines[sr];
          for (let r = sr + 1; r <= er; r++) {
            const trimmed = this.buffer.lines[r].replace(/^\s+/, '');
            if (joined.length > 0 && trimmed.length > 0) {
              joined += ' ' + trimmed;
            } else {
              joined += trimmed;
            }
          }
          this.buffer.lines.splice(sr, er - sr + 1, joined);
          this.cursor.row = sr;
          this.cursor.col = this._firstNonBlank(sr);
        }
        this._redoStack = [];
        break;
      }
      case 'gw': {
        const savedRow = this._opStartPos.row;
        const savedCol = this._opStartPos.col;
        if (sr === er) {
          // Single line: no-op
        } else {
          // Join lines in range
          let joined = this.buffer.lines[sr];
          for (let r = sr + 1; r <= er; r++) {
            const trimmed = this.buffer.lines[r].replace(/^\s+/, '');
            if (joined.length > 0 && trimmed.length > 0) {
              joined += ' ' + trimmed;
            } else {
              joined += trimmed;
            }
          }
          this.buffer.lines.splice(sr, er - sr + 1, joined);
        }
        // Restore cursor position
        this.cursor.row = Math.min(savedRow, this.buffer.lineCount - 1);
        this.cursor.col = Math.min(savedCol, Math.max(0, this.buffer.lineLength(this.cursor.row) - 1));
        this._redoStack = [];
        break;
      }
    }
    this._updateDesiredCol();
    // After text-modifying operator, update CurSearch to cursor position
    // y operator: cursor returns to start, don't show CurSearch
    if (op === 'y') {
      this._showCurSearch = false;
      this._curSearchPos = null;
    } else if (this._showCurSearch && this._searchPattern) {
      this._updateCurSearchPos();
    }
  }

  _updateCurSearchPos() {
    if (!this._searchPattern) return;
    try {
      const re = new RegExp(this._vimPatternToJs(this._searchPattern));
      const line = this.buffer.lines[this.cursor.row] || '';
      const m = line.slice(this.cursor.col).match(re);
      if (m) {
        this._curSearchPos = { row: this.cursor.row, col: this.cursor.col + m.index };
      } else {
        // Search from the beginning of the line
        const m2 = line.match(re);
        if (m2) {
          this._curSearchPos = { row: this.cursor.row, col: m2.index };
        } else {
          this._curSearchPos = null;
        }
      }
    } catch {
      this._curSearchPos = null;
    }
  }

  /** Set CurSearch position only if cursor is exactly at the start of a match */
  _setCurSearchAtCursor() {
    if (!this._searchPattern) { this._curSearchPos = null; return; }
    try {
      const re = new RegExp(this._vimPatternToJs(this._searchPattern));
      const line = this.buffer.lines[this.cursor.row] || '';
      const m = line.slice(this.cursor.col).match(re);
      if (m && m.index === 0) {
        this._curSearchPos = { row: this.cursor.row, col: this.cursor.col };
      } else {
        this._curSearchPos = null;
      }
    } catch {
      this._curSearchPos = null;
    }
  }

  _executeOperatorRange(range) {
    const op = this._pendingOp;
    this._saveSnapshot();

    // Linewise text objects (e.g., ip/ap paragraphs)
    if (range.linewise) {
      const { startRow, endRow } = range;
      switch (op) {
        case 'd': {
          let y = '';
          for (let r = startRow; r <= endRow; r++) y += (r > startRow ? '\n' : '') + this.buffer.lines[r];
          this._setReg(y, 'line');
          this.buffer.lines.splice(startRow, endRow - startRow + 1);
          if (this.buffer.lines.length === 0) this.buffer.lines = [''];
          this.cursor.row = Math.min(startRow, this.buffer.lineCount - 1);
          this.cursor.col = this._firstNonBlank(this.cursor.row);
          this._startRecording(); this._stopRecording();
          this._redoStack = [];
          break;
        }
        case 'c': {
          let y = '';
          for (let r = startRow; r <= endRow; r++) y += (r > startRow ? '\n' : '') + this.buffer.lines[r];
          this._setReg(y, 'line');
          this.buffer.lines.splice(startRow, endRow - startRow + 1, '');
          this.cursor.row = startRow; this.cursor.col = 0;
          this._startRecording();
          this.mode = Mode.INSERT; this.commandLine = '-- INSERT --';
          this._redoStack = [];
          break;
        }
        case 'y': {
          let y = '';
          for (let r = startRow; r <= endRow; r++) y += (r > startRow ? '\n' : '') + this.buffer.lines[r];
          this._setReg(y, 'line', 'yank');
          this.cursor.row = startRow;
          this.cursor.col = this._firstNonBlank(startRow);
          break;
        }
      }
      this._updateDesiredCol();
      return;
    }

    const { startRow, startCol, endRow, endCol } = range;

    switch (op) {
      case 'd': {
        if (startRow !== endRow) {
          let y = this.buffer.lines[startRow].slice(startCol);
          for (let r = startRow + 1; r < endRow; r++) y += '\n' + this.buffer.lines[r];
          y += '\n' + this.buffer.lines[endRow].slice(0, endCol);
          this._setReg(y, 'char');
          this._deleteRange(startRow, startCol, endRow, endCol - 1);
        } else {
          this._setReg(this.buffer.lines[startRow].slice(startCol, endCol), 'char');
          this.buffer.lines[startRow] = this.buffer.lines[startRow].slice(0, startCol) + this.buffer.lines[startRow].slice(endCol);
        }
        this.cursor.row = startRow;
        this.cursor.col = startCol;
        this._startRecording(); this._stopRecording();
        this._redoStack = [];
        break;
      }
      case 'c': {
        if (range.multilineInner && startCol === 0) {
          // ci( / ci{ multiline where inner starts on a new line after the
          // opening delimiter: nvim deletes all inner lines and inserts
          // a blank line with the indentation of the first inner line,
          // keeping the opening/closing delimiter lines intact.
          let cy = this.buffer.lines[startRow].slice(startCol);
          for (let r = startRow + 1; r < endRow; r++) cy += '\n' + this.buffer.lines[r];
          cy += '\n' + this.buffer.lines[endRow].slice(0, endCol);
          this._setReg(cy, 'char');
          // Grab indentation from the first inner line before modifying
          const firstInnerLine = this.buffer.lines[startRow];
          const indentMatch = firstInnerLine.match(/^(\s*)/);
          const indent = indentMatch ? indentMatch[1] : '';
          // Trim the closing delimiter line (keep from endCol onwards)
          this.buffer.lines[endRow] = this.buffer.lines[endRow].slice(endCol);
          // Replace inner lines (startRow through endRow-1) with a single blank indented line
          this.buffer.lines.splice(startRow, endRow - startRow, indent);
          // Cursor goes on the blank indented line
          this.cursor.row = startRow; this.cursor.col = indent.length;
        } else if (startRow !== endRow) {
          let cy = this.buffer.lines[startRow].slice(startCol);
          for (let r = startRow + 1; r < endRow; r++) cy += '\n' + this.buffer.lines[r];
          cy += '\n' + this.buffer.lines[endRow].slice(0, endCol);
          this._setReg(cy, 'char');
          this._deleteRange(startRow, startCol, endRow, endCol - 1);
          this.cursor.row = startRow; this.cursor.col = startCol;
        } else {
          const l = this.buffer.lines[startRow];
          this._setReg(l.slice(startCol, endCol), 'char');
          this.buffer.lines[startRow] = l.slice(0, startCol) + l.slice(endCol);
          this.cursor.row = startRow; this.cursor.col = startCol;
        }
        this._startRecording();
        this.mode = Mode.INSERT; this.commandLine = '-- INSERT --';
        this._redoStack = [];
        break;
      }
      case 'y': {
        if (startRow !== endRow) {
          let y = this.buffer.lines[startRow].slice(startCol);
          for (let r = startRow + 1; r < endRow; r++) y += '\n' + this.buffer.lines[r];
          y += '\n' + this.buffer.lines[endRow].slice(0, endCol);
          this._setReg(y, 'char', 'yank');
        } else {
          this._setReg(this.buffer.lines[startRow].slice(startCol, endCol), 'char', 'yank');
        }
        break;
      }
      case 'gu': {
        if (startRow === endRow) {
          const l = this.buffer.lines[startRow];
          this.buffer.lines[startRow] = l.slice(0, startCol) + l.slice(startCol, endCol).toLowerCase() + l.slice(endCol);
        } else {
          // Multi-line charwise: first line from startCol, middle lines fully, last line to endCol
          const l0 = this.buffer.lines[startRow];
          this.buffer.lines[startRow] = l0.slice(0, startCol) + l0.slice(startCol).toLowerCase();
          for (let r = startRow + 1; r < endRow; r++) this.buffer.lines[r] = this.buffer.lines[r].toLowerCase();
          const lE = this.buffer.lines[endRow];
          this.buffer.lines[endRow] = lE.slice(0, endCol).toLowerCase() + lE.slice(endCol);
        }
        this.cursor.row = startRow; this.cursor.col = startCol; this._redoStack = [];
        break;
      }
      case 'gU': {
        if (startRow === endRow) {
          const l = this.buffer.lines[startRow];
          this.buffer.lines[startRow] = l.slice(0, startCol) + l.slice(startCol, endCol).toUpperCase() + l.slice(endCol);
        } else {
          const l0 = this.buffer.lines[startRow];
          this.buffer.lines[startRow] = l0.slice(0, startCol) + l0.slice(startCol).toUpperCase();
          for (let r = startRow + 1; r < endRow; r++) this.buffer.lines[r] = this.buffer.lines[r].toUpperCase();
          const lE = this.buffer.lines[endRow];
          this.buffer.lines[endRow] = lE.slice(0, endCol).toUpperCase() + lE.slice(endCol);
        }
        this.cursor.row = startRow; this.cursor.col = startCol; this._redoStack = [];
        break;
      }
      case 'g~': {
        const toggle = s => [...s].map(c => c === c.toUpperCase() ? c.toLowerCase() : c.toUpperCase()).join('');
        if (startRow === endRow) {
          const l = this.buffer.lines[startRow];
          this.buffer.lines[startRow] = l.slice(0, startCol) + toggle(l.slice(startCol, endCol)) + l.slice(endCol);
        } else {
          const l0 = this.buffer.lines[startRow];
          this.buffer.lines[startRow] = l0.slice(0, startCol) + toggle(l0.slice(startCol));
          for (let r = startRow + 1; r < endRow; r++) this.buffer.lines[r] = toggle(this.buffer.lines[r]);
          const lE = this.buffer.lines[endRow];
          this.buffer.lines[endRow] = toggle(lE.slice(0, endCol)) + lE.slice(endCol);
        }
        this.cursor.row = startRow; this.cursor.col = startCol; this._redoStack = [];
        break;
      }
    }
    this._updateDesiredCol();
  }

  // ── Line operations (dd, cc, yy, >>, <<) ──

  _doLineOperation(op, count) {
    const sr = this.cursor.row;
    // If on last line and count > 1, do nothing (Neovim behavior)
    if (sr === this.buffer.lineCount - 1 && count > 1) return;
    const er = Math.min(sr + count - 1, this.buffer.lineCount - 1);
    this._saveSnapshot();

    switch (op) {
      case 'd': {
        let y = ''; for (let r = sr; r <= er; r++) y += (r > sr ? '\n' : '') + this.buffer.lines[r];
        this._setReg(y, 'line');
        this.buffer.lines.splice(sr, er - sr + 1);
        if (this.buffer.lines.length === 0) this.buffer.lines = [''];
        this.cursor.row = Math.min(sr, this.buffer.lineCount - 1);
        this.cursor.col = this._firstNonBlank(this.cursor.row);
        this._startRecording(); this._stopRecording();
        this._redoStack = [];
        break;
      }
      case 'c': {
        let y = ''; for (let r = sr; r <= er; r++) y += (r > sr ? '\n' : '') + this.buffer.lines[r];
        this._setReg(y, 'line');
        // Preserve leading whitespace from first line (matches S behavior)
        const indent = this.buffer.lines[sr].match(/^\s*/)[0];
        this.buffer.lines.splice(sr, er - sr + 1, indent);
        this.cursor.row = sr; this.cursor.col = indent.length;
        this._startRecording();
        this.mode = Mode.INSERT; this.commandLine = '-- INSERT --';
        this._redoStack = [];
        break;
      }
      case 'y': {
        let y = ''; for (let r = sr; r <= er; r++) y += (r > sr ? '\n' : '') + this.buffer.lines[r];
        this._setReg(y, 'line', 'yank');
        break;
      }
      case '>': {
        const savedCol = this._desiredCol;
        for (let r = sr; r <= er; r++) this._shiftLineRight(r);
        this.cursor.col = this._byteColForVirtCol(sr, savedCol);
        this._desiredCol = this._virtColEnd(sr, this.cursor.col);
        // Store post-op cursor for redo (Vim redo of >> positions at first non-blank)
        this._undoStack[this._undoStack.length - 1].redoCursor = { ...this.cursor };
        this._redoStack = [];
        break;
      }
      case '<': {
        const savedCol = this._desiredCol;
        for (let r = sr; r <= er; r++) this._shiftLineLeft(r);
        this.cursor.col = this._byteColForVirtCol(sr, savedCol);
        this._desiredCol = this._virtColEnd(sr, this.cursor.col);
        this._redoStack = [];
        break;
      }
      case 'gu': {
        for (let r = sr; r <= er; r++) this.buffer.lines[r] = this.buffer.lines[r].toLowerCase();
        this.cursor.col = this._firstNonBlank(this.cursor.row);
        this._redoStack = [];
        break;
      }
      case 'gU': {
        for (let r = sr; r <= er; r++) this.buffer.lines[r] = this.buffer.lines[r].toUpperCase();
        this.cursor.col = this._firstNonBlank(this.cursor.row);
        this._redoStack = [];
        break;
      }
      case 'g~': {
        const toggle = s => [...s].map(c => c === c.toUpperCase() ? c.toLowerCase() : c.toUpperCase()).join('');
        for (let r = sr; r <= er; r++) this.buffer.lines[r] = toggle(this.buffer.lines[r]);
        this.cursor.col = this._firstNonBlank(this.cursor.row);
        this._redoStack = [];
        break;
      }
      case '=': {
        this._cindent(sr, er);
        this.cursor.col = 0;
        const lineCount = er - sr + 1;
        if (lineCount > 2) {
          this.commandLine = lineCount + ' lines indented';
          this._stickyCommandLine = true;
        }
        this._redoStack = [];
        break;
      }
      case 'g?': {
        for (let r = sr; r <= er; r++) this.buffer.lines[r] = this._rot13(this.buffer.lines[r]);
        this.cursor.col = this._firstNonBlank(this.cursor.row);
        this._redoStack = [];
        break;
      }
      case 'gq': {
        // Single line: no-op, just move cursor
        this.cursor.col = this._firstNonBlank(sr);
        this._redoStack = [];
        break;
      }
      case 'gw': {
        // Single line: no-op
        this._redoStack = [];
        break;
      }
    }
    if (op !== '>' && op !== '<') this._updateDesiredCol();
    this._pendingOp = '';
  }

  // ── Word motions ──

  _isWordChar(ch) { return /[a-zA-Z0-9_]/.test(ch); }

  _moveWordForward(bigWord) {
    let { row, col } = this.cursor;
    const lines = this.buffer.lines;
    if (row >= lines.length) return;
    const line = lines[row];

    if (col >= line.length) {
      // Already past end of current line, move to next line col 0
      if (row < lines.length - 1) {
        row++;
        col = 0;
        // If this line is empty, stop here (empty lines are word boundaries)
        if (lines[row].length === 0) {
          this.cursor.row = row; this.cursor.col = 0; return;
        }
        // Skip leading whitespace on new line
        while (col < lines[row].length && (lines[row][col] === ' ' || lines[row][col] === '\t')) col++;
        // If entire line is whitespace, move to next line
        if (col >= lines[row].length && row < lines.length - 1) {
          row++; col = 0;
          if (lines[row].length === 0) {
            this.cursor.row = row; this.cursor.col = 0; return;
          }
          while (col < lines[row].length && (lines[row][col] === ' ' || lines[row][col] === '\t')) col++;
        }
      }
      this.cursor.row = row; this.cursor.col = col; return;
    }

    if (bigWord) {
      while (col < line.length && line[col] !== ' ' && line[col] !== '\t') col++;
      while (col < line.length && (line[col] === ' ' || line[col] === '\t')) col++;
    } else {
      const ch = line[col];
      if (this._isWordChar(ch)) {
        while (col < line.length && this._isWordChar(line[col])) col++;
      } else if (ch !== ' ' && ch !== '\t') {
        while (col < line.length && !this._isWordChar(line[col]) && line[col] !== ' ' && line[col] !== '\t') col++;
      }
      while (col < line.length && (line[col] === ' ' || line[col] === '\t')) col++;
    }

    if (col >= line.length && row < lines.length - 1) {
      row++; col = 0;
      // Empty lines are word boundaries — stop here
      if (lines[row].length === 0) {
        this.cursor.row = row; this.cursor.col = 0; return;
      }
      // Skip leading whitespace
      while (col < lines[row].length && (lines[row][col] === ' ' || lines[row][col] === '\t')) col++;
      // If entire line was whitespace, try next line
      if (col >= lines[row].length && row < lines.length - 1) {
        row++; col = 0;
        if (lines[row].length === 0) {
          this.cursor.row = row; this.cursor.col = 0; return;
        }
        while (col < lines[row].length && (lines[row][col] === ' ' || lines[row][col] === '\t')) col++;
      }
    }
    this.cursor.row = row; this.cursor.col = col;
  }

  _moveWordBackward(bigWord) {
    let { row, col } = this.cursor;
    const lines = this.buffer.lines;

    if (col === 0) {
      if (row > 0) {
        row--;
        // Empty lines are word boundaries — stop here
        if (lines[row].length === 0) {
          this.cursor.row = row; this.cursor.col = 0; return;
        }
        col = Math.max(0, lines[row].length - 1);
        // Skip trailing whitespace
        while (col > 0 && (lines[row][col] === ' ' || lines[row][col] === '\t')) col--;
        // If entire line was whitespace, go to previous line
        if (col === 0 && lines[row].length > 0 && (lines[row][0] === ' ' || lines[row][0] === '\t')) {
          if (row > 0) { row--; col = Math.max(0, lines[row].length - 1); }
          while (col > 0 && (lines[row][col] === ' ' || lines[row][col] === '\t')) col--;
        }
      } else return;
    } else col--;

    const line = lines[row];
    if (bigWord) {
      while (col > 0 && (line[col] === ' ' || line[col] === '\t')) col--;
      while (col > 0 && line[col - 1] !== ' ' && line[col - 1] !== '\t') col--;
    } else {
      while (col > 0 && (line[col] === ' ' || line[col] === '\t')) col--;
      if (col >= 0 && col < line.length) {
        if (this._isWordChar(line[col])) {
          while (col > 0 && this._isWordChar(line[col - 1])) col--;
        } else if (line[col] !== ' ' && line[col] !== '\t') {
          while (col > 0 && !this._isWordChar(line[col - 1]) && line[col - 1] !== ' ' && line[col - 1] !== '\t') col--;
        }
      }
    }
    this.cursor.row = row; this.cursor.col = Math.max(0, col);
  }

  _moveWordEnd(bigWord) {
    let { row, col } = this.cursor;
    const lines = this.buffer.lines;
    col++;
    if (col >= lines[row].length) {
      if (row < lines.length - 1) {
        row++; col = 0;
        // Skip empty lines
        while (row < lines.length - 1 && lines[row].length === 0) row++;
      }
      else { col = Math.max(0, lines[row].length - 1); this.cursor.row = row; this.cursor.col = col; return; }
    }
    // Skip whitespace (including whitespace-only lines)
    while (row < lines.length) {
      while (col < lines[row].length && (lines[row][col] === ' ' || lines[row][col] === '\t')) col++;
      if (col < lines[row].length) break; // found non-blank
      // This line was all whitespace or we ran past end, try next
      if (row < lines.length - 1) {
        row++; col = 0;
        // Skip empty lines
        while (row < lines.length - 1 && lines[row].length === 0) row++;
      } else break;
    }

    const line = lines[row];
    if (bigWord) {
      while (col + 1 < line.length && line[col + 1] !== ' ' && line[col + 1] !== '\t') col++;
    } else {
      if (col < line.length && this._isWordChar(line[col])) {
        while (col + 1 < line.length && this._isWordChar(line[col + 1])) col++;
      } else if (col < line.length) {
        while (col + 1 < line.length && !this._isWordChar(line[col + 1]) && line[col + 1] !== ' ' && line[col + 1] !== '\t') col++;
      }
    }
    this.cursor.row = row; this.cursor.col = Math.min(col, Math.max(0, lines[row].length - 1));
  }

  _moveWordEndBackward(bigWord) {
    let { row, col } = this.cursor;
    const lines = this.buffer.lines;

    // Helper: classify character
    const cls = (r, c) => {
      if (r < 0 || r >= lines.length) return -1;
      const ln = lines[r];
      if (ln.length === 0) return 0; // empty line
      if (c < 0 || c >= ln.length) return -1;
      const ch = ln[c];
      if (ch === ' ' || ch === '\t') return 1; // whitespace
      if (bigWord) return 2; // gE: all non-whitespace is same class
      return this._isWordChar(ch) ? 2 : 3; // ge: word vs punct
    };

    // Step back one position
    let crossedLine = false;
    col--;
    if (col < 0) {
      row--;
      if (row < 0) { this.cursor.col = 0; return; }
      crossedLine = true;
      if (lines[row].length === 0) { this.cursor.row = row; this.cursor.col = 0; return; }
      col = lines[row].length - 1;
    }

    // Phase 1: skip whitespace and empty lines backward
    for (;;) {
      if (row < 0) { this.cursor.row = 0; this.cursor.col = 0; return; }
      if (lines[row].length === 0) {
        // Empty line is a word-end position — stop here
        this.cursor.row = row; this.cursor.col = 0; return;
      }
      const c = cls(row, col);
      if (c === 1) { // whitespace
        crossedLine = false; // crossing whitespace is like crossing a boundary
        col--;
        if (col < 0) { row--; if (row < 0) { this.cursor.row = 0; this.cursor.col = 0; return; } col = Math.max(0, lines[row].length - 1); crossedLine = true; }
        continue;
      }
      break;
    }

    // Phase 2: we're on a non-blank char.
    // If we crossed a line boundary or whitespace to get here, we're already
    // at the end of a word — just stop.
    if (crossedLine) {
      this.cursor.row = row; this.cursor.col = col; return;
    }

    // Check if our original position (before stepping back) was in the same word.
    const curClass = cls(row, col);
    let nextR = row, nextC = col + 1;
    if (nextC >= lines[nextR].length) { nextR++; nextC = 0; }
    const nextClass = cls(nextR, nextC);
    
    if (nextClass === curClass) {
      // We didn't cross a word boundary. Skip back through this entire word.
      while (col > 0 && cls(row, col - 1) === curClass) col--;
      if (col === 0 && cls(row, 0) === curClass) {
        // Word extends to start of line. Go to previous line.
        row--;
        if (row < 0) { this.cursor.row = 0; this.cursor.col = 0; return; }
        if (lines[row].length === 0) { this.cursor.row = row; this.cursor.col = 0; return; }
        col = lines[row].length - 1;
      } else {
        col--; // move to char before the word start
      }
      // Now skip whitespace again
      for (;;) {
        if (row < 0) { this.cursor.row = 0; this.cursor.col = 0; return; }
        if (lines[row].length === 0) { this.cursor.row = row; this.cursor.col = 0; return; }
        const c2 = cls(row, col);
        if (c2 === 1) {
          col--;
          if (col < 0) { row--; if (row < 0) { this.cursor.row = 0; this.cursor.col = 0; return; } col = Math.max(0, lines[row].length - 1); }
          continue;
        }
        break;
      }
    }

    // Now we're on the last char of the target word
    this.cursor.row = row;
    this.cursor.col = Math.max(0, col);
  }

  // ── Find on line ──

  _doFind(type, char) {
    const line = this.buffer.lines[this.cursor.row];
    let col = this.cursor.col;
    switch (type) {
      case 'f': { const i = line.indexOf(char, col + 1); if (i !== -1) this.cursor.col = i; break; }
      case 'F': { const i = line.lastIndexOf(char, col - 1); if (i !== -1) this.cursor.col = i; break; }
      case 't': { const i = line.indexOf(char, col + 1); if (i > col + 1 || i === col + 1) this.cursor.col = i - 1; break; }
      case 'T': { const i = line.lastIndexOf(char, col - 1); if (i !== -1 && i < col - 1 || i === col - 1) this.cursor.col = i + 1; break; }
    }
  }

  /** Find with count, handling t/T properly for ; and , repeats */
  _doFindRepeat(type, char, count) {
    const savedCol = this.cursor.col;
    let failed = false;
    if (type === 't' || type === 'T') {
      // For t/T repeat: bump cursor 1 step in search direction to skip past the char
      // we're sitting next to, then do f/F, then adjust back for t/T offset
      const fType = type === 't' ? 'f' : 'F';
      const bump = type === 't' ? 1 : -1;
      this.cursor.col += bump;
      for (let i = 0; i < count - 1; i++) {
        const before = this.cursor.col;
        this._doFind(fType, char);
        if (this.cursor.col === before) { failed = true; break; }
      }
      if (!failed) {
        const before = this.cursor.col;
        this._doFind(fType, char);
        if (this.cursor.col === before) { failed = true; }
        else {
          // Adjust for t/T offset
          this.cursor.col -= bump;
        }
      }
    } else {
      for (let i = 0; i < count; i++) {
        const before = this.cursor.col;
        this._doFind(type, char);
        if (this.cursor.col === before) { failed = true; break; }
      }
    }
    if (failed) {
      this.cursor.col = savedCol;
    }
  }

  // ── Match bracket ──

  _doMatchBracket() {
    const matches = { '(': ')', ')': '(', '{': '}', '}': '{', '[': ']', ']': '[' };
    const opens = new Set(['(', '{', '[']);
    const line = this.buffer.lines[this.cursor.row];
    let sc = this.cursor.col;
    while (sc < line.length && !matches[line[sc]]) sc++;
    if (sc >= line.length) return;
    const br = line[sc], target = matches[br], isOpen = opens.has(br), dir = isOpen ? 1 : -1;
    let depth = 1, r = this.cursor.row, c = sc + dir;
    while (depth > 0) {
      if (c < 0 || c >= this.buffer.lines[r].length) {
        r += dir;
        if (r < 0 || r >= this.buffer.lineCount) return;
        c = dir > 0 ? 0 : this.buffer.lines[r].length - 1;
        continue;
      }
      const ch = this.buffer.lines[r][c];
      if (ch === br) depth++;
      else if (ch === target) depth--;
      if (depth === 0) { this.cursor.row = r; this.cursor.col = c; return; }
      c += dir;
    }
  }

  // ── Paragraph motions ──

  // Returns true if cursor moved, false if motion failed
  _moveParagraphForward() {
    const startRow = this.cursor.row;
    const startCol = this.cursor.col;
    let row = this.cursor.row;
    const lc = this.buffer.lineCount;

    // Phase 1: If on a blank (empty) line, skip consecutive blank lines
    if (this.buffer.lines[row] === '') {
      while (row < lc && this.buffer.lines[row] === '') row++;
    }
    // Phase 2: Skip non-blank lines
    while (row < lc && this.buffer.lines[row] !== '') row++;
    // Phase 3: Now at a blank line or past EOF
    if (row < lc) {
      // Found a blank line
      this.cursor.row = row;
      this.cursor.col = 0;
    } else {
      // Past EOF: go to last character of last line
      const lastRow = lc - 1;
      const lastLine = this.buffer.lines[lastRow];
      this.cursor.row = lastRow;
      this.cursor.col = lastLine.length > 0 ? lastLine.length - 1 : 0;
    }
    return (this.cursor.row !== startRow || this.cursor.col !== startCol);
  }

  // Returns true if cursor moved, false if motion failed
  _moveParagraphBackward() {
    const startRow = this.cursor.row;
    const startCol = this.cursor.col;
    let row = this.cursor.row;

    // Phase 1: If on a blank (empty) line, skip consecutive blank lines backward
    if (this.buffer.lines[row] === '') {
      while (row > 0 && this.buffer.lines[row] === '') row--;
    }
    // Phase 2: Skip non-blank lines backward
    while (row > 0 && this.buffer.lines[row] !== '') row--;
    // Phase 3: Now at a blank line or row 0
    if (this.buffer.lines[row] === '') {
      // Found a blank line
      this.cursor.row = row;
      this.cursor.col = 0;
    } else {
      // At row 0 which is non-blank: go to row 0, col 0
      this.cursor.row = 0;
      this.cursor.col = 0;
    }
    return (this.cursor.row !== startRow || this.cursor.col !== startCol);
  }

  // ── Search ──

  /**
   * Compute regex flags for the current search pattern based on ignorecase/smartcase.
   * Returns '' or 'i'.
   */
  _searchCaseFlag() {
    if (!this._settings.ignorecase) return '';
    if (this._settings.smartcase && this._searchPattern && /[A-Z]/.test(this._searchPattern)) return '';
    return 'i';
  }

  /** Translate Vim "magic" regex syntax to JavaScript regex syntax */
  _vimPatternToJs(pat) {
    return pat
      .replace(/\\</g, '\\b')
      .replace(/\\>/g, '\\b')
      .replace(/\\\+/g, '+')
      .replace(/\\\?/g, '?')
      .replace(/\\\(/g, '(')
      .replace(/\\\)/g, ')')
      .replace(/\\\|/g, '|')
      .replace(/\\\{/g, '{')
      .replace(/\\\}/g, '}');
  }

  _searchNext(forward) {
    if (!this._searchPattern) return false;
    const caseFlag = this._searchCaseFlag();
    let pattern;
    try { pattern = new RegExp(this._vimPatternToJs(this._searchPattern), caseFlag); } catch { return false; }
    const sr = this.cursor.row, sc = this.cursor.col;
    const lc = this.buffer.lineCount;
    if (forward) {
      // +1 to allow wrapping back to current line
      for (let i = 0; i <= lc; i++) {
        const r = (sr + i) % lc;
        const start = (r === sr && i === 0) ? sc + 1 : 0;
        const sub = this.buffer.lines[r].slice(start);
        const m = sub.match(pattern);
        if (m) {
          this.cursor.row = r; this.cursor.col = start + m.index;
          this._curSearchPos = { row: r, col: start + m.index };
          return true;
        }
      }
    } else {
      // +1 to allow wrapping back to current line
      for (let i = 0; i <= lc; i++) {
        const r = (sr - i + lc) % lc;
        const end = (r === sr && i === 0) ? sc : this.buffer.lines[r].length;
        const sub = this.buffer.lines[r].slice(0, end);
        let last = null, m;
        const re = new RegExp(this._vimPatternToJs(this._searchPattern), 'g' + caseFlag);
        while ((m = re.exec(sub)) !== null) last = m;
        if (last) {
          this.cursor.row = r; this.cursor.col = last.index;
          this._curSearchPos = { row: r, col: last.index };
          return true;
        }
      }
    }
    return false;
  }

  /**
   * Find the next (or previous) search match, returning { row, col, len } or null.
   * For gn: if cursor is inside a match on the current line, return that match.
   * Otherwise search forward (or backward for gN) wrapping around.
   */
  _findSearchMatch(forward) {
    if (!this._searchPattern) return null;
    const caseFlag = this._searchCaseFlag();
    let re;
    try { re = new RegExp(this._vimPatternToJs(this._searchPattern), 'g' + caseFlag); } catch { return null; }
    const lc = this.buffer.lineCount;
    const cr = this.cursor.row, cc = this.cursor.col;

    // First check if cursor is inside (or at the start of) a match on the current line
    const curLine = this.buffer.lines[cr];
    let m;
    re.lastIndex = 0;
    while ((m = re.exec(curLine)) !== null) {
      const ms = m.index, me = m.index + m[0].length - 1;
      if (forward) {
        // gn: match that starts at or after cursor, or contains cursor
        if (ms >= cc || (ms <= cc && me >= cc)) {
          return { row: cr, col: ms, len: m[0].length };
        }
      } else {
        // gN: match that ends at or before cursor, or contains cursor
        if (me <= cc || (ms <= cc && me >= cc)) {
          // Keep searching for the last qualifying match on this line
          let best = { row: cr, col: ms, len: m[0].length };
          while ((m = re.exec(curLine)) !== null) {
            const ms2 = m.index, me2 = m.index + m[0].length - 1;
            if (me2 <= cc || (ms2 <= cc && me2 >= cc)) {
              best = { row: cr, col: ms2, len: m[0].length };
            } else break;
          }
          return best;
        }
      }
    }

    // No match on current line covering cursor; search forward/backward wrapping
    if (forward) {
      for (let i = 1; i <= lc; i++) {
        const r = (cr + i) % lc;
        const line = this.buffer.lines[r];
        re.lastIndex = 0;
        const fm = re.exec(line);
        if (fm) return { row: r, col: fm.index, len: fm[0].length };
      }
    } else {
      for (let i = 1; i <= lc; i++) {
        const r = (cr - i + lc) % lc;
        const line = this.buffer.lines[r];
        re.lastIndex = 0;
        let last = null;
        while ((m = re.exec(line)) !== null) last = m;
        if (last) return { row: r, col: last.index, len: last[0].length };
      }
    }
    return null;
  }

  _wordUnderCursor() {
    const line = this.buffer.lines[this.cursor.row];
    let s = this.cursor.col, e = this.cursor.col;
    while (s > 0 && this._isWordChar(line[s - 1])) s--;
    while (e < line.length && this._isWordChar(line[e])) e++;
    return s === e ? null : line.slice(s, e);
  }

  // ── Text objects ──

  _getTextObject(type, key) {
    const inner = (type === 'i');
    switch (key) {
      case 'w': return this._textObjWord(inner, false);
      case 'W': return this._textObjWord(inner, true);
      case '"': return this._textObjQuote('"', inner);
      case '\'': return this._textObjQuote('\'', inner);
      case '`': return this._textObjQuote('`', inner);
      case '(': case ')': case 'b': return this._textObjPair('(', ')', inner);
      case '{': case '}': case 'B': return this._textObjPair('{', '}', inner);
      case '[': case ']': return this._textObjPair('[', ']', inner);
      case '<': case '>': return this._textObjPair('<', '>', inner);
      case 'p': return this._textObjParagraph(inner);
      case 's': return this._textObjSentence(inner);
      case 't': return this._textObjTag(inner);
      default: return null;
    }
  }

  _textObjWord(inner, bigWord) {
    const line = this.buffer.lines[this.cursor.row];
    let s = this.cursor.col, e = this.cursor.col;
    const isSpace = (ch) => ch === ' ' || ch === '\t';
    const cursorOnSpace = isSpace(line[s]);
    if (bigWord) {
      if (cursorOnSpace) {
        while (s > 0 && isSpace(line[s - 1])) s--;
        while (e < line.length - 1 && isSpace(line[e + 1])) e++;
      } else {
        while (s > 0 && !isSpace(line[s - 1])) s--;
        while (e < line.length - 1 && !isSpace(line[e + 1])) e++;
      }
    } else {
      if (this._isWordChar(line[s])) {
        while (s > 0 && this._isWordChar(line[s - 1])) s--;
        while (e < line.length - 1 && this._isWordChar(line[e + 1])) e++;
      } else if (!isSpace(line[s])) {
        while (s > 0 && !this._isWordChar(line[s - 1]) && !isSpace(line[s - 1])) s--;
        while (e < line.length - 1 && !this._isWordChar(line[e + 1]) && !isSpace(line[e + 1])) e++;
      } else {
        while (s > 0 && isSpace(line[s - 1])) s--;
        while (e < line.length - 1 && isSpace(line[e + 1])) e++;
      }
    }
    if (!inner) {
      if (cursorOnSpace) {
        // aw on whitespace: include the following word (or preceding if at end)
        if (e + 1 < line.length) {
          // Include the next word
          if (bigWord) {
            while (e + 1 < line.length && !isSpace(line[e + 1])) e++;
          } else if (this._isWordChar(line[e + 1])) {
            while (e + 1 < line.length && this._isWordChar(line[e + 1])) e++;
          } else {
            while (e + 1 < line.length && !this._isWordChar(line[e + 1]) && !isSpace(line[e + 1])) e++;
          }
        } else if (s > 0) {
          // At end of line, include preceding word
          if (bigWord) {
            while (s > 0 && !isSpace(line[s - 1])) s--;
          } else if (this._isWordChar(line[s - 1])) {
            while (s > 0 && this._isWordChar(line[s - 1])) s--;
          } else {
            while (s > 0 && !this._isWordChar(line[s - 1]) && !isSpace(line[s - 1])) s--;
          }
        }
      } else {
        // aw on word: include trailing whitespace, or leading if no trailing
        if (e + 1 < line.length && isSpace(line[e + 1])) {
          while (e + 1 < line.length && isSpace(line[e + 1])) e++;
        } else {
          while (s > 0 && isSpace(line[s - 1])) s--;
        }
      }
    }
    return { startRow: this.cursor.row, startCol: s, endRow: this.cursor.row, endCol: e + 1 };
  }

  _textObjQuote(q, inner) {
    const line = this.buffer.lines[this.cursor.row];
    const pos = [];
    for (let i = 0; i < line.length; i++) {
      if (line[i] === q && (i === 0 || line[i - 1] !== '\\')) pos.push(i);
    }
    let f = -1, s = -1;
    for (let i = 0; i < pos.length - 1; i += 2) {
      if (pos[i] <= this.cursor.col && pos[i + 1] >= this.cursor.col) { f = pos[i]; s = pos[i + 1]; break; }
    }
    if (f === -1) {
      for (let i = 0; i < pos.length - 1; i += 2) {
        if (pos[i] > this.cursor.col) { f = pos[i]; s = pos[i + 1]; break; }
      }
    }
    if (f === -1 || s === -1) return null;
    if (inner) {
      return { startRow: this.cursor.row, startCol: f + 1, endRow: this.cursor.row, endCol: s };
    }
    // "a" text object: include trailing whitespace, or leading if no trailing
    let startC = f, endC = s + 1;
    if (endC < line.length && (line[endC] === ' ' || line[endC] === '\t')) {
      while (endC < line.length && (line[endC] === ' ' || line[endC] === '\t')) endC++;
    } else {
      while (startC > 0 && (line[startC - 1] === ' ' || line[startC - 1] === '\t')) startC--;
    }
    return { startRow: this.cursor.row, startCol: startC, endRow: this.cursor.row, endCol: endC };
  }

  _textObjPair(open, close, inner) {
    let depth = 0, sr = this.cursor.row, sc = this.cursor.col, found = false;
    // Search backward for unmatched opening delimiter
    outer1:
    for (let r = this.cursor.row; r >= 0; r--) {
      const line = this.buffer.lines[r];
      const start = (r === this.cursor.row) ? this.cursor.col : line.length - 1;
      for (let c = start; c >= 0; c--) {
        if (line[c] === close && !(r === this.cursor.row && c === this.cursor.col)) depth++;
        if (line[c] === open) {
          if (depth === 0) { sr = r; sc = c; found = true; break outer1; }
          depth--;
        }
      }
    }
    // If not found inside a pair, search forward on the current line
    // for the opening delimiter (Vim behavior: di( when cursor is before parens)
    if (!found) {
      const line = this.buffer.lines[this.cursor.row];
      for (let c = this.cursor.col + 1; c < line.length; c++) {
        if (line[c] === open) { sr = this.cursor.row; sc = c; found = true; break; }
      }
    }
    if (!found) return null;
    depth = 0; let er = this.cursor.row, ec = this.cursor.col; found = false;
    outer2:
    for (let r = sr; r < this.buffer.lineCount; r++) {
      const line = this.buffer.lines[r];
      const start = (r === sr) ? sc : 0;
      for (let c = start; c < line.length; c++) {
        if (line[c] === open && !(r === sr && c === sc)) depth++;
        if (line[c] === close) {
          if (depth === 0) { er = r; ec = c; found = true; break outer2; }
          depth--;
        }
      }
    }
    if (!found) return null;
    if (inner) {
      let isc = sc + 1, isr = sr;
      if (isc >= this.buffer.lines[isr].length && isr < er) { isr++; isc = 0; }
      const range = { startRow: isr, startCol: isc, endRow: er, endCol: ec };
      if (isr !== er) range.multilineInner = true;
      return range;
    }
    return { startRow: sr, startCol: sc, endRow: er, endCol: ec + 1 };
  }

  _textObjParagraph(inner) {
    const lc = this.buffer.lineCount;
    const row = this.cursor.row;
    let sr, er;

    if (this.buffer.lines[row] === '') {
      // On a blank line: select contiguous blank lines
      sr = row;
      while (sr > 0 && this.buffer.lines[sr - 1] === '') sr--;
      er = row;
      while (er < lc - 1 && this.buffer.lines[er + 1] === '') er++;

      if (!inner) {
        // ap on blank: include following non-blank paragraph
        let ner = er;
        while (ner < lc - 1 && this.buffer.lines[ner + 1] !== '') ner++;
        if (ner > er) {
          er = ner;
        } else if (sr > 0) {
          // No following content: include preceding non-blank paragraph
          while (sr > 0 && this.buffer.lines[sr - 1] !== '') sr--;
        }
      }
    } else {
      // On a non-blank line: select contiguous non-blank lines
      sr = row;
      while (sr > 0 && this.buffer.lines[sr - 1] !== '') sr--;
      er = row;
      while (er < lc - 1 && this.buffer.lines[er + 1] !== '') er++;

      if (!inner) {
        // ap: include trailing blank lines
        let ner = er;
        while (ner < lc - 1 && this.buffer.lines[ner + 1] === '') ner++;
        if (ner > er) {
          er = ner;
        } else if (sr > 0) {
          // No trailing blanks: include leading blank lines
          while (sr > 0 && this.buffer.lines[sr - 1] === '') sr--;
        }
      }
    }

    return { startRow: sr, startCol: 0, endRow: er, endCol: this.buffer.lines[er].length, linewise: true };
  }

  _textObjSentence(inner) {
    const row = this.cursor.row;
    const line = this.buffer.lines[row];
    const col = this.cursor.col;

    if (line.length === 0) return null;

    // Find sentence-end positions on this line.
    // A sentence ends at .!? optionally followed by )]}'" then space/tab/EOL.
    const sentenceEnds = [];
    for (let i = 0; i < line.length; i++) {
      if (line[i] === '.' || line[i] === '!' || line[i] === '?') {
        let j = i + 1;
        while (j < line.length && ')]\'"'.includes(line[j])) j++;
        if (j >= line.length || line[j] === ' ' || line[j] === '\t') {
          sentenceEnds.push(i);
        }
      }
    }

    // If no sentence ends found, the whole line is one sentence
    if (sentenceEnds.length === 0) {
      return { startRow: row, startCol: 0, endRow: row, endCol: line.length };
    }

    // Build sentence ranges: [{start, end}] where start = first char, end = ending punctuation
    const sentences = [];
    for (let i = 0; i < sentenceEnds.length; i++) {
      let start;
      if (i === 0) {
        start = 0;
      } else {
        start = sentenceEnds[i - 1] + 1;
        while (start < line.length && (line[start] === ' ' || line[start] === '\t')) start++;
      }
      sentences.push({ start, end: sentenceEnds[i] });
    }

    // Find which sentence contains the cursor
    let sentIdx = 0;
    for (let i = 0; i < sentences.length; i++) {
      if (col <= sentences[i].end) {
        sentIdx = i;
        break;
      }
      // If cursor is past the last sentence end, use the last sentence
      if (i === sentences.length - 1) {
        sentIdx = i;
      }
    }

    const sent = sentences[sentIdx];
    const isFirst = (sentIdx === 0);

    // Leading whitespace start (after previous sentence end)
    let wsBeforeStart = sent.start;
    if (!isFirst) {
      wsBeforeStart = sentenceEnds[sentIdx - 1] + 1;
    }

    let startCol, endCol;

    if (inner) {
      // is: just the sentence text, no surrounding whitespace
      startCol = sent.start;
      endCol = sent.end + 1;
    } else {
      // as: include trailing whitespace. If no trailing, include leading.
      startCol = sent.start;
      endCol = sent.end + 1;

      if (sent.end + 1 < line.length && (line[sent.end + 1] === ' ' || line[sent.end + 1] === '\t')) {
        // Has trailing whitespace — include it
        let t = sent.end + 1;
        while (t < line.length && (line[t] === ' ' || line[t] === '\t')) t++;
        endCol = t;
      } else if (!isFirst) {
        // No trailing whitespace: include leading whitespace
        startCol = wsBeforeStart;
      }
    }

    return { startRow: row, startCol, endRow: row, endCol };
  }

  // ── Bracket commands ──

  _handleBracketCommand(bracket, key) {
    const combo = bracket + key;
    switch (combo) {
      case '[(':
        this._gotoPrevUnmatched('(', ')');
        break;
      case '])':
        this._gotoNextUnmatched('(', ')');
        break;
      case '[{':
        this._gotoPrevUnmatched('{', '}');
        break;
      case ']}':
        this._gotoNextUnmatched('{', '}');
        break;
      case '[[':
        this._gotoCol0Char('{', false);
        break;
      case ']]':
        this._gotoCol0Char('{', true);
        break;
      case '[]':
        this._gotoCol0Char('}', false);
        break;
      case '][':
        this._gotoCol0Char('}', true);
        break;
      case '[p': {
        // Put before with indent adjustment
        const reg = this._getReg();
        if (!reg.text) break;
        this._saveSnapshot();
        if (reg.type === 'line') {
          const curIndent = this.buffer.lines[this.cursor.row].match(/^[ \t]*/)[0];
          const pasteLines = reg.text.split('\n');
          const firstIndent = pasteLines[0].match(/^[ \t]*/)[0];
          const delta = curIndent.length - firstIndent.length;
          const adjusted = pasteLines.map(line => {
            if (delta > 0) return ' '.repeat(delta) + line;
            if (delta < 0) {
              const li = line.match(/^[ \t]*/)[0];
              return line.slice(Math.min(-delta, li.length));
            }
            return line;
          });
          this.buffer.lines.splice(this.cursor.row, 0, ...adjusted);
          this.cursor.col = this._firstNonBlank(this.cursor.row);
        } else {
          this._putBefore(reg);
        }
        this._redoStack = [];
        this._updateDesiredCol();
        break;
      }
      case ']p': {
        // Put after with indent adjustment
        const reg = this._getReg();
        if (!reg.text) break;
        this._saveSnapshot();
        if (reg.type === 'line') {
          const curIndent = this.buffer.lines[this.cursor.row].match(/^[ \t]*/)[0];
          const pasteLines = reg.text.split('\n');
          const firstIndent = pasteLines[0].match(/^[ \t]*/)[0];
          const delta = curIndent.length - firstIndent.length;
          const adjusted = pasteLines.map(line => {
            if (delta > 0) return ' '.repeat(delta) + line;
            if (delta < 0) {
              const li = line.match(/^[ \t]*/)[0];
              return line.slice(Math.min(-delta, li.length));
            }
            return line;
          });
          this.buffer.lines.splice(this.cursor.row + 1, 0, ...adjusted);
          this.cursor.row++;
          this.cursor.col = this._firstNonBlank(this.cursor.row);
        } else {
          this._putAfter(reg);
        }
        this._redoStack = [];
        this._updateDesiredCol();
        break;
      }
      case "['": {
        // Go to previous line with a lowercase mark
        const markRows = new Set();
        for (const [k, v] of Object.entries(this._marks)) {
          if (k >= 'a' && k <= 'z') markRows.add(v.row);
        }
        for (let r = this.cursor.row - 1; r >= 0; r--) {
          if (markRows.has(r)) {
            this.cursor.row = r;
            this.cursor.col = this._firstNonBlank(r);
            this._updateDesiredCol();
            break;
          }
        }
        break;
      }
      case "]'": {
        // Go to next line with a lowercase mark
        const markRows = new Set();
        for (const [k, v] of Object.entries(this._marks)) {
          if (k >= 'a' && k <= 'z') markRows.add(v.row);
        }
        for (let r = this.cursor.row + 1; r < this.buffer.lineCount; r++) {
          if (markRows.has(r)) {
            this.cursor.row = r;
            this.cursor.col = this._firstNonBlank(r);
            this._updateDesiredCol();
            break;
          }
        }
        break;
      }
      case '[M':
      case '[m': {
        // Go to previous unmatched '{' (method start)
        for (let r = this.cursor.row; r >= 0; r--) {
          const line = this.buffer.lines[r];
          const startC = (r === this.cursor.row) ? this.cursor.col - 1 : line.length - 1;
          for (let c = startC; c >= 0; c--) {
            if (line[c] === '{') {
              this.cursor.row = r;
              this.cursor.col = c;
              this._updateDesiredCol();
              return;
            }
          }
        }
        break;
      }
      case ']M':
      case ']m': {
        // Go to next unmatched '{' (method start)
        for (let r = this.cursor.row; r < this.buffer.lineCount; r++) {
          const line = this.buffer.lines[r];
          const startC = (r === this.cursor.row) ? this.cursor.col + 1 : 0;
          for (let c = startC; c < line.length; c++) {
            if (line[c] === '{') {
              this.cursor.row = r;
              this.cursor.col = c;
              this._updateDesiredCol();
              return;
            }
          }
        }
        break;
      }
      case ']s': {
        // ]s — next misspelled word
        if (this._settings.spell) {
          const pos = this._findNextSpellError(this.cursor.row, this.cursor.col, true);
          if (pos) {
            this.cursor.row = pos.row;
            this.cursor.col = pos.col;
            this._updateDesiredCol();
          }
        }
        break;
      }
      case '[s': {
        // [s — previous misspelled word
        if (this._settings.spell) {
          const pos = this._findNextSpellError(this.cursor.row, this.cursor.col, false);
          if (pos) {
            this.cursor.row = pos.row;
            this.cursor.col = pos.col;
            this._updateDesiredCol();
          }
        }
        break;
      }
      default:
        break;
    }
  }

  /**
   * Go to previous unmatched `open` character, searching backward from cursor.
   * Used by [( and [{
   */
  _gotoPrevUnmatched(open, close) {
    let depth = 0;
    for (let r = this.cursor.row; r >= 0; r--) {
      const line = this.buffer.lines[r];
      const startC = (r === this.cursor.row) ? this.cursor.col - 1 : line.length - 1;
      for (let c = startC; c >= 0; c--) {
        if (line[c] === close) {
          depth++;
        } else if (line[c] === open) {
          if (depth === 0) {
            this.cursor.row = r;
            this.cursor.col = c;
            this._updateDesiredCol();
            return;
          }
          depth--;
        }
      }
    }
  }

  /**
   * Go to next unmatched `close` character, searching forward from cursor.
   * Used by ]) and ]}
   */
  _gotoNextUnmatched(open, close) {
    let depth = 0;
    for (let r = this.cursor.row; r < this.buffer.lineCount; r++) {
      const line = this.buffer.lines[r];
      const startC = (r === this.cursor.row) ? this.cursor.col + 1 : 0;
      for (let c = startC; c < line.length; c++) {
        if (line[c] === open) {
          depth++;
        } else if (line[c] === close) {
          if (depth === 0) {
            this.cursor.row = r;
            this.cursor.col = c;
            this._updateDesiredCol();
            return;
          }
          depth--;
        }
      }
    }
  }

  /**
   * Go to next/previous line that has `ch` at column 0.
   * Used by [[ ]] [] ][
   */
  _gotoCol0Char(ch, forward) {
    if (forward) {
      for (let r = this.cursor.row + 1; r < this.buffer.lineCount; r++) {
        if (this.buffer.lines[r].length > 0 && this.buffer.lines[r][0] === ch) {
          this.cursor.row = r;
          this.cursor.col = 0;
          this._updateDesiredCol();
          return;
        }
      }
    } else {
      for (let r = this.cursor.row - 1; r >= 0; r--) {
        if (this.buffer.lines[r].length > 0 && this.buffer.lines[r][0] === ch) {
          this.cursor.row = r;
          this.cursor.col = 0;
          this._updateDesiredCol();
          return;
        }
      }
    }
  }

  // ── Tag text objects ──

  /**
   * Find enclosing HTML/XML tag pair for it/at text objects.
   * @param {boolean} inner - true for inner tag (between tags), false for outer (including tags)
   * @returns {{ startRow: number, startCol: number, endRow: number, endCol: number } | null}
   */
  _textObjTag(inner) {
    // Flatten buffer into a single string for easier scanning
    const lines = this.buffer.lines;
    const cursorOffset = this._offsetFromPos(this.cursor.row, this.cursor.col);

    // Search backward from cursor for an opening tag that encloses the cursor
    let searchFrom = cursorOffset;

    while (searchFrom >= 0) {
      // Find the previous '<' that starts an opening tag (not </ or <!-- or self-closing)
      const openTagStart = this._findPrevOpeningTagStart(searchFrom);
      if (openTagStart === -1) return null;

      // Parse the tag name and find end of opening tag
      const openTagInfo = this._parseOpeningTag(openTagStart);
      if (!openTagInfo) {
        searchFrom = openTagStart - 1;
        continue;
      }

      // Find the matching closing tag, searching forward from end of opening tag
      const closeTagInfo = this._findMatchingCloseTag(openTagInfo.tagName, openTagInfo.tagEnd);
      if (!closeTagInfo) {
        searchFrom = openTagStart - 1;
        continue;
      }

      // Check if the cursor is between the opening and closing tags
      if (cursorOffset >= openTagStart && cursorOffset <= closeTagInfo.closeEnd) {
        // Found enclosing tag pair
        if (inner) {
          // Inner: between end of opening tag and start of closing tag
          const iStart = openTagInfo.tagEnd + 1;
          const iEnd = closeTagInfo.closeStart; // exclusive end (the '<' of closing tag)
          if (iStart >= iEnd) {
            // Empty tag content
            const startPos = this._posFromOffset(iStart);
            return { startRow: startPos.row, startCol: startPos.col, endRow: startPos.row, endCol: startPos.col };
          }
          const startPos = this._posFromOffset(iStart);
          const endPos = this._posFromOffset(iEnd);
          return { startRow: startPos.row, startCol: startPos.col, endRow: endPos.row, endCol: endPos.col };
        } else {
          // Outer: from start of opening tag to end of closing tag
          const startPos = this._posFromOffset(openTagStart);
          const endPos = this._posFromOffset(closeTagInfo.closeEnd);
          return { startRow: startPos.row, startCol: startPos.col, endRow: endPos.row, endCol: endPos.col + 1 };
        }
      }

      // This tag pair doesn't enclose cursor, keep searching backward
      searchFrom = openTagStart - 1;
    }

    return null;
  }

  /** Convert (row, col) to a flat buffer offset. */
  _offsetFromPos(row, col) {
    let offset = 0;
    for (let r = 0; r < row; r++) {
      offset += this.buffer.lines[r].length + 1; // +1 for newline
    }
    return offset + col;
  }

  /** Convert a flat buffer offset back to {row, col}. */
  _posFromOffset(offset) {
    let remaining = offset;
    for (let r = 0; r < this.buffer.lineCount; r++) {
      const lineLen = this.buffer.lines[r].length + 1; // +1 for newline
      if (remaining < lineLen) {
        return { row: r, col: remaining };
      }
      remaining -= lineLen;
    }
    // Past end of buffer
    const lastRow = this.buffer.lineCount - 1;
    return { row: lastRow, col: this.buffer.lines[lastRow].length };
  }

  /** Get character at flat buffer offset. */
  _charAtOffset(offset) {
    let remaining = offset;
    for (let r = 0; r < this.buffer.lineCount; r++) {
      const line = this.buffer.lines[r];
      if (remaining < line.length) {
        return line[remaining];
      }
      if (remaining === line.length) {
        return '\n'; // newline between lines
      }
      remaining -= line.length + 1;
    }
    return null;
  }

  /** Get total buffer length including newlines. */
  _totalBufferLength() {
    let len = 0;
    for (let r = 0; r < this.buffer.lineCount; r++) {
      len += this.buffer.lines[r].length;
      if (r < this.buffer.lineCount - 1) len++; // newline
    }
    return len;
  }

  /**
   * Search backward from `offset` for a '<' that starts an opening tag.
   * Skips closing tags (</), comments (<!--), and self-closing tags (/>).
   */
  _findPrevOpeningTagStart(offset) {
    const totalLen = this._totalBufferLength();
    for (let i = offset; i >= 0; i--) {
      const ch = this._charAtOffset(i);
      if (ch === '<') {
        // Skip closing tags </
        const next = this._charAtOffset(i + 1);
        if (next === '/') continue;
        // Skip comments <!--
        if (next === '!') continue;
        // Skip processing instructions <?
        if (next === '?') continue;
        // Check it's a valid tag start (letter follows <)
        if (next && /[a-zA-Z]/.test(next)) {
          // Check if it's self-closing: find the > and see if preceded by /
          let j = i + 1;
          while (j < totalLen) {
            const c = this._charAtOffset(j);
            if (c === '>') {
              const prev = this._charAtOffset(j - 1);
              if (prev === '/') break; // self-closing, skip
              return i; // valid opening tag
            }
            if (c === '<') break; // malformed, stop
            j++;
          }
          // If we hit < before >, this is malformed; check for self-closing
          const prevOfClose = this._charAtOffset(j - 1);
          if (j < totalLen && this._charAtOffset(j) === '>' && prevOfClose === '/') continue;
          if (j < totalLen && this._charAtOffset(j) === '>') return i;
        }
      }
    }
    return -1;
  }

  /**
   * Parse an opening tag starting at `offset` (the '<').
   * Returns { tagName, tagEnd } where tagEnd is the offset of the '>'.
   * Returns null if not a valid opening tag.
   */
  _parseOpeningTag(offset) {
    const totalLen = this._totalBufferLength();
    if (this._charAtOffset(offset) !== '<') return null;
    // Extract tag name
    let i = offset + 1;
    let tagName = '';
    while (i < totalLen) {
      const ch = this._charAtOffset(i);
      if (/[a-zA-Z0-9:\-_.]/.test(ch)) {
        tagName += ch;
        i++;
      } else {
        break;
      }
    }
    if (tagName.length === 0) return null;
    // Find the closing >
    while (i < totalLen) {
      const ch = this._charAtOffset(i);
      if (ch === '>') {
        // Check self-closing
        if (this._charAtOffset(i - 1) === '/') return null;
        return { tagName, tagEnd: i };
      }
      if (ch === '<') return null; // malformed
      i++;
    }
    return null;
  }

  /**
   * Find matching closing tag </tagName> starting search from `fromOffset`.
   * Handles nested same-name tags.
   * Returns { closeStart, closeEnd } where closeStart is offset of '<' in </tag>
   * and closeEnd is offset of '>' in </tag>. Returns null if not found.
   */
  _findMatchingCloseTag(tagName, fromOffset) {
    const totalLen = this._totalBufferLength();
    let depth = 0;
    let i = fromOffset + 1;
    while (i < totalLen) {
      const ch = this._charAtOffset(i);
      if (ch === '<') {
        const next = this._charAtOffset(i + 1);
        if (next === '/') {
          // Closing tag — extract name
          let j = i + 2;
          let name = '';
          while (j < totalLen) {
            const c = this._charAtOffset(j);
            if (/[a-zA-Z0-9:\-_.]/.test(c)) { name += c; j++; }
            else break;
          }
          if (name.toLowerCase() === tagName.toLowerCase()) {
            // Find the >
            while (j < totalLen && this._charAtOffset(j) !== '>') j++;
            if (j < totalLen) {
              if (depth === 0) {
                return { closeStart: i, closeEnd: j };
              }
              depth--;
            }
          }
          i = j + 1;
          continue;
        } else if (next && /[a-zA-Z]/.test(next)) {
          // Possible opening tag — extract name
          let j = i + 1;
          let name = '';
          while (j < totalLen) {
            const c = this._charAtOffset(j);
            if (/[a-zA-Z0-9:\-_.]/.test(c)) { name += c; j++; }
            else break;
          }
          // Find the >
          while (j < totalLen && this._charAtOffset(j) !== '>') j++;
          if (j < totalLen) {
            // Check if self-closing
            if (this._charAtOffset(j - 1) !== '/') {
              if (name.toLowerCase() === tagName.toLowerCase()) {
                depth++;
              }
            }
          }
          i = j + 1;
          continue;
        }
      }
      i++;
    }
    return null;
  }

  // ── Surround (nvim-surround plugin) ──

  /**
   * Map a surround char to an open/close pair.
   * Opening marks add space, closing marks don't.
   */
  _getSurroundPair(ch) {
    const pairs = {
      ')': { open: '(', close: ')' }, 'b': { open: '(', close: ')' },
      '(': { open: '( ', close: ' )' },
      ']': { open: '[', close: ']' }, 'r': { open: '[', close: ']' },
      '[': { open: '[ ', close: ' ]' },
      '}': { open: '{', close: '}' }, 'B': { open: '{', close: '}' },
      '{': { open: '{ ', close: ' }' },
      '>': { open: '<', close: '>' }, 'a': { open: '<', close: '>' },
      '<': { open: '< ', close: ' >' },
    };
    if (pairs[ch]) return pairs[ch];
    // Quotes and arbitrary characters: same char on both sides
    return { open: ch, close: ch };
  }

  /**
   * Map a target char (for ds/cs) to the open/close delimiter to search for.
   * Opening marks indicate space-trimming.
   */
  _getSurroundTarget(ch) {
    const trim = ch === '(' || ch === '[' || ch === '{' || ch === '<';
    const map = {
      ')': { open: '(', close: ')', trim: false },
      '(': { open: '(', close: ')', trim: true },
      'b': { open: '(', close: ')', trim: false },
      ']': { open: '[', close: ']', trim: false },
      '[': { open: '[', close: ']', trim: true },
      'r': { open: '[', close: ']', trim: false },
      '}': { open: '{', close: '}', trim: false },
      '{': { open: '{', close: '}', trim: true },
      'B': { open: '{', close: '}', trim: false },
      '>': { open: '<', close: '>', trim: false },
      '<': { open: '<', close: '>', trim: true },
      'a': { open: '<', close: '>', trim: false },
    };
    if (map[ch]) return map[ch];
    // Quotes and arbitrary: same char, no trim
    return { open: ch, close: ch, trim: false };
  }

  /**
   * Find the positions of the surrounding delimiters on the current line (for ds/cs).
   * Returns { openRow, openCol, closeRow, closeCol } or null.
   */
  _findSurrounding(ch) {
    const target = this._getSurroundTarget(ch);
    if (target.open === target.close) {
      // Symmetric (quotes, arbitrary) — use quote-finding logic (single line)
      const line = this.buffer.lines[this.cursor.row];
      const q = target.open;
      const pos = [];
      for (let i = 0; i < line.length; i++) {
        if (line[i] === q && (i === 0 || line[i - 1] !== '\\')) pos.push(i);
      }
      let f = -1, s = -1;
      for (let i = 0; i < pos.length - 1; i += 2) {
        if (pos[i] <= this.cursor.col && pos[i + 1] >= this.cursor.col) {
          f = pos[i]; s = pos[i + 1]; break;
        }
      }
      if (f === -1) {
        for (let i = 0; i < pos.length - 1; i += 2) {
          if (pos[i] > this.cursor.col) { f = pos[i]; s = pos[i + 1]; break; }
        }
      }
      if (f === -1 || s === -1) return null;
      return { openRow: this.cursor.row, openCol: f, closeRow: this.cursor.row, closeCol: s, trim: target.trim };
    }
    // Paired delimiters — use bracket-matching logic (multi-line)
    const open = target.open, close = target.close;
    let depth = 0, sr = -1, sc = -1, found = false;
    outer1:
    for (let r = this.cursor.row; r >= 0; r--) {
      const line = this.buffer.lines[r];
      const start = (r === this.cursor.row) ? this.cursor.col : line.length - 1;
      for (let c = start; c >= 0; c--) {
        if (line[c] === close && !(r === this.cursor.row && c === this.cursor.col)) depth++;
        if (line[c] === open) {
          if (depth === 0) { sr = r; sc = c; found = true; break outer1; }
          depth--;
        }
      }
    }
    if (!found) {
      // Vim/nvim behavior: search forward on current line for next bracket pair
      const fLine = this.buffer.lines[this.cursor.row];
      for (let c = this.cursor.col + 1; c < fLine.length; c++) {
        if (fLine[c] === open) {
          sr = this.cursor.row; sc = c; found = true; break;
        }
      }
      if (!found) return null;
    }
    depth = 0; let er = -1, ec = -1; found = false;
    outer2:
    for (let r = sr; r < this.buffer.lineCount; r++) {
      const line = this.buffer.lines[r];
      const start = (r === sr) ? sc + 1 : 0;
      for (let c = start; c < line.length; c++) {
        if (line[c] === open) depth++;
        if (line[c] === close) {
          if (depth === 0) { er = r; ec = c; found = true; break outer2; }
          depth--;
        }
      }
    }
    if (!found) return null;
    return { openRow: sr, openCol: sc, closeRow: er, closeCol: ec, trim: target.trim };
  }

  /**
   * Add surrounding chars around a range. Used by ys and visual S.
   * nvim-surround trims trailing whitespace from the range before wrapping.
   */
  _doSurroundAdd(sr, sc, er, ec, ch, trim = true, customOpen = null, customClose = null) {
    const open = customOpen != null ? customOpen : this._getSurroundPair(ch).open;
    const close = customClose != null ? customClose : this._getSurroundPair(ch).close;
    // Trim trailing/leading whitespace from range (nvim-surround behavior)
    // Only for motions like w/W/aw/aW that include extraneous whitespace.
    if (trim) {
      if (sr === er) {
        const line = this.buffer.lines[sr];
        while (ec > sc && (line[ec - 1] === ' ' || line[ec - 1] === '\t')) ec--;
        while (sc < ec && (line[sc] === ' ' || line[sc] === '\t')) sc++;
      } else {
        const line = this.buffer.lines[er];
        while (ec > 0 && (line[ec - 1] === ' ' || line[ec - 1] === '\t')) ec--;
      }
    }
    // Insert close first (so positions don't shift for the open insert)
    if (sr === er) {
      const line = this.buffer.lines[sr];
      this.buffer.lines[sr] = line.slice(0, ec) + close + line.slice(ec);
      this.buffer.lines[sr] = this.buffer.lines[sr].slice(0, sc) + open + this.buffer.lines[sr].slice(sc);
    } else {
      // Multi-line: insert close at end position
      const eLine = this.buffer.lines[er];
      this.buffer.lines[er] = eLine.slice(0, ec) + close + eLine.slice(ec);
      // Insert open at start position
      const sLine = this.buffer.lines[sr];
      this.buffer.lines[sr] = sLine.slice(0, sc) + open + sLine.slice(sc);
    }
    this.cursor.row = sr; this.cursor.col = sc;
    this._updateDesiredCol();
  }

  /**
   * Delete surrounding delimiters. Used by ds.
   * Returns true if successful.
   */
  _doSurroundDelete(ch) {
    const pos = this._findSurrounding(ch);
    if (!pos) return false;
    const { openRow, openCol, closeRow, closeCol, trim } = pos;
    if (openRow === closeRow) {
      const line = this.buffer.lines[openRow];
      let inner = line.slice(openCol + 1, closeCol);
      if (trim) inner = inner.trim();
      this.buffer.lines[openRow] = line.slice(0, openCol) + inner + line.slice(closeCol + 1);
    } else {
      // Multi-line: remove close delimiter, then open delimiter
      const cLine = this.buffer.lines[closeRow];
      this.buffer.lines[closeRow] = cLine.slice(0, closeCol) + cLine.slice(closeCol + 1);
      const oLine = this.buffer.lines[openRow];
      this.buffer.lines[openRow] = oLine.slice(0, openCol) + oLine.slice(openCol + 1);
    }
    this.cursor.row = openRow; this.cursor.col = openCol;
    this._updateDesiredCol();
    return true;
  }

  /**
   * Change surrounding delimiters. Used by cs.
   * Returns true if successful.
   */
  _doSurroundChange(target, replacement) {
    const pos = this._findSurrounding(target);
    if (!pos) return false;
    const { openRow, openCol, closeRow, closeCol, trim } = pos;
    const { open, close } = this._getSurroundPair(replacement);
    if (openRow === closeRow) {
      const line = this.buffer.lines[openRow];
      let inner = line.slice(openCol + 1, closeCol);
      if (trim) inner = inner.trim();
      this.buffer.lines[openRow] = line.slice(0, openCol) + open + inner + close + line.slice(closeCol + 1);
    } else {
      // Multi-line: replace close, then open
      const cLine = this.buffer.lines[closeRow];
      this.buffer.lines[closeRow] = cLine.slice(0, closeCol) + close + cLine.slice(closeCol + 1);
      const oLine = this.buffer.lines[openRow];
      this.buffer.lines[openRow] = oLine.slice(0, openCol) + open + oLine.slice(openCol + 1);
    }
    this.cursor.row = openRow; this.cursor.col = openCol;
    this._updateDesiredCol();
    return true;
  }

  /**
   * Find the nearest enclosing HTML tag pair around the cursor.
   * Returns { openRow, openCol, openEndRow, openEndCol, closeRow, closeCol, closeEndRow, closeEndCol, tagName }
   * where openCol..openEndCol spans the full opening tag <tag ...> and closeCol..closeEndCol spans </tag>.
   * Returns null if no enclosing tag found.
   */
  _findSurroundingTag() {
    const cursorOffset = this._offsetFromPos(this.cursor.row, this.cursor.col);
    let searchFrom = cursorOffset;

    while (searchFrom >= 0) {
      const openTagStart = this._findPrevOpeningTagStart(searchFrom);
      if (openTagStart === -1) return null;

      const openTagInfo = this._parseOpeningTag(openTagStart);
      if (!openTagInfo) {
        searchFrom = openTagStart - 1;
        continue;
      }

      const closeTagInfo = this._findMatchingCloseTag(openTagInfo.tagName, openTagInfo.tagEnd);
      if (!closeTagInfo) {
        searchFrom = openTagStart - 1;
        continue;
      }

      // Check if the cursor is between the opening and closing tags (inclusive)
      if (cursorOffset >= openTagStart && cursorOffset <= closeTagInfo.closeEnd) {
        const openStart = this._posFromOffset(openTagStart);
        const openEnd = this._posFromOffset(openTagInfo.tagEnd);
        const closeStart = this._posFromOffset(closeTagInfo.closeStart);
        const closeEnd = this._posFromOffset(closeTagInfo.closeEnd);
        return {
          openRow: openStart.row, openCol: openStart.col,
          openEndRow: openEnd.row, openEndCol: openEnd.col,
          closeRow: closeStart.row, closeCol: closeStart.col,
          closeEndRow: closeEnd.row, closeEndCol: closeEnd.col,
          tagName: openTagInfo.tagName
        };
      }

      searchFrom = openTagStart - 1;
    }
    return null;
  }

  /**
   * Delete surrounding HTML tag pair (dst).
   * Returns true if successful.
   */
  _doSurroundDeleteTag() {
    const tag = this._findSurroundingTag();
    if (!tag) return false;
    const { openRow, openCol, openEndRow, openEndCol, closeRow, closeCol, closeEndRow, closeEndCol } = tag;

    if (openRow === closeRow && openEndRow === closeEndRow) {
      // Everything on one line: remove closing tag, then opening tag
      const line = this.buffer.lines[openRow];
      // closeCol is start of </tag>, closeEndCol is position of '>'
      const afterClose = line.slice(0, closeCol) + line.slice(closeEndCol + 1);
      // openCol is start of <tag>, openEndCol is position of '>'
      this.buffer.lines[openRow] = afterClose.slice(0, openCol) + afterClose.slice(openEndCol + 1);
    } else {
      // Multi-line: remove closing tag first (higher row), then opening tag
      if (closeRow === closeEndRow) {
        const cLine = this.buffer.lines[closeRow];
        this.buffer.lines[closeRow] = cLine.slice(0, closeCol) + cLine.slice(closeEndCol + 1);
      }
      if (openRow === openEndRow) {
        const oLine = this.buffer.lines[openRow];
        this.buffer.lines[openRow] = oLine.slice(0, openCol) + oLine.slice(openEndCol + 1);
      }
    }

    this.cursor.row = openRow;
    this.cursor.col = openCol;
    this._clampCursor();
    this._updateDesiredCol();
    return true;
  }

  /**
   * Change surrounding HTML tag pair to a new tag (cst).
   * tagName is the replacement tag name (e.g. "span", "h2", "div class=\"x\"").
   * Replaces only the tag name in opening tag (preserving existing attributes),
   * and fully replaces the closing tag name.
   * Returns true if successful.
   */
  _doSurroundChangeTag(target, tagName) {
    const tag = this._findSurroundingTag();
    if (!tag) return false;

    const newOpenTag = `<${tagName}>`;
    const newTagBase = tagName.split(/\s/)[0];
    const newCloseTag = `</${newTagBase}>`;

    const { openRow, openCol, openEndRow, openEndCol, closeRow, closeCol, closeEndRow, closeEndCol } = tag;

    // Replace closing tag first (so positions for opening tag are stable)
    if (closeRow === closeEndRow) {
      const cLine = this.buffer.lines[closeRow];
      this.buffer.lines[closeRow] = cLine.slice(0, closeCol) + newCloseTag + cLine.slice(closeEndCol + 1);
    }

    // Replace opening tag (keeping attributes from original if new tag has none)
    if (openRow === openEndRow) {
      const oLine = this.buffer.lines[openRow];
      // Parse old opening tag to see if we should preserve attributes
      const oldOpenStr = oLine.slice(openCol, openEndCol + 1);
      // Extract old tag name end position to preserve attributes
      let nameEnd = openCol + 1; // skip '<'
      while (nameEnd <= openEndCol && /[a-zA-Z0-9:\-_.]/.test(oLine[nameEnd])) nameEnd++;
      const oldAttrs = oLine.slice(nameEnd, openEndCol); // everything between name and '>'

      // If new tag name has attributes (contains space), use it directly
      // Otherwise, preserve old attributes
      let replacement;
      if (tagName.includes(' ')) {
        replacement = newOpenTag;
      } else {
        replacement = `<${tagName}${oldAttrs}>`;
      }

      this.buffer.lines[openRow] = oLine.slice(0, openCol) + replacement + oLine.slice(openEndCol + 1);
    }

    this.cursor.row = openRow;
    this.cursor.col = openCol + 1; // cursor on first char of new tag name (nvim-surround behavior)
    this._updateDesiredCol();
    return true;
  }

  // ── Put (paste) ──

  _putAfter(reg) {
    const text = reg ? reg.text : this._unnamedReg;
    const type = reg ? reg.type : this._regType;
    if (text == null) return;
    if (type === 'block') {
      // Blockwise paste: insert each line after cursor column on successive rows
      const pl = text.split('\n');
      const insertCol = this.cursor.col + 1;
      for (let i = 0; i < pl.length; i++) {
        const r = this.cursor.row + i;
        if (r >= this.buffer.lineCount) this.buffer.lines.push('');
        const line = this.buffer.lines[r];
        const padded = line.length < insertCol ? line + ' '.repeat(insertCol - line.length) : line;
        this.buffer.lines[r] = padded.slice(0, insertCol) + pl[i] + padded.slice(insertCol);
      }
      this.cursor.col = insertCol;
      this._updateDesiredCol();
      return;
    }
    if (type === 'line') {
      const pl = text.split('\n');
      this.buffer.lines.splice(this.cursor.row + 1, 0, ...pl);
      this.cursor.row++; this.cursor.col = this._firstNonBlank(this.cursor.row);
    } else {
      const line = this.buffer.lines[this.cursor.row];
      const at = this.cursor.col + 1;
      const pl = text.split('\n');
      if (pl.length === 1) {
        this.buffer.lines[this.cursor.row] = line.slice(0, at) + pl[0] + line.slice(at);
        this.cursor.col = at + pl[0].length - 1;
      } else {
        const before = line.slice(0, at), after = line.slice(at);
        this.buffer.lines[this.cursor.row] = before + pl[0];
        for (let i = 1; i < pl.length - 1; i++) this.buffer.lines.splice(this.cursor.row + i, 0, pl[i]);
        const li = this.cursor.row + pl.length - 1;
        this.buffer.lines.splice(li, 0, pl[pl.length - 1] + after);
        this.cursor.col = before.length;
      }
    }
    this._updateDesiredCol();
  }

  _putBefore(reg) {
    const text = reg ? reg.text : this._unnamedReg;
    const type = reg ? reg.type : this._regType;
    if (text == null) return;
    if (type === 'block') {
      // Blockwise paste: insert each line at cursor column on successive rows
      const pl = text.split('\n');
      const insertCol = this.cursor.col;
      for (let i = 0; i < pl.length; i++) {
        const r = this.cursor.row + i;
        if (r >= this.buffer.lineCount) this.buffer.lines.push('');
        const line = this.buffer.lines[r];
        const padded = line.length < insertCol ? line + ' '.repeat(insertCol - line.length) : line;
        this.buffer.lines[r] = padded.slice(0, insertCol) + pl[i] + padded.slice(insertCol);
      }
      this._updateDesiredCol();
      return;
    }
    if (type === 'line') {
      const pl = text.split('\n');
      this.buffer.lines.splice(this.cursor.row, 0, ...pl);
      this.cursor.col = this._firstNonBlank(this.cursor.row);
    } else {
      const line = this.buffer.lines[this.cursor.row];
      const at = this.cursor.col;
      const pl = text.split('\n');
      if (pl.length === 1) {
        this.buffer.lines[this.cursor.row] = line.slice(0, at) + pl[0] + line.slice(at);
        this.cursor.col = at + pl[0].length - 1;
      } else {
        const before = line.slice(0, at), after = line.slice(at);
        this.buffer.lines[this.cursor.row] = before + pl[0];
        for (let i = 1; i < pl.length - 1; i++) this.buffer.lines.splice(this.cursor.row + i, 0, pl[i]);
        const li = this.cursor.row + pl.length - 1;
        this.buffer.lines.splice(li, 0, pl[pl.length - 1] + after);
        this.cursor.col = before.length;
      }
    }
    this._updateDesiredCol();
  }

  // ── Range helpers ──

  _extractRange(sr, sc, er, ec) {
    if (sr === er) return this.buffer.lines[sr].slice(sc, ec + 1);
    let t = this.buffer.lines[sr].slice(sc);
    for (let r = sr + 1; r < er; r++) t += '\n' + this.buffer.lines[r];
    t += '\n' + this.buffer.lines[er].slice(0, ec + 1);
    return t;
  }

  _deleteRange(sr, sc, er, ec) {
    if (sr === er) {
      this.buffer.lines[sr] = this.buffer.lines[sr].slice(0, sc) + this.buffer.lines[sr].slice(ec + 1);
    } else {
      const fp = this.buffer.lines[sr].slice(0, sc);
      const lp = this.buffer.lines[er].slice(ec + 1);
      this.buffer.lines[sr] = fp + lp;
      this.buffer.lines.splice(sr + 1, er - sr);
    }
    if (this.buffer.lines.length === 0) this.buffer.lines = [''];
  }

  // ── Core helpers ──

  _maxCol() {
    const len = this.buffer.lineLength(this.cursor.row);
    if (this.mode === Mode.INSERT || this.mode === Mode.REPLACE) return len;
    return len > 0 ? len - 1 : 0;
  }

  // Convert buffer column to screen (virtual) column, accounting for tabs
  // Returns the virtual column where the cursor is displayed (last cell of the char)
  _bufToVirtCol(row, bufCol) {
    const line = this.buffer.lines[row] || '';
    let virtCol = 0;
    for (let i = 0; i < line.length && i <= bufCol; i++) {
      if (i === bufCol) {
        // For the character at bufCol, return the start position
        // (For tabs: cursor shows at start of tab expansion in most cases)
        // Actually Vim shows cursor at the END of tab width
        if (line[i] === '\t') {
          virtCol += 8 - (virtCol % 8) - 1; // right edge of tab
        }
        return virtCol;
      }
      if (line[i] === '\t') {
        virtCol += 8 - (virtCol % 8);
      } else {
        virtCol++;
      }
    }
    return virtCol;
  }

  // Convert screen (virtual) column to buffer column
  _virtToBufCol(row, targetVirtCol) {
    const line = this.buffer.lines[row] || '';
    let virtCol = 0;
    for (let i = 0; i < line.length; i++) {
      if (line[i] === '\t') {
        const nextVirt = virtCol + 8 - (virtCol % 8);
        if (nextVirt > targetVirtCol) return i; // tab spans this position
        virtCol = nextVirt;
      } else {
        virtCol++;
      }
      if (virtCol > targetVirtCol) return i;
    }
    return line.length > 0 ? line.length - 1 : 0;
  }

  _clampCursor() {
    if (this.cursor.row < 0) this.cursor.row = 0;
    if (this.cursor.row >= this.buffer.lineCount) this.cursor.row = this.buffer.lineCount - 1;
    const max = this._maxCol();
    if (this.cursor.col < 0) this.cursor.col = 0;
    // In visual mode after $, allow cursor one past end of line
    if ((this.mode === Mode.VISUAL || this.mode === Mode.VISUAL_LINE || this.mode === Mode.VISUAL_BLOCK) && this._desiredCol === Infinity) {
      const len = this.buffer.lineLength(this.cursor.row);
      if (this.cursor.col > len) this.cursor.col = len;
    } else {
      if (this.cursor.col > max) this.cursor.col = max;
    }
  }

  _ensureCursorVisible() {
    const so = this._settings.scrolloff || 0;
    // Clamp scrolloff so it doesn't exceed half the screen
    const eff = Math.min(so, Math.floor(this._textRows / 2));
    if (this.cursor.row < this.scrollTop + eff) {
      this.scrollTop = Math.max(0, this.cursor.row - eff);
    }
    if (this.cursor.row >= this.scrollTop + this._textRows - eff) {
      this.scrollTop = this.cursor.row - this._textRows + 1 + eff;
      // Don't over-scroll past end of buffer for scrolloff purposes
      // (nvim won't auto-scroll beyond the last line to satisfy scrolloff)
      const maxSoScroll = Math.max(0, this.buffer.lines.length - this._textRows);
      if (this.scrollTop > maxSoScroll) this.scrollTop = maxSoScroll;
    }
  }

  /**
   * Adjust scrollLeft to keep cursor visible in nowrap mode.
   * Uses Neovim-compatible sidescroll=1 behavior:
   * - small overshoot → cursor at edge
   * - large overshoot (> half screen) → recenter
   */
  _adjustHorizontalScroll() {
    if (this._settings.wrap) {
      this.scrollLeft = 0;
      return;
    }
    const textCols = this._computeTextCols();
    if (textCols <= 0) return;
    const virtCol = this._virtColAt(this.cursor.row, this.cursor.col);
    if (virtCol > this.scrollLeft + textCols - 1) {
      // Cursor past right edge
      const needed = virtCol - (this.scrollLeft + textCols - 1);
      if (needed > Math.floor(textCols / 2)) {
        this.scrollLeft = virtCol - Math.floor(textCols / 2);
      } else {
        this.scrollLeft = virtCol - textCols + 1;
      }
    } else if (virtCol < this.scrollLeft) {
      // Cursor past left edge
      this.scrollLeft = virtCol;
    }
    this.scrollLeft = Math.max(0, this.scrollLeft);
  }

  /**
   * Compute the available text columns (total cols minus gutter width).
   */
  _computeTextCols() {
    let gw = 0;
    if (this._settings.number || this._settings.relativenumber) {
      const nd = String(this.buffer.lineCount).length;
      gw = Math.max(4, nd + 1);
    }
    return this.cols - gw;
  }

  // ── Spell checking helpers ──

  /**
   * Check if a word is misspelled.
   * Returns true if the word is NOT in the dictionary and NOT in the good words list,
   * OR if it's explicitly in the bad words list.
   */
  _isSpellBad(word) {
    if (!word || !this._settings.spell) return false;
    const lower = word.toLowerCase();
    if (this._spellBadWords.has(lower)) return true;
    if (this._spellGoodWords.has(lower)) return false;
    return !DICTIONARY.has(lower);
  }

  /**
   * Get the word under or near the cursor.
   * Returns {word, startCol, endCol} or null.
   */
  _getWordAtCursor() {
    const line = this.buffer.lines[this.cursor.row] || '';
    let col = this.cursor.col;
    // Find word boundaries (word = sequence of word chars)
    if (col >= line.length) col = Math.max(0, line.length - 1);
    if (!/[a-zA-Z']/.test(line[col])) return null;
    let start = col, end = col;
    while (start > 0 && /[a-zA-Z']/.test(line[start - 1])) start--;
    while (end < line.length - 1 && /[a-zA-Z']/.test(line[end + 1])) end++;
    return { word: line.slice(start, end + 1), startCol: start, endCol: end };
  }

  /**
   * Find the next misspelled word from the given position.
   * Returns {row, col} or null.
   */
  _findNextSpellError(fromRow, fromCol, forward) {
    const wordRegex = /[a-zA-Z']+/g;
    const lineCount = this.buffer.lineCount;
    let row = fromRow;
    let startOffset = forward ? fromCol + 1 : 0;
    // Search through lines
    for (let i = 0; i < lineCount; i++) {
      const line = this.buffer.lines[row] || '';
      wordRegex.lastIndex = 0;
      let match;
      const matches = [];
      while ((match = wordRegex.exec(line)) !== null) {
        matches.push({ word: match[0], col: match.index });
      }
      if (!forward) matches.reverse();
      for (const m of matches) {
        if (forward && row === fromRow && m.col <= fromCol) continue;
        if (!forward && row === fromRow && m.col >= fromCol) continue;
        if (this._isSpellBad(m.word)) {
          return { row, col: m.col };
        }
      }
      row = forward
        ? (row + 1) % lineCount
        : (row - 1 + lineCount) % lineCount;
    }
    return null;
  }

  /**
   * Generate simple spelling suggestions for a misspelled word.
   * Returns array of up to 5 suggestions.
   */
  _spellSuggest(word) {
    if (!word) return [];
    const lower = word.toLowerCase();
    const suggestions = [];
    // Simple edit distance 1: substitution, deletion, insertion, transposition
    for (const dictWord of DICTIONARY) {
      if (suggestions.length >= 5) break;
      if (Math.abs(dictWord.length - lower.length) > 1) continue;
      let dist = 0;
      const maxLen = Math.max(dictWord.length, lower.length);
      for (let i = 0; i < maxLen; i++) {
        if (dictWord[i] !== lower[i]) dist++;
        if (dist > 1) break;
      }
      if (dist <= 1 && dictWord !== lower) {
        suggestions.push(dictWord);
      }
    }
    return suggestions;
  }

  /** Compute the 0-indexed virtual (screen) column for a byte position in a line. */
  _virtColAt(row, col) {
    const line = this.buffer.lines[row] || '';
    let vc = 0;
    for (let i = 0; i < col && i < line.length; i++) {
      if (line[i] === '\t') vc += 8 - (vc % 8);
      else vc++;
    }
    return vc;
  }

  /** Update _desiredCol from current cursor position (virtual column). */
  _updateDesiredCol() {
    this._desiredCol = this._virtColAt(this.cursor.row, this.cursor.col);
  }

  /** Apply _desiredCol to cursor.col on current row (converts virtual → buffer col). */
  _applyDesiredCol() {
    if (this._desiredCol === Infinity) {
      this.cursor.col = this._maxCol();
    } else {
      this.cursor.col = this._byteColForVirtCol(this.cursor.row, this._desiredCol);
    }
  }

  /** 
   * Compute the 0-indexed virtual (screen) column of the END of the character at `col`.
   * For a tab, this is the last visual column of the tab. For regular chars, same as _virtColAt.
   * Matches Neovim's virtcol('.') - 1.
   */
  _virtColEnd(row, col) {
    const line = this.buffer.lines[row] || '';
    if (col >= line.length) return this._virtColAt(row, col);
    const startVc = this._virtColAt(row, col);
    if (line[col] === '\t') return startVc + (8 - (startVc % 8)) - 1;
    return startVc;
  }

  /**
   * Find the byte column in `row` that corresponds to a target virtual column.
   * If the target falls on a tab, returns that tab's byte position.
   * If the target exceeds the line end, clamps to the last character.
   */
  _byteColForVirtCol(row, targetVirtCol) {
    const line = this.buffer.lines[row] || '';
    if (line.length === 0) return 0;
    let vc = 0;
    for (let i = 0; i < line.length; i++) {
      let nextVc;
      if (line[i] === '\t') nextVc = vc + (8 - (vc % 8));
      else nextVc = vc + 1;
      if (targetVirtCol < nextVc) return i; // target falls within this char
      vc = nextVc;
    }
    // target exceeds line end — clamp to last character
    return Math.max(0, line.length - 1);
  }

  /**
   * Shift (indent) a single line right by shiftwidth.
   * Uses set_indent logic: compute current indent, add sw, rebuild with tabs+spaces.
   * Skips empty lines (nvim behavior).
   * With noexpandtab and tabstop=shiftwidth=8, this simply prepends a tab.
   */
  _shiftLineRight(row) {
    const line = this.buffer.lines[row];
    if (line.length === 0) return; // skip empty lines
    const sw = this._settings.shiftwidth || 8;
    const ts = this._settings.tabstop || 8;
    const et = this._settings.expandtab;
    // Compute current indent in virtual columns
    let indent = 0;
    let i = 0;
    while (i < line.length && (line[i] === ' ' || line[i] === '\t')) {
      if (line[i] === '\t') indent += ts - (indent % ts);
      else indent++;
      i++;
    }
    const text = line.slice(i);
    const newIndent = indent + sw;
    if (et) {
      this.buffer.lines[row] = ' '.repeat(newIndent) + text;
    } else {
      const tabs = Math.floor(newIndent / ts);
      const spaces = newIndent % ts;
      this.buffer.lines[row] = '\t'.repeat(tabs) + ' '.repeat(spaces) + text;
    }
  }

  /**
   * Shift (dedent) a single line left by shiftwidth.
   * Computes current indent, subtracts sw (clamped to 0), rebuilds with tabs+spaces.
   * Skips empty lines.
   */
  _shiftLineLeft(row) {
    const line = this.buffer.lines[row];
    if (line.length === 0) return; // skip empty lines
    const sw = this._settings.shiftwidth || 8;
    const ts = this._settings.tabstop || 8;
    const et = this._settings.expandtab;
    // Compute current indent in virtual columns
    let indent = 0;
    let i = 0;
    while (i < line.length && (line[i] === ' ' || line[i] === '\t')) {
      if (line[i] === '\t') indent += ts - (indent % ts);
      else indent++;
      i++;
    }
    if (indent === 0) return; // nothing to dedent
    const text = line.slice(i);
    const newIndent = Math.max(0, indent - sw);
    if (et) {
      this.buffer.lines[row] = ' '.repeat(newIndent) + text;
    } else {
      const tabs = Math.floor(newIndent / ts);
      const spaces = newIndent % ts;
      this.buffer.lines[row] = '\t'.repeat(tabs) + ' '.repeat(spaces) + text;
    }
  }

  // ── Display-line helpers (for gj, gk, g0, g$, g^, gm, gM) ──

  /** Number of text columns available for content (accounts for line-number gutter). */
  _getTextCols() {
    const showGutter = this._settings?.number || this._settings?.relativenumber;
    if (!showGutter) return this.cols;
    const numDigits = String(this.buffer.lineCount).length;
    const gutterWidth = Math.max(4, numDigits + 1);
    return this.cols - gutterWidth;
  }

  /** Tab-expand a raw buffer line into a screen string (same logic as screen.js). */
  _expandLineText(raw) {
    const ts = this._settings.tabstop || 8;
    let expanded = '';
    for (let i = 0; i < raw.length; i++) {
      if (raw[i] === '\t') {
        const spaces = ts - (expanded.length % ts);
        expanded += ' '.repeat(spaces);
      } else {
        expanded += raw[i];
      }
    }
    return expanded;
  }

  /**
   * Get display-line information for a cursor position within a wrapped buffer line.
   * @param {number} bufRow  - buffer row index
   * @param {number} bufCol  - buffer column (byte index)
   * @returns {{ displayRow: number, totalDisplayRows: number, displayLineStart: number, displayLineEnd: number }}
   *   displayRow        – which display row the cursor is on (0-based)
   *   totalDisplayRows  – total wrapped display rows for this buffer line
   *   displayLineStart  – buffer column where this display row starts
   *   displayLineEnd    – buffer column of the last character on this display row
   */
  _displayLineInfo(bufRow, bufCol) {
    const textCols = this._getTextCols();
    const raw = this.buffer.lines[bufRow] || '';
    const ts = this._settings.tabstop || 8;

    // Build mapping: for each buffer column, what is its screen (expanded) column?
    const bufToScreen = [];
    let screenCol = 0;
    for (let i = 0; i < raw.length; i++) {
      bufToScreen[i] = screenCol;
      if (raw[i] === '\t') {
        screenCol += ts - (screenCol % ts);
      } else {
        screenCol++;
      }
    }
    bufToScreen[raw.length] = screenCol; // sentinel for end-of-line
    const expandedLen = screenCol;

    const totalDisplayRows = expandedLen === 0 ? 1 : Math.ceil(expandedLen / textCols);

    // Which display row is bufCol on?
    const cursorScreenCol = bufToScreen[Math.min(bufCol, raw.length)];
    const displayRow = textCols > 0 ? Math.floor(cursorScreenCol / textCols) : 0;

    // Screen column range for this display row
    const screenStart = displayRow * textCols;
    const screenEnd = Math.min((displayRow + 1) * textCols - 1, expandedLen - 1);

    // Map screen columns back to buffer columns
    // displayLineStart: first buffer col whose screen col >= screenStart
    let displayLineStart = raw.length; // default: end of line
    for (let i = 0; i < raw.length; i++) {
      if (bufToScreen[i] >= screenStart) { displayLineStart = i; break; }
    }

    // displayLineEnd: last buffer col whose screen col <= screenEnd
    let displayLineEnd = displayLineStart;
    for (let i = raw.length - 1; i >= 0; i--) {
      if (bufToScreen[i] <= screenEnd) { displayLineEnd = i; break; }
    }

    // For empty lines, both start and end are 0
    if (raw.length === 0) {
      return { displayRow: 0, totalDisplayRows: 1, displayLineStart: 0, displayLineEnd: 0 };
    }

    return { displayRow, totalDisplayRows, displayLineStart, displayLineEnd };
  }

  /**
   * Map a screen column on a given display row back to a buffer column.
   * @param {number} bufRow       - buffer row
   * @param {number} displayRow   - display row within the wrapped line (0-based)
   * @param {number} targetScreenCol - target screen column relative to the display row start
   * @returns {number} buffer column
   */
  _bufColForDisplayCol(bufRow, displayRow, targetScreenCol) {
    const textCols = this._getTextCols();
    const raw = this.buffer.lines[bufRow] || '';
    if (raw.length === 0) return 0;
    const ts = this._settings.tabstop || 8;

    // Absolute screen column
    const absTarget = displayRow * textCols + targetScreenCol;

    let screenCol = 0;
    for (let i = 0; i < raw.length; i++) {
      let nextScreen;
      if (raw[i] === '\t') {
        nextScreen = screenCol + (ts - (screenCol % ts));
      } else {
        nextScreen = screenCol + 1;
      }
      if (absTarget < nextScreen) return i;
      screenCol = nextScreen;
    }
    return Math.max(0, raw.length - 1);
  }

  _firstNonBlank(row) {
    if (row < 0 || row >= this.buffer.lineCount) return 0;
    const line = this.buffer.lines[row];
    const m = line.match(/\S/);
    if (m) return m.index;
    // All-whitespace line: go to last character (Vim behavior)
    return Math.max(0, line.length - 1);
  }

  _lastNonBlank(row) {
    if (row < 0 || row >= this.buffer.lineCount) return 0;
    const line = this.buffer.lines[row];
    for (let i = line.length - 1; i >= 0; i--) {
      if (line[i] !== ' ' && line[i] !== '\t') return i;
    }
    return 0;
  }

  // ── Mark resolution ──

  /**
   * Resolve a mark key to a {row, col} position, or null if not set.
   * Supports a-z (user marks), . (last change), ' and ` (last jump position),
   * < and > (visual selection bounds).
   */
  _resolveMark(key) {
    // User marks a-z
    if (key.length === 1 && key >= 'a' && key <= 'z') {
      return this._marks[key] || null;
    }
    // `. / '. — last change position
    if (key === '.') {
      if (this._changeList.length > 0) {
        return this._changeList[this._changeList.length - 1];
      }
      return null;
    }
    // `' / '' — position before last jump
    if (key === "'" || key === '`') {
      return this._lastJumpPos || null;
    }
    // `< / '< — start of last visual selection
    if (key === '<') {
      if (this._lastVisual) {
        const s = this._lastVisual.start;
        const e = this._lastVisual.end;
        const sr = Math.min(s.row, e.row);
        const sc = (s.row < e.row) ? s.col : (s.row === e.row ? Math.min(s.col, e.col) : e.col);
        return { row: sr, col: sc };
      }
      return null;
    }
    // `> / '> — end of last visual selection
    if (key === '>') {
      if (this._lastVisual) {
        const s = this._lastVisual.start;
        const e = this._lastVisual.end;
        const er = Math.max(s.row, e.row);
        const ec = (s.row > e.row) ? s.col : (s.row === e.row ? Math.max(s.col, e.col) : e.col);
        return { row: er, col: ec };
      }
      return null;
    }
    return null;
  }

  // ── Jump list ──

  _addJumpEntry() {
    // Record position before jump for '' / `` marks
    this._lastJumpPos = { row: this.cursor.row, col: this.cursor.col };
    const entry = { row: this.cursor.row, col: this.cursor.col };
    // Same-line dedup: if last entry is on same line, update col (nvim setpcmark)
    if (this._jumpList.length > 0) {
      const last = this._jumpList[this._jumpList.length - 1];
      if (last.row === entry.row) {
        last.col = entry.col;
        this._jumpListPos = this._jumpList.length;
        return;
      }
    }
    this._jumpList.push(entry);
    if (this._jumpList.length > 100) this._jumpList.shift();
    this._jumpListPos = this._jumpList.length;
  }

  // ── Increment / Decrement number ──

  _incrementNumber(delta) {
    const line = this.buffer.lines[this.cursor.row];
    if (line.length === 0) return false;

    // Find all numbers on the line; pick the first one whose end >= cursor.col
    const re = /-?\d+/g;
    let m;
    while ((m = re.exec(line)) !== null) {
      const s = m.index;
      const e = s + m[0].length - 1;
      if (e >= this.cursor.col) {
        const num = parseInt(m[0], 10) + delta;
        const newText = num.toString();
        this.buffer.lines[this.cursor.row] = line.slice(0, s) + newText + line.slice(e + 1);
        this.cursor.col = s + newText.length - 1;
        this._updateDesiredCol();
        return true;
      }
    }
    return false;
  }

  // ── Sentence motions ──

  /** ) motion: move forward to beginning of next sentence */
  _moveSentenceForward() {
    const lc = this.buffer.lineCount;
    let row = this.cursor.row;
    let col = this.cursor.col;

    // Advance one character to start scanning past current position
    col++;
    if (col > this.buffer.lines[row].length) {
      row++;
      col = 0;
    }
    if (row >= lc) return false;

    // If we wrapped from a blank line, skip consecutive blank lines
    if (col === 0 && row > 0 && this.buffer.lines[row - 1].length === 0) {
      while (row < lc && this.buffer.lines[row].length === 0) row++;
      if (row < lc) {
        this.cursor.row = row;
        this.cursor.col = this._firstNonBlankOfLine(this.buffer.lines[row]);
        return true;
      }
      return false;
    }

    // If we advanced past a sentence-ending (.!? + optional closing chars),
    // skip whitespace to find the next sentence start
    if (col > 0) {
      const checkLine = this.buffer.lines[row];
      let k = col - 1;
      // Skip whitespace backward
      while (k >= 0 && (checkLine[k] === ' ' || checkLine[k] === '\t')) k--;
      // Skip closing chars
      while (k >= 0 && /[)}\]'""\u201D]/.test(checkLine[k])) k--;
      if (k >= 0 && (checkLine[k] === '.' || checkLine[k] === '!' || checkLine[k] === '?')) {
        let j = col;
        while (j < checkLine.length && (checkLine[j] === ' ' || checkLine[j] === '\t')) j++;
        if (j < checkLine.length) {
          this.cursor.row = row;
          this.cursor.col = j;
          return true;
        }
        // Next sentence is on the next line
        if (row + 1 < lc) {
          this.cursor.row = row + 1;
          this.cursor.col = this.buffer.lines[row + 1].length === 0 ? 0 : this._firstNonBlankOfLine(this.buffer.lines[row + 1]);
          return true;
        }
        return false;
      }
    }

    while (row < lc) {
      const line = this.buffer.lines[row];

      // Empty line is a paragraph/sentence boundary — skip consecutive blanks
      if (line.length === 0) {
        while (row < lc && this.buffer.lines[row].length === 0) row++;
        if (row < lc) {
          this.cursor.row = row;
          this.cursor.col = this._firstNonBlankOfLine(this.buffer.lines[row]);
        } else {
          this.cursor.row = lc - 1;
          this.cursor.col = 0;
        }
        return true;
      }

      // Scan for sentence-ending punctuation on this line
      for (let i = col; i < line.length; i++) {
        if (line[i] === '.' || line[i] === '!' || line[i] === '?') {
          let j = i + 1;
          // Skip optional closing chars
          while (j < line.length && /[)}\]'""]/.test(line[j])) j++;
          // Must be followed by whitespace or end of line
          if (j >= line.length || line[j] === ' ' || line[j] === '\t') {
            // Skip trailing whitespace to find next sentence start
            while (j < line.length && (line[j] === ' ' || line[j] === '\t')) j++;
            if (j < line.length) {
              this.cursor.row = row;
              this.cursor.col = j;
              return true;
            }
            // Sentence starts on next line
            if (row + 1 < lc) {
              this.cursor.row = row + 1;
              this.cursor.col = this.buffer.lines[row + 1].length === 0 ? 0 : this._firstNonBlankOfLine(this.buffer.lines[row + 1]);
              return true;
            }
            return false;
          }
        }
      }

      row++;
      col = 0;
    }
    return false;
  }

  /** ( motion: move backward to beginning of current/previous sentence */
  _moveSentenceBackward() {
    let row = this.cursor.row;
    let col = this.cursor.col;

    // Step back one character to avoid finding current position
    col--;
    if (col < 0) {
      row--;
      if (row < 0) return false;
      col = Math.max(0, this.buffer.lines[row].length - 1);
    }

    while (row >= 0) {
      const line = this.buffer.lines[row];

      // Empty line is a sentence boundary — stop here if it's before our start position
      if (line.length === 0) {
        if (row < this.cursor.row || (row === this.cursor.row && 0 < this.cursor.col)) {
          this.cursor.row = row;
          this.cursor.col = 0;
          return true;
        }
        row--;
        if (row >= 0) col = Math.max(0, this.buffer.lines[row].length - 1);
        continue;
      }

      // Scan backward on this line for sentence end
      for (let i = Math.min(col, line.length - 1); i >= 0; i--) {
        if (line[i] === '.' || line[i] === '!' || line[i] === '?') {
          let j = i + 1;
          while (j < line.length && /[)}\]'""]/.test(line[j])) j++;
          if (j >= line.length || line[j] === ' ' || line[j] === '\t') {
            // Found sentence end. The next sentence starts after whitespace.
            while (j < line.length && (line[j] === ' ' || line[j] === '\t')) j++;
            if (j < line.length && (row < this.cursor.row || j < this.cursor.col)) {
              this.cursor.row = row;
              this.cursor.col = j;
              return true;
            }
            // Sentence end at EOL — the next sentence starts on the next non-blank line
            if (j >= line.length) {
              let nr = row + 1;
              while (nr < this.buffer.lineCount && this.buffer.lines[nr].length === 0) nr++;
              if (nr < this.buffer.lineCount && (nr < this.cursor.row || (nr === this.cursor.row && this._firstNonBlankOfLine(this.buffer.lines[nr]) < this.cursor.col))) {
                this.cursor.row = nr;
                this.cursor.col = this._firstNonBlankOfLine(this.buffer.lines[nr]);
                return true;
              }
            }
          }
        }
      }

      // Check if this line starts after a blank line (= sentence start)
      if (row > 0 && this.buffer.lines[row - 1].length === 0) {
        const sentStart = this._firstNonBlankOfLine(line);
        if (row < this.cursor.row || sentStart < this.cursor.col) {
          this.cursor.row = row;
          this.cursor.col = sentStart;
          return true;
        }
      }

      row--;
      if (row >= 0) col = Math.max(0, this.buffer.lines[row].length - 1);
    }

    // Beginning of buffer
    if (this.cursor.row > 0 || this.cursor.col > 0) {
      this.cursor.row = 0;
      this.cursor.col = 0;
      return true;
    }
    return false;
  }

  _rot13(str) {
    return str.replace(/[a-zA-Z]/g, c => {
      const base = c <= 'Z' ? 65 : 97;
      return String.fromCharCode(((c.charCodeAt(0) - base + 13) % 26) + base);
    });
  }

  _cindent(startRow, endRow) {
    const sw = this._settings.shiftwidth || 8;
    const ts = this._settings.tabstop || 8;
    const et = this._settings.expandtab;
    let level = 0;
    // Scan from start of file to determine indent level at startRow
    for (let r = 0; r < startRow; r++) {
      const line = this.buffer.lines[r];
      for (const ch of line) {
        if (ch === '{') level++;
        else if (ch === '}') level = Math.max(0, level - 1);
      }
    }
    // Track previous trimmed line for continuation detection
    let prevTrimmed = startRow > 0 ? this.buffer.lines[startRow - 1].trim() : '';
    // Apply indent to range
    for (let r = startRow; r <= endRow; r++) {
      const line = this.buffer.lines[r];
      const trimmed = line.trimStart();
      // Line starting with } decreases level first
      if (trimmed.startsWith('}')) level = Math.max(0, level - 1);
      // Continuation: previous line doesn't end with { } or ;
      let continuation = false;
      if (prevTrimmed.length > 0 && !trimmed.startsWith('}')) {
        const lastChar = prevTrimmed[prevTrimmed.length - 1];
        if (lastChar !== '{' && lastChar !== '}' && lastChar !== ';') {
          continuation = true;
        }
      }
      const virtIndent = level * sw + (continuation ? sw : 0);
      let indentStr;
      if (et) {
        indentStr = ' '.repeat(virtIndent);
      } else {
        const tabs = Math.floor(virtIndent / ts);
        const spaces = virtIndent % ts;
        indentStr = '\t'.repeat(tabs) + ' '.repeat(spaces);
      }
      this.buffer.lines[r] = indentStr + trimmed;
      // Count { and } to update level for next line
      for (const ch of trimmed) {
        if (ch === '{') level++;
        else if (ch === '}') level = Math.max(0, level - 1);
      }
      prevTrimmed = trimmed;
    }
  }

  _updateStatus() {
    const r = this.cursor.row + 1, c = this.cursor.col + 1, total = this.buffer.lineCount;
    // Virtual column display: show "bytecol-virtcol" when they differ (tabs)
    const byteCol = c;
    const virtCol = this._virtColEnd(this.cursor.row, this.cursor.col) + 1;
    const colStr = byteCol === virtCol ? `${byteCol}` : `${byteCol}-${virtCol}`;
    const pos = `${r},${colStr}`;
    const pct = total <= this._textRows ? 'All' : r === 1 ? 'Top' : r === total ? 'Bot' : `${Math.round((r / total) * 100)}%`;
    const right = pos.padEnd(14) + ' ' + pct;
    // Left side: filename + modified flag
    let left = '';
    if (this._fileName) {
      left = this._fileName;
      if (this._changeCount > 0) left += ' [+]';
    }
    // Build status line: left-padded right, with filename on left
    const gap = Math.max(1, this.cols - left.length - right.length);
    this.statusLine = left + ' '.repeat(gap) + right;
    if (this.mode === Mode.INSERT) this.commandLine = '-- INSERT --';
    else if (this.mode === Mode.REPLACE) this.commandLine = '-- REPLACE --';
    else if (this.mode === Mode.VISUAL) this.commandLine = '-- VISUAL --';
    else if (this.mode === Mode.VISUAL_LINE) this.commandLine = '-- VISUAL LINE --';
    else if (this.mode === Mode.VISUAL_BLOCK) this.commandLine = '-- VISUAL BLOCK --';
    else if (this.mode === Mode.NORMAL && this._macroRecording) {
      this.commandLine = 'recording @' + this._macroRecording;
    } else if (this.mode === Mode.NORMAL && this._insertOneShot) {
      this.commandLine = '-- (insert) --';
    } else if (this.mode === Mode.NORMAL && !this._stickyCommandLine) {
      if (this._echoMessage != null) {
        this.commandLine = this._echoMessage;
      } else {
        this.commandLine = '';
      }
    }
  }
}
