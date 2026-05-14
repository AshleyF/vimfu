/**
 * VimFu Simulator – Shell (sh / bash / zsh) Language Grammar
 */

import { registerGrammar } from '../highlight.js';

export const shellGrammar = {
  name: 'shell',
  fileTypes: ['.sh', '.bash', '.zsh', '.ksh'],
  rules: [
    // Shebang first — distinctive line scope.
    { match: '^#!.*$', scope: 'special' },

    // Comments (must come after shebang).
    { match: '#.*$', scope: 'comment' },

    // Strings: double-quoted may span lines.
    { begin: '"', end: '"', scope: 'string' },
    { match: "'[^']*'", scope: 'string' },

    // Variable expansions: $VAR, ${VAR}, $1.
    { match: '\\$\\{[^}]*\\}', scope: 'constant' },
    { match: '\\$[A-Za-z_][\\w]*', scope: 'constant' },
    { match: '\\$[0-9*@#?$!_-]', scope: 'constant' },

    // Numbers.
    { match: '\\b\\d+\\b', scope: 'number' },

    // Keywords / control flow.
    { match: '\\b(?:if|then|else|elif|fi|case|esac|for|while|until|do|done|in|function|select|time)\\b', scope: 'keyword' },
    { match: '\\b(?:break|continue|return|exit|trap|set|unset|export|local|readonly|declare|typeset|shift|eval|exec|source)\\b', scope: 'keyword' },

    // Common built-in commands.
    { match: '\\b(?:echo|printf|cd|pwd|ls|cp|mv|rm|mkdir|rmdir|touch|cat|grep|sed|awk|find|xargs|sort|uniq|head|tail|wc|cut|tr|tee|read|test|true|false|env|alias|unalias|history|jobs|fg|bg|kill|wait|sleep)\\b', scope: 'builtin' },
  ],
};

registerGrammar(shellGrammar);
