"""Tiny loader for ``content/site.config.json``.

Single source of truth for site-wide values (contact email, current
edition, base URL). Every renderer imports from here so we change a
value in one place and regenerate.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "site.config.json"


@lru_cache(maxsize=1)
def load() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        return {}
    raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    return {k: v for k, v in raw.items() if not k.startswith("_")}


def contact_email() -> str:
    return load().get("contact_email", "hello@vimfubook.com")


def current_edition() -> str:
    return load().get("current_edition", "1e")


def current_edition_label() -> str:
    return load().get("current_edition_label", "First Edition")


def current_edition_year() -> str:
    return load().get("current_edition_year", "")


def site_base_url() -> str:
    return load().get("site_base_url", "https://vimfubook.com").rstrip("/")


def editions() -> list[dict[str, str]]:
    """All known editions, past and present. Used by the redirect generator
    to keep emitting old errata pages forever — never break a printed QR."""
    return load().get("editions") or [
        {"slug": current_edition(), "label": current_edition_label(),
         "year": current_edition_year()}
    ]
