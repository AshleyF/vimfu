# Normal Mode

# Basic Motions

## Basic Motions 1 (basic_motions_1)

- h          cursor N chars to the left (motion)
  - <Left>   same as "h" (motion)
  - <BS>     same as "h" (motion)
  - ^H       same as "h" (motion)
- j          cursor N lines downward (motion)
  - <Down>   same as "j" (motion)
  - <NL>     same as "j" (motion)
  - ^J       same as "j" (motion)
  - ^N       same as "j" (motion)
- k          cursor N lines upward (motion)
  - <Up>     same as "k" (motion)
  - ^P       same as "k" (motion)
- l          cursor N chars to the right (motion)
  - <Right>  same as "l" (motion)
  - <Space>  same as "l" (motion)

## Basic Motions 2 (basic_motions_2)

- w            cursor N words forward (motion)
  - <C-Right>  same as "w" (motion)
  - <S-Right>  same as "w" (motion)
- b            cursor N words backward (motion)
  - <C-Left>   same as "b" (motion)
  - <S-Left>   same as "b" (motion)
- e            cursor forward to the end of word N (motion)
- ge           go backwards to the end of the previous word (motion)

## Basic Motions 3 (basic_motions_3)

- W   cursor N WORDS forward (motion)
- B   cursor N WORDS backward (motion)
- E   cursor forward to the end of WORD N (motion)
- gE  go backwards to the end of the previous WORD (motion)

## Basic Motions 4 (basic_motions_4)

- $         cursor to the end of Nth next line (motion)
  - <End>   same as "$" (motion)
  - g$      cursor to rightmost character of current screen line (motion)
  - g<End>  same as "g$" (motion)
- ^         cursor to the first CHAR of the line (motion)
  - g^      cursor to the leftmost non-white character of current screen line (motion)
- 0         cursor to the first char of the line (motion)
  - <Home>  same as "0" (motion)
  - g0      cursor to leftmost character of current screen line (motion)
  - g<Home> same as "g0" (motion)

## Basic Motions 5 (basic_motions_5)

- L           cursor to line N from bottom of screen (motion)
- H           cursor to line N from top of screen (motion)
- M           cursor to middle line of screen (motion)
- gg          cursor to line N, default first line (motion)
  - <C-Home>  same as "gg" (motion)
- G           cursor to line N, default last line (motion)
  - <C-End>   same as "G" (motion)

## Basic Motions 6 (basic_motions_6)

- (  cursor N sentences backward (motion)
- )  cursor N sentences forward (motion)
- {  cursor N paragraphs backward (motion)
- }  cursor N paragraphs forward (motion)

## Basic Motions 7 (basic_motions_7)

- [[  cursor N sections backward (motion)
- []  cursor N SECTIONS backward (motion)
- ][  cursor N SECTIONS forward (motion)
- ]]  cursor N sections forward (motion)

## Basic Motions 8 (basic_motions_8)

- <CR>  cursor to the first CHAR N lines lower (motion)
-   +   same as <CR> (motion)
  - ^M  same as <CR> (motion)
- -     cursor to the first CHAR N lines higher (motion)

# Useless Underscore (useless_underscore)

- _  cursor to the first CHAR N - 1 lines lower (motion)

# Find Character (find_character)

- f{char}  cursor to Nth occurrence of {char} to the right (motion)
- F{char}  cursor to the Nth occurrence of {char} to the left (motion)
- t{char}  cursor till before Nth occurrence of {char} to the right (motion)
- T{char}  cursor till after Nth occurrence of {char} to the left (motion)
- ;        repeat latest f, t, F or T N times (motion)
  - g;     go to N older position in change list (motion)
- ,        repeat latest f, t, F or T in opposite direction N times (motion)
  - g,     go to N newer position in change list (motion)

# Join Lines (join_lines)

- J   Join N lines; default is 2
- gJ  join lines without inserting space

# Quitting (quitting)

