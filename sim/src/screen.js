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
    // Visual selection (bg-only; fg keeps its current colour)
    visualBg: '264f78',
    // Search highlights
    searchFg: 'eef1f8',
    searchBg: '6b5300',
    curSearchFg: '07080d',
    curSearchBg: 'fce094',
    // Error and prompt colors
    errorFg: 'ffc0b9',
    promptFg: '8cf8f7',
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
    },
  },
  monokai: {
    normalFg: 'd4d4d4',
    normalBg: '000000',
    tildeFg: '5c5cff',
    tildeBg: '000000',
    statusFg: 'b1b1b1',
    statusBg: '2e323c',
    cmdFg: 'd4d4d4',
    cmdBg: '000000',
    recordingFg: '00ff00',
    visualBg: '333842',
    searchFg: '26292c',
    searchBg: 'e6db74',
    curSearchFg: '26292c',
    curSearchBg: 'fd971f',
    errorFg: 'ff6188',
    promptFg: '78dce8',
    // Syntax highlighting – Monokai palette
    syntax: {
      comment: '88846f',         // gray/olive
      string: 'e6db74',          // yellow
      number: 'ae81ff',          // purple
      constant: 'ae81ff',        // purple
      keyword: 'f92672',         // pink
      'keyword.import': 'f92672', // pink
      decorator: 'e6db74',       // yellow
      'function.def': 'a6e22e',  // green
      'class.def': 'a6e22e',     // green
      builtin: '66d9ef',         // blue
      operator: 'f92672',        // pink
      special: 'fd971f',         // orange
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
      }
    }

    // ── Compute search matches on visible lines ──
    let searchRegex = null;
    if (engine._searchPattern) {
      try { searchRegex = new RegExp(engine._searchPattern, 'gi'); } catch (e) { /* bad regex */ }
    }

    // ── Syntax highlighting setup ──
    let syntaxTokens = null; // array indexed by bufRow → token array
    const grammar = grammarForFile(engine.filename);
    if (grammar && t.syntax) {
      const hl = new SyntaxHighlighter(grammar);
      // Tokenize all lines from 0 through last visible line so multi-line
      // state is propagated correctly.
      const lastVisible = Math.min(scrollTop + textRows, buf.lineCount);
      const allLines = buf.lines.slice(0, lastVisible);
      const result = hl.tokenizeLines(allLines);
      syntaxTokens = result.tokens;
    }

    // ── Text area ──
    for (let r = 0; r < textRows; r++) {
      const bufRow = scrollTop + r;
      if (bufRow < buf.lineCount) {
        const raw = buf.lines[bufRow];
        // Expand tabs to spaces (tabstop=8, matching nvim default)
        let expanded = '';
        // Build a mapping from buffer col → screen col
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

        // Pad or truncate to cols
        const text = expanded.length >= this.cols
          ? expanded.slice(0, this.cols)
          : expanded + ' '.repeat(this.cols - expanded.length);

        // Build per-column colour array then compress into runs
        const colFg = new Array(this.cols).fill(t.normalFg);
        const colBg = new Array(this.cols).fill(t.normalBg);

        // Apply syntax highlighting (base layer, before visual/search)
        if (syntaxTokens && syntaxTokens[bufRow]) {
          for (const tok of syntaxTokens[bufRow]) {
            const color = scopeToColor(tok.scope, t.syntax);
            if (!color) continue;
            // Map buffer columns to screen columns
            const scrStart = bufToScreen[tok.start] ?? tok.start;
            const scrEnd = (bufToScreen[tok.end] ?? tok.end) - 1;
            for (let c = scrStart; c <= Math.min(scrEnd, this.cols - 1); c++) {
              colFg[c] = color;
            }
          }
        }

        // Apply visual highlight
        if (visMode) {
          let hlStart = -1, hlEnd = -1; // screen columns (inclusive)
          if (visMode === 'line') {
            if (bufRow >= visSR && bufRow <= visER) {
              hlStart = 0;
              hlEnd = this.cols - 1;
            }
          } else { // char
            if (bufRow >= visSR && bufRow <= visER) {
              if (visSR === visER) {
                // Single-line selection
                hlStart = bufToScreen[visSC] ?? 0;
                hlEnd = (visSC <= visEC && visEC < raw.length)
                  ? (bufToScreen[visEC + 1] ?? expanded.length) - 1
                  : (bufToScreen[visEC] ?? expanded.length - 1);
                if (visEC >= raw.length) hlEnd = expanded.length - 1;
                // For inclusive end, we want the end screen col of visEC char
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
                // Middle line – fully selected
                hlStart = 0;
                hlEnd = Math.max(expanded.length - 1, 0);
              }
            }
          }

          if (hlStart >= 0 && hlEnd >= hlStart) {
            const end = Math.min(hlEnd, this.cols - 1);
            for (let c = hlStart; c <= end; c++) {
              // Only change bg; fg keeps its original colour
              colBg[c] = t.visualBg;
            }
          }
        }

        // Apply search highlights (on top of visual, so they show through)
        if (searchRegex) {
          searchRegex.lastIndex = 0;
          let m;
          while ((m = searchRegex.exec(raw)) !== null) {
            if (m[0].length === 0) { searchRegex.lastIndex++; continue; }
            const matchStart = bufToScreen[m.index] ?? 0;
            const matchEnd = (bufToScreen[m.index + m[0].length] ?? expanded.length) - 1;
            // CurSearch: match at the tracked search position (last search jump)
            const csp = engine._curSearchPos;
            const isCursorMatch = engine._showCurSearch && csp
              && bufRow === csp.row
              && m.index === csp.col;
            const sFg = isCursorMatch ? t.curSearchFg : t.searchFg;
            const sBg = isCursorMatch ? t.curSearchBg : t.searchBg;
            for (let c = matchStart; c <= Math.min(matchEnd, this.cols - 1); c++) {
              colFg[c] = sFg;
              colBg[c] = sBg;
            }
          }
        }

        // Compress per-column arrays into runs
        const runs = [];
        let runStart = 0;
        for (let c = 1; c <= this.cols; c++) {
          if (c === this.cols || colFg[c] !== colFg[runStart] || colBg[c] !== colBg[runStart]) {
            runs.push({ n: c - runStart, fg: colFg[runStart], bg: colBg[runStart] });
            runStart = c;
          }
        }

        lines.push({ text, runs });
      } else {
        // Tilde lines (past end of buffer)
        const text = '~' + ' '.repeat(this.cols - 1);
        lines.push({
          text,
          runs: [
            { n: this.cols, fg: t.tildeFg, bg: t.tildeBg },
          ],
        });
      }
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
    } else if ((engine.commandLine ?? '').startsWith('E486:')) {
      // Error message in command line (red colored)
      const errLen = Math.min((engine.commandLine || '').length, this.cols);
      const errRuns = [];
      if (errLen > 0) errRuns.push({ n: errLen, fg: t.errorFg || t.cmdFg, bg: t.cmdBg });
      if (errLen < this.cols) errRuns.push({ n: this.cols - errLen, fg: t.cmdFg, bg: t.cmdBg });
      lines.push({ text: cmdText, runs: errRuns });
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

    // Map buffer cursor col to screen col (expand tabs)
    let screenCol = cursor.col;
    const cursorBufRow = cursor.row;
    if (cursorBufRow >= 0 && cursorBufRow < buf.lineCount) {
      const rawLine = buf.lines[cursorBufRow];
      let sc = 0;
      for (let i = 0; i < cursor.col && i < rawLine.length; i++) {
        if (rawLine[i] === '\t') {
          sc += 8 - (sc % 8);
        } else {
          sc++;
        }
      }
      // When cursor is ON a tab character, nvim renders at the LAST
      // visual column of that tab (not the first).
      if (cursor.col < rawLine.length && rawLine[cursor.col] === '\t') {
        sc += 8 - (sc % 8) - 1;
      }
      screenCol = sc;
    }

    return {
      rows: this.rows,
      cols: this.cols,
      cursor: {
        row: cursor.row - scrollTop,
        col: screenCol,
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

  /** @private */
  _padOrTruncate(s, width) {
    if (s.length >= width) return s.slice(0, width);
    return s + ' '.repeat(width - s.length);
  }
}

export { DEFAULT_FG, DEFAULT_BG };
