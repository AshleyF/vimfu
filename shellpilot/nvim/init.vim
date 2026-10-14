set nocompatible
set termguicolors
set background=dark
set noshowmode
syntax enable

highlight clear
if exists("syntax_on")
  syntax reset
endif
let g:colors_name = "vimfu-monokai"

highlight Normal       guifg=#d4d4d4 guibg=#000000
highlight Cursor       guifg=#ffffff guibg=#800000
highlight EndOfBuffer  guifg=#000000 guibg=#000000
highlight Comment      guifg=#9ca0a4
highlight Constant     guifg=#ae81ff
highlight String       guifg=#e6db74
highlight Character    guifg=#e6db74
highlight Number       guifg=#ae81ff
highlight Boolean      guifg=#ae81ff
highlight Float        guifg=#ae81ff
highlight Identifier   guifg=#a6e22e
highlight Function     guifg=#a6e22e
highlight Statement    guifg=#f92672
highlight Conditional  guifg=#f92672
highlight Repeat       guifg=#f92672
highlight Label        guifg=#f92672
highlight Operator     guifg=#f92672
highlight Keyword      guifg=#f92672
highlight Exception    guifg=#f92672
highlight PreProc      guifg=#f92672
highlight Type         guifg=#66d9ef
highlight Special      guifg=#fd971f
highlight Underlined   guifg=#66d9ef gui=underline
highlight Error        guifg=#e95678 guibg=#000000
highlight Todo         guifg=#e6db74 guibg=#000000 gui=bold
highlight LineNr       guifg=#d4d4d4 guibg=#000000
highlight CursorLineNr guifg=#fd971f guibg=#26292c gui=bold
highlight StatusLine   guifg=#b1b1b1 guibg=#2e323c
highlight StatusLineNC guifg=#8f908a guibg=#2e323c
highlight TabLine      guifg=#d4d4d4 guibg=#000000
highlight TabLineSel   guifg=#d4d4d4 guibg=#333842 gui=bold
highlight TabLineFill  guifg=#d4d4d4 guibg=#000000
highlight Visual       guibg=#333842
highlight Search       guifg=#26292c guibg=#e6db74
highlight CurSearch    guifg=#07080d guibg=#fce094
highlight MatchParen   guifg=#f92672 guibg=#000000 gui=bold
highlight ErrorMsg     guifg=#e95678 guibg=#000000 gui=bold
highlight Question     guifg=#e6db74 guibg=#000000
highlight ModeMsg      guifg=#f8f8f0 guibg=#000000
highlight Folded       guifg=#8f908a guibg=#2e323c
highlight SpellBad     guifg=#e95678 guibg=#000000 gui=underline
