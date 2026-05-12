# VimFu Content Outline

The complete part/topic hierarchy. Each entry has:

- A **stable topic ID** (`part.topic-slug`) — never changes.
- A **title** and **summary**.
- The **lessons** it covers (curriculum lesson numbers; some have no video).
- The **keys** it teaches.
- Notes on **internals** content the book should include.

This outline is the source of truth for the part/topic taxonomy. When a topic
is authored, it goes in `content/parts/<NN-part-slug>/<NN-topic-slug>.json`
and renders to both site and book. See [`Strategy.md`](./Strategy.md) and
[`Schema.md`](./Schema.md).

---

## Front Matter (book) / Landing Page (site)

| ID                            | Title                          | Notes |
|-------------------------------|--------------------------------|-------|
| `front.title`                 | Title page                     | Book only. |
| `front.about`                 | About this book / About this site | Audience-tagged variants. |
| `front.how-to-use`            | How to use this book / site    | QR code conventions, video conventions, cross-refs. |
| `front.playlist-qr`           | The VimFu playlist             | Single QR to the YouTube playlist; site renders as a video grid. |

---

## Part 01 — Foundations

_Why Vim, what "modal" really means, and the model in your head._

| ID                                | Title                       | Lessons   | Keys              |
|-----------------------------------|-----------------------------|-----------|-------------------|
| `foundations.modal-editing`       | Modal Editing               | 1, 3, 15  | `Esc`             |
| `foundations.you-dont-need-vim`   | You Don't Need Vim          | —         | —                 |
| `foundations.vi-vim-neovim`       | Vi → Vim → Neovim           | —         | —                 |
| `foundations.modes-overview`      | The Modes (FSM Overview)    | 3, 15     | `Esc`, `i`, `v`, `:` |
| `foundations.universal-grammar`   | The Universal Grammar       | 85        | `[count] [reg] op [count] motion` |

**Internals to cover:** modes as a finite state machine; what's saved per-mode;
why "normal" is normal (it's the default state, not an editing accident); the
ADM-3A history of `hjkl`; the difference between Vim's "command mode" (the `:`
prompt) and "command-line-window" (`q:`).

---

## Part 02 — Survival

_Open, type, save, undo, move with `hjkl` — enough to not panic._

| ID                            | Title                  | Lessons       | Keys                          |
|-------------------------------|------------------------|---------------|-------------------------------|
| `survival.open-save-quit`     | Open, Save, Quit       | 2, 7, 8, 9, 10| `nvim`, `:w`, `:q`, `:wq`, `:x`, `ZZ`, `:q!`, `ZQ` |
| `survival.insert-and-back`    | Insert and Back        | 4, 5, 6, 15   | `i`, `Esc`                    |
| `survival.undo-redo`          | Undo and Redo          | 11, 12        | `u`, `Ctrl-R`                 |
| `survival.hjkl`               | Move with hjkl         | 13, 14        | `h`, `j`, `k`, `l`            |

**Internals:** swapfiles and what `:q!` actually does; `u` walks the undo
*tree* (not stack — full coverage in `advanced.undo-tree`); the buffer/window
distinction (one buffer, one window for now).

---

## Part 03 — Basic Editing

_The grammar's first verbs: enter insert, motion, delete, change, yank._

| ID                                | Title                         | Lessons         | Keys                           |
|-----------------------------------|-------------------------------|-----------------|--------------------------------|
| `editing.insert-variants`         | More Ways into Insert         | 16, 17, 18, 19, 20 | `a`, `I`, `A`, `o`, `O`     |
| `editing.word-motions`            | Word Motions                  | 21, 22, 23, 24  | `w`, `b`, `e`, `ge`            |
| `editing.line-motions`            | Line Motions                  | 25, 26, 27      | `0`, `^`, `$`                  |
| `editing.file-motions`            | File Motions                  | 28, 29, 30      | `gg`, `G`, `{n}G`, `:{n}`      |
| `editing.delete`                  | Delete                        | 31, 32, 33, 34, 35 | `x`, `X`, `dw`, `D`, `dd`   |
| `editing.change`                  | Change                        | 36, 37, 38, 39  | `cw`, `C`, `cc`, `S`, `s`      |
| `editing.yank-put`                | Yank and Put                  | 40, 41, 42, 43, 44 | `yy`, `Y`, `p`, `P`, `yw`, `y$` |
| `editing.replace-char`            | Replace a Character           | 45              | `r{char}`                      |

