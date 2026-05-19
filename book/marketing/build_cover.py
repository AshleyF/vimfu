"""Build a print-ready KDP paperback cover PDF for VimFu.

Generates a single-page wrap-around cover (back + spine + front) sized
to KDP's specs for a 6×9 paperback on white paper, with 0.125" bleed
on all outside edges. The spine width is computed from the page count.

KDP formula for white paper paperbacks:
    spine_inches = page_count * 0.002252

Usage:
    python build_cover.py                       # uses default page count
    python build_cover.py --pages 421
    python build_cover.py --pages 421 --out my-cover.pdf

The PDF goes to ``book/marketing/output/vimfu-cover.pdf`` by default
(the ``output/`` folder is git-ignored, this is a build artifact).

Assets pulled (relative to this script):
  * ``VimFu Cover.png`` — front-cover artwork (raccoon)
  * ``me2.JPG``          — author photo
  * ``../../docs/icon.png`` — round raccoon mascot (placed top of spine)
  * ``back_cover.md``    — back-cover blurb
  * ``author_bio.md``    — author bio paragraph
"""
from __future__ import annotations

import argparse
import io
from pathlib import Path

from PIL import Image
from reportlab.lib.colors import Color, white
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.platypus import Frame, Paragraph

ROOT = Path(__file__).resolve().parent
DOCS_ICON = ROOT.parent.parent / "docs" / "icon.png"
FRONT_ART = ROOT / "VimFu Cover.png"
AUTHOR_PHOTO = ROOT / "me2.JPG"
BACK_COVER_MD = ROOT / "back_cover.md"
AUTHOR_BIO_MD = ROOT / "author_bio.md"
DEFAULT_OUT = ROOT / "output" / "vimfu-cover.pdf"

# --- KDP specs (inches) -------------------------------------------------
TRIM_W = 6.0
TRIM_H = 9.0
BLEED = 0.125
# Inside text/image safe area, measured in from the trim edge.
SAFE = 0.25
# Spine safety: keep critical content this far from the fold on each
# side (KDP recommends 0.0625"; we use a little more for comfort).
SPINE_SAFE = 0.0625
# White paper, B&W interior: 0.002252" per page.
SPINE_PER_PAGE = 0.002252

# --- Visual style -------------------------------------------------------
BG_COLOR = Color(0.04, 0.04, 0.04)  # near-black (slight grey reads as ink rather than punch-out)
TEXT_COLOR = white


def spine_inches(pages: int) -> float:
    """KDP spine-width formula for white paper, B&W interior."""
    return pages * SPINE_PER_PAGE


def read_md_body(path: Path) -> str:
    """Strip the leading ``# Heading`` and return body paragraphs joined."""
    lines = path.read_text(encoding="utf-8").splitlines()
    body = [ln for ln in lines if not ln.startswith("#")]
    # Join non-empty groups with blank-line separators preserved.
    return "\n".join(body).strip()


def cover_aspect_crop(img: Image.Image, target_w: float, target_h: float) -> Image.Image:
    """Crop ``img`` to the aspect ratio of ``target_w × target_h``.

    Centers the crop; preserves the long edge. Returns a new image; the
    original is not modified.
    """
    target_ratio = target_w / target_h
    img_ratio = img.width / img.height
    if img_ratio > target_ratio:
        # Image is wider — crop sides.
        new_w = int(img.height * target_ratio)
        left = (img.width - new_w) // 2
        return img.crop((left, 0, left + new_w, img.height))
    # Image is taller — crop top/bottom.
    new_h = int(img.width / target_ratio)
    top = (img.height - new_h) // 2
    return img.crop((0, top, img.width, top + new_h))


def pil_to_reader(img: Image.Image) -> ImageReader:
    """Wrap a PIL image as a reportlab ``ImageReader`` (in-memory PNG)."""
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return ImageReader(buf)


