# Exhaustive Key Bindings

## Insert Mode

|i_CTRL-@|	CTRL-@		insert previously inserted text and stop insert
|i_CTRL-A|	CTRL-A		insert previously inserted text
|i_CTRL-C|	CTRL-C		quit insert mode, without checking for abbreviation
|i_CTRL-D|	CTRL-D		delete one shiftwidth of indent in the current line
|i_CTRL-E|	CTRL-E		insert the character which is below the cursor
		CTRL-F		not used (but by default it's in 'cinkeys' to re-indent the current line)
|i_CTRL-G_j|	CTRL-G CTRL-J	line down, to column where inserting started
|i_CTRL-G_j|	CTRL-G j	line down, to column where inserting started
|i_CTRL-G_j|	CTRL-G <Down>	line down, to column where inserting started
|i_CTRL-G_k|	CTRL-G CTRL-K	line up, to column where inserting started
|i_CTRL-G_k|	CTRL-G k	line up, to column where inserting started
|i_CTRL-G_k|	CTRL-G <Up>	line up, to column where inserting started
|i_CTRL-G_u|	CTRL-G u	start new undoable edit
|i_CTRL-G_U|	CTRL-G U	don't break undo with next cursor movement
|i_<BS>|	<BS>		delete character before the cursor
|i_digraph|	{char1}<BS>{char2} enter digraph (only when 'digraph' option set)
|i_CTRL-H|	CTRL-H		same as <BS>
|i_<Tab>|	<Tab>		insert a <Tab> character
|i_CTRL-I|	CTRL-I		same as <Tab>
|i_<NL>|	<NL>		same as <CR>
|i_CTRL-J|	CTRL-J		same as <CR>
|i_CTRL-K|	CTRL-K {char1} {char2} enter digraph
|i_<CR>|	<CR>		begin new line
|i_CTRL-M|	CTRL-M		same as <CR>
|i_CTRL-N|	CTRL-N		find next match for keyword in front of the cursor
|i_CTRL-O|	CTRL-O		execute a single command and return to insert mode
|i_CTRL-P|	CTRL-P		find previous match for keyword in front of the cursor
|i_CTRL-Q|	CTRL-Q		same as CTRL-V, unless used for terminal control flow
|i_CTRL-SHIFT-Q|  CTRL-SHIFT-Q {char} like CTRL-Q unless |tui-modifyOtherKeys| is active
|i_CTRL-R|	CTRL-R {register} insert the contents of a register
|i_CTRL-R_CTRL-R| CTRL-R CTRL-R {register} insert the contents of a register literally
|i_CTRL-R_CTRL-O| CTRL-R CTRL-O {register} insert the contents of a register literally and don't auto-indent
|i_CTRL-R_CTRL-P| CTRL-R CTRL-P {register} insert the contents of a register literally and fix indent.
		CTRL-S		not used or used for terminal control flow
|i_CTRL-T|	CTRL-T		insert one shiftwidth of indent in current line
|i_CTRL-U|	CTRL-U		delete all entered characters in the current line
|i_CTRL-V|	CTRL-V {char}	insert next non-digit literally
|i_CTRL-SHIFT-V|  CTRL-SHIFT-V {char} like CTRL-V unless |tui-modifyOtherKeys| is active
|i_CTRL-V_digit| CTRL-V {number} insert three digit decimal number as a single byte.
|i_CTRL-W|	CTRL-W		delete word before the cursor
|i_CTRL-X|	CTRL-X {mode}	enter CTRL-X sub mode, see |i_CTRL-X_index|
|i_CTRL-Y|	CTRL-Y		insert the character which is above the cursor
|i_<Esc>|	<Esc>		end insert mode
|i_CTRL-[|	CTRL-[		same as <Esc>
|i_CTRL-\_CTRL-N| CTRL-\ CTRL-N	go to Normal mode
|i_CTRL-\_CTRL-G| CTRL-\ CTRL-G	go to Normal mode
		CTRL-\ a - z	reserved for extensions
		CTRL-\ others	not used
|i_CTRL-]|	CTRL-]		trigger abbreviation
|i_CTRL-^|	CTRL-^		toggle use of |:lmap| mappings
|i_CTRL-_|	CTRL-_		When 'allowrevins' set: change language (Hebrew)

		<Space> to '~'	not used, except '0' and '^' followed by CTRL-D

|i_0_CTRL-D|	0 CTRL-D	delete all indent in the current line
|i_^_CTRL-D|	^ CTRL-D	delete all indent in the current line, restore it in the next line

|i_<Del>|	<Del>		delete character under the cursor

		Meta characters (0x80 to 0xff, 128 to 255) not used

|i_<Left>|	<Left>		cursor one character left
|i_<S-Left>|	<S-Left>	cursor one word left
|i_<C-Left>|	<C-Left>	cursor one word left
|i_<Right>|	<Right>		cursor one character right
|i_<S-Right>|	<S-Right>	cursor one word right
|i_<C-Right>|	<C-Right>	cursor one word right
|i_<Up>|	<Up>		cursor one line up
|i_<S-Up>|	<S-Up>		same as <PageUp>
|i_<Down>|	<Down>		cursor one line down
|i_<S-Down>|	<S-Down>	same as <PageDown>
|i_<Home>|	<Home>		cursor to start of line
|i_<C-Home>|	<C-Home>	cursor to start of file
|i_<End>|	<End>		cursor past end of line
|i_<C-End>|	<C-End>		cursor past end of file
|i_<PageUp>|	<PageUp>	one screenful backward
|i_<PageDown>|	<PageDown>	one screenful forward
|i_<F1>|	<F1>		same as <Help>
|i_<Help>|	<Help>		stop insert mode and display help window
|i_<Insert>|	<Insert>	toggle Insert/Replace mode
|i_<LeftMouse>|	<LeftMouse>	cursor at mouse click
|i_<ScrollWheelDown>|	<ScrollWheelDown>	move window three lines down
|i_<S-ScrollWheelDown>|	<S-ScrollWheelDown>	move window one page down
|i_<ScrollWheelUp>|	<ScrollWheelUp>		move window three lines up
|i_<S-ScrollWheelUp>|	<S-ScrollWheelUp>	move window one page up
|i_<ScrollWheelLeft>|	<ScrollWheelLeft>	move window six columns left
|i_<S-ScrollWheelLeft>|	<S-ScrollWheelLeft>	move window one page left
|i_<ScrollWheelRight>|	<ScrollWheelRight>	move window six columns right
|i_<S-ScrollWheelRight>| <S-ScrollWheelRight>	move window one page right

commands in CTRL-X submode				*i_CTRL-X_index*

|i_CTRL-X_CTRL-D|	CTRL-X CTRL-D	complete defined identifiers
|i_CTRL-X_CTRL-E|	CTRL-X CTRL-E	scroll up
|i_CTRL-X_CTRL-F|	CTRL-X CTRL-F	complete file names
|i_CTRL-X_CTRL-I|	CTRL-X CTRL-I	complete identifiers
|i_CTRL-X_CTRL-K|	CTRL-X CTRL-K	complete identifiers from dictionary
|i_CTRL-X_CTRL-L|	CTRL-X CTRL-L	complete whole lines
|i_CTRL-X_CTRL-N|	CTRL-X CTRL-N	next completion
|i_CTRL-X_CTRL-O|	CTRL-X CTRL-O	omni completion
|i_CTRL-X_CTRL-P|	CTRL-X CTRL-P	previous completion
|i_CTRL-X_CTRL-S|	CTRL-X CTRL-S	spelling suggestions
|i_CTRL-X_CTRL-T|	CTRL-X CTRL-T	complete identifiers from thesaurus
|i_CTRL-X_CTRL-Y|	CTRL-X CTRL-Y	scroll down
|i_CTRL-X_CTRL-U|	CTRL-X CTRL-U	complete with 'completefunc'
|i_CTRL-X_CTRL-V|	CTRL-X CTRL-V	complete like in : command line
|i_CTRL-X_CTRL-Z|	CTRL-X CTRL-Z	stop completion, keeping the text as-is
|i_CTRL-X_CTRL-]|	CTRL-X CTRL-]	complete tags
|i_CTRL-X_s|		CTRL-X s	spelling suggestions