**Internals:** the operator + motion model (`d` is a verb, `w` is a noun); why
`D` is `d$` but `Y` historically wasn't `y$` (vi compat — it's a wart); word
boundaries via `iskeyword`; what "yank" actually writes to (the unnamed register).

---

## Part 04 — Search and Find

_Pattern search, word search, character find on a line._

| ID                            | Title                   | Lessons          | Keys                                    |
|-------------------------------|-------------------------|------------------|-----------------------------------------|
| `search.pattern`              | Pattern Search          | 46, 47, 48, 49   | `/pattern`, `?pattern`, `n`, `N`        |
| `search.word`                 | Word Search             | 50, 51           | `*`, `#`, `g*`, `g#`                    |
| `search.find-on-line`         | Find on Line            | 52, 53, 54, 55, 56, 57 | `f`, `F`, `t`, `T`, `;`, `,`        |

**Internals:** the `/` and `?` registers; how `*` builds a `\<word\>` regex;
why `;` is so useful (it caches direction *and* character); whole-word
boundaries vs `g*`; search wrapping and `'wrapscan'`.

---

## Part 05 — Counts and Visual Mode

_Multiply commands; select first, act second._

| ID                            | Title                       | Lessons             | Keys                            |
|-------------------------------|-----------------------------|---------------------|---------------------------------|
| `counts-visual.counts`        | Counts                      | 58, 59, 60, 61      | `{n}`, `{n}{motion}`, `{n}{op}` |
| `counts-visual.percent-bar`   | Jump by Percentage / Column | 62, 63              | `{n}%`, `{n}\|`                 |
| `counts-visual.char-visual`   | Character Visual Mode       | 64, 68              | `v`, `o`                        |
| `counts-visual.line-block`    | Line and Block Visual       | 65, 66, 67          | `V`, `Ctrl-V`                   |
| `counts-visual.tricks`        | Visual Mode Tricks          | 69, 70              | `O`, `gv`                       |

**Internals:** counts compose multiplicatively (`2d3w` = 6 words); the visual
selection is a buffer-relative *anchor + cursor* pair; `gv` reuses the
`'<` / `'>` marks that get set automatically.

---

## Part 06 — The Dot Command

_The most important key in Vim._

| ID                            | Title                  | Lessons        | Keys              |
|-------------------------------|------------------------|----------------|-------------------|
| `dot.repeat`                  | Repeat Last Change     | 71             | `.`               |
| `dot.with-counts`             | Dot with Counts        | 72             | `{n}.`            |
| `dot.patterns`                | Dot Patterns           | 73             | `*cw…<Esc>n.`, `cgn.` |

**Internals:** what counts as "the last change" — entering insert through
leaving it is *one* change; an operator+motion is one change; a single `x`
is one change. Dot replays the change with its count. Why `cgn` + `.` is so
much smoother than `*` + `cw` + `n.`.

---

## Part 07 — Operators and Text Objects

_The grammar in full: verbs × nouns. The conceptual climax._

| ID                                  | Title                        | Lessons              | Keys                     |
|-------------------------------------|------------------------------|----------------------|--------------------------|
| `operators-textobjects.iw-aw`       | Inner Word vs A Word         | 74                   | `iw`, `aw`               |
| `operators-textobjects.quotes`      | Quote Text Objects           | 75, 76, 77           | `i"`, `a"`, `i'`, `a'`, `` i` ``, `` a` `` |
| `operators-textobjects.brackets`    | Bracket Text Objects         | 78, 79, 80, 81       | `i(`, `i{`, `i[`, `i<`, `ib`, `iB` |
| `operators-textobjects.sentence-paragraph` | Sentence and Paragraph | 82, 83             | `is`, `as`, `ip`, `ap`   |
| `operators-textobjects.tags`        | HTML/XML Tag Objects         | 84                   | `it`, `at`               |
| `operators-textobjects.grammar`     | The Vim Grammar              | 85                   | `[count] [reg] op [count] motion` |

