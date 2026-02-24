# VimFu Simulator – Development Instructions

## Architecture Overview

The VimFu simulator is a pure-JavaScript Vim engine with MVC architecture:

- **Buffer** (`src/buffer.js`) – line-based text storage
- **VimEngine** (`src/engine.js`) – core Vim command dispatch, mode handling, cursor, undo/redo
- **Screen** (`src/screen.js`) – produces frame dicts with styled runs (theme: `monokai`)
- **Controller** (`src/controller.js`) – maps DOM keyboard events to `feedKey()` calls
- **Renderer** (`src/renderer.js`) – renders frames to an HTML canvas

No build step. ES modules served via HTTP (`python serve.py` from `sim/`).
Use `serve.py` (not `python -m http.server`) — it sends `Cache-Control: no-cache`
headers on every response so the browser always loads fresh JS modules.

## Workflow for Adding a New Feature

### 1. Research

- **Read the Neovim docs** for the feature. Understand exact behavior, edge cases, and interaction with other features (operators, counts, visual mode, dot repeat, undo).
  - `:help q` for macros, `:help @`, etc.
  - Pay attention to exclusive/inclusive motion behavior, linewise vs charwise, and how counts interact.

- **Read `curriculum/Curriculum.md`** to see what lessons reference the feature. This tells you what behavior users will expect.

- **Read any demo scripts** that use the feature (e.g. `curriculum/longs/`, `curriculum/shorts/`). These show real usage patterns that must work correctly.

### 2. Plan the Implementation

- Identify what state needs to be added to the `VimEngine` constructor.
- Identify which mode handlers are affected (`_normalKey`, `_insertKey`, `_visualKey`, `_commandKey`).
- Consider interactions with:
  - **Counts** (e.g. `3@a` runs macro 3 times)
  - **Dot repeat** (`_lastChange` / `_recording` / `_recordedKeys`)
  - **Undo/redo** (should a macro replay be undoable as a single unit?)
  - **Operator-pending mode** (does this feature work as a motion for `d`/`c`/`y`?)
  - **Visual mode** (does it work in visual mode?)
  - **Status line / command line display**

### 3. Write Test Cases

Create a test file `test/cases/test_<feature>.py` following the existing pattern:

```python
"""Description of what this test suite covers."""

CASES = {
    "descriptive_name": {
        "keys": "qaiworldEscqGo@a",  # the keystrokes to replay
        "initial": "hello\n",         # initial buffer content
    },
    # ... more cases ...
}
```

Key formatting:
- `\x1b` = Escape
- `\r` = Enter  
- `\x12` = Ctrl-R (redo)
- `\x06` = Ctrl-F (page down)
- `\x02` = Ctrl-B (page up)
- `\x04` = Ctrl-D (half page down)
- `\x15` = Ctrl-U (half page up)
- Regular characters are literal

Guidelines for test cases:
- **Cover basic usage** – the simplest possible case
- **Cover counts** – e.g. `3@a`
- **Cover edge cases** – empty buffer, single line, end of file
- **Cover interactions** – with operators, visual mode, dot repeat, undo
- **Cover the curriculum** – every usage pattern from Curriculum.md and demo scripts
- **Don't overfit** – tests should verify general behavior, not specific implementation details

### 4. Capture Ground Truth from Neovim

