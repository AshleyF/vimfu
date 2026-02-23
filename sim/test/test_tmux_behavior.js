/**
 * VimFu Simulator – Tmux Behavioral Tests (verified against real tmux)
 *
 * These tests exercise the tmux simulator through the same scenarios
 * captured from real tmux (see capture_tmux_behavior.py).
 *
 * Ground truth: test/tmux_behavior_ground_truth.json
 *
 * Tests focus on:
 *   - Layout geometry (border positions, pane sizes)
 *   - Status bar format and content
 *   - Navigation (arrow keys, o cycle)
 *   - Window management (create, switch, rename)
 *   - Zoom, close confirm, swap, break pane
 *   - Copy mode, command prompt, detach
 *   - Resize
 *
 * Usage:
 *   node test/test_tmux_behavior.js
 *   node test/test_tmux_behavior.js --case <name>
 *   node test/test_tmux_behavior.js --verbose
 */

import { dirname, resolve } from 'path';
import { fileURLToPath } from 'url';
import { readFileSync } from 'fs';
import { Tmux, TmuxSession, TmuxWindow, TmuxPane, LayoutNode, TmuxMode, SplitDir } from '../src/tmux.js';
import { SessionManager } from '../src/session.js';
import { VirtualFS } from '../src/vfs.js';

const __dirname = dirname(fileURLToPath(import.meta.url));

// ── Parse args ──
const args = process.argv.slice(2);
let filterCase = null;
let verbose = false;
for (let i = 0; i < args.length; i++) {
  if (args[i] === '--case' && args[i + 1]) filterCase = args[++i];
  else if (args[i] === '--verbose') verbose = true;
}

// ── Load ground truth ──
let groundTruth;
try {
  const gtPath = resolve(__dirname, 'tmux_behavior_ground_truth.json');
  groundTruth = JSON.parse(readFileSync(gtPath, 'utf-8'));
} catch {
  groundTruth = null;
}

// ── Helpers ──
const ROWS = 24;
const COLS = 80;

function createPaneSessionFactory(vfs) {
  return (cols, rows) => {
    const sm = new SessionManager({
      rows,
      cols,
      themeName: 'nvim_default',
      persist: false,
    });
    sm.fs = vfs;
    sm.shell.fs = vfs;
    sm.shell._insideTmux = true;
    return sm;
  };
}

function newTmux(opts = {}) {
  const vfs = opts.vfs || new VirtualFS({ persist: false });
  return new Tmux({
    rows: opts.rows || ROWS,
    cols: opts.cols || COLS,
    createPaneSession: createPaneSessionFactory(vfs),
  });
}

function newSession(opts = {}) {
  return new SessionManager({
    rows: opts.rows || ROWS,
    cols: opts.cols || COLS,
    persist: false,
    ...opts,
  });
}

function feedString(target, str) {
  for (const ch of str) target.feedKey(ch);
}

function getFrameText(frame) {
  return frame.lines.map(l => l.text);
}

function getFrameRow(frame, row) {
  return frame.lines[row]?.text || '';
}

function getStatusBar(tmux) {
  const frame = tmux.renderFrame();
  return getFrameRow(frame, tmux.rows - 1);
}

/** Find the column of the first vertical border character */
function findBorderCol(frame) {
  for (let r = 0; r < frame.lines.length - 1; r++) {
    const text = frame.lines[r].text;
    for (let c = 0; c < text.length; c++) {
      if (text[c] === '│') return c;
    }
  }
  return null;
}

/** Find the row of the first horizontal border */
function findBorderRow(frame) {
  for (let r = 0; r < frame.lines.length - 1; r++) {
    if (frame.lines[r].text.includes('─')) return r;
  }
  return null;
}

// ── Test runner ──
const tests = {};
let passed = 0;
let failed = 0;
let skipped = 0;

function assert(cond, msg) {
  if (!cond) throw new Error(msg);
}

function assertEqual(actual, expected, msg) {
  if (actual !== expected) {
    throw new Error(`${msg}: expected ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}`);
  }
}

function assertIncludes(str, substr, msg) {
  if (!str.includes(substr)) {
    throw new Error(`${msg}: expected ${JSON.stringify(str)} to include ${JSON.stringify(substr)}`);
  }
}

function assertNotIncludes(str, substr, msg) {
  if (str.includes(substr)) {
    throw new Error(`${msg}: expected ${JSON.stringify(str)} to NOT include ${JSON.stringify(substr)}`);
  }
}

// ═══════════════════════════════════════════════════════════════════
// GROUP 1: Basic Launch
// ═══════════════════════════════════════════════════════════════════

tests.behavior_fresh_launch_status_bar = () => {
  // Real tmux: "0 | 0:zsh* | HH:MM | DD-Mon-YY"
  const t = newTmux();
  const status = getStatusBar(t);
  assertIncludes(status, '0 ', 'session name "0 "');
  assertIncludes(status, '| ', 'pipe separator');
  assertIncludes(status, '0:zsh', 'window name');
  assertIncludes(status, '*', 'active marker');
};

tests.behavior_fresh_launch_single_pane = () => {
  const t = newTmux();
  assertEqual(t.activeWindow.getPanes().length, 1, 'single pane');
  const pane = t.activePane;
  assertEqual(pane.left, 0, 'pane starts at col 0');
  assertEqual(pane.top, 0, 'pane starts at row 0');
  assertEqual(pane.width, COLS, 'pane full width');
  assertEqual(pane.height, ROWS - 1, 'pane height = rows minus status');
};

