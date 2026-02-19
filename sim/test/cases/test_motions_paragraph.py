CASES = {
    # ── } forward to next blank line ─────────────────────────
    "brace_forward_basic": {
        "keys": "}",
        "initial": "aaa\nbbb\n\nccc\nddd",
    },
    "brace_forward_lands_on_blank": {
        "keys": "}",
        "initial": "line one\nline two\n\nline four\nline five",
    },
    "brace_forward_twice": {
        "keys": "}}",
        "initial": "aaa\n\nbbb\n\nccc",
    },
    "brace_forward_three_times": {
        "keys": "}}}",
        "initial": "aaa\n\nbbb\n\nccc\n\nddd",
    },
    "brace_forward_count_2": {
        "keys": "2}",
        "initial": "aaa\n\nbbb\n\nccc",
    },
    "brace_forward_count_3": {
        "keys": "3}",
        "initial": "aaa\n\nbbb\n\nccc\n\nddd",
    },
    "brace_forward_at_eof": {
        "keys": "}",
        "initial": "only line",
    },
    "brace_forward_no_blank_lines": {
        "keys": "}",
        "initial": "aaa\nbbb\nccc\nddd\neee",
    },
    "brace_forward_empty_buffer": {
        "keys": "}",
        "initial": "",
    },
    "brace_forward_single_blank_at_end": {
        "keys": "}",
        "initial": "aaa\nbbb\n",
    },
    "brace_forward_blank_at_start": {
        "keys": "}",
        "initial": "\naaa\nbbb",
    },
    "brace_forward_multiple_consecutive_blanks": {
        "keys": "}",
        "initial": "aaa\n\n\n\nbbb",
    },
    "brace_forward_two_past_consecutive_blanks": {
        "keys": "}}",
        "initial": "aaa\n\n\n\nbbb",
    },
    "brace_forward_all_blank_lines": {
        "keys": "}",
        "initial": "\n\n\n\n",
    },
    "brace_forward_all_blank_twice": {
        "keys": "}}",
        "initial": "\n\n\n\n",
    },
    "brace_forward_whitespace_not_blank": {
        "keys": "}",
        "initial": "aaa\n   \nbbb\n\nccc",
    },
    "brace_forward_tabs_not_blank": {
        "keys": "}",
        "initial": "aaa\n\t\nbbb\n\nccc",
    },
    "brace_forward_from_middle_of_file": {
        "keys": "j}",
        "initial": "aaa\nbbb\n\nccc\nddd",
    },
    "brace_forward_from_blank_line": {
        "keys": "jj}",
        "initial": "aaa\nbbb\n\nccc\n\neee",
    },
    "brace_forward_single_line": {
        "keys": "}",
        "initial": "hello",
    },
    "brace_forward_count_exceeds_paragraphs": {
        "keys": "5}",
        "initial": "aaa\n\nbbb\n\nccc",
    },
    "brace_forward_two_char_lines": {
        "keys": "}",
        "initial": "ab\ncd\n\nef\ngh",
    },
    "brace_forward_long_paragraphs": {
        "keys": "}",
        "initial": "aa\nbb\ncc\ndd\nee\nff\ngg\n\nhh",
    },
    "brace_forward_para_then_eof": {
        "keys": "}}",
        "initial": "aaa\n\nbbb",
    },
    "brace_forward_blank_first_line": {
        "keys": "}",
        "initial": "\nfoo\nbar\n\nbaz",
    },
    "brace_forward_blank_last_line": {
        "keys": "}",
        "initial": "foo\nbar\n",
    },

    # ── { backward to previous blank line ────────────────────
    "brace_backward_basic": {
        "keys": "G{",
        "initial": "aaa\nbbb\n\nccc\nddd",
    },
    "brace_backward_from_last_line": {
        "keys": "G{",
        "initial": "aaa\n\nbbb\nccc",
    },
    "brace_backward_twice": {
        "keys": "G{{",
        "initial": "aaa\n\nbbb\n\nccc",
    },
    "brace_backward_three_times": {
        "keys": "G{{{",
        "initial": "aaa\n\nbbb\n\nccc\n\nddd",
    },
    "brace_backward_count_2": {
        "keys": "G2{",
        "initial": "aaa\n\nbbb\n\nccc",
    },
    "brace_backward_count_3": {
        "keys": "G3{",
        "initial": "aaa\n\nbbb\n\nccc\n\nddd",
    },
    "brace_backward_at_bof": {
        "keys": "{",
        "initial": "only line",
    },
    "brace_backward_no_blank_lines": {
        "keys": "G{",
        "initial": "aaa\nbbb\nccc\nddd\neee",
    },
    "brace_backward_empty_buffer": {
        "keys": "{",
        "initial": "",
    },
    "brace_backward_single_line": {
        "keys": "{",
        "initial": "hello",
    },
    "brace_backward_blank_at_end": {
        "keys": "G{",
        "initial": "aaa\nbbb\n",
    },
    "brace_backward_blank_at_start": {
        "keys": "G{",
        "initial": "\naaa\nbbb",
    },
    "brace_backward_multiple_consecutive": {
        "keys": "G{",
        "initial": "aaa\n\n\n\nbbb",
    },
    "brace_backward_two_past_consecutive": {
        "keys": "G{{",
        "initial": "aaa\n\n\n\nbbb",
    },
    "brace_backward_all_blank_lines": {
        "keys": "G{",
        "initial": "\n\n\n\n",
    },
    "brace_backward_whitespace_not_blank": {
        "keys": "G{",
        "initial": "aaa\n   \nbbb\n\nccc",
    },
    "brace_backward_tabs_not_blank": {
        "keys": "G{",
        "initial": "aaa\n\t\nbbb\n\nccc",
    },
    "brace_backward_from_middle": {
        "keys": "3j{",
        "initial": "aaa\n\nbbb\nccc\nddd",
    },
    "brace_backward_from_blank_line": {
        "keys": "2j{",
        "initial": "aaa\nbbb\n\nccc\nddd",
    },
    "brace_backward_count_exceeds": {
        "keys": "G5{",
        "initial": "aaa\n\nbbb\n\nccc",
    },

    # ── Combined forward and backward ────────────────────────
    "brace_forward_then_backward": {
        "keys": "}{",
        "initial": "aaa\nbbb\n\nccc\nddd\n\neee",
    },
    "brace_backward_then_forward": {
        "keys": "G{}",
        "initial": "aaa\n\nbbb\nccc\n\nddd",
    },
    "brace_zigzag": {
        "keys": "}}{",
        "initial": "aaa\n\nbbb\n\nccc\n\nddd",
    },

    # ── Many paragraphs ──────────────────────────────────────
    "many_paragraphs_forward": {
        "keys": "}",
        "initial": "a\n\nb\n\nc\n\nd\n\ne\n\nf",
    },
    "many_paragraphs_forward_all": {
        "keys": "}}}}}}",
        "initial": "a\n\nb\n\nc\n\nd\n\ne\n\nf",
    },
    "many_paragraphs_backward_all": {
        "keys": "G{{{{{{",
        "initial": "a\n\nb\n\nc\n\nd\n\ne\n\nf",
    },
    "many_paragraphs_count_forward": {
        "keys": "5}",
        "initial": "a\n\nb\n\nc\n\nd\n\ne\n\nf",
    },
    "many_paragraphs_count_backward": {
        "keys": "G5{",
        "initial": "a\n\nb\n\nc\n\nd\n\ne\n\nf",
    },

    # ── Edge cases with content ───────────────────────────────
    "blank_between_every_line": {
        "keys": "}",
        "initial": "a\n\nb\n\nc\n\nd",
    },
    "blank_between_every_line_back": {
        "keys": "G{",
        "initial": "a\n\nb\n\nc\n\nd",
    },
    "only_two_lines_with_blank": {
        "keys": "}",
        "initial": "aaa\n\nbbb",
    },
    "only_two_lines_no_blank": {
        "keys": "}",
        "initial": "aaa\nbbb",
    },
    "forward_mixed_ws_and_empty": {
        "keys": "}}",
        "initial": "aaa\n   \nbbb\n\nccc\n\t\nddd\n\neee",
    },
    "backward_mixed_ws_and_empty": {
        "keys": "G{{",
        "initial": "aaa\n   \nbbb\n\nccc\n\t\nddd\n\neee",
    },
}
