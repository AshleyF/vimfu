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

// ───────────────────────────────────────────────────────────
// Shell vi-mode (set -o vi)
// ───────────────────────────────────────────────────────────

addCase('shell_set_o_vi', () => {
  const s = newSession();
  feedString(s, 'set -o vi');
  s.feedKey('Enter');
  return {
    description: 'Shell after "set -o vi" enables vi-mode (prompt, insert mode)',
    frame: snap(s),
  };
});

addCase('shell_vi_type_and_escape', () => {
  const s = newSession();
  feedString(s, 'set -o vi');
  s.feedKey('Enter');
  feedString(s, 'hello world');
  s.feedKey('Escape');
  return {
    description: 'Vi-mode: typed "hello world" then Escape (cursor moves left, block cursor)',
    frame: snap(s),
  };
});

addCase('shell_vi_motion_0_dollar', () => {
  const s = newSession();
  feedString(s, 'set -o vi');
  s.feedKey('Enter');
  feedString(s, 'hello world foo');
  s.feedKey('Escape');
  s.feedKey('0');
  return {
    description: 'Vi normal: 0 moves to start of line',
    frame: snap(s),
  };
});

addCase('shell_vi_motion_w', () => {
  const s = newSession();
  feedString(s, 'set -o vi');
  s.feedKey('Enter');
  feedString(s, 'hello world foo');
  s.feedKey('Escape');
  s.feedKey('0');
  s.feedKey('w');
  return {
    description: 'Vi normal: w moves to next word',
    frame: snap(s),
  };
});

addCase('shell_vi_motion_b', () => {
  const s = newSession();
  feedString(s, 'set -o vi');
  s.feedKey('Enter');
  feedString(s, 'hello world foo');
  s.feedKey('Escape');
  s.feedKey('b');
  return {
    description: 'Vi normal: b moves to previous word start',
    frame: snap(s),
  };
});

addCase('shell_vi_x_delete', () => {
  const s = newSession();
  feedString(s, 'set -o vi');
  s.feedKey('Enter');
  feedString(s, 'abc');
  s.feedKey('Escape');
  s.feedKey('0');
  s.feedKey('x');
  return {
    description: 'Vi normal: x deletes char under cursor',
    frame: snap(s),
  };
});

addCase('shell_vi_dw', () => {
  const s = newSession();
  feedString(s, 'set -o vi');
  s.feedKey('Enter');
  feedString(s, 'hello world foo');
  s.feedKey('Escape');
  s.feedKey('0');
  s.feedKey('d');
  s.feedKey('w');
  return {
    description: 'Vi normal: dw deletes word + trailing space',
    frame: snap(s),
  };
});

addCase('shell_vi_cw', () => {
  const s = newSession();
  feedString(s, 'set -o vi');
  s.feedKey('Enter');
  feedString(s, 'hello world');
  s.feedKey('Escape');
  s.feedKey('0');
  s.feedKey('c');
  s.feedKey('w');
  feedString(s, 'Hi');
  s.feedKey('Escape');
  return {
    description: 'Vi normal: cw changes word (like ce), replaced "hello" with "Hi"',
    frame: snap(s),
  };
});

addCase('shell_vi_dd', () => {
  const s = newSession();
  feedString(s, 'set -o vi');
  s.feedKey('Enter');
  feedString(s, 'delete me');
  s.feedKey('Escape');
  s.feedKey('d');
  s.feedKey('d');
  return {
    description: 'Vi normal: dd clears entire line',
    frame: snap(s),
  };
});

addCase('shell_vi_f_motion', () => {
  const s = newSession();
  feedString(s, 'set -o vi');
  s.feedKey('Enter');
  feedString(s, 'find the char');
  s.feedKey('Escape');
  s.feedKey('0');
  s.feedKey('f');
  s.feedKey('t');
  return {
    description: 'Vi normal: ft finds "t" forward',
    frame: snap(s),
  };
});

addCase('shell_vi_f_semicolon_repeat', () => {
  const s = newSession();
  feedString(s, 'set -o vi');
  s.feedKey('Enter');
  feedString(s, 'find the things there');
  s.feedKey('Escape');
  s.feedKey('0');
  s.feedKey('f');
  s.feedKey('t');
  s.feedKey(';');
  return {
    description: 'Vi normal: ft then ; repeats find',
    frame: snap(s),
  };
});

