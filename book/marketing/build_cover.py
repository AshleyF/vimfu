"""Build a print-ready KDP paperback cover PDF for VimFu.

Generates a single-page wrap-around cover (back + spine + front) sized
to KDP's specs for a 7.5×9.25 paperback on white paper, with 0.125"
bleed on all outside edges. The spine width is computed from the page
count.

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
from reportlab.lib.colors import Color, black, white
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Frame, Paragraph

ROOT = Path(__file__).resolve().parent
FONT_DIR = ROOT / "fonts"
DOCS_ICON = ROOT.parent.parent / "docs" / "icon.png"
FRONT_ART = ROOT / "VimFu Cover.png"
AUTHOR_PHOTO = ROOT / "me2.JPG"
BACK_WISP = ROOT / "whisp.png"
BACK_COVER_MD = ROOT / "back_cover.md"
AUTHOR_BIO_MD = ROOT / "author_bio.md"
DEFAULT_OUT = ROOT / "output" / "vimfu-cover.pdf"

# --- KDP specs (inches) -------------------------------------------------
TRIM_W = 7.5
TRIM_H = 9.25
BLEED = 0.125
# KDP's official safe-area inset from the trim edge for this trim size
# (per the cover calculator): 0.0625" horizontal, 0.125" vertical. Any
# text or critical artwork must stay inside this.
KDP_SAFE_H = 0.0625
KDP_SAFE_V = 0.125
# Spine safety: keep critical content this far from the fold on each
# side (KDP value for this trim/page count).
SPINE_SAFE = 0.0625
# How far the front-cover art is inset from the trim. Just enough to
# guarantee we never bleed — slightly larger than KDP's minimum so a
# minor mis-cut won't crop into the art.
ART_INSET = 0.0625
# Back-cover text inset from trim. Tighter than the previous 0.4" so
# we use more of the 7.5"-wide trim, but still comfortably outside
# KDP's safe-area minimum.
BACK_SAFE_H = 0.375
BACK_SAFE_V = 0.4
# White paper, B&W interior: 0.002252" per page.
SPINE_PER_PAGE = 0.002252

# --- Visual style -------------------------------------------------------
BG_COLOR = black  # match the solid black in the cover artwork
TEXT_COLOR = white

# Fonts — Ubuntu, matching the original book/cover branding.
FONT_REG = "Ubuntu"
FONT_BOLD = "Ubuntu-Bold"
FONT_ITAL = "Ubuntu-Italic"


def register_fonts() -> None:
    pdfmetrics.registerFont(TTFont(FONT_REG, str(FONT_DIR / "Ubuntu-Regular.ttf")))
    pdfmetrics.registerFont(TTFont(FONT_BOLD, str(FONT_DIR / "Ubuntu-Bold.ttf")))
    pdfmetrics.registerFont(TTFont(FONT_ITAL, str(FONT_DIR / "Ubuntu-Italic.ttf")))


def spine_inches(pages: int) -> float:
    """KDP spine-width formula for white paper, B&W interior."""
    return pages * SPINE_PER_PAGE


def read_md_body(path: Path) -> str:
    """Strip the leading ``# Heading`` and return body paragraphs joined."""
    lines = path.read_text(encoding="utf-8").splitlines()
    body = [ln for ln in lines if not ln.startswith("#")]
    # Join non-empty groups with blank-line separators preserved.
    return "\n".join(body).strip()


def make_qr_image(text: str) -> Image.Image:
    """Render ``text`` as a black-on-white PIL QR code with a small quiet zone."""
    import qrcode
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(text)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white").convert("RGB")