Run the ground truth capture script against Neovim (using the user's WSL config with Monokai colorscheme):

```bash
cd sim
C:/source/vimfu/.venv/Scripts/python.exe test/nvim_ground_truth_v2.py --suite <feature>
```

This produces `test/ground_truth_<feature>.json` with the expected screen output for each test case.

Neovim settings:
- Uses the WSL Neovim config (Monokai colorscheme)
- Screen: 40 cols × 20 rows
- No swap (`-n`), no shada (`-i NONE`)

### 5. Run Comparison Tests

```bash
cd sim
node test/compare_test_v2.js --suite <feature>
```

This replays each test through the VimFu engine, renders via `Screen`, and compares the frame against the Neovim ground truth. Differences are shown as colored diffs.

### 6. Implement the Feature

Edit `src/engine.js` (and `src/screen.js` if display changes are needed).

After each change, re-run the comparison tests:

```bash
node test/compare_test_v2.js --suite <feature>
```

And always check for regressions across ALL suites:

```bash
node test/compare_test_v2.js
```

### 7. Update Reference.md

Whenever you add or change a feature, update `Reference.md` to document it.
This keeps the command reference in sync with the implementation. Add:

- New commands to the appropriate section table
- Short forms / aliases alongside the canonical form
- Behavioral notes where needed (e.g. edge cases, interactions)

### 8. Run All Unit Test Suites

```bash
node test/test_syntax_screen.js    # 46 tests – syntax color integration
node test/test_highlight.js        # 126 tests – tokenizer grammar
node test/test_shell.js            # 82 tests – VFS, shell, session
node test/test_session_screen.js   # 22 tests – session frame snapshots
node test/test_tmux.js             # 75 tests – tmux behavioral assertions
node test/test_tmux_screen.js      # 40 tests – tmux frame snapshots
```

If you changed syntax/theme, also run the nvim color comparison:

```bash
python test/compare_nvim_syntax.py  # must show 0 mismatches
```

If you changed tmux theme/borders/status bar, also run the tmux color comparison:

```bash
python test/compare_tmux_colors.py  # must show 11/11 passed
```

### 9. Final Verification

Before considering a feature complete:

1. All new test cases pass against Neovim ground truth
2. Zero regressions on all existing suites (`node test/compare_test_v2.js`)
3. All unit tests pass:
   ```bash
   node test/test_syntax_screen.js
   node test/test_highlight.js
   node test/test_shell.js
   node test/test_session_screen.js
   node test/test_tmux.js
   node test/test_tmux_screen.js
   ```
4. If syntax/theme changed: nvim color comparison has 0 mismatches (`python test/compare_nvim_syntax.py`)
5. If tmux theme/borders changed: tmux color comparison has 11/11 passed (`python test/compare_tmux_colors.py`)
6. If shell/session changed: regenerate session ground truth (`node test/gen_session_ground_truth.js`)
7. If tmux changed: regenerate tmux ground truth (`node test/gen_tmux_ground_truth.js`)
7. **Browser verification** — serve the sim, Ctrl+Shift+R, and manually test:
   - `vim demo.py` → syntax colors (monokai: pink keywords, yellow strings, purple numbers)
   - `:q` → shell prompt flows right after output
   - `vim` then `:e demo.py` → syntax colors also work via `:e`
   - General feel: does it look like a real terminal?

## Test Inventory

Test suites are in `test/cases/test_*.py`. Ground truth is in `test/ground_truth_*.json`.

Run `node test/compare_test_v2.js` to see current pass/fail counts across all suites.

## Test Layers

The sim has multiple test layers. Each layer catches different kinds of bugs.
All layers must pass before a feature is considered done.

### Layer 1: Vim Engine Ground Truth (nvim comparison)

**What it tests:** Vim motions, operators, text objects — text, cursor, and colors.
**Ground truth source:** Real nvim (with user's Monokai config), captured via ShellPilot + pyte.
**Theme:** `monokai` — tests validate that the sim matches Neovim's actual Monokai rendering.

```bash
cd sim
# Capture ground truth for a specific suite
C:/source/vimfu/.venv/Scripts/python.exe test/nvim_ground_truth_v2.py --suite <feature>
# Or regenerate all suites
C:/source/vimfu/.venv/Scripts/python.exe test/run_all_suites.py

# Compare sim against ground truth
node test/compare_test_v2.js --suite <feature>  # one suite
node test/compare_test_v2.js                     # all suites
```

### Layer 2: Syntax Highlighting – Tokenizer Unit Tests

**What it tests:** The regex grammar produces correct scope assignments for Python constructs.
**Ground truth source:** Hand-written assertions checked against nvim behavior.
**File:** `test/test_highlight.js` (126 tests)

```bash
node test/test_highlight.js
```

### Layer 3: Syntax Highlighting – Screen Color Integration

**What it tests:** The Screen correctly maps scope → color for each theme, and produces correct color runs in the Frame dict.
**Ground truth source:** Self-generated snapshots (`test/syntax_ground_truth.json`) plus hand-written assertions.
**Files:** `test/test_syntax_screen.js` (46 tests), `test/gen_syntax_ground_truth.js`

```bash
node test/gen_syntax_ground_truth.js   # regenerate after grammar/theme changes
node test/test_syntax_screen.js
```

### Layer 4: Syntax Highlighting – Nvim Color Verification

**What it tests:** The sim's rendered colors for a real Python file match real nvim's colors, column by column, across every visible line.
**Ground truth source:** Real nvim with syntax on, captured via ShellPilot + pyte.
**Files:** `test/capture_nvim_syntax.py`, `test/compare_nvim_syntax.py`

```bash
cd sim
# Step 1: Capture what nvim actually renders (only needed once, or when
#          nvim changes or sample file changes)
python test/capture_nvim_syntax.py
# Writes test/nvim_syntax_colors.json

# Step 2: Compare sim output against nvim capture
python test/compare_nvim_syntax.py
# Must show: Mismatched lines: 0
```

**CRITICAL:** This test catches theme/grammar mismatches that unit tests miss.
The capture uses `nvim -u _nvim_init.vim` (syntax on, filetype on, termguicolors)
and renders the full `demo.py` sample. The comparison script renders the same file
through the sim (via `Screen` with `nvim_default` theme) and diffs every column's
foreground color.

### Layer 5: Shell + Session Integration

**What it tests:** ShellSim (prompt, commands, output layout), SessionManager (shell↔vim lifecycle, :w/:q/:e, VFS), full frame output.
**Ground truth source:** Self-generated snapshots (`test/session_ground_truth.json`).
**Files:** `test/test_shell.js` (82 tests), `test/test_session_screen.js` (22 tests), `test/gen_session_ground_truth.js`

```bash
node test/gen_session_ground_truth.js  # regenerate after shell/session changes
node test/test_shell.js
node test/test_session_screen.js
```

### Layer 6: Tmux Screen Tests (frame snapshot comparison)

**What it tests:** Tmux integration — pane layout, borders (active vs inactive color), status bar (session name, window list, zoom indicator, clock), overlays (command prompt, rename, confirm, copy mode, help, pane numbers, window list), split/navigate/zoom/detach/reattach lifecycle, and vim-inside-tmux rendering.
**Ground truth source:** Self-generated snapshots (`test/tmux_ground_truth.json`).
**Files:** `test/test_tmux_screen.js` (40 tests), `test/gen_tmux_ground_truth.js`, `test/test_tmux.js` (75 behavioral tests)

```bash
node test/gen_tmux_ground_truth.js     # regenerate after tmux/session changes
node test/test_tmux_screen.js          # 40 tests – tmux frame snapshots
node test/test_tmux.js                 # 75 tests – tmux behavioral assertions
```

**Note:** The tmux status bar includes a live clock. Both the generator and the
test runner freeze the time (HH:MM → 00:00, date → 01-Jan-26) before comparison
so that tests are deterministic. The `tmux_four_panes` scenario uses non-default
dimensions (24×80) to test a 2×2 grid layout.

### Layer 7: Tmux Color Verification (real tmux comparison)

**What it tests:** The sim's tmux theme colors match what real tmux renders — status bar segment colors (session name, separators, active/inactive windows, clock, date), border colors (active vs inactive pane), and command/copy prompt colors.
**Ground truth source:** Real tmux running under WSL, captured via ShellPilot + pyte.
**Files:** `test/capture_tmux_colors.py`, `test/compare_tmux_colors.py`, `test/tmux_real_colors.json`

```bash
cd sim
# Step 1: Capture what real tmux actually renders (only needed once, or when
#          the user's tmux config changes)
C:/source/vimfu/.venv/Scripts/python.exe test/capture_tmux_colors.py
# Writes test/tmux_real_colors.json (9 scenarios)

# Step 2: Compare sim tmux output against real tmux capture
C:/source/vimfu/.venv/Scripts/python.exe test/compare_tmux_colors.py
# Must show: Checks: 11/11 passed
```

**Scenarios captured:** fresh launch, vertical split, horizontal split, two
windows, renamed window, vsplit active right/left, command prompt, copy mode.

**Comparison strategy:** The test compares *color sequences* (ordered fg/bg/bold
transitions) rather than per-column values, since text content differs between
sim and real (session name "0" vs "test", frozen vs live timestamps). For borders,
the test compares the *primary* (most frequent) border color, since real tmux uses
mixed per-row border coloring as an internal rendering optimization.

**CRITICAL:** This is the only test that verifies the sim's tmux looks like the
user's actual tmux. The Monokai palette (`a6e22e` session green, `49483e` selection,
`75715e` comment gray, `66d9ef` cyan clock, `272822` status bg) was captured from
real tmux — not guessed from screenshots.

### Layer 8: Browser End-to-End Verification

**What it tests:** The actual user experience — serving the page, typing keys, seeing the rendered output in the canvas.
**Ground truth source:** Your eyeballs + the monokai theme that the GIF pipeline uses.

```bash
cd sim
python serve.py
# Open http://localhost:8000
# No need for Ctrl+Shift+R — serve.py sends no-cache headers
# Type: vim demo.py → verify syntax colors (monokai palette)
# Type: :q → verify shell prompt is right after output (not stuck at bottom)
# Type: ls → verify output flows naturally
# Type: vim → then :e demo.py → verify syntax colors work via :e too
```

**This layer is not automated.** It is the final sanity check that catches
integration bugs that slip through all the unit/snapshot tests.

## Lessons Learned: How Bugs Slip Through

### Theme consistency (resolved Feb 2026)

The simulator uses the `monokai` theme everywhere — browser, tests, and ground
truth capture. Ground truth is generated against Neovim with the user's WSL
config (which uses Monokai). The compare tests validate colors match exactly.

**Rule:** Do not use `-u NONE` for Neovim. Do not use `nvim_default` theme.
Everything uses the user's actual Monokai colorscheme.

### The `:e` missing filename bug (caught Feb 2026)

**Bug:** Opening a file via `:e demo.py` inside vim showed no syntax colors.

**Root cause:** The SessionManager's `:e` handler set `this._vimFilename`
but forgot to set `this.engine.filename`. Without `engine.filename`, the
`grammarForFile()` call in `Screen.render()` returned null → no highlighting.

**Why tests missed it:** No session test case covered `:e` with a `.py` file
and then checked the frame's color runs. The existing `:e` tests only checked
that the file content loaded correctly, not that syntax highlighting activated.

**Lesson:** When a feature has two code paths (launch from shell vs `:e`),
test BOTH paths through to the rendered frame including colors.

### The shell prompt stuck at bottom (caught Feb 2026)

**Bug:** After running `ls`, the output appeared at the top but the prompt
stayed glued to the last row (row 19), with blank rows in between.

**Root cause:** `ShellSim.getScreen()` always reserved the last row for the
prompt and filled rows 0 to `rows-2` with output + blank padding. A real
terminal flows the prompt immediately after the output.

**Why tests missed it:** The shell tests used `getOutputLines()` which
filtered to non-empty lines and searched with `.some()`, making them
position-agnostic. The session ground truth snapshots captured the wrong
layout but then the test compared against that same wrong snapshot — a
self-referential loop. No test compared against what a real terminal does.

**Lesson:** Self-generated ground truth only catches *regressions*, not
*initial correctness*. For layout/visual behavior, you need either:
(a) ground truth from a real terminal (ShellPilot capture), or
(b) explicit hand-written assertions about specific row positions.

## Common Gotchas

- **Dot repeat** uses `_recording`/`_recordedKeys`/`_lastChange` – these names are about dot repeat, NOT macro recording. Macros need separate state.
- **`_saveSnapshot()`** must be called before buffer mutations for undo to work.
- **`_clampCursor()`** and **`_ensureCursorVisible()`** are called automatically after `feedKey()`.
- **Exclusive vs inclusive motions** affect operator behavior. See `:help exclusive`.
- **The `commandLine` property** is what shows on the bottom line of the screen. Neovim shows `recording @a` there during macro recording.
- **Tab handling**: Neovim uses `tabstop=8`, `noexpandtab` by default. Tabs render as variable-width spaces.
