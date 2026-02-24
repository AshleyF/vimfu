# VimFu Curriculum

A complete curriculum for learning Vim/Neovim in **sub-60-second video lessons** (YouTube Shorts format).
Each lesson is a tiny, focused topic — one concept, one demo. Watch them in order to build up from
zero to fluency, or jump around once you're comfortable. After the foundational arc (Parts 1–4),
the lessons become daily "flash card" style — walk the keyboard, one key at a time.

---

## Part 1 — Survival (Lessons 1–15)

_Just enough to open a file, type something, save it, and get out alive._

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 001 | What Is Vim? | — | Why learn Vim? Modal editing philosophy. Normal mode is "normal." |
| 002 | Opening a File | `nvim hello.txt` | Launch Neovim, what you see, the empty buffer. |
| 003 | You're in Normal Mode | `Esc` | Normal mode is home base. Always return here after each thought. |
| 004 | Entering Insert Mode | `i` | Press `i` to insert text before the cursor. |
| 005 | Typing Text | — | You're in insert mode — just type normally. |
| 006 | Back to Normal Mode | `Esc` | Press Escape to leave insert mode. Make it a reflex. |
| 007 | Saving Your File | `:w` | Write (save) with colon-w-Enter. |
| 008 | Quitting Vim | `:q` | Quit with colon-q-Enter. The meme, solved. |
| 009 | Save and Quit | `:wq` `:x` `ZZ` | Three ways to save-and-quit. |
| 010 | Quit Without Saving | `:q!` `ZQ` | Discard changes and bail out. |
| 011 | Undo | `u` | Undo the last change. Press it again for more undos. |
| 012 | Redo | `Ctrl-R` | Redo what you just undid. |
| 013 | Moving: h j k l | `h` `j` `k` `l` | Left, down, up, right. Hands on home row. |
| 014 | Why Not Arrow Keys? | `←` `↓` `↑` `→` | They work, but your hands leave home row. Start breaking the habit. |
| 015 | The Escape Habit | `Esc` | After every thought: Escape. Normal mode is your resting state. |

---

## Part 2 — Basic Editing (Lessons 16–45)

_Enough to actually get work done. After this part, go "cold turkey" and use Vim for real work._

### Entering Insert Mode (various ways)

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 016 | Append After Cursor | `a` | Insert text after the cursor. |
| 017 | Insert at Start of Line | `I` | Jump to first non-blank character and insert. |
| 018 | Append at End of Line | `A` | Jump to end of line and insert. |
| 019 | Open Line Below | `o` | Create a new line below and enter insert mode. |
| 020 | Open Line Above | `O` | Create a new line above and enter insert mode. |

### Basic Motions — Horizontal

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 021 | Word Forward | `w` | Jump to the start of the next word. |
| 022 | Word Backward | `b` | Jump to the start of the previous word. |
| 023 | End of Word | `e` | Jump to the end of the current/next word. |
| 024 | Back to End of Word | `ge` | Jump backward to end of previous word. |
| 025 | Start of Line | `0` | Jump to column zero (first character). |
| 026 | First Non-Blank | `^` | Jump to first non-whitespace character. |
| 027 | End of Line | `$` | Jump to the last character on the line. |

### Basic Motions — Vertical

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 028 | Go to Top of File | `gg` | Jump to line 1 (or line N with a count). |
| 029 | Go to Bottom of File | `G` | Jump to the last line (or line N with a count). |
| 030 | Go to Line N | `:42` or `42G` | Jump directly to a specific line number. |

### Deleting

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 031 | Delete Character | `x` | Delete the character under the cursor. |
| 032 | Delete Character Before | `X` | Backspace — delete character before cursor. |
| 033 | Delete Word | `dw` | Delete from cursor to start of next word. |
| 034 | Delete to End of Line | `D` or `d$` | Delete from cursor to end of line. |
| 035 | Delete Entire Line | `dd` | Delete the whole line. |

### Changing (Delete + Insert)

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 036 | Change Word | `cw` | Delete word and enter insert mode. |
| 037 | Change to End of Line | `C` or `c$` | Delete to end and enter insert mode. |
| 038 | Change Entire Line | `cc` or `S` | Delete line contents and enter insert mode. |
| 039 | Substitute Character | `s` | Delete character and enter insert mode. |

### Copy (Yank) and Paste (Put)

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 040 | Yank (Copy) a Line | `yy` or `Y` | Copy the current line. |
| 041 | Put (Paste) After | `p` | Paste after the cursor (or below for lines). |
| 042 | Put (Paste) Before | `P` | Paste before the cursor (or above for lines). |
| 043 | Yank a Motion | `yw` `y$` `y{motion}` | Copy a word, to end of line, or any motion. |
| 044 | The dd-p Swap Trick | `ddp` `ddP` | Swap lines by deleting and putting. `xp` swaps characters. |
| 045 | Replace a Character | `r` | Replace the character under the cursor without entering insert mode. |

---

## Part 3 — Becoming Productive (Lessons 46–90)

_Motions, search, visual mode, counts, the dot command, text objects. This is where Vim starts to feel powerful._

### Searching

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 046 | Search Forward | `/pattern` | Search forward for a pattern. |
| 047 | Search Backward | `?pattern` | Search backward for a pattern. |
| 048 | Next Match | `n` | Jump to the next search match. |
| 049 | Previous Match | `N` | Jump to the previous search match. |
| 050 | Search Word Under Cursor | `*` | Search forward for the word under the cursor. |
| 051 | Search Word Backward | `#` | Search backward for the word under the cursor. |

### Find on Line

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 052 | Find Character Forward | `f{char}` | Jump to the next occurrence of {char} on this line. |
| 053 | Find Character Backward | `F{char}` | Jump to the previous occurrence of {char}. |
| 054 | Till Character Forward | `t{char}` | Jump to just before the next {char}. |
| 055 | Till Character Backward | `T{char}` | Jump to just after the previous {char}. |
| 056 | Repeat Find | `;` | Repeat the last f/t/F/T in the same direction. |
| 057 | Repeat Find Reverse | `,` | Repeat the last f/t/F/T in the opposite direction. |

### Counts

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 058 | Counted Motions | `5j` `3w` `10l` | Prefix any motion with a number to repeat it. |
| 059 | Counted Deletes | `3dd` `2dw` | Delete 3 lines, 2 words, etc. |
| 060 | Counted Inserts | `5i-Esc` `3o` | Insert text N times. Type `5i-` then Escape → five dashes. |
| 061 | Go to Line by Count | `42G` | Jump to line 42. Same as `:42`. |
| 062 | Jump to Percentage | `50%` | Jump to 50% through the file. |
| 063 | Go to Column | `20\|` | Jump to column 20 on the current line. |

### Visual Mode

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 064 | Character Visual Mode | `v` | Start selecting character by character. |
| 065 | Line Visual Mode | `V` | Select whole lines at a time. |
| 066 | Block Visual Mode | `Ctrl-V` | Select a rectangular block (columns). |
| 067 | Switching Visual Modes | `v` `V` `Ctrl-V` | Switch between visual modes while selecting. |
| 068 | Actions on Selection | `d` `c` `y` `>` `<` | Delete, change, yank, indent, unindent the selection. |
| 069 | Other Corner | `o` `O` | Move cursor to the other end of the selection. |
| 070 | Reselect Last Selection | `gv` | Re-highlight the previous visual area. |

### The Dot Command

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 071 | Repeat Last Change | `.` | The most powerful key in Vim. Repeats the last change. |
| 072 | Dot with Counts | `3.` | Repeat the last change 3 times. |
| 073 | Dot Patterns | `cw` → type → `Esc` → `n.` | Change a word, search for next, dot to repeat. |

### Text Objects

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 074 | Inner Word / A Word | `ciw` `diw` `yiw` `daw` | Act on a word. "inner" = just the word. "a" = word + surrounding space. Also `iW`/`aW` for WORDs. |
| 075 | Inner/Around Quotes | `ci"` `da"` `yi"` | Act on text inside or around double quotes. |
| 076 | Inner/Around Single Quotes | `ci'` `da'` | Same but for single quotes. |
| 077 | Inner/Around Backticks | `` ci` `` `` da` `` | Same but for backtick strings. |
| 078 | Inner/Around Parentheses | `ci(` `dib` `ya)` | Act on text inside or around `(...)`. `b` is a synonym. |
| 079 | Inner/Around Braces | `ci{` `diB` `ya}` | Act on text inside or around `{...}`. `B` is a synonym. |
| 080 | Inner/Around Brackets | `ci[` `da]` | Act on text inside or around `[...]`. |
| 081 | Inner/Around Angle Brackets | `ci<` `da>` | Act on text inside or around `<...>`. |
| 082 | Inner/Around Sentence | `cis` `das` | Act on a sentence. |
| 083 | Inner/Around Paragraph | `cip` `dap` | Act on a paragraph (block of text separated by blank lines). |
| 084 | Inner/Around Tag | `cit` `dat` | Act on HTML/XML tag content or the whole tag. |
| 085 | The Vim Grammar | verb + (i/a) + object | Operators × text objects = composable editing language. |

