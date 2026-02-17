"""
Generate animated GIF from a VimFu frames JSON file.

Reads the frames JSON produced by ``capture_frames.py`` and renders
an animated GIF with proper syntax-highlighting colors.

Usage:
    python gif_maker.py videos/0085_the_vim_grammar/0085_the_vim_grammar.frames.json
    python gif_maker.py frames.json --speed 3 --output demo.gif
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


# ---------------------------------------------------------------------------
# Font helpers
# ---------------------------------------------------------------------------

def find_font(size: int) -> ImageFont.FreeTypeFont:
    """Find a monospace font on the system."""
    candidates = [
        "C:/Windows/Fonts/consola.ttf",       # Consolas (Windows)
        "C:/Windows/Fonts/CascadiaMono.ttf",   # Cascadia Mono (Windows)
        "C:/Windows/Fonts/cour.ttf",           # Courier New (Windows)
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/System/Library/Fonts/Menlo.ttc",
    ]
    for p in candidates:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def hex_to_rgb(h: str) -> tuple[int, int, int]:
    """``"d4d4d4"`` → ``(212, 212, 212)``."""
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


# ---------------------------------------------------------------------------
# Frame renderer
# ---------------------------------------------------------------------------

CURSOR_BG = hex_to_rgb("800000")
CURSOR_FG = hex_to_rgb("ffffff")


def render_frame(frame: dict, font: ImageFont.FreeTypeFont,
                 char_w: int, char_h: int,
                 padding: int = 8) -> Image.Image:
    """Render a single Frame dict to a PIL Image."""
    rows = frame["rows"]
    cols = frame["cols"]
    default_bg = hex_to_rgb(frame.get("defaultBg", "000000"))
    bg_color = default_bg

    img_w = padding * 2 + cols * char_w
    img_h = padding * 2 + rows * char_h
    img = Image.new("RGB", (img_w, img_h), bg_color)
    draw = ImageDraw.Draw(img)

    cursor = frame.get("cursor", {})
    cur_row = cursor.get("row", -1)
    cur_col = cursor.get("col", -1)
    cur_vis = cursor.get("visible", True)

    for row_idx, line_obj in enumerate(frame["lines"]):
        text = line_obj["text"]
        runs = line_obj.get("runs", [])
        y = padding + row_idx * char_h

        # Build per-column color arrays from runs
        col = 0
        for run in runs:
            n = run["n"]
            fg = hex_to_rgb(run["fg"])
            bg = hex_to_rgb(run["bg"])

            for j in range(n):
                c = col + j
                if c >= cols:
                    break

                x = padding + c * char_w
                cell_fg = fg
                cell_bg = bg

                # Cursor override
                if cur_vis and row_idx == cur_row and c == cur_col:
                    cell_bg = CURSOR_BG
                    cell_fg = CURSOR_FG

                # Draw background if non-default
                if cell_bg != bg_color:
                    draw.rectangle(
                        [x, y, x + char_w, y + char_h],
                        fill=cell_bg,
                    )

                # Draw character
                ch = text[c] if c < len(text) else " "
                if ch != " ":
                    draw.text((x, y), ch, font=font, fill=cell_fg)

            col += n

    return img


# ---------------------------------------------------------------------------
# Key overlay renderer
# ---------------------------------------------------------------------------

# Overlay colors (matches viewer.py)
KEY_BG = (90, 26, 26)       # #5a1a1a — deep red pill
KEY_FG = (255, 255, 255)     # white key text
CAPTION_FG = (200, 200, 200) # light gray caption


def _draw_key_overlay(img: Image.Image, frame: dict,
                      key_font: ImageFont.FreeTypeFont,
                      caption_font: ImageFont.FreeTypeFont,
                      padding: int) -> None:
    """Draw a key overlay pill at the bottom-center of the image."""
    action = frame.get("action", {})
    key_text = action.get("keyOverlay", "")
    if not key_text:
        return

    caption = action.get("keyCaption", "")
    draw = ImageDraw.Draw(img)
    img_w, img_h = img.size

    # Measure key text
    key_bbox = key_font.getbbox(key_text)
    key_w = key_bbox[2] - key_bbox[0]
    key_h = key_bbox[3] - key_bbox[1]

    # Measure caption
    cap_h = 0
    cap_w = 0
    if caption:
        cap_bbox = caption_font.getbbox(caption)
        cap_w = cap_bbox[2] - cap_bbox[0]
        cap_h = cap_bbox[3] - cap_bbox[1]

    # Pill dimensions
    h_pad = 14
    v_pad = 6
    gap = 4 if caption else 0
    pill_w = max(key_w, cap_w) + h_pad * 2
    pill_h = key_h + gap + cap_h + v_pad * 2

    # Position: centered horizontally, near the bottom
    pill_x = (img_w - pill_w) // 2
    pill_y = img_h - pill_h - padding - 4

    # Draw pill background with rounded corners
    radius = 8
    _rounded_rect(draw, pill_x, pill_y,
                  pill_x + pill_w, pill_y + pill_h,
                  radius, fill=KEY_BG)

    # Draw key text centered in pill
    key_x = pill_x + (pill_w - key_w) // 2
    key_y = pill_y + v_pad
    draw.text((key_x, key_y), key_text, font=key_font, fill=KEY_FG)

    # Draw caption below key text
    if caption:
        cap_x = pill_x + (pill_w - cap_w) // 2
        cap_y = key_y + key_h + gap
        draw.text((cap_x, cap_y), caption, font=caption_font, fill=CAPTION_FG)


def _rounded_rect(draw: ImageDraw.ImageDraw,
                  x1: int, y1: int, x2: int, y2: int,
                  r: int, fill) -> None:
    """Draw a filled rounded rectangle."""
    draw.rectangle([x1 + r, y1, x2 - r, y2], fill=fill)
    draw.rectangle([x1, y1 + r, x2, y2 - r], fill=fill)
    draw.pieslice([x1, y1, x1 + 2*r, y1 + 2*r], 180, 270, fill=fill)
    draw.pieslice([x2 - 2*r, y1, x2, y1 + 2*r], 270, 360, fill=fill)
    draw.pieslice([x1, y2 - 2*r, x1 + 2*r, y2], 90, 180, fill=fill)
    draw.pieslice([x2 - 2*r, y2 - 2*r, x2, y2], 0, 90, fill=fill)


# ---------------------------------------------------------------------------
# GIF assembler
# ---------------------------------------------------------------------------

def make_gif(frames_doc: dict, output: Path, *,
             speed: float = 2.0,
             frame_ms: int = 600,
             first_ms: int = 1200,
             last_ms: int = 1500,
             font_size: int = 16,
             padding: int = 8,
             show_keys: bool = False) -> None:
    """Render all frames and assemble into an animated GIF."""
    frames = frames_doc["frames"]
    if not frames:
        print("No frames to render.")
        return

    font = find_font(font_size)
    bbox = font.getbbox("M")
    char_w = bbox[2] - bbox[0]
    char_h = int((bbox[3] - bbox[1]) * 1.6)

    # Prepare overlay font (larger, for the key pill)
    overlay_font = find_font(font_size * 2) if show_keys else None
    caption_font = find_font(int(font_size * 1.1)) if show_keys else None

    rows = frames_doc["rows"]
    cols = frames_doc["cols"]
    flags = "  keys" if show_keys else ""
    print(f"Terminal: {cols}x{rows}  |  Font: {font_size}px ({char_w}x{char_h}){flags}")
    print(f"Frames: {len(frames)}  |  Speed: {speed}x")

    # Render each frame to an image
    images: list[Image.Image] = []
    for i, frame in enumerate(frames):
        # Inject top-level defaults into each frame for the renderer
        frame.setdefault("defaultBg", frames_doc.get("defaultBg", "000000"))
        frame.setdefault("defaultFg", frames_doc.get("defaultFg", "d4d4d4"))
        img = render_frame(frame, font, char_w, char_h, padding)
        if show_keys:
            _draw_key_overlay(img, frame, overlay_font, caption_font, padding)
        images.append(img)
        sys.stdout.write(f"\rRendering {i+1}/{len(frames)}...")
        sys.stdout.flush()
    print(" done.")

    # Per-frame durations
    durations: list[int] = []
    for i in range(len(images)):
        if i == 0:
            ms = first_ms
        elif i == len(images) - 1:
            ms = last_ms
        else:
            ms = frame_ms
        durations.append(max(int(ms / speed), 20))

    # Save
    images[0].save(
        str(output),
        save_all=True,
        append_images=images[1:],
        duration=durations,
        loop=0,
        optimize=True,
    )

    total_s = sum(durations) / 1000
    size_kb = output.stat().st_size / 1024
    print(f"Saved: {output}  ({size_kb:.0f} KB, {total_s:.1f}s, {len(images)} frames)")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate animated GIF from a VimFu frames JSON."
    )
    parser.add_argument("frames_json", type=Path,
                        help="Path to the .frames.json file")
    parser.add_argument("--output", "-o", type=Path, default=None,
                        help="Output GIF path (default: same dir, .gif)")
    parser.add_argument("--speed", "-s", type=float, default=2.0,
                        help="Speed multiplier (default: 2.0)")
    parser.add_argument("--frame-ms", type=int, default=600,
                        help="Base ms per frame (default: 600)")
    parser.add_argument("--font-size", type=int, default=16,
                        help="Font size in pixels (default: 16)")
    parser.add_argument("--keys", action="store_true", default=False,
                        help="Show key overlay on each frame")

    args = parser.parse_args()

    if not args.frames_json.exists():
        print(f"Error: {args.frames_json} not found")
        sys.exit(1)

    doc = json.loads(args.frames_json.read_text(encoding="utf-8"))

    out = args.output or args.frames_json.with_suffix(".gif")
    make_gif(doc, out, speed=args.speed, frame_ms=args.frame_ms,
             font_size=args.font_size, show_keys=args.keys)


if __name__ == "__main__":
    main()
