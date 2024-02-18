# VimFu Fun Curriculum

## Folds

Folding allows us to hide hierarchical sections.
This may be language specific or can set the foldmethod, or fdm for short, to indent, where each level of indenting becomes a fold.

//  Folds 1  zo zO zc zC za zA zv

We can collapse folds with zc.
We can open folds again with zo.
Or we can toggle folds with za.

If we collapse folds repeatedly (zc zc) it works up the heirarchy.
There are recursive versions of zc zo and za.
We can use zC to collapse folds recursively to the root.
Or zO to open folds recursively.
Or zA to toggle folds recursively.

Finally, notice that when we collapse our cursor position is remembered.
We can open open to view the cursor with zv.

## Miscellaneous

Normal Mode

a        After
b        Back
c        Change
d        Delete
e        End
f        Find
g        *
h        Left
i        Insert
j        Down
k        Up
l        Right
m        Mark
n        Next
o        Open
p        Paste
q        Record
r        Replace char
s        Substitute
t        Till
u        Undo
v        Visual
w        Word
x        Delete
y        Yank
z        * 
A        After line
B        Back WORD
C        Change to end of line
D        Delete to end of line
E        End WORD
F        Find (reversed)
G        End document
H        High
I        Insert before line
J        Join
K        Keyword lookup
L        Low
M        Middle
N        Next (reversed)
O        Open before
P        Paste before
Q        Ex mode
R        Replace mode
S        Substitute line 
T        To (reversed)
U        Undo line
V        Visual line
W        WORD
X        Delete before
Y        Yank line
Z        *
<BS>     Left
<Space>  Right
<Del>    Delete
<Enter>  Down
<Left>   Left
<Right>  Right
<Down>   Down
<Up>     Up
1 - 9    Count
0        First char of line
^        Start of line
$        End of line
~        Toggle case
`        Jump to marked char
'        Jump to marked line
!
@        Play macro
*        Find word
#        Find word (reversed)
%        Matching
&        Repeat substitution
(        Back sentence
)        Forward sentence
{        Back paragraph
}        Forward paragraph
[        * 
]        *
_        [count] - 1 lines down (first non-whitespace)
+        Next line (first non-whitespace)
-        Previous line (first non-whitespace)
=        Format [motion]
|        Column
\        Leader
:        Command
;        Repeat f/t/F/T
,        Repeat f/t/F/T (reversed)
"        Register
>        Indent
<        Unindent
.        Repeat
/        Search
?        Search (reversed)

gg       Start of document
zt       Scroll top
zz       Scroll middle
zb       Scroll bottom
dd       Delete line
cc       Change line
yy       Yank line
==       Format lines
>>       Indent line
<<       Unindent line
ZZ       Save and quit file
@@       Replay last macro
[(       Previous (
])       Next )
[{       Previous {
]}       Next }
[[       Previous section (or { in first column)
[]       Previous section (or } in first column)
]]       Next section (or { in first column)
][       Next section (or } in first column)

<C-e>    Scroll up line
<C-y>    Scroll down line
<C-f>    Forward screen
<C-b>    Back screen
<C-u>    Up half-screen
<C-d>    Down half-screen

"*y/d/p  Yank/Delete/Paste using system clipboard

Visual

c        Change selected
C        Change lines selected
d/x      Delete selected
D/X      Delete lines selected
y        Yank selected
Y        Yank lines selected
J        Join selected
r        Replace selected (with next char)
R        Replace line selected
p/P      Paste over selected
s        Substitute over selected
S        Substitute over line selected
u        Selection to lowercase
U        Selection to uppercase
~        Toggle selection case
>        Indent selected lines
<        Unindent selected lines
=        Format selected lines
v        Change to char selection mode
V        Change to line selection mode
<C-v>    Change to visual block mode
<Del>    Delete selection

Jumps

''       Line before last jump
``       Char before last jump
'. `.    Last changed line/char
'< `<    First line/char of last visual selection
'> `>    Last line/char of last visual selection
'^ `^    Last insert mode stop line/char 

