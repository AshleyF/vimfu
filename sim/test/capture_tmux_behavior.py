"""
Capture real tmux behavior via ShellPilot.

Launches tmux inside a real terminal (WSL), exercises vim-friendly tmux
commands in isolated groups, and captures the resulting screen text.

Each group starts a fresh tmux session to avoid cascading failures.
The output (tmux_behavior_ground_truth.json) is consumed by
compare_tmux_behavior.py to verify the sim matches.

Usage:
    cd sim
    C:/source/vimfu/.venv/Scripts/python.exe test/capture_tmux_behavior.py
"""

from __future__ import annotations

import json
import sys
import time
import traceback
from pathlib import Path

_here = Path(__file__).resolve().parent
_root = _here.parent.parent
sys.path.insert(0, str(_root / "shellpilot"))

from shell_pty import ShellPilot

ROWS = 24
COLS = 80


def wait_stable(shell, seconds=0.5):
    time.sleep(seconds)


def send_ctrl(shell, char):
    code = ord(char.upper()) - ord('A') + 1
    shell.send_keys(chr(code))


def send_prefix(shell):
    """Send Ctrl-B (tmux prefix)."""
    send_ctrl(shell, 'b')
    time.sleep(0.15)


def get_screen_text(shell):
    return [line.rstrip() for line in shell.screen.display]


def get_status_bar(shell):
    lines = get_screen_text(shell)
    return lines[-1] if lines else ""


def capture(shell, label, description):
    text_lines = get_screen_text(shell)
    cursor = shell.get_cursor_position()
    return {
        "label": label,
        "description": description,
        "rows": ROWS,
        "cols": COLS,
        "screen": text_lines,
        "status_bar": text_lines[-1] if text_lines else "",
        "pane_lines": text_lines[:-1],
        "cursor": {"row": cursor[0], "col": cursor[1]},
    }


def find_border_col(lines):
    for line in lines:
        for i, ch in enumerate(line):
            if ch == '│':
                return i
    return None


def find_border_row(lines):
    for i, line in enumerate(lines):
        if '─' in line:
            return i
    return None


def start_tmux(shell, session_name="test"):
    """Start a fresh tmux session."""
    shell.send_line(f"tmux new-session -s {session_name}")
    wait_stable(shell, 2.0)
    status = get_status_bar(shell)
    if session_name not in status:
        print(f"  [WARN] tmux may not have started: {repr(status)}")
    return status


def kill_tmux(shell):
    """Kill tmux server (all sessions)."""
    send_prefix(shell)
    shell.send_keys(':')
    wait_stable(shell, 0.2)
    shell.send_line("kill-server")
    wait_stable(shell, 1.0)


def safe_kill_tmux(shell):
    """Try multiple ways to exit tmux."""
    try:
        kill_tmux(shell)
    except Exception:
        pass
    # Also try sending exit in case we're at shell
    try:
        shell.send_line("tmux kill-server 2>/dev/null")
        wait_stable(shell, 0.5)
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════════════
# Capture Groups — each is independent
# ═══════════════════════════════════════════════════════════════════

def group_basic_launch(shell, results):
    """Group 1: Fresh launch, echo, status bar."""
    print("\n[GROUP 1] Basic launch")

    start_tmux(shell, "basic")

    results["fresh_launch"] = capture(
        shell, "fresh_launch",
        "Fresh tmux launch — single pane, status bar visible"
    )

    shell.send_line("echo 'hello world'")
    wait_stable(shell, 0.5)

    results["after_echo"] = capture(
        shell, "after_echo",
        "After echo — output visible in pane"
    )

    shell.send_line("ls")
    wait_stable(shell, 0.5)

    results["after_ls"] = capture(
        shell, "after_ls",
        "After ls — output visible in pane"
    )

    kill_tmux(shell)