addCase('shell_vi_r_replace', () => {
  const s = newSession();
  feedString(s, 'set -o vi');
  s.feedKey('Enter');
  feedString(s, 'abc');
  s.feedKey('Escape');
  s.feedKey('0');
  s.feedKey('r');
  s.feedKey('X');
  return {
    description: 'Vi normal: rX replaces char under cursor with X',
    frame: snap(s),
  };
});

addCase('shell_vi_p_paste', () => {
  const s = newSession();
  feedString(s, 'set -o vi');
  s.feedKey('Enter');
  feedString(s, 'abc');
  s.feedKey('Escape');
  s.feedKey('0');
  s.feedKey('x');
  s.feedKey('p');
  return {
    description: 'Vi normal: x then p (delete a, paste after cursor)',
    frame: snap(s),
  };
});

addCase('shell_vi_I_insert_start', () => {
  const s = newSession();
  feedString(s, 'set -o vi');
  s.feedKey('Enter');
  feedString(s, 'world');
  s.feedKey('Escape');
  s.feedKey('I');
  feedString(s, 'hello ');
  s.feedKey('Escape');
  return {
    description: 'Vi: I inserts at start of line',
    frame: snap(s),
  };
});

addCase('shell_vi_A_append_end', () => {
  const s = newSession();
  feedString(s, 'set -o vi');
  s.feedKey('Enter');
  feedString(s, 'hello');
  s.feedKey('Escape');
  s.feedKey('A');
  feedString(s, ' world');
  s.feedKey('Escape');
  return {
    description: 'Vi: A appends at end of line',
    frame: snap(s),
  };
});

addCase('shell_vi_tilde_swap_case', () => {
  const s = newSession();
  feedString(s, 'set -o vi');
  s.feedKey('Enter');
  feedString(s, 'hello');
  s.feedKey('Escape');
  s.feedKey('0');
  s.feedKey('~');
  s.feedKey('~');
  s.feedKey('~');
  return {
    description: 'Vi normal: ~~~ swaps case of first 3 chars',
    frame: snap(s),
  };
});

addCase('shell_vi_C_change_to_end', () => {
  const s = newSession();
  feedString(s, 'set -o vi');
  s.feedKey('Enter');
  feedString(s, 'hello world');
  s.feedKey('Escape');
  s.feedKey('0');
  s.feedKey('w');
  s.feedKey('C');
  feedString(s, 'vim');
  s.feedKey('Escape');
  return {
    description: 'Vi: C changes from cursor to end of line',
    frame: snap(s),
  };
});

addCase('shell_vi_D_delete_to_end', () => {
  const s = newSession();
  feedString(s, 'set -o vi');
  s.feedKey('Enter');
  feedString(s, 'hello world foo');
  s.feedKey('Escape');
  s.feedKey('0');
  s.feedKey('w');
  s.feedKey('D');
  return {
    description: 'Vi: D deletes from cursor to end of line',
    frame: snap(s),
  };
});

addCase('shell_vi_cursor_shape_normal', () => {
  const s = newSession();
  feedString(s, 'set -o vi');
  s.feedKey('Enter');
  feedString(s, 'test');
  s.feedKey('Escape');
  return {
    description: 'Vi normal mode has block cursor',
    frame: snap(s),
  };
});

addCase('shell_vi_cursor_shape_insert', () => {
  const s = newSession();
  feedString(s, 'set -o vi');
  s.feedKey('Enter');
  feedString(s, 'test');
  s.feedKey('Escape');
  s.feedKey('i');
  return {
    description: 'Vi insert mode has beam cursor',
    frame: snap(s),
  };
});

addCase('shell_vi_set_o_emacs', () => {
  const s = newSession();
  feedString(s, 'set -o vi');
  s.feedKey('Enter');
  feedString(s, 'set -o emacs');
  s.feedKey('Enter');
  feedString(s, 'test');
  return {
    description: 'set -o emacs disables vi-mode, back to normal editing',
    frame: snap(s),
  };
});

