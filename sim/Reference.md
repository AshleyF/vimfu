# VimFu Simulator — Command Reference

Exhaustive reference of every key, command, and feature supported.

---

## Modes

| Mode | Entry | Status line |
|---|---|---|
| Normal | `Escape` / `Ctrl-[` from any mode | *(empty)* or `recording @x` |
| Insert | `i`, `I`, `a`, `A`, `o`, `O`, `s`, `S`, `c…`, `gi`, `gI` | `-- INSERT --` |
| Replace | `R` | `-- REPLACE --` |
| Visual | `v` | `-- VISUAL --` |
| Visual Line | `V` | `-- VISUAL LINE --` |
| Visual Block | `Ctrl-V` | `-- VISUAL BLOCK --` |
| Command | `:`, `/`, `?` | shows typed command |

---

## Normal Mode

> **Key:** In tables below, the **Count** column shows ✅ if `[count]` is
> supported, or **—** if the command ignores / doesn't take a count.
> All listed commands are implemented.

### Motions

| Key | Count | Description |
|---|---|---|
| `h` / `←` | ✅ | Left (stops at col 0) |
| `l` / `→` | ✅ | Right (stops at last char) |
| `j` / `↓` | ✅ | Down (sticky column) |
| `k` / `↑` | ✅ | Up (sticky column) |
| `w` | ✅ | Word forward |
| `W` | ✅ | WORD forward |
| `b` | ✅ | Word backward |
| `B` | ✅ | WORD backward |
| `e` | ✅ | End of word forward (inclusive) |
| `E` | ✅ | End of WORD forward (inclusive) |
| `ge` | ✅ | End of word backward |
| `gE` | ✅ | End of WORD backward |
| `0` | ✅ | Start of line (col 0) |
| `^` | ✅ | First non-blank on line |
| `$` | ✅ | End of line (`2$` = end of next line) |
| `_` | ✅ | First non-blank, count−1 lines down |
| `g_` | ✅ | Last non-blank on line |
| `f{char}` | ✅ | Find char forward (inclusive; `Tab` = literal tab) |
| `F{char}` | ✅ | Find char backward (inclusive; `Tab` = literal tab) |
| `t{char}` | ✅ | Till char forward (exclusive; `Tab` = literal tab) |
| `T{char}` | ✅ | Till char backward (exclusive; `Tab` = literal tab) |
| `;` | ✅ | Repeat last `f`/`F`/`t`/`T` |
| `,` | ✅ | Repeat last find, reversed |
| `%` | ✅ | Match bracket `(){}[]` |
| `{count}%` | ✅ | Go to N% of file |
| `{` | ✅ | Paragraph backward |
| `}` | ✅ | Paragraph forward |
| `(` | ✅ | Sentence backward |
| `)` | ✅ | Sentence forward |
| `gg` | ✅ | Go to line N (default: first) |
| `G` | ✅ | Go to line N (default: last) |
| `H` | ✅ | Screen top (count = offset) |
| `M` | ✅ | Screen middle |
| `L` | ✅ | Screen bottom (count = offset) |
| `+` / `Enter` | ✅ | Next line, first non-blank |
| `-` | ✅ | Prev line, first non-blank |
| `\|` | ✅ | Go to column N (1-based) |
| `go` | ✅ | Go to byte offset N in the buffer |
| `Backspace` | ✅ | Left, wrapping to prev line |
| `Space` | ✅ | Right, wrapping to next line |
| `n` | ✅ | Next search match |
| `N` | ✅ | Prev search match |
| `*` | ✅ | Search word under cursor forward |
| `#` | ✅ | Search word under cursor backward |
| `g*` | ✅ | Search word under cursor forward (no `\b` boundaries) |
| `g#` | ✅ | Search word under cursor backward (no `\b` boundaries) |
| `gn` | ✅ | Search forward and visually select match (or operate on match with pending operator) |
| `gN` | ✅ | Search backward and visually select match |
| `gj` | ✅ | Down one display line (wrapping-aware) |
| `gk` | ✅ | Up one display line (wrapping-aware) |
| `g0` | ✅ | Start of display line |
| `g$` | ✅ | End of display line |
| `g^` | ✅ | First non-blank of display line |
| `gm` | ✅ | Middle column of screen |
| `gM` | ✅ | Middle of text on line |

### Editing

| Key | Count | Description |
|---|---|---|
| `x` / `Delete` | ✅ | Delete char under cursor |
| `X` | ✅ | Delete char before cursor |
| `s` | ✅ | Substitute N chars (delete + insert) |
| `S` | ✅ | Substitute N lines (preserves indent) |
| `r{char}` | ✅ | Replace N chars with {char} |
| `R` | ✅ | Enter replace mode |
| `~` | ✅ | Toggle case, advance cursor |
| `J` | ✅ | Join N lines (smart spacing) |
| `gJ` | ✅ | Join N lines (no spacing) |
| `D` | ✅ | Delete to end of line (`d$`); `2D` deletes to EOL + next line |
| `C` | ✅ | Change to end of line (`c$`) |
| `Y` | ✅ | Yank to end of line (`y$`) |
| `u` | ✅ | Undo |
| `Ctrl-R` | ✅ | Redo |
| `.` | ✅ | Repeat last change (count overrides) |
| `Ctrl-A` | ✅ | Increment number at/after cursor |
| `Ctrl-X` | ✅ | Decrement number at/after cursor |
| `Ctrl-G` | ✅ | Show file info (name, lines, bytes) |
| `Ctrl-Z` | ❌ | Suspend Vim (Unix only — not implemented, see note below) |
| `ga` | ✅ | Show ASCII/hex/octal of char under cursor |

> **`Ctrl-Z` note:** In real Vim on Unix (Linux/macOS), `Ctrl-Z` sends SIGTSTP to
> suspend the editor and return to the shell. Typing `fg` at the shell prompt
> resumes Vim exactly where you left off. This is a Unix job control feature —
> it does not work on Windows. The simulator does not implement `Ctrl-Z` because
> the project was developed on Windows (ConPTY) where ground truth captures for
> suspend/resume could not be generated. The cross-platform alternative is `:!cmd`
> which runs a shell command from within Vim without suspending.

| `gd` | ✅ | Go to local declaration of word under cursor |
| `gD` | ✅ | Go to global declaration (first occurrence of word in file) |
| `g8` | ✅ | Show hex value of character under cursor |
| `gp` | ✅ | Put after, move cursor past pasted text |
| `gP` | ✅ | Put before, move cursor past pasted text |
| `U` | ✅ | Undo all changes on current line |
| `K` | ✅ | Keyword lookup (shows error in simulator) |
| `&` | ✅ | Repeat last `:s` on current line |
| `g&` | ✅ | Repeat last `:s` on all lines (`:%s//~/&`) |

### Operators

Operators combine with any motion or text object: `{op}[count]{motion}`.

| Key | Line form | Description |
|---|---|---|
| `d` | `dd` | Delete |
| `c` | `cc` | Change (delete + enter insert) |
| `y` | `yy` | Yank (copy) |
| `>` | `>>` | Indent |
| `<` | `<<` | Dedent |
| `gu` | `guu` | Lowercase |
| `gU` | `gUU` | Uppercase |
| `g~` | `g~~` | Toggle case |
| `=` | `==` | Auto-indent (C-style brace indentation) |
| `gq` | `gqq` | Format text (join lines; cursor moves to start) |
| `gw` | `gww` | Format text (join lines; cursor stays) |
| `g?` | `g??` / `g?g?` | ROT13 encode |
| `!` | `!!` | Shell filter — pipes text through external command |

Examples: `d3w`, `ciw`, `>}`, `gUap`, `yy`, `5dd`, `<<`, `dG`, `c/foo↵`