def group_vsplit(shell, results):
    """Group 2: Vertical split, pane navigation, content."""
    print("\n[GROUP 2] Vertical split")

    start_tmux(shell, "vsplit")

    # Split vertically
    send_prefix(shell)
    shell.send_keys('%')
    wait_stable(shell, 0.5)

    results["vsplit"] = capture(
        shell, "vsplit",
        "Vertical split — two panes, right active"
    )

    # Check we have a border
    border = find_border_col(results["vsplit"]["pane_lines"])
    print(f"  Border column: {border}")

    # Type in right pane
    shell.send_line("echo 'RIGHT PANE'")
    wait_stable(shell, 0.5)

    results["vsplit_echo_right"] = capture(
        shell, "vsplit_echo_right",
        "Echo in right pane — RIGHT PANE visible on right side"
    )

    # Navigate left
    send_prefix(shell)
    shell.send_keys('\x1b[D')  # Left arrow
    wait_stable(shell, 0.3)

    shell.send_line("echo 'LEFT PANE'")
    wait_stable(shell, 0.5)

    results["vsplit_echo_left"] = capture(
        shell, "vsplit_echo_left",
        "After nav left and echo — LEFT PANE visible on left side"
    )

    # Navigate right with 'o' (cycle next)
    send_prefix(shell)
    shell.send_keys('o')
    wait_stable(shell, 0.3)

    results["vsplit_after_cycle_o"] = capture(
        shell, "vsplit_after_cycle_o",
        "After Ctrl-B o — cursor cycled to right pane"
    )

    kill_tmux(shell)


def group_hsplit(shell, results):
    """Group 3: Horizontal split, navigate up/down."""
    print("\n[GROUP 3] Horizontal split")

    start_tmux(shell, "hsplit")

    send_prefix(shell)
    shell.send_keys('"')
    wait_stable(shell, 0.5)

    results["hsplit"] = capture(
        shell, "hsplit",
        "Horizontal split — two panes stacked, bottom active"
    )

    border = find_border_row(results["hsplit"]["pane_lines"])
    print(f"  Border row: {border}")

    shell.send_line("echo 'BOTTOM PANE'")
    wait_stable(shell, 0.5)

    results["hsplit_echo_bottom"] = capture(
        shell, "hsplit_echo_bottom",
        "Echo in bottom pane — BOTTOM PANE visible below border"
    )

    # Navigate to top pane
    send_prefix(shell)
    shell.send_keys('\x1b[A')  # Up arrow
    wait_stable(shell, 0.3)

    shell.send_line("echo 'TOP PANE'")
    wait_stable(shell, 0.5)

    results["hsplit_echo_top"] = capture(
        shell, "hsplit_echo_top",
        "After nav up and echo — TOP PANE visible in top section"
    )

    kill_tmux(shell)


def group_three_panes(shell, results):
    """Group 4: Three-pane layout with content in each."""
    print("\n[GROUP 4] Three panes")

    start_tmux(shell, "three")

    # vsplit first, then hsplit the right pane
    send_prefix(shell)
    shell.send_keys('%')
    wait_stable(shell, 0.5)

    send_prefix(shell)
    shell.send_keys('"')
    wait_stable(shell, 0.5)

    results["three_panes"] = capture(
        shell, "three_panes",
        "Three panes: left full-height, right split top/bottom"
    )

    # Label each pane
    shell.send_line("echo 'PANE-BR'")  # bottom-right (current)
    wait_stable(shell, 0.3)

    send_prefix(shell)
    shell.send_keys('\x1b[A')  # Up to top-right
    wait_stable(shell, 0.2)
    shell.send_line("echo 'PANE-TR'")
    wait_stable(shell, 0.3)

    send_prefix(shell)
    shell.send_keys('\x1b[D')  # Left to left
    wait_stable(shell, 0.2)
    shell.send_line("echo 'PANE-L'")
    wait_stable(shell, 0.3)

    results["three_panes_content"] = capture(
        shell, "three_panes_content",
        "Three panes with labels: PANE-L, PANE-TR, PANE-BR"
    )

    kill_tmux(shell)


