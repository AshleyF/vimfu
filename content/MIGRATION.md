# Content Migration

Tracks what existing material has been absorbed into the new `content/`
system and what remains to retire. The principle from the strategy:
**no duplicate information**. As content moves into `content/`, the old
copy is staged for deletion.

This file is itself transient — it should be deleted when the migration
is complete and `content/` is the only home of authored material.

---

## Status legend

- ✅ **Absorbed** — all valuable content has been moved into `content/`.
  Source can be deleted.
- 🟡 **Partially absorbed** — still useful as raw material to mine when
  authoring more topics; delete when topic authoring is complete.
- 🔵 **Keep** — has a separate, ongoing job (e.g. used by tests, or by a
  different subsystem). Reference, don't delete.
- ⏳ **Pending** — not yet absorbed; still primary source of truth.

---

## What's been deleted

These were fully absorbed and are now gone:

- ❌ `book/page_format.md` — superseded by `content/Schema.md`.
- ❌ `book/Outline.md` — structure and prose absorbed into
  `content/Outline.md` and the topics under `content/parts/`.
- ❌ `book/Instructions.md` — tone absorbed into `content/Strategy.md`;
  demo-verification, GIF pipeline, and pairing-not-mirroring sections
  absorbed into `content/Authoring.md`.
- ❌ `brainstorming/book_rendering.md` — historical design notes;
  superseded by `Strategy.md` + `Schema.md`. The actual Frame JSON spec
  lives in `brainstorming/frame_format.md` (kept).

## Still to migrate

These are the last items pending — primary sources of truth until ported:

| File                                     | Status | Notes |
|------------------------------------------|--------|-------|
| `book/content/front_matter.json`         | ⏳     | Should become `content/parts/00-front/*.json`. |
| `book/content/ch01_why_vim.json`         | ⏳     | Most prose forked into `content/parts/01-foundations/*.json`; port the rest, then delete. |
| `book/content/ch02_survival.json`        | ⏳     | `content/parts/02-survival/01-open-save-quit.json` covers a slice. Port the rest. |
| `book/content/ch03_basic_editing.json`   | ⏳     | Will become `content/parts/03-basic-editing/*.json`. |
| `book/render_page.py`                    | 🟡     | Will be split into `render_site.py` and `render_book.py` (Phase 3 of strategy). Keep until both renderers exist. |
| `book/output/*`                          | 🟡     | Generated artifacts from the old renderer. Regenerate from the new pipeline once it lands. |

When `book/content/*.json` is fully ported:

```
git rm -r book/content/
```

When the renderer split is done:

```
git rm book/render_page.py
git rm -r book/output/
```

By then the entire `book/` directory should be empty and can be removed.

## Kept (separate, ongoing jobs)

| File                                     | Why keep |
|------------------------------------------|----------|
| `curriculum/Curriculum.md`               | Master video curriculum. Drives what gets recorded; renderers read it indirectly via lesson JSONs. |
| `curriculum/shorts/*.json`               | Per-lesson source of truth (script, narration, video metadata). |
| `sim/Reference.md`                       | Sim-specific command reference. Used as ground truth by simulator tests. Mine for content tables. |
| `sim/VimBehavior.md`                     | Implementation-grade behavioral spec. Used by simulator tests. Primary source for `internals` blocks — every developer-internals callout should trace back here. |
| `sim/Instructions.md`                    | Sim build/test instructions. |
| `Learnings.md`                           | LLM-collaboration meta-notes. Project-level, not user-facing book/site material. |
| `Notes.md`                               | Project-level miscellany. |
| `Keys.md`                                | Raw `:help index.txt` dump — exhaustive reference data. Source for `appendix.complete-key-reference`. |
| `Commands.md`                            | Raw `:help ex-cmd-index` dump — same. Source for ex-command appendix tables. |
| `README.md`                              | Repo-level. Update once the new content directory is live. |
| `brainstorming/frame_format.md`          | Spec for the Frame JSON used by `screenshot` blocks. Authoritative. |

---

## What to mine, in priority order

For LLM- or human-authored topic generation, these are the highest-value
sources to read, in roughly this order:

1. **`sim/VimBehavior.md`** — the behavioral spec. *The* source for
   `internals` blocks. Every developer-internals callout should be
   factually grounded here.
2. **`curriculum/shorts/<NNNN>.json`** — for the topic's video lessons.
   The `description`, `setup`, and `say` fields tell you exactly what
   each video teaches and in what words.
3. **`sim/Reference.md`** — for reference tables. Especially good for
   `keys` and `table` blocks listing every variant of a command family.
4. **`book/Outline.md`** — for the prose voice and per-section intros.
   The existing outline already has well-tuned narrative paragraphs for
   most of the curriculum.
5. **`book/content/ch0*.json`** — for the existing block format and
   fully-realized voice on a handful of chapters. Use as templates.
