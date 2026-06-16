"""
Video index for VimFu shorts.

Reads every ``curriculum/shorts/NNNN_slug.json`` and exposes a lookup keyed
by lesson number (the ``NNNN`` prefix). Topics in ``content/parts/**/*.json``
carry a ``"lessons": [N, ...]`` array; renderers use this module to resolve
those numbers into video metadata for embedding or linking.

Only shorts whose JSON contains ``youtube.videoId`` are considered "ready".
The rest are tracked as known-but-unpublished — renderers can decide how to
display them (placeholder, hide, etc.).
"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
SHORTS_DIR = REPO_ROOT / "curriculum" / "shorts"
LONGS_DIR = REPO_ROOT / "curriculum" / "longs"

_LESSON_RE = re.compile(r"^(\d{4})([a-z]*)_(.+)\.json$")


@lru_cache(maxsize=1)
def _index() -> dict:
    out: dict = {}
    for d in (SHORTS_DIR, LONGS_DIR):
        if not d.exists():
            continue
        for p in sorted(d.glob("*.json")):
            m = _LESSON_RE.match(p.name)
            if not m:
                continue
            num = int(m.group(1))
            suffix = m.group(2)
            slug = m.group(3)
            key = num if not suffix else f"{num:04d}{suffix}"
            display_id = f"{num:04d}{suffix}"
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                continue
            yt = data.get("youtube") or {}
            video_id = yt.get("videoId") or ""
            url = yt.get("url") or (
                f"https://youtube.com/shorts/{video_id}" if video_id else ""
            )
            out[key] = {
                "lesson": key,
                "display_id": display_id,
                "num": num,
                "suffix": suffix,
                "slug": slug,
                "title": _strip_vimfu_prefix(data.get("title", slug.replace("_", " ").title())),
                "book_title": data.get("book_title", ""),
                "description": data.get("description", ""),
                "kind": "long" if d == LONGS_DIR else "short",
                "videoId": video_id,
                "url": url,
                "published": bool(video_id),
                "source": str(p.relative_to(REPO_ROOT)).replace("\\", "/"),
            }
    return out


import re as _re
_VIMFU_PREFIX_RE = _re.compile(r"^\s*VimFu\s*[-–—:]\s*", _re.IGNORECASE)

def _strip_vimfu_prefix(t: str) -> str:
    return _VIMFU_PREFIX_RE.sub("", t).strip() if t else t


_LESSON_KEY_RE = re.compile(r"^(\d+)([a-z]*)$")


def _normalize_lesson_key(n):
    """Coerce a lesson identifier (int or str) into the canonical index key.

    Numeric-only IDs are returned as ``int``; sub-lettered IDs (e.g. ``880aa``,
    ``"0124a"``) are returned as 4-digit zero-padded strings (``"0880aa"``,
    ``"0124a"``) — matching the keys in ``_index()``. Returns ``None`` for
    inputs that can't be parsed as a lesson identifier.
    """
    if isinstance(n, int):
        return n
    if isinstance(n, str):
        s = n.strip()
        m = _LESSON_KEY_RE.match(s)
        if not m:
            return None
        num = int(m.group(1))
        suffix = m.group(2)
        return num if not suffix else f"{num:04d}{suffix}"
    return None


def video_for_lesson(n):
    """Return the video record for lesson key ``n``, or None.

    Accepts ints (canonical for numeric-only lesson IDs) or strings like
    ``"0430a"`` for sub-lessons. Strings without a leading-zero pad (e.g.
    ``"430a"``) are accepted too — they're normalized to ``"0430a"`` before
    lookup.
    """
    idx = _index()
    key = _normalize_lesson_key(n)
    if key is not None:
        v = idx.get(key)
        if v is not None:
            return v
    # Fall back to the legacy lookup behaviour so callers passing through
    # already-normalized keys (or unusual types) still work.
    if n in idx:
        return idx[n]
    try:
        return idx.get(int(n))
    except (TypeError, ValueError):
        return None


def videos_for_topic(t: dict) -> list[dict[str, Any]]:
    """Return the (resolved) video records for a topic's ``lessons`` array.

    Lessons that don't exist or aren't published yet are returned with
    ``published == False`` so callers can show a placeholder. Both integer IDs
    (``880``) and string IDs for sub-lettered lessons (``"0880aa"``, ``"124a"``)
    are accepted in the array.
    """
    out: list[dict[str, Any]] = []
    for raw in (t.get("lessons") or []):
        key = _normalize_lesson_key(raw)
        if key is None:
            continue
        v = video_for_lesson(key)
        if v is None:
            if isinstance(key, int):
                display_id = f"{key:04d}"
            else:
                m = _LESSON_KEY_RE.match(str(key))
                display_id = f"{int(m.group(1)):04d}{m.group(2)}" if m else str(key)
            v = {
                "lesson": key,
                "display_id": display_id,
                "num": int(display_id[:4]) if display_id[:4].isdigit() else 0,
                "suffix": display_id[4:] if len(display_id) > 4 else "",
                "slug": "",
                "title": f"Lesson {display_id}",
                "book_title": "",
                "description": "",
                "kind": "short",
                "videoId": "",
                "url": "",
                "published": False,
                "source": "",
            }
        out.append(v)
    return out


def stats() -> dict[str, int]:
    idx = _index()
    pub = sum(1 for v in idx.values() if v["published"])
    return {"total": len(idx), "published": pub, "unpublished": len(idx) - pub}


if __name__ == "__main__":
    s = stats()
    print(f"videos indexed: {s['total']} ({s['published']} published, "
          f"{s['unpublished']} not yet)")
