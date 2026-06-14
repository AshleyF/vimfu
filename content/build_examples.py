"""Generate all worked-example JSON files from a single Python source.

Authoring 100+ JSON files by hand is brutal. This module is the source
of truth: each example is a few lines of Python that build a valid
vimfu-content-example payload, which we then write out as JSON for the
renderer to consume.

Two authoring flavors:

  E(...) + F(...)
      Hand-authored compact frames. Use when you want a synthetic frame
      that real Vim can't produce (e.g. a fake window-split layout).

  EL(...) + LF(...)
      Lesson-backed example. Authors a lesson JSON next to it
      (content/example_lessons/<id>.json) and configures the example
      to pull its screenshots from authentic shellpilot captures. This
      is the preferred path — the screenshots can't drift out of sync
      with what Vim actually does, and the redirect generator gets
      explicit initial-state info for the "try this" deep link.

Usage:
    python content/build_examples.py            # write all examples
    python content/build_examples.py grammar    # filter by id substring

Conventions:
- All examples default to a 40-col terminal with status row near bottom.
- Each frame is just (lines, cursor, keys, caption, narration, **opts).
- Status rows render as reverse video automatically.
- '~' lines auto-color blue (Vim's empty-buffer marker).

Run after editing -> regenerates content/examples/*.json (and any
lessons declared via EL).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "examples"
LESSONS_DIR = ROOT / "example_lessons"
REPO_ROOT = ROOT.parent

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


def SF(*, keys="", caption="", narration=""):
    """Build a frame entry that references a captured-lesson frame.

    The frame data itself comes from ``source.select[i]`` on the example
    (see ``content/render_screenshots.py:resolve_frame``). Use this when
    you want a screenshot to be an authentic Vim capture rather than a
    hand-authored ``F(...)`` compact frame.
    """
    out: dict = {}
    if caption: out["caption"] = caption
    if narration: out["narration"] = narration
    if keys: out["keys"] = keys
    return out


def E(eid, title, summary, topic, frames, *,
      source=None, initial=None, lang=None, filename=None):
    """Build a complete example payload.

    Optional kwargs:
      source   : ``{"lesson": "<path>", "select": [i, j, k]}`` — use a
                 shellpilot-captured lesson as the frame source.
      initial  : ``{"file": "<name>", "content": "<text>", "cursor": [r, c]}``
                 — explicit initial-state spec for the sim deep link.
                 Required when ``source`` is used (otherwise the redirect
                 generator has no compact frame[0] to mine).
      lang     : language hint (drives sim's syntax highlighting).
      filename : explicit practice filename (e.g. "Makefile").
    """
    out = {
        "format": "vimfu-content-example",
        "version": 1,
        "id": eid,
        "title": title,
        "summary": summary,
        "topic": topic,
    }
    if source is not None:
        out["source"] = source
    if initial is not None:
        out["initial"] = initial
    if lang is not None:
        out["lang"] = lang
    if filename is not None:
        out["filename"] = filename
    out["frames"] = frames
    return out


def hl(row, col, length=1, **flags):
    """Highlight helper."""
    h = {"row": row, "col": col, "len": length}
    h.update(flags)
    return h


# ---------- lesson-backed (EL) authoring --------------------------------------
#
# An EL() example carries authentic shellpilot-captured screenshots. The
# author describes a small lesson (initial file content + a list of frame
# specs), and EL() takes care of:
#
#   * Writing the lesson JSON to content/example_lessons/<id>.json,
#     wrapped with the standard setup (write file → nvim → swap guard)
#     and teardown (rm -f) blocks.
#   * Computing the `source.select` indices so each example frame maps
#     to the right captured frame.
#   * Filling in `initial: {file, content, cursor}` so the "try this"
#     QR code starts the simulator at the same position the demo does.
#
# Each frame in `frames=` is built with LF(...). The first LF may have
# `actions=[]` (the post-setup state); subsequent LFs list the lesson
# steps that produce the next screenshot. Helpers K/T/X/ESC/ENTER make
# the action lists short and readable.

# Map from `lang=` to a sensible filename extension. Mirrors the
# practice_filename() sniff path in content/lib/sim_link.py so the sim's
# syntax highlighting dispatch lines up with what the example shows.
_LANG_EXT = {
    "text": "txt", "txt": "txt", "plain": "txt", None: "txt", "": "txt",
    "python": "py", "py": "py",
    "javascript": "js", "js": "js",
    "c": "c", "cpp": "cpp",
    "html": "html", "css": "css",
    "json": "json", "yaml": "yaml", "yml": "yaml",
    "shell": "sh", "sh": "sh", "bash": "sh",
    "go": "go", "rust": "rs", "markdown": "md", "md": "md",
}


def K(keys):           return {"keys": keys}
def T(text):           return {"type": text}
def X(cmd):            return {"ex": cmd}
def WAIT_FOR(text):    return {"waitForScreen": text, "timeout": 5.0}
ESC = "escape"
ENTER = "enter"


def LF(*, actions=None, caption="", narration="", keys=""):
    """One frame in an EL() example.

    actions   : list of shellpilot step dicts/strings that run before this
                frame is captured. None or [] means "use the current state"
                (i.e. the post-setup state, for the first frame).
    caption   : caption shown above the screenshot.
    narration : prose printed below the caption.
    keys      : display-only key chord (for the printed caption).
    """
    return {
        "actions": list(actions) if actions else [],
        "caption": caption,
        "narration": narration,
        "keys": keys,
    }


def EL(eid, title, summary, topic, *,
       content,
       cursor=(0, 0),
       filename=None,
       lang=None,
       cols=40, rows=10,
       nvim_args=None,
       prep=None,
       extra_setup=None,
       frames):
    """Lesson-backed example.

    Args:
      eid       : example id (e.g. "foundations.modes").
      title, summary, topic : same as E().
      content   : initial buffer. List of lines OR a single string. A
                  trailing newline is added if missing.
      cursor    : (row, col) tuple — where the cursor sits before the
                  first frame. Translated into preparation key presses
                  (gg / <r>j / 0 / <c>l) appended to the setup block.
      filename  : explicit nvim filename. Defaults to "practice.<ext>"
                  based on `lang`.
      lang      : language hint — drives the file extension and the
                  sim's syntax-highlighting dispatch.
      cols/rows : terminal dimensions for the captured frames.
      nvim_args : list of extra args to pass on the nvim command line.
                  Use this for options like ``-c "set report=0"`` whose
                  echo from ``:set`` would otherwise leak into frame 0.
      prep      : extra lesson steps to run BEFORE the first frame
                  (after cursor positioning). Use for setup actions
                  whose result is the "starting state" of the demo.
                  Either a single step or a list.
      extra_setup : extra shellpilot steps to splice into the lesson's
                    setup block (run fast, not captured). Use for shell
                    commands like `:syntax off` that aren't part of the
                    demo proper.
      frames    : list of LF(...) entries — one per example frame.
    """
    if isinstance(content, str):
        content_str = content if content.endswith("\n") else content + "\n"
    else:
        content_str = "\n".join(content) + "\n"

    # Pick a filename.
    if filename:
        file = filename
    else:
        ext = _LANG_EXT.get(lang, "txt")
        file = f"practice.{ext}"

    # Standard setup: clean nvim state, write file, open it, dismiss the
    # swap-file prompt if one appears.
    nvim_cmd = "nvim"
    if nvim_args:
        # Quote each arg so it can contain spaces/quotes.
        import shlex
        nvim_cmd += " " + " ".join(shlex.quote(a) for a in nvim_args)
    nvim_cmd += f" {file}"
    setup: list = [
        {"line": "export TERM=xterm-256color"},
        {"line": "mkdir -p ~/vimfu && cd ~/vimfu"},
        {"line": f"rm -f {file} .{file}.swp"},
        {"line": "find ~/.local/state/nvim/swap -mindepth 1 -delete 2>/dev/null"},
        {"writeFile": file, "content": content_str, "noDedent": True},
        {"line": "clear"},
        {"line": nvim_cmd},
        {"waitForScreen": "All", "timeout": 30.0},
        {"ifScreen": "swap file", "thenKeys": "d"},
    ]
    if extra_setup:
        setup.extend(extra_setup)

    # Translate non-trivial starting cursors into a positioning sequence
    # appended to setup so the FIRST captured frame already sits where
    # the demo begins.
    r, c = cursor
    if r > 0 or c > 0:
        mv = "gg"
        if r > 0: mv += f"{r}j"
        mv += "0"
        if c > 0: mv += f"{c}l"
        setup.append({"keys": mv})

    # Optional prep steps run between cursor positioning and the first
    # captured frame. Useful for "open a register" or "start recording"
    # style setup that needs to be in effect before the demo proper.
    if prep is not None:
        if isinstance(prep, (list, tuple)):
            setup.extend(prep)
        else:
            setup.append(prep)

    # Flatten all frame actions into the lesson's steps array. Track
    # cumulative captured-frame index so each example frame picks the
    # right one.
    #
    # Frame 0 of the capture is the post-setup state. The FIRST LF with
    # actions=[] sits on that frame (or, if it has actions, after them).
    lesson_steps: list = []
    select: list[int] = []
    cumulative = 0   # last captured frame index (0 = post-setup)
    for fr in frames:
        for act in fr["actions"]:
            lesson_steps.append(act)
            cumulative += 1
        select.append(cumulative)

    teardown = [
        ESC,
        T(":q!"),
        ENTER,
        {"line": f"rm -f {file}"},
    ]

    lesson = {
        "title": f"VimFu — {eid} (example screenshots)",
        "description": f"Lesson used by content/examples/{eid}.json to capture authentic Vim frames. Not intended for video.",
        "speed": 1.0,
        "humanize": 0,
        "rows": rows,
        "cols": cols,
        "ttsEnabled": False,
        "recordVideo": False,
        "clickKeys": False,
        "setup": setup,
        "steps": lesson_steps,
        "teardown": teardown,
    }

    LESSONS_DIR.mkdir(exist_ok=True)
    lesson_path = LESSONS_DIR / f"{eid.replace('.', '_')}.json"
    lesson_path.write_text(
        json.dumps(lesson, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    # Build the example payload. Each frame entry holds only display
    # metadata — the captured frame supplies all the pixels.
    example_frames: list = []
    for fr in frames:
        entry: dict = {}
        if fr.get("caption"):   entry["caption"] = fr["caption"]
        if fr.get("narration"): entry["narration"] = fr["narration"]
        if fr.get("keys"):      entry["keys"] = fr["keys"]
        example_frames.append(entry)

    out = {
        "format": "vimfu-content-example",
        "version": 1,
        "id": eid,
        "title": title,
        "summary": summary,
        "topic": topic,
        "source": {
            "lesson": f"content/example_lessons/{lesson_path.name}",
            "select": select,
        },
        "initial": {
            "file": file,
            "content": content_str,
            "cursor": [r, c],
        },
    }
    if lang is not None:
        out["lang"] = lang
    if filename is not None:
        out["filename"] = filename
    out["frames"] = example_frames
    return out


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

add(EL("foundations.modes",
    "*normal mode* \u2192 *insert mode* \u2192 *normal mode*",
    "The mode transition every editing change goes through.",
    "foundations.modes-overview",
    content="Hello world",
    cursor=(0, 5),
    filename="hi.txt",
    frames=[
        LF(caption="*Normal mode.* Cursor on the space.",
           narration="When you open a file, you start in *normal mode.* Keystrokes are commands."),
        LF(actions=[K("i"), T(", vim")],
           keys="i, vim",
           caption="{key:i}, then type `, vim` \u2014 *insert mode,* text added.",
           narration="{key:i} enters *insert mode* at the cursor; subsequent keys produce text. The status line below advertises the mode."),
        LF(actions=[ESC],
           keys="Esc",
           caption="{key:Esc} \u2014 back to *normal mode.*",
           narration="{key:Esc} commits the insert and returns to *normal mode.* The whole insertion is one undoable change."),
    ]))

add(EL("foundations.grammar",
    "operator + motion = sentence",
    "The grammar in three keystrokes.",
    "foundations.universal-grammar",
    content="the quick brown fox",
    cursor=(0, 4),
    frames=[
        LF(caption="Cursor on `q`.",
           narration="*normal mode.* We'll run `dw`: the delete operator with the word motion."),
        LF(actions=[K("dw")],
           keys="dw",
           caption="`dw` \u2014 `quick ` deleted.",
           narration="Operator `d` (verb) plus motion `w` (noun). The same grammar applies for any operator+motion pair."),
        LF(actions=[K("gUw")],
           keys="gUw",
           caption="`gUw` \u2014 `BROWN` uppercased.",
           narration="Swap the operator for `gU` (uppercase), keep motion `w`. Free upgrade \u2014 every motion works with every operator."),
    ]))


# ============ Part 2 — Survival ============================================

add(EL("survival.open-save-quit",
    ":w and :q",
    "Save and quit from the Ex prompt.",
    "survival.open-save-quit",
    content="greetings\nfrom vi",
    cursor=(1, 0),
    filename="hello.txt",
    prep=[K("A"), T("m"), ESC],
    frames=[
        LF(caption="Modified buffer ([+])."),
        LF(actions=[X("w")], keys=":w",
           caption=":w writes the file.",
           narration="Status loses [+]; the file is on disk. :q would now leave Vim."),
    ]))

add(EL("survival.insert-and-back",
    "i and Esc",
    "Enter Insert with i; leave with Esc.",
    "survival.insert-and-back",
    content="foo",
    cursor=(0, 0),
    frames=[
        LF(),
        LF(actions=[K("i")], keys="i", caption="Insert mode begins."),
        LF(actions=[T("bar")], keys="bar", caption="Three letters typed."),
        LF(actions=[ESC], keys="Esc", caption="Esc — back to Normal.",
           narration="Insert mode is for typing characters; Normal mode is for everything else."),
    ]))

add(EL("survival.undo-redo",
    "u and Ctrl-R",
    "Undo, then redo.",
    "survival.undo-redo",
    content=["alpha", "bravo", "charlie"],
    cursor=(1, 0),
    frames=[
        LF(),
        LF(actions=[K("dd")], keys="dd", caption="dd deletes 'bravo'."),
        LF(actions=[K("u")], keys="u", caption="u — bravo back."),
        LF(actions=[K("Ctrl-R")], keys="Ctrl-R", caption="Ctrl-R — redo (gone again).",
           narration="Undo and redo navigate the change history. Vim keeps a tree, not just a stack — see undo-tree."),
    ]))

add(EL("survival.hjkl",
    "h j k l",
    "Move without leaving home row.",
    "survival.hjkl",
    content=["alpha", "bravo", "charlie"],
    cursor=(0, 0),
    frames=[
        LF(caption="Start at top-left."),
        LF(actions=[K("j")], keys="j", caption="j — down a line."),
        LF(actions=[K("lll")], keys="lll", caption="lll — three right."),
        LF(actions=[K("j")], keys="j", caption="j — down again."),
    ]))


# ============ Part 3 — Editing =============================================

add(EL("editing.insert-variants",
    "i I a A o O",
    "Six entries to Insert mode.",
    "editing.insert-variants",
    content="    indented line",
    cursor=(0, 8),
    frames=[
        LF(caption="Cursor middle of line."),
        LF(actions=[K("I")], keys="I",
           caption="I — first non-blank.",
           narration="Cursor jumps before 'i' (column 4) and Insert begins. I = ^i."),
        LF(actions=[ESC, K("A")], keys="Esc A",
           caption="A — end of line.",
           narration="A jumps past the last char. Pair with I for boundary insertions; pair with o/O for new lines."),
    ]))

add(EL("editing.word-motions",
    "w b e",
    "Move by word boundary.",
    "editing.word-motions",
    content="the quick brown fox",
    cursor=(0, 0),
    frames=[
        LF(caption="Cursor on 't' of 'the'."),
        LF(actions=[K("w")], keys="w", caption="w — start of next word."),
        LF(actions=[K("e")], keys="e", caption="e — end of current word."),
        LF(actions=[K("b")], keys="b", caption="b — back to 'q'.",
           narration="w/b move *to* word boundaries; e moves to the *end* of a word. With operators: dw, db, de all differ slightly — see grammar."),
    ]))

add(EL("editing.line-motions",
    "0 ^ $",
    "Three flavors of line start/end.",
    "editing.line-motions",
    content="    hello world",
    cursor=(0, 8),
    frames=[
        LF(),
        LF(actions=[K("0")], keys="0", caption="0 — column 0 (literal start)."),
        LF(actions=[K("^")], keys="^", caption="^ — first non-blank."),
        LF(actions=[K("$")], keys="$", caption="$ — end of line.",
           narration="Use ^ when you want code, 0 when you want column zero, $ to land on the last char."),
    ]))

add(EL("editing.file-motions",
    "gg G",
    "Top and bottom of file.",
    "editing.file-motions",
    content=["line 1", "line 2", "line 3", "line 4", "line 5"],
    cursor=(2, 0),
    frames=[
        LF(caption="Middle of file."),
        LF(actions=[K("gg")], keys="gg", caption="gg — top."),
        LF(actions=[K("G")], keys="G", caption="G — bottom.",
           narration="With a count: 3G or :3<CR> jumps to line 3."),
    ]))

add(EL("editing.delete",
    "x dw dd",
    "Three deletes, three scopes.",
    "editing.delete",
    content="the quick brown fox",
    cursor=(0, 4),
    frames=[
        LF(caption="Cursor on 'q'."),
        LF(actions=[K("x")], keys="x", caption="x — one char gone."),
        LF(actions=[K("dw")], keys="dw", caption="dw — through next word boundary."),
        LF(actions=[K("dd")], keys="dd", caption="dd — entire line.",
           narration="d is the operator; x is sugar for dl. The deleted text goes to the unnamed register and the numbered register 1."),
    ]))

add(EL("editing.change",
    "cw is c then w",
    "Change = delete + Insert in one step.",
    "editing.change",
    content="the quick brown fox",
    cursor=(0, 4),
    frames=[
        LF(),
        LF(actions=[K("cw")], keys="cw",
           caption="cw — 'quick' gone, Insert mode on.",
           narration="Note the trailing space stays — cw stops *just before* the next word. (One of cw's well-known quirks.)"),
        LF(actions=[T("slow")], keys="slow", caption="Type 'slow'."),
        LF(actions=[ESC], keys="Esc",
           caption="Esc — change is committed and dot-repeatable."),
    ]))

add(EL("editing.yank-put",
    "yy then p",
    "Copy a line, paste below.",
    "editing.yank-put",
    content=["alpha", "bravo", "charlie"],
    cursor=(1, 0),
    filename="list.txt",
    nvim_args=["-c", "set report=0"],
    frames=[
        LF(),
        LF(actions=[K("yy")], keys="yy",
           caption="yy — line into unnamed register.",
           narration="Buffer unchanged. The unnamed register now holds 'bravo\\n'."),
        LF(actions=[K("p")], keys="p", caption="p — pasted below.",
           narration="Linewise paste opens a new line beneath. Capital P pastes above."),
    ]))

add(EL("editing.replace-char",
    "r x",
    "Replace one character without entering Insert.",
    "editing.replace-char",
    content="foo",
    cursor=(0, 0),
    frames=[
        LF(),
        LF(actions=[K("rx")], keys="rx", caption="rx — 'f' becomes 'x'.",
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
    "counts.counts",
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
    "counts.percent-bar",
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
    "visual-modes.char-visual",
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
    "visual-modes.line-block",
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


# ============ Part 7 — Text objects ==========================

add(E("textobj.iw-aw",
    "ciw vs caw",
    "Inner word vs around word.",
    "text-objects.iw-aw",
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
    "text-objects.quotes",
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
    "text-objects.brackets",
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
    "text-objects.tags",
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


# ============ Part 18 — Visual Modes ========================================

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
