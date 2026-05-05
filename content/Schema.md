# Content Topic Schema

The **vimfu-content-topic** format. Every file in `content/parts/<part>/` is
one topic JSON conforming to this schema. Renderers (`render_site.py`,
`render_book.py`) consume these files and emit the website and book.

This format is an evolution of `book/page_format.md` (the
**vimfu-book-page** format). Differences are called out in *Migration notes*
at the end.

---

## File location and naming

```
content/parts/<NN-part-slug>/<NN-topic-slug>.json
```

- `<NN-part-slug>` — two-digit ordering prefix + part slug, e.g.
  `01-foundations`, `07-operators-textobjects`. Order is the reading order in
  the book and the order in the site nav.
- `<NN-topic-slug>` — two-digit ordering prefix + topic slug, e.g.
  `01-modal-editing.json`. Order is the reading/section order within the part.

The numeric prefixes only control sort order; they are not stable IDs. The
**stable ID** of a topic is its `id` field (see below) and never changes
once a topic ships.

---

## Top-level structure

```json
{
  "format": "vimfu-content-topic",
  "version": 1,
  "id": "motion.word",
  "title": "Word Motions",
  "subtitle": "Jump by words instead of characters",
  "part": "basic-editing",
  "summary": "w / b / e / ge — and the WORD variants.",
  "keys": ["w", "W", "b", "B", "e", "E", "ge", "gE"],
  "lessons": [21, 22, 23, 24],
  "see_also": ["motion.line", "motion.find-on-line", "operators.delete"],
  "blocks": [ ... ]
}
```

| Field      | Type      | Required | Description                                              |
|------------|-----------|----------|----------------------------------------------------------|
| `format`   | string    | yes      | Always `"vimfu-content-topic"`.                          |
| `version`  | int       | yes      | Schema version (currently `1`).                          |
| `id`       | string    | yes      | Stable dot-separated identifier. **Never changes**.      |
| `title`    | string    | yes      | Short topic title — used in nav, headings, ToC.          |
| `subtitle` | string    | no       | One-line elaboration.                                    |
| `part`     | string    | yes      | Part slug (e.g. `"basic-editing"`). Must match folder.   |
| `summary`  | string    | no       | One-sentence summary for cards and ToC.                  |
| `keys`     | string[]  | no       | All keys covered. Used for the keyboard heatmap and search. |
| `lessons`  | int[]     | no       | Curriculum lesson numbers (matches `curriculum/shorts/NNNN_*.json`). |
| `see_also` | string[]  | no       | Related topic IDs.                                       |
| `blocks`   | block[]   | yes      | Ordered content blocks (see below).                      |

### `id` — stable identifier

The `id` is a dot-separated namespace. First segment is the part slug;
subsequent segments narrow it down. Examples:

- `foundations.modal-editing`
- `motion.word`
- `motion.find-on-line`
- `operators.delete`
- `registers.named`
- `registers.unnamed`
- `text-objects.aw-iw`

Once a topic has shipped (rendered to a public site or printed in the book),
its `id` is permanent. It appears in:

- The site URL: `vimfu.dev/<part>/<topic-slug>` (slug derived from the last
  ID segment, but redirects keep working forever).
- Book QR codes (which point at the site URL).
- The book's index and cross-references ("see § motion.word, p. 123").
- `see_also` arrays in other topics.

### `lessons` — linking to videos

Each integer is a curriculum lesson number. The renderer reads
`curriculum/shorts/NNNN_*.json` to get:

- The video title and description.
- The `youtube.videoId` (if uploaded) — for embedding (site) or
  computing the topic-page URL the QR code points at (book).

