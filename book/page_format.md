# Book Page Format

The **vimfu-book-page** JSON format is an intermediate representation
for a chapter or tutorial page.  It carries structured content blocks
— prose, key-sequence displays, terminal screenshots, tips, tables —
that can be rendered to HTML, LaTeX, ICML, or Kindle.

## JSON structure

```json
{
  "format": "vimfu-book-page",
  "version": 1,
  "title": "Searching & Finding",
  "subtitle": "Jump anywhere with pattern search and character find",
  "lessons": [46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57],
  "content": [ ... ]
}
```

| Field      | Type     | Description                                  |
|----------- |--------- |----------------------------------------------|
| `format`   | string   | Always `"vimfu-book-page"`                   |
| `version`  | int      | Schema version (currently `1`)               |
| `title`    | string   | Page / chapter title                         |
| `subtitle` | string   | Optional subtitle                            |
| `lessons`  | int[]    | Curriculum lesson numbers covered            |
| `content`  | block[]  | Ordered list of content blocks               |

## Content blocks

Every block is an object with a `"type"` field.

### `heading`

```json
{ "type": "heading", "level": 2, "text": "Pattern Search" }
```

- `level` — 1, 2, or 3 (maps to `<h1>`–`<h3>`)
- `text` — may contain `{key:X}` inline markers

### `prose`

```json
{ "type": "prose", "text": "Type {key:/} and press {key:Enter}..." }
```

The `{key:X}` markers render as styled key badges (`<kbd>`).

### `keys`

A key-sequence callout shown as a row of badges.

```json
{
  "type": "keys",
  "sequence": ["/", "@mode", "Enter"],
  "label": "Search forward for 'mode'"
}
```

- Plain strings → key badges (`<kbd>`)
- `@`-prefixed strings → typed text (styled as user input)
- `label` — optional right-aligned description

### `screenshot`

An embedded terminal screenshot (Frame JSON).

```json
{
  "type": "screenshot",
  "lesson": 46,
  "static_frame": 0,
  "frame": { "rows": 11, "cols": 40, "..." : "..." },
  "caption": "After /mode — cursor on the first match"
}
```

The `frame` follows the Frame JSON spec (see `brainstorming/frame_format.md`).
Renderers convert it to SVG (HTML print), PGF/TikZ (LaTeX), etc.

- `lesson` — (optional) lesson number whose demo GIF should replace this
  screenshot in web/HTML output. When present, the HTML renderer shows the
  lesson's animated GIF instead of the static SVG. The `frame` data is
  preserved for print renderers that need a static diagram.
- `static_frame` — (optional, default `0`) which frame index from the
  generated video to use when a future print renderer needs a single still
  image instead of the full SVG. Acts as a hint for automated still-image
  extraction from the lesson's captured frames.

### `tip`

A callout / aside.

```json
{ "type": "tip", "text": "Search wraps around the file — you'll never miss a match." }
```

### `table`

A reference table.

```json
{
  "type": "table",
  "headers": ["Key", "Action"],
  "rows": [
    ["{key:/}pattern{key:Enter}", "Search forward"],
    ["{key:n}", "Next match (same direction)"]
  ]
}
```

Cell text supports `{key:X}` markers.

### `demo`

An animated GIF of a full lesson demo, sourced from the video pipeline.

```json
{
  "type": "demo",
  "lesson": 85,
  "caption": "The Vim grammar in action"
}
```

- `lesson` — lesson number (matches `curriculum/shorts/NNNN_*.json`)
- `caption` — optional caption below the animation

The renderer locates the lesson's GIF at
`shellpilot/videos/<slug>/<slug>.frames.gif`. If the GIF doesn't exist, it is
generated on the fly (capture frames → render GIF) and cached for future runs.
The GIF is copied into an `images/` subdirectory alongside the HTML output so
the HTML is portable.

### `divider`

A horizontal rule separating major sections.

```json
{ "type": "divider" }
```

## Pipeline

```
curriculum/shorts/*.json
        │
        ▼
  gen_<topic>.py        ──▶  output/<topic>.json   (page JSON)
        │
        ▼
  render_page.py        ──▶  output/<topic>.html   (self-contained HTML)
```

Future renderers: `render_page_latex.py`, `render_page_icml.py`, etc.