**Internals:** every operator is a function `(start, end, type) → effect`;
every motion produces `(start, end, type)`; text objects produce `(start,
end, type)` directly without using the cursor as start. This is the entire
grammar in one sentence. The "i" / "a" naming is *inner* (just the noun) /
*around* (noun + delimiter or surrounding whitespace).

---

## Part 08 — Wider Motions

_Beyond words and lines: sentences, paragraphs, brackets, screen positions._

| ID                            | Title                          | Lessons       | Keys                         |
|-------------------------------|--------------------------------|---------------|------------------------------|
| `wider-motions.sentence-paragraph` | Sentence and Paragraph     | 91, 92        | `(`, `)`, `{`, `}`           |
| `wider-motions.match-bracket` | Match Bracket                  | 93            | `%`                          |
| `wider-motions.screen-positions` | Screen Position Jumps      | 94            | `H`, `M`, `L`                |
| `wider-motions.line-start`    | Line-Start Motions             | 95            | `+`, `-`, `Enter`            |
| `wider-motions.WORD`          | WORD Motions                   | 96            | `W`, `B`, `E`, `gE`          |

**Internals:** sentence boundary is `.!?` followed by whitespace/EOL —
not always what English thinks a sentence is. Paragraph = blank line. WORD
vs word: WORD uses whitespace only; word uses `iskeyword`.

---

## Part 09 — Scrolling and Screen Position

_Move through files without losing context._

| ID                            | Title                        | Lessons              | Keys                        |
|-------------------------------|------------------------------|----------------------|-----------------------------|
| `scroll.half-full-page`       | Half- and Full-Page Scrolling| 86, 87, 88, 89       | `Ctrl-D`, `Ctrl-U`, `Ctrl-F`, `Ctrl-B` |
| `scroll.center-top-bottom`    | Centering the Cursor         | 90, 242, 243, 244    | `zz`, `zt`, `zb`            |
| `scroll.first-non-blank-z`    | z. / z+ / z- (first non-blank variants) | 245, 246, 247 | `z.`, `z+`, `z-`            |
| `scroll.height`               | z{n}{Enter} — set window height | 248               | `z{n}{Enter}`               |
| `scroll.line-by-line`         | Line-by-Line Scroll          | (Ctrl-E/Y videos)    | `Ctrl-E`, `Ctrl-Y`          |
| `scroll.horizontal`           | Horizontal Scroll            | 289                  | `zs`, `ze`, `zh`, `zl`, `zL`, `zH` |

**Internals:** Vim has a *visible top line* per window — not a "scroll
position" in pixels. Scroll commands just change the visible top line and
redraw. `'scrolloff'` reserves N lines around the cursor as a buffer.

---

## Part 10 — Marks and the Jump List

_Leave breadcrumbs and retrace your steps._

| ID                            | Title                      | Lessons             | Keys                                 |
|-------------------------------|----------------------------|---------------------|--------------------------------------|
| `marks.local-global`          | Setting and Jumping        | 97, 98, 99, 100     | `m{a-z}`, `'{a-z}`, `` `{a-z} ``, `m{A-Z}` |
| `marks.special`               | Special Marks              | 101                 | `''`, `` `` ``, `'.`, `'^`, `'<`, `'>` |
| `marks.tick-vs-backtick`      | `'` vs `` ` ``             | (book-only)         | `'a` vs `` `a ``                     |
| `marks.jumplist`              | The Jump List              | 102, 103, 104       | `Ctrl-O`, `Ctrl-I`, `:jumps`         |
| `marks.changelist`            | The Change List            | (g; / g, videos)    | `g;`, `g,`, `:changes`               |