addCase('shell_vi_enter_executes_from_normal', () => {
  const s = newSession();
  feedString(s, 'set -o vi');
  s.feedKey('Enter');
  feedString(s, 'echo hello');
  s.feedKey('Escape');
  s.feedKey('Enter');
  return {
    description: 'Enter in vi normal mode executes command',
    frame: snap(s),
  };
});

addCase('shell_vi_df_motion', () => {
  const s = newSession();
  feedString(s, 'set -o vi');
  s.feedKey('Enter');
  feedString(s, 'abcdef');
  s.feedKey('Escape');
  s.feedKey('0');
  s.feedKey('d');
  s.feedKey('f');
  s.feedKey('d');
  return {
    description: 'Vi normal: dfd deletes from cursor through d (inclusive)',
    frame: snap(s),
  };
});

addCase('shell_vi_s_substitute', () => {
  const s = newSession();
  feedString(s, 'set -o vi');
  s.feedKey('Enter');
  feedString(s, 'xyz');
  s.feedKey('Escape');
  s.feedKey('0');
  s.feedKey('s');
  feedString(s, 'AB');
  s.feedKey('Escape');
  return {
    description: 'Vi: s substitutes char and enters insert mode',
    frame: snap(s),
  };
});

// ───────────────────────────────────────────────────────────
// Shell vi-mode — numeric counts
// ───────────────────────────────────────────────────────────

addCase('shell_vi_2w_count', () => {
  const s = newSession();
  feedString(s, 'set -o vi');
  s.feedKey('Enter');
  feedString(s, 'hello world foo');
  s.feedKey('Escape');
  s.feedKey('0');
  feedString(s, '2');
  s.feedKey('w');
  return {
    description: 'Vi normal: 2w skips two words',
    frame: snap(s),
  };
});

addCase('shell_vi_3x_count', () => {
  const s = newSession();
  feedString(s, 'set -o vi');
  s.feedKey('Enter');
  feedString(s, 'abcdef');
  s.feedKey('Escape');
  s.feedKey('0');
  feedString(s, '3');
  s.feedKey('x');
  return {
    description: 'Vi normal: 3x deletes 3 chars',
    frame: snap(s),
  };
});

addCase('shell_vi_2dw_count', () => {
  const s = newSession();
  feedString(s, 'set -o vi');
  s.feedKey('Enter');
  feedString(s, 'aaa bbb ccc ddd');
  s.feedKey('Escape');
  s.feedKey('0');
  feedString(s, '2');
  s.feedKey('d');
  s.feedKey('w');
  return {
    description: 'Vi normal: 2dw deletes 2 words',
    frame: snap(s),
  };
});

addCase('shell_vi_3l_count', () => {
  const s = newSession();
  feedString(s, 'set -o vi');
  s.feedKey('Enter');
  feedString(s, 'abcdef');
  s.feedKey('Escape');
  s.feedKey('0');
  feedString(s, '3');
  s.feedKey('l');
  return {
    description: 'Vi normal: 3l moves 3 chars right',
    frame: snap(s),
  };
});

addCase('shell_vi_2p_count', () => {
  const s = newSession();
  feedString(s, 'set -o vi');
  s.feedKey('Enter');
  feedString(s, 'abc');
  s.feedKey('Escape');
  s.feedKey('0');
  s.feedKey('x'); // yank 'a'
  feedString(s, '2');
  s.feedKey('p'); // paste 'a' twice
  return {
    description: 'Vi normal: 2p pastes yanked char twice',
    frame: snap(s),
  };
});

// ───────────────────────────────────────────────────────────
// Shell vi-mode — undo
// ───────────────────────────────────────────────────────────

addCase('shell_vi_undo', () => {
  const s = newSession();
  feedString(s, 'set -o vi');
  s.feedKey('Enter');
  feedString(s, 'hello');
  s.feedKey('Escape');
  s.feedKey('0');
  s.feedKey('x'); // delete 'h'
  s.feedKey('u'); // undo
  return {
    description: 'Vi normal: u undoes last delete',
    frame: snap(s),
  };
});

