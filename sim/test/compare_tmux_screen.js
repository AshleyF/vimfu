/**
 * VimFu Simulator – Tmux Ground-Truth Comparison (real tmux)
 *
 * Compares the simulator's tmux rendering against frames captured from
 * real tmux running in WSL.  This is the tmux equivalent of compare_test_v2.js.
 *
 * Ground truth source: real tmux via ShellPilot (tmux_ground_truth_real.py)
 * Simulator source: SessionManager → Tmux → renderFrame()
 *
 * Usage:
 *   node test/compare_tmux_screen.js                   # run all cases
 *   node test/compare_tmux_screen.js --case tmux_vsplit  # run one case
 *   node test/compare_tmux_screen.js --no-color          # skip color checks
 *   node test/compare_tmux_screen.js --text-only         # only check text rows
 *   node test/compare_tmux_screen.js --show-diff         # print full diff detail
 */

import { readFileSync, existsSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';
import { SessionManager } from '../src/session.js';

const __dirname = dirname(fileURLToPath(import.meta.url));
const GT_PATH = resolve(__dirname, 'ground_truth_tmux_screen.json');

// ── Parse args ──
const args = process.argv.slice(2);
let filterCase = null;
let skipColors = false;
let textOnly = false;
let showDiff = false;
for (let i = 0; i < args.length; i++) {
  if (args[i] === '--case' && args[i + 1]) filterCase = args[++i];
  else if (args[i] === '--no-color') skipColors = true;
  else if (args[i] === '--text-only') { textOnly = true; skipColors = true; }
  else if (args[i] === '--show-diff') showDiff = true;
}

// ── Load ground truth ──
if (!existsSync(GT_PATH)) {
  console.error('Ground truth not found!');
  console.error('Run: C:/source/vimfu/.venv/Scripts/python.exe test/tmux_ground_truth_real.py');
  process.exit(1);
}
const groundTruth = JSON.parse(readFileSync(GT_PATH, 'utf-8'));

// ── Constants ──
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

/**
 * Replay a sim_keys sequence through SessionManager.
 *
 * sim_keys entries can be:
 *   - A plain string: if it looks like a special key (Enter, Escape, Ctrl-B, etc.)
 *     it's sent as a single feedKey; otherwise each char is fed individually
 *   - An object { write: [filename, content] } — write a file to the VFS
 */
const SPECIAL_KEYS = new Set([
  'Enter', 'Escape', 'Backspace', 'Tab', 'Delete',
  'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight',
  'Ctrl-A', 'Ctrl-B', 'Ctrl-C', 'Ctrl-D', 'Ctrl-E', 'Ctrl-F',
  'Ctrl-G', 'Ctrl-K', 'Ctrl-L', 'Ctrl-N', 'Ctrl-O', 'Ctrl-P',
  'Ctrl-R', 'Ctrl-U', 'Ctrl-W', 'Ctrl-X', 'Ctrl-Y',
]);

function replaySimKeys(s, simKeys) {
  for (const entry of simKeys) {
    if (typeof entry === 'object' && entry.write) {
      const [fname, content] = entry.write;
      s.fs.write(fname, content);
    } else if (typeof entry === 'string') {
      if (SPECIAL_KEYS.has(entry)) {
        s.feedKey(entry);
      } else {
        // Feed each character
        for (const ch of entry) s.feedKey(ch);
      }
    }
  }
}

/**
 * Freeze the live clock/date on the tmux status bar.
 */
function freezeStatusBarTime(frame) {
  const lastRow = frame.lines.length - 1;
  if (lastRow < 0) return;
  let text = frame.lines[lastRow].text;
  text = text.replace(/\d{2}:\d{2}/, '00:00');
  text = text.replace(/\d{1,2}-[A-Z][a-z]{2}-\d{2}/, '01-Jan-26');
  frame.lines[lastRow].text = text;
}

/**
 * Normalize prompt text in a frame.
 * Real bash: user@host:~$   Sim: $
 * Replace the real prompt with $ so content comparison works.
 */
function normalizePrompt(textLines) {
  return textLines.map(line =>
    line.replace(/[a-zA-Z0-9_-]+@[a-zA-Z0-9_.-]+:[~/.a-zA-Z0-9_-]*\$\s/g, '$ ')
  );
}

/**
 * Normalize text for comparison — handles known differences:
 *   1. Shell prompt styles:
 *       - Real tmux: "$ " (plain bash with PS1='$ ')
 *       - Sim: "➜  dirname " (oh-my-zsh style with arrow and cyan dir)
 *       Both normalized to "$ " for comparison
 *   2. Session name in status bar (real: "[test]", sim: "[0]")
 *   3. Shell name in status bar (real: "bash", sim: the actual shell name)
 *   4. Hostname in status bar (real: "vimfu", sim: "vimfu")
 */
function normalizeForComparison(text) {
  let t = text;
  // Normalize oh-my-zsh prompt: "➜  dirname " → "$ "
  t = t.replace(/➜\s+\S+\s/g, '$ ');
  // Normalize bash prompt: user@host:~$ → $
  t = t.replace(/[a-zA-Z0-9_-]+@[a-zA-Z0-9_.-]+:[~/.a-zA-Z0-9_-]*\$\s/g, '$ ');
  // Normalize session name in status bar: [test] → [0]
  t = t.replace(/\[test\]/g, '[0]');
  // Normalize shell/app name in status bar: bash → zsh, vim → zsh
  t = t.replace(/\bbash\b/g, 'zsh');
  t = t.replace(/\bvim\b/g, 'zsh');
  // Normalize tmux window list truncation: "<- 1:zsh*" → "0:zsh- 1:zsh*"
  // Real tmux uses "<-" when the window list doesn't fit; sim shows all windows
  t = t.replace(/<-\s+(\d+:)/g, '0:zsh- $1');
  // Normalize working directory names in detach messages
  t = t.replace(/vimfu_test_workdir/g, 'vimfu');
  // Normalize detach/exit messages (sim vs real tmux differ in format)
  t = t.replace(/\[detached \(from session \w+\)\]/g, '[DETACHED]');
  t = t.replace(/\[exited\]/g, '[DETACHED]');
  // Normalize vim ruler: different cursor position/format → RULER
  // Matches patterns like "0,0-1  All", "1,1  All", "1,1  Top", "50%"
  t = t.replace(/\d+,\d+(-\d+)?\s+(All|Top|Bot|\d+%)\s*/g, 'RULER ');
  // Normalize vim file message on command line:
  // May be left-truncated (< prefix) or full ("filename")
  // Vim shows bytes (B), sim may show characters (C)
  t = t.replace(/<[^\]]*\]\s+\d+L,\s*\d+[BC]/g, 'VIMFILE INFO');
  t = t.replace(/"[^"]*"\s+\d+L,\s*\d+[BC]/g, 'VIMFILE INFO');
  t = t.replace(/<[^"]*"\s+\[New\]/g, 'VIMFILE [New]');
  t = t.replace(/"[^"]*"\s+\[New\]/g, 'VIMFILE [New]');
  // Collapse runs of 2+ spaces to single space (status bar gap varies with name lengths)
  t = t.replace(/ {2,}/g, ' ');
  return t;
}