def trim_black_border(img: Image.Image, threshold: int = 16) -> Image.Image:
    """Strip uniform near-black borders from the four edges of ``img``.

    The VimFu front-cover PNG has a ~3-5% solid-black margin baked in
    around the actual art. We don't want that margin to compound with
    the cover background, so we detect it (rows/columns where every
    pixel has max channel < ``threshold``) and crop it away.
    """
    import numpy as np
    rgb = img.convert("RGB")
    a = np.asarray(rgb)
    is_black = a.max(axis=2) < threshold
    h, w = is_black.shape
    top = 0
    while top < h and is_black[top].all():
        top += 1
    bottom = h - 1
    while bottom >= 0 and is_black[bottom].all():
        bottom -= 1
    left = 0
    while left < w and is_black[:, left].all():
        left += 1
    right = w - 1
    while right >= 0 and is_black[:, right].all():
        right -= 1
    if top == 0 and bottom == h - 1 and left == 0 and right == w - 1:
        return img
    return img.crop((left, top, right + 1, bottom + 1))


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
    register_fonts()
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
    # Source PNG has ~4-5% solid-black borders baked in around its
    # content. We auto-trim those before fitting so the actual painted
    # art reaches the trim instead of sitting on a double black margin.
    # The art is then uniformly scaled to fit inside the trim and
    # centered. (Background black behind it provides any remaining
    # margin for a clean look without bleeding off the page.)
    front_trim_left = BLEED + TRIM_W + spine
    front_trim_bottom = BLEED
    front_avail_w = TRIM_W - 2 * ART_INSET
    front_avail_h = TRIM_H - 2 * ART_INSET
    art = trim_black_border(Image.open(FRONT_ART))
    art_ratio = art.width / art.height
    if art_ratio > front_avail_w / front_avail_h:
        draw_w = front_avail_w
        draw_h = front_avail_w / art_ratio
    else:
        draw_h = front_avail_h
        draw_w = front_avail_h * art_ratio
    art_x = front_trim_left + (TRIM_W - draw_w) / 2
    art_y = front_trim_bottom + (TRIM_H - draw_h) / 2
    c.drawImage(
        pil_to_reader(art),
        art_x * inch, art_y * inch,
        draw_w * inch, draw_h * inch,
        mask=None,
    )

    # --- 3. Spine ------------------------------------------------------
    # Spine content: mascot icon at top, "VimFu" centered along the
    # spine's length, author name below. Text is rotated -90° so it
    # reads top-to-bottom on the shelf.
    spine_inner_x = spine_x + SPINE_SAFE
    spine_inner_w = spine - 2 * SPINE_SAFE
    spine_center_x_in = spine_x + spine / 2   # spine horizontal centerline (in inches)
    spine_top_in = BLEED + TRIM_H + BLEED     # top edge of cover sheet
    spine_bottom_in = BLEED                   # bottom edge of trim

    # 3a. Round mascot at the top of the spine.
    icon = Image.open(DOCS_ICON)
    icon_size = spine_inner_w        # in inches, fits the spine width
    icon_x = spine_inner_x
    icon_y = spine_top_in - BLEED - 0.35 - icon_size
    c.drawImage(
        pil_to_reader(icon),
        icon_x * inch, icon_y * inch,
        icon_size * inch, icon_size * inch,
        mask="auto",
    )

    def draw_rotated_centered(text: str, font: str, size_pt: float,
                              center_y_in: float, color=TEXT_COLOR) -> None:
        """Draw rotated (reads top-to-bottom) text centered both on the
        spine's horizontal centerline and on a target y (inches from the
        bottom of the sheet, in user space).
        """
        c.saveState()
        c.setFillColor(color)
        c.setFont(font, size_pt)
        text_w_pt = c.stringWidth(text, font, size_pt)
        # After rotate(-90), the text's height (cap + descender) lies
        # along user +x and its width lies along user -y. To center the
        # visible glyphs horizontally on the spine centerline we offset
        # the baseline back by ~0.36 * size (cap-half).
        baseline_x_pt = spine_center_x_in * inch - size_pt * 0.36
        # To center the text's length on a target y, start the baseline
        # half-width above it (text grows downward from baseline).
        baseline_y_pt = center_y_in * inch + text_w_pt / 2
        c.translate(baseline_x_pt, baseline_y_pt)
        c.rotate(-90)
        c.drawString(0, 0, text)
        c.restoreState()

    # 3b. Title "VimFu" — large, taking ~75% of the spine width, centered
    # both horizontally between the folds and vertically along the spine.
    # Ubuntu Bold cap-height ≈ 0.72 × font size, so a size of ~1.0 × the
    # spine inner width (in pt) lands the cap-height near 75%.
    title_size = spine_inner_w * inch * 1.05
    title_center_y = spine_bottom_in + (TRIM_H + 2 * BLEED) / 2 + 0.4
    draw_rotated_centered("VimFu", FONT_BOLD, title_size, title_center_y)

    # 3c. Author name — sits below the title, near the bottom. Rendered
    # slightly muted (warm grey) so it doesn't compete with the title.
    author_size = max(10, int(spine_inner_w * inch * 0.22))
    draw_rotated_centered("Ashley Feniello", FONT_REG, author_size,
                          spine_bottom_in + 1.8,
                          color=Color(0.45, 0.45, 0.45))

    # --- 4. Back cover -------------------------------------------------
    # Critical content lives inside BACK_SAFE from the trim edges. The
    # back-cover trim runs from x = BLEED (outer) to x = BLEED + TRIM_W
    # (spine fold).
    safe_left = back_x + BACK_SAFE_H
    safe_right = back_x + TRIM_W - BACK_SAFE_H
    safe_bottom = BLEED + BACK_SAFE_V
    safe_top = BLEED + TRIM_H - BACK_SAFE_V
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
        "bio", fontName=FONT_REG, fontSize=13.5, leading=17,
        textColor=TEXT_COLOR, alignment=TA_LEFT,
    )
    draw_paragraph(c, bio_text, bio_x, photo_y * inch, bio_w, bio_h, bio_style)

    # 4c. Back-cover blurb (below the photo). We reserve a taller bottom
    # band (~2.5") so the wisp flourish + QR/URL row + KDP-auto barcode
    # all have room without crowding.
    blurb_text = read_md_body(BACK_COVER_MD)
    first_line, _, rest = blurb_text.partition("\n")
    blurb_top = photo_y - 0.4
    blurb_bottom = safe_bottom + 2.5
    blurb_h = (blurb_top - blurb_bottom) * inch

    heading_style = ParagraphStyle(
        "heading", fontName=FONT_BOLD, fontSize=16.5, leading=20,
        textColor=TEXT_COLOR, alignment=TA_LEFT,
        spaceAfter=13,
    )
    body_style = ParagraphStyle(
        "blurb", fontName=FONT_REG, fontSize=14, leading=18,
        textColor=TEXT_COLOR, alignment=TA_LEFT,
        spaceAfter=12,
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

    # 4d. Decorative wisp between the blurb and the QR/URL/barcode row.
    # Echoes the colored flourishes on the front cover, tying the two
    # sides together visually. The PNG is already on solid black so it
    # blends seamlessly into the cover background.
    qr_size_in = 0.75
    qr_x = safe_left
    qr_y = safe_bottom + 0.15
    wisp_top = blurb_bottom - 0.1
    wisp_bottom = qr_y + qr_size_in + 0.15
    wisp_band_h = wisp_top - wisp_bottom
    wisp = Image.open(BACK_WISP)
    wisp_ratio = wisp.width / wisp.height
    # Fit inside the band, leaving the bottom-right barcode zone alone.
    barcode_reserve_w = 2.2   # KDP barcode reserve (bottom-right of back)
    max_w = safe_w   # wisp can span full safe width since it's centered
    if max_w / wisp_band_h >= wisp_ratio:
        wisp_h_in = wisp_band_h
        wisp_w_in = wisp_h_in * wisp_ratio
    else:
        wisp_w_in = max_w
        wisp_h_in = wisp_w_in / wisp_ratio
    # Pull the wisp slightly left of center so its decorative core sits
    # over the empty area rather than overlapping the (right-aligned)
    # KDP barcode zone below it.
    wisp_x = safe_left + (safe_w - wisp_w_in) / 2 - 0.3
    wisp_y = wisp_bottom + (wisp_band_h - wisp_h_in) / 2
    c.drawImage(
        pil_to_reader(wisp),
        wisp_x * inch, wisp_y * inch,
        wisp_w_in * inch, wisp_h_in * inch,
        mask=None,
    )

    # 4e. URL footer + small QR code at the bottom-left of the safe
    # area. The QR encodes the same URL so a phone scan jumps straight
    # to the companion site. KDP auto-stamps its barcode at the
    # bottom-right at print time, so we keep that quadrant empty.
    qr_img = make_qr_image("https://vimfubook.com")
    c.drawImage(
        pil_to_reader(qr_img),
        qr_x * inch, qr_y * inch,
        qr_size_in * inch, qr_size_in * inch,
        mask=None,
    )
    c.setFillColor(TEXT_COLOR)
    c.setFont(FONT_ITAL, 13)
    # Baseline aligned roughly with the vertical center of the QR.
    c.drawString((qr_x + qr_size_in + 0.18) * inch,
                 (qr_y + qr_size_in / 2 - 0.07) * inch,
                 "vimfubook.com")

    c.showPage()
    c.save()
    print(f"  ✓ {out_path}")
    print(f"    pages={pages}  spine={spine:.4f}\"  "
          f"sheet={page_w:.4f}\" × {page_h:.4f}\"")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pages", type=int, default=420,
                    help="interior page count (drives spine width)")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT,
                    help="output PDF path")
    args = ap.parse_args()
    build_cover(args.pages, args.out)


if __name__ == "__main__":
    main()