addCase('shell_vi_undo_multiple', () => {
  const s = newSession();
  feedString(s, 'set -o vi');
  s.feedKey('Enter');
  feedString(s, 'abc');
  s.feedKey('Escape');
  s.feedKey('0');
  s.feedKey('x'); // delete 'a' -> 'bc'
  s.feedKey('x'); // delete 'b' -> 'c'
  s.feedKey('u'); // undo -> 'bc'
  s.feedKey('u'); // undo -> 'abc'
  return {
    description: 'Vi normal: multiple u undoes multiple changes',
    frame: snap(s),
  };
});

// ───────────────────────────────────────────────────────────
// Shell vi-mode — dot repeat
// ───────────────────────────────────────────────────────────

addCase('shell_vi_dot_repeat_cw', () => {
  const s = newSession();
  feedString(s, 'set -o vi');
  s.feedKey('Enter');
  feedString(s, 'aaa bbb ccc');
  s.feedKey('Escape');
  s.feedKey('0');
  s.feedKey('c');
  s.feedKey('w');
  feedString(s, 'XXX');
  s.feedKey('Escape');
  s.feedKey('w');
  s.feedKey('.');
  return {
    description: 'Vi normal: . repeats cw change',
    frame: snap(s),
  };
});

addCase('shell_vi_dot_repeat_x', () => {
  const s = newSession();
  feedString(s, 'set -o vi');
  s.feedKey('Enter');
  feedString(s, 'abcd');
  s.feedKey('Escape');
  s.feedKey('0');
  s.feedKey('x'); // delete 'a'
  s.feedKey('.'); // delete 'b'
  s.feedKey('.'); // delete 'c'
  return {
    description: 'Vi normal: . repeats x three times',
    frame: snap(s),
  };
});

// ───────────────────────────────────────────────────────────
// Shell vi-mode — t/T motions
// ───────────────────────────────────────────────────────────

addCase('shell_vi_t_motion', () => {
  const s = newSession();
  feedString(s, 'set -o vi');
  s.feedKey('Enter');
  feedString(s, 'hello world');
  s.feedKey('Escape');
  s.feedKey('0');
  s.feedKey('t');
  s.feedKey('o');
  return {
    description: 'Vi normal: to moves to one before first "o"',
    frame: snap(s),
  };
});

addCase('shell_vi_T_motion', () => {
  const s = newSession();
  feedString(s, 'set -o vi');
  s.feedKey('Enter');
  feedString(s, 'hello world');
  s.feedKey('Escape');
  // cursor at end (pos 9, on 'd')... Escape from pos 11 -> pos 10
  s.feedKey('T');
  s.feedKey(' ');
  return {
    description: 'Vi normal: T space from end moves after last space',
    frame: snap(s),
  };
});

addCase('shell_vi_dt_motion', () => {
  const s = newSession();
  feedString(s, 'set -o vi');
  s.feedKey('Enter');
  feedString(s, 'abcdef');
  s.feedKey('Escape');
  s.feedKey('0');
  s.feedKey('d');
  s.feedKey('t');
  s.feedKey('d');
  return {
    description: 'Vi normal: dtd deletes up to (not including) d',
    frame: snap(s),
  };
});

addCase('shell_vi_ct_motion', () => {
  const s = newSession();
  feedString(s, 'set -o vi');
  s.feedKey('Enter');
  feedString(s, 'abcdef');
  s.feedKey('Escape');
  s.feedKey('0');
  s.feedKey('c');
  s.feedKey('t');
  s.feedKey('d');
  feedString(s, 'XY');
  s.feedKey('Escape');
  return {
    description: 'Vi normal: ctd changes up to d, type XY',
    frame: snap(s),
  };
});

// ───────────────────────────────────────────────────────────
// Shell vi-mode — R replace mode
// ───────────────────────────────────────────────────────────

addCase('shell_vi_R_replace_mode', () => {
  const s = newSession();
  feedString(s, 'set -o vi');
  s.feedKey('Enter');
  feedString(s, 'abcdef');
  s.feedKey('Escape');
  s.feedKey('0');
  s.feedKey('R');
  feedString(s, 'XY');
  s.feedKey('Escape');
  return {
    description: 'Vi: R overtypes chars, XY replaces ab',
    frame: snap(s),
  };
});

