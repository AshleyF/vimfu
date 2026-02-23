"""
Capture real tmux's actual colors via ShellPilot.

Launches tmux inside a real terminal (via WSL), captures frames at
various states (fresh launch, splits, status bar, etc.), and writes
the color data to tmux_real_colors.json.

The sim's tmux theme must match these captured colors exactly.

Usage:
    cd sim
    C:/source/vimfu/.venv/Scripts/python.exe test/capture_tmux_colors.py
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

# Add shellpilot to path
_here = Path(__file__).resolve().parent
_root = _here.parent.parent  # vimfu/
sys.path.insert(0, str(_root / "shellpilot"))

from shell_pty import ShellPilot
from capture_frames import capture_frame

ROWS = 20
COLS = 40


def wait_for_text(shell, text, timeout=10.0):
    """Wait for text to appear on screen."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        screen_text = shell.get_screen_text()
        if text in screen_text:
            return True
        time.sleep(0.1)
    return False


def wait_stable(shell, seconds=0.5):
    """Wait for screen to stabilize."""
    time.sleep(seconds)


def send_ctrl(shell, char):
    """Send Ctrl+<char>."""
    code = ord(char.upper()) - ord('A') + 1
    shell.send_keys(chr(code))


def capture_scenario(shell, label, description):
    """Capture a frame and return scenario dict."""
    frame = capture_frame(shell.screen)
    return {
        "label": label,
        "description": description,
        "frame": frame,
    }


