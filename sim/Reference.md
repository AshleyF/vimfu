# VimFu Simulator — Command Reference

Exhaustive reference of every key, command, and feature supported.

---

## Modes

| Mode | Entry | Status line |
|---|---|---|
| Normal | `Escape` from any mode | *(empty)* or `recording @x` |
| Insert | `i`, `I`, `a`, `A`, `o`, `O`, `s`, `S`, `c…`, `gi`, `gI` | `-- INSERT --` |
| Replace | `R` | `-- REPLACE --` |
| Visual | `v` | `-- VISUAL --` |
| Visual Line | `V` | `-- VISUAL LINE --` |
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
| `0` | — | Start of line (col 0) |
| `^` | — | First non-blank on line |
| `$` | ✅ | End of line (`2$` = end of next line) |
| `_` | ✅ | First non-blank, count−1 lines down |
| `g_` | ✅ | Last non-blank on line |
| `f{char}` | ✅ | Find char forward (inclusive) |
| `F{char}` | ✅ | Find char backward (inclusive) |
| `t{char}` | ✅ | Till char forward (exclusive) |
| `T{char}` | ✅ | Till char backward (exclusive) |
| `;` | ✅ | Repeat last `f`/`F`/`t`/`T` |
| `,` | ✅ | Repeat last find, reversed |
| `%` | — | Match bracket `(){}[]` |
| `{count}%` | ✅ | Go to N% of file |
| `{` | ✅ | Paragraph backward |
| `}` | ✅ | Paragraph forward |
| `(` | ✅ | Sentence backward |
| `)` | ✅ | Sentence forward |
| `gg` | ✅ | Go to line N (default: first) |
| `G` | ✅ | Go to line N (default: last) |
| `H` | ✅ | Screen top (count = offset) |
| `M` | — | Screen middle |
| `L` | ✅ | Screen bottom (count = offset) |
| `+` / `Enter` | ✅ | Next line, first non-blank |
| `-` | ✅ | Prev line, first non-blank |
| `\|` | ✅ | Go to column N (1-based) |
| `Backspace` | ✅ | Left, wrapping to prev line |
| `Space` | ✅ | Right, wrapping to next line |
| `n` | ✅ | Next search match |
| `N` | ✅ | Prev search match |
| `*` | — | Search word under cursor forward |
| `#` | — | Search word under cursor backward |

### Editing

| Key | Count | Description |
|---|---|---|
| `x` / `Delete` | ✅ | Delete char under cursor |
| `X` | ✅ | Delete char before cursor |
| `s` | ✅ | Substitute N chars (delete + insert) |
| `S` | ✅ | Substitute N lines (preserves indent) |
| `r{char}` | ✅ | Replace N chars with {char} |
| `R` | — | Enter replace mode |
| `~` | ✅ | Toggle case, advance cursor |
| `J` | ✅ | Join N lines (smart spacing) |
| `gJ` | ✅ | Join N lines (no spacing) |
| `D` | — | Delete to end of line (`d$`) |
| `C` | — | Change to end of line (`c$`) |
| `Y` | ✅ | Yank to end of line (`y$`) |
| `u` | ✅ | Undo |
| `Ctrl-R` | ✅ | Redo |
| `.` | ✅ | Repeat last change (count overrides) |
| `Ctrl-A` | ✅ | Increment number at/after cursor |
| `Ctrl-X` | ✅ | Decrement number at/after cursor |
| `Ctrl-G` | — | Show file info (name, lines, bytes) |
| `ga` | — | Show ASCII/hex/octal of char under cursor |
| `gd` | — | Go to local declaration of word under cursor |

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

Examples: `d3w`, `ciw`, `>}`, `gUap`, `yy`, `5dd`, `<<`, `dG`, `c/foo↵`

