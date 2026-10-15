/**
 * Mutation checks for the Neovim oracle suite.
 *
 * This is deliberately separate from code coverage.  Each behavioral mutant
 * makes the simulator observably wrong, and the test passes only when at least
 * one previously passing oracle case kills it.  The observation mutants prove
 * that every field we claim to compare is actually capable of failing a test.
 */

import { readFileSync, readdirSync } from 'fs';
import { dirname, resolve } from 'path';
import { fileURLToPath } from 'url';
import { VimEngine } from '../src/engine.js';
import { Screen } from '../src/screen.js';
import { SessionManager } from '../src/session.js';

const here = dirname(fileURLToPath(import.meta.url));
const ROWS = 20;
const COLS = 40;

function feedKeys(feed, keys) {
  for (let i = 0; i < keys.length; i++) {
    const ch = keys[i];
    if (ch === '\x1b' && keys[i + 1] === '[') {
      const arrows = { A: 'ArrowUp', B: 'ArrowDown', C: 'ArrowRight', D: 'ArrowLeft' };
      if (arrows[keys[i + 2]]) { feed(arrows[keys[i + 2]]); i += 2; continue; }
      if (keys.slice(i, i + 4) === '\x1b[3~') { feed('Delete'); i += 3; continue; }
    }
    const controls = {
      '\x1b': 'Escape', '\r': 'Enter', '\n': 'Ctrl-J', '\x03': 'Ctrl-C',
      '\x08': 'Backspace', '\x7f': 'Backspace', '\x00': 'Ctrl-@', '\x01': 'Ctrl-A',
      '\x02': 'Ctrl-B', '\x04': 'Ctrl-D', '\x05': 'Ctrl-E', '\x06': 'Ctrl-F',
      '\x07': 'Ctrl-G', '\x09': 'Tab', '\x0b': 'Ctrl-K', '\x0c': 'Ctrl-L',
      '\x0e': 'Ctrl-N', '\x0f': 'Ctrl-O', '\x10': 'Ctrl-P', '\x12': 'Ctrl-R',
      '\x13': 'Ctrl-S', '\x14': 'Ctrl-T', '\x15': 'Ctrl-U', '\x16': 'Ctrl-V',
      '\x17': 'Ctrl-W', '\x18': 'Ctrl-X', '\x19': 'Ctrl-Y', '\x1d': 'Ctrl-]',
      '\x1e': 'Ctrl-^',
    };
    feed(controls[ch] || ch);
  }
}

function runCase(gt, mutateKey = null) {
  const engine = new VimEngine({ rows: ROWS, cols: COLS });
  if (gt.initialContent) engine.loadFile(gt.initialContent, gt.fileName || null);
  const originalFeed = engine.feedKey.bind(engine);
  feedKeys(key => {
    const replacement = mutateKey ? mutateKey(key, engine) : key;
    if (replacement !== null) originalFeed(replacement);
  }, gt.keys);
  return new Screen(ROWS, COLS, 'monokai').render(engine);
}

function runSessionCase(gt, configure = null) {
  const session = new SessionManager({ rows: ROWS, cols: COLS, persist: false });
  for (const [path, content] of Object.entries(gt.setupFiles || {})) {
    if (path !== 'init.lua') session.fs.write(path, content);
  }
  const launch = gt.launch || {};
  const launchFiles = (launch.files || []).filter(path => session.fs.exists(path));
  const fileName = launchFiles[0] || gt.fileName || 'test.txt';
  if (!gt.setupFiles && gt.initialContent != null) session.fs.write(fileName, gt.initialContent);
  for (const ch of `vim ${fileName}`) session.feedKey(ch);
  session.feedKey('Enter');
  if (launchFiles.length > 1) {
    for (const path of launchFiles.slice(1)) {
      session.engine._doSplit(launch.layout === 'vertical', false);
      session.engine.loadFile(session.fs.read(path), path);
    }
    session.engine._switchToWindow(0);
  }
  if (configure) configure(session);
  feedKeys(key => session.feedKey(key), gt.keys);
  return session;
}

function matchesSessionOracle(gt, session) {
  const expectedMode = gt.expectsExit ? 'shell' : 'vim';
  if (session.getMode() !== expectedMode) return false;
  const actualPaths = new Set(session.fs.ls());
  for (const [path, content] of Object.entries(gt.filesAfter || {})) {
    if (session.fs.read(path) !== content) return false;
    actualPaths.delete(path);
  }
  if (actualPaths.size > 0) return false;
  return gt.expectsExit || matchesOracle(gt, session.renderFrame());
}

function runSignature(run) {
  return `${run.n}:${run.fg}/${run.bg}/${run.b ? 'b' : ''}${run.i ? 'i' : ''}${run.u ? 'u' : ''}${run.s ? 's' : ''}`;
}

