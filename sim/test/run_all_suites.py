"""Batch runner for all Neovim ground-truth suites.

This file deliberately delegates discovery and capture to
``nvim_ground_truth_v2.py``.  There must be only one implementation of the
Neovim oracle setup; otherwise full-suite and single-suite captures can use
different configuration, clipboard providers, filenames, or timing.

Usage:
    python run_all_suites.py              # run everything
    python run_all_suites.py --fast       # reduced delays (less reliable)
    python run_all_suites.py --skip-existing  # skip suites with existing JSON
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(_here))

from nvim_ground_truth_v2 import discover_suites, run_suite


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--fast", action="store_true")
    ap.add_argument("--skip-existing", action="store_true")
    ap.add_argument("--suite", "-s", default=None)
    args = ap.parse_args()

    suites = discover_suites()
    if args.suite:
        if args.suite not in suites:
            print(f"Unknown suite: {args.suite}")
            print(f"Available: {', '.join(suites)}")
            sys.exit(1)
        suites = {args.suite: suites[args.suite]}

    total_cases = sum(len(info["cases"]) for info in suites.values())
    print(f"Running {total_cases} test cases across {len(suites)} suites")
    print(f"Estimated time: ~{total_cases * 2 // 60} minutes\n")

    grand_ok = 0
    grand_err = 0
    start_time = time.time()

    for suite_name, info in suites.items():
        cases = info["cases"]
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

        if args.fast:
            cases = {
                name: {
                    **case,
                    "key_delay": min(case.get("key_delay", 0.04), 0.03),
                    "settle": min(case.get("settle", 0.3), 0.2),
                }
                for name, case in cases.items()
            }

        results = run_suite(
            suite_name,
            cases,
            nvim_cmd=info.get("nvim_cmd"),
        )
        suite_errors = sum(1 for result in results.values() if "error" in result)
        grand_err += suite_errors
        grand_ok += len(results) - suite_errors

        out_file.write_text(json.dumps(results, indent=2), encoding="utf-8")
        print(f"  Wrote {out_file.name}")

    elapsed = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"DONE: {grand_ok} OK, {grand_err} errors in {elapsed:.0f}s")
    print(f"{'='*60}")
    if grand_err:
        sys.exit(1)


if __name__ == "__main__":
    main()