Special: `cw` on a word behaves like `ce` (doesn't include trailing space). `dw` at EOL doesn't cross lines. `cc` / `S` preserve leading indent.

#### Shell Filter Operator (`!`)

`!{motion}cmd↵` — filter lines through an external command. The operator selects
lines based on the motion, then enters command mode pre-filled with `:.,.+N!`.
Type the shell command and press Enter.

| Key | Description |
|---|---|
| `!{motion}cmd↵` | Filter lines covered by motion through `cmd` |
| `!!cmd↵` | Filter current line through `cmd` |
| `{count}!!cmd↵` | Filter count lines through `cmd` |
| `:{range}!cmd` | Ex form: filter range through `cmd` |
| Visual `!cmd↵` | Filter visual selection through `cmd` |

Supported shell commands: `sort`, `grep`, `cat`, `uniq`, `tr`, `rev`, `tac`,
`head`, `tail`, `sed`, `wc`.

### Put (Paste)

| Key | Count | Description |
|---|---|---|
| `p` | ✅ | Put after cursor (linewise: below) |
| `P` | ✅ | Put before cursor (linewise: above) |
| `[p` | ✅ | Put before with indent adjustment |
| `]p` | ✅ | Put after with indent adjustment |

**Cursor placement after put:** When putting characterwise text (e.g. from `yw`,
`d$`, `x`), the cursor lands at the **end** of the pasted text. When putting
linewise text (e.g. from `yy`, `dd`), the cursor lands at the **beginning**
(first non-blank) of the pasted block. This applies to both `p` and `P`.

### Enter Insert Mode

| Key | Count | Description |
|---|---|---|
| `i` | ✅ | Insert before cursor (`3i` repeats text) |
| `I` | ✅ | Insert at first non-blank |
| `a` | ✅ | Append after cursor |
| `A` | ✅ | Append at end of line |
| `o` | ✅ | Open line below (inherits indent) |
| `O` | ✅ | Open line above (inherits indent) |
| `gi` | ✅ | Insert at last insert position |
| `gI` | ✅ | Insert at column 0 |

### Scroll

| Key | Count | Description |
|---|---|---|
| `Ctrl-D` | ✅ | Half-page down (sticky count) |
| `Ctrl-U` | ✅ | Half-page up (sticky count) |
| `Ctrl-F` | ✅ | Full page forward |
| `Ctrl-B` | ✅ | Full page backward (⚠️ conflicts with tmux prefix — see Tmux section) |
| `Ctrl-E` | ✅ | Scroll viewport down 1 line |
| `Ctrl-Y` | ✅ | Scroll viewport up 1 line |
| `zz` | ✅ | Center current line |
| `zt` | ✅ | Current line to top |
| `zb` | ✅ | Current line to bottom |
| `z.` | ✅ | Center current line, cursor to first non-blank |
| `z-` | ✅ | Current line to bottom, cursor to first non-blank |
| `z Enter` | ✅ | Current line to top, cursor to first non-blank |
| `z+` | ✅ | Scroll: line below window to top, cursor to first non-blank |
| `z^` | ✅ | Scroll: line above window to bottom, cursor to first non-blank |

### Horizontal Scroll (nowrap mode)

When `:set nowrap` is active, long lines are truncated at the screen edge
instead of wrapping. The viewport can be scrolled horizontally.

| Key | Description |
|---|---|
| `zl` | Scroll screen right by N columns |
| `zh` | Scroll screen left by N columns |
| `zL` | Scroll screen right by half screen width |
| `zH` | Scroll screen left by half screen width |
| `zs` | Scroll so cursor column is at left edge |
| `ze` | Scroll so cursor column is at right edge |

Auto-scroll: when the cursor moves past the visible area, the viewport
auto-adjusts. Small overflows scroll the minimum amount; large jumps
recenter the cursor.

### Folding (Manual)

The simulator supports manual folding (`foldmethod=manual`). Create folds with
`zf{motion}` or visual selection + `zf`. Closed folds render as a single line
showing the fold summary. Cursor movement (`j`/`k`) skips over closed folds.

| Key | Description |
|---|---|
| `zf{motion}` | Create fold over motion range (operator) |
| `zf` (visual) | Create fold from visual selection |
| `zo` | Open fold under cursor |
| `zO` | Open all folds under cursor (recursive) |
| `zc` | Close fold under cursor |
| `zC` | Close all folds under cursor (recursive) |
| `za` | Toggle fold under cursor |
| `zA` | Toggle all folds under cursor (recursive) |
| `zd` | Delete fold under cursor |
| `zD` | Delete all folds under cursor (recursive) |
| `zE` | Delete all folds in buffer |
| `zR` | Open all folds |
| `zM` | Close all folds |
| `zj` | Move to next fold start |
| `zk` | Move to previous fold |

### Window Splits

The simulator supports horizontal window splits. Each window shows the same
or different buffers with independent cursor and scroll positions.

| Key | Description |
|---|---|
| `:sp[lit]` | Horizontal split (new window above) |
| `:vsp[lit]` | Vertical split (same as `:sp` in flat model) |
| `:clo[se]` | Close current window |
| `:on[ly]` | Close all other windows |
| `Ctrl-W s` | Same as `:sp` |
| `Ctrl-W v` | Same as `:vsp` |
| `Ctrl-W w` | Cycle to next window |
| `Ctrl-W j` | Move to window below |
| `Ctrl-W k` | Move to window above |
| `Ctrl-W h` | Move to window left |
| `Ctrl-W l` | Move to window right |
| `Ctrl-W c` | Close current window |
| `Ctrl-W o` | Close all other windows |
| `Ctrl-W q` | Close current window |
| `Ctrl-W T` | Move current window to a new tab |

> **Browser limitation:** Desktop browsers reserve `Ctrl-W` as "close tab" and
> intercept the keystroke before JavaScript can capture it. The simulator's
> `preventDefault()` call is ignored for this browser-reserved shortcut.
>
> **Workaround:** Use `Ctrl-Q` as a drop-in replacement — the simulator maps
> `Ctrl-Q` → `Ctrl-W` so every command in the table above works by pressing
> `Ctrl-Q` instead (e.g. `Ctrl-Q s` to split, `Ctrl-Q w` to cycle). All
> commands also work via the **virtual keyboard** (touch/mobile) or through
> their ex-command equivalents (`:sp`, `:vsp`, `:close`, `:only`).

### Buffer List

The engine maintains a buffer list tracking all open buffers. Each buffer
preserves its own cursor, scroll position, undo history, marks, and folds.

| Key | Description |
|---|---|
| `:ls` / `:buffers` | List all buffers |
| `:bn[ext]` | Switch to next buffer |
| `:bp[rev]` | Switch to previous buffer |
| `:b[uffer] N` | Switch to buffer N |
| `:b[uffer] name` | Switch to buffer by name (partial match) |
| `:bd[elete][!]` | Delete current buffer |
| `:enew[!]` | Edit a new unnamed buffer |
| `Ctrl-^` / `Ctrl-6` | Toggle alternate buffer |

Buffer indicators in `:ls` output:
- `%` — current buffer
- `#` — alternate buffer
- `a` — active (loaded and displayed)
- `+` — modified

### Tab Pages

Tab pages provide a way to organize multiple window layouts. Each tab
contains its own set of windows. A tab line appears when ≥2 tabs exist.

| Key | Description |
|---|---|
| `:tabnew` | Open new tab with empty buffer |
| `:tabe[dit]` | Open new tab with empty buffer |
| `:tabn[ext]` | Go to next tab |
| `:tabp[rev]` | Go to previous tab |
| `:tabc[lose]` | Close current tab |
| `:tabo[nly]` | Close all other tabs |
| `gt` | Go to next tab (with count: go to tab N) |
| `gT` | Go to previous tab |
| `Ctrl-W T` | Move current window to new tab |

### Spell Checking

Enable with `:set spell`. Uses a built-in ~5000-word English dictionary.
Misspelled words are highlighted with `SpellBad` (red foreground).

| Key | Description |
|---|---|
| `:set spell` | Enable spell checking |
| `:set nospell` | Disable spell checking |
| `]s` | Jump to next misspelled word |
| `[s` | Jump to previous misspelled word |
| `z=` | Show spelling suggestions for word under cursor |
| `zg` | Add word under cursor to good words list |
| `zw` | Mark word under cursor as misspelled |
| `zug` | Undo `zg` (remove from good list) |
| `zuw` | Undo `zw` (remove from bad list) |

### Bracket Commands

| Key | Count | Description |
|---|---|---|
| `[(` | ✅ | Go to previous unmatched `(` |
| `])` | ✅ | Go to next unmatched `)` |
| `[{` | ✅ | Go to previous unmatched `{` |
| `]}` | ✅ | Go to next unmatched `}` |
| `[[` | ✅ | Go to previous `{` in column 0 (section start) |
| `]]` | ✅ | Go to next `{` in column 0 (section start) |
| `[]` | ✅ | Go to previous `}` in column 0 (section end) |
| `][` | ✅ | Go to next `}` in column 0 (section end) |
| `[m` | ✅ | Go to previous `{` (method start) |
| `]m` | ✅ | Go to next `{` (method start) |
| `[M` | ✅ | Go to previous `}` (method end) |
| `]M` | ✅ | Go to next `}` (method end) |
| `[p` | ✅ | Put before with indent adjustment |
| `]p` | ✅ | Put after with indent adjustment |
| `['` | ✅ | Go to previous line with a lowercase mark |
| `]'` | ✅ | Go to next line with a lowercase mark |

### Marks

| Key | Description |
|---|---|
| `m{a-z}` | Set local mark (buffer-scoped) |
| `m{A-Z}` | Set global mark (cross-file) — ❌ not in simulator |
| `'{a-z}` | Jump to mark line (first non-blank) |
| `'{A-Z}` | Jump to global mark line, switching files — ❌ not in simulator |
| `` `{a-z} `` | Jump to exact mark position |
| `` `{A-Z} `` | Jump to exact global mark position, switching files — ❌ not in simulator |
| `` `. `` / `'.` | Jump to last change position |
| ` `` ` `` ` / `''` | Jump to position before last jump |
| `` `< `` / `'<` | Jump to start of last visual selection |
| `` `> `` / `'>` | Jump to end of last visual selection |

Works with operators: `d'a` (linewise), `` d`a `` (charwise), `d'.` (delete to last change), etc.

> **Global marks (`m{A-Z}`)** are one of Vim's best navigation tools for real
> codebases. Mark key classes, functions, and config files with uppercase letters
> (`mA`, `mB`, …) and jump to them from any file with `'A`, `'B`, etc. They
> persist across `:e` file switches and across sessions (saved in ShaDa/viminfo).
> The simulator only supports local marks (`a`–`z`) because it operates on a
> single buffer; practice global marks in real Neovim.

### Jump List

| Key | Description |
|---|---|
| `Ctrl-O` | Jump to older position in jump list |
| `Ctrl-I` / `Tab` | Jump to newer position in jump list |

Jump entries added by: `G`, `gg`, `/`, `?`, `n`, `N`, `*`, `#`, `gd`.

### Change List

| Key | Description |
|---|---|
| `g;` | Go to older position in change list |
| `g,` | Go to newer position in change list |

Change positions recorded on every buffer modification.

### Macros

| Key | Description |
|---|---|
| `q{a-z}` | Start recording into register |
| `q` (while recording) | Stop recording |
| `@{a-z}` | Play macro (supports count) |
| `@@` | Replay last *played* macro (supports count) |
| `@:` | Repeat last ex command (supports count) |
| `Q` | Replay last *recorded* macro (supports count) |

Entire macro is a single undo unit. Aborts on failed motion.
`@@` and `Q` can differ: if you record `qa…q` then play `@b`, then `@@` replays `@b` while `Q` replays `@a`.

### Registers

| Key | Description |
|---|---|
| `"{a-z}` | Select named register for next `d`/`c`/`y`/`p` |
| `"{A-Z}` | Append to named register (uppercase = append) |
| `"{0-9}` | Select numbered register |
| `"+` / `"*` | Clipboard registers |
| `"-` | Small delete register (sub-line deletes) |
| `"_` | Black hole register (discard text) |
| `"/` | Last search pattern register (read-only) |
| `""` | Unnamed register (explicit) |
| `".` | Last inserted text (read-only) |
| `":` | Last ex command (read-only) |
| `"%` | Current filename (read-only) |

All register types work in both normal and visual mode.
`Ctrl-R` in insert mode accepts `a-z`, `0-9`, and `"` (unnamed).

**Numbered register behavior:**
- `"0` always holds the most recent yank.
- `"1`–`"9` form a delete queue: linewise or multiline deletes shift through `"1`→`"2`→…→`"9`.
- Small (single-line charwise) deletes go to `"-` instead of `"1`.

Clipboard registers (`"+`/`"*`) trigger the external clipboard callback when written.

### Search

| Key | Description |
|---|---|
| `/pattern↵` | Search forward (regex) |
| `?pattern↵` | Search backward |
| `n` | Next match (same direction) |
| `N` | Next match (reverse direction) |
| `*` | Search word under cursor forward |
| `#` | Search word under cursor backward |

Wraps around file. Supports operator + search: `d/foo↵` deletes to match.

### Quit / Save

| Key | Description |
|---|---|
| `ZZ` | Write and quit |
| `ZQ` | Quit without saving |

### Normal Mode Ctrl-Key Synonyms

| Key | Equivalent | Description |
|---|---|---|
| `Ctrl-H` | `h` | Move left |

### Redundant & Shortcut Keys

Some normal mode keys are truly redundant (identical to another key) or are shortcut aliases for common two-key combos:

**Truly redundant (interchangeable):**

| Key | Same As | Notes |
|---|---|---|
| `_` | `^` | First non-blank. With count, same as `+`. Prime remap target. |
| `Space` | `l` | Move right. Universally remapped to Leader. |
| `BS`/`Ctrl-H` | `h` | Move left (in normal mode). |
| `+` | `Enter` | Next line, first non-blank. |
| `0` | `|` (no count) | Column 1. But `|` also takes a count (`25|`). |

**Shortcut aliases (single key for a two-key combo):**

| Key | Expands To |
|---|---|
| `s` | `cl` |
| `S` | `cc` |
| `C` | `c$` |
| `D` | `d$` |
| `x` | `dl` |
| `X` | `dh` |
| `ZZ` | `:wq` |
| `ZQ` | `:q!` |

**Neovim-specific changes:**

| Key | Classic Vim | Neovim |
|---|---|---|
| `Y` | `yy` (inconsistent with `D`/`C`) | Remapped to `y$` by default since 0.6 |
| `Q` | Enter Ex mode | Replay last recorded macro (`@@`) |
| `Ctrl-J` | `j` | Move down |
| `Ctrl-M` | `+` | Next line, first non-blank |
| `Ctrl-N` | `j` | Move down |
| `Ctrl-P` | `k` | Move up |
| `Ctrl-L` | ✅ | Redraw screen (no-op in simulator) |
| `Ctrl-C` | ✅ | Cancel / interrupt (returns to normal) |

---

## Insert Mode

| Key | Description |
|---|---|
| `Escape` / `Ctrl-[` | Return to normal (cursor moves left 1) |
| `Enter` / `Ctrl-J` | Split line at cursor |
| `Backspace` / `Ctrl-H` | Delete char before cursor (joins lines) |
| `Delete` | Delete char at cursor (forward delete) |
| `Ctrl-W` | Delete word backward |
| `Ctrl-U` | Delete to start of line |
| `Ctrl-R {reg}` | Paste from register (`a-z`, `0-9`, `"`) |
| `Ctrl-O {cmd}` | Execute one normal-mode command, then return to insert |
| `Ctrl-T` | Indent current line (add one shiftwidth) |
| `Ctrl-D` | Unindent current line (remove one shiftwidth) |
| `Ctrl-E` | Copy character from line below |
| `Ctrl-Y` | Copy character from line above |
| `Ctrl-A` | Re-insert last inserted text |
| `Ctrl-C` | Exit insert mode (like `Escape`, no abbreviation trigger) |
| `←` / `→` | Move cursor left/right |
| `↑` / `↓` | Move cursor up/down |
| Any printable | Insert character |

Count-insert: `3iHa↵` types `Ha` then repeats 2 more times on Escape → `HaHaHa`.

---

## Replace Mode

| Key | Description |
|---|---|
| `Escape` / `Ctrl-[` | Return to normal |
| `Enter` / `Ctrl-J` | Split line |
| `Backspace` / `Ctrl-H` | Restore original character |
| Any printable | Overwrite char at cursor |

Backspace cannot go before the position where `R` was pressed.

---

## Visual Mode

> **Editorial note:** Visual mode is useful for selecting irregular regions that
> are hard to express as a single motion, and it lets beginners *see* what
> they're about to act on. However, if the selection can be described by a
> single motion or text object, the direct **operator + motion** form is almost
> always more efficient. For example, `dw` (delete word) is faster than
> `vwd` (visual-select word, then delete) — same result, one fewer keystroke,
> and it's dot-repeatable. As a rule of thumb: **use visual mode when the
> shape of the selection is complex or exploratory; use operator + motion
> when you know exactly what you want.** Many of our demos use visual mode
> to make the operation visible on screen, but in practice experienced Vim
> users reach for it sparingly. Any book or website generated from this
> content should mention that visual mode is a useful learning tool but
> can become a crutch — the operator + motion grammar is Vim's real power.

### Mode Switching

| Key | Description |
|---|---|
| `v` | Toggle char-visual / exit |
| `V` | Toggle line-visual / exit |
| `Ctrl-V` | Toggle block-visual / exit |
| `gv` | Reselect last visual selection |
| `Escape` | Return to normal |
| `o` / `O` | Swap cursor and selection anchor |

### Motions

All normal-mode motions work in visual mode to extend the selection.

### Actions

| Key | Description |
|---|---|
| `d` / `x` / `Delete` | Delete selection |
| `c` / `s` | Change selection (delete + insert) |
| `y` | Yank selection |
| `>` | Indent selected lines |
| `<` | Dedent selected lines |
| `~` | Toggle case |
| `U` | Uppercase selection |
| `u` | Lowercase selection |
| `J` | Join selected lines |
| `p` | Replace selection with register |
| `r{char}` | Replace every char with {char} |
| `"{a-z}` | Select register for next action |
| `:` | Enter command line with `'<,'>` range pre-filled |
| `g Ctrl-A` | Sequential increment (first number on each selected line: +1, +2, …) |
| `g Ctrl-X` | Sequential decrement |

### Visual Block Mode (`Ctrl-V`)

Block-visual selects a rectangular column region across multiple lines.

| Key | Description |
|---|---|
| `d` / `x` | Delete the block (removes columns from each line) |
| `c` | Change the block (delete + enter insert; typed text replaces on all lines) |
| `I` | Insert before block column (typed text prepended to all lines on Esc) |
| `A` | Append after block column (typed text appended to all lines on Esc) |
| `y` | Yank blockwise |
| `p` | Replace block with register (blockwise paste) |
| `r{char}` | Replace all chars in block with {char} |
| `>` / `<` | Indent / dedent selected lines |
| `$` | Extend selection to end of each line |
| `o` | Toggle active corner (top-left ↔ bottom-right) |
| `O` | Toggle horizontal edge (left ↔ right) |

### Text Objects in Visual

`iw`, `aw`, `ip`, `ap`, `is`, `as`, `i"`, `a"`, `i(`, `a)`, etc. — expand the selection.

---

## Text Objects

Used with operators or in visual mode: `{op}{i|a}{object}`.

| Object | `i` (inner) | `a` (around) |
|---|---|---|
| `w` | Word | Word + surrounding whitespace |
| `W` | WORD | WORD + surrounding whitespace |
| `p` | Paragraph (contiguous non-blank/blank lines, linewise) | Paragraph + adjacent blank lines |
| `s` | Sentence (to ending `.!?`) | Sentence + trailing whitespace |
| `"` | Inside `""` | Including `""` |
| `'` | Inside `''` | Including `''` |
| `` ` `` | Inside `` `` `` | Including `` `` `` |
| `(` / `)` / `b` | Inside `()` | Including `()` |
| `{` / `}` / `B` | Inside `{}` | Including `{}` |
| `[` / `]` | Inside `[]` | Including `[]` |
| `<` / `>` | Inside `<>` | Including `<>` |
| `t` | Inside HTML/XML tag (`<tag>…</tag>`) | Including the tags |

Multi-line pairs supported. Handles escaped quotes. If cursor not inside, searches forward.

---

## Surround (nvim-surround)

Requires nvim-surround plugin. Delete, change, or add surrounding delimiters.

### Delimiter Types

Every surround operation accepts the same set of delimiter characters:

| Char | Pair | Notes |
|---|---|---|
| `)` / `b` | `(`…`)` | Closing — no inner space |
| `(` | `( `…` )` | Opening — adds inner space |
| `]` / `r` | `[`…`]` | Closing — no inner space |
| `[` | `[ `…` ]` | Opening — adds inner space |
| `}` / `B` | `{`…`}` | Closing — no inner space |
| `{` | `{ `…` }` | Opening — adds inner space |
| `>` / `a` | `<`…`>` | Closing — no inner space |
| `<` | `< `…` >` | Opening — adds inner space |
| `"` | `"`…`"` | Double quotes |
| `'` | `'`…`'` | Single quotes |
| `` ` `` | `` ` ``…`` ` `` | Backticks |
| *any other* | *char*…*char* | Symmetric — e.g. `*`, `|`, `_`, `/`, `~` |
| `t` / `<` | `<tag>`…`</tag>` | HTML/XML tag (prompts for tag name) |

**Closing** characters (`)`/`]`/`}`/`>`) produce tight delimiters.
**Opening** characters (`(`/`[`/`{`/`<`) add an inner space on each side.
Aliases: `b` = `)`, `r` = `]`, `B` = `}`, `a` = `>`.

### Delete Surroundings (`ds`)

`ds{target}` — delete the nearest surrounding pair that matches *target*.

| Key | Description |
|---|---|
| `ds"` | Delete surrounding double quotes |
| `ds'` | Delete surrounding single quotes |
| `` ds` `` | Delete surrounding backticks |
| `ds)` / `dsb` | Delete surrounding parentheses |
| `ds(` | Delete surrounding parentheses **and** trim inner whitespace |
| `ds]` / `dsr` | Delete surrounding brackets |
| `ds[` | Delete surrounding brackets **and** trim inner whitespace |
| `ds}` / `dsB` | Delete surrounding braces |
| `ds{` | Delete surrounding braces **and** trim inner whitespace |
| `ds>` / `dsa` | Delete surrounding angle brackets |
| `ds<` | Delete surrounding angle brackets **and** trim inner whitespace |
| `ds*`, `ds|`, `ds/`, … | Delete any symmetric surrounding character |
| `dst` | Delete surrounding HTML/XML tag (`<div>hello</div>` → `hello`) |

When the target is an **opening** bracket (`(`, `[`, `{`, `<`), inner whitespace
adjacent to the delimiters is trimmed. When it's a **closing** bracket or alias,
the content is left untouched.

### Change Surroundings (`cs`)

`cs{target}{replacement}` — find the nearest pair matching *target*, then
replace both delimiters with the *replacement* pair.

| Key | Description |
|---|---|
| `cs"'` | `"hello"` → `'hello'` |
| `cs'"` | `'hello'` → `"hello"` |
| `` cs"` `` | `"hello"` → `` `hello` `` |
| `` cs`" `` | `` `hello` `` → `"hello"` |
| `cs)]` | `(hello)` → `[hello]` |
| `cs])` | `[hello]` → `(hello)` |
| `cs)}` | `(hello)` → `{hello}` |
| `cs}>` | `{hello}` → `<hello>` |
| `cs)"` | `(hello)` → `"hello"` |
| `cs"[` | `"hello"` → `[ hello ]` (opening replacement adds space) |
| `cs)(` | `(hello)` → `( hello )` (opening replacement adds space) |
| `cs({` | `( hello )` → `{hello}` (opening target trims inner space) |
| `cst<span>` | `<div>hello</div>` → `<span>hello</span>` (change tag) |
| `cst"` | `<div>hello</div>` → `"hello"` (tag to quotes) |

