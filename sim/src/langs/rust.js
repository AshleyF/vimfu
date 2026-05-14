/**
 * VimFu Simulator – Rust Language Grammar
 */

import { registerGrammar } from '../highlight.js';

export const rustGrammar = {
  name: 'rust',
  fileTypes: ['.rs'],
  rules: [
    { begin: '/\\*', end: '\\*/', scope: 'comment' },
    // Raw strings (best-effort, single # delim).
    { begin: 'r#*"', end: '"#*', scope: 'string' },
    { match: '"(?:[^"\\\\]|\\\\.)*"', scope: 'string' },
    // Char / byte literal.
    { match: "b?'(?:[^'\\\\]|\\\\.)+'", scope: 'string' },
    { match: '//.*$', scope: 'comment' },

    { match: '\\b0[xX][0-9a-fA-F_]+(?:[ui](?:8|16|32|64|128|size))?\\b', scope: 'number' },
    { match: '\\b0[bB][01_]+(?:[ui](?:8|16|32|64|128|size))?\\b', scope: 'number' },
    { match: '\\b\\d[\\d_]*(?:\\.\\d[\\d_]*)?(?:[eE][+-]?\\d+)?(?:f32|f64|[ui](?:8|16|32|64|128|size))?\\b', scope: 'number' },

    { match: '\\b(?:true|false|None|Some|Ok|Err|Self)\\b', scope: 'constant' },

    { match: '\\b(?:use|mod|extern|crate|pub)\\b', scope: 'keyword.import' },

    { match: '\\b(?:as|async|await|break|const|continue|dyn|else|enum|fn|for|if|impl|in|let|loop|match|move|mut|ref|return|self|static|struct|super|trait|type|union|unsafe|where|while|yield|box|do|final|macro|override|priv|try|typeof|virtual)\\b', scope: 'keyword' },

    { match: '\\b(?:bool|char|str|String|i8|i16|i32|i64|i128|isize|u8|u16|u32|u64|u128|usize|f32|f64|Vec|Box|Rc|Arc|RefCell|Cell|Option|Result|HashMap|HashSet|BTreeMap|BTreeSet)\\b', scope: 'builtin' },

    { match: '\\b\\w+!(?=\\s*[(\\[{])', scope: 'special' },

    { match: '(?<=\\bfn\\s)[a-zA-Z_]\\w*', scope: 'function.def' },
    { match: '(?<=\\b(?:struct|enum|trait|union|type)\\s)[a-zA-Z_]\\w*', scope: 'class.def' },
  ],
};

registerGrammar(rustGrammar);