If a lesson is listed but its `videoId` is missing, the site shows a
"coming soon" placeholder and the book still produces the QR code (the
topic page exists; it just doesn't have all its videos yet).

---

## Audience tagging

Every block may carry an `audience` field:

| Value     | Meaning                                                          |
|-----------|------------------------------------------------------------------|
| `"both"`  | Default if omitted. Renders in both site and book.               |
| `"book"`  | Only the book renderer emits this block.                         |
| `"web"`   | Only the site renderer emits this block.                         |

Some block types have implicit audiences:

- `internals` defaults to `"book"` (deep dive — book-prominent; the site may
  show it collapsed-by-default behind a "Show internals" toggle).
- `embed` defaults to `"web"` (the book uses QR codes, not video embeds).
- `qr` defaults to `"book"` (the site doesn't print QR codes — it *is* the
  link target).
- `buy-prompt` defaults to `"web"` (the site upsells the book).

---

## Block types

### `heading`

```json
{ "type": "heading", "level": 2, "text": "Word Boundaries" }
```

- `level` — 1, 2, or 3.
- `text` — may contain `{key:X}` inline markers.

### `prose`

```json
{ "type": "prose", "text": "Press {key:w} to jump to the start of the next word." }
```

The default content block. `{key:X}` markers render as styled key badges.

### `keys`

A key-sequence callout shown as a row of badges.

```json
{
  "type": "keys",
  "sequence": ["d", "i", "w"],
  "label": "Delete inside word"
}
```

- Plain strings → key badges.
- `@`-prefixed strings → typed text (styled as user input).
- `label` — optional right-aligned description.

### `table`

```json
{
  "type": "table",
  "headers": ["Key", "Action"],
  "rows": [
    ["{key:w}", "Word forward"],
    ["{key:b}", "Word backward"]
  ]
}
```

### `tip`

A short callout / aside.

```json
{ "type": "tip", "text": "..." }
```

### `internals`  *(new — book-focused by default)*

The "Under the Hood" sidebar. Used for developer-internals callouts: the
state machine, the data structures, the *why* behind the keys. Default
audience is `"book"`. The site may render it as a collapsible details
element behind a "Show internals" link.

```json
{
  "type": "internals",
  "title": "What counts as a 'word'",
  "text": "Vim has two notions of word. The lowercase motions (w, b, e, ge) use the iskeyword option — by default, letters, digits, and underscore. The uppercase variants (W, B, E, gE) use whitespace as the only delimiter. ..."
}
```

- `title` — sidebar heading.
- `text` — body. May contain `{key:X}` markers and inline code spans.

### `screenshot`

A single embedded terminal frame (one Frame JSON). Useful for spot
illustrations. For multi-step *worked examples* with narration, use
`example` instead — it's the more common case.

```json
{
  "type": "screenshot",
  "lesson": 21,
  "static_frame": 0,
  "frame": { "rows": 11, "cols": 40, "...": "..." },
  "caption": "After w — cursor on 'level'"
}
```

- `lesson` — (optional) lesson whose demo GIF replaces this in HTML output.
- `static_frame` — (optional) which frame to use as a still in print.
- `frame` — Frame JSON (see `brainstorming/frame_format.md`).

### `example`  *(worked example with screenshots)*

Reference a `content/examples/<id>.json` file by id. The renderer
expands it to a sequence of step screenshots (color SVG on the website,
B&W SVG in the book) with caption and narration per frame.

```json
{ "type": "example", "ref": "grammar.dw-then-dot" }
```

The example file conforms to the `vimfu-content-example` schema —
see `content/Examples.md`. Screenshots are produced by
`python content/render_screenshots.py` and live (gitignored) at
`content/output/screenshots/<id>/frame_NN.{color,bw}.svg`.

### `embed`  *(new — site-focused by default)*

An embedded YouTube video. The site renders an iframe; the book skips it
(use `qr` for the book).

```json
{
  "type": "embed",
  "lesson": 21,
  "caption": "Word forward — w in action"
}
```

The renderer resolves the lesson's `youtube.videoId` to embed the right
video. If no `videoId` exists yet, render a placeholder.

### `demo`

An animated GIF of a full lesson demo, sourced from the video pipeline.
Used primarily for print where iframes can't render. Same as the existing
`demo` block in `vimfu-book-page`.

```json
{ "type": "demo", "lesson": 21, "caption": "..." }
```

### `qr`  *(book-default)*

A QR code. Default audience: `"book"`.

```json
{
  "type": "qr",
  "url": "https://vimfu.dev/basic-editing/word-motions",
  "caption": "Watch the demos at vimfu.dev/basic-editing/word-motions"
}
```

The renderer can also auto-generate the QR for a topic — just emit
`{ "type": "qr", "topic": "motion.word" }` and it resolves the URL.

### `buy-prompt`  *(site-default)*

A "Get the book" call-to-action.

```json
{ "type": "buy-prompt", "section": "Word Motions" }
```

The site renderer renders it as a styled card with a buy link. The book
suppresses it.

### `crossref`

An inline cross-reference.

```json
{ "type": "crossref", "topic": "operators.delete", "label": "the delete operator" }
```

Renders as:
- **Site:** anchor link `<a href="...">the delete operator</a>`.
- **Book:** "(see § *Delete*, p. 123)".

### `divider`

```json
{ "type": "divider" }
```

A horizontal rule separating major subsections.

---

## Inline markup

Within `text` fields:

- `{key:X}` — styled key badge (`<kbd>X</kbd>` on the site).
- `` `code` `` — inline code spans.
- `[link text](#topic-id)` — internal cross-reference (renderer resolves).
- `*emphasis*`, `**strong**` — standard Markdown, kept minimal.

No full Markdown — just these few markers. Keeps the format unambiguous and
easy to render.

---

## Migration notes (from `vimfu-book-page`)

The new format is mostly a superset of the old:

| `vimfu-book-page` (old)              | `vimfu-content-topic` (new)                 |
|--------------------------------------|---------------------------------------------|
| `format: "vimfu-book-page"`          | `format: "vimfu-content-topic"`             |
| no `id` field                        | `id` is required and stable                 |
| `lessons: int[]`                     | unchanged                                   |
| no `part` field                      | `part: string` — required                   |
| no `see_also` field                  | `see_also: string[]`                        |
| `content: block[]`                   | renamed to `blocks: block[]`                |
| `heading`, `prose`, `keys`, `table`, `tip`, `screenshot`, `demo`, `divider`, `qr` | unchanged |
| no `audience` field on blocks        | optional `audience: "both" \| "book" \| "web"` |
| no `internals` block                 | new — sidebar/callout for the book          |
| no `embed` block                     | new — YouTube iframe for the site           |
| no `buy-prompt` block                | new — site upsell for the book              |
| no `crossref` block                  | new — inline see-also                       |

A migration script can mostly walk the old files and:

1. Add `format: "vimfu-content-topic"`, `version: 1`.
2. Assign a stable `id` (often derivable from the filename).
3. Set `part`.
4. Rename `content` → `blocks`.
5. Promote `tip` blocks that contain implementation lore to `internals`.
6. Add `embed` blocks for any topic that has uploaded videos.