addCase('shell_vi_R_backspace_restores', () => {
  const s = newSession();
  feedString(s, 'set -o vi');
  s.feedKey('Enter');
  feedString(s, 'abcdef');
  s.feedKey('Escape');
  s.feedKey('0');
  s.feedKey('R');
  feedString(s, 'XY');
  s.feedKey('Backspace');
  s.feedKey('Escape');
  return {
    description: 'Vi: R then Backspace restores original char',
    frame: snap(s),
  };
});

// ───────────────────────────────────────────────────────────
// Shell vi-mode — G history jump
// ───────────────────────────────────────────────────────────

addCase('shell_vi_G_oldest_history', () => {
  const s = newSession();
  feedString(s, 'set -o vi');
  s.feedKey('Enter');
  feedString(s, 'echo first');
  s.feedKey('Enter');
  feedString(s, 'echo second');
  s.feedKey('Enter');
  feedString(s, 'echo third');
  s.feedKey('Enter');
  // Now in insert mode on blank line. Escape to normal.
  s.feedKey('Escape');
  s.feedKey('G'); // oldest history entry
  return {
    description: 'Vi normal: G jumps to oldest history entry',
    frame: snap(s),
  };
});

// ───────────────────────────────────────────────────────────
// Shell vi-mode — # comment-out
// ───────────────────────────────────────────────────────────

addCase('shell_vi_hash_comment', () => {
  const s = newSession();
  feedString(s, 'set -o vi');
  s.feedKey('Enter');
  feedString(s, 'echo hello');
  s.feedKey('Escape');
  s.feedKey('#');
  return {
    description: 'Vi normal: # comments out line and executes',
    frame: snap(s),
  };
});

// ───────────────────────────────────────────────────────────
// Shell vi-mode — history search (/ ? n N)
// ───────────────────────────────────────────────────────────

addCase('shell_vi_search_history', () => {
  const s = newSession();
  feedString(s, 'set -o vi');
  s.feedKey('Enter');
  feedString(s, 'echo alpha');
  s.feedKey('Enter');
  feedString(s, 'echo beta');
  s.feedKey('Enter');
  feedString(s, 'echo gamma');
  s.feedKey('Enter');
  // Escape to normal, search for 'alpha'
  s.feedKey('Escape');
  s.feedKey('/');
  feedString(s, 'alpha');
  s.feedKey('Enter');
  return {
    description: 'Vi normal: /alpha searches history for "alpha"',
    frame: snap(s),
  };
});

addCase('shell_vi_r_count', () => {
  const s = newSession();
  feedString(s, 'set -o vi');
  s.feedKey('Enter');
  feedString(s, 'abcdef');
  s.feedKey('Escape');
  s.feedKey('0');
  feedString(s, '3');
  s.feedKey('r');
  s.feedKey('X');
  return {
    description: 'Vi normal: 3rX replaces 3 chars with X',
    frame: snap(s),
  };
});

addCase('shell_vi_tilde_count', () => {
  const s = newSession();
  feedString(s, 'set -o vi');
  s.feedKey('Enter');
  feedString(s, 'hello');
  s.feedKey('Escape');
  s.feedKey('0');
  feedString(s, '3');
  s.feedKey('~');
  return {
    description: 'Vi normal: 3~ swaps case of 3 chars',
    frame: snap(s),
  };
});

// ───────────────────────────────────────────────────────────
// New shell commands
// ───────────────────────────────────────────────────────────

addCase('shell_wc', () => {
  const s = newSession();
  s.fs.write('data.txt', 'hello world\nfoo bar baz\nend');
  feedString(s, 'wc data.txt');
  s.feedKey('Enter');
  return {
    description: 'wc shows line, word, byte counts',
    frame: snap(s),
  };
});

addCase('shell_wc_l_flag', () => {
  const s = newSession();
  s.fs.write('data.txt', 'line1\nline2\nline3');
  feedString(s, 'wc -l data.txt');
  s.feedKey('Enter');
  return {
    description: 'wc -l shows only line count',
    frame: snap(s),
  };
});



addCase('shell_grep', () => {
  const s = newSession();
  s.fs.write('poem.txt', 'roses are red\nviolets are blue\nsugar is sweet\nand so are you');
  feedString(s, 'grep are poem.txt');
  s.feedKey('Enter');
  return {
    description: 'grep shows matching lines',
    frame: snap(s),
  };
});