### Scrolling

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 086 | Scroll Down Half Page | `Ctrl-D` | Move half a screen down. |
| 087 | Scroll Up Half Page | `Ctrl-U` | Move half a screen up. |
| 088 | Scroll Full Page Forward | `Ctrl-F` | Move a full screen forward. |
| 089 | Scroll Full Page Backward | `Ctrl-B` | Move a full screen backward. |
| 090 | Center / Top / Bottom | `zz` `zt` `zb` | Scroll so cursor line is at center, top, or bottom. |

---

## Part 4 — Intermediate Power (Lessons 91–135)

_Registers, macros, marks, windows, replace mode, and more motions. Now Vim feels like a superpower._

### More Motions

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 091 | Sentence Forward/Backward | `)` `(` | Jump by sentences. |
| 092 | Paragraph Forward/Backward | `}` `{` | Jump by paragraphs (blank-line separated). |
| 093 | Matching Bracket | `%` | Jump to matching `(`, `{`, `[`, etc. |
| 094 | Screen Top / Middle / Bottom | `H` `M` `L` `3H` `5L` | Jump to highest, middle, or lowest visible line. Count offsets from edge. |
| 095 | Next/Previous Line Start | `+` `-` `Enter` | Jump to first non-blank of next/previous line. |
| 096 | WORD Motions | `W` `B` `E` `gE` | Like `w`/`b`/`e`/`ge` but by whitespace-delimited WORDs. |

### Marks

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 097 | Setting a Mark | `m{a-z}` | Set a local mark at the cursor position. |
| 098 | Jumping to a Mark (Line) | `'{a-z}` | Jump to the line of mark. |
| 099 | Jumping to a Mark (Exact) | `` `{a-z} `` | Jump to the exact position of mark. |
| 100 | Global Marks | `m{A-Z}` | Uppercase marks work across files. |
| 101 | Special Marks | `''` ` `` ` `'.` `'^` | Last jump position, last change, last insert. |

### The Jump List

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 102 | Jump Back | `Ctrl-O` | Go to the previous position in the jump list. |
| 103 | Jump Forward | `Ctrl-I` / `Tab` | Go to the next position in the jump list. |
| 104 | Last Jump Position | `''` ` `` ` | Return to where you were before the last jump. |

### Replace Mode

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 105 | Replace Mode | `R` | Overtype existing characters until you press Escape. |
| 106 | Single Replace | `r{char}` | Replace one character and stay in normal mode. |

### Indenting & Formatting

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 107 | Indent Lines | `>>` | Indent the current line one shiftwidth. |
| 108 | Unindent Lines | `<<` | Unindent the current line. |
| 109 | Indent with Motion | `>{motion}` | Indent multiple lines via motion (e.g., `>ip`). |
| 110 | Auto-Indent | `==` `={motion}` | Re-indent line(s) using Vim's equalprg. |
| 111 | Visual Indent | `v` → select → `>` or `<` | Indent/unindent selected lines. |

### Case Changing

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 112 | Toggle Case | `~` | Toggle case of character under cursor and advance. |
| 113 | Uppercase Motion | `gU{motion}` | Make text uppercase (e.g., `gUiw` uppercases a word). |
| 114 | Lowercase Motion | `gu{motion}` | Make text lowercase. |
| 115 | Toggle Case Motion | `g~{motion}` | Toggle case over a motion. |
| 116 | Visual Case | `U` `u` `~` in visual | Uppercase, lowercase, or toggle the selection. |

### Join Lines

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 117 | Join Lines | `J` | Join current line with the next (adds a space). |
| 118 | Join Without Space | `gJ` | Join lines without inserting a space. |

### Registers

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 119 | Named Registers | `"a` through `"z` | Specify a register before yank/delete/put. `"ayy` yanks into register `a`. |
| 120 | Append to Register | `"A` through `"Z` | Uppercase letter appends to the register instead of replacing. |
| 121 | The Unnamed Register | `""` | Default register — where deletes and yanks go. |
| 122 | The System Clipboard | `"+` `"*` | Yank to / put from the system clipboard. |
| 123 | Small Delete Register | `"-` | Last delete smaller than a line. |
| 124 | Numbered Registers | `"0` through `"9` | `"0` = last yank. `"1`–`"9` = last 9 deletes. |
| 125 | View Registers | `:reg` | List all register contents. |

### Macros

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 126 | Record a Macro | `q{a-z}` | Start recording keystrokes into register {a-z}. |
| 127 | Stop Recording | `q` | Press `q` again to stop recording. |
| 128 | Play a Macro | `@{a-z}` | Execute the macro stored in register {a-z}. |
| 129 | Repeat Last Macro | `@@` | Replay the most recently executed macro. |
| 130 | Counted Macros | `100@a` | Run a macro 100 times (stops on error). |

### Windows (Splits)

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 131 | Horizontal Split | `Ctrl-W s` or `:sp` | Split window horizontally. |
| 132 | Vertical Split | `Ctrl-W v` or `:vs` | Split window vertically. |
| 133 | Navigate Windows | `Ctrl-W h/j/k/l` | Move between splits. |
| 134 | Close Window | `Ctrl-W c` or `:close` | Close the current split. |
| 135 | Only Window | `Ctrl-W o` or `:only` | Close all other splits. |

---

## Part 5 — Walking the Keyboard: Lowercase (Lessons 136–161)

_Every key on the keyboard does something in normal mode. Learn them one at a time._

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 136 | The `a` Key | `a` | Append: insert text after the cursor. |
| 137 | The `b` Key | `b` | Back: move to the start of the previous word. |
| 138 | The `c` Key | `c{motion}` | Change: delete motion and enter insert mode. |
| 139 | The `d` Key | `d{motion}` | Delete: delete text covered by motion. |
| 140 | The `e` Key | `e` | End: move to the end of the current/next word. |
| 141 | The `f` Key | `f{char}` | Find: jump to next {char} on the line. |
| 142 | The `g` Key | `g` (prefix) | Gateway to dozens of `g`-commands (covered later). |
| 143 | The `h` Key | `h` | Left: move one character left. |
| 144 | The `i` Key | `i` | Insert: enter insert mode before the cursor. |
| 145 | The `j` Key | `j` | Down: move one line down. |
| 146 | The `k` Key | `k` | Up: move one line up. |
| 147 | The `l` Key | `l` | Right: move one character right. |
| 148 | The `m` Key | `m{a-z}` | Mark: set a mark at cursor position. |
| 149 | The `n` Key | `n` | Next: jump to next search match. |
| 150 | The `o` Key | `o` | Open: new line below and insert. |
| 151 | The `p` Key | `p` | Put: paste after the cursor. |
| 152 | The `q` Key | `q{a-z}` / `q` | Record/stop recording a macro. |
| 153 | The `r` Key | `r{char}` | Replace: replace one character. |
| 154 | The `s` Key | `s` | Substitute: delete character and insert. |
| 155 | The `t` Key | `t{char}` | Till: jump to just before {char}. |
| 156 | The `u` Key | `u` | Undo: undo the last change. |
| 157 | The `v` Key | `v` | Visual: start character-wise visual mode. |
| 158 | The `w` Key | `w` | Word: move to start of next word. |
| 159 | The `x` Key | `x` | X-out: delete character under cursor. |
| 160 | The `y` Key | `y{motion}` | Yank: copy text covered by motion. |
| 161 | The `z` Key | `z` (prefix) | Gateway to dozens of `z`-commands (covered later). |

---

## Part 6 — Walking the Keyboard: Uppercase / Shifted (Lessons 162–187)

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 162 | The `A` Key | `A` | Append at end of line. |
| 163 | The `B` Key | `B` | Back WORD (whitespace-delimited). |
| 164 | The `C` Key | `C` | Change to end of line (synonym: `c$`). |
| 165 | The `D` Key | `D` | Delete to end of line (synonym: `d$`). |
| 166 | The `E` Key | `E` | End of WORD (whitespace-delimited). |
| 167 | The `F` Key | `F{char}` | Find character backward on the line. |
| 168 | The `G` Key | `G` | Go to last line (or line N). |
| 169 | The `H` Key | `H` | High: cursor to top visible line. |
| 170 | The `I` Key | `I` | Insert at first non-blank of line. |
| 171 | The `J` Key | `J` | Join current line with the next. |
| 172 | The `K` Key | `K` | Keyword lookup (man page / help). |
| 173 | The `L` Key | `L` | Low: cursor to bottom visible line. |
| 174 | The `M` Key | `M` | Middle: cursor to middle visible line. |
| 175 | The `N` Key | `N` | Previous search match (opposite of `n`). |
| 176 | The `O` Key | `O` | Open line above and insert. |
| 177 | The `P` Key | `P` | Put (paste) before cursor. |
| 178 | The `Q` Key | `Q` | Replay last recorded macro (nvim default; Ex mode in classic Vim). |
| 179 | The `R` Key | `R` | Replace mode: overtype until Escape. |
| 180 | The `S` Key | `S` | Substitute line (synonym: `cc`). |
| 181 | The `T` Key | `T{char}` | Till character backward on the line. |
| 182 | The `U` Key | `U` | Undo all changes on the current line. |
| 183 | The `V` Key | `V` | Visual line mode. |
| 184 | The `W` Key | `W` | WORD forward (whitespace-delimited). |
| 185 | The `X` Key | `X` | Delete character before cursor (backspace). |
| 186 | The `Y` Key | `Y` | Yank line (synonym: `yy`). |
| 187 | The `ZZ` and `ZQ` Keys | `ZZ` `ZQ` | Save-and-quit / quit-without-saving. |