commands in completion mode (see |popupmenu-keys|)

|complete_CTRL-E| CTRL-E	stop completion and go back to original text
|complete_CTRL-Y| CTRL-Y	accept selected match and stop completion
		CTRL-L		insert one character from the current match
		<CR>		insert currently selected match
		<BS>		delete one character and redo search
		CTRL-H		same as <BS>
		<Up>		select the previous match
		<Down>		select the next match
		<PageUp>	select a match several entries back
		<PageDown>	select a match several entries forward
		other		stop completion and insert the typed character

## Normal Mode

|CTRL-\_CTRL-N|	CTRL-\ CTRL-N	   go to Normal mode (no-op) Insert mode?
|CTRL-\_CTRL-G|	CTRL-\ CTRL-G	   go to Normal mode (no-op) Insert mode?

## Operator-pending Mode

These can be used after an operator, but before a {motion} has been entered.

|o_v|		v		force operator to work charwise
|o_V|		V		force operator to work linewise
|o_CTRL-V|	CTRL-V		force operator to work blockwise

## Visual Mode

Most commands in Visual mode are the same as in Normal mode.  The ones listed
here are those that are different.

|v_CTRL-\_CTRL-N| CTRL-\ CTRL-N	   stop Visual mode
|v_CTRL-\_CTRL-G| CTRL-\ CTRL-G	   go to Normal mode
|v_CTRL-A|	CTRL-A		2  add N to number in highlighted text
|v_CTRL-C|	CTRL-C		   stop Visual mode
|v_CTRL-G|	CTRL-G		   toggle between Visual mode and Select mode
|v_<BS>|	<BS>		2  Select mode: delete highlighted area
|v_CTRL-H|	CTRL-H		2  same as <BS>
|v_CTRL-O|	CTRL-O		   switch from Select to Visual mode for one command
|v_CTRL-V|	CTRL-V		   make Visual mode blockwise or stop Visual mode
|v_CTRL-X|	CTRL-X		2  subtract N from number in highlighted text
|v_<Esc>|	<Esc>		   stop Visual mode
|v_CTRL-]|	CTRL-]		   jump to highlighted tag
|v_!|		!{filter}	2  filter the highlighted lines through the external command {filter}
|v_:|		:		   start a command-line with the highlighted lines as a range
|v_<|		<		2  shift the highlighted lines one 'shiftwidth' left
|v_=|		=		2  filter the highlighted lines through the external program given with the 'equalprg' option
|v_>|		>		2  shift the highlighted lines one 'shiftwidth' right
|v_b_A|		A		2  block mode: append same text in all lines, after the highlighted area
|v_C|		C		2  delete the highlighted lines and start insert
|v_D|		D		2  delete the highlighted lines
|v_b_I|		I		2  block mode: insert same text in all lines, before the highlighted area
|v_J|		J		2  join the highlighted lines
|v_K|		K		   run 'keywordprg' on the highlighted area
|v_O|		O		   move horizontally to other corner of area
|v_P|		P		   replace highlighted area with register contents; registers are unchanged Q		   does not start Ex mode
|v_R|		R		2  delete the highlighted lines and start insert
|v_S|		S		2  delete the highlighted lines and start insert
|v_U|		U		2  make highlighted area uppercase
|v_V|		V		   make Visual mode linewise or stop Visual mode
|v_X|		X		2  delete the highlighted lines
|v_Y|		Y		   yank the highlighted lines
|v_aquote|	a"		   extend highlighted area with a double quoted string
|v_a'|		a'		   extend highlighted area with a single quoted string
|v_a(|		a(		   same as ab
|v_a)|		a)		   same as ab
|v_a<|		a<		   extend highlighted area with a <> block
|v_a>|		a>		   same as a<
|v_aB|		aB		   extend highlighted area with a {} block
|v_aW|		aW		   extend highlighted area with "a WORD"
|v_a[|		a[		   extend highlighted area with a [] block
|v_a]|		a]		   same as a[
|v_a`|		a`		   extend highlighted area with a backtick quoted string
|v_ab|		ab		   extend highlighted area with a () block
|v_ap|		ap		   extend highlighted area with a paragraph
|v_as|		as		   extend highlighted area with a sentence
|v_at|		at		   extend highlighted area with a tag block
|v_aw|		aw		   extend highlighted area with "a word"
|v_a{|		a{		   same as aB
|v_a}|		a}		   same as aB
|v_c|		c		2  delete highlighted area and start insert
|v_d|		d		2  delete highlighted area
|v_g_CTRL-A|	g CTRL-A	2  add N to number in highlighted text
|v_g_CTRL-X|	g CTRL-X	2  subtract N from number in highlighted text
|v_gJ|		gJ		2  join the highlighted lines without inserting spaces
|v_gq|		gq		2  format the highlighted lines
|v_gv|		gv		   exchange current and previous highlighted area
|v_iquote|	i"		   extend highlighted area with a double quoted string (without quotes)
|v_i'|		i'		   extend highlighted area with a single quoted string (without quotes)
|v_i(|		i(		   same as ib
|v_i)|		i)		   same as ib
|v_i<|		i<		   extend highlighted area with inner <> block
|v_i>|		i>		   same as i<
|v_iB|		iB		   extend highlighted area with inner {} block
|v_iW|		iW		   extend highlighted area with "inner WORD"
|v_i[|		i[		   extend highlighted area with inner [] block
|v_i]|		i]		   same as i[
|v_i`|		i`		   extend highlighted area with a backtick quoted string (without the backticks)
|v_ib|		ib		   extend highlighted area with inner () block
|v_ip|		ip		   extend highlighted area with inner paragraph
|v_is|		is		   extend highlighted area with inner sentence
|v_it|		it		   extend highlighted area with inner tag block
|v_iw|		iw		   extend highlighted area with "inner word"
|v_i{|		i{		   same as iB
|v_i}|		i}		   same as iB
|v_o|		o		   move cursor to other corner of area
|v_p|		p		   replace highlighted area with register contents; deleted text in unnamed register
|v_r|		r		2  replace highlighted area with a character
|v_s|		s		2  delete highlighted area and start insert
|v_u|		u		2  make highlighted area lowercase
|v_v|		v		   make Visual mode charwise or stop Visual mode
|v_x|		x		2  delete the highlighted area
|v_y|		y		   yank the highlighted area
|v_~|		~		2  swap case for the highlighted area

## Command-line Editing

Get to the command-line with the ':', '!', '/' or '?' commands.
Normal characters are inserted at the current cursor position.
"Completion" below refers to context-sensitive completion.  It will complete
file names, tags, commands etc. as appropriate.

		CTRL-@		not used
|c_CTRL-A|	CTRL-A		do completion on the pattern in front of the cursor and insert all matches
|c_CTRL-B|	CTRL-B		cursor to begin of command-line
|c_CTRL-C|	CTRL-C		same as <Esc>
|c_CTRL-D|	CTRL-D		list completions that match the pattern in front of the cursor
|c_CTRL-E|	CTRL-E		cursor to end of command-line
|'cedit'|	CTRL-F		default value for 'cedit': opens the command-line window; otherwise not used
|c_CTRL-G|	CTRL-G		next match when 'incsearch' is active
|c_<BS>|	<BS>		delete the character in front of the cursor
|c_digraph|	{char1} <BS> {char2} enter digraph when 'digraph' is on
|c_CTRL-H|	CTRL-H		same as <BS>
|c_<Tab>|	<Tab>		if 'wildchar' is <Tab>: Do completion on the pattern in front of the cursor
|c_<S-Tab>|	<S-Tab>		same as CTRL-P
|c_wildchar|	'wildchar'	Do completion on the pattern in front of the cursor (default: <Tab>)
|c_CTRL-I|	CTRL-I		same as <Tab>
|c_<NL>|	<NL>		same as <CR>
|c_CTRL-J|	CTRL-J		same as <CR>
|c_CTRL-K|	CTRL-K {char1} {char2} enter digraph
|c_CTRL-L|	CTRL-L		do completion on the pattern in front of the cursor and insert the longest common part
|c_<CR>|	<CR>		execute entered command
|c_CTRL-M|	CTRL-M		same as <CR>
|c_CTRL-N|	CTRL-N		after using 'wildchar' with multiple matches: go to next match, otherwise: recall older command-line from history.
		CTRL-O		not used
|c_CTRL-P|	CTRL-P		after using 'wildchar' with multiple matches: go to previous match, otherwise: recall older command-line from history.
|c_CTRL-Q|	CTRL-Q		same as CTRL-V, unless it's used for terminal control flow
|c_CTRL-R|	CTRL-R {regname} insert the contents of a register or object under the cursor as if typed
|c_CTRL-R_CTRL-R| CTRL-R CTRL-R {regname}
|c_CTRL-R_CTRL-O| CTRL-R CTRL-O {regname} insert the contents of a register or object under the cursor literally
		CTRL-S		not used, or used for terminal control flow
|c_CTRL-T|	CTRL-T		previous match when 'incsearch' is active
|c_CTRL-U|	CTRL-U		remove all characters
|c_CTRL-V|	CTRL-V		insert next non-digit literally, insert three digit decimal number as a single byte.
|c_CTRL-W|	CTRL-W		delete the word in front of the cursor
		CTRL-X		not used (reserved for completion)
		CTRL-Y		copy (yank) modeless selection
		CTRL-Z		not used (reserved for suspend)
|c_<Esc>|	<Esc>		abandon command-line without executing it
|c_CTRL-[|	CTRL-[		same as <Esc>
|c_CTRL-\_CTRL-N| CTRL-\ CTRL-N	go to Normal mode, abandon command-line
|c_CTRL-\_CTRL-G| CTRL-\ CTRL-G	go to Normal mode, abandon command-line
		CTRL-\ a - d	reserved for extensions
|c_CTRL-\_e|	CTRL-\ e {expr} replace the command line with the result of {expr}
		CTRL-\ f - z	reserved for extensions
		CTRL-\ others	not used
|c_CTRL-]|	CTRL-]		trigger abbreviation
|c_CTRL-^|	CTRL-^		toggle use of |:lmap| mappings
|c_CTRL-_|	CTRL-_		when 'allowrevins' set: change language (Hebrew)
|c_<Del>|	<Del>		delete the character under the cursor

|c_<Left>|	<Left>		cursor left
|c_<S-Left>|	<S-Left>	cursor one word left
|c_<C-Left>|	<C-Left>	cursor one word left
|c_<Right>|	<Right>		cursor right
|c_<S-Right>|	<S-Right>	cursor one word right
|c_<C-Right>|	<C-Right>	cursor one word right
|c_<Up>|	<Up>		recall previous command-line from history that matches pattern in front of the cursor
|c_<S-Up>|	<S-Up>		recall previous command-line from history
|c_<Down>|	<Down>		recall next command-line from history that matches pattern in front of the cursor
|c_<S-Down>|	<S-Down>	recall next command-line from history
|c_<Home>|	<Home>		cursor to start of command-line
|c_<End>|	<End>		cursor to end of command-line
|c_<PageDown>|	<PageDown>	same as <S-Down>
|c_<PageUp>|	<PageUp>	same as <S-Up>
|c_<Insert>|	<Insert>	toggle insert/overstrike mode
|c_<LeftMouse>|	<LeftMouse>	cursor at mouse click

## Terminal Mode

In a |terminal| buffer all keys except CTRL-\ are forwarded to the terminal job.  If CTRL-\ is pressed, the next key is forwarded unless it is CTRL-N or CTRL-O.
Use |CTRL-\_CTRL-N| to go to Normal mode.
Use |t_CTRL-\_CTRL-O| to execute one normal mode command and then return to terminal mode.