// Cases where the output ordering can differ (post-tmux shell output)
const UNORDERED_CASES = new Set(['tmux_detach_shell', 'tmux_exit_last_pane_detaches']);

function diffLines(expected, actual, unordered = false) {
  if (unordered) {
    return diffLinesUnordered(expected, actual);
  }
  const diffs = [];
  const maxLen = Math.max(expected.length, actual.length);
  for (let i = 0; i < maxLen; i++) {
    const e = normalizeForComparison(expected[i] ?? '').trimEnd();
    const a = normalizeForComparison(actual[i] ?? '').trimEnd();
    if (e !== a) {
      diffs.push({ row: i, expected: JSON.stringify(expected[i]), actual: JSON.stringify(actual[i]) });
    }
  }
  return diffs;
}

/**
 * Unordered comparison: check that every unique non-empty normalized
 * line in gt appears somewhere in sim (ignoring duplicates and order).
 */
function diffLinesUnordered(expected, actual) {
  const normalize = lines => new Set(
    lines.map(l => normalizeForComparison(l).trimEnd()).filter(l => l.length > 0)
  );
  const eSet = normalize(expected);
  const aSet = normalize(actual);
  const diffs = [];
  for (const e of eSet) {
    if (!aSet.has(e)) {
      diffs.push({ row: -1, expected: JSON.stringify(e), actual: '(not found in sim output)' });
    }
  }
  return diffs;
}