---

## Part 7 — Walking the Keyboard: Symbols & Numbers (Lessons 188–218)

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 188 | The `0` Key | `0` | Go to first column of the line. |
| 189 | Numbers `1`–`9` | `1`–`9` | Start a count prefix for any command. |
| 190 | The `^` Key | `^` | First non-blank character of line. |
| 191 | The `$` Key | `$` | End of line. |
| 192 | The `%` Key | `%` | Jump to matching bracket/brace/paren. |
| 193 | The `~` Key | `~` | Toggle case of character. |
| 194 | The `` ` `` Key | `` `{mark} `` | Go to exact position of mark. |
| 195 | The `'` Key | `'{mark}` | Go to first non-blank of mark's line. |
| 196 | The `!` Key | `!{motion}{filter}` | Filter text through an external command. |
| 197 | The `@` Key | `@{reg}` | Execute macro from register. |
| 198 | The `#` Key | `#` | Search backward for word under cursor. |
| 199 | The `*` Key | `*` | Search forward for word under cursor. |
| 200 | The `&` Key | `&` | Repeat last `:s` substitution. |
| 201 | The `(` and `)` Keys | `(` `)` | Move by sentences. |
| 202 | The `{` and `}` Keys | `{` `}` | Move by paragraphs. |
| 203 | The `[` and `]` Keys | `[` `]` | Bracket command prefix (covered in depth later). |
| 204 | The `-` and `+` Keys | `-` `+` | Previous/next line, first non-blank. |
| 205 | The `_` Key | `_` | Like `+` but to current line (count - 1 lines down). |
| 206 | The `=` Key | `={motion}` | Auto-indent lines. |
| 207 | The `<` and `>` Keys | `<{motion}` `>{motion}` | Unindent / indent. |
| 208 | The `\|` Key | `{count}\|` | Go to column N. |
| 209 | The `\` Key | `\` | Leader key (reserved for custom mappings). |
| 210 | The `:` Key | `:` | Enter command-line (Ex) mode. |
| 211 | The `;` Key | `;` | Repeat last `f`/`t`/`F`/`T` same direction. |
| 212 | The `,` Key | `,` | Repeat last `f`/`t`/`F`/`T` opposite direction. |
| 213 | The `"` Key | `"{reg}` | Specify register for next yank/delete/put. |
| 214 | The `.` Key | `.` | Repeat the last change. |
| 215 | The `/` Key | `/{pattern}` | Search forward. |
| 216 | The `?` Key | `?{pattern}` | Search backward. |
| 217 | The `Space` Key | `Space` | Move right (synonym for `l`). |
| 218 | The `Backspace` Key | `BS` | Move left (synonym for `h`). |

---

## Part 8 — Walking the Keyboard: Ctrl Keys (Lessons 219–248)

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 219 | `Ctrl-A` | `Ctrl-A` | Increment the number at/after the cursor. |
| 220 | `Ctrl-X` | `Ctrl-X` | Decrement the number at/after the cursor. |
| 221 | `Ctrl-B` | `Ctrl-B` | Scroll one full page backward. |
| 222 | `Ctrl-F` | `Ctrl-F` | Scroll one full page forward. |
| 223 | `Ctrl-U` | `Ctrl-U` | Scroll half page up. |
| 224 | `Ctrl-D` | `Ctrl-D` | Scroll half page down. |
| 225 | `Ctrl-E` | `Ctrl-E` | Scroll one line up (window moves, cursor stays). |
| 226 | `Ctrl-Y` | `Ctrl-Y` | Scroll one line down (window moves, cursor stays). |
| 227 | `Ctrl-O` | `Ctrl-O` | Older position in jump list. |
| 228 | `Ctrl-I` / `Tab` | `Ctrl-I` | Newer position in jump list. |
| 229 | `Ctrl-R` | `Ctrl-R` | Redo. |
| 230 | `Ctrl-G` | `Ctrl-G` | Show file info (name, line count, position). |
| 231 | `Ctrl-L` | `Ctrl-L` | Redraw the screen. |
| 232 | `Ctrl-V` | `Ctrl-V` | Start visual block mode. |
| 233 | `Ctrl-C` | `Ctrl-C` | Interrupt / cancel current command. |
| 234 | `Ctrl-Z` | `Ctrl-Z` | Suspend Vim (return with `fg`). |
| 235 | `Ctrl-]` | `Ctrl-]` | Jump to tag definition under cursor. |
| 236 | `Ctrl-T` | `Ctrl-T` | Jump to older tag in tag stack. |
| 237 | `Ctrl-^` | `Ctrl-^` | Edit alternate (previous) file. |
| 238 | `Ctrl-W` Prefix | `Ctrl-W` | Window command prefix (covered in depth later). |
| 239 | `Ctrl-N` / `Ctrl-P` | `Ctrl-N` `Ctrl-P` | Same as `j` / `k` in normal mode. |
| 240 | `Ctrl-H` | `Ctrl-H` | Same as `h` (left). |
| 241 | `Ctrl-J` / `Ctrl-M` | `Ctrl-J` `Ctrl-M` | Same as `j` / `Enter`. |

### Line Scrolling Refinements

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 242 | `zz` — Center Cursor | `zz` | Scroll so cursor is at center of screen. |
| 243 | `zt` — Cursor to Top | `zt` | Scroll so cursor is at top of screen. |
| 244 | `zb` — Cursor to Bottom | `zb` | Scroll so cursor is at bottom of screen. |
| 245 | `z.` — Center, First Non-Blank | `z.` | Like `zz` but cursor goes to first non-blank. |
| 246 | `z+` — Top, First Non-Blank | `z+` | Like `zt` but cursor on first non-blank. |
| 247 | `z-` — Bottom, First Non-Blank | `z-` | Like `zb` but cursor on first non-blank. |
| 248 | `z{height}Enter` | `z{height}Enter` | Set window height. |

---

## Part 9 — The `g` Commands (Lessons 249–285)

_The `g` prefix is a second entire keyboard of commands._

### g + Lowercase

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 249 | `ga` — ASCII Value | `ga` | Print the ASCII/Unicode value of char under cursor. |
| 250 | `gd` — Go to Definition | `gd` | Jump to local definition of word under cursor. |
| 251 | `gD` — Go to Definition (File) | `gD` | Jump to definition in the current file. |
| 252 | `ge` — End of Previous Word | `ge` | Move backward to end of previous word. |
| 253 | `gE` — End of Previous WORD | `gE` | Move backward to end of previous WORD. |
| 254 | `gf` — Go to File | `gf` | Open the file whose name is under the cursor. |
| 255 | `gF` — Go to File at Line | `gF` | Like `gf` but also jump to the line number. |
| 256 | `gg` — Go to Top | `gg` | Go to first line (or line N). |
| 257 | `gj` / `gk` — Screen Lines | `gj` `gk` | Move by screen lines when lines wrap. |
| 258 | `gm` / `gM` — Middle of Line | `gm` `gM` | Go to middle of screen line / middle of text. |
| 259 | `gn` / `gN` — Select Match | `gn` `gN` | Find next/previous search match and visually select it. |
| 260 | `go` — Byte Offset | `go` | Go to byte N in the buffer. |
| 261 | `gp` / `gP` — Put and Move | `gp` `gP` | Like `p`/`P` but leave cursor after pasted text. |
| 262 | `gq` — Format | `gq{motion}` | Format text (wrap to textwidth). |
| 263 | `gw` — Format, Keep Cursor | `gw{motion}` | Like `gq` but keep cursor position. |
| 264 | `gr` — Virtual Replace | `gr{char}` | Replace N chars virtually (respects tabs). |
| 265 | `gs` — Sleep | `gs` | Go to sleep for N seconds. (Yes, really.) |
| 266 | `gt` / `gT` — Tabs | `gt` `gT` | Next / previous tab page. |
| 267 | `gu` — Lowercase | `gu{motion}` | Make motion text lowercase. |
| 268 | `gU` — Uppercase | `gU{motion}` | Make motion text uppercase. |
| 269 | `g~` — Toggle Case | `g~{motion}` | Toggle case over motion. |
| 270 | `gv` — Reselect Visual | `gv` | Reselect the previous visual area. |
| 271 | `gx` — Open URL/File | `gx` | Open file/URL under cursor with system app. |

### g + Uppercase (Less Common)

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 272 | `gH` — Select Line Mode | `gH` | Start select line mode (rare). |
| 273 | `gh` — Select Mode | `gh` | Start select mode (rare). |
| 274 | `gI` — Insert at Column 1 | `gI` | Like `I` but always at column 1. |
| 275 | `gi` — Insert at Last Insert | `gi` | Go to where you last left insert mode and enter insert mode. |
| 276 | `gJ` — Join Without Space | `gJ` | Join lines without adding a space. |
| 277 | `gQ` — Ex Mode (Vim Editing) | `gQ` | Enter Ex mode with Vim-style editing. |
| 278 | `gR` — Virtual Replace Mode | `gR` | Enter virtual replace mode. |
| 279 | `gV` — Don't Reselect | `gV` | Prevent reselection in select mode mappings. |

### g + Symbols

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 280 | `g*` / `g#` — Partial Word Search | `g*` `g#` | Like `*`/`#` but without word boundary matching. |
| 281 | `g$` / `g0` / `g^` / `g_` — Line Edges | `g$` `g0` `g^` `g_` | End / start / first non-blank of screen line. `g_` = last non-blank of line. |
| 282 | `g&` — Repeat Substitution Globally | `g&` | Repeat last `:s` on all lines. |
| 283 | `g;` / `g,` — Change List | `g;` `g,` | Navigate the change list (older / newer). |
| 284 | `g?` — ROT13 | `g?{motion}` `g??` | ROT13 encode text. |
| 285 | `g@` — Operator Function | `g@{motion}` | Call the `operatorfunc`. |