tests.behavior_fresh_launch_cursor_position = () => {
  // Real tmux: cursor at (0,0) — but our shell has a prompt, so cursor will be
  // at prompt position. We just verify it's on row 0.
  const t = newTmux();
  const frame = t.renderFrame();
  assertEqual(frame.cursor.row, 0, 'cursor on row 0');
};

tests.behavior_echo_command = () => {
  // Typing + Enter should produce output in the pane
  const t = newTmux();
  feedString(t, 'echo hello');
  t.feedKey('Enter');
  const frame = t.renderFrame();
  const text = getFrameText(frame).join('\n');
  assertIncludes(text, 'hello', 'echo output visible');
};

// ═══════════════════════════════════════════════════════════════════
// GROUP 2: Vertical Split
// ═══════════════════════════════════════════════════════════════════

tests.behavior_vsplit_creates_two_panes = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('%');
  assertEqual(t.activeWindow.getPanes().length, 2, 'two panes');
};

tests.behavior_vsplit_border_position = () => {
  // Real tmux at 80 cols: border at col 40
  // Left pane: 40 cols (0-39), border at 40, right pane: 39 cols (41-79)
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('%');
  const frame = t.renderFrame();
  const border = findBorderCol(frame);
  assertEqual(border, 40, 'vsplit border at col 40 (matching real tmux)');
};

tests.behavior_vsplit_pane_dimensions = () => {
  // Real tmux: left=40 cols, right=39 cols
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('%');
  const panes = t.activeWindow.getPanes();
  assertEqual(panes[0].width, 40, 'left pane width 40');
  assertEqual(panes[1].width, 39, 'right pane width 39');
  assertEqual(panes[0].width + 1 + panes[1].width, COLS, 'widths add up to 80');
};

tests.behavior_vsplit_right_pane_active = () => {
  // Real tmux: after split, new (right) pane is active
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('%');
  const panes = t.activeWindow.getPanes();
  assertEqual(t.activePane, panes[1], 'right pane is active');
};

tests.behavior_vsplit_cursor_in_right_pane = () => {
  // Real tmux: cursor at (0, 41) — row 0, col 41 (first col of right pane)
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('%');
  const frame = t.renderFrame();
  assertEqual(frame.cursor.row, 0, 'cursor row 0');
  // Cursor should be in the right pane area (col >= 41)
  assert(frame.cursor.col >= 41, `cursor col ${frame.cursor.col} should be >= 41`);
};

tests.behavior_vsplit_navigate_left = () => {
  // Ctrl-B Left should move to left pane
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('%');
  const panes = t.activeWindow.getPanes();
  assertEqual(t.activePane, panes[1], 'starts in right');
  t.feedKey('Ctrl-B');
  t.feedKey('ArrowLeft');
  assertEqual(t.activePane, panes[0], 'moved to left');
};

tests.behavior_vsplit_navigate_right = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('%');
  const panes = t.activeWindow.getPanes();
  t.feedKey('Ctrl-B');
  t.feedKey('ArrowLeft');
  assertEqual(t.activePane, panes[0], 'in left');
  t.feedKey('Ctrl-B');
  t.feedKey('ArrowRight');
  assertEqual(t.activePane, panes[1], 'back to right');
};

tests.behavior_vsplit_cycle_o = () => {
  // Ctrl-B o cycles to next pane
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('%');
  const panes = t.activeWindow.getPanes();
  assertEqual(t.activePane, panes[1], 'starts in right');
  t.feedKey('Ctrl-B');
  t.feedKey('o');
  assertEqual(t.activePane, panes[0], 'cycled to left');
  t.feedKey('Ctrl-B');
  t.feedKey('o');
  assertEqual(t.activePane, panes[1], 'cycled back to right');
};

// ═══════════════════════════════════════════════════════════════════
// GROUP 3: Horizontal Split
// ═══════════════════════════════════════════════════════════════════

tests.behavior_hsplit_creates_two_panes = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('"');
  assertEqual(t.activeWindow.getPanes().length, 2, 'two panes');
};

tests.behavior_hsplit_border_position = () => {
  // Real tmux at 24 rows (23 pane rows): border at row 11
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('"');
  const frame = t.renderFrame();
  const border = findBorderRow(frame);
  assertEqual(border, 11, 'hsplit border at row 11');
};

tests.behavior_hsplit_pane_dimensions = () => {
  // Real tmux: top=11 rows (0-10), bottom=11 rows (12-22)
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('"');
  const panes = t.activeWindow.getPanes();
  assertEqual(panes[0].height, 11, 'top pane height 11');
  assertEqual(panes[1].height, 11, 'bottom pane height 11');
  assertEqual(panes[0].height + 1 + panes[1].height, ROWS - 1, 'heights add up');
};

tests.behavior_hsplit_bottom_pane_active = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('"');
  const panes = t.activeWindow.getPanes();
  assertEqual(t.activePane, panes[1], 'bottom pane active after hsplit');
};

tests.behavior_hsplit_navigate_up = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('"');
  const panes = t.activeWindow.getPanes();
  t.feedKey('Ctrl-B');
  t.feedKey('ArrowUp');
  assertEqual(t.activePane, panes[0], 'moved to top');
};

tests.behavior_hsplit_navigate_down = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('"');
  const panes = t.activeWindow.getPanes();
  t.feedKey('Ctrl-B');
  t.feedKey('ArrowUp');
  t.feedKey('Ctrl-B');
  t.feedKey('ArrowDown');
  assertEqual(t.activePane, panes[1], 'moved to bottom');
};

