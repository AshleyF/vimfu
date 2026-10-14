# Visual Mode						*visual-index*

Most commands in Visual mode are the same as in Normal mode.  The ones listed
here are those that are different.

tag		command	      note action in Visual mode	~
------------------------------------------------------------------------------ ~
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
|v_P|		P		   replace highlighted area with register contents; registers are unchanged
		Q		   does not start Ex mode
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
|v_g_CTRL-A|	g CTRL-A	2  add N to number in highlighted text (ordinal lines)
|v_g_CTRL-X|	g CTRL-X	2  subtract N from number in highlighted text (ordinal lines)
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