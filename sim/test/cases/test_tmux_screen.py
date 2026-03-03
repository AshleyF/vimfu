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
    # Kill any existing tmux, launch with controlled shell
    ("line", f"tmux kill-server 2>/dev/null; cd {_TEST_DIR} && SHELL=/bin/bash tmux new-session -s test '{_BASH_CMD}'"),
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
}
