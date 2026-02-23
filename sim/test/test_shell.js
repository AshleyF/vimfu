/**
 * VimFu Simulator – Shell & Session Tests
 *
 * Tests VirtualFS, ShellSim, and SessionManager integration.
 * Run: node test/test_shell.js
 */

import { VirtualFS } from '../src/vfs.js';
import { ShellSim } from '../src/shell.js';
import { SessionManager } from '../src/session.js';

let passed = 0;
let failed = 0;

function assert(cond, msg) {
  if (cond) {
    passed++;
  } else {
    failed++;
    console.log(`  FAIL  ${msg}`);
  }
}

function feedString(target, str) {
  for (const ch of str) target.feedKey(ch);
}

function getOutputLines(shell) {
  return shell.getScreen().lines
    .map(l => l.trimEnd())
    .filter(l => l.length > 0);
}

// ════════════════════════════════════════════════════════════════
// VirtualFS Tests
// ════════════════════════════════════════════════════════════════
console.log('============================================================');
console.log('Suite: VirtualFS');
console.log('============================================================');

{
  const fs = new VirtualFS({ persist: false });

  // Initially empty
  assert(fs.ls().length === 0, 'vfs: initially empty');
  assert(fs.fileCount === 0, 'vfs: fileCount 0');

  // Write and read
  fs.write('hello.txt', 'Hello, world!');
  assert(fs.exists('hello.txt'), 'vfs: exists after write');
  assert(fs.read('hello.txt') === 'Hello, world!', 'vfs: read matches write');
  assert(fs.fileCount === 1, 'vfs: fileCount 1');

  // ls returns sorted
  fs.write('alpha.txt', 'aaa');
  fs.write('zebra.txt', 'zzz');
  const listing = fs.ls();
  assert(listing[0] === 'alpha.txt', 'vfs: ls sorted first');
  assert(listing[listing.length - 1] === 'zebra.txt', 'vfs: ls sorted last');

  // Overwrite
  fs.write('hello.txt', 'Updated!');
  assert(fs.read('hello.txt') === 'Updated!', 'vfs: overwrite works');

  // Remove
  assert(fs.rm('hello.txt') === true, 'vfs: rm returns true');
  assert(fs.exists('hello.txt') === false, 'vfs: removed file gone');
  assert(fs.rm('nonexistent') === false, 'vfs: rm nonexistent returns false');

  // Read nonexistent
  assert(fs.read('nope') === null, 'vfs: read nonexistent returns null');

  // Clear
  fs.clear();
  assert(fs.ls().length === 0, 'vfs: clear empties all');

  console.log(`  VirtualFS: ${passed} passed`);
}

// ════════════════════════════════════════════════════════════════
// ShellSim Tests
// ════════════════════════════════════════════════════════════════
const shellPassed = passed;
console.log('============================================================');
console.log('Suite: ShellSim');
console.log('============================================================');

{
  // Basic prompt
  const fs = new VirtualFS({ persist: false });
  const sh = new ShellSim({ fs, rows: 20, cols: 40 });
  const screen = sh.getScreen();
  assert(screen.lines.length === 20, 'shell: 20 lines');
  assert(screen.cursor.row === 0, 'shell: cursor on first row (fresh shell)');
  const promptLine = screen.lines[0].trimEnd();
  assert(promptLine === '\u279c  vimfu', 'shell: prompt shown');
}

{
  // ls empty directory
  const fs = new VirtualFS({ persist: false });
  const sh = new ShellSim({ fs, rows: 20, cols: 40 });
  feedString(sh, 'ls');
  sh.feedKey('Enter');
  const lines = getOutputLines(sh);
  // Only the echoed command + prompt, no file listing
  assert(lines.some(l => l.includes('\u279c  vimfu ls')), 'shell: ls echoed');
}

{
  // ls with files
  const fs = new VirtualFS({ persist: false });
  fs.write('a.txt', 'aaa');
  fs.write('b.txt', 'bbb');
  const sh = new ShellSim({ fs, rows: 20, cols: 40 });
  feedString(sh, 'ls');
  sh.feedKey('Enter');
  const lines = getOutputLines(sh);
  assert(lines.some(l => l.includes('a.txt') && l.includes('b.txt')), 'shell: ls shows files');
}

