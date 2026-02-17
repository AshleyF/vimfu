# VimFu Book — Instructions

These are standing instructions for generating the VimFu book. Feed this document into an LLM
alongside the book outline (`book/Outline.md`), the curriculum (`curriculum/Curriculum.md`),
the page format spec (`book/page_format.md`), and any relevant lesson JSONs when producing
new book content.

---

## Content Generation Flow

The flow for producing book content follows this pipeline:

1. **Read `curriculum/Curriculum.md`** — the master curriculum for the video series. This is
   the raw material: 500 lessons organized into 18 parts, covering every Vim keybinding.

2. **Read `book/Outline.md`** — the book outline. This reorganizes the curriculum into a
   27-chapter book structure with 7 appendices. The outline defines which video lessons map
   to which book chapters/sections, adds book-only material (introduction, philosophy,
   deep dives), and establishes the reading order. The outline is the source of truth for
   book structure — it supersedes the curriculum's part numbering.

3. **Read this file (`book/Instructions.md`)** — for tone, style, visual design, and
   technical guidelines.

4. **Read `book/page_format.md`** — for the JSON schema that content files must follow.

5. **To generate a specific chapter**, read the relevant lesson JSONs from
   `curriculum/shorts/` (or `curriculum/longs/`). These contain the demo file content, key
   sequences, narration, and (for uploaded videos) YouTube video IDs for QR codes.

6. **Hand-author a content JSON** in `book/content/` following the `vimfu-book-page` format.
   Use the lesson JSONs for demo content; write prose following the tone guidelines;
   reference the outline for what the chapter should cover. For screenshots, capture frames
   from real nvim sessions using ShellPilot and embed the Frame JSON directly in the content
   file (see "Demo Verification" below).

7. **Run `render_page.py`** to produce HTML in `book/output/`. Future: LaTeX, EPUB.

The key principle: **the content JSON files are the source of truth**, just like lesson JSONs
are the source of truth for videos. You hand-author (or LLM-author) the JSON, and renderers
produce output from it. There are no code generators that produce the JSON — it's written
directly, reviewed, and committed.

Second principle: **`Curriculum.md` is for the videos. `Outline.md` is for the book.** The
curriculum is a flat list of 500 lessons. The outline reorganizes those into chapters that
read well as prose — grouping related concepts, adding introductory and connective material,
and structuring the content for a book rather than a playlist.

---

## Content Directory Structure

Book content lives in `book/content/`. Each chapter/section is a JSON file in the
`vimfu-book-page` format (see `book/page_format.md`). Files are named by chapter number
and slug:

```
book/content/
  front_matter.json          Front matter (title, about, how-to-use)
  ch01_why_vim.json           Chapter 1 — Why Vim?
  ch02_survival.json          Chapter 2 — Survival
  ch03_basic_editing.json     Chapter 3 — Basic Editing
  ch04_search_and_find.json   Chapter 4 — Search and Find
  ...
  ch27_advanced_topics.json   Chapter 27 — Advanced Topics
  app_a_synonyms.json         Appendix A — Synonym Reference
  app_b_grammar_matrix.json   Appendix B — The Vim Grammar Matrix
  ...
```

Each JSON file is self-contained: title, subtitle, lesson numbers, and an ordered array of
content blocks (heading, prose, keys, screenshot, tip, table, divider, qr). The renderer
(`render_page.py`) converts each to self-contained HTML. A future assembler will combine
them into a full book.

---

## Demo Verification

### Why Verify

Screenshots in the book are captured from a real Neovim session running in a terminal
emulator (ShellPilot + ConPTY + pyte). If the key sequences in a demo are wrong — wrong
motion, wrong file content, wrong cursor position — the screenshot will show the error.
**Every demo must be verified by replaying it against the terminal emulator.**

### How to Capture Screenshots

Use ShellPilot to drive a real nvim session and capture the pyte screen buffer as Frame
JSON. The process:

1. Start a ConPTY session via ShellPilot
2. Create a temp file with the demo content
3. Open it in nvim
4. Send key sequences (with settle pauses between steps)
5. Read the pyte screen buffer → Frame JSON (rows, cols, cursor, lines with color runs)
6. Clean up the temp file and session

The captured Frame JSON gets embedded directly in the content JSON as a `"screenshot"` block
with `"frame"` and `"caption"` fields.