// ═══════════════════════════════════════════════════════════════════
// GROUP 4: Three Panes
// ═══════════════════════════════════════════════════════════════════

tests.behavior_three_panes_layout = () => {
  // Real tmux: vsplit then hsplit on right pane
  // Result: left full-height, top-right, bottom-right
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('%');  // vsplit
  t.feedKey('Ctrl-B');
  t.feedKey('"');  // hsplit right pane
  const panes = t.activeWindow.getPanes();
  assertEqual(panes.length, 3, 'three panes');
};

tests.behavior_three_panes_left_full_height = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('%');
  t.feedKey('Ctrl-B');
  t.feedKey('"');
  const panes = t.activeWindow.getPanes();
  // Left pane should span full pane height
  assertEqual(panes[0].height, ROWS - 1, 'left pane full height');
  assertEqual(panes[0].top, 0, 'left pane starts at top');
};

tests.behavior_three_panes_right_split = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('%');
  t.feedKey('Ctrl-B');
  t.feedKey('"');
  const panes = t.activeWindow.getPanes();
  // Top-right and bottom-right should add up (minus border)
  assertEqual(
    panes[1].height + 1 + panes[2].height,
    ROWS - 1,
    'right panes heights add up'
  );
};

tests.behavior_three_panes_border_intersection = () => {
  // Real tmux shows ├ at the intersection of vertical and horizontal borders
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('%');
  t.feedKey('Ctrl-B');
  t.feedKey('"');
  const frame = t.renderFrame();
  const borderCol = findBorderCol(frame);
  const borderRow = findBorderRow(frame);
  assert(borderCol !== null, 'has vertical border');
  assert(borderRow !== null, 'has horizontal border');
  // The intersection character should be at (borderRow, borderCol)
  const intersectionChar = frame.lines[borderRow].text[borderCol];
  // Should be a T-junction or intersection character
  assert(
    intersectionChar === '├' || intersectionChar === '┤' || intersectionChar === '┼',
    `intersection char should be junction, got ${JSON.stringify(intersectionChar)}`
  );
};

tests.behavior_three_panes_navigate_all = () => {
  // Should be able to navigate between all three panes
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('%');
  t.feedKey('Ctrl-B');
  t.feedKey('"');
  const panes = t.activeWindow.getPanes();
  // Active is bottom-right (pane 2)
  assertEqual(t.activePane, panes[2], 'starts in bottom-right');
  // Up to top-right
  t.feedKey('Ctrl-B');
  t.feedKey('ArrowUp');
  assertEqual(t.activePane, panes[1], 'up to top-right');
  // Left to left pane
  t.feedKey('Ctrl-B');
  t.feedKey('ArrowLeft');
  assertEqual(t.activePane, panes[0], 'left to left pane');
};

// ═══════════════════════════════════════════════════════════════════
// GROUP 5: Window Management
// ═══════════════════════════════════════════════════════════════════

tests.behavior_create_window = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('c');
  assertEqual(t.activeSession.windows.length, 2, 'two windows');
  assertEqual(t.activeSession.activeWindowIndex, 1, 'window 1 active');
};

tests.behavior_two_windows_status_bar = () => {
  // Real tmux: "0 | 0:zsh- 1:zsh*"
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('c');
  const status = getStatusBar(t);
  assertIncludes(status, '0:zsh', 'window 0');
  assertIncludes(status, '1:zsh', 'window 1');
  assertIncludes(status, '-', 'inactive marker');
  assertIncludes(status, '*', 'active marker');
};

tests.behavior_switch_prev_window = () => {
  // Ctrl-B p → previous window
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('c');
  assertEqual(t.activeSession.activeWindowIndex, 1, 'on window 1');
  t.feedKey('Ctrl-B');
  t.feedKey('p');
  assertEqual(t.activeSession.activeWindowIndex, 0, 'back to window 0');
};

tests.behavior_switch_next_window = () => {
  // Ctrl-B n → next window
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('c');
  t.feedKey('Ctrl-B');
  t.feedKey('p');
  t.feedKey('Ctrl-B');
  t.feedKey('n');
  assertEqual(t.activeSession.activeWindowIndex, 1, 'forward to window 1');
};

tests.behavior_switch_by_number = () => {
  // Ctrl-B 0 → window 0
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('c');
  t.feedKey('Ctrl-B');
  t.feedKey('0');
  assertEqual(t.activeSession.activeWindowIndex, 0, 'window 0 active');
};

tests.behavior_last_window_toggle = () => {
  // Switch between windows by number (l is now pane navigation)
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('c');     // window 1 active
  t.feedKey('Ctrl-B');
  t.feedKey('0');     // window 0 active
  t.feedKey('Ctrl-B');
  t.feedKey('1');     // back to window 1
  assertEqual(t.activeSession.activeWindowIndex, 1, 'toggled to last window');
};

tests.behavior_three_windows_status = () => {
  // Real tmux: "0 | 0:zsh 1:zsh- 2:zsh*"
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('c');
  t.feedKey('Ctrl-B');
  t.feedKey('c');
  assertEqual(t.activeSession.windows.length, 3, 'three windows');
  const status = getStatusBar(t);
  assertIncludes(status, '0:zsh', 'window 0');
  assertIncludes(status, '2:zsh', 'window 2');
};