function matchesOracle(gt, frame) {
  if (!gt.textLines || !gt.cursor) return false;
  const text = frame.lines.slice(0, ROWS - 2).map(line => line.text);
  if (JSON.stringify(text) !== JSON.stringify(gt.textLines)) return false;
  if (frame.cursor.row !== gt.cursor.row || frame.cursor.col !== gt.cursor.col
      || frame.cursor.visible !== (gt.cursor.visible ?? true)) return false;
  if (gt.frame?.lines && !gt.colorError) {
    for (let row = 0; row < Math.min(ROWS, gt.frame.lines.length, frame.lines.length); row++) {
      // The production comparator includes text attributes in buffer rows.  On
      // status/cmdline rows it intentionally compares only color segmentation.
      const signature = row < ROWS - 2
        ? runSignature
        : run => `${run.n}:${run.fg}/${run.bg}`;
      const expected = gt.frame.lines[row].runs.map(signature).join(' ');
      const actual = frame.lines[row].runs.map(signature).join(' ');
      if (expected !== actual) return false;
    }
  }
  return true;
}

function loadCases() {
  const cases = [];
  for (const file of readdirSync(here).filter(name =>
    name.startsWith('ground_truth_') && name.endsWith('.json')
    && name !== 'ground_truth_all.json' && name !== 'ground_truth_tmux_screen.json')) {
    const suite = file.slice('ground_truth_'.length, -'.json'.length);
    const data = JSON.parse(readFileSync(resolve(here, file), 'utf8'));
    for (const [name, gt] of Object.entries(data)) {
      if (!gt.error && !gt.skip && gt.keys != null && !gt.setupFiles) cases.push({ suite, name, gt });
    }
  }
  return cases;
}

const candidates = loadCases();
const passing = [];
for (const candidate of candidates) {
  // Shell/session scenarios are intentionally outside this engine-level test.
  if (candidate.suite === 'filter' && candidate.gt.keys.includes('!')) continue;
  const frame = runCase(candidate.gt);
  if (matchesOracle(candidate.gt, frame)) passing.push(candidate);
}

function idleNormal(engine) {
  return engine.mode === 'normal'
    && !engine._pendingCtrlW && !engine._pendingOp && !engine._pendingG
    && !engine._pendingZ && !engine._pendingF && !engine._pendingR
    && !engine._pendingM && !engine._pendingQ && !engine._pendingAt;
}

const behavioralMutants = [
  ['ignore normal-mode left motion', (key, e) => key === 'h' && idleNormal(e) ? null : key],
  ['ignore normal-mode down motion', (key, e) => key === 'j' && idleNormal(e) ? null : key],
  ['ignore normal-mode right motion', (key, e) => key === 'l' && idleNormal(e) ? null : key],
  ['ignore normal-mode word motion', (key, e) => key === 'w' && idleNormal(e) ? null : key],
  ['ignore normal-mode backward-word motion', (key, e) => key === 'b' && idleNormal(e) ? null : key],
  ['ignore normal-mode end-of-word motion', (key, e) => key === 'e' && idleNormal(e) ? null : key],
  ['ignore entry to insert mode', (key, e) => key === 'i' && idleNormal(e) ? null : key],
  ['ignore normal-mode delete character', (key, e) => key === 'x' && idleNormal(e) ? null : key],
  ['ignore normal-mode delete operator', (key, e) => key === 'd' && idleNormal(e) ? null : key],
  ['ignore normal-mode change operator', (key, e) => key === 'c' && idleNormal(e) ? null : key],
  ['ignore normal-mode yank operator', (key, e) => key === 'y' && idleNormal(e) ? null : key],
  ['ignore normal-mode undo', (key, e) => key === 'u' && idleNormal(e) ? null : key],
  ['ignore normal-mode put', (key, e) => key === 'p' && idleNormal(e) ? null : key],
  ['ignore normal-mode dot repeat', (key, e) => key === '.' && idleNormal(e) ? null : key],
  ['ignore visual-mode entry', (key, e) => key === 'v' && idleNormal(e) ? null : key],
  ['ignore insert-mode newline', (key, e) => key === 'Enter' && e.mode === 'insert' ? null : key],
  ['ignore insert-mode backspace', (key, e) => key === 'Backspace' && e.mode === 'insert' ? null : key],
  ['ignore normal-mode search repeat', (key, e) => key === 'n' && idleNormal(e) && e._searchPattern ? null : key],
  ['reverse normal-mode half-page scroll', (key, e) => key === 'Ctrl-U' && idleNormal(e) ? 'Ctrl-D' : key],
  ['reverse normal-mode forward half-page scroll', (key, e) => key === 'Ctrl-D' && idleNormal(e) ? 'Ctrl-U' : key],
  ['ignore insert-mode escape', (key, e) => key === 'Escape' && e.mode === 'insert' ? null : key],
  ['ignore normal-mode line-start motion', (key, e) => key === '0' && idleNormal(e) ? null : key],
  ['ignore normal-mode line-end motion', (key, e) => key === '$' && idleNormal(e) ? null : key],
  ['ignore normal-mode file-end motion', (key, e) => key === 'G' && idleNormal(e) ? null : key],
  ['ignore normal-mode line join', (key, e) => key === 'J' && idleNormal(e) ? null : key],
  ['ignore normal-mode append', (key, e) => key === 'a' && idleNormal(e) ? null : key],
  ['ignore normal-mode open-below', (key, e) => key === 'o' && idleNormal(e) ? null : key],
  ['ignore normal-mode replace', (key, e) => key === 'r' && idleNormal(e) ? null : key],
  ['ignore normal-mode search entry', (key, e) => key === '/' && idleNormal(e) ? null : key],
  ['ignore command-line execution', (key, e) => key === 'Enter' && e.mode === 'command' ? null : key],
  ['ignore command-line completion', (key, e) => key === 'Tab' && e.mode === 'command' ? null : key],
  ['ignore command-line completion listing', (key, e) => key === 'Ctrl-D' && e.mode === 'command' ? null : key],
  ['ignore window-command prefix', (key, e) => key === 'Ctrl-W' && idleNormal(e) ? null : key],
  ['ignore macro-recording prefix', (key, e) => key === 'q' && idleNormal(e) ? null : key],
  ['ignore mark-setting prefix', (key, e) => key === 'm' && idleNormal(e) ? null : key],
  ['ignore visual delete', (key, e) => key === 'd' && e.mode.startsWith('visual') ? null : key],
];