---

## Part 10 — The `z` Commands (Lessons 286–316)

### Scrolling with `z`

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 286 | `zz` — Center | `zz` | Scroll cursor line to center. |
| 287 | `zt` — Top | `zt` | Scroll cursor line to top. |
| 288 | `zb` — Bottom | `zb` | Scroll cursor line to bottom. |
| 289 | `z.` `z+` `z-` `z^` | `z.` `z+` `z-` `z^` | Scroll variants with cursor on first non-blank. |
| 290 | `zs` / `ze` — Horizontal Scroll | `zs` `ze` | Scroll so cursor is at start / end of screen (nowrap). |
| 291 | `zh` / `zl` — Scroll Characters | `zh` `zl` | Scroll N characters right / left (nowrap). |
| 292 | `zH` / `zL` — Scroll Half-Screen | `zH` `zL` | Scroll half a screen width right / left. |

### Folds

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 293 | `zo` — Open Fold | `zo` | Open one fold under the cursor. |
| 294 | `zc` — Close Fold | `zc` | Close one fold under the cursor. |
| 295 | `za` — Toggle Fold | `za` | Toggle fold open/closed. |
| 296 | `zO` `zC` `zA` — Recursive | `zO` `zC` `zA` | Open / close / toggle folds recursively. |
| 297 | `zv` — View Cursor Line | `zv` | Open enough folds to show the cursor line. |
| 298 | `zr` / `zm` — Fold Level | `zr` `zm` | Increase / decrease fold level by one. |
| 299 | `zR` / `zM` — All Folds | `zR` `zM` | Open all folds / close all folds. |
| 300 | `zx` / `zX` — Reapply Fold Level | `zx` `zX` | Reapply `foldlevel`, open folds for cursor. |
| 301 | `zn` / `zN` / `zi` — Enable/Disable | `zn` `zN` `zi` | Disable / enable / toggle folding. |
| 302 | `zf` — Create Manual Fold | `zf{motion}` | Create a fold over a motion. |
| 303 | `zF` — Create Fold N Lines | `{count}zF` | Create a fold for N lines. |
| 304 | `zd` / `zD` — Delete Fold | `zd` `zD` | Delete fold / delete folds recursively. |
| 305 | `zE` — Eliminate All Folds | `zE` | Remove all manually created folds. |
| 306 | `zj` / `zk` — Navigate Folds | `zj` `zk` | Move to next / previous fold. |
| 307 | `[z` / `]z` — Fold Start/End | `[z` `]z` | Move to start / end of current open fold. |

### Spelling with `z`

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 308 | `z=` — Spelling Suggestions | `z=` | Show spelling suggestions for word under cursor. |
| 309 | `zg` — Mark Correct | `zg` | Mark word as correctly spelled. |
| 310 | `zw` — Mark Incorrect | `zw` | Mark word as incorrectly spelled. |
| 311 | `zug` / `zuw` — Undo Spelling Mark | `zug` `zuw` | Undo `zg` / undo `zw`. |
| 312 | `zG` / `zW` — Temporary Spelling | `zG` `zW` | Temporarily mark word correct / incorrect. |
| 313 | `zuG` / `zuW` — Undo Temp Spelling | `zuG` `zuW` | Undo `zG` / undo `zW`. |
| 314 | `[s` / `]s` — Navigate Misspelled | `[s` `]s` | Previous / next misspelled word. |

### Other `z` Commands

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 315 | `zp` / `zy` — Block Paste/Yank | `zp` `zP` `zy` | Put/yank in block mode without trailing spaces. |
| 316 | `z=` in Practice | `z=` | Pick a suggestion and apply it. |

---

## Part 11 — Bracket Commands `[` and `]` (Lessons 317–333)

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 317 | `[(` / `])` — Unmatched Parens | `[(` `])` | Jump to previous/next unmatched `(` / `)`. |
| 318 | `[{` / `]}` — Unmatched Braces | `[{` `]}` | Jump to previous/next unmatched `{` / `}`. |
| 319 | `[[` / `]]` — Sections Forward/Back | `[[` `]]` | Jump by sections (function boundaries in C). |
| 320 | `[]` / `][` — SECTIONS | `[]` `][` | Jump by SECTIONS. |
| 321 | `[m` / `]m` — Member Functions | `[m` `]m` | Jump to start/end of member functions (Java/C). |
| 322 | `[c` / `]c` — Diff Changes | `[c` `]c` | Jump to previous/next diff change. |
| 323 | `[s` / `]s` — Misspelled Words | `[s` `]s` | Jump to previous/next misspelled word. |
| 324 | `[#` / `]#` — Preprocessor | `[#` `]#` | Jump to previous/next unmatched `#if`/`#endif`. |
| 325 | `[*` `[/` / `]*` `]/` — Comments | `[*` `]*` | Jump to start/end of C comments. |
| 326 | `['` `[`` / `]'` `]`` — Marks | `['` `]'` | Jump to previous/next lowercase mark. |
| 327 | `[p` / `]p` — Put with Indent | `[p` `]p` | Like `P`/`p` but adjust indent to current line. |
| 328 | `[z` / `]z` — Fold Boundaries | `[z` `]z` | Start / end of current open fold. |
| 329 | `[d` / `]d` — Show Define | `[d` `]d` | Show first `#define` matching word under cursor. |
| 330 | `[D` / `]D` — List Defines | `[D` `]D` | List all `#define`s matching word under cursor. |
| 331 | `[i` / `]i` — Show Include | `[i` `]i` | Show first line matching word in includes. |
| 332 | `[I` / `]I` — List Includes | `[I` `]I` | List all lines matching word in includes. |
| 333 | `[f` / `]f` — Go to File | `[f` `]f` | Same as `gf` — open file under cursor. |

---

## Part 12 — Window Commands `Ctrl-W` (Lessons 334–365)

### Creating Splits

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 334 | `Ctrl-W s` — Horizontal Split | `Ctrl-W s` | Split current window horizontally. |
| 335 | `Ctrl-W v` — Vertical Split | `Ctrl-W v` | Split current window vertically. |
| 336 | `Ctrl-W n` — New Window | `Ctrl-W n` | Open a new empty window. |

### Navigating Splits

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 337 | `Ctrl-W h/j/k/l` — Navigate | `Ctrl-W h/j/k/l` | Move to left/down/up/right window. |
| 338 | `Ctrl-W w` / `Ctrl-W W` — Cycle | `Ctrl-W w` `Ctrl-W W` | Cycle to next / previous window. |
| 339 | `Ctrl-W t` / `Ctrl-W b` — Top/Bottom | `Ctrl-W t` `Ctrl-W b` | Go to top-left / bottom-right window. |
| 340 | `Ctrl-W p` — Previous Window | `Ctrl-W p` | Go to last accessed window. |

### Closing Windows

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 341 | `Ctrl-W c` — Close | `Ctrl-W c` | Close current window. |
| 342 | `Ctrl-W q` — Quit | `Ctrl-W q` | Quit current window (closes Vim if last). |
| 343 | `Ctrl-W o` — Only | `Ctrl-W o` | Close all other windows. |

### Moving Windows

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 344 | `Ctrl-W H/J/K/L` — Move Window | `Ctrl-W H/J/K/L` | Move window to far left/bottom/top/right. |
| 345 | `Ctrl-W r/R` — Rotate | `Ctrl-W r` `Ctrl-W R` | Rotate windows down / up. |
| 346 | `Ctrl-W x` — Exchange | `Ctrl-W x` | Exchange current window with next. |
| 347 | `Ctrl-W T` — Window to Tab | `Ctrl-W T` | Move current window to a new tab. |

