"""Test Vim regex translation in / search and :s backreferences."""

CASES = {
    # ── / search with Vim regex ──

    "search_word_boundary": {
        "description": "Search /\\<word\\> matches whole word only",
        "initial": "foo foobar bar foo",
        "keys": r"/\<foo\>" + "\rn",
        "initial_cursor": [0, 4],
    },

    "search_one_or_more": {
        "description": "Search /ab\\+c matches abbc with \\+",
        "initial": "ac abc abbc abbbc",
        "keys": r"/ab\+c" + "\r",
    },

    "search_optional": {
        "description": "Search /colou\\?r matches color and colour",
        "initial": "color colour colouur",
        "keys": r"/colou\?r" + "\rn",
    },

    "search_group_alternation": {
        "description": "Search /\\(foo\\|bar\\) matches foo or bar",
        "initial": "baz foo bar qux",
        "keys": r"/\(foo\|bar\)" + "\rn",
    },

    # ── :s with backreferences ──

    "sub_backreference_1": {
        "description": ":s with \\1 backreference - swap parens content",
        "initial": "hello world",
        "keys": r":s/\(hello\) \(world\)/\2 \1/" + "\r",
    },

    "sub_backreference_wrap": {
        "description": ":s wraps matched group in brackets",
        "initial": "foo bar baz",
        "keys": r":s/\(bar\)/[\1]/" + "\r",
    },

    "sub_ampersand_and_backref": {
        "description": ":s with & (whole match) and \\1 together",
        "initial": "abc123def",
        "keys": r":s/\([a-z]\+\)\([0-9]\+\)/\2-\1/" + "\r",
    },
}