### Inspect the Frame

Before embedding, verify that:
- The cursor is where you expect it
- The syntax highlighting looks correct
- The status bar shows the expected filename and cursor position
- Search highlights or visual selections appear if expected
- The content hasn't been corrupted by timing issues

Render to HTML and visually inspect:
`python render_page.py book/content/ch02_survival.json -o book/output/`

### Timing and Reliability

Terminal emulator capture is inherently timing-sensitive. If a screenshot looks wrong:
- Increase the settle time between key steps
- Split complex key sequences into smaller steps with pauses
- Re-run the capture — pyte rendering is deterministic for the same input, so flaky
  captures usually indicate insufficient settle time

### When to Create New Videos

If the book outline references lessons that don't have video JSONs yet (lessons beyond 85),
the book content should wait until the videos are done:
1. Create the video JSON following `curriculum/Instructions.md` guidelines
2. Run the video through `player.py` to generate and verify it
3. Upload to YouTube and record the `youtube.videoId`
4. Then author the book chapter using the lesson's demo content for screenshots

The principle: **videos come first, then book content**. The book references the videos,
not the other way around.

---

## Demo GIF Animations (HTML Output)

In addition to static screenshots, the HTML output supports **animated GIF demos** of
entire lessons. These show the full terminal replay — cursor movement, text changes,
syntax highlighting — as a looping animation.

### The `demo` Block

To embed a lesson animation, add a `"demo"` block to the content JSON:

```json
{
  "type": "demo",
  "lesson": 7,
  "caption": "Saving a file in Vim"
}
```

- `lesson` — the lesson number (matches `curriculum/shorts/NNNN_*.json`)
- `caption` — optional caption below the animation

### How It Works

The renderer (`render_page.py`) resolves the lesson number to a GIF file using a
two-stage pipeline:

1. **Check cache** — look for `shellpilot/videos/<slug>/<slug>.frames.gif`
2. **Generate on the fly** — if the GIF doesn't exist:
   - Run `capture_frames.py` to replay the lesson headlessly (ConPTY + pyte)
     and capture terminal frames with full color data
   - Run `gif_maker.py` to render the frames into an animated GIF
3. **Copy to output** — the GIF is copied into `output/images/` alongside the HTML

The `shellpilot/videos/` directory is a **cache**. GIFs are only generated when they
don't already exist. To force regeneration, delete the cached `.frames.json` and
`.frames.gif` files, or use `gen_all_gifs.py --force`.

### Batch Pre-generation

To pre-generate GIFs for all lessons (so rendering is instant):

```bash
cd shellpilot
python gen_all_gifs.py              # all lessons
python gen_all_gifs.py 42           # just lesson 42
python gen_all_gifs.py 10-20        # range
python gen_all_gifs.py --force      # regenerate even if cached
```

### HTML Output Structure

When `render_page.py` produces HTML with demo blocks, the output looks like:

```
book/output/
  ch02_survival.html              self-contained HTML
  images/
    0007_saving_your_file.frames.gif
    0005_typing_text.frames.gif
    ...                            one GIF per demo block
```

The `images/` directory is shared across all chapters. GIFs are referenced by
relative path (`images/NNNN_slug.frames.gif`) so the HTML is portable.

### When to Use Demo vs Screenshot

- **`screenshot`** — static Frame JSON embedded in the content JSON. Best for
  showing a specific cursor position, before/after states, or annotated moments.
  Works in all output formats (HTML, LaTeX, EPUB).
- **`demo`** — animated GIF of the full lesson. Best for showing motion, flow,
  and the overall feel of a command sequence. **HTML only** (future formats will
  need a different approach — e.g., QR code linking to the video).

---

## Purpose

The VimFu book is a **printed / Kindle companion** to the VimFu YouTube Shorts video series.
The videos are sub-60-second lessons — punchy, visual, one concept each. The book provides the
**cohesive, instructional narrative** that ties those bite-sized lessons together: deeper
explanations, conceptual context, how things work under the hood, and practical advice that
can't fit in 60 seconds.

The book is **not a transcript of the videos**. It's a parallel telling of the same material,
structured for reading rather than watching. A reader who only reads the book should learn
everything. A viewer who only watches the videos should learn everything. But someone who does
both gets the best of both worlds — the book explains *why*, the videos show *how*.

---

## Relationship to the Videos

