/**
 * VimFu Simulator – Session Screen Ground Truth Generator
 *
 * Generates ground truth frame snapshots for SessionManager scenarios.
 * These cover the full shell↔vim integration including:
 *   - Shell prompt display and command output
 *   - Vim launch from shell
 *   - :w write messages, :q error handling (E37), :wq round-trips
 *   - Visual accuracy: prompt colors, error colors, cursor position
 *
 * The output is saved as ground_truth_session.json and compared by
 * test_session_screen.js (similar to compare_test_v2.js for vim engine).
 *
 * Usage:
 *   node test/gen_session_ground_truth.js          # generate ground truth
 *   node test/gen_session_ground_truth.js --print   # also print frames
 */

import { writeFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';
import { SessionManager } from '../src/session.js';

const __dirname = dirname(fileURLToPath(import.meta.url));
const OUT_PATH = resolve(__dirname, 'session_ground_truth.json');

const args = process.argv.slice(2);
const doPrint = args.includes('--print');

const ROWS = 20;
const COLS = 40;

// ── Helpers ──

function newSession(opts = {}) {
  const s = new SessionManager({
    rows: ROWS, cols: COLS, persist: false, ...opts,
  });
  return s;
}

function feedString(s, str) {
  for (const ch of str) s.feedKey(ch);
}

function snap(s) {
  const frame = s.renderFrame();
  return frame;
}

function printFrame(label, frame) {
  if (!doPrint) return;
  console.log(`\n── ${label} ──`);
  for (let i = 0; i < frame.lines.length; i++) {
    const l = frame.lines[i];
    const runsStr = l.runs.map(r => `${r.n}:${r.fg}/${r.bg}`).join(' ');
    console.log(`  ${String(i).padStart(2)}: ${JSON.stringify(l.text)}  [${runsStr}]`);
  }
  console.log(`  cursor: (${frame.cursor.row}, ${frame.cursor.col})`);
}

// ── Scenarios ──

const groundTruth = {};

function addCase(name, fn) {
  const { frame, description } = fn();
  groundTruth[name] = {
    description,
    frame,
    cursor: frame.cursor,
    textLines: frame.lines.map(l => l.text),
  };
  printFrame(name, frame);
}

// ───────────────────────────────────────────────────────────
// Shell scenarios
// ───────────────────────────────────────────────────────────

addCase('shell_initial_prompt', () => {
  const s = newSession();
  return {
    description: 'Fresh shell with zsh prompt (➜  vimfu)',
    frame: snap(s),
  };
});

addCase('shell_ls_with_files', () => {
  const s = newSession();
  s.fs.write('hello.txt', 'hello');
  s.fs.write('world.txt', 'world');
  feedString(s, 'ls');
  s.feedKey('Enter');
  return {
    description: 'Shell after ls showing two files',
    frame: snap(s),
  };
});

addCase('shell_cat_file', () => {
  const s = newSession();
  s.fs.write('demo.txt', 'line one\nline two\nline three');
  feedString(s, 'cat demo.txt');
  s.feedKey('Enter');
  return {
    description: 'Shell after cat showing file contents',
    frame: snap(s),
  };
});

addCase('shell_unknown_command', () => {
  const s = newSession();
  feedString(s, 'badcmd');
  s.feedKey('Enter');
  return {
    description: 'Shell showing "command not found" error',
    frame: snap(s),
  };
});

addCase('shell_echo_redirect', () => {
  const s = newSession();
  feedString(s, 'echo hello > test.txt');
  s.feedKey('Enter');
  return {
    description: 'Shell after echo redirect (creates file)',
    frame: snap(s),
  };
});

addCase('shell_clear', () => {
  const s = newSession();
  feedString(s, 'echo noise');
  s.feedKey('Enter');
  feedString(s, 'clear');
  s.feedKey('Enter');
  return {
    description: 'Shell after clear (only prompt remains)',
    frame: snap(s),
  };
});

// ───────────────────────────────────────────────────────────
// Vim launch from shell
// ───────────────────────────────────────────────────────────

addCase('vim_launch_new_file', () => {
  const s = newSession();
  feedString(s, 'vim test.txt');
  s.feedKey('Enter');
  return {
    description: 'Vim launched with new (empty) file from shell',
    frame: snap(s),
  };
});

addCase('vim_launch_existing_file', () => {
  const s = newSession();
  s.fs.write('existing.txt', 'Hello from VFS\nSecond line');
  feedString(s, 'vim existing.txt');
  s.feedKey('Enter');
  return {
    description: 'Vim launched with existing file (2 lines)',
    frame: snap(s),
  };
});

// ───────────────────────────────────────────────────────────
// :w write message
// ───────────────────────────────────────────────────────────

addCase('vim_write_new_file', () => {
  const s = newSession();
  feedString(s, 'vim test.txt');
  s.feedKey('Enter');
  s.feedKey('i');
  feedString(s, 'Hello VimFu');
  s.feedKey('Escape');
  s.feedKey(':');
  feedString(s, 'w');
  s.feedKey('Enter');
  return {
    description: ':w on new file shows "test.txt" 1L, 12B written',
    frame: snap(s),
  };
});

addCase('vim_write_multiline', () => {
  const s = newSession();
  feedString(s, 'vim multi.txt');
  s.feedKey('Enter');
  s.feedKey('i');
  feedString(s, 'Line 1');
  s.feedKey('Enter');
  feedString(s, 'Line 2');
  s.feedKey('Enter');
  feedString(s, 'Line 3');
  s.feedKey('Escape');
  s.feedKey(':');
  feedString(s, 'w');
  s.feedKey('Enter');
  return {
    description: ':w multi-line file shows 3L, NB written',
    frame: snap(s),
  };
});

// ───────────────────────────────────────────────────────────
// E37 error (:q with unsaved changes)
// ───────────────────────────────────────────────────────────

addCase('vim_quit_dirty_e37', () => {
  const s = newSession();
  feedString(s, 'vim dirty.txt');
  s.feedKey('Enter');
  s.feedKey('i');
  feedString(s, 'unsaved data');
  s.feedKey('Escape');
  s.feedKey(':');
  feedString(s, 'q');
  s.feedKey('Enter');
  return {
    description: ':q on dirty buffer shows E37+E162 multi-line error with "Press ENTER"',
    frame: snap(s),
  };
});

addCase('vim_quit_dirty_e37_dismiss', () => {
  const s = newSession();
  feedString(s, 'vim dirty.txt');
  s.feedKey('Enter');
  s.feedKey('i');
  feedString(s, 'unsaved data');
  s.feedKey('Escape');
  s.feedKey(':');
  feedString(s, 'q');
  s.feedKey('Enter');
  // Now dismiss the E37 prompt
  s.feedKey('Enter');
  return {
    description: 'After dismissing E37 prompt, back to normal vim',
    frame: snap(s),
  };
});

// ───────────────────────────────────────────────────────────
// :wq and :q round trips
// ───────────────────────────────────────────────────────────

addCase('vim_wq_back_to_shell', () => {
  const s = newSession();
  feedString(s, 'vim wq.txt');
  s.feedKey('Enter');
  s.feedKey('i');
  feedString(s, 'saved');
  s.feedKey('Escape');
  s.feedKey(':');
  feedString(s, 'wq');
  s.feedKey('Enter');
  return {
    description: ':wq returns to shell prompt',
    frame: snap(s),
  };
});

addCase('vim_q_clean_back_to_shell', () => {
  const s = newSession();
  feedString(s, 'vim test.txt');
  s.feedKey('Enter');
  s.feedKey(':');
  feedString(s, 'q');
  s.feedKey('Enter');
  return {
    description: ':q on clean buffer returns to shell',
    frame: snap(s),
  };
});

addCase('vim_q_bang_back_to_shell', () => {
  const s = newSession();
  feedString(s, 'vim dirty.txt');
  s.feedKey('Enter');
  s.feedKey('i');
  feedString(s, 'will discard');
  s.feedKey('Escape');
  s.feedKey(':');
  feedString(s, 'q!');
  s.feedKey('Enter');
  return {
    description: ':q! on dirty buffer returns to shell without saving',
    frame: snap(s),
  };
});

// ───────────────────────────────────────────────────────────
// ZZ / ZQ
// ───────────────────────────────────────────────────────────

addCase('vim_ZZ_saves_and_quits', () => {
  const s = newSession();
  feedString(s, 'vim zz.txt');
  s.feedKey('Enter');
  s.feedKey('i');
  feedString(s, 'ZZ content');
  s.feedKey('Escape');
  s.feedKey('Z');
  s.feedKey('Z');
  return {
    description: 'ZZ saves and returns to shell',
    frame: snap(s),
  };
});

addCase('vim_ZQ_quits_without_saving', () => {
  const s = newSession();
  feedString(s, 'vim zq.txt');
  s.feedKey('Enter');
  s.feedKey('i');
  feedString(s, 'discard me');
  s.feedKey('Escape');
  s.feedKey('Z');
  s.feedKey('Q');
  return {
    description: 'ZQ discards and returns to shell',
    frame: snap(s),
  };
});

// ───────────────────────────────────────────────────────────
// :e (edit different file)
// ───────────────────────────────────────────────────────────

addCase('vim_edit_different_file', () => {
  const s = newSession();
  s.fs.write('other.txt', 'Other file content');
  feedString(s, 'vim first.txt');
  s.feedKey('Enter');
  s.feedKey(':');
  feedString(s, 'e other.txt');
  s.feedKey('Enter');
  return {
    description: ':e other.txt loads a different file',
    frame: snap(s),
  };
});

// ───────────────────────────────────────────────────────────
// Shell round-trip (vim → shell → vim)
// ───────────────────────────────────────────────────────────

addCase('roundtrip_create_reopen', () => {
  const s = newSession();
  // Create and save
  feedString(s, 'vim rt.txt');
  s.feedKey('Enter');
  s.feedKey('i');
  feedString(s, 'persistent data');
  s.feedKey('Escape');
  s.feedKey(':');
  feedString(s, 'wq');
  s.feedKey('Enter');
  // Reopen
  feedString(s, 'vim rt.txt');
  s.feedKey('Enter');
  return {
    description: 'File created with :wq, reopened from shell with data intact',
    frame: snap(s),
  };
});

addCase('shell_ls_after_vim_write', () => {
  const s = newSession();
  feedString(s, 'vim newfile.txt');
  s.feedKey('Enter');
  s.feedKey('i');
  feedString(s, 'content');
  s.feedKey('Escape');
  s.feedKey(':');
  feedString(s, 'wq');
  s.feedKey('Enter');
  feedString(s, 'ls');
  s.feedKey('Enter');
  return {
    description: 'ls after vim :wq shows the file',
    frame: snap(s),
  };
});

// ───────────────────────────────────────────────────────────
// :! shell command from vim
// ───────────────────────────────────────────────────────────

addCase('vim_shell_escape_ls', () => {
  const s = newSession();
  s.fs.write('afile.txt', 'data');
  feedString(s, 'vim test');
  s.feedKey('Enter');
  s.feedKey(':');
  feedString(s, '!ls');
  s.feedKey('Enter');
  return {
    description: ':!ls shows file listing in shell_msg mode',
    frame: snap(s),
  };
});

addCase('vim_shell_escape_ls_dismiss', () => {
  const s = newSession();
  s.fs.write('afile.txt', 'data');
  feedString(s, 'vim test');
  s.feedKey('Enter');
  s.feedKey(':');
  feedString(s, '!ls');
  s.feedKey('Enter');
  // Dismiss
  s.feedKey('Enter');
  return {
    description: 'After dismissing :!ls, back to normal vim',
    frame: snap(s),
  };
});

// ── Write output ──
writeFileSync(OUT_PATH, JSON.stringify(groundTruth, null, 2));
console.log(`Generated ${Object.keys(groundTruth).length} session ground truth cases`);
console.log(`Written to: ${OUT_PATH}`);