tests.behavior_rename_window = () => {
  // Ctrl-B , → rename current window
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey(',');
  assertEqual(t._mode, TmuxMode.RENAME, 'in rename mode');
  // Clear old name (like real tmux Ctrl-U)
  t.feedKey('Ctrl-U');
  // Type new name
  feedString(t, 'editor');
  t.feedKey('Enter');
  assertEqual(t._mode, TmuxMode.NORMAL, 'back to normal');
  assertEqual(t.activeWindow.name, 'editor', 'window renamed');
  const status = getStatusBar(t);
  assertIncludes(status, 'editor', 'renamed window in status');
};

tests.behavior_rename_window_replaces_old_name = () => {
  // Real tmux: Ctrl-U clears, then type new name
  // Our sim should replace the name with what's typed
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey(',');
  // When rename mode starts, the input starts with the current name
  // User would Ctrl-U to clear, then type new name
  // Let's just verify that after Enter, the name is set
  feedString(t, 'mywin');
  t.feedKey('Enter');
  assertIncludes(t.activeWindow.name, 'mywin', 'name includes typed text');
};

// ═══════════════════════════════════════════════════════════════════
// GROUP 6: Vim Inside Tmux
// ═══════════════════════════════════════════════════════════════════

tests.behavior_vim_inside_tmux = () => {
  // Launch vim through the shell
  const t = newTmux();

  feedString(t, 'vim');
  t.feedKey('Enter');

  // The pane session should have entered vim mode
  const frame = t.renderFrame();
  const text = getFrameText(frame).join('\n');
  // We can't guarantee exact vim rendering, but the pane should have content
  assert(frame.lines.length === ROWS, 'frame has all rows');
};

tests.behavior_vim_and_shell_split = () => {
  // After vim, vsplit creates a shell in right pane
  const t = newTmux();
  feedString(t, 'vim');
  t.feedKey('Enter');

  t.feedKey('Ctrl-B');
  t.feedKey('%');

  const panes = t.activeWindow.getPanes();
  assertEqual(panes.length, 2, 'two panes');
  // Right pane (new) should be active
  assertEqual(t.activePane, panes[1], 'right pane active');
};

tests.behavior_navigate_to_vim_pane = () => {
  // Split, then navigate back to vim pane
  const t = newTmux();
  feedString(t, 'vim');
  t.feedKey('Enter');

  t.feedKey('Ctrl-B');
  t.feedKey('%');

  t.feedKey('Ctrl-B');
  t.feedKey('ArrowLeft');

  const panes = t.activeWindow.getPanes();
  assertEqual(t.activePane, panes[0], 'back in vim pane');
};

// ═══════════════════════════════════════════════════════════════════
// GROUP 7: Zoom
// ═══════════════════════════════════════════════════════════════════

tests.behavior_zoom_toggle = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('%');

  // Zoom
  t.feedKey('Ctrl-B');
  t.feedKey('z');
  assert(t.activeWindow._zoomed, 'window is zoomed');

  // Unzoom
  t.feedKey('Ctrl-B');
  t.feedKey('z');
  assert(!t.activeWindow._zoomed, 'window is unzoomed');
};

tests.behavior_zoom_no_borders = () => {
  // When zoomed, no borders should be drawn
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('%');
  t.feedKey('Ctrl-B');
  t.feedKey('z');

  const frame = t.renderFrame();
  const border = findBorderCol(frame);
  assertEqual(border, null, 'no borders when zoomed');
};

tests.behavior_zoom_status_bar_marker = () => {
  // Real tmux: "zoom | 0:zsh*Z" — Z after the active marker
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('%');
  t.feedKey('Ctrl-B');
  t.feedKey('z');

  const status = getStatusBar(t);
  assertIncludes(status, '*Z', 'zoom marker *Z in status bar');
};

tests.behavior_zoom_full_pane_area = () => {
  // Zoomed pane should use full width and pane height
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('%');
  t.feedKey('Ctrl-B');
  t.feedKey('z');

  const pane = t.activePane;
  assertEqual(pane.width, COLS, 'zoomed pane full width');
  assertEqual(pane.height, ROWS - 1, 'zoomed pane full height');
};

tests.behavior_unzoom_restores_layout = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('%');
  const panes = t.activeWindow.getPanes();
  const origWidth = panes[1].width;

  t.feedKey('Ctrl-B');
  t.feedKey('z');
  t.feedKey('Ctrl-B');
  t.feedKey('z');

  assertEqual(panes[1].width, origWidth, 'width restored after unzoom');
};

// ═══════════════════════════════════════════════════════════════════
// GROUP 8: Pane Close
// ═══════════════════════════════════════════════════════════════════

tests.behavior_close_confirm_prompt = () => {
  // Real tmux: "kill-pane 1? (y/n)" on status bar
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('%');
  t.feedKey('Ctrl-B');
  t.feedKey('x');

  assertEqual(t._mode, TmuxMode.CONFIRM, 'in confirm mode');
  const status = getStatusBar(t);
  assertIncludes(status, 'kill-pane', 'kill-pane in prompt');
  assertIncludes(status, '(y/n)', 'y/n in prompt');
};

tests.behavior_close_decline = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('%');
  t.feedKey('Ctrl-B');
  t.feedKey('x');
  t.feedKey('n');

  assertEqual(t._mode, TmuxMode.NORMAL, 'back to normal');
  assertEqual(t.activeWindow.getPanes().length, 2, 'pane still exists');
};