**Internals:** marks are a per-buffer (lowercase) and per-Vim (uppercase)
key→position dictionary. Jumplist is a per-window stack-with-cursor: max 100
positions; "big jumps" push (search, `gg`, `G`, `%`, mark jumps); `Ctrl-O`/
`Ctrl-I` move the cursor through the stack without popping. Change list is
per-buffer; `'.`  is just the most recent entry.

---

## Part 11 — Transform

_Replace, indent, case-change, join — operators that aren't delete/change._

| ID                            | Title                         | Lessons               | Keys                              |
|-------------------------------|-------------------------------|-----------------------|-----------------------------------|
| `transform.replace-mode`      | Replace Mode                  | 105, 106              | `R`, `r{char}`                    |
| `transform.indent`            | Indent and Auto-Indent        | 107, 108, 109, 110, 111 | `>>`, `<<`, `>{motion}`, `={motion}`, `==` |
| `transform.case`              | Case Changing                 | 112, 113, 114, 115, 116 | `~`, `gU`, `gu`, `g~`            |
| `transform.join`              | Joining Lines                 | 117, 118              | `J`, `gJ`                         |

**Internals:** `>` / `<` / `=` / `gU` / `gu` / `g~` are all operators —
they take a motion. So `>ip` is "indent inner paragraph." `==` is the
"linewise" form of `=` (every operator has a doubled form for the line);
likewise `>>` and `<<`.

---

## Part 12 — Registers (deep dive)

_The system Vim uses to hold text. The single best thing to understand
deeply._

| ID                            | Title                            | Lessons        | Keys                       |
|-------------------------------|----------------------------------|----------------|----------------------------|
| `registers.overview`          | Registers Overview               | 119, 121, 125  | `"a`–`"z`, `:reg`          |
| `registers.unnamed`           | The Unnamed Register             | 119            | `""`                       |
| `registers.named`             | Named Registers                  | 119, 120       | `"a`–`"z`, `"A`–`"Z`       |
| `registers.numbered`          | Numbered Registers               | 122            | `"0`, `"1`–`"9`            |
| `registers.small-delete`      | Small Delete Register            | 123            | `"-`                       |
| `registers.clipboard`         | System Clipboard Registers       | 124            | `"+`, `"*`                 |
| `registers.special`           | Special Registers (`/`, `:`, `.`, `%`, `#`, `=`, `_`) | 483–488 | `"/`, `":`, `".`, `"%`, `"#`, `"=`, `"_` |
| `registers.macros-as-text`    | Macros Are Just Register Contents| —              | `"ap`, edit, `"ay$`        |

**Internals:** registers are a key→(text, type) dictionary. `type` is `char`
or `line` (sometimes `block`). Every yank/delete writes the unnamed register;
named are opt-in; numbered shift on each delete; `"0` only updates on yank.
Macros are stored *as the same kind of text*, which is why you can paste a
macro, edit the keystrokes, and yank it back.

---

## Part 13 — Macros

_Record, replay, compose._

| ID                            | Title                        | Lessons         | Keys                |
|-------------------------------|------------------------------|-----------------|---------------------|
| `macros.record-play`          | Recording and Playing        | 126, 127, 128, 129 | `qa`, `q`, `@a`, `@@` |
| `macros.counted`              | Counted Macros               | 130             | `100@a`             |
| `macros.editing`              | Editing a Macro              | —               | `"ap`, edit, `"ay$` |

**Internals:** the recorder appends each typed key to register `a` until you
press `q` again. Playback feeds those keys to the input buffer. `100@a` runs
until error — that's the "abort on error" pattern.

---

## Part 14 — Windows, Buffers, Tabs

_Multiple views on multiple files._

