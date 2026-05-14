/**
 * VimFu Simulator – CSS Language Grammar
 */

import { registerGrammar } from '../highlight.js';

export const cssGrammar = {
  name: 'css',
  fileTypes: ['.css', '.scss', '.sass', '.less'],
  rules: [
    { begin: '/\\*', end: '\\*/', scope: 'comment' },
    { match: '"(?:[^"\\\\]|\\\\.)*"', scope: 'string' },
    { match: "'(?:[^'\\\\]|\\\\.)*'", scope: 'string' },

    // At-rules: @media, @import, @keyframes, ...
    { match: '@[a-zA-Z-]+', scope: 'keyword.import' },

    // Hex colours.
    { match: '#[0-9a-fA-F]{3,8}\\b', scope: 'constant' },

    // Numbers + units.
    { match: '\\b\\d+(?:\\.\\d+)?(?:px|em|rem|ex|ch|vh|vw|vmin|vmax|%|s|ms|deg|rad|turn|fr|pt|pc|in|cm|mm)?\\b', scope: 'number' },

    // !important.
    { match: '!important\\b', scope: 'keyword' },

    // Pseudo-classes and pseudo-elements.
    { match: '::?[a-zA-Z-]+(?:\\([^)]*\\))?', scope: 'special' },

    // Property names (identifiers before a colon, before the value).
    { match: '\\b[a-zA-Z-]+(?=\\s*:)', scope: 'builtin' },

    // Common CSS-wide values.
    { match: '\\b(?:inherit|initial|unset|revert|auto|none|normal|bold|italic|underline|transparent|currentColor|true|false)\\b', scope: 'constant' },
  ],
};

registerGrammar(cssGrammar);
