/**
 * VimFu Simulator – Markdown Language Grammar
 *
 * Regex-based syntax rules for Markdown, modelled on Neovim's built-in
 * treesitter @markup.* highlight groups.  Verified against nvim -u NONE
 * with `set termguicolors` + `syntax on`.
 *
 * Scope → Vim highlight group mapping:
 *   heading         → Title          (NvimDarkCyan 8cf8f7 / monokai green a6e22e)
 *   code            → String         (NvimDarkGreen b3f6c0 / monokai yellow e6db74)
 *   code.block      → String         (same as code)
 *   list.marker     → @markup.list   (NvimDarkCyan / monokai pink f92672)
 *   link            → @markup.link   (NvimDarkCyan / monokai blue 66d9ef)
 *   link.url        → Comment-like   (grey)
 *   blockquote      → @markup.quote  (grey)
 *   hr              → Special        (NvimDarkCyan / monokai pink f92672)
 */

import { registerGrammar } from '../highlight.js';

export const markdownGrammar = {
  name: 'markdown',
  fileTypes: ['.md', '.markdown', '.mkd'],
  rules: [
    // ── Fenced code blocks (``` ... ```) ───────────────────
    // Must come first so backtick fences aren't matched as inline code.
    { begin: '^```', end: '^```', scope: 'code.block' },

    // ── Inline code (`...`) ────────────────────────────────
    { match: '`[^`]+`', scope: 'code' },

    // ── Headings (# at start of line) ──────────────────────
    // nvim highlights the # markers AND the heading text in Title color.
    { match: '^#{1,6}\\s+.*$', scope: 'heading' },

    // ── Horizontal rules (---, ***, ___) ───────────────────
    { match: '^\\s*(?:---+|\\*\\*\\*+|___+)\\s*$', scope: 'hr' },

    // ── Unordered list markers (-, *, +) ───────────────────
    // Only the bullet character + space, not the content after it.
    { match: '^\\s*[-*+]\\s', scope: 'list.marker' },

    // ── Ordered list markers (1., 2., etc.) ────────────────
    { match: '^\\s*\\d+\\.\\s', scope: 'list.marker' },

    // ── Links [text](url) ──────────────────────────────────
    // Match the [text] part when followed by (url)
    { match: '\\[[^\\]]+\\](?=\\([^)]*\\))', scope: 'link' },
    // Match the (url) part after ]
    { match: '(?<=\\])\\([^)]+\\)', scope: 'link.url' },

    // ── Blockquote markers (>) ─────────────────────────────
    { match: '^\\s*>+.*$', scope: 'blockquote' },
  ],
};

// Auto-register
registerGrammar(markdownGrammar);
