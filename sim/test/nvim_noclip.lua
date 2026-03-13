-- Wrapper init.lua for :reg/:di ground truth tests.
-- Used with: nvim -u <this_file>
-- Sources the user's real config, then disables clipboard registers.

-- First, source the user's actual init.lua for monokai, surround, etc.
local user_init = vim.fn.stdpath("config") .. "/init.lua"
vim.cmd("source " .. user_init)

-- Now override the clipboard provider with a dummy that returns empty.
-- This runs AFTER the user config, so it won't be overridden.
vim.g.clipboard = {
  name = 'noop',
  copy = {
    ['+'] = { 'dd', 'of=/dev/null' },
    ['*'] = { 'dd', 'of=/dev/null' },
  },
  paste = {
    ['+'] = { 'cat', '/dev/null' },
    ['*'] = { 'cat', '/dev/null' },
  },
  cache_enabled = 0,
}
-- Force-clear any cached clipboard content
vim.fn.setreg('*', '')
vim.fn.setreg('+', '')
