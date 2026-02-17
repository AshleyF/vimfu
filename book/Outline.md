# VimFu — Book Outline

This is the master outline for the VimFu book. Each chapter and section lists the curriculum
video lessons it covers, the keys it teaches, and a brief description of its content. This
outline is the source of truth for what the book contains and in what order. Use it when
generating book content — each section here becomes a `gen_<topic>.py` → page JSON → rendered
output.

The curriculum (`curriculum/Curriculum.md`) defines the videos. This outline reorganizes that
material into a cohesive book — grouping related lessons, adding introductory and contextual
material the videos don't have, and structuring it for a reading experience rather than a
playlist.

---

## Front Matter

### Title Page

_VimFu: Master the Vim Editing Language_

### About This Book

Who this book is for, what it assumes (basic programming experience, any editor background),
and what you'll be able to do by the end. Mention the video series and QR codes. Explain that
this is about Vim keybindings as a universal editing language — not about any specific editor.

### How to Use This Book

- Read front to back for beginners
- Jump around for intermediate users who want to fill gaps
- Scan QR codes to watch 60-second video demos
- Have an editor open and follow along — learning Vim is physical, not just intellectual
- Each section has a reference table at the end for quick review

### QR: The VimFu YouTube Playlist

A single QR code linking to the full YouTube playlist so readers can find the series.

---

## Chapter 1 — Why Vim?

_No videos — book-only introductory material._

### 1.1 The Case for Modal Editing

| | |
|---|---|
| **Videos** | 001 (What Is Vim?) |
| **Keys** | — |

Why learn an editing paradigm from 1976? Because you spend more time navigating and
manipulating text than inserting it. Modal editing gives you a full keyboard of commands
for the thing you do most. The productivity argument: once you internalize the grammar,
you think in edits — "delete this word," "change inside quotes," "yank this paragraph" —
rather than reaching for the mouse or holding Ctrl-Shift-Arrow.

### 1.2 You Don't Need Vim

| | |
|---|---|
| **Videos** | — |
| **Keys** | — |

The demos in this book use Neovim, but you can use Vim keybindings in almost any editor.
VS Code (Vim extension), JetBrains IDEs (IdeaVim), Visual Studio, Sublime Text, Emacs
(Evil mode), terminal multiplexers, even web browsers (Vimium). This book teaches the
**keybindings and the editing language**, not any specific editor. Use whatever you like —
just turn on Vim mode.

### 1.3 Vi, Vim, Neovim — A Brief History

| | |
|---|---|
| **Videos** | — |
| **Keys** | — |

Vi (1976, Bill Joy) → Vim (1991, Bram Moolenaar) → Neovim (2014, community fork). For the
keybindings in this book, the differences between them are negligible. The differences matter
for configuration, plugins, and scripting — not for `daw` or `ci"`. Brief timeline, key
milestones, why Neovim exists.

### 1.4 The Modal Philosophy

