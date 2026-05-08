"""Audience filtering for VimFu content.

Every topic and every block may carry an ``audience`` key whose value is
``"book"``, ``"web"``, or ``"both"`` (the default). Renderers pass their own
audience name and use :func:`visible` to decide whether to emit each item.

Markdown is treated as the universal "review" format and shows everything
(audience ``"all"``).
"""
from __future__ import annotations


def visible(item: dict, target: str) -> bool:
    """Return True if *item* should be rendered for the *target* audience.

    *item* is a dict (topic or block); the audience key is optional.
    *target* is the renderer's audience: ``"book"``, ``"web"``, or ``"all"``.
    """
    if target == "all":
        return True
    aud = (item.get("audience") or "both").strip().lower()
    if aud in ("both", "all", ""):
        return True
    return aud == target