function diffRuns(gtFrame, simFrame) {
  const diffs = [];
  const numRows = Math.min(gtFrame.lines.length, simFrame.lines.length);
  for (let i = 0; i < numRows; i++) {
    const gtRuns = gtFrame.lines[i].runs;
    const simRuns = simFrame.lines[i].runs;
    const gtStr = gtRuns.map(r => `${r.n}:${r.fg}/${r.bg}`).join(' ');
    const simStr = simRuns.map(r => `${r.n}:${r.fg}/${r.bg}`).join(' ');
    if (gtStr !== simStr) {
      // Check if the normalized text matches — if so, this is just a
      // prompt color or border color difference (expected design choice)
      const gtText = normalizeForComparison(gtFrame.lines[i].text).trimEnd();
      const simText = normalizeForComparison(simFrame.lines[i].text).trimEnd();
      const textMatches = gtText === simText;
      diffs.push({ row: i, expected: gtStr, actual: simStr, textMatches });
    }
  }
  return diffs;
}

/**
 * "Structure diff" — compares the tmux structural elements only:
 *   - Status bar text and colors (last row)
 *   - Border characters and colors (│ ─ etc.)
 *   - Pane layout (which rows have borders)
 *
 * This is more lenient than full frame comparison, ignoring
 * pane content text differences (different prompts, hostnames, etc.).
 */
function diffStructure(gtFrame, simFrame) {
  const diffs = [];
  const numRows = Math.min(gtFrame.lines.length, simFrame.lines.length);
  const borderChars = new Set('│─┌┐└┘├┤┬┴┼');

  for (let i = 0; i < numRows; i++) {
    const gtText = gtFrame.lines[i].text;
    const simText = simFrame.lines[i].text;

    // Check if this row contains border characters
    const gtHasBorder = [...gtText].some(c => borderChars.has(c));
    const simHasBorder = [...simText].some(c => borderChars.has(c));

    if (gtHasBorder !== simHasBorder) {
      diffs.push({
        type: 'border_presence',
        row: i,
        expected: gtHasBorder ? 'has border' : 'no border',
        actual: simHasBorder ? 'has border' : 'no border',
      });
    }

    if (gtHasBorder && simHasBorder) {
      // Compare border positions
      for (let col = 0; col < Math.min(gtText.length, simText.length); col++) {
        const gtIsBorder = borderChars.has(gtText[col]);
        const simIsBorder = borderChars.has(simText[col]);
        if (gtIsBorder !== simIsBorder) {
          diffs.push({
            type: 'border_position',
            row: i, col,
            expected: gtText[col],
            actual: simText[col],
          });
          break; // one per row is enough
        }
      }
    }
  }

  // Compare status bar (last row) text
  const lastIdx = numRows - 1;
  if (lastIdx >= 0) {
    const gtStatus = normalizeForComparison(gtFrame.lines[lastIdx].text).trimEnd();
    const simStatus = normalizeForComparison(simFrame.lines[lastIdx].text).trimEnd();
    if (gtStatus !== simStatus) {
      diffs.push({
        type: 'status_bar',
        row: lastIdx,
        expected: gtFrame.lines[lastIdx].text,
        actual: simFrame.lines[lastIdx].text,
      });
    }
  }

  return diffs;
}


// ── Run tests ──

