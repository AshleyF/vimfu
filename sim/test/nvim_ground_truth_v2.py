"""
Modular Neovim ground-truth generator for VimFu simulator tests.

Loads test cases from sim/test/cases/*.py modules and runs them
against Neovim via ShellPilot, capturing screen state.

Usage:
    python nvim_ground_truth_v2.py                          # run ALL modular tests
    python nvim_ground_truth_v2.py --suite motions_basic     # run one suite
    python nvim_ground_truth_v2.py --suite motions_basic --case h_basic
    python nvim_ground_truth_v2.py --list                   # list all suites & counts
    python nvim_ground_truth_v2.py --output results/         # write per-suite JSON files

Output is written as per-suite JSON files in the output directory:
    ground_truth_motions_basic.json
    ground_truth_motions_word.json
    ...
Each file has the same format as ground_truth.json.
"""

from __future__ import annotations

import importlib
import importlib.util
import json
import sys
import time
import tempfile
from pathlib import Path

# Add parent dirs to path
_here = Path(__file__).resolve().parent
_root = _here.parent.parent  # vimfu/
sys.path.insert(0, str(_root / "shellpilot"))
sys.path.insert(0, str(_here))  # for cases package

from shell_pty import ShellPilot  # noqa: E402
from capture_frames import capture_frame  # noqa: E402

# ── Screen dimensions (must match the sim's defaults) ──
ROWS = 20
COLS = 40

# ── Discover and load test suites ──
CASES_DIR = _here / "cases"


def discover_suites() -> dict[str, dict]:
    """Import all test_*.py modules from cases/ and return {suite_name: CASES_dict}."""
    suites = {}
    for py_file in sorted(CASES_DIR.glob("test_*.py")):
        module_name = py_file.stem  # e.g. "test_motions_basic"
        suite_name = module_name.removeprefix("test_")  # e.g. "motions_basic"
        spec = importlib.util.spec_from_file_location(module_name, py_file)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if hasattr(mod, "CASES") and isinstance(mod.CASES, dict):
            suites[suite_name] = mod.CASES
        else:
            print(f"  WARNING: {py_file.name} has no CASES dict, skipping")
    return suites


def run_case(name: str, case: dict) -> dict:
    """Run a single test case against Neovim and return captured state."""
    keys = case["keys"]
    initial = case.get("initial", "")

    # Write initial content to a temp file in the current directory
    # (short path avoids ConPTY escaping issues)
    tmp = Path(tempfile.mktemp(suffix=".txt", dir="."))
    tmp.write_text(initial, encoding="utf-8")

    shell = ShellPilot(
        shell=f'nvim -u NONE -n -i NONE {tmp.name}',
        rows=ROWS,
        cols=COLS,
    )
    try:
        shell.start()

        # Wait for nvim to render
        first_line = initial.split('\n')[0] if initial else ''
        # Tabs render as spaces in nvim, so strip tabs for the wait check
        wait_text = first_line.replace('\t', ' ')[:10].strip()
        wait_for = wait_text if wait_text else '~'

        deadline = time.time() + 10.0
        while time.time() < deadline:
            screen_text = shell.get_screen_text()
            if wait_for in screen_text:
                break
            time.sleep(0.1)
        else:
            screen = shell.get_screen()
            for i, line in enumerate(screen[:5]):
                print(f"  DEBUG line {i}: {repr(line)}")
            raise RuntimeError(
                f"Neovim did not render within 10s "
                f"(waiting for {wait_for!r})"
            )
        time.sleep(0.15)

        # Feed keys one at a time
        for ch in keys:
            shell.send_keys(ch)
            time.sleep(0.04)

        time.sleep(0.3)  # settle

        # Capture frame
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


def run_suite(suite_name: str, cases: dict, case_filter: str | None = None) -> dict:
    """Run all cases in a suite and return results dict."""
    if case_filter:
        if case_filter not in cases:
            print(f"  Unknown case '{case_filter}' in suite '{suite_name}'")
            print(f"  Available: {', '.join(list(cases)[:20])}...")
            return {}
        cases = {case_filter: cases[case_filter]}

    results = {}
    total = len(cases)
    for i, (name, case) in enumerate(cases.items(), 1):
        print(f"  [{i}/{total}] {name} ...", end=" ", flush=True)
        try:
            result = run_case(name, case)
            results[name] = result
            r, c = result["cursor"]["row"], result["cursor"]["col"]
            print(f"OK  cursor=({r},{c})")
        except Exception as e:
            print(f"FAILED: {e}")
            results[name] = {"error": str(e)}
    return results


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Modular Neovim ground-truth generator")
    ap.add_argument("--suite", "-s", default=None,
                    help="Run only this suite (e.g. motions_basic)")
    ap.add_argument("--case", "-c", default=None,
                    help="Run only this case within the suite")
    ap.add_argument("--list", "-l", action="store_true",
                    help="List all suites and their case counts")
    ap.add_argument("--output", "-o", default=str(_here),
                    help="Output directory for JSON files (default: test/)")
    ap.add_argument("--combined", action="store_true",
                    help="Also write a single combined ground_truth_all.json")
    args = ap.parse_args()

    suites = discover_suites()

    if args.list:
        total = 0
        for name, cases in suites.items():
            print(f"  {name}: {len(cases)} cases")
            total += len(cases)
        print(f"\n  TOTAL: {total} test cases across {len(suites)} suites")
        return

    # Filter suites
    if args.suite:
        if args.suite not in suites:
            print(f"Unknown suite: {args.suite}")
            print(f"Available: {', '.join(suites)}")
            sys.exit(1)
        run_suites = {args.suite: suites[args.suite]}
    else:
        run_suites = suites

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    all_results = {}
    grand_total = sum(len(c) for c in run_suites.values())
    completed = 0

    for suite_name, cases in run_suites.items():
        count = len(cases) if not args.case else 1
        print(f"\n{'='*60}")
        print(f"Suite: {suite_name} ({count} cases)")
        print(f"{'='*60}")

        results = run_suite(suite_name, cases, args.case)

        # Write per-suite JSON
        out_file = out_dir / f"ground_truth_{suite_name}.json"
        # Merge with existing if present
        if out_file.exists() and not args.case:
            pass  # overwrite
        elif out_file.exists() and args.case:
            existing = json.loads(out_file.read_text(encoding="utf-8"))
            existing.update(results)
            results = existing

        out_file.write_text(json.dumps(results, indent=2), encoding="utf-8")
        print(f"  Wrote {out_file.name} ({len(results)} cases)")

        all_results.update(results)
        completed += len(results)

    if args.combined and not args.case:
        combined_file = out_dir / "ground_truth_all.json"
        combined_file.write_text(
            json.dumps(all_results, indent=2), encoding="utf-8"
        )
        print(f"\nWrote combined {combined_file.name} ({len(all_results)} cases)")

    errors = sum(1 for v in all_results.values() if "error" in v)
    print(f"\n{'='*60}")
    print(f"Done: {completed} cases, {errors} errors")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
