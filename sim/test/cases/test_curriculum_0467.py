"""Tests for video range 0467-0476: :%norm recipes and macros."""

NAMES = "alice,30\nbob,25\ncarol,40\ndave,35\n"

LINES_FIVE = "alpha\nbeta\ngamma\ndelta\nepsilon"

CASES = {
    # ── 0468 :%norm ^x — delete first non-blank char of every line ─
    "norm_caret_x_delete_first": {
        "description": ":%norm ^x deletes the first non-blank char on every line",
        "keys": ":%norm ^x\r",
        "initial": "  hello\n  world\n  again\n",
    },

    # ── 0467 :%norm I// — comment every line ─────────────────
    "norm_I_comment_all": {
        "description": ":%norm I// inserts // at the start of every line",
        "keys": ":%norm I//\r",
        "initial": "line one\nline two\nline three\n",
    },

    # ── 0469 visual block comment with Ctrl-V + I ────────────
    "visual_block_comment_insert": {
        "description": "Ctrl-V 2j I// Esc inserts // on three lines at col 0",
        "keys": "\x162jI//\x1b",
        "initial": "line one\nline two\nline three\n",
    },

    # ── 0474 Record-and-apply macro: qa ... q then :%norm @a ─
    "record_apply_macro": {
        "description": "qa edits then q to stop; :%norm @a applies the macro to every line",
        # Macro: prepend ' " ' to each line.
        # qa I" Esc q to record. Then 2u to undo the demo edit on line 1.
        # Then :%norm @a to apply to all lines.
        "keys": "qaI\"\x1bq2u:%norm @a\r",
        "initial": NAMES,
    },

    # ── 0473 Useless underscore: _ goes to first non-blank ──
    "underscore_first_non_blank": {
        "description": "_ moves to first non-blank of current line",
        "keys": "j_",
        "initial": "first\n    indented\nthird\n",
    },
    "underscore_with_count": {
        "description": "3_ moves down 2 lines then to first non-blank",
        "keys": "3_",
        "initial": "first\n  two\n    three\nfourth\n",
    },
}
