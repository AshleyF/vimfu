# VimFu Content Strategy

The single source of truth for **VimFu** content: one set of structured content
files that produces **both** a print/EPUB book and a reference website. This
document is the standing brief — feed it to an LLM (or a human author) when
generating, refining, or reorganizing content.

---

## The Two Outputs

### Website — `vimfu.dev` (working title)

A **reference**. Quick to scan, broken into short pages, organized by topic.
Each topic page is a focused unit:

- Compact prose that explains the keys.
- Embedded YouTube videos (the shorts, hosted on YouTube; the site just uses
  iframes — no self-hosted video).
- Reference tables (key → action).
- Cross-links to related topics.
- A persistent "**Want the full story? Get the book →**" call-to-action that
  links to a deeper treatment of the same subject in the book.

The site is the *map*. It is intentionally lightweight: just enough prose to
remember a key and find related ones. People who want the *terrain* — the why,
the internals, the connections — go to the book.

### Book — _VimFu_ (working title: _VimFu: The Editing Language_)

A **comprehensive, developer-focused tutorial**. Read front-to-back or jump
around. Each section:

- Teaches the keys *and* the model behind them.
- Includes **"Under the Hood"** sidebars that explain how Vim actually works:
  the mode automaton, the operator+motion grammar, registers as a key→buffer
  map, the jumplist as a per-window ring, undo as a tree, `iskeyword` and what
  counts as a "word", `'` vs `` ` `` marks, the difference between buffers and
  windows, how `.` actually replays, etc.
- Has **QR codes** beside each topic that link to the matching topic page on
  the website — where the embedded video plays.
- Has reference tables at the end of each section for quick review.

The book is the *terrain*. It assumes a developer audience — people who are
comfortable with state machines, data structures, and "this is implemented as
X" framing. The premise: **once you know how Vim is built, the keybindings
stop being arbitrary and become inevitable**. A register isn't a clipboard;
it's a named slot in a key→buffer dictionary, which is why named registers
(`"ay`), the unnamed register (`""`), the system clipboard (`"+`), the
expression register (`"=`), and the small-delete register (`"-`) all work the
same way and the same operators interact with them. Once you see the table,
you see the language.

---

## Why a Single Source

Two outputs, one corpus. The book and the site cover the same subject — they
should not drift, and authors should not have to update two places when a
behavior changes or a video is added. So:

- **All content lives in `content/`** (this directory). Everything else
  derives from it.
- Each *topic* is one JSON file (the **vimfu-content-topic** format — see
  [`Schema.md`](./Schema.md)).
- Each block in a topic is tagged with an `audience`: `"both"` (default),
  `"book"`, or `"web"`.
- Cross-references between topics are by stable ID (`motion.word`,
  `registers.named`), not by URL or page number — so renderers can resolve
  them however they want (anchor link on the site, "see §7.4" in the book,
  QR code, etc.).

The same JSON corpus is consumed by **two renderers**:

```
              ┌──────────────────────────┐
              │   content/parts/**.json   │   ← single source of truth
              └────────────┬─────────────┘
                           │
            ┌──────────────┴───────────────┐
            ▼                              ▼
   render_site.py                  render_book.py
   (HTML, embedded video,          (HTML→LaTeX→PDF /
    nav, search, links to book)     EPUB, QR codes, sidebars)
```

The existing `book/render_page.py` and the existing book content in
`book/content/` are the **prototype** for this — the new `content/` layer
generalizes and replaces it. Migration is phase 4 below.

---

## The Hierarchy

Two levels:

- **Parts** — top-level groupings (~15–20 of them). On the site, parts are
  the main nav sections. In the book, a part roughly corresponds to a chapter
  or a small group of related chapters. *We deliberately don't call these
  "chapters" — they are part of one corpus that becomes a chapter only when
  rendered to the book.*
- **Topics** — atomic content units within a part (~5–15 per part). On the
  site, each topic is one page. In the book, a topic is one section.

The full part/topic taxonomy is in [`Outline.md`](./Outline.md). Topic IDs
look like `motion.word` or `registers.named` and are stable forever — they
appear in URLs, QR codes, cross-references, and book indexes.

---

## How Topics Map to Videos

Most (not all) topics correspond to one or more video lessons in
`curriculum/shorts/NNNN_*.json`. A topic file declares:

```json
"lessons": [21, 22, 23, 24]
```

Renderers look up the lesson JSON, read its `youtube.videoId` (set after
upload by `upload_youtube.py`), and produce the right output:

- **Site:** an embedded YouTube iframe per lesson.
- **Book:** one QR code linking to the topic page on the site (which has the
  videos), *not* one QR per video. Readers want fewer phone-pickups, not more.

When a video has not been uploaded yet, the lesson JSON has no `videoId`. The
renderers should:

- **Site:** show a placeholder card ("Video coming soon — lesson 0249").
- **Book:** still produce the QR code (the topic page exists on the site even
  if the video doesn't yet); optionally suppress the QR until at least one
  lesson in the topic has a video.

This is why we link topics to *lessons* and lessons to *videos*, instead of
linking topics to videos directly. The lesson layer is stable; the video
layer is fluid (re-recordings, schedule slips, etc.).

---

## Developer-Focused Tone (for the Book)

The book's distinctive voice. Apply these consistently:

1. **Explain the data structure first, the keystrokes second.** Don't say
   "press `"ay` to yank to register `a`". Say: "Vim has a dictionary of
   *registers* — a–z, plus a dozen named ones. Every yank, delete, and macro
   reads or writes one. `"a` selects register `a`; `y` writes; `p` reads.
   The whole register interface is built from this one primitive."

2. **Name the state.** Modes are states in a finite-state machine. The
   jumplist is a stack with a cursor. The change list is a per-buffer ring
   buffer of size N. The unnamed register is a fallthrough alias for "the
   last anonymous yank/delete." Make these explicit.

3. **Use "Under the Hood" sidebars** for the deep stuff. Keep the main flow
   readable; readers who want internals get them in a clearly-marked aside.
   These do not appear in the website (or appear collapsed by default).

4. **Don't drown readers in code.** This is not a Vimscript or Lua book.
   "Implementation" here means *behavioral model*, not *source code*. We're
   reverse-engineering the user model, not the C source.

5. **Lean on the grammar.** Operator + motion is the central insight. Once
   the grammar clicks, every new key is just "another verb" or "another
   noun." Frame everything in those terms.

6. **Acknowledge what's weird.** Vim has cruft (`Y` vs `yy`, `D` vs `d$`,
   `cc` vs `S`, `s` vs `cl`, the `"` quoting in registers). Don't apologize
   for it — explain *why it exists* (vi compatibility, terminal-era
   constraints, design accidents that became muscle memory). The book is a
   chance to be honest about Vim's history without losing reverence.

---

## Cross-Promotion

The book and the site sell each other:

- **Site → Book.** Every topic page ends with: "Want the full story behind
  these keys? Read [§ Topic Title] in *VimFu*." With a buy link.
- **Book → Site.** Every section has a QR code: "Watch the demos at
  vimfu.dev/<part>/<topic>." Plus a single front-matter QR for the YouTube
  playlist as a whole.

The site is intentionally less complete than the book — readers should feel
they got value, but feel curious about the bits that aren't there. This is a
content strategy choice, not a paywall: nothing on the site is hidden, but
the site simply doesn't *try* to teach the model. The book does that.

---

## Existing Material — What to Reuse

When generating new content, the LLM should mine these existing sources:

| Source                              | What to use it for                                         |
|-------------------------------------|------------------------------------------------------------|
| `curriculum/Curriculum.md`          | Master list of 500+ lessons, organized into 18 parts.      |
| `curriculum/shorts/NNNN_*.json`     | Per-lesson title, description, key sequence, narration.    |
| `book/Outline.md`                   | Existing 27-chapter book outline — supersede with new hierarchy in `content/Outline.md` but cannibalize prose. |
| `book/content/*.json`               | Existing hand-authored book pages — port to new format.    |
| `book/Instructions.md`              | Tone, style, visual design (still applicable; this doc extends it). |
| `book/page_format.md`               | Original block format — `Schema.md` is the evolved version.|
| `sim/Reference.md`                  | Exhaustive command reference — useful for tables.          |
| `sim/VimBehavior.md`                | Implementation notes — gold for "Under the Hood" sidebars. |
| `Learnings.md`, `Notes.md`, `Keys.md`| Background on the project; mostly meta, not user-facing. |

---

## Phases

1. **Strategy + scaffolding** *(this commit)*
   - `content/Strategy.md` (this file)
   - `content/Schema.md` (the topic JSON format)
   - `content/Outline.md` (full part/topic hierarchy)
   - A few seed topic JSONs in `content/parts/` to demonstrate the model.

2. **Topic authoring**
   - Hand- or LLM-author one topic JSON per item in the outline.
   - Each topic is reviewable in isolation — it's a small file with a clear
     scope.
   - Use the `lessons` array to reference videos; renderers resolve later.

3. **Renderer split**
   - `render_site.py` — produces a static site (HTML, JS for video embeds,
     a search index).
   - `render_book.py` — produces print HTML → LaTeX/PDF and EPUB. Reuses
     most of `book/render_page.py`'s logic; adds QR codes, sidebars,
     audience filtering.

4. **Migration**
   - Move existing `book/content/*.json` into `content/parts/` (renamed and
     re-tagged with audience).
   - Retire `book/Outline.md` and `book/page_format.md` once everything is
     ported. Keep `book/Instructions.md` (still relevant).

---

## Non-goals

- We are **not** building a CMS. Content is plain JSON in git, edited by
  humans (with LLM assistance), reviewed via PR.
- We are **not** mirroring the YouTube videos. They live on YouTube. The
  site embeds; the book QR-codes.
- We are **not** writing one giant book file or one giant website page. The
  unit of authorship is the **topic** — small, scoped, independently
  reviewable.
- We are **not** going to maintain duplicate prose for site and book. If a
  paragraph is different on the site than in the book, it's because it's
  tagged for a different audience — not because it was written twice.
