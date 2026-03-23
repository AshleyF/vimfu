"""Test g<Tab> (go to last accessed tab) and additional tab features."""

CASES = {
    # ── g<Tab>: Go to last accessed tab ──

    "gtab_goes_to_last_tab": {
        "description": "g<Tab> goes back to the previously accessed tab",
        "initial": "first tab content\nsecond line",
        "keys": ":tabnew\rg\t",
    },

    "gtab_toggles_between_tabs": {
        "description": "g<Tab> toggles between two tabs",
        "initial": "first tab content\nsecond line",
        "keys": ":tabnew\rg\tg\t",
    },
}
