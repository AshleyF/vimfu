"""Tests for tag text objects: it (inner tag) and at (a tag)."""

CASES = {
    # ── dit — delete inner tag ──
    "dit_basic": {
        "keys": "fhdit",
        "initial": "<div>hello</div>\n",
    },
    "dit_nested": {
        "keys": "fhdit",
        "initial": "<p><b>hello</b></p>\n",
    },
    "dit_empty": {
        "keys": "fdit",
        "initial": "<span></span>\n",
    },
    "dit_multiline": {
        "keys": "jdit",
        "initial": "<div>\n  content\n</div>\n",
    },

    # ── dat — delete a tag (including tags) ──
    "dat_basic": {
        "keys": "fhdat",
        "initial": "<div>hello</div>\n",
    },
    "dat_with_surrounding": {
        "keys": "fhdat",
        "initial": "before <b>bold</b> after\n",
    },

    # ── cit — change inner tag ──
    "cit_basic": {
        "keys": "fhcitworld\x1b",
        "initial": "<div>hello</div>\n",
    },

    # ── yit — yank inner tag then paste ──
    "yit_basic": {
        "keys": "fhyitGp",
        "initial": "<div>hello</div>\nresult: \n",
    },

    # ── vit — visual select inner tag ──
    "vit_basic": {
        "keys": "fhvitd",
        "initial": "<div>hello</div>\n",
    },
}