def draw_paragraph(c: canvas.Canvas, text: str, x: float, y: float,
                   w: float, h: float, style: ParagraphStyle) -> None:
    """Draw wrapped paragraph text inside the rectangle (x, y, w, h).

    Coordinates are in points (reportlab's native unit). ``y`` is the
    bottom of the frame.
    """
    paragraphs = []
    for chunk in text.split("\n\n"):
        chunk = chunk.replace("\n", " ").strip()
        if chunk:
            paragraphs.append(Paragraph(chunk, style))
    frame = Frame(x, y, w, h, leftPadding=0, rightPadding=0,
                  topPadding=0, bottomPadding=0, showBoundary=0)
    frame.addFromList(paragraphs, c)


def build_cover(pages: int, out_path: Path) -> None:
    spine = spine_inches(pages)
    page_w = (BLEED + TRIM_W + spine + TRIM_W + BLEED)
    page_h = (BLEED + TRIM_H + BLEED)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(out_path), pagesize=(page_w * inch, page_h * inch))

    # --- 1. Solid background ------------------------------------------
    c.setFillColor(BG_COLOR)
    c.rect(0, 0, page_w * inch, page_h * inch, fill=1, stroke=0)

    # Region origins (x in inches, measured from left of the cover sheet).
    back_x = BLEED                                  # back cover starts after left bleed
    spine_x = BLEED + TRIM_W                        # spine starts after back cover
    front_x = BLEED + TRIM_W + spine                # front cover starts after spine

    # --- 2. Front-cover artwork ---------------------------------------
    # The front-cover image bleeds off the top, bottom, and outside
    # (right) edges, but is flush to the spine on the inside.
    front_region_w = TRIM_W + BLEED   # includes outer bleed
    front_region_h = TRIM_H + 2 * BLEED
    art = Image.open(FRONT_ART)
    art_cropped = cover_aspect_crop(art, front_region_w, front_region_h)
    c.drawImage(
        pil_to_reader(art_cropped),
        front_x * inch, 0,
        front_region_w * inch, front_region_h * inch,
        mask=None,
    )

    # --- 3. Spine ------------------------------------------------------
    # Spine is purely text + small mascot icon at the top. Content is
    # constrained to the spine width minus a 1/16" fold-safety margin
    # on each side. Text runs rotated 90° (reads top-to-bottom on the
    # shelf, which is the standard direction for English titles).
    spine_inner_x = spine_x + SPINE_SAFE
    spine_inner_w = spine - 2 * SPINE_SAFE

    # 3a. Round mascot at the top of the spine.
    icon = Image.open(DOCS_ICON)
    # Size: square that fits the spine inner width.
    icon_size = spine_inner_w        # in inches
    icon_x = spine_inner_x
    icon_y = (BLEED + TRIM_H + BLEED) - (BLEED + 0.35 + icon_size)
    # (Place ~0.35" below the top trim, inside the safe area.)
    c.drawImage(
        pil_to_reader(icon),
        icon_x * inch, icon_y * inch,
        icon_size * inch, icon_size * inch,
        mask="auto",
    )

    # 3b. Title "VimFu" — large, rotated 90° clockwise so it reads
    # top-to-bottom when the book is shelved spine-up.
    c.saveState()
    title_y_top = icon_y - 0.4    # start of title block below the icon
    # Rotation pivot: somewhere in the spine. Rotated text origin is
    # the baseline. We translate to the start point and rotate -90°
    # (text now reads downward as we move along its new x-axis).
    title_size = max(20, int(spine_inner_w * inch * 0.55))
    c.setFillColor(TEXT_COLOR)
    c.setFont("Helvetica-Bold", title_size)
    # Place the title baseline along the spine's centerline.
    title_baseline_x = (spine_x + spine / 2) * inch + title_size * 0.35
    title_top_y = title_y_top * inch
    c.translate(title_baseline_x, title_top_y)
    c.rotate(-90)
    c.drawString(0, 0, "VimFu")
    c.restoreState()

    # 3c. Author name — smaller, lower on the spine.
    c.saveState()
    author_size = max(10, int(spine_inner_w * inch * 0.22))
    c.setFillColor(TEXT_COLOR)
    c.setFont("Helvetica", author_size)
    author_baseline_x = (spine_x + spine / 2) * inch + author_size * 0.35
    author_top_y = (BLEED + 1.5) * inch       # ~1.5" up from bottom trim
    c.translate(author_baseline_x, author_top_y)
    c.rotate(-90)
    c.drawString(0, 0, "Ashley Feniello")
    c.restoreState()

    # --- 4. Back cover -------------------------------------------------
    # Critical content lives inside SAFE from the trim edges. The trim
    # on the back cover runs from x = BLEED (outer) to x = BLEED + TRIM_W
    # (spine fold). So the safe rect is:
    safe_left = back_x + SAFE
    safe_right = back_x + TRIM_W - SAFE
    safe_bottom = BLEED + SAFE
    safe_top = BLEED + TRIM_H - SAFE
    safe_w = safe_right - safe_left

    # 4a. Author photo (top-left of back cover, square).
    photo_size = 1.5  # inches
    photo_x = safe_left
    photo_y = safe_top - photo_size
    photo = Image.open(AUTHOR_PHOTO)
    photo_sq = cover_aspect_crop(photo, 1, 1)
    c.drawImage(
        pil_to_reader(photo_sq),
        photo_x * inch, photo_y * inch,
        photo_size * inch, photo_size * inch,
        mask=None,
    )

    # 4b. Author bio text (top-right of photo, same vertical band).
    bio_text = read_md_body(AUTHOR_BIO_MD)
    bio_x = (photo_x + photo_size + 0.2) * inch
    bio_w = (safe_right - photo_x - photo_size - 0.2) * inch
    bio_h = photo_size * inch
    bio_style = ParagraphStyle(
        "bio", fontName="Helvetica", fontSize=10, leading=12.5,
        textColor=TEXT_COLOR, alignment=TA_LEFT,
    )
    draw_paragraph(c, bio_text, bio_x, photo_y * inch, bio_w, bio_h, bio_style)

    # 4c. Back-cover blurb (below the photo, full safe width).
    blurb_text = read_md_body(BACK_COVER_MD)
    # First sentence as the hook — render as a heading-ish line.
    first_line, _, rest = blurb_text.partition("\n")
    blurb_top = photo_y - 0.4   # 0.4" gap below photo, in inches
    blurb_bottom = safe_bottom + 1.2  # leave ~1.2" at bottom for ISBN/barcode area
    blurb_h = (blurb_top - blurb_bottom) * inch

    heading_style = ParagraphStyle(
        "heading", fontName="Helvetica-Bold", fontSize=12.5, leading=15,
        textColor=TEXT_COLOR, alignment=TA_LEFT,
        spaceAfter=10,
    )
    body_style = ParagraphStyle(
        "blurb", fontName="Helvetica", fontSize=10.2, leading=13.2,
        textColor=TEXT_COLOR, alignment=TA_LEFT,
        spaceAfter=9,
    )
    paragraphs = [Paragraph(first_line.strip(), heading_style)]
    for chunk in rest.split("\n\n"):
        chunk = chunk.replace("\n", " ").strip()
        if chunk:
            paragraphs.append(Paragraph(chunk, body_style))
    frame = Frame(
        safe_left * inch, blurb_bottom * inch,
        safe_w * inch, blurb_h,
        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
        showBoundary=0,
    )
    frame.addFromList(paragraphs, c)

    # 4d. URL footer at the bottom-left of the safe area, so a reader
    # always sees where the companion site lives even before opening
    # the book. The barcode area sits in the bottom-right (KDP adds the
    # actual barcode automatically when uploaded).
    c.setFillColor(TEXT_COLOR)
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(safe_left * inch, (safe_bottom + 0.15) * inch,
                 "vimfubook.com")

    c.showPage()
    c.save()
    print(f"  ✓ {out_path}")
    print(f"    pages={pages}  spine={spine:.4f}\"  "
          f"sheet={page_w:.4f}\" × {page_h:.4f}\"")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pages", type=int, default=421,
                    help="interior page count (drives spine width)")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT,
                    help="output PDF path")
    args = ap.parse_args()
    build_cover(args.pages, args.out)


if __name__ == "__main__":
    main()
