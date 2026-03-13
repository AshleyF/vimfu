"""
Exhaustive test suite for Vim ex (colon) commands — editing operations.

Covers:
  :d[elete]   — delete lines
  :y[ank]     — yank lines (verified via put)
  :m[ove]     — move lines to target address
  :co[py]/:t  — copy lines to target address
  :j[oin]     — join lines
  :norm[al]   — execute normal-mode commands on range
  :g[lobal]   — execute command on matching lines
  :v[global]  — execute command on NON-matching lines
  Range addresses: ., $, N, +N, -N, %, '<,'>, /pat/, ?pat?
  :pu[t]      — additional put cases
  :s (substitute) — additional edge cases beyond test_new_features.py
  :marks      — display marks
  :reg[isters] — display registers
"""

TENLINES = "\n".join(f"Line {i:02d} content" for i in range(1, 11))
FIVELINES = "\n".join(f"Line {i:02d} content" for i in range(1, 6))
TWENTYLINES = "\n".join(f"Line {i:02d} content" for i in range(1, 21))
ALPHA = "alpha\nbeta\ngamma\ndelta\nepsilon"
FRUITS = "apple\nbanana\ncherry\ndate\nelderberry"
MIXED = "foo bar\nhello world\nfoo baz\nhello vim\nfoo end"
NUMBERS = "one 1\ntwo 2\nthree 3\nfour 4\nfive 5"
DUPES = "aaa\nbbb\naaa\nccc\nbbb\naaa"
INDENT_LINES = "  alpha\n    beta\n  gamma\n    delta\n  epsilon"
CODE = "if true\n  print a\n  print b\nend\nif false\n  print c\nend"

# Note: Clipboard registers (*, +, %) will appear in :reg/:di output since
# the user's nvim config uses the system clipboard. Display test cases should
# account for this by using compareMode='colors' to only check color patterns.
NVIM_CMD = 'nvim'