let killed = 0;
for (const [name, mutateKey] of behavioralMutants) {
  const killer = passing.find(({ gt }) => !matchesOracle(gt, runCase(gt, mutateKey)));
  if (killer) {
    killed++;
    console.log(`KILLED   ${name} (${killer.suite}/${killer.name})`);
  } else {
    console.error(`SURVIVED ${name}`);
  }
}

const sessionCases = [];
for (const file of readdirSync(here).filter(name =>
  name.startsWith('ground_truth_') && name.endsWith('.json'))) {
  const suite = file.slice('ground_truth_'.length, -'.json'.length);
  const data = JSON.parse(readFileSync(resolve(here, file), 'utf8'));
  for (const [name, gt] of Object.entries(data)) {
    if (gt.requiresSession && !gt.error && !gt.skip) sessionCases.push({ suite, name, gt });
  }
}

const sessionMutants = [
  ['discard session file writes', session => { session._saveFile = () => {}; }],
  ['skip session filter transformation', session => {
    session.engine._tryBuiltinFilter = () => true;
  }],
  ['refuse to exit the editor session', session => { session._exitVim = () => {}; }],
];
let sessionKilled = 0;
for (const [name, configure] of sessionMutants) {
  const killer = sessionCases.find(({ gt }) => {
    const baseline = runSessionCase(gt);
    if (!matchesSessionOracle(gt, baseline)) return false;
    return !matchesSessionOracle(gt, runSessionCase(gt, configure));
  });
  if (killer) {
    sessionKilled++;
    console.log(`KILLED   ${name} (${killer.suite}/${killer.name})`);
  } else {
    console.error(`SURVIVED ${name}`);
  }
}

// Comparator sensitivity: corrupt one observed property of a known-good frame.
const witness = passing.find(({ gt }) => gt.frame?.lines?.some(line => line.runs.length));
if (!witness) throw new Error('No passing ground-truth case available for observation mutations');
const observationMutants = {
  text(frame) { frame.lines[0].text = `X${frame.lines[0].text.slice(1)}`; },
  'cursor row'(frame) { frame.cursor.row = (frame.cursor.row + 1) % ROWS; },
  'cursor column'(frame) { frame.cursor.col = (frame.cursor.col + 1) % COLS; },
  'cursor visibility'(frame) { frame.cursor.visible = !frame.cursor.visible; },
  foreground(frame) { frame.lines[0].runs[0].fg = '123456'; },
  background(frame) { frame.lines[0].runs[0].bg = '654321'; },
  bold(frame) { frame.lines[0].runs[0].b = !frame.lines[0].runs[0].b; },
  italic(frame) { frame.lines[0].runs[0].i = !frame.lines[0].runs[0].i; },
  underline(frame) { frame.lines[0].runs[0].u = !frame.lines[0].runs[0].u; },
  strikethrough(frame) { frame.lines[0].runs[0].s = !frame.lines[0].runs[0].s; },
};

let observed = 0;
for (const [name, mutate] of Object.entries(observationMutants)) {
  const frame = structuredClone(runCase(witness.gt));
  mutate(frame);
  if (!matchesOracle(witness.gt, frame)) {
    observed++;
    console.log(`OBSERVED ${name}`);
  } else {
    console.error(`MISSED   ${name}`);
  }
}

console.log(`\nBehavior mutation score: ${killed}/${behavioralMutants.length}`);
console.log(`Session mutation score: ${sessionKilled}/${sessionMutants.length}`);
console.log(`Observation sensitivity: ${observed}/${Object.keys(observationMutants).length}`);
console.log(`Baseline oracle cases used: ${passing.length}`);
if (killed !== behavioralMutants.length || sessionKilled !== sessionMutants.length
    || observed !== Object.keys(observationMutants).length) process.exit(1);
