# Marketing Copy

Source-of-truth text for the book's external listings and cover. Keep these in
sync with the live KDP listing and the printed cover artwork.

| File | Used for |
|------|----------|
| `amazon_kdp_description.md` | KDP "Book Description" field (HTML-formatted) |
| `back_cover.md` | Back-cover blurb on the printed book |
| `author_bio.md` | "About the Author" page / press kit / back cover byline |
| `build_cover.py` | Generates the print-ready KDP wrap-cover PDF |

**Subtitle (current):** *Master Your Editor. Unleash Your Flow.*

## Cover PDF (`build_cover.py`)

`python book/marketing/build_cover.py --pages N` writes
`book/marketing/output/vimfu-cover.pdf`, the single-page wrap cover
ready for upload to KDP's "Use a print-ready cover PDF" flow. The
`output/` folder is git-ignored.

### KDP specs baked into the script

The book is **7.5 × 9.25 in paperback, B&W interior on white paper**.
Constants in `build_cover.py` reflect KDP's cover calculator for that
trim:

| Constant | Value | What it is |
|----------|-------|------------|
| `TRIM_W`, `TRIM_H` | `7.5`, `9.25` | Interior trim size — DO NOT change unless the book is re-formatted to a different size. |
| `BLEED` | `0.125` | Full-bleed outside all four edges of the assembled wrap. |
| `SPINE_PER_PAGE` | `0.002252` | KDP's white-paper formula: spine inches = pages × this number. **Cream paper would be 0.0025** (update if paper type ever changes). |
| `KDP_SAFE_H`, `KDP_SAFE_V` | `0.0625`, `0.125` | KDP's stated safe-area inset from trim for this size. Anything critical (text, faces, logos) must be inside this. |
| `SPINE_SAFE` | `0.0625` | Fold safety on each side of the spine. |
| `ART_INSET` | `0.125` | How far the front-cover artwork sits in from the trim. Slightly more than KDP's minimum so a minor mis-cut never crops the art. |
| `BACK_SAFE_H`, `BACK_SAFE_V` | `0.375`, `0.4` | Where back-cover text/photo sits relative to trim. Tighter than KDP's required margin so we use the larger 7.5"-wide trim well. |

### What changes between print runs

- **`--pages`** — every reprint with a different final page count
  needs the right `--pages` so the spine width and total sheet width
  recompute. Sheet width = `2 × BLEED + 2 × TRIM_W + spine`. Verify
  against KDP's "Full Cover" width in the cover calculator after
  rebuilding.
- **Page count drift**: when you change typography, add/remove
  topics, etc., always re-check the final interior PDF page count
  and pass it as `--pages N` before uploading.

### Assets used

| Path | What |
|------|------|
| `book/marketing/VimFu Cover.png` | Front-cover artwork. The non-ornate raccoon. (Not `VimFu Cover Ornate.png`.) |
| `book/marketing/me2.JPG` | Back-cover author photo. |
| `book/marketing/whisp.png` | Decorative wispy flourish placed between the back-cover blurb and the QR/URL row. Echoes the colored swirls on the front cover to tie front and back together. Source PNG is already on solid black so it blends seamlessly. Filename historical — keep the `wh` spelling. |
| `book/marketing/back_cover.md` | Back-cover blurb text. First line is rendered as the hook (large bold). |
| `book/marketing/author_bio.md` | "About the Author" paragraph next to the photo. |
| `book/marketing/fonts/Ubuntu-{Regular,Bold,Italic}.ttf` | Ubuntu Font Family (Ubuntu Font Licence) — matches the original cover branding. Bundled because Ubuntu is not available system-wide on Windows. |
| `docs/icon.png` | The round raccoon mascot placed at the top of the spine. |

### Style rules that the cover follows

- **Solid black** `(0, 0, 0)` background everywhere outside the
  artwork, so the seam between the front-cover art (which has its
  own black field) and the spine/back is invisible. Don't use a
  near-black — true `(0, 0, 0)` is what the cover art uses and any
  deviation shows up as a visible band.
- **Auto-trim the front-cover PNG.** The source `VimFu Cover.png`
  ships with a 3–5% solid-black border baked around the actual
  painted artwork. The script detects rows/columns of uniformly
  near-black pixels (`max channel < 16`) on all four edges and
  crops them off before fitting (`trim_black_border()`), so the
  visible art reaches the trim. If the cover artwork is ever
  re-exported without that border, the helper is a no-op (it
  returns the image unchanged) — leave it in.
