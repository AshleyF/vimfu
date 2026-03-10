"""
Tmux screen test cases for ground-truth comparison.

Each case defines a sequence of steps to execute against real tmux (via ShellPilot)
AND the equivalent keystrokes to replay through the sim's SessionManager.

Steps sent to real tmux:
  - ("line", text)        — send text + Enter
  - ("keys", text)        — send raw keys (e.g. Ctrl-B = \\x02)
  - ("wait", pattern)     — wait for pattern on screen
  - ("sleep", seconds)    — sleep for stability
  - ("write_file", name, content)  — create a file in WSL before starting tmux

Sim replay: each case also has "sim_keys" — a list of (method, *args) calls
on SessionManager. These are used by the JS comparator to replay the same
scenario through the simulator.

Layout / content comparisons:
  - Text on each row must match (after normalizing the prompt/hostname difference)
  - Cursor position must match
  - Color runs must match (border colors, status bar, pane content)

Status bar time/date is frozen in both captures for determinism.
"""

# ── Ctrl-B as a constant ──
CTRL_B = "\x02"  # tmux prefix key

# ── Tmux launch preamble (shared by all cases) ──
# Kill any existing sessions, launch tmux with a clean bash shell
# that uses PS1='$ ' to match the simulator's prompt exactly.
# We create a tiny bashrc that sets PS1 and use it for all panes.
# We also use -f /dev/null to skip the user's tmux.conf.
_SETUP_BASHRC = "printf 'export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\\nPS1=\"\\$ \"\\n' > /tmp/vimfu_test_bashrc"
_BASH_CMD = "bash --rcfile /tmp/vimfu_test_bashrc --noprofile"
_TEST_DIR = "/tmp/vimfu_test_workdir"
_TMUX_LAUNCH = [
    # Create a minimal bashrc that sets the sim-matching prompt
    ("line", _SETUP_BASHRC),
    ("sleep", 0.3),
    # Create and clean a temp working directory (avoids swap file leftovers)
    ("line", f"rm -rf {_TEST_DIR}; mkdir -p {_TEST_DIR}; cd {_TEST_DIR}"),
    ("sleep", 0.3),
    # Kill any existing tmux (with a delay for socket cleanup), then launch
    ("line", "tmux kill-server 2>/dev/null; sleep 0.5"),
    ("sleep", 0.8),
    ("line", f"cd {_TEST_DIR} && SHELL=/bin/bash tmux new-session -s test '{_BASH_CMD}'"),
    ("wait", "[test]", 15.0),
    ("sleep", 0.8),
    # Set default-command so splits/new-panes also get our controlled shell
    ("keys", CTRL_B + ":"),
    ("sleep", 0.2),
    ("line", f"set-option default-command '{_BASH_CMD}'"),
    ("sleep", 0.2),
    # cd into our clean working directory inside tmux, then clear
    ("line", f"cd {_TEST_DIR} && clear"),
    ("sleep", 0.3),
    # Marker: write_files will be injected here by the ground-truth generator
    ("__inject_write_files__",),
]

def _tmux(*extra_steps):
    """Build a step list: launch tmux + extra steps."""
    return list(_TMUX_LAUNCH) + list(extra_steps)