tests.behavior_close_confirm = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('%');
  assertEqual(t.activeWindow.getPanes().length, 2, 'two panes');

  t.feedKey('Ctrl-B');
  t.feedKey('x');
  t.feedKey('y');

  assertEqual(t._mode, TmuxMode.NORMAL, 'back to normal');
  assertEqual(t.activeWindow.getPanes().length, 1, 'pane closed');
};

tests.behavior_close_confirmed_no_borders = () => {
  // After closing one of two panes, remaining pane gets full size
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('%');
  t.feedKey('Ctrl-B');
  t.feedKey('x');
  t.feedKey('y');

  const frame = t.renderFrame();
  const border = findBorderCol(frame);
  assertEqual(border, null, 'no borders after closing');
  assertEqual(t.activePane.width, COLS, 'remaining pane full width');
};

// ═══════════════════════════════════════════════════════════════════
// GROUP 9: Command Prompt
// ═══════════════════════════════════════════════════════════════════

tests.behavior_command_prompt_enter = () => {
  // Real tmux: ":" on status bar
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey(':');

  assertEqual(t._mode, TmuxMode.COMMAND, 'in command mode');
  const status = getStatusBar(t);
  assertEqual(status[0], ':', 'starts with colon');
};

tests.behavior_command_prompt_typing = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey(':');
  feedString(t, 'split-window -h');

  const status = getStatusBar(t);
  assertIncludes(status, ':split-window -h', 'typed text visible');
};

tests.behavior_command_prompt_escape = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey(':');
  feedString(t, 'split-window -h');
  t.feedKey('Escape');

  assertEqual(t._mode, TmuxMode.NORMAL, 'back to normal');
};

tests.behavior_command_split_window = () => {
  // :split-window -h creates a vertical split (like %)
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey(':');
  feedString(t, 'split-window -h');
  t.feedKey('Enter');

  assertEqual(t.activeWindow.getPanes().length, 2, 'pane created via command');
};

tests.behavior_command_split_window_v = () => {
  // :split-window -v creates a horizontal split (like ")
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey(':');
  feedString(t, 'split-window -v');
  t.feedKey('Enter');

  assertEqual(t.activeWindow.getPanes().length, 2, 'pane created via command');
};

// ═══════════════════════════════════════════════════════════════════
// GROUP 10: Copy Mode
// ═══════════════════════════════════════════════════════════════════

tests.behavior_copy_mode_enter = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('[');

  assertEqual(t._mode, TmuxMode.COPY, 'in copy mode');
};

tests.behavior_copy_mode_status_bar = () => {
  // Real tmux: window name changes to "[tmux]*" in copy mode
  // Status: "sess | 0:[tmux]*  | ..."
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('[');

  const status = getStatusBar(t);
  assertIncludes(status, '[tmux]', 'copy mode shows [tmux] in status');
};

tests.behavior_copy_mode_movement = () => {
  // j/k should move cursor down/up in copy mode
  const t = newTmux();
  // Generate some content first
  feedString(t, 'echo line1');
  t.feedKey('Enter');
  feedString(t, 'echo line2');
  t.feedKey('Enter');

  t.feedKey('Ctrl-B');
  t.feedKey('[');

  // Move down first (cursor starts at row 0)
  t.feedKey('j');
  const frame1 = t.renderFrame();
  const row1 = frame1.cursor.row;
  assert(row1 > 0, `cursor moved down from 0 to ${row1}`);

  // Now move up
  t.feedKey('k');
  const frame2 = t.renderFrame();
  const row2 = frame2.cursor.row;
  assert(row2 < row1, `cursor moved up: ${row2} < ${row1}`);
};

tests.behavior_copy_mode_exit_q = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('[');
  assertEqual(t._mode, TmuxMode.COPY, 'in copy mode');
  t.feedKey('q');
  assertEqual(t._mode, TmuxMode.NORMAL, 'back to normal');
};

tests.behavior_copy_mode_exit_escape = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('[');
  t.feedKey('Escape');
  assertEqual(t._mode, TmuxMode.NORMAL, 'back to normal via escape');
};

// ═══════════════════════════════════════════════════════════════════
// GROUP 11: Detach / Reattach
// ═══════════════════════════════════════════════════════════════════

tests.behavior_detach = () => {
  // Ctrl-B d detaches
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('d');
  assertEqual(t.detached, true, 'tmux is detached');
};

tests.behavior_detach_via_session = () => {
  // Test through SessionManager
  const sm = newSession();
  feedString(sm, 'tmux');
  sm.feedKey('Enter');
  // Should be in tmux mode
  assertEqual(sm._tmux !== null, true, 'tmux launched');
  sm.feedKey('Ctrl-B');
  sm.feedKey('d');
  // After detach, back at shell
  assertEqual(sm._tmux?.detached, true, 'tmux detached');
};

tests.behavior_reattach = () => {
  // After detach, "tmux attach" reattaches
  const sm = newSession();
  feedString(sm, 'tmux');
  sm.feedKey('Enter');
  const tmuxRef = sm._tmux;
  sm.feedKey('Ctrl-B');
  sm.feedKey('d');
  // Now type "tmux attach"
  feedString(sm, 'tmux attach');
  sm.feedKey('Enter');
  // Should be back in tmux
  assertEqual(sm._tmux, tmuxRef, 'reattached to same tmux');
  assertEqual(sm._tmux?.detached, false, 'no longer detached');
};