{
  // cat
  const fs = new VirtualFS({ persist: false });
  fs.write('hello.txt', 'line1\nline2');
  const sh = new ShellSim({ fs, rows: 20, cols: 40 });
  feedString(sh, 'cat hello.txt');
  sh.feedKey('Enter');
  const lines = getOutputLines(sh);
  assert(lines.some(l => l.includes('line1')), 'shell: cat shows line1');
  assert(lines.some(l => l.includes('line2')), 'shell: cat shows line2');
}

{
  // cat nonexistent
  const fs = new VirtualFS({ persist: false });
  const sh = new ShellSim({ fs, rows: 20, cols: 40 });
  feedString(sh, 'cat nope.txt');
  sh.feedKey('Enter');
  const lines = getOutputLines(sh);
  assert(lines.some(l => l.includes('No such file')), 'shell: cat nonexistent error');
}

{
  // touch + rm
  const fs = new VirtualFS({ persist: false });
  const sh = new ShellSim({ fs, rows: 20, cols: 40 });
  feedString(sh, 'touch newfile');
  sh.feedKey('Enter');
  assert(fs.exists('newfile'), 'shell: touch creates file');

  feedString(sh, 'rm newfile');
  sh.feedKey('Enter');
  assert(!fs.exists('newfile'), 'shell: rm removes file');
}

{
  // echo
  const fs = new VirtualFS({ persist: false });
  const sh = new ShellSim({ fs, rows: 20, cols: 40 });
  feedString(sh, 'echo hello world');
  sh.feedKey('Enter');
  const lines = getOutputLines(sh);
  assert(lines.some(l => l.includes('hello world')), 'shell: echo prints text');
}

{
  // echo with redirect
  const fs = new VirtualFS({ persist: false });
  const sh = new ShellSim({ fs, rows: 20, cols: 40 });
  feedString(sh, 'echo some content > myfile');
  sh.feedKey('Enter');
  assert(fs.exists('myfile'), 'shell: echo > creates file');
  assert(fs.read('myfile') === 'some content', 'shell: echo > writes content');
}

{
  // unknown command
  const fs = new VirtualFS({ persist: false });
  const sh = new ShellSim({ fs, rows: 20, cols: 40 });
  feedString(sh, 'badcmd');
  sh.feedKey('Enter');
  const lines = getOutputLines(sh);
  assert(lines.some(l => l.includes('command not found')), 'shell: unknown command error');
}

{
  // clear
  const fs = new VirtualFS({ persist: false });
  const sh = new ShellSim({ fs, rows: 20, cols: 40 });
  feedString(sh, 'echo noise');
  sh.feedKey('Enter');
  feedString(sh, 'clear');
  sh.feedKey('Enter');
  const lines = getOutputLines(sh);
  // After clear, only the prompt should remain
  assert(lines.length <= 1, 'shell: clear clears output');
}

{
  // history up/down
  const fs = new VirtualFS({ persist: false });
  const sh = new ShellSim({ fs, rows: 20, cols: 40 });
  feedString(sh, 'echo first');
  sh.feedKey('Enter');
  feedString(sh, 'echo second');
  sh.feedKey('Enter');
  sh.feedKey('ArrowUp');
  assert(sh._inputLine === 'echo second', 'shell: history up 1');
  sh.feedKey('ArrowUp');
  assert(sh._inputLine === 'echo first', 'shell: history up 2');
  sh.feedKey('ArrowDown');
  assert(sh._inputLine === 'echo second', 'shell: history down');
}

{
  // Ctrl-C cancels input
  const fs = new VirtualFS({ persist: false });
  const sh = new ShellSim({ fs, rows: 20, cols: 40 });
  feedString(sh, 'partial');
  sh.feedKey('Ctrl-C');
  assert(sh._inputLine === '', 'shell: Ctrl-C clears input');
}

{
  // Ctrl-A / Ctrl-E
  const fs = new VirtualFS({ persist: false });
  const sh = new ShellSim({ fs, rows: 20, cols: 40 });
  feedString(sh, 'hello');
  sh.feedKey('Ctrl-A');
  assert(sh._cursorPos === 0, 'shell: Ctrl-A moves to start');
  sh.feedKey('Ctrl-E');
  assert(sh._cursorPos === 5, 'shell: Ctrl-E moves to end');
}