def main():
    print(f"[CAPTURE] Starting tmux color capture ({ROWS}x{COLS})")
    print(f"[CAPTURE] Using ShellPilot → WSL → tmux")

    shell = ShellPilot(rows=ROWS, cols=COLS)
    results = {}

    try:
        shell.start()
        wait_stable(shell, 2.0)

        # Make sure we have a clean prompt
        screen_text = shell.get_screen_text()
        print(f"[CAPTURE] Initial screen (first 3 lines):")
        for line in shell.get_screen()[:3]:
            print(f"  {repr(line)}")

        # ── Scenario 1: Fresh tmux launch ──
        print("\n[CAPTURE] Launching tmux...")
        shell.send_line("tmux new-session -s test")
        time.sleep(2.0)

        # Verify tmux is running (status bar should appear)
        screen = shell.get_screen()
        last_line = screen[-1] if screen else ""
        print(f"[CAPTURE] Status bar: {repr(last_line)}")
        if "[test]" not in last_line and "test" not in last_line:
            print("[WARN] tmux status bar not detected, trying anyway...")

        results["tmux_fresh"] = capture_scenario(
            shell, "tmux_fresh",
            "Fresh tmux launch — single pane, status bar visible"
        )

        # ── Scenario 2: Vertical split ──
        print("[CAPTURE] Vertical split (Ctrl-B %)...")
        send_ctrl(shell, 'b')
        time.sleep(0.2)
        shell.send_keys('%')
        wait_stable(shell, 0.5)

        results["tmux_vsplit"] = capture_scenario(
            shell, "tmux_vsplit",
            "Vertical split — two panes side by side with border"
        )

        # ── Scenario 3: Close right pane, back to single ──
        print("[CAPTURE] Closing right pane...")
        shell.send_line("exit")
        wait_stable(shell, 0.5)

        # ── Scenario 4: Horizontal split ──
        print("[CAPTURE] Horizontal split (Ctrl-B \")...")
        send_ctrl(shell, 'b')
        time.sleep(0.2)
        shell.send_keys('"')
        wait_stable(shell, 0.5)

        results["tmux_hsplit"] = capture_scenario(
            shell, "tmux_hsplit",
            "Horizontal split — two panes stacked with border"
        )

        # Close bottom pane
        print("[CAPTURE] Closing bottom pane...")
        shell.send_line("exit")
        wait_stable(shell, 0.5)

        # ── Scenario 5: Two windows (status bar) ──
        print("[CAPTURE] Creating second window (Ctrl-B c)...")
        send_ctrl(shell, 'b')
        time.sleep(0.2)
        shell.send_keys('c')
        wait_stable(shell, 0.5)

        results["tmux_two_windows"] = capture_scenario(
            shell, "tmux_two_windows",
            "Status bar with two windows"
        )

        # ── Scenario 6: Renamed window ──
        print("[CAPTURE] Renaming window (Ctrl-B ,)...")
        send_ctrl(shell, 'b')
        time.sleep(0.2)
        shell.send_keys(',')
        wait_stable(shell, 0.3)
        # Clear existing name and type new one
        send_ctrl(shell, 'u')
        time.sleep(0.1)
        shell.send_keys('myterm')
        time.sleep(0.1)
        shell.send_keys('\r')
        wait_stable(shell, 0.5)

        results["tmux_renamed"] = capture_scenario(
            shell, "tmux_renamed",
            "Status bar after renaming window to myterm"
        )

        # Go back to window 0 for remaining tests
        send_ctrl(shell, 'b')
        time.sleep(0.2)
        shell.send_keys('0')
        wait_stable(shell, 0.3)

        # ── Scenario 7: Vsplit with active pane right ──
        print("[CAPTURE] Vsplit active right...")
        send_ctrl(shell, 'b')
        time.sleep(0.2)
        shell.send_keys('%')
        wait_stable(shell, 0.5)

        results["tmux_vsplit_active_right"] = capture_scenario(
            shell, "tmux_vsplit_active_right",
            "Vsplit with right pane active — border color test"
        )

        # ── Scenario 8: Navigate left ──
        print("[CAPTURE] Navigate to left pane...")
        send_ctrl(shell, 'b')
        time.sleep(0.2)
        shell.send_keys('\x1b[D')  # Left arrow
        wait_stable(shell, 0.3)

        results["tmux_vsplit_active_left"] = capture_scenario(
            shell, "tmux_vsplit_active_left",
            "Vsplit with left pane active — border color test"
        )

        # Close right pane (navigate right first)
        send_ctrl(shell, 'b')
        time.sleep(0.2)
        shell.send_keys('\x1b[C')  # Right arrow
        wait_stable(shell, 0.2)
        shell.send_line("exit")
        wait_stable(shell, 0.5)

        # ── Scenario 9: Command prompt ──
        print("[CAPTURE] Command prompt (Ctrl-B :)...")
        send_ctrl(shell, 'b')
        time.sleep(0.2)
        shell.send_keys(':')
        wait_stable(shell, 0.3)

        results["tmux_command_prompt"] = capture_scenario(
            shell, "tmux_command_prompt",
            "Command prompt visible on status bar"
        )

        # Cancel command prompt
        shell.send_keys('\x1b')  # Escape
        wait_stable(shell, 0.3)

        # ── Scenario 10: Copy mode ──
        print("[CAPTURE] Copy mode (Ctrl-B [)...")
        send_ctrl(shell, 'b')
        time.sleep(0.2)
        shell.send_keys('[')
        wait_stable(shell, 0.5)

        results["tmux_copy_mode"] = capture_scenario(
            shell, "tmux_copy_mode",
            "Copy mode with indicator on status bar"
        )

        # Exit copy mode
        shell.send_keys('q')
        wait_stable(shell, 0.3)

        # ── Cleanup: exit tmux ──
        print("[CAPTURE] Exiting tmux...")
        # Kill all windows
        send_ctrl(shell, 'b')
        time.sleep(0.2)
        shell.send_keys(':')
        time.sleep(0.2)
        shell.send_line("kill-session")
        wait_stable(shell, 1.0)

    finally:
        try:
            shell.stop()
        except Exception:
            pass

    # ── Write results ──
    out = _here / "tmux_real_colors.json"
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\n[CAPTURE] Wrote {len(results)} scenarios → {out}")

    # ── Print color summary ──
    print("\n" + "=" * 70)
    print("TMUX COLOR SUMMARY")
    print("=" * 70)

    for name, scenario in results.items():
        frame = scenario["frame"]
        print(f"\n── {name}: {scenario['description']} ──")

        # Show last row (status bar) in detail
        last = frame["lines"][-1]
        print(f"  Status bar text: {repr(last['text'])}")
        col = 0
        for run in last["runs"]:
            text_slice = last["text"][col:col + run["n"]]
            flags = ""
            if run.get("b"):
                flags += " BOLD"
            print(f"    [{col:3d}-{col + run['n'] - 1:3d}] fg={run['fg']} bg={run['bg']}{flags} '{text_slice}'")
            col += run["n"]

        # If split, show border colors
        for i, line in enumerate(frame["lines"][:-1]):
            for run in line["runs"]:
                # Look for single-column border characters
                if run["n"] == 1 and run["fg"] not in ("d4d4d4", "000000"):
                    start = sum(r["n"] for r in line["runs"][:line["runs"].index(run)])
                    ch = line["text"][start:start + 1]
                    if ch in "│─┌┐└┘├┤┬┴┼|":
                        print(f"  Border at row {i}: fg={run['fg']} bg={run['bg']} char='{ch}'")
                        break

    # Collect all unique status bar colors across scenarios
    print("\n" + "=" * 70)
    print("UNIQUE STATUS BAR COLORS")
    print("=" * 70)
    status_colors = set()
    for name, scenario in results.items():
        last = scenario["frame"]["lines"][-1]
        for run in last["runs"]:
            status_colors.add((run["fg"], run["bg"]))
    for fg, bg in sorted(status_colors):
        print(f"  fg={fg} bg={bg}")


if __name__ == "__main__":
    main()