def group_windows(shell, results):
    """Group 5: Window management — create, switch, rename."""
    print("\n[GROUP 5] Window management")

    start_tmux(shell, "wins")

    shell.send_line("echo 'WINDOW-0'")
    wait_stable(shell, 0.3)

    # Create second window
    send_prefix(shell)
    shell.send_keys('c')
    wait_stable(shell, 0.5)

    results["two_windows"] = capture(
        shell, "two_windows",
        "After Ctrl-B c — window 1 created, now active"
    )

    shell.send_line("echo 'WINDOW-1'")
    wait_stable(shell, 0.3)

    # Switch to previous window (p)
    send_prefix(shell)
    shell.send_keys('p')
    wait_stable(shell, 0.5)

    results["switch_prev"] = capture(
        shell, "switch_prev",
        "After Ctrl-B p — back to window 0 (WINDOW-0 visible)"
    )

    # Switch to next (n)
    send_prefix(shell)
    shell.send_keys('n')
    wait_stable(shell, 0.5)

    results["switch_next"] = capture(
        shell, "switch_next",
        "After Ctrl-B n — forward to window 1 (WINDOW-1 visible)"
    )

    # Switch by number (0)
    send_prefix(shell)
    shell.send_keys('0')
    wait_stable(shell, 0.5)

    results["switch_by_number"] = capture(
        shell, "switch_by_number",
        "After Ctrl-B 0 — window 0 active"
    )

    # Last window toggle (l)
    send_prefix(shell)
    shell.send_keys('l')
    wait_stable(shell, 0.5)

    results["last_window"] = capture(
        shell, "last_window",
        "After Ctrl-B l — toggle to last window (1)"
    )

    # Create third window
    send_prefix(shell)
    shell.send_keys('c')
    wait_stable(shell, 0.5)

    results["three_windows"] = capture(
        shell, "three_windows",
        "After Ctrl-B c — 3 windows, window 2 active"
    )

    # Rename current window
    send_prefix(shell)
    shell.send_keys(',')
    wait_stable(shell, 0.3)
    send_ctrl(shell, 'u')  # Clear line
    time.sleep(0.1)
    shell.send_keys('editor')
    time.sleep(0.1)
    shell.send_keys('\r')
    wait_stable(shell, 0.5)

    results["renamed_window"] = capture(
        shell, "renamed_window",
        "After renaming window 2 to 'editor'"
    )

    kill_tmux(shell)


def group_vim_in_tmux(shell, results):
    """Group 6: Vim inside tmux, vim+shell split."""
    print("\n[GROUP 6] Vim inside tmux")

    start_tmux(shell, "vim")

    # Create a test file
    shell.send_line("echo -e 'line 1\\nline 2\\nline 3\\nline 4\\nline 5' > /tmp/test_tmux.txt")
    wait_stable(shell, 0.3)

    # Launch vim
    shell.send_line("vim /tmp/test_tmux.txt")
    wait_stable(shell, 1.5)

    results["vim_in_tmux"] = capture(
        shell, "vim_in_tmux",
        "Vim opened inside tmux — file content visible"
    )

    # Split — vim in left, shell in right
    send_prefix(shell)
    shell.send_keys('%')
    wait_stable(shell, 0.5)

    results["vim_and_shell_split"] = capture(
        shell, "vim_and_shell_split",
        "Vim in left pane, fresh shell in right pane"
    )

    # Run commands in right (shell) pane
    shell.send_line("echo 'shell output'")
    wait_stable(shell, 0.3)
    shell.send_line("ls /tmp/test_tmux.txt")
    wait_stable(shell, 0.3)

    results["vim_left_shell_right_with_output"] = capture(
        shell, "vim_left_shell_right_with_output",
        "Vim left, shell right with echo + ls output"
    )

    # Navigate back to vim pane
    send_prefix(shell)
    shell.send_keys('\x1b[D')  # Left
    wait_stable(shell, 0.3)

    results["vim_pane_active"] = capture(
        shell, "vim_pane_active",
        "Cursor back in vim pane (left)"
    )

    # Quit vim
    shell.send_keys(':')
    time.sleep(0.1)
    shell.send_keys('q')
    time.sleep(0.1)
    shell.send_keys('\r')
    wait_stable(shell, 0.5)

    results["after_vim_quit"] = capture(
        shell, "after_vim_quit",
        "After :q from vim — shell prompt in left pane"
    )

    kill_tmux(shell)


def group_zoom(shell, results):
    """Group 7: Pane zoom/unzoom."""
    print("\n[GROUP 7] Pane zoom")

    start_tmux(shell, "zoom")

    send_prefix(shell)
    shell.send_keys('%')  # vsplit
    wait_stable(shell, 0.5)

    shell.send_line("echo 'ZOOM-THIS'")
    wait_stable(shell, 0.3)

    results["before_zoom"] = capture(
        shell, "before_zoom",
        "Before zoom — two panes, ZOOM-THIS in right"
    )

    send_prefix(shell)
    shell.send_keys('z')
    wait_stable(shell, 0.5)

    results["zoomed"] = capture(
        shell, "zoomed",
        "After Ctrl-B z — right pane zoomed to full screen"
    )

    send_prefix(shell)
    shell.send_keys('z')
    wait_stable(shell, 0.5)

    results["unzoomed"] = capture(
        shell, "unzoomed",
        "After Ctrl-B z again — back to split"
    )

    kill_tmux(shell)