Motion Capture

a/ib       Around/In block
a/iB       Around/In BLOCK
a/ip       Around/In paragraph
a/is       Around/In sentence
a/iw       Around/In word
a/iW       Around/In WORD
a/i"       Around/In quotes
a/i'       Around/In quotes
a/i`       Around/In quotes
a/i]       Around/In brackets
a/i[       Around/In brackets
a/i(       Around/In parens
a/i)       Around/In parens
a/i<       Around/In angle brackets
a/i>       Around/In angle brackets
a/i{       Around/In braces
a/i}       Around/In braces

Insert Mode

<C-o>    Single normal mode command
<C-w>    Delete word

Commands

:w       Write file
:q       Quit file
:x       Save and quit file
:e foo   Edit file

--------------------------------------------------------------------------------------------

Verbs

v (visual)
c (change)
d (delete)
y (yank/copy)

Modifiers

i (inside)
a (around)
t (till)
f (find)
/ (search)

Objects

w (word)
s (sentence)
p (paragraph)
b (block/parentheses)
t (tag)

Surround Plugin

Visually select a word and surround it with quotes: viwS”
Change surround from single quote to double quote: cs’”

--------------------------------------------------------------------------------------------

Some nice trics from Practical Vim

!{motion}
q/ q:
cnoremap <C-p> <Up>
cnoremap <C-n> <Down>
:set history=200
*cwfoo<Esc>:%s//<C-r><C-w>/g
<C-o> in normal mode to navigate the jump list
:%normal i//

--------------------------------------------------------------------------------------------

Order of things in the tutor:

hjkl
<esc>:q!
x
i<esc>
A
:wq{Enter}
dw
d$
d{motion} w e $
2w 3e 0
d[count]{motion}
dd 2dd
u U {Ctrl-R}
p
r{char}
ce
c[count]{motion}
{Ctrl-G} G gg
/ ? n N {Ctrl-O} {Ctrl-I}
%
:s/old/new/[g][c]
:!<command>{Enter} :!ls{Enter} :!dir{Enter}
:w TEST{Enter} :!rm TEST{Enter} :!del TEST{Enter}
v{motion} including using with commands (e.g. vG:w TEST)
:r TEST (merge file) :r !ls
o O
a
R
y yw v{motion}y
:set ic  :set hls is  :set noic nohls nois
{Help} {F1} :help  {Ctrl-W}{Ctrl-W}  :q{Enter}
vimrc
{Ctrl-D}{Tab} (on command line for completion)

--------------------------------------------------------------------------------------------

Normal Mode

	Key synonyms

		b {ShiftLeft}
		h {Left} {Ctrl-H} {BS}
		i {Insert}
		j {Down} {Ctrl-J} {NL} {Ctrl-N}
		k {Up} {Ctrl-P}
		l {Right} {Space}
		u {Undo}
		w {ShiftRight}
		x {Del}
		# {PoundSign}
		$ {End}
		- {Minus}
		+ {Ctrl-M} {CR}
		B {Ctrl-Left}
		W {Ctrl-Right}

	Grammar

		Commands

			[count]a
			["x]c{motion}

		Motions

			[count]b

	Instructions

		Append
		Move

	Motions

		BackWord

- Marks a-z are "local", A-Z0-9 may span files
- Dot with count replaces count of thing being repeated
- Search patters allow offsets
- Jumplist maintained
- Y should be y$ (inconsistency)
- Visual mode is extended/contracted by text objects and motions
- Changes in Visual mode affect the selection
- In Visual mode, insert keys (i, a, o) have special meaning (O acts like o? A switched to insert?)
- In Visual mode o switched cursor sides (allows extension either way)

a  -> 1 Append
2a -> 2 Append
b  -> 1 BackWord
3b -> 2 BackWord
cb -> [1 BackWord] 1 Change
c2b -> [2 BackWord] 1 Change
3c2b -> [2 BackWord] 3 Change

-----------------

Grammar from Vim docs:

Normal Mode:

0                          Motion (exclusive)
1-9                        Count
!                          ?
#                          Motion (C pattern)
$                          Motion (C inclusive)
%                          Motion (inclusive)       No count (actual percentage)
^                          Motion (exclusive)       Docs say "unexpectedly" doesn't support count
&                          Change                   Synonym :s
*                          Motion (C exclusive?)
(                          Motion (C exclusive)
)                          Motion (C exclusive)
-                          Motion (C linewise)
={motion}                  ? (C)
\                          Reserved
`{a-zA-Z0-9}               Motion
[                          *
]                          *
;                          Motion (C inclusive)
,                          Motion (C inclusive)
.                          Change (C)
/{pattern}[/]<CR>          Motion (C exclusive)
a                          Insert (C)
b                          Motion (C exclusive)
c{motion}                  Change (C R)
d{motion}                  Change (C R)
e                          Motion (C inclusive)
f{char}                    Motion (C inclusive)
g                          *
h                          Motion (C exclusive)
i                          Insert (C)
j                          Motion (C linewise)
k                          Motion (C linewise)
l                          Motion (C exclusive)
m{a-zA-Z'`[]}              Operator
n                          Motion (C last-pattern)
o                          Insert (C)
p                          Change (C R)
q{0-9a-zA-Z"}              Operator
r{char}                    Change (C)
s                          Change (C R)             Synonym cl
t{char}                    Motion (C inclusive)
u                          Operator (C)
v                          Mode (Visual)
w                          Motion (C exclusive)
x                          Change (C R)             Synonym dl
y{motion}                  Change (C R)
z                          *
A                          Insert (C)
B                          Motion (C exclusive)
C                          Change (C R)             Synonym c$
D                          Change (C R)             Synonym d$
E                          Motion (C inclusive)
F{char}                    Motion (C exclusive)
G                          Motion (C linewise)
H                          Motion (C linewise)
I                          Insert (C)
J                          Change (C)
K                          ?
L                          Motion (C linewise)
M                          Motion (C linewise)
N                          Motion (C last-pattern)
O                          Insert (C)
P                          Change (C R)
Q                          Mode (Ex)
R                          Mode (Replace)
S                          Change (S R linewise)    Synonym cc
T{char}                    Motion (C exclusive)
U                          Change
V                          Mode (Visual-Line)
W                          Motion (C exclusive)
X                          Change (C R)             Synonym dh
Y                          Change (C R linewise)
Z                          *
_                          Motion (C linewise)
+                          Motion (C linewise)
|                          Motion (C exclusive)
~[motion]                  Motion                   Default l motion
{                          Motion (C exclusive)
[count]}                   Motion (exclusive)
:                          *
"{a-zA-Z0-9.%#:-"}         Register                 .%#: only work with put
<{motion}                  Change (C)
>{motion}                  Change (C)
?{pattern}[?]<CR>          Motion (C exclusive)

Visual Mode:

v[text-objects][motions]   

Text Objects:

a{object}                 Text object (around)
i{object}                 Text object (inner)
w
W
s
p
[
]
(
)
b
B
<
>
t
{
}
"
'
`

-----------------------------------------------------------------------

How to learn Vim

- Normal mode is "normal"
    - Always hit <Esc> after each thought
    - Keys, front right pocket (except when driving)
    - Sublime - "vintage_start_in_command_mode": true
- Learn lowercase alphabet
    - Except g and z
- Learn symbols
- Learn uppercase alphabet
- Learn control keys
- Learn insert mode things
- Learn enough to be comfortable, then go "cold turkey"
    - Basic motions, visual mode, delete, copy/paste, ...
    - Learn a few insert mode tricks: <C-o>, <C-w>, ...
- Hands off the mouse (never use "select mode")
- Hands off the arrows
- Hands off the hjkl keys?
- More thinking, less mindless keystrokes
    - Like Petrus method