addCase('shell_grep_n_flag', () => {
  const s = newSession();
  s.fs.write('poem.txt', 'roses are red\nviolets are blue\nsugar is sweet\nand so are you');
  feedString(s, 'grep -n are poem.txt');
  s.feedKey('Enter');
  return {
    description: 'grep -n shows line numbers with matches',
    frame: snap(s),
  };
});

addCase('shell_grep_c_flag', () => {
  const s = newSession();
  s.fs.write('poem.txt', 'roses are red\nviolets are blue\nsugar is sweet\nand so are you');
  feedString(s, 'grep -c are poem.txt');
  s.feedKey('Enter');
  return {
    description: 'grep -c shows count of matching lines',
    frame: snap(s),
  };
});

addCase('shell_grep_i_flag', () => {
  const s = newSession();
  s.fs.write('names.txt', 'Alice\nalice\nBob\nALICE');
  feedString(s, 'grep -i alice names.txt');
  s.feedKey('Enter');
  return {
    description: 'grep -i case-insensitive match',
    frame: snap(s),
  };
});

addCase('shell_cp', () => {
  const s = newSession();
  s.fs.write('src.txt', 'original content');
  feedString(s, 'cp src.txt dst.txt');
  s.feedKey('Enter');
  feedString(s, 'cat dst.txt');
  s.feedKey('Enter');
  return {
    description: 'cp copies file, cat shows the copy',
    frame: snap(s),
  };
});

addCase('shell_mv', () => {
  const s = newSession();
  s.fs.write('old.txt', 'moved content');
  feedString(s, 'mv old.txt new.txt');
  s.feedKey('Enter');
  feedString(s, 'cat new.txt');
  s.feedKey('Enter');
  return {
    description: 'mv moves file, cat shows moved content',
    frame: snap(s),
  };
});

addCase('shell_history', () => {
  const s = newSession();
  feedString(s, 'echo one');
  s.feedKey('Enter');
  feedString(s, 'echo two');
  s.feedKey('Enter');
  feedString(s, 'history');
  s.feedKey('Enter');
  return {
    description: 'history shows numbered command list',
    frame: snap(s),
  };
});



addCase('shell_echo_append_redirect', () => {
  const s = newSession();
  feedString(s, 'echo hello > test.txt');
  s.feedKey('Enter');
  feedString(s, 'echo world >> test.txt');
  s.feedKey('Enter');
  feedString(s, 'cat test.txt');
  s.feedKey('Enter');
  return {
    description: 'echo >> appends to file',
    frame: snap(s),
  };
});

addCase('shell_exit', () => {
  const s = newSession();
  feedString(s, 'exit');
  s.feedKey('Enter');
  feedString(s, 'echo should not appear');
  s.feedKey('Enter');
  return {
    description: 'exit stops accepting input',
    frame: snap(s),
  };
});

addCase('shell_tab_complete_command', () => {
  const s = newSession();
  feedString(s, 'hel');
  s.feedKey('Tab');
  return {
    description: 'Tab completes command name "hel" → "help "',
    frame: snap(s),
  };
});

addCase('shell_tab_complete_file', () => {
  const s = newSession();
  s.fs.write('readme.txt', 'hello');
  feedString(s, 'cat rea');
  s.feedKey('Tab');
  return {
    description: 'Tab completes filename "rea" → "readme.txt"',
    frame: snap(s),
  };
});

// ───────────────────────────────────────────────────────────
// :! commands from vim
// ───────────────────────────────────────────────────────────

addCase('vim_bang_wc', () => {
  const s = newSession();
  s.fs.write('data.txt', 'one two three\nfour five');
  feedString(s, 'vim data.txt');
  s.feedKey('Enter');
  s.feedKey(':');
  feedString(s, '!wc data.txt');
  s.feedKey('Enter');
  return {
    description: ':!wc shows word count output in vim',
    frame: snap(s),
  };
});

addCase('vim_bang_grep', () => {
  const s = newSession();
  s.fs.write('data.txt', 'apple\nbanana\napricot');
  feedString(s, 'vim data.txt');
  s.feedKey('Enter');
  s.feedKey(':');
  feedString(s, '!grep ap data.txt');
  s.feedKey('Enter');
  return {
    description: ':!grep shows matching lines in vim',
    frame: snap(s),
  };
});

