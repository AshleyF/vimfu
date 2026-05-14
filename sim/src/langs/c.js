/**
 * VimFu Simulator – C Language Grammar
 */

import { registerGrammar } from '../highlight.js';

export const cGrammar = {
  name: 'c',
  fileTypes: ['.c', '.h'],
  rules: [
    { begin: '/\\*', end: '\\*/', scope: 'comment' },
    { match: '"(?:[^"\\\\]|\\\\.)*"', scope: 'string' },
    { match: "'(?:[^'\\\\]|\\\\.)*'", scope: 'string' },
    { match: '//.*$', scope: 'comment' },

    // Preprocessor directives — entire line.
    { match: '^\\s*#\\s*(?:include|define|undef|if|ifdef|ifndef|else|elif|endif|pragma|error|warning|line).*$', scope: 'keyword.import' },

    { match: '\\b0[xX][0-9a-fA-F]+[uUlL]*\\b', scope: 'number' },
    { match: '\\b\\d+(?:\\.\\d+)?(?:[eE][+-]?\\d+)?[fFlLuU]*\\b', scope: 'number' },

    { match: '\\b(?:NULL|true|false|TRUE|FALSE)\\b', scope: 'constant' },

    { match: '\\b(?:auto|break|case|const|continue|default|do|else|enum|extern|for|goto|if|inline|register|restrict|return|sizeof|static|struct|switch|typedef|union|volatile|while|_Alignas|_Alignof|_Atomic|_Bool|_Complex|_Generic|_Imaginary|_Noreturn|_Static_assert|_Thread_local)\\b', scope: 'keyword' },

    { match: '\\b(?:char|short|int|long|float|double|signed|unsigned|void|size_t|ssize_t|ptrdiff_t|intptr_t|uintptr_t|int8_t|int16_t|int32_t|int64_t|uint8_t|uint16_t|uint32_t|uint64_t|FILE)\\b', scope: 'builtin' },

    { match: '\\b(?:printf|fprintf|sprintf|snprintf|scanf|fscanf|sscanf|fopen|fclose|fread|fwrite|fgets|fputs|getchar|putchar|malloc|calloc|realloc|free|memcpy|memmove|memset|memcmp|strlen|strcpy|strncpy|strcat|strncat|strcmp|strncmp|strchr|strstr|strtok|exit|abort|atoi|atof|atol)\\b', scope: 'builtin' },
  ],
};

registerGrammar(cGrammar);