### Pairing, Not Mirroring

The book follows the same curriculum arc as the videos (see `curriculum/Curriculum.md`), but
it doesn't map one-to-one. A single **section** of the book may cover several video lessons.
For example, the "Searching & Finding" section covers lessons 46–57 (pattern search, character
find, repeat motions) as one coherent chapter, whereas the videos treat each of those as an
independent 60-second short.

The book groups related lessons into sections that read well as prose. The curriculum's
18-part structure is a good starting point for chapters, but the book may combine, reorder,
or expand as needed for narrative flow.

### QR Codes to Videos

Every section of the book will include **QR codes** linking to the corresponding YouTube
videos. A reader can scan the QR code and immediately watch the demo that matches what
they just read. This is one of the book's key selling points — it bridges print and video.

Because sections cover multiple lessons, a single section may have several QR codes (one per
video, or a curated subset). The QR codes should appear at natural break points — after a
concept is introduced and before the next one begins, or collected in a sidebar/margin.

### Similar Demos

The book and videos should use **similar or matching demo content** wherever practical. If the
video for lesson 52 (`f{char}`) demonstrates finding characters in a Python function called
`summon_familiar()`, the book's coverage of `f` should reference the same or a similar example.
This way, when a reader scans the QR code and watches the video, the demo feels like a
continuation of what they just read, not a completely unrelated example.

That said, the book can (and should) include **additional examples** beyond what the video
shows. The video picks one tight demo; the book can walk through two or three variations,
discuss edge cases, and show before/after states.

---

## What the Book Adds Beyond the Videos

### Introductory Material

The book should open with material the videos don't cover:

- **Why learn Vim keybindings?** — The productivity argument. Modal editing lets you express
  editing intent as a language. Once you internalize the grammar, you think in edits rather
  than mouse movements. This isn't nostalgia — it's ergonomics and speed.

- **You don't need Vim (the editor).** — The demos use Neovim, but you can use Vim keybindings
  in almost any editor: VS Code (Vim extension), JetBrains IDEs (IdeaVim), Visual Studio,
  Sublime Text, Emacs (Evil mode), and more. The book is about the **keybindings and the
  editing language**, not about any specific editor. Use whatever you like — just turn on
  Vim mode.

- **Vi vs Vim vs Neovim — does it matter?** — Brief history. Vi was the original (1976).
  Vim added massive improvements (1991). Neovim is a modern fork with Lua config and better
  defaults (2014). For the keybindings covered in this book, they're all the same. The
  differences matter for configuration and plugins, not for `daw` or `ci"`.

- **How to use this book.** — Read it front to back if you're a beginner. Jump around if
  you already know the basics. Scan the QR codes to watch the demos. Practice each command
  as you read — have an editor open and follow along.

### Conceptual Explanations

The book should explain **how Vim works internally** in ways the videos can't:

- **Registers** — What are they? Where does yanked text go? What's the unnamed register (`""`)?
  What are the numbered registers (`"0`–`"9`)? How does the small delete register work? Can
  you paste from a named register you recorded a macro into — and see the macro as text?
  (Yes, and you can edit it and put it back. Mind-blowing.)

- **The undo tree** — Vim doesn't have linear undo. It has a *tree*. Every branch is preserved.
  `u` walks back, `Ctrl-R` walks forward, but `g-` and `g+` walk the tree chronologically.
  `:earlier 5m` goes back five minutes. This is wild and the book should explain it well.

- **The Vim grammar** — Operators × motions × text objects. The book should have a dedicated
  section that explains this composable grammar thoroughly, with a matrix table showing how
  a handful of operators and a handful of motions/objects produce dozens of commands.

- **Modes** — Normal, Insert, Visual (charwise, linewise, blockwise), Command-line, Replace,
  Select, Ex, Terminal. How they interact. Why modal editing is powerful, not primitive.

- **The dot command** — How it records "the last change." What counts as a change (hint:
  entering insert mode through leaving it is one change). How to structure your editing to
  make dot maximally useful.

- **Macros** — How they're just register contents. Record into `a`, paste from `"a`, edit the
  text, yank back into `"a` — now you've edited a macro. How `100@a` runs until it errors.
  How macros compose with the rest of the grammar.

### Philosophy and Mindset

Sprinkle these themes throughout the book, not as a separate chapter:

