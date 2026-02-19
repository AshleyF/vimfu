"""Comprehensive macro recording and playback tests.

Tests Vim's macro system: q{a-z} to record, q to stop, @{a-z} to play,
@@ to replay last, counted macros, and interactions with all edit types.

Covers curriculum items 126-130 and the macro demo (long_0001_macro_demo).
"""

CASES = {
    # ================================================================
    # Basic recording and playback
    # ================================================================
    "record_and_play_simple": {
        "description": "Record inserting text, play it back",
        "keys": "qaiHello\x1bq@a",
        "initial": "one\ntwo\nthree",
    },
    "record_and_play_x": {
        "description": "Record deleting a char, play it back",
        "keys": "qaxqj@a",
        "initial": "abc\ndef\nghi",
    },
    "record_movement_and_edit": {
        "description": "Record w then x, play on next line",
        "keys": "qawxqj@a",
        "initial": "hello world\nfoo bar\nbaz qux",
    },
    "record_dd": {
        "description": "Record deleting a line",
        "keys": "qaddqj@a",
        "initial": "line1\nline2\nline3\nline4",
    },
    "record_empty_macro": {
        "description": "Record nothing (just q then q), play does nothing",
        "keys": "qaq@a",
        "initial": "hello",
    },

    # ================================================================
    # @@ (replay last macro)
    # ================================================================
    "replay_last_macro": {
        "description": "@@ replays the last executed macro",
        "keys": "qaxqj@aj@@",
        "initial": "abc\ndef\nghi\njkl",
    },
    "replay_last_twice": {
        "description": "@@ twice after @a",
        "keys": "qaxqj@aj@@j@@",
        "initial": "abcd\nefgh\nijkl\nmnop\nqrst",
    },

    # ================================================================
    # Counted macros
    # ================================================================
    "counted_macro_2": {
        "description": "2@a runs macro twice",
        "keys": "qaxq2@a",
        "initial": "abcdef",
    },
    "counted_macro_3": {
        "description": "3@a runs macro three times",
        "keys": "qaxq3@a",
        "initial": "abcdefgh",
    },
    "counted_replay_last": {
        "description": "3@@ runs last macro three times",
        "keys": "qaxq@a3@@",
        "initial": "abcdefgh",
    },

    # ================================================================
    # Multiple registers
    # ================================================================
    "two_registers": {
        "description": "Record into a and b, play both",
        "keys": "qaiX\x1bqqbiY\x1bqj@aj@b",
        "initial": "one\ntwo\nthree",
    },
    "overwrite_register": {
        "description": "Recording into same register overwrites",
        "keys": "qaiOLD\x1bqqaiNEW\x1bqj@a",
        "initial": "one\ntwo\nthree",
    },

    # ================================================================
    # Macros with insert mode
    # ================================================================
    "macro_insert_text": {
        "description": "Record i...Esc, replay",
        "keys": "qaIprefix: \x1bqj@a",
        "initial": "hello\nworld",
    },
    "macro_append_text": {
        "description": "Record A...Esc, replay",
        "keys": "qaA!!!\x1bqj@a",
        "initial": "hello\nworld",
    },
    "macro_open_line": {
        "description": "Record o...Esc (open line below), replay",
        "keys": "qaoinserted\x1bqjj@a",
        "initial": "aaa\nbbb\nccc",
    },
    "macro_open_above": {
        "description": "Record O...Esc (open line above), replay",
        "keys": "jqaOabove\x1bqjj@a",
        "initial": "aaa\nbbb\nccc",
    },

    # ================================================================
    # Macros with search
    # ================================================================
    "macro_with_search": {
        "description": "Record search and edit, replay",
        "keys": "qa/world\rrbqgg@a",
        "initial": "hello world foo world bar",
    },
    "macro_search_and_delete": {
        "description": "Record search then dd, replay",
        "keys": "qa/def\rddqgg@a",
        "initial": "abc\ndef\nghi\njkl\ndef\nmno",
    },
    "macro_with_n_repeat": {
        "description": "Record n (next match) and edit",
        "keys": "/hello\rqanrXq@a",
        "initial": "hello and hello and hello end",
    },

    # ================================================================
    # Macros with operators
    # ================================================================
    "macro_dw": {
        "description": "Record dw, replay",
        "keys": "qadwqj@a",
        "initial": "hello world\nfoo bar\nbaz qux",
    },
    "macro_cw": {
        "description": "Record cw...Esc, replay on next line",
        "keys": "qacwREPLACED\x1bjq@a",
        "initial": "hello world\nfoo bar\nbaz qux",
    },
    "macro_yank_paste": {
        "description": "Record yw then P on next line, replay",
        "keys": "qaywjPq@a",
        "initial": "aaa bbb\nccc ddd\neee fff\nggg hhh",
    },
    "macro_indent": {
        "description": "Record >>, replay",
        "keys": "qa>>jqj@a",
        "initial": "one\ntwo\nthree\nfour",
    },

    # ================================================================
    # Macros with find (f/t)
    # ================================================================
    "macro_f_and_edit": {
        "description": "Record f<char> then r replacement, replay",
        "keys": "qaf.rXqj@a",
        "initial": "a.b.c\nd.e.f\ng.h.i",
    },
    "macro_dt_and_replay": {
        "description": "Record dt<char> to delete, replay",
        "keys": "qadt:qj@a",
        "initial": "key: value\nfoo: bar\nbaz: qux",
    },

    # ================================================================
    # Macros with marks
    # ================================================================
    "macro_set_and_jump_mark": {
        "description": "Record setting a mark, moving, jumping back",
        "keys": "qama3j`aq@a",
        "initial": "one\ntwo\nthree\nfour\nfive\nsix\nseven",
    },

    # ================================================================
    # Macros with line motions
    # ================================================================
    "macro_j_x": {
        "description": "Record j then x, replay with count",
        "keys": "qajxq2@a",
        "initial": "abcd\nefgh\nijkl\nmnop",
    },
    "macro_plus_edit": {
        "description": "Record + then x, replay",
        "keys": "qa+xq@a",
        "initial": "abcd\nefgh\nijkl",
    },

    # ================================================================
    # Macros with undo interaction
    # ================================================================
    "macro_then_undo": {
        "description": "Play macro then undo — undo reverses the whole macro at once? No, each change separately.",
        "keys": "qaxjxq@auu",
        "initial": "abc\ndef\nghi\njkl\nmno",
    },

    # ================================================================
    # Recording indicator display
    # ================================================================
    "recording_indicator_shown": {
        "description": "During recording, command line shows 'recording @a'",
        "keys": "qa",
        "initial": "hello",
    },
    "recording_indicator_gone_after_stop": {
        "description": "After q to stop, command line is clear",
        "keys": "qaq",
        "initial": "hello",
    },
    "recording_indicator_during_different_reg": {
        "description": "Recording into register b",
        "keys": "qb",
        "initial": "hello",
    },

    # ================================================================
    # Macros with visual mode
    # ================================================================
    "macro_visual_delete": {
        "description": "Record visual select + delete, replay",
        "keys": "qavlldqj@a",
        "initial": "abcdef\nghijkl\nmnopqr",
    },

    # ================================================================
    # Macros with dot repeat inside
    # ================================================================
    "macro_with_dot": {
        "description": "Record a change, then dot inside macro",
        "keys": "rx0qal.q@a",
        "initial": "abcdef",
    },

    # ================================================================
    # Macro demo scenario (simplified)
    # From curriculum/longs/long_0001_macro_demo.json:
    # Search for function, open line, type log, search next, replay
    # ================================================================
    "macro_demo_add_logging": {
        "description": "Simplified version of the macro demo: add text after each 'def' line",
        "keys": "/def\rqaojLOG\x1b/def\rq@a@@",
        "initial": "import os\n\ndef alpha():\n    pass\n\ndef beta():\n    pass\n\ndef gamma():\n    pass\n\ndef delta():\n    pass",
    },

    # ================================================================
    # Edge cases
    # ================================================================
    "macro_on_last_line": {
        "description": "Macro that moves down on last line (j does nothing)",
        "keys": "Gqajxq@a",
        "initial": "abc\ndef",
    },
    "macro_overwrite_with_different": {
        "description": "Record different content into same register",
        "keys": "qaiA\x1bqqaiB\x1bqj@a",
        "initial": "one\ntwo",
    },
    "macro_register_persists": {
        "description": "Macro register survives across multiple plays",
        "keys": "qaxq@a@a@a",
        "initial": "abcdef",
    },
    "macro_with_replace_char": {
        "description": "Record r (replace char), replay",
        "keys": "qarZqj@a",
        "initial": "abc\ndef\nghi",
    },
    "macro_with_tilde": {
        "description": "Record ~ (toggle case), replay",
        "keys": "qa~q@a",
        "initial": "abcdef",
    },
    "macro_with_join": {
        "description": "Record J (join), replay",
        "keys": "qaJq@a",
        "initial": "aaa\nbbb\nccc\nddd",
    },
    "macro_with_paste_p": {
        "description": "Record yank word + paste after, replay",
        "keys": "qaywepq0@a",
        "initial": "abc def ghi",
    },
    "macro_with_0_dollar": {
        "description": "Record 0 and $ movement in macro",
        "keys": "qa$xjq@a",
        "initial": "abcde\nfghij\nklmno",
    },
    "counted_at_at_2": {
        "description": "2@@ works",
        "keys": "qajxq@a2@@",
        "initial": "abcd\nefgh\nijkl\nmnop\nqrst",
    },
}