| ID                            | Title                       | Lessons             | Keys                              |
|-------------------------------|-----------------------------|---------------------|-----------------------------------|
| `windows.splits`              | Creating Splits             | 131, 132            | `Ctrl-W s`, `Ctrl-W v`, `:sp`, `:vs` |
| `windows.navigate`            | Navigating Windows          | 133, 134, 135       | `Ctrl-W h/j/k/l`, `Ctrl-W c`, `Ctrl-W o` |
| `windows.move-resize`         | Move and Resize             | (ch 21.2)           | `Ctrl-W H/J/K/L`, `Ctrl-W +`, `Ctrl-W -`, `Ctrl-W =` |
| `windows.buffers`             | Buffers                     | (ch 23.3)           | `:ls`, `:b`, `:bn`, `:bp`, `:bd`  |
| `windows.tabs`                | Tabs                        | (ch 23.3)           | `:tabnew`, `:tabnext`, `gt`, `gT` |
| `windows.buffers-vs-windows-vs-tabs` | Buffer vs Window vs Tab | —              | —                                 |

**Internals (key topic):** buffers are *files in memory*; windows are
*viewports onto buffers*; tabs are *layouts of windows*. One buffer can be
shown in many windows. `:ls` lists buffers; `Ctrl-W` is the window prefix;
`gt` is the tab prefix. Most users want buffers, not tabs.

---

## Part 15 — Prefix Families

_The hidden keyboards behind `g`, `z`, `[`/`]`, and `Ctrl-W`._

| ID                            | Title                        | Lessons       | Keys                             |
|-------------------------------|------------------------------|---------------|----------------------------------|
| `prefixes.g-overview`         | The `g` Family               | 249–285       | `gd`, `gf`, `gv`, `gi`, `gq`, `g;`, `g,`, … |
| `prefixes.z-overview`         | The `z` Family               | 286–316       | `zo`, `zc`, `za`, `zr`, `zm`, `zf`, `z=`, `zg`, … |
| `prefixes.bracket-pairs`      | The `[` and `]` Family       | 317–333       | `[(`, `])`, `[{`, `]m`, `[c`, `]c`, `[s`, `]s`, … |
| `prefixes.ctrl-w`             | The `Ctrl-W` Family          | 334–365       | `Ctrl-W` + 30+ keys              |

Each prefix gets one *narrative* topic explaining the family, plus a flat
reference table.

---

## Part 16 — Insert-Mode Power

_Keys that work while you're typing._

| ID                            | Title                              | Lessons       | Keys                          |
|-------------------------------|------------------------------------|---------------|-------------------------------|
| `insert.exits`                | Leaving Insert Mode                | 366           | `Esc`, `Ctrl-[`, `Ctrl-C`     |
| `insert.one-shot-normal`      | One Normal-Mode Command            | 367           | `Ctrl-O`                      |
| `insert.editing-keys`         | Backspace, Delete-Word, Delete-Line| 368, 369      | `Ctrl-H`, `Ctrl-W`, `Ctrl-U`  |
| `insert.indent`               | Indent in Insert                   | 370, 371      | `Ctrl-T`, `Ctrl-D`            |
| `insert.from-register`        | Paste from Register                | 372           | `Ctrl-R{a}`, `Ctrl-R Ctrl-R{a}` |
| `insert.copy-adjacent`        | Copy from Above/Below              | 373, 374      | `Ctrl-Y`, `Ctrl-E`            |
| `insert.completion`           | Word Completion                    | 375, 376      | `Ctrl-N`, `Ctrl-P`            |
| `insert.ctrl-x-completion`    | The `Ctrl-X` Completion Sub-Menu   | 377–390       | `Ctrl-X Ctrl-L/F/K/T/I/D/]/O/S/V` |
| `insert.literal-digraph`      | Literal Keys and Digraphs          | 391–395       | `Ctrl-V`, `Ctrl-K`            |

---

## Part 17 — Ex Commands

_The `:` prompt — file ops, substitution, ranges._

