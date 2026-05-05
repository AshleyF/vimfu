# Authoring Guide

How to actually write content for VimFu — voice, demo verification,
screenshots, GIFs, and the order in which a topic comes together.

This document complements [`Strategy.md`](./Strategy.md) (*why* this system
exists), [`Schema.md`](./Schema.md) (*what* a topic file looks like), and
[`Outline.md`](./Outline.md) (*which* topics exist). It tells you *how* to
produce a topic in practice.

---

## Generation flow

A new topic comes together in this order:

1. **Read [`Outline.md`](./Outline.md)** — find your topic. Note its `id`,
   `lessons`, `keys`, and the `internals` notes.

2. **Read the lesson JSONs** — `curriculum/shorts/NNNN_*.json` for every
   lesson the topic covers. Each one has:
   - `description` — a one-paragraph summary in the voice of the video.
   - `setup` — the file/buffer state the demo starts in.
   - `steps` — the keystrokes and `say` narration, step by step.
   - `youtube.videoId` — the uploaded video ID (or absent if not uploaded).

3. **Mine the supporting docs** — pick from these in roughly this order:
   - [`sim/VimBehavior.md`](../sim/VimBehavior.md) — the behavioral spec.
     Every `internals` block should be factually grounded here.
   - [`sim/Reference.md`](../sim/Reference.md) — exhaustive command tables.
   - [`book/Outline.md`](../book/Outline.md) (during migration) — well-tuned
     narrative paragraphs for most chapters.
   - [`book/content/*.json`](../book/content/) (during migration) — fully
     realized voice on the first few chapters.

4. **Author the JSON** — one file per topic at
   `content/parts/<NN-part>/<NN-topic>.json`. Follow [`Schema.md`](./Schema.md).
   Use `audience` to direct blocks at site, book, or both.

5. **Render and review** *(future, once `render_site.py` and
   `render_book.py` exist)*. Until then, validate by reading the JSON and
   comparing to the topic's lessons.

---

## Voice and tone

See `Strategy.md` § "Developer-Focused Tone" for the foundation. A few
practical reinforcements:

- **One topic, one idea.** A topic should fit on a single page of the book
  and a single screen of the site. If you're writing more than ~10KB of
  prose for one topic, it should probably be split.
- **Prose first, tables second.** Open with a paragraph that says the
  thing. Reference tables earn their place at the end, not in place of an
  explanation.
- **Show, then enumerate.** A `keys` block with a `label` is worth two
  paragraphs of "press i to enter Insert mode, then..."
- **`internals` blocks are not optional polish.** They are the book's
  reason for existing. If a topic has no `internals` block, ask whether
  there's truly no model worth explaining or whether you skipped it.
  *Some topics genuinely don't need one* (e.g. `editing.replace-char` is
  pretty much "press r, then a character"). Many do.

---

## Linking topics to videos

A topic declares its video lessons:

```json
"lessons": [21, 22, 23, 24]
```

Renderers read each lesson JSON and resolve `youtube.videoId`. They emit:

- **Site:** an `<iframe>` per `embed` block (or per lesson if the topic has
  no explicit `embed` blocks — TBD).
- **Book:** one **QR code** per topic — pointing at the topic page on the
  site, *not* one QR per video. Readers want fewer phone-pickups, not more.
  Use `{ "type": "qr", "topic": "<topic-id>" }` to let the renderer
  compute the URL.

