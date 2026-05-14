/**
 * VimFu Simulator – JSON Language Grammar
 */

import { registerGrammar } from '../highlight.js';

export const jsonGrammar = {
  name: 'json',
  fileTypes: ['.json', '.jsonc'],
  rules: [
    // JSONC (with-comments) tolerance — harmless in strict JSON.
    { begin: '/\\*', end: '\\*/', scope: 'comment' },
    { match: '//.*$', scope: 'comment' },

    // Object keys (string immediately before a colon) — distinguish from values.
    { match: '"(?:[^"\\\\]|\\\\.)*"(?=\\s*:)', scope: 'builtin' },

    // String values.
    { match: '"(?:[^"\\\\]|\\\\.)*"', scope: 'string' },

    // Numbers.
    { match: '-?\\b\\d+(?:\\.\\d+)?(?:[eE][+-]?\\d+)?\\b', scope: 'number' },

    // Literals.
    { match: '\\b(?:true|false|null)\\b', scope: 'constant' },
  ],
};

registerGrammar(jsonGrammar);
