/**
 * VimFu Simulator – HTML Language Grammar
 *
 * Highlights tags, attributes, attribute values, and HTML comments. Embedded
 * <script> / <style> blocks fall through to the surrounding text colour.
 */

import { registerGrammar } from '../highlight.js';

export const htmlGrammar = {
  name: 'html',
  fileTypes: ['.html', '.htm', '.xhtml'],
  rules: [
    // ── HTML comment ─────────────────────────────────────
    { begin: '<!--', end: '-->', scope: 'comment' },

    // ── DOCTYPE ──────────────────────────────────────────
    { match: '<!DOCTYPE[^>]*>', scope: 'keyword.import' },

    // ── Attribute values (must come before generic tag rule) ──
    { match: '"[^"]*"', scope: 'string' },
    { match: "'[^']*'", scope: 'string' },

    // ── Entity references ────────────────────────────────
    { match: '&(?:#\\d+|#x[0-9a-fA-F]+|[a-zA-Z][a-zA-Z0-9]*);', scope: 'constant' },

    // ── Tag names (open + close) ─────────────────────────
    { match: '</?[a-zA-Z][\\w-]*', scope: 'keyword' },

    // ── Tag terminators / self-close ─────────────────────
    { match: '/?>', scope: 'keyword' },

    // ── Attribute names ──────────────────────────────────
    { match: '\\b[a-zA-Z_:][\\w:.-]*(?==)', scope: 'builtin' },
  ],
};

registerGrammar(htmlGrammar);
