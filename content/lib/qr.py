"""
QR-code SVG generator for VimFu topics.

Renderers ask for ``topic_qr_svg(topic_id)``; the result is a small,
self-contained SVG (vector — scales for any output: web, book, foldable
pamphlet, the side of a building) encoding the public site URL for that
topic on https://vimfubook.com.

URL scheme: ``{base}/{part_dir}/{file_stem}`` to mirror the on-disk
HTML output. The QR encodes that exact URL so a phone scan deep-links
into the website section corresponding to the page in the printed book.
"""

from __future__ import annotations

import io
from typing import Any

import qrcode
from qrcode.image.svg import SvgPathImage

DEFAULT_BASE_URL = "https://vimfubook.com"


def topic_url(topic: dict[str, Any], base_url: str = DEFAULT_BASE_URL) -> str:
    part = topic.get("__part_dir") or topic.get("part_dir") or ""
    stem = topic.get("__file_stem") or topic.get("file_stem") or ""
    if part and stem:
        return f"{base_url}/{part}/{stem}"
    tid = topic.get("id", "")
    return f"{base_url}/t/{tid}" if tid else base_url


def qr_svg(text: str, *, box_size: int = 8, border: int = 2) -> str:
    """Return a self-contained SVG string encoding ``text``.

    Path-based for compactness; one ``<path d="...">`` per QR code.
    """
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=box_size,
        border=border,
    )
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(image_factory=SvgPathImage)
    buf = io.BytesIO()
    img.save(buf)
    svg = buf.getvalue().decode("utf-8")
    # qrcode emits a fixed-size SVG by default; widen viewBox handling so the
    # consumer can size it freely via CSS / [width] attribute.
    return svg


def topic_qr_svg(topic: dict[str, Any], base_url: str = DEFAULT_BASE_URL,
                 **kw: Any) -> tuple[str, str]:
    """Return (url, svg_string) for the topic's site page."""
    url = topic_url(topic, base_url=base_url)
    return url, qr_svg(url, **kw)


if __name__ == "__main__":
    url = "https://vimfubook.com/03-basic-editing/05-delete"
    print(qr_svg(url)[:400], "...")
