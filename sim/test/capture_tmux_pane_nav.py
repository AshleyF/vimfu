"""
Capture real tmux pane navigation behavior via ShellPilot.

Tests hjkl pane navigation with custom bindings (matching our simulator).
Also tests arrow key navigation, last-window (L), and complex split layouts.

Usage:
    cd sim
    C:/source/vimfu/.venv/Scripts/python.exe test/capture_tmux_pane_nav.py
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


def start_tmux_with_hjkl(shell, session_name="test"):
    """Start a fresh tmux session with hjkl pane navigation bindings."""
    shell.send_line(f"tmux new-session -s {session_name}")
    wait_stable(shell, 2.0)
    status = get_status_bar(shell)
    if session_name not in status:
        print(f"  [WARN] tmux may not have started: {repr(status)}")

    # Set up vim-style hjkl bindings for pane navigation
    # This matches what our simulator does
    send_prefix(shell)
    shell.send_keys(':')
    wait_stable(shell, 0.2)
    shell.send_line("bind h select-pane -L")
    wait_stable(shell, 0.3)

    send_prefix(shell)
    shell.send_keys(':')
    wait_stable(shell, 0.2)
    shell.send_line("bind j select-pane -D")
    wait_stable(shell, 0.3)

    send_prefix(shell)
    shell.send_keys(':')
    wait_stable(shell, 0.2)
    shell.send_line("bind k select-pane -U")
    wait_stable(shell, 0.3)

    send_prefix(shell)
    shell.send_keys(':')
    wait_stable(shell, 0.2)
    shell.send_line("bind l select-pane -R")
    wait_stable(shell, 0.3)

    # Also bind L (uppercase) for last-window
    send_prefix(shell)
    shell.send_keys(':')
    wait_stable(shell, 0.2)
    shell.send_line("bind L last-window")
    wait_stable(shell, 0.3)

    return status


def kill_tmux(shell):
    send_prefix(shell)
    shell.send_keys(':')
    wait_stable(shell, 0.2)
    shell.send_line("kill-server")
    wait_stable(shell, 1.0)


def safe_kill_tmux(shell):
    try:
        kill_tmux(shell)
    except Exception:
        pass
    try:
        shell.send_line("tmux kill-server 2>/dev/null")
        wait_stable(shell, 0.5)
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════════
# Capture Groups
# ═══════════════════════════════════════════════════════════════

def group_vsplit_hjkl(shell, results):
    """Vertical split: test h/l navigation."""
    print("\n[GROUP 1] Vertical split h/l navigation")

    start_tmux_with_hjkl(shell, "vsplit_hl")

    # Split vertically (left | right)
    send_prefix(shell)
    shell.send_keys('%')
    wait_stable(shell, 0.5)

    # We're in the RIGHT pane. Echo a marker.
    shell.send_line("echo 'RIGHT'")
    wait_stable(shell, 0.3)

    results["vsplit_initial"] = capture(
        shell, "vsplit_initial",
        "Vertical split, right pane active, 'RIGHT' echoed"
    )

    # Navigate left with 'h'
    send_prefix(shell)
    shell.send_keys('h')
    wait_stable(shell, 0.3)

    shell.send_line("echo 'LEFT'")
    wait_stable(shell, 0.3)

    results["vsplit_after_h"] = capture(
        shell, "vsplit_after_h",
        "After Ctrl-B h: left pane active, 'LEFT' echoed"
    )

    # Navigate right with 'l'
    send_prefix(shell)
    shell.send_keys('l')
    wait_stable(shell, 0.3)

    shell.send_line("echo 'BACK_RIGHT'")
    wait_stable(shell, 0.3)

    results["vsplit_after_l"] = capture(
        shell, "vsplit_after_l",
        "After Ctrl-B l: right pane active, 'BACK_RIGHT' echoed"
    )

    kill_tmux(shell)


def group_hsplit_jk(shell, results):
    """Horizontal split: test j/k navigation."""
    print("\n[GROUP 2] Horizontal split j/k navigation")

    start_tmux_with_hjkl(shell, "hsplit_jk")

    # Split horizontally (top / bottom)
    send_prefix(shell)
    shell.send_keys('"')
    wait_stable(shell, 0.5)

    # We're in the BOTTOM pane
    shell.send_line("echo 'BOTTOM'")
    wait_stable(shell, 0.3)

    results["hsplit_initial"] = capture(
        shell, "hsplit_initial",
        "Horizontal split, bottom pane active, 'BOTTOM' echoed"
    )

    # Navigate up with 'k'
    send_prefix(shell)
    shell.send_keys('k')
    wait_stable(shell, 0.3)

    shell.send_line("echo 'TOP'")
    wait_stable(shell, 0.3)

    results["hsplit_after_k"] = capture(
        shell, "hsplit_after_k",
        "After Ctrl-B k: top pane active, 'TOP' echoed"
    )

    # Navigate down with 'j'
    send_prefix(shell)
    shell.send_keys('j')
    wait_stable(shell, 0.3)

    shell.send_line("echo 'BACK_BOTTOM'")
    wait_stable(shell, 0.3)

    results["hsplit_after_j"] = capture(
        shell, "hsplit_after_j",
        "After Ctrl-B j: bottom pane active, 'BACK_BOTTOM' echoed"
    )

    kill_tmux(shell)


def group_three_panes_hjkl(shell, results):
    """Three panes: left | (top-right / bottom-right). Navigate all with hjkl."""
    print("\n[GROUP 3] Three panes hjkl")

    start_tmux_with_hjkl(shell, "three_hjkl")

    # Vsplit: left | right
    send_prefix(shell)
    shell.send_keys('%')
    wait_stable(shell, 0.5)

    # Hsplit the right pane: left | (top-right / bottom-right)
    send_prefix(shell)
    shell.send_keys('"')
    wait_stable(shell, 0.5)

    # We're in bottom-right. Label it.
    shell.send_line("echo 'BR'")
    wait_stable(shell, 0.3)

    # k: go to top-right
    send_prefix(shell)
    shell.send_keys('k')
    wait_stable(shell, 0.3)
    shell.send_line("echo 'TR'")
    wait_stable(shell, 0.3)

    # h: go to left
    send_prefix(shell)
    shell.send_keys('h')
    wait_stable(shell, 0.3)
    shell.send_line("echo 'L'")
    wait_stable(shell, 0.3)

    results["three_panes_labeled"] = capture(
        shell, "three_panes_labeled",
        "Three panes labeled: L (left), TR (top-right), BR (bottom-right)"
    )

    # l: go right (should go to top-right or one of the right panes)
    send_prefix(shell)
    shell.send_keys('l')
    wait_stable(shell, 0.3)
    shell.send_line("echo 'NAVIGATED_RIGHT'")
    wait_stable(shell, 0.3)

    results["three_panes_l_from_left"] = capture(
        shell, "three_panes_l_from_left",
        "After l from left pane: moved to a right pane"
    )

    # j: go down (if in top-right, should go to bottom-right)
    send_prefix(shell)
    shell.send_keys('j')
    wait_stable(shell, 0.3)
    shell.send_line("echo 'NAVIGATED_DOWN'")
    wait_stable(shell, 0.3)

    results["three_panes_j_down"] = capture(
        shell, "three_panes_j_down",
        "After j: moved down within right column"
    )

    kill_tmux(shell)


def group_four_panes_grid(shell, results):
    """Four panes in a 2x2 grid. Navigate all directions."""
    print("\n[GROUP 4] Four panes 2x2 grid")

    start_tmux_with_hjkl(shell, "grid")

    # Create 2x2: vsplit, then hsplit each half
    send_prefix(shell)
    shell.send_keys('%')  # left | right
    wait_stable(shell, 0.5)

    # Hsplit right pane
    send_prefix(shell)
    shell.send_keys('"')  # left | (top-right / bottom-right)
    wait_stable(shell, 0.5)

    # Go to left pane
    send_prefix(shell)
    shell.send_keys('h')
    wait_stable(shell, 0.3)

    # Hsplit left pane
    send_prefix(shell)
    shell.send_keys('"')  # (top-left / bottom-left) | (top-right / bottom-right)
    wait_stable(shell, 0.5)

    # We're in bottom-left. Label all panes.
    shell.send_line("echo 'BL'")
    wait_stable(shell, 0.3)

    # k -> top-left
    send_prefix(shell)
    shell.send_keys('k')
    wait_stable(shell, 0.3)
    shell.send_line("echo 'TL'")
    wait_stable(shell, 0.3)

    # l -> top-right
    send_prefix(shell)
    shell.send_keys('l')
    wait_stable(shell, 0.3)
    shell.send_line("echo 'TR'")
    wait_stable(shell, 0.3)

    # j -> bottom-right
    send_prefix(shell)
    shell.send_keys('j')
    wait_stable(shell, 0.3)
    shell.send_line("echo 'BR'")
    wait_stable(shell, 0.3)

    results["grid_labeled"] = capture(
        shell, "grid_labeled",
        "2x2 grid labeled: TL, TR, BL, BR"
    )

    # Full circle: h -> bottom-left, k -> top-left, l -> top-right, j -> bottom-right
    send_prefix(shell)
    shell.send_keys('h')
    wait_stable(shell, 0.3)
    shell.send_line("echo 'CIRCLE_BL'")
    wait_stable(shell, 0.3)

    results["grid_h_to_bl"] = capture(
        shell, "grid_h_to_bl",
        "After h from BR: now in BL (or closest left pane)"
    )

    send_prefix(shell)
    shell.send_keys('k')
    wait_stable(shell, 0.3)
    shell.send_line("echo 'CIRCLE_TL'")
    wait_stable(shell, 0.3)

    results["grid_k_to_tl"] = capture(
        shell, "grid_k_to_tl",
        "After k from BL: now in TL"
    )

    send_prefix(shell)
    shell.send_keys('l')
    wait_stable(shell, 0.3)
    shell.send_line("echo 'CIRCLE_TR'")
    wait_stable(shell, 0.3)

    results["grid_l_to_tr"] = capture(
        shell, "grid_l_to_tr",
        "After l from TL: now in TR"
    )

    send_prefix(shell)
    shell.send_keys('j')
    wait_stable(shell, 0.3)
    shell.send_line("echo 'CIRCLE_BR'")
    wait_stable(shell, 0.3)

    results["grid_j_to_br"] = capture(
        shell, "grid_j_to_br",
        "After j from TR: now in BR"
    )

    kill_tmux(shell)


def group_deep_vsplits(shell, results):
    """Three vertical splits: 4 columns. Navigate all with h/l."""
    print("\n[GROUP 5] Deep vertical splits (4 columns)")

    start_tmux_with_hjkl(shell, "deepv")

    # Create 4 vertical panes
    send_prefix(shell)
    shell.send_keys('%')
    wait_stable(shell, 0.5)

    send_prefix(shell)
    shell.send_keys('%')
    wait_stable(shell, 0.5)

    send_prefix(shell)
    shell.send_keys('%')
    wait_stable(shell, 0.5)

    # We should be in the rightmost pane. Label it.
    shell.send_line("echo 'P4'")
    wait_stable(shell, 0.3)

    # h three times to get to leftmost
    for i in range(3):
        send_prefix(shell)
        shell.send_keys('h')
        wait_stable(shell, 0.3)

    shell.send_line("echo 'P1'")
    wait_stable(shell, 0.3)

    results["deep_vsplit_leftmost"] = capture(
        shell, "deep_vsplit_leftmost",
        "4 vertical panes, in leftmost after 3x h"
    )

    # l three times to get back to rightmost
    for i in range(3):
        send_prefix(shell)
        shell.send_keys('l')
        wait_stable(shell, 0.3)

    shell.send_line("echo 'P4_BACK'")
    wait_stable(shell, 0.3)

    results["deep_vsplit_rightmost"] = capture(
        shell, "deep_vsplit_rightmost",
        "4 vertical panes, in rightmost after 3x l"
    )

    kill_tmux(shell)


def group_deep_hsplits(shell, results):
    """Three horizontal splits: 4 rows. Navigate all with j/k."""
    print("\n[GROUP 6] Deep horizontal splits (4 rows)")

    start_tmux_with_hjkl(shell, "deeph")

    # Create 4 horizontal panes
    send_prefix(shell)
    shell.send_keys('"')
    wait_stable(shell, 0.5)

    send_prefix(shell)
    shell.send_keys('"')
    wait_stable(shell, 0.5)

    send_prefix(shell)
    shell.send_keys('"')
    wait_stable(shell, 0.5)

    # We should be in the bottom pane. Label it.
    shell.send_line("echo 'P4'")
    wait_stable(shell, 0.3)

    # k three times to get to top
    for i in range(3):
        send_prefix(shell)
        shell.send_keys('k')
        wait_stable(shell, 0.3)

    shell.send_line("echo 'P1'")
    wait_stable(shell, 0.3)

    results["deep_hsplit_top"] = capture(
        shell, "deep_hsplit_top",
        "4 horizontal panes, in topmost after 3x k"
    )

    # j three times to get back to bottom
    for i in range(3):
        send_prefix(shell)
        shell.send_keys('j')
        wait_stable(shell, 0.3)

    shell.send_line("echo 'P4_BACK'")
    wait_stable(shell, 0.3)

    results["deep_hsplit_bottom"] = capture(
        shell, "deep_hsplit_bottom",
        "4 horizontal panes, in bottommost after 3x j"
    )

    kill_tmux(shell)


def group_nested_splits(shell, results):
    """Complex nested splits: vsplit, hsplit left, vsplit bottom-left."""
    print("\n[GROUP 7] Complex nested splits")

    start_tmux_with_hjkl(shell, "nested")

    # vsplit: L | R
    send_prefix(shell)
    shell.send_keys('%')
    wait_stable(shell, 0.5)

    # Go left
    send_prefix(shell)
    shell.send_keys('h')
    wait_stable(shell, 0.3)

    # hsplit left: TL / BL | R
    send_prefix(shell)
    shell.send_keys('"')
    wait_stable(shell, 0.5)

    # Now in BL. Vsplit it: TL / (BL-L | BL-R) | R
    send_prefix(shell)
    shell.send_keys('%')
    wait_stable(shell, 0.5)

    # We should be in BL-R. Label everything.
    shell.send_line("echo 'BLR'")
    wait_stable(shell, 0.3)

    send_prefix(shell)
    shell.send_keys('h')
    wait_stable(shell, 0.3)
    shell.send_line("echo 'BLL'")
    wait_stable(shell, 0.3)

    send_prefix(shell)
    shell.send_keys('k')
    wait_stable(shell, 0.3)
    shell.send_line("echo 'TL'")
    wait_stable(shell, 0.3)

    send_prefix(shell)
    shell.send_keys('l')
    wait_stable(shell, 0.3)
    shell.send_line("echo 'R'")
    wait_stable(shell, 0.3)

    results["nested_labeled"] = capture(
        shell, "nested_labeled",
        "Nested splits labeled: TL, BLL, BLR, R"
    )

    # Navigate from R -> h -> should go to TL or BLR (whichever is adjacent)
    send_prefix(shell)
    shell.send_keys('h')
    wait_stable(shell, 0.3)
    shell.send_line("echo 'FROM_R_H'")
    wait_stable(shell, 0.3)

    results["nested_r_h"] = capture(
        shell, "nested_r_h",
        "After h from R pane"
    )

    kill_tmux(shell)


def group_last_window(shell, results):
    """Test Ctrl-B L (uppercase) for last window toggle."""
    print("\n[GROUP 8] Last window (Ctrl-B L)")

    start_tmux_with_hjkl(shell, "lastwin")

    # We're in window 0. Create window 1.
    send_prefix(shell)
    shell.send_keys('c')
    wait_stable(shell, 0.5)

    # Now in window 1
    shell.send_line("echo 'WIN1'")
    wait_stable(shell, 0.3)

    results["lastwin_win1"] = capture(
        shell, "lastwin_win1",
        "Window 1 active, 'WIN1' echoed"
    )

    # L -> toggle to last window (window 0)
    send_prefix(shell)
    shell.send_keys('L')
    wait_stable(shell, 0.3)

    shell.send_line("echo 'BACK_WIN0'")
    wait_stable(shell, 0.3)

    results["lastwin_toggle_back"] = capture(
        shell, "lastwin_toggle_back",
        "After Ctrl-B L: back in window 0"
    )

    # L again -> toggle back to window 1
    send_prefix(shell)
    shell.send_keys('L')
    wait_stable(shell, 0.3)

    shell.send_line("echo 'TOGGLE_WIN1'")
    wait_stable(shell, 0.3)

    results["lastwin_toggle_again"] = capture(
        shell, "lastwin_toggle_again",
        "After second Ctrl-B L: back in window 1"
    )

    kill_tmux(shell)


def group_edge_cases(shell, results):
    """Edge cases: h at leftmost, l at rightmost, j at bottom, k at top."""
    print("\n[GROUP 9] Edge cases (no-op at boundary)")

    start_tmux_with_hjkl(shell, "edges")

    # Vsplit: left | right
    send_prefix(shell)
    shell.send_keys('%')
    wait_stable(shell, 0.5)

    # Go left
    send_prefix(shell)
    shell.send_keys('h')
    wait_stable(shell, 0.3)
    shell.send_line("echo 'AT_LEFT'")
    wait_stable(shell, 0.3)

    # Try h again (already leftmost — should stay)
    send_prefix(shell)
    shell.send_keys('h')
    wait_stable(shell, 0.3)
    shell.send_line("echo 'STILL_LEFT'")
    wait_stable(shell, 0.3)

    results["edge_h_at_left"] = capture(
        shell, "edge_h_at_left",
        "After h when already at leftmost: still in left pane"
    )

    # Go right
    send_prefix(shell)
    shell.send_keys('l')
    wait_stable(shell, 0.3)

    # Try l again (already rightmost)
    send_prefix(shell)
    shell.send_keys('l')
    wait_stable(shell, 0.3)
    shell.send_line("echo 'STILL_RIGHT'")
    wait_stable(shell, 0.3)

    results["edge_l_at_right"] = capture(
        shell, "edge_l_at_right",
        "After l when already at rightmost: still in right pane"
    )

    kill_tmux(shell)


# ═══════════════════════════════════════════════════════════════

def main():
    print(f"[CAPTURE] Tmux pane navigation capture ({ROWS}x{COLS})")
    print("  Testing hjkl bindings, arrow keys, last-window, and complex layouts")

    shell = ShellPilot(rows=ROWS, cols=COLS)
    results = {}
    groups = [
        group_vsplit_hjkl,
        group_hsplit_jk,
        group_three_panes_hjkl,
        group_four_panes_grid,
        group_deep_vsplits,
        group_deep_hsplits,
        group_nested_splits,
        group_last_window,
        group_edge_cases,
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
                safe_kill_tmux(shell)
                wait_stable(shell, 1.0)

    finally:
        try:
            shell.stop()
        except Exception:
            pass

    # Write results
    out = _here / "tmux_pane_nav_ground_truth.json"
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\n[CAPTURE] Wrote {len(results)} scenarios -> {out}")

    # Summary
    print(f"\n{'=' * 70}")
    print("CAPTURE SUMMARY")
    print(f"{'=' * 70}")
    for name, sc in results.items():
        cursor = sc.get("cursor", {})
        desc = sc.get("description", "")[:60]
        print(f"  {name:40s} cursor=({cursor.get('row', '?')},{cursor.get('col', '?'):>2})  {desc}")
    print(f"\nTotal: {len(results)} scenarios captured")


if __name__ == "__main__":
    main()