If a lesson is in `lessons` but its `videoId` is absent (not uploaded
yet), renderers fall back gracefully: the site shows a "coming soon"
placeholder; the book still emits the QR (the topic page exists; it just
doesn't have all its videos yet).

**Principle:** **videos come first, then content**. The book and site
*reference* the videos — never the other way around. Author topics that
correspond to videos that exist; defer topics whose videos haven't been
recorded.

---

## Demo screenshots

Some topics benefit from static terminal screenshots (cursor on a specific
character, before/after states, annotated moments). Use a `screenshot`
block — see [`Schema.md`](./Schema.md) § `screenshot`.

The Frame JSON inside a `screenshot` block follows
[`brainstorming/frame_format.md`](../brainstorming/frame_format.md).

### Why verify

Screenshots are captured from a real Neovim session running in a terminal
emulator (ShellPilot + ConPTY + pyte). If the keystrokes in a demo are
wrong — wrong motion, wrong file content, wrong cursor position — the
screenshot will show the error. **Every demo screenshot must be verified
by replaying it against the terminal emulator.**

### How to capture

Use ShellPilot to drive a real `nvim` session and capture the pyte screen
buffer as Frame JSON:

1. Start a ConPTY session via ShellPilot.
2. Create a temp file with the demo content.
3. Open it in `nvim`.
4. Send key sequences with settle pauses between steps.
5. Read the pyte screen buffer → Frame JSON (rows, cols, cursor, lines
   with color runs).
6. Clean up the temp file and session.

The captured Frame JSON gets embedded directly into the topic JSON as a
`screenshot` block.

### Inspect before embedding

Before pasting the captured frame into a topic, verify:

- The cursor is where you expect it.
- The syntax highlighting looks correct.
- The status bar shows the expected filename and cursor position.
- Search highlights or visual selections appear if expected.
- The content hasn't been corrupted by timing issues.

### Timing tips

Terminal emulator capture is timing-sensitive. If a screenshot looks
wrong:

- Increase the settle time between key steps.
- Split complex sequences into smaller steps with pauses.
- Re-run the capture — pyte rendering is deterministic for the same
  input, so flaky captures usually indicate insufficient settle time.

---

## Animated GIF demos (HTML / site only)

Beyond static screenshots, the HTML/site renderer supports **animated
GIFs** of full lessons. Use a `demo` block:

```json
{ "type": "demo", "lesson": 21, "caption": "..." }
```

The renderer resolves the lesson number to a GIF using a two-stage
pipeline:

1. **Cache check** — look for `shellpilot/videos/<slug>/<slug>.frames.gif`.
2. **Generate on the fly** — if the GIF doesn't exist, run
   `capture_frames.py` (replays the lesson via ConPTY + pyte) and then
   `gif_maker.py` to produce the GIF.
3. **Copy to output** — the GIF is copied into the renderer's `images/`
   directory alongside the HTML so the output is portable.

The `shellpilot/videos/` directory is a **cache**. To force regeneration:

```bash
cd shellpilot
python gen_all_gifs.py              # all lessons
python gen_all_gifs.py 42           # just lesson 42
python gen_all_gifs.py 10-20        # range
python gen_all_gifs.py --force      # regenerate even if cached
```

### When to use which media block

| Block         | Best for                                              | Where it renders             |
|---------------|-------------------------------------------------------|------------------------------|
| `embed`       | The actual YouTube short, hosted on YouTube.          | Site only (iframe).          |
| `demo`        | An animated GIF of the lesson, for portable HTML.     | Site (HTML); print needs a fallback. |
| `screenshot`  | A single annotated terminal frame.                    | Site (SVG) and book (vector).|
| `qr`          | A QR code linking to the site's topic page.           | Book only.                   |

For most topics, one `embed` per video lesson plus one `qr` at the end is
enough. Reach for `demo` when you want HTML readers to see motion without
clicking a video; reach for `screenshot` when you want to point at a
specific moment ("after `dw`, the cursor lands on the next word").

---

## Pairing, not mirroring

The book and the site cover the same material — but they are *not*
transcripts of the videos and *not* transcripts of each other.

- A reader who only reads the book should learn everything.
- A viewer who only watches the videos should learn everything.
- A site-only reader should be able to find any reference they need.
- Someone who does all three gets the best of all worlds — the videos
  show *how*, the book explains *why*, the site is the *map*.

This means:

- A single topic may cover multiple videos (a "section" by the old
  vocabulary). Group lessons that read well as one narrative.
- Topics may include book/site material that has *no* corresponding video
  (Vi history, the modes FSM, the universal grammar, etc.). That's fine —
  the `lessons` array can be empty.
- When the videos themselves drift over time (a re-recording with a
  different demo), update the lesson JSON, not the topic. The topic
  references the lesson by number.
