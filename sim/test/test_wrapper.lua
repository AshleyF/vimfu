-- Disable clipboard provider so * and + don't appear in :di/:reg
vim.g.loaded_clipboard_provider = 1
-- Define dummy clipboard functions to suppress 'No provider' warnings
vim.cmd([=[
function! provider#clipboard#Call(method, args) abort
  if a:method ==# 'get'
    return [[], '']
  endif
  return 0
endfunction
]=])
local home = os.getenv('HOME') or ''
local f = io.open(home .. '/.config/nvim/init.lua', 'r')
if f then f:close(); dofile(home .. '/.config/nvim/init.lua') end