{
  // Tab completion
  const fs = new VirtualFS({ persist: false });
  fs.write('document.txt', 'doc');
  const sh = new ShellSim({ fs, rows: 20, cols: 40 });
  feedString(sh, 'cat doc');
  sh.feedKey('Tab');
  assert(sh._inputLine === 'cat document.txt', 'shell: tab completes filename');
}

{
  // vim callback
  const fs = new VirtualFS({ persist: false });
  let launchedFile = null;
  const sh = new ShellSim({
    fs, rows: 20, cols: 40,
    onLaunchVim: (f) => { launchedFile = f; },
  });
  feedString(sh, 'vim myfile.txt');
  sh.feedKey('Enter');
  assert(launchedFile === 'myfile.txt', 'shell: vim launches with filename');
}

{
  // vim with no filename
  const fs = new VirtualFS({ persist: false });
  let launchedFile = 'NOT_SET';
  const sh = new ShellSim({
    fs, rows: 20, cols: 40,
    onLaunchVim: (f) => { launchedFile = f; },
  });
  feedString(sh, 'vim');
  sh.feedKey('Enter');
  assert(launchedFile === null, 'shell: vim with no filename passes null');
}

{
  // renderFrame produces valid Frame dict
  const fs = new VirtualFS({ persist: false });
  const sh = new ShellSim({ fs, rows: 20, cols: 40 });
  const theme = { normalFg: 'e0e2ea', normalBg: '14161b', promptFg: '8cf8f7' };
  const frame = sh.renderFrame(theme);
  assert(frame.rows === 20, 'shell: frame rows');
  assert(frame.cols === 40, 'shell: frame cols');
  assert(frame.lines.length === 20, 'shell: frame lines count');
  assert(frame.cursor.visible === true, 'shell: frame cursor visible');
  assert(frame.lines[0].runs.length >= 1, 'shell: frame has runs on prompt row');
}

{
  // Ctrl-D on empty line exits
  const fs = new VirtualFS({ persist: false });
  let exited = false;
  const sh = new ShellSim({
    fs, rows: 20, cols: 40,
    onExit: () => { exited = true; },
  });
  sh.feedKey('Ctrl-D');
  assert(sh._exited === true, 'shell: Ctrl-D exits on empty line');
}

{
  // Ctrl-D on non-empty line deletes char forward
  const fs = new VirtualFS({ persist: false });
  const sh = new ShellSim({ fs, rows: 20, cols: 40 });
  feedString(sh, 'abc');
  // Move cursor to start: use Home or Ctrl-A
  sh.feedKey('Home');
  sh.feedKey('Ctrl-D');  // delete 'a'
  // The input should now be 'bc'
  assert(sh._inputLine === 'bc', 'shell: Ctrl-D deletes forward char');
}

{
  // Delete key deletes char forward
  const fs = new VirtualFS({ persist: false });
  const sh = new ShellSim({ fs, rows: 20, cols: 40 });
  feedString(sh, 'xyz');
  sh.feedKey('Home');
  sh.feedKey('Delete');  // delete 'x'
  assert(sh._inputLine === 'yz', 'shell: Delete key deletes forward char');
}

{
  // tmux appears in tab completion
  const fs = new VirtualFS({ persist: false });
  const sh = new ShellSim({ fs, rows: 20, cols: 40 });
  feedString(sh, 'tmu');
  sh.feedKey('Tab');
  assert(sh._inputLine === 'tmux ', 'shell: tmux tab completes');
}

console.log(`  ShellSim: ${passed - shellPassed} passed`);

// ════════════════════════════════════════════════════════════════
// SessionManager Tests
// ════════════════════════════════════════════════════════════════
const sessionPassed = passed;
console.log('============================================================');
console.log('Suite: SessionManager');
console.log('============================================================');

{
  // Starts in shell mode
  const s = new SessionManager({ rows: 20, cols: 40, persist: false });
  assert(s.getMode() === 'shell', 'session: starts in shell');
  assert(s.getModeLabel() === 'SHELL', 'session: label is SHELL');
}

{
  // vim command switches to vim mode
  const s = new SessionManager({ rows: 20, cols: 40, persist: false });
  feedString(s, 'vim test.txt');
  s.feedKey('Enter');
  assert(s.getMode() === 'vim', 'session: vim launches');
  assert(s.engine !== null, 'session: engine created');
}

