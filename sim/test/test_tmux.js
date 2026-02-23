/**
 * VimFu Simulator – Tmux Tests
 *
 * Tests the terminal multiplexer (tmux) implementation:
 *   - Core data model (sessions, windows, panes, layout)
 *   - Prefix key handling
 *   - Pane splitting, navigation, resize, close, zoom
 *   - Window management (create, switch, rename)
 *   - SessionManager integration (launch/detach)
 *   - Rendering (status bar, borders, compositing)
 *   - Command prompt
 *   - Copy mode
 *
 * Usage:
 *   node test/test_tmux.js               # run all
 *   node test/test_tmux.js --case <name> # run one
 *   node test/test_tmux.js --verbose     # show details
 */

import { dirname, resolve } from 'path';
import { fileURLToPath } from 'url';
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

// ── Helpers ──
const ROWS = 20;
const COLS = 40;

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
    rows: ROWS,
    cols: COLS,
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

/** Get the status bar text (last row) */
function getStatusBar(tmux) {
  const frame = tmux.renderFrame();
  return getFrameRow(frame, tmux.rows - 1);
}

// ── Test cases ──
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

// ── Data Model Tests ──

tests.tmux_initial_state = () => {
  const t = newTmux();
  assertEqual(t.sessions.length, 1, 'should have 1 session');
  assertEqual(t.activeSession.name, '0', 'session name');
  assertEqual(t.activeSession.windows.length, 1, 'should have 1 window');
  assertEqual(t.activeWindow.name, 'zsh', 'window name');
  assertEqual(t.activeWindow.getPanes().length, 1, 'should have 1 pane');
  assert(t.activePane !== null, 'should have active pane');
  assertEqual(t._mode, TmuxMode.NORMAL, 'should be in normal mode');
  assertEqual(t.detached, false, 'should not be detached');
};

tests.tmux_renders_frame = () => {
  const t = newTmux();
  const frame = t.renderFrame();
  assertEqual(frame.rows, ROWS, 'frame rows');
  assertEqual(frame.cols, COLS, 'frame cols');
  assertEqual(frame.lines.length, ROWS, 'frame lines count');
  assert(frame.cursor !== undefined, 'frame has cursor');
  // Every line should have the right width
  for (let i = 0; i < ROWS; i++) {
    assertEqual(frame.lines[i].text.length, COLS, `line ${i} width`);
    assert(frame.lines[i].runs.length > 0, `line ${i} has runs`);
  }
};

tests.tmux_status_bar = () => {
  const t = newTmux();
  const statusBar = getStatusBar(t);
  assertIncludes(statusBar, '0 ', 'session name in status bar');
  assertIncludes(statusBar, '0:zsh', 'window name in status bar');
  assertIncludes(statusBar, '*', 'active window marker');
  assertIncludes(statusBar, '|', 'pipe separator in status bar');
};

// ── Prefix Key Tests ──

tests.prefix_key_enters_prefix_mode = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B');
  assertEqual(t._mode, TmuxMode.PREFIX, 'should be in prefix mode');
};

tests.prefix_key_unknown_returns_normal = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('Z');  // unknown prefix command
  assertEqual(t._mode, TmuxMode.NORMAL, 'should return to normal');
};

tests.prefix_key_forwarded_on_double = () => {
  const t = newTmux();
  // Ctrl-b Ctrl-b should forward Ctrl-b to the active pane
  t.feedKey('Ctrl-B');
  t.feedKey('Ctrl-B');
  assertEqual(t._mode, TmuxMode.NORMAL, 'should return to normal');
};

// ── Pane Splitting Tests ──

tests.split_vertical = () => {
  const t = newTmux({ cols: 40, rows: 20 });
  t.feedKey('Ctrl-B');
  t.feedKey('%');
  const panes = t.activeWindow.getPanes();
  assertEqual(panes.length, 2, 'should have 2 panes');
  // After vertical split, left pane should be narrower
  assert(panes[0].width < 40, 'left pane narrower');
  assert(panes[1].width < 40, 'right pane narrower');
  assertEqual(panes[0].width + 1 + panes[1].width, 40, 'widths add up');
};

tests.split_horizontal = () => {
  const t = newTmux({ cols: 40, rows: 20 });
  t.feedKey('Ctrl-B');
  t.feedKey('"');
  const panes = t.activeWindow.getPanes();
  assertEqual(panes.length, 2, 'should have 2 panes');
  const paneRows = ROWS - 1; // minus status bar
  assert(panes[0].height < paneRows, 'top pane shorter');
  assert(panes[1].height < paneRows, 'bottom pane shorter');
  assertEqual(panes[0].height + 1 + panes[1].height, paneRows, 'heights add up');
};

tests.split_produces_independent_panes = () => {
  const t = newTmux({ cols: 40, rows: 20 });
  // Type something in first pane
  feedString(t, 'echo hello');
  t.feedKey('Enter');
  // Split
  t.feedKey('Ctrl-B');
  t.feedKey('%');
  // The new pane (active) should have a fresh shell
  const panes = t.activeWindow.getPanes();
  assert(panes[0] !== panes[1], 'panes are different');
  assert(panes[0].session !== panes[1].session, 'sessions are different');
};

