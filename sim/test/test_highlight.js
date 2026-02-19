/**
 * VimFu Simulator – Syntax Highlighting Unit Tests
 *
 * Tests the highlight engine + Python grammar tokenizer.
 * Run: node test/test_highlight.js
 */

import { SyntaxHighlighter, grammarForFile, scopeToColor, registerGrammar } from '../src/highlight.js';
import '../src/langs/python.js';  // registers the Python grammar
import { pythonGrammar } from '../src/langs/python.js';

let passed = 0;
let failed = 0;

function assert(cond, msg) {
  if (cond) { passed++; }
  else { failed++; console.log(`  FAIL  ${msg}`); }
}

/**
 * Helper: tokenize a line, return a simplified array of [scope, text] pairs.
 * Gaps (no scope) are included as [null, text].
 */
function tokenize(line, state = {}) {
  const hl = new SyntaxHighlighter(pythonGrammar);
  const result = hl.tokenizeLine(line, state);
  const parts = [];
  let pos = 0;
  for (const tok of result.tokens) {
    if (tok.start > pos) {
      parts.push([null, line.slice(pos, tok.start)]);
    }
    parts.push([tok.scope, line.slice(tok.start, tok.end)]);
    pos = tok.end;
  }
  if (pos < line.length) {
    parts.push([null, line.slice(pos)]);
  }
  return { parts, state: result.state };
}

/** Check that the given scope appears at the expected text fragment. */
function hasToken(parts, scope, text) {
  return parts.some(([s, t]) => s === scope && t === text);
}

/** Check that none of the tokens has the given scope for the given text. */
function noToken(parts, scope, text) {
  return !parts.some(([s, t]) => s === scope && t === text);
}

// ════════════════════════════════════════════════════════════════
// Grammar Registry
// ════════════════════════════════════════════════════════════════
console.log('============================================================');
console.log('Suite: Grammar Registry');
console.log('============================================================');

{
  const g = grammarForFile('hello.py');
  assert(g !== null && g.name === 'python', 'registry: .py → python');
  assert(grammarForFile('test.txt') === null, 'registry: .txt → null');
  assert(grammarForFile('noext') === null, 'registry: no ext → null');
  assert(grammarForFile(null) === null, 'registry: null → null');
}

// ════════════════════════════════════════════════════════════════
// scopeToColor
// ════════════════════════════════════════════════════════════════
console.log('============================================================');
console.log('Suite: scopeToColor');
console.log('============================================================');

{
  const colors = { comment: 'aaa', keyword: 'bbb', 'keyword.import': 'ccc' };
  assert(scopeToColor('comment', colors) === 'aaa', 'scope: exact match');
  assert(scopeToColor('keyword.import', colors) === 'ccc', 'scope: exact dotted match');
  assert(scopeToColor('keyword.other', colors) === 'bbb', 'scope: falls back to parent');
  assert(scopeToColor('unknown', colors) === null, 'scope: unknown → null');
  assert(scopeToColor('comment', null) === null, 'scope: null colors → null');
  assert(scopeToColor(null, colors) === null, 'scope: null scope → null');
}

// ════════════════════════════════════════════════════════════════
// Comments
// ════════════════════════════════════════════════════════════════
console.log('============================================================');
console.log('Suite: Comments');
console.log('============================================================');

{
  const { parts } = tokenize('# a comment');
  assert(hasToken(parts, 'comment', '# a comment'), 'comment: whole line');
}

{
  const { parts } = tokenize('x = 1  # inline');
  assert(hasToken(parts, 'comment', '# inline'), 'comment: inline');
  assert(noToken(parts, 'comment', 'x'), 'comment: x not commented');
}

{
  const { parts } = tokenize('url = "http://example.com"');
  assert(noToken(parts, 'comment', '//example.com"'), 'comment: not inside string');
}

// ════════════════════════════════════════════════════════════════
// Strings
// ════════════════════════════════════════════════════════════════
console.log('============================================================');
console.log('Suite: Strings');
console.log('============================================================');

{
  const { parts } = tokenize('x = "hello"');
  assert(hasToken(parts, 'string', '"hello"'), 'string: double quoted');
}

{
  const { parts } = tokenize("x = 'world'");
  assert(hasToken(parts, 'string', "'world'"), 'string: single quoted');
}

{
  const { parts } = tokenize('x = "he said \\"hi\\""');
  assert(hasToken(parts, 'string', '"he said \\"hi\\""'), 'string: escaped quotes');
}

