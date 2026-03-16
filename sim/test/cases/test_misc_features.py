"""Misc features: [p ]p, U, special registers, g Ctrl-A, [' ]'"""

CASES = {
    # [p — put above with indent adjustment (linewise paste matches context indent)
    "bracket_p_put_above_indented": {
        "keys": "jyyGkk[p",
        "initial": "  if true\n    hello\n    world\n  end\n",
    },
    
    # ]p — put below with indent adjustment
    "bracket_p_put_below_indented": {
        "keys": "jyy]p",
        "initial": "  if true\n    hello\n    world\n  end\n",
    },
    
    # U — undo all changes on current line
    "undo_line": {
        "keys": "Ahello\x1bIworld \x1bU",
        "initial": "test\n",
    },
    
    # Special register ". — last inserted text
    "reg_dot_last_insert": {
        "keys": "ihello \x1b\".p",
        "initial": "world\n",
    },
    
    # Special register ": — last ex command (no :set number to avoid gutter)
    "reg_colon_last_command": {
        "keys": ":echo 'hi'\r\":p",
        "initial": "test\n",
    },

    # g Ctrl-A — sequential increment in visual block
    "g_ctrl_a_visual_block": {
        "keys": "\x16jjjg\x01",
        "initial": "0\n0\n0\n0\n",
    },
    
    # g Ctrl-A in visual mode (line)
    "g_ctrl_a_visual_line": {
        "keys": "Vjjjg\x01",
        "initial": "0\n0\n0\n0\n",
    },
    
    # [' — go to previous mark (lowercase)
    "bracket_tick_prev_mark": {
        "keys": "mambjj['",
        "initial": "line 1\nline 2\nline 3\nline 4\n",
    },
    
    # ]' — go to next mark  
    "bracket_tick_next_mark": {
        "keys": "jjmajjmb]'",
        "initial": "line 1\nline 2\nline 3\nline 4\nline 5\n",
    },
    
    # [m — go to previous method start ({)
    "bracket_m_prev_method": {
        "keys": "G[m",
        "initial": "void foo() {\n  x = 1;\n}\nvoid bar() {\n  y = 2;\n}\n",
    },
    
    # ]m — go to next method start ({)
    "bracket_m_next_method": {
        "keys": "]m",
        "initial": "void foo() {\n  x = 1;\n}\nvoid bar() {\n  y = 2;\n}\n",
    },
}