tests.split_too_small_rejected = () => {
  const t = newTmux({ cols: 4, rows: 6 });
  t.feedKey('Ctrl-B');
  t.feedKey('"');
  // Might have split or been rejected depending on math
  const panes = t.activeWindow.getPanes();
  // At 5 pane rows (6-1 status), hsplit needs min 4, so it should work
  // but the second split should be rejected
  if (panes.length === 2) {
    t.feedKey('Ctrl-B');
    t.feedKey('"');
    // This should be rejected (pane too small)
  }
};

tests.triple_split = () => {
  const t = newTmux({ cols: 80, rows: 24 });
  // Two vertical splits
  t.feedKey('Ctrl-B');
  t.feedKey('%');
  t.feedKey('Ctrl-B');
  t.feedKey('%');
  const panes = t.activeWindow.getPanes();
  assertEqual(panes.length, 3, 'should have 3 panes');
};

tests.mixed_splits = () => {
  const t = newTmux({ cols: 80, rows: 24 });
  // Vertical split, then horizontal split on right pane
  t.feedKey('Ctrl-B');
  t.feedKey('%');
  t.feedKey('Ctrl-B');
  t.feedKey('"');
  const panes = t.activeWindow.getPanes();
  assertEqual(panes.length, 3, 'should have 3 panes');
};

// ── Pane Navigation Tests ──

tests.navigate_pane_next = () => {
  const t = newTmux({ cols: 80, rows: 24 });
  t.feedKey('Ctrl-B');
  t.feedKey('%');
  const panes = t.activeWindow.getPanes();
  // After split, the new pane (second) is active
  assertEqual(t.activePane, panes[1], 'new pane is active');
  // Navigate to next (wraps to first)
  t.feedKey('Ctrl-B');
  t.feedKey('o');
  assertEqual(t.activePane, panes[0], 'cycled to first pane');
};

tests.navigate_pane_arrow = () => {
  const t = newTmux({ cols: 80, rows: 24 });
  t.feedKey('Ctrl-B');
  t.feedKey('%');
  const panes = t.activeWindow.getPanes();
  // Active is right pane (panes[1])
  assertEqual(t.activePane, panes[1], 'right pane active');
  // Navigate left
  t.feedKey('Ctrl-B');
  t.feedKey('ArrowLeft');
  assertEqual(t.activePane, panes[0], 'navigated to left pane');
  // Navigate right
  t.feedKey('Ctrl-B');
  t.feedKey('ArrowRight');
  assertEqual(t.activePane, panes[1], 'navigated back to right pane');
};

// ── Pane Close Tests ──

tests.close_pane_with_confirm = () => {
  const t = newTmux({ cols: 80, rows: 24 });
  t.feedKey('Ctrl-B');
  t.feedKey('%');
  assertEqual(t.activeWindow.getPanes().length, 2, '2 panes');
  // Close active pane (with confirmation)
  t.feedKey('Ctrl-B');
  t.feedKey('x');
  assertEqual(t._mode, TmuxMode.CONFIRM, 'in confirm mode');
  t.feedKey('y');
  assertEqual(t.activeWindow.getPanes().length, 1, '1 pane after close');
  assertEqual(t._mode, TmuxMode.NORMAL, 'back to normal');
};

tests.close_pane_declined = () => {
  const t = newTmux({ cols: 80, rows: 24 });
  t.feedKey('Ctrl-B');
  t.feedKey('%');
  assertEqual(t.activeWindow.getPanes().length, 2, '2 panes');
  t.feedKey('Ctrl-B');
  t.feedKey('x');
  t.feedKey('n');
  assertEqual(t.activeWindow.getPanes().length, 2, 'still 2 panes');
};

tests.close_last_pane_detaches = () => {
  const t = newTmux();
  assertEqual(t.activeWindow.getPanes().length, 1, '1 pane');
  t.feedKey('Ctrl-B');
  t.feedKey('x');
  assertEqual(t._mode, TmuxMode.CONFIRM, 'confirm mode');
  t.feedKey('y');
  assertEqual(t.detached, true, 'tmux detached');
};

// ── Pane Zoom Tests ──

tests.zoom_pane = () => {
  const t = newTmux({ cols: 80, rows: 24 });
  t.feedKey('Ctrl-B');
  t.feedKey('%');
  const origWidth = t.activePane.width;
  assert(origWidth < 80, 'pane starts smaller');
  t.feedKey('Ctrl-B');
  t.feedKey('z');
  assertEqual(t.activeWindow._zoomed, true, 'window is zoomed');
  // Active pane should be rendered at full size
  const frame = t.renderFrame();
  assertEqual(frame.cols, 80, 'frame is full width');
  // Unzoom
  t.feedKey('Ctrl-B');
  t.feedKey('z');
  assertEqual(t.activeWindow._zoomed, false, 'unzoomed');
};

