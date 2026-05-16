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
    "search-find": "Search and Find",
    "marks-jumps": "Marks and Jumps",
    "scrolling-screen": "Scrolling the Screen",
}


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