| ID                            | Title                          | Lessons          | Keys                       |
|-------------------------------|--------------------------------|------------------|----------------------------|
| `ex.file-ops`                 | Save, Quit, Open, Read         | 396–404          | `:w`, `:q`, `:e`, `:r`, `:r!` |
| `ex.substitute`               | Substitute                     | 405–409          | `:s`, `:%s`, `:%s/g`, `:%s/gc` |
| `ex.ranges`                   | Ranges                         | (book-only)      | `:1,5`, `:.`, `:%`, `:'<,'>` |
| `ex.global`                   | The Global Command             | 446–460          | `:g/pat/cmd`, `:v/pat/cmd` |
| `ex.norm`                     | Normal-Mode on Lines           | (ch 25)          | `:norm`                    |
| `ex.shell`                    | Shell Commands and Filters     | 419–427          | `:!`, `:%!sort`, `:terminal` |
| `ex.set`                      | Settings                       | 428–430          | `:set`, `:noh`             |
| `ex.quickfix`                 | The Quickfix List              | —                | `:make`, `:copen`, `:cnext`, `:cprev`, `:cdo` |
| `ex.sort`                     | Sort                           | —                | `:sort`, `:sort u`, `:sort!`, `:sort n` |

---

## Part 18 — Visual Mode in Depth

_Block edits, automatic ranges, the o/O secret._

| ID                            | Title                       | Lessons     | Keys                                    |
|-------------------------------|-----------------------------|-------------|-----------------------------------------|
| `visual.modes`                | The Three Visual Modes      | 431, 432    | `v`, `V`, `Ctrl-V`                      |
| `visual.block-insert-append`  | Block Insert and Append     | 433, 434    | `Ctrl-V` → `I` / `A`                    |
| `visual.endpoints`            | Switch Endpoints            | 435         | `o`, `O`                                |
| `visual.ops`                  | Operators on Selections     | 436, 437, 438 | `d`, `c`, `y`, `>`, `<`, `=`, `~`, `U`, `u`, `J` |
| `visual.range`                | The `'<,'>` Range           | 439         | `:'<,'>...`, `:` after visual           |
| `visual.gv`                   | Re-select Last Visual       | 440         | `gv`                                    |

---

## Part 19 — Command-Line Power

_The colon prompt as a programmable shell._

| ID                            | Title                        | Lessons      | Keys                            |
|-------------------------------|------------------------------|--------------|---------------------------------|
| `cmdline.history-window`      | The Command History Window   | 446, 447     | `q:`, `q/`, `q?`                |
| `cmdline.repeat-ex`           | Repeat Last Ex Command       | 448          | `@:`                            |
| `cmdline.edit-buffer`         | Edit the Command in a Buffer | 449          | `Ctrl-F`                        |
| `cmdline.paste-from-buffer`   | Paste into the Command       | 450          | `Ctrl-R`, `Ctrl-R Ctrl-W`, `Ctrl-R Ctrl-A` |
| `cmdline.completion`          | Completion at the `:` prompt | 451          | `Tab`, `Ctrl-D`                 |
| `cmdline.wildmenu`            | The Wildmenu                 | —            | `'wildmenu'`, `'wildmode'`, `'wildoptions'` |

---

## Part 20 — Patterns and Recipes

_Real editing problems, solved by composition._

| ID                            | Title                         | Lessons   | Keys                              |
|-------------------------------|-------------------------------|-----------|-----------------------------------|
| `recipes.swap-and-duplicate`  | Swap, Duplicate, Move         | 461, 462, 463 | `xp`, `ddp`, `yyp`            |
| `recipes.star-cw-dot`         | The `*cw…<Esc>n.` Pattern     | 464, 465  | `*`, `cw`, `<Esc>`, `n`, `.`      |
| `recipes.cgn-dot`             | `cgn` + `.` (smoother)        | 466       | `cgn`, `.`                        |
| `recipes.block-comment`       | Block Commenting              | 467, 468  | `Ctrl-V` `I//` `Esc`, `:%norm I//` |
| `recipes.increment-decrement` | Increment / Decrement         | 469, 470, 471 | `Ctrl-A`, `Ctrl-X`, `g Ctrl-A` |
| `recipes.numbered-paste`      | Numbered Register Paste Trick | 472       | `"1p`, `.`                        |
| `recipes.diff`                | Diff Commands                 | 473, 474  | `do`, `dp`                        |
| `recipes.external-filter`     | External Filtering            | 475–480   | `!ip sort`, `:%!jq`, etc.         |