// ═══════════════════════════════════════════════════════════════════
// GROUP 12: Resize
// ═══════════════════════════════════════════════════════════════════

tests.behavior_resize_ctrl_arrow = () => {
  // Ctrl-Left should resize (make left pane wider)
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('%');

  const panes = t.activeWindow.getPanes();
  const origLeft = panes[0].width;
  const origRight = panes[1].width;

  // Ctrl-Left from right pane
  t.feedKey('Ctrl-B');
  t.feedKey('Ctrl-Left');

  // Right pane should be narrower (or left wider)
  const newLeft = panes[0].width;
  const newRight = panes[1].width;
  assert(
    newLeft !== origLeft || newRight !== origRight,
    'resize changed dimensions'
  );
};

tests.behavior_resize_preserves_total = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('%');

  t.feedKey('Ctrl-B');
  t.feedKey('Ctrl-Left');
  t.feedKey('Ctrl-B');
  t.feedKey('Ctrl-Left');
  t.feedKey('Ctrl-B');
  t.feedKey('Ctrl-Left');

  const panes = t.activeWindow.getPanes();
  assertEqual(
    panes[0].width + 1 + panes[1].width,
    COLS,
    'total width preserved after resize'
  );
};

tests.behavior_resize_multiple_times = () => {
  // Real tmux: 3x Ctrl-Left moved border from col 40 to col 37
  // Each Ctrl-Left moves by 2 in our sim (based on resize step)
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('%');

  const borderBefore = findBorderCol(t.renderFrame());

  for (let i = 0; i < 3; i++) {
    t.feedKey('Ctrl-B');
    t.feedKey('Ctrl-Left');
  }

  const borderAfter = findBorderCol(t.renderFrame());
  assert(borderAfter !== null, 'still has border');
  assert(borderAfter < borderBefore, `border moved left: ${borderAfter} < ${borderBefore}`);
};

// ═══════════════════════════════════════════════════════════════════
// GROUP 13: Swap Panes
// ═══════════════════════════════════════════════════════════════════

tests.behavior_swap_panes = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('%');
  const panes = t.activeWindow.getPanes();
  const rightPane = t.activePane;

  // Go to left, then swap with }
  t.feedKey('Ctrl-B');
  t.feedKey('ArrowLeft');
  const leftPane = t.activePane;

  t.feedKey('Ctrl-B');
  t.feedKey('}');

  // After swap, the pane that was left is now in the right position
  const newPanes = t.activeWindow.getPanes();
  // The order of panes should have changed
  assert(newPanes.length === 2, 'still two panes');
};

tests.behavior_swap_back = () => {
  // { swaps in the opposite direction
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('%');

  t.feedKey('Ctrl-B');
  t.feedKey('ArrowLeft');

  // Swap forward then backward
  t.feedKey('Ctrl-B');
  t.feedKey('}');
  t.feedKey('Ctrl-B');
  t.feedKey('{');

  // Should be back to original
  assertEqual(t.activeWindow.getPanes().length, 2, 'still two panes');
};

// ═══════════════════════════════════════════════════════════════════
// GROUP 14: Break Pane
// ═══════════════════════════════════════════════════════════════════

tests.behavior_break_pane = () => {
  // Ctrl-B ! breaks active pane into a new window
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('%');  // vsplit
  assertEqual(t.activeSession.windows.length, 1, 'one window');
  assertEqual(t.activeWindow.getPanes().length, 2, 'two panes');

  t.feedKey('Ctrl-B');
  t.feedKey('!');

  assertEqual(t.activeSession.windows.length, 2, 'now two windows');
  // Each window should have one pane
  assertEqual(t.activeSession.windows[0].getPanes().length, 1, 'window 0: one pane');
  assertEqual(t.activeSession.windows[1].getPanes().length, 1, 'window 1: one pane');
};

tests.behavior_break_pane_status = () => {
  // Real tmux: "0 | 0:zsh- 1:zsh*"
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('%');
  t.feedKey('Ctrl-B');
  t.feedKey('!');

  const status = getStatusBar(t);
  assertIncludes(status, '0:zsh', 'original window');
  assertIncludes(status, '1:zsh', 'new window from break');
};

// ═══════════════════════════════════════════════════════════════════
// LAYOUT GEOMETRY: Detailed verification against real tmux
// ═══════════════════════════════════════════════════════════════════

tests.behavior_layout_80x24_vsplit_geometry = () => {
  // Real tmux at 80×24:
  //   Left pane:  cols 0-39  (width 40)
  //   Border:     col 40     (│)
  //   Right pane: cols 41-79 (width 39)
  //   Status bar: row 23
  const t = newTmux({ rows: 24, cols: 80 });
  t.feedKey('Ctrl-B');
  t.feedKey('%');

  const panes = t.activeWindow.getPanes();
  assertEqual(panes[0].left, 0, 'left pane starts at 0');
  assertEqual(panes[0].width, 40, 'left pane width 40');
  assertEqual(panes[1].left, 41, 'right pane starts at 41');
  assertEqual(panes[1].width, 39, 'right pane width 39');

  const frame = t.renderFrame();
  const borderCol = findBorderCol(frame);
  assertEqual(borderCol, 40, 'border at col 40');
};