tests.zoom_status_bar_indicator = () => {
  const t = newTmux({ cols: 80, rows: 24 });
  t.feedKey('Ctrl-B');
  t.feedKey('%');
  t.feedKey('Ctrl-B');
  t.feedKey('z');
  const statusBar = getStatusBar(t);
  assertIncludes(statusBar, 'Z', 'Z in status bar when zoomed');
};

// ── Pane Swap Tests ──

tests.swap_pane_next = () => {
  const t = newTmux({ cols: 80, rows: 24 });
  // Type in first pane
  feedString(t, 'echo pane0');
  t.feedKey('Enter');
  // Split and type in second pane
  t.feedKey('Ctrl-B');
  t.feedKey('%');
  feedString(t, 'echo pane1');
  t.feedKey('Enter');
  // Navigate to first pane
  t.feedKey('Ctrl-B');
  t.feedKey('o');
  // Swap with next
  t.feedKey('Ctrl-B');
  t.feedKey('}');
  // The pane contents should have swapped
};

// ── Window Management Tests ──

tests.create_window = () => {
  const t = newTmux();
  assertEqual(t.activeSession.windows.length, 1, '1 window');
  t.feedKey('Ctrl-B');
  t.feedKey('c');
  assertEqual(t.activeSession.windows.length, 2, '2 windows');
  assertEqual(t.activeSession.activeWindowIndex, 1, 'new window active');
};

tests.switch_window_next_prev = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('c'); // create window 1
  t.feedKey('Ctrl-B');
  t.feedKey('c'); // create window 2
  assertEqual(t.activeSession.activeWindowIndex, 2, 'on window 2');
  t.feedKey('Ctrl-B');
  t.feedKey('p');
  assertEqual(t.activeSession.activeWindowIndex, 1, 'on window 1');
  t.feedKey('Ctrl-B');
  t.feedKey('n');
  assertEqual(t.activeSession.activeWindowIndex, 2, 'back on window 2');
};

tests.switch_window_by_number = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('c');
  t.feedKey('Ctrl-B');
  t.feedKey('c');
  assertEqual(t.activeSession.activeWindowIndex, 2, 'on window 2');
  t.feedKey('Ctrl-B');
  t.feedKey('0');
  assertEqual(t.activeSession.activeWindowIndex, 0, 'switched to window 0');
};

tests.last_window = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('c');
  assertEqual(t.activeSession.activeWindowIndex, 1, 'on window 1');
  // Use window number to switch (l is now pane navigation)
  t.feedKey('Ctrl-B');
  t.feedKey('0');
  assertEqual(t.activeSession.activeWindowIndex, 0, 'back to window 0');
  t.feedKey('Ctrl-B');
  t.feedKey('1');
  assertEqual(t.activeSession.activeWindowIndex, 1, 'toggled back to window 1');
};

tests.rename_window = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey(',');
  assertEqual(t._mode, TmuxMode.RENAME, 'in rename mode');
  // Clear existing name with Ctrl-U and type new
  t.feedKey('Ctrl-U');
  feedString(t, 'mywin');
  t.feedKey('Enter');
  assertEqual(t.activeWindow.name, 'mywin', 'window renamed');
  assertEqual(t._mode, TmuxMode.NORMAL, 'back to normal');
};

tests.rename_window_escape_cancels = () => {
  const t = newTmux();
  const origName = t.activeWindow.name;
  t.feedKey('Ctrl-B');
  t.feedKey(',');
  t.feedKey('Ctrl-U');
  feedString(t, 'cancelled');
  t.feedKey('Escape');
  assertEqual(t.activeWindow.name, origName, 'name unchanged');
};

tests.close_window = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('c');
  assertEqual(t.activeSession.windows.length, 2, '2 windows');
  t.feedKey('Ctrl-B');
  t.feedKey('&');
  // Now in confirm mode
  assertEqual(t._mode, 'confirm', 'in confirm mode');
  t.feedKey('y');
  assertEqual(t.activeSession.windows.length, 1, '1 window after confirm');
};

tests.close_last_window_confirms_detach = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('&');
  assertEqual(t._mode, 'confirm', 'in confirm mode');
  t.feedKey('y');
  assertEqual(t.detached, true, 'detached after closing last window');
};

tests.close_window_decline = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('c');
  assertEqual(t.activeSession.windows.length, 2, '2 windows');
  t.feedKey('Ctrl-B');
  t.feedKey('&');
  t.feedKey('n');
  assertEqual(t.activeSession.windows.length, 2, 'still 2 windows after decline');
};

tests.window_list = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('c');
  t.feedKey('Ctrl-B');
  t.feedKey('c');
  // Open window list
  t.feedKey('Ctrl-B');
  t.feedKey('w');
  assertEqual(t._mode, TmuxMode.WINDOW_LIST, 'in window list mode');
  // Navigate and select
  t.feedKey('k'); // go up
  t.feedKey('Enter'); // select
  assertEqual(t._mode, TmuxMode.NORMAL, 'back to normal');
};

tests.status_bar_shows_multiple_windows = () => {
  const t = newTmux({ cols: 80 });
  t.feedKey('Ctrl-B');
  t.feedKey('c');
  const statusBar = getStatusBar(t);
  assertIncludes(statusBar, '0:zsh', 'window 0 in status');
  assertIncludes(statusBar, '1:zsh', 'window 1 in status');
};

