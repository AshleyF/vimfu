/**
 * VimFu Simulator – Virtual File System
 *
 * A minimal in-memory filesystem backed by localStorage.
 * Simulates a single flat directory (no subdirectories).
 * Used by both the shell simulator and the Vim engine for
 * :w / :e / :q file operations.
 *
 * Storage format in localStorage:
 *   key = "vimfu:files"
 *   value = JSON { "filename": "contents", ... }
 *
 * Also tracks file metadata (modified flag, etc.) in memory.
 */

const STORAGE_KEY = 'vimfu:files';

export class VirtualFS {
  /**
   * @param {object} [opts]
   * @param {boolean} [opts.persist=true] – use localStorage for persistence
   */
  constructor({ persist = true } = {}) {
    this._persist = persist;
    /** @type {Map<string, string>} filename → contents */
    this._files = new Map();
    this._load();
  }

  // ── Public API ──

  /**
   * List all filenames, optionally sorted.
   * @returns {string[]}
   */
  ls() {
    return [...this._files.keys()].sort();
  }

  /**
   * Check if a file exists.
   * @param {string} name
   * @returns {boolean}
   */
  exists(name) {
    return this._files.has(name);
  }

  /**
   * Read file contents. Returns null if file doesn't exist.
   * @param {string} name
   * @returns {string|null}
   */
  read(name) {
    return this._files.get(name) ?? null;
  }

  /**
   * Write (create or overwrite) a file.
   * @param {string} name
   * @param {string} contents
   */
  write(name, contents) {
    this._files.set(name, contents);
    this._save();
  }

  /**
   * Remove a file. Returns true if it existed.
   * @param {string} name
   * @returns {boolean}
   */
  rm(name) {
    const had = this._files.delete(name);
    if (had) this._save();
    return had;
  }

  /**
   * Remove all files.
   */
  clear() {
    this._files.clear();
    this._save();
  }

  /**
   * Number of files.
   * @returns {number}
   */
  get fileCount() {
    return this._files.size;
  }

  // ── Persistence ──

  /** @private */
  _load() {
    if (!this._persist) return;
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) {
        const obj = JSON.parse(raw);
        for (const [k, v] of Object.entries(obj)) {
          this._files.set(k, v);
        }
      }
    } catch {
      // localStorage unavailable or corrupt – start empty
    }
  }

  /** @private */
  _save() {
    if (!this._persist) return;
    try {
      const obj = Object.fromEntries(this._files);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(obj));
    } catch {
      // localStorage full or unavailable – ignore
    }
  }
}
