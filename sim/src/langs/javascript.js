/**
 * VimFu Simulator – JavaScript Language Grammar
 *
 * Regex-based syntax rules for JavaScript, using the same scope vocabulary
 * as the Python grammar so it picks up existing theme colors automatically.
 */

import { registerGrammar } from '../highlight.js';

export const javascriptGrammar = {
  name: 'javascript',
  fileTypes: ['.js', '.mjs', '.cjs', '.jsx'],
  rules: [
    // ── Multi-line block comment ─────────────────────────
    { begin: '/\\*', end: '\\*/', scope: 'comment' },

    // ── Strings (single / double / template) ─────────────
    // Templates can span multiple lines.
    { begin: '`', end: '`', scope: 'string' },
    { match: '"(?:[^"\\\\]|\\\\.)*"', scope: 'string' },
    { match: "'(?:[^'\\\\]|\\\\.)*'", scope: 'string' },

    // ── Line comment ─────────────────────────────────────
    { match: '//.*$', scope: 'comment' },

    // ── Numbers ──────────────────────────────────────────
    { match: '\\b0[xX][0-9a-fA-F][0-9a-fA-F_]*n?\\b', scope: 'number' },
    { match: '\\b0[bB][01][01_]*n?\\b', scope: 'number' },
    { match: '\\b0[oO][0-7][0-7_]*n?\\b', scope: 'number' },
    { match: '\\b\\d[\\d_]*(?:\\.\\d[\\d_]*)?(?:[eE][+-]?\\d+)?n?\\b', scope: 'number' },

    // ── Constants ────────────────────────────────────────
    { match: '\\b(?:true|false|null|undefined|NaN|Infinity)\\b', scope: 'constant' },

    // ── Import / export keywords ─────────────────────────
    { match: '\\b(?:import|export|from|as|default)\\b', scope: 'keyword.import' },

    // ── Keywords ─────────────────────────────────────────
    { match: '\\b(?:var|let|const|function|class|extends|return|yield|await|async|new|delete|typeof|instanceof|void|in|of|this|super)\\b', scope: 'keyword' },
    { match: '\\b(?:if|else|switch|case|break|continue|default|do|while|for|try|catch|finally|throw|debugger)\\b', scope: 'keyword' },

    // ── Built-ins ────────────────────────────────────────
    { match: '\\b(?:console|window|document|globalThis|process|Buffer|Math|JSON|Object|Array|String|Number|Boolean|Symbol|BigInt|Date|RegExp|Error|Promise|Map|Set|WeakMap|WeakSet|Proxy|Reflect|parseInt|parseFloat|isNaN|isFinite|encodeURIComponent|decodeURIComponent|setTimeout|setInterval|clearTimeout|clearInterval)\\b', scope: 'builtin' },

    // ── Function / class definition names ────────────────
    { match: '(?<=\\bfunction\\s)[a-zA-Z_$][\\w$]*', scope: 'function.def' },
    { match: '(?<=\\bclass\\s)[a-zA-Z_$][\\w$]*', scope: 'class.def' },
  ],
};

registerGrammar(javascriptGrammar);
