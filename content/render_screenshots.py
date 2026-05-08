"""Render worked examples to SVG screenshots.

Reads content/examples/*.json. For each example, produces:

  content/output/screenshots/<example-id>/
    meta.json
    frame_01.color.svg  frame_01.bw.svg
    frame_02.color.svg  frame_02.bw.svg
    ...

Frames may be supplied in any of three forms (resolved in this order):

  1. example["frames"][i]["frame"]          — full Frame JSON inline
  2. example["frames"][i]["compact"]        — compact-frame DSL inline
                                              (see lib/compact_frame.py)
  3. example["source"]["lesson"] +          — capture from a curriculum
     example["source"]["select"]              lesson via shellpilot.

Usage:
  python content/render_screenshots.py
  python content/render_screenshots.py grammar.dw-then-dot
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Make ./lib importable without a package install
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

from lib.svg import frame_to_svg
from lib.compact_frame import expand as expand_compact

ROOT = HERE.parent
EXAMPLES_DIR = HERE / "examples"
OUTPUT_DIR = HERE / "output" / "html" / "screenshots"


def resolve_frame(spec, *, captured_cache):
    """Return a Frame dict from a frame-entry spec."""
    if "frame" in spec:
        return spec["frame"]
    if "compact" in spec:
        return expand_compact(spec["compact"])
    raise ValueError(
        "Frame entry has no 'frame' or 'compact' key (and no source resolution wired): "
        + json.dumps(spec)[:200]
    )


def capture_lesson_frames(lesson_path: Path) -> list:
    """Replay a curriculum lesson via shellpilot and return its frames list.

    Cached on disk under content/output/screenshots/_captured/<stem>.json
    so we don't re-run pyte on every render.
    """
    cache_root = OUTPUT_DIR / "_captured"
    cache_root.mkdir(parents=True, exist_ok=True)
    cache_path = cache_root / f"{lesson_path.stem}.json"
    if cache_path.exists():
        return json.loads(cache_path.read_text("utf-8"))["frames"]

    # Lazy import — only needed if a captured-source example exists
    sp_dir = ROOT / "shellpilot"
    sys.path.insert(0, str(sp_dir))
    from capture_frames import capture_lesson  # type: ignore

    out = capture_lesson(lesson_path, output=cache_path)
    data = json.loads(Path(out).read_text("utf-8"))
    return data["frames"]


def render_example(example_path: Path) -> dict:
    ex = json.loads(example_path.read_text("utf-8"))
    ex_id = ex["id"]
    out_dir = OUTPUT_DIR / ex_id
    out_dir.mkdir(parents=True, exist_ok=True)

    source = ex.get("source") or {}
    captured = None
    if source.get("lesson"):
        lesson = ROOT / source["lesson"]
        if not lesson.exists():
            raise FileNotFoundError(f"Lesson not found: {lesson}")
        captured = capture_lesson_frames(lesson)

    select = source.get("select") or []
    frames_meta = []

    for i, fspec in enumerate(ex.get("frames", [])):
        # Determine the frame data
        if "frame" in fspec or "compact" in fspec:
            frame = resolve_frame(fspec, captured_cache=captured)
        elif captured is not None:
            if i >= len(select):
                raise ValueError(
                    f"{ex_id}: frame {i} has no inline data and no select index"
                )
            frame = captured[select[i]]
        else:
            raise ValueError(f"{ex_id}: frame {i} has no resolvable frame data")

        n = i + 1
        color_path = out_dir / f"frame_{n:02d}.color.svg"
        bw_path = out_dir / f"frame_{n:02d}.bw.svg"
        color_path.write_text(frame_to_svg(frame, theme="color"), encoding="utf-8")
        bw_path.write_text(frame_to_svg(frame, theme="bw"), encoding="utf-8")

        frames_meta.append({
            "n": n,
            "color": color_path.name,
            "bw": bw_path.name,
            "caption": fspec.get("caption", ""),
            "narration": fspec.get("narration", ""),
            "keys": fspec.get("keys", ""),
        })

    meta = {
        "id": ex_id,
        "title": ex.get("title", ex_id),
        "summary": ex.get("summary", ""),
        "topic": ex.get("topic"),
        "frames": frames_meta,
    }
    (out_dir / "meta.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8"
    )
    return meta


def main():
    targets = sys.argv[1:]
    if targets:
        files = []
        for t in targets:
            cand = EXAMPLES_DIR / f"{t}.json"
            if not cand.exists():
                cand = Path(t)
            if not cand.exists():
                print(f"  skip: {t} not found")
                continue
            files.append(cand)
    else:
        files = sorted(EXAMPLES_DIR.glob("*.json"))

    if not files:
        print(f"No examples found in {EXAMPLES_DIR}")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    total_frames = 0
    for f in files:
        try:
            meta = render_example(f)
            n = len(meta["frames"])
            total_frames += n
            print(f"  {meta['id']}: {n} frame(s)")
        except Exception as e:
            print(f"  ERROR {f.name}: {e}")

    print(f"Wrote {total_frames} frame(s) across {len(files)} example(s) -> {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
