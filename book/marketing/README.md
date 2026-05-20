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
| `book/marketing/back_cover.md` | Back-cover blurb text. First line is rendered as the hook (large bold). |
| `book/marketing/author_bio.md` | "About the Author" paragraph next to the photo. |
| `book/marketing/fonts/Ubuntu-{Regular,Bold,Italic}.ttf` | Ubuntu Font Family (Ubuntu Font Licence) — matches the original cover branding. Bundled because Ubuntu is not available system-wide on Windows. |
| `docs/icon.png` | The round raccoon mascot placed at the top of the spine. |

### Style rules that the cover follows

- **Solid black** `(0, 0, 0)` background everywhere outside the
  artwork, so the seam between the front-cover art (which has its
  own black field) and the spine/back is invisible.
- **No bleed of the cover art**: the front-cover image is uniformly
  scaled to fit inside the trim minus `ART_INSET` and centered. It
  must never reach the trim edge.
- **Spine title** "VimFu" is sized at `≈1.05 × spine_inner_width`
  (in points) so it occupies about three-quarters of the spine
  width regardless of page count, and is centered both horizontally
  (between the front/back folds) and vertically (along the spine
  length). It reads top-to-bottom on the shelf (the standard
  English-language direction).
- **Mascot icon** at the top of the spine is square, sized to the
  spine inner width.
- **Back-cover hook**: the first non-empty line of `back_cover.md`
  is rendered as the bold heading; remaining paragraphs are body
  copy.

### When iterating

1. Edit `build_cover.py` or the source `.md` files.
2. Re-run `python book/marketing/build_cover.py --pages N`.
3. Visually inspect `book/marketing/output/vimfu-cover.pdf` (or
   render a PNG preview via PyMuPDF: `doc[0].get_pixmap(dpi=110)`).
4. Before uploading to KDP, sanity-check: full-cover width matches
   KDP's reported value for the final page count (use the cover
   calculator at the same trim/paper/page count to confirm).

### KDP cover calculator (reference)

For 7.5 × 9.25 paperback, B&W, white paper, the numbers KDP reports
scale with page count. Examples:

| Pages | Spine | Full cover (W × H) |
|------:|------:|--------------------|
| 400   | 0.901 | 16.151 × 9.50 |
| 420   | 0.946 | 16.196 × 9.50 |
| 440   | 0.991 | 16.241 × 9.50 |

(`spine = pages × 0.002252`, `width = 2 × 0.125 + 2 × 7.5 + spine`,
`height = 2 × 0.125 + 9.25 = 9.50`.)

