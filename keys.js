let keys = {
  normal: {
    'a': { form: 'a', name: 'Append after', description: 'Append text after the cursor N times.', count: true },
    'b': { form: 'b', name: 'Back word', description: 'Cursor N words backward.', categories: ['motion'], count: true },
    'c': { form: '["x]c{motion}', name: 'Change', description: 'Delete Nmove text [into register x] and start insert.', count: true },
    'cc': { form: '["x]cc', name: 'Change line', description: 'Delete N lines [into register x] and start insert.', count: true },
    'd': { form: '["x]d{motion}', name: 'Delete', description: 'Delete Nmove text [into register x].', count: true },
    'dd': { form: '["x]dd', name: 'Delete line', description: 'Delete N lines [into register x].', count: true },
    'do': { form: 'do', name: 'Diff get', description: 'Modify the current buffer to undo difference with another buffer. Same as `:diffget`.' },
    'dp': { form: 'dp', name: 'Diff put', description: 'Modify another buffer to undo difference with the current buffer. Same as `:diffput`.' },
    'e': { form: 'e', name: 'End word', description: 'Cursor forward to the end of word N.', categories: ['motion'], count: true },
    'f': { form: 'f{char}', name: 'Find char', description: 'Cursor to Nth occurrence of {char} to the right.', categories: ['motion'], count: true },
    'ga': { form: 'ga', name: 'Char value under cursor', description: 'Print ascii value of character under the cursor.' },
    // gb gc
    'gd': { form: 'gd', name: 'Go to definition', description: 'Go to definition of word under the cursor in current function.', categories: ['motion'] },
    'ge': { form: 'ge', name: 'Go previous end word', description: 'Go backwards to the end of the previous word.', categories: ['motion'], count: true },
    'gf': { form: 'gf', name: 'Go to file', description: 'Start editing the file whose name is under the cursor.' },
    'gg': { form: 'gg', name: 'Go to line/beginning', description: 'Cursor to line N, default first line.', count: true },
    'gh': { form: 'gh', name: 'Select mode', description: 'Start Select mode (uncommon mode to select with arrows and overtype).' },
    'gi': { form: 'gi', name: 'Insert mode at previous', description: 'Like `i`, but first move to the `\'^` mark.' },
    'gj': { form: 'gj', name: 'Down screen line', description: 'Like `j`, but when `wrap` on go N screen lines down.', categories: ['motion'] },
    'gk': { form: 'gk', name: 'Up screen line', description: 'Like `k`, but when `wrap` on go N screen lines up.', categories: ['motion'] },
    // gl
    'gm': { form: 'gm', name: 'Middle screenline', description: 'Go to character at middle of the screenline.', categories: ['motion'] },
    'gn': { form: 'gn', name: 'Find next and select', description: 'Find the next match with the last used search pattern and Visually select to it.', categories: ['motion'] },
    'go': { form: 'go', name: 'Byte N', description: 'Cursor to byte N in the buffer.', categories: ['motion'] },
    'gp': { form: '["x]gp', name: 'Put and move after', description: 'Put the text [from register x] after the cursor N times, leave the cursor after it.' },
    'gq': { form: 'gq{motion}', name: 'Format', description: 'Format Nmove text.' },
    'gr': { form: 'gr{char}', name: 'Virtual replace', description: 'Virtual replace N chars with {char}.' },
    'gs': { form: 'gs', name: 'Sleep', description: 'Go to sleep for N seconds (default 1).' },
    'gt': { form: 'gt', name: 'Next tab', description: 'Go to the next tab page.' },
    'gu': { form: 'gu{motion}', name: 'Lowercase', description: 'Make Nmove text lowercase.' },
    'gv': { form: 'gv', name: 'Reselect visual', description: 'Reselect the previous Visual area.' },
    'gw': { form: 'gw{motion}', name: 'Format and keep cursor', description: 'Format Nmove text and keep cursor.' },
    'gx': { form: 'gx', name: 'Execute file', description: 'Execute application for file name under the cursor (only with |netrw| plugin).' },
    // gy gz gA gB gC
    'gD': { form: 'gD', name: 'Go to definition within file', description: 'Go to definition of word under the cursor in current file.' },
    'gE': { form: 'gE', name: 'Go previous end WORD', description: 'Go backwards to the end of the previous WORD.', categories: ['motion'] },
    'gF': { form: 'gF', name: 'Go to file and jump to line', description: 'Start editing the file whose name is under the cursor and jump to the line number following the filename.' },
    // gG
    'gH': { form: 'gH', name: 'Select line mode', description: 'Start Select line mode.' },
    'gI': { form: 'gI', name: 'Insert at first column', description: 'Like `I`, but always start in column 1.' },
    'gJ': { form: 'gJ', name: 'Join line without space', description: 'Join lines without inserting space.' },
    // gK gL
    'gM': { form: 'gM', name: 'Middle text line', description: 'Go to character at middle of the text line.', categories: ['motion'] },
    'gN': { form: 'gN', name: 'Find next reverse and select', description: 'Find the previous match with the last used search pattern and Visually select to it.', categories: ['motion'] },
    // gO
    'gP': { form: '["x]gP', name: 'Put before and move after', description: 'Put the text [from register x] before the cursor N times, leave the cursor after it.' },
    'gQ': { form: 'gQ', name: 'Ex mode with Vim editing', description: 'Switch to `Ex` mode with Vim editing.' },
    'gR': { form: 'gR', name: 'Visual Replace mode', description: 'Enter Virtual Replace mode (uncommon mode to navigate with arrows while overtyping).' },
    // gS
    'gT': { form: 'gT', name: 'Previous tab', description: 'Go to the previous tab page.' },
    'gU': { form: 'gU{motion}', name: 'Uppercase', description: 'Make Nmove text uppercase.' },
    'gV': { form: 'gV', name: "Don't reselect visual", description: "Don't reselect the previous Visual area when executing a mapping or menu in Select mode." },
    // gW gX gY gZ
    'g*': { form: 'g*', name: 'Find under cursor (partial)', description: 'Like `*`, but without including partial word matches.', categories: ['motion'] },
    'g#': { form: 'g#', name: 'Find under cursor reverse (partial)', description: 'Like `#`, but without including partial word matches.', categories: ['motion'] },
    'g$': { form: 'g$', name: 'End of screen line', description: 'When `wrap` off go to rightmost character of the current line that is on the screen; when `wrap` on go to the rightmost character of the current screen line.', categories: ['motion'] },
    'g&': { form: 'g&', name: 'Repeat search on all lines', description: 'Repeat last `:s` on all lines.' },
    "g'": { form: "g'{a-zA-Z0-9}", name: 'Go to marked line without changing jumplist', description: "like `'` but without changing the jumplist.", categories: ['motion'] },
    "g`": { form: "g`{a-zA-Z0-9}", name: 'Go to marked character without changing jumplist', description: "like ` but without changing the jumplist.", categories: ['motion'] },
    'g+': { form: 'g+', name: 'Newer text state', description: 'Go to newer text state N times.', categories: ['motion'] },
    'g-': { form: 'g-', name: 'Older text state', description: 'Go to older text state N times.', categories: ['motion'] },
    'g,': { form: 'g,', name: 'Newer change', description: 'Go to N newer position in change list.', categories: ['motion'] },
    'g;': { form: 'g;', name: 'Older change', description: 'Go to N older position in change list.' },
    'g0': { form: 'g0', name: 'Leftmost screen character', description: 'When `wrap` off go to leftmost character of the current line that is on the screen; when `wrap` on go to the leftmost character of the current screen line.', categories: ['motion'] },
    'g8': { form: 'g8', name: 'Hex value', description: 'Print hex value of bytes used in UTF-8 character under the cursor.' },
    'g<': { form: 'g<', name: 'Previous output', description: 'Display previous command output.' },
    'g?': { form: 'g?', name: 'Rot13', description: 'Rot13 encoding operator.' },
    'g??': { form: 'g??', name: 'Rot13 line', description: 'Rot13 encode current line. (`g?g?` also works).' },
    'g]': { form: 'g]', name: 'Select tag', description: '`:tselect` on the tag under the cursor.' },
    'g^': { form: 'g^', name: 'Leftmost non-white screen character', description: 'When `wrap` off go to leftmost non-white character of the current line that is on the screen; when `wrap` on go to the leftmost non-white character of the current screen line.', categories: ['motion'] },
    'g_': { form: 'g_', name: 'End of line', description: 'Cursor to the last CHAR N - 1 lines lower.' },
    'g@': { form: 'g@{motion}', name: 'Call operatorfunc', description: 'Call `operatorfunc`.' },
    'g~': { form: 'g~{motion}', name: 'Toggle case', description: 'Swap case for Nmove text.' },
    'g<Tab>': { form: 'g<Tab>', name: 'Go to tab', description: 'Go to last accessed tab page.' },
    'g<Down>': { form: 'g<Down>', name: 'Down screen line', description: 'Like `j`, but when `wrap` on go N screen lines down.', categories: ['motion'] },
    'g<Up>': { form: 'g<Up>', name: 'Up screen line', description: 'Like `k`, but when `wrap` on go N screen lines up.', categories: ['motion'] },
    'g<End>': { form: 'g<End>', name: 'End of screen line', description: 'When `wrap` off go to rightmost character of the current line that is on the screen; when `wrap` on go to the rightmost character of the current screen line.', categories: ['motion'] },
    'g<Home>': { form: 'g<Home>', name: 'Leftmost screen character', description: 'When `wrap` off go to leftmost character of the current line that is on the screen; when `wrap` on go to the leftmost character of the current screen line.', categories: ['motion'] },
    'g<LeftMouse>': { form: 'g<LeftMouse>', name: 'Tag definition', description: '`:ta` to ident at the mouse click.' },
    'g<MiddleMouse>': { form: 'g<MiddleMouse>', name: 'Put', description: 'Put at mouse position.' },
    'g<RightMouse>': { form: 'g<RightMouse>', name: 'Tag', description: 'Jump to N older Tag in tag list.' },
    'g^a': { form: 'g^a', name: 'Increment ordinal', description: 'Increment numbers as ordinals.' },
    'g^g': { form: 'g^g', name: 'Show info', description: 'Show information about current cursor position.' },
    'g^h': { form: 'g^h', name: 'Select block mode', description: 'Start Select block mode.' },
    'g^j': { form: 'g^j', name: 'Jump tag', description: '`:tjump` to the tag under the cursor.' },
    'h': { form: 'h', name: 'Left', description: 'Cursor N chars to the left.', categories: ['motion'], count: true },
    'i': { form: 'i', name: 'Insert', description: 'Insert text before the cursor N times.', count: true },
    'j': { form: 'j', name: 'Down', description: 'Cursor N lines downward.', categories: ['motion'], count: true },
    'k': { form: 'k', name: 'Up', description: 'Cursor N lines upward.', categories: ['motion'], count: true },
    'l': { form: 'l', name: 'Right', description: 'Cursor N chars to the right.', categories: ['motion'], count: true },
    'm': { form: 'm{A-Za-z}', name: 'Mark', description: 'Set mark {A-Za-z} at cursor position. Uppercase marks are global.', count: true },
    'n': { form: 'n', name: 'Find next', description: 'Repeat the latest `/` or `?` N times.', categories: ['motion'], count: true },
    'o': { form: 'o', name: 'Open line', description: 'Begin a new line below the cursor and insert text, repeat N times.', count: true },
    'p': { form: '["x]p', name: 'Put', description: 'Put the text [from register x] after the cursor N times.', count: true },
    'q': { form: 'q{0-9a-zA-Z"}', name: 'Start/Stop macro', description: 'Record typed characters into named register {0-9a-zA-Z"} (uppercase to append). While recording, stops recording.' },
    'q:': { form: 'q:', name: 'Edit command', description: 'Edit : command-line in command-line window.' },
    'q/': { form: 'q/', name: 'Edit search', description: 'Edit / command-line in command-line window.' },
    'q?': { form: 'q?', name: 'Edit search reverse', description: 'Edit ? command-line in command-line window.' },
    'r': { form: 'r{char}', name: 'Replace char', description: 'Replace N chars with {char}.', count: true },
    's': { form: '["x]s', name: 'Substitute', description: 'Delete N characters [into register x] and start insert.', count: true },
    't': { form: 't{char}', name: 'Find to char', description: 'Cursor till before Nth occurrence of {char} to the right.', categories: ['motion'], count: true },
    'u': { form: 'u', name: 'Undo', description: 'Undo changes.', count: true },
    'v': { form: 'v', name: 'Visual mode', description: 'Start charwise Visual mode.' },
    'w': { form: 'w', name: 'Word', description: 'Cursor N words forward.', categories: ['motion'], count: true },
    'x': { form: '["x]x', name: 'Delete char', description: 'Delete N characters under and after the cursor [into register x].', count: true },
    'y': { form: '["x]y{motion}', name: 'Yank', description: 'Yank Nmove text [into register x].', count: true },
    'yy': { form: '["x]yy', name: 'Yank line', description: 'Yank N lines [into register x].', count: true },
    'za': { form: 'za', name: 'Toggle fold', description: 'Open a closed fold, close an open fold.' },
    'zb': { form: 'zb', name: 'Scroll bottom', description: 'Redraw, cursor line at bottom of window.' },
    'zc': { form: 'zc', name: 'Close fold', description: 'Close a fold.' },
    'zd': { form: 'zd', name: 'Delete fold', description: 'Delete a fold.' },
    'ze': { form: 'ze', name: 'Scroll end of line', description: 'When `wrap` off scroll horizontally to position the cursor at the end (right side) of the screen.' },
    'zf': { form: 'zf{motion}', name: 'Create fold', description: 'Create a fold for Nmove text.' },
    '': { form: '', name: '', description: '' },
    'z+': { form: 'z+', name: 'Scroll top', description: 'Redraw, cursor line (N if given) to top of window, cursor on first non-blank.' },
    'z-': { form: 'z-', name: 'Scroll bottom', description: 'Redraw, cursor line at bottom of window, cursor on first non-blank.' },
    'z.': { form: 'z.', name: 'Scroll middle', description: 'Redraw, cursor line to center of window, cursor on first non-blank.' },
    'z=': { form: 'z=', name: 'Spelling', description: 'Give spelling suggestions.' },
    'zg': { form: 'zg', name: 'Mark correct', description: 'Permanently mark word as correctly spelled.' },
    'zug': { form: 'zug', name: 'Undo mark correct', description: 'Undo `zg`.' },
    'zh': { form: 'zh', name: 'Scroll right', description: 'When `wrap` off scroll screen N characters to the right.' },
    'zi': { form: 'zi', name: 'Toggle folding', description: 'Toggle `foldenable`.' },
    'zj': { form: 'zj', name: 'Next fold', description: 'Move to the start of the next fold.', categories: ['motion'] },
    'zk': { form: 'zk', name: 'Previous fold', description: 'Move to the end of the previous fold.', categories: ['motion'] },
    'zl': { form: 'zl', name: 'Scroll left', description: 'When `wrap` off scroll screen N characters to the left.' },
    'zm': { form: 'zm', name: 'Decrement fold level', description: 'Subtract one from `foldlevel`.' },
    'zn': { form: 'zn', name: 'Reset folding', description: 'Reset `foldenable`.' },
    'zo': { form: 'zo', name: 'Open fold', description: 'Open fold.' },
    'zp': { form: 'zp', name: 'Put block-mode without space', description: 'Put in block-mode without trailing spaces.' },
    // zq
    'zr': { form: 'zr', name: 'Add fold level', description: 'Add one to `foldlevel`.' },
    'zs': { form: 'zs', name: 'Scroll to start of line', description: 'When `wrap` off scroll horizontally to position the cursor at the start (left side) of the screen.' },
    'zt': { form: 'zt', name: 'Scroll top', description: 'Redraw, cursor line at top of window.' },
    // zu* elsewhere
    'zv': { form: 'zv', name: 'Open folds to cursor', description: 'Open enough folds to view the cursor line.' },
    'zw': { form: 'zw', name: 'Mark incorrect', description: 'Permanently mark word as incorrectly spelled.' },
    'zuw': { form: 'zuw', name: 'Undo mark incorrect', description: 'Undo `zw`.' },
    'zx': { form: 'zx', name: 'Reapply fold level', description: 'Re-apply `foldlevel` and do `zv`.' },
    'zy': { form: 'zy', name: 'Yank without space', description: 'Yank without trailing spaces.' },
    'zz': { form: 'zz', name: 'Scroll center', description: 'Redraw, cursor line at center of window.' },
    'zA': { form: 'zA', name: 'Toggle folds recursive', description: 'Open a closed fold or close an open fold recursively.' },
    'zC': { form: 'zC', name: 'Close folds recursive', description: 'Close folds recursively.' },
    'zD': { form: 'zD', name: 'Delete folds recursive', description: 'Delete folds recursively.' },
    'zE': { form: 'zE', name: 'Eliminate folds', description: 'Eliminate all folds.' },
    'zF': { form: 'zF', name: 'Create fold', description: 'Create a fold for N lines.' },
    'zG': { form: 'zG', name: 'Temporarily mark correct', description: 'Temporarily mark word as correctly spelled.' },
    'zuG': { form: 'zuG', name: 'Undo mark correct', description: 'Undo |zG|.' },
    'zH': { form: 'zH', name: 'Scroll half-screen right', description: 'When `wrap` off scroll half a screenwidth to the right.' },
    'zL': { form: 'zL', name: 'Scroll half-screen left', description: 'When `wrap` off scroll half a screenwidth to the left.' },
    'zM': { form: 'zM', name: 'Fold level zero', description: 'Set `foldlevel` to zero.' },
    'zN': { form: 'zN', name: 'Enable folding', description: 'Set `foldenable`.' },
    'zO': { form: 'zO', name: 'Open folds recursive', description: 'Open folds recursively.' },
    'zP': { form: 'zP', name: 'Put block-mode without space', description: 'Paste in block-mode without trailing spaces.' },
    'zR': { form: 'zR', name: 'Set fold level deepest', description: 'Set `foldlevel` to the deepest fold.' },
    'zW': { form: 'zW', name: 'Temporarily mark incorrect', description: 'Temporarily mark word as incorrectly spelled.' },
    'zuW': { form: 'zuW', name: 'Undo mark incorrect', description: 'Undo |zW|.' },
    'zX': { form: 'zX', name: 'Reapply fold level', description: 'Re-apply `foldlevel`.' },
    'z^': { form: 'z^', name: 'Scroll line above top', description: 'Cursor on line N (default line above window), otherwise like "z-".' },
    'z<CR>': { form: 'z<CR>', name: 'Scroll top', description: 'Redraw, cursor line to top of window, cursor on first non-blank.' },
    'z{height}<CR>': { form: 'z{height}<CR>', name: 'Window height', description: 'Redraw, make window {height} lines high.' },
    'z<Left>': { form: 'z<Left>', name: 'Scroll right', description: 'When `wrap` off scroll screen N characters to the right.' },
    'z<Right>': { form: 'z<Right>', name: 'Scroll left', description: 'When `wrap` off scroll screen N characters to the left.' },
    'A': { form: 'A', name: 'Append after line', description: 'Append text after the end of the line N times.', count: true },
    'B': { form: 'B', name: 'Back WORD', description: 'Cursor N WORDS backward.', categories: ['motion'], count: true },
    'C': { form: '["x]C', name: 'Change line', description: 'Change from the cursor position to the end of the line, and N-1 more lines [into register x]', count: true },
    'D': { form: '["x]D', name: 'Delete line', description: 'Delete the characters under the cursor until the end of the line and N-1 more lines [into register x]', count: true },
    'E': { form: 'E', name: 'End WORD', description: 'Cursor forward to the end of WORD N.', categories: ['motion'], count: true },
    'F': { form: 'F{char}', name: 'Find char reverse', description: 'Cursor to the Nth occurrence of {char} to the left.', categories: ['motion'], count: true },
    'G': { form: 'G', name: 'Go to line/end', description: 'Cursor to line N, default last line.', categories: ['motion'], count: true },
    'H': { form: 'H', name: 'Highest line', description: 'Cursor to line N from top of screen.', categories: ['motion'], count: true },
    'I': { form: 'I', name: 'Insert before line', description: 'Insert text before the first CHAR on the line N times.', count: true },
    'J': { form: 'J', name: 'Join line', description: 'Join N lines; default is 2.', count: true },
    'K': { form: 'K', name: 'Lookup keyword', description: 'lookup Keyword under the cursor with `keywordprg`.' },
    'L': { form: 'L', name: 'Lowest line', description: 'Cursor to line N from bottom of screen.', categories: ['motion'], count: true },
    'M': { form: 'M', name: 'Middle line', description: 'Cursor to middle line of screen.', categories: ['motion'] },
    'N': { form: 'N', name: 'Find next reverse', description: 'repeat the latest `/` or `?` N times in opposite direction.', categories: ['motion'], count: true },
    'O': { form: 'O', name: 'Open line above', description: 'Begin a new line above the cursor and insert text, repeat N times.', count: true },
    'P': { form: '["x]P', name: 'Put before', description: 'Put the text [from register x] before the cursor N times.', count: true },
    'Q': { form: 'Q', name: 'Ex mode', description: 'Switch to Ex mode.' },
    'R': { form: 'R', name: 'Replace mode', description: 'Enter replace mode: overtype existing characters, repeat the entered text N-1 times.', count: true },
    'S': { form: '["x]S', name: 'Substitute line', description: 'Delete N lines [into register x] and start insert', count: true },
    'T': { form: 'T{char}', name: 'Find to char reverse', description: 'Cursor till after Nth occurrence of {char} to the left.', categories: ['motion'], count: true },
    'U': { form: 'U', name: 'Undo line', description: 'Undo all latest changes on one line.' },
    'V': { form: 'V', name: 'Visual line mode', description: 'Start linewise Visual mode.' },
    'W': { form: 'W', name: 'WORD', description: 'Cursor N WORDS forward.', categories: ['motion'], count: true },
    'X': { form: '["x]X', name: 'Delete char', description: 'Delete N characters before the cursor [into register x].', count: true },
    'Y': { form: '["x]Y', name: 'Yank line', description: 'Yank N lines [into register x]. |default-mappings|.', count: true },
    'ZZ': { form: 'ZZ', name: 'Write and close', description: 'Write if buffer changed and close window.' },
    'ZQ': { form: 'ZQ', name: 'Clise without writing', description: 'Close window without writing.' },
    '!': { form: '!{motion}{filter}', name: 'Filter', description: 'Filter Nmove text through the {filter} command.', count: true },
    '!!': { form: '!!{filter}', name: 'Filter line', description: 'Filter N lines through the {filter} command.', count: true },
    '"': { form: '"{register}', name: 'Register', description: 'Use {register} for next delete, yank or put ({.%#:} only work with put).' },
    '*': { form: '*', name: 'Find under cursor', description: 'Search forward for the Nth occurrence of the ident under the cursor.', categories: ['motion'], count: true },
    '#': { form: '#', name: 'Find under cursor reverse', description: 'Search backward for the Nth occurrence of the ident under the cursor.', categories: ['motion'], count: true },
    '$': { form: '$', name: 'End of line', description: 'Cursor to the end of Nth next line.', categories: ['motion'], count: true },
    '%': { form: '%', name: 'Find matching', description: 'Find the next (curly/square) bracket on this line and go to its match, or go to matching comment bracket, or go to matching preprocessor directive. Or, with count, go to N percentage in the file.', categories: ['motion'], count: true },
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
    '\'"': { form: '\'"', name: 'To last exiting line', description: 'To the cursor line when last exiting the current buffer.', categories: ['motion'] },
    "'^": { form: "'^", name: 'To last insert line', description: 'To the line where the cursor was the last time when Insert mode was stopped.', categories: ['motion'] },
    "'.": { form: "'.", name: 'To last change line', description: 'To the position where the last change was made.', categories: ['motion'] },
    '(': { form: '(', name: 'Back sentence', description: 'Cursor N sentences backward.', categories: ['motion'], count: true },
    ')': { form: ')', name: 'Sentence', description: 'Cursor N sentences forward.', categories: ['motion'], count: true },
    '+': { form: '+', name: 'Start of lower line', description: 'Cursor to the first CHAR N lines lower.', categories: ['motion'], count: true },
    ',': { form: ',', name: 'Find previous', description: 'Repeat latest f, t, F or T in opposite direction N times.', categories: ['motion'], count: true },
    '-': { form: '-', name: 'Start of higher line', description: 'Cursor to the first CHAR N lines higher.', categories: ['motion'], count: true },
    '.': { form: '.', name: 'Repeat action', description: 'Repeat last change with count replaced with N.', count: true },
    '/': { form: '/{pattern}<CR>', name: 'Search', description: 'Search forward for the Nth occurrence of {pattern}. Or repeat last search with `/<CR>`.', categories: ['motion'], count: true },
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
    ':': { form: ':', name: 'Ex command mode', description: 'Start entering an Ex command. Given count (`N:`), with range from current line to N-1 lines down.', count: true },
    ';': { form: ';', name: 'Find next', description: 'Repeat latest f, t, F or T N times.', categories: ['motion'], count: true },
    '<': { form: '<{motion}', name: 'Unindent', description: 'Shift Nmove lines one `shiftwidth` leftwards.', count: true },
    '<<': { form: '<<', name: 'Unindent line', description: 'Shift N lines one `shiftwidth` leftwards.', count: true },
    '=': { form: '={motion}', name: 'Autoindent', description: 'Filter Nmove lines through `indent`.', count: true },
    '==': { form: '==', name: 'Autoindent line', description: 'Filter N lines through `indent`.', count: true },
    '>': { form: '>{motion}', name: 'Indent', description: 'Shift Nmove lines one `shiftwidth` rightwards.', count: true },
    '>>': { form: '>>', name: 'Indent line', description: 'Shift N lines one `shiftwidth` rightwards.', count: true },
    '?': { form: '?{pattern}<CR>', name: 'Search reverse', description: 'Search backward for the Nth occurrence of {pattern}. Or repeat last search with `?<CR>`.', categories: ['motion'], count: true },
    '@': { form: '@{a-z}', name: 'Execute macro', description: 'Execute the contents of register {a-z} N times.', count: true },
    '@:': { form: '@:', name: 'Repeat command', description: 'Repeat the previous `:` command N times.', count: true },
    '@@': { form: '@@', name: 'Repeat macro', description: 'Repeat the previous @{a-z} N times.', count: true },
    '[#': { form: '[#', name: 'Previous ifdef', description: 'Cursor to N previous unmatched #if, #else or #ifdef.', categories: ['motion'] },
    ']#': { form: ']#', name: 'Next ifdef', description: 'Cursor to N next unmatched #endif or #else.', categories: ['motion'] },
    "['": { form: "['", name: 'Previous marked line', description: 'Cursor to previous lowercase mark, on first non-blank.', categories: ['motion'] },
    "]'": { form: "]'", name: 'Next marked line', description: 'Cursor to next lowercase mark, on first non-blank.', categories: ['motion'] },
    '[`': { form: '[`', name: 'Previous mark', description: 'Cursor to previous lowercase mark.', categories: ['motion'] },
    ']`': { form: ']`', name: 'Next mark', description: 'Cursor to next lowercase mark.', categories: ['motion'] },
    '[(': { form: '[(', name: 'Previous (', description: 'Cursor N times back to unmatched `(`.', categories: ['motion'] },
    '](': { form: '](', name: 'Next (', description: 'Cursor N times forward to next unmatched `(`.', categories: ['motion'] },
    '[{': { form: '[{', name: 'Previous {', description: 'Cursor N times back to unmatched `{`.', categories: ['motion'] },
    ']{': { form: ']{', name: 'Next {', description: 'Cursor N times forward to unmatched `}`.', categories: ['motion'] },
    '[*': { form: '[*', name: 'Previous comment', description: 'Cursor to N previous start of a C comment.', categories: ['motion'] },
    ']*': { form: ']*', name: 'Next comment', description: 'Cursor to N next end of a C comment.', categories: ['motion'] },
    '[/': { form: '[/', name: 'Previous comment', description: 'Cursor to N previous start of a C comment.', categories: ['motion'] },
    ']/': { form: ']/', name: 'Next comment', description: 'Cursor to N next end of a C comment.', categories: ['motion'] },
    '[c': { form: '[c', name: 'Start of Change', description: 'Cursor N times backwards to start of change.', categories: ['motion'] },
    ']c': { form: ']c', name: 'End of Change', description: 'Cursor N times forwards to end of change.', categories: ['motion'] },
    '[d': { form: '[d', name: 'Show #define', description: 'Show first #define found in current and included files matching the word under the cursor, start searching at beginning of current file.' },
    ']d': { form: ']d', name: 'Show #define', description: 'Show first #define found in current and included files matching the word under the cursor, start searching at beginning of current file.' },
    '[f': { form: '[f', name: 'Go to file', description: 'Start editing the file whose name is under the cursor.' },
    ']f': { form: ']f', name: 'Go to file', description: 'Start editing the file whose name is under the cursor.' },
    '[i': { form: '[i', name: 'Show word', description: 'Show first line found in current and included files that contains the word under the cursor, start searching at beginning of current file.' },
    ']i': { form: ']i', name: 'Show word', description: 'Show first line found in current and included files that contains the word under the cursor, start searching at beginning of current file.' },
    '[m': { form: '[m', name: 'Start of member', description: 'Cursor N times back to start of member function.', categories: ['motion'] },
    ']m': { form: ']m', name: 'End of member', description: 'Cursor N times forward to end of member function.', categories: ['motion'] },
    '[s': { form: '[s', name: 'Previous misspelling', description: 'Move to the previous misspelled word.', categories: ['motion'] },
    ']s': { form: ']s', name: 'Next misspelling', description: 'Move to the next misspelled word.', categories: ['motion'] },
    '[z': { form: '[z', name: 'Start of fold', description: 'Move to start of open fold.', categories: ['motion'] },
    ']z': { form: ']z', name: 'End of fold', description: 'Move to end of open fold.', categories: ['motion'] },
    '[[': { form: '[[', name: 'Back section', description: 'Cursor N sections backward.', categories: ['motion'] },
    '[]': { form: '[]', name: 'Back SECTION', description: 'Cursor N SECTIONS backward.', categories: ['motion'] },
    ']]': { form: ']]', name: 'Forward section', description: 'Cursor N sections forward.', categories: ['motion'] },
    '][': { form: '][', name: 'Forward SECTION', description: 'Cursor N SECTIONS forward.', categories: ['motion'] },
    '[p': { form: '[p', name: 'Put before and indent', description: 'Like `p`, but adjust indent to current line.' },
    ']p': { form: ']p', name: 'Put and indent', description: 'Like `p`, but adjust indent to current line.' },
    '[P': { form: '[P', name: 'Put before and indent', description: 'Like `P`, but adjust indent to current line.' },
    ']P': { form: ']P', name: 'Put before and indent', description: 'Like `P`, but adjust indent to current line.' },
    '[D': { form: '[D', name: 'List defines', description: 'List all defines found in current and included files matching the word under the cursor, start searching at beginning of current file.' },
    ']D': { form: ']D', name: 'List defines', description: 'List all defines found in current and included files matching the word under the cursor, start searching at beginning of current file.' },
    '[I': { form: '[I', name: 'List includes', description: 'List all lines found in current and included files that contain the word under the cursor, start searching at beginning of current file.' },
    ']I': { form: ']I', name: 'List includes', description: 'List all lines found in current and included files that contain the word under the cursor, start searching at beginning of current file.' },
    ']^i': { form: ']^d', name: 'Find #define', description: 'Jump to first #define found in current and included files matching the word under the cursor, start searching at cursor position.' },
    ']^d': { form: ']^i', name: 'Find under cursor', description: 'Jump to first line in current and included files that contains the word under the cursor, start searching at cursor position.' },
    ']<MiddleMouse>': { form: ']<MiddleMouse>', name: 'Put and indent', description: 'Like `p`, but adjust indent to current line.' },
    '^': { form: '^', name: 'Start of line', description: 'Cursor to the first CHAR of the line.', categories: ['motion'] },
    '_': { form: '_', name: 'Start of line', description: 'Cursor to the first CHAR N - 1 lines lower.', categories: ['motion'], count: true },
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
    '`"': { form: '`"', name: 'To last exiting position', description: 'To the cursor position when last exiting the current buffer.', categories: ['motion'] },
    '`^': { form: '`^', name: 'To last insert position', description: 'To the position where the cursor was the last time when Insert mode was stopped.', categories: ['motion'] },
    '`.': { form: '`.', name: 'To last change position', description: 'To the position where the last change was made.', categories: ['motion'] },
    '{': { form: '{', name: 'Back paragraph', description: 'Cursor N paragraphs backward.', categories: ['motion'], count: true },
    '|': { form: '|', name: 'Go to column', description: 'Cursor to column N.', categories: ['motion'], count: true },
    '}': { form: '}', name: 'Paragraph', description: 'Cursor N paragraphs forward.', categories: ['motion'], count: true },
    '~': { form: '~', name: 'Toggle case', description: 'Switch case of N characters under cursor and move the cursor N characters to the right (`tildeop` may allow taking motion, but so does `g~`).', count: true },
    '\\': { form: '\\', name: 'Leader', description: 'Reserved for user mappings.' },
    '<Space>': { form: '<Space>', name: 'Right', description: 'Cursor N chars to the right.', categories: ['motion'], count: true },
    '<BS>': { form: '<BS>', name: 'Left', description: 'Cursor N chars to the left.', categories: ['motion'], count: true },
    '<CR>': { form: '<CR>', name: 'Start of following line', description: 'Cursor to the first CHAR N lines lower.', categories: ['motion'], count: true },
    '<Tab>': { form: '<Tab>', name: 'Previous jump', description: 'Go to N newer entry in jump list.', count: true },
    '<Esc>': { form: '<Esc>', name: 'Reset', description: 'Reset state and remain in Normal mode.' },
    '<Left>': { form: '<Left>', name: 'Left', description: 'Cursor N chars to the left.', categories: ['motion'], count: true },
    '<Down>': { form: '<Down>', name: 'Down', description: 'Cursor N lines downward.', categories: ['motion'], count: true },
    '<Up>': { form: '<Up>', name: 'Up', description: 'Cursor N lines upward.', categories: ['motion'], count: true },
    '<Right>': { form: '<Right>', name: 'Right', description: 'Cursor N chars to the right.', categories: ['motion'], count: true },
    '<Del>': { form: '["x]<Del>', name: 'Delete char', description: 'Delete N characters under and after the cursor [into register x]. Also, remove the last digit when entering count.', count: true },
    '<NL>': { form: '<NL>', name: 'Down', description: 'Cursor N lines downward.', categories: ['motion'], count: true },
    '<End>': { form: '<End>', name: 'End of line', description: 'Cursor to the end of Nth next line.', categories: ['motion'], count: true },
    '<F1>': { form: '<F1>', name: 'Help', description: 'Open a help window.' },
    '<Help>': { form: '<Help>', name: 'Help', description: 'Open a help window.' },
    '<Home>': { form: '<Home>', name: 'First column', description: 'Cursor to the first char of the line.' },
    '<Insert>': { form: '<Insert>', name: 'Insert', description: 'Insert text before the cursor N times.', count: true },
    '<PageDown>': { form: '<PageDown>', name: 'Scroll forward screen', description: 'Scroll N screens Forward.', count: true },
    '<S-Down>': { form: '⇧<Down>', name: 'Scroll forward screen', description: 'Scroll N screens Forward.', count: true },
    '<PageUp>': { form: '<PageUp>', name: 'Scroll back screen', description: 'Scroll N screens Backwards.', count: true },
    '<S-Up>': { form: '⇧<Up>', name: 'Scroll back screen', description: 'Scroll N screens Backwards.', count: true },
    '<Undo>': { form: '<Undo>', name: 'Undo', description: 'Undo changes.', count: true },
    '<C-End>': { form: '^<End>', name: 'Go to line/end', description: 'Cursor to line N, default last line.', categories: ['motion'], count: true },
    '<C-Home>': { form: '^<Home>', name: 'Go to line/beginning', description: 'Cursor to line N, default first line.', count: true },
    '<C-Left>': { form: '^<Left>', name: 'Back word', description: 'Cursor N words backward.', categories: ['motion'], count: true },
    '<S-Left>': { form: '⇧<Left>', name: 'Back word', description: 'Cursor N words backward.', categories: ['motion'], count: true },
    '<C-Right>': { form: '^<Right>', name: 'Word', description: 'Cursor N words forward.', categories: ['motion'], count: true },
    '<S-Right>': { form: '⇧<Right>', name: 'Word', description: 'Cursor N words forward.', categories: ['motion'], count: true },
    '<C-LeftMouse>': { form: '^<LeftMouse>', name: 'Tag definition', description: '`:ta` to ident at the mouse click.' },
    '<C-MiddleMouse>': { form: '^<MiddleMouse>', name: 'Put', description: 'Put at mouse position.', count: true },
    '<C-RightMouse>': { form: '^<RightMouse>', name: 'Tag', description: 'Jump to N older Tag in tag list.' },
    '<LeftMouse>': { form: '<LeftMouse>', name: 'Move cursor', description: 'Move cursor to the mouse click position.' },
    '<MiddleMouse>': { form: '<MiddleMouse>', name: 'Put before', description: 'Put the text [from register x] before the cursor N times, leave the cursor after it.' },
    '<RightMouse>': { form: '<RightMouse>', name: 'Visual mode', description: 'Start Visual mode, move cursor to the mouse click position.' },
    '<S-LeftMouse>': { form: '⇧<LeftMouse>', name: 'Find under cursor', description: 'Search forward for the Nth occurrence of the ident under the mouse.', count: true },
    '<S-RightMouse>': { form: '⇧<RightMouse>', name: 'Find under cursor reverse', description: 'Search backward for the Nth occurrence of the ident under the mouse.', count: true },
    '<ScrollWheelDown>': { form: '<ScrollWheelDown>', name: 'Scroll down', description: 'Move window three lines down.' },
    '<S-ScrollWheelDown>': { form: '<S-ScrollWheelDown>', name: 'Scroll down', description: 'Move window one page down.' },
    '<ScrollWheelUp>': { form: '<ScrollWheelUp>', name: 'Scroll up', description: 'Move window three lines up.' },
    '<S-ScrollWheelUp>': { form: '<S-ScrollWheelUp>', name: 'Scroll up', description: 'Move window one page up.' },
    '<ScrollWheelLeft>': { form: '<ScrollWheelLeft>', name: 'Scroll left', description: 'Move window six columns left.' },
    '<S-ScrollWheelLeft>': { form: '<S-ScrollWheelLeft>', name: 'Scroll left', description: 'Move window one page left.' },
    '<ScrollWheelRight>': { form: '<ScrollWheelRight>', name: 'Scroll right', description: 'Move window six columns right.' },
    '<S-ScrollWheelRight>': { form: '<S-ScrollWheelRight>', name: 'Scroll right', description: 'Move window one page right.' },
    '^a': { form: '^a', name: 'Increment', description: 'Add N to number at/after cursor.', count: true },
    '^b': { form: '^b', name: 'Scroll back screen', description: 'Scroll N screens Backwards.', count: true },
    '^c': { form: '^c', name: 'Cancel command', description: 'Interrupt current (search) command.' },
    '^d': { form: '^d', name: 'Scroll down half-screen', description: 'Scroll Down N lines (default: half a screen).', count: true },
    '^e': { form: '^e', name: 'Scroll up line', description: 'Scroll N lines upwards (N lines Extra).', count: true },
    '^f': { form: '^f', name: 'Scroll forward screen', description: 'Scroll N screens Forward.', count: true },
    '^g': { form: '^g', name: 'Display info', description: 'Display current file name and position.' },
    '^h': { form: '^h', name: 'Left', description: 'Cursor N chars to the left.', categories: ['motion'], count: true },
    '^i': { form: '^i', name: 'Previous jump', description: 'Go to N newer entry in jump list.', count: true },
    '^j': { form: '^j', name: 'Down', description: 'Cursor N lines downward.', categories: ['motion'], count: true },
    // ^k
    '^l': { form: '^l', name: 'Redraw', description: 'Redraw screen.' },
    '^m': { form: '^m', name: 'Start of following line', description: 'Cursor to the first CHAR N lines lower.', categories: ['motion'], count: true },
    '^n': { form: '^n', name: 'Down', description: 'Cursor N lines downward.', categories: ['motion'], count: true },
    '^o': { form: '^o', name: 'Jump', description: 'Go to N older entry in jump list.', categories: ['motion'], count: true },
    '^p': { form: '^p', name: 'Up', description: 'Cursor N lines upward.', categories: ['motion'], count: true },
    // ^q
    '^r': { form: '^r', name: 'Redo', description: 'Redo changes which were undone with `u`.', count: true },
    // ^s
    '^t': { form: '^t', name: 'Tag', description: 'Jump to N older Tag in tag list.', count: true },
    '^u': { form: '^u', name: 'Scroll up half-screen', description: 'Scroll N lines Upwards (default: half a screen).', count: true },
    '^v': { form: '^v', name: 'Visual block mode', description: 'Start blockwise Visual mode.' },
    // window commands (note ^wx == ^w^x)
    '^w+': { form: '^w+', name: 'Increase height', description: 'Increase current window height N lines.' },
    '^w-': { form: '^w-', name: 'Decrease height', description: 'Decrease current window height N lines.' },
    '^w<': { form: '^w<', name: 'Decrease width', description: 'Decrease current window width N columns.' },
    '^w>': { form: '^w>', name: 'Increase width', description: 'Increase current window width N columns.' },
    '^w=': { form: '^w=', name: 'Equalize windows', description: 'Make all windows the same height & width.' },
    '^wH': { form: '^wH', name: 'Window left', description: 'Move current window to the far left.' },
    '^wJ': { form: '^wJ', name: 'Window bottom', description: 'Move current window to the very bottom.' },
    '^wK': { form: '^wK', name: 'Window top', description: 'Move current window to the very top.' },
    '^wL': { form: '^wL', name: 'Window right', description: 'Move current window to the far right.' },
    '^wP': { form: '^wP', name: 'Preview window', description: 'Go to preview window.' },
    '^wT': { form: '^wT', name: 'Window to tab', description: 'Move current window to a new tab page.' },
    '^wb': { form: '^wb', name: 'Bottom window', description: 'Go to bottom window.' },
    '^wc': { form: '^wc', name: 'Close window', description: 'Close current window (like |:close|).' },
    '^wd': { form: '^wd', name: 'Split and jump to definition', description: 'Split window and jump to definition under the cursor.' },
    '^wf': { form: '^wf', name: 'Split and edit file', description: 'Split window and edit file name under the cursor.' },
    '^wF': { form: '^wF', name: 'Split and edit file at line', description: 'Split window and edit file name under the cursor and jump to the line number following the file name..' },
    '^wh': { form: '^wh', name: 'Go to window', description: 'Go to Nth left window (stop at first window).' },
    '^wi': { form: '^wi', name: 'Split and jump to declaration', description: 'Split window and jump to declaration of identifier under the cursor.' },
    '^wj': { form: '^wj', name: 'Down window', description: 'Go N windows down (stop at last window).' },
    '^wk': { form: '^wk', name: 'Up window', description: 'Go N windows up (stop at first window).' },
    '^wl': { form: '^wl', name: 'Right window', description: 'Go to Nth right window (stop at last window).' },
    '^wn': { form: '^wn', name: 'New window', description: 'Open new window, N lines high.' },
    '^wo': { form: '^wo', name: 'Only window', description: 'Close all but current window (like `:only`).' },
    '^wp': { form: '^wp', name: 'Previous window', description: 'Go to previous (last accessed) window.' },
    '^wq': { form: '^wq', name: 'Quit window', description: 'Quit current window (like `:quit`).' },
    '^wr': { form: '^wr', name: 'Rotate windows down', description: 'Rotate windows downwards N times.' },
    '^wR': { form: '^wR', name: 'Rotate windows up', description: 'Rotate windows upwards N times.' },
    '^ws': { form: '^ws', name: 'Split window', description: 'Split current window in two parts, new window N lines high.' },
    '^wS': { form: '^wS', name: 'Split window', description: 'Split current window in two parts, new window N lines high.' },
    '^wt': { form: '^wt', name: 'Top window', description: 'Go to top window.' },
    '^wv': { form: '^wv', name: 'Split vertically', description: 'Split current window vertically, new window N columns wide.' },
    '^ww': { form: '^ww', name: 'Next window', description: 'Go to N next window (wrap around).' },
    '^wW': { form: '^wW', name: 'Previous window', description: 'Go to N previous window (wrap around).' },
    '^wx': { form: '^wx', name: 'Exchange window', description: 'Exchange current window with window N (default: next window).' },
    '^wz': { form: '^wz', name: 'Close preview window', description: 'Close preview window.' },
    '^wgf': { form: '^wgf', name: 'Edit file in new tab', description: 'Edit file name under the cursor in a new tab page.' },
    '^wgF': { form: '^wgF', name: 'Edit file in new tab at line', description: 'Edit file name under the cursor in a new tab page and jump to the line number following the file name..' },
    '^wgt': { form: '^wgt', name: 'Next tab', description: 'Go to the next tab page.' },
    '^wgT': { form: '^wgT', name: 'Previous tab', description: 'Go to the previous tab page.' },
    '^wg]': { form: '^wg]', name: 'Split window and select tag', description: 'Split window and do |:tselect| for tag under cursor.' },
    '^wg}': { form: '^wg}', name: 'Jump to tag', description: 'Do a `:ptjump` to the tag under the cursor.' },
    '^wg<Tab>': { form: '^wg<Tab>', name: 'Go to tab', description: 'Go to last accessed tab page.' },
    '^wg^]': { form: '^wg^]', name: 'Split window and jump to tag', description: 'Split window and do `:tjump` to tag under cursor.' },
    '^w]': { form: '^w]', name: 'Split window and jump to tag', description: 'Split window and jump to tag under cursor.' },
    '^w^': { form: '^w^', name: 'Split window and etid alternate', description: 'Split current window and edit alternate file N.' },
    '^w_': { form: '^w_', name: 'Set window height', description: 'Set current window height to N (default: very high). Similar to `z{height}<CR>`.' },
    '^w|': { form: '^w|', name: 'Set window width', description: 'Set window width to N columns.' },
    '^w}': { form: '^w}', name: 'Show tag', description: 'Show tag under cursor in preview window.' },
    '^w<Down>': { form: '^w<Down>', name: 'Down window', description: 'Go N windows down (stop at last window).' },
    '^w<Up>': { form: '^w<Up>', name: 'Up window', description: 'Go N windows up (stop at first window).' },
    '^w<Left>': { form: '^w<Left>', name: 'Go to window', description: 'Go to Nth left window (stop at first window).' },
    '^w<Right>': { form: '^w<Right>', name: 'Right window', description: 'Go to Nth right window (stop at last window).' },
    '^x': { form: '^x', name: 'Decrement', description: 'Subtract N from number at/after cursor.', count: true },
    '^y': { form: '^y', name: 'Scroll down line', description: 'Scroll N lines downwards.', count: true },
    '^z': { form: '^z', name: 'Suspend', description: 'Suspend program (or start new shell).' },
    '^]': { form: '^]', name: 'Tag definition', description: '`:ta` to ident under cursor.' },
    '^[': { form: '^[', name: 'Reset', description: 'Reset state and remain in Normal mode. Alternative to <Esc>.' },
    '^^': { form: '^^', name: 'Alternate file', description: 'Edit Nth alternate file. Same as `:e #N`.', count: true },
    '^<Tab>': { form: '^<Tab>', name: 'Go to tab', description: 'Go to last accessed tab page.' },
    '^\\': { form: '^\\', name: 'Leader', description: 'Reserved for user mappings.' },
  },
  textObjects: {
    'quotes': { forms: ['"'], name: "Quotes", description: 'Double quoted string.' },
    'tick': { forms: ["'"], name: "Tick", description: 'Single quoted string.' },
    'backticks': { forms: ['`'], name: "Backticks", description: 'Backtick string `...`.' },
    'angle_brackets': { forms: ['<','>'], name: "Angle Brackets", description: 'Angle brackets <...>.' },
    'brackets': { forms: ['[',']'], name: "Brackets", description: 'Square brackets [...].' },
    'block': { forms: ['(',')','b'], name: "Block", description: 'Parenthesis (...).' },
    'big_block': { forms: ['{','}','B'], name: "BLOCK", description: 'Curly braces {...}.' },
    'word': { forms: ['w'], name: "Word", description: 'Word (with white space).' },
    'big_word': { forms: ['W'], name: "WORD", description: 'WORD (with white space).' },
    'paragraph': { forms: ['p'], name: "Paragraph", description: 'Paragraph (with white space).' },
    'sentence': { forms: ['s'], name: "Sentence", description: 'Sentence (with white space).' },
    'tag': { forms: ['t'], name: "Tag", description: 'Tag block (with white space).' },
  },
  insert: {
    'i_^@': { form: '^@', name: 'Insert Previous and Normal Mode', description: 'Insert previously inserted text and stop insert.' },
    'i_^a': { form: '^a', name: 'Insert Previous', description: 'Insert previously inserted text.' },
    'i_^c': { form: '^c', name: 'Quit Insert Mode', description: 'Quit insert mode, without checking for abbreviation.' },
    'i_^d': { form: '^d', name: 'Unindent', description: 'Delete one shiftwidth of indent in the current line.' },
    'i_^e': { form: '^e', name: 'Copy Below', description: 'Insert the character which is below the cursor.' },
    'i_^f': { form: '^f', name: 'Reindent', description: "Not used (but by default it's in `cinkeys` to re-indent the current line)." },
    'i_^gj': { form: '^gj', name: 'Down', description: 'Line down, to column where inserting started.' },
    'i_^gk': { form: '^gk', name: 'Up', description: 'Line up, to column where inserting started.' },
    'i_^gu': { form: '^gu', name: 'New Undoable Edit', description: 'Start new undoable edit.' },
    'i_^gU': { form: '^gU{movement}', name: 'Move Within Undo', description: "Don't break undo with next cursor movement." },
    'i_<CR>': { form: '<CR>', name: 'New Line', description: 'Begin new line.' },
    'i_<NL>': { form: '<NL>', name: 'New Line', description: 'Begin new line. Same as <CR>.' },
    'i_^j': { form: '^j', name: 'New Line', description: 'Begin new line. Same as <CR>.' },
    'i_^m': { form: '^m', name: 'New Line', description: 'Begin new line. Same as <CR>.' },
    'i_<Tab>': { form: '<Tab>', name: 'Tab', description: 'Insert a <Tab> character.' },
    'i_^i': { form: '^i', name: 'Tab', description: 'Insert a <Tab> character. Same as <Tab>.' },
    'i_<BS>': { form: '<BS>', name: 'Backspace', description: 'Delete character before the cursor.' },
    'i_^h': { form: '^h', name: 'Backspace', description: 'Delete character before the cursor. Same as <BS>.' },
    'i_^k': { form: '^k{char1}{char2}', name: 'Digraph', description: 'CTRL-K {char1} {char2} enter digraph.' },
    'i_^n': { form: '^n', name: 'Next', description: 'Find next match for keyword in front of the cursor.' },
    'i_^o': { form: '^o{command}', name: 'Normal Command', description: 'Execute a single command and return to insert mode.' },
    'i_^p': { form: '^p', name: 'Previous', description: 'Find previous match for keyword in front of the cursor.' },
    'i_^q': { form: '^q{char}', name: 'Literal', description: 'Insert next non-digit literally or insert three digit decimal number as a single byte. Same as CTRL-V, unless used for terminal control flow.' },
    'i_^Q': { form: '^Q{char}', name: 'Literal', description: 'Insert next non-digit literally or insert three digit decimal number as a single byte. Like CTRL-Q unless `tui-modifyOtherKeys` is active.' },
    'i_^r': { form: '^r{register}', name: 'Insert Register', description: 'CTRL-R {register} insert the contents of a register.' },
    'i_^rr': { form: '^rr{register}', name: 'Insert Literal Register', description: 'CTRL-R CTRL-R {register} insert the contents of a register literally.' },
    'i_^rr': { form: '^rr{register}', name: 'Insert Literal Register (No Indent)', description: "CTRL-R CTRL-O {register} insert the contents of a register literally and don't auto-indent." },
    'i_^rr': { form: '^rr{register}', name: 'Insert Literal Register (Autoindent)', description: 'CTRL-R CTRL-P {register} insert the contents of a register literally and fix indent.' },
    // i_^s
    'i_^t': { form: '^t', name: 'Indent', description: 'Insert one shiftwidth of indent in current line.' },
    'i_^u': { form: '^u', name: 'Undo Line', description: 'Delete all entered characters in the current line.' },
    'i_^v': { form: '^v{char}', name: 'Literal', description: 'Insert next non-digit literally or insert three digit decimal number as a single byte.' },
    'i_^V': { form: '^V{char/number}', name: 'Literal', description: 'Insert next non-digit literally or insert three digit decimal number as a single byte.. Like CTRL-V unless `tui-modifyOtherKeys` is active.' },
    'i_': { form: '', name: '', description: '' },
    /*
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

|i_CTRL-G_k|	CTRL-G <Up>	line up, to column where inserting started
|i_digraph|	{char1}<BS>{char2} enter digraph (only when 'digraph' option set)

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
    */
  },
  synonyms: [
    ['h','^h','<BS>','<Left>'], // Left
    ['l','<Space>','<Right>'], // Right
    ['k','^p','<Up>'], // Up
    ['j','^j','^n','<Down>','<NL>'], // Down
    ['C','c$'], // Change line
    ['D','d$'], // Delete line
    ['S','cc'], // Substitute line 
    ['Y','yy','y$'] // Yank line
    ['+','^m','<CR>'], // Start of lower line
    ['g<Tab>','^<Tab>'], // Go to tab
    ['[*','[/'], // Previous comment
    [']*',']/'], // Next comment
    ['[d',']d'], // Show #define
    [']f','[f','gf'], // Go to file
    [']i','[i'], // Show word
    [']p','[p'], // Put and indent
    [']P','[P'], // Put before and indent
    [']D','[D'], // List defines
    [']I','[I'], // List includes
    ['<Tab>','^i'], // Previous jump
    ['x','<Del>'], // Delete char
    ['$','<End>'], // End of line
    ['<F1>','<Help>'], // Help
    ['0','<Home>'], // First column
    ['i','<Insert>'], // Insert
    ['^f','<PageDown>','<S-Down>'], // Scroll forward screen
    ['^b','<PageUp>','<S-Up>'], // Scroll back screen
    ['u','<Undo>'], // Undo
    ['G','<C-End>'], // Go to line/end
    ['gg','<C-Home>'], // Got to line/beginning
    ['b','<C-Left>','<S-Left>'], // Back word
    ['w','<C-Right>','<S-Right>'], // Word
    ['^]','<C-LeftMouse>'], // Tag definition
    ['^t','<RightMouse>'], // Tag
    ['gP','<MiddleMouse>'] // Put before and move after
    ['v','<RightMouse>'], // Visual mode
    ['*','<S-LeftMouse>'], // Find under cursor/mouse
    ['#','<S-RightMouse>'], // Find under cursor/mouse reverse
    ['zh','z<Left>'], // Scroll right
    ['zl','z<Right>'], // Scroll left
    ['gj','g<Down>'], // Down screen line
    ['gk','g<Up>'], // Up screen line
    ['g$','g<End>'], // End screen line
    ['g0','g<Home>'], // Leftmost screen character
    ['<C-LeftMouse>','g<LeftMouse>'], // Tag definition
    ['<C-MiddleMouse>','g<MiddleMouse>'], // Put
    ['<C-RightMouse>','g<RightMouse>'], // Tag
    [']p',']<MiddleMouse>'], // Put and indent
    ['^ws','^wS'], // Split window
    ['gt','^wgt'], // Next tab
    ['gT','^wgT'], // Previous tab
    ['g<Tab>','^wg<Tab>'], // Go to tab
    ['^wj','^w<Down>'], // Window down
    ['^wk','^w<Up>'], // Window up
    ['^wh','^w<Left>'], // Window left
    ['^wl','^w<Right>'], // Window right
    ['<Esc>','^['], // Escape
    ['i_<BS>','i_^h'], // backspace
    ['i_<NL>','i_<CR>','i_^j','i_^m'], // new line
    ['i_<Tab>','i_^i'], // tab
    ['i_^q','i_^Q','i_^v','i_^V'], // literal
  ],
  videos: {
    'align_text': { name: 'Align Text', description: 'Align text with `:\'<,\'>norm` commands.', commands: [':norm'], link: "https://youtube.com/shorts/GlnyZDs0aaY" },
    'numbering_lists': { name: 'Numbering Lists', description: 'Numbering lists with `^a`.', keys: ['^a'] },
    'useless_underscore': { name: 'Useless Underscore', description: 'The underscore key is useless, remap it!', keys: ['_'] },
    'basic_motions_1': { name: 'Basic Motions 1', description: 'Moving around with `h` `j` `k` `l`.', keys: ['h','j','k','l','<Left>','<Right>','<Up>','<Down>','<Space>','<BS>'] },
    'basic_motions_2': { name: 'Basic Motions 2', description: 'Moving by words with `w` `b` `e` `ge`.', keys: ['w','b','e','ge'] },
    'basic_motions_3': { name: 'Basic Motions 3', description: 'Moving by big WORDS with `W` `B` `E` `gE`.', keys: ['W','B','E','gE'] },
    'basic_motions_4': { name: 'Basic Motions 4', description: 'Moving horizontally with `$` `^` `0`.', keys: ['$','^','0'] },
    'basic_motions_5': { name: 'Basic Motions 5', description: 'Moving vertically with `L` `H` `M` `gg` `G`.', keys: ['L','H','M','gg','G'] },
    'basic_motions_6': { name: 'Basic Motions 6', description: 'Moving by sentences and paragraphs with `(` `)` `{` `}`.', keys: ['(',')','{','}'] },
    'basic_motions_7': { name: 'Basic Motions 7', description: 'Moving by sections with `]]` `[[` `][` `[]`.', keys: [']]','[[','][','[]'] },
    'basic_motions_8': { name: 'Basic Motions 8', description: 'Moving by lines with `+` `-` `<CR>`.', keys: ['+','-','<CR>'] },
    'find_character': { name: 'Find Character', description: 'Finding characters with `f` `F` `t` `T` `,` `;`.', keys: ['f','F','t','T',',',';'] },
    'join_lines': { name: 'Join Lines', description: 'Joining lines with `J` `gJ`.', keys: ['J','gJ'] },
    'quitting': { name: 'Quitting', description: 'Quitting with `ZZ` `:x` `:wq` `ZQ` `:q!` `:q` `^Z`.', keys: ['ZZ','ZQ','^Z'], commands: [':x',':wq',':q!',':q'] },
    'reverting': { name: 'Reverting', description: 'Reverting with `:e!`.', commands: [':e!'] },
    'scrolling_and_jumping': { name: 'Scrolling and Jumping', description: 'Scrolling and jumping with `^y` `^e` `zt` `zb` `zz` `^f` `^b` `^d` `^u`.', keys: ['^y','^e','zt','zb','zz','^f','^b','^d','^u'] },
    'matching_pairs': { name: 'Matching Pairs', description: 'Moving between matching pairs with `%`.', keys: ['%'] },
    'changing_case': { name: 'Changing Case', description: 'Changing case with `~` `g~` `gu` `gU`.', keys: ['~','g~','gu','gU'] },
    'marks': { name: 'Marks', descrition: 'Marking with `m` and navigating with `\'` ```.', keys: ['m',"'",'`'] },
    'search': { name: 'Search', description: 'Searching with `*` `#` `n` `N` `/` `?`.', keys: ['*','#','n','N','/','?'] },
    'line_column': { name: 'Go To Line/Column', description: 'Navigating to lines and columns with `G` `|` `:{num}`.', keys: ['G','|'], commands: [':{num}'] },
    'advanced_selection': { name: 'Advanced Selection', description: "Extending selection with `o` and motions. Reselecting with `gv`. And navigating to the start and end of previous selections with `'<` `'>` ``<` ``>`.", keys: ['v_o' /* visual mode o */,'gv',"'<","'>",'`<','`>'] },
    'visual_modes': { name: 'Visual Modes', description: 'Visual mode with `v`, visual line mode with `V`, and visual block mode with `^v` or `^q`.', keys: ['v','V','^v','^q'] },
    'undo': { name: 'Undo', description: 'Undoing changes with `u` and `U`. Redoing them with `^r`.', keys: ['u','U','^r'] },
    'delete_char': { name: 'Delete Character', description: 'Deleting characters with `x` and `X`.', keys: ['x','X'] },
    'indenting': { name: 'Indenting', description: 'Indenting, unindenting and autoindenting with `<{motion}` `<<` `>{motion}` `>>` `={motion}` `==`.', keys: ['<<','<','>>','>','==','=','v_=','v_<','v_>'] },
    'jumps': { name: 'Jumps', description: "Navigating jumps with `''` ```` `^o` `^i`.", keys: ["''",'``','^o','^i'] },
    'replace': { name: 'Replace', description: "Replacing characters with `r` and `R`.", keys: ['r','R'] },
    'delete': { name: 'Delete', description: "Deleting with `d{motion}`, `dd`, `D` and `d` in Visual mode.", keys: ['dd','d','D','vd'] },
    'put': { name: 'Put', description: "Put with `p` and `P` and about line behavior.", keys: ['p','P'] },
    'yank': { name: 'Yank', description: "Yank with `y{motion}` `yy` `Y` and in `y` in Visual mode. Also `:map Y y `yy` `Y` and in `y` in Visual mode. Also `:map Y y$`.", keys: ['y','yy','Y','v_y'], commands: [`:map Y y$`] },
    'patterns': { name: 'Patterns', description: "Common patterns of usage: `xp` `deep` `ddp` `ddP` `yyp`." },
    'text_obj_1': { name: 'Text Objects 1', description: "Specifying inner/around quotes, single-quotes and back ticks.", textobj: ['i"','a"',"i'","a'",'i`','a`'] },
    'text_obj_2': { name: 'Text Objects 2', description: "Specifying inner/around square brackets, parenthesis, curly braces and angle brackets.", textobj: ['i[','i]','a[','a]','i(','i)','ib','a(','a)','ab','i{','i}','iB','a{','a}','aB','i<','i>','a<','a>'] },
    'text_obj_3': { name: 'Text Objects 3', description: "Specifying inner/around words, WORDS, sentences and paragraphs.", textobj: ['iw','aw','iW','aW','ip','ap','is','as'] },
    'text_obj_4': { name: 'Text Objects 4', description: "Specifying inner/around HTML and XML tags..", textobj: ['it','at'] },
    'insert': { name: 'Insert', description: "Insert mode with `i`, `a`, `I`, and `A`.", keys: ['i','I','a','A'] },
    'insert_adv': { name: 'Advanced Insert', description: "Advanced insert mode with `gi` and `gI`.", keys: ['gi','gI'] },
    'open_line': { name: 'Open Line', description: "Open lines with `o` and `O`.", keys: ['o','O'] },
    'change': { name: 'Change', description: "Change with `cc`, `C`, and `c{motion}`.", keys: ['cc','C','c'] },
    'substitute': { name: 'Substitute', description: "Substitute with `S` and `s{motion}.", keys: ['S','s'] },
    'numbered_lines': { name: 'Numbered Lines', description: "Number lines with `:set nu` and/or `:set rnu`.", keys: ['{count}G'], commands: [':{line}',':set nu',':set rnu',':set nu!',':set nonu'] },
  }
}