CASES = {
    # === >> (indent line right) ===
    "indent_basic": {"keys": ">>", "initial": "hello"},
    "indent_second_line": {"keys": "j>>", "initial": "aaa\nbbb\nccc"},
    "indent_last_line": {"keys": "G>>", "initial": "aaa\nbbb\nccc"},
    "indent_empty_line": {"keys": ">>", "initial": ""},
    "indent_already_indented": {
        "keys": ">>",
        "initial": "\thello"
    },
    "indent_double": {"keys": ">>>>", "initial": "hello"},
    "indent_triple": {"keys": ">>>>>>", "initial": "hello"},
    "indent_preserves_content": {"keys": ">>", "initial": "hello world"},
    "indent_line_with_spaces": {"keys": ">>", "initial": "    hello"},
    "indent_multiple_lines_content": {
        "keys": ">>j>>",
        "initial": "aaa\nbbb\nccc"
    },

    # === >> with count ===
    "indent_count_2": {"keys": "2>>", "initial": "aaa\nbbb\nccc"},
    "indent_count_3": {"keys": "3>>", "initial": "aaa\nbbb\nccc\nddd"},
    "indent_count_exceeds_lines": {
        "keys": "5>>",
        "initial": "aaa\nbbb"
    },
    "indent_count_from_middle": {
        "keys": "j2>>",
        "initial": "aaa\nbbb\nccc\nddd"
    },
    "indent_count_1": {"keys": "1>>", "initial": "hello"},

    # === << (dedent line left) ===
    "dedent_basic": {"keys": "<<", "initial": "\thello"},
    "dedent_no_indent": {"keys": "<<", "initial": "hello"},
    "dedent_double_tab": {"keys": "<<", "initial": "\t\thello"},
    "dedent_second_line": {
        "keys": "j<<",
        "initial": "aaa\n\tbbb\nccc"
    },
    "dedent_spaces_8": {"keys": "<<", "initial": "        hello"},
    "dedent_spaces_4": {"keys": "<<", "initial": "    hello"},
    "dedent_spaces_12": {"keys": "<<", "initial": "            hello"},
    "dedent_empty_line": {"keys": "<<", "initial": ""},
    "dedent_tab_and_spaces": {
        "keys": "<<",
        "initial": "\t    hello"
    },

    # === << with count ===
    "dedent_count_2": {
        "keys": "2<<",
        "initial": "\taaa\n\tbbb\nccc"
    },
    "dedent_count_3": {
        "keys": "3<<",
        "initial": "\taaa\n\tbbb\n\tccc\nddd"
    },
    "dedent_count_from_middle": {
        "keys": "j2<<",
        "initial": "aaa\n\tbbb\n\tccc\nddd"
    },

    # === >{motion} (indent over motion) ===
    "indent_j": {"keys": ">j", "initial": "aaa\nbbb\nccc"},
    "indent_k": {"keys": "j>k", "initial": "aaa\nbbb\nccc"},
    "indent_G_from_top": {
        "keys": ">G",
        "initial": "aaa\nbbb\nccc"
    },
    "indent_gg_from_bottom": {
        "keys": "G>gg",
        "initial": "aaa\nbbb\nccc"
    },
    "indent_j_from_middle": {
        "keys": "j>j",
        "initial": "aaa\nbbb\nccc\nddd"
    },
    "indent_2j": {
        "keys": ">2j",
        "initial": "aaa\nbbb\nccc\nddd"
    },
    "indent_G_from_middle": {
        "keys": "j>G",
        "initial": "aaa\nbbb\nccc\nddd"
    },

    # === <{motion} (dedent over motion) ===
    "dedent_j": {
        "keys": "<j",
        "initial": "\taaa\n\tbbb\nccc"
    },
    "dedent_k": {
        "keys": "j<k",
        "initial": "\taaa\n\tbbb\nccc"
    },
    "dedent_G_from_top": {
        "keys": "<G",
        "initial": "\taaa\n\tbbb\n\tccc"
    },
    "dedent_gg_from_bottom": {
        "keys": "G<gg",
        "initial": "\taaa\n\tbbb\n\tccc"
    },
    "dedent_j_from_middle": {
        "keys": "j<j",
        "initial": "aaa\n\tbbb\n\tccc\nddd"
    },
    "dedent_2j": {
        "keys": "<2j",
        "initial": "\taaa\n\tbbb\n\tccc\nddd"
    },

    # === Cursor position after indent ===
    "indent_cursor_on_first_nonblank": {
        "keys": ">>",
        "initial": "hello"
    },
    "indent_cursor_stays_content": {
        "keys": ">>",
        "initial": "  hello world"
    },
    "dedent_cursor_on_first_nonblank": {
        "keys": "<<",
        "initial": "\thello"
    },

    # === Tab behavior (sw=8, noexpandtab) ===
    "indent_produces_tab": {"keys": ">>", "initial": "test"},
    "indent_existing_tab_adds_tab": {
        "keys": ">>",
        "initial": "\texisting"
    },
    "indent_two_tabs": {"keys": ">>>>", "initial": "deep"},
    "dedent_removes_tab": {
        "keys": "<<",
        "initial": "\tremove"
    },
    "dedent_two_tabs_once": {
        "keys": "<<",
        "initial": "\t\ttwotabs"
    },
    "dedent_two_tabs_twice": {
        "keys": "<<<<",
        "initial": "\t\ttwotabs"
    },
}
