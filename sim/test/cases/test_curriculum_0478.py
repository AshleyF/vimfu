"""Tests for video 0478: numbered register put with u. trick."""

CASES = {
    # ── 0478 "1p then u. cycles through delete history ────────
    # Setup: file with 5 lines. Delete top 3, then "1p brings them
    # back one at a time. u. should undo and put the NEXT register.
    "numbered_register_1p_basic": {
        "description": "After 3 deletes, \"1p brings back most-recent delete",
        "keys": "dddddd\"1p",
        "initial": "alpha\nbravo\ncharlie\ndelta\nepsilon\n",
    },

    "numbered_register_u_dot_cycle": {
        "description": "After \"1p, u. cycles to register 2 (bravo)",
        "keys": "dddddd\"1pu.",
        "initial": "alpha\nbravo\ncharlie\ndelta\nepsilon\n",
    },

    "numbered_register_u_dot_dot": {
        "description": "After \"1p u., another u. goes to register 3 (alpha)",
        "keys": "dddddd\"1pu.u.",
        "initial": "alpha\nbravo\ncharlie\ndelta\nepsilon\n",
    },

    # ── Explicit register access ──────────────────────────────
    "numbered_register_2p_explicit": {
        "description": "\"2p directly accesses second-most-recent delete",
        "keys": "dddddd\"2p",
        "initial": "alpha\nbravo\ncharlie\ndelta\nepsilon\n",
    },

    "numbered_register_3p_explicit": {
        "description": "\"3p directly accesses third delete",
        "keys": "dddddd\"3p",
        "initial": "alpha\nbravo\ncharlie\ndelta\nepsilon\n",
    },
}