### Resizing Windows

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 348 | `Ctrl-W +` / `Ctrl-W -` — Height | `Ctrl-W +` `Ctrl-W -` | Increase / decrease window height. |
| 349 | `Ctrl-W >` / `Ctrl-W <` — Width | `Ctrl-W >` `Ctrl-W <` | Increase / decrease window width. |
| 350 | `Ctrl-W =` — Equalize | `Ctrl-W =` | Make all windows equal size. |
| 351 | `Ctrl-W _` — Max Height | `Ctrl-W _` | Set window height to N (default: maximum). |
| 352 | `Ctrl-W \|` — Max Width | `Ctrl-W \|` | Set window width to N (default: maximum). |

### Split + Jump

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 353 | `Ctrl-W d` — Definition | `Ctrl-W d` | Split and jump to definition. |
| 354 | `Ctrl-W f` — File | `Ctrl-W f` | Split and open file under cursor. |
| 355 | `Ctrl-W F` — File at Line | `Ctrl-W F` | Split and open file, jump to line. |
| 356 | `Ctrl-W i` — Declaration | `Ctrl-W i` | Split and jump to declaration. |
| 357 | `Ctrl-W ]` — Tag | `Ctrl-W ]` | Split and jump to tag. |
| 358 | `Ctrl-W }` — Preview Tag | `Ctrl-W }` | Show tag in preview window. |
| 359 | `Ctrl-W P` — Preview Window | `Ctrl-W P` | Go to preview window. |
| 360 | `Ctrl-W z` — Close Preview | `Ctrl-W z` | Close preview window. |

### Tab Commands via `Ctrl-W g`

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 361 | `Ctrl-W gf` — File in New Tab | `Ctrl-W gf` | Open file under cursor in a new tab. |
| 362 | `Ctrl-W gF` — File in Tab at Line | `Ctrl-W gF` | Open file in new tab and jump to line. |
| 363 | `Ctrl-W gt` / `Ctrl-W gT` — Tabs | `Ctrl-W gt` `Ctrl-W gT` | Next / previous tab. |
| 364 | `Ctrl-W g<Tab>` — Last Tab | `Ctrl-W g<Tab>` | Go to last accessed tab. |
| 365 | `Ctrl-W ^` — Alternate File | `Ctrl-W ^` | Split and edit alternate file. |

---

## Part 13 — Insert Mode Keys (Lessons 366–395)

_Keys that work while you're in insert mode._

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 366 | `Escape` / `Ctrl-[` — Leave Insert | `Esc` `Ctrl-[` | Return to normal mode. |
| 367 | `Ctrl-C` — Quick Leave | `Ctrl-C` | Leave insert mode (no abbreviation check). |
| 368 | `Ctrl-O` — One Normal Command | `Ctrl-O` | Execute one normal mode command, then return to insert. |
| 369 | `Ctrl-H` / `Backspace` — Delete Char | `Ctrl-H` `BS` | Delete character before cursor. |
| 370 | `Ctrl-W` — Delete Word | `Ctrl-W` | Delete the word before the cursor. |
| 371 | `Ctrl-U` — Delete Line | `Ctrl-U` | Delete all text on current line before cursor. |
| 372 | `Ctrl-T` — Indent | `Ctrl-T` | Insert one shiftwidth of indent. |
| 373 | `Ctrl-D` — Unindent | `Ctrl-D` | Delete one shiftwidth of indent. |
| 374 | `Ctrl-R {reg}` — Insert Register | `Ctrl-R` | Insert contents of a register. |
| 375 | `Ctrl-A` — Insert Previous | `Ctrl-A` | Re-insert previously inserted text. |
| 376 | `Ctrl-@` — Insert Previous + Leave | `Ctrl-@` | Insert previously inserted text and leave insert mode. |
| 377 | `Ctrl-E` — Copy from Below | `Ctrl-E` | Insert the character from the line below. |
| 378 | `Ctrl-Y` — Copy from Above | `Ctrl-Y` | Insert the character from the line above. |
| 379 | `Ctrl-N` — Autocomplete Next | `Ctrl-N` | Keyword completion — next match. |
| 380 | `Ctrl-P` — Autocomplete Prev | `Ctrl-P` | Keyword completion — previous match. |
| 381 | `Ctrl-K` — Digraph | `Ctrl-K {c1}{c2}` | Insert a digraph (special character). |
| 382 | `Ctrl-V` — Literal Character | `Ctrl-V {char}` | Insert the next character literally. |
| 383 | `Ctrl-G u` — Break Undo | `Ctrl-G u` | Start a new undo sequence. |
| 384 | `Ctrl-G U` — Don't Break Undo | `Ctrl-G U{motion}` | Next cursor motion won't break undo. |
| 385 | `Ctrl-G j/k` — Move in Insert | `Ctrl-G j` `Ctrl-G k` | Move down/up to column where insert started. |

### Insert Mode Completion (`Ctrl-X` submenu)

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 386 | `Ctrl-X Ctrl-L` — Line Completion | `Ctrl-X Ctrl-L` | Complete whole lines. |
| 387 | `Ctrl-X Ctrl-F` — File Completion | `Ctrl-X Ctrl-F` | Complete file names. |
| 388 | `Ctrl-X Ctrl-K` — Dictionary | `Ctrl-X Ctrl-K` | Complete from dictionary. |
| 389 | `Ctrl-X Ctrl-T` — Thesaurus | `Ctrl-X Ctrl-T` | Complete from thesaurus. |
| 390 | `Ctrl-X Ctrl-I` — Identifier | `Ctrl-X Ctrl-I` | Complete identifiers. |
| 391 | `Ctrl-X Ctrl-D` — Define | `Ctrl-X Ctrl-D` | Complete defined identifiers. |
| 392 | `Ctrl-X Ctrl-]` — Tags | `Ctrl-X Ctrl-]` | Complete tags. |
| 393 | `Ctrl-X Ctrl-O` — Omni | `Ctrl-X Ctrl-O` | Omni completion. |
| 394 | `Ctrl-X Ctrl-S` — Spelling | `Ctrl-X Ctrl-S` | Spelling suggestions. |
| 395 | `Ctrl-X Ctrl-V` — Vim Command | `Ctrl-X Ctrl-V` | Complete like on the command line. |

---

## Part 14 — Ex Commands Essentials (Lessons 396–430)

_The colon commands you'll use most often._

### File Operations

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 396 | `:w` — Write | `:w` | Save the file. |
| 397 | `:w {file}` — Write As | `:w {file}` | Save to a different filename. |
| 398 | `:q` — Quit | `:q` | Quit (fails if unsaved changes). |
| 399 | `:q!` — Force Quit | `:q!` | Quit discarding changes. |
| 400 | `:wq` / `:x` — Write and Quit | `:wq` `:x` | Save and quit. |
| 401 | `:e {file}` — Edit File | `:e {file}` | Open a file. |
| 402 | `:e!` — Revert | `:e!` | Revert to the saved version. |
| 403 | `:r {file}` — Read File | `:r {file}` | Insert contents of a file below cursor. |
| 404 | `:r !{cmd}` — Read Command | `:r !{cmd}` | Insert output of a shell command. |

### Search and Replace

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 405 | `:s/old/new/` — Substitute | `:s/old/new/` | Replace first occurrence on current line. |
| 406 | `:s/old/new/g` — Substitute All | `:s/old/new/g` | Replace all occurrences on current line. |
| 407 | `:%s/old/new/g` — File-Wide | `:%s/old/new/g` | Replace all occurrences in the entire file. |
| 408 | `:%s/old/new/gc` — Confirm | `:%s/old/new/gc` | Replace with confirmation for each match. |
| 409 | `:s` with Ranges | `:'<,'>s/old/new/g` | Substitute within a visual selection or line range. |

### Buffers and Arguments

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 410 | `:ls` / `:buffers` — List Buffers | `:ls` | Show all open buffers. |
| 411 | `:b {N}` / `:b {name}` — Switch | `:b 3` `:b foo` | Switch to a buffer by number or partial name. |
| 412 | `:bn` / `:bp` — Next/Prev Buffer | `:bn` `:bp` | Cycle through buffers. |
| 413 | `:bd` — Delete Buffer | `:bd` | Remove a buffer from the list. |
| 414 | `:args` — Argument List | `:args` | Show the argument list. |

### Tabs

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 415 | `:tabnew` — New Tab | `:tabnew` | Open a new tab. |
| 416 | `:tabnext` / `:tabprev` | `:tabnext` `:tabprev` | Cycle tabs (also `gt` / `gT`). |
| 417 | `:tabclose` — Close Tab | `:tabclose` | Close current tab. |
| 418 | `:tabonly` — Only Tab | `:tabonly` | Close all other tabs. |