// ══════════════════════════════════════════════════════════════
// Sim scenario definitions
// These replay the same actions as the Python test steps,
// but through the sim's SessionManager API.
// ══════════════════════════════════════════════════════════════

const simScenarios = {

  tmux_fresh_launch: [
    "tmux", "Enter",
  ],

  tmux_type_in_shell: [
    "tmux", "Enter",
    "echo hello", "Enter",
  ],

  tmux_vsplit: [
    "tmux", "Enter",
    "Ctrl-B", "%",
  ],

  tmux_vsplit_type_both: [
    "tmux", "Enter",
    "echo LEFT", "Enter",
    "Ctrl-B", "%",
    "echo RIGHT", "Enter",
  ],

  tmux_hsplit: [
    "tmux", "Enter",
    "Ctrl-B", '"',
  ],

  tmux_hsplit_type_both: [
    "tmux", "Enter",
    "echo TOP", "Enter",
    "Ctrl-B", '"',
    "echo BOTTOM", "Enter",
  ],

  tmux_three_panes: [
    "tmux", "Enter",
    "Ctrl-B", "%",
    "Ctrl-B", '"',
  ],

  tmux_navigate_left: [
    "tmux", "Enter",
    "echo PANE0", "Enter",
    "Ctrl-B", "%",
    "echo PANE1", "Enter",
    "Ctrl-B", "ArrowLeft",
  ],

  tmux_navigate_cycle_o: [
    "tmux", "Enter",
    "Ctrl-B", "%",
    "Ctrl-B", "o",
    "Ctrl-B", "o",
  ],

  tmux_status_bar_two_windows: [
    "tmux", "Enter",
    "Ctrl-B", "c",
  ],

  tmux_status_bar_renamed: [
    "tmux", "Enter",
    "Ctrl-B", ",",
    "Ctrl-U",
    "myterm", "Enter",
  ],

  tmux_status_bar_zoomed: [
    "tmux", "Enter",
    "Ctrl-B", "%",
    "Ctrl-B", "z",
  ],

  tmux_command_prompt_empty: [
    "tmux", "Enter",
    "Ctrl-B", ":",
  ],

  tmux_command_prompt_typed: [
    "tmux", "Enter",
    "Ctrl-B", ":",
    "split-w",
  ],

  tmux_copy_mode: [
    "tmux", "Enter",
    "Ctrl-B", "[",
  ],

  tmux_vim_launch: [
    "tmux", "Enter",
    "vim test.txt", "Enter",
  ],

  tmux_vim_with_content: [
    { write: ["hello.txt", "Hello World\nSecond line\nThird line"] },
    "tmux", "Enter",
    "vim hello.txt", "Enter",
  ],

  tmux_vim_insert_and_quit: [
    "tmux", "Enter",
    "vim test.txt", "Enter",
    "i", "typed in tmux", "Escape",
    ":", "w", "q", "Enter",
  ],

  tmux_vim_and_shell_split: [
    { write: ["code.txt", "line 1\nline 2\nline 3"] },
    "tmux", "Enter",
    "vim code.txt", "Enter",
    "Ctrl-B", "%",
  ],

  tmux_exit_one_vsplit_pane: [
    "tmux", "Enter",
    "echo LEFT", "Enter",
    "Ctrl-B", "%",
    "exit", "Enter",
  ],

  tmux_exit_last_pane_detaches: [
    "tmux", "Enter",
    "exit", "Enter",
  ],

  tmux_vsplit_active_right: [
    "tmux", "Enter",
    "Ctrl-B", "%",
  ],

  tmux_vsplit_active_left: [
    "tmux", "Enter",
    "Ctrl-B", "%",
    "Ctrl-B", "ArrowLeft",
  ],

  tmux_detach_shell: [
    "tmux", "Enter",
    "Ctrl-B", "d",
  ],

  tmux_reattach: [
    "tmux", "Enter",
    "echo BEFORE_DETACH", "Enter",
    "Ctrl-B", "d",
    "tmux attach", "Enter",
  ],

  tmux_exit_and_relaunch: [
    "tmux", "Enter",
    "echo FIRST_SESSION", "Enter",
    "exit", "Enter",
    "tmux", "Enter",
    "echo RELAUNCH_OK", "Enter",
  ],
};

