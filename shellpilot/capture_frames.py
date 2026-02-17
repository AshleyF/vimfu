"""
Capture terminal frames from a ShellPilot lesson replay.

Replays a lesson JSON headlessly (no viewer, no video, no TTS, no
clicks) and captures the pyte screen buffer — with full color data —
after every visible step.  Writes the result as a **frames JSON** file
that downstream tools (gif_maker, etc.) can consume.

The output follows the Frame Format spec (see brainstorming/frame_format.md)
extended with per-frame timing and action metadata.

Usage:
    python capture_frames.py curriculum/shorts/0085_the_vim_grammar.json
    python capture_frames.py lesson.json --output frames.json
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Color resolution (mirrors viewer.py TerminalViewer._resolve_color)
# ---------------------------------------------------------------------------

DEFAULT_FG = "d4d4d4"
DEFAULT_BG = "000000"

_ANSI = {
    "black": "000000", "red": "cd0000", "green": "00cd00",
    "brown": "cdcd00", "yellow": "cdcd00", "blue": "0000ee",
    "magenta": "cd00cd", "cyan": "00cdcd", "white": "e5e5e5",
    "brightblack": "7f7f7f", "brightred": "ff0000",
    "brightgreen": "00ff00", "brightbrown": "ffff00",
    "brightyellow": "ffff00", "brightblue": "5c5cff",
    "brightmagenta": "ff00ff", "brightcyan": "00ffff",
    "brightwhite": "ffffff",
}


def _color_256(code: int) -> str:
    if code < 16:
        pal = [
            "000000", "cd0000", "00cd00", "cdcd00",
            "0000ee", "cd00cd", "00cdcd", "e5e5e5",
            "7f7f7f", "ff0000", "00ff00", "ffff00",
            "5c5cff", "ff00ff", "00ffff", "ffffff",
        ]
        return pal[code]
    if code < 232:
        code -= 16
        r = (code // 36) % 6
        g = (code // 6) % 6
        b = code % 6
        r = 0 if r == 0 else 55 + r * 40
        g = 0 if g == 0 else 55 + g * 40
        b = 0 if b == 0 else 55 + b * 40
        return f"{r:02x}{g:02x}{b:02x}"
    gray = (code - 232) * 10 + 8
    return f"{gray:02x}{gray:02x}{gray:02x}"


def resolve_color(raw, bold: bool, is_fg: bool) -> str:
    """Resolve a pyte color value to a 6-digit hex string (no ``#``)."""
    if raw == "default":
        return DEFAULT_FG if is_fg else DEFAULT_BG

    if isinstance(raw, str):
        # 256-color numeric
        if raw.isdigit() and len(raw) <= 3:
            return _color_256(int(raw))

        # Hex string
        h = raw.lstrip("#")
        if h and all(c in "0123456789abcdefABCDEF" for c in h):
            if len(h) == 6:
                return h.lower()
            if len(h) == 3:
                return (h[0]*2 + h[1]*2 + h[2]*2).lower()
            if len(h) == 12:
                return (h[0:2] + h[4:6] + h[8:10]).lower()
            if len(h) > 6:
                return h[:6].lower()

        # Named ANSI
        lo = raw.lower()
        if bold and is_fg and not lo.startswith("bright"):
            bright = "bright" + lo
            if bright in _ANSI:
                return _ANSI[bright]
        if lo in _ANSI:
            return _ANSI[lo]

    return DEFAULT_FG if is_fg else DEFAULT_BG


# ---------------------------------------------------------------------------
# Vim key overlay resolution (mirrors viewer.py TerminalViewer._vim_commands)
# ---------------------------------------------------------------------------

_VIM_COMMANDS = {
    'h': 'left', 'j': 'down', 'k': 'up', 'l': 'right',
    'w': 'next word', 'W': 'next WORD', 'b': 'back word', 'B': 'back WORD',
    'e': 'end of word', 'E': 'end of WORD',
    '0': 'line start', '^': 'first char', '$': 'line end',
    'gg': 'file start', 'G': 'file end',
    'f': 'find char', 'F': 'find back', 't': 'till char', 'T': 'till back',
    ';': 'repeat find', ',': 'reverse find', '%': 'match bracket',
    '{': 'prev paragraph', '}': 'next paragraph',
    '(': 'prev sentence', ')': 'next sentence',
    'H': 'screen top', 'M': 'screen middle', 'L': 'screen bottom',
    'n': 'next match', 'N': 'prev match', '*': 'find word', '#': 'find word back',
    'gn': 'select next match', 'gN': 'select prev match',
    'i': 'insert', 'I': 'insert at start', 'a': 'append', 'A': 'append at end',
    'o': 'open below', 'O': 'open above',
    'v': 'visual', 'V': 'visual line',
    'R': 'replace mode', 's': 'substitute', 'S': 'substitute line',
    'c': 'change', 'C': 'change to end', 'cc': 'change line',
    'x': 'delete char', 'X': 'backspace',
    'd': 'delete', 'dd': 'delete line', 'D': 'delete to end',
    'y': 'yank', 'yy': 'yank line', 'Y': 'yank line',
    'p': 'paste after', 'P': 'paste before',
    'u': 'undo', 'U': 'undo line', '.': 'repeat',
    'r': 'replace char', '~': 'toggle case', 'J': 'join lines',
    '>': 'indent', '<': 'unindent', '>>': 'indent line', '<<': 'unindent line',
    '=': 'auto-indent', '==': 'indent line',
    'iw': 'inner word', 'aw': 'a word', 'iW': 'inner WORD', 'aW': 'a WORD',
    'is': 'inner sentence', 'as': 'a sentence',
    'ip': 'inner paragraph', 'ap': 'a paragraph',
    'i(': 'inner parens', 'a(': 'around parens',
    'i)': 'inner parens', 'a)': 'around parens',
    'i{': 'inner braces', 'a{': 'around braces',
    'i}': 'inner braces', 'a}': 'around braces',
    'i[': 'inner brackets', 'a[': 'around brackets',
    'i]': 'inner brackets', 'a]': 'around brackets',
    'i"': 'inner quotes', 'a"': 'around quotes',
    "i'": 'inner quotes', "a'": 'around quotes',
    'i`': 'inner backticks', 'a`': 'around backticks',
    'i<': 'inner angle', 'a<': 'around angle',
    'i>': 'inner angle', 'a>': 'around angle',
    'it': 'inner tag', 'at': 'around tag',
    '/': 'search', '?': 'search back', ':': 'command mode',
    'm': 'set mark', "'": 'go to mark', '`': 'go to mark exact',
    'q': 'record macro', '@': 'play macro', '@@': 'repeat macro',
    'ZZ': 'save & quit', 'ZQ': 'force quit',
}


def _resolve_key_overlay(keys: str, overlay_hint: str | None = None
                         ) -> tuple[str, str]:
    """Resolve keys to (display_text, caption).

    Tries compound lookups first (e.g. ``ci"`` → ``change inner "``).
    Returns (display, caption) where caption may be empty.
    """
    if overlay_hint is not None:
        # Step provided an explicit overlay override
        return (keys, overlay_hint)

    # Try the full key string first
    if keys in _VIM_COMMANDS:
        return (keys, _VIM_COMMANDS[keys])

    # Keys that consume the next character as a target — don't split
    _CHAR_CONSUMERS = {'f', 'F', 't', 'T', 'r', 'm', "'", '`', 'q', '@'}

    # Try operator + text-object split (e.g. ci" → c + i")
    if len(keys) >= 2:
        for split in range(1, len(keys)):
            op = keys[:split]
            obj = keys[split:]
            # Don't split if the operator consumes the next char as a target
            if op in _CHAR_CONSUMERS:
                continue
            if op in _VIM_COMMANDS and obj in _VIM_COMMANDS:
                return (keys, f"{_VIM_COMMANDS[op]} {_VIM_COMMANDS[obj]}")

    # Single char fallback
    if len(keys) == 1:
        lo = keys.lower()
        if lo in _VIM_COMMANDS:
            return (keys, _VIM_COMMANDS[lo])

    return (keys, "")


# ---------------------------------------------------------------------------
# Buffer → frame dict
# ---------------------------------------------------------------------------

def capture_frame(screen) -> dict:
    """Capture a pyte ``Screen`` as a Frame dict.

    Returns the format defined in ``brainstorming/frame_format.md``.
    """
    lines = []
    default_char = screen.default_char

    for row in range(screen.lines):
        line_buf = screen.buffer.get(row, {})
        chars: list[str] = []
        runs: list[dict] = []
        prev_key = None  # (fg, bg, flags)
        run_len = 0

        for col in range(screen.columns):
            cell = line_buf.get(col, default_char)
            chars.append(cell.data if cell.data else " ")

            fg = resolve_color(cell.fg, cell.bold, True)
            bg = resolve_color(cell.bg, cell.bold, False)
            if cell.reverse:
                fg, bg = bg, fg

            flags = ""
            if cell.bold:
                flags += "b"
            if cell.italics:
                flags += "i"
            if cell.underscore:
                flags += "u"
            if getattr(cell, "strikethrough", False):
                flags += "s"

            key = (fg, bg, flags)
            if key == prev_key:
                run_len += 1
            else:
                if prev_key is not None:
                    runs.append(_make_run(run_len, *prev_key))
                prev_key = key
                run_len = 1

        if prev_key is not None:
            runs.append(_make_run(run_len, *prev_key))

        lines.append({
            "text": "".join(chars),
            "runs": runs,
        })

    return {
        "rows": screen.lines,
        "cols": screen.columns,
        "cursor": {
            "row": screen.cursor.y,
            "col": screen.cursor.x,
            "visible": not screen.cursor.hidden,
        },
        "defaultFg": DEFAULT_FG,
        "defaultBg": DEFAULT_BG,
        "lines": lines,
    }


def _make_run(n: int, fg: str, bg: str, flags: str) -> dict:
    run: dict = {"n": n, "fg": fg, "bg": bg}
    if "b" in flags:
        run["b"] = True
    if "i" in flags:
        run["i"] = True
    if "u" in flags:
        run["u"] = True
    if "s" in flags:
        run["s"] = True
    return run


# ---------------------------------------------------------------------------
# Frame deduplication
# ---------------------------------------------------------------------------

def _frame_text(frame: dict) -> str:
    """Quick fingerprint: text + cursor position."""
    parts = [line["text"] for line in frame["lines"]]
    c = frame["cursor"]
    parts.append(f"{c['row']},{c['col']}")
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Main: replay lesson and capture frames
# ---------------------------------------------------------------------------

def _step_label(step) -> tuple[str, str]:
    """Return (action_type, detail) for a step object."""
    from player import (
        Say, Type, Keys, Line, Wait, Escape, Enter,
        Backspace, Ctrl, Overlay, Comment, IfScreen,
        WaitForScreen, WriteFile, Pause,
    )
    if isinstance(step, Say):
        return ("say", step.text)
    if isinstance(step, Type):
        return ("type", step.text)
    if isinstance(step, Keys):
        return ("keys", step.keys)
    if isinstance(step, Line):
        return ("line", step.command)
    if isinstance(step, Wait):
        return ("wait", str(step.seconds))
    if isinstance(step, Escape):
        return ("escape", "")
    if isinstance(step, Enter):
        return ("enter", "")
    if isinstance(step, Backspace):
        return ("backspace", str(step.count))
    if isinstance(step, Ctrl):
        return ("ctrl", step.char)
    if isinstance(step, Overlay):
        return ("overlay", step.text)
    if isinstance(step, Comment):
        return ("comment", step.text)
    if isinstance(step, IfScreen):
        return ("ifScreen", step.contains)
    if isinstance(step, WaitForScreen):
        return ("waitForScreen", step.text)
    if isinstance(step, WriteFile):
        return ("writeFile", step.path)
    if isinstance(step, Pause):
        return ("pause", step.message)
    return ("unknown", str(step))


def _produces_visible_change(step) -> bool:
    """Does this step type visibly change the terminal screen?"""
    from player import Say, Wait, Comment, Overlay
    return not isinstance(step, (Say, Wait, Comment, Overlay))


def capture_lesson(json_path: Path, *, output: Path = None) -> Path:
    """Replay a lesson headlessly and save captured frames.

    Returns the path to the output frames JSON file.
    """
    from player import load_lesson, Demo, Say, Overlay, Comment, Wait, Keys
    from viewer import ScriptedDemo

    lesson = load_lesson(json_path)
    title = json_path.stem

    # Determine output path
    if output is None:
        video_dir = Path("videos") / title
        video_dir.mkdir(parents=True, exist_ok=True)
        output = video_dir / f"{title}.frames.json"

    print(f"[CAPTURE] Replaying {title} ({lesson.rows}x{lesson.cols})")
    print(f"[CAPTURE] Steps: {len(lesson.setup)} setup, "
          f"{len(lesson.steps)} main, {len(lesson.teardown)} teardown")

    frames: list[dict] = []
    t0 = None  # set after setup

    with ScriptedDemo(
        rows=lesson.rows,
        cols=lesson.cols,
        speed=lesson.speed,
        show_viewer=False,
        click_keys=False,
        click_volume=0.0,
        humanize=lesson.humanize,
        mistakes=lesson.mistakes,
        seed=lesson.seed,
        tts_enabled=False,
        tts_voice=lesson.tts_voice,
        record_video=False,
        title=title,
        auto_start_recording=False,
    ) as demo:
        # ---- Setup (fast, not captured) ----
        Demo._run_fast(demo, lesson.setup)
        time.sleep(3.0)

        t0 = time.time()

        # ---- Capture initial frame ----
        init_frame = capture_frame(demo.shell.screen)
        init_frame["ms"] = 0
        init_frame["action"] = {"type": "start"}
        frames.append(init_frame)

        # Track narration / overlay context for each frame
        pending_say: str | None = None
        pending_overlay: str | None = None
        pending_overlay_caption: str | None = None

        # ---- Main steps ----
        for step in lesson.steps:
            action_type, detail = _step_label(step)

            # Accumulate metadata from non-visual steps
            if isinstance(step, Say):
                pending_say = step.text
            if isinstance(step, Overlay):
                pending_overlay = step.text
                pending_overlay_caption = step.caption or None

            # Execute the step (but skip TTS since it's disabled)
            step.execute(demo)

            # Capture frame after every step that changes the screen
            if _produces_visible_change(step):
                f = capture_frame(demo.shell.screen)
                f["ms"] = int((time.time() - t0) * 1000)
                f["action"] = {"type": action_type, "detail": detail}
                if pending_say:
                    f["action"]["say"] = pending_say
                    pending_say = None
                if pending_overlay:
                    f["action"]["overlay"] = pending_overlay
                    if pending_overlay_caption:
                        f["action"]["overlayCaption"] = pending_overlay_caption
                    pending_overlay = None
                    pending_overlay_caption = None
                # Resolve key overlay for steps that press keys
                if isinstance(step, Keys):
                    disp, caption = _resolve_key_overlay(
                        step.keys, step.overlay)
                    f["action"]["keyOverlay"] = disp
                    if caption:
                        f["action"]["keyCaption"] = caption
                elif action_type == "escape":
                    f["action"]["keyOverlay"] = "ESC"
                    f["action"]["keyCaption"] = "normal mode"
                elif action_type == "enter":
                    f["action"]["keyOverlay"] = "RET"
                    f["action"]["keyCaption"] = "execute"
                elif action_type == "ctrl":
                    f["action"]["keyOverlay"] = f"^{detail.upper()}"
                frames.append(f)

        # ---- Teardown (fast, not captured) ----
        Demo._run_fast(demo, lesson.teardown)

    # ---- Deduplicate consecutive identical frames ----
    deduped: list[dict] = [frames[0]] if frames else []
    for f in frames[1:]:
        if _frame_text(f) != _frame_text(deduped[-1]):
            deduped.append(f)
        else:
            # Keep the richer action metadata
            if f.get("action"):
                deduped[-1]["action"] = f["action"]

    # ---- Write output ----
    doc = {
        "format": "vimfu-frames",
        "version": 1,
        "title": lesson.title,
        "source": str(json_path),
        "rows": lesson.rows,
        "cols": lesson.cols,
        "defaultFg": DEFAULT_FG,
        "defaultBg": DEFAULT_BG,
        "frameCount": len(deduped),
        "frames": deduped,
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(doc, separators=(",", ":")), encoding="utf-8")

    size_kb = output.stat().st_size / 1024
    print(f"[CAPTURE] Saved {len(deduped)} frames ({size_kb:.0f} KB) → {output}")
    return output


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Capture terminal frames from a ShellPilot lesson replay."
    )
    parser.add_argument("lesson", type=Path,
                        help="Path to the lesson JSON file")
    parser.add_argument("--output", "-o", type=Path, default=None,
                        help="Output frames JSON path "
                             "(default: videos/<name>/<name>.frames.json)")
    args = parser.parse_args()

    if not args.lesson.exists():
        print(f"Error: {args.lesson} not found")
        sys.exit(1)

    capture_lesson(args.lesson, output=args.output)


if __name__ == "__main__":
    main()