{
  // :q returns to shell
  const s = new SessionManager({ rows: 20, cols: 40, persist: false });
  feedString(s, 'vim test.txt');
  s.feedKey('Enter');
  s.feedKey(':'); feedString(s, 'q'); s.feedKey('Enter');
  assert(s.getMode() === 'shell', 'session: :q returns to shell');
  assert(s.engine === null, 'session: engine cleaned up');
}

{
  // :w saves file to VFS
  const s = new SessionManager({ rows: 20, cols: 40, persist: false });
  feedString(s, 'vim test.txt');
  s.feedKey('Enter');
  s.feedKey('i'); feedString(s, 'Hello VFS'); s.feedKey('Escape');
  s.feedKey(':'); feedString(s, 'w'); s.feedKey('Enter');
  assert(s.fs.exists('test.txt'), 'session: :w creates file');
  assert(s.fs.read('test.txt') === 'Hello VFS', 'session: :w writes content');
  assert(s.getMode() === 'vim', 'session: :w stays in vim');
}

{
  // :wq saves and quits
  const s = new SessionManager({ rows: 20, cols: 40, persist: false });
  feedString(s, 'vim wq.txt');
  s.feedKey('Enter');
  s.feedKey('i'); feedString(s, 'save me'); s.feedKey('Escape');
  s.feedKey(':'); feedString(s, 'wq'); s.feedKey('Enter');
  assert(s.fs.exists('wq.txt'), 'session: :wq saves file');
  assert(s.fs.read('wq.txt') === 'save me', 'session: :wq content correct');
  assert(s.getMode() === 'shell', 'session: :wq returns to shell');
}

{
  // :q on dirty buffer shows error
  const s = new SessionManager({ rows: 20, cols: 40, persist: false });
  feedString(s, 'vim dirty.txt');
  s.feedKey('Enter');
  s.feedKey('i'); feedString(s, 'unsaved'); s.feedKey('Escape');
  s.feedKey(':'); feedString(s, 'q'); s.feedKey('Enter');
  assert(s.getMode() === 'vim', 'session: :q dirty stays in vim');
  assert(s.engine._messagePrompt && s.engine._messagePrompt.error.includes('E37'), 'session: :q dirty shows E37');
}

{
  // :q! on dirty buffer force-quits
  const s = new SessionManager({ rows: 20, cols: 40, persist: false });
  feedString(s, 'vim dirty2.txt');
  s.feedKey('Enter');
  s.feedKey('i'); feedString(s, 'discard'); s.feedKey('Escape');
  s.feedKey(':'); feedString(s, 'q!'); s.feedKey('Enter');
  assert(s.getMode() === 'shell', 'session: :q! force quits');
  assert(!s.fs.exists('dirty2.txt'), 'session: :q! no file saved');
}

{
  // ZZ saves and quits
  const s = new SessionManager({ rows: 20, cols: 40, persist: false });
  feedString(s, 'vim zz.txt');
  s.feedKey('Enter');
  s.feedKey('i'); feedString(s, 'ZZ data'); s.feedKey('Escape');
  s.feedKey('Z'); s.feedKey('Z');
  assert(s.getMode() === 'shell', 'session: ZZ returns to shell');
  assert(s.fs.read('zz.txt') === 'ZZ data', 'session: ZZ saves content');
}

{
  // ZQ force-quits without saving
  const s = new SessionManager({ rows: 20, cols: 40, persist: false });
  feedString(s, 'vim zq.txt');
  s.feedKey('Enter');
  s.feedKey('i'); feedString(s, 'discard'); s.feedKey('Escape');
  s.feedKey('Z'); s.feedKey('Q');
  assert(s.getMode() === 'shell', 'session: ZQ returns to shell');
  assert(!s.fs.exists('zq.txt'), 'session: ZQ no file saved');
}

{
  // :q after change+undo should succeed (undo restores clean state)
  const s = new SessionManager({ rows: 20, cols: 40, persist: false });
  s.fs.write('undo_test.txt', 'hello\nworld');
  feedString(s, 'vim undo_test.txt'); s.feedKey('Enter');
  s.feedKey('i'); s.feedKey('X'); s.feedKey('Escape'); // insert X
  s.feedKey('u'); // undo
  s.feedKey(':'); feedString(s, 'q'); s.feedKey('Enter');
  assert(s.getMode() === 'shell', 'session: :q after undo returns to shell');
}