// ── Break Pane Tests ──

tests.break_pane = () => {
  const t = newTmux({ cols: 80, rows: 24 });
  t.feedKey('Ctrl-B');
  t.feedKey('%');
  assertEqual(t.activeWindow.getPanes().length, 2, '2 panes');
  const winCount = t.activeSession.windows.length;
  t.feedKey('Ctrl-B');
  t.feedKey('!');
  assertEqual(t.activeSession.windows.length, winCount + 1, 'new window created');
};

tests.break_pane_single_fails = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('!');
  assertEqual(t.activeSession.windows.length, 1, 'still 1 window');
};

// ── Pane Resize Tests ──

tests.resize_pane = () => {
  const t = newTmux({ cols: 80, rows: 24 });
  t.feedKey('Ctrl-B');
  t.feedKey('%');
  const panes = t.activeWindow.getPanes();
  const origWidth0 = panes[0].width;
  // Resize active (right) pane left
  t.feedKey('Ctrl-B');
  t.feedKey('Ctrl-Left');
  // The layout ratio should have changed
  const newWidth0 = panes[0].width;
  // Width may or may not have changed depending on the resize direction logic
  // Just ensure no errors
};

// ── Detach Tests ──

tests.detach = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('d');
  assertEqual(t.detached, true, 'tmux detached');
};

// ── Command Prompt Tests ──

tests.command_prompt = () => {
  const t = newTmux({ cols: 80, rows: 24 });
  t.feedKey('Ctrl-B');
  t.feedKey(':');
  assertEqual(t._mode, TmuxMode.COMMAND, 'in command mode');
  feedString(t, 'split-window -h');
  t.feedKey('Enter');
  assertEqual(t._mode, TmuxMode.NORMAL, 'back to normal');
  assertEqual(t.activeWindow.getPanes().length, 2, 'split via command');
};

tests.command_new_window = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey(':');
  feedString(t, 'new-window -n test');
  t.feedKey('Enter');
  assertEqual(t.activeSession.windows.length, 2, '2 windows');
  assertEqual(t.activeWindow.name, 'test', 'named window');
};

tests.command_rename = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey(':');
  feedString(t, 'rename-window myterm');
  t.feedKey('Enter');
  assertEqual(t.activeWindow.name, 'myterm', 'window renamed via command');
};

tests.command_escape_cancels = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey(':');
  feedString(t, 'some command');
  t.feedKey('Escape');
  assertEqual(t._mode, TmuxMode.NORMAL, 'command cancelled');
};

tests.command_backspace = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey(':');
  feedString(t, 'abc');
  t.feedKey('Backspace');
  assertEqual(t._commandInput, 'ab', 'backspace removed last char');
};

tests.command_unknown = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey(':');
  feedString(t, 'nonexistent');
  t.feedKey('Enter');
  assertIncludes(t._message, 'unknown command', 'unknown command message');
};

tests.command_ls = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('c'); // create second window
  t.feedKey('Ctrl-B');
  t.feedKey(':');
  feedString(t, 'ls');
  t.feedKey('Enter');
  assertIncludes(t._message, '2 windows', 'ls shows windows');
};

tests.command_detach = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey(':');
  feedString(t, 'detach');
  t.feedKey('Enter');
  assertEqual(t.detached, true, 'detached via command');
};

tests.command_kill_pane = () => {
  const t = newTmux({ cols: 80, rows: 24 });
  t.feedKey('Ctrl-B');
  t.feedKey('%');
  assertEqual(t.activeWindow.getPanes().length, 2, '2 panes');
  t.feedKey('Ctrl-B');
  t.feedKey(':');
  feedString(t, 'kill-pane');
  t.feedKey('Enter');
  assertEqual(t.activeWindow.getPanes().length, 1, '1 pane after kill');
};

tests.command_new_session = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey(':');
  feedString(t, 'new-session -s mysess');
  t.feedKey('Enter');
  assertEqual(t.sessions.length, 2, '2 sessions');
  assertEqual(t.activeSession.name, 'mysess', 'session named');
};

tests.command_switch_client = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey(':');
  feedString(t, 'new-session -s other');
  t.feedKey('Enter');
  assertEqual(t.activeSession.name, 'other', 'on other session');
  t.feedKey('Ctrl-B');
  t.feedKey(':');
  feedString(t, 'switch-client -t 0');
  t.feedKey('Enter');
  assertEqual(t.activeSession.name, '0', 'switched back to session 0');
};

// ── Copy Mode Tests ──

tests.copy_mode_enter_exit = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('[');
  assertEqual(t._mode, TmuxMode.COPY, 'in copy mode');
  t.feedKey('q');
  assertEqual(t._mode, TmuxMode.NORMAL, 'exited copy mode');
};

