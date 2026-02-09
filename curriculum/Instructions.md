# VimFu Video Creation Instructions

These are standing instructions for creating VimFu tutorial videos. Read this before generating any new lessons.

---

## Curriculum

The source of truth for what each lesson covers is **Curriculum.md** (in this same folder). When asked to create a video, look up the lesson number there to find the title, keys, and description. Follow the curriculum order.

---

## The Feedback Loop

Every video goes through a generate → inspect → fix cycle:

1. **Generate** the video by running the script.
2. **Inspect the log** (`Select-String` on the `.log` file for `[KEYS]`, `[SAY]`, `[OVERLAY]`, and `cursor` lines).
3. **Critique the log** — check that:
   - Cursor positions are where you expect.
   - The right characters were deleted/changed/inserted.
   - Navigation was efficient (see below).
   - Narration matches what's actually happening on screen.
   - **No extraneous keystrokes** — every key press should serve the demo. If you see navigation that could be shorter (e.g., `0` then `w w w` when `3w` or `f<char>` would do), redesign the file content or pick a better motion.
   - **The demo is compelling** — the log should read like a clean, purposeful walkthrough. If a section feels clunky or repetitive, restructure it. Better motions make for better demos.
4. **Fix and regenerate** if anything is off. This isn't just about fixing errors — it's about **improving the demo**. A log that works but feels inefficient or cluttered is not done yet. Repeat until the log reads like a crisp, polished tutorial.

---

## Nvim Goes in Setup

Unless the lesson is specifically about opening a file or launching Vim, **nvim must launch in the `setup=[]` block**, not in `steps=[]`. The recording should start with the file already open. No one wants to watch a blank terminal while nvim loads.

Standard setup pattern:
```python
setup=[
    Comment("Set TERM for proper color support in Neovim"),
    Line("export TERM=xterm-256color"),
    Comment("Prepare workspace"),
    Line("mkdir -p ~/vimfu && cd ~/vimfu"),
    Line("rm -f demo.py .demo.py.swp .demo.py.swo"),
    Line("rm -f ~/.local/state/nvim/swap/*demo.py*"),
    Comment("Create the demo file"),
    WriteFile("demo.py", """
        ...file contents...
    """),
    Line("clear"),
    Comment("Launch nvim before recording"),
    Line("nvim demo.py"),
    WaitForScreen("some visible text", timeout=10.0),
    IfScreen("swap file", "d"),
],
```

---

## Efficient Navigation

When navigating around the file, **use the fewest keystrokes possible** — unless the navigation command itself is what the lesson is teaching.

Bad (when demoing `dw`, not `f` or `0`):
```python
Keys("j"),       # down a line
Keys("0"),       # go to start of line
Keys("f"),
Keys("v"),       # find character
Keys("d"),
Keys("w"),       # finally do the thing
```

Good:
```python
Keys("j"),       # down — cursor already on the right column
Keys("d"),
Keys("w"),       # just do the thing
```

### Design the file content to minimize navigation

The best way to have efficient navigation is to **design the demo file so the cursor naturally lands where you need it**. Tricks:

- **Align target words at the same column** across lines. If variable names are all the same length, `j` preserves the column and you land right on target.
- **Put the target at the start of the line** when possible, so no horizontal movement is needed.
- **Avoid variable names that contain the character you need to `f`-search for.** E.g., if you need `fr` to find "red", don't name the variable `color` (the 'r' in color will match first). Use `theme` instead.

---

## Narration Rules

- **Spell out key names** in narration for TTS clarity: say "D W" not "dw", "capital X" not "shift-x".
- **Narration must match the screen.** If you say "the main function" while navigating to a line, that line had better contain a main function. If you say "dollar sign next", the next lesson had better actually be about `$`.
- **Don't tease future lessons unless you're certain of the order.** Prefer a strong closing statement about the current command instead.
- **Keep it tight.** These are sub-60-second Shorts. Every sentence should earn its place.

---

## Sample Content

The demo files should be **funny, entertaining, and imaginative** — mostly programming-themed since the audience is developers. Don't use bland `foo`/`bar` variables or generic placeholder text. Instead, write little code snippets that tell a story: a game inventory system, a robot personality module, a spell-casting class, a pizza-ordering API, a cat behavior simulator. The content should make viewers smile and want to watch the next one.

