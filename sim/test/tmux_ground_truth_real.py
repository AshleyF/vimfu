"""
Tmux ground-truth generator — captures frames from REAL tmux via ShellPilot.

For each test case in cases/test_tmux_screen.py, this script:
  1. Starts a ShellPilot session (WSL bash)
  2. Kills any existing tmux, launches a fresh session
  3. Sends the scenario's steps (commands, keys, waits)
  4. Captures the frame (text + colors + cursor) via pyte
  5. Writes the result to ground_truth_tmux_screen.json

The comparator (compare_tmux_screen.js) then replays the same scenario
through the sim's SessionManager and diffs the frames.

Usage:
    cd sim
    C:/source/vimfu/.venv/Scripts/python.exe test/tmux_ground_truth_real.py
    C:/source/vimfu/.venv/Scripts/python.exe test/tmux_ground_truth_real.py --case tmux_vsplit
    C:/source/vimfu/.venv/Scripts/python.exe test/tmux_ground_truth_real.py --list
"""

from __future__ import annotations

import importlib.util
import json
import sys
import time
from pathlib import Path

# Add paths
_here = Path(__file__).resolve().parent
_root = _here.parent.parent  # vimfu/
sys.path.insert(0, str(_root / "shellpilot"))
sys.path.insert(0, str(_here))  # for cases package

from shell_pty import ShellPilot
from capture_frames import capture_frame

# ── Screen dimensions (must match the sim's defaults) ──
ROWS = 20
COLS = 40

CTRL_B = "\x02"


