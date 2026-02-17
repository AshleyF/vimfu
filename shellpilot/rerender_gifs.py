#!/usr/bin/env python3
"""Re-render GIFs from existing .frames.json files at a new resolution.

Unlike gen_all_gifs.py --force, this does NOT re-capture frames.
It only re-renders the GIF from the already-captured .frames.json.

Usage:
    python rerender_gifs.py                 # all lessons with frames
    python rerender_gifs.py 42             # just lesson 42
    python rerender_gifs.py 10-20          # lessons 10 through 20
    python rerender_gifs.py --font-size 48 # custom font size (default: 48)
"""

from __future__ import annotations
import argparse, json, sys, time
from pathlib import Path

# Ensure CWD is shellpilot/
import os
os.chdir(Path(__file__).resolve().parent)

VIDEOS_DIR = Path("videos")


def find_frames_jsons(spec: str | None) -> list[Path]:
    """Find all .frames.json files, optionally filtered by lesson range."""
    all_frames = sorted(VIDEOS_DIR.glob("*/*.frames.json"))
    if spec is None:
        return all_frames
    if "-" in spec:
        lo, hi = spec.split("-", 1)
        lo, hi = int(lo), int(hi)
    else:
        lo = hi = int(spec)
    return [p for p in all_frames if lo <= int(p.parent.name[:4]) <= hi]


def main():
    parser = argparse.ArgumentParser(
        description="Re-render GIFs from existing .frames.json at higher resolution."
    )
    parser.add_argument("range", nargs="?", default=None,
                        help="Lesson number or range, e.g. '42' or '10-20'")
    parser.add_argument("--font-size", type=int, default=48,
                        help="Font size in pixels (default: 48)")
    parser.add_argument("--speed", type=float, default=2.0,
                        help="Speed multiplier (default: 2.0)")
    args = parser.parse_args()

    from gif_maker import make_gif

    frames_files = find_frames_jsons(args.range)
    if not frames_files:
        print("No .frames.json files found.")
        sys.exit(1)

    print(f"=== Re-rendering {len(frames_files)} GIF(s) at font_size={args.font_size} ===\n")

    ok = 0
    fail = 0
    for i, fp in enumerate(frames_files, 1):
        slug = fp.parent.name
        gif_path = fp.with_suffix(".gif")
        print(f"[{i}/{len(frames_files)}] {slug}")

        try:
            doc = json.loads(fp.read_text(encoding="utf-8"))
            t0 = time.time()
            make_gif(doc, gif_path, speed=args.speed, font_size=args.font_size,
                     show_keys=False)
            dt = time.time() - t0
            size_kb = gif_path.stat().st_size / 1024
            print(f"    OK ({size_kb:.0f} KB, {dt:.1f}s)")
            ok += 1
        except KeyboardInterrupt:
            print(f"    INTERRUPTED — skipping")
            fail += 1
            continue
        except Exception as exc:
            print(f"    FAIL: {exc}")
            fail += 1

    print(f"\n=== Done: {ok} succeeded, {fail} failed ===")


if __name__ == "__main__":
    main()
