# VimFu Video Creation Instructions

These are standing instructions for creating VimFu tutorial videos. Read this before generating any new lessons.

---

## Curriculum

The source of truth for what each lesson covers is **Curriculum.md** (in this same folder). When asked to create a video, look up the lesson number there to find the title, keys, and description. Follow the curriculum order.

---

## The Feedback Loop

Every video goes through a generate → inspect → fix cycle:

1. **Generate** the video by running the script.
2. **Inspect the log** (`Select-String` on the `.log` file for `[KEYS]`, `[SAY]`, `[OVERLAY]`, `[RECORDING_START]`, and `cursor` lines).
3. **Critique the log** — check that:
   - **The `[RECORDING_START]` screen snapshot shows file content.** If it's blank (just `cursor (0,0)`), the setup timing is broken — fix the `WaitForScreen` text (see below).
   - Cursor positions are where you expect.
   - The right characters were deleted/changed/inserted.
   - Navigation was efficient (see below).
   - Narration matches what's actually happening on screen.
   - **CRITICAL: Trace every `[SAY]` against the surrounding `[KEYS]` and cursor lines.** If narration says "change this to level", the log MUST show the text actually changing to "level" in the screen state lines that follow. If the narration says "skip this one", the cursor MUST actually move past that match without a `.` (dot). Don't trust the script — trust the log. The log is what the viewer sees. Common failures:
     - Saying "change X to Y" but `cw` + type lands on the wrong word due to cursor column carry-over from a previous demo.
     - Saying "skip" but `n` wraps around to the same match (not enough matches in the file).
     - Saying "delete three lines" but `3.` doesn't visibly remove content (e.g., repeating `ciw` on the same position instead of across lines).
   - **Key overlays are accurate** — look at every `[OVERLAY]` line in the log. The caption next to each key should match what the key *means in that context*. Watch for cases where a key has multiple meanings depending on mode or sequence:
     - `a` after `q` or `@` means *register a*, not *append*.
     - `0` after `Ctrl-R` (in insert mode) means *register 0*, not *line start*.
     - `Ctrl-R` in insert mode means *paste from register*, not *redo*.
     - `y` at a tmux confirm prompt means *yes*, not *yank*.
     - `h`/`j`/`k`/`l` after tmux prefix mean *left*/*down*/*up*/*right*, not Vim motions.
     - Arrow escape sequences (`\u001b[B` etc.) render as `⎋[B` — unreadable. Use letter keys or set explicit overlays.
     - If an overlay is wrong, add `overlay="correct caption"` to the `Keys()` call. Pass `overlay=""` to suppress a caption entirely.
     - **Every single `[OVERLAY]` line must make sense to a viewer.** If it doesn't, the JSON is wrong.
   - **No extraneous keystrokes** — every key press should serve the demo. If you see navigation that could be shorter (e.g., `0` then `w w w` when `3w` or `f<char>` would do), redesign the file content or pick a better motion.
   - **The featured command must be the most efficient way to do what's shown.** After writing a demo, ask: "Could the viewer achieve the same result with fewer keystrokes using a different command?" If `i` or `a` would be simpler, the demo is bad — come up with a different scenario where the featured command is genuinely the best tool. For example, when demoing `s` (substitute), don't type the same character that was already there — that's just `i` or `a` with extra steps. Show a case where the character *truly changes* and `s` is the only efficient option.
   - **The demo is compelling** — the log should read like a clean, purposeful walkthrough. If a section feels clunky or repetitive, restructure it. Better motions make for better demos.
   - **CRITICAL: Verify the resulting screen state is semantically correct.** After every editing operation, read the full screen rows in the log and confirm the file content makes sense as real code. Don't just check that keys were sent — check that the *result* is right. Common failures:
     - Indenting/unindenting includes a line that shouldn't be in the selection (e.g., indenting a `def` line along with its body, producing invalid Python where `def` and body are at the same level).
     - A visual selection is one line too many or too few because the cursor was on the wrong row after a previous demo.
     - A delete, change, or paste produces malformed code that a viewer would instantly spot as wrong.
     - **If a human would look at the resulting screen and say "that's wrong", the video is wrong.** Fix it.
4. **Check the duration.** Shorts must be **under 60 seconds**. After generating, run:
   ```
   python -c "import subprocess; r = subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0','shellpilot/videos/<NAME>/<NAME>.mp4'], capture_output=True, text=True); print(f'{float(r.stdout.strip()):.1f}s')"
   ```
   If it's over 60 seconds, tighten narration (shorter sentences, cut filler words) and trim waits before re-generating. Don't cut demos — cut words. Longs have no hard limit but should stay focused.
5. **Fix and regenerate** if anything is off. This isn't just about fixing errors — it's about **improving the demo**. A log that works but feels inefficient or cluttered is not done yet. Repeat until the log reads like a crisp, polished tutorial.

---

## Nvim Goes in Setup

Unless the lesson is specifically about opening a file or launching Vim, **nvim must launch in the `setup=[]` block**, not in `steps=[]`. The recording should start with the file already open. No one wants to watch a blank terminal while nvim loads.

### WaitForScreen Must Match the Nvim Status Bar

The `WaitForScreen` text must be something that **only appears after nvim has fully rendered**, NOT in the heredoc output or shell commands. File content words are NOT safe because the `WriteFile` heredoc echoes them to the terminal before nvim even starts. If `WaitForScreen` matches the heredoc text, it returns immediately, then `clear` + nvim launch, nvim switches to the alternate screen (initially blank), and the recording starts with a blank screen.

**Bad:** `WaitForScreen("quest log")` — matches heredoc echo of `# quest log`  
**Bad:** `WaitForScreen("tower")` — matches command echo `nvim tower.py`  
**Good:** `WaitForScreen("All")` — nvim status bar indicator (only appears when nvim renders)

**Always use `WaitForScreen("All", timeout=30.0)`** — the `All` text appears in nvim's status bar when all file content fits on screen (true for all our small demo files). This is the only reliable indicator that nvim has fully loaded and rendered. The 30-second timeout handles slow ConPTY startup (nvim can take 10-15 seconds to render via ConPTY on Windows).

### Verify Screen at Recording Start

The log now includes a `[RECORDING_START]` screen snapshot at the very beginning of recording. **Always check this** — if it shows a blank screen (just `cursor (0,0)`), the setup timing is broken and the video will start with nothing visible. The file content must be fully rendered before steps begin.

### Line Numbers for Line-Navigation Lessons

When the lesson teaches line-based navigation (`G` with count, `%`, `:<number>`, etc.), **turn on line numbers** so the viewer can see which line they're jumping to:

```python
Line("nvim -c 'set number' demo.py"),
```

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
    WaitForScreen("some text from the file content", timeout=10.0),
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

### Sending Escape and Enter

To send an Escape or Enter key, use the **bare string** form, not a `keys` object:

**Good:**
```json
"escape",
{ "type": ":w" },
"enter"
```

**Bad — this types the literal text "escape" into the buffer:**
```json
{ "keys": "escape", "overlay": "back to normal" }
```

The player now defensively remaps `{"keys":"escape"}` → `Escape()` and `{"keys":"enter"}` → `Enter()` so old broken scripts don't silently corrupt the demo, but new scripts should use the bare-string form. If you need a custom overlay, send the actual control byte instead: `{"keys": "\u001b", "overlay": "back to normal"}`.

### Use deterministic positioning when targets are non-letter characters

`f<char>` motions can be unreliable when chained with the rest of a script — especially when the target character is one that has its own normal-mode meaning (`@`, `0`, `:`, `/`, `<Esc>`, etc.) or when the previous step left Vim at a more-prompt (`Press ENTER to continue`, common after `ga`, `:!`, multi-line `:set`, etc.). The first key sent often gets consumed by the prompt and the rest of the keystrokes execute in an unexpected order.

**Symptoms in the log:**
- After `4Gf@` the cursor is one column past `@` (on `#`).
- After `3Gf0` the cursor is several columns past the `0` (because `0` was eaten as start-of-line).
- After any `ga` step, the next `<count>G` lands one line off because the count digit dismissed the prompt.

**Fixes:**
1. **Use absolute column motion `N|`** instead of `f<special>`: `4G12|` jumps line 4 column 12, deterministically. Count column 1-based, including spaces and quotes.
2. **Always dismiss the more-prompt explicitly** with a `\r` step right after `ga`, `:!`, or any command that may produce more than one line of feedback:
   ```json
   { "keys": "ga", "overlay": "show ASCII" },
   { "wait": 0.8 },
   { "say": "..." },
   { "keys": "\r", "overlay": "" }
   ```
3. Prefer `/<target>\r` (search) over `f<target>` when the target is special and you can guarantee it's the first match from the cursor.

### `writeFile` cannot reliably emit TAB characters

`writeFile` types content into the shell via a heredoc. ConPTY/the terminal mangles literal TAB bytes (often dropping them or converting to spaces), so any file that **requires** real tab separators — most notably `tags` files for `:tag`/`Ctrl-W }` previews — silently breaks (the file is created but Vim reports `E431: Format error in tags file`).

**Workaround:** write tab-bearing files via a `line` step using `printf` (which interprets `\t` itself):

```json
{ "line": "printf 'forge\\tcraft.py\\t/^def forge(/\\nbrew\\tcraft.py\\t/^def brew(/\\n' > tags" }
```

Note the doubled backslashes in JSON (`\\t`, `\\n`) so that `printf` sees `\t` and `\n` after JSON decoding.

### Oh-My-Zsh update prompt corrupts recordings

When Oh-My-Zsh decides it's time to check for updates (it runs auto-update on its own cadence), it injects a `[oh-my-zsh] Would you like to update? [Y/n]` prompt at the top of the terminal *before* the recording even begins. The prompt sits there for the whole video and — worse — the prompt's `[Y/n]` reader eats the first keystrokes the script sends, so the actual demo never runs as authored. The recording then completes "successfully" and you get a silently broken video.

`shellpilot/viewer.py:start_recording` now hard-fails with a `RuntimeError` the moment it sees `[oh-my-zsh] Would you like to (update|check for updates)` in the screen text at recording start. If you hit this, run `omz update` in a regular shell (or `zsh -ic 'omz update'`) so the prompt is gone, then re-run the lesson.

**Rule:** if shellpilot raises the Oh-My-Zsh guard, update Oh-My-Zsh once and re-record the affected lesson. Do not work around it.

### Never use `rm -f .../path/*` in setup (zsh `RM_STAR_WAIT`)

Zsh's default `RM_STAR_WAIT` halts on `rm -f .../*` with a `[yn]?` prompt for ~10 seconds. The prompt steals the next keystrokes, which then eat the start of subsequent `cat << EOF > file` heredocs — so the **first multi-file `writeFile` lands empty in the buffer** while later ones look fine. This is the root cause of the `0,0-1 All` "empty buffer" symptom in multi-file `nvim a.py b.py c.py` setups.

**Rule:** never write `rm -f ~/.local/state/nvim/swap/*` (or any `rm -f path/*`). Use `find` with `-delete`:

```json
{ "line": "find ~/.local/state/nvim/swap -mindepth 1 -delete 2>/dev/null" }
```

### `ctrl+X` and `tab` keysyms

`{"keys": "ctrl+x"}` (any case, plus `Ctrl-X` / `C-x` / `5ctrl+a` count-prefixed forms) and `{"keys": "tab"}` are defensively remapped in `player.py` to actual control characters / `\t`. You may use them as-is; the literal-text bug is no longer a concern.

### Dismissing the more-prompt: use `\r`, never `q`

After multi-line `:set`, `:!`, `ga`, `g8`, `:undolist`, `:marks`, etc., Vim shows `Press ENTER or type command to continue`. Always dismiss with `{"keys": "\r"}` (Enter). **Do not use `q`** — once back in normal mode, `q` starts macro-recording and leaves a visible `recording @q` indicator.

### Auto-indent (`=`) demos: stock Neovim has no Python indentexpr

`gg=G` on a Python file produces inconsistent results because stock Neovim ships no Python indent script. Use a filetype with a working indentexpr — JSON, JavaScript, C, HTML, or Lua — for any `=` / `gg=G` demonstration.

### `nvim-surround` (not tpope's vim-surround) — limited delimiters

VimFu uses **nvim-surround** (Lua). Some tpope-style triggers do **not** exist:

- No `<C-T>` "tag on separate lines" mode.
- No self-closing tag detection (`br/>` produces `<br/>...</br/>`, not `<br/>`).
- No `l` / `\` LaTeX environment delimiter.

For inline HTML tags, use `t` then the tag content + `>` + `\r`:

```json
{ "keys": "ysiwtem>\r" }
```

---

## Narration Rules

- **Spell out key names** in narration for TTS clarity. **Preferred:** use the `{key:...}` markup in your `say` strings — `{key:zn}` → "zee en", `{key:zN}` → "zee capital en", `{key:Ctrl-W}` → "control double-you", `{key:Esc}` → "escape", `{key:]s}` → "close bracket ess", `{key:[(}` → "open bracket open paren". The TTS layer expands the markup (including bracket/paren/punctuation symbols) to NATO-style spelling automatically. To include a literal `}` in the body — needed for keys like `]}` — escape it as `\}`: `{key:]\}}` → "close bracket close brace". Use the same exact tokens as the on-screen keystrokes — that way the JSON source stays grep-able and the spoken cadence matches what the viewer sees.
- **Why the markup over hand-spelling**: prior shorts wrote "Z I toggles" hoping TTS would say "zee eye", but OpenAI's voices often slur it into "zai eye" or mangle the spacing. The `{key:...}` form is unambiguous and guarantees consistent pronunciation across all videos. Fall back to spelled form like "D W" only for purely descriptive prose ("the D W combination", not "press D W").
- **Say "capital" before uppercase key names** if you must spell by hand. TTS reads "U" as "you" — the viewer can't tell if you mean `u` or `U`. Always say "capital U", "capital G", "capital X" when referring to an uppercase key. Lowercase is assumed and doesn't need a qualifier — just say the letter. Only add "lowercase" when directly contrasting with the capital version in the same sentence (e.g., "capital U uppercases, lowercase u lowercases"). The `{key:...}` markup handles this automatically.
- **Narration must match the screen.** If you say "the main function" while navigating to a line, that line had better contain a main function. If you say "dollar sign next", the next lesson had better actually be about `$`.
- **Narration must match screen position.** Don't say "let me scroll to the top" when the file just opened and you're already at the top. Don't say "let me scroll down" when the content is already visible. Check cursor position and line numbers in the log before writing positional narration.
- **Narration must match direction of movement.** If you say "select down and right", verify in the log that the cursor column actually increases. Cursor column often carries over between demos — after Demo 2 leaves the cursor at column 10, Demo 3's `gg` + `j` will inherit that column. Add `Keys("0")` or similar to reset before starting a new selection if needed.
- **Verify left/right/top/bottom in split and pane narration.** After `Ctrl-W v`, the cursor stays in the **left** pane. After `Ctrl-W s`, the cursor stays in the **top** pane. If narration says "the left pane scrolled" or "the right pane is at the top", verify against the log's screen snapshot — check which side has `Bot`/`Top` in the status bar and which side the cursor marker (`◂ cursor`) is on. Getting left/right or top/bottom swapped is an easy mistake that makes the whole video wrong.
- **Don't self-correct in narration.** Never say "capital W — wait, I mean lowercase W." Just say the correct thing. A scripted tutorial should sound confident and rehearsed, not improvised.
- **Explain every key the first time you use it.** Don't press a key the viewer hasn't seen before without at least a one-sentence explanation. For example, don't silently press `Ctrl-F` to page down — say "Control F scrolls down one screen" as you use it.
- **Don't include unnecessary keystrokes.** If a command works regardless of cursor position (e.g., `o` opens below no matter where you are on the line), don't press `$` first just "to be safe." Extra keystrokes confuse beginners who think every keystroke is intentional and meaningful.
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

### Don't Undo Between Demos Unnecessarily

**Do NOT reflexively undo** every demo step before moving to the next one. If a demo shows a useful edit (e.g., copying a value and pasting it where it belongs), that's a *correction* — it should stay. Undoing it makes the video feel like a toy demo instead of real editing.

**When to undo:**
- The lesson is *about* undo (e.g., lesson 11).
- You're demonstrating a destructive command (like `dd`) and want to show that Vim is safe — undo once to make the point, then move on.
- Leaving the change would genuinely confuse the next demo (e.g., a line you need to operate on again is now gone).

**When NOT to undo:**
- The edit was a logical improvement to the file (fixing a typo, filling in a value, removing junk). Keep it — it looks like real editing.
- You're about to move to a *different* line for the next demo. The previous edit doesn't interfere.
- You just want a "clean slate" out of habit. Don't. The viewer sees undo-redo-undo-redo as pointless busywork.

**Design files so demos build on each other** rather than resetting between each one. If Demo 1 fixes line 1 and Demo 2 fixes line 3, there's no conflict — just leave Demo 1's result in place and move on. The video should feel like a series of real edits, not isolated experiments.

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

### Lesson Format

Every lesson is a **JSON file** in `curriculum/shorts/` (`curriculum/shorts/NNNN_topic.json`).
Longer demos (over 60 seconds) go in `curriculum/longs/` (`curriculum/longs/long_NNNN_topic.json`).

All lesson logic lives in the JSON file. Do not import step classes directly.

### Running a Lesson

Run directly via the player:
```
python shellpilot/player.py curriculum/shorts/0042_example.json
python shellpilot/player.py curriculum/longs/long_0001_macro_demo.json
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

### Key Overlay Overrides

When a key's default overlay caption is wrong for the context, override it. **Every `[OVERLAY]` line in the log must make sense to the viewer.** The default captions assume Vim context, so they will be wrong for:

- **tmux prompts**: `y` defaults to "yank" but means "yes" at a tmux confirm prompt. Override: `overlay="yes"`.
- **tmux pane navigation**: `h`/`j`/`k`/`l` after prefix mean "left"/"down"/"up"/"right", not Vim motions.
- **Shell context**: Any key pressed outside of Vim (e.g., at a shell prompt or in a tmux mode) needs its overlay checked.
- **Arrow keys**: Escape sequences like `\u001b[B` render as `⎋[B` in the overlay — unreadable. The viewer's `KEY_DISPLAY` dict now maps common arrow sequences to proper symbols (`↑↓←→`, `⌃↑` for Ctrl+Arrow, etc.), so basic arrows should display correctly automatically. If you use an unusual arrow variant not in `KEY_DISPLAY`, always set an explicit `overlay` (e.g., `"overlay": "↓"`). **After generating, grep the log for `⎋[` in `[OVERLAY]` lines to catch any that slipped through.**

```python
# Register names after q or @ — 'a' normally shows "append"
Keys("q"),                                  # shows "record macro" (correct)
Keys("a", overlay="register a"),            # override "append" → "register a"

# Insert-mode Ctrl-R pastes from register — not "redo"
Keys("\x12", overlay="paste register"),     # Ctrl-R in insert mode
Keys("0", overlay="register 0"),            # "0" register, not "line start"

# tmux confirm prompts — 'y' is "yes", not "yank"
Keys("y", overlay="yes"),                   # at a tmux kill-pane? prompt
Keys("n", overlay="no"),                    # decline a tmux prompt

# Multi-char keys show as a single overlay
Keys("qa", overlay="record into a"),        # alternative: send both at once

# Suppress a caption entirely
Keys("x", overlay=""),                      # shows the key but no caption
```

### Key Overlay Grouping: Phrases vs. Sequences

Not every multi-key sequence belongs in a single `keys` step. The rule: **group keys that form a Vim "phrase" — a single semantic action. Split keys that are independent navigational steps.**

**Good as a single step (Vim phrases):**
- `diw` — "delete inner word" is one mental action
- `ci{` — "change inner braces" is one command
- `da<` — "delete around angle brackets" is one operation
- `vi"` — "select inner quotes" is one text object
- `3dd` — "delete 3 lines" is one counted command
- `f<` — "find the angle bracket" is one motion

**Bad as a single step (independent navigations jammed together):**
- `j0f<` — this is three separate actions: go down, go to start of line, find character. Each should be its own step so the viewer sees each motion individually with its own overlay.
- `gg0` — go to top of file, then go to column 0. Two separate motions.
- `jjj` — use `3j` instead, or split into individual `j` steps if you want the viewer to see each move.

**Why this matters:** The key overlay shows each step as a caption (e.g., `j  down`, `0  start of line`, `f<  find <`). If you cram `j0f<` into one step, the viewer sees one flash of `j0f<` with no explanation of what each part does. Beginners won't be able to parse it. Split them so each key gets its own moment on screen.

**Rule of thumb:** If you would explain the keys with "and then" between them, they should be separate steps. "Go down *and then* go to the start of the line *and then* find the angle bracket" = three steps. "Delete inner word" = one step.

### Key Overlay Captions: Don't Repeat the Keys

The key overlay display has two parts: the **keys** (shown prominently) and the **caption** (shown beside them as explanation). The viewer already sees what keys were pressed — the caption's job is to explain *what they mean*, not echo them.

**Bad (repeating the keys in the caption):**
```python
Keys("diw", overlay="diw  delete inner word")
Keys("\"ayy", overlay="\"ayy  yank line into a")
Keys("ci{", overlay="ci{  change inner braces")
```

**Good (caption explains, doesn't repeat):**
```python
Keys("diw", overlay="delete inner word")
Keys("\"ayy", overlay="yank line into a")
Keys("ci{", overlay="change inner braces")
```

The keys are right there on screen. Repeating them in the caption wastes space and looks redundant. Just write the meaning.

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

- [ ] `[RECORDING_START]` screen snapshot shows file content (not blank — must see `~` lines and status bar)
- [ ] `[WAIT] Found after X.Xs` in stdout — confirm timing is reasonable (>3s means nvim loaded; <1s means it matched heredoc)
- [ ] Log inspected — cursor positions correct
- [ ] Log inspected — navigation is efficient (no unnecessary `0`, `f`, `^` unless teaching those)
- [ ] Narration matches what's on screen
- [ ] No nvim launch visible in the recording (unless that's the lesson)
- [ ] `WaitForScreen("All")` used (nvim status bar, never file content or command text)
- [ ] **No garbled arrow key overlays** — search the log for `[OVERLAY]` lines containing `⎋[` (e.g., `⎋[1;5C`, `⎋[A`). These are raw escape sequences leaking into the display. The viewer's `KEY_DISPLAY` dict maps common arrow sequences (`\x1b[A`–`D`, `\x1b[1;5A`–`D`, etc.) to proper symbols (`↑`, `⌃→`, etc.), so the key display should show arrows, not escape codes. If you still see `⎋[` in an overlay, either the escape sequence isn't in `KEY_DISPLAY` (add it) or the JSON `keys` field uses a non-standard encoding (fix it).

---

## Publishing Pipeline (after a video is recorded and ready)

Whenever you upload or re-upload a video (whether that's a single lesson or a batch), **always** run these four steps in order, even if the user only asked you to "upload" or "re-record". The QR codes in the book and the `/r/` short links on the site embed YouTube video IDs — a fresh upload changes the ID, so any link that isn't refreshed will silently point to the old (or deleted) video.

1. **Upload to YouTube** — `python upload_youtube.py [--schedule … --schedule-daily] <json paths>`. This writes the new `youtube.videoId` back into each lesson JSON.
2. **Refresh redirects** — `python content/render_redirects.py`. The `/r/v-XXXX/` pages embed the video ID from the JSON; if you skip this, every short URL still points at the old ID.
3. **Deploy the site** — `python content/deploy_site.py --skip-sim` (omit `--skip-sim` if the simulator changed). This re-runs the renderers and syncs `content/output/html/` into `docs/`.
4. **Update `unpublished_shorts.txt`** — remove the lines for the lessons you just uploaded (they're no longer unpublished). The file is hand-maintained; nothing regenerates it.

Then `git add -A && git commit && git push`. Include the new video IDs and the schedule (if any) in the commit message so the audit trail is self-explanatory.

If a re-recorded video reuses the same lesson JSON, **the YouTube ID changes** — the previous step 2 is not optional. Skipping it is the most common cause of "the QR code in the printed book opens the wrong video" reports.

---

