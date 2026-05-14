/**
 * VimFu Simulator – Go Language Grammar
 */

import { registerGrammar } from '../highlight.js';

export const goGrammar = {
  name: 'go',
  fileTypes: ['.go'],
  rules: [
    { begin: '/\\*', end: '\\*/', scope: 'comment' },
    { begin: '`', end: '`', scope: 'string' },
    { match: '"(?:[^"\\\\]|\\\\.)*"', scope: 'string' },
    { match: "'(?:[^'\\\\]|\\\\.)*'", scope: 'string' },
    { match: '//.*$', scope: 'comment' },

    { match: '\\b0[xX][0-9a-fA-F]+\\b', scope: 'number' },
    { match: '\\b\\d+(?:\\.\\d+)?(?:[eE][+-]?\\d+)?i?\\b', scope: 'number' },

    { match: '\\b(?:true|false|nil|iota)\\b', scope: 'constant' },

    { match: '\\b(?:import|package)\\b', scope: 'keyword.import' },

    { match: '\\b(?:break|case|chan|const|continue|default|defer|else|fallthrough|for|func|go|goto|if|interface|map|range|return|select|struct|switch|type|var)\\b', scope: 'keyword' },

    { match: '\\b(?:bool|byte|complex64|complex128|error|float32|float64|int|int8|int16|int32|int64|rune|string|uint|uint8|uint16|uint32|uint64|uintptr|any)\\b', scope: 'builtin' },

    { match: '\\b(?:append|cap|close|complex|copy|delete|imag|len|make|new|panic|print|println|real|recover)\\b', scope: 'builtin' },

    { match: '(?<=\\bfunc\\s)[a-zA-Z_]\\w*', scope: 'function.def' },
    { match: '(?<=\\btype\\s)[a-zA-Z_]\\w*', scope: 'class.def' },
  ],
};

registerGrammar(goGrammar);
