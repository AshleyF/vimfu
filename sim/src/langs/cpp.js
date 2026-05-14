/**
 * VimFu Simulator – C++ Language Grammar
 */

import { registerGrammar } from '../highlight.js';

export const cppGrammar = {
  name: 'cpp',
  fileTypes: ['.cpp', '.cc', '.cxx', '.hpp', '.hh', '.hxx', '.ipp'],
  rules: [
    { begin: '/\\*', end: '\\*/', scope: 'comment' },
    { begin: 'R"\\(', end: '\\)"', scope: 'string' },
    { match: '"(?:[^"\\\\]|\\\\.)*"', scope: 'string' },
    { match: "'(?:[^'\\\\]|\\\\.)*'", scope: 'string' },
    { match: '//.*$', scope: 'comment' },

    { match: '^\\s*#\\s*(?:include|define|undef|if|ifdef|ifndef|else|elif|endif|pragma|error|warning|line).*$', scope: 'keyword.import' },

    { match: '\\b0[xX][0-9a-fA-F]+[uUlL]*\\b', scope: 'number' },
    { match: '\\b\\d+(?:\\.\\d+)?(?:[eE][+-]?\\d+)?[fFlLuU]*\\b', scope: 'number' },

    { match: '\\b(?:nullptr|true|false|NULL)\\b', scope: 'constant' },

    { match: '\\b(?:alignas|alignof|and|and_eq|asm|auto|bitand|bitor|break|case|catch|class|compl|concept|const|consteval|constexpr|constinit|const_cast|continue|co_await|co_return|co_yield|decltype|default|delete|do|dynamic_cast|else|enum|explicit|export|extern|for|friend|goto|if|inline|mutable|namespace|new|noexcept|not|not_eq|operator|or|or_eq|private|protected|public|register|reinterpret_cast|requires|return|sizeof|static|static_assert|static_cast|struct|switch|template|this|thread_local|throw|try|typedef|typeid|typename|union|using|virtual|volatile|while|xor|xor_eq)\\b', scope: 'keyword' },

    { match: '\\b(?:bool|char|char8_t|char16_t|char32_t|short|int|long|float|double|signed|unsigned|void|wchar_t|size_t|ptrdiff_t|int8_t|int16_t|int32_t|int64_t|uint8_t|uint16_t|uint32_t|uint64_t|string|wstring|vector|map|unordered_map|set|unordered_set|list|deque|array|pair|tuple|shared_ptr|unique_ptr|weak_ptr|optional|variant)\\b', scope: 'builtin' },

    { match: '\\b(?:std|cout|cerr|cin|endl|std::cout|std::cerr|std::cin|std::endl)\\b', scope: 'builtin' },
  ],
};

registerGrammar(cppGrammar);
