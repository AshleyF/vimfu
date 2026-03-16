"""Extra bracket commands: ]M [M"""

CASES = {
    # ── ]M — go to next end of method (next }) ──
    "bracket_M_next_method_end": {
        "keys": "]M",
        "initial": "void foo() {\n  x = 1;\n}\nvoid bar() {\n  y = 2;\n}\n",
    },
    # ── [M — go to previous end of method (previous }) ──
    "bracket_M_prev_method_end": {
        "keys": "G[M",
        "initial": "void foo() {\n  x = 1;\n}\nvoid bar() {\n  y = 2;\n}\n",
    },
}
