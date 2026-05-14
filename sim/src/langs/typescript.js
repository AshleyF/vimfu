/**
 * VimFu Simulator – TypeScript Language Grammar
 *
 * Extends JavaScript with type-system keywords.
 */

import { registerGrammar } from '../highlight.js';

export const typescriptGrammar = {
  name: 'typescript',
  fileTypes: ['.ts', '.tsx', '.mts', '.cts'],
  rules: [
    { begin: '/\\*', end: '\\*/', scope: 'comment' },
    { begin: '`', end: '`', scope: 'string' },
    { match: '"(?:[^"\\\\]|\\\\.)*"', scope: 'string' },
    { match: "'(?:[^'\\\\]|\\\\.)*'", scope: 'string' },
    { match: '//.*$', scope: 'comment' },

    { match: '\\b0[xX][0-9a-fA-F][0-9a-fA-F_]*n?\\b', scope: 'number' },
    { match: '\\b0[bB][01][01_]*n?\\b', scope: 'number' },
    { match: '\\b0[oO][0-7][0-7_]*n?\\b', scope: 'number' },
    { match: '\\b\\d[\\d_]*(?:\\.\\d[\\d_]*)?(?:[eE][+-]?\\d+)?n?\\b', scope: 'number' },

    { match: '\\b(?:true|false|null|undefined|NaN|Infinity)\\b', scope: 'constant' },

    { match: '\\b(?:import|export|from|as|default)\\b', scope: 'keyword.import' },

    { match: '\\b(?:var|let|const|function|class|interface|type|enum|namespace|module|extends|implements|return|yield|await|async|new|delete|typeof|instanceof|keyof|infer|readonly|public|private|protected|abstract|static|override|void|in|of|this|super|declare|satisfies)\\b', scope: 'keyword' },
    { match: '\\b(?:if|else|switch|case|break|continue|default|do|while|for|try|catch|finally|throw|debugger)\\b', scope: 'keyword' },

    { match: '\\b(?:string|number|boolean|bigint|symbol|object|any|unknown|never|Record|Partial|Readonly|Pick|Omit|Required|Exclude|Extract|ReturnType|Parameters|Promise|Map|Set|Array)\\b', scope: 'builtin' },

    { match: '(?<=\\bfunction\\s)[a-zA-Z_$][\\w$]*', scope: 'function.def' },
    { match: '(?<=\\bclass\\s)[a-zA-Z_$][\\w$]*', scope: 'class.def' },
    { match: '(?<=\\binterface\\s)[a-zA-Z_$][\\w$]*', scope: 'class.def' },
    { match: '(?<=\\btype\\s)[a-zA-Z_$][\\w$]*', scope: 'class.def' },
  ],
};

registerGrammar(typescriptGrammar);
