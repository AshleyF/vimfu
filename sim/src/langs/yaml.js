/**
 * VimFu Simulator – YAML Language Grammar
 */

import { registerGrammar } from '../highlight.js';

export const yamlGrammar = {
  name: 'yaml',
  fileTypes: ['.yaml', '.yml'],
  rules: [
    { match: '#.*$', scope: 'comment' },

    // Document separators.
    { match: '^(?:---|\\.\\.\\.)\\s*$', scope: 'keyword.import' },

    // Quoted strings.
    { match: '"(?:[^"\\\\]|\\\\.)*"', scope: 'string' },
    { match: "'(?:[^']|'')*'", scope: 'string' },

    // Anchors and aliases.
    { match: '[&*][A-Za-z_][\\w-]*', scope: 'special' },

    // Tags.
    { match: '![A-Za-z_][\\w!]*', scope: 'special' },

    // Keys (identifier-ish before colon at non-trivial column).
    { match: '^[\\s-]*[A-Za-z_][\\w.-]*(?=:(?:\\s|$))', scope: 'builtin' },

    // Numbers.
    { match: '\\b-?\\d+(?:\\.\\d+)?(?:[eE][+-]?\\d+)?\\b', scope: 'number' },

    // Booleans / null.
    { match: '\\b(?:true|false|null|yes|no|on|off|True|False|Null|TRUE|FALSE|NULL|~)\\b', scope: 'constant' },

    // List markers.
    { match: '^\\s*-\\s', scope: 'keyword' },
  ],
};

registerGrammar(yamlGrammar);