**Rules for `cs`:**
- The *target* follows `ds` rules: opening targets (`(`, `[`, `{`, `<`) trim inner whitespace; closing targets leave content intact.
- The *replacement* follows `ys` rules: opening chars add inner space; closing chars don't.
- Both effects compose: `cs({` trims then wraps tight; `cs)(` keeps then adds space.
- Quotes, backticks, and arbitrary characters work as both target and replacement.

### Add Surroundings (`ys`)

`ys{motion}{char}` — surround the text described by *motion* with the
delimiter pair for *char*.

| Key | Description |
|---|---|
| `ysiw)` | `hello` → `(hello)` |
| `ysiw(` | `hello` → `( hello )` |
| `ysiw]` | `hello` → `[hello]` |
| `ysiw[` | `hello` → `[ hello ]` |
| `ysiw}` | `hello` → `{hello}` |
| `ysiw{` | `hello` → `{ hello }` |
| `ysiw>` | `hello` → `<hello>` |
| `ysiw<` | `hello` → `< hello >` |
| `ysiw"` | `hello` → `"hello"` |
| `ysiw'` | `hello` → `'hello'` |
| `` ysiw` `` | `hello` → `` `hello` `` |
| `ysiw*` | `hello` → `*hello*` |
| `ysiw|` | `hello` → `\|hello\|` |
| `ysaw)` | Surround a-word (includes trailing whitespace in selection) |
| `ysaW}` | Surround a-WORD |
| `ysiW)` | Surround inner WORD |
| `ys$"` | Surround from cursor to end of line |
| `ysw)` | Surround from cursor to next word start |
| `yse]` | Surround from cursor to end of word |
| `ysf.)` | Surround from cursor up to and including next `.` |
| `yst.)` | Surround from cursor up to (not including) next `.` |
| `ysF.)` | Surround backward up to and including previous `.` |
| `ys2w"` | Surround next 2 words |
| `yss)` | Surround entire line (leading/trailing whitespace preserved inside) |
| `yss(` | Surround entire line with inner space |
| `yss"` | Surround entire line in double quotes |
| `ysiw<div>` | `hello` → `<div>hello</div>` (tag surround) |
| `ysiwt` + `div>` | Same as above (tag prompt) |