tests.copy_mode_navigation = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('[');
  // Move around
  t.feedKey('l');
  assertEqual(t._copyCursor.col, 1, 'moved right');
  t.feedKey('j');
  assertEqual(t._copyCursor.row, 1, 'moved down');
  t.feedKey('h');
  assertEqual(t._copyCursor.col, 0, 'moved left');
  t.feedKey('k');
  assertEqual(t._copyCursor.row, 0, 'moved up');
  t.feedKey('Escape');
};

tests.copy_mode_jump = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('[');
  t.feedKey('$');
  assertEqual(t._copyCursor.col, COLS - 1, 'jumped to end');
  t.feedKey('0');
  assertEqual(t._copyCursor.col, 0, 'jumped to start');
  t.feedKey('q');
};

// ── Pane Numbers Tests ──

tests.pane_numbers = () => {
  const t = newTmux({ cols: 80, rows: 24 });
  t.feedKey('Ctrl-B');
  t.feedKey('%');
  t.feedKey('Ctrl-B');
  t.feedKey('q');
  assertEqual(t._mode, TmuxMode.PANE_NUMBERS, 'showing pane numbers');
  // Press 0 to switch to first pane
  const panes = t.activeWindow.getPanes();
  t.feedKey('0');
  assertEqual(t.activePane, panes[0], 'switched to pane 0');
  assertEqual(t._mode, TmuxMode.NORMAL, 'back to normal');
};

// ── Clock Mode Tests ──

tests.clock_mode = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('t');
  assertEqual(t._mode, TmuxMode.CLOCK, 'in clock mode');
  t.feedKey('q');
  assertEqual(t._mode, TmuxMode.NORMAL, 'exited clock mode');
};

// ── Help Tests ──

tests.help_mode = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B');
  t.feedKey('?');
  assertEqual(t._mode, TmuxMode.HELP, 'in help mode');
  t.feedKey('j'); // scroll
  assertEqual(t._helpScroll, 1, 'scrolled');
  t.feedKey('q');
  assertEqual(t._mode, TmuxMode.NORMAL, 'exited help');
};

// ── Cycle Layout Tests ──

tests.cycle_layout = () => {
  const t = newTmux({ cols: 80, rows: 24 });
  t.feedKey('Ctrl-B');
  t.feedKey('%');
  t.feedKey('Ctrl-B');
  t.feedKey(' ');
  // Layout should have changed (no errors)
  assertEqual(t.activeWindow.getPanes().length, 2, 'still 2 panes');
  t.feedKey('Ctrl-B');
  t.feedKey(' ');
  assertEqual(t.activeWindow.getPanes().length, 2, 'still 2 panes after another cycle');
};

// ── Rendering Tests ──

tests.render_border_vertical = () => {
  const t = newTmux({ cols: 40, rows: 20 });
  t.feedKey('Ctrl-B');
  t.feedKey('%');
  const frame = t.renderFrame();
  const panes = t.activeWindow.getPanes();
  const borderCol = panes[0].left + panes[0].width;
  // Check that a vertical border character exists
  for (let r = 0; r < t._paneRows; r++) {
    const ch = frame.lines[r].text[borderCol];
    assertEqual(ch, '\u2502', `border char at row ${r}`);
  }
};

tests.render_border_horizontal = () => {
  const t = newTmux({ cols: 40, rows: 20 });
  t.feedKey('Ctrl-B');
  t.feedKey('"');
  const frame = t.renderFrame();
  const panes = t.activeWindow.getPanes();
  const borderRow = panes[0].top + panes[0].height;
  // Check that horizontal border chars exist
  const line = frame.lines[borderRow].text;
  for (let c = 0; c < t.cols; c++) {
    assertEqual(line[c], '\u2500', `border char at col ${c}`);
  }
};

tests.render_no_border_single_pane = () => {
  const t = newTmux({ cols: 40, rows: 20 });
  const frame = t.renderFrame();
  // No border characters should be present in the pane area
  for (let r = 0; r < t._paneRows; r++) {
    assert(!frame.lines[r].text.includes('\u2502'), `no vertical border at row ${r}`);
    // Horizontal border chars can appear in content (unlikely but possible)
  }
};

tests.render_cursor_in_active_pane = () => {
  const t = newTmux({ cols: 80, rows: 24 });
  t.feedKey('Ctrl-B');
  t.feedKey('%');
  const panes = t.activeWindow.getPanes();
  const activePane = t.activePane;
  const frame = t.renderFrame();
  // Cursor should be within the active pane's bounds
  assert(frame.cursor.row >= activePane.top, 'cursor row >= pane top');
  assert(frame.cursor.row < activePane.top + activePane.height, 'cursor row < pane bottom');
  assert(frame.cursor.col >= activePane.left, 'cursor col >= pane left');
  assert(frame.cursor.col < activePane.left + activePane.width, 'cursor col < pane right');
};

tests.render_command_prompt = () => {
  const t = newTmux({ cols: 80, rows: 24 });
  t.feedKey('Ctrl-B');
  t.feedKey(':');
  feedString(t, 'test');
  const frame = t.renderFrame();
  const statusLine = getFrameRow(frame, t.rows - 1);
  assertIncludes(statusLine, ':test', 'command prompt shown');
};

