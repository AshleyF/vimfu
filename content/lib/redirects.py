"""
Stable redirect URLs for QR codes.

Print is forever. A QR code printed in the book is etched-in-ink — we can
never change where it points. So every QR we generate encodes a redirect
URL on our own domain (``vimfubook.com/r/<slug>``) and the actual target
lives in a JSON map that we own and can update at any time.

Slug taxonomy
-------------
``v-NNNN``      One curriculum video (lesson NNNN). Resolves to the
                YouTube URL when published, or to a "coming soon" landing
                page when not.

``p-<part_dir>`` The video collection page for one part of the book
                (e.g. ``p-22-tmux``).

``t-<topic_id>`` Reference page for a topic on the website. Mirrors the
                content of the chapter; useful for sharing and for
                copy-pasteable code samples.

``sim-tmux``    Open the live simulator with tmux already running.

``sim-ex-<example_id>``   Open the simulator pre-loaded with the
                          starting buffer of a worked example.

``book``        Buy-the-book landing page (Amazon / direct).

Adding a new redirect
---------------------
Either:

  * It's auto-derivable from the content (any of the schemes above) — no
    action needed; ``content/render_redirects.py`` produces it on its
    next run.

  * It's hand-curated (``book``, ``faq``, errata pages, etc.) — add it to
    ``content/redirects.manual.json``.

Then run ``python content/render_redirects.py`` to regenerate
``output/html/r/<slug>/index.html`` for every entry.
"""

from __future__ import annotations

DEFAULT_BASE_URL = "https://vimfubook.com"
REDIRECT_PATH = "/r/"


def redirect_url(slug: str, base_url: str = DEFAULT_BASE_URL) -> str:
    """Return the public redirect URL for ``slug``."""
    return f"{base_url.rstrip('/')}{REDIRECT_PATH}{slug}"


# ---- slug builders --------------------------------------------------------- #

def video_slug(lesson: int) -> str:
    return f"v-{int(lesson):04d}"


def part_videos_slug(part_dir: str) -> str:
    return f"p-{part_dir}"


def topic_slug(topic_id: str) -> str:
    # Topic ids may contain dots (e.g. ``tmux.panes``); keep them — slugs
    # are URL-path segments and dots are legal there.
    return f"t-{topic_id}"


def sim_example_slug(example_id: str) -> str:
    return f"sim-ex-{example_id}"


def errata_slug(edition: str) -> str:
    """Per-edition errata slug, e.g. ``errata-1e``. The printed book bakes
    one of these into a QR — never re-use a slug across editions."""
    return f"errata-{edition}"


SIM_TMUX_SLUG = "sim-tmux"
BOOK_SLUG = "book"
REPORT_ISSUE_SLUG = "report-issue"      # generic "found a bug?" mailto
REPORT_BOOK_ISSUE_SLUG = "report-book"  # specifically for the printed book