{
  // :q after multi-char insert + undo should succeed
  const s = new SessionManager({ rows: 20, cols: 40, persist: false });
  s.fs.write('undo2.txt', 'hello\nworld');
  feedString(s, 'vim undo2.txt'); s.feedKey('Enter');
  s.feedKey('i'); feedString(s, 'ABC'); s.feedKey('Escape'); // insert ABC
  s.feedKey('u'); // undo all of insert
  s.feedKey(':'); feedString(s, 'q'); s.feedKey('Enter');
  assert(s.getMode() === 'shell', 'session: :q after multi-insert undo returns to shell');
}

{
  // :q after manual revert should FAIL (E37) — content same but undo position differs
  const s = new SessionManager({ rows: 20, cols: 40, persist: false });
  s.fs.write('manual.txt', 'hello\nworld');
  feedString(s, 'vim manual.txt'); s.feedKey('Enter');
  s.feedKey('i'); s.feedKey('X'); s.feedKey('Escape'); // insert X before hello
  s.feedKey('x'); // delete X manually — content back to original but 2 changes made
  s.feedKey(':'); feedString(s, 'q'); s.feedKey('Enter');
  assert(s.getMode() === 'vim', 'session: :q manual revert stays in vim');
  assert(s.engine._messagePrompt && s.engine._messagePrompt.error.includes('E37'),
    'session: :q manual revert shows E37');
}

{
  // :q! after manual revert should force-quit
  const s = new SessionManager({ rows: 20, cols: 40, persist: false });
  s.fs.write('manual2.txt', 'hello\nworld');
  feedString(s, 'vim manual2.txt'); s.feedKey('Enter');
  s.feedKey('i'); s.feedKey('X'); s.feedKey('Escape');
  s.feedKey('x');
  s.feedKey(':'); feedString(s, 'q!'); s.feedKey('Enter');
  assert(s.getMode() === 'shell', 'session: :q! manual revert force quits');
}

{
  // :q after change+undo+redo should FAIL (redo reintroduces the change)
  const s = new SessionManager({ rows: 20, cols: 40, persist: false });
  s.fs.write('redo.txt', 'hello\nworld');
  feedString(s, 'vim redo.txt'); s.feedKey('Enter');
  s.feedKey('i'); s.feedKey('X'); s.feedKey('Escape');
  s.feedKey('u');  // undo
  s.feedKey('Ctrl-R');  // redo — back to modified state
  s.feedKey(':'); feedString(s, 'q'); s.feedKey('Enter');
  assert(s.getMode() === 'vim', 'session: :q after redo stays in vim');
  assert(s.engine._messagePrompt && s.engine._messagePrompt.error.includes('E37'),
    'session: :q after redo shows E37');
}

{
  // :w then :q should succeed (save resets dirty flag)
  const s = new SessionManager({ rows: 20, cols: 40, persist: false });
  s.fs.write('save.txt', 'hello\nworld');
  feedString(s, 'vim save.txt'); s.feedKey('Enter');
  s.feedKey('i'); s.feedKey('X'); s.feedKey('Escape');
  s.feedKey(':'); feedString(s, 'w'); s.feedKey('Enter'); // save
  s.feedKey(':'); feedString(s, 'q'); s.feedKey('Enter'); // quit
  assert(s.getMode() === 'shell', 'session: :q after :w returns to shell');
}

{
  // :e loads a different file
  const s = new SessionManager({ rows: 20, cols: 40, persist: false });
  s.fs.write('existing.txt', 'I exist');
  feedString(s, 'vim dummy');
  s.feedKey('Enter');
  s.feedKey(':'); feedString(s, 'e existing.txt'); s.feedKey('Enter');
  assert(s.engine.buffer.lines[0] === 'I exist', 'session: :e loads file');
}

{
  // :!ls shows files
  const s = new SessionManager({ rows: 20, cols: 40, persist: false });
  s.fs.write('afile.txt', 'data');
  feedString(s, 'vim check');
  s.feedKey('Enter');
  s.feedKey(':'); feedString(s, '!ls'); s.feedKey('Enter');
  assert(s.getMode() === 'shell_msg', 'session: :! enters shell_msg mode');
  assert(s._shellMsgLines.some(l => l.includes('afile.txt')), 'session: :!ls shows files');
  // Dismiss
  s.feedKey('Enter');
  assert(s.getMode() === 'vim', 'session: Enter dismisses shell_msg');
}

