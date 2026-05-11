"""
Stable short-id allocator for redirect slugs.

The taxonomy in ``redirects.py`` (``v-NNNN``, ``t-<topic_id>``, ``p-<part>``,
``sim-ex-<id>``, etc.) is great for code clarity — but it makes printed URLs
verbose and visually repetitive ("they all start with v-"). This module
maps each taxonomy slug to a short opaque id so that printed URLs read
``vimfubook.com/r/0042`` instead of ``vimfubook.com/r/v-0042``.

Stability rules
---------------
* Once a slug is assigned an id, that id is **frozen forever** (it may be
  on a printed page). New slugs get the next free id.
* The mapping lives in ``content/redirect_ids.json`` and is committed
  to the repo. Never edit by hand to renumber.
* Hand-curated short aliases (``book``, ``site``, ``faq`` from
  ``redirects.manual.json``) are *also* recognised at the redirect
  endpoint, but a copy of the canonical short-id always exists too.

Id format
---------
4 digits of base-36 (0-9, lowercase a-z). 1.6 million unique ids — far
more than we will ever need, while staying short enough to type and
readable beside a QR code. We pad to width 4 for visual alignment so
``r/0001`` lines up with ``r/zzzz``.
"""
from __future__ import annotations

import json
import string
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ID_FILE = ROOT / "redirect_ids.json"

ID_ALPHABET = string.digits + string.ascii_lowercase  # base 36
ID_WIDTH = 4
_LOCK = threading.Lock()
_CACHE: dict[str, str] | None = None


def _to_base36(n: int) -> str:
    if n == 0:
        return ID_ALPHABET[0]
    out = []
    while n:
        n, r = divmod(n, 36)
        out.append(ID_ALPHABET[r])
    return "".join(reversed(out))


def _load() -> dict[str, str]:
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    if ID_FILE.exists():
        try:
            _CACHE = json.loads(ID_FILE.read_text(encoding="utf-8"))
        except Exception:
            _CACHE = {}
    else:
        _CACHE = {}
    return _CACHE


def _persist() -> None:
    if _CACHE is None:
        return
    ID_FILE.write_text(
        json.dumps(_CACHE, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def id_for_slug(slug: str) -> str:
    """Return the short stable id for ``slug``, allocating one on first use."""
    with _LOCK:
        m = _load()
        if slug in m:
            return m[slug]
        # Allocate next free numeric id, encoded base-36, padded.
        used = set(m.values())
        n = 1
        while True:
            cand = _to_base36(n).rjust(ID_WIDTH, "0")
            if cand not in used:
                m[slug] = cand
                _persist()
                return cand
            n += 1


def all_ids() -> dict[str, str]:
    """Return a copy of the full slug -> id map."""
    with _LOCK:
        return dict(_load())
