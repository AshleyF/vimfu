#!/usr/bin/env python3
"""Batch-generate animated GIFs for all short lessons.

Two-stage pipeline per lesson:
  1. capture_frames.py  → .frames.json  (headless ConPTY + pyte replay)
  2. gif_maker.py        → .gif          (Pillow render)

Usage:
    python gen_all_gifs.py                  # all 85 lessons
    python gen_all_gifs.py 42              # just lesson 42
    python gen_all_gifs.py 10-20           # lessons 10 through 20
    python gen_all_gifs.py --force          # regenerate even if output exists
"""

from __future__ import annotations
import argparse, json, os, sys, time, traceback
from pathlib import Path

# Ensure CWD is shellpilot/ so relative imports and video paths work
os.chdir(Path(__file__).resolve().parent)

SHORTS_DIR = Path(__file__).resolve().parent.parent / "curriculum" / "shorts"
LOG_FILE = Path(__file__).resolve().parent.parent / "gen_all_gifs_output.txt"
SPEED = 2.0

def log(msg: str):
    """Print and append to log file."""
    print(msg, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
FRAME_MS = 600
FONT_SIZE = 48


def all_lessons() -> list[Path]:
    """Return sorted list of lesson JSON paths."""
    return sorted(SHORTS_DIR.glob("*.json"))


def parse_range(spec: str | None, lessons: list[Path]) -> list[Path]:
    """Filter lessons by number or range spec like '42' or '10-20'."""
    if spec is None:
        return lessons
    if "-" in spec:
        lo, hi = spec.split("-", 1)
        lo, hi = int(lo), int(hi)
    else:
        lo = hi = int(spec)
    return [p for p in lessons if lo <= int(p.stem[:4]) <= hi]


def process(lesson_json: Path, *, force: bool = False) -> dict:
    """Capture frames and render GIF for one lesson.  Returns status dict."""
    from capture_frames import capture_lesson
    from gif_maker import make_gif

    title = lesson_json.stem
    num = title[:4]
    video_dir = Path("videos") / title
    frames_path = video_dir / f"{title}.frames.json"
    gif_path = video_dir / f"{title}.frames.gif"

    result = {"lesson": num, "title": title}

    # --- Stage 1: Capture frames ---
    if frames_path.exists() and not force:
        doc = json.loads(frames_path.read_text(encoding="utf-8"))
        n_frames = len(doc.get("frames", []))
        result["capture"] = f"skipped ({n_frames} frames exist)"
    else:
        try:
            t0 = time.time()
            capture_lesson(lesson_json, output=frames_path)
            dt = time.time() - t0
            doc = json.loads(frames_path.read_text(encoding="utf-8"))
            n_frames = len(doc.get("frames", []))
            result["capture"] = f"OK ({n_frames} frames, {dt:.1f}s)"
        except Exception:
            result["capture"] = f"FAIL: {traceback.format_exc().splitlines()[-1]}"
            result["gif"] = "skipped (no frames)"
            return result

    # --- Stage 2: Render GIF ---
    if gif_path.exists() and not force:
        size_kb = gif_path.stat().st_size / 1024
        result["gif"] = f"skipped ({size_kb:.0f} KB exists)"
    else:
        try:
            t0 = time.time()
            make_gif(doc, gif_path, speed=SPEED, frame_ms=FRAME_MS,
                     font_size=FONT_SIZE, show_keys=False)
            dt = time.time() - t0
            size_kb = gif_path.stat().st_size / 1024
            result["gif"] = f"OK ({size_kb:.0f} KB, {dt:.1f}s)"
        except Exception:
            result["gif"] = f"FAIL: {traceback.format_exc().splitlines()[-1]}"

    return result


def main():
    parser = argparse.ArgumentParser(description="Batch-generate GIFs for VimFu shorts.")
    parser.add_argument("range", nargs="?", default=None,
                        help="Lesson number or range, e.g. '42' or '10-20'")
    parser.add_argument("--force", "-f", action="store_true",
                        help="Regenerate even if output already exists")
    args = parser.parse_args()

    lessons = parse_range(args.range, all_lessons())
    if not lessons:
        log("No lessons matched.")
        sys.exit(1)

    # Clear log file
    LOG_FILE.write_text("", encoding="utf-8")

    log(f"=== Generating GIFs for {len(lessons)} lesson(s) ===")
    log("")

    results = []
    for i, lp in enumerate(lessons, 1):
        num = lp.stem[:4]
        log(f"[{i}/{len(lessons)}] {lp.stem}")
        try:
            r = process(lp, force=args.force)
        except KeyboardInterrupt:
            log(f"    INTERRUPTED")
            r = {"lesson": num, "title": lp.stem,
                 "capture": "FAIL: KeyboardInterrupt",
                 "gif": "skipped"}
        results.append(r)
        log(f"    capture: {r['capture']}")
        log(f"    gif:     {r['gif']}")
        log("")

    # --- Summary ---
    ok = sum(1 for r in results if "OK" in r.get("gif", "")
             or "skipped" in r.get("gif", ""))
    fail = sum(1 for r in results if "FAIL" in r.get("capture", "")
               or "FAIL" in r.get("gif", ""))
    log(f"=== Done: {ok} succeeded, {fail} failed ===")

    if fail:
        log("\nFailures:")
        for r in results:
            if "FAIL" in r.get("capture", "") or "FAIL" in r.get("gif", ""):
                log(f"  {r['lesson']}: capture={r['capture']}  gif={r['gif']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
