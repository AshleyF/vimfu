"""
Capture real Neovim behavior for :r (read) command and Tab completion.

Creates test files in the current directory, launches nvim via ShellPilot,
captures screen state, then cleans up.

Usage:
    cd sim/test
    python capture_nvim_read.py
"""

from __future__ import annotations

import json
import os
import sys
import time
import tempfile
from pathlib import Path

_here = Path(__file__).resolve().parent
_root = _here.parent.parent  # vimfu/
sys.path.insert(0, str(_root / "shellpilot"))

from shell_pty import ShellPilot
from capture_frames import capture_frame

ROWS = 20
COLS = 80

# Test files we create in cwd for completion tests
TEST_FILES = {
    "demo.py": 'def hello():\n    print("hi")\n',
    "demo.txt": "Hello world\nLine two\n",
    "notes.txt": "Shopping list\n  - milk\n  - eggs\n",
}


def wait_for_nvim(shell, text="", timeout=10):
    """Wait for nvim to render."""
    wait_for = text[:10].strip() if text else "~"
    deadline = time.time() + timeout
    while time.time() < deadline:
        screen_text = shell.get_screen_text()
        if wait_for in screen_text:
            break
        time.sleep(0.1)
    else:
        raise RuntimeError(f"Neovim did not render within {timeout}s (waiting for {wait_for!r})")
    time.sleep(0.15)


def run_scenario(name, main_file, main_content, keys, settle=0.4):
    """Run a single nvim scenario and capture the screen state."""
    main_file.write_text(main_content, encoding="utf-8")

    shell = ShellPilot(
        shell=f'nvim -u NONE -n -i NONE {main_file.name}',
        rows=ROWS,
        cols=COLS,
    )
    try:
        shell.start()
        wait_for_nvim(shell, main_content)

        # Feed keys — send escape sequences as atomic units
        i = 0
        while i < len(keys):
            ch = keys[i]
            if ch == '\x1b' and i + 2 < len(keys) and keys[i + 1] == '[':
                # CSI escape sequence: find the terminator
                j = i + 2
                while j < len(keys) and keys[j] not in 'ABCDEFGHJKSTfmnsu~':
                    j += 1
                if j < len(keys):
                    j += 1  # include terminator
                shell.send_keys(keys[i:j])
                i = j
            elif ch == '\t':
                shell.send_keys('\t')
                i += 1
                time.sleep(0.15)  # Tab completion needs time
            else:
                shell.send_keys(ch)
                i += 1
            time.sleep(0.04)

        time.sleep(settle)

        frame = capture_frame(shell.screen)
        text_lines = [line["text"] for line in frame["lines"]]
        cmd_line = text_lines[-1] if text_lines else ""

        return {
            "name": name,
            "keys": repr(keys),
            "frame": frame,
            "cursor": frame["cursor"],
            "textLines": text_lines,
            "cmdLine": cmd_line,
            "bufferLines": text_lines[:ROWS - 2],  # exclude status + cmd lines
        }
    finally:
        try:
            shell.send_keys('\x1b:q!\r')
            time.sleep(0.3)
        except Exception:
            pass
        try:
            shell.stop()
        except Exception:
            pass


def setup_test_files():
    """Create test files in current directory."""
    for name, content in TEST_FILES.items():
        Path(name).write_text(content, encoding="utf-8")


def cleanup_test_files():
    """Remove test files from current directory."""
    for name in list(TEST_FILES.keys()) + ["main.txt"]:
        try:
            Path(name).unlink()
        except FileNotFoundError:
            pass


