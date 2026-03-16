"""Tests for :set hlsearch/nohlsearch, :set wrap/nowrap, :set list/nolist."""

CASES = {
    # ── hlsearch toggle ──
    "set_hlsearch_off_on": {
        "keys": "/test\r:set nohlsearch\r",
        "initial": "test one test two\n",
    },
    "set_hlsearch_reenable": {
        "keys": "/test\r:set nohlsearch\r:set hlsearch\r",
        "initial": "test one test two\n",
    },
    "set_hls_short": {
        "keys": "/test\r:set nohls\r",
        "initial": "test one test two\n",
    },
}