def group_close_pane(shell, results):
    """Group 8: Pane close with confirmation."""
    print("\n[GROUP 8] Pane close")

    start_tmux(shell, "close")

    send_prefix(shell)
    shell.send_keys('%')  # vsplit
    wait_stable(shell, 0.5)

    send_prefix(shell)
    shell.send_keys('x')
    wait_stable(shell, 0.5)

    results["close_confirm"] = capture(
        shell, "close_confirm",
        "Ctrl-B x — confirmation prompt visible"
    )

    # Decline
    shell.send_keys('n')
    wait_stable(shell, 0.3)

    results["close_declined"] = capture(
        shell, "close_declined",
        "After n — pane still exists"
    )

    # Confirm
    send_prefix(shell)
    shell.send_keys('x')
    wait_stable(shell, 0.3)
    shell.send_keys('y')
    wait_stable(shell, 0.5)

    results["close_confirmed"] = capture(
        shell, "close_confirmed",
        "After y — right pane closed"
    )

    kill_tmux(shell)


def group_command_prompt(shell, results):
    """Group 9: Command prompt."""
    print("\n[GROUP 9] Command prompt")

    start_tmux(shell, "cmd")

    send_prefix(shell)
    shell.send_keys(':')
    wait_stable(shell, 0.3)

    results["cmd_prompt_empty"] = capture(
        shell, "cmd_prompt_empty",
        "Command prompt open (empty)"
    )

    shell.send_keys('split-window -h')
    wait_stable(shell, 0.2)

    results["cmd_prompt_typed"] = capture(
        shell, "cmd_prompt_typed",
        "Command prompt with 'split-window -h' typed"
    )

    # Cancel
    shell.send_keys('\x1b')
    wait_stable(shell, 0.3)

    results["cmd_prompt_cancelled"] = capture(
        shell, "cmd_prompt_cancelled",
        "After Escape — back to normal"
    )

    # Execute split-window via command
    send_prefix(shell)
    shell.send_keys(':')
    wait_stable(shell, 0.2)
    shell.send_line("split-window -h")
    wait_stable(shell, 0.5)

    results["cmd_split_executed"] = capture(
        shell, "cmd_split_executed",
        "After :split-window -h — pane created"
    )

    kill_tmux(shell)


def group_copy_mode(shell, results):
    """Group 10: Copy mode."""
    print("\n[GROUP 10] Copy mode")

    start_tmux(shell, "copy")

    # Create some content
    shell.send_line("echo 'line A'")
    wait_stable(shell, 0.2)
    shell.send_line("echo 'line B'")
    wait_stable(shell, 0.2)
    shell.send_line("echo 'line C'")
    wait_stable(shell, 0.3)

    send_prefix(shell)
    shell.send_keys('[')
    wait_stable(shell, 0.5)

    results["copy_mode_enter"] = capture(
        shell, "copy_mode_enter",
        "Copy mode entered"
    )

    # Move around
    shell.send_keys('k')
    wait_stable(shell, 0.2)
    shell.send_keys('k')
    wait_stable(shell, 0.2)
    shell.send_keys('0')  # Beginning of line
    wait_stable(shell, 0.2)

    results["copy_mode_moved"] = capture(
        shell, "copy_mode_moved",
        "After moving up twice and to col 0 in copy mode"
    )

    # Exit
    shell.send_keys('q')
    wait_stable(shell, 0.3)

    results["copy_mode_exited"] = capture(
        shell, "copy_mode_exited",
        "After q — back to normal"
    )

    kill_tmux(shell)


def group_detach_reattach(shell, results):
    """Group 11: Detach and reattach."""
    print("\n[GROUP 11] Detach/reattach")

    start_tmux(shell, "detach")

    shell.send_line("echo 'BEFORE DETACH'")
    wait_stable(shell, 0.3)

    # Detach
    send_prefix(shell)
    shell.send_keys('d')
    wait_stable(shell, 1.0)

    results["detached"] = capture(
        shell, "detached",
        "After Ctrl-B d — back at shell, detached message"
    )

    # List sessions
    shell.send_line("tmux ls")
    wait_stable(shell, 0.5)

    results["tmux_ls"] = capture(
        shell, "tmux_ls",
        "tmux ls — shows detached session"
    )

    # Reattach
    shell.send_line("tmux attach -t detach")
    wait_stable(shell, 1.5)

    results["reattached"] = capture(
        shell, "reattached",
        "After tmux attach — back in session, BEFORE DETACH visible"
    )

    kill_tmux(shell)


