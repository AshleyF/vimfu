"""Build worked-example JSON from content-authored definitions.

Example *definitions* live under ``content/example_defs/<id>.json``
(``vimfu-example-def``). This script loads them, expands each through
``EL(...)`` / ``E(...)`` helpers, and writes:

  - ``content/examples/<id>.json`` — payloads the site/book renderers read
  - ``content/example_lessons/<id>.json`` — shellpilot lessons for captures

Two runtime flavors (still available as helpers for rare hand-authored
compact frames):

  E(...) + F(...)
      Hand-authored compact frames. Use when you want a synthetic frame
      that real Vim can't produce (e.g. a fake window-split layout).

  EL(...) + LF(...)
      Lesson-backed example (the default path for defs). Authors a lesson
      JSON and configures the example to pull screenshots from authentic
      shellpilot captures.

Usage:
    python content/build_examples.py            # write all examples
    python content/build_examples.py grammar    # filter by id substring

Conventions:
- Prefer editing ``content/example_defs/*.json`` — not this file — when
  changing example content, captions, or keystroke sequences.
- All examples default to a 40-col terminal with status row near bottom.
- Run after editing defs -> regenerates ``content/examples/*.json``
  (and lessons declared via EL).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "examples"
LESSONS_DIR = ROOT / "example_lessons"
DEFS_DIR = ROOT / "example_defs"
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
       pre_setup=None,
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
      pre_setup : extra shellpilot steps to splice into the setup
                  block BEFORE the nvim launch. Use for shell-level
                  prep like writing additional files that need to
                  exist on disk before nvim starts.
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
    ]
    if pre_setup:
        setup.extend(pre_setup)
    setup.extend([
        {"line": "clear"},
        {"line": nvim_cmd},
        {"waitForScreen": file, "timeout": 30.0},
        {"ifScreen": "swap file", "thenKeys": "d"},
    ])
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
        "captureDedup": False,
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



# ---------- load content/example_defs ---------------------------------------
#
# Authoring source of truth is content/example_defs/<id>.json.
# Schema: vimfu-example-def (see content/Examples.md / content/README.md).

EXAMPLES = []


def add(ex):
    EXAMPLES.append(ex)
    return ex


def _action_from_def(act):
    """Convert a JSON action into the shellpilot step form EL expects."""
    if isinstance(act, str):
        if act in ("escape", "esc", "Esc"):
            return ESC
        if act in ("enter", "Enter", "CR"):
            return ENTER
        return act
    if not isinstance(act, dict):
        raise TypeError(f"bad action: {act!r}")
    if "keys" in act:
        return K(act["keys"])
    if "type" in act:
        return T(act["type"])
    if "ex" in act:
        return X(act["ex"])
    if "waitForScreen" in act:
        return WAIT_FOR(act["waitForScreen"])
    # Pass through shellpilot-native dicts (writeFile, line, …)
    return act


def _frames_from_def(frames):
    out = []
    for fr in frames:
        actions = [_action_from_def(a) for a in fr.get("actions") or []]
        out.append(LF(
            actions=actions or None,
            caption=fr.get("caption", ""),
            narration=fr.get("narration", ""),
            keys=fr.get("keys", ""),
        ))
    return out


def load_def(path: Path):
    """Load one vimfu-example-def JSON and expand it via EL() or E()."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    if raw.get("format") not in ("vimfu-example-def", "vimfu-content-example"):
        raise ValueError(f"{path}: unknown format {raw.get('format')!r}")

    # Compact-frame flavor: already a full example with inline F-style frames
    if raw.get("format") == "vimfu-content-example" and "source" not in raw:
        # Pass through — already a finished payload (rare).
        return raw

    eid = raw["id"]
    title = raw["title"]
    summary = raw["summary"]
    topic = raw["topic"]
    content = raw["content"]
    cursor = tuple(raw.get("cursor") or (0, 0))

    kwargs = {}
    for key in ("filename", "lang", "cols", "rows", "nvim_args",
                "pre_setup", "extra_setup"):
        if key in raw:
            kwargs[key] = raw[key]

    if "prep" in raw:
        prep = raw["prep"]
        if isinstance(prep, list):
            kwargs["prep"] = [_action_from_def(a) for a in prep]
        else:
            kwargs["prep"] = _action_from_def(prep)

    frames = _frames_from_def(raw.get("frames") or [])
    return EL(eid, title, summary, topic, content=content, cursor=cursor,
              frames=frames, **kwargs)


def load_all_defs(filt: str = ""):
    """Load every example_defs/*.json (optionally filtered by id substring)."""
    if not DEFS_DIR.is_dir():
        raise SystemExit(f"missing defs directory: {DEFS_DIR}")
    paths = sorted(DEFS_DIR.glob("*.json"))
    loaded = 0
    for path in paths:
        if filt and filt not in path.stem and filt not in path.name:
            # Also allow filter against id inside file cheaply via stem
            # (ids use dots; filenames match ids).
            raw_id = path.stem
            if filt not in raw_id:
                continue
        ex = load_def(path)
        if filt and filt not in ex["id"]:
            continue
        add(ex)
        loaded += 1
    return loaded


# Generation -----------------------------------------------------------------

def main():
    filt = sys.argv[1] if len(sys.argv) > 1 else ""
    OUT_DIR.mkdir(exist_ok=True)
    load_all_defs(filt="")  # always load all; filter on write
    written = 0
    for ex in EXAMPLES:
        if filt and filt not in ex["id"]:
            continue
        if not re.fullmatch(r"[a-z0-9.\-]+", ex["id"]):
            print(f"  ! invalid id: {ex['id']}", file=sys.stderr)
            continue
        path = OUT_DIR / f"{ex['id']}.json"
        path.write_text(json.dumps(ex, indent=2), encoding="utf-8")
        written += 1
    print(f"Wrote {written} example file(s) -> {OUT_DIR}")
    print(f"  (from {DEFS_DIR})")


if __name__ == "__main__":
    main()
