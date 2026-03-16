"""Test manual folding: zf, zo, zc, zd, zR, zM, za, zj, zk, zE."""

CASES = {
    # ── zf{motion}: Create fold ──

    "fold_zf_j_creates_fold": {
        "description": "zfj creates a 2-line fold and closes it",
        "initial": "aaa\nbbb\nccc\nddd\neee",
        "keys": "zfj",
    },

    "fold_zf_2j_creates_fold": {
        "description": "zf2j creates a 3-line fold",
        "initial": "aaa\nbbb\nccc\nddd\neee",
        "keys": "zf2j",
    },

    "fold_zf_G_creates_fold": {
        "description": "zfG creates fold from cursor to last line",
        "initial": "aaa\nbbb\nccc\nddd\neee",
        "keys": "jzfG",
    },

    # ── zo: Open fold ──

    "fold_zo_opens_fold": {
        "description": "zo opens a closed fold",
        "initial": "aaa\nbbb\nccc\nddd\neee",
        "keys": "zfjzo",
    },

    # ── zc: Close fold ──

    "fold_zc_closes_fold": {
        "description": "zc closes an open fold",
        "initial": "aaa\nbbb\nccc\nddd\neee",
        "keys": "zfjzozc",
    },

    # ── za: Toggle fold ──

    "fold_za_toggles_fold": {
        "description": "za toggles fold open then closed",
        "initial": "aaa\nbbb\nccc\nddd\neee",
        "keys": "zfjzaza",
    },

    # ── zd: Delete fold ──

    "fold_zd_deletes_fold": {
        "description": "zd deletes the fold definition",
        "initial": "aaa\nbbb\nccc\nddd\neee",
        "keys": "zfjzd",
    },

    # ── zR: Open all folds ──

    "fold_zR_opens_all": {
        "description": "zR opens all folds",
        "initial": "aaa\nbbb\nccc\nddd\neee",
        "keys": "zfjjjzfjzR",
    },

    # ── zM: Close all folds ──

    "fold_zM_closes_all": {
        "description": "zM closes all folds",
        "initial": "aaa\nbbb\nccc\nddd\neee",
        "keys": "zfjzojjzfjzozM",
    },

    # ── zE: Delete all folds ──

    "fold_zE_deletes_all": {
        "description": "zE deletes all folds",
        "initial": "aaa\nbbb\nccc\nddd\neee",
        "keys": "zfjjjzfjzE",
    },

    # ── Visual mode zf ──

    "fold_visual_zf": {
        "description": "Vzf creates fold from visual selection",
        "initial": "aaa\nbbb\nccc\nddd\neee",
        "keys": "Vjzf",
    },

    # ── zj: Move to next fold ──

    "fold_zj_next_fold": {
        "description": "zj moves to next fold start",
        "initial": "aaa\nbbb\nccc\nddd\neee\nfff\nggg",
        "keys": "zf2jjjjzfjggzj",
    },

    # ── zk: Move to previous fold ──

    "fold_zk_prev_fold": {
        "description": "zk moves to previous fold",
        "initial": "aaa\nbbb\nccc\nddd\neee\nfff\nggg",
        "keys": "zf2jjjjzfjGzk",
    },
}
