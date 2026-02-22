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

/** @enum {string} */
export const Mode = {
  NORMAL: 'normal',
  INSERT: 'insert',
  VISUAL: 'visual',
  VISUAL_LINE: 'visual_line',
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
    this.statusLine = '';
    this.commandLine = '';
    this.filename = null;   // set by SessionManager for syntax highlighting
    this._textRows = rows - 2;

    // Pending state
    this._pendingCount = '';
    this._pendingOp = '';
    this._pendingG = false;
    this._pendingZ = false;
    this._pendingCapZ = false;
    this._pendingF = '';
    this._pendingR = false;
    this._pendingM = false;
    this._pendingQ = false;
    this._pendingAt = false;
    this._pendingQuote = false;
    this._pendingBacktick = false;
    this._pendingTextObjType = null;
    this._opStartPos = null;
    this._motionInclusive = false;
    this._motionLinewise = false;
    this._motionExclusive = false;
    this._insertCount = 1;
    this._scrollHalf = 0; // sticky scroll amount for Ctrl-D/Ctrl-U

    // Operator saved across async-like sequences (e.g. d/pattern<CR>)
    this._pendingOpForSearch = '';
    this._opStartPosForSearch = null;

    // Registers
    this._unnamedReg = '';
    this._regType = 'char'; // 'char' or 'line'
    this._namedRegs = {};   // {a-z}: { text, type }
    this._pendingRegKey = ''; // pending " register prefix
    this._pendingCtrlR = false; // pending Ctrl-R in insert mode

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

    // Last insert position (for gi)
    this._lastInsertPos = null;

    // Find on line
    this._lastFind = null;

    // Visual mode
    this._visualStart = { row: 0, col: 0 };
    this._visualExclusive = false; // true when last visual motion was exclusive (e.g. ), ()
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

    // Ex command hook — set by _executeCommand when it processes :w/:q etc.
    // SessionManager reads and clears this after each feedKey.
    this._lastExCommand = null;

    // Visual command range — set when : is pressed in visual mode
    this._visualCmdRange = null;

    // Desired column for vertical movement
    this._desiredCol = 0;

    // Settings (:set)
    this._settings = {
      number: false,       // :set number / :set nonumber
      relativenumber: false, // :set relativenumber / :set norelativenumber
    };

    this._updateStatus();
  }

  // ── Public API ──

  loadFile(text) {
    const lines = text.split('\n');
    if (lines.length > 1 && lines[lines.length - 1] === '') lines.pop();
    this.buffer = new Buffer(lines);
    // Neovim opens files with cursor at the first non-blank character
    const fnb = this._firstNonBlank(0);
    this.cursor = { row: 0, col: fnb };
    // Set desiredCol to the virtual column of the first non-blank
    this._desiredCol = this._virtColAt(0, fnb);
    this.scrollTop = 0;
    this._undoStack = [];
    this._redoStack = [];
    this._changeCount = 0;
    this._jumpList = [];
    this._jumpListPos = -1;
    this._changeList = [];
    this._changeListPos = -1;
    this._saveSnapshot();
    this._changeCount = 0; // reset after initial snapshot
    // Clear change list — loading a file is not a "change"
    this._changeList = [];
    this._changeListPos = -1;
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
      this.commandLine = '';
    }

    // Capture keys into macro register (but not keys generated by macro playback)
    if (this._macroRecording && !this._macroPlaying) {
      this._macroKeys.push(key);
    }

    if (this.mode === Mode.COMMAND) this._commandKey(key);
    else if (this.mode === Mode.NORMAL) this._normalKey(key);
    else if (this.mode === Mode.INSERT) this._insertKey(key);
    else if (this.mode === Mode.VISUAL || this.mode === Mode.VISUAL_LINE) this._visualKey(key);
    else if (this.mode === Mode.REPLACE) this._replaceKey(key);
    this._clampCursor();
    this._ensureCursorVisible();
    this._updateStatus();
  }

  // ── Snapshot / Undo / Redo ──

  _saveSnapshot() {
    // During macro playback, suppress intermediate snapshots
    // (the single pre-playback snapshot handles undo for the whole macro)
    if (this._macroPlaying) return;
    this._changeCount++;
    // Record position in change list
    this._changeList.push({ row: this.cursor.row, col: this.cursor.col });
    if (this._changeList.length > 100) this._changeList.shift();
    this._changeListPos = this._changeList.length;
    this._undoStack.push({
      lines: [...this.buffer.lines],
      cursor: { ...this.cursor },
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

  /** Save text to the current register (named or unnamed) */
  _setReg(text, type) {
    const reg = this._pendingRegKey;
    this._unnamedReg = text;
    this._regType = type;
    if (reg) {
      this._namedRegs[reg] = { text, type };
      this._pendingRegKey = '';
    }
  }

  /** Get text and type from the current register (named or unnamed) */
  _getReg() {
    const reg = this._pendingRegKey;
    this._pendingRegKey = '';
    if (reg) {
      const r = this._namedRegs[reg];
      return r ? r : { text: '', type: 'char' };
    }
    return { text: this._unnamedReg, type: this._regType };
  }

  // ── Normal mode ──

  _normalKey(key) {
    // q stops macro recording (before any other dispatch)
    if (this._macroRecording && key === 'q' && !this._pendingOp && !this._pendingF && !this._pendingR && !this._pendingG && !this._pendingZ && !this._pendingCapZ && !this._pendingM && !this._pendingQuote && !this._pendingBacktick && !this._pendingTextObjType) {
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
      if (key.length === 1 && key >= 'a' && key <= 'z') {
        this._pendingRegKey = key;
      }
      // After setting register, fall through to normal processing
      // (the next key like d, y, p etc. will use the register)
      return;
    }

    // Pending r
    if (this._pendingR) {
      this._pendingR = false;
      if (key.length === 1 && key !== 'Escape') {
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
          if (moved || (!failed && (type === 't' || type === 'T'))) {
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
      if (key.length === 1 && key >= 'a' && key <= 'z' && this._marks[key]) {
        const sr = this.cursor.row, sc = this.cursor.col;
        this.cursor.row = this._marks[key].row;
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
      if (key.length === 1 && key >= 'a' && key <= 'z' && this._marks[key]) {
        const sr = this.cursor.row, sc = this.cursor.col;
        this.cursor.row = this._marks[key].row;
        this.cursor.col = this._marks[key].col;
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

    // Pending z
    if (this._pendingZ) {
      this._pendingZ = false;
      this._handleZ(key);
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
      case 'j': case 'ArrowDown': {
        const count = this._getCount();
        const beforeRow = this.cursor.row;
        for (let i = 0; i < count; i++) {
          if (this.cursor.row < this.buffer.lineCount - 1) this.cursor.row++;
        }
        if (this._macroPlaying && this.cursor.row === beforeRow) this._macroAborted = true;
        this._applyDesiredCol();
        break;
      }
      case 'k': case 'ArrowUp': {
        const count = this._getCount();
        const beforeRow = this.cursor.row;
        for (let i = 0; i < count; i++) {
          if (this.cursor.row > 0) this.cursor.row--;
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

      // Operators
      case 'd': this._pendingOp = 'd'; this._opStartPos = { ...this.cursor }; return;
      case 'c': this._pendingOp = 'c'; this._opStartPos = { ...this.cursor }; return;
      case 'y': this._pendingOp = 'y'; this._opStartPos = { ...this.cursor }; return;
      case '>': this._pendingOp = '>'; this._opStartPos = { ...this.cursor }; return;
      case '<': this._pendingOp = '<'; this._opStartPos = { ...this.cursor }; return;

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
        this._setReg(line.slice(this.cursor.col), 'char');
        break;
      }

      // p P
      case 'p': {
        const count = this._getCount();
        const explicitReg = this._pendingRegKey;
        const reg = this._getReg();
        if (explicitReg && !reg.text) {
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
        if (explicitReg && !reg.text) {
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
        const oIndent = this.buffer.lines[this.cursor.row].match(/^[ \t]*/)[0];
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
        const OIndent = this.buffer.lines[this.cursor.row].match(/^[ \t]*/)[0];
        this.buffer.insertLineBefore(this.cursor.row);
        this.buffer.lines[this.cursor.row] = OIndent;
        this.cursor.col = OIndent.length;
        this.mode = Mode.INSERT; this.commandLine = '-- INSERT --';
        break;
      }

      // Undo/Redo
      case 'u': { const c = this._getCount(); for (let i = 0; i < c; i++) this._undo(); break; }
      case 'Ctrl-R': { const c = this._getCount(); for (let i = 0; i < c; i++) this._redo(); break; }

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
      case 'n': { this._addJumpEntry(); const c = this._getCount(); for (let i = 0; i < c; i++) this._searchNext(this._searchForward); this._showCurSearch = true; this._hlsearchActive = true; break; }
      case 'N': { this._addJumpEntry(); const c = this._getCount(); for (let i = 0; i < c; i++) this._searchNext(!this._searchForward); this._showCurSearch = true; this._hlsearchActive = true; break; }
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
        }
        this._pendingCount = '';
        break;
      }

      // File info
      case 'Ctrl-G': {
        const name = this.filename || '[No Name]';
        const total = this.buffer.lineCount;
        let bytes = 0;
        for (let i = 0; i < total; i++) bytes += this.buffer.lines[i].length + (i < total - 1 ? 1 : 0);
        this.commandLine = `"${name}" ${total}L, ${bytes}B`;
        this._stickyCommandLine = true;
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
            // Save current position before jumping back
            this._jumpList.push({ row: this.cursor.row, col: this.cursor.col });
            this._jumpListPos = this._jumpList.length - 1;
          }
          this._jumpListPos--;
          const entry = this._jumpList[this._jumpListPos];
          this.cursor.row = Math.min(entry.row, this.buffer.lineCount - 1);
          this.cursor.col = Math.min(entry.col, this._maxCol());
          this._updateDesiredCol();
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
        if (line.length === 0) {
          this.commandLine = 'NUL';
        } else {
          const ch = line[this.cursor.col] || line[line.length - 1];
          const code = ch.charCodeAt(0);
          const dec = code;
          const hex = code.toString(16);
          const oct = code.toString(8);
          const display = code < 32 ? '^' + String.fromCharCode(code + 64) : ch;
          this.commandLine = `<${display}>  ${dec},  Hex ${hex.padStart(2, '0')},  Oct ${oct.padStart(3, '0')}`;
        }
        this._stickyCommandLine = true;
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
      default:
        this._pendingCount = '';
        break;
    }
  }

  // ── z prefix ──

  _handleZ(key) {
    const maxST = Math.max(0, this.buffer.lineCount - 1);
    switch (key) {
      case 'z':
        this.scrollTop = Math.max(0, Math.min(this.cursor.row - Math.floor((this._textRows - 1) / 2), maxST));
        this.cursor.col = this._firstNonBlank(this.cursor.row);
        this._updateDesiredCol();
        break;
      case 't':
        this.scrollTop = Math.max(0, Math.min(this.cursor.row, maxST));
        this.cursor.col = this._firstNonBlank(this.cursor.row);
        this._updateDesiredCol();
        break;
      case 'b':
        this.scrollTop = Math.max(0, Math.min(this.cursor.row - this._textRows + 1, maxST));
        this.cursor.col = this._firstNonBlank(this.cursor.row);
        this._updateDesiredCol();
        break;
    }
  }

  // ── Command (Ex) mode ──

  _commandKey(key) {
    if (key === 'Escape') {
      this.mode = Mode.NORMAL; this.commandLine = '';
      this._pendingOpForSearch = '';
      this._opStartPosForSearch = null;
      this._visualCmdRange = null;
      return;
    }
    if (key === 'Enter') { this._executeCommand(); return; }
    if (key === 'Backspace') {
      if (this._searchInput.length > 0) {
        this._searchInput = this._searchInput.slice(0, -1);
        this.commandLine = this.commandLine[0] + this._searchInput;
      } else {
        this.mode = Mode.NORMAL; this.commandLine = '';
        this._visualCmdRange = null;
      }
      return;
    }
    if (key.length === 1) {
      this._searchInput += key;
      this.commandLine = this.commandLine[0] + this._searchInput;
    }
  }

  _executeCommand() {
    const prefix = this.commandLine[0];
    const cmd = this._searchInput.trim();
    this.mode = Mode.NORMAL;

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

    // : commands — file/quit operations (with nvim-style abbreviations)
    // :w[rite], :wq, :x[it], :q[uit], :q[uit]!, :e[dit], :r[ead], :!
    // Set _lastExCommand so SessionManager can intercept; clear commandLine.
    if (/^(w(r(i(te?)?)?)?|wq|x(it?)?|q(u(it?)?)?!?)(\s|$)/.test(cmd) || /^e(d(it?)?)?!?(\s|$)/.test(cmd) || /^r(e(ad?)?)?!/.test(cmd) || /^r(e(ad?)?)?(\s|$)/.test(cmd) || cmd.startsWith('!')) {
      this._lastExCommand = cmd;
      this.commandLine = '';
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

    // :sort — sort lines in buffer or visual range
    const sortMatch = cmd.match(/^(?:'<,'>\s*)?sort(!)?\s*(.*)?$/);
    if (sortMatch) {
      const bang = !!sortMatch[1];  // :sort! = reverse
      const flags = (sortMatch[2] || '').trim();
      let reverse = bang;
      let numeric = false;
      let unique = false;
      let ignoreCase = false;
      // Parse flags: n=numeric, i=ignore-case, u=unique
      for (const ch of flags) {
        if (ch === 'n') numeric = true;
        else if (ch === 'i') ignoreCase = true;
        else if (ch === 'u') unique = true;
      }
      // Determine range
      let sr = 0, er = this.buffer.lineCount - 1;
      if (this._visualCmdRange) {
        sr = this._visualCmdRange.start;
        er = this._visualCmdRange.end;
        this._visualCmdRange = null;
      }
      // Extract lines to sort
      const slice = this.buffer.lines.slice(sr, er + 1);
      // Sort
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
      // Replace lines in buffer
      this._saveSnapshot();
      this._redoStack = [];
      this.buffer.lines.splice(sr, er - sr + 1, ...slice);
      // Position cursor at start of sorted range
      this.cursor.row = sr;
      this.cursor.col = this._firstNonBlank(sr);
      this._updateDesiredCol();
      const count = slice.length;
      this.commandLine = `${count} line${count !== 1 ? 's' : ''} sorted`;
      this._stickyCommandLine = true;
      return;
    }
    // Clear visual range if it wasn't consumed
    this._visualCmdRange = null;

    let targetLine = -1;
    if (cmd === '$') {
      targetLine = this.buffer.lineCount - 1;
    } else {
      const lineNum = parseInt(cmd, 10);
      if (!isNaN(lineNum)) targetLine = Math.max(0, Math.min(lineNum - 1, this.buffer.lineCount - 1));
    }
    if (targetLine >= 0) {
      this.cursor.row = targetLine;
      this.cursor.col = this._firstNonBlank(this.cursor.row);
      // Neovim-style scroll: center when jump distance is large
      const half = Math.floor((this._textRows - 1) / 2);
      if (this.cursor.row < this.scrollTop) {
        // Cursor above viewport
        const dist = this.scrollTop - this.cursor.row;
        if (dist >= half) {
          // Center
          this.scrollTop = Math.max(0, this.cursor.row - half);
        } else {
          this.scrollTop = this.cursor.row;
        }
      } else if (this.cursor.row >= this.scrollTop + this._textRows) {
        // Cursor below viewport
        const dist = this.cursor.row - (this.scrollTop + this._textRows - 1);
        if (dist >= half) {
          // Center
          const maxST = Math.max(0, this.buffer.lineCount - this._textRows);
          this.scrollTop = Math.min(this.cursor.row - half, maxST);
        } else {
          this.scrollTop = this.cursor.row - this._textRows + 1;
        }
      }
    }
    this.commandLine = '';
  }

  /** Handle :set commands */
  _executeSet(cmd) {
    // Parse: "set option" or "set nooption" or "set option=value"
    const args = cmd.replace(/^set?\s*/, '').split(/\s+/);
    for (const arg of args) {
      if (!arg) continue;
      // Boolean options: :set option / :set nooption
      const noMatch = arg.match(/^no(.+)$/);
      if (noMatch) {
        const opt = noMatch[1];
        if (opt in this._settings && typeof this._settings[opt] === 'boolean') {
          this._settings[opt] = false;
        }
        // Handle short forms
        else if (opt === 'nu') this._settings.number = false;
        else if (opt === 'rnu') this._settings.relativenumber = false;
        continue;
      }
      // Handle short forms for enabling
      if (arg === 'nu') { this._settings.number = true; continue; }
      if (arg === 'rnu') { this._settings.relativenumber = true; continue; }
      // Direct boolean enable
      if (arg in this._settings && typeof this._settings[arg] === 'boolean') {
        this._settings[arg] = true;
        continue;
      }
    }
  }

  // ── Insert mode ──

  _insertKey(key) {
    // Pending Ctrl-R: next key is register name, paste register contents
    if (this._pendingCtrlR) {
      this._pendingCtrlR = false;
      this._saveForDot(key);
      let regText = '';
      if (/^[a-zA-Z0-9]$/.test(key)) {
        const rk = key.toLowerCase();
        const r = this._namedRegs[rk];
        regText = r ? r.text : '';
      } else if (key === '"') {
        regText = this._unnamedReg || '';
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
        // Save cursor position before adjusting for gi
        this._lastInsertPos = { row: this.cursor.row, col: this.cursor.col };
        this.mode = Mode.NORMAL; this.commandLine = '';
        if (this.cursor.col > 0) this.cursor.col--;
        this._stopRecording(); this._redoStack = [];
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

    // Pending register selection ("x)
    if (this._pendingDblQuote) {
      this._pendingDblQuote = false;
      if (/^[a-zA-Z0-9]$/.test(key)) {
        this._pendingRegKey = key.toLowerCase();
      }
      return;
    }

    if (key === '"') {
      this._pendingDblQuote = true;
      return;
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
      } else { this.mode = Mode.VISUAL; this.commandLine = '-- VISUAL --'; }
      this._pendingCount = ''; return;
    }
    if (key === 'V') {
      if (this.mode === Mode.VISUAL_LINE) {
        this._lastVisual = { mode: this.mode, start: { ...this._visualStart }, end: { ...this.cursor } };
        this.mode = Mode.NORMAL; this.commandLine = '';
      } else { this.mode = Mode.VISUAL_LINE; this.commandLine = '-- VISUAL LINE --'; }
      this._pendingCount = ''; return;
    }
    if (key === 'o' || key === 'O') {
      const t = { ...this._visualStart };
      this._visualStart = { ...this.cursor };
      this.cursor = t;
      this._pendingCount = ''; return;
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

    // Actions
    const actionKeys = new Set(['d','c','y','>','<','~','U','u','J','p','x','s','r','Delete']);
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
          this._setReg(y, 'line');
        } else {
          this._setReg(this._extractRange(sr, sc, er, ec), 'char');
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
        if (this.mode === Mode.VISUAL || this.mode === Mode.VISUAL_LINE) {
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
          this._setReg(y, 'line');
        } else {
          this._setReg(this.buffer.lines[sr].slice(sc, ecSlice), 'char');
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
      const re = new RegExp(this._searchPattern);
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
          this._setReg(y, 'line');
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
        if (range.multilineInner) {
          // ci( / ci{ multiline: replace inner lines with indented blank line
          const indent = this.buffer.lines[startRow].match(/^(\s*)/)[1];
          // Remove all inner lines and insert blank indented line
          this.buffer.lines.splice(startRow, endRow - startRow, indent);
          this.cursor.row = startRow; this.cursor.col = indent.length;
        } else if (startRow !== endRow) {
          this._deleteRange(startRow, startCol, endRow, endCol - 1);
          this.cursor.row = startRow; this.cursor.col = startCol;
        } else {
          const l = this.buffer.lines[startRow];
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
          this._setReg(y, 'char');
        } else {
          this._setReg(this.buffer.lines[startRow].slice(startCol, endCol), 'char');
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
        this._setReg(y, 'line');
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

  _searchNext(forward) {
    if (!this._searchPattern) return false;
    let pattern;
    try { pattern = new RegExp(this._searchPattern); } catch { return false; }
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
        const re = new RegExp(this._searchPattern, 'g');
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

  // ── Put (paste) ──

  _putAfter(reg) {
    const text = reg ? reg.text : this._unnamedReg;
    const type = reg ? reg.type : this._regType;
    if (text == null) return;
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
    if ((this.mode === Mode.VISUAL || this.mode === Mode.VISUAL_LINE) && this._desiredCol === Infinity) {
      const len = this.buffer.lineLength(this.cursor.row);
      if (this.cursor.col > len) this.cursor.col = len;
    } else {
      if (this.cursor.col > max) this.cursor.col = max;
    }
  }

  _ensureCursorVisible() {
    if (this.cursor.row < this.scrollTop) this.scrollTop = this.cursor.row;
    if (this.cursor.row >= this.scrollTop + this._textRows) this.scrollTop = this.cursor.row - this._textRows + 1;
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
    const sw = 8;
    // Compute current indent in virtual columns
    let indent = 0;
    let i = 0;
    while (i < line.length && (line[i] === ' ' || line[i] === '\t')) {
      if (line[i] === '\t') indent += sw - (indent % sw);
      else indent++;
      i++;
    }
    const text = line.slice(i);
    const newIndent = indent + sw;
    // With noexpandtab and tabstop=8: convert to tabs + spaces
    const tabs = Math.floor(newIndent / sw);
    const spaces = newIndent % sw;
    this.buffer.lines[row] = '\t'.repeat(tabs) + ' '.repeat(spaces) + text;
  }

  /**
   * Shift (dedent) a single line left by shiftwidth.
   * Computes current indent, subtracts sw (clamped to 0), rebuilds with tabs+spaces.
   * Skips empty lines.
   */
  _shiftLineLeft(row) {
    const line = this.buffer.lines[row];
    if (line.length === 0) return; // skip empty lines
    const sw = 8;
    // Compute current indent in virtual columns
    let indent = 0;
    let i = 0;
    while (i < line.length && (line[i] === ' ' || line[i] === '\t')) {
      if (line[i] === '\t') indent += sw - (indent % sw);
      else indent++;
      i++;
    }
    if (indent === 0) return; // nothing to dedent
    const text = line.slice(i);
    const newIndent = Math.max(0, indent - sw);
    const tabs = Math.floor(newIndent / sw);
    const spaces = newIndent % sw;
    this.buffer.lines[row] = '\t'.repeat(tabs) + ' '.repeat(spaces) + text;
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

  // ── Jump list ──

  _addJumpEntry() {
    const entry = { row: this.cursor.row, col: this.cursor.col };
    // Don't add duplicate of top entry
    if (this._jumpList.length > 0) {
      const last = this._jumpList[this._jumpList.length - 1];
      if (last.row === entry.row && last.col === entry.col) return;
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

  _updateStatus() {
    const r = this.cursor.row + 1, c = this.cursor.col + 1, total = this.buffer.lineCount;
    const pos = `${r},${c}`;
    const pct = total <= 1 ? 'All' : r === 1 ? 'Top' : r === total ? 'Bot' : `${Math.round((r / total) * 100)}%`;
    const right = `${pos}          ${pct}`;
    this.statusLine = ' '.repeat(Math.max(0, this.cols - right.length)) + right;
    if (this.mode === Mode.INSERT) this.commandLine = '-- INSERT --';
    else if (this.mode === Mode.REPLACE) this.commandLine = '-- REPLACE --';
    else if (this.mode === Mode.VISUAL) this.commandLine = '-- VISUAL --';
    else if (this.mode === Mode.VISUAL_LINE) this.commandLine = '-- VISUAL LINE --';
    else if (this.mode === Mode.NORMAL && this._macroRecording) {
      this.commandLine = 'recording @' + this._macroRecording;
    } else if (this.mode === Mode.NORMAL && !this._stickyCommandLine) {
      this.commandLine = '';
    }
  }
}
