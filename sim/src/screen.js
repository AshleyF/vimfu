/**
 * VimFu Simulator – Screen
 *
 * Produces a Frame dict that matches the project's frame_format.md spec.
 * This is the bridge between the engine model and any renderer (HTML, GIF,
 * or the ground-truth comparison tests).
 *
 * Frame format:
 *   { rows, cols, cursor: {row, col, visible},
 *     defaultFg, defaultBg,
 *     lines: [ { text, runs: [{n, fg, bg, ...}] } ] }
 */

import { SyntaxHighlighter, grammarForFile, scopeToColor } from './highlight.js';

// Ensure built-in grammars are registered
import './langs/python.js';
import './langs/markdown.js';

// ── Theme palettes ──────────────────────────────────────────
// Each theme defines the fixed colours for every UI element.
// The 'nvim_default' theme matches `nvim -u NONE` (Neovim 0.10+ default).
// The 'monokai' theme matches the Monokai config used in the GIFs/book.

const THEMES = {
  nvim_default: {
    // Text area
    normalFg: 'e0e2ea',
    normalBg: '14161b',
    // Tilde (~) lines past end-of-buffer
    tildeFg: '4f5258',
    tildeBg: '14161b',
    // Status line
    statusFg: '2c2e33',
    statusBg: 'c4c6cd',
    // Command / message line
    cmdFg: 'e0e2ea',
    cmdBg: '14161b',
    // Recording indicator
    recordingFg: 'b3f6c0',
    // Mode indicator (-- INSERT --, -- VISUAL --, etc.)
    modeMsgFg: 'b3f6c0',
    // Visual selection (bg-only; fg keeps its current colour)
    visualBg: '4f5258',
    // Search highlights
    searchFg: 'eef1f8',
    searchBg: '6b5300',
    curSearchFg: '07080d',
    curSearchBg: 'fce094',
    // Error and prompt colors
    errorFg: 'ffc0b9',
    promptFg: '8cf8f7',
    // Line numbers
    lineNrFg: '4f5258',       // LineNr (dark grey)
    cursorLineNrFg: 'e0e2ea', // CursorLineNr (bright white)
    // MatchParen – default nvim uses bold+underline only (no fg change)
    matchParenFg: null,
    // Syntax highlighting – verified against nvim -u NONE + syntax on + termguicolors
    syntax: {
      comment: '9b9ea4',        // Comment           (NvimDarkGrey4)
      string: 'b3f6c0',         // String            (NvimDarkGreen)
      constant: '8cf8f7',       // True/False/None   (NvimDarkCyan)
      decorator: '8cf8f7',      // decorator name    (NvimDarkCyan)
      'function.def': '8cf8f7', // def name          (NvimDarkCyan)
      'class.def': '8cf8f7',    // class name        (NvimDarkCyan)
      builtin: '8cf8f7',        // print, len, str…  (NvimDarkCyan)
      special: '8cf8f7',        // __init__ etc      (NvimDarkCyan)
      // NOT highlighted in nvim default: number, keyword, keyword.import, operator
      // Markdown scopes – verified against nvim -u NONE + treesitter
      heading: '8cf8f7',        // Title             (NvimDarkCyan)
      code: 'b3f6c0',           // String            (NvimDarkGreen)
      'code.block': 'b3f6c0',   // String            (NvimDarkGreen)
      'list.marker': '8cf8f7',  // @markup.list      (NvimDarkCyan)
      link: '8cf8f7',           // @markup.link      (NvimDarkCyan)
      'link.url': '9b9ea4',     // Comment-like      (NvimDarkGrey4)
      blockquote: '9b9ea4',     // @markup.quote     (grey)
      hr: '8cf8f7',             // Special           (NvimDarkCyan)
    },
  },
  monokai: {
    // Verified against tanvirtin/monokai.nvim with bg override to #000000
    normalFg: 'd4d4d4',
    normalBg: '000000',
    tildeFg: '000000',          // EndOfBuffer – hidden (black on black)
    tildeBg: '000000',
    statusFg: 'b1b1b1',
    statusBg: '2e323c',
    cmdFg: 'd4d4d4',
    cmdBg: '000000',
    recordingFg: 'f8f8f0',     // ModeMsg
    modeMsgFg: 'f8f8f0',       // ModeMsg
    visualBg: '333842',
    searchFg: '26292c',
    searchBg: 'e6db74',
    curSearchFg: '07080d',     // CurSearch
    curSearchBg: 'fce094',     // CurSearch
    errorFg: 'e95678',         // ErrorMsg
    promptFg: 'f8f8f0',        // MoreMsg
    // Line numbers
    lineNrFg: 'd4d4d4',          // LineNr (fg=default → terminal default)
    cursorLineNrFg: 'fd971f',    // CursorLineNr (orange)
    matchParenFg: 'f92672',        // MatchParen (pink)
    // Syntax highlighting – tanvirtin/monokai.nvim palette
    syntax: {
      comment: '9ca0a4',         // Comment
      string: 'e6db74',          // String (yellow)
      number: 'ae81ff',          // Number (purple)
      constant: 'ae81ff',        // Boolean (purple) – True/False/None
      keyword: 'f92672',         // Keyword (pink)
      'keyword.import': 'f92672', // Keyword (pink)
      decorator: 'e6db74',       // String (yellow)
      'function.def': 'a6e22e',  // Function (green)
      'class.def': 'a6e22e',     // Function (green)
      builtin: '66d9ef',         // Type/Constant (blue)
      operator: 'f92672',        // Operator (pink)
      special: 'f8f8f0',         // Special (white)
      // Markdown scopes – monokai palette
      heading: 'a6e22e',         // Title (green)
      code: 'e6db74',            // String (yellow)
      'code.block': 'e6db74',    // String (yellow)
      'list.marker': 'f92672',   // Keyword (pink)
      link: '66d9ef',            // Type (blue)
      'link.url': '9ca0a4',      // Comment (grey)
      blockquote: '9ca0a4',      // Comment (grey)
      hr: 'f92672',              // Keyword (pink)
    },
  },
};