---

## Part 21 — Advanced Topics

_Undo trees, special registers, op-pending mode, terminal, folding, config._

| ID                            | Title                          | Lessons        | Keys                              |
|-------------------------------|--------------------------------|----------------|-----------------------------------|
| `advanced.undo-tree`          | The Undo Tree                  | 481, 482       | `g-`, `g+`, `:earlier`, `:later`  |
| `advanced.special-registers`  | The Special Registers in Depth | 483–488        | `"/`, `":`, `".`, `"%`, `"#`, `"=` |
| `advanced.op-pending`         | Operator-Pending Mode          | 489, 490       | `g@`, `operatorfunc`              |
| `advanced.terminal`           | Terminal Mode                  | 491, 492       | `:term`, `Ctrl-\ Ctrl-N`          |
| `advanced.character-info`     | Character Inspection           | (ga, g8 videos)| `ga`, `g8`                        |
| `advanced.gx-g-less`          | Open URLs and Output History   | (gx, g< videos)| `gx`, `g<`                        |
| `advanced.folding`            | Folding in Practice            | 493, 494, 495  | `:set fdm=indent`, `zo`, `zc`, `zM`, `zR`, `zf`, `zd` |
| `advanced.config`             | Configuration                  | 498, 499, 500  | `:help`, `vimrc`, `init.lua`      |
| `advanced.spell`              | Spell Checking                 | —              | `:set spell`, `]s`, `[s`, `z=`, `zg`, `zw` |
| `advanced.tags`               | Tags and Code Navigation       | —              | `Ctrl-]`, `Ctrl-T`, `:tag`, `:tags`, `:tselect` |
| `advanced.mappings`           | Mappings — :map, :noremap, and Friends | —      | `:nnoremap`, `:vnoremap`, `:xnoremap`, `:onoremap`, `:inoremap`, `:cnoremap`, `<silent>`, `<expr>`, `<buffer>` |

---

## Part 22 — Tmux

_The other half of a terminal workflow: terminal multiplexing with vim-flavored
keys._

| ID                            | Title                                | Lessons                          | Keys                                                  |
|-------------------------------|--------------------------------------|----------------------------------|-------------------------------------------------------|
| `tmux.what-is-tmux`           | What Is tmux?                        | 501, 502                         | `tmux`                                                |
| `tmux.prefix-key`             | The Prefix Key                       | 503, 504                         | `Ctrl-B`, `Ctrl-B ?`                                  |
| `tmux.panes`                  | Panes — Split, Navigate, Resize      | 505–515                          | `Ctrl-B %`, `Ctrl-B "`, `Ctrl-B o`, `Ctrl-B z`, `Ctrl-B x`, `Ctrl-B q` |
| `tmux.windows`                | Windows                              | 516–523                          | `Ctrl-B c`, `Ctrl-B n`, `Ctrl-B p`, `Ctrl-B 0`, `Ctrl-B w`, `Ctrl-B ,`, `Ctrl-B &` |
| `tmux.sessions`               | Sessions, Detach, Reattach           | 524, 525, 526                    | `Ctrl-B d`, `tmux attach`, `tmux new -s`, `tmux ls`   |
| `tmux.copy-mode`              | Copy Mode — Vim Motions in Scrollback| 527, 528, 529                    | `Ctrl-B [`, `h`, `j`, `k`, `l`, `/`, `n`, `v`, `y`, `q` |