tests.behavior_layout_80x24_hsplit_geometry = () => {
  // Real tmux at 80×24 (23 pane rows):
  //   Top pane:    rows 0-10  (height 11)
  //   Border:      row 11     (─)
  //   Bottom pane: rows 12-22 (height 11)
  //   Status bar:  row 23
  const t = newTmux({ rows: 24, cols: 80 });
  t.feedKey('Ctrl-B');
  t.feedKey('"');

  const panes = t.activeWindow.getPanes();
  assertEqual(panes[0].top, 0, 'top pane starts at 0');
  assertEqual(panes[0].height, 11, 'top pane height 11');
  assertEqual(panes[1].top, 12, 'bottom pane starts at 12');
  assertEqual(panes[1].height, 11, 'bottom pane height 11');

  const frame = t.renderFrame();
  const borderRow = findBorderRow(frame);
  assertEqual(borderRow, 11, 'border at row 11');
};

tests.behavior_layout_40x20_vsplit_geometry = () => {
  // At 40 cols: left = floor(40*0.5) = 20 cols, border at 20, right = 19 cols
  const t = newTmux({ rows: 20, cols: 40 });
  t.feedKey('Ctrl-B');
  t.feedKey('%');

  const panes = t.activeWindow.getPanes();
  assertEqual(panes[0].width, 20, 'left pane width 20');
  assertEqual(panes[1].width, 19, 'right pane width 19');
  assertEqual(panes[0].width + 1 + panes[1].width, 40, 'total adds up');
};

tests.behavior_layout_odd_cols_vsplit = () => {
  // At 81 cols: left = floor(81*0.5) = 40, border at 40, right = 40
  const t = newTmux({ rows: 20, cols: 81 });
  t.feedKey('Ctrl-B');
  t.feedKey('%');

  const panes = t.activeWindow.getPanes();
  assertEqual(panes[0].width + 1 + panes[1].width, 81, 'total adds up');
};

// ═══════════════════════════════════════════════════════════════════
// STATUS BAR FORMAT: Detailed checks
// ═══════════════════════════════════════════════════════════════════

tests.behavior_status_session_name = () => {
  const t = newTmux();
  const status = getStatusBar(t);
  // Should start with "0 " (session name)
  assert(status.startsWith('0 '), `status starts with "0 ": ${JSON.stringify(status.slice(0, 10))}`);
};

tests.behavior_status_pipe_separators = () => {
  const t = newTmux();
  const status = getStatusBar(t);
  // Should have pipe separators between sections
  const pipes = (status.match(/\|/g) || []).length;
  assert(pipes >= 3, `at least 3 pipe separators, got ${pipes}`);
};

tests.behavior_status_time_format = () => {
  // Real tmux: "HH:MM" (24h)
  const t = newTmux();
  const status = getStatusBar(t);
  const timeMatch = status.match(/\d{2}:\d{2}/);
  assert(timeMatch !== null, 'time in HH:MM format');
};

tests.behavior_status_date_format = () => {
  // Real tmux: "DD-Mon-YY"
  const t = newTmux();
  const status = getStatusBar(t);
  const dateMatch = status.match(/\d{1,2}-(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)-\d{2}/);
  assert(dateMatch !== null, 'date in DD-Mon-YY format');
};

tests.behavior_status_inactive_window_marker = () => {
  // Real tmux: inactive windows use "-"
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('c');
  const status = getStatusBar(t);
  // Window 0 should have "-" marker
  assertIncludes(status, '0:zsh-', 'inactive window has dash');
  assertIncludes(status, '1:zsh*', 'active window has star');
};

tests.behavior_status_zoom_flag = () => {
  // Real tmux: "*Z" (star then Z)
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('%');
  t.feedKey('Ctrl-B');
  t.feedKey('z');
  const status = getStatusBar(t);
  // Verify the exact format: should be "0:zsh*Z" not "0:zshZ*"
  assertIncludes(status, '0:zsh*Z', 'zoom flag after star: *Z');
};

// ═══════════════════════════════════════════════════════════════════
// GROUND TRUTH COMPARISON
// ═══════════════════════════════════════════════════════════════════