CASES = {
    # ═══════════════════════════════════════════════════════════════
    #  :d[elete] — delete lines
    # ═══════════════════════════════════════════════════════════════

    # ── Basic :d (current line) ──
    "delete_current_line": {
        "keys": ":d\r",
        "initial": FIVELINES,
    },
    "delete_abbrev": {
        "keys": ":de\r",
        "initial": FIVELINES,
    },
    "delete_full_word": {
        "keys": ":delete\r",
        "initial": FIVELINES,
    },

    # ── :d from different cursor positions ──
    "delete_line_from_middle": {
        "keys": "2j:d\r",
        "initial": FIVELINES,
    },
    "delete_last_line": {
        "keys": "G:d\r",
        "initial": FIVELINES,
    },
    "delete_first_line": {
        "keys": ":1d\r",
        "initial": FIVELINES,
    },

    # ── :Nd — delete specific line ──
    "delete_line_3": {
        "keys": ":3d\r",
        "initial": FIVELINES,
    },
    "delete_line_5": {
        "keys": ":5d\r",
        "initial": FIVELINES,
    },
    "delete_line_1": {
        "keys": ":1d\r",
        "initial": FIVELINES,
    },

    # ── Range :N,Md — delete range ──
    "delete_range_2_4": {
        "keys": ":2,4d\r",
        "initial": FIVELINES,
    },
    "delete_range_1_3": {
        "keys": ":1,3d\r",
        "initial": FIVELINES,
    },
    "delete_range_3_5": {
        "keys": ":3,5d\r",
        "initial": FIVELINES,
    },
    "delete_range_1_5_all": {
        "keys": ":1,5d\r",
        "initial": FIVELINES,
    },
    "delete_range_1_dollar": {
        "keys": ":1,$d\r",
        "initial": FIVELINES,
    },

    # ── :% d — delete all lines ──
    "delete_percent_all": {
        "keys": ":%d\r",
        "initial": FIVELINES,
    },

    # ── :d with dot (current line) ──
    "delete_dot": {
        "keys": "2j:.d\r",
        "initial": FIVELINES,
    },
    "delete_dot_to_dollar": {
        "keys": "2j:.,$d\r",
        "initial": FIVELINES,
    },
    "delete_dot_to_plus2": {
        "keys": "1j:.,+2d\r",
        "initial": FIVELINES,
    },

    # ── :d on single line file ──
    "delete_single_line": {
        "keys": ":d\r",
        "initial": "only line",
    },

    # ── :d on empty file ──
    "delete_empty_file": {
        "keys": ":d\r",
        "initial": "",
    },

    # ── :d to named register ──
    "delete_to_register_a": {
        "keys": ":d a\r",
        "initial": FIVELINES,
    },
    "delete_range_to_register": {
        "keys": ":2,4d a\r",
        "initial": FIVELINES,
    },

    # ── Verify deleted text goes to register (delete then put) ──
    "delete_then_put": {
        "keys": ":3d\rG:pu\r",
        "initial": FIVELINES,
    },
    "delete_range_then_put": {
        "keys": ":2,3d\rG:pu\r",
        "initial": FIVELINES,
    },
    "delete_to_reg_a_then_put_a": {
        "keys": ":d a\rG:pu a\r",
        "initial": FIVELINES,
    },

    # ═══════════════════════════════════════════════════════════════
    #  :y[ank] — yank lines (verify via p)
    # ═══════════════════════════════════════════════════════════════

    # ── Basic :y (yank current line, then paste) ──
    "yank_current_then_put": {
        "keys": ":y\rGp",
        "initial": FIVELINES,
    },
    "yank_line_3_then_put": {
        "keys": ":3y\rGp",
        "initial": FIVELINES,
    },

    # ── Range yank ──
    "yank_range_2_4_then_put": {
        "keys": ":2,4y\rGp",
        "initial": FIVELINES,
    },
    "yank_all_then_put": {
        "keys": ":%y\rGp",
        "initial": FIVELINES,
    },
    "yank_dollar_then_put": {
        "keys": ":$y\rGp",
        "initial": FIVELINES,
    },

    # ── :y to named register ──
    "yank_to_reg_a_then_put": {
        "keys": ":2y a\rG\"ap",
        "initial": FIVELINES,
    },
    "yank_range_to_reg_b": {
        "keys": ":1,3y b\rG\"bp",
        "initial": FIVELINES,
    },

    # ── Yank doesn't change buffer ──
    "yank_leaves_buffer_intact": {
        "keys": ":3y\r",
        "initial": FIVELINES,
    },
    "yank_range_leaves_buffer_intact": {
        "keys": ":2,4y\r",
        "initial": FIVELINES,
    },

    # ═══════════════════════════════════════════════════════════════
    #  :m[ove] — move lines
    # ═══════════════════════════════════════════════════════════════

    # ── Move current line down ──
    "move_line_to_3": {
        "keys": ":m3\r",
        "initial": FIVELINES,
    },
    "move_line_to_end": {
        "keys": ":m$\r",
        "initial": FIVELINES,
    },
    "move_line_to_0": {
        "keys": "2j:m0\r",
        "initial": FIVELINES,
    },

    # ── Move specific line ──
    "move_line3_to_end": {
        "keys": ":3m$\r",
        "initial": FIVELINES,
    },
    "move_line5_to_0": {
        "keys": ":5m0\r",
        "initial": FIVELINES,
    },
    "move_line1_to_3": {
        "keys": ":1m3\r",
        "initial": FIVELINES,
    },

    # ── Move range ──
    "move_range_2_3_to_end": {
        "keys": ":2,3m$\r",
        "initial": FIVELINES,
    },
    "move_range_4_5_to_0": {
        "keys": ":4,5m0\r",
        "initial": FIVELINES,
    },
    "move_range_1_2_to_4": {
        "keys": ":1,2m4\r",
        "initial": FIVELINES,
    },

    # ── Move with dot address ──
    "move_dot_to_end": {
        "keys": "2j:.m$\r",
        "initial": FIVELINES,
    },

    # ═══════════════════════════════════════════════════════════════
    #  :co[py] / :t — copy lines
    # ═══════════════════════════════════════════════════════════════

    # ── :copy — basic ──
    "copy_line_to_end": {
        "keys": ":co$\r",
        "initial": FIVELINES,
    },
    "copy_line_to_0": {
        "keys": "2j:co0\r",
        "initial": FIVELINES,
    },
    "copy_line_to_3": {
        "keys": ":co3\r",
        "initial": FIVELINES,
    },

    # ── :t alias ──
    "t_alias_to_end": {
        "keys": ":t$\r",
        "initial": FIVELINES,
    },
    "t_alias_to_0": {
        "keys": ":t0\r",
        "initial": FIVELINES,
    },

    # ── :copy specific line ──
    "copy_line3_to_end": {
        "keys": ":3co$\r",
        "initial": FIVELINES,
    },
    "copy_line1_to_4": {
        "keys": ":1t4\r",
        "initial": FIVELINES,
    },

    # ── :copy range ──
    "copy_range_2_4_to_end": {
        "keys": ":2,4co$\r",
        "initial": FIVELINES,
    },
    "copy_range_1_3_to_0": {
        "keys": ":1,3t0\r",
        "initial": FIVELINES,
    },
    "copy_percent_to_end": {
        "keys": ":%t$\r",
        "initial": FIVELINES,
    },

    # ── Copy with dot address ──
    "copy_dot_to_end": {
        "keys": "2j:.t$\r",
        "initial": FIVELINES,
    },

    # ═══════════════════════════════════════════════════════════════
    #  :j[oin] — join lines
    # ═══════════════════════════════════════════════════════════════

    # ── Basic join ──
    "join_current_two_lines": {
        "keys": ":j\r",
        "initial": FIVELINES,
    },
    "join_full_word": {
        "keys": ":join\r",
        "initial": FIVELINES,
    },

    # ── Join range ──
    "join_range_1_3": {
        "keys": ":1,3j\r",
        "initial": FIVELINES,
    },
    "join_range_2_5": {
        "keys": ":2,5j\r",
        "initial": FIVELINES,
    },
    "join_all_lines": {
        "keys": ":%j\r",
        "initial": FIVELINES,
    },

    # ── Join with bang (no spaces) ──
    "join_bang_current": {
        "keys": ":j!\r",
        "initial": FIVELINES,
    },
    "join_range_bang": {
        "keys": ":1,3j!\r",
        "initial": FIVELINES,
    },
    "join_all_bang": {
        "keys": ":%j!\r",
        "initial": FIVELINES,
    },

    # ── Join from middle of file ──
    "join_from_line3": {
        "keys": "2j:j\r",
        "initial": FIVELINES,
    },

    # ═══════════════════════════════════════════════════════════════
    #  :norm[al] — run normal-mode keys on range
    # ═══════════════════════════════════════════════════════════════

    # ── Basic normal ──
    "normal_append_text": {
        "keys": ":%norm Aend\r",
        "initial": FIVELINES,
    },
    "normal_delete_first_word": {
        "keys": ":%norm dw\r",
        "initial": "hello world\nfoo bar\nbaz qux",
    },
    "normal_range_2_4": {
        "keys": ":2,4norm Aend\r",
        "initial": FIVELINES,
    },
    "normal_insert_at_start": {
        "keys": ":%norm I>> \r",
        "initial": ALPHA,
    },
    "normal_dd_on_range": {
        "keys": ":2,4norm dd\r",
        "initial": FIVELINES,
    },
    "normal_x_on_range": {
        "keys": ":%norm x\r",
        "initial": ALPHA,
    },

    # ═══════════════════════════════════════════════════════════════
    #  :g[lobal] — execute command on matching lines
    # ═══════════════════════════════════════════════════════════════

    # ── :g/pattern/d — delete matching lines ──
    "global_delete_matching": {
        "keys": ":g/foo/d\r",
        "initial": MIXED,
    },
    "global_delete_hello": {
        "keys": ":g/hello/d\r",
        "initial": MIXED,
    },
    "global_delete_all_aaa": {
        "keys": ":g/aaa/d\r",
        "initial": DUPES,
    },

    # ── :g/pattern/normal ──
    "global_normal_append": {
        "keys": ":g/foo/norm A!\r",
        "initial": MIXED,
    },

    # ── :v[global] — delete NON-matching lines ──
    "vglobal_keep_foo": {
        "keys": ":v/foo/d\r",
        "initial": MIXED,
    },
    "vglobal_keep_hello": {
        "keys": ":v/hello/d\r",
        "initial": MIXED,
    },

    # ── :g with range ──
    "global_range_delete": {
        "keys": ":1,3g/foo/d\r",
        "initial": MIXED,
    },

    # ═══════════════════════════════════════════════════════════════
    #  :substitute — additional edge cases
    # ═══════════════════════════════════════════════════════════════

    # ── Range addressing with :s ──
    "sub_line3_only": {
        "keys": ":3s/Line/ROW\r",
        "initial": TENLINES,
    },
    "sub_range_2_4": {
        "keys": ":2,4s/content/stuff\r",
        "initial": TENLINES,
    },
    "sub_dot_range": {
        "keys": "4j:.,+2s/content/stuff\r",
        "initial": TENLINES,
    },
    "sub_dot_to_dollar": {
        "keys": "7j:.,$s/content/DATA/g\r",
        "initial": TENLINES,
    },

    # ── :s with empty replacement (delete pattern) ──
    "sub_delete_word": {
        "keys": ":%s/content//g\r",
        "initial": FIVELINES,
    },

    # ── :s with special chars in replacement ──
    "sub_replace_with_ampersand": {
        "keys": ":%s/Line/[&]/g\r",
        "initial": FIVELINES,
    },

    # ── :s repeat last substitution ──
    "sub_repeat_with_s": {
        "keys": ":s/Line/Row\rj:s\r",
        "initial": FIVELINES,
    },

    # ── :s with count (single line, first only) ──
    "sub_first_occurrence_only": {
        "keys": ":s/o/O\r",
        "initial": "foo boo moo",
    },
    "sub_global_flag": {
        "keys": ":s/o/O/g\r",
        "initial": "foo boo moo",
    },

    # ── :s with n flag (report count, no sub) ──
    "sub_n_flag_count": {
        "keys": ":%s/Line//gn\r",
        "initial": FIVELINES,
    },

    # ═══════════════════════════════════════════════════════════════
    #  Range address forms
    # ═══════════════════════════════════════════════════════════════

    # ── Plus and minus offsets ──
    "range_plus_offset": {
        "keys": ":1,2+2d\r",
        "initial": FIVELINES,
    },
    "range_minus_offset": {
        "keys": ":$-2,$d\r",
        "initial": FIVELINES,
    },
    "range_dot_plus": {
        "keys": "2j:.,.+1d\r",
        "initial": FIVELINES,
    },

    # ═══════════════════════════════════════════════════════════════
    #  :pu[t] — additional put cases
    # ═══════════════════════════════════════════════════════════════

    "put_after_yank": {
        "keys": "yy:pu\r",
        "initial": ALPHA,
    },
    "put_bang_above": {
        "keys": "yy:pu!\r",
        "initial": ALPHA,
    },
    "put_at_line_3": {
        "keys": "yy:3pu\r",
        "initial": FIVELINES,
    },
    "put_from_named_reg": {
        "keys": "\"ayy:pu a\r",
        "initial": ALPHA,
    },

    # ═══════════════════════════════════════════════════════════════
    #  :marks — display marks list
    # ═══════════════════════════════════════════════════════════════

    "marks_no_marks": {
        "keys": ":marks\r",
        "initial": ALPHA,
    },
    "marks_with_a_mark": {
        "keys": "majj:marks\r",
        "initial": ALPHA,
    },
    "marks_multiple": {
        "keys": "ma2jmb:marks\r",
        "initial": FIVELINES,
    },

    # ═══════════════════════════════════════════════════════════════
    #  :reg[isters] / :di[splay] — show register contents
    #  Note: verified via :put since :reg display includes system
    #  registers ("*, "+, "%) which vary by environment
    # ═══════════════════════════════════════════════════════════════

    "registers_empty": {
        # Nothing yanked or deleted — :put should produce empty line
        "keys": ":pu\r",
        "initial": ALPHA,
    },
    "registers_after_yank": {
        # yy puts line in "" and "0 — :put inserts it below
        "keys": "yy:pu\r",
        "initial": ALPHA,
    },
    "registers_after_delete": {
        # dd puts line in "" and "1 — :put inserts it below
        "keys": "dd:pu\r",
        "initial": ALPHA,
    },
    "registers_named": {
        # "ayy puts in "a — :pu a inserts it below
        "keys": "\"ayy:pu a\r",
        "initial": ALPHA,
    },

    # ═══════════════════════════════════════════════════════════════
    #  :di[splay] — screen capture of register display
    #  With clipboard provider disabled, output is deterministic.
    #  NOTE: skipped for automated comparison — nvim still shows
    #  system clipboard registers ("*, "+, "%) that the simulator
    #  does not have.  Ground truth data used to verify colors.
    # ═══════════════════════════════════════════════════════════════

    "display_after_yank": {
        # yy then :di — shows "" and "0 with yanked text
        "keys": "yy:di\r",
        "initial": ALPHA,
        "settle": 0.5,
    },
    "display_after_delete": {
        # dd then :di — shows "" and "1 with deleted text
        "keys": "dd:di\r",
        "initial": ALPHA,
        "settle": 0.5,
    },
    "display_named_register": {
        # "ayy then :di — shows "a register
        "keys": "\"ayy:di\r",
        "initial": ALPHA,
        "settle": 0.5,
    },
    "display_search_register": {
        # search for 'beta' then :di — shows "/ register
        "keys": "/beta\r:di\r",
        "initial": ALPHA,
        "settle": 0.5,
    },
    "display_jumps": {
        # 3j then :jumps — screen capture of jump list display
        "keys": "3j:jumps\r",
        "initial": ALPHA,
        "settle": 0.5,
    },
    "display_changes": {
        # Delete a line then :changes — screen capture of change list
        "keys": "dd:changes\r",
        "initial": ALPHA,
        "settle": 0.5,
    },

    # ═══════════════════════════════════════════════════════════════
    #  :d then undo — verify undoable
    # ═══════════════════════════════════════════════════════════════

    "delete_line_then_undo": {
        "keys": ":d\ru",
        "initial": FIVELINES,
    },
    "delete_range_then_undo": {
        "keys": ":2,4d\ru",
        "initial": FIVELINES,
    },
    "move_then_undo": {
        "keys": ":1m$\ru",
        "initial": FIVELINES,
    },
    "copy_then_undo": {
        "keys": ":1t$\ru",
        "initial": FIVELINES,
    },
    "join_then_undo": {
        "keys": ":1,3j\ru",
        "initial": FIVELINES,
    },
    "global_delete_then_undo": {
        "keys": ":g/foo/d\ru",
        "initial": MIXED,
    },
    "normal_then_undo": {
        "keys": ":%norm dd\ru",
        "initial": FIVELINES,
    },

    # ═══════════════════════════════════════════════════════════════
    #  Visual range with ex commands
    # ═══════════════════════════════════════════════════════════════

    "visual_delete_range": {
        "keys": "jVjj:d\r",
        "initial": FIVELINES,
    },
    "visual_yank_range_then_put": {
        "keys": "jVjj:y\rGp",
        "initial": FIVELINES,
    },
    "visual_join_range": {
        "keys": "Vjj:j\r",
        "initial": FIVELINES,
    },
    "visual_join_bang": {
        "keys": "Vjj:j!\r",
        "initial": FIVELINES,
    },
    "visual_normal_range": {
        "keys": "jVjj:norm A!\r",
        "initial": FIVELINES,
    },
    "visual_copy_to_end": {
        "keys": "Vj:t$\r",
        "initial": FIVELINES,
    },
    "visual_move_to_end": {
        "keys": "Vj:m$\r",
        "initial": FIVELINES,
    },

    # ═══════════════════════════════════════════════════════════════
    #  Edge cases
    # ═══════════════════════════════════════════════════════════════

    # Single-line file operations
    "delete_only_line_in_file": {
        "keys": ":1d\r",
        "initial": "single",
    },
    "join_on_last_line": {
        "keys": "G:j\r",
        "initial": FIVELINES,
    },
    "move_line_to_itself": {
        "keys": ":2m2\r",
        "initial": FIVELINES,
    },
    "copy_line_to_itself": {
        "keys": ":2t2\r",
        "initial": FIVELINES,
    },

    # ── Unknown command ──
    "unknown_command": {
        "keys": ":foobar\r",
        "initial": ALPHA,
    },

    # ── Multiple ex commands in sequence ──
    "sequence_delete_two_lines": {
        "keys": ":1d\r:1d\r",
        "initial": FIVELINES,
    },
    "sequence_yank_then_put_bottom": {
        "keys": ":1y\r:$pu\r",
        "initial": FIVELINES,
    },
    "sequence_copy_and_delete": {
        "keys": ":1t$\r:1d\r",
        "initial": FIVELINES,
    },

    # ═══════════════════════════════════════════════════════════════
    #  :[range]> — shift lines right (indent)
    # ═══════════════════════════════════════════════════════════════
    "shift_right_current_line": {
        "keys": ":>\r",
        "initial": ALPHA,
    },
    "shift_right_line_3": {
        "keys": ":3>\r",
        "initial": ALPHA,
    },
    "shift_right_range": {
        "keys": ":2,4>\r",
        "initial": ALPHA,
    },
    "shift_right_all": {
        "keys": ":%>\r",
        "initial": ALPHA,
    },
    "shift_right_double": {
        "keys": ":2,3>>\r",
        "initial": ALPHA,
    },
    "shift_right_visual": {
        "keys": "Vjj:>\r",
        "initial": ALPHA,
    },

    # ═══════════════════════════════════════════════════════════════
    #  :[range]< — shift lines left (unindent)
    # ═══════════════════════════════════════════════════════════════
    "shift_left_current_line": {
        "keys": ":<\r",
        "initial": INDENT_LINES,
    },
    "shift_left_line_2": {
        "keys": ":2<\r",
        "initial": INDENT_LINES,
    },
    "shift_left_range": {
        "keys": ":1,3<\r",
        "initial": INDENT_LINES,
    },
    "shift_left_all": {
        "keys": ":%<\r",
        "initial": INDENT_LINES,
    },
    "shift_left_double": {
        "keys": ":2,3<<\r",
        "initial": INDENT_LINES,
    },
    "shift_left_visual": {
        "keys": "Vjj:<\r",
        "initial": INDENT_LINES,
    },

    # ═══════════════════════════════════════════════════════════════
    #  := — print line number
    # ═══════════════════════════════════════════════════════════════
    "equals_total_lines": {
        "keys": ":=\r",
        "initial": FIVELINES,
    },
    "equals_current_line": {
        "keys": ":.=\r",
        "initial": FIVELINES,
    },
    "equals_last_line": {
        "keys": ":$=\r",
        "initial": FIVELINES,
    },
    "equals_line_3": {
        "keys": ":3=\r",
        "initial": FIVELINES,
    },

    # ═══════════════════════════════════════════════════════════════
    #  :p[rint] — display lines
    # ═══════════════════════════════════════════════════════════════
    "print_current_line": {
        "keys": ":p\r",
        "initial": ALPHA,
    },
    "print_range": {
        "keys": ":1,3p\r",
        "initial": ALPHA,
    },
    "print_all": {
        "keys": ":%p\r",
        "initial": ALPHA,
    },
    "print_full_word": {
        "keys": ":print\r",
        "initial": ALPHA,
    },

    # ═══════════════════════════════════════════════════════════════
    #  :nu[mber] / :# — display lines with numbers
    # ═══════════════════════════════════════════════════════════════
    "number_current_line": {
        "keys": ":nu\r",
        "initial": ALPHA,
    },
    "number_range": {
        "keys": ":1,3nu\r",
        "initial": ALPHA,
    },
    "number_full_word": {
        "keys": ":number\r",
        "initial": ALPHA,
    },
    "hash_current_line": {
        "keys": ":#\r",
        "initial": ALPHA,
    },
    "hash_range": {
        "keys": ":1,3#\r",
        "initial": ALPHA,
    },
}
