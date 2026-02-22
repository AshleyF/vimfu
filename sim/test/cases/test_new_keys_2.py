"""Thorough tests for all new keys and their edge cases.

Covers every feature added in the "new keys" sprint, stress-testing
edge cases, counts, undo, dot-repeat, operators, and interactions.

Features tested:
  - Delete key (normal mode alias for x)
  - Q (replay last macro)
  - Insert mode: Ctrl-W, Ctrl-U, Delete (fwd), arrow keys
  - Insert mode Ctrl-H / Ctrl-J aliases
  - Replace mode Ctrl-H / Ctrl-J aliases
  - () sentence motions (forward / backward)
  - Ctrl-A / Ctrl-X (increment / decrement numbers)
  - Ctrl-O / Ctrl-I (jump list navigation)
  - g; / g, (change list navigation)
  - gd (go to local declaration)
"""

CASES = {
    # ================================================================
    # Delete key in normal mode — edge cases
    # ================================================================
    "delete_on_empty_line": {
        "description": "Delete on an empty line does nothing",
        "keys": "j\x1b[3~",
        "initial": "abc\n\ndef",
    },
    "delete_3_presses": {
        "description": "3 Delete presses delete 3 characters",
        "keys": "\x1b[3~\x1b[3~\x1b[3~",
        "initial": "abcdef",
    },
    "delete_near_end": {
        "description": "Delete near end of line deletes char and clamps cursor",
        "keys": "lll\x1b[3~\x1b[3~",
        "initial": "abcde",
    },
    "delete_last_char": {
        "description": "Delete on last char of line cursor stays valid",
        "keys": "$\x1b[3~",
        "initial": "abc",
    },
    "delete_dot_repeat": {
        "description": "Delete then dot repeats the deletion",
        "keys": "\x1b[3~j.",
        "initial": "abc\ndef",
    },
    "delete_undo": {
        "description": "Delete then undo restores deleted char",
        "keys": "\x1b[3~u",
        "initial": "abcde",
    },
    "delete_single_char_line": {
        "description": "Delete on a single-char line",
        "keys": "\x1b[3~",
        "initial": "x",
    },

    # ================================================================
    # Q — replay last macro edge cases
    # ================================================================
    "Q_undo_whole_macro": {
        "description": "Undo after Q undoes entire macro in one step",
        "keys": "qaiX\x1bqjQu",
        "initial": "aaa\nbbb",
    },
    "Q_after_recording_only": {
        "description": "Q works even without @a first",
        "keys": "qax\x1bqjQ",
        "initial": "abc\ndefg",
    },
    "Q_empty_macro": {
        "description": "Q of empty macro is no-op",
        "keys": "qaqQ",
        "initial": "hello",
    },
    "Q_with_count_3": {
        "description": "3Q replays macro 3 times",
        "keys": "qax\x1bqj3Q",
        "initial": "aaa\nbbbbbbb",
    },
    "Q_replays_last_played": {
        "description": "Q replays whichever macro was last played with @",
        "keys": "qaiA\x1bqqbiB\x1bqj@bj@ajQ",
        "initial": "111\n222\n333\n444",
    },

    # ================================================================
    # Insert mode Ctrl-W — more edge cases
    # ================================================================
    "insert_ctrl_w_punctuation": {
        "description": "Ctrl-W deletes punctuation group separately from word",
        "keys": "A\x17\x1b",
        "initial": "hello...",
    },
    "insert_ctrl_w_mixed_then_word": {
        "description": "Ctrl-W twice: first punct, then word",
        "keys": "A\x17\x17\x1b",
        "initial": "hello...",
    },
    "insert_ctrl_w_row0_col0": {
        "description": "Ctrl-W at row 0 col 0 does nothing",
        "keys": "i\x17\x1b",
        "initial": "hello",
    },
    "insert_ctrl_w_after_insert": {
        "description": "Type text then Ctrl-W deletes it",
        "keys": "Afoo bar\x17\x1b",
        "initial": "prefix ",
    },
    "insert_ctrl_w_tabs": {
        "description": "Ctrl-W skips tab whitespace then deletes word",
        "keys": "A\x17\x1b",
        "initial": "hello\tworld",
    },

    # ================================================================
    # Insert mode Ctrl-U — more edge cases
    # ================================================================
    "insert_ctrl_u_row0_col0": {
        "description": "Ctrl-U at row 0 col 0 does nothing",
        "keys": "i\x15\x1b",
        "initial": "hello",
    },
    "insert_ctrl_u_preserves_after": {
        "description": "Ctrl-U preserves text after cursor",
        "keys": "lllli\x15\x1b",
        "initial": "abcdefgh",
    },
    "insert_ctrl_u_on_second_line": {
        "description": "Ctrl-U on second line deletes to start of that line",
        "keys": "jA\x15\x1b",
        "initial": "first\nsecond line here",
    },
    "insert_ctrl_u_join_lines": {
        "description": "Ctrl-U at col 0 on line 2 joins with line 1",
        "keys": "jI\x15\x1b",
        "initial": "abc\ndef",
    },

    # ================================================================
    # Insert mode Delete (forward) — more edge cases
    # ================================================================
    "insert_delete_join_next_line": {
        "description": "Delete at end of line joins with next line",
        "keys": "A\x1b[3~\x1b",
        "initial": "hello\nworld",
    },
    "insert_delete_last_line_end": {
        "description": "Delete at end of last line does nothing",
        "keys": "A\x1b[3~\x1b",
        "initial": "hello",
    },
    "insert_delete_empty_line": {
        "description": "Delete on empty line joins with next",
        "keys": "jI\x1b[3~\x1b",
        "initial": "abc\n\ndef",
    },
    "insert_delete_multiple": {
        "description": "Multiple Delete keys forward-delete consecutively",
        "keys": "i\x1b[3~\x1b[3~\x1b[3~\x1b",
        "initial": "abcde",
    },

    # ================================================================
    # Insert mode arrow keys — edge cases
    # ================================================================
    "insert_arrow_left_at_col0": {
        "description": "Left arrow at col 0 stays put",
        "keys": "i\x1b[D\x1b",
        "initial": "hello",
    },
    "insert_arrow_right_at_end": {
        "description": "Right arrow at end of line stays put",
        "keys": "A\x1b[C\x1b",
        "initial": "hello",
    },
    "insert_arrow_up_at_row0": {
        "description": "Up arrow at row 0 stays put",
        "keys": "i\x1b[A\x1b",
        "initial": "hello",
    },
    "insert_arrow_down_at_last_row": {
        "description": "Down arrow at last row stays put",
        "keys": "i\x1b[B\x1b",
        "initial": "hello",
    },
    "insert_arrow_up_col_clamp": {
        "description": "Up arrow clamps col to shorter line",
        "keys": "jA\x1b[A\x1b",
        "initial": "ab\nabcdef",
    },
    "insert_arrow_down_col_clamp": {
        "description": "Down arrow clamps col to shorter line",
        "keys": "A\x1b[B\x1b",
        "initial": "abcdef\nab",
    },
    "insert_arrows_navigate_and_type": {
        "description": "Use arrows to navigate then insert text",
        "keys": "A\x1b[D\x1b[DX\x1b",
        "initial": "abcde",
    },

    # ================================================================
    # Insert mode Ctrl-H / Ctrl-J (aliases for Backspace / Enter)
    # ================================================================
    "insert_ctrl_h_basic": {
        "description": "Ctrl-H in insert mode works like Backspace",
        "keys": "A\x08\x1b",
        "initial": "abcde",
    },
    "insert_ctrl_h_at_start": {
        "description": "Ctrl-H at start of first line does nothing",
        "keys": "i\x08\x1b",
        "initial": "abc",
    },
    "insert_ctrl_h_join_lines": {
        "description": "Ctrl-H at start of line 2 joins with line 1",
        "keys": "jI\x08\x1b",
        "initial": "abc\ndef",
    },
    "insert_ctrl_j_basic": {
        "description": "Ctrl-J in insert mode splits line like Enter",
        "keys": "lli\x0a\x1b",
        "initial": "abcde",
    },
    "insert_ctrl_j_at_end": {
        "description": "Ctrl-J at end of line opens new line below",
        "keys": "A\x0a\x1b",
        "initial": "hello",
    },

    # ================================================================
    # Replace mode Ctrl-H / Ctrl-J
    # ================================================================
    "replace_ctrl_j": {
        "description": "Ctrl-J in replace mode splits line",
        "keys": "llR\x0a\x1b",
        "initial": "abcde",
    },
    "replace_ctrl_h_basic": {
        "description": "Ctrl-H in replace mode moves back",
        "keys": "llRxy\x08\x08\x1b",
        "initial": "abcde",
    },

    # ================================================================
    # Ctrl-A / Ctrl-X — exhaustive edge cases
    # ================================================================
    "ctrl_a_no_number": {
        "description": "Ctrl-A on line with no number does nothing",
        "keys": "\x01",
        "initial": "no numbers here",
    },
    "ctrl_a_cursor_past_all_numbers": {
        "description": "Ctrl-A when cursor is past all numbers",
        "keys": "$\x01",
        "initial": "42 abc",
    },
    "ctrl_a_on_negative": {
        "description": "Ctrl-A on -1 makes 0",
        "keys": "\x01",
        "initial": "-1",
    },
    "ctrl_x_on_1_to_0": {
        "description": "Ctrl-X on 1 makes 0",
        "keys": "\x18",
        "initial": "1",
    },
    "ctrl_x_on_0_to_negative": {
        "description": "Ctrl-X on 0 makes -1",
        "keys": "\x18",
        "initial": "0",
    },
    "ctrl_a_large_count": {
        "description": "100 Ctrl-A increments by 100",
        "keys": "100\x01",
        "initial": "0",
    },
    "ctrl_a_second_number": {
        "description": "Ctrl-A on second number when cursor is between them",
        "keys": "www\x01",
        "initial": "a 10 20 b",
    },
    "ctrl_x_negative_further": {
        "description": "Ctrl-X on -5 makes -6",
        "keys": "\x18",
        "initial": "-5",
    },
    "ctrl_a_dot_with_count_override": {
        "description": "3 Ctrl-A then 5. overrides count to 5",
        "keys": "3\x015.",
        "initial": "0",
    },
    "ctrl_a_cursor_on_digit": {
        "description": "Ctrl-A with cursor directly on a digit",
        "keys": "ll\x01",
        "initial": "a 42 b",
    },
    "ctrl_x_multi_digit": {
        "description": "Ctrl-X on 100 makes 99",
        "keys": "\x18",
        "initial": "100",
    },
    "ctrl_a_number_at_end": {
        "description": "Ctrl-A on number at end of line",
        "keys": "$\x01",
        "initial": "val 7",
    },
    "ctrl_a_empty_line": {
        "description": "Ctrl-A on empty line does nothing",
        "keys": "j\x01",
        "initial": "abc\n\ndef",
    },
    "ctrl_a_undo": {
        "description": "Ctrl-A then undo restores original",
        "keys": "\x01u",
        "initial": "42",
    },
    "ctrl_x_undo": {
        "description": "Ctrl-X then undo restores original",
        "keys": "\x18u",
        "initial": "42",
    },
    "ctrl_a_multiple_numbers_cursor_at_start": {
        "description": "Ctrl-A at start increments first number found",
        "keys": "\x01",
        "initial": "abc 10 20 30",
    },

    # ================================================================
    # Sentence motions () — exhaustive
    # ================================================================
    "paren_right_multiple_on_line": {
        "description": ") with multiple sentences on one line",
        "keys": "))",
        "initial": "One. Two. Three.",
    },
    "paren_right_at_end_no_move": {
        "description": ") at end of last sentence doesn't move",
        "keys": "f.)",
        "initial": "Only sentence.",
    },
    "paren_left_multiple_on_line": {
        "description": "( from end walks back through sentences",
        "keys": "$(((",
        "initial": "One. Two. Three. Four.",
    },
    "paren_right_question_mark": {
        "description": ") recognizes ? as sentence ending",
        "keys": ")",
        "initial": "Really?  Yes indeed.",
    },
    "paren_right_exclamation": {
        "description": ") recognizes ! as sentence ending",
        "keys": ")",
        "initial": "Wow!  Amazing.",
    },
    "paren_right_closing_quotes": {
        "description": ") skips closing chars after punctuation",
        "keys": ")",
        "initial": "He said \"hello.\" Next sentence.",
    },
    "paren_left_at_buffer_start": {
        "description": "( at buffer start doesn't move",
        "keys": "(",
        "initial": "Hello world.",
    },
    "paren_right_across_multiple_lines": {
        "description": ") crosses multiple lines to find next sentence",
        "keys": ")",
        "initial": "First sentence.\nNot ending here\nSecond sentence.",
    },
    "paren_right_two_blank_lines": {
        "description": ") treats each blank line as boundary",
        "keys": "))",
        "initial": "Para one.\n\n\nPara two.",
    },
    "paren_left_across_blank": {
        "description": "( backward across blank line finds sentence",
        "keys": "G(",
        "initial": "Sentence one.\n\nSentence two.",
    },
    "d_paren_left": {
        "description": "d( deletes backward to sentence start",
        "keys": "$d(",
        "initial": "First. Second here.",
    },
    "c_paren_right": {
        "description": "c) changes to next sentence",
        "keys": "c)CHANGED\x1b",
        "initial": "Hello world. Next part.",
    },
    "y_paren_right_p": {
        "description": "y) yanks to next sentence, p pastes",
        "keys": "y)$p",
        "initial": "Hello.  World.",
    },
    "paren_right_sentence_ending_at_eol": {
        "description": ") when sentence ends at end of line",
        "keys": ")",
        "initial": "End here.\nNew start.",
    },
    "2_paren_left": {
        "description": "2( jumps back two sentences",
        "keys": "$2(",
        "initial": "One. Two. Three.",
    },

    # ================================================================
    # Jump list (Ctrl-O / Ctrl-I)
    # ================================================================
    "ctrl_o_after_G": {
        "description": "G then Ctrl-O returns to start",
        "keys": "G\x0f",
        "initial": "line1\nline2\nline3\nline4\nline5",
    },
    "ctrl_i_after_ctrl_o": {
        "description": "Ctrl-I goes forward after Ctrl-O",
        "keys": "G\x0f\x09",
        "initial": "line1\nline2\nline3\nline4\nline5",
    },
    "ctrl_o_multiple_jumps": {
        "description": "Multiple G/gg jumps, Ctrl-O walks back",
        "keys": "Ggg4G\x0f\x0f",
        "initial": "line1\nline2\nline3\nline4\nline5",
    },
    "ctrl_o_empty_jumplist": {
        "description": "Ctrl-O with no jumps does nothing",
        "keys": "\x0f",
        "initial": "hello",
    },
    "ctrl_i_at_end": {
        "description": "Ctrl-I at end of jump list does nothing",
        "keys": "\x09",
        "initial": "hello",
    },
    "ctrl_o_after_search": {
        "description": "Search then Ctrl-O returns to pre-search pos",
        "keys": "/line4\nj\x0f",
        "initial": "line1\nline2\nline3\nline4\nline5",
    },
    "ctrl_o_after_star": {
        "description": "* then Ctrl-O returns to start",
        "keys": "*\x0f",
        "initial": "foo bar foo baz foo",
    },
    "ctrl_o_after_hash": {
        "description": "# then Ctrl-O returns to original position",
        "keys": "$b#\x0f",
        "initial": "foo bar foo baz foo",
    },
    "ctrl_o_after_gd": {
        "description": "gd then Ctrl-O returns to original position",
        "keys": "jjwgd\x0f",
        "initial": "abc def\nghi jkl\nmno abc",
    },
    "ctrl_o_ctrl_i_round_trip": {
        "description": "Ctrl-O then Ctrl-I returns to same spot",
        "keys": "3G\x0f\x09",
        "initial": "aaa\nbbb\nccc\nddd\neee",
    },

    # ================================================================
    # Change list (g; / g,)
    # ================================================================
    "g_semicolon_single_edit": {
        "description": "g; after one edit jumps back to edit pos",
        "keys": "jAx\x1bGg;",
        "initial": "aaa\nbbb\nccc\nddd",
    },
    "g_semicolon_multiple_edits": {
        "description": "g; twice walks back through two edit positions",
        "keys": "iA\x1bjjAx\x1bGg;g;",
        "initial": "aaa\nbbb\nccc\nddd",
    },
    "g_comma_forward": {
        "description": "g, goes forward in change list after g;",
        "keys": "iA\x1bjjAx\x1bGg;g;g,",
        "initial": "aaa\nbbb\nccc\nddd",
    },
    "g_semicolon_at_oldest": {
        "description": "g; at oldest change stops",
        "keys": "Ax\x1bg;g;g;",
        "initial": "hello",
    },
    "g_comma_at_newest": {
        "description": "g, at newest change stops",
        "keys": "Ax\x1bg,",
        "initial": "hello",
    },
    "g_semicolon_no_changes": {
        "description": "g; with no changes does nothing",
        "keys": "g;",
        "initial": "hello",
    },

    # ================================================================
    # gd — additional edge cases
    # ================================================================
    "gd_word_not_found": {
        "description": "gd on unique word at start stays at cursor",
        "keys": "gd",
        "initial": "unique abc def",
    },
    "gd_sets_search_pattern": {
        "description": "gd sets search pattern, n finds next occurrence",
        "keys": "jjwgdn",
        "initial": "abc def\nghi jkl\nmno abc",
    },
    "gd_ctrl_o_returns": {
        "description": "gd then Ctrl-O returns to original position",
        "keys": "jjwgd\x0f",
        "initial": "abc def\nghi jkl\nmno abc",
    },
    "gd_on_first_line": {
        "description": "gd on word whose first occurrence is current line",
        "keys": "wgd",
        "initial": "abc hello xyz\nhello again",
    },
    "gd_multiline_first_occurrence": {
        "description": "gd jumps from line 5 to first occurrence on line 1",
        "keys": "4Ggd",
        "initial": "target = 1\nfoo = 2\nbar = 3\nbaz = target + 1\nqux = 5",
    },

    # ================================================================
    # Interaction: Delete in visual mode (existing x alias)
    # ================================================================
    "visual_delete_key": {
        "description": "Delete in visual mode deletes selection like x",
        "keys": "vll\x1b[3~",
        "initial": "abcdefgh",
    },

    # ================================================================
    # Interaction: () motions in visual mode
    # ================================================================
    "visual_paren_right": {
        "description": ") extends visual selection to next sentence",
        "keys": "v)",
        "initial": "Hello world.  Next sentence.",
    },
    "visual_paren_left": {
        "description": "( extends visual selection backward",
        "keys": "$v(",
        "initial": "First.  Second here.",
    },

    # ================================================================
    # Interaction: Ctrl-A/X dot repeat with counts
    # ================================================================
    "ctrl_a_dot_repeat_3_times": {
        "description": "Ctrl-A then 3 dots increments 4 total",
        "keys": "\x01...",
        "initial": "0",
    },
    "ctrl_x_dot_repeat_3_times": {
        "description": "Ctrl-X then 3 dots decrements 4 total",
        "keys": "\x18...",
        "initial": "10",
    },
    "ctrl_a_count_dot": {
        "description": "5Ctrl-A then dot repeats 5 increment",
        "keys": "5\x01.",
        "initial": "0",
    },

    # ================================================================
    # Interaction: insert mode keys during count-insert
    # ================================================================
    "count_insert_with_ctrl_w": {
        "description": "3i with Ctrl-W: Ctrl-W replayed in each insert",
        "keys": "3ifoo bar\x17\x1b",
        "initial": "",
    },
    "count_insert_with_arrows": {
        "description": "2i with arrow navigation, replayed twice",
        "keys": "2iab\x1b[Dc\x1b",
        "initial": "xyz",
    },
    "count_insert_with_ctrl_h": {
        "description": "2i with Ctrl-H, replayed",
        "keys": "2iab\x08\x1b",
        "initial": "xyz",
    },
    "count_insert_with_ctrl_j": {
        "description": "2i with Ctrl-J (Enter), replayed",
        "keys": "2ix\x0a\x1b",
        "initial": "abc",
    },
    "count_insert_with_delete_fwd": {
        "description": "2i with Delete key, replayed",
        "keys": "2i\x1b[3~Y\x1b",
        "initial": "abcde",
    },

    # ================================================================
    # Interaction: Q inside macro
    # ================================================================
    "Q_inside_another_macro": {
        "description": "Macro that contains Q (replays last macro within macro)",
        "keys": "qaiX\x1bqqbjQ\x1bqj@b",
        "initial": "aaa\nbbb\nccc",
    },

    # ================================================================
    # Interaction: gd after search (pattern changes)
    # ================================================================
    "gd_after_search": {
        "description": "gd overrides previous search pattern",
        "keys": "/def\njwgdn",
        "initial": "abc def\nabc ghi\nabc def",
    },

    # ================================================================
    # Multiple sentence motions combined with operators
    # ================================================================
    "d_2_paren_right": {
        "description": "d2) deletes two sentences",
        "keys": "d2)",
        "initial": "One. Two. Three.",
    },

    # ================================================================
    # Ctrl-A on numbers in various positions
    # ================================================================
    "ctrl_a_number_mid_word": {
        "description": "Ctrl-A finds number embedded in text",
        "keys": "\x01",
        "initial": "v2beta",
    },
    "ctrl_a_negative_count": {
        "description": "10 Ctrl-X on 5 makes -5",
        "keys": "10\x18",
        "initial": "5",
    },

    # ================================================================
    # Jump list: multiple operations build up history
    # ================================================================
    "jumplist_search_then_G_then_back": {
        "description": "Search + G + Ctrl-O twice walks back",
        "keys": "/line3\nG\x0f\x0f",
        "initial": "line1\nline2\nline3\nline4\nline5",
    },
    "jumplist_gg_then_back": {
        "description": "G then gg then Ctrl-O returns to bottom",
        "keys": "Ggg\x0f",
        "initial": "aaa\nbbb\nccc\nddd\neee",
    },

    # ================================================================
    # Replace mode: R then use the new keys
    # ================================================================
    "replace_then_escape": {
        "description": "R overwrites then Escape leaves replaced text",
        "keys": "RXYZ\x1b",
        "initial": "abcde",
    },

    # ================================================================
    # Sentence motion: period not followed by space isn't sentence end
    # ================================================================
    "paren_right_period_no_space": {
        "description": ") doesn't treat period without trailing space as sentence end",
        "keys": ")",
        "initial": "file.txt is here. Next.",
    },
    "paren_right_abbreviation": {
        "description": ") skips abbreviation-like periods mid-line",
        "keys": ")",
        "initial": "Dr.Smith is here. Next.",
    },

    # ================================================================
    # Ctrl-A/X cursor positioning
    # ================================================================
    "ctrl_a_cursor_on_last_digit": {
        "description": "Ctrl-A leaves cursor on last digit of result",
        "keys": "\x01",
        "initial": "9",
    },
    "ctrl_a_999_to_1000": {
        "description": "Ctrl-A on 999 → 1000, cursor on last digit",
        "keys": "\x01",
        "initial": "999",
    },
    "ctrl_x_100_to_99": {
        "description": "Ctrl-X on 100 → 99, cursor on last digit",
        "keys": "\x18",
        "initial": "100",
    },

    # ================================================================
    # Sentence motion edge case: sentence at exact start of buffer
    # ================================================================
    "paren_right_from_start": {
        "description": ") from very start of buffer finds next sentence",
        "keys": ")",
        "initial": "Start.  Next.",
    },
    "paren_left_second_sentence": {
        "description": "( from second sentence goes to its start",
        "keys": "w)(",
        "initial": "Start.  Next.  Third.",
    },
}