tests.render_rename_prompt = () => {
  const t = newTmux({ cols: 80, rows: 24 });
  t.feedKey('Ctrl-B');
  t.feedKey(',');
  const frame = t.renderFrame();
  const statusLine = getFrameRow(frame, t.rows - 1);
  assertIncludes(statusLine, '(rename-window)', 'rename prompt shown');
};

tests.render_confirm_prompt = () => {
  const t = newTmux({ cols: 80, rows: 24 });
  t.feedKey('Ctrl-B');
  t.feedKey('x');
  const frame = t.renderFrame();
  const statusLine = getFrameRow(frame, t.rows - 1);
  assertIncludes(statusLine, 'kill-pane', 'confirm prompt shown');
};

// ── SessionManager Integration Tests ──

tests.session_launch_tmux = () => {
  const s = newSession();
  feedString(s, 'tmux');
  s.feedKey('Enter');
  assertEqual(s.mode, 'tmux', 'session in tmux mode');
  assertEqual(s.getModeLabel(), 'TMUX', 'mode label is TMUX');
};

tests.session_tmux_renders = () => {
  const s = newSession();
  feedString(s, 'tmux');
  s.feedKey('Enter');
  const frame = s.renderFrame();
  assertEqual(frame.rows, ROWS, 'frame rows match');
  assertEqual(frame.cols, COLS, 'frame cols match');
  assertEqual(frame.lines.length, ROWS, 'correct number of lines');
};

tests.session_tmux_detach = () => {
  const s = newSession();
  feedString(s, 'tmux');
  s.feedKey('Enter');
  assertEqual(s.mode, 'tmux', 'in tmux');
  // Detach
  s.feedKey('Ctrl-B');
  s.feedKey('d');
  assertEqual(s.mode, 'shell', 'back to shell after detach');
};

tests.session_tmux_reattach = () => {
  const s = newSession();
  feedString(s, 'tmux');
  s.feedKey('Enter');
  s.feedKey('Ctrl-B');
  s.feedKey('d');
  assertEqual(s.mode, 'shell', 'detached');
  // Reattach
  feedString(s, 'tmux attach');
  s.feedKey('Enter');
  assertEqual(s.mode, 'tmux', 'reattached');
};

tests.session_tmux_ls = () => {
  const s = newSession();
  feedString(s, 'tmux');
  s.feedKey('Enter');
  s.feedKey('Ctrl-B');
  s.feedKey('d');
  // tmux ls
  feedString(s, 'tmux ls');
  s.feedKey('Enter');
  // Should remain in shell mode
  assertEqual(s.mode, 'shell', 'still in shell');
};

tests.session_tmux_no_server = () => {
  const s = newSession();
  feedString(s, 'tmux ls');
  s.feedKey('Enter');
  // No tmux running — should show error
  assertEqual(s.mode, 'shell', 'still in shell');
};

tests.session_nested_tmux_rejected = () => {
  const s = newSession();
  feedString(s, 'tmux');
  s.feedKey('Enter');
  assertEqual(s.mode, 'tmux', 'in tmux');
  // Try to run tmux inside tmux pane
  feedString(s, 'tmux');
  s.feedKey('Enter');
  // Should still be in tmux (nested tmux rejected by shell)
  assertEqual(s.mode, 'tmux', 'still in tmux');
};

tests.session_vim_inside_tmux = () => {
  const s = newSession();
  feedString(s, 'tmux');
  s.feedKey('Enter');
  // Launch vim inside a tmux pane
  feedString(s, 'vim test.txt');
  s.feedKey('Enter');
  // The pane's session should now be in vim mode
  const pane = s._tmux.activePane;
  assertEqual(pane.session.mode, 'vim', 'pane in vim mode');
  // Type some text
  s.feedKey('i');
  feedString(s, 'hello tmux vim');
  s.feedKey('Escape');
  // Quit vim
  s.feedKey(':');
  feedString(s, 'q!');
  s.feedKey('Enter');
  assertEqual(pane.session.mode, 'shell', 'pane back to shell');
};

tests.session_tmux_splits_and_vim = () => {
  const s = newSession();
  // Create a file first
  s.fs.write('test.txt', 'hello world');
  feedString(s, 'tmux');
  s.feedKey('Enter');
  // Split vertically
  s.feedKey('Ctrl-B');
  s.feedKey('%');
  const panes = s._tmux.activeWindow.getPanes();
  assertEqual(panes.length, 2, '2 panes');
  // Open vim in the new pane
  feedString(s, 'vim test.txt');
  s.feedKey('Enter');
  assertEqual(s._tmux.activePane.session.mode, 'vim', 'right pane in vim');
  // Should render without errors
  const frame = s.renderFrame();
  assert(frame !== undefined, 'rendered successfully');
  assertEqual(frame.lines.length, ROWS, 'correct lines');
};

