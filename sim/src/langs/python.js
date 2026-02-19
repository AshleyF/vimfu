/**
 * VimFu Simulator – Python Language Grammar
 *
 * Regex-based syntax rules for Python, modelled on Neovim's built-in
 * syntax/python.vim highlight groups.  Rules are listed in priority
 * order – the first rule to claim a character position wins.
 *
 * Scope → Vim highlight group mapping (verified against nvim -u NONE):
 *   comment         → Comment       (gray, 9b9ea4)
 *   string          → String        (green, b3f6c0)
 *   constant        → Constant      (cyan, 8cf8f7) – True / False / None
 *   decorator       → Function      (cyan, 8cf8f7) – name only, not @
 *   function.def    → Function      (cyan, 8cf8f7) – name after def
 *   class.def       → Function      (cyan, 8cf8f7) – name after class
 *   builtin         → Function      (cyan, 8cf8f7) – print, len, str…
 *   special         → Special       (cyan, 8cf8f7) – dunder methods
 *   keyword         → Statement     (normal fg, e0e2ea – NOT highlighted)
 *   keyword.import  → Statement     (normal fg – NOT highlighted)
 *   number          → (normal fg – NOT highlighted by nvim default)
 *   operator        → (normal fg – NOT highlighted)
 */

import { registerGrammar } from '../highlight.js';

export const pythonGrammar = {
  name: 'python',
  fileTypes: ['.py'],
  rules: [
    // ── Multi-line strings (triple-quoted) ─────────────────
    // Must come first so """ / ''' are matched before single-char quotes.
    // nvim includes r/b/u prefix in string color but NOT f prefix.
    { begin: '(?:[rRbBuU]|[rRbB][bBrR])?"""', end: '"""', scope: 'string' },
    { begin: "(?:[rRbBuU]|[rRbB][bBrR])?'''", end: "'''", scope: 'string' },

    // ── Single-line strings ────────────────────────────────
    // Must come before comments so that # inside strings isn't a comment.
    // nvim treats the f prefix separately (normal fg), not as part of the string.
    { match: '(?:[rRbBuU]|[rRbB][bBrR])?"(?:[^"\\\\]|\\\\.)*"', scope: 'string' },
    { match: "(?:[rRbBuU]|[rRbB][bBrR])?'(?:[^'\\\\]|\\\\.)*'", scope: 'string' },

    // ── Comments ───────────────────────────────────────────
    { match: '#.*$', scope: 'comment' },

    // ── Decorators ─────────────────────────────────────────
    // nvim highlights only the name after @, not the @ itself
    { match: '(?<=@)\\w+', scope: 'decorator' },

    // ── Import keywords (PreProc group in nvim) ────────────
    { match: '\\b(?:import|from)\\b', scope: 'keyword.import' },

    // ── Keywords (Statement group in nvim) ─────────────────
    { match: '\\b(?:def|class|return|yield|raise|pass|break|continue|del|assert|global|nonlocal|lambda|with|as|async|await)\\b', scope: 'keyword' },

    // ── Conditionals ───────────────────────────────────────
    { match: '\\b(?:if|elif|else)\\b', scope: 'keyword' },

    // ── Repeat ─────────────────────────────────────────────
    { match: '\\b(?:for|while)\\b', scope: 'keyword' },

    // ── Exception ──────────────────────────────────────────
    { match: '\\b(?:try|except|finally)\\b', scope: 'keyword' },

    // ── Boolean / keyword operators ────────────────────────
    { match: '\\b(?:and|or|not|in|is)\\b', scope: 'keyword' },

    // ── Built-in constants ─────────────────────────────────
    { match: '\\b(?:True|False|None)\\b', scope: 'constant' },

    // ── Numeric literals ───────────────────────────────────
    // Hex, binary, octal
    { match: '\\b0[xX][0-9a-fA-F][0-9a-fA-F_]*\\b', scope: 'number' },
    { match: '\\b0[bB][01][01_]*\\b', scope: 'number' },
    { match: '\\b0[oO][0-7][0-7_]*\\b', scope: 'number' },
    // Complex (must come before float/int so 3+4j matches)
    { match: '\\b\\d[\\d_]*\\.?\\d*[jJ]\\b', scope: 'number' },
    // Float with dot or exponent
    { match: '\\b\\d[\\d_]*\\.\\d[\\d_]*(?:[eE][+-]?\\d[\\d_]*)?\\b', scope: 'number' },
    { match: '\\b\\d[\\d_]*[eE][+-]?\\d[\\d_]*\\b', scope: 'number' },
    // Plain integer
    { match: '\\b\\d[\\d_]*\\b', scope: 'number' },

    // ── Built-in functions / types ──────────────────────────
    // nvim highlights these everywhere (as function calls AND type annotations)
    { match: '\\b(?:print|len|range|enumerate|zip|map|filter|sorted|reversed|list|dict|set|tuple|int|str|float|bool|bytes|type|isinstance|issubclass|hasattr|getattr|setattr|delattr|super|open|input|abs|min|max|sum|any|all|iter|next|repr|id|hash|callable|format|round|chr|ord|hex|oct|bin|pow|vars|dir|help|eval|exec|compile|globals|locals|__import__|staticmethod|classmethod|property)\\b', scope: 'builtin' },

    // ── Dunder (magic) names ───────────────────────────────
    // nvim does NOT highlight self or cls
    { match: '\\b__[a-zA-Z_][a-zA-Z0-9_]*__\\b', scope: 'special' },

    // ── Function / class definition names ──────────────────
    // Matches the identifier right after def / class keywords
    { match: '(?<=\\bdef\\s)[a-zA-Z_]\\w*', scope: 'function.def' },
    { match: '(?<=\\bclass\\s)[a-zA-Z_]\\w*', scope: 'class.def' },
  ],
};

// Auto-register
registerGrammar(pythonGrammar);
