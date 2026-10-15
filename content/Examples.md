# Worked Examples — Schema and Pipeline

Worked examples are the "show, don't tell" half of VimFu content. A topic
explains a concept; an **example** drops the reader into a real terminal
and walks through the keystrokes one frame at a time.

Each example produces a sequence of **terminal screenshots** rendered as
**SVG**, in two themes:

| Theme   | Used by                | File suffix    |
|-------- |----------------------- |--------------- |
| `color` | website (HTML), markdown | `frame_NN.color.svg` |
| `bw`    | book (InDesign, print)  | `frame_NN.bw.svg`    |

Both SVGs are **self-contained** — embedded `<style>`, no external CSS
needed. Drop the file into anything that renders SVG and it just works.

---

## Layout

```
content/
  example_defs/
    <example-id>.json           ← AUTHOR HERE (vimfu-example-def)
  examples/
    <example-id>.json           ← generated (vimfu-content-example)
  example_lessons/
    <example_id>.json           ← generated shellpilot lessons
  output/
    screenshots/                ← gitignored, generated
      <example-id>/
        meta.json               ← title, captions, narration per frame
        frame_01.color.svg
        frame_01.bw.svg
        frame_02.color.svg
        ...
```

Author defs under `example_defs/`, then run
`python content/build_examples.py` to regenerate `examples/` and
`example_lessons/`. Screenshots regenerate with
`python content/render_screenshots.py`.

---

## Example schema (`vimfu-content-example`)

There are two flavors. Both produce the same output.

### Flavor A — Inline frames (hand-authored)

Frames are written directly using the [Frame Format](../brainstorming/frame_format.md).

```json
{
  "format": "vimfu-content-example",
  "version": 1,
  "id": "grammar.dw-then-dot",
  "title": "Delete a word, then repeat it",
  "summary": "The dot command repeats your last delete — for free.",
  "topic": "text-objects.grammar",
  "frames": [
    {
      "caption": "Cursor on the first word of a list.",
      "narration": "Three lines, three stats. Cursor parked on speed.",
      "frame": { "rows": 8, "cols": 40, "cursor": {...}, ... }
    },
    {
      "caption": "After dw — word deleted.",
      "narration": "dw deletes through the next word boundary.",
      "frame": { ... }
    }
  ]
}
```

### Flavor B — Captured from a curriculum lesson

Reference an existing `curriculum/shorts/*.json`. The renderer invokes
`shellpilot/capture_frames.py` to produce frame JSON, then picks the
indices listed.

```json
{
  "format": "vimfu-content-example",
  "version": 1,
  "id": "grammar.dw-then-dot",
  "title": "Delete a word, then repeat it",
  "summary": "...",
  "topic": "text-objects.grammar",
  "source": {
    "lesson": "curriculum/shorts/0085_the_vim_grammar.json",
    "select": [0, 5, 9, 14]
  },
  "frames": [
    { "caption": "Cursor on the first word of a list." },
    { "caption": "After dw — word deleted." },
    { "caption": "Repeat with dot." },
    { "caption": "Repeat again." }
  ]
}
```

`select` indexes into the captured frames array (after step deduping).
The number of `select` entries must match the number of `frames` entries
— they pair up, and `frames[i].caption/narration` apply to the
corresponding selected frame.

---

## Embedding examples in topics

Add an `example` block to any topic's `blocks` array:

```json
{ "type": "example", "ref": "grammar.dw-then-dot" }
```

The block expands to:

- **Markdown** — image + caption per frame, narration as a blockquote.
- **HTML** — inline `<svg>` (color theme) wrapped in a figure with caption.
- **InDesign** — inline graphic placeholder pointing at the BW SVG path,
  caption paragraph, narration paragraph.

You can also embed inline (no separate example file) by writing the full
example payload as the block — the schema accepts either `ref` or the
example fields directly.

---

## Theming details

The SVG renderer (in `content/lib/svg.py`, adapted from
`brainstorming/render_svg.py`) discovers the palette of every frame and
assigns semantic class names: `bg0 / bg1 / …` and `fg0 / fg1 / …`.
The color theme maps each class back to its original terminal hex; the
B&W theme collapses everything to two grays plus white, with one accent
gray for highlights / status bars.

That means a third-party theme (high-contrast, sepia, brand-colored) is
just another CSS file mapping the `bgN/fgN` classes to whatever you like.

---

## Authoring defs (`vimfu-example-def`)

Preferred path — one JSON file per example under `example_defs/`:

```json
{
  "format": "vimfu-example-def",
  "version": 1,
  "id": "editing.delete",
  "title": "x dw dd",
  "summary": "Three deletes, three scopes.",
  "topic": "editing.delete",
  "content": "the quick brown fox",
  "cursor": [0, 4],
  "frames": [
    { "caption": "Cursor on `q`." },
    {
      "actions": [{ "keys": "dw" }],
      "keys": "dw",
      "caption": "`dw` — through next word boundary.",
      "narration": "`d` is the operator; `x` is sugar for `dl`."
    }
  ]
}
```

Optional fields: `filename`, `lang`, `nvim_args`, `prep`, `pre_setup`,
`extra_setup`, `cols`, `rows`. Frame actions use `{ "keys": "..." }`,
`{ "type": "..." }`, `{ "ex": "..." }`, or `"escape"` / `"enter"`.

```bash
python content/build_examples.py            # all defs → examples/ + lessons
python content/build_examples.py grammar    # filter by id substring
python content/render_screenshots.py        # all examples → SVG
python content/render_screenshots.py grammar.dw-then-dot  # one example
```

Then re-run `render_html.py` / `render_markdown.py` / `render_indesign.py`
/ `build_pdf.py` to pick up the screenshots in topic output.