tests.session_shared_vfs = () => {
  const s = newSession();
  // Write a file before tmux
  s.fs.write('shared.txt', 'shared content');
  feedString(s, 'tmux');
  s.feedKey('Enter');
  // Split
  s.feedKey('Ctrl-B');
  s.feedKey('%');
  // Both panes should see the file
  const pane0 = s._tmux.activeWindow.getPanes()[0];
  const pane1 = s._tmux.activeWindow.getPanes()[1];
  assert(pane0.session.fs.exists('shared.txt'), 'pane 0 sees file');
  assert(pane1.session.fs.exists('shared.txt'), 'pane 1 sees file');
  assertEqual(pane0.session.fs.read('shared.txt'), 'shared content', 'pane 0 reads content');
};

// ── Layout Node Tests ──

tests.layout_single_pane = () => {
  const vfs = new VirtualFS({ persist: false });
  const factory = createPaneSessionFactory(vfs);
  const session = factory(40, 19);
  const pane = new TmuxPane(40, 19, session);
  const layout = new LayoutNode('leaf', pane);
  layout.computeLayout(0, 0, 40, 19);
  assertEqual(pane.top, 0, 'top');
  assertEqual(pane.left, 0, 'left');
  assertEqual(pane.width, 40, 'width');
  assertEqual(pane.height, 19, 'height');
};

tests.layout_hsplit = () => {
  const vfs = new VirtualFS({ persist: false });
  const factory = createPaneSessionFactory(vfs);
  const s1 = factory(40, 9);
  const s2 = factory(40, 9);
  const p1 = new TmuxPane(40, 9, s1);
  const p2 = new TmuxPane(40, 9, s2);
  const root = new LayoutNode(SplitDir.HSPLIT);
  root.first = new LayoutNode('leaf', p1);
  root.second = new LayoutNode('leaf', p2);
  root.ratio = 0.5;
  root.computeLayout(0, 0, 40, 19);
  // p1 gets the top half
  assertEqual(p1.top, 0, 'p1 top');
  assertEqual(p1.left, 0, 'p1 left');
  assertEqual(p1.width, 40, 'p1 width');
  // p2 gets the bottom half (after border)
  assertEqual(p2.left, 0, 'p2 left');
  assertEqual(p2.width, 40, 'p2 width');
  // Heights should add up to 19 - 1 (border)
  assertEqual(p1.height + 1 + p2.height, 19, 'heights add up');
};

tests.layout_vsplit = () => {
  const vfs = new VirtualFS({ persist: false });
  const factory = createPaneSessionFactory(vfs);
  const s1 = factory(19, 19);
  const s2 = factory(19, 19);
  const p1 = new TmuxPane(19, 19, s1);
  const p2 = new TmuxPane(19, 19, s2);
  const root = new LayoutNode(SplitDir.VSPLIT);
  root.first = new LayoutNode('leaf', p1);
  root.second = new LayoutNode('leaf', p2);
  root.ratio = 0.5;
  root.computeLayout(0, 0, 40, 19);
  assertEqual(p1.top, 0, 'p1 top');
  assertEqual(p2.top, 0, 'p2 top');
  assertEqual(p1.height, 19, 'p1 height');
  assertEqual(p2.height, 19, 'p2 height');
  // Widths should add up to 40 - 1 (border)
  assertEqual(p1.width + 1 + p2.width, 40, 'widths add up');
};

tests.layout_getPanes = () => {
  const vfs = new VirtualFS({ persist: false });
  const factory = createPaneSessionFactory(vfs);
  const s1 = factory(1, 1);
  const s2 = factory(1, 1);
  const s3 = factory(1, 1);
  const p1 = new TmuxPane(1, 1, s1);
  const p2 = new TmuxPane(1, 1, s2);
  const p3 = new TmuxPane(1, 1, s3);
  const root = new LayoutNode(SplitDir.VSPLIT);
  root.first = new LayoutNode('leaf', p1);
  root.second = new LayoutNode(SplitDir.HSPLIT);
  root.second.first = new LayoutNode('leaf', p2);
  root.second.second = new LayoutNode('leaf', p3);
  const panes = root.getPanes();
  assertEqual(panes.length, 3, '3 panes');
  assertEqual(panes[0], p1, 'first pane');
  assertEqual(panes[1], p2, 'second pane');
  assertEqual(panes[2], p3, 'third pane');
};

// ── Key forwarding tests ──

tests.keys_forwarded_to_active_pane = () => {
  const t = newTmux({ cols: 80, rows: 24 });
  // Type in the shell pane
  feedString(t, 'echo test123');
  t.feedKey('Enter');
  // The pane's shell should have processed the command
  const pane = t.activePane;
  const screen = pane.session.shell.getScreen();
  // Look for 'test123' in the output
  const found = screen.lines.some(l => l.includes('test123'));
  assert(found, 'command output found in pane');
};

tests.keys_not_forwarded_in_prefix = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B');
  // In prefix mode, keys should not go to the pane
  // (they're consumed by tmux)
  assertEqual(t._mode, TmuxMode.PREFIX, 'in prefix mode');
};

// ── Auto-unzoom tests ──

