CASES = {
    # ===== :noh clears search highlighting =====
    "noh_after_search": {
        "keys": "/hello\r:noh\r",
        "initial": "hello world hello end",
    },
    "noh_cursor_stays": {
        "keys": "/world\r:noh\r",
        "initial": "hello world hello end",
    },
    "nohlsearch_long_form": {
        "keys": "/hello\r:nohlsearch\r",
        "initial": "hello world hello end",
    },
    "noh_after_star": {
        "keys": "*:noh\r",
        "initial": "hello world hello end",
    },
    "noh_after_backward_search": {
        "keys": "G?hello\r:noh\r",
        "initial": "hello\nworld\nhello\nend",
    },
    "noh_then_n_rehighlights": {
        "keys": "/hello\r:noh\rn",
        "initial": "hello world hello end",
    },

    # ===== :noh on multiline content =====
    "noh_multiline": {
        "keys": "/line\r:noh\r",
        "initial": "line one\nline two\nline three",
    },
    "noh_after_n_next": {
        "keys": "/line\rn:noh\r",
        "initial": "line one\nline two\nline three",
    },
}
