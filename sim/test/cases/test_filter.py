"""Test !{motion} shell filter operator and :{range}!cmd."""

CASES = {
    # ── !{motion} from normal mode ──

    "filter_sort_all": {
        "description": "Sort all lines with !G sort from line 1",
        "initial": "cherry\napple\nbanana\ndate",
        "keys": "gg!Gsort\r",
    },

    "filter_sort_range_motion": {
        "description": "Sort first 3 lines with !2j sort",
        "keys": "gg!2jsort\r",
        "initial": "cherry\napple\nbanana\ndate",
    },

    "filter_double_bang_sort": {
        "description": "3!! sorts 3 lines starting from current",
        "initial": "cherry\napple\nbanana\ndate",
        "keys": "3!!sort\r\r",
    },

    # ── Visual mode ! ──

    "filter_visual_sort": {
        "description": "Visual select all lines then !sort",
        "initial": "cherry\napple\nbanana\ndate",
        "keys": "ggVG!sort\r",
    },

    "filter_visual_partial": {
        "description": "Visual select middle lines then !sort",
        "initial": "cherry\napple\nbanana\ndate",
        "keys": "jVj!sort\r",
    },

    # ── :{range}!cmd ex command ──

    "filter_ex_sort_all": {
        "description": ":%!sort sorts entire file",
        "initial": "cherry\napple\nbanana\ndate",
        "keys": ":%!sort\r",
    },

    "filter_ex_range_sort": {
        "description": ":2,3!sort to sort lines 2-3 only",
        "initial": "cherry\napple\nbanana\ndate",
        "keys": ":2,3!sort\r",
    },
}