def group_resize(shell, results):
    """Group 12: Pane resize."""
    print("\n[GROUP 12] Resize")

    start_tmux(shell, "resize")

    send_prefix(shell)
    shell.send_keys('%')  # vsplit
    wait_stable(shell, 0.5)

    border_before = find_border_col(get_screen_text(shell)[:-1])
    print(f"  Border col before: {border_before}")

    results["before_resize"] = capture(
        shell, "before_resize",
        "Before resize — default split position"
    )

    # Resize: Ctrl-Left (makes left pane wider / right narrower)
    for _ in range(3):
        send_prefix(shell)
        shell.send_keys('\x1b[1;5D')  # Ctrl-Left
        wait_stable(shell, 0.2)

    border_after = find_border_col(get_screen_text(shell)[:-1])
    print(f"  Border col after 3x Ctrl-Left: {border_after}")

    results["after_resize"] = capture(
        shell, "after_resize",
        "After 3x Ctrl-Left — border moved"
    )
    results["after_resize"]["border_before"] = border_before
    results["after_resize"]["border_after"] = border_after

    kill_tmux(shell)


def group_swap(shell, results):
    """Group 13: Swap panes."""
    print("\n[GROUP 13] Swap panes")

    start_tmux(shell, "swap")

    send_prefix(shell)
    shell.send_keys('%')  # vsplit
    wait_stable(shell, 0.5)

    # Right pane is active
    shell.send_line("echo 'SWAP-RIGHT'")
    wait_stable(shell, 0.3)

    # Go left
    send_prefix(shell)
    shell.send_keys('\x1b[D')
    wait_stable(shell, 0.2)
    shell.send_line("echo 'SWAP-LEFT'")
    wait_stable(shell, 0.3)

    results["before_swap"] = capture(
        shell, "before_swap",
        "Before swap: SWAP-LEFT in left, SWAP-RIGHT in right"
    )

    # Swap with next (})
    send_prefix(shell)
    shell.send_keys('}')
    wait_stable(shell, 0.5)

    results["after_swap"] = capture(
        shell, "after_swap",
        "After Ctrl-B } — panes swapped"
    )

    kill_tmux(shell)


def group_break_pane(shell, results):
    """Group 14: Break pane into new window."""
    print("\n[GROUP 14] Break pane")

    start_tmux(shell, "brk")

    send_prefix(shell)
    shell.send_keys('%')  # vsplit
    wait_stable(shell, 0.5)

    shell.send_line("echo 'BREAK-PANE'")
    wait_stable(shell, 0.3)

    results["before_break"] = capture(
        shell, "before_break",
        "Before break — two panes, BREAK-PANE in right"
    )

    send_prefix(shell)
    shell.send_keys('!')
    wait_stable(shell, 0.5)

    results["after_break"] = capture(
        shell, "after_break",
        "After Ctrl-B ! — pane moved to new window"
    )

    kill_tmux(shell)


# ═══════════════════════════════════════════════════════════════════


def main():
    print(f"[CAPTURE] Starting tmux behavior capture ({ROWS}x{COLS})")

    shell = ShellPilot(rows=ROWS, cols=COLS)
    results = {}
    groups = [
        group_basic_launch,
        group_vsplit,
        group_hsplit,
        group_three_panes,
        group_windows,
        group_vim_in_tmux,
        group_zoom,
        group_close_pane,
        group_command_prompt,
        group_copy_mode,
        group_detach_reattach,
        group_resize,
        group_swap,
        group_break_pane,
    ]

    try:
        shell.start()
        wait_stable(shell, 2.0)

        for group_fn in groups:
            try:
                group_fn(shell, results)
            except Exception as e:
                name = group_fn.__name__
                print(f"\n  [ERROR] {name} failed: {e}")
                traceback.print_exc()
                # Try to clean up tmux
                safe_kill_tmux(shell)
                wait_stable(shell, 1.0)

    finally:
        try:
            shell.stop()
        except Exception:
            pass

    # Write results
    out = _here / "tmux_behavior_ground_truth.json"
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\n[CAPTURE] Wrote {len(results)} scenarios -> {out}")

    # Summary
    print(f"\n{'=' * 70}")
    print("CAPTURE SUMMARY")
    print(f"{'=' * 70}")
    for name, sc in results.items():
        status = sc.get("status_bar", "")
        cursor = sc.get("cursor", {})
        print(f"  {name:45s} cursor=({cursor.get('row', '?')},{cursor.get('col', '?'):>2})  status={repr(status[:60])}")
    print(f"\nTotal: {len(results)} scenarios captured")


if __name__ == "__main__":
    main()