Also, **fill the ~60-second YouTube Shorts window** as much as needed to produce a thorough demo. Don't rush through a single example and leave 30 seconds on the table. If the core concept is simple, show it in multiple contexts, add a count-prefix variation, or demonstrate an undo. The goal is a polished, complete demo — not a speed run.

---

## Demo Structure Template

A typical lesson follows this arc:

1. **Title overlay** (3 seconds) — `Overlay("VimFu", caption="...", duration=3.0)`
2. **Intro sentence** — what the command does, one line.
3. **First demo** — show the command on the simplest case. Explain what happened.
4. **Second demo** — repeat on a different line to reinforce. Shorter narration.
5. **Third demo or variation** — show a twist (count prefix, related shortcut, undo).
6. **Closing sentence** — restate the key and what it does. Strong and memorable.

After destructive operations (delete, change), **show undo** (`u`) to restore the file — it reinforces that Vim is safe to experiment in.

---

## Technical Notes

- **Python venv** (`C:/source/vimfu/.venv/Scripts/python.exe`) — for video generation.
- **Exit code 1** from ffmpeg resize warnings is normal — ignore it.
- **TTS cache** — audio clips are cached in `shellpilot/.tts_cache/`. If you change narration text, new clips are generated automatically. Old clips for unchanged text are reused.

---

## Common Script Patterns

These patterns are established across all 40 existing lesson scripts. Follow them for consistency.

### Demo() Parameters (never vary)

```python
lesson = Demo(
    title="VimFu — <Topic Name>",         # always "VimFu — " + em dash + topic
    description="...",                      # 1-2 plain sentences
    speed=0.55,
    rows=20,
    cols=40,
    humanize=0.7,
    mistakes=0.0,
    seed=<unique int>,                      # increment from previous lesson
    tts_voice="echo",
    borderless=True,
    playlist="VimFu",
    ...
)
```

### Imports (always the same)

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "shellpilot"))
from dsl import Demo, Comment, Say, Line, Type, Keys, Wait, Escape, Enter, IfScreen, WaitForScreen, Overlay, WriteFile
```

### Docstring

```python
"""
Lesson NNN: <Topic Name>

Sub-60-second lesson: <one-line pitch>.
<Optional second line>.
"""
```

### Variable & Entry Point

Always `lesson = Demo(...)` and:
```python
if __name__ == "__main__":
    lesson.run()
```

### Title Card (always the first two steps)

```python
Overlay("VimFu", caption="<Topic Name>", duration=3.0),
Wait(0.7),
```

The caption must match the portion after the em dash in the `title` parameter.

### Teardown (always the same structure)

```python
teardown=[
    Comment("Quit nvim without saving"),
    Escape(),
    Type(":q!"),
    Enter(),
    Comment("Clean up"),
    Line("rm -f <filename>.py"),
],
```

### Wait Timing Conventions

| Context | Value |
|---------|-------|
| After title overlay | `0.7` |
| After nvim opens / WaitForScreen | `0.5` |
| Before a key sequence (let viewer focus) | `0.3` |
| After a key sequence (let viewer see result) | `0.5`–`0.6` |
| After Say() before next section | `0.3` |
| After Escape() back to normal mode | `0.3`–`0.5` |
| **Final Wait before steps end** | **`1.5`** (always — every script) |

### Narration Style

- `Say("...", wait=False)` — speech overlaps with the next action (common when narrating during a demo).
- `Say("...", wait=True)` or `Say("...")` — speech finishes before continuing (good for intros/explanations).
- Short, punchy sentences. Conversational tone.

### Section Comments

Use `# --- Section name ---` to divide steps into logical blocks (title card, demo 1, demo 2, wrap up, etc.).

### Demo File Names

Always short, lowercase `.py` files relevant to the lesson context: `typo.py`, `config.py`, `fix.py`, `words.py`, etc. Names can be reused across unrelated lessons since each script cleans up after itself.

---

## Checklist Before Moving On

- [ ] Log inspected — cursor positions correct
- [ ] Log inspected — navigation is efficient (no unnecessary `0`, `f`, `^` unless teaching those)
- [ ] Narration matches what's on screen
- [ ] No nvim launch visible in the recording (unless that's the lesson)