- **Normal mode is "normal."** You spend more time reading and navigating code than inserting.
  Normal mode is your resting state. Insert mode is a brief excursion.

- **Every key does something.** In normal mode, every single key on the keyboard has a function.
  That's the whole point of modal editing — you don't need modifier keys because you have an
  entire keyboard of commands. Lowercase, uppercase, symbols, Ctrl-keys, and prefix keys
  (`g`, `z`, `[`, `]`, `Ctrl-W`) give you hundreds of commands.

- **It's a language, not a list.** The power isn't in memorizing 500 keybindings. It's in
  learning a vocabulary of ~15 operators and ~30 motions/text objects that multiply together.
  `d` + `iw` = delete inner word. `c` + `i"` = change inside quotes. Learn one new operator
  and it instantly works with every motion you already know.

- **Hands off the mouse. Hands off the arrows.** Then eventually, less reliance on `hjkl` too.
  The goal is to think in terms of "jump to the next function" or "change this word," not
  "move right 14 characters."

---

## Book Structure (Tentative)

```
Front Matter
  - Title page
  - About this book / How to use it
  - QR code to the YouTube playlist

Introduction
  - Why Vim keybindings?
  - You don't need Vim (the editor)
  - Vi vs Vim vs Neovim
  - The modal editing philosophy
  - How to read this book

Part I — Survival (Curriculum Part 1, lessons 1–15)
  - Getting in, getting out, and staying calm

Part II — Basic Editing (Curriculum Part 2, lessons 16–45)
  - Insert modes, motions, delete, change, yank, put, replace

Part III — Becoming Productive (Curriculum Part 3, lessons 46–90)
  - Search, find, counts, visual mode, dot command, text objects, scrolling
  - The Vim grammar (deep dive)

Part IV — Intermediate Power (Curriculum Part 4, lessons 91–135)
  - Motions, marks, jump list, replace, indent, case, join, registers, macros, windows

Part V — Walking the Keyboard (Curriculum Parts 5–8, lessons 136–248)
  - Lowercase, uppercase, symbols, numbers, Ctrl keys
  - Presented as a reference with short entries per key

Part VI — Prefix Commands (Curriculum Parts 9–12, lessons 249–365)
  - The g commands, z commands, bracket commands, Ctrl-W window commands

Part VII — Insert & Command-Line Modes (Curriculum Parts 13–16, lessons 366–460)
  - Insert mode keys, Ctrl-X completion, Ex commands, visual mode deep dive, command-line tips

Part VIII — Patterns & Advanced (Curriculum Parts 17–18, lessons 461–500)
  - Practical patterns, tips, tricks, advanced topics

Appendices
  - Synonym reference (keys that do the same thing)
  - The Vim grammar matrix (operators × motions × text objects)
  - Suggested learning path (day-by-day guide)
  - Surround plugin reference
  - Motion classification (exclusive, inclusive, linewise)
  - Glossary
```

---

## Visual Design & Screenshots

### Dense but Not Cluttered

The book should have **frequent screenshots** — more than a typical programming book. Since
Vim is visual (you need to *see* the cursor move, the text change, the selection highlight),
screenshots are essential for print where you can't embed video.

Target layout: **text on one side, screenshots on the other**, alternating sides page by page.
Most prose should be adjacent to a relevant screenshot. This gives the book a distinctive,
visually rich feel — almost like a comic book for terminal nerds.

### Screenshot Format

Screenshots are terminal frame captures rendered as SVG (for HTML) or PGF/TikZ (for LaTeX/PDF).
They use the same Frame JSON format as the video pipeline — see `book/page_format.md` for the
`"screenshot"` block type and `brainstorming/frame_format.md` for the Frame JSON spec.

For showing full lesson demos as animations, use the `"demo"` block type instead — it embeds
an animated GIF of the entire lesson replay (see "Demo GIF Animations" section above).

Keep screenshots focused: **11–20 rows, 40 columns** is the sweet spot. Show just enough
context for the reader to understand what's happening. Highlight the active area (cursor
position, changed text, visual selection) with the editor's own colors — no external
annotations needed since Neovim's syntax highlighting and cursor do the work.

### Fewer Screenshots Than the Videos, But Still Lots

