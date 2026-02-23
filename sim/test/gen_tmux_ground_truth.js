/**
 * VimFu Simulator – Tmux Ground Truth Generator
 *
 * Generates ground truth frame snapshots for Tmux scenarios.
 * These cover the full tmux integration including:
 *   - Single pane display (shell inside tmux, vim inside tmux)
 *   - Status bar (session name, window list, active marker, zoom)
 *   - Pane splitting (vertical, horizontal) with border characters
 *   - Pane borders: active vs inactive color
 *   - Window management (create, switch, rename)
 *   - Overlays (command prompt, rename, confirm, pane numbers, help, copy mode)
 *   - SessionManager integration (launch, detach, reattach)
 *   - Mixed content: vim in one pane, shell in another
 *
 * The output is saved as tmux_ground_truth.json and compared by
 * test_tmux_screen.js.
 *
 * Usage:
 *   node test/gen_tmux_ground_truth.js          # generate ground truth
 *   node test/gen_tmux_ground_truth.js --print   # also print frames
 */

import { writeFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';
import { SessionManager } from '../src/session.js';

const __dirname = dirname(fileURLToPath(import.meta.url));
const OUT_PATH = resolve(__dirname, 'tmux_ground_truth.json');

const args = process.argv.slice(2);
const doPrint = args.includes('--print');

const ROWS = 20;
const COLS = 40;

// ── Helpers ──

function newSession(opts = {}) {
  return new SessionManager({
    rows: ROWS, cols: COLS, persist: false, ...opts,
  });
}

function feedString(s, str) {
  for (const ch of str) s.feedKey(ch);
}

function snap(s) {
  return s.renderFrame();
}

function printFrame(label, frame) {
  if (!doPrint) return;
  console.log(`\n── ${label} ──`);
  for (let i = 0; i < frame.lines.length; i++) {
    const l = frame.lines[i];
    const runsStr = l.runs.map(r => `${r.n}:${r.fg}/${r.bg}`).join(' ');
    console.log(`  ${String(i).padStart(2)}: ${JSON.stringify(l.text)}  [${runsStr}]`);
  }
  console.log(`  cursor: (${frame.cursor.row}, ${frame.cursor.col}) visible=${frame.cursor.visible} shape=${frame.cursor.shape || 'block'}`);
}

// ── Scenarios ──

const groundTruth = {};

function addCase(name, fn) {
  const { frame, description } = fn();
  // Freeze out the clock/time from the status bar since it changes every minute
  // Replace the time portion with a fixed placeholder
  freezeStatusBarTime(frame);
  groundTruth[name] = {
    description,
    frame,
    cursor: frame.cursor,
    textLines: frame.lines.map(l => l.text),
  };
  printFrame(name, frame);
}

/**
 * The tmux status bar includes a live clock (HH:MM) and date.
 * Since these change between generation and test runs, we replace
 * them with fixed placeholders. The test runner does the same
 * substitution before comparing.
 */
function freezeStatusBarTime(frame) {
  const lastRow = frame.lines.length - 1;
  if (lastRow < 0) return;
  // Replace time pattern HH:MM with 00:00 and date pattern DD-Mon-YY with 01-Jan-26
  let text = frame.lines[lastRow].text;
  text = text.replace(/\d{2}:\d{2}/, '00:00');
  text = text.replace(/\d{1,2}-[A-Z][a-z]{2}-\d{2}/, '01-Jan-26');
  frame.lines[lastRow].text = text;
}

// ───────────────────────────────────────────────────────────
// Basic tmux launch
// ───────────────────────────────────────────────────────────

addCase('tmux_fresh_launch', () => {
  const s = newSession();
  feedString(s, 'tmux');
  s.feedKey('Enter');
  return {
    description: 'Fresh tmux launch — single pane with shell, green status bar',
    frame: snap(s),
  };
});

addCase('tmux_type_in_shell', () => {
  const s = newSession();
  feedString(s, 'tmux');
  s.feedKey('Enter');
  feedString(s, 'echo hello');
  s.feedKey('Enter');
  return {
    description: 'Tmux pane after running echo hello',
    frame: snap(s),
  };
});

addCase('tmux_ls_in_pane', () => {
  const s = newSession();
  s.fs.write('foo.txt', 'foo');
  s.fs.write('bar.txt', 'bar');
  feedString(s, 'tmux');
  s.feedKey('Enter');
  feedString(s, 'ls');
  s.feedKey('Enter');
  return {
    description: 'Tmux pane after ls showing files',
    frame: snap(s),
  };
});

// ───────────────────────────────────────────────────────────
// Vim inside tmux
// ───────────────────────────────────────────────────────────

addCase('tmux_vim_launch', () => {
  const s = newSession();
  feedString(s, 'tmux');
  s.feedKey('Enter');
  feedString(s, 'vim test.txt');
  s.feedKey('Enter');
  return {
    description: 'Vim launched inside a tmux pane',
    frame: snap(s),
  };
});

addCase('tmux_vim_with_content', () => {
  const s = newSession();
  s.fs.write('hello.txt', 'Hello World\nSecond line\nThird line');
  feedString(s, 'tmux');
  s.feedKey('Enter');
  feedString(s, 'vim hello.txt');
  s.feedKey('Enter');
  return {
    description: 'Vim with existing file in a tmux pane',
    frame: snap(s),
  };
});

addCase('tmux_vim_insert_and_quit', () => {
  const s = newSession();
  feedString(s, 'tmux');
  s.feedKey('Enter');
  feedString(s, 'vim test.txt');
  s.feedKey('Enter');
  s.feedKey('i');
  feedString(s, 'typed in tmux');
  s.feedKey('Escape');
  s.feedKey(':');
  feedString(s, 'wq');
  s.feedKey('Enter');
  return {
    description: 'Back to shell after :wq inside tmux',
    frame: snap(s),
  };
});

// ───────────────────────────────────────────────────────────
// Vertical split
// ───────────────────────────────────────────────────────────

addCase('tmux_vsplit', () => {
  const s = newSession();
  feedString(s, 'tmux');
  s.feedKey('Enter');
  s.feedKey('Ctrl-B');
  s.feedKey('%');
  return {
    description: 'Vertical split — two panes side by side with border',
    frame: snap(s),
  };
});

addCase('tmux_vsplit_type_left', () => {
  const s = newSession();
  feedString(s, 'tmux');
  s.feedKey('Enter');
  // Type in first pane
  feedString(s, 'echo LEFT');
  s.feedKey('Enter');
  // Split vertically
  s.feedKey('Ctrl-B');
  s.feedKey('%');
  // Go back to left pane
  s.feedKey('Ctrl-B');
  s.feedKey('ArrowLeft');
  return {
    description: 'Vsplit with LEFT text in left pane, cursor in left pane',
    frame: snap(s),
  };
});

addCase('tmux_vsplit_type_both', () => {
  const s = newSession();
  feedString(s, 'tmux');
  s.feedKey('Enter');
  feedString(s, 'echo LEFT');
  s.feedKey('Enter');
  s.feedKey('Ctrl-B');
  s.feedKey('%');
  feedString(s, 'echo RIGHT');
  s.feedKey('Enter');
  return {
    description: 'Vsplit with different content in each pane',
    frame: snap(s),
  };
});

// ───────────────────────────────────────────────────────────
// Horizontal split
// ───────────────────────────────────────────────────────────

addCase('tmux_hsplit', () => {
  const s = newSession();
  feedString(s, 'tmux');
  s.feedKey('Enter');
  s.feedKey('Ctrl-B');
  s.feedKey('"');
  return {
    description: 'Horizontal split — two panes stacked with border',
    frame: snap(s),
  };
});

addCase('tmux_hsplit_type_both', () => {
  const s = newSession();
  feedString(s, 'tmux');
  s.feedKey('Enter');
  feedString(s, 'echo TOP');
  s.feedKey('Enter');
  s.feedKey('Ctrl-B');
  s.feedKey('"');
  feedString(s, 'echo BOTTOM');
  s.feedKey('Enter');
  return {
    description: 'Hsplit with different content in each pane',
    frame: snap(s),
  };
});

// ───────────────────────────────────────────────────────────
// Mixed splits (3+ panes)
// ───────────────────────────────────────────────────────────

addCase('tmux_three_panes', () => {
  const s = newSession();
  feedString(s, 'tmux');
  s.feedKey('Enter');
  s.feedKey('Ctrl-B');
  s.feedKey('%');  // vsplit
  s.feedKey('Ctrl-B');
  s.feedKey('"');  // hsplit the right pane
  return {
    description: 'Three panes: left full-height, right split top/bottom',
    frame: snap(s),
  };
});

addCase('tmux_four_panes', () => {
  const s = newSession({ rows: 24, cols: 80 });
  feedString(s, 'tmux');
  s.feedKey('Enter');
  s.feedKey('Ctrl-B');
  s.feedKey('%');  // vsplit
  s.feedKey('Ctrl-B');
  s.feedKey('"');  // hsplit right pane
  // Go to left pane and hsplit it too
  s.feedKey('Ctrl-B');
  s.feedKey('ArrowLeft');
  s.feedKey('Ctrl-B');
  s.feedKey('"');  // hsplit left pane
  return {
    description: 'Four panes in a 2x2 grid',
    frame: snap(s),
  };
});

addCase('tmux_vim_and_shell_split', () => {
  const s = newSession();
  s.fs.write('code.txt', 'line 1\nline 2\nline 3');
  feedString(s, 'tmux');
  s.feedKey('Enter');
  feedString(s, 'vim code.txt');
  s.feedKey('Enter');
  s.feedKey('Ctrl-B');
  s.feedKey('%');  // vsplit — right pane gets a shell
  return {
    description: 'Left pane: vim with file, right pane: fresh shell',
    frame: snap(s),
  };
});

// ───────────────────────────────────────────────────────────
// Pane navigation
// ───────────────────────────────────────────────────────────

addCase('tmux_navigate_left', () => {
  const s = newSession();
  feedString(s, 'tmux');
  s.feedKey('Enter');
  feedString(s, 'echo PANE0');
  s.feedKey('Enter');
  s.feedKey('Ctrl-B');
  s.feedKey('%');
  feedString(s, 'echo PANE1');
  s.feedKey('Enter');
  s.feedKey('Ctrl-B');
  s.feedKey('ArrowLeft');
  return {
    description: 'After navigating left, cursor in left pane',
    frame: snap(s),
  };
});

addCase('tmux_navigate_cycle_o', () => {
  const s = newSession();
  feedString(s, 'tmux');
  s.feedKey('Enter');
  s.feedKey('Ctrl-B');
  s.feedKey('%');
  // Active is right pane
  s.feedKey('Ctrl-B');
  s.feedKey('o');  // cycle to left
  s.feedKey('Ctrl-B');
  s.feedKey('o');  // cycle back to right
  return {
    description: 'After cycling twice, cursor back in right pane',
    frame: snap(s),
  };
});

// ───────────────────────────────────────────────────────────
// Status bar variations
// ───────────────────────────────────────────────────────────

addCase('tmux_status_bar_single_window', () => {
  const s = newSession();
  feedString(s, 'tmux');
  s.feedKey('Enter');
  return {
    description: 'Status bar with single window: [0] 0:zsh*',
    frame: snap(s),
  };
});

addCase('tmux_status_bar_two_windows', () => {
  const s = newSession();
  feedString(s, 'tmux');
  s.feedKey('Enter');
  s.feedKey('Ctrl-B');
  s.feedKey('c');
  return {
    description: 'Status bar with two windows, second active',
    frame: snap(s),
  };
});

addCase('tmux_status_bar_three_windows', () => {
  const s = newSession();
  feedString(s, 'tmux');
  s.feedKey('Enter');
  s.feedKey('Ctrl-B');
  s.feedKey('c');
  s.feedKey('Ctrl-B');
  s.feedKey('c');
  // Go to middle window
  s.feedKey('Ctrl-B');
  s.feedKey('1');
  return {
    description: 'Status bar with three windows, middle active',
    frame: snap(s),
  };
});

addCase('tmux_status_bar_renamed', () => {
  const s = newSession();
  feedString(s, 'tmux');
  s.feedKey('Enter');
  s.feedKey('Ctrl-B');
  s.feedKey(',');
  s.feedKey('Ctrl-U');
  feedString(s, 'myterm');
  s.feedKey('Enter');
  return {
    description: 'Status bar after renaming window to myterm',
    frame: snap(s),
  };
});

addCase('tmux_status_bar_zoomed', () => {
  const s = newSession();
  feedString(s, 'tmux');
  s.feedKey('Enter');
  s.feedKey('Ctrl-B');
  s.feedKey('%');
  s.feedKey('Ctrl-B');
  s.feedKey('z');
  return {
    description: 'Status bar with Z zoom indicator',
    frame: snap(s),
  };
});

// ───────────────────────────────────────────────────────────
// Command prompt overlay
// ───────────────────────────────────────────────────────────

addCase('tmux_command_prompt_empty', () => {
  const s = newSession();
  feedString(s, 'tmux');
  s.feedKey('Enter');
  s.feedKey('Ctrl-B');
  s.feedKey(':');
  return {
    description: 'Command prompt with empty input',
    frame: snap(s),
  };
});

addCase('tmux_command_prompt_typed', () => {
  const s = newSession();
  feedString(s, 'tmux');
  s.feedKey('Enter');
  s.feedKey('Ctrl-B');
  s.feedKey(':');
  feedString(s, 'split-window');
  return {
    description: 'Command prompt with "split-window" typed',
    frame: snap(s),
  };
});

// ───────────────────────────────────────────────────────────
// Rename overlay
// ───────────────────────────────────────────────────────────

addCase('tmux_rename_prompt', () => {
  const s = newSession();
  feedString(s, 'tmux');
  s.feedKey('Enter');
  s.feedKey('Ctrl-B');
  s.feedKey(',');
  return {
    description: 'Rename window prompt shown on status bar',
    frame: snap(s),
  };
});

addCase('tmux_rename_prompt_typed', () => {
  const s = newSession();
  feedString(s, 'tmux');
  s.feedKey('Enter');
  s.feedKey('Ctrl-B');
  s.feedKey(',');
  s.feedKey('Ctrl-U');
  feedString(s, 'editor');
  return {
    description: 'Rename prompt after clearing and typing "editor"',
    frame: snap(s),
  };
});

// ───────────────────────────────────────────────────────────
// Confirm prompt
// ───────────────────────────────────────────────────────────

addCase('tmux_confirm_kill', () => {
  const s = newSession();
  feedString(s, 'tmux');
  s.feedKey('Enter');
  s.feedKey('Ctrl-B');
  s.feedKey('x');
  return {
    description: 'Kill pane confirmation prompt',
    frame: snap(s),
  };
});

// ───────────────────────────────────────────────────────────
// Copy mode
// ───────────────────────────────────────────────────────────

addCase('tmux_copy_mode', () => {
  const s = newSession();
  feedString(s, 'tmux');
  s.feedKey('Enter');
  s.feedKey('Ctrl-B');
  s.feedKey('[');
  return {
    description: 'Copy mode with yellow status bar indicator',
    frame: snap(s),
  };
});

addCase('tmux_copy_mode_moved', () => {
  const s = newSession();
  feedString(s, 'tmux');
  s.feedKey('Enter');
  s.feedKey('Ctrl-B');
  s.feedKey('[');
  s.feedKey('l');
  s.feedKey('l');
  s.feedKey('j');
  return {
    description: 'Copy mode after moving cursor (1,2)',
    frame: snap(s),
  };
});

// ───────────────────────────────────────────────────────────
// Pane close results
// ───────────────────────────────────────────────────────────

addCase('tmux_close_pane', () => {
  const s = newSession();
  feedString(s, 'tmux');
  s.feedKey('Enter');
  s.feedKey('Ctrl-B');
  s.feedKey('%');
  s.feedKey('Ctrl-B');
  s.feedKey('x');
  s.feedKey('y');
  return {
    description: 'After closing right pane, back to single pane',
    frame: snap(s),
  };
});

// ───────────────────────────────────────────────────────────
// Window switching
// ───────────────────────────────────────────────────────────

addCase('tmux_switch_window', () => {
  const s = newSession();
  feedString(s, 'tmux');
  s.feedKey('Enter');
  feedString(s, 'echo WIN0');
  s.feedKey('Enter');
  s.feedKey('Ctrl-B');
  s.feedKey('c');
  feedString(s, 'echo WIN1');
  s.feedKey('Enter');
  s.feedKey('Ctrl-B');
  s.feedKey('0');
  return {
    description: 'Switched back to window 0 with WIN0 content',
    frame: snap(s),
  };
});

// ───────────────────────────────────────────────────────────
// Detach and reattach
// ───────────────────────────────────────────────────────────

addCase('tmux_detach_shell', () => {
  const s = newSession();
  feedString(s, 'tmux');
  s.feedKey('Enter');
  s.feedKey('Ctrl-B');
  s.feedKey('d');
  return {
    description: 'Shell after tmux detach — shows detached message',
    frame: snap(s),
  };
});

addCase('tmux_reattach', () => {
  const s = newSession();
  feedString(s, 'tmux');
  s.feedKey('Enter');
  feedString(s, 'echo PERSISTENT');
  s.feedKey('Enter');
  s.feedKey('Ctrl-B');
  s.feedKey('d');
  feedString(s, 'tmux attach');
  s.feedKey('Enter');
  return {
    description: 'Reattached tmux showing PERSISTENT from before detach',
    frame: snap(s),
  };
});

// ───────────────────────────────────────────────────────────
// Help overlay
// ───────────────────────────────────────────────────────────

addCase('tmux_help', () => {
  const s = newSession();
  feedString(s, 'tmux');
  s.feedKey('Enter');
  s.feedKey('Ctrl-B');
  s.feedKey('?');
  return {
    description: 'Help overlay with keybinding list',
    frame: snap(s),
  };
});

// ───────────────────────────────────────────────────────────
// Pane numbers overlay
// ───────────────────────────────────────────────────────────

addCase('tmux_pane_numbers', () => {
  const s = newSession();
  feedString(s, 'tmux');
  s.feedKey('Enter');
  s.feedKey('Ctrl-B');
  s.feedKey('%');
  s.feedKey('Ctrl-B');
  s.feedKey('q');
  return {
    description: 'Pane number overlay showing 0 and 1',
    frame: snap(s),
  };
});

// ───────────────────────────────────────────────────────────
// Break pane to window
// ───────────────────────────────────────────────────────────

addCase('tmux_break_pane', () => {
  const s = newSession();
  feedString(s, 'tmux');
  s.feedKey('Enter');
  feedString(s, 'echo ORIGINAL');
  s.feedKey('Enter');
  s.feedKey('Ctrl-B');
  s.feedKey('%');
  feedString(s, 'echo BROKEN_OUT');
  s.feedKey('Enter');
  s.feedKey('Ctrl-B');
  s.feedKey('!');
  return {
    description: 'After break-pane, pane is now its own window',
    frame: snap(s),
  };
});

// ───────────────────────────────────────────────────────────
// Zoom
// ───────────────────────────────────────────────────────────

addCase('tmux_zoom_pane', () => {
  const s = newSession();
  feedString(s, 'tmux');
  s.feedKey('Enter');
  s.feedKey('Ctrl-B');
  s.feedKey('%');
  feedString(s, 'echo ZOOMED');
  s.feedKey('Enter');
  s.feedKey('Ctrl-B');
  s.feedKey('z');
  return {
    description: 'Zoomed pane takes full width, Z in status bar',
    frame: snap(s),
  };
});

addCase('tmux_zoom_unzoom', () => {
  const s = newSession();
  feedString(s, 'tmux');
  s.feedKey('Enter');
  s.feedKey('Ctrl-B');
  s.feedKey('%');
  s.feedKey('Ctrl-B');
  s.feedKey('z');
  s.feedKey('Ctrl-B');
  s.feedKey('z');
  return {
    description: 'Unzoomed pane — back to split view',
    frame: snap(s),
  };
});

// ───────────────────────────────────────────────────────────
// Border colors (active vs inactive)
// ───────────────────────────────────────────────────────────

addCase('tmux_vsplit_active_right', () => {
  const s = newSession();
  feedString(s, 'tmux');
  s.feedKey('Enter');
  s.feedKey('Ctrl-B');
  s.feedKey('%');
  // Active pane is right (the new one after split)
  return {
    description: 'Vsplit with right pane active — border should be green',
    frame: snap(s),
  };
});

addCase('tmux_vsplit_active_left', () => {
  const s = newSession();
  feedString(s, 'tmux');
  s.feedKey('Enter');
  s.feedKey('Ctrl-B');
  s.feedKey('%');
  s.feedKey('Ctrl-B');
  s.feedKey('ArrowLeft');
  // Active pane is left
  return {
    description: 'Vsplit with left pane active — border still adjacent to active',
    frame: snap(s),
  };
});

// ───────────────────────────────────────────────────────────
// Window list overlay
// ───────────────────────────────────────────────────────────

addCase('tmux_window_list', () => {
  const s = newSession();
  feedString(s, 'tmux');
  s.feedKey('Enter');
  s.feedKey('Ctrl-B');
  s.feedKey('c');
  s.feedKey('Ctrl-B');
  s.feedKey('c');
  s.feedKey('Ctrl-B');
  s.feedKey('w');
  return {
    description: 'Window list chooser with 3 windows',
    frame: snap(s),
  };
});

// ───────────────────────────────────────────────────────────
// Save and finish
// ───────────────────────────────────────────────────────────

const caseCount = Object.keys(groundTruth).length;
writeFileSync(OUT_PATH, JSON.stringify(groundTruth, null, 2));
console.log(`\nGenerated ${caseCount} tmux ground truth cases → ${OUT_PATH}`);