def load_cases() -> dict:
    """Load test cases from cases/test_tmux_screen.py."""
    spec = importlib.util.spec_from_file_location(
        "test_tmux_screen",
        _here / "cases" / "test_tmux_screen.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.CASES


def wait_for_text(shell, text, timeout=10.0):
    """Wait for text to appear on screen."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        screen_text = shell.get_screen_text()
        if text in screen_text:
            return True
        time.sleep(0.1)
    print(f"    [WARN] wait_for_text({text!r}) timed out after {timeout}s")
    return False


def freeze_status_bar_time(frame):
    """Replace live clock/date with fixed placeholders for determinism."""
    import re
    for i, line in enumerate(frame["lines"]):
        text = line["text"]
        new_text = re.sub(r'\d{2}:\d{2}', '00:00', text)
        new_text = re.sub(r'\d{1,2}-[A-Z][a-z]{2}-\d{2}', '01-Jan-26', new_text)
        if new_text != text:
            line["text"] = new_text


def normalize_prompt(frame, rows=ROWS):
    """
    Normalize shell prompt differences between real bash and the sim.

    Real bash prompt: user@host:~$  (varies by system)
    Sim prompt: $

    We replace the real prompt with just "$ " so text comparison can focus
    on the tmux structure (borders, status bar, overlays, vim content)
    rather than prompt cosmetics.
    """
    import re
    for line in frame["lines"]:
        # Match common bash prompts: user@host:path$
        # But be careful not to clobber non-prompt lines
        text = line["text"]
        # Match: anything ending with "$ " preceded by user@host:path
        new_text = re.sub(
            r'[a-zA-Z0-9_-]+@[a-zA-Z0-9_.-]+:[~/.a-zA-Z0-9_-]*\$\s',
            '$ ',
            text,
        )
        if new_text != text:
            # Pad to original length
            if len(new_text) < len(text):
                new_text = new_text + " " * (len(text) - len(new_text))
            line["text"] = new_text[:len(text)]


def run_case(name: str, case: dict) -> dict | None:
    """Run a single test case against real tmux and return captured state."""
    steps = case["steps"]
    description = case.get("description", name)
    write_files = case.get("write_files", {})

    shell = ShellPilot(rows=ROWS, cols=COLS)
    try:
        shell.start()
        time.sleep(1.5)  # let WSL bash start

        # Create any needed files in the test working directory
        # (must happen after the _TMUX_LAUNCH creates the temp dir but before tmux starts)
        # We write them to /tmp/vimfu_test_workdir since that's where tmux will cd to
        for fname, content in write_files.items():
            escaped = content.replace("'", "'\\''")
            shell.send_line(f"mkdir -p /tmp/vimfu_test_workdir && printf '%s' '{escaped}' > /tmp/vimfu_test_workdir/{fname}")
            time.sleep(0.2)

        # Execute steps
        for step in steps:
            if step[0] == "line":
                shell.send_line(step[1])
            elif step[0] == "keys":
                shell.send_keys(step[1])
            elif step[0] == "wait":
                wait_for_text(shell, step[1], timeout=step[2] if len(step) > 2 else 10.0)
            elif step[0] == "sleep":
                time.sleep(step[1])
            else:
                print(f"    [WARN] Unknown step type: {step[0]}")

        # Let everything settle
        time.sleep(0.3)

        # Capture frame
        frame = capture_frame(shell.screen)
        freeze_status_bar_time(frame)

        text_lines = [line["text"] for line in frame["lines"]]

        return {
            "description": description,
            "frame": frame,
            "textLines": text_lines,
            "cursor": frame["cursor"],
            "screenRows": ROWS,
            "screenCols": COLS,
        }

    except Exception as e:
        print(f"    ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

    finally:
        # Clean up: kill tmux, remove temp files
        try:
            shell.send_keys("\x03")  # Ctrl-C to cancel anything
            time.sleep(0.1)
            shell.send_line("tmux kill-server 2>/dev/null")
            time.sleep(0.3)
            for fname in write_files:
                shell.send_line(f"rm -f {fname}")
            time.sleep(0.1)
        except Exception:
            pass
        try:
            shell.stop()
        except Exception:
            pass


def main():
    import argparse
    import gc
    import subprocess
    ap = argparse.ArgumentParser(description="Tmux ground-truth generator (real tmux)")
    ap.add_argument("--case", "-c", default=None, help="Run only this case")
    ap.add_argument("--list", "-l", action="store_true", help="List all cases")
    ap.add_argument("--batch", "-b", action="store_true",
                    help="Run each case in a separate subprocess (more reliable)")
    ap.add_argument("--merge", action="store_true",
                    help="Merge result into existing JSON (used by --batch)")
    args = ap.parse_args()

    cases = load_cases()

    if args.list:
        for name, case in cases.items():
            print(f"  {name}: {case.get('description', '')}")
        print(f"\n  TOTAL: {len(cases)} cases")
        return

    # ── Batch mode: fork one subprocess per case ──
    if args.batch:
        out_file = _here / "ground_truth_tmux_screen.json"
        # Start fresh
        results = {}
        if out_file.exists():
            try:
                results = json.loads(out_file.read_text("utf-8"))
            except Exception:
                results = {}

        total = len(cases) if not args.case else 1
        case_names = [args.case] if args.case else list(cases.keys())
        passed = 0
        failed = 0

        print(f"{'='*60}")
        print(f"Tmux Ground Truth Generator (BATCH mode)")
        print(f"Screen: {ROWS}x{COLS}")
        print(f"Cases: {len(case_names)}")
        print(f"{'='*60}")

        for i, name in enumerate(case_names, 1):
            print(f"\n  [{i}/{len(case_names)}] {name} ...", end=" ", flush=True)
            # Run this case in a subprocess
            cmd = [
                sys.executable,
                str(Path(__file__).resolve()),
                "--case", name, "--merge",
            ]
            try:
                cp = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=60,
                    cwd=str(_root),
                )
                if cp.returncode == 0:
                    # Reload the merged result
                    try:
                        merged = json.loads(out_file.read_text("utf-8"))
                        if name in merged and "error" not in merged[name]:
                            r = merged[name]["cursor"]["row"]
                            c = merged[name]["cursor"]["col"]
                            print(f"OK  cursor=({r},{c})")
                            passed += 1
                        else:
                            print(f"FAILED (in subprocess)")
                            failed += 1
                    except Exception:
                        print("FAILED (can't read result)")
                        failed += 1
                else:
                    print(f"CRASHED (exit {cp.returncode})")
                    if cp.stderr:
                        for line in cp.stderr.strip().split('\n')[-3:]:
                            print(f"    {line}")
                    failed += 1
            except subprocess.TimeoutExpired:
                print("TIMEOUT (60s)")
                failed += 1

            time.sleep(0.5)  # breathing room between subprocesses

        print(f"\n{'='*60}")
        print(f"RESULTS: {passed} passed, {failed} failed")
        final = json.loads(out_file.read_text("utf-8")) if out_file.exists() else {}
        print(f"Ground truth file has {len(final)} cases")
        print(f"{'='*60}")
        return

    # ── Single case + merge mode ──
    if args.case:
        if args.case not in cases:
            print(f"Unknown case: {args.case}")
            print(f"Available: {', '.join(cases)}")
            sys.exit(1)
        run_cases = {args.case: cases[args.case]}
    else:
        run_cases = cases

    results = {}
    total = len(run_cases)
    errors = 0

    if not args.merge:
        print(f"{'='*60}")
        print(f"Tmux Ground Truth Generator (REAL tmux via ShellPilot)")
        print(f"Screen: {ROWS}x{COLS}")
        print(f"Cases: {total}")
        print(f"{'='*60}")

    for i, (name, case) in enumerate(run_cases.items(), 1):
        if not args.merge:
            print(f"\n  [{i}/{total}] {name} ...", end=" ", flush=True)

        try:
            result = run_case(name, case)
        except Exception as e:
            if not args.merge:
                print(f"OUTER ERROR: {e}")
            import traceback
            traceback.print_exc()
            result = {"error": str(e)}

        if result and "error" not in result:
            if not args.merge:
                r, c = result["cursor"]["row"], result["cursor"]["col"]
                print(f"OK  cursor=({r},{c})")
            results[name] = result
        elif result and "error" in result:
            if not args.merge:
                print(f"FAILED: {result['error']}")
            results[name] = result
            errors += 1
        else:
            if not args.merge:
                print("FAILED: no result")
            errors += 1

        # Force garbage collection to free pywinpty resources
        gc.collect()

    # Write output (merge mode: merge into existing file)
    out_file = _here / "ground_truth_tmux_screen.json"
    if args.merge and out_file.exists():
        try:
            existing = json.loads(out_file.read_text("utf-8"))
        except Exception:
            existing = {}
        existing.update(results)
        results = existing

    out_file.write_text(json.dumps(results, indent=2), encoding="utf-8")
    if not args.merge:
        print(f"\n{'='*60}")
        print(f"Wrote {len(results)} cases → {out_file.name}")
        print(f"Errors: {errors}")
        print(f"{'='*60}")


if __name__ == "__main__":
    main()