### Running External Commands

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 419 | `:!{cmd}` — Shell Command | `:!ls` | Run a shell command. |
| 420 | `:!!` — Repeat Last | `:!!` | Repeat the last shell command. |
| 421 | `:{range}!{filter}` — Filter | `:%!sort` | Filter lines through an external program. |
| 422 | `:terminal` — Terminal | `:terminal` | Open a terminal inside Vim. |

### Additional File Commands

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| —   | `:sav {file}` — Save As | `:sav {file}` | Save buffer to a new file and switch to editing it (unlike `:w {file}` which keeps the original). |
| —   | `:[range]sort` — Sort Lines | `:sort` `:sort!` `:sort n` `:sort u` | Sort lines (`!` = reverse, `n` = numeric, `i` = ignore-case, `u` = unique). |

### Settings

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 423 | `:set number` — Line Numbers | `:set nu` `:set nonu` | Toggle line numbers. |
| 424 | `:set relativenumber` | `:set rnu` `:set nornu` | Toggle relative line numbers. |
| 425 | `:set hlsearch` — Highlight | `:set hls` `:set nohls` | Toggle search highlighting. |
| 426 | `:set incsearch` — Incremental | `:set is` | Highlight matches as you type. |
| 427 | `:set ignorecase` / `smartcase` | `:set ic` `:set scs` | Case-insensitive / smart-case search. |
| 428 | `:set wrap` / `nowrap` | `:set wrap` `:set nowrap` | Toggle line wrapping. |
| 429 | `:noh` — Clear Highlight | `:noh` | Clear current search highlighting. |
| 430 | `:set list` — Show Invisible | `:set list` `:set nolist` | Show tabs, trailing spaces, etc. |

---

## Part 15 — Visual Mode in Depth (Lessons 431–445)

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 431 | `v` — Charwise | `v` | Select characters. Any motion extends selection. |
| 432 | `V` — Linewise | `V` | Select whole lines. |
| 433 | `Ctrl-V` — Blockwise | `Ctrl-V` | Select a rectangular column block. |
| 434 | `o` — Other End | `o` | Jump to the other end of the selection. |
| 435 | `O` — Other Corner (Block) | `O` | In block mode, move to other corner horizontally. |
| 436 | `gv` — Reselect | `gv` | Reselect the previous visual area. |
| 437 | `v_d` / `v_c` — Delete/Change | `d` `c` | Delete or change the selected text. |
| 438 | `v_y` — Yank Selection | `y` | Yank the selected text. |
| 439 | `v_r` — Replace Selection | `r{char}` | Replace every selected character with {char}. |
| 440 | `v_J` — Join Selection | `J` | Join selected lines. |
| 441 | `v_u` / `v_U` / `v_~` — Case | `u` `U` `~` | Lowercase / uppercase / toggle selection. |
| 442 | `v_>` / `v_<` / `v_=` — Indent | `>` `<` `=` | Indent / unindent / auto-indent selection. |
| 443 | Block Insert | `Ctrl-V` → select → `I` | Insert text at the start of each line in block. |
| 444 | Block Append | `Ctrl-V` → select → `A` | Append text at the end of each line in block. |
| 445 | `:'<,'>` — Visual Range | `:'<,'>` | After visual selection, `:` automatically adds the range. |

---

## Part 16 — Command-Line Mode Tips (Lessons 446–460)

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 446 | `q:` — Command History Window | `q:` | Open the command-line history in an editable window. |
| 447 | `q/` / `q?` — Search History | `q/` `q?` | Edit search history in a window. |
| 448 | `Ctrl-D` — Show Completions | `Ctrl-D` (in `:`) | List all possible completions. |
| 449 | `Tab` — Complete Command | `Tab` (in `:`) | Tab-complete commands, files, etc. |
| 450 | `Ctrl-R {reg}` — Insert Register | `Ctrl-R` (in `:`) | Insert a register's contents into the command line. |
| 451 | `Ctrl-R Ctrl-W` — Insert Word | `Ctrl-R Ctrl-W` | Insert the word under cursor into command line. |
| 452 | `Ctrl-B` / `Ctrl-E` — Start/End | `Ctrl-B` `Ctrl-E` (in `:`) | Move to beginning / end of command line. |
| 453 | `Ctrl-U` — Clear Line | `Ctrl-U` (in `:`) | Delete entire command line. |
| 454 | `Ctrl-W` — Delete Word | `Ctrl-W` (in `:`) | Delete word before cursor in command line. |
| 455 | Up/Down — History | `Up` `Down` (in `:`) | Recall previous/next commands matching prefix. |
| 456 | `@:` — Repeat Last Command | `@:` | Repeat the last Ex command. |
| 457 | `:norm` — Normal on Lines | `:%norm I//` | Run normal-mode commands on every line. |
| 458 | `:g/{pattern}/{cmd}` — Global | `:g/TODO/d` | Execute command on all matching lines. |
| 459 | `:v/{pattern}/{cmd}` — Inverse | `:v/keep/d` | Execute command on all non-matching lines. |
| 460 | `Ctrl-F` — Edit Command | `Ctrl-F` (in `:`) | Open command line in editable window. |

---

## Part 17 — Practical Patterns & Tips (Lessons 461–480)

_Real-world editing patterns that combine what you've learned._

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 461 | `xp` — Transpose Characters | `xp` | Swap two characters. |
| 462 | `deep` — Delete to End × 2 | `deep` | Delete to end of word, paste, paste. |
| 463 | `ddp` — Swap Lines Down | `ddp` | Move current line down one. |
| 464 | `ddP` — Swap Lines Up | `ddP` | Move current line up one (technically: delete, paste above). |
| 465 | `yyp` — Duplicate Line | `yyp` | Copy current line and paste below. |
| 466 | Star-Dot Pattern | `*cw{new}Esc` then `n.` | Find word, change it, repeat with `n.` |
| 467 | `:%normal I//` | `:%norm I//` | Comment out every line (prepend `//`). |
| 468 | `:%normal ^x` | `:%norm ^x` | Delete first char of every line. |
| 469 | Visual Block Comment | `Ctrl-V` → select → `I//Esc` | Comment a block of lines. |
| 470 | `Ctrl-A` / `Ctrl-X` Incrementing | `Ctrl-A` `Ctrl-X` | Increment/decrement numbers. Works with counts! |
| 471 | `g Ctrl-A` in Visual | `g Ctrl-A` | Create incrementing number sequences in visual block. |
| 472 | Align Text with `:norm` | `:'<,'>norm 20\|r\|` | Align text to a column using `:norm`. |
| 473 | The Useless `_` Key | `_` | Remap it! It's basically `+` but for the current line. |
| 474 | Record-and-Apply Macro | `qa...q` then `:%norm @a` | Record a macro and apply it to every line. |
| 475 | `Ctrl-O` in Insert Mode | `Ctrl-O dd` | Delete a line without leaving insert mode. |
| 476 | Map `Y` to `y$` | `:map Y y$` | Make `Y` consistent with `C` and `D`. |
| 477 | `gn` with Dot | `/pattern` then `cgn{text}Esc` then `.` | Change next match, dot to repeat on subsequent matches. |
| 478 | Numbered Register Put | `"1p...` | Put from register 1, then `.` advances through `"2`, `"3`, etc. |
| 479 | `do` / `dp` — Diff | `do` `dp` | Diff obtain / diff put (in diff mode). |
| 480 | External Filtering | `!ip sort` | Sort the current paragraph through `sort`. |

---

## Part 18 — Advanced Topics (Lessons 481–500)

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 481 | Undo Branches | `g-` `g+` | Navigate the full undo tree (not just linear). |
| 482 | `:earlier` / `:later` | `:earlier 5m` | Go back/forward in time. |
| 483 | The `.` Register | `".` | Contains the last inserted text. |
| 484 | The `:` Register | `":` | Contains the last Ex command. |
| 485 | The `/` Register | `"/` | Contains the last search pattern. |
| 486 | The `%` Register | `"%` | Contains the current filename. |
| 487 | The `#` Register | `"#` | Contains the alternate filename. |
| 488 | The `=` Register | `"=` | Expression register — evaluate an expression. |
| 489 | Operator-Pending Mode | `d`, `c`, `y` ... waiting | What happens between operator and motion. |
| 490 | `g@` — Custom Operator | `g@{motion}` | Create your own operators with `operatorfunc`. |
| 491 | Terminal Mode | `:term` → `Ctrl-\ Ctrl-N` | Enter/exit terminal mode. |
| 492 | `ga` / `g8` — Character Info | `ga` `g8` | Show ASCII/Unicode / hex value of char. |
| 493 | `:set fdm=indent` — Fold by Indent | `:set fdm=indent` | Set fold method to indent-based. |
| 494 | `:set fdm=syntax` — Fold by Syntax | `:set fdm=syntax` | Set fold method to syntax-based. |
| 495 | `:mkview` / `:loadview` — Save Folds | `:mkview` `:loadview` | Save and restore fold state. |
| 496 | `gx` — Open URL | `gx` | Open URL or file under cursor with system app. |
| 497 | `g<` — Previous Output | `g<` | Redisplay previous command output. |
| 498 | The `vimrc` / `init.lua` | — | Where to put your personal configuration. |
| 499 | `:help` — The Help System | `:help` `:h {topic}` | Navigate Vim's built-in help. |
| 500 | What's Next? | — | Plugins, LSP, Treesitter, and the endless journey. |