**Internals:** tmux is a long-lived server with attached/detached clients —
that architecture *is* the killer feature (SSH drops don't kill sessions).
Panes are independent shells inside one window; windows are virtual-desktop
layouts inside one session; sessions outlive every terminal they run in.
{key:Ctrl-B} clashes with Vim's page-back; the modern consensus is to remap
the prefix to {key:Ctrl-Space}. Copy mode borrows Vim's motion vocabulary
deliberately — set `mode-keys vi` in `~/.tmux.conf` to make it complete.

---

## Appendices

| ID                              | Title                          | Notes |
|---------------------------------|--------------------------------|-------|
| `appendix.keyboard-walk`        | Walking the Keyboard           | Reference: every key in normal mode (lessons 136–248). Site renders as a clickable keyboard map; book renders as keyboard diagrams + flat tables. |
| `appendix.synonyms`             | Synonym Reference              | `C`=`c$`, `D`=`d$`, `S`=`cc`, `Y` (caveat), etc. |
| `appendix.grammar-matrix`       | The Vim Grammar Matrix         | Operators × motions/text-objects table. |
| `appendix.learning-path`        | Suggested Learning Path        | A 120-day plan from zero to fluency. |
| `appendix.motion-classification`| Motion Classification          | Inclusive vs exclusive vs linewise. |
| `appendix.surround-plugin`      | The Surround Plugin            | `ys`, `cs`, `ds`, visual `S`. |
| `appendix.vim-in-other-editors` | Vim in Other Editors           | VS Code, JetBrains, etc. — site has a setup-guides section per editor. |
| `appendix.complete-key-reference`| Complete Key Reference        | Alphabetical index of every key. Site's main "search" target; book's last appendix. |

---

## Lesson → Topic mapping (sanity check)

| Lessons        | Primary topic(s)                                |
|----------------|-------------------------------------------------|
| 1, 3, 15       | `foundations.modal-editing`, `survival.insert-and-back` |
| 2, 7–10        | `survival.open-save-quit`                        |
| 4–6            | `survival.insert-and-back`                       |
| 11, 12         | `survival.undo-redo`                             |
| 13, 14         | `survival.hjkl`                                  |
| 16–20          | `editing.insert-variants`                        |
| 21–24          | `editing.word-motions`                           |
| 25–27          | `editing.line-motions`                           |
| 28–30          | `editing.file-motions`                           |
| 31–35          | `editing.delete`                                 |
| 36–39          | `editing.change`                                 |
| 40–44          | `editing.yank-put`                               |
| 45             | `editing.replace-char`                           |
| 46–49          | `search.pattern`                                 |
| 50–51          | `search.word`                                    |
| 52–57          | `search.find-on-line`                            |
| 58–61          | `counts-visual.counts`                           |
| 62–63          | `counts-visual.percent-bar`                      |
| 64–70          | `counts-visual.char-visual`, `.line-block`, `.tricks` |
| 71–73          | `dot.repeat`, `.with-counts`, `.patterns`        |
| 74–85          | `operators-textobjects.*`                        |
| 86–90          | `scroll.half-full-page`, `.center-top-bottom`    |
| 91–96          | `wider-motions.*`                                |
| 97–104         | `marks.*`                                        |
| 105–118        | `transform.*`                                    |
| 119–125        | `registers.*`                                    |
| 126–130        | `macros.*`                                       |
| 131–135        | `windows.splits`, `.navigate`                    |
| 136–248        | `appendix.keyboard-walk` (split among `survival.hjkl`, `editing.*`, `scroll.*`, etc. — most lessons map *both* to a primary topic and to the keyboard-walk appendix) |
| 249–285        | `prefixes.g-overview`                            |
| 286–316        | `prefixes.z-overview`, `scroll.*`, folding       |
| 317–333        | `prefixes.bracket-pairs`                         |
| 334–365        | `prefixes.ctrl-w`, `windows.*`                   |
| 366–395        | `insert.*`                                       |
| 396–430        | `ex.*`                                           |
| 431–445        | `visual.*`                                       |
| 446–460        | `cmdline.*`, `ex.global`, `ex.norm`              |
| 461–480        | `recipes.*`                                      |
| 481–500        | `advanced.*`                                     |

When a lesson appears in multiple topics (e.g. lesson 21 lives both in
`editing.word-motions` and in `appendix.keyboard-walk`'s `w` entry), only
the *primary* topic embeds the video; the appendix entry uses a `crossref`
to the primary topic.
