"""
Text object tests for paragraph (ip/ap) and sentence (is/as).
Also tests gv (reselect last visual selection).
"""

FIVEPARA = """\
First paragraph line one.
First paragraph line two.

Second paragraph.

Third paragraph line one.
Third paragraph line two.
Third paragraph line three.

Fourth paragraph."""

SENTENCES = """\
Hello world. This is a test. And another one.
Second line here. More text follows.

New paragraph starts. It has sentences."""

CASES = {
    # ═══════════════════════════════════════════
    # ip — inner paragraph
    # ═══════════════════════════════════════════

    # Basic inner paragraph: selects contiguous non-blank lines
    "dip_basic": {
        "keys": "dip",
        "initial": FIVEPARA,
    },
    # ip from middle of paragraph
    "dip_middle": {
        "keys": "jdip",
        "initial": FIVEPARA,
    },
    # ip on single-line paragraph
    "dip_single_line": {
        "keys": "4jdip",
        "initial": FIVEPARA,
    },
    # ip on blank line selects blank lines
    "dip_on_blank": {
        "keys": "2jdip",
        "initial": FIVEPARA,
    },
    # ip at last paragraph (no trailing blank)
    "dip_last_para": {
        "keys": "Gdip",
        "initial": FIVEPARA,
    },
    # yip + paste
    "yip_paste": {
        "keys": "yipp",
        "initial": FIVEPARA,
    },
    # cip enters insert
    "cip_basic": {
        "keys": "cipReplacement\x1b",
        "initial": FIVEPARA,
    },

    # ═══════════════════════════════════════════
    # ap — a paragraph
    # ═══════════════════════════════════════════

    # ap includes trailing blank lines
    "dap_basic": {
        "keys": "dap",
        "initial": FIVEPARA,
    },
    # ap from middle of paragraph
    "dap_middle": {
        "keys": "jdap",
        "initial": FIVEPARA,
    },
    # ap on last paragraph (no trailing blank → includes leading blank)
    "dap_last_para": {
        "keys": "Gdap",
        "initial": FIVEPARA,
    },
    # ap on blank line
    "dap_on_blank": {
        "keys": "2jdap",
        "initial": FIVEPARA,
    },
    # Visual ap extends selection
    "vap_basic": {
        "keys": "vapd",
        "initial": FIVEPARA,
    },
    # Visual line ap
    "Vap_basic": {
        "keys": "Vapd",
        "initial": FIVEPARA,
    },

    # ═══════════════════════════════════════════
    # is — inner sentence
    # ═══════════════════════════════════════════

    "dis_basic": {
        "keys": "dis",
        "initial": SENTENCES,
    },
    "dis_second_sentence": {
        "keys": "wdis",
        "initial": "Hello world. This is a test.",
    },
    "dis_at_period": {
        "keys": "f.dis",
        "initial": "Hello world. This is a test.",
    },
    "cis_basic": {
        "keys": "cisNew sentence\x1b",
        "initial": "Hello world. This is a test.",
    },
    "yis_paste": {
        "keys": "yisp",
        "initial": "Hello world. This is a test.",
    },
    # Sentence at end of line
    "dis_end_of_line": {
        "keys": "$bdis",
        "initial": "First. Second. Third.",
    },
    # Single sentence
    "dis_single": {
        "keys": "dis",
        "initial": "Only one sentence here.",
    },

    # ═══════════════════════════════════════════
    # as — a sentence
    # ═══════════════════════════════════════════

    "das_basic": {
        "keys": "das",
        "initial": SENTENCES,
    },
    "das_second": {
        "keys": "wdas",
        "initial": "Hello world. This is a test. Final one.",
    },
    "das_last_sentence": {
        "keys": "$bdas",
        "initial": "First sentence. Last sentence.",
    },
    "vas_basic": {
        "keys": "vasd",
        "initial": "Hello world. This is a test.",
    },

    # ═══════════════════════════════════════════
    # gv — reselect last visual selection
    # ═══════════════════════════════════════════

    # Basic gv: select a word, exit, reselect and delete
    "gv_basic": {
        "keys": "viw\x1bgvd",
        "initial": "hello world foo",
    },
    # gv after visual line
    "gv_visual_line": {
        "keys": "Vj\x1bGgvd",
        "initial": "line one\nline two\nline three\nline four",
    },
    # gv preserves the exact range
    "gv_exact_range": {
        "keys": "wvee\x1bggvd",
        "initial": "aaa bbb ccc ddd",
    },
    # gv after visual yank, then paste
    "gv_yank_reselect_paste": {
        "keys": "vey\x1bwgvp",
        "initial": "hello world",
    },
    # gv when no prior visual (should be no-op)
    "gv_no_prior": {
        "keys": "gvx",
        "initial": "hello",
    },
}