---

## Part 19 — Tmux & Shell (Lessons 501–545)

_Tmux is the perfect partner for Vim. Learn to split your terminal, manage windows, and become a keyboard-only powerhouse. The shell is your launchpad._

### Getting Started

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 501 | What Is tmux? | — | Terminal multiplexer: one terminal, many sessions, windows, and panes. |
| 502 | Starting tmux | `tmux` | Launch tmux from the shell. Notice the green status bar at the bottom. |
| 503 | The Prefix Key | `Ctrl-B` | All tmux commands start with the prefix key. Press `Ctrl-B`, release, then press the command key. |
| 504 | tmux Help | `Ctrl-B ?` | Show all key bindings in a scrollable list. The ultimate cheat sheet — always one keystroke away. |

### Panes

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 505 | Split Horizontally | `Ctrl-B "` | Split the current pane into top and bottom. |
| 506 | Split Vertically | `Ctrl-B %` | Split the current pane into left and right. |
| 507 | Navigate Panes (Arrows) | `Ctrl-B ↑/↓/←/→` | Move focus to the pane in that direction. |
| 508 | Navigate Panes (Vim Keys) | `Ctrl-B h/j/k/l` | Same as arrows but vim-style. No hand movement! |
| 509 | Cycle Panes | `Ctrl-B o` | Move focus to the next pane in order. |
| 510 | Last Active Pane | `Ctrl-B ;` | Toggle back to the previously active pane. |
| 511 | Close a Pane | `Ctrl-B x` | Kill the active pane (press `y` to confirm). |
| 512 | Zoom a Pane | `Ctrl-B z` | Toggle zoom — pane fills the entire window. Press again to unzoom. |
| 513 | Resize Panes | `Ctrl-B Ctrl-↑/↓/←/→` | Resize the active pane by one cell at a time. |
| 514 | Swap Panes | `Ctrl-B {` / `Ctrl-B }` | Swap the active pane with the previous or next pane. |
| 515 | Break Pane to Window | `Ctrl-B !` | Move the current pane into its own new window. |
| 516 | Pane Numbers | `Ctrl-B q` | Show pane number overlays; press `0`–`9` to jump to that pane. |

### Windows

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 517 | Create a Window | `Ctrl-B c` | Open a new window with a fresh shell. |
| 518 | Next / Previous Window | `Ctrl-B n` / `Ctrl-B p` | Cycle forward and backward through windows. |
| 519 | Switch to Window N | `Ctrl-B 0`–`9` | Jump directly to a numbered window. |
| 520 | Last Active Window | `Ctrl-B L` | Toggle to the most recently active window. |
| 521 | Rename Window | `Ctrl-B ,` | Give the current window a meaningful name. |
| 522 | Close a Window | `Ctrl-B &` | Kill the current window and all its panes (press `y` to confirm). |
| 523 | Window Chooser | `Ctrl-B w` | Interactive list — navigate with `j`/`k` and press `Enter` to select. |
| 524 | Cycle Layouts | `Ctrl-B Space` | Rearrange panes through preset layout patterns. |

### Sessions & Detach

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 525 | Detach from tmux | `Ctrl-B d` | Detach — tmux keeps running in the background. |
| 526 | The Command Prompt | `Ctrl-B :` | Type tmux commands directly (e.g. `split-window -h`, `new-session work`). |
| 527 | Multiple Sessions | `new-session` / `switch-client -t` | Create and switch between named sessions from the command prompt. `list-sessions` (or `ls`) shows them all. |

### Copy Mode & Extras

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 528 | Enter Copy Mode | `Ctrl-B [` | Read-only scrollback view with vim-style navigation. `Ctrl-B PageUp` also works. Press `q` or `Escape` to exit. |
| 529 | Copy Mode Navigation | `h/j/k/l` `0/$` `w/b` `g/G` | Navigate with all the Vim motions you already know. `Ctrl-F/B/D/U` for page/half-page scrolling. |
| 530 | Copy Mode Visual Selection | `v` | Toggle visual selection in copy mode — highlight text as you navigate. |
| 531 | Clock Mode | `Ctrl-B t` | Show a fullscreen ASCII art clock (press any key to exit). |
| 532 | The Status Bar | — | Reading the tmux status bar: session name, window list (`*` = active), time, date. |

### Shell Essentials

| #   | Title | Keys | Description |
|-----|-------|------|-------------|
| 533 | The Shell Prompt | — | Your command-line home base. Type a command, press `Enter`. `↑`/`↓` recall command history. |
| 534 | File Management | `ls` `cat` `touch` `rm` `cp` `mv` | Create, view, copy, move, and delete files from the shell. |
| 535 | Creating Files with Content | `echo "text" > file` | Write text into a file. Use `>>` to append instead of overwrite. |
| 536 | Shell Utilities | `wc` `grep` `sort` `history` `date` | Count words, search files, sort lines, view history, check the date. |
| 537 | Shell Shortcuts | `clear` `help` `exit` | Clear the screen, show available commands, exit the shell. `Ctrl-D` on an empty line also exits. |
| 538 | Tab Completion | `Tab` | Complete command names and filenames. Saves typing and prevents typos. |
| 539 | Shell Editing Keys | `Ctrl-A` `Ctrl-E` `Ctrl-K` `Ctrl-U` `Ctrl-W` | Jump to start/end of line, delete to end/start of line, delete word — standard readline keys. |
| 540 | Cancel & Clear | `Ctrl-C` `Ctrl-L` | Cancel the current input line, or clear the screen (same as `clear`). |
| 541 | Opening Vim | `nvim file.py` | Launch Vim from the shell. `vim` and `vi` also work. |
| 542 | Vi-Mode in the Shell | `set -o vi` | Enable vim-style line editing at the shell prompt. Press `Escape` for normal mode. `set -o emacs` to go back. |
| 543 | Vi-Mode Editing | `Esc` → `h/l/w/b/d/c/y/p` | Full vim motions and operators work on your command line. |
| 544 | Vi-Mode History Search | `Esc` → `/pattern` | Search command history backward. `n`/`N` to cycle through matches. |
| 545 | Vim + Tmux Together | — | The ultimate workflow: tmux panes for splits, vim for editing. One keyboard, infinite power. |

---

## Appendix A — Synonym Reference

Many keys do the same thing. Knowing synonyms helps you recognize them in the wild.

| Primary | Synonyms | Action |
|---------|----------|--------|
| `h` | `Ctrl-H`, `BS`, `←` | Left |
| `l` | `Space`, `→` | Right |
| `k` | `Ctrl-P`, `↑` | Up |
| `j` | `Ctrl-J`, `Ctrl-N`, `↓`, `NL` | Down |
| `C` | `c$` | Change to end |
| `D` | `d$` | Delete to end |
| `S` | `cc` | Substitute line |
| `Y` | `yy` | Yank line |
| `+` | `Ctrl-M`, `Enter` | Next line start |
| `0` | `Home` | First column |
| `$` | `End` | End of line |
| `x` | `Del` | Delete char |
| `u` | `Undo` | Undo |
| `Ctrl-F` | `PageDown`, `Shift-Down` | Page forward |
| `Ctrl-B` | `PageUp`, `Shift-Up` | Page backward |
| `Esc` | `Ctrl-[` | Escape |

---

## Appendix B — The Vim Grammar

Vim commands follow a composable grammar:

```
[count] [register] operator [count] motion/text-object
```

**Operators** (verbs): `d` `c` `y` `>` `<` `=` `g~` `gu` `gU` `!` `gq` `gw` `g?` `g@`

**Motions** (where): `w` `b` `e` `ge` `W` `B` `E` `0` `^` `$` `f` `t` `F` `T` `{` `}` `(` `)` `gg` `G` `H` `M` `L` `/` `?` `n` `N` `%` etc.

**Text Objects** (what): `iw` `aw` `iW` `aW` `is` `as` `ip` `ap` `i"` `a"` `i'` `a'` `` i` `` `` a` `` `i(` `a(` `i{` `a{` `i[` `a[` `i<` `a<` `it` `at`

Any operator × any motion/text-object = a command. This is why Vim scales — learn one new operator and it works with every motion you know, and vice versa.

---

## Appendix C — Suggested Learning Path

