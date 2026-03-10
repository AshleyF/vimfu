# Vim Behavioral Specification

A precise, implementation-independent description of Vim's behavior. Every rule
here should hold true in Neovim and serve as a source of truth for any Vim
implementation. Features not yet implemented in the VimFu simulator are noted
inline.

This document describes the *what*, not the *how*. No code, no data structures,
no implementation strategy — only observable behavior expressed in plain English,
detailed enough to write a correct implementation from scratch.

---

## Table of Contents

1. [Concepts](#1-concepts)
2. [Modes](#2-modes)
3. [Cursor](#3-cursor)
4. [Registers](#4-registers)
5. [Counts](#5-counts)
6. [Motions](#6-motions)
7. [Operators](#7-operators)
8. [Operator–Motion Interaction](#8-operatormotion-interaction)
9. [Text Objects](#9-text-objects)
10. [Editing Commands](#10-editing-commands)
11. [Insert Mode](#11-insert-mode)
12. [Replace Mode](#12-replace-mode)
13. [Visual Mode](#13-visual-mode)
14. [Search](#14-search)
15. [Marks](#15-marks)
16. [Jump List](#16-jump-list)
17. [Change List](#17-change-list)
18. [Undo and Redo](#18-undo-and-redo)
19. [Dot Repeat](#19-dot-repeat)
20. [Macros](#20-macros)
21. [Put (Paste)](#21-put-paste)
22. [Surround (nvim-surround)](#22-surround-nvim-surround)
23. [Scroll](#23-scroll)
24. [Command Mode (Ex Commands)](#24-command-mode-ex-commands)
25. [Settings](#25-settings)
26. [Messages and Prompts](#26-messages-and-prompts)

---

## 1. Concepts

### 1.1 Buffer

A buffer is an ordered list of lines. Each line is a string of characters. A
buffer always contains at least one line; deleting the last remaining content
leaves a single empty line.

### 1.2 Word vs WORD

A **word** is a maximal sequence of word-characters, or a maximal sequence of
non-word non-whitespace characters. Word-characters are letters, digits, and
underscore. Punctuation such as `.`, `-`, `,`, `:`, `(`, `)` forms its own
word.

A **WORD** is a maximal sequence of non-whitespace characters. Only whitespace
(space, tab, newline) separates WORDs. Under this definition `hello-world.foo`
is a single WORD.

An empty line is a word/WORD boundary.

### 1.3 Whitespace and Blank Lines

A blank line is a line that contains no characters at all (length zero). A line
containing only spaces or tabs is not blank — it is a whitespace-only line. This
distinction matters for paragraph motions: only truly blank lines are paragraph
boundaries.

### 1.4 Inclusive vs Exclusive Motions

Every motion is classified as inclusive or exclusive. An inclusive motion includes
the character at the endpoint in the operated range. An exclusive motion excludes
it.

### 1.5 Linewise vs Charwise

Operations on text are either linewise (whole lines) or charwise (arbitrary
character ranges). The distinction affects cursor placement after the operation
and how registers store text.

### 1.6 Sticky Column (Desired Column)

When moving vertically with `j` or `k`, the cursor tries to reach the column it
was at before the first vertical move (the "desired column"). If the target line
is shorter, the cursor lands on the last character. If a subsequent line is long
enough, the cursor returns to the desired column. Horizontal movement resets the
desired column to the current position. The `$` motion sets the desired column
to infinity (always goes to end of line until the next horizontal movement).

---

## 2. Modes

### 2.1 Normal Mode

The default mode. Keystrokes are interpreted as commands. The cursor is a block
covering one character. In normal mode the cursor cannot be positioned past the
last character of a line (it sits *on* the last character, not after it). On an
empty line the cursor is at column 0.

### 2.2 Insert Mode

Entered from normal mode via `i`, `I`, `a`, `A`, `o`, `O`, `s`, `S`, `c`
operations, `gi`, or `gI`. Characters typed are inserted into the buffer. The
cursor is a thin beam positioned between characters and may rest one position
past the end of a line (the append position). Exiting insert mode moves the
cursor one position to the left unless already at column 0.

### 2.3 Replace Mode

Entered via `R` from normal mode. Characters typed overwrite existing characters
rather than inserting. The cursor is a block. Overwriting past the end of a line
appends characters. Exiting replace mode moves the cursor one position left
unless at column 0.

### 2.4 Visual Mode (Charwise)

Entered via `v` from normal mode. A selection range extends from an anchor point
to the cursor. The selection is charwise. All normal-mode motions work and
extend the selection.

### 2.5 Visual Line Mode

Entered via `V` from normal mode. The selection always covers full lines from
the anchor line to the cursor line. Motions extend the line range.

### 2.6 Command Mode

Entered via `:`, `/`, or `?` from normal mode. A command line appears at the
bottom of the screen. Characters typed are appended to the command. Enter
executes, Escape cancels.

---

## 3. Cursor

### 3.1 Position Rules

In normal mode the cursor column is clamped to 0..max(0, lineLength-1). In
insert and replace modes the cursor column can be 0..lineLength. On an empty
line the cursor is always at column 0 regardless of mode.

### 3.2 Cursor After Escape

Returning to normal mode from insert or replace moves the cursor one column to
the left, unless the cursor is already at column 0.

### 3.3 Virtual Column and Tab Handling

Tabs occupy multiple screen columns. The tab stop interval is 8 by default. A
tab at screen column 0 spans columns 0–7. A tab at screen column 5 spans
columns 5–7. Motions and column displays use the virtual (screen) column for
positioning. The `|` motion uses 1-based virtual columns.

---

## 4. Registers

### 4.1 Unnamed Register (`""`)

Every delete, change, or yank updates the unnamed register. It always holds the
text of the last such operation plus a type flag: `line` (from linewise ops like
`dd`, `yy`) or `char` (from charwise ops like `dw`, `yw`, `x`).

Importantly, even a single-character `x` overwrites the unnamed register, and it
may change the register type. If the unnamed register held a linewise yank from
`yy`, then `x` makes it charwise containing that one deleted character.

### 4.2 Named Registers (`"a`–`"z`)

A named register is selected by typing `"` followed by a letter before the next
operator or put command. The selected register receives a copy of the text (in
addition to the unnamed register). The register selection is consumed after one
operation.

Named registers are never implicitly overwritten — they change only when
explicitly selected.

### 4.3 Uppercase Registers (`"A`–`"Z`)

Selecting a register with an uppercase letter **appends** to the existing
content of the corresponding lowercase register rather than replacing it.

### 4.4 Numbered Registers (`"0`–`"9`)

Register `"0` holds the text of the most recent yank (not delete). Registers
`"1`–`"9` hold the last nine deletes/changes, with `"1` being the most recent,
shifting older entries down.

### 4.5 Small Delete Register (`"-`)

Deletes of less than one line that do not specify a register go into the small
delete register.

### 4.6 Clipboard Registers (`"+` and `"*`)

The system clipboard registers. When yanking or pasting to/from these, the
system clipboard is accessed. (Wired to a callback for
clipboard access but not universally available.)

### 4.7 Last Search Register (`"/`)

Contains the most recent search pattern.

### 4.8 Expression Register (`"=`)

Prompts for an expression to evaluate. Not implemented (reads as empty).

### 4.9 Black Hole Register (`"_`)

Discards the text — nothing is stored.

### 4.10 Register Type

Every register stores both its text content and a type: `line` or `char`. The
type is determined by the operation that wrote the register. Linewise operations
(`dd`, `yy`, `dj`, `d{`, visual-line delete, etc.) store as `line`. Charwise
operations (`dw`, `yw`, `x`, `d$`, visual-char delete, etc.) store as `char`.
The type governs how `p` and `P` behave (see [Put](#21-put-paste)).

---

## 5. Counts

### 5.1 Count Prefix

Most commands accept a numeric count prefix. Digits `1`–`9` start a count; `0`
continues one that has already started (since `0` alone is the start-of-line
motion). If no count is given, the default is 1.

### 5.2 Count with Operators

When an operator has a count and the following motion also has a count, the
counts multiply. `2d3w` deletes 6 words.

### 5.3 Count with Insert

`3i` enters insert mode; when Escape is pressed, the text typed during that
insert session is repeated 2 more times (total 3 copies). This includes
newlines and editing keys like Ctrl-W and Ctrl-U, which are replayed faithfully.

---

## 6. Motions

### 6.1 Character Motions

**`h`** (or left arrow): Move left one character. Stops at column 0. With count,
repeats. Never wraps to the previous line.

**`l`** (or right arrow): Move right one character. Stops at the last character
in normal mode (one past in insert). Never wraps to the next line.

**`Backspace`**: Move left one character. Unlike `h`, wraps to the end of the
previous line when at column 0.

**`Space`**: Move right one character. Unlike `l`, wraps to the start of the
next line when at the last character.

### 6.2 Line Motions (j/k)

**`j`** (or down arrow): Move down one line, preserving the desired column. If
the target line is shorter, the cursor lands on the last character. The desired
column is not reset.

**`k`** (or up arrow): Move up one line, same column-preserving logic as `j`.

### 6.3 Word Motions

**`w`**: Move forward to the start of the next word. From a word-character
sequence, skip past it, then skip whitespace. From punctuation, skip past the
punctuation, then skip whitespace. An empty line is a word boundary — the cursor
stops on it. With count, repeats. At the last word of the buffer, moves to the
last character.

**`W`**: Like `w` but only whitespace separates WORDs.

**`b`**: Move backward to the start of the previous word. From the start of a
word, skip whitespace backward, then scan backward through the word. Empty lines
are word boundaries. At the first word of the buffer, goes to column 0.

**`B`**: Like `b` but for WORDs.

**`e`**: Move forward to the end of the current or next word. Inclusive motion.
Skips forward one character, then skips whitespace, then moves to the end of the
word. Empty lines are boundaries.

**`E`**: Like `e` but for WORDs. Inclusive.

**`ge`**: Move backward to the end of the previous word. From inside a word,
move back to the end of the preceding word. Handles empty lines as boundaries.

**`gE`**: Like `ge` but for WORDs.

### 6.4 Line Position Motions

**`0`**: Go to column 0 (absolute start of line).

**`^`**: Go to the first non-whitespace character on the line. On an
all-whitespace line, goes to the last character.

**`$`**: Go to the last character of the line. Inclusive motion. With count N
greater than 1, moves down N-1 lines first, then to end of that line.

**`g_`**: Go to the last non-whitespace character on the line.

**`_`**: Go to the first non-whitespace character, count-1 lines down. `1_` is
the current line. Linewise when used with an operator.

**`|`**: Go to screen column N (1-based, using virtual/screen columns). If the
line is shorter than N, goes to the last character.

### 6.5 Line Navigation Motions

**`+`** (or `Enter`): Go to the first non-blank of the next line. With count,
moves N lines down.

**`-`**: Go to the first non-blank of the previous line. With count, moves N
lines up.

**`G`**: Go to line N (1-based). Without count, goes to the last line of the
buffer. Cursor lands on the first non-blank. Linewise when used with an
operator. Adds a jump list entry.

**`gg`**: Go to line N. Without count, goes to line 1. Same cursor placement
and operator behavior as `G`. Adds a jump list entry.

**`H`**: Go to the first non-blank of the line at the top of the visible screen.
With count N, goes to the Nth line from the top. When used with operators, the
motion is linewise.

**`M`**: Go to the first non-blank of the middle line of the visible screen.
Linewise with operators.

**`L`**: Go to the first non-blank of the line at the bottom of the visible
screen. With count N, goes to the Nth line from the bottom. Linewise with
operators.

### 6.6 Find on Line (f/F/t/T)

**`f{char}`**: Move forward to the next occurrence of {char} on the current
line. Inclusive. Does not cross lines. Skips the character under the cursor. If
the character is not found, the cursor does not move. Tab can be used as the
target character. With count N, finds the Nth occurrence.

**`F{char}`**: Like `f` but searches backward. Inclusive.

**`t{char}`**: Move forward to one character before the next occurrence of
{char} on the current line. Exclusive. If the target character is immediately
adjacent (one position ahead), the cursor does not move. With count N, finds the
Nth occurrence.

**`T{char}`**: Like `t` but searches backward; lands one character after the
found character.

**`;`**: Repeat the last `f`, `F`, `t`, or `T` in the same direction.
Preserves the semantics of the original find (if the last find was `t`, the
semicolon uses `t` behavior). With count, repeats N times.

**`,`**: Repeat the last find in the reversed direction. `f` becomes `F`, `t`
becomes `T`, and vice versa.

Operators work with all find variants: `df.` deletes through the period, `ct:`
changes up to (not including) the colon, `yF"` yanks backward to a quote.
Every printable character and many punctuation characters work as targets,
including space, quote, backslash, pipe, tilde, and others.

### 6.7 Paragraph Motions

**`}`**: Move forward to the line after the current paragraph. A paragraph is a
block of non-blank lines. The cursor lands on the next blank line (or on the
last line of the buffer if there is no trailing blank line). Exclusive, linewise
motion. Important: whitespace-only lines (spaces, tabs) are NOT considered blank
for this purpose — only lines with length zero count as paragraph boundaries.

**`{`**: Move backward to the line before the current paragraph. Same blank-line
rules. Lands on the blank line before the paragraph (or line 0 if at the
beginning of the buffer).

Multiple consecutive blank lines: `}` lands on the first blank line of the
group. Successive `}` presses advance through each paragraph.

### 6.8 Sentence Motions

**`)`**: Move forward to the start of the next sentence. A sentence ends at
`.`, `!`, or `?` followed by optional closing characters (`"`, `'`, `)`, `]`)
and then whitespace or end-of-line. A blank line also starts a new sentence.

Important: a period not followed by whitespace does NOT end a sentence. In
`file.txt`, the period is part of the word. In `Dr.Smith`, the period does not
end a sentence. The pattern is strictly: sentence-ending punctuation, optional
closing characters, then one or more spaces or a newline.

**`(`**: Move backward to the start of the current or previous sentence. Same
rules.

### 6.9 Bracket Matching (%)

Without count: scan forward from the cursor for the first bracket character
(`(`, `)`, `{`, `}`, `[`, `]`) on the current line. Once found, jump to its
matching partner using depth-counting. If the cursor is already on a bracket,
use it directly.

- Handles nesting correctly.
- If no bracket is found on the line, or the bracket is unmatched, the cursor
  does not move.
- Inclusive motion.

With count N: jump to the line at N% of the file. `50%` goes to the middle of
the file, `100%` goes to the last line, etc. This is percentage-based line
jumping, not bracket matching.

### 6.10 Search Motions (n/N/\*/\#)

**`n`**: Jump to the next match of the current search pattern, in the original
search direction. Wraps around the end of the buffer. Adds a jump entry.

**`N`**: Jump to the next match in the reverse direction.

**`*`**: Search forward for the word under the cursor (whole-word match using
word boundaries). Sets the search pattern. Adds a jump entry. Works even when
the cursor is in the middle of the word.

**`#`**: Like `*` but searches backward.

---

## 7. Operators

An operator is a command that waits for a motion or text object and then
performs an action on the text between the cursor's starting position and the
endpoint of the motion.

### 7.1 Delete (`d`)

Removes the text in the operated range. Stores the deleted text in a register
(the unnamed register, or a named register if one was selected). After a
charwise delete, the cursor stays at the start of the deleted range. After a
linewise delete, the cursor goes to the first non-blank of the line that takes
the position of the first deleted line; if the deletion was at the end of the
buffer, the cursor moves up.

Line form `dd`: deletes count lines starting from the cursor line. On the last
line of the buffer, leaves a single empty line. On a single-line buffer, clears
the line.

### 7.2 Change (`c`)

Deletes the text in the operated range and enters insert mode. Charwise change
places the cursor at the start of the deleted range and enters insert mode
there. Linewise change on `cc` or `S` deletes the line content but preserves
the leading whitespace (indent) and places the cursor at the end of that indent
in insert mode.

Special: `cw` behaves like `ce` — it does not include trailing whitespace. This
is a deliberate Vim quirk maintained for historical compatibility. `dw` at the
end of a line does not cross to the next line.

Line form `cc`: same as `S`. Preserves indent.

### 7.3 Yank (`y`)

Copies the text in the operated range into a register without modifying the
buffer. After yank, the cursor returns to the position where the operator was
initiated (the start of the range), not the motion endpoint.

Line form `yy`: yanks count lines. Cursor does not move.

`Y` (capital): in Neovim, `Y` is equivalent to `y$` (yank to end of line,
charwise). Note: in classic Vi, `Y` was equivalent to `yy` (linewise). Neovim's
default mapping changed this.

### 7.4 Indent (`>`)

Shifts every line in the operated range one shiftwidth to the right by
prepending a tab (or equivalent spaces if expandtab is set). After indenting,
the cursor moves to the first non-blank of the first affected line.

Line form `>>`: indents count lines.

### 7.5 Dedent (`<`)

Removes one shiftwidth of leading whitespace from every line in the operated
range. If a line has less than one shiftwidth of indent, removes what is there.
Blank lines (empty) are not modified. After dedenting, the cursor moves to the
first non-blank of the first affected line.

Line form `<<`: dedents count lines.

### 7.6 Case Operators

**`gu`**: Lowercase all characters in the operated range.

**`gU`**: Uppercase all characters in the operated range.

**`g~`**: Toggle the case of all characters in the operated range.

Line forms: `guu`, `gUU`, `g~~` operate on count lines.

When used with vertical motions (`j`, `k`), these are linewise — `guj` changes
the case of two full lines.

---

## 8. Operator–Motion Interaction

### 8.1 Inclusive vs Exclusive

When an operator acts on the range defined by a motion:
- For an **inclusive** motion, the character at the endpoint is included.
- For an **exclusive** motion, the character at the endpoint is excluded.

### 8.2 Exclusive-to-Inclusive Adjustment

When an exclusive motion ends at column 0 (the very start of a line), and the
range is not empty, the endpoint is adjusted backward to the end of the
previous line. This makes `d}` include the last line of the paragraph rather
than leaving it.

### 8.3 Linewise Promotion

If after the exclusive-to-inclusive adjustment, the range starts at column 0 of
one line and ends at the last character of another line, and the range covers
full lines, the operation is promoted to linewise. This is the mechanism by
which `d}` becomes a linewise delete rather than a charwise one.

### 8.4 Backward Motions

If the motion moves the cursor backward (the endpoint is before the start
position), the range is simply reversed so that the operator processes from the
earlier position to the later one. The behavior of the operator itself is
unchanged.

### 8.5 Line Form Operators (dd, cc, yy, >>, <<)

When an operator key is pressed twice, it operates on count lines starting from
the cursor line. If the cursor is on the last line and count is greater than 1,
the operation is a no-op (nothing happens). This matches Neovim behavior.

### 8.6 Operator with Search

`d/pattern<Enter>` deletes from the cursor to the search match. The search
motion is exclusive. If the pattern is not found, the operation is cancelled and
an error message is shown.

---

## 9. Text Objects

Text objects define regions of text and are used with operators (`d`, `c`, `y`,
etc.) or to extend visual selections. They come in inner (`i`) and around (`a`)
variants.

### 9.1 Word Objects (iw, aw, iW, aW)

**`iw`**: Select the word under the cursor. If the cursor is on whitespace
between words, selects the whitespace run. If the cursor is on punctuation,
selects the punctuation run.

**`aw`**: Select the word under the cursor plus adjacent whitespace. If the word
has trailing whitespace, that whitespace is included. If the word is at the end
of a line (no trailing whitespace), leading whitespace is included instead.

**`iW`** / **`aW`**: Like `iw`/`aw` but for WORDs (only whitespace is a
boundary).

### 9.2 Quote Objects (i"/a", i'/a', i\`/a\`)

**`i"`**: Select the text between the nearest pair of double quotes on the
current line. Does not include the quotes themselves. Escaped quotes (preceded
by backslash) are skipped.

**`a"`**: Select the text including the quotes. Also includes trailing
whitespace if present, or leading whitespace if no trailing whitespace exists.

If the cursor is not inside a quoted string, the search proceeds forward on the
current line to find the next quoted string. If none is found, no selection is
made. Quote objects do not cross line boundaries.

The same logic applies to single quotes (`i'`/`a'`) and backticks
(`` i` ``/`` a` ``).

### 9.3 Bracket/Pair Objects

**`i(`** / **`i)`** / **`ib`**: Select the text between the nearest enclosing
pair of parentheses. Does not include the parentheses. Searches backward for the
unmatched opening parenthesis, then forward for the matching close. Handles
nesting (depth counting). Works across multiple lines.

**`a(`** / **`a)`** / **`ab`**: Select the text including the parentheses.

If the cursor is not inside parentheses, searches forward on the current line
for an opening parenthesis and uses that pair.

The same applies to:
- `i{` / `i}` / `iB` and `a{` / `a}` / `aB` for curly braces
- `i[` / `i]` and `a[` / `a]` for square brackets
- `i<` / `i>` and `a<` / `a>` for angle brackets

**Special behavior for `ci(`/`ci{` on multi-line pairs**: when the inner content
spans multiple lines, the inner lines are replaced with a single blank line that
is indented to the level of the opening bracket plus one shiftwidth.

**Empty brackets**: `di(` on `()` is a no-op (nothing between the brackets to
delete). `ci(` on `()` enters insert mode between the brackets.

### 9.4 Paragraph Objects (ip, ap)

**`ip`**: Linewise. If the cursor is on a non-blank line, selects all contiguous
non-blank lines. If the cursor is on a blank line, selects all contiguous blank
lines.

**`ap`**: Linewise. Like `ip` but includes adjacent blank lines. If the
paragraph has trailing blank lines, those are included. If it is the last
paragraph in the buffer (no trailing blanks), leading blank lines are included
instead.

### 9.5 Sentence Objects (is, as)

**`is`**: Select the current sentence. A sentence ends at `.`, `!`, or `?`
followed by whitespace or end-of-line (with optional closing characters in
between). The inner sentence excludes trailing whitespace after the punctuation.

**`as`**: Select the sentence including trailing whitespace. If there is no
trailing whitespace, includes leading whitespace instead.

---

## 10. Editing Commands

### 10.1 Delete Character (x, X)

**`x`** (or `Delete`): Delete the character under the cursor. With count,
deletes N characters forward. Stores deleted text in the unnamed register as
charwise. After deletion, if the cursor would be past the end of the line, it
moves to the last remaining character. On an empty line, does nothing. After `x`
on the last character of a line, the cursor lands on the new last character.

**`X`**: Delete the character before the cursor. At column 0, does nothing.
With count, deletes N characters backward.

### 10.2 Substitute (s, S)

**`s`**: Delete N characters and enter insert mode (equivalent to `cl` with
count). If count exceeds the remaining characters on the line, deletes to end of
line and enters insert mode there.

**`S`**: Delete the content of N lines (preserving leading indent) and enter
insert mode. Equivalent to `cc`.

### 10.3 Replace Character (r)

**`r{char}`**: Replace the character under the cursor with {char}. With count N,
replaces N characters starting from the cursor. If count exceeds the remaining
characters on the line, the replacement does not happen (no-op). If {char} is
Enter, the character is replaced with a newline (line is split). The cursor
stays on the last replaced character (or the first character of the new line if
Enter was used).

### 10.4 Toggle Case (~)

Toggle the case of the character under the cursor and advance the cursor one
position. Does not cross line boundaries — at the end of a line, the cursor
stays on the last character. Non-letter characters (digits, punctuation, spaces)
are not modified but the cursor still advances. With count, toggles N
characters.

### 10.5 Join Lines (J, gJ)

**`J`**: Join the current line with the next line. Removes the newline and all
leading whitespace from the next line, then inserts a single space at the join
point. Smart join rules:

- If the next line starts with `)`, no space is added.
- If the current line ends with a space, no additional space is added.
- The cursor moves to the join point (where the space was inserted).

With count N, joins N lines together (N-1 joins). `1J` is a no-op. On the last
line of the buffer, does nothing.

**`gJ`**: Join without inserting a space and without removing leading whitespace
from the next line. Otherwise identical to `J`.

### 10.6 Delete to End (D, C, Y)

**`D`**: Delete from cursor to end of line (equivalent to `d$`). With count N,
deletes to end of line plus N-1 more lines (mirrors `d{N}$`).

**`C`**: Change from cursor to end of line (equivalent to `c$`). Enters insert
mode after deleting.

**`Y`**: Yank to end of line (equivalent to `y$`, charwise). Note: in classic
Vi, `Y` was `yy` (linewise); Neovim changed this default.

### 10.7 Increment and Decrement (Ctrl-A, Ctrl-X)

**`Ctrl-A`**: Find the first number at or after the cursor on the current line.
Increment it by count (default 1). The cursor moves to the last digit of the
resulting number.

**`Ctrl-X`**: Same as Ctrl-A but decrements. `Ctrl-X` on `0` produces `-1`.
`Ctrl-A` on `-1` produces `0`.

If no number is found at or after the cursor on the current line, does nothing.
On an empty line, does nothing.

### 10.8 Show File Info (Ctrl-G)

Displays a message showing the filename, number of lines, number of characters
(bytes), and the cursor's position as a percentage through the file.

### 10.9 Show ASCII Value (ga)

Displays the decimal, hexadecimal, and octal values of the character under the
cursor.

### 10.10 Go to Definition (gd)

Searches backward (then wraps forward) for the first occurrence of the word
under the cursor. Sets the search pattern so that subsequent `n`/`N` navigate
between occurrences. Adds to the jump list.

### 10.11 Reselect Visual (gv)

Re-enters visual mode with the exact same selection range as the last visual
selection. If no prior visual selection exists, does nothing.

### 10.12 Insert at Last Position (gi)

Enter insert mode at the position where insert mode was last exited. If the
remembered column is beyond the end of the line (the line is now shorter), the
cursor is clamped to the end of the line.

### 10.13 Insert at Column Zero (gI)

Enter insert mode at column 0 of the current line, ignoring any indentation.

---

## 11. Insert Mode

### 11.1 Entering Insert Mode

| Key | Effect |
|---|---|
| `i` | Insert before cursor |
| `I` | Insert at first non-blank character |
| `a` | Append after cursor (cursor moves right by 1) |
| `A` | Append at end of line |
| `o` | Open a new line below, inheriting indent, enter insert mode |
| `O` | Open a new line above, inheriting indent, enter insert mode |
| `s` | Delete character(s) then insert |
| `S` / `cc` | Clear line (preserve indent) then insert |
| `c{motion}` | Delete motion range then insert |
| `gi` | Insert at last insert position |
| `gI` | Insert at column 0 |

### 11.2 Keys in Insert Mode

**Printable characters**: Insert at the cursor position.

**`Enter`** (or `Ctrl-J`): Split the line at the cursor. The text after the
cursor moves to a new line below.

**`Backspace`** (or `Ctrl-H`): Delete the character before the cursor. If at
column 0 and not on the first line, join with the previous line (move remaining
text to end of previous line). At row 0, column 0, does nothing.

**`Delete`**: Delete the character at the cursor (forward delete). If at the end
of a line and there is a next line, join the next line onto the current line.

**`Ctrl-W`**: Delete the word before the cursor. Word boundaries follow the same
rules as `b` (word-characters, punctuation, whitespace are distinct classes). At
column 0, joins with the previous line. At row 0, column 0, does nothing.

**`Ctrl-U`**: Delete from the cursor to the start of the line. At column 0,
joins with the previous line (moves cursor to end of previous line). At row 0,
column 0, does nothing.

**`Ctrl-R`**: Followed by a register character (`a`–`z`, `0`–`9`, `"`), inserts
the contents of that register at the cursor position.

**Arrow keys**: Move the cursor without exiting insert mode. Up and down clamp
the column to the target line's length.

### 11.3 Exiting Insert Mode

`Escape` or `Ctrl-[` returns to normal mode. The cursor moves one column to the
left (unless at column 0). If a count was used to enter insert mode (`3i`), the
text typed during the insert session is repeated count-1 additional times before
returning to normal mode. The repeat includes all keys typed: characters,
Enter, Backspace, Ctrl-W, Ctrl-U.

### 11.4 Insert Recording for Dot Repeat

All keystrokes typed during an insert session (from entry to Escape) are
recorded for dot repeat. Arrow keys are excluded from the recording (they move
the cursor but are not part of the "change"). The Ctrl-R register paste
sequence is recorded.

---

## 12. Replace Mode

### 12.1 Entering Replace Mode

`R` from normal mode enters replace mode. The cursor is displayed as a block.
A start position is recorded.

### 12.2 Typing in Replace Mode

Each character typed overwrites the character at the cursor and moves the cursor
right. If the cursor is at the end of the line, characters are appended
(extending the line). Enter splits the line.

### 12.3 Backspace in Replace Mode

Backspace moves the cursor left and restores the original character that was at
that position before the replace session started. If the cursor is at the start
position where `R` was pressed, Backspace does nothing (cannot go further back).
This is fundamentally different from insert mode Backspace which deletes.

### 12.4 Exiting Replace Mode

Escape returns to normal mode. The cursor moves one column left (unless at
column 0).

---

## 13. Visual Mode

### 13.1 Charwise Visual (v)

Pressing `v` enters charwise visual mode with the cursor position as the anchor.
Moving the cursor extends the selection from the anchor to the current cursor
position. The selection includes the character under the cursor.

Pressing `v` again exits visual mode. Pressing `V` switches to visual-line
mode. `Escape` exits visual mode.

### 13.2 Linewise Visual (V)

Pressing `V` enters visual-line mode. The selection always covers full lines
from the anchor line to the cursor line. Pressing `V` again exits. Pressing `v`
switches to charwise visual.

### 13.3 Swapping Ends (o, O)

`o` in visual mode swaps the cursor to the other end of the selection. The
anchor and cursor switch roles. `O` behaves identically to `o` in charwise
visual mode.

### 13.4 Motions in Visual

All normal-mode motions work in visual mode and extend the selection. Text
objects (`iw`, `a(`, etc.) expand the selection to cover the object.

### 13.5 Operations in Visual Mode

Operations consume the selection and return to normal mode:

**`d`** / **`x`** / **`Delete`**: Delete the selection. Linewise visual deletes
whole lines. Charwise visual deletes the character range. If a charwise
selection spans complete lines (from col 0 of one line to the end of another),
it is promoted to a linewise delete.

**`c`** / **`s`**: Delete the selection and enter insert mode. Linewise change
preserves indent (like `cc`).

**`y`**: Yank the selection. Cursor returns to the start of the selection (the
earlier of anchor and cursor).

**`>`** / **`<`**: Indent or dedent all lines in the selection. The selection is
cleared and the cursor stays on the first affected line.

**`~`**: Toggle case of all characters in the selection. In charwise mode, only
characters within the column range on each line are toggled. In linewise mode,
entire lines are toggled.

**`U`**: Uppercase all characters in the selection (same scoping as `~`).

**`u`**: Lowercase all characters in the selection.

**`J`**: Join all lines in the selection using smart join rules.

**`p`**: Replace the selection with the contents of the register. Linewise
register into linewise visual: replaces the selected lines. Charwise register
into charwise visual: deletes the selection, inserts the register text.

**`r{char}`**: Replace every character in the selection with {char}. In charwise
mode, only characters within the column range on each line. In linewise mode,
every non-newline character in the selected lines.

**`:`**: Open command mode with the range `'<,'>` pre-filled, allowing ex
commands to act on the selection (e.g., `:'<,'>sort`).

**`S{char}`** (surround): Surround the visual selection with delimiters. See
[Surround](#22-surround-nvim-surround).

### 13.6 Dot Repeat for Visual Operations

After a visual operation, the dot command repeats it on a similarly-sized
selection starting from the cursor. The selection shape (charwise/linewise) and
size are replayed.

---

## 14. Search

### 14.1 Forward Search (/)

Typing `/` from normal mode enters command mode with a forward search prompt.
Characters typed form the search pattern (regular expression). Pressing Enter
executes the search. The cursor jumps to the first match after the current
position, wrapping around the end of the buffer if necessary.

During typing, incremental search highlighting shows the next match in real time
(IncSearch highlight).

### 14.2 Backward Search (?)

Same as forward search but in the reverse direction. The cursor jumps to the
first match before the current position, wrapping around the beginning.

### 14.3 Repeat Search (n, N)

`n` repeats the search in the original direction. `N` repeats in the reverse
direction. Both wrap around the buffer. Both add to the jump list.

### 14.4 Word Search (\*, \#)

`*` takes the word under the cursor, constructs a whole-word search pattern
(with word boundaries), and searches forward. `#` does the same but backward.
Both set the search pattern for subsequent `n`/`N`.

### 14.5 Search Highlighting

All matches of the current search pattern are highlighted (`Search` highlight
group). The match under the cursor or the most recently jumped-to match gets a
distinct highlight (`CurSearch` highlight group). The incremental match during
typing uses `IncSearch`. `:noh` clears the highlighting but preserves the
pattern for `n`/`N`.

### 14.6 Search with Operators

An operator followed by a search motion (e.g., `d/foo<Enter>`) operates on the
range from the cursor to the search match. The search motion is exclusive. If
the search fails, the operator is cancelled and an error is shown.

---

## 15. Marks

### 15.1 Setting Marks

`m{a-z}` sets a mark at the current cursor position. Each mark stores both the
line number and the column. Setting a mark to a letter that already has a mark
overwrites the previous position.

### 15.2 Jumping to Marks

**`'{a-z}`**: Jump to the first non-blank character of the marked line. This is
a linewise motion.

**`` `{a-z} ``**: Jump to the exact marked position (line and column). This is a
charwise motion. If the marked line is now shorter than the marked column, the
cursor is clamped to the end of the line.

### 15.3 Special Marks

**`'.`** and **`` `. ``**: Jump to the position of the last change.

**`''`** and **` `` `**: Jump to the position before the last jump.

**`'<`**, **`'>`**: First and last line of the last visual selection. Used
internally for ex command ranges and also accessible as user marks.

### 15.4 Marks with Operators

Operators combine with mark jumps: `d'a` deletes linewise from the current line
to the marked line. `` d`a `` deletes charwise from the cursor to the mark
position. `y'a`, `c'a`, etc. all work.

---

## 16. Jump List

### 16.1 Recording Jumps

Certain motions add the cursor position to the jump list before executing:
`G`, `gg`, `/search`, `?search`, `n`, `N`, `*`, `#`, `gd`, `%` (when jumping
to a match).

The jump list stores up to 100 entries. Adding a new entry that duplicates the
current top entry is suppressed.

### 16.2 Navigating

**`Ctrl-O`**: Jump to the older position in the jump list (go back).

**`Ctrl-I`** (or `Tab`): Jump to the newer position (go forward).

At the ends of the list, further navigation does nothing.

---

## 17. Change List

### 17.1 Recording Changes

Every buffer modification records the cursor position in the change list. Each
insert session, delete, or other edit adds an entry.

### 17.2 Navigating

**`g;`**: Jump to the older position in the change list.

**`g,`**: Jump to the newer position.

At the ends of the list, further navigation does nothing.

---

## 18. Undo and Redo

### 18.1 Undo Units

Each command from normal mode is one undo unit. An entire insert session (from
entering insert mode to pressing Escape) is one undo unit — undoing it removes
all text typed during that session. Individual operations within a macro are
separate undo units (macros are not atomic).

### 18.2 Undo (u)

`u` reverts the buffer to the state before the last change. The cursor moves to
the position where the change began. With count N, undoes N changes. If N
exceeds the number of undo entries, undoes everything available.

### 18.3 Redo (Ctrl-R)

`Ctrl-R` reapplies the last undone change. With count N, redoes N changes. Any
new edit after undo clears the redo stack — those undone changes can no longer
be redone.

### 18.4 Dirty Detection

A buffer is considered "dirty" (modified) based on undo position, not content
comparison. If you type `iHello<Esc>` then `u`, the buffer is clean (back to
original undo position). If you type `iHello<Esc>` then manually delete the
characters, the buffer is still dirty — even though the content matches the
original.

---

## 19. Dot Repeat

### 19.1 What Is Recorded

The `.` command repeats the last change. A "change" includes:

- Delete commands: `x`, `X`, `s`, `dd`, `d{motion}`, `D`
- Change commands: `c{motion}`, `cc`, `C`, `S`, `r{char}`, `R` session
- Insert commands: `i`, `I`, `a`, `A`, `o`, `O` (including all typed text)
- Put commands: `p`, `P`
- Case toggle: `~`, `gu`, `gU`, `g~` with motions
- Indent/dedent: `>>`, `<<`, `>{motion}`, `<{motion}`
- Increment/decrement: `Ctrl-A`, `Ctrl-X`
- Surround: `ys`, `ds`, `cs`
- Visual mode operations
- Join: `J`, `gJ`

### 19.2 What Is NOT Recorded

Yanks (`y`, `yy`, `yw`, etc.) do not set the dot-repeat buffer. After a yank,
`.` still repeats the previous change, not the yank.

Motions alone (without an operator) do not set dot-repeat.

### 19.3 Count Override

If `.` is given a count, that count overrides the original count. `2dd` then
`3.` executes `3dd`, not `2dd`. `5Ctrl-A` then `10.` increments by 10 (not 5).

### 19.4 Dot After Visual Operations

After a visual mode operation (e.g., `Vjd`), `.` replays the operation on a
similarly-sized selection from the current cursor position.

### 19.5 Dot After Change with Text

After `cwfoo<Esc>`, `.` on another word replaces that word with "foo"
regardless of the original or target word length.

---

## 20. Macros

### 20.1 Recording

`q{a-z}` begins recording keystrokes into register {letter}. The command line
shows `recording @a` (or whichever register). All subsequent keystrokes are
captured. `q` pressed again stops recording and saves the sequence.

Recording into the same register overwrites the previous contents. Recording
`qaq` (start and immediately stop) clears register `a`.

### 20.2 Playback

`@{a-z}` plays back the macro in the named register. With count N, the macro is
played N times. `@@` replays the most recently *played* macro. `Q` replays the
most recently *recorded* macro. These can differ: if you record into `a` then
play `@b`, `@@` replays `b` while `Q` replays `a`.

`@:` replays the last ex command.

### 20.3 Playback Behavior

Macros feed their keystrokes as if typed by the user. All commands work inside
macros: insert mode, search, motions, operators, visual mode, dot repeat, marks,
etc. If a motion within the macro fails (e.g., search not found, `f{char}` not
found), the macro aborts immediately.

### 20.4 Macro and Undo

Each individual operation within a macro is a separate undo unit. Undoing after
a macro that performed 5 edits requires 5 presses of `u`.

### 20.5 Nested Macros

A macro can invoke another macro (`@b` inside macro `a`). Recursion depth is
limited to prevent infinite loops.

---

## 21. Put (Paste)

### 21.1 Charwise Put

When the register contains charwise text:

**`p`**: Insert the text after the cursor. For single-line text, insert at
cursor+1. For multi-line text, split the current line at cursor+1 and splice in
the register lines. The cursor lands on the **last character** of the pasted
text.

**`P`**: Insert the text before the cursor. For single-line text, insert at the
cursor position. The cursor lands on the **last character** of the pasted text.

With count N, the text is pasted N times.

### 21.2 Linewise Put

When the register contains linewise text:

**`p`**: Insert the lines below the current line. The cursor moves to the first
non-blank of the first inserted line.

**`P`**: Insert the lines above the current line. The cursor moves to the first
non-blank of the first inserted line.

With count N, the lines are pasted N times.

### 21.3 Unnamed Register Overwrite

Because `d` and `x` overwrite the unnamed register, `yy` then `dd` then `p`
pastes the deleted line, not the yanked line. To preserve a yank across
deletes, use a named register (`"ayy`).

### 21.4 Classic Idioms

- `xp`: Swap two characters (delete char, put after).
- `ddp`: Swap two lines (delete line, put below).
- `yyp`: Duplicate a line.

---

## 22. Surround (nvim-surround)

This describes the behavior of the nvim-surround plugin, which is included as
part of the standard feature set.

### 22.1 Delimiter Pairs

Every surround operation uses a character to determine a pair of delimiters:

| Character | Opening | Closing | Inner Space |
|---|---|---|---|
| `)` or `b` | `(` | `)` | No |
| `(` | `(` | `)` | Yes: `( ` and ` )` |
| `]` or `r` | `[` | `]` | No |
| `[` | `[` | `]` | Yes: `[ ` and ` ]` |
| `}` or `B` | `{` | `}` | No |
| `{` | `{` | `}` | Yes: `{ ` and ` }` |
| `>` or `a` | `<` | `>` | No |
| `<` | `<` | `>` | Yes: `< ` and ` >` |
| `"` | `"` | `"` | No |
| `'` | `'` | `'` | No |
| `` ` `` | `` ` `` | `` ` `` | No |
| Any other char | That char | That char | No |

The key distinction: **opening** bracket characters (`(`, `[`, `{`, `<`) add a
space inside the delimiters. **Closing** bracket characters and their aliases do
not.

### 22.2 Add Surroundings (ys)

`ys{motion}{char}` surrounds the text covered by {motion} with the delimiter
pair for {char}.

The text to surround is determined by executing the motion from the cursor. Any
motion works: `w`, `e`, `iw`, `aw`, `$`, `0`, `f{c}`, `t{c}`, text objects,
counted motions, etc.

`yss{char}` surrounds the entire current line. Leading and trailing whitespace
on the line is preserved outside the delimiters (the content between the
delimiters is the trimmed line text).

### 22.3 Delete Surroundings (ds)

`ds{target}` finds and removes the nearest surrounding pair matching {target}.

For quotes: finds paired quotes on the current line containing the cursor.

For brackets: searches backward for the unmatched opening bracket, then forward
for the matching close. Handles nesting.

When the target is an **opening** bracket (`(`, `[`, `{`, `<`), whitespace
immediately inside the delimiters is also removed (one space on each side, if
present). When the target is a **closing** bracket or alias, the content is left
untouched.

If no matching pair is found, nothing happens.

### 22.4 Change Surroundings (cs)

`cs{target}{replacement}` finds the nearest pair matching {target}, removes it,
then wraps the content with the {replacement} pair.

This combines the rules of `ds` and `ys`:
- The {target} follows `ds` rules: opening brackets trim inner whitespace.
- The {replacement} follows `ys` rules: opening brackets add inner space.
- Effects compose: `cs({` trims spaces (opening target) then wraps tight
  (closing replacement). `cs)(` keeps spaces (closing target) then adds spaces
  (opening replacement).

### 22.5 Visual Surround (S)

In visual mode, pressing `S{char}` surrounds the selected text with the
delimiter pair for {char}. Opening brackets add inner spaces; closing brackets
do not.

In visual-line mode, the delimiters are placed on their own lines with the
content indented.

### 22.6 Dot Repeat

All surround operations are dot-repeatable. `ysiw)` then `w.` applies the same
surround to the next word.

---

## 23. Scroll

### 23.1 Half-Page Scroll (Ctrl-D, Ctrl-U)

**`Ctrl-D`**: Scroll down by half the screen height. The cursor moves down by
the same amount. If a count is given, that count becomes the new scroll amount
for future Ctrl-D and Ctrl-U presses (sticky count).

**`Ctrl-U`**: Scroll up by half the screen height. Same sticky count behavior.

### 23.2 Full-Page Scroll (Ctrl-F, Ctrl-B)

**`Ctrl-F`**: Scroll forward one full page. Keeps a 2-line overlap (the second-
to-last visible line becomes the first visible line of the new view). The
cursor goes to the first non-blank of the top visible line.

**`Ctrl-B`**: Scroll backward one full page. Same overlap logic.

### 23.3 Single-Line Scroll (Ctrl-E, Ctrl-Y)

**`Ctrl-E`**: Scroll the viewport down by one line. If the cursor would be
above the viewport, it moves down to stay visible.

**`Ctrl-Y`**: Scroll the viewport up by one line. If the cursor would be below
the viewport, it moves up to stay visible.

### 23.4 Cursor-Centered Scroll (z commands)

**`zz`**: Scroll so the cursor line is at the center of the screen.

**`zt`**: Scroll so the cursor line is at the top of the screen.

**`zb`**: Scroll so the cursor line is at the bottom of the screen.

---

## 24. Command Mode (Ex Commands)

### 24.1 Entering Command Mode

`:` from normal mode opens the command line at the bottom of the screen.
`/` opens a forward search prompt. `?` opens a backward search prompt.

### 24.2 Command-Line Keys

**Characters**: Appended to the command line.

**`Backspace`**: Deletes the last character. If the command line is empty,
returns to normal mode.

**`Enter`**: Executes the command.

**`Escape`**: Cancels the command and returns to normal mode.

**`Tab`**: For file-related commands (`:e`, `:w`, `:r`, `:sav`), completes
filenames from the virtual filesystem. Repeated Tab presses cycle through
matches.

### 24.3 File Commands

**`:w[rite] [file]`**: Save the buffer to the filesystem. If a filename is
given and the buffer has no current filename, sets it. Displays a message
showing the filename, line count, and byte count. If the message exceeds screen
width, it is truncated with a leading `<`.

**`:wq [file]`**: Write the buffer and quit. Always writes, even if the buffer
is clean.

**`:x[it]`**: Write the buffer only if it has been modified, then quit. If the
buffer is clean, quits without writing.

**`:q[uit]`**: Quit. Fails with error E37 ("No write since last change") if the
buffer is dirty.

**`:q[uit]!`**: Quit without saving, discarding changes.

**`:e[dit] [file]`**: Edit a file. With no argument, reloads the current file.
Fails if the current buffer is dirty (use `:e!` to force). When opening a new
file, displays "N lines, NC characters" or "new file" message.

**`:e[dit]! [file]`**: Force edit, discarding current changes.

**`:sav[eas] file`**: Save the buffer to a new filename and set that as the
current filename.

**`:r[ead] file`**: Read the contents of a file and insert them below the
cursor. If the buffer has no filename, sets it to the read file's name.

**`:r[ead]! command`**: Execute a shell command and insert its output below
the cursor.

### 24.4 Navigation Commands

**`:{number}`**: Jump to line {number}. The cursor goes to the first non-blank.

**`:$`**: Jump to the last line.

### 24.5 Sort Command

**`:[range]sort[!] [flags]`**: Sort lines in the range. Without a range, sorts
the entire buffer. With `'<,'>` range (from visual mode), sorts the selected
lines. `!` reverses the sort. Flags: `n` for numeric sort, `i` for
case-insensitive, `u` for unique (remove duplicates).

### 24.6 Shell Commands

**`:!command`**: Execute a shell command. Output is displayed in a prompt
overlay. The user must press Enter or Escape to dismiss.

### 24.7 Set Commands

See [Settings](#25-settings).

### 24.8 Search Highlighting

**`:noh[lsearch]`**: Clear search highlighting. The search pattern is preserved
for `n`/`N`, but matches are no longer highlighted on screen.

### 24.9 Abbreviation

All ex commands accept any unambiguous prefix: `:wri` for `:write`, `:qui` for
`:quit`, `:noh` for `:nohlsearch`, etc.

---

## 25. Settings

### 25.1 Line Numbers

**`:set number`** (or `:set nu`): Show absolute line numbers in a left gutter.

**`:set nonumber`** (or `:set nonu`): Hide absolute line numbers.

**`:set relativenumber`** (or `:set rnu`): Show relative line distances. The
cursor line shows `0`; other lines show their distance from the cursor.

**`:set norelativenumber`** (or `:set nornu`): Hide relative numbers.

When both `number` and `relativenumber` are active, the cursor line shows its
absolute number and all other lines show relative distances.

The gutter width is at least 4 columns (matching Neovim's default
`numberwidth=4`), expanding as needed for larger line counts.

### 25.2 Tab and Indent Settings

The default settings are `tabstop=8`, `shiftwidth=8`, `noexpandtab`. Indent
operations (`>>`, `<<`) use shiftwidth. Tabs are displayed using tabstop width.

### 25.3 Not Yet Implemented Settings

The following common Vim settings are not yet implemented:

- `wrap` / `nowrap` — not implemented
- `hlsearch` / `nohlsearch` (highlighting is always on when there is a pattern)
- `incsearch` (incremental search is always on)
- `smartindent` — not implemented (`autoindent` is implemented)

---

## 26. Messages and Prompts

### 26.1 Error Messages

**E37**: "No write since last change (add ! to override)" — shown when `:q` is
used with unsaved changes.

**E32**: "No file name" — shown when `:w` or `:wq` is used and no filename is
set.

**E484**: "Can't open file" — shown when `:r` or `:e` references a non-existent
file.

**E486**: "Pattern not found: {pattern}" — shown when a search finds no
matches.

### 26.2 File Info Messages

After `:w`: `"filename" NL, NB written` (N lines, N bytes). Truncated with
leading `<` if too long for the screen.

After `:e`: `"filename" NL, NC` (N lines, N characters) for existing files, or
`"filename" [New]` for new files.

After `:r`: `N line(s) added`.

### 26.3 Prompt Messages

After `:!command`: output is shown followed by "Press ENTER or type command to
continue". Enter or Escape dismisses; `:` dismisses and enters command mode.

### 26.4 Recording Indicator

When recording a macro, `recording @{register}` is shown in the command line
area.

### 26.5 Mode Indicators

| Mode | Status Line |
|---|---|
| Normal | *(empty)* |
| Insert | `-- INSERT --` |
| Replace | `-- REPLACE --` |
| Visual | `-- VISUAL --` |
| Visual Line | `-- VISUAL LINE --` |

---

## Appendix A: Not Implemented Features

The following Vim features are documented here for completeness but are not yet
implemented in the simulator:

- **Expression register** (`"=`): evaluate expression (reads as empty)
- **Line wrapping** (`wrap`/`nowrap`)
- **`smartindent`** (basic `autoindent` is implemented)
- **`:global`** (`:g/pattern/command`)
- **Visual block mode** (`Ctrl-V`)
- **Completion** (`Ctrl-N`/`Ctrl-P` in insert mode)
- **Folds**
- **Quickfix/location lists**
- **Multiple buffers** (`:bn`, `:bp`, `:ls`)
- **Window splits** (`:split`, `:vsplit` — tmux provides pane splitting)
- **Tags** (`Ctrl-]`, `:tag`)
- **`:map`/`:noremap`** custom mappings
- **Text object `it`/`at`** (HTML/XML tag objects)
