let keys = {
  normal: {
    'a': { form: 'a', name: 'Append after', description: 'Append text after the cursor N times.' },
    'b': { form: 'b', name: 'Back word', description: 'Cursor N words backward.', categories: ['motion'] },
    'c': { form: '["x]c{motion}', name: 'Change', description: 'Delete Nmove text [into register x] and start insert.' },
    'cc': { form: '["x]cc', name: 'Change line', description: 'Delete N lines [into register x] and start insert.' },
    'd': { form: '["x]d{motion}', name: 'Delete', description: 'Delete Nmove text [into register x].' },
    'dd': { form: '["x]dd', name: 'Delete line', description: 'Delete N lines [into register x].' },
    'do': { form: 'do', name: 'Diff get', description: 'Modify the current buffer to undo difference with another buffer.', synomyms: [':diffget'] },
    'dp': { form: 'dp', name: 'Diff put', description: 'Modify another buffer to undo difference with the current buffer.', synonyms: [':diffput'] },
    'e': { form: 'e', name: 'End word', description: 'Cursor forward to the end of word N.', categories: ['motion'] },
    'f': { form: 'f{char}', name: 'Find char', description: 'Cursor to Nth occurrence of {char} to the right.', categories: ['motion'] },
    'ga': { form: 'ga', name: 'Char value under cursor', description: 'Print ascii value of character under the cursor.' },
    'gd': { form: 'gd', name: 'Go to definition', description: 'Go to definition of word under the cursor in current function.' },
    'ge': { form: 'ge', name: 'Go previous end word', description: 'Go backwards to the end of the previous word.' },
    'gf': { form: 'gf', name: 'Go to file', description: 'Start editing the file whose name is under the cursor.' },
    'gg': { form: 'gg', name: 'Go to line', description: 'Cursor to line N, default first line.' },
    'gh': { form: 'gh', name: 'Select mode', description: 'Start Select mode (uncommon mode to select with arrows and overtype).' },
    'gi': { form: 'gi', name: '', description: 'like "i", but first move to the `\'^` mark.' },
    '': { form: '', name: '', description: '' },
    '': { form: '', name: '', description: '' },
    '': { form: '', name: '', description: '' },
    '': { form: '', name: '', description: '' },
    '': { form: '', name: '', description: '' },
    /*
|gi|		gi		2  
|gH|		gH		   start Select line mode
|g#|		g#		1  like "#", but without using "\<" and "\>"
|g$|		g$		1  when 'wrap' off go to rightmost character of the current line that is on the screen; when 'wrap' on go to the rightmost character of the current screen line
|g&|		g&		2  repeat last ":s" on all lines
|g'|		g'{mark}	1  like |'| but without changing the jumplist
|g`|		g`{mark}	1  like |`| but without changing the jumplist
|gstar|		g*		1  like "*", but without using "\<" and "\>"
|g+|		g+		   go to newer text state N times
|g,|		g,		1  go to N newer position in change list
|g-|		g-		   go to older text state N times
|g0|		g0		1  when 'wrap' off go to leftmost character of the current line that is on the screen; when 'wrap' on go to the leftmost character of the current screen line
|g8|		g8		   print hex value of bytes used in UTF-8 character under the cursor
|g;|		g;		1  go to N older position in change list
|g<|		g<		   display previous command output
|g?|		g?		2  Rot13 encoding operator
|g?g?|		g??		2  Rot13 encode current line
|g?g?|		g?g?		2  Rot13 encode current line
|gD|		gD		1  go to definition of word under the cursor in current file
|gE|		gE		1  go backwards to the end of the previous WORD
|gI|		gI		2  like "I", but always start in column 1
|gJ|		gJ		2  join lines without inserting space
|gN|		gN	      1,2  find the previous match with the last used search pattern and Visually select it
|gP|		["x]gP		2  put the text [from register x] before the cursor N times, leave the cursor after it
|gQ|		gQ		    switch to "Ex" mode with Vim editing
|gR|		gR		2  enter Virtual Replace mode
|gT|		gT		   go to the previous tab page
|gU|		gU{motion}	2  make Nmove text uppercase
|gV|		gV		   don't reselect the previous Visual area when executing a mapping or menu in Select mode
|g]|		g]		   :tselect on the tag under the cursor
|g^|		g^		1  when 'wrap' off go to leftmost non-white character of the current line that is on the screen; when 'wrap' on go to the leftmost non-white character of the current screen line
|g_|		g_		1  cursor to the last CHAR N - 1 lines lower
|gF|		gF		   start editing the file whose name is under the cursor and jump to the line number following the filename.
|gj|		gj		1  like "j", but when 'wrap' on go N screen lines down
|gk|		gk		1  like "k", but when 'wrap' on go N screen lines up
|gm|		gm		1  go to character at middle of the screenline
|gM|		gM		1  go to character at middle of the text line
|gn|		gn	      1,2  find the next match with the last used search pattern and Visually select it
|go|		go		1  cursor to byte N in the buffer
|gp|		["x]gp		2  put the text [from register x] after the cursor N times, leave the cursor after it
|gq|		gq{motion}	2  format Nmove text
|gr|		gr{char}	2  virtual replace N chars with {char}
|gs|		gs		   go to sleep for N seconds (default 1)
|gt|		gt		   go to the next tab page
|gu|		gu{motion}	2  make Nmove text lowercase
|gv|		gv		   reselect the previous Visual area
|gw|		gw{motion}	2  format Nmove text and keep cursor
|netrw-gx|	gx		   execute application for file name under the cursor (only with |netrw| plugin)
|g@|		g@{motion}	   call 'operatorfunc'
|g~|		g~{motion}	2  swap case for Nmove text
    */
    'h': { form: 'h', name: 'Left', description: 'Cursor N chars to the left.', categories: ['motion'] },
    'i': { form: 'i', name: 'Insert', description: 'Insert text before the cursor N times.' },
    'j': { form: 'j', name: 'Down', description: 'Cursor N lines downward.', categories: ['motion'] },
    'k': { form: 'k', name: 'Up', description: 'Cursor N lines upward.', categories: ['motion'] },
    'l': { form: 'l', name: 'Right', description: 'Cursor N chars to the right.', categories: ['motion'] },
    'm': { form: 'm{A-Za-z}', name: 'Mark', description: 'Set mark {A-Za-z} at cursor position. Uppercase marks are global.' },
    'n': { form: 'n', name: 'Find next', description: 'Repeat the latest `/` or `?` N times.', categories: ['motion'] },
    'o': { form: 'o', name: 'Open line', description: 'Begin a new line below the cursor and insert text, repeat N times.' },
    'p': { form: '["x]p', name: 'Put', description: 'Put the text [from register x] after the cursor N times.' },
    'q': { form: 'q{0-9a-zA-Z"}', name: 'Start/Stop macro', description: 'Record typed characters into named register {0-9a-zA-Z"} (uppercase to append). While recording, stops recording.' },
    'q:': { form: 'q:', name: 'Edit command', description: 'Edit : command-line in command-line window.' },
    'q/': { form: 'q/', name: 'Edit search', description: 'Edit / command-line in command-line window.' },
    'q?': { form: 'q?', name: 'Edit search reverse', description: 'Edit ? command-line in command-line window.' },
    'r': { form: 'r{char}', name: 'Replace char', description: 'Replace N chars with {char}.' },
    's': { form: '["x]s', name: 'Substitute', description: 'Delete N characters [into register x] and start insert.' },
    't': { form: 't{char}', name: 'Find to char', description: 'Cursor till before Nth occurrence of {char} to the right.', categories: ['motion'] },
    'u': { form: 'u', name: 'Undo', description: 'Undo changes.' },
    'v': { form: 'v', name: 'Visual mode', description: 'Start charwise Visual mode.' },
    'w': { form: 'w', name: 'Word', description: 'Cursor N words forward.', categories: ['motion'] },
    'x': { form: '["x]x', name: 'Delete char', description: 'Delete N characters under and after the cursor [into register x].' },
    'y': { form: '["x]y{motion}', name: 'Yank', description: 'Yank Nmove text [into register x].' },
    'yy': { form: '["x]yy', name: 'Yank line', description: 'Yank N lines [into register x].' },
    // z*
    'A': { form: 'A', name: 'Append after line', description: 'Append text after the end of the line N times.' },
    'B': { form: 'B', name: 'Back WORD', description: 'Cursor N WORDS backward.', categories: ['motion'] },
    'C': { form: '["x]C', name: 'Change line', description: 'Change from the cursor position to the end of the line, and N-1 more lines [into register x]', synonyms: ['c$'] },
    'D': { form: '["x]D', name: 'Delete line', description: 'Delete the characters under the cursor until the end of the line and N-1 more lines [into register x]', synonyms: ['d$'] },
    'E': { form: 'E', name: 'End WORD', description: 'Cursor forward to the end of WORD N.', categories: ['motion'] },
    'F': { form: 'F{char}', name: 'Find char reverse', description: 'Cursor to the Nth occurrence of {char} to the left.', categories: ['motion'] },
    'G': { form: 'G', name: 'Go to line', description: 'Cursor to line N, default last line.', categories: ['motion'] },
    'H': { form: 'H', name: 'Highest line', description: 'Cursor to line N from top of screen.', categories: ['motion'] },
    'I': { form: 'I', name: 'Insert before line', description: 'Insert text before the first CHAR on the line N times.' },
    'J': { form: 'J', name: 'Join line', description: 'Join N lines; default is 2.' },
    'K': { form: 'K', name: 'Lookup keyword', description: 'lookup Keyword under the cursor with `keywordprg`.' },
    'L': { form: 'L', name: 'Lowest line', description: 'Cursor to line N from bottom of screen.', categories: ['motion'] },
    'M': { form: 'M', name: 'Middle line', description: 'Cursor to middle line of screen.', categories: ['motion'] },
    'N': { form: 'N', name: 'Find next reverse', description: 'repeat the latest `/` or `?` N times in opposite direction.', categories: ['motion'] },
    'O': { form: 'O', name: 'Open line above', description: 'Begin a new line above the cursor and insert text, repeat N times.' },
    'P': { form: '["x]P', name: 'Put', description: 'Put the text [from register x] before the cursor N times.' },
    'Q': { form: 'Q', name: 'Repeat last macro', description: 'Repeat the last recorded register [count] times.' },
    'R': { form: 'R', name: 'Replay overtype', description: 'Enter replace mode: overtype existing characters, repeat the entered text N-1 times.' },
    'S': { form: '["x]S', name: 'Substitute line', description: 'Delete N lines [into register x] and start insert', synonyms: ['cc'] },
    'T': { form: 'T{char}', name: 'Find to char reverse', description: 'Cursor till after Nth occurrence of {char} to the left.', categories: ['motion'] },
    'U': { form: 'U', name: 'Undo line', description: 'Undo all latest changes on one line.' },
    'V': { form: 'V', name: 'Visual line mode', description: 'Start linewise Visual mode.' },
    'W': { form: 'W', name: 'WORD', description: 'Cursor N WORDS forward.', categories: ['motion'] },
    'X': { form: '["x]X', name: 'Delete char', description: 'Delete N characters before the cursor [into register x].' },
    'Y': { form: '["x]Y', name: 'Yank line', description: 'Yank N lines [into register x]; synonym for "yy" Note: Mapped to "y$" by default. |default-mappings|.' },
    'ZZ': { form: 'ZZ', name: 'Write and close', description: 'Write if buffer changed and close window.' },
    'ZQ': { form: 'ZQ', name: 'Clise without writing', description: 'Close window without writing.' },
    '!': { form: '!{motion}{filter}', name: 'Filter', description: 'Filter Nmove text through the {filter} command.' },
    '!!': { form: '!!{filter}', name: 'Filter line', description: 'Filter N lines through the {filter} command.' },
    '"': { form: '"{register}', name: 'Register', description: 'Use {register} for next delete, yank or put ({.%#:} only work with put).' },
    '#': { form: '#', name: 'Find under cursor reverse', description: 'Search backward for the Nth occurrence of the ident under the cursor.', categories: ['motion'] },
    '$': { form: '$', name: 'End of line', description: 'Cursor to the end of Nth next line.', categories: ['motion'] },
    '%': { form: '%', name: 'Find matching', description: 'Find the next (curly/square) bracket on this line and go to its match, or go to matching comment bracket, or go to matching preprocessor directive. Or, with count, go to N percentage in the file.', categories: ['motion'] },
    '&': { form: '&', name: 'Repeat search', description: 'Repeat last `:s`.' },
    "'": { form: "'{a-zA-Z0-9}", name: 'Go to marked line', description: 'Cursor to the first CHAR on the line with mark {a-zA-Z0-9}.', categories: ['motion'] },
    "''": { form: "''", name: 'Previous jump line', description: 'Cursor to the first CHAR of the line where the cursor was before the latest jump.', categories: ['motion'] },
    "'(": { form: "'(", name: 'Start of sentence line', description: 'Cursor to the first CHAR on the line of the start of the current sentence.', categories: ['motion'] },
    "')": { form: "')", name: 'End of sentence line', description: 'Cursor to the first CHAR on the line of the end of the current sentence.', categories: ['motion'] },
    "'<": { form: "'<", name: 'Start of selection line', description: 'Cursor to the first CHAR of the line where highlighted area starts/started in the current buffer.', categories: ['motion'] },
    "'>": { form: "'>", name: 'End of selection line', description: 'Cursor to the first CHAR of the line where highlighted area ends/ended in the current buffer.', categories: ['motion'] },
    "'[": { form: "'[", name: 'Start of last text', description: 'Cursor to the first CHAR on the line of the start of last operated text or start of put text.', categories: ['motion'] },
    "']": { form: "']", name: 'End of last text', description: 'Cursor to the first CHAR on the line of the end of last operated text or end of put text.', categories: ['motion'] },
    "'{": { form: "'{", name: 'Start of paragraph line', description: 'Cursor to the first CHAR on the line of the start of the current paragraph.', categories: ['motion'] },
    "'}": { form: "'}", name: 'End of paragraph line', description: 'Cursor to the first CHAR on the line of the end of the current paragraph.', categories: ['motion'] },
    '(': { form: '(', name: 'Back sentence', description: 'Cursor N sentences backward.', categories: ['motion'] },
    ')': { form: ')', name: 'Sentence', description: 'Cursor N sentences forward.', categories: ['motion'] },
    '*': { form: '*', name: 'Find under cursor', description: 'Search forward for the Nth occurrence of the ident under the cursor.', categories: ['motion'] },
    '+': { form: '+', name: 'Start of lower line', description: 'Cursor to the first CHAR N lines lower.', synonyms: ['<CR>'], categories: ['motion'] },
    ',': { form: ',', name: 'Find previous', description: 'Repeat latest f, t, F or T in opposite direction N times.', categories: ['motion'] },
    '-': { form: '-', name: 'Start of higher line', description: 'Cursor to the first CHAR N lines higher.', categories: ['motion'] },
    '.': { form: '.', name: 'Repeat action', description: 'Repeat last change with count replaced with N.' },
    '/': { form: '/{pattern}<CR>', name: 'Search', description: 'Search forward for the Nth occurrence of {pattern}. Or repeat last search with `/<CR>`.', categories: ['motion'] },
    '0': { form: '0', name: 'First column', description: 'Cursor to the first char of the line.' },
    '1': { form: '1', name: 'Count', description: 'Prepend to command to give a count.' },
    '2': { form: '2', name: 'Count', description: 'Prepend to command to give a count.' },
    '3': { form: '3', name: 'Count', description: 'Prepend to command to give a count.' },
    '4': { form: '4', name: 'Count', description: 'Prepend to command to give a count.' },
    '5': { form: '5', name: 'Count', description: 'Prepend to command to give a count.' },
    '6': { form: '6', name: 'Count', description: 'Prepend to command to give a count.' },
    '7': { form: '7', name: 'Count', description: 'Prepend to command to give a count.' },
    '8': { form: '8', name: 'Count', description: 'Prepend to command to give a count.' },
    '9': { form: '9', name: 'Count', description: 'Prepend to command to give a count.' },
    ':': { form: ':', name: 'Ex command mode', description: 'Start entering an Ex command. Given count (`N:`), with range from current line to N-1 lines down.' },
    ';': { form: ';', name: 'Find next', description: 'Repeat latest f, t, F or T N times.', categories: ['motion'] },
    '<': { form: '<{motion}', name: 'Unindent', description: 'Shift Nmove lines one `shiftwidth` leftwards.' },
    '<<': { form: '<<', name: 'Unindent line', description: 'Shift N lines one `shiftwidth` leftwards.' },
    '=': { form: '={motion}', name: 'Autoindent', description: 'Filter Nmove lines through `indent`.' },
    '==': { form: '==', name: 'Autoindent line', description: 'Filter N lines through `indent`.' },
    '>': { form: '>{motion}', name: 'Indent', description: 'Shift Nmove lines one `shiftwidth` rightwards.' },
    '>>': { form: '>>', name: 'Indent line', description: 'Shift N lines one `shiftwidth` rightwards.' },
    '?': { form: '?{pattern}<CR>', name: 'Search reverse', description: 'Search backward for the Nth occurrence of {pattern}. Or repeat last search with `?<CR>`.', categories: ['motion'] },
    '@': { form: '@{a-z}', name: 'Execute macro', description: 'Execute the contents of register {a-z} N times.' },
    '@:': { form: '@:', name: 'Repeat command', description: 'Repeat the previous `:` command N times.' },
    '@@': { form: '@@', name: 'Repeat macro', description: 'Repeat the previous @{a-z} N times.' },
    // [
    '\\': { form: '\\', name: 'Leader', description: 'Not used. Reserved for user mappings.' },
    // ]
    '^': { form: '^', name: 'Start of line', description: 'Cursor to the first CHAR of the line.', categories: ['motion'] },
    '_': { form: '_', name: 'Start of line', description: 'Cursor to the first CHAR N - 1 lines lower.', categories: ['motion'] },
    '`': { form: '`{a-zA-Z0-9}', name: 'Go to marked char', description: 'Cursor to the mark {a-zA-Z0-9}.', categories: ['motion'] },
    '`(': { form: '`(', name: 'Start of sentence', description: 'Cursor to the start of the current sentence.', categories: ['motion'] },
    '`)': { form: '`)', name: 'End of sentence', description: 'Cursor to the end of the current sentence.', categories: ['motion'] },
    '`<': { form: '`<', name: 'Start of selection', description: 'Cursor to the start of the highlighted area.', categories: ['motion'] },
    '`>': { form: '`>', name: 'End of selection', description: 'Cursor to the end of the highlighted area.', categories: ['motion'] },
    '`[': { form: '`[', name: 'Start of text', description: 'Cursor to the start of last operated text or start of putted text.', categories: ['motion'] },
    '`]': { form: '`]', name: 'End of text', description: 'Cursor to the end of last operated text or end of putted text.', categories: ['motion'] },
    '``': { form: '``', name: 'Previous jump', description: 'Cursor to the position before latest jump.', categories: ['motion'] },
    '`{': { form: '`{', name: 'Start of paragraph', description: 'Cursor to the start of the current paragraph.', categories: ['motion'] },
    '`}': { form: '`}', name: 'End of paragraph', description: 'Cursor to the end of the current paragraph.', categories: ['motion'] },
    '{': { form: '{', name: 'Back paragraph', description: 'Cursor N paragraphs backward.', categories: ['motion'] },
    '|': { form: '|', name: 'Go to column', description: 'Cursor to column N.', categories: ['motion'] },
    '}': { form: '}', name: 'Paragraph', description: 'Cursor N paragraphs forward.', categories: ['motion'] },
    '~': { form: '~', name: 'Toggle case', description: 'Switch case of N characters under cursor and move the cursor N characters to the right (`tildeop` may allow taking motion, but so does `g~`).' },
    '<Space>': { form: '<Space>', name: 'Right', description: 'Cursor N chars to the right.', synonyms: ['l'], categories: ['motion'] },
    '<BS>': { form: '<BS>', name: 'Left', description: 'Cursor N chars to the left.', synonyms: ['h'], categories: ['motion'] },
    '<CR>': { form: '<CR>', name: 'Start of following line', description: 'Cursor to the first CHAR N lines lower.', synonyms: ['+'], categories: ['motion'] },
    '<Tab>': { form: '<Tab>', name: 'Previous jump', description: 'Go to N newer entry in jump list.' },
    '': { form: '', name: '', description: '' },
/*
*/
  }
}