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
| `f{char}` | ✅ | Find char forward (inclusive; `Tab` = literal tab) |
| `F{char}` | ✅ | Find char backward (inclusive; `Tab` = literal tab) |
| `t{char}` | ✅ | Till char forward (exclusive; `Tab` = literal tab) |
| `T{char}` | ✅ | Till char backward (exclusive; `Tab` = literal tab) |
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
| `D` | ✅ | Delete to end of line (`d$`); `2D` deletes to EOL + next line |
| `C` | — | Change to end of line (`c$`) |
| `Y` | — | Yank to end of line (`y$`) |
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

Special: `cw` on a word behaves like `ce` (doesn't include trailing space). `dw` at EOL doesn't cross lines. `cc` / `S` preserve leading indent.

### Put (Paste)

| Key | Count | Description |
|---|---|---|
| `p` | ✅ | Put after cursor (linewise: below) |
| `P` | ✅ | Put before cursor (linewise: above) |

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
| `"{a-z}` | Select register for next `d`/`c`/`y`/`p` |

Unnamed register always updated. Named registers `a-z` only when explicitly selected. Each stores content + type (line or char).
In visual mode, `"` also accepts uppercase `A-Z` and digit `0-9` registers.
`Ctrl-R` in insert mode accepts `a-z`, `0-9`, and `"` (unnamed).

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
| `Escape` / `Ctrl-[` | Return to normal (cursor moves left 1) |
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
| `Escape` / `Ctrl-[` | Return to normal |
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

| Command | Description |
|---|---|
| `:w[rite] [file]` | Save to VFS (shows `"file" NL, NB written`); if buffer has no filename, uses the given name and sets it as current |
| `:wq [file]` | Save and quit (always writes; shows E32 if no filename available) |
| `:x[it]` | Save (only if dirty) and quit (shows E32 if no filename available) |
| `:q[uit]` | Quit (fails with E37 if dirty) |
| `:q[uit]!` | Force quit (discard changes) |
| `:e[dit] [file]` | Edit file; with no arg, reloads current file from VFS (shows E32 if no filename set) |
| `:e[dit]! [file]` | Force re-edit (discard changes); also accepts a filename |
| `:sav[eas] file` | Save buffer to new file, set it as current filename, update highlighting |
| `:{number}` | Go to line number |
| `:$` | Go to last line |
| `:noh[lsearch]` | Clear search highlighting (pattern kept for `n`/`N`) |
| `:se[t] …` | Set options (see below) |
| `:r[ead] file` | Read file contents below cursor (shows "N line(s) added"; sets filename if none; shows E484 if file not found) |
| `:r[ead]! command` | Read shell command output below cursor (shows "N line(s) added") |
| `:[range]sort[!] [flags]` | Sort lines (`!` = reverse; flags: `n` numeric, `i` ignore-case, `u` unique) |
| `:!command` | Run shell command (see below) |

### `:wq` vs `:x`

`:wq` always writes the file, even if the buffer is clean. `:x` only writes if
the buffer has been modified (dirty). Both quit after writing.

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

### Command-Line Keys

| Key | Description |
|---|---|
| `Escape` | Cancel |
| `Enter` | Execute |
| `Backspace` | Delete char (or cancel if empty) |
| `Tab` | Tab-complete filename (for `:e`, `:w`, `:r`, `:sav`); cycles through matches |
| Any printable | Append to command |

Tab completion matches filenames from the VFS, cycling through matches with
repeated `Tab` presses (nvim `wildmode=full` behavior). The cycle resets on
`Escape` or `Enter`.

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

## Tmux

The simulator includes a full tmux terminal multiplexer with sessions, windows,
panes, and the standard prefix-key interface.

### Prefix Key

All tmux commands are triggered by pressing `Ctrl-B` (the prefix key) followed
by a command key. Pressing `Escape` in prefix mode cancels back to normal mode.

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
| `clock-mode` | — | Show ASCII art clock |
| `list-keys` | `lsk` | Show key bindings help |

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