addCase('vim_bang_cp', () => {
  const s = newSession();
  s.fs.write('src.txt', 'content');
  feedString(s, 'vim src.txt');
  s.feedKey('Enter');
  s.feedKey(':');
  feedString(s, '!cp src.txt copy.txt');
  s.feedKey('Enter');
  return {
    description: ':!cp copies file while in vim',
    frame: snap(s),
  };
});

// ───────────────────────────────────────────────────────────
// :r (read) — insert file contents below cursor
// ───────────────────────────────────────────────────────────

addCase('vim_read_file', () => {
  const s = newSession();
  s.fs.write('main.txt', 'Line one\nLine two\nLine three');
  s.fs.write('extra.txt', 'Alpha\nBravo');
  feedString(s, 'vim main.txt');
  s.feedKey('Enter');
  s.feedKey(':');
  feedString(s, 'r extra.txt');
  s.feedKey('Enter');
  return {
    description: ':r extra.txt inserts below cursor (line 1), cursor on first inserted line',
    frame: snap(s),
  };
});

addCase('vim_read_file_line2', () => {
  const s = newSession();
  s.fs.write('main.txt', 'Line one\nLine two\nLine three');
  s.fs.write('extra.txt', 'Alpha\nBravo');
  feedString(s, 'vim main.txt');
  s.feedKey('Enter');
  s.feedKey('j');   // move to line 2
  s.feedKey(':');
  feedString(s, 'r extra.txt');
  s.feedKey('Enter');
  return {
    description: ':r on line 2 inserts below line 2, cursor on first inserted line',
    frame: snap(s),
  };
});

addCase('vim_read_file_last_line', () => {
  const s = newSession();
  s.fs.write('main.txt', 'Line one\nLine two\nLine three');
  s.fs.write('extra.txt', 'Alpha\nBravo\nCharlie');
  feedString(s, 'vim main.txt');
  s.feedKey('Enter');
  s.feedKey('G');   // move to last line
  s.feedKey(':');
  feedString(s, 'r extra.txt');
  s.feedKey('Enter');
  return {
    description: ':r on last line inserts below, cursor on first inserted line',
    frame: snap(s),
  };
});

addCase('vim_read_nonexistent', () => {
  const s = newSession();
  s.fs.write('main.txt', 'Hello');
  feedString(s, 'vim main.txt');
  s.feedKey('Enter');
  s.feedKey(':');
  feedString(s, 'r nosuchfile.txt');
  s.feedKey('Enter');
  return {
    description: ':r nonexistent file shows E484 error',
    frame: snap(s),
  };
});

addCase('vim_read_no_filename', () => {
  const s = newSession();
  s.fs.write('main.txt', 'Hello');
  feedString(s, 'vim main.txt');
  s.feedKey('Enter');
  s.feedKey(':');
  feedString(s, 'r');
  s.feedKey('Enter');
  return {
    description: ':r with no filename shows E32 error',
    frame: snap(s),
  };
});

// ───────────────────────────────────────────────────────────
// :r Tab completion (matches nvim wildmode=full behavior)
// ───────────────────────────────────────────────────────────

addCase('vim_tab_r_no_partial', () => {
  const s = newSession();
  s.fs.write('main.txt', 'Hello');
  s.fs.write('demo.py', 'def f(): pass');
  s.fs.write('demo.txt', 'some text');
  s.fs.write('notes.txt', 'my notes');
  feedString(s, 'vim main.txt');
  s.feedKey('Enter');
  s.feedKey(':');
  feedString(s, 'r ');
  s.feedKey('Tab');
  return {
    description: ':r <Tab> picks first file alphabetically',
    frame: snap(s),
  };
});

addCase('vim_tab_r_partial_d', () => {
  const s = newSession();
  s.fs.write('main.txt', 'Hello');
  s.fs.write('demo.py', 'def f(): pass');
  s.fs.write('demo.txt', 'some text');
  s.fs.write('notes.txt', 'my notes');
  feedString(s, 'vim main.txt');
  s.feedKey('Enter');
  s.feedKey(':');
  feedString(s, 'r d');
  s.feedKey('Tab');
  return {
    description: ':r d<Tab> picks first match (demo.py)',
    frame: snap(s),
  };
});