Any motion (`w`, `e`, `b`, `$`, `0`, `^`, `f`, `F`, `t`, `T`, counted motions)
and any text object (`iw`, `aw`, `iW`, `aW`, `i)`, `a]`, etc.) can be
used with `ys`.

### Visual Surround (`S`)

Select text in Visual mode, then press `S{char}` to surround it.

| Key | Description |
|---|---|
| `viw` → `S)` | `hello` → `(hello)` |
| `viw` → `S"` | `hello` → `"hello"` |
| `viw` → `S'` | `hello` → `'hello'` |
| `viw` → `` S` `` | `hello` → `` `hello` `` |
| `viw` → `S]` | `hello` → `[hello]` |
| `viw` → `S}` | `hello` → `{hello}` |
| `viw` → `S>` | `hello` → `<hello>` |
| `viw` → `S*` | `hello` → `*hello*` |
| `viw` → `S(` | `hello` → `( hello )` (opening adds space) |
| `V` → `S)` | Linewise — content placed on its own indented line |
| `V` → `S]` | Linewise — works with any delimiter type |

All surround operations support dot-repeat (`.`), undo (`u`), and redo (`Ctrl-R`).

---

## Command Mode (Ex Commands)

All Ex commands accept standard nvim abbreviations — any unambiguous prefix
of the full command name is valid (e.g. `:wri` → `:write`, `:qui` → `:quit`).

### Command-Line Editing

| Key | Description |
|---|---|
| `Backspace` / `Ctrl-H` | Delete character before cursor |
| `Ctrl-U` | Delete to start of command (after the `:`) |
| `Ctrl-W` | Delete word backward (word-class aware) |
| `Ctrl-R {reg}` | Insert register contents into command line (`"`, `a`–`z`, `/`, `:`, `%`) |
| `Up` / `Down` | Browse command/search history |
| `Tab` | Tab-complete commands, `:set` options, and filenames |
| `Ctrl-D` | Show all possible completions |
| `Escape` | Cancel command |
| `Enter` | Execute command |

### File / Quit / Navigation

| Command | Description |
|---|---|
| `:w[rite] [file]` | Save to VFS (shows `"file" NL, NB written`); if buffer has no filename, uses the given name and sets it as current |
| `:wq [file]` | Save and quit (always writes; shows E32 if no filename available) |
| `:x[it]` | Save (only if dirty) and quit (shows E32 if no filename available) |
| `:q[uit]` | Quit (fails with E37 if dirty) |
| `:q[uit]!` | Force quit (discard changes) |
| `:qa[!]` | Quit all windows (with `!` discards changes) |
| `:wa[!]` | Write all buffers |
| `:wqa` / `:xa` | Write all and quit |
| `:e[dit] [file]` | Edit file; with no arg, reloads current file from VFS (shows E32 if no filename set) |
| `:e[dit]! [file]` | Force re-edit (discard changes); also accepts a filename |
| `:sav[eas] file` | Save buffer to new file, set it as current filename, update highlighting |
| `:new` | Open a new empty buffer in a horizontal split |
| `:ene[w][!]` | Edit a new unnamed buffer (clears current buffer) |
| `:{number}` | Go to line number |
| `:$` | Go to last line |
| `:noh[lsearch]` | Clear search highlighting (pattern kept for `n`/`N`) |
| `:se[t] …` | Set options (see below) |
| `:r[ead] file` | Read file contents below cursor (shows "N line(s) added"; sets filename if none; shows E484 if file not found) |
| `:r[ead]! command` | Read shell command output below cursor (shows "N line(s) added") |
| `:[range]sort[!] [flags]` | Sort lines (`!` = reverse; flags: `n` numeric, `i` ignore-case, `u` unique) |
| `:[range]ret[ab][!] [N]` | Convert tabs↔spaces; with `expandtab` or `!`, converts tabs to N spaces |
| `:!command` | Run shell command (see below) |
| `:pwd` | Display current directory |
| `:f[ile]` | Show file info (name, modified status, line count) |
| `:delm[arks] {marks}` | Delete specified marks |
| `:delm[arks]!` | Delete all lowercase marks |
| `:undol[ist]` | Show number of undo entries |

### Editing Commands

| Command | Description |
|---|---|
| `:[range]d[elete] [reg]` | Delete lines in range; saves to register (linewise) |
| `:[range]y[ank] [reg]` | Yank lines in range to register (no buffer modification) |
| `:[range]m[ove] {addr}` | Move lines in range to after {addr} |
| `:[range]co[py] {addr}` | Copy lines in range to after {addr} |
| `:[range]t {addr}` | Alias for `:copy` |
| `:[range]j[oin][!]` | Join lines in range (with spaces; `!` = no spaces) |
| `:[range]norm[al][!] {keys}` | Execute normal-mode keys on each line in range |
| `:[range]g[lobal]/{pat}/{cmd}` | Execute {cmd} on lines matching {pat} |
| `:[range]v[global]/{pat}/{cmd}` | Execute {cmd} on lines NOT matching {pat} |
| `:[range]s[ubstitute]/{pat}/{rep}/[flags]` | Substitute (see below) |
| `:s` | Repeat last substitution on current line |
| `:[range]pu[t][!] [reg]` | Put register content as lines (below; `!` = above) |
| `:[range]>` | Shift lines right (indent) by `shiftwidth` |
| `:[range]<` | Shift lines left (unindent) by `shiftwidth` |
| `:[range]p[rint]` | Display lines |
| `:[range]nu[mber]` | Display lines with line numbers |
| `:[range]#` | Same as `:number` |
| `:=` | Print total number of lines (or line number with range) |
| `:marks` | Display marks list (message prompt) |
| `:reg[isters]` | Display register contents (message prompt) |
| `:di[splay]` | Alias for `:registers` |
| `:ju[mps]` | Display jump list (message prompt) |
| `:changes` | Display change list (message prompt) |

All editing commands are undoable with `u` and support visual-mode ranges via `:'<,'>`.

Unknown commands show `E492: Not an editor command: {cmd}`.

### Range Addressing

Ranges prefix editing commands to specify which lines to operate on.
If no range is given, most commands default to the current line.

| Address | Meaning |
|---|---|
| `N` | Line N (1-based) |
| `.` | Current line |
| `$` | Last line |
| `%` | Entire file (shorthand for `1,$`) |
| `'<,'>` | Visual selection (auto-filled when `:` pressed in visual mode) |
| `'{a-z}` | Line of mark |
| `.+N` | Current line + N |
| `.-N` | Current line − N |
| `$-N` | Last line − N |
| `N+M` | Line N + M |

Ranges are formed by combining two addresses with a comma:
`:2,4d` (delete lines 2–4), `:.,$d` (delete from cursor to end),
`:1,3m$` (move lines 1–3 to end), `:%y` (yank all lines).

Offsets can be chained: `:2+2` means line 4, `:$-2,$` means last 3 lines.

### `:d[elete]` — Delete Lines

`:[range]d[elete] [register]`

Deletes the specified lines and stores them in a register (linewise).