| | |
|---|---|
| **Videos** | 003 (You're in Normal Mode), 015 (The Escape Habit) |
| **Keys** | `Esc` |

Normal mode is your resting state. Insert mode is a brief excursion — get in, type what you
need, get out. Every key on the keyboard does something in normal mode. That's the whole
point: no modifier keys needed, because you have an entire keyboard of commands. Modes:
Normal, Insert, Visual, Command-line, Replace. How they interact. Why this feels weird at
first and why it clicks later.

---

## Chapter 2 — Survival

_Get in, type, save, and get out alive. After this chapter, you can use Vim without panicking._

### 2.1 Opening and Closing Files

| | |
|---|---|
| **Videos** | 002, 007, 008, 009, 010 |
| **Keys** | `nvim`, `:w`, `:q`, `:wq`, `:x`, `ZZ`, `:q!`, `ZQ` |

Launch Neovim, the empty buffer, what you see. Saving with `:w`, quitting with `:q`, the
combined `:wq` and `:x` and `ZZ`. The meme solved: how to quit Vim. Discarding changes
with `:q!` and `ZQ`. Three ways to save-and-quit, two ways to force-quit.

### 2.2 Insert Mode and Back Again

| | |
|---|---|
| **Videos** | 004, 005, 006, 015 |
| **Keys** | `i`, `Esc` |

Press `i` to insert text. Type normally. Press `Esc` to return to normal mode. The most
fundamental mode switch. Build the `Esc` reflex — after every thought, Escape. This becomes
second nature.

### 2.3 Undo and Redo

| | |
|---|---|
| **Videos** | 011, 012 |
| **Keys** | `u`, `Ctrl-R` |

Undo with `u`, redo with `Ctrl-R`. Vim is safe to experiment in — you can always undo.
Multiple levels of undo. Brief mention that Vim's undo is actually a tree, not a stack
(deeper dive in a later chapter).

### 2.4 Basic Movement: h j k l

| | |
|---|---|
| **Videos** | 013, 014 |
| **Keys** | `h`, `j`, `k`, `l`, `←`, `↓`, `↑`, `→` |

Left, down, up, right. Hands stay on the home row. Arrow keys work but defeat the purpose.
Why `hjkl`? Historical reason (ADM-3A terminal), practical reason (home row speed). Start
breaking the arrow key habit now.

---

## Chapter 3 — Basic Editing

_Enough to get real work done. After this chapter, go cold turkey — use Vim for everything._

### 3.1 More Ways into Insert Mode

| | |
|---|---|
| **Videos** | 016, 017, 018, 019, 020 |
| **Keys** | `a`, `I`, `A`, `o`, `O` |

`a` appends after the cursor, `I` inserts at the start of the line, `A` appends at the end,
`o` opens a new line below, `O` opens above. Six ways to enter insert mode, each saves you
a motion. Choose the one that puts you exactly where you need to be.

### 3.2 Word Motions

| | |
|---|---|
| **Videos** | 021, 022, 023, 024 |
| **Keys** | `w`, `b`, `e`, `ge` |

Navigate by words instead of characters. `w` jumps to the next word start, `b` jumps back,
`e` jumps to the end of the current/next word, `ge` jumps backward to the end of the previous
word. What counts as a "word" (letters, digits, underscores vs. punctuation). These are
your bread-and-butter motions.

### 3.3 Line Motions

| | |
|---|---|
| **Videos** | 025, 026, 027 |
| **Keys** | `0`, `^`, `$` |

Jump within a line: `0` goes to column zero, `^` goes to the first non-whitespace character,
`$` goes to the end. The difference between `0` and `^` — indented code makes `^` essential.

### 3.4 File Motions

| | |
|---|---|
| **Videos** | 028, 029, 030 |
| **Keys** | `gg`, `G`, `:{n}`, `{n}G` |

Jump anywhere in the file: `gg` to the top, `G` to the bottom, `42G` or `:42` to line 42.
Big jumps for big files. These are the motions that make scrolling with `j`/`k` feel
primitive.

### 3.5 Deleting Text

| | |
|---|---|
| **Videos** | 031, 032, 033, 034, 035 |
| **Keys** | `x`, `X`, `dw`, `D`, `d$`, `dd` |

Character deletes: `x` deletes under the cursor, `X` deletes before (like backspace).
Motion deletes: `dw` deletes a word, `D` (or `d$`) deletes to end of line, `dd` deletes
the whole line. First taste of the **operator + motion** pattern: `d` is the operator,
`w`/`$` is the motion. This pattern scales to everything.

### 3.6 Changing Text

| | |
|---|---|
| **Videos** | 036, 037, 038, 039 |
| **Keys** | `cw`, `C`, `c$`, `cc`, `S`, `s` |

Change = delete + enter insert mode. `cw` changes a word, `C` (or `c$`) changes to end of
line, `cc` (or `S`) changes the whole line, `s` substitutes a single character. Same operator
pattern as delete, but you end up in insert mode ready to type the replacement.

### 3.7 Yank and Put (Copy and Paste)

| | |
|---|---|
| **Videos** | 040, 041, 042, 043, 044 |
| **Keys** | `yy`, `Y`, `p`, `P`, `yw`, `y$`, `y{motion}` |

Vim calls it "yank" and "put" instead of "copy" and "paste." `yy` yanks the current line,
`p` puts after, `P` puts before. `yw`, `y$`, `y{motion}` — same operator pattern again.
The `ddp` line-swap trick, the `xp` character-swap trick. Where does yanked text go? (Brief
intro to the unnamed register — deeper dive in the Registers chapter.)

### 3.8 Replace

| | |
|---|---|
| **Videos** | 045 |
| **Keys** | `r{char}` |

Replace the character under the cursor without entering insert mode. Quick single-character
fixes. No mode switch overhead — stay in normal mode.

---

## Chapter 4 — Search and Find

_Jump anywhere on the screen or in the file by searching._

### 4.1 Pattern Search

| | |
|---|---|
| **Videos** | 046, 047, 048, 049 |
| **Keys** | `/pattern`, `?pattern`, `n`, `N` |

Search forward with `/`, backward with `?`. Navigate matches with `n` (next) and `N`
(previous). Search wraps around the file. Regex basics (just enough to be useful). The
search highlighting.

### 4.2 Word Search

| | |
|---|---|
| **Videos** | 050, 051 |
| **Keys** | `*`, `#` |

Place your cursor on a word and press `*` to search forward for it, `#` to search backward.
Whole-word matching (word boundaries). The fastest way to find other occurrences of a variable
or function name.

### 4.3 Find on Line

| | |
|---|---|
| **Videos** | 052, 053, 054, 055, 056, 057 |
| **Keys** | `f{char}`, `F{char}`, `t{char}`, `T{char}`, `;`, `,` |

Character-level precision on the current line. `f` finds forward, `F` finds backward, `t`
stops just before (till), `T` stops just after. Repeat with `;` (same direction) and `,`
(opposite). These are surgical motions — jump exactly to the character you want. Combined
with operators (`df.`, `ct"`, etc.) they're incredibly powerful.

---

## Chapter 5 — Counts, Positions, and Visual Mode

_Multiply your commands, jump to precise positions, and select text visually._

### 5.1 Counts

| | |
|---|---|
| **Videos** | 058, 059, 060, 061 |
| **Keys** | `{n}j`, `{n}w`, `{n}dd`, `{n}dw`, `{n}i`, `{n}G` |

Prefix any motion or command with a number to repeat it. `5j` moves down 5 lines, `3dd`
deletes 3 lines, `5i-Esc` inserts five dashes. Counts multiply everything. The grammar
expands: `[count] operator [count] motion`.

### 5.2 Jump to Percentage and Column

| | |
|---|---|
| **Videos** | 062, 063 |
| **Keys** | `{n}%`, `{n}\|` |

`50%` jumps to the middle of the file. `20|` jumps to column 20. Positional precision
for large files and wide lines.

### 5.3 Character Visual Mode

| | |
|---|---|
| **Videos** | 064, 068 |
| **Keys** | `v`, `d`, `c`, `y`, `>`, `<` |

Press `v` to start selecting character by character. Any motion extends the selection.
Then apply an operator: `d` to delete, `c` to change, `y` to yank, `>` to indent, `<` to
unindent. Visual mode is the "select, then act" paradigm — familiar from other editors but
powered by Vim motions.

### 5.4 Line and Block Visual Mode

| | |
|---|---|
| **Videos** | 065, 066, 067 |
| **Keys** | `V`, `Ctrl-V` |

`V` selects whole lines. `Ctrl-V` selects a rectangular block (columns) — uniquely powerful
for editing tabular data, adding prefixes to multiple lines, or working with columnar output.
Switch between modes with `v`, `V`, `Ctrl-V` while a selection is active.

### 5.5 Visual Mode Tricks

| | |
|---|---|
| **Videos** | 069, 070 |
| **Keys** | `o`, `O`, `gv` |

`o` jumps to the other end of the selection (extend from either side). `O` in block visual
mode moves to the other corner horizontally. `gv` re-selects the previous visual area —
handy when you need to operate on the same region again.

---

## Chapter 6 — The Dot Command

_The most important key in Vim: repeat the last change._

### 6.1 Repeat Last Change

| | |
|---|---|
| **Videos** | 071 |
| **Keys** | `.` |

The dot command repeats your last change — whatever you did between entering and leaving
insert mode, or whatever operator+motion you just executed. It's Vim's "do it again" button.
What counts as "a change": entering insert mode through leaving it is one change; an
operator+motion is one change; a single `x` or `r` is one change.

### 6.2 Dot with Counts

| | |
|---|---|
| **Videos** | 072 |
| **Keys** | `{n}.` |

`3.` repeats the last change three times. Counted dot is a lightweight alternative to macros
for simple repetition.

### 6.3 Dot Patterns

| | |
|---|---|
| **Videos** | 073 |
| **Keys** | `cw`, `n`, `.` (star-dot pattern) |

The classic workflow: change a word (`cw` + type + `Esc`), search for the next occurrence
(`n`), repeat the change (`.`). The `*cwreplacement<Esc>` then `n.n.n.` pattern. Also
`/pattern` + `cgn` + `.` for even smoother repeating. Structure your edits to make dot
maximally useful — this is a skill worth developing.

---

## Chapter 7 — Text Objects

_The concept that makes Vim's grammar truly powerful: structured editing._

### 7.1 Inner Word and A Word

| | |
|---|---|
| **Videos** | 074 |
| **Keys** | `ciw`, `diw`, `yiw`, `daw`, `caw` |

The difference between "inner" and "a": `iw` is just the word, `aw` includes surrounding
whitespace. `ciw` changes the word (leaves you in insert mode), `daw` deletes the word plus
the space after it. Text objects don't care where your cursor is within the word — they
operate on the whole thing.

### 7.2 Quote Text Objects

| | |
|---|---|
| **Videos** | 075, 076, 077 |
| **Keys** | `ci"`, `da"`, `yi"`, `ci'`, `da'`, `` ci` ``, `` da` `` |

Act on text inside or around double quotes, single quotes, or backticks. The cursor doesn't
need to be on the quote — Vim searches forward on the line to find the nearest pair. `ci"`
is one of the most-used commands in daily editing: jump into a string and replace its
contents without touching the quotes.

### 7.3 Bracket Text Objects

| | |
|---|---|
| **Videos** | 078, 079, 080, 081 |
| **Keys** | `ci(`, `ci{`, `ci[`, `ci<`, `da)`, `da}`, `da]`, `da>`, `dib`, `diB` |

Parentheses, braces, brackets, angle brackets — each has an inner/around text object.
`ci{` changes everything inside curly braces (function bodies, blocks). `da(` deletes the
parenthesized expression including the parens. `b` is a synonym for `(`, `B` is a synonym
for `{`. These are essential for editing code.

### 7.4 Sentence and Paragraph

| | |
|---|---|
| **Videos** | 082, 083 |
| **Keys** | `cis`, `das`, `cip`, `dap` |

Sentences (delimited by `.` `!` `?` followed by whitespace) and paragraphs (separated by
blank lines). `dap` deletes a whole paragraph. `cip` changes a paragraph — great for
rewriting blocks of prose or comment blocks.

### 7.5 Tag Text Objects

| | |
|---|---|
| **Videos** | 084 |
| **Keys** | `cit`, `dat` |

HTML/XML tag content: `cit` changes the text between matching tags, `dat` deletes the
entire tag including the tags themselves. Essential for web development.

### 7.6 The Vim Grammar — Putting It All Together

| | |
|---|---|
| **Videos** | 085 |
| **Keys** | `[count] [register] operator [count] motion/text-object` |

The composable grammar: operators (verbs) × motions/text objects (nouns) = commands. Learn
one new operator, it works with every motion. Learn one new text object, it works with every
operator. This is why Vim scales. Matrix table showing the combinations. This section is the
conceptual climax of the book's first half.

---

## Chapter 8 — Scrolling and Screen Position

_Move through files without losing context._

### 8.1 Half-Page and Full-Page Scrolling

| | |
|---|---|
| **Videos** | 086, 087, 088, 089 |
| **Keys** | `Ctrl-D`, `Ctrl-U`, `Ctrl-F`, `Ctrl-B` |

Half-page scrolls (`Ctrl-D` down, `Ctrl-U` up) keep more context. Full-page scrolls
(`Ctrl-F` forward, `Ctrl-B` backward) move faster. When to use each. These work with
counts: `5Ctrl-D` scrolls 5 half-pages.

### 8.2 Centering the Cursor

| | |
|---|---|
| **Videos** | 090 |
| **Keys** | `zz`, `zt`, `zb` |

Scroll so the cursor line is at the center (`zz`), top (`zt`), or bottom (`zb`) of the
screen. Use `zz` constantly — it keeps your focus area centered and visible.

---

## Chapter 9 — More Motions

_Beyond words and lines: sentences, paragraphs, brackets, and screen positions._

### 9.1 Sentence and Paragraph Motions

| | |
|---|---|
| **Videos** | 091, 092 |
| **Keys** | `)`, `(`, `}`, `{` |

Navigate by sentences and paragraphs — larger jumps for prose and code. `}` jumps to the
next blank line (paragraph boundary), which in code means jumping between functions or
blocks. These work as motions with operators: `d}` deletes to the next paragraph.

### 9.2 Matching Bracket

| | |
|---|---|
| **Videos** | 093 |
| **Keys** | `%` |

Jump to the matching parenthesis, brace, or bracket. Essential for navigating nested code.
Works as a motion with operators: `d%` deletes from the cursor to the matching bracket,
inclusive.

### 9.3 Screen Position Jumps

| | |
|---|---|
| **Videos** | 094 |
| **Keys** | `H`, `M`, `L` |

`H` jumps to the highest visible line, `M` to the middle, `L` to the lowest. Quick jumps
within the current viewport without scrolling.

### 9.4 Line Start Motions and WORD Motions

| | |
|---|---|
| **Videos** | 095, 096 |
| **Keys** | `+`, `-`, `Enter`, `W`, `B`, `E`, `gE` |

`+` and `Enter` jump to the first non-blank of the next line, `-` to the previous. WORD
motions (`W`, `B`, `E`, `gE`) navigate by whitespace-delimited WORDs — coarser than word
motions, useful when text has lots of punctuation.

---

## Chapter 10 — Marks and the Jump List

_Leave breadcrumbs and retrace your steps._

### 10.1 Setting and Jumping to Marks

| | |
|---|---|
| **Videos** | 097, 098, 099, 100 |
| **Keys** | `m{a-z}`, `'{a-z}`, `` `{a-z} ``, `m{A-Z}` |

Set a mark with `m` + any letter. Jump to the mark's line with `'` or exact position with
`` ` ``. Lowercase marks are local to the buffer, uppercase marks are global (cross-file).
Marks are your personal bookmarks within and across files.

### 10.2 Special Marks

| | |
|---|---|
| **Videos** | 101 |
| **Keys** | `''`, ` `` `, `'.`, `'^` |

Automatic marks: `''` or ` `` ` returns to where you were before the last jump. `'.` jumps
to the last change. `'^` jumps to where you last left insert mode. These are free —
Vim maintains them automatically.

### 10.3 The Jump List

| | |
|---|---|
| **Videos** | 102, 103, 104 |
| **Keys** | `Ctrl-O`, `Ctrl-I`, `Tab` |

Every big jump (search, `G`, `%`, marks, etc.) gets recorded in the jump list. `Ctrl-O` goes
back, `Ctrl-I` (or `Tab`) goes forward. It's like browser back/forward for your cursor.

---

## Chapter 11 — Replace, Indent, Case, and Join

_Transform text without the full delete-insert cycle._

### 11.1 Replace Mode

| | |
|---|---|
| **Videos** | 105, 106 |
| **Keys** | `R`, `r{char}` |

`R` enters replace mode — overtype existing characters until Escape. `r{char}` replaces
a single character without entering insert mode. Replace mode is rare but perfect when you
need to overwrite fixed-width text.

### 11.2 Indenting and Formatting

| | |
|---|---|
| **Videos** | 107, 108, 109, 110, 111 |
| **Keys** | `>>`, `<<`, `>{motion}`, `={motion}`, `==` |

Indent with `>>`, unindent with `<<`. Works with motions: `>ip` indents a paragraph, `=ip`
auto-indents it. Visual mode indenting: select lines, press `>` or `<`. These are operators
— they follow the same grammar.

### 11.3 Case Changing

| | |
|---|---|
| **Videos** | 112, 113, 114, 115, 116 |
| **Keys** | `~`, `gU{motion}`, `gu{motion}`, `g~{motion}`, `U`/`u`/`~` in visual |

Toggle case with `~`, uppercase a motion with `gU`, lowercase with `gu`, toggle with `g~`.
In visual mode: `U` uppercases, `u` lowercases, `~` toggles. `gUiw` uppercases a word —
grammar at work again.

### 11.4 Joining Lines

| | |
|---|---|
| **Videos** | 117, 118 |
| **Keys** | `J`, `gJ` |

`J` joins the current line with the next (inserts a space). `gJ` joins without adding a
space. Works with counts: `3J` joins three lines. Handy for reflowing text or collapsing
multi-line statements.

---

## Chapter 12 — Registers

_Where your text goes when you yank or delete — and how to control it._

### 12.1 Understanding Registers

| | |
|---|---|
| **Videos** | 119, 121, 125 |
| **Keys** | `"a`–`"z`, `""`, `:reg` |

Every yank or delete goes into a register. The unnamed register (`""`) is the default. Named
registers (`"a`–`"z`) let you store multiple clips. `"ayy` yanks a line into register `a`.
`"ap` pastes from register `a`. View all registers with `:reg`.

### 12.2 Append to Registers

| | |
|---|---|
| **Videos** | 120 |
| **Keys** | `"A`–`"Z` |

Uppercase letter appends to the register instead of replacing. `"Ayy` adds a line to
whatever is already in register `a`. Great for collecting lines from different parts of a
file.

### 12.3 Numbered and Special Registers

| | |
|---|---|
| **Videos** | 122, 123, 124 |
| **Keys** | `"+`, `"*`, `"-`, `"0`–`"9` |

The system clipboard (`"+`, `"*`), the small delete register (`"-`), and the numbered
registers (`"0` = last yank, `"1`–`"9` = last 9 deletes in order). Understanding the
numbered registers demystifies why `p` sometimes pastes something unexpected.

### 12.4 Registers and Macros — The Connection

| | |
|---|---|
| **Videos** | — (book-only deep dive) |
| **Keys** | `"ap`, `"ayy`, `qa`, `@a` |

Macros are just register contents. Record a macro into `a`, then paste from `"a` — you'll
see the keystrokes as text. Edit that text, yank it back into `"a` — now you've edited a
macro without re-recording it. This connection between registers and macros is one of Vim's
most elegant design decisions.

---

## Chapter 13 — Macros

_Record, replay, and compose automated editing sequences._

### 13.1 Recording and Playing Macros

| | |
|---|---|
| **Videos** | 126, 127, 128, 129 |
| **Keys** | `q{a-z}`, `q`, `@{a-z}`, `@@` |

`qa` starts recording into register `a`. `q` stops recording. `@a` plays it back. `@@`
repeats the last macro. A macro is just a sequence of normal mode commands stored as text
in a register.

### 13.2 Counted Macros and Patterns

| | |
|---|---|
| **Videos** | 130 |
| **Keys** | `100@a` |

`100@a` runs the macro 100 times — but stops on the first error. This is the "run until it
fails" pattern: make your macro operate on one unit (one line, one match), then throw a big
count at it. It'll process everything and stop cleanly.

---

## Chapter 14 — Windows and Splits

_Work with multiple views of your files._

### 14.1 Creating Splits

| | |
|---|---|
| **Videos** | 131, 132 |
| **Keys** | `Ctrl-W s`, `Ctrl-W v`, `:sp`, `:vs` |

Horizontal split (`Ctrl-W s`), vertical split (`Ctrl-W v`). View the same file in two
places, or open different files side by side.

### 14.2 Navigating and Closing Windows

| | |
|---|---|
| **Videos** | 133, 134, 135 |
| **Keys** | `Ctrl-W h/j/k/l`, `Ctrl-W c`, `Ctrl-W o` |

Move between windows with `Ctrl-W` + direction. Close the current window with `Ctrl-W c`.
Close all others with `Ctrl-W o`. The `Ctrl-W` prefix is a whole keyboard of window commands
(deep dive in a later chapter).

---

## Chapter 15 — Walking the Keyboard: Lowercase

_Every lowercase key in normal mode, one at a time._

| | |
|---|---|
| **Videos** | 136–161 |
| **Keys** | `a`–`z` (all 26) |

Reference-style chapter. Each key gets a short entry: what it does, a one-line example,
cross-reference to the chapter where it was taught in depth. Presented as a visual keyboard
map with entries. This chapter serves as both review and reference.

Keys: `a` append, `b` back, `c` change, `d` delete, `e` end, `f` find, `g` prefix,
`h` left, `i` insert, `j` down, `k` up, `l` right, `m` mark, `n` next, `o` open, `p` put,
`q` record, `r` replace, `s` substitute, `t` till, `u` undo, `v` visual, `w` word,
`x` delete char, `y` yank, `z` prefix.

---

## Chapter 16 — Walking the Keyboard: Uppercase

_The shifted keys — less common but equally important._

| | |
|---|---|
| **Videos** | 162–187 |
| **Keys** | `A`–`Z`, `ZZ`, `ZQ` |

Same reference format. Uppercase keys are often the "bigger" or "opposite" version of their
lowercase counterpart: `A` (append at end) vs `a` (append after cursor), `D` (delete to end)
vs `dd` (delete line), `F` (find backward) vs `f` (find forward).

---

## Chapter 17 — Walking the Keyboard: Symbols and Numbers

_Every symbol key and number key in normal mode._

| | |
|---|---|
| **Videos** | 188–218 |
| **Keys** | `0`–`9`, `^`, `$`, `%`, `~`, `` ` ``, `'`, `!`, `@`, `#`, `*`, `&`, `(`, `)`, `{`, `}`, `[`, `]`, `-`, `+`, `_`, `=`, `<`, `>`, `\|`, `\`, `:`, `;`, `,`, `"`, `.`, `/`, `?`, `Space`, `BS` |

Reference-style entries for each. Symbols are where a lot of Vim's power hides: `%` for
matching brackets, `*` for word search, `.` for repeat, `;` for repeat-find, `"` for
register prefix, etc.

---

## Chapter 18 — Walking the Keyboard: Ctrl Keys

_Control-key commands in normal mode._

| | |
|---|---|
| **Videos** | 219–248 |
| **Keys** | `Ctrl-A`, `Ctrl-X`, `Ctrl-B`, `Ctrl-F`, `Ctrl-U`, `Ctrl-D`, `Ctrl-E`, `Ctrl-Y`, `Ctrl-O`, `Ctrl-I`, `Ctrl-R`, `Ctrl-G`, `Ctrl-L`, `Ctrl-V`, `Ctrl-C`, `Ctrl-Z`, `Ctrl-]`, `Ctrl-T`, `Ctrl-^`, `Ctrl-W`, `Ctrl-N`, `Ctrl-P`, `Ctrl-H`, `Ctrl-J`, `Ctrl-M` |

Plus the `z` scroll refinements (`zz`, `zt`, `zb`, `z.`, `z+`, `z-`). Reference-style
entries. Ctrl keys are the least-used layer but include essential commands like `Ctrl-O`/`Ctrl-I`
(jump list), `Ctrl-R` (redo), and `Ctrl-A`/`Ctrl-X` (increment/decrement).

---

## Chapter 19 — The `g` Commands

_A second keyboard hidden behind the `g` prefix._

| | |
|---|---|
| **Videos** | 249–285 |
| **Keys** | `ga`, `gd`, `gD`, `ge`, `gE`, `gf`, `gF`, `gg`, `gj`, `gk`, `gm`, `gM`, `gn`, `gN`, `go`, `gp`, `gP`, `gq`, `gw`, `gr`, `gs`, `gt`, `gT`, `gu`, `gU`, `g~`, `gv`, `gx`, `gH`, `gh`, `gI`, `gi`, `gJ`, `gQ`, `gR`, `gV`, `g*`, `g#`, `g$`, `g0`, `g^`, `g&`, `g;`, `g,`, `g?`, `g@`, `g<` |

The `g` prefix opens up a second entire alphabet of commands. Highlights: `gd` (go to
definition), `gf` (go to file), `gq` (format), `gv` (reselect), `gi` (insert at last insert
position), `g;`/`g,` (navigate the change list). Reference-style with examples.

---

## Chapter 20 — The `z` Commands

_Scrolling, folding, and spelling — all under `z`._

| | |
|---|---|
| **Videos** | 286–316 |
| **Keys** | `zz`, `zt`, `zb`, `zo`, `zc`, `za`, `zO`, `zC`, `zA`, `zv`, `zr`, `zm`, `zR`, `zM`, `zf`, `zd`, `zn`, `zN`, `zi`, `z=`, `zg`, `zw`, etc. |

Three families: scrolling (`zz`, `zt`, `zb`, `zs`, `ze`, `zh`, `zl`), folding (`zo`, `zc`,
`za`, `zr`, `zm`, `zR`, `zM`, `zf`, `zd`, etc.), and spelling (`z=`, `zg`, `zw`). Folding
gets a proper tutorial — how to create, open, close, and navigate folds.

---

## Chapter 21 — Bracket Commands and `Ctrl-W` Window Commands

_Navigation within code structures and advanced window management._

### 21.1 Bracket Commands

| | |
|---|---|
| **Videos** | 317–333 |
| **Keys** | `[(`, `])`, `[{`, `]}`, `[[`, `]]`, `[m`, `]m`, `[c`, `]c`, `[s`, `]s`, `[p`, `]p`, etc. |

Navigate by unmatched brackets, function boundaries, diff changes, misspelled words, and
more. The `[`/`]` prefix provides structural navigation — jumping by code constructs rather
than raw text.

### 21.2 Window Commands in Depth

| | |
|---|---|
| **Videos** | 334–365 |
| **Keys** | `Ctrl-W s`, `Ctrl-W v`, `Ctrl-W n`, `Ctrl-W h/j/k/l`, `Ctrl-W w`, `Ctrl-W c`, `Ctrl-W o`, `Ctrl-W H/J/K/L`, `Ctrl-W r`, `Ctrl-W x`, `Ctrl-W T`, `Ctrl-W +/-`, `Ctrl-W >/<`, `Ctrl-W =`, `Ctrl-W _`, `Ctrl-W \|`, `Ctrl-W d`, `Ctrl-W f`, `Ctrl-W ]`, `Ctrl-W gt`, `Ctrl-W ^` |

Complete reference for window management: creating, navigating, closing, moving, resizing,
and split-and-jump commands. Tab management via `Ctrl-W g` prefix. This is a reference
section — most readers will use a handful of these daily and look up the rest as needed.

---

## Chapter 22 — Insert Mode

_Keys that work while you're typing — more powerful than you think._

| | |
|---|---|
| **Videos** | 366–395 |
| **Keys** | `Esc`, `Ctrl-[`, `Ctrl-C`, `Ctrl-O`, `Ctrl-H`, `Ctrl-W`, `Ctrl-U`, `Ctrl-T`, `Ctrl-D`, `Ctrl-R`, `Ctrl-A`, `Ctrl-@`, `Ctrl-E`, `Ctrl-Y`, `Ctrl-N`, `Ctrl-P`, `Ctrl-K`, `Ctrl-V`, `Ctrl-G u`, `Ctrl-X Ctrl-L/F/K/T/I/D/]/O/S/V` |

Insert mode isn't just "type text." You can delete words (`Ctrl-W`), delete to start of
line (`Ctrl-U`), paste from registers (`Ctrl-R`), copy from adjacent lines (`Ctrl-E`,
`Ctrl-Y`), autocomplete (`Ctrl-N`, `Ctrl-P`), execute one normal-mode command (`Ctrl-O`),
and use the `Ctrl-X` completion sub-menu. Understanding insert mode makes you faster even
while typing.

---

## Chapter 23 — Ex Commands

_The colon commands you'll use every day._

### 23.1 File Operations

| | |
|---|---|
| **Videos** | 396–404 |
| **Keys** | `:w`, `:q`, `:wq`, `:x`, `:e`, `:e!`, `:r`, `:r!` |

Saving, quitting, opening files, reverting, reading in file contents or command output.

### 23.2 Search and Replace

| | |
|---|---|
| **Videos** | 405–409 |
| **Keys** | `:s/old/new/`, `:%s/old/new/g`, `:%s/old/new/gc` |

Substitution on the current line, the whole file, with confirmation. Ranges and visual
selection. Regex in substitution patterns.

### 23.3 Buffers, Tabs, and Arguments

| | |
|---|---|
| **Videos** | 410–418 |
| **Keys** | `:ls`, `:b`, `:bn`, `:bp`, `:bd`, `:tabnew`, `:tabnext`, `:tabclose` |

Managing multiple files: buffers (Vim's "open files"), tabs (viewport containers), and the
argument list. When to use buffers vs tabs vs splits.

### 23.4 Shell Commands and Settings

| | |
|---|---|
| **Videos** | 419–430 |
| **Keys** | `:!`, `:!!`, `:%!sort`, `:terminal`, `:set`, `:noh` |

Running external commands, filtering text through shell programs, the built-in terminal.
Essential settings: `number`, `relativenumber`, `hlsearch`, `incsearch`, `ignorecase`,
`smartcase`, `wrap`, `list`.

---

## Chapter 24 — Visual Mode in Depth

_Advanced visual mode techniques and block editing._

| | |
|---|---|
| **Videos** | 431–445 |
| **Keys** | `v`, `V`, `Ctrl-V`, `o`, `O`, `gv`, `I`, `A`, `r`, `J`, `u`, `U`, `~`, `>`, `<`, `=`, `:'<,'>` |

Deep dive into all three visual modes. Block insert (`Ctrl-V` → `I`) and block append
(`Ctrl-V` → `A`) for multi-line editing. Case operations on selections. The automatic
`'<,'>` range on the command line after visual selection. Block visual mode is Vim's answer
to multi-cursor editing.

---

## Chapter 25 — Command-Line Mode Tips

_Power user techniques for the colon prompt._

| | |
|---|---|
| **Videos** | 446–460 |
| **Keys** | `q:`, `q/`, `q?`, `@:`, `:norm`, `:g`, `:v`, `Ctrl-R`, `Ctrl-R Ctrl-W`, `Ctrl-F` |

The command history window (`q:`), the global command (`:g/{pattern}/{cmd}`), the inverse
global (`:v`), normal mode on lines (`:norm`), repeating the last Ex command (`@:`), and
editing the command line in a buffer (`Ctrl-F`). These are power-user techniques that
transform Ex commands from one-off actions into batch operations.

---

## Chapter 26 — Practical Patterns and Tricks

_Real-world editing recipes that combine everything you've learned._

| | |
|---|---|
| **Videos** | 461–480 |
| **Keys** | `xp`, `ddp`, `yyp`, `*cwNew<Esc>n.`, `:%norm I//`, `Ctrl-V I//Esc`, `Ctrl-A`, `Ctrl-X`, `g Ctrl-A`, `cgn`, `"1p...`, `do`, `dp`, `!ip sort` |

Transpose characters (`xp`), swap lines (`ddp`), duplicate lines (`yyp`), star-dot pattern,
block commenting, increment/decrement, `cgn` + dot, numbered register paste trick, diff
commands, external filtering. These patterns demonstrate how Vim's composable grammar lets
you solve real editing problems in seconds.

---

## Chapter 27 — Advanced Topics

_Under the hood: undo trees, special registers, operators, and configuration._

### 27.1 The Undo Tree

| | |
|---|---|
| **Videos** | 481, 482 |
| **Keys** | `g-`, `g+`, `:earlier`, `:later` |

Vim's undo is a tree, not a stack. Every branch is preserved. `g-` and `g+` navigate
chronologically. `:earlier 5m` goes back 5 minutes. `:later 10s` goes forward 10 seconds.
You literally cannot lose work in Vim.

### 27.2 Special Registers

| | |
|---|---|
| **Videos** | 483–488 |
| **Keys** | `".`, `":`, `"/`, `"%`, `"#`, `"=` |

The last-inserted-text register (`.`), the last Ex command (`:`), the last search pattern
(`/`), the current filename (`%`), the alternate filename (`#`), and the expression register
(`=`). The expression register is the wildest — it evaluates an expression and inserts the
result.

### 27.3 Operator-Pending Mode and Custom Operators

| | |
|---|---|
| **Videos** | 489, 490 |
| **Keys** | `g@{motion}` |

What happens between pressing an operator and a motion. How to create custom operators with
`operatorfunc`. Understanding this mode deepens your grasp of Vim's grammar.

### 27.4 Terminal Mode, Character Info, and Miscellany

| | |
|---|---|
| **Videos** | 491–497 |
| **Keys** | `:term`, `Ctrl-\ Ctrl-N`, `ga`, `g8`, `gx`, `g<` |

Terminal mode and how to escape it. Character inspection (`ga`, `g8`). Opening URLs (`gx`).
Previous command output (`g<`).

### 27.5 Folding in Practice

| | |
|---|---|
| **Videos** | 493, 494, 495 |
| **Keys** | `:set fdm=indent`, `:set fdm=syntax`, `:mkview`, `:loadview` |

Setting up fold methods (indent, syntax, marker, manual). Saving and restoring fold state.
Practical folding workflows for different file types.

### 27.6 Configuration and What's Next

| | |
|---|---|
| **Videos** | 498, 499, 500 |
| **Keys** | `:help`, `vimrc`, `init.lua` |

Where to put your personal configuration. How to navigate Vim's built-in help (it's
excellent). Where to go from here: plugins (surround, commentary, fugitive), LSP,
Treesitter, and the endless journey of Vim mastery.

---

## Appendices

### Appendix A — Synonym Reference

Keys that do the same thing. Quick lookup table: `h`=`Ctrl-H`=`BS`=`←`, `C`=`c$`,
`D`=`d$`, `S`=`cc`, etc.

| **Videos** | — (curriculum Appendix A) |

### Appendix B — The Vim Grammar Matrix

Full matrix: operators down the left, motions/text objects across the top. Every cell is a
valid command. Poster-worthy reference. Include the formal grammar:
`[count] [register] operator [count] motion/text-object`.

| **Videos** | 085, — (curriculum Appendix B) |

### Appendix C — Suggested Learning Path

Day-by-day guide. 120-day plan from zero to fluency. What to learn each week, when to go
cold turkey, when to add new commands.

| **Videos** | — (curriculum Appendix C) |

### Appendix D — Surround Plugin

`ys`, `cs`, `ds`, `S` in visual mode. The most universally useful Vim plugin. Works in
VS Code, IdeaVim, and standalone Vim/Neovim with a plugin.

| **Videos** | — (curriculum Appendix D, potentially future video series) |

### Appendix E — Motion Classification

Exclusive vs. inclusive vs. linewise motions. Why `dw` and `de` behave differently. Technical
reference for when commands behave unexpectedly.

| **Videos** | — (curriculum Appendix E excerpt) |

### Appendix F — Vim in Other Editors

Detailed setup guides for using Vim keybindings in: VS Code, JetBrains IDEs, Visual Studio,
Sublime Text, Emacs (Evil mode). What works, what doesn't, what's different. This appendix
makes the book useful even for readers who will never open Vim or Neovim.

| **Videos** | — (book-only) |

### Appendix G — Complete Key Reference

Alphabetical index of every key covered in the book. For each key: what it does, what chapter
covers it, what video demonstrates it. The ultimate lookup table.

| **Videos** | All |

---

## Chapter / Video Cross-Reference

| Chapter | Title | Videos |
|---------|-------|--------|
| 1 | Why Vim? | 001, 003, 015 |
| 2 | Survival | 002, 004–015 |
| 3 | Basic Editing | 016–045 |
| 4 | Search and Find | 046–057 |
| 5 | Counts, Positions, and Visual Mode | 058–070 |
| 6 | The Dot Command | 071–073 |
| 7 | Text Objects | 074–085 |
| 8 | Scrolling and Screen Position | 086–090 |
| 9 | More Motions | 091–096 |
| 10 | Marks and the Jump List | 097–104 |
| 11 | Replace, Indent, Case, and Join | 105–118 |
| 12 | Registers | 119–125 |
| 13 | Macros | 126–130 |
| 14 | Windows and Splits | 131–135 |
| 15 | Walking the Keyboard: Lowercase | 136–161 |
| 16 | Walking the Keyboard: Uppercase | 162–187 |
| 17 | Walking the Keyboard: Symbols & Numbers | 188–218 |
| 18 | Walking the Keyboard: Ctrl Keys | 219–248 |
| 19 | The `g` Commands | 249–285 |
| 20 | The `z` Commands | 286–316 |
| 21 | Bracket & Window Commands | 317–365 |
| 22 | Insert Mode | 366–395 |
| 23 | Ex Commands | 396–430 |
| 24 | Visual Mode in Depth | 431–445 |
| 25 | Command-Line Mode Tips | 446–460 |
| 26 | Practical Patterns and Tricks | 461–480 |
| 27 | Advanced Topics | 481–500 |
| App. A | Synonym Reference | — |
| App. B | Vim Grammar Matrix | 085 |
| App. C | Learning Path | — |
| App. D | Surround Plugin | — |
| App. E | Motion Classification | — |
| App. F | Vim in Other Editors | — |
| App. G | Complete Key Reference | All |