The video logs capture a screenshot at every screen change. The book should be **sparser** —
show key "before" and "after" states, not every intermediate step. For a `ci"` demo, show:
1. The line with the cursor on/near the quotes (before)
2. The line with the text deleted and cursor in insert mode (after typing the replacement)
3. Optionally, the result after pressing Escape

Three screenshots, not twelve. But over a whole section covering several commands, that's
still a lot of screenshots — which is good. The book should feel visual.

### Key Badges

Inline key references use the `{key:X}` marker syntax (see `page_format.md`). These render
as styled keyboard badges (`<kbd>` in HTML, custom macro in LaTeX). Use them liberally in
prose: "Press {key:d}{key:i}{key:w} to delete the inner word."

---

## Tone and Style

- **Conversational but authoritative.** Not academic, not slangy. Like a knowledgeable friend
  explaining things clearly.
- **Short paragraphs.** Print books with dense technical content need breathing room.
- **Concrete before abstract.** Show the command, then explain the concept. Don't lead with
  theory.
- **Humor welcome.** The demo files are deliberately funny (spell-casting classes, robot
  personality modules, pizza-ordering APIs). The prose can be lighthearted too, but the
  humor should serve the teaching, not distract from it.
- **No "obviously" or "simply."** What's obvious to an expert is confusing to a beginner.
  Explain everything clearly, even if it feels redundant.

---

## Pipeline

The book pipeline mirrors the video pipeline: **hand-author JSON, then render.**

```
curriculum/Curriculum.md          (what to cover)
curriculum/shorts/*.json          (lesson definitions, demo content, video IDs)
curriculum/longs/*.json           (longer-form lessons)
book/Outline.md                   (chapter structure)
book/Instructions.md              (this file — tone, style, guidelines)
        │
        ▼  (human + LLM authoring)
  book/content/<chapter>.json     (hand-authored page JSON, the SOURCE)
        │
        ▼
  book/render_page.py             (renders to self-contained HTML)
        │                              │
        │    ┌─────────────────────────┘
        │    │  demo blocks trigger GIF pipeline:
        │    │  shellpilot/capture_frames.py → .frames.json
        │    │  shellpilot/gif_maker.py      → .frames.gif  (cached)
        │    │  copy .gif → output/images/
        │    └─────────────────────────┐
        ▼                              ▼
  book/output/<chapter>.html      (viewable in browser — DERIVED, gitignored)
  book/output/images/*.gif        (demo GIFs — DERIVED, gitignored)
```

Future renderers will produce LaTeX (for print PDF) and ICML/EPUB (for Kindle/ebook).

The content JSON files are the source of truth — the same way lesson JSONs are the source
of truth for videos. There are no Python scripts that generate the content JSON. You write
it directly (with LLM assistance), review it, and commit it.

Screenshots are embedded directly in the content JSON as Frame JSON (captured from real nvim
via ShellPilot). The prose should follow the tone and style guidelines above, and the demos
should use similar content to the corresponding videos.

### QR Code Integration

When a chapter covers lessons that have YouTube video IDs (stored in the lesson JSON under
`youtube.videoId` and `youtube.url`), include QR code blocks linking to those videos:

```json
{
  "type": "qr",
  "url": "https://youtube.com/shorts/kH-tncv1g4w",
  "caption": "Watch: The Vim Grammar (60s)"
}
```

Renderers generate the QR image inline (using a Python QR library for HTML/PDF, or a
LaTeX QR package).

---

## Existing Book Content

The following content files exist in `book/content/`:

- **Front Matter** (`front_matter.json`) — title page, about, how to use the book
- **Chapter 1 — Why Vim?** (`ch01_why_vim.json`) — book-only intro, no screenshots
- **Chapter 2 — Survival** (`ch02_survival.json`) — lessons 2, 4–15, with nvim screenshots
- **Chapter 3 — Basic Editing** (`ch03_basic_editing.json`) — lessons 16–45, with nvim screenshots

Use these as reference for tone, structure, and screenshot density when authoring new chapters.

---

## What Comes Next

The immediate priority is generating sections for the curriculum parts that already have
completed videos (lessons 1–85). After that, the pipeline is:

1. Write more videos (lessons 86+)
2. Generate corresponding book sections
3. Build a full-book assembler that combines all sections into a single document
4. Add front matter, introduction, and appendices
5. Render to print-ready PDF (LaTeX) and Kindle format (EPUB/ICML)
6. Generate and embed QR codes linking to YouTube videos