{
  // Round-trip: shell → vim (write) → shell → vim (read back)
  const s = new SessionManager({ rows: 20, cols: 40, persist: false });
  // Create file
  feedString(s, 'vim roundtrip.txt');
  s.feedKey('Enter');
  s.feedKey('i'); feedString(s, 'roundtrip data'); s.feedKey('Escape');
  s.feedKey(':'); feedString(s, 'wq'); s.feedKey('Enter');
  assert(s.getMode() === 'shell', 'session: roundtrip back to shell');

  // Reopen
  feedString(s, 'vim roundtrip.txt');
  s.feedKey('Enter');
  assert(s.getMode() === 'vim', 'session: roundtrip back to vim');
  assert(s.engine.buffer.lines[0] === 'roundtrip data', 'session: roundtrip data persisted');
  s.feedKey(':'); feedString(s, 'q'); s.feedKey('Enter');
}

{
  // renderFrame returns valid frame in all modes
  const s = new SessionManager({ rows: 20, cols: 40, persist: false });

  // Shell mode
  const shellFrame = s.renderFrame();
  assert(shellFrame.rows === 20, 'session: shell frame rows');
  assert(shellFrame.lines.length === 20, 'session: shell frame lines');

  // Vim mode
  feedString(s, 'vim test');
  s.feedKey('Enter');
  const vimFrame = s.renderFrame();
  assert(vimFrame.rows === 20, 'session: vim frame rows');
  assert(vimFrame.lines.length === 20, 'session: vim frame lines');
}

{
  // :w with filename (save-as)
  const s = new SessionManager({ rows: 20, cols: 40, persist: false });
  feedString(s, 'vim');
  s.feedKey('Enter');
  s.feedKey('i'); feedString(s, 'saveas content'); s.feedKey('Escape');
  s.feedKey(':'); feedString(s, 'w newname.txt'); s.feedKey('Enter');
  assert(s.fs.exists('newname.txt'), 'session: :w filename saves-as');
  assert(s.fs.read('newname.txt') === 'saveas content', 'session: :w filename content');
}

{
  // Multiple vim sessions use same VFS
  const s = new SessionManager({ rows: 20, cols: 40, persist: false });

  // Session 1: create file
  feedString(s, 'vim shared.txt');
  s.feedKey('Enter');
  s.feedKey('i'); feedString(s, 'from session 1'); s.feedKey('Escape');
  s.feedKey(':'); feedString(s, 'wq'); s.feedKey('Enter');

  // Session 2: open same file
  feedString(s, 'vim shared.txt');
  s.feedKey('Enter');
  assert(s.engine.buffer.lines[0] === 'from session 1', 'session: VFS persists across vim sessions');
  s.feedKey(':'); feedString(s, 'q'); s.feedKey('Enter');
}

{
  // vim with existing file loads content
  const s = new SessionManager({ rows: 20, cols: 40, persist: false });
  s.fs.write('preexist.txt', 'preexisting content');
  feedString(s, 'vim preexist.txt');
  s.feedKey('Enter');
  assert(s.engine.buffer.lines[0] === 'preexisting content', 'session: vim loads existing file');
  s.feedKey(':'); feedString(s, 'q'); s.feedKey('Enter');
}

{
  // getModeLabel reflects vim modes
  const s = new SessionManager({ rows: 20, cols: 40, persist: false });
  feedString(s, 'vim test');
  s.feedKey('Enter');
  assert(s.getModeLabel() === 'NORMAL', 'session: label NORMAL');
  s.feedKey('i');
  assert(s.getModeLabel() === 'INSERT', 'session: label INSERT');
  s.feedKey('Escape');
  s.feedKey('v');
  assert(s.getModeLabel() === 'VISUAL', 'session: label VISUAL');
  s.feedKey('Escape');
  s.feedKey(':');
  assert(s.getModeLabel() === 'COMMAND', 'session: label COMMAND');
}

{
  // :wq with no filename shows E32
  const s = new SessionManager({ rows: 20, cols: 40, persist: false });
  feedString(s, 'vim');
  s.feedKey('Enter');
  s.feedKey('i'); feedString(s, 'data'); s.feedKey('Escape');
  s.feedKey(':'); feedString(s, 'wq'); s.feedKey('Enter');
  assert(s.getMode() === 'vim', 'session: :wq no filename stays in vim');
  assert(s.engine.commandLine && s.engine.commandLine.includes('E32'),
    'session: :wq no filename shows E32');
}

