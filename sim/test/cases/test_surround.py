"""Consolidated surround test suite.

Merged from test_surround.py, test_surround_edge.py, and
test_surround_full.py with duplicates removed.

Tests nvim-surround (kylechui/nvim-surround) which is compatible with
Tim Pope's surround.vim keybindings: ds (delete), cs (change), ys (add),
and visual S (wrap selection).

Sections:
  01. ys HIGHLIGHT STATE (10 cases)
  02. ds — DELETE SURROUNDING (51 cases)
  03. cs — CHANGE SURROUNDING (90 cases)
  04. ys — ADD SURROUNDING (121 cases)
  05. VISUAL S / VISUAL LINE S (41 cases)
  06. DOT REPEAT (11 cases)
  07. UNDO / REDO (11 cases)
  08. CURSOR POSITION (2 cases)
  09. MULTI-OP SEQUENCES (7 cases)

Total: 344 unique test cases.
"""

# Use nvim with user's config (has nvim-surround installed via lazy.nvim)
NVIM_CMD = 'nvim'

CASES = {
    # ==========================================================
    # 01. ys HIGHLIGHT STATE
    # ==========================================================

    "ys_w_highlight": {
        "description": "ysw pending — target word should be highlighted",
        "keys": "ysw",
        "initial": "hello world today",
    },
    "ys_iw_highlight": {
        "description": "ysiw pending — inner word highlighted",
        "keys": "ysiw",
        "initial": "hello world today",
    },
    "ys_aw_highlight": {
        "description": "ysaw pending — a-word (word + space) highlighted",
        "keys": "ysaw",
        "initial": "hello world today",
    },
    "ys_e_highlight": {
        "description": "yse pending — to end-of-word highlighted",
        "keys": "yse",
        "initial": "hello world today",
    },
    "ys_dollar_highlight": {
        "description": "ys$ pending — to end-of-line highlighted",
        "keys": "ys$",
        "initial": "hello world today",
    },
    "ys_2w_highlight": {
        "description": "ys2w pending — two words highlighted",
        "keys": "ys2w",
        "initial": "one two three four",
    },
    "ys_iw_mid_highlight": {
        "description": "ysiw with cursor mid-word — full word highlighted",
        "keys": "llysiw",
        "initial": "hello world today",
    },
    "ys_f_highlight": {
        "description": "ysfd pending — up to 'd' highlighted",
        "keys": "ysfd",
        "initial": "abcdef ghij",
    },
    "ys_W_highlight": {
        "description": "ysW pending — WORD highlighted",
        "keys": "ysW",
        "initial": "foo-bar baz-qux",
    },
    "yss_highlight": {
        "description": "yss pending — whole line highlighted",
        "keys": "yss",
        "initial": "hello world",
    },
    # ==========================================================
    # 02. ds — DELETE SURROUNDING
    # ==========================================================

    "ds_double_quote": {
        "description": "ds\" removes surrounding double quotes",
        "keys": "ds\"",
        "initial": "\"hello world\"",
    },
    "ds_double_quote_cursor_middle": {
        "description": "ds\" with cursor in middle of quoted text",
        "keys": "fwds\"",
        "initial": "\"hello world\"",
    },
    "ds_single_quote": {
        "description": "ds' removes surrounding single quotes",
        "keys": "ds'",
        "initial": "'hello'",
    },
    "ds_backtick": {
        "description": "ds` removes surrounding backticks",
        "keys": "ds`",
        "initial": "`hello`",
    },
    "ds_quote_with_surrounding_text": {
        "description": "ds\" with text before and after",
        "keys": "f\"lds\"",
        "initial": "say \"hello\" now",
    },
    "ds_close_paren": {
        "description": "ds) removes parentheses",
        "keys": "ds)",
        "initial": "(hello)",
    },
    "ds_paren_alias_b": {
        "description": "dsb removes parentheses (b is alias for ))",
        "keys": "dsb",
        "initial": "(hello)",
    },
    "ds_open_paren_trims_space": {
        "description": "ds( removes parens AND trims inner space",
        "keys": "ds(",
        "initial": "( hello )",
    },
    "ds_close_paren_keeps_space": {
        "description": "ds) removes parens but keeps inner space",
        "keys": "ds)",
        "initial": "( hello )",
    },
    "ds_close_bracket": {
        "description": "ds] removes brackets",
        "keys": "ds]",
        "initial": "[hello]",
    },
    "ds_bracket_alias_r": {
        "description": "dsr removes brackets (r is alias for ])",
        "keys": "dsr",
        "initial": "[hello]",
    },
    "ds_open_bracket_trims_space": {
        "description": "ds[ removes brackets AND trims inner space",
        "keys": "ds[",
        "initial": "[ hello ]",
    },
    "ds_close_brace": {
        "description": "ds} removes braces",
        "keys": "ds}",
        "initial": "{hello}",
    },
    "ds_brace_alias_B": {
        "description": "dsB removes braces",
        "keys": "dsB",
        "initial": "{hello}",
    },
    "ds_open_brace_trims_space": {
        "description": "ds{ removes braces AND trims inner space",
        "keys": "ds{",
        "initial": "{ hello }",
    },
    "ds_close_angle": {
        "description": "ds> removes angle brackets",
        "keys": "ds>",
        "initial": "<hello>",
    },
    "ds_angle_alias_a": {
        "description": "dsa removes angle brackets",
        "keys": "dsa",
        "initial": "<hello>",
    },
    "ds_pipe": {
        "description": "ds| removes pipes",
        "keys": "ds|",
        "initial": "|hello|",
    },
    "ds_asterisk": {
        "description": "ds* removes asterisks",
        "keys": "ds*",
        "initial": "*hello*",
    },
    "ds_underscore": {
        "description": "ds_ removes underscores",
        "keys": "ds_",
        "initial": "_hello_",
    },
    "ds_slash": {
        "description": "ds/ removes slashes",
        "keys": "ds/",
        "initial": "/hello/",
    },
    "ds_tilde": {
        "description": "ds~ removes tildes",
        "keys": "ds~",
        "initial": "~hello~",
    },
    "ds_nested_parens_inner": {
        "description": "ds) removes innermost parens when nested",
        "keys": "fhds)",
        "initial": "((hello))",
    },
    "ds_with_surrounding_text": {
        "description": "ds) with text around the parens",
        "keys": "fhds)",
        "initial": "foo (hello) bar",
    },
    "ds_multiword_content": {
        "description": "ds\" with multiple words inside",
        "keys": "fhds\"",
        "initial": "\"hello world foo\"",
    },
    "ds_then_ys": {
        "description": "Delete surrounding then add new ones",
        "keys": "ds\"ysiw)",
        "initial": "\"hello\" world",
    },
    "ds_empty_content": {
        "description": "ds\" on empty quoted string",
        "keys": "ds\"",
        "initial": "\"\"",
    },
    "ds_single_char_content": {
        "description": "ds\" with single char inside",
        "keys": "fads\"",
        "initial": "\"a\"",
    },
    "ds_no_match_noop": {
        "description": "ds\" when no quotes around cursor — should be no-op",
        "keys": "ds\"",
        "initial": "hello world",
    },
    "ds_nested_paren_inner": {
        "description": "ds) cursor inside inner parens of ((x)) removes inner",
        "keys": "lllds)",
        "initial": "((hello))",
    },
    "ds_nested_bracket_inner": {
        "description": "ds] cursor inside inner brackets of [[x]] removes inner",
        "keys": "lllds]",
        "initial": "[[hello]]",
    },
    "ds_nested_brace_inner": {
        "description": "ds} cursor inside inner braces of {{x}} removes inner",
        "keys": "lllds}",
        "initial": "{{hello}}",
    },
    "ds_paren_no_match": {
        "description": "ds) when no parens around cursor — noop",
        "keys": "ds)",
        "initial": "hello world",
    },
    "ds_bracket_no_match": {
        "description": "ds] when no brackets around cursor — noop",
        "keys": "ds]",
        "initial": "hello world",
    },
    "ds_open_angle_trim": {
        "description": "ds< deletes angle brackets and trims inner space",
        "keys": "ds<",
        "initial": "< hello >",
    },
    "ds_paren_multiword": {
        "description": "ds) on parens around multiple words",
        "keys": "ds)",
        "initial": "(one two three)",
    },
    "ds_bracket_in_context": {
        "description": "ds] with text before and after",
        "keys": "fhds]",
        "initial": "before [hello] after",
    },
    "ds_brace_in_context": {
        "description": "ds} with text before and after",
        "keys": "fhds}",
        "initial": "before {hello} after",
    },
    "ds_angle_in_context": {
        "description": "ds> with text before and after",
        "keys": "fhds>",
        "initial": "before <hello> after",
    },
    "ds_nested_diff_outer_paren": {
        "description": "ds) with quotes inside — removes parens only",
        "keys": "fhds)",
        "initial": "(\"hello\")",
    },
    "ds_nested_diff_inner_quote": {
        "description": "ds\" with parens outside — removes quotes only",
        "keys": "fhds\"",
        "initial": "(\"hello\")",
    },
    "ds_on_second_line": {
        "description": "ds\" on second line of buffer",
        "keys": "jfhds\"",
        "initial": "line one\n\"hello world\"\nline three",
    },
    "ds_open_paren_multiword": {
        "description": "ds( trims inner space with multiple words",
        "keys": "ds(",
        "initial": "( one two three )",
    },
    "ds_open_bracket_multiword": {
        "description": "ds[ trims inner space with multiple words",
        "keys": "ds[",
        "initial": "[ one two three ]",
    },
    "ds_open_brace_multiword": {
        "description": "ds{ trims inner space with multiple words",
        "keys": "ds{",
        "initial": "{ one two three }",
    },
    "ds_open_angle_multiword": {
        "description": "ds< trims inner space from angles",
        "keys": "ds<",
        "initial": "< one two three >",
    },
    "ds_with_numbers_inside": {
        "description": "ds\" with numbers inside quotes",
        "keys": "ds\"",
        "initial": "\"12345\"",
    },
    "ds_empty_parens": {
        "description": "ds) on empty parens ()",
        "keys": "ds)",
        "initial": "()",
    },
    "ds_multiline_paren": {
        "description": "ds) when parens span lines",
        "keys": "fhds)",
        "initial": "(hello\nworld)",
    },
    "ds_multiline_bracket": {
        "description": "ds] when brackets span lines",
        "keys": "fhds]",
        "initial": "[line one\nline two]",
    },
    "ds_multiline_brace": {
        "description": "ds} when braces span lines",
        "keys": "fhds}",
        "initial": "{line one\nline two}",
    },
    # ==========================================================
    # 03. cs — CHANGE SURROUNDING
    # ==========================================================

    "cs_double_to_single": {
        "description": "cs\"' changes double to single quotes",
        "keys": "cs\"'",
        "initial": "\"hello\"",
    },
    "cs_single_to_double": {
        "description": "cs'\" changes single to double quotes",
        "keys": "cs'\"",
        "initial": "'hello'",
    },
    "cs_double_to_backtick": {
        "description": "cs\"` changes double quotes to backticks",
        "keys": "cs\"`",
        "initial": "\"hello\"",
    },
    "cs_bracket_to_paren": {
        "description": "cs]) changes brackets to parens",
        "keys": "cs])",
        "initial": "[hello]",
    },
    "cs_paren_to_bracket": {
        "description": "cs)[  changes parens to brackets (open = add space)",
        "keys": "cs)[",
        "initial": "(hello)",
    },
    "cs_paren_to_brace_close": {
        "description": "cs)} changes parens to braces (close = no space)",
        "keys": "cs)}",
        "initial": "(hello)",
    },
    "cs_brace_to_paren": {
        "description": "cs}) changes braces to parens",
        "keys": "cs})",
        "initial": "{hello}",
    },
    "cs_bracket_to_angle": {
        "description": "cs]> changes brackets to angle brackets",
        "keys": "cs]>",
        "initial": "[hello]",
    },
    "cs_close_to_open_paren": {
        "description": "cs)( adds space inside parens",
        "keys": "cs)(",
        "initial": "(hello)",
    },
    "cs_close_to_open_brace": {
        "description": "cs){ adds space inside braces",
        "keys": "cs){",
        "initial": "(hello)",
    },
    "cs_open_paren_trims_space": {
        "description": "cs(} trims inner space and changes to braces",
        "keys": "cs(}",
        "initial": "( hello )",
    },
    "cs_open_bracket_trims_space": {
        "description": "cs[) trims inner space and changes to parens",
        "keys": "cs[)",
        "initial": "[ hello ]",
    },
    "cs_in_context": {
        "description": "cs\"' with text around the quotes",
        "keys": "fhcs\"'",
        "initial": "say \"hello\" now",
    },
    "cs_paren_in_context": {
        "description": "cs)] with text around the parens",
        "keys": "fhcs)]",
        "initial": "call(hello) end",
    },
    "cs_then_ds": {
        "description": "Change surrounding then delete them",
        "keys": "cs\"'ds'",
        "initial": "\"hello\" world",
    },
    "cs_quotes_in_multiline": {
        "description": "cs\"' on a line in a multiline buffer",
        "keys": "jfhcs\"'",
        "initial": "line one\n\"hello world\"\nline three",
    },
    "cs_empty_content": {
        "description": "cs\"' on empty quoted string",
        "keys": "cs\"'",
        "initial": "\"\"",
    },
    "cs_no_match_noop": {
        "description": "cs\"' when no quotes around cursor — should be no-op",
        "keys": "cs\"'",
        "initial": "hello world",
    },
    "cs_angle_to_paren": {
        "description": "cs>) changes <x> to (x)",
        "keys": "cs>)",
        "initial": "<hello>",
    },
    "cs_angle_to_bracket": {
        "description": "cs>] changes <x> to [x]",
        "keys": "cs>]",
        "initial": "<hello>",
    },
    "cs_angle_to_quote": {
        "description": "cs>\" changes <x> to \"x\"",
        "keys": "cs>\"",
        "initial": "<hello>",
    },
    "cs_paren_to_angle": {
        "description": "cs)> changes (x) to <x>",
        "keys": "cs)>",
        "initial": "(hello)",
    },
    "cs_paren_no_match": {
        "description": "cs)] when no parens — noop",
        "keys": "cs)]",
        "initial": "hello world",
    },
    "cs_quote_to_paren": {
        "description": "cs\") changes quotes to parens",
        "keys": "cs\")",
        "initial": "\"hello\"",
    },
    "cs_quote_to_bracket": {
        "description": "cs\"] changes quotes to brackets",
        "keys": "cs\"]",
        "initial": "\"hello\"",
    },
    "cs_quote_to_brace": {
        "description": "cs\"} changes quotes to braces",
        "keys": "cs\"}",
        "initial": "\"hello\"",
    },
    "cs_quote_to_angle": {
        "description": "cs\"> changes quotes to angle brackets",
        "keys": "cs\">",
        "initial": "\"hello\"",
    },
    "cs_paren_to_quote": {
        "description": "cs)\" changes parens to double quotes",
        "keys": "cs)\"",
        "initial": "(hello)",
    },
    "cs_bracket_to_quote": {
        "description": "cs]\" changes brackets to double quotes",
        "keys": "cs]\"",
        "initial": "[hello]",
    },
    "cs_brace_to_quote": {
        "description": "cs}\" changes braces to double quotes",
        "keys": "cs}\"",
        "initial": "{hello}",
    },
    "cs_paren_to_single_quote": {
        "description": "cs)' changes parens to single quotes",
        "keys": "cs)'",
        "initial": "(hello)",
    },
    "cs_bracket_to_backtick": {
        "description": "cs]` changes brackets to backticks",
        "keys": "cs]`",
        "initial": "[hello]",
    },
    "cs_backtick_to_quote": {
        "description": "cs`\" changes backticks to double quotes",
        "keys": "cs`\"",
        "initial": "`hello`",
    },
    "cs_backtick_to_single_quote": {
        "description": "cs`' changes backticks to single quotes",
        "keys": "cs`'",
        "initial": "`hello`",
    },
    "cs_alias_b_to_bracket": {
        "description": "csb] uses b alias for ) as target",
        "keys": "csb]",
        "initial": "(hello)",
    },
    "cs_alias_r_to_paren": {
        "description": "csr) uses r alias for ] as target",
        "keys": "csr)",
        "initial": "[hello]",
    },
    "cs_alias_B_to_paren": {
        "description": "csB) uses B alias for } as target",
        "keys": "csB)",
        "initial": "{hello}",
    },
    "cs_alias_a_to_paren": {
        "description": "csa) uses a alias for > as target",
        "keys": "csa)",
        "initial": "<hello>",
    },
    "cs_quote_to_star": {
        "description": "cs\"* changes quotes to stars",
        "keys": "cs\"*",
        "initial": "\"hello\"",
    },
    "cs_star_to_quote": {
        "description": "cs*\" changes stars to double quotes",
        "keys": "cs*\"",
        "initial": "*hello*",
    },
    "cs_pipe_to_quote": {
        "description": "cs|\" changes pipes to double quotes",
        "keys": "cs|\"",
        "initial": "|hello|",
    },
    "cs_open_brace_trim": {
        "description": "cs{) trims inner space from braces then wraps in parens",
        "keys": "cs{)",
        "initial": "{ hello }",
    },
    "cs_open_angle_trim": {
        "description": "cs<) trims inner space from angles then wraps in parens",
        "keys": "cs<)",
        "initial": "< hello >",
    },
    "cs_angle_to_brace": {
        "description": "cs>} changes <x> to {x}",
        "keys": "cs>}",
        "initial": "<hello>",
    },
    "cs_angle_to_backtick": {
        "description": "cs>` changes <x> to `x`",
        "keys": "cs>`",
        "initial": "<hello>",
    },
    "cs_angle_to_squote": {
        "description": "cs>' changes <x> to 'x'",
        "keys": "cs>'",
        "initial": "<hello>",
    },
    "cs_brace_to_bracket": {
        "description": "cs}] changes {x} to [x]",
        "keys": "cs}]",
        "initial": "{hello}",
    },
    "cs_brace_to_angle": {
        "description": "cs}> changes {x} to <x>",
        "keys": "cs}>",
        "initial": "{hello}",
    },
    "cs_brace_to_backtick": {
        "description": "cs}` changes {x} to `x`",
        "keys": "cs}`",
        "initial": "{hello}",
    },
    "cs_brace_to_squote": {
        "description": "cs}' changes {x} to 'x'",
        "keys": "cs}'",
        "initial": "{hello}",
    },
    "cs_bracket_to_brace": {
        "description": "cs]} changes [x] to {x}",
        "keys": "cs]}",
        "initial": "[hello]",
    },
    "cs_bracket_to_squote": {
        "description": "cs]' changes [x] to 'x'",
        "keys": "cs]'",
        "initial": "[hello]",
    },
    "cs_paren_to_backtick": {
        "description": "cs)` changes (x) to `x`",
        "keys": "cs)`",
        "initial": "(hello)",
    },
    "cs_squote_to_backtick": {
        "description": "cs'` changes 'x' to `x`",
        "keys": "cs'`",
        "initial": "'hello'",
    },
    "cs_squote_to_paren": {
        "description": "cs') changes 'x' to (x)",
        "keys": "cs')",
        "initial": "'hello'",
    },
    "cs_squote_to_bracket": {
        "description": "cs'] changes 'x' to [x]",
        "keys": "cs']",
        "initial": "'hello'",
    },
    "cs_squote_to_brace": {
        "description": "cs'} changes 'x' to {x}",
        "keys": "cs'}",
        "initial": "'hello'",
    },
    "cs_squote_to_angle": {
        "description": "cs'> changes 'x' to <x>",
        "keys": "cs'>",
        "initial": "'hello'",
    },
    "cs_backtick_to_paren": {
        "description": "cs`) changes `x` to (x)",
        "keys": "cs`)",
        "initial": "`hello`",
    },
    "cs_backtick_to_bracket": {
        "description": "cs`] changes `x` to [x]",
        "keys": "cs`]",
        "initial": "`hello`",
    },
    "cs_backtick_to_brace": {
        "description": "cs`} changes `x` to {x}",
        "keys": "cs`}",
        "initial": "`hello`",
    },
    "cs_backtick_to_angle": {
        "description": "cs`> changes `x` to <x>",
        "keys": "cs`>",
        "initial": "`hello`",
    },
    "cs_open_paren_to_bracket": {
        "description": "cs(] trims space and changes to brackets",
        "keys": "cs(]",
        "initial": "( hello )",
    },
    "cs_open_paren_to_dquote": {
        "description": "cs(\" trims space and changes to quotes",
        "keys": "cs(\"",
        "initial": "( hello )",
    },
    "cs_open_bracket_to_dquote": {
        "description": "cs[\" trims space and changes to quotes",
        "keys": "cs[\"",
        "initial": "[ hello ]",
    },
    "cs_open_bracket_to_brace": {
        "description": "cs[} trims space and changes to braces",
        "keys": "cs[}",
        "initial": "[ hello ]",
    },
    "cs_open_brace_to_bracket": {
        "description": "cs{] trims space and changes to brackets",
        "keys": "cs{]",
        "initial": "{ hello }",
    },
    "cs_open_brace_to_dquote": {
        "description": "cs{\" trims space and changes to quotes",
        "keys": "cs{\"",
        "initial": "{ hello }",
    },
    "cs_open_angle_to_bracket": {
        "description": "cs<] trims space and changes to brackets",
        "keys": "cs<]",
        "initial": "< hello >",
    },
    "cs_open_angle_to_dquote": {
        "description": "cs<\" trims space and changes to quotes",
        "keys": "cs<\"",
        "initial": "< hello >",
    },
    "cs_dquote_to_open_paren": {
        "description": "cs\"( adds space inside parens",
        "keys": "cs\"(",
        "initial": "\"hello\"",
    },
    "cs_dquote_to_open_bracket": {
        "description": "cs\"[ adds space inside brackets",
        "keys": "cs\"[",
        "initial": "\"hello\"",
    },
    "cs_dquote_to_open_brace": {
        "description": "cs\"{ adds space inside braces",
        "keys": "cs\"{",
        "initial": "\"hello\"",
    },
    "cs_dquote_to_open_angle": {
        "description": "cs\"< adds space inside angle brackets",
        "keys": "cs\"<",
        "initial": "\"hello\"",
    },
    "cs_paren_to_open_angle": {
        "description": "cs)< changes parens to angles with space",
        "keys": "cs)<",
        "initial": "(hello)",
    },
    "cs_bracket_to_open_paren": {
        "description": "cs]( changes brackets to parens with space",
        "keys": "cs](",
        "initial": "[hello]",
    },
    "cs_bracket_to_open_brace": {
        "description": "cs]{ changes brackets to braces with space",
        "keys": "cs]{",
        "initial": "[hello]",
    },
    "cs_brace_to_open_paren": {
        "description": "cs}( changes braces to parens with space",
        "keys": "cs}(",
        "initial": "{hello}",
    },
    "cs_brace_to_open_bracket": {
        "description": "cs}[ changes braces to brackets with space",
        "keys": "cs}[",
        "initial": "{hello}",
    },
    "cs_dquote_to_b": {
        "description": "cs\"b changes to parens (b alias)",
        "keys": "cs\"b",
        "initial": "\"hello\"",
    },
    "cs_dquote_to_B": {
        "description": "cs\"B changes to braces (B alias)",
        "keys": "cs\"B",
        "initial": "\"hello\"",
    },
    "cs_dquote_to_r": {
        "description": "cs\"r changes to brackets (r alias)",
        "keys": "cs\"r",
        "initial": "\"hello\"",
    },
    "cs_dquote_to_a": {
        "description": "cs\"a changes to angle brackets (a alias)",
        "keys": "cs\"a",
        "initial": "\"hello\"",
    },
    "cs_then_cs": {
        "description": "cs\"' then cs') — double change",
        "keys": "cs\"'cs')",
        "initial": "\"hello\"",
    },
    "cs_with_spaces_inside": {
        "description": "cs\"' preserves inner spaces",
        "keys": "cs\"'",
        "initial": "\"  hello  \"",
    },
    "cs_empty_brackets": {
        "description": "cs]\" on empty brackets []",
        "keys": "cs]\"",
        "initial": "[]",
    },
    "cs_dquote_to_pipe": {
        "description": "cs\"| changes quotes to pipes",
        "keys": "cs\"|",
        "initial": "\"hello\"",
    },
    "cs_dquote_to_underscore": {
        "description": "cs\"_ changes quotes to underscores",
        "keys": "cs\"_",
        "initial": "\"hello\"",
    },
    "cs_star_to_paren": {
        "description": "cs*) changes stars to parens",
        "keys": "cs*)",
        "initial": "*hello*",
    },
    "cs_multiline_paren_to_bracket": {
        "description": "cs)] when parens span lines",
        "keys": "fhcs)]",
        "initial": "(hello\nworld)",
    },
    # ==========================================================
    # 04. ys — ADD SURROUNDING
    # ==========================================================

    "ys_iw_close_paren": {
        "description": "ysiw) wraps word in parens (no space)",
        "keys": "ysiw)",
        "initial": "hello world",
    },
    "ys_iw_open_paren": {
        "description": "ysiw( wraps iw in parens with inner space",
        "keys": "ysiw(",
        "initial": "hello world today",
    },
    "ys_iw_close_bracket": {
        "description": "ysiw] wraps word in brackets (no space)",
        "keys": "ysiw]",
        "initial": "hello world",
    },
    "ys_iw_open_bracket": {
        "description": "ysiw[ wraps word in brackets with space",
        "keys": "ysiw[",
        "initial": "hello world",
    },
    "ys_iw_close_brace": {
        "description": "ysiw} wraps word in braces (no space)",
        "keys": "ysiw}",
        "initial": "hello world",
    },
    "ys_iw_open_brace": {
        "description": "ysiw{ wraps word in braces with space",
        "keys": "ysiw{",
        "initial": "hello world",
    },
    "ys_iw_double_quote": {
        "description": "ysiw\" wraps word in double quotes",
        "keys": "ysiw\"",
        "initial": "hello world",
    },
    "ys_iw_single_quote": {
        "description": "ysiw' wraps word in single quotes",
        "keys": "ysiw'",
        "initial": "hello world",
    },
    "ys_iw_backtick": {
        "description": "ysiw` wraps word in backticks",
        "keys": "ysiw`",
        "initial": "hello world",
    },
    "ys_iw_angle": {
        "description": "ysiw> wraps word in angle brackets",
        "keys": "ysiw>",
        "initial": "hello world",
    },
    "ys_iw_second_word": {
        "description": "ysiw) on second word",
        "keys": "wysiw)",
        "initial": "hello world today",
    },
    "ys_iw_middle_of_word": {
        "description": "ysiw) with cursor in middle of word",
        "keys": "llysiw)",
        "initial": "hello world",
    },
    "ys_iw_pipe": {
        "description": "ysiw| wraps word in pipes",
        "keys": "ysiw|",
        "initial": "hello world",
    },
    "ys_iw_asterisk": {
        "description": "ysiw* wraps word in asterisks",
        "keys": "ysiw*",
        "initial": "hello world",
    },
    "ys_iw_underscore": {
        "description": "ysiw_ wraps word in underscores",
        "keys": "ysiw_",
        "initial": "hello world",
    },
    "ys_aw_paren": {
        "description": "ysaw) wraps a-word in parens",
        "keys": "ysaw)",
        "initial": "hello world",
    },
    "ys_iW_brace": {
        "description": "ysiW} wraps WORD in braces",
        "keys": "ysiW}",
        "initial": "foo-bar baz",
    },
    "ys_dollar_quote": {
        "description": "ys$\" wraps to end of line in quotes",
        "keys": "ys$\"",
        "initial": "hello world",
    },
    "ys_w_paren": {
        "description": "ysw) wraps from cursor to next word boundary",
        "keys": "ysw)",
        "initial": "hello world today",
    },
    "ys_e_paren": {
        "description": "yse) wraps to end of word",
        "keys": "yse)",
        "initial": "hello world today",
    },
    "ys_f_char_paren": {
        "description": "ysf.) wraps up to and including the period",
        "keys": "ysf.)",
        "initial": "hello. world",
    },
    "yss_paren": {
        "description": "yss) wraps entire line in parens (strips leading whitespace)",
        "keys": "yss)",
        "initial": "hello world",
    },
    "yss_bracket": {
        "description": "yss] wraps entire line in brackets",
        "keys": "yss]",
        "initial": "hello world",
    },
    "yss_brace": {
        "description": "yss} wraps entire line in braces",
        "keys": "yss}",
        "initial": "hello world",
    },
    "yss_quote": {
        "description": "yss\" wraps entire line in double quotes",
        "keys": "yss\"",
        "initial": "hello world",
    },
    "yss_with_indent": {
        "description": "yss) on indented line preserves indent",
        "keys": "yss)",
        "initial": "    hello world",
    },
    "ys_then_cs": {
        "description": "Add surrounding then change them",
        "keys": "ysiw)cs)]",
        "initial": "hello world",
    },
    "ys_then_ds": {
        "description": "Add surrounding then delete them",
        "keys": "ysiw)ds)",
        "initial": "hello world",
    },
    "ys_iw_in_multiline": {
        "description": "ysiw) on a specific word in multiline buffer",
        "keys": "jwysiw)",
        "initial": "line one\nhello world\nline three",
    },
    "ys_single_char_word": {
        "description": "ysiw) on a single-character word",
        "keys": "ysiw)",
        "initial": "a b c",
    },
    "yss_empty_line": {
        "description": "yss) on empty line",
        "keys": "yss)",
        "initial": "",
    },
    "yss_single_word": {
        "description": "yss) on single word line",
        "keys": "yss)",
        "initial": "hello",
    },
    "ys_2w_paren": {
        "description": "ys2w) surrounds two words",
        "keys": "ys2w)",
        "initial": "one two three four",
    },
    "ys_3w_bracket": {
        "description": "ys3w] surrounds three words",
        "keys": "ys3w]",
        "initial": "alpha beta gamma delta",
    },
    "ys_2e_brace": {
        "description": "ys2e} surrounds to end of second word",
        "keys": "ys2e}",
        "initial": "foo bar baz qux",
    },
    "ys_2w_quote": {
        "description": "ys2w\" surrounds two words in quotes",
        "keys": "ys2w\"",
        "initial": "hello world today",
    },
    "yss_whitespace_only": {
        "description": "yss) on line with only spaces",
        "keys": "yss)",
        "initial": "    ",
    },
    "ys_iw_b_alias": {
        "description": "ysiwb wraps in parens (b = paren alias)",
        "keys": "ysiwb",
        "initial": "hello world",
    },
    "ys_iw_B_alias": {
        "description": "ysiwB wraps in braces (B = brace alias)",
        "keys": "ysiwB",
        "initial": "hello world",
    },
    "ys_iw_r_alias": {
        "description": "ysiwr wraps in brackets (r = bracket alias)",
        "keys": "ysiwr",
        "initial": "hello world",
    },
    "ys_iw_a_alias": {
        "description": "ysiwa wraps in angle brackets (a = angle alias)",
        "keys": "ysiwa",
        "initial": "hello world",
    },
    "ys_aW_brace": {
        "description": "ysaW} wraps a WORD in braces",
        "keys": "ysaW}",
        "initial": "foo-bar baz",
    },
    "ys_t_char_paren": {
        "description": "yst.) wraps to just before the period",
        "keys": "yst.)",
        "initial": "hello. world",
    },
    "ys_iw_open_angle": {
        "description": "ysiw< wraps inner word in angle brackets with space",
        "keys": "ysiw<",
        "initial": "hello world",
    },
    "ys_w_last_word": {
        "description": "ysw\" on last word of line stays on that line",
        "keys": "2wysw\"",
        "initial": "one two three\nfour five six",
    },
    "ys_2w_last_word_eol": {
        "description": "ys2w\" when only 1 word remains wraps just that word",
        "keys": "2wys2w\"",
        "initial": "one two three\nfour five six",
    },
    "ys_2w_two_words_eol": {
        "description": "ys2w\" when exactly 2 words remain wraps both",
        "keys": "2wys2w\"",
        "initial": "one two three four\nfive six seven",
    },
    "ys_3w_crosses_eol": {
        "description": "ys3w) when only 2 words remain wraps both",
        "keys": "wys3w)",
        "initial": "alpha beta gamma\ndelta epsilon",
    },
    "ys_W_last_WORD_eol": {
        "description": "ysW\" on last WORD of line stays on that line",
        "keys": "2wysW\"",
        "initial": "one two three\nfour five six",
    },
    "ys_W_brace": {
        "description": "ysW} wraps WORD in braces",
        "keys": "ysW}",
        "initial": "foo-bar baz-qux end",
    },
    "ys_W_bracket": {
        "description": "ysW] wraps WORD in brackets",
        "keys": "ysW]",
        "initial": "hello world today",
    },
    "ys_W_quote": {
        "description": "ysW\" wraps WORD in quotes",
        "keys": "ysW\"",
        "initial": "foo-bar baz",
    },
    "ys_E_paren": {
        "description": "ysE) wraps to end of WORD",
        "keys": "ysE)",
        "initial": "foo-bar baz",
    },
    "ys_E_quote": {
        "description": "ysE\" wraps to end of WORD in quotes",
        "keys": "ysE\"",
        "initial": "hello world",
    },
    "ys_0_paren": {
        "description": "ys0) from second word wraps to col 0",
        "keys": "wys0)",
        "initial": "hello world today",
    },
    "ys_0_quote": {
        "description": "ys0\" from second word wraps to col 0",
        "keys": "wys0\"",
        "initial": "hello world today",
    },
    "ys_caret_paren": {
        "description": "ys^) from end wraps to first non-blank",
        "keys": "$ys^)",
        "initial": "  hello world",
    },
    "ys_caret_bracket": {
        "description": "ys^] wraps to first non-blank in brackets",
        "keys": "$ys^]",
        "initial": "   abc def",
    },
    "ys_f_bracket": {
        "description": "ysfd] wraps from cursor to 'd' (inclusive)",
        "keys": "ysfd]",
        "initial": "abcdef ghij",
    },
    "ys_F_paren": {
        "description": "ysFa) backward to 'a'",
        "keys": "$ysFg)",
        "initial": "abcdefghij",
    },
    "ys_t_bracket": {
        "description": "yst.] wraps up to (not including) period",
        "keys": "yst.]",
        "initial": "hello. world",
    },
    "ys_T_paren": {
        "description": "ysTa) backward to just after 'a'",
        "keys": "$ysTa)",
        "initial": "abcdefghij",
    },
    "ys_4w_paren": {
        "description": "ys4w) wraps four words",
        "keys": "ys4w)",
        "initial": "aa bb cc dd ee ff",
    },
    "ys_2W_paren": {
        "description": "ys2W) wraps two WORDs",
        "keys": "ys2W)",
        "initial": "foo-bar baz-qux end-fin",
    },
    "ys_3e_bracket": {
        "description": "ys3e] wraps three word-ends",
        "keys": "ys3e]",
        "initial": "aa bb cc dd ee",
    },
    "ys_2E_brace": {
        "description": "ys2E} wraps to end of second WORD",
        "keys": "ys2E}",
        "initial": "foo-bar baz-qux end",
    },
    "ys_percent_quote": {
        "description": "ys%\" from opening paren to matching close",
        "keys": "ys%\"",
        "initial": "(hello world) end",
    },
    "ys_i_paren_bracket": {
        "description": "ysi)] wraps inner-paren content in brackets",
        "keys": "fysi)]",
        "initial": "(hello world) end",
    },
    "ys_a_paren_bracket": {
        "description": "ysa)] wraps whole paren group in brackets",
        "keys": "fysa)]",
        "initial": "(hello world) end",
    },
    "ys_i_bracket_paren": {
        "description": "ysi]) wraps inner-bracket content in parens",
        "keys": "fysi])",
        "initial": "[hello world] end",
    },
    "ys_a_bracket_brace": {
        "description": "ysa]} wraps whole bracket group in braces",
        "keys": "fysa]}",
        "initial": "[hello world] end",
    },
    "ys_i_brace_paren": {
        "description": "ysi}) wraps inner-brace content in parens",
        "keys": "fysi})",
        "initial": "{hello world} end",
    },
    "ys_a_brace_bracket": {
        "description": "ysa}] wraps whole brace group in brackets",
        "keys": "fysa}]",
        "initial": "{hello world} end",
    },
    "ys_i_dquote_paren": {
        "description": "ysi\") wraps inner-quote content in parens",
        "keys": "fysi\")",
        "initial": "\"hello world\" end",
    },
    "ys_a_dquote_bracket": {
        "description": "ysa\"] wraps whole quoted string in brackets",
        "keys": "fysa\"]",
        "initial": "\"hello world\" end",
    },
    "ys_i_squote_paren": {
        "description": "ysi') wraps inner single-quoted text in parens",
        "keys": "fysi')",
        "initial": "'hello world' end",
    },
    "ys_a_squote_bracket": {
        "description": "ysa'] wraps whole single-quoted text in brackets",
        "keys": "fysa']",
        "initial": "'hello world' end",
    },
    "ys_i_backtick_paren": {
        "description": "ysi`) wraps inner backtick text in parens",
        "keys": "fysi`)",
        "initial": "`hello world` end",
    },
    "ys_a_backtick_bracket": {
        "description": "ysa`] wraps whole backtick text in brackets",
        "keys": "fysa`]",
        "initial": "`hello world` end",
    },
    "ys_i_angle_paren": {
        "description": "ysi>) wraps inner-angle content in parens",
        "keys": "fysi>)",
        "initial": "<hello world> end",
    },
    "ys_a_angle_bracket": {
        "description": "ysa>] wraps whole angle group in brackets",
        "keys": "fysa>]",
        "initial": "<hello world> end",
    },
    "ys_iW_paren": {
        "description": "ysiW) wraps inner WORD in parens",
        "keys": "ysiW)",
        "initial": "foo-bar baz",
    },
    "ys_aW_bracket": {
        "description": "ysaW] wraps a WORD (includes trailing space) in brackets",
        "keys": "ysaW]",
        "initial": "foo-bar baz end",
    },
    "ys_w_open_paren": {
        "description": "ysw( wraps word in parens with inner space",
        "keys": "ysw(",
        "initial": "hello world today",
    },
    "ys_w_open_bracket": {
        "description": "ysw[ wraps word in brackets with inner space",
        "keys": "ysw[",
        "initial": "hello world today",
    },
    "ys_w_open_brace": {
        "description": "ysw{ wraps word in braces with inner space",
        "keys": "ysw{",
        "initial": "hello world today",
    },
    "ys_w_open_angle": {
        "description": "ysw< wraps word in angles with inner space",
        "keys": "ysw<",
        "initial": "hello world today",
    },
    "ys_e_open_bracket": {
        "description": "yse[ wraps to end-of-word in brackets with space",
        "keys": "yse[",
        "initial": "hello world today",
    },
    "ys_dollar_open_brace": {
        "description": "ys${ wraps to EOL in braces with space",
        "keys": "ys${",
        "initial": "hello world",
    },
    "yss_open_paren": {
        "description": "yss( wraps line in parens with inner space",
        "keys": "yss(",
        "initial": "hello world",
    },
    "yss_open_bracket": {
        "description": "yss[ wraps line in brackets with inner space",
        "keys": "yss[",
        "initial": "hello world",
    },
    "yss_open_brace": {
        "description": "yss{ wraps line in braces with inner space",
        "keys": "yss{",
        "initial": "hello world",
    },
    "yss_open_angle": {
        "description": "yss< wraps line in angles with inner space",
        "keys": "yss<",
        "initial": "hello world",
    },
    "ys_e_at_eol": {
        "description": "yse\" on last word of line",
        "keys": "2wyse\"",
        "initial": "one two three\nfour five six",
    },
    "ys_E_at_eol": {
        "description": "ysE\" on last WORD of line",
        "keys": "2wysE\"",
        "initial": "one two three\nfour five six",
    },
    "ys_2e_at_eol": {
        "description": "ys2e) when 1 word left on line",
        "keys": "2wys2e)",
        "initial": "one two three\nfour five six",
    },
    "ys_w_single_word_line": {
        "description": "ysw\" on a single-word line",
        "keys": "ysw\"",
        "initial": "hello\nworld",
    },
    "ys_2w_single_word_line": {
        "description": "ys2w\" on single-word line wraps just that word",
        "keys": "ys2w\"",
        "initial": "hello\nworld",
    },
    "ys_iw_last_word_line": {
        "description": "ysiw) on last word of line",
        "keys": "$bysiw)",
        "initial": "hello world today",
    },
    "ys_iw_second_line": {
        "description": "ysiw\" on word in second line",
        "keys": "jwysiw\"",
        "initial": "line one\nhello world\nline three",
    },
    "ys_e_last_word_mid": {
        "description": "yse) on last word of line",
        "keys": "$byse)",
        "initial": "hello world today",
    },
    "ys_dollar_mid_line": {
        "description": "ys$) from middle of line",
        "keys": "wys$)",
        "initial": "hello world today",
    },
    "yss_angle": {
        "description": "yss> wraps line in angle brackets",
        "keys": "yss>",
        "initial": "hello world",
    },
    "yss_single_quote": {
        "description": "yss' wraps line in single quotes",
        "keys": "yss'",
        "initial": "hello world",
    },
    "yss_backtick": {
        "description": "yss` wraps line in backticks",
        "keys": "yss`",
        "initial": "hello world",
    },
    "yss_pipe": {
        "description": "yss| wraps line in pipes",
        "keys": "yss|",
        "initial": "hello world",
    },
    "yss_star": {
        "description": "yss* wraps line in asterisks",
        "keys": "yss*",
        "initial": "hello world",
    },
    "yss_on_second_line": {
        "description": "yss) on second line",
        "keys": "jyss)",
        "initial": "first line\nhello world\nthird line",
    },
    "yss_cursor_mid_line": {
        "description": "yss) with cursor mid-line (wraps whole line)",
        "keys": "wyss)",
        "initial": "hello world today",
    },
    "yss_deep_indent": {
        "description": "yss) on deeply indented line",
        "keys": "yss)",
        "initial": "        hello world",
    },
    "yss_tab_indent": {
        "description": "yss) on tab-indented line",
        "keys": "yss)",
        "initial": "\thello world",
    },
    "ys_w_b_alias": {
        "description": "yswb wraps in parens (b alias)",
        "keys": "yswb",
        "initial": "hello world today",
    },
    "ys_w_B_alias": {
        "description": "yswB wraps in braces (B alias)",
        "keys": "yswB",
        "initial": "hello world today",
    },
    "ys_w_r_alias": {
        "description": "yswr wraps in brackets (r alias)",
        "keys": "yswr",
        "initial": "hello world today",
    },
    "ys_w_a_alias": {
        "description": "yswa wraps in angles (a alias)",
        "keys": "yswa",
        "initial": "hello world today",
    },
    "ys_iw_on_number": {
        "description": "ysiw) on a numeric word",
        "keys": "wysiw)",
        "initial": "abc 123 def",
    },
    "ys_iw_near_punctuation": {
        "description": "ysiw) on word next to comma",
        "keys": "ysiw)",
        "initial": "hello, world",
    },
    "ys_iw_single_word_file": {
        "description": "ysiw) on the only word in the file",
        "keys": "ysiw)",
        "initial": "hello",
    },
    "ys_dollar_single_word": {
        "description": "ys$\" on single word wraps whole line",
        "keys": "ys$\"",
        "initial": "hello",
    },
    "yss_single_char": {
        "description": "yss) on single-character content",
        "keys": "yss)",
        "initial": "x",
    },
    "ys_iw_after_tab": {
        "description": "ysiw) on word after tab character",
        "keys": "wysiw)",
        "initial": "\thello world",
    },
    # ==========================================================
    # 05. VISUAL S / VISUAL LINE S
    # ==========================================================

    "visual_S_paren": {
        "description": "Visual select then S) wraps in parens",
        "keys": "viwS)",
        "initial": "hello world",
    },
    "visual_S_bracket": {
        "description": "Visual select then S] wraps in brackets",
        "keys": "viwS]",
        "initial": "hello world",
    },
    "visual_S_brace": {
        "description": "Visual select then S} wraps in braces",
        "keys": "viwS}",
        "initial": "hello world",
    },
    "visual_S_double_quote": {
        "description": "Visual select then S\" wraps in double quotes",
        "keys": "viwS\"",
        "initial": "hello world",
    },
    "visual_S_single_quote": {
        "description": "Visual select then S' wraps in single quotes",
        "keys": "viwS'",
        "initial": "hello world",
    },
    "visual_S_backtick": {
        "description": "Visual select then S` wraps in backticks",
        "keys": "viwS`",
        "initial": "hello world",
    },
    "visual_S_angle": {
        "description": "Visual select then S> wraps in angle brackets",
        "keys": "viwS>",
        "initial": "hello world",
    },
    "visual_S_partial_word": {
        "description": "Visual select partial text then S)",
        "keys": "vllS)",
        "initial": "hello world",
    },
    "visual_S_multiple_words": {
        "description": "Visual select multiple words then S\"",
        "keys": "v2wS\"",
        "initial": "one two three four",
    },
    "visual_S_open_paren_space": {
        "description": "Visual S( adds space inside parens",
        "keys": "viwS(",
        "initial": "hello world",
    },
    "visual_S_pipe": {
        "description": "Visual S| wraps in pipes",
        "keys": "viwS|",
        "initial": "hello world",
    },
    "visual_line_S_paren": {
        "description": "Visual line then S) wraps line in parens",
        "keys": "VS)",
        "initial": "hello world",
    },
    "visual_S_in_multiline": {
        "description": "Visual S\" on word in multiline buffer",
        "keys": "jwviwS\"",
        "initial": "line one\nhello world\nline three",
    },
    "visual_S_single_char": {
        "description": "v selects one char, S) wraps just that char",
        "keys": "vS)",
        "initial": "abcdef",
    },
    "visual_S_single_char_mid": {
        "description": "v on middle char, S\" wraps just one char",
        "keys": "llvS\"",
        "initial": "abcdef",
    },
    "visual_S_star": {
        "description": "viwS* wraps in stars",
        "keys": "viwS*",
        "initial": "hello world",
    },
    "visual_S_underscore": {
        "description": "viwS_ wraps in underscores",
        "keys": "viwS_",
        "initial": "hello world",
    },
    "visual_linewise_S_quote": {
        "description": "VS\" wraps line in quotes (linewise)",
        "keys": "VS\"",
        "initial": "hello world",
    },
    "visual_linewise_S_bracket": {
        "description": "VS] wraps line in brackets (linewise)",
        "keys": "VS]",
        "initial": "hello world",
    },
    "vis_S_open_bracket": {
        "description": "viwS[ wraps in brackets with space",
        "keys": "viwS[",
        "initial": "hello world",
    },
    "vis_S_open_brace": {
        "description": "viwS{ wraps in braces with space",
        "keys": "viwS{",
        "initial": "hello world",
    },
    "vis_S_open_angle": {
        "description": "viwS< wraps in angles with space",
        "keys": "viwS<",
        "initial": "hello world",
    },
    "vis_S_to_eol": {
        "description": "v$S) wraps to end of line",
        "keys": "v$S)",
        "initial": "hello world today",
    },
    "vis_S_to_eow": {
        "description": "veS\" wraps to end-of-word",
        "keys": "veS\"",
        "initial": "hello world today",
    },
    "vis_S_3w": {
        "description": "v3wS) wraps 3 words",
        "keys": "v3wS)",
        "initial": "one two three four five",
    },
    "vis_S_whole_line_v_dollar": {
        "description": "v$S\" wraps full line",
        "keys": "v$S\"",
        "initial": "hello world",
    },
    "vis_S_multiline": {
        "description": "vjS) wraps across two lines",
        "keys": "vjS)",
        "initial": "hello\nworld\nend",
    },
    "vis_S_second_word": {
        "description": "wviwS) wraps second word",
        "keys": "wviwS)",
        "initial": "hello world today",
    },
    "vis_S_mid_word": {
        "description": "visual partial word from middle",
        "keys": "vllS)",
        "initial": "abcdef ghij",
    },
    "vis_S_b_alias": {
        "description": "viwSb wraps in parens (b alias)",
        "keys": "viwSb",
        "initial": "hello world",
    },
    "vis_S_B_alias": {
        "description": "viwSB wraps in braces (B alias)",
        "keys": "viwSB",
        "initial": "hello world",
    },
    "vis_S_r_alias": {
        "description": "viwSr wraps in brackets (r alias)",
        "keys": "viwSr",
        "initial": "hello world",
    },
    "vis_S_a_alias": {
        "description": "viwSa wraps in angles (a alias)",
        "keys": "viwSa",
        "initial": "hello world",
    },
    "vline_S_brace": {
        "description": "VS} wraps line in braces (linewise)",
        "keys": "VS}",
        "initial": "hello world",
    },
    "vline_S_angle": {
        "description": "VS> wraps line in angle brackets (linewise)",
        "keys": "VS>",
        "initial": "hello world",
    },
    "vline_S_squote": {
        "description": "VS' wraps line in single quotes (linewise)",
        "keys": "VS'",
        "initial": "hello world",
    },
    "vline_S_backtick": {
        "description": "VS` wraps line in backticks (linewise)",
        "keys": "VS`",
        "initial": "hello world",
    },
    "vline_S_open_paren": {
        "description": "VS( wraps line in parens with space (linewise)",
        "keys": "VS(",
        "initial": "hello world",
    },
    "vline_S_open_bracket": {
        "description": "VS[ wraps line in brackets with space (linewise)",
        "keys": "VS[",
        "initial": "hello world",
    },
    "vline_S_multiline_2": {
        "description": "Vj selects 2 lines, S) wraps",
        "keys": "VjS)",
        "initial": "line one\nline two\nline three",
    },
    "vline_S_multiline_3": {
        "description": "V2j selects 3 lines, S] wraps",
        "keys": "V2jS]",
        "initial": "aaa\nbbb\nccc\nddd",
    },
    # ==========================================================
    # 06. DOT REPEAT
    # ==========================================================

    "dot_repeat_ds": {
        "description": "ds\" then dot repeats on next occurrence",
        "keys": "ds\"j0f\"lds\"",
        "initial": "\"hello\"\n\"world\"",
    },
    "dot_repeat_ysiw": {
        "description": "ysiw) then dot on next word",
        "keys": "ysiw)w.",
        "initial": "hello world today",
    },
    "dot_repeat_cs": {
        "description": "cs\"' then dot on next occurrence",
        "keys": "cs\"'jfhcs\"'",
        "initial": "\"hello\"\n\"world\"",
    },
    "dot_after_ds_quote": {
        "description": "ds\" on first quoted string, navigate then . on second",
        "keys": "ds\"f\".",
        "initial": "\"aaa\" \"bbb\" end",
    },
    "dot_after_cs_quote": {
        "description": "cs\"' on first, navigate to second, dot repeat",
        "keys": "cs\"'f\".",
        "initial": "\"foo\" \"bar\" end",
    },
    "dot_ys_w_paren": {
        "description": "ysw) then move and dot",
        "keys": "ysw)w.",
        "initial": "aaa bbb ccc ddd",
    },
    "dot_ys_iw_bracket": {
        "description": "ysiw] then move and dot",
        "keys": "ysiw]w.",
        "initial": "aaa bbb ccc ddd",
    },
    "dot_ds_paren": {
        "description": "ds) then dot on another pair",
        "keys": "ds)w.",
        "initial": "(aaa) (bbb) ccc",
    },
    "dot_cs_bracket_paren": {
        "description": "cs]) then dot",
        "keys": "cs])w.",
        "initial": "[aaa] [bbb] ccc",
    },
    "dot_ys_e_quote": {
        "description": "yse\" then move and dot",
        "keys": "yse\"w.",
        "initial": "aaa bbb ccc ddd",
    },
    "dot_yss_paren": {
        "description": "yss) then j and dot",
        "keys": "yss)j.",
        "initial": "line one\nline two\nline three",
    },
    # ==========================================================
    # 07. UNDO / REDO
    # ==========================================================

    "undo_ds": {
        "description": "ds\" then undo restores quotes",
        "keys": "ds\"u",
        "initial": "\"hello\"",
    },
    "undo_cs": {
        "description": "cs\"' then undo restores original",
        "keys": "cs\"'u",
        "initial": "\"hello\"",
    },
    "undo_ys": {
        "description": "ysiw) then undo removes parens",
        "keys": "ysiw)u",
        "initial": "hello world",
    },
    "undo_visual_S": {
        "description": "visual S) then undo",
        "keys": "viwS)u",
        "initial": "hello world",
    },
    "undo_ys_w": {
        "description": "ysw) then u — restores original",
        "keys": "ysw)u",
        "initial": "hello world today",
    },
    "undo_yss": {
        "description": "yss) then u — restores line",
        "keys": "yss)u",
        "initial": "hello world",
    },
    "undo_ds_bracket": {
        "description": "ds] then u — restores brackets",
        "keys": "ds]u",
        "initial": "[hello]",
    },
    "undo_cs_bracket": {
        "description": "cs]) then u — restores brackets",
        "keys": "cs])u",
        "initial": "[hello]",
    },
    "redo_ds_quote": {
        "description": "ds\" then u then Ctrl-R",
        "keys": "ds\"u",
        "initial": "\"hello\"",
    },
    "redo_ys_iw": {
        "description": "ysiw) then u then Ctrl-R",
        "keys": "ysiw)u",
        "initial": "hello world",
    },
    "undo_two_ops": {
        "description": "ysiw) then cs)] then u twice restores original",
        "keys": "ysiw)cs)]uu",
        "initial": "hello world",
    },
    # ==========================================================
    # 08. CURSOR POSITION
    # ==========================================================

    "cursor_after_ds_quote": {
        "description": "Cursor position after ds\" with context",
        "keys": "fwds\"",
        "initial": "say \"hello\" end",
    },
    "cursor_after_cs_quote": {
        "description": "Cursor position after cs\"'",
        "keys": "fhcs\"'",
        "initial": "say \"hello\" end",
    },
    # ==========================================================
    # 09. MULTI-OP SEQUENCES
    # ==========================================================

    "nested_ds": {
        "description": "ds) on nested parens: inner first, then outer",
        "keys": "fhds)0fhds)",
        "initial": "((hello))",
    },
    "multi_ys_ys_two_words": {
        "description": "ysiw) then wysiw] — surround two different words",
        "keys": "ysiw)wysiw]",
        "initial": "foo bar baz",
    },
    "multi_ys_cs_ds": {
        "description": "ysiw) then cs)] then ds] — add, change, delete",
        "keys": "ysiw)cs)]ds]",
        "initial": "hello world",
    },
    "multi_ds_ds_nested": {
        "description": "ds) twice on doubly-wrapped word",
        "keys": "llds)ds)",
        "initial": "((word))",
    },
    "double_wrap_ys_ys": {
        "description": "ysiw) then ysiw] — double wrap",
        "keys": "ysiw)ysiw]",
        "initial": "hello world",
    },
    "triple_wrap": {
        "description": "ysiw) then ysiw] then ysiw\" — triple wrap",
        "keys": "ysiw)ysiw]ysiw\"",
        "initial": "hello world",
    },
    "wrap_then_delete_inner": {
        "description": "ysiw) then ysiw] then ds) deletes inner pair",
        "keys": "ysiw)lysiw]ds)",
        "initial": "hello world",
    },

    # ==========================================================
    # 10. CROSS-SUITE (moved from edge_cases / matchparen)
    # ==========================================================

    "dot_after_ysiw_paren_w": {
        "description": "ysiw) on first word, w. on next — dot repeats surround",
        "keys": "ysiw)w.",
        "initial": "alpha beta gamma",
    },
    "dot_after_ysiw_bracket_w": {
        "description": "ysiw] then w. — repeats bracket surround",
        "keys": "ysiw]w.",
        "initial": "one two three",
    },
    "dot_after_ys_dollar_quote": {
        "description": "ys$\" wraps to EOL in quotes, j0. repeats on next line",
        "keys": "ys$\"j0.",
        "initial": "first line\nsecond line",
    },
    "mp_after_ysiw_paren": {
        "description": "After ysiw), cursor on ( — both brackets highlighted",
        "keys": "ysiw)",
        "initial": "hello world",
    },
}