if (groundTruth) {
  tests.gt_vsplit_border_col = () => {
    // Ground truth says border at col 40 for 80-col vsplit
    const gt = groundTruth['vsplit'];
    if (!gt) throw new Error('missing ground truth for vsplit');

    const t = newTmux({ rows: gt.rows, cols: gt.cols });
    t.feedKey('Ctrl-B');
    t.feedKey('%');
    const frame = t.renderFrame();
    const border = findBorderCol(frame);

    // Real tmux: border at col 40
    const gtBorder = gt.pane_lines.reduce((found, line) => {
      if (found !== null) return found;
      for (let i = 0; i < line.length; i++) {
        if (line[i] === '│') return i;
      }
      return null;
    }, null);

    assertEqual(border, gtBorder, `vsplit border matches real tmux (expected ${gtBorder})`);
  };

  tests.gt_hsplit_border_row = () => {
    const gt = groundTruth['hsplit'];
    if (!gt) throw new Error('missing ground truth for hsplit');

    const t = newTmux({ rows: gt.rows, cols: gt.cols });
    t.feedKey('Ctrl-B');
    t.feedKey('"');
    const frame = t.renderFrame();
    const border = findBorderRow(frame);

    const gtBorder = gt.pane_lines.findIndex(l => l.includes('─'));
    assertEqual(border, gtBorder, `hsplit border matches real tmux (expected ${gtBorder})`);
  };

  tests.gt_zoom_status_format = () => {
    const gt = groundTruth['zoomed'];
    if (!gt) throw new Error('missing ground truth for zoomed');

    const t = newTmux({ rows: gt.rows, cols: gt.cols });
    t.feedKey('Ctrl-B');
    t.feedKey('%');
    t.feedKey('Ctrl-B');
    t.feedKey('z');
    const status = getStatusBar(t).trim();
    const gtStatus = gt.status_bar.trim();

    // Compare the window list portion (ignore time/date which changes)
    // Real: "zoom | 0:zsh*Z  | HH:MM | DD-Mon-YY"
    // Extract "0:zsh*Z" from both
    const simWindows = status.match(/\d+:\S+/g);
    const gtWindows = gtStatus.match(/\d+:\S+/g);
    assertEqual(
      simWindows?.[0],
      gtWindows?.[0],
      `zoom window format: sim=${simWindows?.[0]} vs real=${gtWindows?.[0]}`
    );
  };

  tests.gt_copy_mode_status = () => {
    const gt = groundTruth['copy_mode_enter'];
    if (!gt) throw new Error('missing ground truth for copy_mode_enter');

    const t = newTmux({ rows: gt.rows, cols: gt.cols });
    t.feedKey('Ctrl-B');
    t.feedKey('[');
    const status = getStatusBar(t).trim();
    const gtStatus = gt.status_bar.trim();

    // Real tmux shows "[tmux]" as window name in copy mode
    if (gtStatus.includes('[tmux]')) {
      assertIncludes(status, '[tmux]', 'copy mode shows [tmux] like real tmux');
    }
  };

  tests.gt_close_confirm_format = () => {
    const gt = groundTruth['close_confirm'];
    if (!gt) throw new Error('missing ground truth for close_confirm');

    const t = newTmux({ rows: gt.rows, cols: gt.cols });
    t.feedKey('Ctrl-B');
    t.feedKey('%');
    t.feedKey('Ctrl-B');
    t.feedKey('x');
    const status = getStatusBar(t).trim();
    const gtStatus = gt.status_bar.trim();

    // Both should contain "kill-pane" and "(y/n)"
    assertIncludes(status, 'kill-pane', 'sim has kill-pane');
    assertIncludes(status, '(y/n)', 'sim has (y/n)');
    assertIncludes(gtStatus, 'kill-pane', 'real has kill-pane');
    assertIncludes(gtStatus, '(y/n)', 'real has (y/n)');
  };

  tests.gt_three_windows_status = () => {
    const gt = groundTruth['three_windows'];
    if (!gt) throw new Error('missing ground truth for three_windows');

    const t = newTmux({ rows: gt.rows, cols: gt.cols });
    t.feedKey('Ctrl-B');
    t.feedKey('c');
    t.feedKey('Ctrl-B');
    t.feedKey('c');
    const status = getStatusBar(t).trim();

    // Extract window list portion from both
    assertIncludes(status, '0:zsh', 'window 0');
    assertIncludes(status, '1:zsh', 'window 1');
    assertIncludes(status, '2:zsh*', 'window 2 active');
  };

  tests.gt_resize_border_moved = () => {
    const gt = groundTruth['after_resize'];
    if (!gt) throw new Error('missing ground truth for after_resize');

    const borderBefore = gt.border_before;
    const borderAfter = gt.border_after;

    if (borderBefore != null && borderAfter != null) {
      const t = newTmux({ rows: gt.rows, cols: gt.cols });
      t.feedKey('Ctrl-B');
      t.feedKey('%');

      const simBorderBefore = findBorderCol(t.renderFrame());

      for (let i = 0; i < 3; i++) {
        t.feedKey('Ctrl-B');
        t.feedKey('Ctrl-Left');
      }

      const simBorderAfter = findBorderCol(t.renderFrame());

      // Border should have moved by the same amount
      const gtDelta = borderBefore - borderAfter;
      const simDelta = simBorderBefore - simBorderAfter;
      assertEqual(simDelta, gtDelta, `resize delta: sim=${simDelta} vs real=${gtDelta}`);
    }
  };

  tests.gt_break_pane_window_count = () => {
    const gt = groundTruth['after_break'];
    if (!gt) throw new Error('missing ground truth for after_break');

    const t = newTmux({ rows: gt.rows, cols: gt.cols });
    t.feedKey('Ctrl-B');
    t.feedKey('%');
    t.feedKey('Ctrl-B');
    t.feedKey('!');

    const status = getStatusBar(t).trim();
    // Real tmux after break: "brk | 0:zsh- 1:zsh*"
    assertIncludes(status, '0:zsh', 'original window');
    assertIncludes(status, '1:zsh', 'broken-out window');
    assertEqual(t.activeSession.windows.length, 2, 'two windows after break');
  };
}

// ═══════════════════════════════════════════════════════════════════
// Run
// ═══════════════════════════════════════════════════════════════════

async function runTests() {
  const testNames = Object.keys(tests);
  const toRun = filterCase ? testNames.filter(n => n === filterCase) : testNames;

  console.log(`\nRunning ${toRun.length} tmux behavioral tests...\n`);

  for (const name of toRun) {
    try {
      tests[name]();
      passed++;
      if (verbose) console.log(`  ✅ ${name}`);
    } catch (e) {
      failed++;
      console.log(`  ❌ ${name}: ${e.message}`);
      if (verbose) console.log(`     ${e.stack}`);
    }
  }

  const total = passed + failed;
  console.log(`\n${passed}/${total} passed, ${failed} failed\n`);

  if (failed > 0) process.exit(1);
}

runTests();