{
  // :x on clean buffer exits without writing
  const s = new SessionManager({ rows: 20, cols: 40, persist: false });
  s.fs.write('xtest.txt', 'original');
  feedString(s, 'vim xtest.txt');
  s.feedKey('Enter');
  s.feedKey(':'); feedString(s, 'x'); s.feedKey('Enter');
  assert(s.getMode() === 'shell', 'session: :x clean exits');
}

{
  // :x on dirty buffer writes and exits
  const s = new SessionManager({ rows: 20, cols: 40, persist: false });
  s.fs.write('xdirty.txt', 'original');
  feedString(s, 'vim xdirty.txt');
  s.feedKey('Enter');
  s.feedKey('i'); feedString(s, 'mod'); s.feedKey('Escape');
  s.feedKey(':'); feedString(s, 'x'); s.feedKey('Enter');
  assert(s.getMode() === 'shell', 'session: :x dirty exits');
  assert(s.fs.read('xdirty.txt') !== 'original', 'session: :x dirty writes');
}

{
  // :e with no args reloads current file
  const s = new SessionManager({ rows: 20, cols: 40, persist: false });
  s.fs.write('reload.txt', 'initial content');
  feedString(s, 'vim reload.txt');
  s.feedKey('Enter');
  s.feedKey('i'); feedString(s, 'junk'); s.feedKey('Escape');
  // Externally change file
  s.fs.write('reload.txt', 'reloaded content');
  s.feedKey(':'); feedString(s, 'e'); s.feedKey('Enter');
  assert(s.engine.buffer.lines[0] === 'reloaded content', 'session: :e no args reloads');
}

{
  // :e with no filename and no current file shows E32
  const s = new SessionManager({ rows: 20, cols: 40, persist: false });
  feedString(s, 'vim');
  s.feedKey('Enter');
  s.feedKey(':'); feedString(s, 'e'); s.feedKey('Enter');
  assert(s.getMode() === 'vim', 'session: :e no file stays in vim');
  assert(s.engine.commandLine && s.engine.commandLine.includes('E32'),
    'session: :e no file shows E32');
}

{
  // :sav writes to new filename
  const s = new SessionManager({ rows: 20, cols: 40, persist: false });
  feedString(s, 'vim orig.txt');
  s.feedKey('Enter');
  s.feedKey('i'); feedString(s, 'hello'); s.feedKey('Escape');
  s.feedKey(':'); feedString(s, 'sav copy.txt'); s.feedKey('Enter');
  assert(s.fs.exists('copy.txt'), 'session: :sav creates new file');
  assert(s.fs.read('copy.txt') === 'hello', 'session: :sav content correct');
}

{
  // :N line number jump
  const s = new SessionManager({ rows: 20, cols: 40, persist: false });
  s.fs.write('lines.txt', 'line1\nline2\nline3\nline4\nline5');
  feedString(s, 'vim lines.txt');
  s.feedKey('Enter');
  s.feedKey(':'); feedString(s, '3'); s.feedKey('Enter');
  assert(s.engine.cursor.row === 2, 'session: :3 jumps to line 3');
}

{
  // shell_msg only dismisses on Enter (not arbitrary keys)
  const s = new SessionManager({ rows: 20, cols: 40, persist: false });
  s.fs.write('f.txt', 'data');
  feedString(s, 'vim test');
  s.feedKey('Enter');
  s.feedKey(':'); feedString(s, '!ls'); s.feedKey('Enter');
  assert(s.getMode() === 'shell_msg', 'session: :! enters shell_msg');
  s.feedKey('a');  // arbitrary key should NOT dismiss
  assert(s.getMode() === 'shell_msg', 'session: arbitrary key stays in shell_msg');
  s.feedKey('Enter');  // Enter dismisses
  assert(s.getMode() === 'vim', 'session: Enter dismisses shell_msg');
}

console.log(`  SessionManager: ${passed - sessionPassed} passed`);

// ════════════════════════════════════════════════════════════════
// Summary
// ════════════════════════════════════════════════════════════════
console.log('============================================================');
console.log(`TOTAL: ${passed} passed, ${failed} failed`);
console.log('============================================================');

if (failed > 0) process.exit(1);