// Backwards-compat exports (used by a few external callers)
const DEFAULT_FG = 'd4d4d4';
const DEFAULT_BG = '000000';

export class Screen {
  /**
   * @param {number} rows – total screen rows (including status line)
   * @param {number} cols – screen width in columns
   * @param {string} [themeName='monokai'] – colour theme to use
   */
  constructor(rows = 20, cols = 40, themeName = 'monokai') {
    this.rows = rows;
    this.cols = cols;
    this.theme = THEMES[themeName] || THEMES.monokai;
  }

  /**
   * Build a Frame dict from the engine state.
   *
   * @param {import('./engine.js').VimEngine} engine
   * @returns {object} Frame dict per frame_format.md
   */
  render(engine) {
    const t = this.theme;
    const buf = engine.buffer;
    const cursor = engine.cursor;
    const mode = engine.mode;

    // Neovim uses rows-2 for the text area (1 status, 1 command/msg line)
    const textRows = this.rows - 2;
    const lines = [];

    // Compute the viewport window (scroll offset)
    const scrollTop = engine.scrollTop ?? 0;

    // ── Compute visual selection range (in buffer coordinates) ──
    let visSR = -1, visSC = -1, visER = -1, visEC = -1;
    let visMode = null; // 'char' | 'line' | null
    if (mode === 'visual' || mode === 'visual_line') {
      const vs = engine._visualStart;
      const vc = cursor;
      if (mode === 'visual_line') {
        visMode = 'line';
        visSR = Math.min(vs.row, vc.row);
        visER = Math.max(vs.row, vc.row);
      } else {
        visMode = 'char';
        if (vs.row < vc.row || (vs.row === vc.row && vs.col <= vc.col)) {
          visSR = vs.row; visSC = vs.col;
          visER = vc.row; visEC = vc.col;
        } else {
          visSR = vc.row; visSC = vc.col;
          visER = vs.row; visEC = vs.col;
        }
        // Exclusive visual motions: the cursor char is NOT highlighted
        if (engine._visualExclusive) {
          const cursorAtEnd = (vc.row === visER && vc.col === visEC);
          const cursorAtStart = (vc.row === visSR && vc.col === visSC);
          if (cursorAtEnd && visEC > visSC) {
            visEC--;
          } else if (cursorAtStart && visSC < visEC) {
            visSC++;
          }
        }
      }
    } else if (mode === 'command' && engine._visualCmdRange) {
      // Keep visual highlight visible while typing :'<,'> commands
      const vcr = engine._visualCmdRange;
      if (vcr.visMode === 'visual_line') {
        visMode = 'line';
        visSR = vcr.start;
        visER = vcr.end;
      } else {
        visMode = 'char';
        const vs = vcr.visStart;
        const vc = vcr.visEnd;
        if (vs.row < vc.row || (vs.row === vc.row && vs.col <= vc.col)) {
          visSR = vs.row; visSC = vs.col;
          visER = vc.row; visEC = vc.col;
        } else {
          visSR = vc.row; visSC = vc.col;
          visER = vs.row; visEC = vs.col;
        }
      }
    }

    // ── Compute search matches on visible lines ──
    let searchRegex = null;
    if (engine._searchPattern && engine._hlsearchActive) {
      try { searchRegex = new RegExp(engine._searchPattern, 'g'); } catch (e) { /* bad regex */ }
    }

    // ── Syntax highlighting setup ──
    let syntaxTokens = null; // array indexed by bufRow → token array
    const grammar = grammarForFile(engine.filename);
    if (grammar && t.syntax) {
      const hl = new SyntaxHighlighter(grammar);
      // Tokenize all lines through the end of the buffer so multi-line
      // state is propagated correctly.
      const allLines = buf.lines.slice(0, buf.lineCount);
      const result = hl.tokenizeLines(allLines);
      syntaxTokens = result.tokens;
    }

    // ── MatchParen highlight setup ──
    // Neovim highlights the bracket under the cursor and its matching pair.
    let matchParenA = null; // bracket under cursor {row, col}
    let matchParenB = null; // matching bracket    {row, col}
    if (t.matchParenFg && (mode === 'normal' || mode === 'visual' || mode === 'visual_line' || mode === 'insert')) {
      const curLine = buf.lines[cursor.row] || '';
      const ch = curLine[cursor.col];
      if (ch && '([{)]}'.includes(ch)) {
        matchParenB = this._findMatchingBracket(buf, cursor.row, cursor.col, ch);
        if (matchParenB) {
          matchParenA = { row: cursor.row, col: cursor.col };
        }
      }
    }

    // ── Line number gutter computation ──
    const showNumber = engine._settings?.number ?? false;
    const showRelNumber = engine._settings?.relativenumber ?? false;
    const showGutter = showNumber || showRelNumber;
    // Gutter width: match nvim — default numberwidth=4, expands for large files
    let gutterWidth = 0;
    if (showGutter) {
      const maxLineNum = buf.lineCount;
      const numDigits = String(maxLineNum).length;
      gutterWidth = Math.max(4, numDigits + 1); // nvim default numberwidth=4
    }
    const textCols = this.cols - gutterWidth; // available columns for text

    // ── Helper: expand a raw buffer line into screen text and mappings ──
    const expandLine = (raw) => {
      let expanded = '';
      const bufToScreen = [];
      for (let i = 0; i < raw.length; i++) {
        bufToScreen[i] = expanded.length;
        if (raw[i] === '\t') {
          const spaces = 8 - (expanded.length % 8);
          expanded += ' '.repeat(spaces);
        } else {
          expanded += raw[i];
        }
      }
      bufToScreen[raw.length] = expanded.length; // sentinel
      return { expanded, bufToScreen };
    };

    // ── Helper: how many screen rows does a buffer line consume? ──
    const wrapRows = (expanded) => expanded.length === 0 ? 1 : Math.ceil(expanded.length / textCols);

    // ── Adjust scrollTop so cursor is on-screen (accounting for wrapping) ──
    // scrollTop is in buffer rows. We need to ensure the cursor's wrapped
    // screen row falls within the visible textRows.
    let scrollTopAdj = scrollTop;
    {
      // First ensure the cursor's buffer row is at or below scrollTop
      if (cursor.row < scrollTopAdj) scrollTopAdj = cursor.row;

      // Compute screen rows consumed from scrollTop to the cursor's row
      // and check if the cursor's wrapped position fits within textRows.
      let usedRows = 0;
      for (let br = scrollTopAdj; br < cursor.row && br < buf.lineCount; br++) {
        const { expanded } = expandLine(buf.lines[br]);
        usedRows += wrapRows(expanded);
      }
      // Add the cursor's own row offset within its wrapped line
      if (cursor.row < buf.lineCount) {
        const { expanded, bufToScreen } = expandLine(buf.lines[cursor.row]);
        const cursorVirtCol = bufToScreen[Math.min(cursor.col, buf.lines[cursor.row].length)] ?? 0;
        const cursorWrapRow = Math.floor(cursorVirtCol / textCols);
        usedRows += cursorWrapRow;

        // If cursor row is past the visible area, scroll down
        while (usedRows >= textRows && scrollTopAdj < cursor.row) {
          const { expanded: topExpanded } = expandLine(buf.lines[scrollTopAdj]);
          usedRows -= wrapRows(topExpanded);
          scrollTopAdj++;
        }
        // Edge case: cursor's own wrapped line is taller than the screen
        // (scrollTopAdj === cursor.row but cursorWrapRow >= textRows).
        // In this case nvim would show the portion that contains the cursor.
        // We handle this in rendering by starting from the right wrap offset.
      }
    }
    // Update the engine's scrollTop so it stays in sync
    engine.scrollTop = scrollTopAdj;

    // ── Text area (with wrapping) ──
    let screenRow = 0;       // current screen row being filled
    let bufRow = scrollTopAdj;
    let cursorScreenRow = -1;
    let cursorScreenCol = -1;

    while (screenRow < textRows && bufRow < buf.lineCount) {
      const raw = buf.lines[bufRow];
      const { expanded, bufToScreen } = expandLine(raw);
      const numWraps = wrapRows(expanded);

      for (let wrapIdx = 0; wrapIdx < numWraps && screenRow < textRows; wrapIdx++) {
        const sliceStart = wrapIdx * textCols;
        const sliceEnd = Math.min(sliceStart + textCols, expanded.length);
        const sliceText = expanded.slice(sliceStart, sliceEnd);
        const bodyText = sliceText.length >= textCols
          ? sliceText
          : sliceText + ' '.repeat(textCols - sliceText.length);

        // Build per-column colour arrays for this screen row
        const colFg = new Array(textCols).fill(t.normalFg);
        const colBg = new Array(textCols).fill(t.normalBg);

        // Apply syntax highlighting (base layer)
        if (syntaxTokens && syntaxTokens[bufRow]) {
          for (const tok of syntaxTokens[bufRow]) {
            const color = scopeToColor(tok.scope, t.syntax);
            if (!color) continue;
            const scrStart = bufToScreen[tok.start] ?? tok.start;
            const scrEnd = (bufToScreen[tok.end] ?? tok.end) - 1;
            // Map to this wrap slice
            for (let sc = Math.max(scrStart, sliceStart); sc <= Math.min(scrEnd, sliceEnd - 1); sc++) {
              colFg[sc - sliceStart] = color;
            }
          }
        }

        // Apply visual highlight
        if (visMode) {
          let hlStart = -1, hlEnd = -1; // in expanded-string coords (absolute)
          if (visMode === 'line') {
            if (bufRow >= visSR && bufRow <= visER) {
              hlStart = sliceStart;
              hlEnd = sliceStart + textCols - 1;
            }
          } else { // char
            if (bufRow >= visSR && bufRow <= visER) {
              if (visSR === visER) {
                hlStart = bufToScreen[visSC] ?? 0;
                hlEnd = (visSC <= visEC && visEC < raw.length)
                  ? (bufToScreen[visEC + 1] ?? expanded.length) - 1
                  : (bufToScreen[visEC] ?? expanded.length - 1);
                if (visEC >= raw.length) hlEnd = expanded.length - 1;
                hlEnd = Math.max(hlStart, hlEnd);
              } else if (bufRow === visSR) {
                hlStart = bufToScreen[visSC] ?? 0;
                hlEnd = Math.max(expanded.length - 1, hlStart);
              } else if (bufRow === visER) {
                hlStart = 0;
                hlEnd = (visEC < raw.length)
                  ? (bufToScreen[visEC + 1] ?? expanded.length) - 1
                  : expanded.length - 1;
                hlEnd = Math.max(0, hlEnd);
              } else {
                hlStart = 0;
                hlEnd = Math.max(expanded.length - 1, 0);
              }
            }
          }

          if (hlStart >= 0 && hlEnd >= hlStart) {
            // Clamp to this wrap slice
            const cStart = Math.max(hlStart, sliceStart) - sliceStart;
            const cEnd = Math.min(hlEnd, sliceStart + textCols - 1) - sliceStart;
            for (let c = cStart; c <= cEnd; c++) {
              colBg[c] = t.visualBg;
            }
          }
        }

        // Apply search highlights
        if (searchRegex) {
          searchRegex.lastIndex = 0;
          let m;
          while ((m = searchRegex.exec(raw)) !== null) {
            if (m[0].length === 0) { searchRegex.lastIndex++; continue; }
            const matchStart = bufToScreen[m.index] ?? 0;
            const matchEnd = (bufToScreen[m.index + m[0].length] ?? expanded.length) - 1;
            const csp = engine._curSearchPos;
            const isCursorMatch = engine._showCurSearch && csp
              && bufRow === csp.row
              && m.index === csp.col;
            const sFg = isCursorMatch ? t.curSearchFg : t.searchFg;
            const sBg = isCursorMatch ? t.curSearchBg : t.searchBg;
            for (let sc = Math.max(matchStart, sliceStart); sc <= Math.min(matchEnd, sliceEnd - 1); sc++) {
              colFg[sc - sliceStart] = sFg;
              colBg[sc - sliceStart] = sBg;
            }
          }
        }

        // Apply MatchParen highlight (fg-only, preserves bg)
        if (matchParenA || matchParenB) {
          for (const mp of [matchParenA, matchParenB]) {
            if (mp && mp.row === bufRow) {
              const scrCol = bufToScreen[mp.col] ?? 0;
              if (scrCol >= sliceStart && scrCol < sliceEnd) {
                colFg[scrCol - sliceStart] = t.matchParenFg;
              }
            }
          }
        }

        // Build gutter
        let gutterText = '';
        const gutterRuns = [];
        if (showGutter) {
          if (wrapIdx === 0) {
            // First wrapped row gets the line number
            const isCursorLine = (bufRow === cursor.row);
            let numStr;
            if (showNumber && showRelNumber) {
              if (isCursorLine) {
                numStr = String(bufRow + 1);
                gutterText = numStr + ' '.repeat(gutterWidth - numStr.length);
              } else {
                numStr = String(Math.abs(bufRow - cursor.row));
                gutterText = numStr.padStart(gutterWidth - 1) + ' ';
              }
            } else if (showRelNumber) {
              numStr = isCursorLine ? '0' : String(Math.abs(bufRow - cursor.row));
              gutterText = numStr.padStart(gutterWidth - 1) + ' ';
            } else {
              numStr = String(bufRow + 1);
              gutterText = numStr.padStart(gutterWidth - 1) + ' ';
            }
          } else {
            // Continuation wrapped rows: blank gutter
            gutterText = ' '.repeat(gutterWidth);
          }
          const nrFg = t.lineNrFg || t.normalFg;
          gutterRuns.push({ n: gutterWidth, fg: nrFg, bg: t.normalBg });
        }

        // Compress colour arrays into runs
        const textRuns = [];
        let runStart = 0;
        for (let c = 1; c <= textCols; c++) {
          if (c === textCols || colFg[c] !== colFg[runStart] || colBg[c] !== colBg[runStart]) {
            textRuns.push({ n: c - runStart, fg: colFg[runStart], bg: colBg[runStart] });
            runStart = c;
          }
        }

        const text = gutterText + bodyText;
        const runs = [...gutterRuns, ...textRuns];
        lines.push({ text, runs });

        // Track cursor screen position
        if (bufRow === cursor.row) {
          const cursorVirtCol = bufToScreen[Math.min(cursor.col, raw.length)] ?? 0;
          // When cursor is ON a tab character, nvim renders at the LAST
          // visual column of that tab (not the first).
          let adjustedVirtCol = cursorVirtCol;
          if (cursor.col < raw.length && raw[cursor.col] === '\t') {
            adjustedVirtCol += 8 - (cursorVirtCol % 8) - 1;
          }
          const cursorWrapRow = Math.floor(adjustedVirtCol / textCols);
          if (wrapIdx === cursorWrapRow) {
            cursorScreenRow = screenRow;
            cursorScreenCol = (adjustedVirtCol % textCols) + gutterWidth;
          }
        }

        screenRow++;
      }
      bufRow++;
    }

    // Fill remaining screen rows with tilde lines
    while (screenRow < textRows) {
      const tildeText = '~' + ' '.repeat(this.cols - 1);
      lines.push({
        text: tildeText,
        runs: [{ n: this.cols, fg: t.tildeFg, bg: t.tildeBg }],
      });
      screenRow++;
    }

    // ── Status line (row rows-2) ──
    const statusText = this._padOrTruncate(
      engine.statusLine ?? '',
      this.cols
    );
    lines.push({
      text: statusText,
      runs: [{ n: this.cols, fg: t.statusFg, bg: t.statusBg }],
    });

    // ── Command / message line (row rows-1) ──
    const cmdText = this._padOrTruncate(
      engine.commandLine ?? '',
      this.cols
    );
    // Recording indicator gets special color (green in nvim_default)
    if (t.recordingFg && engine._macroRecording && engine.mode === 'normal'
        && (engine.commandLine ?? '').startsWith('recording @')) {
      const recLen = ('recording @' + engine._macroRecording).length;
      lines.push({
        text: cmdText,
        runs: [
          { n: recLen, fg: t.recordingFg, bg: t.cmdBg },
          { n: this.cols - recLen, fg: t.cmdFg, bg: t.cmdBg },
        ],
      });
    } else if (/^E\d{3}:/.test(engine.commandLine ?? '')) {
      // Error message in command line (red colored)
      const errLen = Math.min((engine.commandLine || '').length, this.cols);
      const errRuns = [];
      if (errLen > 0) errRuns.push({ n: errLen, fg: t.errorFg || t.cmdFg, bg: t.cmdBg });
      if (errLen < this.cols) errRuns.push({ n: this.cols - errLen, fg: t.cmdFg, bg: t.cmdBg });
      lines.push({ text: cmdText, runs: errRuns });
    } else if (t.modeMsgFg && /^-- (INSERT|VISUAL|VISUAL LINE|REPLACE) --$/.test((engine.commandLine ?? '').trim())) {
      // Mode indicator (ModeMsg) in green
      const modeLen = (engine.commandLine ?? '').replace(/\s+$/, '').length;
      lines.push({
        text: cmdText,
        runs: [
          { n: modeLen, fg: t.modeMsgFg, bg: t.cmdBg },
          { n: this.cols - modeLen, fg: t.cmdFg, bg: t.cmdBg },
        ],
      });
    } else {
      lines.push({
        text: cmdText,
        runs: [{ n: this.cols, fg: t.cmdFg, bg: t.cmdBg }],
      });
    }

    // ── Message prompt overlay ("Press ENTER or type command to continue") ──
    if (engine._messagePrompt) {
      const mp = engine._messagePrompt;
      const errRaw = mp.error || '';
      const prompt = 'Press ENTER or type command to continue';

      // Split error into physical lines: first split on \n, then wrap each
      // line to screen width (matching nvim's behavior).
      const errPhysical = [];
      for (const logicalLine of errRaw.split('\n')) {
        if (logicalLine.length <= this.cols) {
          errPhysical.push(logicalLine);
        } else {
          for (let i = 0; i < logicalLine.length; i += this.cols) {
            errPhysical.push(logicalLine.slice(i, i + this.cols));
          }
        }
      }

      // We need: 1 blank status-bar separator + N error lines + 1 prompt line.
      // Total overlay rows = errPhysical.length + 2 (separator + prompt).
      const overlayRows = errPhysical.length + 2;
      const startRow = this.rows - overlayRows;

      // Blank status-colored separator line
      if (startRow >= 0) {
        lines[startRow] = {
          text: ' '.repeat(this.cols),
          runs: [{ n: this.cols, fg: t.statusFg, bg: t.statusBg }],
        };
      }

      // Error message lines (red text)
      for (let i = 0; i < errPhysical.length; i++) {
        const row = startRow + 1 + i;
        if (row >= 0 && row < this.rows) {
          const errText = this._padOrTruncate(errPhysical[i], this.cols);
          const errLen = Math.min(errPhysical[i].length, this.cols);
          const runs = [];
          if (errLen > 0) runs.push({ n: errLen, fg: t.errorFg || t.cmdFg, bg: t.cmdBg });
          if (errLen < this.cols) runs.push({ n: this.cols - errLen, fg: t.cmdFg, bg: t.cmdBg });
          lines[row] = { text: errText, runs };
        }
      }

      // "Press ENTER..." prompt on the last row
      const promptRow = this.rows - 1;
      const promptText = this._padOrTruncate(prompt, this.cols);
      const promptLen = Math.min(prompt.length, this.cols);
      const promptRuns = [];
      if (promptLen > 0) promptRuns.push({ n: promptLen, fg: t.promptFg || t.cmdFg, bg: t.cmdBg });
      if (promptLen < this.cols) promptRuns.push({ n: this.cols - promptLen, fg: t.cmdFg, bg: t.cmdBg });
      lines[promptRow] = { text: promptText, runs: promptRuns };

      return {
        rows: this.rows,
        cols: this.cols,
        cursor: {
          row: this.rows - 1,
          col: this.cols - 1,
          visible: true,
        },
        defaultFg: t.normalFg,
        defaultBg: t.normalBg,
        lines,
      };
    }

    // Cursor position was computed during rendering (accounting for wrapping).
    return {
      rows: this.rows,
      cols: this.cols,
      cursor: {
        row: cursorScreenRow >= 0 ? cursorScreenRow : 0,
        col: cursorScreenCol >= 0 ? cursorScreenCol : gutterWidth,
        visible: true,
      },
      defaultFg: t.normalFg,
      defaultBg: t.normalBg,
      lines,
    };
  }

