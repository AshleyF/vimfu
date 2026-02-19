/**
 * VimFu Simulator – Buffer
 *
 * Manages the text content as an array of lines.
 * Pure data structure with no rendering logic.
 */

export class Buffer {
  /**
   * @param {string[]} lines – initial content (one string per line)
   */
  constructor(lines = ['']) {
    /** @type {string[]} */
    this.lines = lines.length > 0 ? [...lines] : [''];
  }

  /** Total number of lines. */
  get lineCount() {
    return this.lines.length;
  }

  /**
   * Length of a given line (0-indexed).
   * @param {number} row
   */
  lineLength(row) {
    if (row < 0 || row >= this.lines.length) return 0;
    return this.lines[row].length;
  }

  /**
   * Character at (row, col). Returns '' if out of range.
   * @param {number} row
   * @param {number} col
   */
  charAt(row, col) {
    if (row < 0 || row >= this.lines.length) return '';
    const line = this.lines[row];
    if (col < 0 || col >= line.length) return '';
    return line[col];
  }

  /**
   * Insert a single character at (row, col).
   * @param {number} row
   * @param {number} col
   * @param {string} ch
   */
  insertChar(row, col, ch) {
    const line = this.lines[row];
    this.lines[row] = line.slice(0, col) + ch + line.slice(col);
  }

  /**
   * Insert text at (row, col) – may contain newlines.
   * Returns the final cursor position { row, col }.
   * @param {number} row
   * @param {number} col
   * @param {string} text
   */
  insertText(row, col, text) {
    const parts = text.split('\n');
    const line = this.lines[row];
    const before = line.slice(0, col);
    const after = line.slice(col);

    if (parts.length === 1) {
      this.lines[row] = before + parts[0] + after;
      return { row, col: col + parts[0].length };
    }

    // Multiple lines
    this.lines[row] = before + parts[0];
    const newLines = parts.slice(1, -1);
    const lastPart = parts[parts.length - 1];
    const insertRow = row + 1;
    this.lines.splice(insertRow, 0, ...newLines, lastPart + after);
    return { row: row + parts.length - 1, col: lastPart.length };
  }

  /**
   * Delete a character at (row, col).
   * If col is at end-of-line, joins with the next line.
   * @param {number} row
   * @param {number} col
   */
  deleteChar(row, col) {
    const line = this.lines[row];
    if (col < line.length) {
      this.lines[row] = line.slice(0, col) + line.slice(col + 1);
    } else if (row + 1 < this.lines.length) {
      // Join with next line
      this.lines[row] = line + this.lines[row + 1];
      this.lines.splice(row + 1, 1);
    }
  }

  /**
   * Split a line at (row, col) — used by Enter in insert mode.
   * @param {number} row
   * @param {number} col
   */
  splitLine(row, col) {
    const line = this.lines[row];
    this.lines[row] = line.slice(0, col);
    this.lines.splice(row + 1, 0, line.slice(col));
  }

  /**
   * Insert a new empty line after the given row.
   * @param {number} afterRow
   */
  insertLineAfter(afterRow) {
    this.lines.splice(afterRow + 1, 0, '');
  }

  /**
   * Insert a new empty line before the given row.
   * @param {number} beforeRow
   */
  insertLineBefore(beforeRow) {
    this.lines.splice(beforeRow, 0, '');
  }

  /**
   * Delete the character before (row, col) — Backspace in insert mode.
   * Returns the new cursor position { row, col }.
   * @param {number} row
   * @param {number} col
   */
  deleteCharBefore(row, col) {
    if (col > 0) {
      const line = this.lines[row];
      this.lines[row] = line.slice(0, col - 1) + line.slice(col);
      return { row, col: col - 1 };
    } else if (row > 0) {
      // Join with previous line
      const prevLen = this.lines[row - 1].length;
      this.lines[row - 1] += this.lines[row];
      this.lines.splice(row, 1);
      return { row: row - 1, col: prevLen };
    }
    return { row, col };
  }
}
