-- Minimal init.lua for running surround ground truth tests.
-- Loads only nvim-surround from the lazy.nvim package directory.
local surround_path = vim.fn.stdpath("data") .. "/lazy/nvim-surround"
vim.opt.rtp:prepend(surround_path)
require("nvim-surround").setup({})