addCase('vim_tab_r_partial_d_cycle', () => {
  const s = newSession();
  s.fs.write('main.txt', 'Hello');
  s.fs.write('demo.py', 'def f(): pass');
  s.fs.write('demo.txt', 'some text');
  s.fs.write('notes.txt', 'my notes');
  feedString(s, 'vim main.txt');
  s.feedKey('Enter');
  s.feedKey(':');
  feedString(s, 'r d');
  s.feedKey('Tab');
  s.feedKey('Tab');
  return {
    description: ':r d<Tab><Tab> cycles to second match (demo.txt)',
    frame: snap(s),
  };
});

addCase('vim_tab_r_unique_match', () => {
  const s = newSession();
  s.fs.write('main.txt', 'Hello');
  s.fs.write('demo.py', 'def f(): pass');
  s.fs.write('demo.txt', 'some text');
  s.fs.write('notes.txt', 'my notes');
  feedString(s, 'vim main.txt');
  s.feedKey('Enter');
  s.feedKey(':');
  feedString(s, 'r n');
  s.feedKey('Tab');
  return {
    description: ':r n<Tab> completes to notes.txt (unique match)',
    frame: snap(s),
  };
});

addCase('vim_tab_r_no_match', () => {
  const s = newSession();
  s.fs.write('main.txt', 'Hello');
  s.fs.write('demo.py', 'def f(): pass');
  feedString(s, 'vim main.txt');
  s.feedKey('Enter');
  s.feedKey(':');
  feedString(s, 'r z');
  s.feedKey('Tab');
  return {
    description: ':r z<Tab> no matches, text unchanged',
    frame: snap(s),
  };
});

addCase('vim_tab_e_partial', () => {
  const s = newSession();
  s.fs.write('main.txt', 'Hello');
  s.fs.write('demo.py', 'def f(): pass');
  s.fs.write('demo.txt', 'some text');
  feedString(s, 'vim main.txt');
  s.feedKey('Enter');
  s.feedKey(':');
  feedString(s, 'e d');
  s.feedKey('Tab');
  return {
    description: ':e d<Tab> picks first match (demo.py)',
    frame: snap(s),
  };
});

addCase('vim_tab_w_no_partial', () => {
  const s = newSession();
  s.fs.write('main.txt', 'Hello');
  s.fs.write('demo.py', 'def f(): pass');
  s.fs.write('notes.txt', 'my notes');
  feedString(s, 'vim main.txt');
  s.feedKey('Enter');
  s.feedKey(':');
  feedString(s, 'w ');
  s.feedKey('Tab');
  return {
    description: ':w <Tab> picks first file alphabetically',
    frame: snap(s),
  };
});

addCase('vim_tab_r_dot_partial', () => {
  const s = newSession();
  s.fs.write('main.txt', 'Hello');
  s.fs.write('demo.py', 'def f(): pass');
  s.fs.write('demo.txt', 'some text');
  feedString(s, 'vim main.txt');
  s.feedKey('Enter');
  s.feedKey(':');
  feedString(s, 'r demo.');
  s.feedKey('Tab');
  return {
    description: ':r demo.<Tab> picks first match (demo.py)',
    frame: snap(s),
  };
});

addCase('vim_tab_r_dot_cycle', () => {
  const s = newSession();
  s.fs.write('main.txt', 'Hello');
  s.fs.write('demo.py', 'def f(): pass');
  s.fs.write('demo.txt', 'some text');
  feedString(s, 'vim main.txt');
  s.feedKey('Enter');
  s.feedKey(':');
  feedString(s, 'r demo.');
  s.feedKey('Tab');
  s.feedKey('Tab');
  return {
    description: ':r demo.<Tab><Tab> cycles to second match (demo.txt)',
    frame: snap(s),
  };
});

// ── Write output ──
writeFileSync(OUT_PATH, JSON.stringify(groundTruth, null, 2));
console.log(`Generated ${Object.keys(groundTruth).length} session ground truth cases`);
console.log(`Written to: ${OUT_PATH}`);