Special: `cw` on a word behaves like `ce` (doesn't include trailing space). `dw` at EOL doesn't cross lines.

### Put (Paste)

| Key | Count | Description |
|---|---|---|
| `p` | ✅ | Put after cursor (linewise: below) |
| `P` | ✅ | Put before cursor (linewise: above) |

### Enter Insert Mode

| Key | Count | Description |
|---|---|---|
| `i` | ✅ | Insert before cursor (`3i` repeats text) |
| `I` | ✅ | Insert at first non-blank |
| `a` | ✅ | Append after cursor |
| `A` | ✅ | Append at end of line |
| `o` | ✅ | Open line below (inherits indent) |
| `O` | ✅ | Open line above (inherits indent) |
| `gi` | — | Insert at last insert position |
| `gI` | — | Insert at column 0 |

### Scroll

| Key | Count | Description |
|---|---|---|
| `Ctrl-D` | ✅ | Half-page down (sticky count) |
| `Ctrl-U` | ✅ | Half-page up (sticky count) |
| `Ctrl-F` | ✅ | Full page forward |
| `Ctrl-B` | ✅ | Full page backward |
| `Ctrl-E` | ✅ | Scroll viewport down 1 line |
| `Ctrl-Y` | ✅ | Scroll viewport up 1 line |
| `zz` | — | Center current line |
| `zt` | — | Current line to top |
| `zb` | — | Current line to bottom |

### Marks

| Key | Description |
|---|---|
| `m{a-z}` | Set mark |
| `'{a-z}` | Jump to mark line (first non-blank) |
| `` `{a-z} `` | Jump to exact mark position |

Works with operators: `d'a` (linewise), `` d`a `` (charwise).

### Jump List

| Key | Description |
|---|---|
| `Ctrl-O` | Jump to older position in jump list |
| `Ctrl-I` | Jump to newer position in jump list |

Jump entries added by: `G`, `gg`, `n`, `N`, `*`, `#`, `gd`.

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
| `@@` | Replay last macro (supports count) |
| `Q` | Replay last macro (supports count) |

Entire macro is a single undo unit. Aborts on failed motion.

### Registers

| Key | Description |
|---|---|
| `"{a-z}` | Select register for next `d`/`c`/`y`/`p` |

Unnamed register always updated. Named registers `a-z` only when explicitly selected. Each stores content + type (line or char).

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

---

## Insert Mode

| Key | Description |
|---|---|
| `Escape` | Return to normal (cursor moves left 1) |
| `Enter` / `Ctrl-J` | Split line at cursor |
| `Backspace` / `Ctrl-H` | Delete char before cursor (joins lines) |
| `Delete` | Delete char at cursor (forward delete) |
| `Ctrl-W` | Delete word backward |
| `Ctrl-U` | Delete to start of line |
| `Ctrl-R {reg}` | Paste from register (`a-z`, `0-9`, `"`) |
| `←` / `→` | Move cursor left/right |
| `↑` / `↓` | Move cursor up/down |
| Any printable | Insert character |

Count-insert: `3iHa↵` types `Ha` then repeats 2 more times on Escape → `HaHaHa`.

---

## Replace Mode

| Key | Description |
|---|---|
| `Escape` | Return to normal |
| `Enter` / `Ctrl-J` | Split line |
| `Backspace` / `Ctrl-H` | Restore original character |
| Any printable | Overwrite char at cursor |

Backspace cannot go before the position where `R` was pressed.

---

## Visual Mode

### Mode Switching

| Key | Description |
|---|---|
| `v` | Toggle char-visual / exit |
| `V` | Toggle line-visual / exit |
| `gv` | Reselect last visual selection |
| `Escape` | Return to normal |
| `o` / `O` | Swap cursor and selection anchor |

### Motions

All normal-mode motions work in visual mode to extend the selection.

### Actions

| Key | Description |
|---|---|
| `d` / `x` | Delete selection |
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

Multi-line pairs supported. Handles escaped quotes. If cursor not inside, searches forward.

---

## Command Mode (Ex Commands)

All Ex commands accept standard nvim abbreviations — any unambiguous prefix
of the full command name is valid (e.g. `:wri` → `:write`, `:qui` → `:quit`).

| Command | Description |
|---|---|
| `:w[rite] [file]` | Save to VFS (shows `"file" NL, NB written`) |
| `:wq [file]` | Save and quit |
| `:x[it]` | Save and quit |
| `:q[uit]` | Quit (fails with E37 if dirty) |
| `:q[uit]!` | Force quit (discard changes) |
| `:e[dit] file` | Edit a different file |
| `:{number}` | Go to line number |
| `:$` | Go to last line |
| `:noh[lsearch]` | Clear search highlighting (pattern kept for `n`/`N`) |
| `:se[t] number` / `:se[t] nu` | Show absolute line numbers |
| `:se[t] nonumber` / `:se[t] nonu` | Hide line numbers |
| `:se[t] relativenumber` / `:se[t] rnu` | Show relative line numbers |
| `:se[t] norelativenumber` / `:se[t] nornu` | Hide relative line numbers |
| `:r[ead] file` | Read file contents into buffer below cursor |
| `:r[ead]! command` | Read shell command output into buffer below cursor |
| `:[range]sort[!] [flags]` | Sort lines (`!` = reverse; flags: `n` numeric, `i` ignore-case, `u` unique) |
| `:!command` | Run shell command (see below) |

### `:set` Options

| Option | Short | Description |
|---|---|---|
| `number` | `nu` | Show absolute line numbers in a left gutter |
| `nonumber` | `nonu` | Hide absolute line numbers |
| `relativenumber` | `rnu` | Show relative line distances in the gutter |
| `norelativenumber` | `nornu` | Hide relative line numbers |

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
| `:!pwd` | Print working directory |
| `:!echo text` | Print text |
| `:!rm file` | Remove file from VFS |
| `:!anything_else` | Shows "command not found" |

Output shown in a "Press ENTER" prompt overlay.

### Command-Line Keys

| Key | Description |
|---|---|
| `Escape` | Cancel |
| `Enter` | Execute |
| `Backspace` | Delete char (or cancel if empty) |
| Any printable | Append to command |

---

## Shell

### Commands

| Command | Description |
|---|---|
| `vim [file]` | Open file in vim (`vi` and `nvim` also work) |
| `ls` | List files |
| `cat file…` | Print file contents |
| `touch file…` | Create empty file(s) |
| `rm file…` | Delete file(s) |
| `echo text` | Print text (supports `> file` redirect) |
| `sort file` | Sort lines of a file (`-r` reverse, `-n` numeric, `-u` unique) |
| `set -o vi` | Enable vi-mode line editing |
| `set -o emacs` | Disable vi-mode (default) |
| `set` | Show current editing mode |
| `date` | Print current date and time |
| `pwd` | Print working directory (`~/vimfu`) |
| `clear` | Clear screen |
| `help` | Show command list |
| *anything else* | "command not found" |

### Keys (Emacs mode — default)

| Key | Description |
|---|---|
| `Enter` | Execute command |
| `Backspace` | Delete char before cursor |
| `←` / `→` | Move cursor |
| `↑` / `↓` | Command history navigation |
| `Home` / `Ctrl-A` | Cursor to start |
| `End` / `Ctrl-E` | Cursor to end |
| `Ctrl-C` | Cancel current input |
| `Ctrl-L` | Clear screen |
| `Ctrl-U` | Delete to start of line |
| `Ctrl-K` | Delete to end of line |
| `Ctrl-W` | Delete word backward |
| `Tab` | Filename tab completion |

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
| `0` / `Home` | — | Start of line |
| `$` / `End` | — | End of line (inclusive) |
| `^` / `_` | — | First non-whitespace character |
| `f{char}` | — | Find char forward (inclusive) |
| `F{char}` | — | Find char backward (inclusive) |
| `t{char}` | — | Till char forward (exclusive — stops one before) |
| `T{char}` | — | Till char backward (exclusive — stops one after) |
| `;` | — | Repeat last `f`/`F`/`t`/`T` |
| `,` | — | Repeat last find, reversed direction |

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
| `S` | — | Substitute entire line |
| `r{char}` | ✅ | Replace N chars with {char} |
| `R` | — | Enter replace (overtype) mode |
| `~` | ✅ | Toggle case, advance cursor |
| `D` | — | Delete to end of line |
| `C` | — | Change to end of line |
| `p` | ✅ | Put yanked text after cursor (N times) |
| `P` | ✅ | Put yanked text before cursor (N times) |
| `u` | — | Undo last change |
| `.` | — | Repeat last change (dot-repeat) |
| `#` | — | Comment out line (prepend `#`) and execute |

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