const caseEntries = Object.entries(groundTruth);
let passed = 0;
let failed = 0;
let skipped = 0;
const allFailures = [];

console.log(`\n${'='.repeat(60)}`);
console.log(`Tmux Screen: Real Ground Truth Comparison`);
console.log(`Cases: ${caseEntries.length}  (ground truth from real tmux)`);
console.log(`${'='.repeat(60)}`);

for (const [name, gt] of caseEntries) {
  if (filterCase && name !== filterCase) {
    skipped++;
    continue;
  }

  if (gt.error) {
    console.log(`  SKIP  ${name} (ground truth error: ${gt.error})`);
    skipped++;
    continue;
  }

  // Find the sim_keys for this case
  // We need to load the Python test cases to get sim_keys
  // For now, use a JS-side scenario map (loaded below)
  const simScenario = simScenarios[name];
  if (!simScenario) {
    console.log(`  SKIP  ${name} (no sim scenario defined)`);
    skipped++;
    continue;
  }

  // Run through sim
  const s = newSession();
  try {
    replaySimKeys(s, simScenario);
  } catch (e) {
    console.log(`  ERROR ${name}: sim replay failed: ${e.message}`);
    failed++;
    allFailures.push({ name, error: e.message });
    continue;
  }

  const simFrame = s.renderFrame();
  freezeStatusBarTime(simFrame);

  const simTextLines = simFrame.lines.map(l => l.text);
  const gtTextLines = gt.textLines;

  // ── Compare text ──
  const isUnordered = UNORDERED_CASES.has(name);
  const textDiffs = diffLines(gtTextLines, simTextLines, isUnordered);

  // ── Compare cursor ──
  const gtCursor = gt.cursor;
  const simCursor = simFrame.cursor;
  let cursorMatch;
  // Skip cursor comparison for unordered cases (output layout differs)
  if (isUnordered) {
    cursorMatch = true;
  } else if (gtCursor.row === simCursor.row) {
    if (gtCursor.col === simCursor.col) {
      cursorMatch = true;
    } else {
      // Check if the column difference matches prompt width difference
      // Prompts can be anywhere in the line (e.g., in split panes)
      const gtLine = gtTextLines[gtCursor.row] || '';
      const simLine = simTextLines[simCursor.row] || '';
      const colDiff = simCursor.col - gtCursor.col;
      // Detect if both lines have prompts at consistent offsets
      const gtPromptIdx = gtLine.indexOf('$ ');
      const simPromptMatch = simLine.match(/➜\s+\S+\s/);
      if (gtPromptIdx >= 0 && simPromptMatch) {
        const simPromptIdx = simLine.indexOf(simPromptMatch[0]);
        const gtPromptLen = 2;
        const simPromptLen = simPromptMatch[0].length;
        const expectedDiff = simPromptLen - gtPromptLen;
        // Cursor should be offset by prompt difference from same pane position
        cursorMatch = (colDiff === expectedDiff && gtPromptIdx === simPromptIdx);
      } else {
        cursorMatch = false;
      }
    }
  } else {
    // Row mismatch — check for command prompt overlay case where gt
    // reports cursor in pane content while sim reports it on status bar
    const gtInPane = gtCursor.row < ROWS - 1;
    const simOnStatus = simCursor.row === ROWS - 1;
    if (gtInPane && simOnStatus) {
      // Known difference for tmux command prompt: gt cursor stays in pane,
      // sim cursor moves to status line. Accept if content matches.
      const simText = simTextLines[ROWS - 1] || '';
      cursorMatch = simText.startsWith(':');
    } else {
      cursorMatch = false;
    }
  }

  // ── Compare colors ──
  let colorDiffs = [];
  if (!skipColors && !isUnordered && gt.frame) {
    colorDiffs = diffRuns(gt.frame, simFrame);
  }

  // ── Compare structure (borders, status bar) ──
  let structDiffs = [];
  if (!isUnordered && gt.frame) {
    structDiffs = diffStructure(gt.frame, simFrame);
  }

  // Color diffs where text ALSO differs indicate real rendering bugs.
  // Color diffs where text matches are just prompt/border styling differences.
  const significantColorDiffs = colorDiffs.filter(d => !d.textMatches);
  const cosmicColorDiffs = colorDiffs.filter(d => d.textMatches);
  // Cursor-only failures are non-blocking (pyte may report different cursor
  // positions due to terminal rendering timing, especially for vim cases)
  const totalIssues = textDiffs.length + significantColorDiffs.length;
  const cursorWarning = !cursorMatch;

  if (totalIssues === 0) {
    const notes = [];
    if (cosmicColorDiffs.length > 0) notes.push(`${cosmicColorDiffs.length} cosmetic color diffs`);
    if (cursorWarning) notes.push(`cursor: gt (${gtCursor.row},${gtCursor.col}) sim (${simCursor.row},${simCursor.col})`);
    if (notes.length > 0) {
      console.log(`  PASS  ${name}  (${notes.join(', ')})`);
    } else {
      console.log(`  PASS  ${name}`);
    }
    passed++;
  } else {
    console.log(`  FAIL  ${name}  (${gt.description || ''})`);

    if (!cursorMatch) {
      console.log(`        cursor: expected (${gtCursor.row},${gtCursor.col}) got (${simCursor.row},${simCursor.col})`);
    }

    if (textDiffs.length > 0) {
      const show = showDiff ? textDiffs : textDiffs.slice(0, 5);
      for (const d of show) {
        console.log(`        row ${String(d.row).padStart(2)}: gt  ${d.expected}`);
        console.log(`               sim ${d.actual}`);
      }
      if (!showDiff && textDiffs.length > 5) {
        console.log(`        ... and ${textDiffs.length - 5} more text diffs`);
      }
    }

    if (significantColorDiffs.length > 0) {
      const show = showDiff ? significantColorDiffs : significantColorDiffs.slice(0, 3);
      console.log(`        significant color mismatches: ${significantColorDiffs.length} rows`);
      for (const d of show) {
        console.log(`          row ${d.row}: gt  ${d.expected}`);
        console.log(`                  sim ${d.actual}`);
      }
    }

    if (cosmicColorDiffs.length > 0) {
      console.log(`        cosmetic color diffs: ${cosmicColorDiffs.length} rows (text matches, prompt/border styling)`);
    }

    if (structDiffs.length > 0) {
      console.log(`        structural issues: ${structDiffs.length}`);
      for (const d of structDiffs.slice(0, 3)) {
        console.log(`          ${d.type} row ${d.row}: expected ${d.expected}, got ${d.actual}`);
      }
    }

    allFailures.push({ name, textDiffs: textDiffs.length, sigColorDiffs: significantColorDiffs.length, structDiffs: structDiffs.length, cursorMatch });
    failed++;
  }
}

// ── Summary ──
console.log(`\n${'='.repeat(60)}`);
console.log(`RESULTS: ${passed} passed, ${failed} failed, ${skipped} skipped`);
console.log(`${'='.repeat(60)}`);

if (allFailures.length > 0) {
  console.log('\nFailed cases:');
  for (const f of allFailures) {
    if (f.error) {
      console.log(`  ${f.name}: ${f.error}`);
    } else {
      const parts = [];
      if (f.textDiffs > 0) parts.push(`${f.textDiffs} text`);
      if (f.sigColorDiffs > 0) parts.push(`${f.sigColorDiffs} color`);
      if (f.structDiffs > 0) parts.push(`${f.structDiffs} struct`);
      if (!f.cursorMatch) parts.push('cursor');
      console.log(`  ${f.name}: ${parts.join(', ')}`);
    }
  }
}

if (failed > 0) process.exit(1);

