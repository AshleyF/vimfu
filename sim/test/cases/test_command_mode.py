THIRTYLINES = "\n".join(f"Line {i:02d} content" for i in range(1, 31))
FIFTYLINES = "\n".join(f"Line {i:02d} content" for i in range(1, 51))

CASES = {
    # ===== :{number} - go to line =====
    "goto_line_1": {
        "keys": ":1\r",
        "initial": THIRTYLINES,
    },
    "goto_line_5": {
        "keys": ":5\r",
        "initial": THIRTYLINES,
    },
    "goto_line_10": {
        "keys": ":10\r",
        "initial": THIRTYLINES,
    },
    "goto_line_15": {
        "keys": ":15\r",
        "initial": THIRTYLINES,
    },
    "goto_line_20": {
        "keys": ":20\r",
        "initial": THIRTYLINES,
    },
    "goto_line_25": {
        "keys": ":25\r",
        "initial": THIRTYLINES,
    },
    "goto_line_30": {
        "keys": ":30\r",
        "initial": THIRTYLINES,
    },
    "goto_last_line_dollar": {
        "keys": ":$\r",
        "initial": THIRTYLINES,
    },
    "goto_line_beyond_range": {
        "keys": ":999\r",
        "initial": THIRTYLINES,
    },
    "goto_line_100_on_30_lines": {
        "keys": ":100\r",
        "initial": THIRTYLINES,
    },
    "goto_line_0": {
        "keys": ":0\r",
        "initial": THIRTYLINES,
    },
    "goto_line_on_short_file": {
        "keys": ":3\r",
        "initial": "Line 1\nLine 2\nLine 3\nLine 4\nLine 5",
    },
    "goto_line_beyond_short_file": {
        "keys": ":10\r",
        "initial": "Line 1\nLine 2\nLine 3\nLine 4\nLine 5",
    },
    "goto_line_1_on_single_line": {
        "keys": ":1\r",
        "initial": "Only one line here",
    },
    "goto_line_5_on_single_line": {
        "keys": ":5\r",
        "initial": "Only one line here",
    },
    "goto_line_dollar_on_single_line": {
        "keys": ":$\r",
        "initial": "Only one line here",
    },
    "goto_line_on_empty_file": {
        "keys": ":1\r",
        "initial": "",
    },
    "goto_line_dollar_on_empty_file": {
        "keys": ":$\r",
        "initial": "",
    },

    # ===== goto line on fifty-line file (needs scrolling) =====
    "goto_line_25_fifty_lines": {
        "keys": ":25\r",
        "initial": FIFTYLINES,
    },
    "goto_line_40_fifty_lines": {
        "keys": ":40\r",
        "initial": FIFTYLINES,
    },
    "goto_line_50_fifty_lines": {
        "keys": ":50\r",
        "initial": FIFTYLINES,
    },
    "goto_last_line_dollar_fifty": {
        "keys": ":$\r",
        "initial": FIFTYLINES,
    },
    "goto_line_beyond_fifty": {
        "keys": ":200\r",
        "initial": FIFTYLINES,
    },

    # ===== Multiple goto commands =====
    "goto_line_then_goto_another": {
        "keys": ":20\r:5\r",
        "initial": THIRTYLINES,
    },
    "goto_bottom_then_top": {
        "keys": ":30\r:1\r",
        "initial": THIRTYLINES,
    },
    "goto_top_then_bottom": {
        "keys": ":1\r:$\r",
        "initial": THIRTYLINES,
    },

    # ===== Escape from command mode =====
    "command_mode_escape": {
        "keys": ":\x1b",
        "initial": THIRTYLINES,
    },
    "command_mode_type_then_escape": {
        "keys": ":abc\x1b",
        "initial": THIRTYLINES,
    },
    "command_mode_type_number_then_escape": {
        "keys": ":15\x1b",
        "initial": THIRTYLINES,
    },
    "command_mode_escape_cursor_unchanged": {
        "keys": "10G:abc\x1b",
        "initial": THIRTYLINES,
    },

    # ===== Backspace in command mode =====
    "command_mode_backspace_exits": {
        "keys": ":\x08",
        "initial": THIRTYLINES,
    },
    "command_mode_type_then_backspace_all": {
        "keys": ":a\x08\x08",
        "initial": THIRTYLINES,
    },
    "command_mode_backspace_partial": {
        "keys": ":15\x08" + "0\r",
        "initial": THIRTYLINES,
    },

    # ===== Command mode entry and normal mode interaction =====
    "command_mode_after_movement": {
        "keys": "5j:10\r",
        "initial": THIRTYLINES,
    },
    "movement_after_command": {
        "keys": ":15\r5j",
        "initial": THIRTYLINES,
    },
    "goto_line_then_normal_ops": {
        "keys": ":20\r0w",
        "initial": THIRTYLINES,
    },
}