{
  // nvim doesn't include the f prefix in the string — only the quoted part
  const { parts } = tokenize('x = f"pi is {PI:.2f}"');
  assert(hasToken(parts, 'string', '"pi is {PI:.2f}"'), 'string: f-string (without f prefix)');
}

{
  const { parts } = tokenize("x = r'no\\\\escape'");
  assert(hasToken(parts, 'string', "r'no\\\\escape'"), 'string: raw string');
}

{
  const { parts } = tokenize('x = b"bytes"');
  assert(hasToken(parts, 'string', 'b"bytes"'), 'string: byte string');
}

{
  const { parts } = tokenize('x = rb"raw bytes"');
  assert(hasToken(parts, 'string', 'rb"raw bytes"'), 'string: rb string');
}

// ── Triple-quoted strings (same line) ──
{
  const { parts } = tokenize('x = """hello"""');
  assert(hasToken(parts, 'string', '"""hello"""'), 'string: triple-quoted same line');
}

// ── Triple-quoted strings (multi-line) ──
{
  const hl = new SyntaxHighlighter(pythonGrammar);
  const r1 = hl.tokenizeLine('x = """', {});
  assert(r1.state.multiLine != null, 'string: triple-quoted opens multiline state');
  assert(r1.tokens.some(t => t.scope === 'string'), 'string: triple-quoted begin is string');

  const r2 = hl.tokenizeLine('middle line', r1.state);
  assert(r2.tokens.length === 1, 'string: multiline middle is one token');
  assert(r2.tokens[0].scope === 'string', 'string: multiline middle is string');
  assert(r2.tokens[0].start === 0 && r2.tokens[0].end === 11, 'string: multiline middle covers line');
  assert(r2.state.multiLine != null, 'string: multiline state continues');

  const r3 = hl.tokenizeLine('end"""', r2.state);
  assert(r3.tokens.some(t => t.scope === 'string'), 'string: multiline end is string');
  assert(!r3.state.multiLine, 'string: multiline state cleared after end');
}

// ── String inside comment should not be highlighted ──
{
  const { parts } = tokenize('# "not a string"');
  assert(hasToken(parts, 'comment', '# "not a string"'), 'string: inside comment is comment');
  assert(noToken(parts, 'string', '"not a string"'), 'string: not extracted from comment');
}

// ════════════════════════════════════════════════════════════════
// Keywords
// ════════════════════════════════════════════════════════════════
console.log('============================================================');
console.log('Suite: Keywords');
console.log('============================================================');

{
  const keywords = [
    'def', 'class', 'return', 'yield', 'raise', 'pass', 'break',
    'continue', 'del', 'assert', 'global', 'nonlocal', 'lambda',
    'with', 'as', 'async', 'await', 'if', 'elif', 'else', 'for',
    'while', 'try', 'except', 'finally', 'and', 'or', 'not', 'in', 'is',
  ];
  for (const kw of keywords) {
    const { parts } = tokenize(`${kw} something`);
    assert(
      hasToken(parts, 'keyword', kw),
      `keyword: '${kw}' highlighted`,
    );
  }
}

{
  // Keywords shouldn't match inside identifiers
  const { parts } = tokenize('define = 1');
  assert(noToken(parts, 'keyword', 'def'), 'keyword: no match inside "define"');
}

{
  // import / from are keyword.import (PreProc in nvim)
  const { parts } = tokenize('from os import path');
  assert(hasToken(parts, 'keyword.import', 'from'), 'keyword.import: from');
  assert(hasToken(parts, 'keyword.import', 'import'), 'keyword.import: import');
}

// ════════════════════════════════════════════════════════════════
// Constants (True, False, None)
// ════════════════════════════════════════════════════════════════
console.log('============================================================');
console.log('Suite: Constants');
console.log('============================================================');

{
  const { parts } = tokenize('x = True');
  assert(hasToken(parts, 'constant', 'True'), 'constant: True');
}

{
  const { parts } = tokenize('x = False');
  assert(hasToken(parts, 'constant', 'False'), 'constant: False');
}

{
  const { parts } = tokenize('x = None');
  assert(hasToken(parts, 'constant', 'None'), 'constant: None');
}

// ════════════════════════════════════════════════════════════════
// Numbers
// ════════════════════════════════════════════════════════════════
console.log('============================================================');
console.log('Suite: Numbers');
console.log('============================================================');

{
  const { parts } = tokenize('x = 42');
  assert(hasToken(parts, 'number', '42'), 'number: integer');
}

{
  const { parts } = tokenize('x = 3.14');
  assert(hasToken(parts, 'number', '3.14'), 'number: float');
}

{
  const { parts } = tokenize('x = 0xFF');
  assert(hasToken(parts, 'number', '0xFF'), 'number: hex');
}