- ZZ  write if buffer changed and close window
- ZQ  close window without writing
- ^Z  suspend program (or start new shell)
- Also: `:x` `:wq` `:q!` `:q`

# Reverting (reverting)

- `:e!`

# Scrolling and Jumping (scrolling_and_jumping)

- zt                    redraw, cursor line at top of window
- zb                    redraw, cursor line at bottom of window
- zz                    redraw, cursor line at center of window
- ^Y                    scroll N lines downwards
- ^E                    scroll N lines upwards (N lines Extra)
- ^F                    scroll N screens Forward (motion)
  - <PageDown>          same as ^F
  - <S-Down>            same as ^F (motion)
- ^B                    scroll N screens Backwards (motion)
  - <PageUp>            same as ^B
  - <S-Up>              same as ^B (motion)
- ^D                    scroll Down N lines (default: half a screen)
- ^U                    scroll N lines Upwards (default: half a screen)
- <ScrollWheelDown>     move window three lines down (TODO)
- <S-ScrollWheelDown>   move window one page down (motion) (TODO)
- <ScrollWheelUp>       move window three lines up (TODO)
- <S-ScrollWheelUp>     move window one page up (TODO)
- <ScrollWheelLeft>     move window six columns left (TODO)
- <S-ScrollWheelLeft>   move window one page left (TODO)
- <ScrollWheelRight>    move window six columns right (TODO)
- <S-ScrollWheelRight>  move window one page right (TODO)

# Matching Pairs (matching_pairs)

- %  find the next (curly/square) bracket on this line and go to its match, or go to matching comment bracket, or go to matching preprocessor directive. (motion)

# Changing Case (changing_case)

- ~           'tildeop' off: switch case of N characters under cursor and move the cursor N characters to the right
- ~{motion}   'tildeop' on: switch case of Nmove text
- g~{motion}  swap case for Nmove text
- gu{motion}  make Nmove text lowercase
- gU{motion}  make Nmove text uppercase

# Marks (marks)

- m{A-Za-z}     set mark {A-Za-z} at cursor position
- '{a-zA-Z0-9}  cursor to the first CHAR on the line with mark {a-zA-Z0-9} (motion)
  - g'{mark}    like |'| but without changing the jumplist (motion)
