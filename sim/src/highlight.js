/**
 * VimFu Simulator – Syntax Highlighting Engine
 *
 * A general-purpose, regex-based tokenizer inspired by TextMate grammars.
 * Takes a language grammar definition and produces per-character scope
 * assignments for colorizing source code in the renderer.
 *
 * Grammar format (compatible subset of TextMate):
 *
 *   {
 *     name: 'python',
 *     fileTypes: ['.py'],
 *     rules: [
 *       // Multi-line begin/end (must appear before single-line rules
 *       // that could match part of the delimiter):
 *       { begin: '"""', end: '"""', scope: 'string' },
 *
 *       // Single-line match:
 *       { match: '#.*$', scope: 'comment' },
 *       { match: '\\b(def|class)\\b', scope: 'keyword' },
 *     ]
 *   }
 *
 * Rules are processed in priority order (first rule in the array wins).
 * A position claimed by a higher-priority rule cannot be overridden.
 *
 * Multi-line state is tracked between calls to tokenizeLine() so that
 * constructs like triple-quoted strings span across lines correctly.
 */

// ── Grammar registry ──────────────────────────────────────────
const _grammars = new Map();

/**
 * Register a grammar so it can be resolved by filetype.
 * @param {object} grammar
 */
export function registerGrammar(grammar) {
  _grammars.set(grammar.name, grammar);
}

/**
 * Resolve a grammar from a filename extension.
 * @param {string|null} filename
 * @returns {object|null}
 */
export function grammarForFile(filename) {
  if (!filename) return null;
  const dot = filename.lastIndexOf('.');
  if (dot < 0) return null;
  const ext = filename.slice(dot);
  for (const g of _grammars.values()) {
    if (g.fileTypes && g.fileTypes.includes(ext)) return g;
  }
  return null;
}

// ── Highlighter ───────────────────────────────────────────────

export class SyntaxHighlighter {
  /**
   * @param {object} grammar – language grammar definition
   */
  constructor(grammar) {
    this.grammar = grammar;
    this.name = grammar.name;
  }

  /**
   * Tokenize a single line.
   *
   * Uses a left-to-right sweep: at each position, finds the earliest
   * match across all rules.  Ties (same start position) are broken by
   * rule priority (index in the rules array).
   *
   * @param {string} line
   * @param {object} state – { multiLine?: { endPattern: string, scope: string } }
   * @returns {{ tokens: Array<{start:number, end:number, scope:string}>, state: object }}
   */
  tokenizeLine(line, state = {}) {
    const tokens = [];
    let pos = 0;

    // ── Handle multi-line continuation ────────────────────────
    if (state.multiLine) {
      const endRe = new RegExp(state.multiLine.endPattern, 'g');
      const m = endRe.exec(line);
      if (m) {
        const endPos = m.index + m[0].length;
        tokens.push({ start: 0, end: endPos, scope: state.multiLine.scope });
        pos = endPos;
        state = {};
      } else {
        // Entire line inside the multi-line construct
        tokens.push({ start: 0, end: line.length, scope: state.multiLine.scope });
        return { tokens, state };
      }
    }

    // ── Left-to-right sweep ──────────────────────────────────
    const rules = this.grammar.rules;

    while (pos < line.length) {
      let bestStart = line.length; // sentinel: no match
      let bestEnd = -1;
      let bestScope = null;
      let bestIsMultiLine = false;
      let bestEndPattern = null;
      let bestPriority = Infinity;

      for (let ri = 0; ri < rules.length; ri++) {
        const rule = rules[ri];

        if (rule.begin != null) {
          // Begin/end rule
          const beginRe = new RegExp(rule.begin, 'g');
          beginRe.lastIndex = pos;
          const bm = beginRe.exec(line);
          if (!bm) continue;
          // Compare: earliest start wins, then priority
          if (bm.index < bestStart || (bm.index === bestStart && ri < bestPriority)) {
            // Look for end on same line
            const afterBegin = bm.index + bm[0].length;
            const endRe = new RegExp(rule.end, 'g');
            endRe.lastIndex = afterBegin;
            const em = endRe.exec(line);
            if (em) {
              bestStart = bm.index;
              bestEnd = em.index + em[0].length;
              bestScope = rule.scope;
              bestIsMultiLine = false;
              bestPriority = ri;
            } else {
              // Multi-line: extends to end of line
              bestStart = bm.index;
              bestEnd = line.length;
              bestScope = rule.scope;
              bestIsMultiLine = true;
              bestEndPattern = rule.end;
              bestPriority = ri;
            }
          }
        } else if (rule.match != null) {
          // Single-line rule
          const re = new RegExp(rule.match, 'g');
          re.lastIndex = pos;
          const mm = re.exec(line);
          if (!mm || mm[0].length === 0) continue;
          if (mm.index < bestStart || (mm.index === bestStart && ri < bestPriority)) {
            bestStart = mm.index;
            bestEnd = mm.index + mm[0].length;
            bestScope = rule.scope;
            bestIsMultiLine = false;
            bestEndPattern = null;
            bestPriority = ri;
          }
        }
      }

      if (bestScope === null) break; // no more matches

      tokens.push({ start: bestStart, end: bestEnd, scope: bestScope });
      pos = bestEnd;

      if (bestIsMultiLine) {
        return {
          tokens,
          state: {
            multiLine: {
              endPattern: bestEndPattern,
              scope: bestScope,
            },
          },
        };
      }
    }

    return { tokens, state: {} };
  }

  /**
   * Tokenize an array of lines, propagating state.
   * Returns an array of token arrays (one per line) and the final state.
   *
   * @param {string[]} lines
   * @returns {{ tokens: Array<Array>, finalState: object }}
   */
  tokenizeLines(lines) {
    const allTokens = [];
    let state = {};
    for (const line of lines) {
      const result = this.tokenizeLine(line, state);
      allTokens.push(result.tokens);
      state = result.state;
    }
    return { tokens: allTokens, finalState: state };
  }
}

/**
 * Convert a scope name to a theme color.
 *
 * Tries exact match first, then walks up the dotted hierarchy:
 *   'keyword.import' → 'keyword' → null
 *
 * @param {string} scope
 * @param {object} syntaxColors – theme's syntax color map
 * @returns {string|null} hex colour (without #) or null
 */
export function scopeToColor(scope, syntaxColors) {
  if (!syntaxColors || !scope) return null;
  // Exact match
  if (syntaxColors[scope] !== undefined) return syntaxColors[scope];
  // Walk up dotted hierarchy
  let s = scope;
  while (s.includes('.')) {
    s = s.slice(0, s.lastIndexOf('.'));
    if (syntaxColors[s] !== undefined) return syntaxColors[s];
  }
  return null;
}