def main():
    results = {}
    main_file = Path("main.txt")
    initial = "Line one\nLine two\nLine three"

    setup_test_files()
    try:
        # ── :r file (read file into buffer) ──

        print("=== :r command behavior ===")

        # 1. :r demo.py – read python file below cursor (cursor on line 1)
        print("  [1] :r demo.py ...", end=" ", flush=True)
        r = run_scenario("r_demo_py", main_file, initial, ":r demo.py\r")
        results["r_demo_py"] = r
        print(f"OK cursor=({r['cursor']['row']},{r['cursor']['col']})")

        # 2. :r demo.txt – read text file
        print("  [2] :r demo.txt ...", end=" ", flush=True)
        r = run_scenario("r_demo_txt", main_file, initial, ":r demo.txt\r")
        results["r_demo_txt"] = r
        print(f"OK cursor=({r['cursor']['row']},{r['cursor']['col']})")

        # 3. :r notes.txt on last line
        print("  [3] :r notes.txt on last line ...", end=" ", flush=True)
        r = run_scenario("r_notes_last_line", main_file, initial, "G:r notes.txt\r")
        results["r_notes_last_line"] = r
        print(f"OK cursor=({r['cursor']['row']},{r['cursor']['col']})")

        # 4. :r nonexistent – error
        print("  [4] :r nonexistent ...", end=" ", flush=True)
        r = run_scenario("r_nonexistent", main_file, initial, ":r nonexistent\r")
        results["r_nonexistent"] = r
        print(f"OK cmd={r['cmdLine'][:50]}")

        # 5. :r demo.py after moving to line 2
        print("  [5] :r demo.py on line 2 ...", end=" ", flush=True)
        r = run_scenario("r_demo_py_line2", main_file, initial, "j:r demo.py\r")
        results["r_demo_py_line2"] = r
        print(f"OK cursor=({r['cursor']['row']},{r['cursor']['col']})")

        # ── Tab completion in command line ──

        print("\n=== Tab completion behavior ===")

        # 6. :r <Tab> – first tab with no partial
        print("  [6] :r <Tab> ...", end=" ", flush=True)
        r = run_scenario("r_tab_no_partial", main_file, initial, ":r \t")
        results["r_tab_no_partial"] = r
        print(f"OK cmd={r['cmdLine'][:60]}")

        # 7. :r d<Tab> – partial 'd' with multiple matches
        print("  [7] :r d<Tab> ...", end=" ", flush=True)
        r = run_scenario("r_tab_partial_d", main_file, initial, ":r d\t")
        results["r_tab_partial_d"] = r
        print(f"OK cmd={r['cmdLine'][:60]}")

        # 8. :r d<Tab><Tab> – cycle to second match
        print("  [8] :r d<Tab><Tab> ...", end=" ", flush=True)
        r = run_scenario("r_tab_partial_d_2", main_file, initial, ":r d\t\t")
        results["r_tab_partial_d_2"] = r
        print(f"OK cmd={r['cmdLine'][:60]}")

        # 9. :r n<Tab> – unique match 'notes.txt'
        print("  [9] :r n<Tab> ...", end=" ", flush=True)
        r = run_scenario("r_tab_partial_n", main_file, initial, ":r n\t")
        results["r_tab_partial_n"] = r
        print(f"OK cmd={r['cmdLine'][:60]}")

        # 10. :e <Tab> – edit tab completion
        print("  [10] :e <Tab> ...", end=" ", flush=True)
        r = run_scenario("e_tab_no_partial", main_file, initial, ":e \t")
        results["e_tab_no_partial"] = r
        print(f"OK cmd={r['cmdLine'][:60]}")

        # 11. :e d<Tab> – edit partial completion
        print("  [11] :e d<Tab> ...", end=" ", flush=True)
        r = run_scenario("e_tab_partial_d", main_file, initial, ":e d\t")
        results["e_tab_partial_d"] = r
        print(f"OK cmd={r['cmdLine'][:60]}")

        # 12. :r demo.<Tab> – partial with dot
        print("  [12] :r demo.<Tab> ...", end=" ", flush=True)
        r = run_scenario("r_tab_partial_demo_dot", main_file, initial, ":r demo.\t")
        results["r_tab_partial_demo_dot"] = r
        print(f"OK cmd={r['cmdLine'][:60]}")

        # 13. :r demo.<Tab><Tab> – cycle after dot
        print("  [13] :r demo.<Tab><Tab> ...", end=" ", flush=True)
        r = run_scenario("r_tab_partial_demo_dot_2", main_file, initial, ":r demo.\t\t")
        results["r_tab_partial_demo_dot_2"] = r
        print(f"OK cmd={r['cmdLine'][:60]}")

        # 14. :r z<Tab> – no matches
        print("  [14] :r z<Tab> ...", end=" ", flush=True)
        r = run_scenario("r_tab_no_match", main_file, initial, ":r z\t")
        results["r_tab_no_match"] = r
        print(f"OK cmd={r['cmdLine'][:60]}")

        # 15. :w <Tab> – write tab completion
        print("  [15] :w <Tab> ...", end=" ", flush=True)
        r = run_scenario("w_tab_no_partial", main_file, initial, ":w \t")
        results["w_tab_no_partial"] = r
        print(f"OK cmd={r['cmdLine'][:60]}")

    finally:
        cleanup_test_files()

    # Write results
    out_path = _here / "nvim_read_ground_truth.json"
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nWrote {out_path.name} ({len(results)} scenarios)")

    # Print summary
    print(f"\n{'='*60}")
    print("Summary of command lines after Tab:")
    print(f"{'='*60}")
    for name, r in results.items():
        if "tab" in name:
            print(f"  {name:30s} -> {r['cmdLine'].rstrip()}")

    print(f"\nBuffer contents after :r:")
    print(f"{'='*60}")
    for name, r in results.items():
        if not "tab" in name and not "nonexist" in name:
            print(f"\n  --- {name} ---")
            for i, line in enumerate(r['bufferLines']):
                print(f"  {i:2d}: {line.rstrip()}")


if __name__ == "__main__":
    main()