  /**
   * Render the frame as a flat array of text lines (no colors).
   * Useful for quick comparisons in tests.
   *
   * @param {import('./engine.js').VimEngine} engine
   * @returns {string[]}
   */
  renderText(engine) {
    const frame = this.render(engine);
    return frame.lines.map(l => l.text);
  }

  /**
   * Find the matching bracket for the character at (row, col).
   * @private
   * @returns {{row: number, col: number}|null}
   */
  _findMatchingBracket(buf, row, col, ch) {
    const PAIRS = { '(': ')', ')': '(', '[': ']', ']': '[', '{': '}', '}': '{' };
    const match = PAIRS[ch];
    if (!match) return null;
    const forward = '([{'.includes(ch);
    let depth = 1;
    if (forward) {
      let r = row, c = col + 1;
      while (r < buf.lineCount) {
        const line = buf.lines[r];
        while (c < line.length) {
          if (line[c] === ch) depth++;
          else if (line[c] === match) { depth--; if (depth === 0) return { row: r, col: c }; }
          c++;
        }
        r++; c = 0;
      }
    } else {
      let r = row, c = col - 1;
      while (r >= 0) {
        const line = buf.lines[r];
        while (c >= 0) {
          if (line[c] === ch) depth++;
          else if (line[c] === match) { depth--; if (depth === 0) return { row: r, col: c }; }
          c--;
        }
        r--; if (r >= 0) c = buf.lines[r].length - 1;
      }
    }
    return null;
  }

  /** @private */
  _padOrTruncate(s, width) {
    if (s.length >= width) return s.slice(0, width);
    return s + ' '.repeat(width - s.length);
  }
}

export { DEFAULT_FG, DEFAULT_BG };