{
  const { parts } = tokenize('x = 0b1010');
  assert(hasToken(parts, 'number', '0b1010'), 'number: binary');
}

{
  const { parts } = tokenize('x = 0o777');
  assert(hasToken(parts, 'number', '0o777'), 'number: octal');
}

{
  const { parts } = tokenize('x = 1_000_000');
  assert(hasToken(parts, 'number', '1_000_000'), 'number: underscores');
}

{
  const { parts } = tokenize('x = 1e10');
  assert(hasToken(parts, 'number', '1e10'), 'number: scientific');
}

// ════════════════════════════════════════════════════════════════
// Decorators
// ════════════════════════════════════════════════════════════════
console.log('============================================================');
console.log('Suite: Decorators');
console.log('============================================================');

{
  const { parts } = tokenize('@property');
  assert(hasToken(parts, 'decorator', 'property'), 'decorator: property (name only, not @)');
}

{
  const { parts } = tokenize('@staticmethod');
  assert(hasToken(parts, 'decorator', 'staticmethod'), 'decorator: staticmethod');
}

{
  const { parts } = tokenize('    @classmethod');
  assert(hasToken(parts, 'decorator', 'classmethod'), 'decorator: indented');
}

// ════════════════════════════════════════════════════════════════
// Built-in functions
// ════════════════════════════════════════════════════════════════
console.log('============================================================');
console.log('Suite: Built-ins');
console.log('============================================================');

{
  const { parts } = tokenize('print("hello")');
  assert(hasToken(parts, 'builtin', 'print'), 'builtin: print');
}

{
  const { parts } = tokenize('x = len(data)');
  assert(hasToken(parts, 'builtin', 'len'), 'builtin: len');
}

{
  const { parts } = tokenize('r = range(10)');
  assert(hasToken(parts, 'builtin', 'range'), 'builtin: range');
}

{
  // Built-in even without () (nvim highlights builtins everywhere)
  const { parts } = tokenize('my_range = range');
  assert(hasToken(parts, 'builtin', 'range'), 'builtin: range without paren still matches');
}

// ════════════════════════════════════════════════════════════════
// Special: dunder names (nvim does NOT highlight self/cls)
// ════════════════════════════════════════════════════════════════
console.log('============================================================');
console.log('Suite: Special');
console.log('============================================================');

{
  // self is NOT highlighted by nvim default
  const { parts } = tokenize('self.name = name');
  assert(noToken(parts, 'special', 'self'), 'special: self NOT highlighted');
}

{
  // cls is NOT highlighted by nvim default
  const { parts } = tokenize('cls.count += 1');
  assert(noToken(parts, 'special', 'cls'), 'special: cls NOT highlighted');
}

{
  const { parts } = tokenize('def __init__(self):');
  assert(hasToken(parts, 'special', '__init__'), 'special: __init__');
}

{
  const { parts } = tokenize('if __name__ == "__main__":');
  assert(hasToken(parts, 'special', '__name__'), 'special: __name__');
  // __main__ inside a string is claimed by the string rule, not special
  assert(noToken(parts, 'special', '__main__'), 'special: __main__ inside string is not special');
}

// ════════════════════════════════════════════════════════════════
// Function / class def names
// ════════════════════════════════════════════════════════════════
console.log('============================================================');
console.log('Suite: Def Names');
console.log('============================================================');

{
  const { parts } = tokenize('def hello():');
  assert(hasToken(parts, 'keyword', 'def'), 'def: keyword');
  assert(hasToken(parts, 'function.def', 'hello'), 'def: function name');
}

{
  const { parts } = tokenize('class MyClass:');
  assert(hasToken(parts, 'keyword', 'class'), 'def: class keyword');
  assert(hasToken(parts, 'class.def', 'MyClass'), 'def: class name');
}

{
  const { parts } = tokenize('async def fetch():');
  assert(hasToken(parts, 'keyword', 'async'), 'def: async keyword');
  assert(hasToken(parts, 'keyword', 'def'), 'def: def keyword (async)');
}

// ════════════════════════════════════════════════════════════════
// Priority / overlap
// ════════════════════════════════════════════════════════════════
console.log('============================================================');
console.log('Suite: Priority');
console.log('============================================================');

{
  // # inside a string should be string, not comment
  const { parts } = tokenize('x = "has # inside"');
  assert(hasToken(parts, 'string', '"has # inside"'), 'priority: # inside string is string');
  assert(noToken(parts, 'comment', '# inside"'), 'priority: no comment inside string');
}