| Example | Description |
|---|---|
| `:d` | Delete current line |
| `:3d` | Delete line 3 |
| `:2,4d` | Delete lines 2 through 4 |
| `:%d` | Delete all lines |
| `:.,$d` | Delete from cursor line to end |
| `:.,+2d` | Delete current line and next 2 |
| `:d a` | Delete current line into register `a` |
| `:2,4d a` | Delete lines 2–4 into register `a` |

The deleted text goes to the unnamed register (and numbered registers shift)
unless a named register is specified. If all lines are deleted, the buffer
becomes a single empty line. Cursor moves to the first non-blank character
of the line at the deletion point (or the new last line if deleted past end).

### `:y[ank]` — Yank Lines

`:[range]y[ank] [register]`

Copies the specified lines into a register without modifying the buffer.

| Example | Description |
|---|---|
| `:y` | Yank current line |
| `:3y` | Yank line 3 |
| `:2,4y` | Yank lines 2 through 4 |
| `:%y` | Yank all lines |
| `:$y` | Yank last line |
| `:2y a` | Yank line 2 into register `a` |
| `:1,3y b` | Yank lines 1–3 into register `b` |

Cursor moves to the first line of the range. Yanked text is linewise and
can be pasted with `p`/`P` or `:pu`. If a named register is specified,
the text is stored there; otherwise it goes to the unnamed and `"0` registers.

### `:m[ove]` — Move Lines

`:[range]m[ove] {address}`

Removes lines from the range and inserts them after {address}.

| Example | Description |
|---|---|
| `:m3` | Move current line to after line 3 |
| `:m$` | Move current line to end of file |
| `:m0` | Move current line to top of file |
| `:3m$` | Move line 3 to end |
| `:5m0` | Move line 5 to top |
| `:1m3` | Move line 1 to after line 3 |
| `:2,3m$` | Move lines 2–3 to end |
| `:4,5m0` | Move lines 4–5 to top |
| `:.m$` | Move current line to end |

Address `0` means "before line 1" (top of file). Cursor lands on the last
moved line at the first non-blank character. Moving a line to its own position
is a no-op (line stays, cursor moves to it).

### `:co[py]` / `:t` — Copy Lines

`:[range]co[py] {address}` or `:[range]t {address}`

Copies lines from the range and inserts the copy after {address}.
`:t` is a short alias for `:copy`.

| Example | Description |
|---|---|
| `:co$` | Copy current line to end |
| `:co0` | Copy current line to top |
| `:co3` | Copy current line to after line 3 |
| `:t$` | Same as `:co$` |
| `:t0` | Same as `:co0` |
| `:3co$` | Copy line 3 to end |
| `:1t4` | Copy line 1 to after line 4 |
| `:2,4co$` | Copy lines 2–4 to end |
| `:1,3t0` | Copy lines 1–3 to top |
| `:%t$` | Duplicate entire file (append below) |
| `:.t$` | Copy current line to end |
| `:2t2` | Duplicate line 2 (insert copy after it) |

Cursor lands on the last copied line at the first non-blank character.

### `:j[oin]` — Join Lines

`:[range]j[oin][!]`

Joins lines in the range into a single line. Without `!`, a space is added
between joined lines (matching `J` in normal mode). With `!`, lines are
concatenated directly (matching `gJ`).

| Example | Description |
|---|---|
| `:j` | Join current line with next |
| `:join` | Same as `:j` |
| `:1,3j` | Join lines 1 through 3 |
| `:2,5j` | Join lines 2 through 5 |
| `:%j` | Join all lines into one |
| `:j!` | Join current + next without spaces |
| `:1,3j!` | Join lines 1–3 without spaces |
| `:%j!` | Join all lines without spaces |

Without a range, `:j` joins the current line with the line below it.
With a single-line range (e.g. `:3j`), it joins that line with the next.
Cursor moves to the first line of the joined range.

### `:norm[al]` — Execute Normal-Mode Keys

`:[range]norm[al][!] {keys}`

Executes the given normal-mode key sequence on each line in the range.
The cursor is placed at column 0 of each line before executing the keys.

| Example | Description |
|---|---|
| `:%norm Aend` | Append "end" to every line |
| `:%norm dw` | Delete first word on every line |
| `:2,4norm Aend` | Append "end" to lines 2–4 |
| `:%norm I>> ` | Prepend ">> " to every line |
| `:2,4norm dd` | Delete lines 2–4 (one `dd` per line) |
| `:%norm x` | Delete first character of every line |

If the key sequence enters insert mode, `Escape` is automatically sent
after the keys to return to normal mode. The entire `:norm` operation is
a single undo unit.

### `:g[lobal]` — Execute on Matching Lines

`:[range]g[lobal]/{pattern}/{command}`

Executes {command} on every line matching {pattern}.

| Example | Description |
|---|---|
| `:g/foo/d` | Delete all lines containing "foo" |
| `:g/hello/d` | Delete all lines containing "hello" |
| `:g/aaa/d` | Delete all lines matching "aaa" |
| `:g/foo/norm A!` | Append "!" to lines matching "foo" |
| `:1,3g/foo/d` | Delete matching lines only in range 1–3 |

Supported sub-commands: `d[elete]`, `norm[al] {keys}`.
The search pattern is set for `/`/`?`/`n`/`N` highlighting.
Deletions are processed from bottom to top to preserve line indices.
The entire `:g` operation is a single undo unit.

### `:v[global]` — Execute on Non-Matching Lines

`:[range]v[global]/{pattern}/{command}`

Inverted form of `:g` — executes {command} on lines NOT matching {pattern}.

| Example | Description |
|---|---|
| `:v/foo/d` | Delete all lines NOT containing "foo" (keep only "foo" lines) |
| `:v/hello/d` | Keep only lines containing "hello" |

Same sub-commands as `:g`. Same undo behavior.

### `:s[ubstitute]` — Search and Replace

`:[range]s[ubstitute]/{pattern}/{replacement}/[flags]`

Performs regex substitution on lines in the range.

| Flag | Description |
|---|---|
| `g` | Replace all occurrences on each line (not just first) |
| `i` | Case-insensitive matching |
| `c` | Confirm each replacement (currently applies all) |
| `n` | Count matches only — do not replace (reports count) |

| Example | Description |
|---|---|
| `:s/foo/bar` | Replace first "foo" with "bar" on current line |
| `:s/foo/bar/g` | Replace all "foo" with "bar" on current line |
| `:%s/foo/bar/g` | Replace all "foo" with "bar" in entire file |
| `:2,4s/old/new` | Replace on lines 2–4 |
| `:.,+2s/a/b/g` | Replace from cursor line through 2 lines below |
| `:.,$s/a/b/g` | Replace from cursor to end of file |
| `:%s/word//g` | Delete all occurrences of "word" |
| `:%s/Line/[&]/g` | Wrap matches with brackets (`&` = matched text) |
| `:s` | Repeat last substitution on current line |
| `:%s/foo//gn` | Count "foo" occurrences without replacing |

Any single character can serve as the delimiter (not just `/`): `:s!old!new!g`,
`:s#old#new#g`, etc. Escaped delimiters (`\/`) are handled correctly.

The `&` character in the replacement refers to the matched text (like `\0`).
Use `\&` for a literal ampersand. Backreferences `\1` through `\9` refer to
captured groups from `\(…\)` in the pattern.

**Vim regex syntax:** Patterns use Vim's "magic" mode, which is automatically
translated to JavaScript regex. Key mappings:

| Vim | JS | Meaning |
|---|---|---|
| `\+` | `+` | One or more |
| `\?` | `?` | Zero or one |
| `\(…\)` | `(…)` | Capture group |
| `\|` | `\|` | Alternation |
| `\{…\}` | `{…}` | Quantifier |
| `\<`, `\>` | `\b` | Word boundary |

This translation applies to `/` and `?` search, `:s`, `:g`, `&`, and `g&`.

The search pattern is set for `n`/`N`/highlighting after substitution.
A bare `:s` with no arguments repeats the last substitution on the current line.

### `:pu[t]` — Put Register Content

`:[line]pu[t][!] [register]`

Inserts register content as new lines below the current line (or above with `!`).

| Example | Description |
|---|---|
| `:pu` | Put unnamed register below current line |
| `:pu!` | Put unnamed register above current line |
| `:3pu` | Put unnamed register below line 3 |
| `:pu a` | Put register `a` below current line |

If a line number precedes the command, the put happens relative to that line
rather than the cursor position.

### `:[range]>` — Shift Right (Indent)

`:[range]>`

Shifts lines in the range right by one `shiftwidth` (default 8). Adds leading spaces to each line.

| Example | Description |
|---|---|
| `:>` | Indent current line |
| `:3>` | Indent line 3 |
| `:2,4>` | Indent lines 2 through 4 |
| `:%>` | Indent all lines |
| `:>>` | Indent current line twice (4 spaces) |
| `:'<,'>>` | Indent visual selection |

Multiple `>` characters repeat the shift: `:>>` shifts twice, `:>>>` shifts
three times. Cursor moves to the last line of the range, at the first non-blank
character. The shift is undoable with `u`.

### `:[range]<` — Shift Left (Unindent)

`:[range]<`

Shifts lines in the range left by one `shiftwidth` (default 8). Removes up to one `shiftwidth` of leading spaces from each line.

| Example | Description |
|---|---|
| `:<` | Unindent current line |
| `:2<` | Unindent line 2 |
| `:2,4<` | Unindent lines 2 through 4 |
| `:%<` | Unindent all lines |
| `:<<` | Unindent current line twice (4 spaces) |
| `:'<,'><` | Unindent visual selection |

Multiple `<` characters repeat the shift: `:<<` shifts twice, `:<<<` shifts
three times. Lines with insufficient leading whitespace lose only the whitespace
they have. Cursor moves to the last line of the range, at the first non-blank
character. The shift is undoable with `u`.

### `:[range]p[rint]` — Display Lines

`:[range]p[rint]`

Displays the contents of the specified lines.

| Example | Description |
|---|---|
| `:p` | Display current line |
| `:3p` | Display line 3 |
| `:1,3p` | Display lines 1 through 3 |
| `:%p` | Display all lines |
| `:print` | Full form of `:p` |

With a single-line range, the line is shown in the command line area. With
multiple lines, a message prompt overlay is shown with the line contents.
Cursor moves to the last line of the range at the first non-blank character.

### `:[range]nu[mber]` / `:[range]#` — Display Lines with Numbers

`:[range]nu[mber]` or `:[range]#`