1. **Days 1–3**: Part 1 (Survival) — watch all 15, practice each one
2. **Days 4–10**: Part 2 (Basic Editing) — go "cold turkey" after this
3. **Days 11–20**: Part 3 (Becoming Productive) — text objects are the big unlock
4. **Days 21–30**: Part 4 (Intermediate Power) — registers, macros, marks
5. **Days 25–35**: Part 19 (Tmux & Shell) — learn alongside Part 4; use panes and windows daily
6. **Days 36–60**: Parts 5–8 (Walking the Keyboard) — one key per day, daily flash cards
7. **Days 61–90**: Parts 9–12 (`g`, `z`, `[`, `Ctrl-W`) — one command per day
8. **Days 91–120**: Parts 13–16 (Insert mode, Ex commands, visual, command-line) — as needed
9. **Days 121+**: Parts 17–18 (Patterns & Advanced) — ongoing daily tips

---

## Appendix D — Surround Plugin

The Surround plugin (`vim-surround` / `nvim-surround`) is arguably the most universally useful
Vim plugin. It's built into many emulators (VS Code Vim, IdeaVim, etc.) and may deserve its own
mini-series of lessons. Consider adding these as a **Part 20** or bonus section.

| Action | Keys | Description |
|--------|------|-------------|
| Surround word with `"` | `ysiw"` | You Surround Inner Word with `"`. |
| Surround visual selection | `viwS"` | Visual select a word, then `S"` to wrap in quotes. |
| Change surround | `cs'"` | Change surrounding `'` to `"`. |
| Delete surround | `ds"` | Delete surrounding `"`. |
| Surround with tag | `ysiw<em>` | Surround word with `<em>...</em>`. |
| Change tag | `cst<div>` | Change surrounding tag to `<div>`. |
| Surround line | `yss"` | Surround the entire line with `"`. |
| Surround with parens | `ysiw)` or `ysiw(` | `)` = no spaces, `(` = with spaces inside. |

> **Note**: Neovim does _not_ include surround by default. Install `kylechui/nvim-surround` or
> `tpope/vim-surround`. However, VS Code's Vim extension includes surround support out of the box.

---

## Appendix E — Original Handwritten Notes

_Preserved from the original Curriculum.md — personal observations and tips worth keeping._

### Visual Mode — Special Behavior of Insert Keys

In Visual mode, the "insert" keys (`i`, `a`, `o`, `O`) have different meanings than in Normal mode:
- `i` and `a` are **text-object modifiers** (e.g., `viw` = visual-select inner word), _not_ insert commands
- `o` switches the cursor to the **other end** of the selection (extend either direction)
- `O` in block-visual mode switches to the **other corner** horizontally
- `I` and `A` in block-visual mode insert/append on **every line** of the block
- `c` / `s` / `r` / `R` all operate on the selection (change, substitute, replace)

### Practical Vim Tips

From _Practical Vim_ by Drew Neil:

- `q:` and `q/` open editable command/search history windows — much better than pressing `↑` repeatedly
- Map `<C-p>` and `<C-n>` on the command line to filter history by prefix:
  ```vim
  cnoremap <C-p> <Up>
  cnoremap <C-n> <Down>
  ```
- Increase command-line history: `:set history=200`
- Power pattern — search with `*`, change the word, then apply globally:
  `*cwfoo<Esc>` then `:%s//<C-r><C-w>/g` (empty pattern reuses last search)
- `Y` should be `y$` for consistency with `C` and `D` — add `:map Y y$` to your config

### Motion Classification (from Vim docs)

Vim motions are categorized as **exclusive** or **inclusive**, which affects which characters
an operator acts on:

- **Inclusive** (`e`, `f`, `t`, `;`, `,`, `$`, `%`, `G`, `H`, `L`, `M`, etc.) — the last
  character of the motion _is_ included in the operation
- **Exclusive** (`w`, `b`, `h`, `l`, `0`, `^`, `{`, `}`, `(`, `)`, `/`, `?`, etc.) — the
  last character is _not_ included
- **Linewise** (`j`, `k`, `G`, `H`, `L`, `M`, `+`, `-`, `_`, `dd`, `cc`, etc.) — entire
  lines are affected regardless of cursor column

This matters when you do things like `dw` (doesn't grab the space after) vs `de` (grabs the
last letter) — and explains some surprising behaviors.

### The Vimtutor Lesson Order

For reference, the official `vimtutor` teaches concepts in this order:
`hjkl` → `Esc :q!` → `x` → `i Esc` → `A` → `:wq` → `dw` → `d$` → `d{motion}` →
`2w 3e 0` → `d[count]{motion}` → `dd 2dd` → `u U Ctrl-R` → `p` → `r{char}` → `ce` →
`c[count]{motion}` → `Ctrl-G G gg` → `/ ? n N Ctrl-O Ctrl-I` → `%` → `:s/old/new/[g][c]` →
`:!{cmd}` → `:w` → `v{motion}` → `:r` → `o O` → `a` → `R` → `y yw` → `:set ic hls is` →
help / vimrc / completion

### How to Learn Vim (Philosophy)

- **Normal mode is "normal."** You spend most of your time _reading_ and _navigating_ code,
  not inserting. Get comfortable living in Normal mode.
- **Always hit `Esc` after each thought.** Think of insert mode as a brief excursion.
- **Keys, front right pocket** (except when driving). Carry a cheat sheet on your phone.
- **Learn in this order:**
  1. Lowercase alphabet (except `g` and `z` — those are prefix keys)
  2. Symbols
  3. Uppercase alphabet
  4. Control keys
  5. Insert mode tricks
- **Go "cold turkey" as soon as you're comfortable enough.** Basic motions, visual mode,
  delete, copy/paste — that's enough to be productive. Then force yourself.
- **Hands off the mouse** (never use "select mode")
- **Hands off the arrows** → then eventually, less reliance on `hjkl` too
- **More thinking, less mindless keystrokes** — like the Petrus method for Rubik's cube:
  think ahead, plan your moves, execute efficiently

---

## Appendix F — Simulator Coverage

The VimFu simulator supports a curated subset of Vim, tmux, and shell features — enough to
practice the entire foundational curriculum (Parts 1–4) and the tmux section (Part 19), plus
many features from the reference parts. Features not in the simulator can be practiced in
real Neovim.

### Fully Supported in Simulator

- **Parts 1–3** (Lessons 1–90): All features except `Ctrl-V` block visual mode (Lessons 66–67)
- **Part 4** (Lessons 91–135): All features except global marks (`m{A-Z}`), special marks
  (`''`, `` `` ``, `'.`, `'^`), auto-indent (`=`), append registers (`"A-Z`), system clipboard
  (`"+`, `"*`), small delete register (`"-`), numbered registers (`"0`–`"9`), `:reg`, and nvim
  window splits (`:sp`, `:vs`, `Ctrl-W`). Use tmux panes instead of nvim splits!
- **Part 19** (Lessons 501–545): All tmux and shell features fully supported

### Not in Simulator

The following features are taught in the curriculum as standard Vim/Neovim knowledge but are
not available in the VimFu simulator. Practice these in real Neovim.

| Feature | Lessons | Notes |
|---------|---------|-------|
| `Ctrl-V` block visual | 66, 67, 232, 433, 443, 444, 469 | Use `v` and `V` instead |
| Global marks `m{A-Z}` | 100 | Local marks `m{a-z}` work fine |
| Special marks `''` `'.` `'^` | 101 | |
| Auto-indent `=` / `==` | 110, 206 | `>` and `<` indent/dedent work |
| Append registers `"A-Z` | 120 | Named `"a-z` work |
| System clipboard `"+` `"*` | 122 | |
| Small delete register `"-` | 123 | |
| Numbered registers `"0`–`"9` | 124 | |
| `:reg` | 125 | |
| Nvim window splits | 131–135, 334–365 | Use tmux panes instead |
| `K` keyword lookup | 172 | |
| `U` undo line | 182 | `u` undo works |
| `!{motion}{filter}` filter | 196, 421 | `:!cmd` works |
| `&` repeat `:s` | 200 | |
| `Ctrl-L` redraw | 231 | |
| `Ctrl-C` | 233 | Use `Escape` instead |
| `Ctrl-Z` suspend | 234 | |
| `Ctrl-]` / `Ctrl-T` tags | 235, 236 | |
| `Ctrl-^` alternate file | 237 | |
| `z.` `z+` `z-` `z^` scroll | 245–248, 289 | `zz` `zt` `zb` work |
| Most `g` commands | 254–265, 271–285 | `ga` `gd` `ge` `gE` `gi` `gI` `gJ` `gu` `gU` `g~` `gv` `g_` work |
| Folds | 293–307 | |
| Spelling | 308–314 | |
| Bracket `[` / `]` commands | 317–333 | |
| Insert `Ctrl-O` (insert-normal) | 368 | |
| Insert `Ctrl-T` / `Ctrl-D` indent | 372, 373 | |
| `:s` substitution | 405–409 | |
| Buffers / `:ls` / `:b` | 410–414 | |
| Tabs / `:tabnew` | 415–418 | |
| `:{range}!{filter}` | 421 | |
| `:terminal` | 422 | |
| `q:` / `q/` history windows | 446, 447 | |
| `:norm` / `:g` / `:v` | 457–459 | |
