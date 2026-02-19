"""
Batch runner: Run ALL test suites against Neovim in sequence.

Usage:
    python run_all_suites.py              # run everything
    python run_all_suites.py --fast       # reduced delays (less reliable)
    python run_all_suites.py --skip-existing  # skip suites with existing JSON
"""

from __future__ import annotations

import importlib
import importlib.util
import json
import sys
import time
import tempfile
from pathlib import Path

_here = Path(__file__).resolve().parent
_root = _here.parent.parent
sys.path.insert(0, str(_root / "shellpilot"))
sys.path.insert(0, str(_here))

from shell_pty import ShellPilot
from capture_frames import capture_frame

ROWS = 20
COLS = 40
CASES_DIR = _here / "cases"


def discover_suites():
    suites = {}
    for py_file in sorted(CASES_DIR.glob("test_*.py")):
        module_name = py_file.stem
        suite_name = module_name.removeprefix("test_")
        spec = importlib.util.spec_from_file_location(module_name, py_file)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if hasattr(mod, "CASES") and isinstance(mod.CASES, dict):
            suites[suite_name] = mod.CASES
    return suites


def run_case(name, case, fast=False):
    keys = case["keys"]
    initial = case.get("initial", "")

    tmp = Path(tempfile.mktemp(suffix=".txt", dir="."))
    tmp.write_text(initial, encoding="utf-8")

    key_delay = 0.03 if fast else 0.04
    settle_time = 0.2 if fast else 0.3
    post_key_settle = 0.15 if fast else 0.3

    shell = ShellPilot(
        shell=f'nvim -u NONE -n -i NONE {tmp.name}',
        rows=ROWS,
        cols=COLS,
    )
    try:
        shell.start()

        first_line = initial.split('\n')[0] if initial else ''
        wait_text = first_line.replace('\t', ' ')[:10].strip()
        wait_for = wait_text if wait_text else '~'

        deadline = time.time() + 10.0
        while time.time() < deadline:
            screen_text = shell.get_screen_text()
            if wait_for in screen_text:
                break
            time.sleep(0.1)
        else:
            raise RuntimeError(f"Neovim did not render (waiting for {wait_for!r})")
        time.sleep(settle_time)

        for ch in keys:
            shell.send_keys(ch)
            time.sleep(key_delay)

        time.sleep(post_key_settle)

        frame = capture_frame(shell.screen)
        text_lines = [line["text"] for line in frame["lines"][:ROWS - 2]]

        return {
            "keys": keys,
            "initialContent": initial,
            "frame": frame,
            "textLines": text_lines,
            "cursor": frame["cursor"],
            "screenRows": ROWS,
            "screenCols": COLS,
        }
    finally:
        try:
            shell.send_keys('\x1b:q!\r')
            time.sleep(0.1)
        except Exception:
            pass
        try:
            shell.stop()
        except Exception:
            pass
        try:
            tmp.unlink()
        except Exception:
            pass


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--fast", action="store_true")
    ap.add_argument("--skip-existing", action="store_true")
    ap.add_argument("--suite", "-s", default=None)
    args = ap.parse_args()

    suites = discover_suites()
    if args.suite:
        suites = {args.suite: suites[args.suite]}

    total_cases = sum(len(c) for c in suites.values())
    print(f"Running {total_cases} test cases across {len(suites)} suites")
    print(f"Estimated time: ~{total_cases * 2 // 60} minutes\n")

    grand_ok = 0
    grand_err = 0
    start_time = time.time()

    for suite_name, cases in suites.items():
        out_file = _here / f"ground_truth_{suite_name}.json"

        if args.skip_existing and out_file.exists():
            existing = json.loads(out_file.read_text(encoding="utf-8"))
            if len(existing) == len(cases) and not any("error" in v for v in existing.values()):
                print(f"SKIP {suite_name} ({len(cases)} cases, already captured)")
                grand_ok += len(cases)
                continue

        print(f"\n{'='*60}")
        print(f"Suite: {suite_name} ({len(cases)} cases)")
        print(f"{'='*60}")

        results = {}
        for i, (name, case) in enumerate(cases.items(), 1):
            print(f"  [{i}/{len(cases)}] {name} ...", end=" ", flush=True)
            try:
                result = run_case(name, case, fast=args.fast)
                results[name] = result
                r, c = result["cursor"]["row"], result["cursor"]["col"]
                print(f"OK  ({r},{c})")
                grand_ok += 1
            except Exception as e:
                print(f"FAILED: {e}")
                results[name] = {"error": str(e)}
                grand_err += 1

        out_file.write_text(json.dumps(results, indent=2), encoding="utf-8")
        print(f"  Wrote {out_file.name}")

    elapsed = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"DONE: {grand_ok} OK, {grand_err} errors in {elapsed:.0f}s")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