Same as `:print` but prefixes each line with its line number.

| Example | Description |
|---|---|
| `:nu` | Display current line with number |
| `:3nu` | Display line 3 with number |
| `:1,3nu` | Display lines 1–3 with numbers |
| `:%nu` | Display all lines with numbers |
| `:number` | Full form of `:nu` |
| `:#` | Same as `:nu` |
| `:1,3#` | Same as `:1,3nu` |

Line numbers are right-aligned in a column with minimum width 3, expanding
for files with more than 999 lines. The number column is displayed in
`LineNr` color (dark grey in nvim_default theme).

### `:=` — Print Line Number

`:=` or `:[range]=`

Without a range, prints the total number of lines in the buffer. With a range,
prints the line number of the last line in the range.

| Example | Description |
|---|---|
| `:=` | Print total number of lines |
| `:.=` | Print current line number |
| `:$=` | Print last line number (same as total) |
| `:3=` | Print `3` |

The result is displayed in the command line area.

### `:marks` — Display Marks

`:marks`

Shows a message prompt listing all set marks with their line number, column,
and the text of the line they point to. Includes:
- `'` — position before last jump (defaults to line 1, col 0)
- User marks `a`–`z` (sorted alphabetically)
- `"` — last position when exiting file
- `[` — start of buffer (always line 1, col 0)
- `]` — end of buffer (last line, col 0)

Format:
```
mark line  col file/text
 '      1    0 first line of file
 a      3    5 third line content
 "      1    0 first line of file
 [      1    0 first line of file
 ]      7    0 last line of file
```

Press `Enter` to dismiss the prompt.

### `:reg[isters]` — Display Registers

`:reg[isters]`

Shows a message prompt listing all non-empty registers with their type and content.
Displays in order: unnamed (`""`), numbered (`"0`–`"9`), small delete (`"-`),
named (`"a`–`"z`), and last search (`"/`).

Format:
```
Type Name Content
  l  ""   line content^J
  c  "0   yanked text
  c  "-   small delete
  c  "a   some text
  c  "/   search pattern
```

Type is `l` (linewise) or `c` (charwise). Newlines are displayed as `^J`.
Press `Enter` to dismiss the prompt.

### `:di[splay]` — Display Registers (Alias)

`:di[splay]`

Alias for `:reg[isters]`. Shows the same register listing.

### `:ju[mps]` — Display Jump List

`:ju[mps]`

Shows a message prompt listing the jump list entries.

Format:
```
 jump line  col file/text
   3     1    0 first line
   2     5    3 fifth line
   1    10    0 tenth line
>  0    15    4 current position
```

The `>` marker indicates the current position in the jump list.
Jump numbers count backwards: the most recent jump is 1, the one before is 2, etc.
Press `Enter` to dismiss the prompt.

### `:changes` — Display Change List

`:changes`

Shows a message prompt listing the change list entries.

Format:
```
change line  col text
    3     1    0 first change
    2     5    3 second change
    1    10    0 third change
>   0    15    4 current position
```

The `>` marker indicates the current position in the change list.
Change numbers count backwards: the most recent change is 1, the one before is 2, etc.
Press `Enter` to dismiss the prompt.

### `:wq` vs `:x`

`:wq` always writes the file, even if the buffer is clean. `:x` only writes if
the buffer has been modified (dirty). Both quit after writing.

### `:set` Options

#### Boolean Options

| Option | Short | `no`-prefix | Default | Description |
|---|---|---|---|---|
| `number` | `nu` | `nonumber` / `nonu` | off | Show absolute line numbers in a left gutter |
| `relativenumber` | `rnu` | `norelativenumber` / `nornu` | off | Show relative line distances in the gutter |
| `ignorecase` | `ic` | `noignorecase` / `noic` | off | Case-insensitive search |
| `smartcase` | `scs` | `nosmartcase` / `noscs` | off | Override `ignorecase` when pattern has uppercase |
| `expandtab` | `et` | `noexpandtab` / `noet` | off | Insert spaces instead of tab characters |
| `autoindent` | `ai` | `noautoindent` / `noai` | **on** | Copy indent from current line on `Enter`/`o`/`O` |
| `cursorline` | `cul` | `nocursorline` / `nocul` | off | Highlight the screen line of the cursor |
| `hlsearch` | `hls` | `nohlsearch` / `nohls` | on | Highlight all search matches |
| `wrap` | | `nowrap` | **on** | Wrap long lines (off enables horizontal scroll) |
| `incsearch` | `is` | `noincsearch` / `nois` | off | Show incremental search matches while typing |
| `list` | | `nolist` | off | Show whitespace characters (tabs, trailing spaces) |
| `splitbelow` | `sb` | `nosplitbelow` / `nosb` | off | New horizontal splits open below current window |
| `splitright` | `spr` | `nosplitright` / `nospr` | off | New vertical splits open to the right |
| `spell` | | `nospell` | off | Enable spell checking (highlights misspelled words) |

#### Numeric Options

| Option | Short | Default | Description |
|---|---|---|---|
| `tabstop` | `ts` | 8 | Number of spaces a tab character displays as |
| `shiftwidth` | `sw` | 8 | Spaces per indent level (`>>`, `<<`, `:>`, `:<`) |
| `scrolloff` | `so` | 0 | Minimum lines to keep above/below cursor |

#### String Options

| Option | Short | Default | Values | Description |
|---|---|---|---|---|
| `fileformat` | `ff` | `dos` | `dos`, `unix` | Line ending format (affects byte count in `Ctrl-G`) |

Numeric options use `=` syntax: `:set ts=4`, `:set sw=2`, `:set so=5`.
All short aliases work everywhere: `:set nu`, `:set noic`, `:set sw=2`.

When both `number` and `relativenumber` are set, the cursor line shows the
absolute number (left-aligned) and all other lines show relative distances.
When only `relativenumber` is set, the cursor line shows `0`.
Gutter width defaults to 4 columns (matching nvim `numberwidth=4`), expanding
for files with more than 999 lines.

### Dirty Detection

`:q` uses undo-position tracking, not content comparison. Undoing all changes = clean. Manually reverting content ≠ clean (matches real nvim).

### `:!` Shell Commands

| Command | Description |
|---|---|
| `:!ls` | List files in VFS |
| `:!cat file` | Print file contents |
| `:!echo text` | Print text |
| `:!rm file` | Remove file from VFS |
| `:!touch file` | Create empty file |
| `:!cp src dst` | Copy file |
| `:!mv src dst` | Move/rename file |
| `:!wc file` | Count lines, words, bytes (`-l` `-w` `-c`) |
| `:!grep pat file` | Search for pattern (`-i` `-n` `-c`) |
| `:!sort file` | Sort lines (`-r` `-n` `-u`) |
| `:!date` | Print date and time |
| `:!history` | Show shell command history |
| `:!anything_else` | Shows "command not found" |

Output shown in a "Press ENTER or type command to continue" prompt.
Dismissal keys: `Enter` or `Escape` (return to normal mode), or `:` (dismiss
and enter command mode). All other keys are ignored.

### Key Mappings

The simulator supports Vim key mappings — both via ex commands and `init.lua`.

#### Ex Commands

| Command | Description |
|---|---|
| `:map {lhs} {rhs}` | Map `{lhs}` → `{rhs}` in normal, visual, operator-pending (recursive) |
| `:nmap {lhs} {rhs}` | Map in normal mode (recursive) |
| `:imap {lhs} {rhs}` | Map in insert mode (recursive) |
| `:vmap {lhs} {rhs}` | Map in visual mode (recursive) |
| `:xmap {lhs} {rhs}` | Map in visual-only mode (recursive) |
| `:noremap {lhs} {rhs}` | Map in normal+visual+op (non-recursive) |
| `:nnoremap {lhs} {rhs}` | Map in normal mode (non-recursive) |
| `:inoremap {lhs} {rhs}` | Map in insert mode (non-recursive) |
| `:vnoremap {lhs} {rhs}` | Map in visual mode (non-recursive) |
| `:unmap {lhs}` | Remove mapping from normal+visual+op |
| `:nunmap {lhs}` | Remove normal mode mapping |
| `:iunmap {lhs}` | Remove insert mode mapping |
| `:mapclear` | Remove all mappings |
| `:nmapclear` | Remove all normal mode mappings |
| `:map` | List all mappings |
| `:nmap` | List normal mode mappings |
| `:let mapleader = ' '` | Set the leader key |

**Recursive vs non-recursive:** `:nmap` mappings allow the `{rhs}` to trigger
other mappings. `:nnoremap` mappings execute `{rhs}` literally, bypassing
further mapping resolution. Always prefer `noremap` unless you specifically
need chaining.

#### Key Notation

Key sequences in `{lhs}` and `{rhs}` support Vim-style angle-bracket notation:

| Notation | Key |
|---|---|
| `<CR>` / `<Enter>` | Enter |
| `<Esc>` / `<Escape>` | Escape |
| `<Space>` | Space |
| `<BS>` / `<Backspace>` | Backspace |
| `<Tab>` | Tab |
| `<Del>` / `<Delete>` | Delete |
| `<Up>` `<Down>` `<Left>` `<Right>` | Arrow keys |
| `<C-x>` | Ctrl + x (e.g. `<C-w>` = Ctrl-W) |
| `<Leader>` | Expands to the `mapleader` value (default `\`) |
| `<lt>` | Literal `<` |
| `<Bar>` | Literal `\|` |
| `<Bslash>` | Literal `\` |

#### init.lua Config File

If an `init.lua` file exists in the virtual filesystem, it is loaded
automatically when vim starts. The simulator parses a subset of Neovim Lua:

```lua
-- Set leader key
vim.g.mapleader = " "

-- Key mappings (noremap by default, like real Neovim)
vim.keymap.set("n", "Y", "y$")
vim.keymap.set("n", "<Leader>w", ":w<CR>")
vim.keymap.set("i", "jk", "<Esc>")
vim.keymap.set({"n", "v"}, "<Leader>y", '"+y')

-- Use { remap = true } for recursive mappings
vim.keymap.set("n", "X", "x", { remap = true })

-- Settings (proxied to :set)
vim.opt.number = true
vim.opt.relativenumber = true
vim.o.scrolloff = 8
vim.o.shiftwidth = 2

-- Execute ex commands directly
vim.cmd("set wrap")
vim.cmd("nnoremap Q @@")
```

**Supported `init.lua` constructs:**
- `vim.g.mapleader = "x"` — set leader key
- `vim.keymap.set(mode, lhs, rhs [, opts])` — key mapping (noremap by default)
- `vim.opt.X = value` / `vim.o.X = value` — proxy to `:set`
- `vim.cmd("...")` — execute an ex command
- `-- comments` — ignored
- Lines not matching any pattern are silently ignored

### Command-Line Keys

| Key | Description |
|---|---|
| `Escape` | Cancel |
| `Enter` | Execute |
| `Backspace` | Delete char (or cancel if empty) |
| `Ctrl-U` | Delete to start of command (after the `:`) |
| `Ctrl-W` | Delete word backward |
| `Ctrl-R {reg}` | Insert register contents (`"`, `a`–`z`, `/`, `:`, `%`) |
| `Up` / `Down` | Browse command/search history |
| `Tab` | Tab-complete: commands, `:set` options, filenames; cycles through matches |
| `Ctrl-D` | Show all possible completions (wildmenu-style list) |
| Any printable | Append to command |

Tab completion works for:
- **Commands**: on the first word (`:ta` → `:tabclose`, `:tabedit`, …)
- **`:set` options**: after `:set ` (`:set sp` → `:set spell`, `:set splitbelow`, …)
- **Filenames**: for `:e`, `:w`, `:r`, `:sav` (cycles through VFS matches)

Repeated `Tab` cycles through matches (`wildmode=full` behavior). `Ctrl-D`
lists all matches below the command line. The cycle resets on `Escape` or `Enter`.

### Message Truncation

When the `"file" NL, NB written` message exceeds screen width, it is truncated
with a leading `<` prefix (matching nvim behavior).

---

## Shell

### Commands

| Command | Description |
|---|---|
| `vim [file]` / `vi [file]` / `nvim [file]` | Open file in vim |
| `ls` | List files |
| `cat file…` | Print file contents |
| `touch file…` | Create empty file(s) |
| `rm file…` | Delete file(s) |
| `cp src dst` | Copy file |
| `mv src dst` | Move/rename file |
| `echo text` | Print text (`> file` overwrite, `>> file` append) |
| `wc file…` | Count lines, words, bytes (`-l` lines, `-w` words, `-c` bytes) |
| `grep pat file…` | Search for regex pattern (`-i` case-insensitive, `-n` line numbers, `-c` count only) |
| `sort file` | Sort lines of a file (`-r` reverse, `-n` numeric, `-u` unique) |
| `history` | Show numbered command history |
| `tmux` | Launch tmux (errors if already inside tmux) |
| `set -o vi` | Enable vi-mode line editing |
| `set -o emacs` | Disable vi-mode (default) |
| `set` | Show current editing mode |
| `date` | Print current date and time |
| `clear` | Clear screen |
| `exit` | Exit shell (stops accepting input) |
| `help` | Show command list |
| *anything else* | "command not found" |

### Keys (Emacs mode — default)

| Key | Description |
|---|---|
| `Enter` | Execute command |
| `Backspace` | Delete char before cursor |
| `Delete` | Delete char at cursor (forward delete) |
| `←` / `→` | Move cursor |
| `↑` / `↓` | Command history navigation |
| `Home` / `Ctrl-A` | Cursor to start |
| `End` / `Ctrl-E` | Cursor to end |
| `Ctrl-C` | Cancel current input |
| `Ctrl-D` | On empty line: exit shell; otherwise: delete char at cursor |
| `Ctrl-L` | Clear screen |
| `Ctrl-U` | Delete to start of line |
| `Ctrl-K` | Delete to end of line |
| `Ctrl-W` | Delete word backward |
| `Tab` | Tab completion (commands on first word, filenames otherwise) |

### Prompt

```
➜  vimfu ▍
```

ZSH oh-my-zsh robbyrussell theme — green arrow, cyan dirname.

### Vi-Mode Line Editing (`set -o vi`)

Enables vim-style editing for the shell input line, matching the behavior
of bash/zsh `set -o vi`. The shell starts in **insert mode** after enabling;
press `Escape` to enter **normal mode**.

Cursor shape changes: **beam** (thin bar) in insert mode, **block** in normal
and replace modes.

#### Normal Mode — Motions

| Key | Count | Description |
|---|---|---|
| `h` / `←` | ✅ | Left |
| `l` / `→` / `Space` | ✅ | Right |
| `w` | ✅ | Word forward |
| `W` | ✅ | WORD forward (whitespace-delimited) |
| `b` | ✅ | Word backward |
| `B` | ✅ | WORD backward |
| `e` | ✅ | End of word forward (inclusive) |
| `E` | ✅ | End of WORD forward |
| `0` / `Home` | ✅ | Start of line |
| `$` / `End` | ✅ | End of line (inclusive) |
| `^` / `_` | ✅ | First non-whitespace character |
| `f{char}` | ✅ | Find char forward (inclusive) |
| `F{char}` | ✅ | Find char backward (inclusive) |
| `t{char}` | ✅ | Till char forward (exclusive — stops one before) |
| `T{char}` | ✅ | Till char backward (exclusive — stops one after) |
| `;` | ✅ | Repeat last `f`/`F`/`t`/`T` |
| `,` | ✅ | Repeat last find, reversed direction |

#### Normal Mode — Operators

Operators combine with motions: `{op}[count]{motion}`.

| Key | Line form | Description |
|---|---|---|
| `d` | `dd` | Delete |
| `c` | `cc` | Change (delete + enter insert) |
| `y` | `yy` | Yank (copy) |

Examples: `dw`, `d2w`, `cw` (acts like `ce`), `yy`, `df{c}`, `dt{c}`,
`cf{c}`, `ct{c}`, `yf{c}`.

Special: `cw` on a word behaves like `ce` (doesn't include trailing space),
matching vim behavior.

#### Normal Mode — Editing

| Key | Count | Description |
|---|---|---|
| `x` | ✅ | Delete char under cursor |
| `X` | ✅ | Delete char before cursor |
| `s` | ✅ | Substitute N chars (delete + insert mode) |
| `S` | ✅ | Substitute entire line |
| `r{char}` | ✅ | Replace N chars with {char} |
| `R` | ✅ | Enter replace (overtype) mode |
| `~` | ✅ | Toggle case, advance cursor |
| `D` | ✅ | Delete to end of line |
| `C` | ✅ | Change to end of line |
| `p` | ✅ | Put yanked text after cursor (N times) |
| `P` | ✅ | Put yanked text before cursor (N times) |
| `u` | ✅ | Undo last change |
| `.` | ✅ | Repeat last change (dot-repeat) |
| `#` | ✅ | Comment out line (prepend `#`) and execute |

#### Normal Mode — Mode Switching

| Key | Description |
|---|---|
| `i` | Insert before cursor |
| `I` | Insert at start of line |
| `a` | Append after cursor |
| `A` | Append at end of line |
| `R` | Enter replace (overtype) mode |

#### Normal Mode — History

| Key | Description |
|---|---|
| `k` / `↑` | Previous history entry |
| `j` / `↓` | Next history entry |
| `G` | Jump to oldest history entry (or entry N with count) |
| `/pattern↵` | Search history backward for pattern (regex) |
| `?pattern↵` | Search history backward for pattern |
| `n` | Repeat last history search |
| `N` | Repeat last history search (opposite direction) |

#### Normal Mode — Numeric Counts

Prefix most commands with digits 1–9 to repeat: `3w`, `2dw`, `5x`,
`3rX`, `2p`, `3~`, `3l`, etc.

#### Insert Mode (vi)

Same as emacs-mode editing (typing inserts characters), plus:
- `Escape` returns to normal mode (cursor moves left by 1)
- All standard emacs keys (`Ctrl-A`, `Ctrl-E`, etc.) still work

#### Replace Mode (vi)

Entered with `R` from normal mode:
- Typing overtypes existing characters (does not insert)
- `Backspace` restores the original character
- Cannot backspace before the position where `R` was pressed
- `Escape` returns to normal mode
- Cursor displays as block

---

## Tmux

The simulator includes a full tmux terminal multiplexer with sessions, windows,
panes, and the standard prefix-key interface.

### Prefix Key

All tmux commands are triggered by pressing `Ctrl-B` (the prefix key) followed
by a command key. Pressing `Escape` in prefix mode cancels back to normal mode.

> **`Ctrl-B` conflict:** This is the same key as Vim's full-page-backward scroll.
> When running Vim inside tmux, tmux intercepts `Ctrl-B` first — Vim never receives
> it. Workarounds: (1) Remap tmux prefix to `Ctrl-Space` (cleanest — no Vim
> conflicts), (2) use `Ctrl-A` as prefix (but shadows Vim's increment-number),
> (3) double-tap `Ctrl-B Ctrl-B` to pass it through to Vim, (4) use `Ctrl-U` or
> `PageUp` instead of `Ctrl-B` in Vim. Almost nobody keeps the default prefix
> when using Vim inside tmux.

### Pane Management

| Prefix + Key | Description |
|---|---|
| `"` | Split pane horizontally (top/bottom); auto-unzooms |
| `%` | Split pane vertically (left/right); auto-unzooms |
| `x` | Close active pane (enters confirm mode: `y`/`n`) |
| `!` | Break pane out to new window; auto-unzooms |
| `z` | Toggle zoom on active pane |
| `q` | Display pane numbers (press `0`–`9` to jump to pane) |

### Pane Navigation

All navigation keys auto-unzoom if the window is zoomed.

| Prefix + Key | Description |
|---|---|
| `↑` / `k` | Navigate to pane above |
| `↓` / `j` | Navigate to pane below |
| `←` / `h` | Navigate to pane left |
| `→` / `l` | Navigate to pane right |
| `o` | Cycle to next pane |
| `;` | Toggle to last-active pane |

> **Common remapping note:** The `h`/`j`/`k`/`l` bindings are not tmux defaults —
> they are added via `bind h select-pane -L`, etc. in `~/.tmux.conf` (our
> simulator has them built-in). Because `l` (lowercase) shadows the default
> "last window" binding, most people remap last-window to another key — `Tab` is
> a popular choice (`bind Tab last-window`). In our simulator, last-window is on
> `L` (uppercase, i.e. `Prefix + Shift-L`).

### Pane Resize

| Prefix + Key | Description |
|---|---|
| `Ctrl-↑` | Resize pane up by 1 cell |
| `Ctrl-↓` | Resize pane down by 1 cell |
| `Ctrl-←` | Resize pane left by 1 cell |
| `Ctrl-→` | Resize pane right by 1 cell |

### Pane Swap

Auto-unzooms before swapping.

| Prefix + Key | Description |
|---|---|
| `{` | Swap active pane with previous |
| `}` | Swap active pane with next |

### Window Management

| Prefix + Key | Description |
|---|---|
| `c` | Create new window |
| `n` | Next window |
| `p` | Previous window |
| `L` | Toggle to last-active window |
| `0`–`9` | Switch to window N |
| `,` | Rename current window |
| `&` | Close current window (enters confirm mode: `y`/`n`) |
| `w` | Interactive window chooser |

### Layout

| Prefix + Key | Description |
|---|---|
| `Space` | Cycle through preset layouts |

Layout presets cycle through 4 arrangements: even-horizontal, even-vertical,
main-horizontal (60/40), main-vertical (60/40).

### Session

| Prefix + Key | Description |
|---|---|
| `d` | Detach from tmux |

### Other Prefix Keys

| Prefix + Key | Description |
|---|---|
| `[` / `PageUp` | Enter copy mode |
| `:` | Open command prompt |
| `t` | Clock mode (ASCII art clock; any key exits) |
| `?` | Help overlay (scrollable key binding list) |
| `Ctrl-B` | Send literal `Ctrl-B` to the active pane |

### Copy Mode (vi bindings)

Entered via `Ctrl-B [` or `Ctrl-B PageUp`. Provides a read-only view of the
pane with vim-style navigation.

| Key | Description |
|---|---|
| `q` / `Escape` | Exit copy mode |
| `j` / `↓` | Cursor down |
| `k` / `↑` | Cursor up (scrolls viewport when at top) |
| `h` / `←` | Cursor left |
| `l` / `→` | Cursor right |
| `g` | Jump to top (row 0) |
| `G` | Jump to bottom |
| `0` | Start of line |
| `$` | End of line |
| `w` | Word forward (simplified: +5 columns) |
| `b` | Word backward (simplified: −5 columns) |
| `Ctrl-F` | Page down |
| `Ctrl-B` | Page up |
| `Ctrl-D` | Half-page down |
| `Ctrl-U` | Half-page up |
| `v` | Toggle visual selection |

### Command Prompt

Entered via `Ctrl-B :`. Type a command and press `Enter`.

| Command | Alias | Description |
|---|---|---|
| `split-window [-h]` | `splitw` | Split pane (default: top/bottom; `-h`: left/right) |
| `new-window` | `neww` | Create new window |
| `rename-window name` | `renamew` | Rename active window |
| `select-window -t N` | `selectw` | Switch to window N |
| `select-pane -t N` | `selectp` | Switch to pane N |
| `resize-pane -U/-D/-L/-R [n]` | `resizep` | Resize active pane in direction by n cells |
| `kill-pane` | `killp` | Close active pane (detaches if last pane of last window) |
| `kill-window` | `killw` | Close active window (only if >1 window) |
| `swap-pane -U/-D` | `swapp` | Swap active pane up or down |
| `new-session name` | `new` | Create a new session |
| `switch-client -t name` | `switchc` | Switch to a named session |
| `list-sessions` | `ls` | List all sessions |
| `detach-client` | `detach` | Detach from tmux |
| `next-layout` | `nextl` | Cycle to next layout preset |
| `display-panes` | `displayp` | Show pane number overlay |
| `clock-mode` | `clock` | Show ASCII art clock |
| `list-keys` | `lsk` | Show key bindings help |
| `bind[-key] key command [args]` | `bind` | Bind a key in the prefix table |
| `unbind[-key] key` | `unbind` | Remove a prefix key binding |
| `set[-option] [-g] prefix key` | `set` | Change the prefix key |
| `source[-file] path` | `source` | Reload `.tmux.conf` from VFS |

Unknown commands display: `unknown command: …`

### Command Prompt Keys

| Key | Description |
|---|---|
| Characters | Append to input |
| `Backspace` | Delete last character (stays in command mode if empty) |
| `Ctrl-U` | Clear entire input |
| `Enter` | Execute command |
| `Escape` | Cancel |

### Confirm Mode

Triggered by prefix `x` (kill pane) or prefix `&` (kill window). Shows a
confirmation prompt:

- Pane close: `kill-pane N? (y/n)`
- Window close: `kill-window name? (y/n)`

| Key | Description |
|---|---|
| `y` / `Y` | Confirm the kill |
| Any other key | Cancel, return to normal mode |

If killing the last pane in the last window (or last window), tmux detaches.

### Rename Mode

Entered via prefix `,`. Pre-populates with the current window name.

| Key | Description |
|---|---|
| Characters | Append to name |
| `Backspace` | Delete last character |
| `Ctrl-U` | Clear entire name |
| `Enter` | Commit rename |
| `Escape` | Cancel |

### Window List Mode

Entered via prefix `w`. Shows all windows with `(N) name` per entry.

| Key | Description |
|---|---|
| `j` / `↓` | Cursor down |
| `k` / `↑` | Cursor up |
| `Enter` | Switch to selected window |
| `Escape` / `q` | Cancel |

### Pane Numbers Mode

Entered via prefix `q`. Shows pane index numbers overlaid on each pane.
Active pane number is green, inactive are red.

| Key | Description |
|---|---|
| `0`–`9` | Switch to pane N |
| Any other key | Exit |

### Status Bar

```
<session> | <window_list>              | HH:MM | DD-Mon-YY
```

| Segment | Content | Color |
|---|---|---|
| Session name | `0:name` | Green, bold |
| Separator | `\|` | Gray |
| Active window | `N:name*` (or `N:name*Z` if zoomed) | Green on selection bg, bold |
| Inactive windows | `N:name` | Gray |
| Clock | `HH:MM` | Cyan |
| Date | `DD-Mon-YY` | Gray |

### Pane Borders

- Active pane border: green
- Inactive pane border: muted/selection color
- Border characters: `─` (horizontal), `│` (vertical), `┼` (intersection)

### Auto-Unzoom Behavior

When the active pane is zoomed, the following prefix keys automatically unzoom
before performing their action: `"`, `%`, `↑`/`↓`/`←`/`→`, `h`/`j`/`k`/`l`,
`o`, `;`, `{`, `}`, `!`.

### Pane Auto-Close

When a pane's shell process exits (via `exit` or `Ctrl-D`), tmux automatically
closes that pane. If it was the last pane in the window, the window closes. If
it was the last window in the session, tmux detaches.

### Key Binding Configuration

All prefix-key bindings are fully configurable at runtime via the command prompt
or on startup via `.tmux.conf`.

#### Changing the Prefix Key

```
set -g prefix C-Space
```

Accepted key notations:

| Notation | Internal Key |
|---|---|
| `C-a` | `Ctrl-A` |
| `C-Space` | `Ctrl-Space` |
| `C-b` | `Ctrl-B` |
| `Up` / `Down` / `Left` / `Right` | `ArrowUp` / `ArrowDown` / `ArrowLeft` / `ArrowRight` |
| `Space` | ` ` (space character) |
| `M-x` | `Alt-x` |
| Single character | Itself (`x`, `"`, `%`, etc.) |

#### Binding and Unbinding Keys

```
bind v split-window -h       # bind Prefix+v to vertical split
bind s split-window           # bind Prefix+s to horizontal split
bind e next-window            # bind Prefix+e to next window
unbind "                      # remove the " binding
```

Supported tmux commands for `bind`:

| Command | Action |
|---|---|
| `split-window [-h]` | Split (default: horizontal; `-h`: vertical) |
| `select-pane -U/-D/-L/-R` | Navigate pane in direction |
| `resize-pane -U/-D/-L/-R` | Resize pane in direction |
| `next-pane` | Cycle to next pane |
| `last-pane` | Toggle to last-active pane |
| `swap-pane -U/-D` | Swap pane up/down |
| `break-pane` | Break pane to new window |
| `display-panes` | Show pane numbers |
| `new-window` | Create new window |
| `next-window` / `previous-window` | Switch windows |
| `rename-window` | Enter rename mode |
| `kill-window` | Close window |
| `choose-tree` | Window list chooser |
| `last-window` | Toggle last window |
| `detach-client` | Detach from tmux |
| `copy-mode` | Enter copy mode |
| `command-prompt` | Open command prompt |
| `clock-mode` | Clock display |
| `next-layout` | Cycle layout |
| `list-keys` | Show help |

#### `.tmux.conf`

On tmux startup, the simulator reads `.tmux.conf` from the VFS (if it exists)
and executes each line. Supported directives:

```bash
# Comments start with #
set -g prefix C-Space             # change prefix key
bind v split-window -h            # add a binding
bind h select-pane -L             # remap h to nav left
unbind "                          # remove a binding
```

To reload the config at runtime: `:source .tmux.conf`

#### Dynamic Help Overlay

The `?` help overlay dynamically reflects the current bindings. If you remap
keys or change the prefix, the help screen updates to show the actual
configuration.

---

## Virtual Filesystem (VFS)

- Flat in-memory filesystem (no directories)
- Optional localStorage persistence
- Operations: `ls`, `exists`, `read`, `write`, `rm`, `clear`

---

## Rendering

### Screen

Converts engine state → Frame dict with colored runs per line:
- Tab expansion (tabstop 8)
- Syntax highlighting (Python grammar)
- Visual selection overlay
- Search match highlighting (CurSearch vs regular)
- Status line + command line theming
- Message prompt overlay (E37, E486 errors)

### Themes

| Theme | Background | Foreground | Use |
|---|---|---|---|
| `nvim_default` | `#14161b` | `#e0e2ea` | Ground truth tests |
| `monokai` | `#000000` | `#d4d4d4` | Browser / GIFs |

### Syntax Highlighting

- Python only (`.py` files)
- TextMate-style regex tokenizer
- Scopes: keyword, string, comment, number, constant, decorator, builtin, special, function.def, class.def, operator

### Renderer

Canvas-based HTML renderer:
- Monospace font (Cascadia Mono / Consolas)
- Per-run foreground + background drawing
- Bold support
- Block cursor (dark red `#800000`) for vim and shell vi-normal/replace modes
- Beam cursor (thin 2px vertical bar, `#cccccc`) for shell insert/emacs modes
