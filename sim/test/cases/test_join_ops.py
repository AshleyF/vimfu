CASES = {
    # === J basic ===
    "join_basic": {"keys": "J", "initial": "hello\nworld"},
    "join_three_words": {"keys": "J", "initial": "aaa\nbbb\nccc"},
    "join_with_indent": {"keys": "J", "initial": "hello\n    world"},
    "join_with_tab_indent": {"keys": "J", "initial": "hello\n\tworld"},
    "join_second_pair": {"keys": "jJ", "initial": "aaa\nbbb\nccc"},
    "join_first_of_four": {
        "keys": "J",
        "initial": "one\ntwo\nthree\nfour"
    },

    # === J on last line / single line ===
    "join_last_line": {"keys": "GJ", "initial": "aaa\nbbb"},
    "join_single_line_buffer": {"keys": "J", "initial": "only"},
    "join_last_line_three": {
        "keys": "GJ",
        "initial": "aaa\nbbb\nccc"
    },

    # === J with empty lines ===
    "join_empty_above_nonempty": {"keys": "J", "initial": "\nhello"},
    "join_nonempty_above_empty": {"keys": "J", "initial": "hello\n"},
    "join_two_empty_lines": {"keys": "J", "initial": "\n"},
    "join_empty_between": {
        "keys": "J",
        "initial": "hello\n\nworld"
    },
    "join_three_empty": {"keys": "J", "initial": "\n\n\n"},
    "join_nonempty_above_empty_above_nonempty": {
        "keys": "J",
        "initial": "aaa\n\nbbb"
    },

    # === J with trailing/leading whitespace ===
    "join_trailing_space": {"keys": "J", "initial": "hello \nworld"},
    "join_leading_spaces_removed": {
        "keys": "J",
        "initial": "hello\n   world"
    },
    "join_both_spaces": {
        "keys": "J",
        "initial": "hello  \n   world"
    },

    # === J next line starts with ) ===
    "join_paren_no_space": {"keys": "J", "initial": "foo(\n)"},
    "join_paren_indented": {
        "keys": "J",
        "initial": "foo(\n    )"
    },
    "join_paren_with_content": {
        "keys": "J",
        "initial": "bar(\n);"
    },

    # === J with count ===
    "join_count_3": {
        "keys": "3J",
        "initial": "aaa\nbbb\nccc\nddd"
    },
    "join_count_4": {
        "keys": "4J",
        "initial": "aaa\nbbb\nccc\nddd\neee"
    },
    "join_count_2": {"keys": "2J", "initial": "hello\nworld\nfoo"},
    "join_count_exceeds_lines": {
        "keys": "10J",
        "initial": "aaa\nbbb\nccc"
    },
    "join_count_from_middle": {
        "keys": "j3J",
        "initial": "aaa\nbbb\nccc\nddd\neee"
    },
    "join_count_1_noop": {"keys": "1J", "initial": "hello\nworld"},

    # === Cursor position after J ===
    "join_cursor_at_join_point": {
        "keys": "J",
        "initial": "hello\nworld"
    },
    "join_cursor_3J": {
        "keys": "3J",
        "initial": "aa\nbb\ncc\ndd"
    },
    "join_cursor_empty_next": {
        "keys": "J",
        "initial": "hello\n\nworld"
    },

    # === Multiple J in sequence ===
    "join_two_sequential": {
        "keys": "JJ",
        "initial": "aaa\nbbb\nccc"
    },
    "join_three_sequential": {
        "keys": "JJJ",
        "initial": "aaa\nbbb\nccc\nddd"
    },
    "join_all_lines": {
        "keys": "JJJJ",
        "initial": "a\nb\nc\nd\ne"
    },

    # === gJ (join without space) ===
    "gJ_basic": {"keys": "gJ", "initial": "hello\nworld"},
    "gJ_preserves_indent": {
        "keys": "gJ",
        "initial": "hello\n    world"
    },
    "gJ_no_space_added": {
        "keys": "gJ",
        "initial": "foo\nbar"
    },
    "gJ_empty_next_line": {"keys": "gJ", "initial": "hello\n"},
    "gJ_empty_current_line": {"keys": "gJ", "initial": "\nhello"},
    "gJ_two_empty": {"keys": "gJ", "initial": "\n"},
    "gJ_last_line": {"keys": "GgJ", "initial": "aaa\nbbb"},
    "gJ_single_line": {"keys": "gJ", "initial": "only"},
    "gJ_trailing_space": {
        "keys": "gJ",
        "initial": "hello \nworld"
    },

    # === gJ with count ===
    "gJ_count_3": {
        "keys": "3gJ",
        "initial": "aaa\nbbb\nccc\nddd"
    },
    "gJ_count_2": {"keys": "2gJ", "initial": "foo\nbar\nbaz"},
    "gJ_count_exceeds": {
        "keys": "10gJ",
        "initial": "aaa\nbbb"
    },

    # === gJ cursor position ===
    "gJ_cursor_position": {"keys": "gJ", "initial": "abc\ndef"},
    "gJ_cursor_empty_next": {
        "keys": "gJ",
        "initial": "abc\n\ndef"
    },
}