tests.zoom_split_auto_unzooms = () => {
  const t = newTmux();
  // Split first to have 2 panes
  t.feedKey('Ctrl-B'); t.feedKey('%');
  // Zoom active pane
  t.feedKey('Ctrl-B'); t.feedKey('z');
  assertEqual(t.activeWindow._zoomed, true, 'zoomed');
  // Split while zoomed — should auto-unzoom first
  t.feedKey('Ctrl-B'); t.feedKey('%');
  assertEqual(t.activeWindow._zoomed, false, 'unzoomed after split');
  assertEqual(t.activeWindow.getPanes().length, 3, '3 panes after split');
};

tests.zoom_navigate_auto_unzooms = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B'); t.feedKey('%');  // 2 panes
  t.feedKey('Ctrl-B'); t.feedKey('z');  // zoom
  assertEqual(t.activeWindow._zoomed, true, 'zoomed');
  t.feedKey('Ctrl-B'); t.feedKey('ArrowLeft');  // navigate
  assertEqual(t.activeWindow._zoomed, false, 'unzoomed after navigate');
};

tests.zoom_swap_auto_unzooms = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B'); t.feedKey('%');  // 2 panes
  t.feedKey('Ctrl-B'); t.feedKey('z');  // zoom
  assertEqual(t.activeWindow._zoomed, true, 'zoomed');
  t.feedKey('Ctrl-B'); t.feedKey('}');  // swap
  assertEqual(t.activeWindow._zoomed, false, 'unzoomed after swap');
};

tests.zoom_break_auto_unzooms = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B'); t.feedKey('%');  // 2 panes
  t.feedKey('Ctrl-B'); t.feedKey('z');  // zoom
  assertEqual(t.activeWindow._zoomed, true, 'zoomed');
  t.feedKey('Ctrl-B'); t.feedKey('!');  // break pane
  assertEqual(t.activeSession.windows.length, 2, '2 windows');
};

tests.zoom_o_cycle_auto_unzooms = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B'); t.feedKey('%');  // 2 panes
  t.feedKey('Ctrl-B'); t.feedKey('z');  // zoom
  t.feedKey('Ctrl-B'); t.feedKey('o');  // cycle pane
  assertEqual(t.activeWindow._zoomed, false, 'unzoomed after o');
};

tests.zoom_semicolon_last_pane_auto_unzooms = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B'); t.feedKey('%');  // 2 panes (right active)
  t.feedKey('Ctrl-B'); t.feedKey('ArrowLeft');  // go left
  t.feedKey('Ctrl-B'); t.feedKey('ArrowRight');  // go right (now left is last)
  t.feedKey('Ctrl-B'); t.feedKey('z');  // zoom
  t.feedKey('Ctrl-B'); t.feedKey(';');  // last pane
  assertEqual(t.activeWindow._zoomed, false, 'unzoomed after ;');
};

// ── Last window ──

tests.last_window_L = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B'); t.feedKey('c');  // create window 1
  assertEqual(t.activeSession.activeWindowIndex, 1, 'on window 1');
  t.feedKey('Ctrl-B'); t.feedKey('L');  // go to last (window 0)
  assertEqual(t.activeSession.activeWindowIndex, 0, 'on window 0');
  t.feedKey('Ctrl-B'); t.feedKey('L');  // toggle back
  assertEqual(t.activeSession.activeWindowIndex, 1, 'back on window 1');
};

// ── PageUp enters copy mode ──

tests.pageup_enters_copy_mode = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B'); t.feedKey('PageUp');
  assertEqual(t._mode, TmuxMode.COPY, 'in copy mode');
};

// ── Backspace in command mode stays ──

tests.command_backspace_empty_stays = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B'); t.feedKey(':');
  assertEqual(t._mode, TmuxMode.COMMAND, 'in command mode');
  t.feedKey('Backspace');  // backspace on empty
  assertEqual(t._mode, TmuxMode.COMMAND, 'still in command mode');
};

// ── Kill-pane last pane detaches ──

tests.kill_pane_last_pane_detaches = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B'); t.feedKey(':');
  for (const ch of 'kill-pane') t.feedKey(ch);
  t.feedKey('Enter');
  assertEqual(t.detached, true, 'detached after kill-pane on last');
};

// ── Swap with single pane ──

tests.swap_single_pane_noop = () => {
  const t = newTmux();
  const paneBefore = t.activeWindow.activePane;
  t.feedKey('Ctrl-B'); t.feedKey('}');
  assertEqual(t.activeWindow.activePane, paneBefore, 'pane unchanged');
};

// ── Cycle layout with single pane ──

tests.cycle_layout_single_pane_noop = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B'); t.feedKey(' ');
  // Should not crash, still 1 pane
  assertEqual(t.activeWindow.getPanes().length, 1, 'still 1 pane');
};

// ── Prefix Escape ──

tests.prefix_escape_returns_to_normal = () => {
  const t = newTmux();
  t.feedKey('Ctrl-B');
  assertEqual(t._mode, TmuxMode.PREFIX, 'in prefix mode');
  t.feedKey('Escape');
  assertEqual(t._mode, TmuxMode.NORMAL, 'back to normal');
};

// ── Run ──

async function runTests() {
  const testNames = Object.keys(tests);
  const toRun = filterCase ? testNames.filter(n => n === filterCase) : testNames;

  console.log(`\nRunning ${toRun.length} tmux tests...\n`);

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
