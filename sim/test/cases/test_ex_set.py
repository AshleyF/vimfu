FIVELINES = "\n".join(f"Line {i:02d} content" for i in range(1, 6))
TENLINES = "\n".join(f"Line {i:02d} content" for i in range(1, 11))
TWENTYLINES = "\n".join(f"Line {i:02d} content" for i in range(1, 21))
THIRTYLINES = "\n".join(f"Line {i:02d} content" for i in range(1, 31))

CASES = {
    # ===== :set number =====
    "set_number_basic": {
        "keys": ":set number\r",
        "initial": FIVELINES,
    },
    "set_nu_short": {
        "keys": ":set nu\r",
        "initial": FIVELINES,
    },
    "set_number_tenlines": {
        "keys": ":set number\r",
        "initial": TENLINES,
    },
    "set_number_twentylines": {
        "keys": ":set number\r",
        "initial": TWENTYLINES,
    },
    "set_number_thirtylines": {
        "keys": ":set number\r",
        "initial": THIRTYLINES,
    },
    "set_number_single_line": {
        "keys": ":set number\r",
        "initial": "Hello world",
    },
    "set_number_empty": {
        "keys": ":set number\r",
        "initial": "",
    },
    "set_number_cursor_on_line5": {
        "keys": "4j:set number\r",
        "initial": TENLINES,
    },

    # ===== :set nonumber =====
    "set_nonumber": {
        "keys": ":set number\r:set nonumber\r",
        "initial": FIVELINES,
    },
    "set_nonu_short": {
        "keys": ":set nu\r:set nonu\r",
        "initial": FIVELINES,
    },

    # ===== :set relativenumber =====
    "set_relativenumber": {
        "keys": ":set relativenumber\r",
        "initial": TENLINES,
    },
    "set_rnu_short": {
        "keys": ":set rnu\r",
        "initial": TENLINES,
    },
    "set_relativenumber_on_line5": {
        "keys": "4j:set relativenumber\r",
        "initial": TENLINES,
    },
    "set_relativenumber_twentylines": {
        "keys": ":set relativenumber\r",
        "initial": TWENTYLINES,
    },

    # ===== :set norelativenumber =====
    "set_norelativenumber": {
        "keys": ":set rnu\r:set nornu\r",
        "initial": TENLINES,
    },

    # ===== Both number + relativenumber =====
    "set_number_and_relativenumber": {
        "keys": ":set number\r:set relativenumber\r",
        "initial": TENLINES,
    },
    "set_nu_rnu_on_line5": {
        "keys": "4j:set nu\r:set rnu\r",
        "initial": TENLINES,
    },
    "set_nu_rnu_twentylines": {
        "keys": ":set nu\r:set rnu\r",
        "initial": TWENTYLINES,
    },

    # ===== Cursor and editing with line numbers =====
    "set_number_then_move": {
        "keys": ":set number\r5j",
        "initial": TENLINES,
    },
    "set_number_then_insert": {
        "keys": ":set number\riHello \x1b",
        "initial": "world",
    },
    "set_number_then_dd": {
        "keys": ":set number\rdd",
        "initial": FIVELINES,
    },
    "set_number_then_o": {
        "keys": ":set number\roNew line\x1b",
        "initial": FIVELINES,
    },
    "set_number_scroll_down": {
        "keys": ":set number\rG",
        "initial": THIRTYLINES,
    },

    # ===== Wide line numbers (>9, >99) =====
    "set_number_wide_gutter": {
        "keys": ":set number\r",
        "initial": "\n".join(f"Line {i}" for i in range(1, 101)),
    },
}