CASES = {
    # ─────────────────────────────────────────────────────
    # Basic tmux launch
    # ─────────────────────────────────────────────────────

    "tmux_fresh_launch": {
        "description": "Fresh tmux launch — single pane with shell, green status bar",
        "steps": _tmux(),
        "sim_keys": ["tmux", "Enter"],
    },

    "tmux_type_in_shell": {
        "description": "Tmux pane after running echo hello",
        "steps": _tmux(
            ("line", "echo hello"),
            ("wait", "hello"),
            ("sleep", 0.3),
        ),
        "sim_keys": ["tmux", "Enter", "echo hello", "Enter"],
    },

    # ─────────────────────────────────────────────────────
    # Vertical split
    # ─────────────────────────────────────────────────────

    "tmux_vsplit": {
        "description": "Vertical split — two panes side by side with border",
        "steps": _tmux(
            ("keys", CTRL_B + "%"),
            ("sleep", 0.5),
        ),
        "sim_keys": ["tmux", "Enter", "Ctrl-B", "%"],
    },

    "tmux_vsplit_type_both": {
        "description": "Vertical split with typed text in both panes",
        "steps": _tmux(
            ("line", "echo LEFT"),
            ("sleep", 0.3),
            ("keys", CTRL_B + "%"),
            ("sleep", 0.5),
            ("line", "echo RIGHT"),
            ("sleep", 0.3),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "echo LEFT", "Enter",
            "Ctrl-B", "%",
            "echo RIGHT", "Enter",
        ],
    },

    # ─────────────────────────────────────────────────────
    # Horizontal split
    # ─────────────────────────────────────────────────────

    "tmux_hsplit": {
        "description": "Horizontal split — two panes stacked with border",
        "steps": _tmux(
            ("keys", CTRL_B + '"'),
            ("sleep", 0.5),
        ),
        "sim_keys": ["tmux", "Enter", "Ctrl-B", '"'],
    },

    "tmux_hsplit_type_both": {
        "description": "Horizontal split with typed text in both panes",
        "steps": _tmux(
            ("line", "echo TOP"),
            ("sleep", 0.3),
            ("keys", CTRL_B + '"'),
            ("sleep", 0.5),
            ("line", "echo BOTTOM"),
            ("sleep", 0.3),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "echo TOP", "Enter",
            "Ctrl-B", '"',
            "echo BOTTOM", "Enter",
        ],
    },

    # ─────────────────────────────────────────────────────
    # Three panes
    # ─────────────────────────────────────────────────────

    "tmux_three_panes": {
        "description": "Three panes: vsplit then hsplit the right pane",
        "steps": _tmux(
            ("keys", CTRL_B + "%"),
            ("sleep", 0.5),
            ("keys", CTRL_B + '"'),
            ("sleep", 0.5),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "Ctrl-B", "%",
            "Ctrl-B", '"',
        ],
    },

    # ─────────────────────────────────────────────────────
    # Pane navigation
    # ─────────────────────────────────────────────────────

    "tmux_navigate_left": {
        "description": "Vsplit then navigate to left pane — border colors change",
        "steps": _tmux(
            ("line", "echo PANE0"),
            ("sleep", 0.3),
            ("keys", CTRL_B + "%"),
            ("sleep", 0.5),
            ("line", "echo PANE1"),
            ("sleep", 0.3),
            ("keys", CTRL_B + "\x1b[D"),  # Ctrl-B then Left arrow
            ("sleep", 0.3),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "echo PANE0", "Enter",
            "Ctrl-B", "%",
            "echo PANE1", "Enter",
            "Ctrl-B", "ArrowLeft",
        ],
    },

    "tmux_navigate_cycle_o": {
        "description": "Cycle panes with Ctrl-B o twice",
        "steps": _tmux(
            ("keys", CTRL_B + "%"),
            ("sleep", 0.5),
            ("keys", CTRL_B + "o"),
            ("sleep", 0.3),
            ("keys", CTRL_B + "o"),
            ("sleep", 0.3),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "Ctrl-B", "%",
            "Ctrl-B", "o",
            "Ctrl-B", "o",
        ],
    },

    # ─────────────────────────────────────────────────────
    # Status bar variations
    # ─────────────────────────────────────────────────────

    "tmux_status_bar_two_windows": {
        "description": "Status bar showing two windows",
        "steps": _tmux(
            ("keys", CTRL_B + "c"),
            ("sleep", 0.5),
        ),
        "sim_keys": ["tmux", "Enter", "Ctrl-B", "c"],
    },

    "tmux_status_bar_renamed": {
        "description": "Status bar after renaming a window",
        "steps": _tmux(
            ("keys", CTRL_B + ","),
            ("sleep", 0.3),
            ("keys", "\x15"),  # Ctrl-U to clear
            ("sleep", 0.1),
            ("keys", "myterm\r"),
            ("sleep", 0.5),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "Ctrl-B", ",",
            "Ctrl-U",
            "myterm", "Enter",
        ],
    },

    "tmux_status_bar_zoomed": {
        "description": "Status bar with zoom indicator (*Z)",
        "steps": _tmux(
            ("keys", CTRL_B + "%"),
            ("sleep", 0.5),
            ("keys", CTRL_B + "z"),
            ("sleep", 0.3),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "Ctrl-B", "%",
            "Ctrl-B", "z",
        ],
    },

    # ─────────────────────────────────────────────────────
    # Overlays
    # ─────────────────────────────────────────────────────

    "tmux_command_prompt_empty": {
        "description": "Command prompt overlay (empty)",
        "steps": _tmux(
            ("keys", CTRL_B + ":"),
            ("sleep", 0.3),
        ),
        "sim_keys": ["tmux", "Enter", "Ctrl-B", ":"],
    },

    "tmux_command_prompt_typed": {
        "description": "Command prompt with some text typed",
        "steps": _tmux(
            ("keys", CTRL_B + ":"),
            ("sleep", 0.3),
            ("keys", "split-w"),
            ("sleep", 0.2),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "Ctrl-B", ":",
            "split-w",
        ],
    },

    "tmux_copy_mode": {
        "description": "Copy mode indicator on status bar",
        "steps": _tmux(
            ("keys", CTRL_B + "["),
            ("sleep", 0.5),
        ),
        "sim_keys": ["tmux", "Enter", "Ctrl-B", "["],
    },

    # ─────────────────────────────────────────────────────
    # Vim inside tmux
    # ─────────────────────────────────────────────────────

    "tmux_vim_launch": {
        "description": "Vim launched inside a tmux pane (new file)",
        "steps": _tmux(
            ("line", "vim test.txt"),
            ("sleep", 1.0),
            ("wait", "~"),
        ),
        "sim_keys": ["tmux", "Enter", "vim test.txt", "Enter"],
    },

    "tmux_vim_with_content": {
        "description": "Vim with existing file content inside tmux",
        "steps": _tmux(
            ("line", "printf 'Hello World\\nSecond line\\nThird line' > hello.txt"),
            ("sleep", 0.3),
            ("line", "vim hello.txt"),
            ("sleep", 1.0),
            ("wait", "Hello"),
        ),
        "sim_keys": [
            {"write": ("hello.txt", "Hello World\nSecond line\nThird line")},
            "tmux", "Enter",
            "vim hello.txt", "Enter",
        ],
    },

    "tmux_vim_insert_and_quit": {
        "description": "Vim: enter insert, type text, :wq — back to shell prompt",
        "steps": _tmux(
            ("line", "vim test.txt"),
            ("sleep", 1.0),
            ("wait", "~"),
            ("keys", "ityped in tmux"),
            ("sleep", 0.3),
            ("keys", "\x1b:wq\r"),  # Escape :wq Enter
            ("sleep", 0.5),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "vim test.txt", "Enter",
            "i", "typed in tmux", "Escape",
            ":", "w", "q", "Enter",
        ],
    },

    # ─────────────────────────────────────────────────────
    # Vim + shell split
    # ─────────────────────────────────────────────────────

    "tmux_vim_and_shell_split": {
        "description": "Vim in left pane, shell in right pane",
        "steps": _tmux(
            ("line", "printf 'line 1\\nline 2\\nline 3' > code.txt"),
            ("sleep", 0.3),
            ("line", "vim code.txt"),
            ("sleep", 1.0),
            ("wait", "line 1"),
            ("keys", CTRL_B + "%"),
            ("sleep", 0.5),
        ),
        "sim_keys": [
            {"write": ("code.txt", "line 1\nline 2\nline 3")},
            "tmux", "Enter",
            "vim code.txt", "Enter",
            "Ctrl-B", "%",
        ],
    },

    # ─────────────────────────────────────────────────────
    # Pane exit / close
    # ─────────────────────────────────────────────────────

    "tmux_exit_one_vsplit_pane": {
        "description": "Exit right pane in vsplit — left pane fills space",
        "steps": _tmux(
            ("line", "echo LEFT"),
            ("sleep", 0.3),
            ("keys", CTRL_B + "%"),
            ("sleep", 0.5),
            ("line", "exit"),
            ("sleep", 0.5),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "echo LEFT", "Enter",
            "Ctrl-B", "%",
            "exit", "Enter",
        ],
    },

    "tmux_exit_last_pane_detaches": {
        "description": "Exit the last pane — tmux session ends, back to outer shell",
        "steps": _tmux(
            ("line", "exit"),
            ("sleep", 1.0),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "exit", "Enter",
        ],
    },

    # ─────────────────────────────────────────────────────
    # Border colors (active vs inactive)
    # ─────────────────────────────────────────────────────

    "tmux_vsplit_active_right": {
        "description": "Vsplit with right pane active — check border colors",
        "steps": _tmux(
            ("keys", CTRL_B + "%"),
            ("sleep", 0.5),
        ),
        "sim_keys": ["tmux", "Enter", "Ctrl-B", "%"],
    },

    "tmux_vsplit_active_left": {
        "description": "Vsplit with left pane active — check border colors",
        "steps": _tmux(
            ("keys", CTRL_B + "%"),
            ("sleep", 0.5),
            ("keys", CTRL_B + "\x1b[D"),  # Left arrow
            ("sleep", 0.3),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "Ctrl-B", "%",
            "Ctrl-B", "ArrowLeft",
        ],
    },

    # ─────────────────────────────────────────────────────
    # Detach / reattach
    # ─────────────────────────────────────────────────────

    "tmux_detach_shell": {
        "description": "Detach from tmux — back to outer shell",
        "steps": _tmux(
            ("keys", CTRL_B + "d"),
            ("sleep", 0.5),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "Ctrl-B", "d",
        ],
    },

    "tmux_reattach": {
        "description": "Detach and reattach — tmux state preserved",
        "steps": _tmux(
            ("line", "echo BEFORE_DETACH"),
            ("sleep", 0.3),
            ("keys", CTRL_B + "d"),
            ("sleep", 0.5),
            ("wait", "detached"),
            ("line", "tmux attach -t test"),
            ("sleep", 1.0),
            ("wait", "BEFORE_DETACH"),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "echo BEFORE_DETACH", "Enter",
            "Ctrl-B", "d",
            "tmux attach", "Enter",
        ],
    },

    # ─────────────────────────────────────────────────────
    # Exit + re-launch (regression: second tmux must work)
    # ─────────────────────────────────────────────────────

    "tmux_exit_and_relaunch": {
        "description": "Exit tmux (last pane), then launch tmux again — second session must be fully functional",
        "steps": _tmux(
            # Use first tmux session: type something, then exit
            ("line", "echo FIRST_SESSION"),
            ("sleep", 0.3),
            ("line", "exit"),
            ("sleep", 1.0),
            # Now we're back at the outer shell — relaunch tmux fresh
            ("line", f"SHELL=/bin/bash tmux new-session -s test '{_BASH_CMD}'"),
            ("wait", "[test]", 15.0),
            ("sleep", 0.8),
            # Set default-command for new session too
            ("keys", CTRL_B + ":"),
            ("sleep", 0.2),
            ("line", f"set-option default-command '{_BASH_CMD}'"),
            ("sleep", 0.2),
            # cd into our clean working directory and clear
            ("line", f"cd {_TEST_DIR} && clear"),
            ("sleep", 0.3),
            # Type something to prove it works
            ("line", "echo RELAUNCH_OK"),
            ("wait", "RELAUNCH_OK"),
            ("sleep", 0.3),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "echo FIRST_SESSION", "Enter",
            "exit", "Enter",
            "tmux", "Enter",
            "echo RELAUNCH_OK", "Enter",
        ],
    },

    # ═════════════════════════════════════════════════════════
    #  INTEGRATION TESTS
    #  Complex multi-step scenarios exercising interactions
    #  between tmux, vim, shell, and the virtual filesystem.
    # ═════════════════════════════════════════════════════════

    # ─────────────────────────────────────────────────────
    # Vim file lifecycle inside tmux
    # ─────────────────────────────────────────────────────

    "int_vim_write_cat": {
        "description": "Vim: write file then cat it — VFS round-trip",
        "steps": _tmux(
            ("line", "vim test.txt"),
            ("sleep", 1.5),
            ("keys", "iHello World\x1b"),       # i, type, Escape
            ("sleep", 0.3),
            ("keys", ":wq\n"),
            ("sleep", 0.5),
            ("wait", "$"),
            ("line", "cat test.txt"),
            ("sleep", 0.5),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "vim test.txt", "Enter",
            "i", "Hello World", "Escape",
            ":", "w", "q", "Enter",
            "cat test.txt", "Enter",
        ],
    },

    "int_vim_reopen": {
        "description": "Vim: write, quit, reopen — content persisted in VFS",
        "steps": _tmux(
            ("line", "vim test.txt"),
            ("sleep", 1.5),
            ("keys", "iSaved text\x1b"),
            ("sleep", 0.3),
            ("keys", ":wq\n"),
            ("sleep", 0.5),
            ("wait", "$"),
            ("line", "vim test.txt"),
            ("sleep", 1.5),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "vim test.txt", "Enter",
            "i", "Saved text", "Escape",
            ":", "w", "q", "Enter",
            "vim test.txt", "Enter",
        ],
    },

    "int_vim_quit_nosave_reopen": {
        "description": "Vim: edit, :q! (no save), reopen — original content preserved",
        "steps": _tmux(
            ("line", "vim test.txt"),
            ("sleep", 1.5),
            ("keys", "iChanged text\x1b"),
            ("sleep", 0.3),
            ("keys", ":q!\n"),
            ("sleep", 0.5),
            ("wait", "$"),
            ("line", "vim test.txt"),
            ("sleep", 1.5),
        ),
        "write_files": {"test.txt": "Original"},
        "sim_keys": [
            {"write": ["test.txt", "Original"]},
            "tmux", "Enter",
            "vim test.txt", "Enter",
            "i", "Changed text", "Escape",
            ":", "q", "!", "Enter",
            "vim test.txt", "Enter",
        ],
    },

    "int_vim_edit_save_edit_save": {
        "description": "Vim: two edit-save cycles on same file",
        "steps": _tmux(
            ("line", "vim test.txt"),
            ("sleep", 1.5),
            ("keys", "iFirst\x1b"),
            ("sleep", 0.3),
            ("keys", ":wq\n"),
            ("sleep", 0.5),
            ("wait", "$"),
            ("line", "vim test.txt"),
            ("sleep", 1.5),
            ("keys", "oSecond\x1b"),
            ("sleep", 0.3),
            ("keys", ":wq\n"),
            ("sleep", 0.5),
            ("wait", "$"),
            ("line", "cat test.txt"),
            ("sleep", 0.5),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "vim test.txt", "Enter",
            "i", "First", "Escape",
            ":", "w", "q", "Enter",
            "vim test.txt", "Enter",
            "o", "Second", "Escape",
            ":", "w", "q", "Enter",
            "cat test.txt", "Enter",
        ],
    },

    "int_vim_open_echoed_file": {
        "description": "Shell echo > file, then vim it — VFS bridging",
        "steps": _tmux(
            ("line", "echo Hello from shell > greet.txt"),
            ("sleep", 0.3),
            ("line", "vim greet.txt"),
            ("sleep", 1.5),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "echo Hello from shell > greet.txt", "Enter",
            "vim greet.txt", "Enter",
        ],
    },

    # ─────────────────────────────────────────────────────
    # Vim editing operations inside tmux
    # ─────────────────────────────────────────────────────

    "int_vim_insert_escape_append": {
        "description": "Vim: i→type→Esc→A→type→Esc — insert then append",
        "steps": _tmux(
            ("line", "vim test.txt"),
            ("sleep", 1.5),
            ("keys", "iHello\x1b"),
            ("sleep", 0.2),
            ("keys", "A World\x1b"),
            ("sleep", 0.3),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "vim test.txt", "Enter",
            "i", "Hello", "Escape",
            "A", " World", "Escape",
        ],
    },

    "int_vim_open_below": {
        "description": "Vim: o to open line below and type",
        "steps": _tmux(
            ("line", "vim test.txt"),
            ("sleep", 1.5),
            ("keys", "iLine one\x1b"),
            ("sleep", 0.2),
            ("keys", "oLine two\x1b"),
            ("sleep", 0.3),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "vim test.txt", "Enter",
            "i", "Line one", "Escape",
            "o", "Line two", "Escape",
        ],
    },

    "int_vim_open_above": {
        "description": "Vim: O to open line above and type",
        "steps": _tmux(
            ("line", "vim test.txt"),
            ("sleep", 1.5),
            ("keys", "iLine two\x1b"),
            ("sleep", 0.2),
            ("keys", "OLine one\x1b"),
            ("sleep", 0.3),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "vim test.txt", "Enter",
            "i", "Line two", "Escape",
            "O", "Line one", "Escape",
        ],
    },

    "int_vim_dd_p": {
        "description": "Vim: dd (delete line) then p (paste below)",
        "steps": _tmux(
            ("line", "vim test.txt"),
            ("sleep", 1.5),
            ("keys", "gg"),
            ("sleep", 0.2),
            ("keys", "ddp"),
            ("sleep", 0.3),
        ),
        "write_files": {"test.txt": "First\nSecond\nThird"},
        "sim_keys": [
            {"write": ["test.txt", "First\nSecond\nThird"]},
            "tmux", "Enter",
            "vim test.txt", "Enter",
            "d", "d", "p",
        ],
    },

    "int_vim_yy_p": {
        "description": "Vim: yy (yank line) then p (paste below)",
        "steps": _tmux(
            ("line", "vim test.txt"),
            ("sleep", 1.5),
            ("keys", "gg"),
            ("sleep", 0.2),
            ("keys", "yyp"),
            ("sleep", 0.3),
        ),
        "write_files": {"test.txt": "Alpha\nBravo"},
        "sim_keys": [
            {"write": ["test.txt", "Alpha\nBravo"]},
            "tmux", "Enter",
            "vim test.txt", "Enter",
            "y", "y", "p",
        ],
    },

    "int_vim_undo": {
        "description": "Vim: dd then u (undo) — restore deleted line",
        "steps": _tmux(
            ("line", "vim test.txt"),
            ("sleep", 1.5),
            ("keys", "gg"),
            ("sleep", 0.2),
            ("keys", "ddu"),
            ("sleep", 0.3),
        ),
        "write_files": {"test.txt": "Keep me\nAnd me"},
        "sim_keys": [
            {"write": ["test.txt", "Keep me\nAnd me"]},
            "tmux", "Enter",
            "vim test.txt", "Enter",
            "d", "d", "u",
        ],
    },

    "int_vim_x_delete_chars": {
        "description": "Vim: x to delete characters at cursor",
        "steps": _tmux(
            ("line", "vim test.txt"),
            ("sleep", 1.5),
            ("keys", "gg"),
            ("sleep", 0.2),
            ("keys", "xxx"),
            ("sleep", 0.3),
        ),
        "write_files": {"test.txt": "ABCDE"},
        "sim_keys": [
            {"write": ["test.txt", "ABCDE"]},
            "tmux", "Enter",
            "vim test.txt", "Enter",
            "x", "x", "x",
        ],
    },

    "int_vim_w_motion": {
        "description": "Vim: w (word forward) then i (insert at new position)",
        "steps": _tmux(
            ("line", "vim test.txt"),
            ("sleep", 1.5),
            ("keys", "gg"),
            ("sleep", 0.2),
            ("keys", "wi_INSERTED_\x1b"),
            ("sleep", 0.3),
        ),
        "write_files": {"test.txt": "hello world end"},
        "sim_keys": [
            {"write": ["test.txt", "hello world end"]},
            "tmux", "Enter",
            "vim test.txt", "Enter",
            "w", "i", "_INSERTED_", "Escape",
        ],
    },

    "int_vim_G_gg": {
        "description": "Vim: G (go to end) then gg (go to top)",
        "steps": _tmux(
            ("line", "vim test.txt"),
            ("sleep", 1.5),
            ("keys", "G"),
            ("sleep", 0.2),
            ("keys", "gg"),
            ("sleep", 0.3),
        ),
        "write_files": {"test.txt": "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"},
        "sim_keys": [
            {"write": ["test.txt", "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"]},
            "tmux", "Enter",
            "vim test.txt", "Enter",
            "G",
            "g", "g",
        ],
    },

    "int_vim_dollar_caret": {
        "description": "Vim: $ (end of line) then ^ (first non-blank)",
        "steps": _tmux(
            ("line", "vim test.txt"),
            ("sleep", 1.5),
            ("keys", "gg"),
            ("sleep", 0.2),
            ("keys", "$"),
            ("sleep", 0.2),
            ("keys", "^"),
            ("sleep", 0.3),
        ),
        "write_files": {"test.txt": "  indented text here"},
        "sim_keys": [
            {"write": ["test.txt", "  indented text here"]},
            "tmux", "Enter",
            "vim test.txt", "Enter",
            "$",
            "^",
        ],
    },

    # ─────────────────────────────────────────────────────
    # Tmux split panes + vim
    # ─────────────────────────────────────────────────────

    "int_vsplit_vim_left": {
        "description": "Vsplit: vim in left pane, shell prompt in right",
        "steps": _tmux(
            ("keys", CTRL_B + "%"),
            ("sleep", 0.5),
            ("keys", CTRL_B + "\x1b[D"),  # Left arrow
            ("sleep", 0.3),
            ("line", "vim test.txt"),
            ("sleep", 1.5),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "Ctrl-B", "%",
            "Ctrl-B", "ArrowLeft",
            "vim test.txt", "Enter",
        ],
    },

    "int_vsplit_vim_both": {
        "description": "Vsplit: vim in both panes (different files)",
        "steps": _tmux(
            ("line", "vim left.txt"),
            ("sleep", 1.5),
            ("keys", CTRL_B + "%"),
            ("sleep", 0.5),
            ("line", "vim right.txt"),
            ("sleep", 1.5),
        ),
        "write_files": {
            "left.txt": "LEFT PANE",
            "right.txt": "RIGHT PANE",
        },
        "sim_keys": [
            {"write": ["left.txt", "LEFT PANE"]},
            {"write": ["right.txt", "RIGHT PANE"]},
            "tmux", "Enter",
            "vim left.txt", "Enter",
            "Ctrl-B", "%",
            "vim right.txt", "Enter",
        ],
    },

    "int_hsplit_vim_bottom": {
        "description": "Hsplit: shell on top, vim on bottom",
        "steps": _tmux(
            ("line", "echo TOP PANE"),
            ("sleep", 0.3),
            ("keys", CTRL_B + '"'),
            ("sleep", 0.5),
            ("line", "vim test.txt"),
            ("sleep", 1.5),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "echo TOP PANE", "Enter",
            "Ctrl-B", '"',
            "vim test.txt", "Enter",
        ],
    },

    "int_split_exit_vim": {
        "description": "Vsplit: vim in right pane, :q, back to shell in that pane",
        "steps": _tmux(
            ("keys", CTRL_B + "%"),
            ("sleep", 0.5),
            ("line", "vim test.txt"),
            ("sleep", 1.5),
            ("keys", ":q\n"),
            ("sleep", 0.5),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "Ctrl-B", "%",
            "vim test.txt", "Enter",
            ":", "q", "Enter",
        ],
    },

    "int_split_vim_echo": {
        "description": "Vsplit: vim left, echo output right — mixed content",
        "steps": _tmux(
            ("line", "vim test.txt"),
            ("sleep", 1.5),
            ("keys", "iLEFT VIM\x1b"),
            ("sleep", 0.5),
            ("keys", CTRL_B + "%"),
            ("sleep", 0.5),
            ("line", "echo RIGHT SHELL"),
            ("sleep", 0.3),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "vim test.txt", "Enter",
            "i", "LEFT VIM", "Escape",
            "Ctrl-B", "%",
            "echo RIGHT SHELL", "Enter",
        ],
    },

    "int_three_panes_vim_center": {
        "description": "Three vertical panes: shell | vim | shell",
        "steps": _tmux(
            ("line", "echo PANE_0"),
            ("sleep", 0.3),
            ("keys", CTRL_B + "%"),
            ("sleep", 0.5),
            ("line", "vim center.txt"),
            ("sleep", 1.5),
            ("keys", "iCENTER\x1b"),
            ("sleep", 0.5),
            ("keys", CTRL_B + "%"),
            ("sleep", 0.5),
            ("line", "echo PANE_2"),
            ("sleep", 0.3),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "echo PANE_0", "Enter",
            "Ctrl-B", "%",
            "vim center.txt", "Enter",
            "i", "CENTER", "Escape",
            "Ctrl-B", "%",
            "echo PANE_2", "Enter",
        ],
    },

    # ─────────────────────────────────────────────────────
    # Tmux navigation + content verification
    # ─────────────────────────────────────────────────────

    "int_navigate_type_navigate": {
        "description": "Vsplit: type right, navigate left, type, navigate back — right content preserved",
        "steps": _tmux(
            ("line", "echo LEFT"),
            ("sleep", 0.3),
            ("keys", CTRL_B + "%"),
            ("sleep", 0.5),
            ("line", "echo RIGHT"),
            ("sleep", 0.3),
            ("keys", CTRL_B + "\x1b[D"),  # Left arrow
            ("sleep", 0.3),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "echo LEFT", "Enter",
            "Ctrl-B", "%",
            "echo RIGHT", "Enter",
            "Ctrl-B", "ArrowLeft",
        ],
    },

    "int_hsplit_navigate_up": {
        "description": "Hsplit: type bottom, navigate up — top pane active",
        "steps": _tmux(
            ("line", "echo TOP"),
            ("sleep", 0.3),
            ("keys", CTRL_B + '"'),
            ("sleep", 0.5),
            ("line", "echo BOTTOM"),
            ("sleep", 0.3),
            ("keys", CTRL_B + "\x1b[A"),  # Up arrow
            ("sleep", 0.3),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "echo TOP", "Enter",
            "Ctrl-B", '"',
            "echo BOTTOM", "Enter",
            "Ctrl-B", "ArrowUp",
        ],
    },

    "int_last_pane_semicolon": {
        "description": "Vsplit: navigate using ; (last active pane toggle)",
        "steps": _tmux(
            ("line", "echo LEFT"),
            ("sleep", 0.3),
            ("keys", CTRL_B + "%"),
            ("sleep", 0.5),
            ("line", "echo RIGHT"),
            ("sleep", 0.3),
            ("keys", CTRL_B + ";"),
            ("sleep", 0.3),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "echo LEFT", "Enter",
            "Ctrl-B", "%",
            "echo RIGHT", "Enter",
            "Ctrl-B", ";",
        ],
    },

    # ─────────────────────────────────────────────────────
    # Tmux window management + content
    # ─────────────────────────────────────────────────────

    "int_two_windows_echo": {
        "description": "Two windows: echo in each, verify window 1 visible",
        "steps": _tmux(
            ("line", "echo WINDOW_ZERO"),
            ("sleep", 0.3),
            ("keys", CTRL_B + "c"),
            ("sleep", 0.5),
            ("line", "echo WINDOW_ONE"),
            ("sleep", 0.3),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "echo WINDOW_ZERO", "Enter",
            "Ctrl-B", "c",
            "echo WINDOW_ONE", "Enter",
        ],
    },

    "int_window_switch_back": {
        "description": "Two windows: switch back to window 0, content preserved",
        "steps": _tmux(
            ("line", "echo WINDOW_ZERO"),
            ("sleep", 0.3),
            ("keys", CTRL_B + "c"),
            ("sleep", 0.5),
            ("line", "echo WINDOW_ONE"),
            ("sleep", 0.3),
            ("keys", CTRL_B + "p"),
            ("sleep", 0.3),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "echo WINDOW_ZERO", "Enter",
            "Ctrl-B", "c",
            "echo WINDOW_ONE", "Enter",
            "Ctrl-B", "p",
        ],
    },

    "int_three_windows": {
        "description": "Three windows: status bar shows all three",
        "steps": _tmux(
            ("keys", CTRL_B + "c"),
            ("sleep", 0.5),
            ("keys", CTRL_B + "c"),
            ("sleep", 0.5),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "Ctrl-B", "c",
            "Ctrl-B", "c",
        ],
    },

    "int_window_select_number": {
        "description": "Three windows: select window 0 by number",
        "steps": _tmux(
            ("keys", CTRL_B + "c"),
            ("sleep", 0.5),
            ("keys", CTRL_B + "c"),
            ("sleep", 0.5),
            ("line", "echo IN_WIN2"),
            ("sleep", 0.3),
            ("keys", CTRL_B + "0"),
            ("sleep", 0.3),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "Ctrl-B", "c",
            "Ctrl-B", "c",
            "echo IN_WIN2", "Enter",
            "Ctrl-B", "0",
        ],
    },

    "int_window_last_active": {
        "description": "Toggle last window with Ctrl-B l",
        "steps": _tmux(
            ("line", "echo WIN0"),
            ("sleep", 0.3),
            ("keys", CTRL_B + "c"),
            ("sleep", 0.5),
            ("line", "echo WIN1"),
            ("sleep", 0.3),
            ("keys", CTRL_B + "l"),
            ("sleep", 0.3),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "echo WIN0", "Enter",
            "Ctrl-B", "c",
            "echo WIN1", "Enter",
            "Ctrl-B", "l",
        ],
    },

    "int_window_rename_verify": {
        "description": "Rename window and verify status bar",
        "steps": _tmux(
            ("keys", CTRL_B + ","),
            ("sleep", 0.3),
            ("keys", "\x15"),  # Ctrl-U clear
            ("sleep", 0.1),
            ("line", "mywin"),
            ("sleep", 0.3),
            ("line", "echo RENAMED"),
            ("sleep", 0.3),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "Ctrl-B", ",",
            "Ctrl-U",
            "mywin", "Enter",
            "echo RENAMED", "Enter",
        ],
    },

    # ─────────────────────────────────────────────────────
    # Window tree (Ctrl-B w) — tree-style chooser
    # ─────────────────────────────────────────────────────

    "int_window_tree_single": {
        "description": "Ctrl-B w with 1 window: tree with session + 1 window",
        "steps": _tmux(
            ("keys", CTRL_B + "w"),
            ("sleep", 1.0),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "Ctrl-B", "w",
        ],
    },

    "int_window_tree_three": {
        "description": "Ctrl-B w with 3 windows: full tree visible",
        "steps": _tmux(
            ("keys", CTRL_B + "c"),
            ("sleep", 0.5),
            ("keys", CTRL_B + "c"),
            ("sleep", 0.5),
            ("keys", CTRL_B + "0"),
            ("sleep", 0.3),
            ("keys", CTRL_B + "w"),
            ("sleep", 1.0),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "Ctrl-B", "c",
            "Ctrl-B", "c",
            "Ctrl-B", "0",
            "Ctrl-B", "w",
        ],
    },

    "int_window_tree_navigate_down": {
        "description": "Ctrl-B w with 3 windows, arrow down moves highlight",
        "steps": _tmux(
            ("keys", CTRL_B + "c"),
            ("sleep", 0.5),
            ("keys", CTRL_B + "c"),
            ("sleep", 0.5),
            ("keys", CTRL_B + "0"),
            ("sleep", 0.3),
            ("keys", CTRL_B + "w"),
            ("sleep", 1.0),
            ("keys", "\x1b[B"),  # Arrow Down
            ("sleep", 0.5),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "Ctrl-B", "c",
            "Ctrl-B", "c",
            "Ctrl-B", "0",
            "Ctrl-B", "w",
            "ArrowDown",
        ],
    },

    "int_window_tree_select": {
        "description": "Ctrl-B w: navigate to window 2 and Enter to switch",
        "steps": _tmux(
            ("keys", CTRL_B + "c"),
            ("sleep", 0.5),
            ("keys", CTRL_B + "c"),
            ("sleep", 0.5),
            ("keys", CTRL_B + "0"),
            ("sleep", 0.3),
            ("keys", CTRL_B + "w"),
            ("sleep", 1.0),
            ("keys", "\x1b[B"),  # Down
            ("sleep", 0.3),
            ("keys", "\x1b[B"),  # Down
            ("sleep", 0.3),
            ("line", ""),         # Enter
            ("sleep", 0.5),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "Ctrl-B", "c",
            "Ctrl-B", "c",
            "Ctrl-B", "0",
            "Ctrl-B", "w",
            "ArrowDown",
            "ArrowDown",
            "Enter",
        ],
    },

    "int_window_tree_escape": {
        "description": "Ctrl-B w: Escape closes tree without switching",
        "steps": _tmux(
            ("keys", CTRL_B + "c"),
            ("sleep", 0.5),
            ("keys", CTRL_B + "0"),
            ("sleep", 0.3),
            ("keys", CTRL_B + "w"),
            ("sleep", 1.0),
            ("keys", "\x1b[B"),  # Down to window 1
            ("sleep", 0.3),
            ("keys", "\x1b"),    # Escape
            ("sleep", 0.5),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "Ctrl-B", "c",
            "Ctrl-B", "0",
            "Ctrl-B", "w",
            "ArrowDown",
            "Escape",
        ],
    },

    "int_window_tree_q_close": {
        "description": "Ctrl-B w: q closes tree without switching",
        "steps": _tmux(
            ("keys", CTRL_B + "c"),
            ("sleep", 0.5),
            ("keys", CTRL_B + "0"),
            ("sleep", 0.3),
            ("keys", CTRL_B + "w"),
            ("sleep", 1.0),
            ("keys", "q"),
            ("sleep", 0.5),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "Ctrl-B", "c",
            "Ctrl-B", "0",
            "Ctrl-B", "w",
            "q",
        ],
    },

    # ─────────────────────────────────────────────────────
    # Detach / reattach with state
    # ─────────────────────────────────────────────────────

    "int_detach_echo_reattach": {
        "description": "Echo, detach, reattach — output preserved",
        "steps": _tmux(
            ("line", "echo BEFORE_DETACH"),
            ("sleep", 0.3),
            ("line", "echo STILL_HERE"),
            ("sleep", 0.3),
            ("keys", CTRL_B + "d"),
            ("sleep", 0.5),
            ("wait", "detached"),
            ("line", "tmux attach -t test"),
            ("sleep", 1.0),
            ("wait", "STILL_HERE"),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "echo BEFORE_DETACH", "Enter",
            "echo STILL_HERE", "Enter",
            "Ctrl-B", "d",
            "tmux attach", "Enter",
        ],
    },

    "int_detach_vim_reattach": {
        "description": "Open vim, detach, reattach — vim still open",
        "steps": _tmux(
            ("line", "vim test.txt"),
            ("sleep", 1.5),
            ("keys", "iIn vim before detach\x1b"),
            ("sleep", 0.3),
            ("keys", CTRL_B + "d"),
            ("sleep", 0.5),
            ("wait", "detached"),
            ("line", "tmux attach -t test"),
            ("sleep", 1.0),
            ("wait", "In vim"),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "vim test.txt", "Enter",
            "i", "In vim before detach", "Escape",
            "Ctrl-B", "d",
            "tmux attach", "Enter",
        ],
    },

    "int_detach_split_reattach": {
        "description": "Split, type both, detach, reattach — split preserved",
        "steps": _tmux(
            ("line", "echo LEFT_PANE"),
            ("sleep", 0.3),
            ("keys", CTRL_B + "%"),
            ("sleep", 0.5),
            ("line", "echo RIGHT_PANE"),
            ("sleep", 0.3),
            ("keys", CTRL_B + "d"),
            ("sleep", 0.5),
            ("wait", "detached"),
            ("line", "tmux attach -t test"),
            ("sleep", 1.0),
            ("wait", "RIGHT_PANE"),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "echo LEFT_PANE", "Enter",
            "Ctrl-B", "%",
            "echo RIGHT_PANE", "Enter",
            "Ctrl-B", "d",
            "tmux attach", "Enter",
        ],
    },

    # ─────────────────────────────────────────────────────
    # Tmux exit + relaunch (lifecycle)
    # ─────────────────────────────────────────────────────

    "int_exit_relaunch_vim": {
        "description": "Exit tmux, relaunch, open vim — vim works after relaunch",
        "steps": _tmux(
            ("line", "exit"),
            ("sleep", 1.0),
            # Relaunch
            ("line", f"SHELL=/bin/bash tmux new-session -s test '{_BASH_CMD}'"),
            ("wait", "[test]", 15.0),
            ("sleep", 0.8),
            ("keys", CTRL_B + ":"),
            ("sleep", 0.2),
            ("line", f"set-option default-command '{_BASH_CMD}'"),
            ("sleep", 0.2),
            ("line", f"cd {_TEST_DIR} && clear"),
            ("sleep", 0.3),
            ("line", "vim hello.txt"),
            ("sleep", 1.5),
            ("keys", "iAfter relaunch\x1b"),
            ("sleep", 0.3),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "exit", "Enter",
            "tmux", "Enter",
            "vim hello.txt", "Enter",
            "i", "After relaunch", "Escape",
        ],
    },

    "int_double_relaunch": {
        "description": "Exit, relaunch, exit, relaunch again — third session works",
        "steps": _tmux(
            ("line", "echo SESSION_1"),
            ("sleep", 0.3),
            ("line", "exit"),
            ("sleep", 1.0),
            # Second launch
            ("line", f"SHELL=/bin/bash tmux new-session -s test '{_BASH_CMD}'"),
            ("wait", "[test]", 15.0),
            ("sleep", 0.8),
            ("keys", CTRL_B + ":"),
            ("sleep", 0.2),
            ("line", f"set-option default-command '{_BASH_CMD}'"),
            ("sleep", 0.2),
            ("line", f"cd {_TEST_DIR} && clear"),
            ("sleep", 0.3),
            ("line", "echo SESSION_2"),
            ("sleep", 0.3),
            ("line", "exit"),
            ("sleep", 1.0),
            # Third launch
            ("line", f"SHELL=/bin/bash tmux new-session -s test '{_BASH_CMD}'"),
            ("wait", "[test]", 15.0),
            ("sleep", 0.8),
            ("keys", CTRL_B + ":"),
            ("sleep", 0.2),
            ("line", f"set-option default-command '{_BASH_CMD}'"),
            ("sleep", 0.2),
            ("line", f"cd {_TEST_DIR} && clear"),
            ("sleep", 0.3),
            ("line", "echo SESSION_3_OK"),
            ("sleep", 0.3),
            ("wait", "SESSION_3_OK"),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "echo SESSION_1", "Enter",
            "exit", "Enter",
            "tmux", "Enter",
            "echo SESSION_2", "Enter",
            "exit", "Enter",
            "tmux", "Enter",
            "echo SESSION_3_OK", "Enter",
        ],
    },

    # ─────────────────────────────────────────────────────
    # Tmux zoom + content
    # ─────────────────────────────────────────────────────

    "int_zoom_vim": {
        "description": "Vsplit, zoom right pane with vim — full width",
        "steps": _tmux(
            ("line", "echo LEFT"),
            ("sleep", 0.3),
            ("keys", CTRL_B + "%"),
            ("sleep", 0.5),
            ("line", "vim test.txt"),
            ("sleep", 1.5),
            ("keys", "iZOOMED VIM\x1b"),
            ("sleep", 0.5),
            ("keys", CTRL_B + "z"),
            ("sleep", 0.3),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "echo LEFT", "Enter",
            "Ctrl-B", "%",
            "vim test.txt", "Enter",
            "i", "ZOOMED VIM", "Escape",
            "Ctrl-B", "z",
        ],
    },

    "int_zoom_unzoom": {
        "description": "Vsplit, zoom, unzoom — both panes visible again",
        "steps": _tmux(
            ("line", "echo LEFT"),
            ("sleep", 0.3),
            ("keys", CTRL_B + "%"),
            ("sleep", 0.5),
            ("line", "echo RIGHT"),
            ("sleep", 0.3),
            ("keys", CTRL_B + "z"),
            ("sleep", 0.3),
            ("keys", CTRL_B + "z"),
            ("sleep", 0.3),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "echo LEFT", "Enter",
            "Ctrl-B", "%",
            "echo RIGHT", "Enter",
            "Ctrl-B", "z",
            "Ctrl-B", "z",
        ],
    },

    # ─────────────────────────────────────────────────────
    # Complex multi-step integration
    # ─────────────────────────────────────────────────────

    "int_vim_save_split_cat": {
        "description": "Vim: write file, split, cat in other pane — content matches",
        "steps": _tmux(
            ("line", "vim data.txt"),
            ("sleep", 1.5),
            ("keys", "iImportant data\x1b"),
            ("sleep", 0.2),
            ("keys", ":wq\n"),
            ("sleep", 0.5),
            ("wait", "$"),
            ("keys", CTRL_B + "%"),
            ("sleep", 0.5),
            ("line", "cat data.txt"),
            ("sleep", 0.3),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "vim data.txt", "Enter",
            "i", "Important data", "Escape",
            ":", "w", "q", "Enter",
            "Ctrl-B", "%",
            "cat data.txt", "Enter",
        ],
    },

    "int_full_lifecycle_vim": {
        "description": "Full lifecycle: vim→edit→save→quit→cat→split→echo",
        "steps": _tmux(
            ("line", "vim notes.txt"),
            ("sleep", 1.5),
            ("keys", "iMy notes\x1b"),
            ("sleep", 0.2),
            ("keys", ":wq\n"),
            ("sleep", 0.5),
            ("wait", "$"),
            ("line", "cat notes.txt"),
            ("sleep", 0.3),
            ("keys", CTRL_B + "%"),
            ("sleep", 0.5),
            ("line", "echo Split done"),
            ("sleep", 0.3),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "vim notes.txt", "Enter",
            "i", "My notes", "Escape",
            ":", "w", "q", "Enter",
            "cat notes.txt", "Enter",
            "Ctrl-B", "%",
            "echo Split done", "Enter",
        ],
    },

    "int_navigate_vim_shell": {
        "description": "Vsplit: vim left, navigate right echo, navigate back — vim preserved",
        "steps": _tmux(
            ("line", "vim test.txt"),
            ("sleep", 1.5),
            ("keys", "iVIM CONTENT\x1b"),
            ("sleep", 0.5),
            ("keys", CTRL_B + "%"),
            ("sleep", 0.5),
            ("line", "echo SHELL SIDE"),
            ("sleep", 0.3),
            ("keys", CTRL_B + "\x1b[D"),  # Left arrow
            ("sleep", 0.3),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "vim test.txt", "Enter",
            "i", "VIM CONTENT", "Escape",
            "Ctrl-B", "%",
            "echo SHELL SIDE", "Enter",
            "Ctrl-B", "ArrowLeft",
        ],
    },

    "int_window_with_splits": {
        "description": "Window 0 has split, create window 1, switch back — split preserved",
        "steps": _tmux(
            ("line", "echo WIN0_LEFT"),
            ("sleep", 0.3),
            ("keys", CTRL_B + "%"),
            ("sleep", 0.5),
            ("line", "echo WIN0_RIGHT"),
            ("sleep", 0.3),
            ("keys", CTRL_B + "c"),
            ("sleep", 0.5),
            ("line", "echo WIN1_FULL"),
            ("sleep", 0.3),
            ("keys", CTRL_B + "0"),
            ("sleep", 0.3),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "echo WIN0_LEFT", "Enter",
            "Ctrl-B", "%",
            "echo WIN0_RIGHT", "Enter",
            "Ctrl-B", "c",
            "echo WIN1_FULL", "Enter",
            "Ctrl-B", "0",
        ],
    },

    "int_vim_quit_types_ZZ": {
        "description": "Vim: ZZ to save and quit",
        "steps": _tmux(
            ("line", "vim test.txt"),
            ("sleep", 1.5),
            ("keys", "iSaved with ZZ\x1b"),
            ("sleep", 0.2),
            ("keys", "ZZ"),
            ("sleep", 0.5),
            ("wait", "$"),
            ("line", "cat test.txt"),
            ("sleep", 0.3),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "vim test.txt", "Enter",
            "i", "Saved with ZZ", "Escape",
            "Z", "Z",
            "cat test.txt", "Enter",
        ],
    },

    "int_vim_quit_types_ZQ": {
        "description": "Vim: ZQ to quit without saving",
        "steps": _tmux(
            ("line", "vim test.txt"),
            ("sleep", 1.5),
            ("keys", "iNot saved\x1b"),
            ("sleep", 0.2),
            ("keys", "ZQ"),
            ("sleep", 0.5),
            ("wait", "$"),
            ("line", "cat test.txt"),
            ("sleep", 0.3),
        ),
        "write_files": {"test.txt": "Original content"},
        "sim_keys": [
            {"write": ["test.txt", "Original content"]},
            "tmux", "Enter",
            "vim test.txt", "Enter",
            "i", "Not saved", "Escape",
            "Z", "Q",
            "cat test.txt", "Enter",
        ],
    },

    "int_copy_mode_navigate": {
        "description": "Enter copy mode, navigate with hjkl",
        "steps": _tmux(
            ("line", "echo LINE_ONE"),
            ("sleep", 0.3),
            ("line", "echo LINE_TWO"),
            ("sleep", 0.3),
            ("line", "echo LINE_THREE"),
            ("sleep", 0.3),
            ("keys", CTRL_B + "["),
            ("sleep", 0.3),
            ("keys", "kk"),
            ("sleep", 0.3),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "echo LINE_ONE", "Enter",
            "echo LINE_TWO", "Enter",
            "echo LINE_THREE", "Enter",
            "Ctrl-B", "[",
            "k", "k",
        ],
    },

    "int_pane_swap": {
        "description": "Vsplit: swap panes with Ctrl-B }",
        "steps": _tmux(
            ("line", "echo ORIG_LEFT"),
            ("sleep", 0.3),
            ("keys", CTRL_B + "%"),
            ("sleep", 0.5),
            ("line", "echo ORIG_RIGHT"),
            ("sleep", 0.3),
            ("keys", CTRL_B + "}"),
            ("sleep", 0.3),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "echo ORIG_LEFT", "Enter",
            "Ctrl-B", "%",
            "echo ORIG_RIGHT", "Enter",
            "Ctrl-B", "}",
        ],
    },

    # int_layout_cycle removed — real tmux and sim cycle through different layout orders

    "int_split_command_mode": {
        "description": "Use Ctrl-B : split-window to create a split",
        "steps": _tmux(
            ("keys", CTRL_B + ":"),
            ("sleep", 0.3),
            ("line", "split-window"),
            ("sleep", 0.5),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "Ctrl-B", ":",
            "split-window", "Enter",
        ],
    },

    "int_echo_redirect_cat": {
        "description": "Shell: echo > file, echo >> file, cat — file I/O",
        "steps": _tmux(
            ("line", "echo first line > out.txt"),
            ("sleep", 0.3),
            ("line", "echo second line >> out.txt"),
            ("sleep", 0.3),
            ("line", "cat out.txt"),
            ("sleep", 0.3),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "echo first line > out.txt", "Enter",
            "echo second line >> out.txt", "Enter",
            "cat out.txt", "Enter",
        ],
    },

    "int_touch_vim_new": {
        "description": "Touch file, then vim it — opens empty file",
        "steps": _tmux(
            ("line", "touch blank.txt"),
            ("sleep", 0.3),
            ("line", "vim blank.txt"),
            ("sleep", 1.5),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "touch blank.txt", "Enter",
            "vim blank.txt", "Enter",
        ],
    },

    "int_vim_e_switch_file": {
        "description": "Vim: :e to switch from one file to another",
        "steps": _tmux(
            ("line", "vim first.txt"),
            ("sleep", 1.5),
            ("keys", ":e second.txt\n"),
            ("sleep", 0.5),
        ),
        "write_files": {
            "first.txt": "File one",
            "second.txt": "File two",
        },
        "sim_keys": [
            {"write": ["first.txt", "File one"]},
            {"write": ["second.txt", "File two"]},
            "tmux", "Enter",
            "vim first.txt", "Enter",
            ":", "e", " ", "s", "e", "c", "o", "n", "d", ".", "t", "x", "t", "Enter",
        ],
    },

    "int_vim_search_highlight": {
        "description": "Vim: / search highlights match",
        "steps": _tmux(
            ("line", "vim test.txt"),
            ("sleep", 1.5),
            ("keys", "/target\n"),
            ("sleep", 0.3),
        ),
        "write_files": {"test.txt": "some words here\ntarget word here\nmore text"},
        "sim_keys": [
            {"write": ["test.txt", "some words here\ntarget word here\nmore text"]},
            "tmux", "Enter",
            "vim test.txt", "Enter",
            "/", "t", "a", "r", "g", "e", "t", "Enter",
        ],
    },

    "int_vim_multiline_edit": {
        "description": "Vim: multi-line insert with Enter in insert mode",
        "steps": _tmux(
            ("line", "vim test.txt"),
            ("sleep", 1.5),
            ("keys", "iLine 1\nLine 2\nLine 3\x1b"),
            ("sleep", 0.3),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "vim test.txt", "Enter",
            "i", "Line 1", "Enter", "Line 2", "Enter", "Line 3", "Escape",
        ],
    },

    "int_vim_visual_delete": {
        "description": "Vim: visual mode select and delete",
        "steps": _tmux(
            ("line", "vim test.txt"),
            ("sleep", 1.5),
            ("keys", "gg"),
            ("sleep", 0.2),
            ("keys", "vllld"),
            ("sleep", 0.3),
        ),
        "write_files": {"test.txt": "ABCDEFGH"},
        "sim_keys": [
            {"write": ["test.txt", "ABCDEFGH"]},
            "tmux", "Enter",
            "vim test.txt", "Enter",
            "v", "l", "l", "l", "d",
        ],
    },

    "int_vim_visual_line_delete": {
        "description": "Vim: visual line mode select and delete",
        "steps": _tmux(
            ("line", "vim test.txt"),
            ("sleep", 1.5),
            ("keys", "gg"),
            ("sleep", 0.2),
            ("keys", "V"),
            ("sleep", 0.1),
            ("keys", "jd"),
            ("sleep", 0.3),
        ),
        "write_files": {"test.txt": "Line 1\nLine 2\nLine 3\nLine 4"},
        "sim_keys": [
            {"write": ["test.txt", "Line 1\nLine 2\nLine 3\nLine 4"]},
            "tmux", "Enter",
            "vim test.txt", "Enter",
            "V", "j", "d",
        ],
    },

    # ─────────────────────────────────────────────────────
    # Exit sequences from various states
    # ─────────────────────────────────────────────────────

    "int_exit_vim_exit_tmux": {
        "description": "Vim :q then exit tmux — back at outer shell",
        "steps": _tmux(
            ("line", "vim test.txt"),
            ("sleep", 1.5),
            ("keys", ":q\n"),
            ("sleep", 0.5),
            ("wait", "$"),
            ("line", "exit"),
            ("sleep", 1.0),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "vim test.txt", "Enter",
            ":", "q", "Enter",
            "exit", "Enter",
        ],
    },

    "int_split_exit_both": {
        "description": "Vsplit: exit right pane, then exit remaining left — tmux exits",
        "steps": _tmux(
            ("line", "echo LEFT"),
            ("sleep", 0.3),
            ("keys", CTRL_B + "%"),
            ("sleep", 0.5),
            ("line", "echo RIGHT"),
            ("sleep", 0.3),
            ("line", "exit"),
            ("sleep", 0.5),
            ("line", "exit"),
            ("sleep", 1.0),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "echo LEFT", "Enter",
            "Ctrl-B", "%",
            "echo RIGHT", "Enter",
            "exit", "Enter",
            "exit", "Enter",
        ],
    },

    # ─────────────────────────────────────────────────────
    # Shell operations in tmux
    # ─────────────────────────────────────────────────────

    "int_shell_echo_multiple": {
        "description": "Shell: multiple echo commands — output stacks",
        "steps": _tmux(
            ("line", "echo AAA"),
            ("sleep", 0.2),
            ("line", "echo BBB"),
            ("sleep", 0.2),
            ("line", "echo CCC"),
            ("sleep", 0.2),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "echo AAA", "Enter",
            "echo BBB", "Enter",
            "echo CCC", "Enter",
        ],
    },

    "int_shell_clear_type": {
        "description": "Shell: type, clear, type again — only new output visible",
        "steps": _tmux(
            ("line", "echo BEFORE_CLEAR"),
            ("sleep", 0.3),
            ("line", "clear"),
            ("sleep", 0.3),
            ("line", "echo AFTER_CLEAR"),
            ("sleep", 0.3),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "echo BEFORE_CLEAR", "Enter",
            "clear", "Enter",
            "echo AFTER_CLEAR", "Enter",
        ],
    },

    # int_shell_history removed — real bash has persistent history; sim only tracks session commands

    # ─────────────────────────────────────────────────────
    # Border rendering (multi-split active pane border coloring)
    # ─────────────────────────────────────────────────────

    "border_three_pane_active_bottom_right": {
        "description": "Three panes (vsplit + hsplit right) — active bottom-right, only adjacent borders green",
        "steps": _tmux(
            ("keys", CTRL_B + "%"),
            ("sleep", 0.5),
            ("keys", CTRL_B + '"'),
            ("sleep", 0.5),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "Ctrl-B", "%",
            "Ctrl-B", '"',
        ],
    },

    "border_three_pane_active_top_right": {
        "description": "Three panes (vsplit + hsplit right) — navigate to top-right pane",
        "steps": _tmux(
            ("keys", CTRL_B + "%"),
            ("sleep", 0.5),
            ("keys", CTRL_B + '"'),
            ("sleep", 0.5),
            ("keys", CTRL_B + "\x1b[A"),  # Up arrow → top-right pane
            ("sleep", 0.3),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "Ctrl-B", "%",
            "Ctrl-B", '"',
            "Ctrl-B", "ArrowUp",
        ],
    },

    "border_three_pane_active_left": {
        "description": "Three panes (vsplit + hsplit right) — navigate to left pane",
        "steps": _tmux(
            ("keys", CTRL_B + "%"),
            ("sleep", 0.5),
            ("keys", CTRL_B + '"'),
            ("sleep", 0.5),
            ("keys", CTRL_B + "\x1b[D"),  # Left arrow → left pane
            ("sleep", 0.3),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "Ctrl-B", "%",
            "Ctrl-B", '"',
            "Ctrl-B", "ArrowLeft",
        ],
    },

    "border_four_panes_cross": {
        "description": "Four panes (vsplit both sides) — cross intersection, active bottom-right",
        "steps": _tmux(
            ("keys", CTRL_B + "%"),
            ("sleep", 0.5),
            ("keys", CTRL_B + '"'),
            ("sleep", 0.5),
            ("keys", CTRL_B + "\x1b[D"),  # Left arrow → left pane
            ("sleep", 0.3),
            ("keys", CTRL_B + '"'),
            ("sleep", 0.5),
            ("keys", CTRL_B + "\x1b[C"),  # Right arrow → right side
            ("sleep", 0.3),
            ("keys", CTRL_B + "\x1b[B"),  # Down arrow → bottom-right
            ("sleep", 0.3),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "Ctrl-B", "%",
            "Ctrl-B", '"',
            "Ctrl-B", "ArrowLeft",
            "Ctrl-B", '"',
            "Ctrl-B", "ArrowRight",
            "Ctrl-B", "ArrowDown",
        ],
    },

    "border_four_panes_active_top_left": {
        "description": "Four panes — navigate to top-left, check partial border coloring",
        "steps": _tmux(
            ("keys", CTRL_B + "%"),
            ("sleep", 0.5),
            ("keys", CTRL_B + '"'),
            ("sleep", 0.5),
            ("keys", CTRL_B + "\x1b[D"),  # Left arrow → left pane
            ("sleep", 0.3),
            ("keys", CTRL_B + '"'),
            ("sleep", 0.5),
            ("keys", CTRL_B + "\x1b[A"),  # Up arrow → top-left
            ("sleep", 0.3),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "Ctrl-B", "%",
            "Ctrl-B", '"',
            "Ctrl-B", "ArrowLeft",
            "Ctrl-B", '"',
            "Ctrl-B", "ArrowUp",
        ],
    },

    "border_hsplit_then_vsplit": {
        "description": "Hsplit then vsplit bottom — T intersection, active bottom-right",
        "steps": _tmux(
            ("keys", CTRL_B + '"'),
            ("sleep", 0.5),
            ("keys", CTRL_B + "%"),
            ("sleep", 0.5),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "Ctrl-B", '"',
            "Ctrl-B", "%",
        ],
    },

    "border_hsplit_vsplit_active_top": {
        "description": "Hsplit then vsplit bottom — navigate to top pane",
        "steps": _tmux(
            ("keys", CTRL_B + '"'),
            ("sleep", 0.5),
            ("keys", CTRL_B + "%"),
            ("sleep", 0.5),
            ("keys", CTRL_B + "\x1b[A"),  # Up arrow → top pane
            ("sleep", 0.3),
        ),
        "sim_keys": [
            "tmux", "Enter",
            "Ctrl-B", '"',
            "Ctrl-B", "%",
            "Ctrl-B", "ArrowUp",
        ],
    },
}