{
  // Keyword inside a string should not be highlighted
  const { parts } = tokenize('x = "return value"');
  assert(hasToken(parts, 'string', '"return value"'), 'priority: keyword inside string is string');
  assert(noToken(parts, 'keyword', 'return'), 'priority: no keyword inside string');
}

{
  // Number inside a string should not be highlighted
  const { parts } = tokenize('x = "42"');
  assert(noToken(parts, 'number', '42'), 'priority: no number inside string');
}

{
  // Number inside a comment should not be highlighted
  const { parts } = tokenize('# value is 42');
  assert(hasToken(parts, 'comment', '# value is 42'), 'priority: whole comment');
  assert(noToken(parts, 'number', '42'), 'priority: no number inside comment');
}

// ════════════════════════════════════════════════════════════════
// Multi-line tokenization
// ════════════════════════════════════════════════════════════════
console.log('============================================================');
console.log('Suite: Multi-line');
console.log('============================================================');

{
  const hl = new SyntaxHighlighter(pythonGrammar);
  const lines = [
    'x = """',
    'line 1',
    'line 2',
    '"""',
    'y = 42',
  ];
  const result = hl.tokenizeLines(lines);
  // Line 0: x = """ (string starts at """)
  assert(result.tokens[0].some(t => t.scope === 'string'), 'multi: line 0 has string');
  // Line 1: entire line is string
  assert(result.tokens[1].length === 1 && result.tokens[1][0].scope === 'string', 'multi: line 1 all string');
  // Line 2: entire line is string
  assert(result.tokens[2].length === 1 && result.tokens[2][0].scope === 'string', 'multi: line 2 all string');
  // Line 3: """ closing
  assert(result.tokens[3].some(t => t.scope === 'string'), 'multi: line 3 has string');
  // Line 4: number
  assert(result.tokens[4].some(t => t.scope === 'number'), 'multi: line 4 has number');
  assert(!result.finalState.multiLine, 'multi: final state is clean');
}

// ════════════════════════════════════════════════════════════════
// Complex / real-world lines
// ════════════════════════════════════════════════════════════════
console.log('============================================================');
console.log('Suite: Complex Lines');
console.log('============================================================');

{
  const { parts } = tokenize('from typing import List, Optional');
  assert(hasToken(parts, 'keyword.import', 'from'), 'complex: from');
  assert(hasToken(parts, 'keyword.import', 'import'), 'complex: import');
}

{
  const { parts } = tokenize('def greet(name: str) -> str:');
  assert(hasToken(parts, 'keyword', 'def'), 'complex: def');
  assert(hasToken(parts, 'function.def', 'greet'), 'complex: function name');
}

{
  const { parts } = tokenize('    return f"Hello, {name}!"');
  assert(hasToken(parts, 'keyword', 'return'), 'complex: return');
  assert(hasToken(parts, 'string', '"Hello, {name}!"'), 'complex: f-string (without f prefix)');
}

{
  const { parts } = tokenize('result = [x**2 for x in range(10)]');
  assert(hasToken(parts, 'keyword', 'for'), 'complex: for in comprehension');
  assert(hasToken(parts, 'keyword', 'in'), 'complex: in');
  assert(hasToken(parts, 'builtin', 'range'), 'complex: range()');
  assert(hasToken(parts, 'number', '10'), 'complex: 10');
  assert(hasToken(parts, 'number', '2'), 'complex: 2 in x**2');
}

{
  const { parts } = tokenize('if __name__ == "__main__":');
  assert(hasToken(parts, 'keyword', 'if'), 'complex: if');
  assert(hasToken(parts, 'special', '__name__'), 'complex: __name__');
  assert(hasToken(parts, 'string', '"__main__"'), 'complex: "__main__" string');
}

{
  const { parts } = tokenize('except ZeroDivisionError as e:');
  assert(hasToken(parts, 'keyword', 'except'), 'complex: except');
  assert(hasToken(parts, 'keyword', 'as'), 'complex: as');
}

{
  const { parts } = tokenize('x = True if y else False');
  assert(hasToken(parts, 'constant', 'True'), 'complex: True');
  assert(hasToken(parts, 'keyword', 'if'), 'complex: ternary if');
  assert(hasToken(parts, 'keyword', 'else'), 'complex: ternary else');
  assert(hasToken(parts, 'constant', 'False'), 'complex: False');
}

// ════════════════════════════════════════════════════════════════
// Summary
// ════════════════════════════════════════════════════════════════
console.log('============================================================');
console.log(`TOTAL: ${passed} passed, ${failed} failed`);
console.log('============================================================');
if (failed > 0) process.exit(1);