- `{a-zA-Z0-9}  cursor to the mark {a-zA-Z0-9} (motion)
  - g`{mark}    like |`| but without changing the jumplist (motion)

# Search (search)

- *                 search forward for the Nth occurrence of the ident under the cursor (motion)
  - <S-LeftMouse>   same as "*" at the mouse click position
- #                 search backward for the Nth occurrence of the ident under the cursor (motion)
  - <S-RightMouse>  same as "#" at the mouse click position
- /{pattern}<CR>    search forward for the Nth occurrence of {pattern} (motion)
- /<CR>             search forward for {pattern} of last search (motion)
- ?{pattern}<CR>    search backward for the Nth previous occurrence of {pattern} (motion)
- ?<CR>             search backward for {pattern} of last search (motion)
- n                 repeat the latest '/' or '?' N times (motion)
- N                 repeat the latest '/' or '?' N times in opposite direction (motion)
- q/                edit / command-line in command-line window (TODO)
- q?                edit ? command-line in command-line window (TODO)

# Go To Line/Column (line_column)

- G           cursor to line N, default last line (motion) (note: covered in basic motions too)
  - <C-End>   same as "G" (motion) (note: covered in basic motions too)
- |           cursor to column N (motion)
- `:{num}`

# Advanced Selection (advanced_selection)

- Also `o` in visual mode (note: covered in Visual Mode)

Extending selection with `o` and motions. Reselecting with `gv`. And navigating to the start and end of previous selections with `'<` `'>` ``<` ``>`.", keys: ['v_o' /* visual mode o */,'gv',"'<","'>",'`<','`>'], link: 'https://youtube.com/shorts/Ug8q6hafgt4' },

# Visual Modes (visual_modes)

- v             start charwise Visual mode
- V             start linewise Visual mode
- ^V            start blockwise Visual mode
  - ^Q          same as ^v or not used, or used for terminal control flow
- gv            reselect the previous Visual area
- <RightMouse>  start Visual mode, move cursor to the mouse click position (TODO)

# Undo (undo)

- u         undo changes
  - <Undo>  same as "u"
- U         undo all latest changes on one line
- ^R        redo changes which were undone with 'u'

# Delete Character (delete_char)

- ["x]x        delete N characters under and after the cursor [into register x]
  - ["x]<Del>  same as "x"
- ["x]X        delete N characters before the cursor [into register x]

# Jumps (jumps)

- ^O     go to N older entry in jump list (motion)
- <Tab>  go to N newer entry in jump list (motion)
  - ^I   same as <Tab> (motion)
- ''     cursor to the first CHAR of the line where the cursor was before the latest jump. (motion)
- ``     cursor to the position before latest jump (motion)

# Indenting (indenting)

- <{motion}  shift Nmove lines one 'shiftwidth' leftwards
- >{motion}  shift Nmove lines one 'shiftwidth' rightwards
- <<         shift N lines one 'shiftwidth' leftwards
- >>         shift N lines one 'shiftwidth' rightwards
- ={motion}  filter Nmove lines through "indent"
- ==         filter N lines through "indent"
- Also covers `v_<` `v_>` `v_=`

# Replace (replace)

- r{char}  replace N chars with {char}
- R        enter replace mode: overtype existing characters, repeat the entered text N-1 times

# Delete (delete)

- ["x]d{motion}        delete Nmove text [into register x]
- ["x]dd               delete N lines [into register x]
- ["x]D                delete the characters under the cursor until the end of the line and N-1 more lines [into register x]; synonym for "d$"
- Also covers `v_d`

# Put (put)

- ["x]p          put the text [from register x] after the cursor N times
- ["x]P          put the text [from register x] before the cursor N times
- ["x]gP         put the text [from register x] before the cursor N times, leave the cursor after it (TODO)
- <MiddleMouse>  same as "gP" at the mouse click position (TODO)

# Yank (yank)

-["x]y{motion}        yank Nmove text [into register x]
-["x]yy               yank N lines [into register x]
-["x]Y                yank N lines [into register x]; synonym for "yy" Note: Mapped to "y$" by default. |default-mappings|
- Also covers `v_y`

# Patterns (patterns)

- Common patterns of usage: `xp` `deep` `ddp` `ddP` `yyp`

# Text Objects

## Text Objects 1 (text_obj_1)

- a"  double quoted string
- a'  single quoted string
- a`  string in backticks
- i"  double quoted string without the quotes
- i'  single quoted string without the quotes
- i`  string in backticks without the backticks

## Text Objects 2 (text_obj_2)

- ab    "a block" from "[(" to "])" (with braces)
  - a(  same as ab
  - a)  same as ab
- aB    "a Block" from "[{" to "]}" (with brackets)
  - a{  same as aB
  - a}  same as aB
- a[  "a []" from '[' to the matching ']'
  - a]  same as a[
- a<  "a <>" from '<' to the matching '>'
  - a>  same as a<
- ib    "inner block" from "[(" to "])"
  - i(  same as ib
  - i)  same as ib
- iB    "inner Block" from "[{" and "]}"
  - i{  same as iB
  - i}  same as iB
- i[  "inner []" from '[' to the matching ']'
  - i]  same as i[
- i<  "inner <>" from '<' to the matching '>'
  - i>  same as i<

## Text Objects 3 (text_obj_3)

- aw  "a word" (with white space)
- aW  "a WORD" (with white space)
- ap  "a paragraph" (with white space)
- as  "a sentence" (with white space)
- iw  "inner word"
- iW  "inner WORD"
- ip  "inner paragraph"
- is  "inner sentence"

## Text Objects 4 (text_obj_4)

- at  "a tag block" (with white space)
- it  "inner tag block"

# Insert (insert)

- i           insert text before the cursor N times
  - <Insert>  same as "i"
- I           insert text before the first CHAR on the line N times
- a           append text after the cursor N times
- A           append text after the end of the line N times

# Advanced Insert (insert_adv)

- gi  like "i", but first move to the |'^| mark
- gI  like "I", but always start in column 1

# Open Line (open_line)

- o  begin a new line below the cursor and insert text, repeat N times
- O  begin a new line above the cursor and insert text, repeat N times

# Change (change)

- ["x]c{motion}  delete Nmove text [into register x] and start insert
- ["x]cc         delete N lines [into register x] and start insert
- ["x]C          change from the cursor position to the end of the line, and N-1 more lines [into register x]; synonym for "c$"

# Substitute (substitute)

- ["x]s  (substitute) delete N characters [into register x] and start insert
- ["x]S  delete N lines [into register x] and start insert; synonym for "cc".

# Jump Percent (jump_percent)

- {count}%  go to N percentage in the file (motion)

# Counted Motions (counted_motions)

- `{count}l` `{count}j` `{count}h` `{count}k` `{count}w` `{count}b` `{count}/` `{count}f`

# Numbered Lines (numbered_lines)

- G  cursor to line N, default last line (motion) (note: covered in basic motions, and go to line too)
- `:set nu` `:set rnu` `:set nu!` `:set nonu`
- `:{line}`

# Counted Insert (counted_insert)

- `{count}i` `{count}a` `{count}I` `{count}A` `{count}o` `{count}O`

# Delete in Insert Mode (delete_in_insert)

- Insert mode `i_^h` `i_^w` `i_^u`

# Vertical Insert (vertical_insert)

- `vb_I` `vb_A`

# Dot (dot)

- .  repeat last change with count replaced with N

# Macros (macros)

- q{0-9a-zA-Z"}  record typed characters into named register {0-9a-zA-Z"} (uppercase to append)
- q              (while recording) stops recording
- @{a-z}         execute the contents of register {a-z} N times
- @@             repeat the previous @{a-z} N times

# Folds

## Folds 1 (folds1)

- zo  open fold
- zO  open folds recursively
- zc  close a fold
- zC  close folds recursively
- zv  open enough folds to view the cursor line
- za  open a closed fold, close an open fold
- zA  open a closed fold or close an open fold recursively

## Folds 2 (folds2)

- zr  add one to 'foldlevel'
- zR  set 'foldlevel' to the deepest fold
- zm  subtract one from 'foldlevel'
- zM  set 'foldlevel' to zero
- zX  re-apply 'foldlevel'

## Folds 3 (folds3)

- zn  reset 'foldenable'
- zN  set 'foldenable'
- zi  toggle 'foldenable'

## Folds 4 (folds4)

- zj  move to the start of the next fold (motion)
- zk  move to the end of the previous fold (motion)
- [z  move to start of open fold (motion)
- ]z  move to end of open fold (motion)

## Folds 5 (folds5)

- zf{motion}  create a fold for Nmove text
- zF          create a fold for N lines
- zd          delete a fold
- zD          delete folds recursively
- zE          eliminate all folds

# Rot13 (rot13)

- g?    Rot13 encoding operator
- g??   Rot13 encode current line
- g?g?  Rot13 encode current line

# Search Word Advanced (search_word_adv)

- g*  like "*", but without using "\<" and "\>" (motion)
- g#  like "#", but without using "\<" and "\>" (motion)
- gN  find the previous match with the last used search pattern and Visually select it (motion)
- gn  find the next match with the last used search pattern and Visually select it (motion)

# Counts (TODO)

- 1 .. 9        prepend to command to give a count
- {count}<Del>  remove the last digit from {count}

# Commands (TODO)

- :         start entering an Ex command (motion)
- {count}:  start entering an Ex command with range from current line to N-1 lines down
- @:        repeat the previous ":" command N times
- Q         replay last recorded macro
  - gQ      switch to "Ex" mode with Vim editing
- q:        edit : command-line in command-line window

# Leader (TODO)

- \        reserved for extensions
- ^\{a-z}  reserved for extensions

# Increment/Decrement (TODO)

- ^A  add N to number at/after cursor
- ^X  subtract N from number at/after cursor

# Filter

- !{motion}{filter}  filter Nmove text through the {filter} command
- !!{filter}         filter N lines through the {filter} command

# Window

## Size

- ^W +  increase current window height N lines
- ^W -  decrease current window height N lines
- ^W >  increase current window width N columns
- ^W <  decrease current window width N columns
- ^W =  make all windows the same height & width
- ^W _  set current window height to N (default: very high) (CTRL*)
- ^W |  set window width to N columns

## Move

- ^W H  move current window to the far left
- ^W J  move current window to the very bottom
- ^W K  move current window to the very top
- ^W L  move current window to the far right
- ^W R  rotate windows upwards N times
- ^W r  rotate windows downwards N times (CTRL*)
- ^W x  exchange current window with window N (default: next window) (CTRL*)

## Navigate

- ^W P          go to preview window
- ^W p          go to previous (last accessed) window (CTRL*)
- ^W W          go to N previous window (wrap around)
- ^W b          go to bottom window (CTRL*)
- ^W h          go to Nth left window (stop at first window) (CTRL*)
  - ^W <Left>   same as "^W h"
- ^W j          go N windows down (stop at last window) (CTRL*)
  - ^W <Down>   same as "^W j"
- ^W k          go N windows up (stop at first window) (CTRL*)
  - ^W <Up>     same as "^W k"
- ^W l          go to Nth right window (stop at last window) (CTRL*)
  - ^W <Right>  same as "^W l"
- ^W t          go to top window (CTRL*)
- ^W w          go to N next window (wrap around) (CTRL*)

## Split

- ^W ^    split current window and edit alternate file N (CTRL*)
- ^W d    split window and jump to definition under the cursor (CTRL*)
- ^W f    split window and edit file name under the cursor (CTRL*)
- ^W F    split window and edit file name under the cursor and jump to the line number following the file name.
- ^W i    split window and jump to declaration of identifier under the cursor (CTRL*)
- ^W s    split current window in two parts, new window N lines high (CTRL*)
  - ^W S  same as "^W s"
- ^W v    split current window vertically, new window N columns wide (CTRL*)

## New/Close

- ^W n  open new window, N lines high (CTRL*)
- ^W c  close current window (like |:close|) (CTRL*)
- ^W o  close all but current window (like |:only|) (CTRL*)
- ^W q  quit current window (like |:quit|) (CTRL*)
- ^W z  close preview window (CTRL*)

## Tabs

- ^W T        move current window to a new tab page
- ^W g f      edit file name under the cursor in a new tab page (CTRL*)
- ^W g F      edit file name under the cursor in a new tab page and jump to the line number following the file name. (CTRL*)
- ^W g t      same as `gt`: go to next tab page (CTRL*)
- ^W g T      same as `gT`: go to previous tab page (CTRL*)
- ^W g <Tab>  same as |g<Tab>|: go to last accessed tab page (CTRL*)
- g<Tab>      go to last accessed tab page
  - ^<Tab>    same as `g<Tab>` : go to last accessed tab page
  - <C-Tab>    as "g<Tab>"
- gT          go to the previous tab page
- gt          go to the next tab page

# Tags

- ^W g }          do a |:ptjump| to the tag under the cursor (CTRL*)
- ^W }            show tag under cursor in preview window
- ^W g ^]         split window and do |:tjump| to tag under cursor (CTRL*)
- ^W g ]          split window and do |:tselect| for tag under cursor (CTRL*)
- ^T              jump to N older Tag in tag list
  - <C-RightMouse>  same as "^T"
- g ^]            |:tjump| to the tag under the cursor
- g]              :tselect on the tag under the cursor
- ^W ]            split window and jump to tag under cursor (CTRL*)

# Search & Replace

- :s/foo/bar/g
- :%s/foo/bar/g
- /gi
- /gc
- &   repeat last :s
- g&  repeat last ":s" on all lines

# Keyword

- K  lookup Keyword under the cursor with 'keywordprg'

# TODO

^C               interrupt current (search) command
^G               display current file name and position
^L               redraw screen
^[ <Esc>         not used
^\ ^N        go to Normal mode (no-op)
^\ ^G        go to Normal mode (no-op)
^]               :ta to ident under cursor
^^               edit Nth alternate file (equivalent to ":e #N")
"{register}          use {register} for next delete, yank or put ({.%#:} only work with put)
'(                   1  cursor to the first CHAR on the line of the start of the current sentence
')                   1  cursor to the first CHAR on the line of the end of the current sentence
'<                   1  cursor to the first CHAR of the line where highlighted area starts/started in the current buffer.
'>                   1  cursor to the first CHAR of the line where highlighted area ends/ended in the current buffer.
'[                   1  cursor to the first CHAR on the line of the start of last operated text or start of put text
']                   1  cursor to the first CHAR on the line of the end of last operated text or end of put text
'{                   1  cursor to the first CHAR on the line of the start of the current paragraph
'}                   1  cursor to the first CHAR on the line of the end of the current paragraph
`(                   1  cursor to the start of the current sentence
`)                   1  cursor to the end of the current sentence
`<                   1  cursor to the start of the highlighted area
`>                   1  cursor to the end of the highlighted area
`[                   1  cursor to the start of last operated text or start of putted text
`]                   1  cursor to the end of last operated text or end of putted text
`{                   1  cursor to the start of the current paragraph
`}                   1  cursor to the end of the current paragraph
do                   2  same as ":diffget"
dp                   2  same as ":diffput"
<C-LeftMouse>        ":ta" to the keyword at the mouse click
<F1>                 same as <Help>
<Help>               open a help window
<LeftMouse>          1  move cursor to the mouse click position

[^D    jump to first #define found in current and included files matching the word under the cursor, start searching at beginning of current file
[^I   jump to first line in current and included files that contains the word under the cursor, start searching at beginning of current file
[# 1  cursor to N previous unmatched #if, #else or #ifdef
[' 1  cursor to previous lowercase mark, on first non-blank
[(    1  cursor N times back to unmatched '('
[*    1  same as "[/"
[`    1  cursor to previous lowercase mark
[/    1  cursor to N previous start of a C comment
[D       list all defines found in current and included files matching the word under the cursor, start searching at beginning of current file
[I       list all lines found in current and included files that contain the word under the cursor, start searching at beginning of current file
[P    2  same as "[p"
[c    1  cursor N times backwards to start of change
[d       show first #define found in current and included files matching the word under the cursor, start searching at beginning of current file
[f       same as "gf"
[i       show first line found in current and included files that contains the word under the cursor, start searching at beginning of current file
[m    1  cursor N times back to start of member function
[p    2  like "P", but adjust indent to current line
[s    1  move to the previous misspelled word
[{    1  cursor N times back to unmatched '{'
[<MiddleMouse>  2  same as "[p"
]^D     jump to first #define found in current and included files matching the word under the cursor, start searching at cursor position
]^I     jump to first line in current and included files that contains the word under the cursor, start searching at cursor position
]#    1  cursor to N next unmatched #endif or #else
]'    1  cursor to next lowercase mark, on first non-blank
])    1  cursor N times forward to unmatched ')'
]*    1  same as "]/"
]`    1  cursor to next lowercase mark
]/    1  cursor to N next end of a C comment
]D       list all #defines found in current and included files matching the word under the cursor, start searching at cursor position
]I       list all lines found in current and included files that contain the word under the cursor, start searching at cursor position
]P    2  same as "[p"
]c    1  cursor N times forward to start of change
]d       show first #define found in current and included files matching the word under the cursor, start searching at cursor position
]f       same as "gf"
]i       show first line found in current and included files that contains the word under the cursor, start searching at cursor position
]m    1  cursor N times forward to end of member function
]p    2  like "p", but adjust indent to current line
]s    1  move to next misspelled word
]}    1  cursor N times forward to unmatched '}'
]<MiddleMouse>  2  same as "]p"

g^A       dump a memory profile
g^G     show information about current cursor position
g^H     start Select block mode
g+       go to newer text state N times
g-       go to older text state N times
g8       print hex value of bytes used in UTF-8 character under the cursor
g<       display previous command output
gD    1  go to definition of word under the cursor in current file
gH       start Select line mode
gR    2  enter Virtual Replace mode
gV       don't reselect the previous Visual area when executing a mapping or menu in Select mode
g_    1  cursor to the last CHAR N - 1 lines lower
ga       print ascii value of character under the cursor
gd    1  go to definition of word under the cursor in current function
gf       start editing the file whose name is under the cursor
gF       start editing the file whose name is under the cursor and jump to the line number following the filename.
gh       start Select mode
gj    1  like "j", but when 'wrap' on go N screen lines down
gk    1  like "k", but when 'wrap' on go N screen lines up
gm    1  go to character at middle of the screenline
gM    1  go to character at middle of the text line
go    1  cursor to byte N in the buffer
["x]gp    2  put the text [from register x] after the cursor N times, leave the cursor after it
gq{motion}  2  format Nmove text
gr{char}  2  virtual replace N chars with {char}
gs       go to sleep for N seconds (default 1)
gw{motion}  2  format Nmove text and keep cursor
gx       execute application for file name under the cursor (only with |netrw| plugin)
g@{motion}     call 'operatorfunc'
g<Down>    1  same as "gj"
g<LeftMouse>     same as <C-LeftMouse>
g<MiddleMouse>     same as <C-MiddleMouse>
g<RightMouse>     same as <C-RightMouse>
g<Up>    1  same as "gk"

z<CR>       redraw, cursor line to top of window, cursor on first non-blank
z{height}<CR>     redraw, make window {height} lines high
z+       cursor on line N (default line below window), otherwise like "z<CR>"
z-       redraw, cursor line at bottom of window, cursor on first non-blank
z.       redraw, cursor line to center of window, cursor on first non-blank
z=       give spelling suggestions
zG       temporarily mark word as correctly spelled
zH       when 'wrap' off scroll half a screenwidth to the right
zL       when 'wrap' off scroll half a screenwidth to the left
zW       temporarily mark word as incorrectly spelled
z^       cursor on line N (default line above window), otherwise like "z-"
ze       when 'wrap' off scroll horizontally to position the cursor at the end (right side) of the screen
zg       permanently mark word as correctly spelled
zh       when 'wrap' off scroll screen N characters to the right
zl       when 'wrap' off scroll screen N characters to the left
zp       paste in block-mode without trailing spaces
zP       paste in block-mode without trailing spaces
zs       when 'wrap' off scroll horizontally to position the cursor at the start (left side) of the screen
zuw       undo |zw|
zug       undo |zg|
zuW       undo |zW|
zuG       undo |zG|
zw       permanently mark word as incorrectly spelled
zx       re-apply 'foldlevel' and do "zv"
zy       yank without trailing spaces
z<Left>       same as "zh"
z<Right>     same as "zl"

==============================================================================
2.6 Operator-pending mode      *operator-pending-index*
These can be used after an operator, but before a {motion} has been entered.

|o_v|    v    force operator to work charwise
|o_V|    V    force operator to work linewise
|o_^V|  ^V    force operator to work blockwise