- **No bleed of the cover art.** The trimmed artwork is uniformly
  scaled to fit inside the trim minus `ART_INSET` (`0.0625"`,
  matching KDP's horizontal safe-area minimum) and centered. The
  art must never reach the trim edge — KDP can shift the cut by a
  fraction of an inch and would crop into the art.
- **Use the non-ornate front cover.** The marketing folder contains
  both `VimFu Cover.png` (this one — flat black field, used) and
  `VimFu Cover Ornate.png` (with a decorative border, unused). The
  ornate version's frame conflicts with the spine, so we always use
  the non-ornate file.
- **Spine title** "VimFu" is sized at `≈1.05 × spine_inner_width`
  (in points) so it occupies about three-quarters of the spine
  width regardless of page count, and is centered both horizontally
  (between the front/back folds) and vertically (along the spine
  length). It reads top-to-bottom on the shelf (the standard
  English-language direction). The horizontal-centering offset of
  `0.36 × size` is the cap-half for Ubuntu Bold; if the font ever
  changes, that constant in `draw_rotated_centered()` will need to
  be re-tuned.
- **Mascot icon** at the top of the spine is square, sized to the
  spine inner width, placed 0.35" below the top trim. We pass
  `mask="auto"` so any transparency in `docs/icon.png` shows the
  black background through — currently the icon's PNG isn't fully
  transparent at the corners so a faint square frame is visible
  against the black; that has been judged acceptable.
- **Back-cover hook**: the first non-empty line of `back_cover.md`
  is rendered as the bold heading; remaining paragraphs are body
  copy. The hook is sized so the current copy (*"Stop memorizing
  keystrokes. Start understanding the editor."*) fits on a single
  line at the current `BACK_SAFE_H` width. If you change the hook
  text, re-check that it doesn't wrap — either shorten the line or
  drop `heading_style.fontSize` a hair.
- **Back-cover copy framing** mirrors the book's own "About the QR
  codes" intro ("the book stands on its own…", "companion website,
  short screen-recorded video for every technique, browser-based
  Vim simulator…") rather than the older "book is the why / site
  is the show-me" line. Keep the back cover and the QR-codes intro
  voicing consistent.
- **Author photo** (`me2.JPG`) goes top-left of the back cover at
  1.5" square, with the bio paragraph to its right in the same
  vertical band. The blurb sits below them and the
  `vimfubook.com` URL footer pinned 0.15" above the bottom safe
  edge — leaving the bottom-right empty for KDP's auto-added
  barcode (KDP reserves a 2"-wide block there at print time, so
  never put critical content in the back-cover bottom-right).

### When iterating

1. Edit `build_cover.py` or the source `.md` files.
2. Re-run `python book/marketing/build_cover.py --pages N`.
3. Visually inspect `book/marketing/output/vimfu-cover.pdf` (or
   render a PNG preview via PyMuPDF: `doc[0].get_pixmap(dpi=110)`).
4. Before uploading to KDP, sanity-check: full-cover width matches
   KDP's reported value for the final page count (use the cover
   calculator at the same trim/paper/page count to confirm).

### Design decisions worth knowing (not obvious from the code)

- **Why Ubuntu, not Libertinus.** The book interior is set in
  Libertinus Serif; the cover uses **Ubuntu** to match the original
  branding (the YouTube channel, the website wordmark, the
  `vimfu_dark.png` banner, and stickers). Don't switch the cover
  font to Libertinus without also re-branding the rest of the
  marketing surfaces. Ubuntu TTFs are bundled under `fonts/`
  because Ubuntu is not installed system-wide on the target
  Windows dev machine.
- **Why true black, not "rich black" or "warm black".** KDP prints
  POD covers on a digital press where any color other than `K=100`
  shifts slightly between print runs. The cover artwork is built
  on `(0, 0, 0)`; matching that exactly avoids a visible band
  between art and surrounding fields.
- **Why we crop the PNG instead of fixing the source.** The
  artwork ships from the designer with the black margin baked in
  at the requested aspect. We crop in code so a re-export with or
  without that border both work — and so it's reproducible by
  agents without round-tripping through an image editor.
- **Why `ART_INSET = 0.0625"` and not `0"`.** KDP's safe-area
  minimum horizontally is 0.0625"; printing exactly at that lets
  the art look as big as possible without risking a cut into it.
  Going to `0"` (right at the trim) gambles on KDP's cut precision.
- **Why centered spine title, not top-aligned.** Earlier drafts
  put VimFu just below the mascot. A page-count change moves the
  spine width and ends up shifting both elements unpredictably.
  Centering "VimFu" along the length of the spine makes the
  composition robust to spine-width changes between print runs —
  only the spacing around it (icon at top, author near bottom)
  needs to relax/tighten.
- **Why no barcode area in the script.** KDP auto-stamps the
  barcode at upload time, so we deliberately leave the
  back-cover bottom-right empty. Do not draw anything there.
- **Why the back cover copies the book's QR-codes-page voicing.**
  When a reader picks up the book and turns it over, the line
  "the book stands on its own — you can read it cover to cover
  without ever picking up a phone" sets the same expectation they
  meet again in the front matter. Keep them in sync.

### Updating this doc

If you change a constant or layout decision in `build_cover.py`,
update the matching row in the table above. If you make a design
call that isn't expressible in code (e.g. why a value was chosen,
what alternative was rejected, how a future iteration should
think about a tradeoff), record it under "Design decisions worth
knowing". This file is what an agent (or future you) reads before
touching the cover.

### KDP cover calculator (reference)

For 7.5 × 9.25 paperback, B&W, white paper, the numbers KDP reports
scale with page count. Examples:

| Pages | Spine | Full cover (W × H) |
|------:|------:|--------------------|
| 400   | 0.901 | 16.151 × 9.50 |
| 420   | 0.946 | 16.196 × 9.50 |
| 422   | 0.950 | 16.200 × 9.50 | ← current
| 440   | 0.991 | 16.241 × 9.50 |

(`spine = pages × 0.002252`, `width = 2 × 0.125 + 2 × 7.5 + spine`,
`height = 2 × 0.125 + 9.25 = 9.50`.)

