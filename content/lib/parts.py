"""Display labels for book parts.

The part *slug* (directory name minus the leading number) is the stable
identifier used in URLs, redirect IDs (e.g. ``p-04-search-find``), QR
codes already printed in physical copies, and filenames. It should not
change.

The display label is what readers see on covers, in nav, and in the
contents list. By default it's derived from the slug
(``"search-find" -> "Search Find"``). For parts where that mechanical
title-case doesn't read well, override here.
"""

from __future__ import annotations

# Map of part slug (no leading NN-) -> display label.
PART_LABELS: dict[str, str] = {
    "survival": "Getting Started",
    "counts": "Counts and Visual Basics",
    "visual-modes": "Visual Mode in Depth",
    "search-find": "Search and Find",
    "marks-jumps": "Marks and Jumps",
    "scrolling-screen": "Scrolling the Screen",
    "windows-buffers-tabs": "Windows, Buffers and Tabs",
    "patterns-recipes": "Patterns and Recipes",
    "tmux": "Bonus: tmux",
}

# Filesystem prefixes are stable URL identifiers, not the reader-facing order.
# Start with the hands-on survival material, then provide the conceptual and
# historical foundations. All remaining parts keep their numeric order.
_PART_ORDER = {
    "02-survival": 1,
    "01-foundations": 2,
    # Prefix Families is a synthesis/reference part. Present it after the
    # feature chapters whose commands it gathers, but before the tmux bonus.
    "15-prefix-families": 24,
    "22-tmux": 25,
}


def part_sort_key(part_dir: str) -> tuple[int, str]:
    """Return the reader-facing sort key without changing stable slugs."""
    try:
        numeric = int(part_dir.split("-", 1)[0])
    except (ValueError, IndexError):
        numeric = 999
    return (_PART_ORDER.get(part_dir, numeric + 2), part_dir)


def part_label(part_dir: str) -> str:
    """Return the human-readable label for a part directory.

    ``part_dir`` is the directory name (e.g. ``"04-search-find"``).
    Strips the leading ``NN-`` and either applies an override from
    :data:`PART_LABELS` or title-cases the dashed slug.
    """
    slug = part_dir.split("-", 1)[-1] if "-" in part_dir else part_dir
    if slug in PART_LABELS:
        return PART_LABELS[slug]
    return slug.replace("-", " ").title()
