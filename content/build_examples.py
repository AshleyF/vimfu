"""Generate all worked-example JSON files from a single Python source.

Authoring 100+ JSON files by hand is brutal. This module is the source
of truth: each example is a few lines of Python that build a valid
vimfu-content-example payload, which we then write out as JSON for the
renderer to consume.

Usage:
    python content/build_examples.py            # write all examples
    python content/build_examples.py grammar    # filter by id substring

Conventions:
- All examples default to a 40-col terminal with status row near bottom.
- Each frame is just (lines, cursor, keys, caption, narration, **opts).
- Status rows render as reverse video automatically.
- '~' lines auto-color blue (Vim's empty-buffer marker).

Run after editing -> regenerates content/examples/*.json.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "examples"

# ---------- builder helpers -------------------------------------------------

def F(lines, cursor=None, *, keys="", caption="", narration="",
      highlights=None, cols=40, rows=None, status=None, mode_line=None):
    """Build one frame entry.

    lines    : list of strings (top of file).
    cursor   : (row, col) tuple, or None for hidden.
    keys     : keystrokes that produced this frame (display-only).
    caption  : short caption shown above the screenshot.
    narration: prose that explains what's happening.
    highlights: list of dicts {row, col, len, fg?, bg?, b?, i?}
    status   : optional content for an auto-positioned status row.
               If given, status row is len(lines)+1 (file row 0..N, blank, status).
    mode_line: optional content for the line BELOW the status row
               (e.g. "-- INSERT --").
    """
    work_lines = list(lines)

    status_row_idx = None
    if status is not None:
        # Pad to leave at least one tilde row before the status line
        if len(work_lines) < 8:
            # Pad with tildes up to row 8
            while len(work_lines) < 8:
                work_lines.append("~")
        # Pad status: width = cols, left-justified caption
        status_text = (status if len(status) <= cols else status[:cols]).ljust(cols)
        status_row_idx = len(work_lines)
        work_lines.append(status_text)

    if mode_line is not None:
        work_lines.append(mode_line)

    if rows is None:
        rows = max(len(work_lines), 10)
        # Ensure we have a couple of trailing tildes if no status line
        if status is None and rows < 10:
            rows = 10

    # Build compact frame
    compact = {
        "rows": rows,
        "cols": cols,
        "lines": work_lines,
    }
    if cursor is not None:
        compact["cursor"] = [cursor[0], cursor[1]]
    if highlights:
        compact["highlights"] = highlights
    if status_row_idx is not None:
        compact["statusRow"] = status_row_idx

    out = {"compact": compact}
    if caption: out["caption"] = caption
    if narration: out["narration"] = narration
    if keys: out["keys"] = keys
    return out


def E(eid, title, summary, topic, frames):
    """Build a complete example payload."""
    return {
        "format": "vimfu-content-example",
        "version": 1,
        "id": eid,
        "title": title,
        "summary": summary,
        "topic": topic,
        "frames": frames,
    }


def hl(row, col, length=1, **flags):
    """Highlight helper."""
    h = {"row": row, "col": col, "len": length}
    h.update(flags)
    return h


# Common "INSERT mode" status row mode_line value
INSERT_LINE = "-- INSERT --".ljust(40)
VISUAL_LINE = "-- VISUAL --".ljust(40)
VBLOCK_LINE = "-- VISUAL BLOCK --".ljust(40)
VLINE_LINE = "-- VISUAL LINE --".ljust(40)
REPLACE_LINE = "-- REPLACE --".ljust(40)


# ---------- the examples ---------------------------------------------------
#
# Order matches content/parts/*. Each variable is one example.
# Naming: e_<short-id> = E(...)
# Topics that don't need examples are simply omitted; the wire step skips them.

EXAMPLES = []


def add(ex):
    EXAMPLES.append(ex)
    return ex


# ============ Part 1 — Foundations ==========================================

add(E("foundations.modes",
    "Normal -> Insert -> Normal",
    "The mode transition every editing change goes through.",
    "foundations.modes-overview",
    [
        F(["Hello world", ""], cursor=(0,6),
          status="hi.txt                   1,7            All",
          caption="Normal mode. Cursor as a block on the space.",
          narration="When you open a file, you start in Normal mode. Keystrokes are commands."),
        F(["Hello, vim world", ""], cursor=(0,11), keys="i, vim",
          status="hi.txt [+]               1,12           All",
          mode_line=INSERT_LINE,
          highlights=[hl(11, 0, 12, b=True)],  # bolded mode line below status
          caption="i then ', vim' — Insert mode, text added.",
          narration="i enters Insert at the cursor; subsequent keys produce text. The status line below advertises the mode."),
        F(["Hello, vim world", ""], cursor=(0,10), keys="Esc",
          status="hi.txt [+]               1,11           All",
          caption="Esc — back to Normal mode.",
          narration="Esc commits the insert and returns to Normal. The whole insertion is one undoable change."),
    ]))

add(E("foundations.grammar",
    "operator + motion = sentence",
    "The grammar in three keystrokes.",
    "foundations.universal-grammar",
    [
        F(["the quick brown fox"], cursor=(0,4),
          caption="Cursor on 'q'.", narration="Normal mode. We will run d-w: the delete operator with the word motion."),
        F(["the brown fox"], cursor=(0,4), keys="dw",
          caption="dw — 'quick ' deleted.",
          narration="Operator d (verb) plus motion w (noun). Same grammar applies for any operator+motion pair."),
        F(["the BROWN fox"], cursor=(0,8), keys="lgUw",
          caption="gUw — 'BROWN' uppercased.",
          narration="Swap the operator for gU (uppercase), keep motion w. Free upgrade — every motion works with every operator."),
    ]))


# ============ Part 2 — Survival ============================================

add(E("survival.open-save-quit",
    ":w and :q",
    "Save and quit from the Ex prompt.",
    "survival.open-save-quit",
    [
        F(["greetings", "from vim"], cursor=(1,8),
          status="hello.txt [+]            2,9            All",
          caption="Modified buffer ([+])."),
        F(["greetings", "from vim"], cursor=(1,8), keys=":w",
          status="hello.txt              2,9            All",
          mode_line='"hello.txt" 2L, 19B written',
          caption=":w writes the file.", narration="Status loses [+]; the file is on disk. :q would now leave Vim."),
    ]))

add(E("survival.insert-and-back",
    "i and Esc",
    "Enter Insert with i; leave with Esc.",
    "survival.insert-and-back",
    [
        F(["foo"], cursor=(0,0)),
        F(["foo"], cursor=(0,0), keys="i", mode_line=INSERT_LINE,
          caption="Insert mode begins."),
        F(["barfoo"], cursor=(0,2), keys="bar", mode_line=INSERT_LINE,
          caption="Three letters typed."),
        F(["barfoo"], cursor=(0,2), keys="Esc",
          caption="Esc — back to Normal.",
          narration="Insert mode is for typing characters; Normal mode is for everything else."),
    ]))

add(E("survival.undo-redo",
    "u and Ctrl-R",
    "Undo, then redo.",
    "survival.undo-redo",
    [
        F(["alpha", "bravo", "charlie"], cursor=(1,0)),
        F(["alpha", "charlie"], cursor=(1,0), keys="dd",
          caption="dd deletes 'bravo'."),
        F(["alpha", "bravo", "charlie"], cursor=(1,0), keys="u",
          caption="u — bravo back."),
        F(["alpha", "charlie"], cursor=(1,0), keys="Ctrl-R",
          caption="Ctrl-R — redo (gone again).",
          narration="Undo and redo navigate the change history. Vim keeps a tree, not just a stack — see undo-tree."),
    ]))

add(E("survival.hjkl",
    "h j k l",
    "Move without leaving home row.",
    "survival.hjkl",
    [
        F(["alpha", "bravo", "charlie"], cursor=(0,0),
          caption="Start at top-left."),
        F(["alpha", "bravo", "charlie"], cursor=(1,0), keys="j",
          caption="j — down a line."),
        F(["alpha", "bravo", "charlie"], cursor=(1,3), keys="lll",
          caption="lll — three right."),
        F(["alpha", "bravo", "charlie"], cursor=(2,3), keys="j",
          caption="j — down again."),
    ]))


# ============ Part 3 — Editing =============================================

add(E("editing.insert-variants",
    "i I a A o O",
    "Six entries to Insert mode.",
    "editing.insert-variants",
    [
        F(["    indented line"], cursor=(0,8),
          caption="Cursor middle of line."),
        F(["    indented line"], cursor=(0,8), keys="I", mode_line=INSERT_LINE,
          caption="I — first non-blank.",
          narration="Cursor jumps before 'i' (column 4) and Insert begins. I = ^i."),
        F(["    indented line"], cursor=(0,17), keys="Esc A", mode_line=INSERT_LINE,
          caption="A — end of line.",
          narration="A jumps past the last char. Pair with I for boundary insertions; pair with o/O for new lines."),
    ]))

add(E("editing.word-motions",
    "w b e",
    "Move by word boundary.",
    "editing.word-motions",
    [
        F(["the quick brown fox"], cursor=(0,0),
          caption="Cursor on 't' of 'the'."),
        F(["the quick brown fox"], cursor=(0,4), keys="w",
          caption="w — start of next word."),
        F(["the quick brown fox"], cursor=(0,8), keys="e",
          caption="e — end of current word."),
        F(["the quick brown fox"], cursor=(0,4), keys="b",
          caption="b — back to 'q'.",
          narration="w/b move *to* word boundaries; e moves to the *end* of a word. With operators: dw, db, de all differ slightly — see grammar."),
    ]))

add(E("editing.line-motions",
    "0 ^ $",
    "Three flavors of line start/end.",
    "editing.line-motions",
    [
        F(["    hello world"], cursor=(0,8)),
        F(["    hello world"], cursor=(0,0), keys="0",
          caption="0 — column 0 (literal start)."),
        F(["    hello world"], cursor=(0,4), keys="^",
          caption="^ — first non-blank."),
        F(["    hello world"], cursor=(0,14), keys="$",
          caption="$ — end of line.",
          narration="Use ^ when you want code, 0 when you want column zero, $ to land on the last char."),
    ]))

add(E("editing.file-motions",
    "gg G",
    "Top and bottom of file.",
    "editing.file-motions",
    [
        F(["line 1", "line 2", "line 3", "line 4", "line 5"], cursor=(2,0),
          caption="Middle of file."),
        F(["line 1", "line 2", "line 3", "line 4", "line 5"], cursor=(0,0), keys="gg",
          caption="gg — top."),
        F(["line 1", "line 2", "line 3", "line 4", "line 5"], cursor=(4,0), keys="G",
          caption="G — bottom.",
          narration="With a count: 3G or :3<CR> jumps to line 3."),
    ]))

add(E("editing.delete",
    "x dw dd",
    "Three deletes, three scopes.",
    "editing.delete",
    [
        F(["the quick brown fox"], cursor=(0,4),
          caption="Cursor on 'q'."),
        F(["the uick brown fox"], cursor=(0,4), keys="x",
          caption="x — one char gone."),
        F(["the brown fox"], cursor=(0,4), keys="dw",
          caption="dw — through next word boundary."),
        F([""], cursor=(0,0), keys="dd",
          caption="dd — entire line.",
          narration="d is the operator; x is sugar for dl. The deleted text goes to the unnamed register and the numbered register 1."),
    ]))

add(E("editing.change",
    "cw is c then w",
    "Change = delete + Insert in one step.",
    "editing.change",
    [
        F(["the quick brown fox"], cursor=(0,4)),
        F(["the  brown fox"], cursor=(0,4), keys="cw", mode_line=INSERT_LINE,
          caption="cw — 'quick' gone, Insert mode on.",
          narration="Note the trailing space stays — cw stops *just before* the next word. (One of cw's well-known quirks.)"),
        F(["the slow brown fox"], cursor=(0,7), keys="slow", mode_line=INSERT_LINE,
          caption="Type 'slow'."),
        F(["the slow brown fox"], cursor=(0,7), keys="Esc",
          caption="Esc — change is committed and dot-repeatable."),
    ]))

add(E("editing.yank-put",
    "yy then p",
    "Copy a line, paste below.",
    "editing.yank-put",
    [
        F(["alpha", "bravo", "charlie"], cursor=(1,0)),
        F(["alpha", "bravo", "charlie"], cursor=(1,0), keys="yy",
          status="list.txt                 2,1            All",
          mode_line="1 line yanked",
          caption="yy — line into unnamed register.",
          narration="Buffer unchanged. The unnamed register now holds 'bravo\\n'."),
        F(["alpha", "bravo", "bravo", "charlie"], cursor=(2,0), keys="p",
          caption="p — pasted below.",
          narration="Linewise paste opens a new line beneath. Capital P pastes above."),
    ]))

add(E("editing.replace-char",
    "r x",
    "Replace one character without entering Insert.",
    "editing.replace-char",
    [
        F(["foo"], cursor=(0,0)),
        F(["xoo"], cursor=(0,0), keys="rx",
          caption="rx — 'f' becomes 'x'.",
          narration="r waits for the next keystroke and writes that char in place. No mode change. R enters Replace mode for many chars."),
    ]))


# ============ Part 4 — Search ==============================================

add(E("search.pattern",
    "/word and n / N",
    "Forward search, then jump through hits.",
    "search.pattern",
    [
        F(["the cat", "ran past", "the cat", "and away"], cursor=(0,0)),
        F(["the cat", "ran past", "the cat", "and away"], cursor=(0,0), keys="/cat",
          mode_line="/cat",
          caption="/ shows search prompt at the bottom."),
        F(["the cat", "ran past", "the cat", "and away"], cursor=(0,4), keys="Enter",
          highlights=[hl(0,4,3,bg="666666"), hl(2,4,3,bg="666666")],
          caption="Enter — first match highlighted."),
        F(["the cat", "ran past", "the cat", "and away"], cursor=(2,4), keys="n",
          highlights=[hl(0,4,3,bg="666666"), hl(2,4,3,bg="666666")],
          caption="n — next match.",
          narration="N goes back. // repeats with the same pattern; ? searches backward."),
    ]))

add(E("search.word",
    "* on a word",
    "Search for the current word, no typing required.",
    "search.word",
    [
        F(["foo bar foo baz", "foo qux"], cursor=(0,8),
          caption="Cursor on second 'foo'."),
        F(["foo bar foo baz", "foo qux"], cursor=(1,0), keys="*",
          mode_line="/\\<foo\\>",
          highlights=[hl(0,0,3,bg="666666"), hl(0,8,3,bg="666666"), hl(1,0,3,bg="666666")],
          caption="* — searched for \\<foo\\>; jumped to the next.",
          narration="* turns the cursor word into a search pattern with word boundaries (\\<...\\>) so 'foobar' won't match. # is the same backward."),
    ]))

add(E("search.find-on-line",
    "f and t",
    "Inline character search.",
    "search.find-on-line",
    [
        F(["the quick brown fox jumps"], cursor=(0,0)),
        F(["the quick brown fox jumps"], cursor=(0,16), keys="ff",
          caption="ff — find 'f' on this line."),
        F(["the quick brown fox jumps"], cursor=(0,18), keys="0tx",
          caption="tx — *till* x: stops one before.",
          narration="f lands ON the char; t lands JUST before. ; repeats; , reverses. Operator-friendly: dtx deletes up to but not including 'x'."),
    ]))


# ============ Part 5 — Counts and Visual ===================================

add(E("counts.basics",
    "5j and 3dw",
    "Counts multiply motions and operators.",
    "counts-visual.counts",
    [
        F(["one","two","three","four","five","six"], cursor=(0,0)),
        F(["one","two","three","four","five","six"], cursor=(5,0), keys="5j",
          caption="5j — down five lines."),
        F(["one","two","three","four","five","six"], cursor=(0,0), keys="gg 3dw",
          # actually showing post-state of 3dw on a single longer line below
          caption="3dw — three words gone (next demo)."),
        F(["the fox jumps"], cursor=(0,0), keys="3dw",
          caption="On 'the quick brown fox jumps', 3dw deletes the first three words.",
          narration="Counts apply equally to motions and to operator+motion combos. 3dw == d3w == ddwdwdw."),
    ]))

add(E("counts.percent",
    "% jumps to matching bracket",
    "% bounces between paired (), [], {}.",
    "counts-visual.percent-bar",
    [
        F(["if (x > 0) {", "    do_thing();", "}"], cursor=(0,3),
          caption="Cursor on '('."),
        F(["if (x > 0) {", "    do_thing();", "}"], cursor=(0,9), keys="%",
          caption="% — landed on ')'."),
        F(["if (x > 0) {", "    do_thing();", "}"], cursor=(0,11), keys="l%",
          caption="l then % — bounced from { to }."),
    ]))

add(E("visual.char",
    "v and motion",
    "Character-wise visual selection.",
    "counts-visual.char-visual",
    [
        F(["the quick brown fox"], cursor=(0,4)),
        F(["the quick brown fox"], cursor=(0,9), keys="vw", mode_line=VISUAL_LINE,
          highlights=[hl(0,4,6,bg="666666")],
          caption="vw — selected through next word."),
        F(["the  brown fox"], cursor=(0,4), keys="d",
          caption="d — delete the selection.",
          narration="Visual mode picks a range *first*, then you apply an operator. Useful when the right motion is hard to compose."),
    ]))

add(E("visual.line-block",
    "V and Ctrl-V",
    "Linewise vs block visual.",
    "counts-visual.line-block",
    [
        F(["foo 1","bar 2","baz 3"], cursor=(0,0)),
        F(["foo 1","bar 2","baz 3"], cursor=(2,0), keys="Vjj", mode_line=VLINE_LINE,
          highlights=[hl(0,0,5,bg="666666"), hl(1,0,5,bg="666666"), hl(2,0,5,bg="666666")],
          caption="V then jj — three full lines."),
        F(["foo 1","bar 2","baz 3"], cursor=(2,4), keys="Esc Ctrl-V jj l", mode_line=VBLOCK_LINE,
          highlights=[hl(0,4,1,bg="666666"), hl(1,4,1,bg="666666"), hl(2,4,1,bg="666666")],
          caption="Ctrl-V — block of just the digits.",
          narration="Block mode operates on a rectangle — perfect for tabular data and column edits."),
    ]))


# ============ Part 6 — Dot ==================================================

add(E("dot.repeat",
    ".",
    "The single most powerful key in Vim.",
    "dot.repeat",
    [
        F(["foo bar", "foo baz", "foo qux"], cursor=(0,0)),
        F(["xxx bar", "foo baz", "foo qux"], cursor=(0,0), keys="cwxxx Esc",
          caption="cw to xxx, Esc."),
        F(["xxx bar", "xxx baz", "foo qux"], cursor=(1,0), keys="j0 .",
          caption=". — same change at new cursor.",
          narration="Dot replays the last *change* (anything that modified the buffer). Cheap revolution: structure your motions so dot becomes useful."),
        F(["xxx bar", "xxx baz", "xxx qux"], cursor=(2,0), keys="j0 .",
          caption=". again — third line.",
          narration="Move-and-dot is a Vim idiom. Beats keyboard macros for trivial repetitions."),
    ]))

add(E("dot.with-counts",
    "5.",
    "Dot honors counts.",
    "dot.with-counts",
    [
        F(["x", "x", "x", "x", "x", "x"], cursor=(0,0)),
        F(["", "x", "x", "x", "x", "x"], cursor=(0,0), keys="dd",
          caption="dd — delete one line."),
        F(["", "", "", "", "", "x"], cursor=(0,0), keys="4.",
          caption="4. — repeat dd four times.",
          narration="A count on dot replays the change that many times — even if the original change had a different count."),
    ]))


# ============ Part 7 — Operators and text objects ==========================

add(E("textobj.iw-aw",
    "ciw vs caw",
    "Inner word vs around word.",
    "operators-textobjects.iw-aw",
    [
        F(["the (quick) brown fox"], cursor=(0,5)),
        F(["the () brown fox"], cursor=(0,5), keys="diw",
          caption="diw — 'quick' gone, parens kept."),
        F(["the  brown fox"], cursor=(0,4), keys="u daw",
          caption="daw — 'quick ' AND its surrounding space gone.",
          narration="i = inner (just the thing). a = around (thing + its delimiters or trailing space)."),
    ]))

add(E("textobj.quotes",
    'ci" and ca"',
    "Operate on whatever is in the quotes.",
    "operators-textobjects.quotes",
    [
        F(['greeting = "hello, world"'], cursor=(0,15),
          caption="Cursor inside the string."),
        F(['greeting = ""'], cursor=(0,12), keys='ci"', mode_line=INSERT_LINE,
          caption='ci" — string contents gone.',
          narration='You don\'t need to be on a quote — Vim finds the surrounding pair on the line. Same for \', `, (), [], {}, <>, t (tag).'),
    ]))

add(E("textobj.brackets",
    "di( vs da(",
    "Brackets work like quotes.",
    "operators-textobjects.brackets",
    [
        F(["call(arg1, arg2)"], cursor=(0,8),
          caption="Cursor on 'a' of arg1."),
        F(["call()"], cursor=(0,5), keys="di(",
          caption="di( — args removed."),
        F(["call"], cursor=(0,4), keys="u da(",
          caption="da( — parens removed too."),
    ]))

add(E("textobj.tags",
    "cit and cat",
    "HTML/XML tag objects.",
    "operators-textobjects.tags",
    [
        F(["<p>hello world</p>"], cursor=(0,5)),
        F(["<p></p>"], cursor=(0,3), keys="cit", mode_line=INSERT_LINE,
          caption="cit — inner-tag content cleared."),
    ]))

# ============ Part 8 — Wider motions =======================================

add(E("motion.match",
    "% on different brackets",
    "% picks the right pair automatically.",
    "wider-motions.match-bracket",
    [
        F(["arr[i] = (a + b);"], cursor=(0,3), caption="Cursor on '['."),
        F(["arr[i] = (a + b);"], cursor=(0,5), keys="%", caption="% — to ']'."),
        F(["arr[i] = (a + b);"], cursor=(0,9), keys="ww %",
          caption="From '(', % goes to ')'."),
    ]))

add(E("motion.bigword",
    "W vs w",
    "WORD motions ignore punctuation as separators.",
    "wider-motions.WORD",
    [
        F(["foo.bar baz"], cursor=(0,0), caption="Cursor on 'f'."),
        F(["foo.bar baz"], cursor=(0,3), keys="w",
          caption="w — stopped at '.'.",
          narration="Lower-case w treats '.' as a word boundary."),
        F(["foo.bar baz"], cursor=(0,8), keys="0W",
          caption="W — skipped to 'baz'.",
          narration="Upper-case W treats whitespace-separated chunks as one WORD."),
    ]))

# ============ Part 9 — Scroll =============================================

add(E("scroll.center",
    "zz",
    "Bring the current line to the center.",
    "scroll.center-top-bottom",
    [
        F(["1","2","3","4","5","6","7","8","9","10"], cursor=(8,0),
          caption="Cursor near the bottom of the visible viewport."),
        F(["4","5","6","7","8","9","10","","",""], cursor=(4,0), keys="zz",
          caption="zz — line moved to center, screen scrolled.",
          narration="zt puts the line at the top; zb at the bottom. The cursor doesn't move in the buffer — only the viewport."),
    ]))


# ============ Part 10 — Marks and jumps ====================================

add(E("marks.set-jump",
    "ma and 'a",
    "Set a mark, jump back later.",
    "marks.local-global",
    [
        F(["chapter one","...content...","chapter two","..."], cursor=(0,0)),
        F(["chapter one","...content...","chapter two","..."], cursor=(0,0), keys="ma",
          caption="ma — mark 'a' set at this line."),
        F(["chapter one","...content...","chapter two","..."], cursor=(2,0), keys="2j",
          caption="Wandered to chapter two."),
        F(["chapter one","...content...","chapter two","..."], cursor=(0,0), keys="'a",
          caption="'a — jumped back to mark 'a'.",
          narration="Lowercase marks are file-local; uppercase marks are global (jump across files)."),
    ]))

add(E("marks.jumplist",
    "Ctrl-O and Ctrl-I",
    "Walk back through your jump history.",
    "marks.jumplist",
    [
        F(["line A","line B","line C"], cursor=(0,0)),
        F(["line A","line B","line C"], cursor=(2,0), keys="G",
          caption="G — jumped to bottom (recorded)."),
        F(["line A","line B","line C"], cursor=(0,0), keys="Ctrl-O",
          caption="Ctrl-O — back where we came from.",
          narration="Vim records 'big' jumps in a per-window list. Ctrl-O goes back, Ctrl-I goes forward."),
    ]))


# ============ Part 11 — Transformations ====================================

add(E("transform.case",
    "gUw and ~",
    "Change case without retyping.",
    "transform.case",
    [
        F(["hello world"], cursor=(0,0)),
        F(["HELLO world"], cursor=(0,0), keys="gUw",
          caption="gUw — uppercase one word."),
        F(["hELLO world"], cursor=(0,1), keys="0~",
          caption="~ — toggle one char's case.",
          narration="gu/gU/g~ are operators; ~ is a one-shot toggle. With visual mode you can transform any selection."),
    ]))

add(E("transform.indent",
    ">> and <<",
    "Indent and dedent the current line.",
    "transform.indent",
    [
        F(["if x:","print('hi')"], cursor=(1,0)),
        F(["if x:","    print('hi')"], cursor=(1,4), keys=">>",
          caption=">> — indented one shiftwidth.",
          narration="Doubled operator pattern. >ip indents an inner paragraph; >G indents to end of file."),
    ]))

add(E("transform.join",
    "J",
    "Join two lines into one.",
    "transform.join",
    [
        F(["the quick","brown fox"], cursor=(0,3)),
        F(["the quick brown fox"], cursor=(0,9), keys="J",
          caption="J — joined with a single space.",
          narration="gJ joins without adding a space — useful for code."),
    ]))


# ============ Part 12 — Registers ==========================================

add(E("registers.unnamed",
    "yy then p",
    "Copy a line, paste below.",
    "registers.unnamed",
    [
        F(["alpha","bravo","charlie"], cursor=(1,0)),
        F(["alpha","bravo","charlie"], cursor=(1,0), keys="yy",
          caption='yy — yanked to "" (unnamed).'),
        F(["alpha","bravo","bravo","charlie"], cursor=(2,0), keys="p",
          caption="p — pasted below."),
        F(["alpha","bravo","bravo","bravo","charlie"], cursor=(3,0), keys="p",
          caption="p again — same register, same content.",
          narration='The unnamed register " is the default destination for yanks/deletes and source for p/P.'),
    ]))

add(E("registers.named",
    '"ay and "ap',
    "Use named register a.",
    "registers.named",
    [
        F(["foo","bar"], cursor=(0,0)),
        F(["foo","bar"], cursor=(0,0), keys='"ayy',
          caption='"ayy — yanked into register a.'),
        F(["foo","bar","foo"], cursor=(2,0), keys='G "ap',
          caption='"ap — pasted from register a.',
          narration='Named registers a-z survive subsequent yanks. Use them for stable clipboard slots.'),
    ]))

add(E("registers.numbered",
    '"1p and "2p',
    "Walk back through deletion history.",
    "registers.numbered",
    [
        F(["A","B","C"], cursor=(0,0)),
        F(["B","C"], cursor=(0,0), keys="dd",
          caption='dd — A goes to "1.'),
        F(["C"], cursor=(0,0), keys="dd",
          caption='dd — B goes to "1, A pushed to "2.'),
        F(["C","B"], cursor=(1,0), keys='"1p',
          caption='"1p — most recent (B) back.'),
        F(["C","B","A"], cursor=(2,0), keys='"3p',  # actually "2p but we're past
          caption='"2p — older one (A) back.',
          narration='"1-"9 hold the last 9 line-deletes. They shift each time you delete.'),
    ]))

add(E("registers.clipboard",
    '"+y and "+p',
    "Cross-application copy/paste.",
    "registers.clipboard",
    [
        F(["secret = 'abc123'"], cursor=(0,0)),
        F(["secret = 'abc123'"], cursor=(0,0), keys='"+yy',
          caption='"+yy — line into the system clipboard.',
          narration='"+ writes to the system clipboard. Now Ctrl-V in your browser pastes the line.'),
    ]))


# ============ Part 13 — Macros =============================================

add(E("macros.record-play",
    "qa ... q  then  @a",
    "Record once, play forever.",
    "macros.record-play",
    [
        F(["one","two","three"], cursor=(0,0), mode_line="recording @a",
          keys="qa", caption="qa — start recording into a."),
        F(["1. one","two","three"], cursor=(0,5), mode_line="recording @a",
          keys="I1. Esc", caption="Prefix with '1. '."),
        F(["1. one","two","three"], cursor=(1,0), mode_line="recording @a",
          keys="j0", caption="Move to next line (recorded)."),
        F(["1. one","two","three"], cursor=(1,0), keys="q",
          caption="q — stop recording."),
        F(["1. one","2. two","3. three"], cursor=(2,0), keys="@a @a",
          caption="@a twice — replays on the next two lines.",
          narration="Macros are just register contents. Open the register, edit it, paste it — they're text."),
    ]))


# ============ Part 14 — Windows =============================================

add(E("windows.splits",
    ":split and :vsplit",
    "Two views of one buffer (or two).",
    "windows.splits",
    [
        F(["main.py","def f():"], cursor=(1,0)),
        F(["main.py","def f():","    pass","main.py","def f():"], cursor=(0,0), keys=":sp",
          mode_line="Press ENTER to continue",
          caption=":sp — horizontal split."),
        F(["main.py        |main.py","def f():       |def f():","    pass       |    pass"], cursor=(0,0),
          cols=40, keys=":vsp",
          caption=":vsp — vertical split.",
          narration="Each split is an independent view. Use Ctrl-W h/j/k/l to navigate."),
    ]))

add(E("windows.buffers",
    ":ls and :b",
    "Edit many files in one Vim session.",
    "windows.buffers",
    [
        F(["main.py","..."], cursor=(0,0)),
        F(["main.py","..."], cursor=(0,0), keys=":ls",
          mode_line="1 %a 'main.py'  2 # 'lib.py'",
          caption=":ls — list of loaded buffers."),
        F(["lib.py","def helper():"], cursor=(0,0), keys=":b lib",
          caption=":b lib — switch to lib.py."),
    ]))


# ============ Part 15 — Prefix families (use one example each) ============

add(E("prefix.g",
    "gU gu g~ ga",
    "The 'g' prefix is a grab-bag of useful commands.",
    "prefixes.g-overview",
    [
        F(["hello"], cursor=(0,0)),
        F(["HELLO"], cursor=(0,0), keys="gUiw",
          caption="gUiw — uppercase inner word."),
        F(["hello"], cursor=(0,0), keys="u guiw",
          caption="guiw — lowercase inner word."),
        F(["hello"], cursor=(0,0), keys="ga",
          mode_line="<h>  104,  Hex 68,  Octal 150",
          caption="ga — character info under cursor."),
    ]))

add(E("prefix.z",
    "zz zt zb",
    "Viewport positioning with z.",
    "prefixes.z-overview",
    [
        F(["1","2","3","4","5","6","7","8","9","10"], cursor=(4,0)),
        F(["3","4","5","6","7","8","9","10","",""], cursor=(2,0), keys="zt",
          caption="zt — current line to top."),
    ]))


# ============ Part 16 — Insert mode power ==================================

add(E("insert.one-shot",
    "Ctrl-O in Insert",
    "One Normal command without leaving Insert.",
    "insert.one-shot-normal",
    [
        F(["hello world"], cursor=(0,5), mode_line=INSERT_LINE),
        F(["hello world"], cursor=(0,11), mode_line=INSERT_LINE,
          keys="Ctrl-O $",
          caption="Ctrl-O $ — jumped to EOL, still in Insert."),
        F(["hello world!"], cursor=(0,11), mode_line=INSERT_LINE,
          keys="!", caption="Type '!' — Insert mode resumes seamlessly."),
    ]))

add(E("insert.completion",
    "Ctrl-N",
    "Word completion from buffer.",
    "insert.completion",
    [
        F(["congratulations","con"], cursor=(1,3), mode_line=INSERT_LINE),
        F(["congratulations","congratulations"], cursor=(1,15), mode_line=INSERT_LINE,
          keys="Ctrl-N",
          caption="Ctrl-N — matched 'con' to the only word starting with it.",
          narration="Ctrl-N searches forward through known words; Ctrl-P backward. Ctrl-X opens the sub-completion menu (filenames, lines, etc.)."),
    ]))


# ============ Part 17 — Ex =================================================

add(E("ex.substitute",
    ":s/foo/bar/g",
    "Find and replace on the current line.",
    "ex.substitute",
    [
        F(["foo and foo and foo"], cursor=(0,0)),
        F(["foo and foo and foo"], cursor=(0,0), mode_line=":s/foo/bar/g",
          caption="Type the substitute command."),
        F(["bar and bar and bar"], cursor=(0,0), keys="Enter",
          mode_line="3 substitutions on 1 line",
          caption="3 substitutions on this line.",
          narration="Range :%s/.../.../g applies to whole file. With c flag you confirm each."),
    ]))

add(E("ex.global",
    ":g/TODO/d",
    "Run an Ex command on every matching line.",
    "ex.global",
    [
        F(["x = 1","# TODO: fix","y = 2","# TODO: again"], cursor=(0,0)),
        F(["x = 1","y = 2"], cursor=(0,0), keys=":g/TODO/d Enter",
          mode_line=":g/TODO/d",
          caption="All TODO lines deleted.",
          narration=":g/pat/cmd runs cmd on each matching line. :v/pat/cmd runs on every NON-matching line."),
    ]))

add(E("ex.norm",
    ':%norm I// ',
    "Run a Normal-mode sequence on every line.",
    "ex.norm",
    [
        F(["x = 1","y = 2","z = 3"], cursor=(0,0)),
        F(["// x = 1","// y = 2","// z = 3"], cursor=(0,0),
          keys=':%norm I// Enter',
          mode_line=':%norm I// ',
          caption=":%norm prefixes every line with '// '.",
          narration="Like a macro that doesn't need recording. Combine with :g for selective application."),
    ]))


# ============ Part 18 — Visual depth ========================================

add(E("visual.gv",
    "gv",
    "Re-select the previous visual region.",
    "visual.gv",
    [
        F(["lorem ipsum dolor sit amet"], cursor=(0,12)),
        F(["lorem ipsum dolor sit amet"], cursor=(0,17), keys="vw",
          mode_line=VISUAL_LINE,
          highlights=[hl(0,12,6,bg="666666")],
          caption="Selected 'dolor '."),
        F(["lorem ipsum DOLOR sit amet"], cursor=(0,12), keys="U",
          caption="U — uppercased the selection."),
        F(["lorem ipsum DOLOR sit amet"], cursor=(0,17), keys="gv",
          mode_line=VISUAL_LINE,
          highlights=[hl(0,12,6,bg="666666")],
          caption="gv — same region selected again.",
          narration="gv is great for chained visual operations."),
    ]))


# ============ Part 19 — Command line power =================================

add(E("cmdline.history",
    "q:",
    "Command-line history as an editable buffer.",
    "cmdline.history-window",
    [
        F([":w","%s/foo/bar/g","make","Press ? for help"], cursor=(2,0),
          status="[Command Line]            3,1            All",
          caption="q: — opens the history window."),
        F([":w","%s/foo/bar/g","make","Press ? for help"], cursor=(1,0), keys="kk",
          caption="Pick any line, edit it, Enter to run."),
    ]))


# ============ Part 20 — Patterns ==========================================

add(E("pattern.star-cw-dot",
    "* cw . . .",
    "Search-cursor-change-repeat — mass rename.",
    "patterns.star-cw-dot",
    [
        F(["foo()","foo()","foo()"], cursor=(0,0)),
        F(["foo()","foo()","foo()"], cursor=(0,0), keys="*",
          highlights=[hl(0,0,3,bg="666666"),hl(1,0,3,bg="666666"),hl(2,0,3,bg="666666")],
          caption="* — search for 'foo'."),
        F(["bar()","foo()","foo()"], cursor=(0,2), keys="cwbar Esc",
          caption="cwbar — change to bar."),
        F(["bar()","bar()","foo()"], cursor=(1,2), keys="n .",
          caption="n then . — next match, dot."),
        F(["bar()","bar()","bar()"], cursor=(2,2), keys="n .",
          caption="And again. The Replace Loop.",
          narration="The classic Vim mass-edit. cgn is similar and even slicker — see cgn-dot."),
    ]))

add(E("pattern.cgn-dot",
    "*  then  cgn  then  . . .",
    "Change-next-match — fewer keystrokes than star-cw-dot.",
    "patterns.cgn-dot",
    [
        F(["foo()","foo()","foo()"], cursor=(0,0)),
        F(["foo()","foo()","foo()"], cursor=(0,0), keys="*",
          highlights=[hl(0,0,3,bg="666666"),hl(1,0,3,bg="666666"),hl(2,0,3,bg="666666")],
          caption="* — pattern set."),
        F(["bar()","foo()","foo()"], cursor=(0,2), keys="cgnbar Esc",
          caption="cgn — change next match."),
        F(["bar()","bar()","foo()"], cursor=(1,2), keys=".",
          caption=". — finds next AND changes it."),
        F(["bar()","bar()","bar()"], cursor=(2,2), keys=".",
          caption="One key per replacement.",
          narration="cgn = c + gn (motion: 'next match'). Dot replays the whole thing — search-and-change in one keystroke."),
    ]))

add(E("pattern.block-comment",
    "Ctrl-V  jjj  I//<Esc>",
    "Block-prefix many lines at once.",
    "patterns.block-comment",
    [
        F(["x = 1","y = 2","z = 3"], cursor=(0,0)),
        F(["x = 1","y = 2","z = 3"], cursor=(2,0), keys="Ctrl-V jj",
          mode_line=VBLOCK_LINE,
          highlights=[hl(0,0,1,bg="666666"),hl(1,0,1,bg="666666"),hl(2,0,1,bg="666666")],
          caption="Ctrl-V jj — three rows selected."),
        F(["// x = 1","y = 2","z = 3"], cursor=(0,0), keys="I//", mode_line=INSERT_LINE,
          caption="I// — typing on the first row only."),
        F(["// x = 1","// y = 2","// z = 3"], cursor=(0,0), keys="Esc",
          caption="Esc — Vim replays the insertion on every selected row.",
          narration="The trick: in block-Insert mode, the typing only shows on row one until you press Esc."),
    ]))

add(E("pattern.increment",
    "Ctrl-A and Ctrl-X",
    "Bump numbers up or down.",
    "patterns.increment-decrement",
    [
        F(["item 41"], cursor=(0,5)),
        F(["item 42"], cursor=(0,6), keys="Ctrl-A",
          caption="Ctrl-A — number under (or to the right of) the cursor incremented."),
        F(["item 47"], cursor=(0,6), keys="5Ctrl-A",
          caption="5Ctrl-A — increment by 5."),
    ]))


# ============ Part 21 — Advanced ===========================================

add(E("advanced.character-info",
    "ga",
    "Inspect the byte under the cursor.",
    "advanced.character-info",
    [
        F(["café"], cursor=(0,3)),
        F(["café"], cursor=(0,3), keys="ga",
          mode_line="<é>  233,  Hex 00e9,  Octal 351, Digr e'",
          caption="ga — decimal/hex/octal codepoint, plus digraph if any."),
    ]))


# Generation -----------------------------------------------------------------

def main():
    filt = sys.argv[1] if len(sys.argv) > 1 else ""
    OUT_DIR.mkdir(exist_ok=True)
    written = 0
    for ex in EXAMPLES:
        if filt and filt not in ex["id"]:
            continue
        # validate id slug
        if not re.fullmatch(r"[a-z0-9.\-]+", ex["id"]):
            print(f"  ! invalid id: {ex['id']}", file=sys.stderr); continue
        path = OUT_DIR / f"{ex['id']}.json"
        path.write_text(json.dumps(ex, indent=2), encoding="utf-8")
        written += 1
    print(f"Wrote {written} example file(s) -> {OUT_DIR}")


if __name__ == "__main__":
    main()
