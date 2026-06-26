"""
Ground-truth generator for vt-term escape-code tests.

For each test case in test/cases/*.py, feeds the raw byte stream
through a fresh pyte.Stream/Screen and captures the resulting frame
dict.  Writes per-suite JSON to test/ground_truth/<suite>.json.

This bypasses the PTY entirely — the bytes are deterministic so we
get reproducible, fast ground truth that doesn't depend on any shell.

Usage:
    python test/gen_ground_truth.py                      # all suites
    python test/gen_ground_truth.py --suite csi_cursor   # one suite
    python test/gen_ground_truth.py --list

Test case file format (Python):

    NAME = "csi_cursor"
    ROWS = 24
    COLS = 80
    CASES = {
        "case_id_1": "input bytes (raw, may contain escapes)",
        "case_id_2": {"bytes": "...", "rows": 10, "cols": 20},
        ...
    }
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

# UTF-8 stdout on Windows (cp1252)
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parent.parent
sys.path.insert(0, str(_ROOT / "shellpilot"))

try:
    import pyte
except ImportError:
    print("error: pip install pyte", file=sys.stderr)
    sys.exit(1)

from capture_frames import capture_frame  # reuse Vim-sim capture format

CASES_DIR = _HERE / "cases"
OUT_DIR = _HERE / "ground_truth"


def discover_suites() -> dict[str, dict]:
    """Load every test/cases/test_*.py and return {suite_name: module_dict}."""
    suites: dict[str, dict] = {}
    for py in sorted(CASES_DIR.glob("test_*.py")):
        if py.name == "__init__.py":
            continue
        module_name = py.stem
        suite_name = module_name.removeprefix("test_")
        spec = importlib.util.spec_from_file_location(module_name, py)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if not hasattr(mod, "CASES"):
            print(f"  WARNING: {py.name} has no CASES dict")
            continue
        suites[suite_name] = {
            "cases": mod.CASES,
            "rows": getattr(mod, "ROWS", 24),
            "cols": getattr(mod, "COLS", 80),
        }
    return suites


def run_case(byte_str: str, rows: int, cols: int) -> dict:
    """Feed bytes through pyte and capture a frame dict."""
    screen = pyte.Screen(cols, rows)
    stream = pyte.Stream(screen)
    stream.feed(byte_str)
    return capture_frame(screen)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--suite", help="Run only this suite")
    p.add_argument("--case", help="Run only this case (with --suite)")
    p.add_argument("--list", action="store_true", help="List suites + counts")
    args = p.parse_args()

    suites = discover_suites()
    if not suites:
        print(f"No suites found in {CASES_DIR}")
        return 1

    if args.list:
        for name, info in suites.items():
            print(f"  {name:20s}  ({len(info['cases'])} cases, {info['rows']}x{info['cols']})")
        return 0

    if args.suite:
        if args.suite not in suites:
            print(f"unknown suite: {args.suite}")
            print(f"available: {', '.join(suites)}")
            return 1
        suites = {args.suite: suites[args.suite]}

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    total = 0
    for name, info in suites.items():
        cases = info["cases"]
        rows, cols = info["rows"], info["cols"]
        if args.case:
            if args.case not in cases:
                print(f"unknown case: {args.case}")
                continue
            cases = {args.case: cases[args.case]}

        results = {}
        for case_id, payload in cases.items():
            if isinstance(payload, str):
                byte_str = payload
                r, c = rows, cols
            else:
                byte_str = payload["bytes"]
                r = payload.get("rows", rows)
                c = payload.get("cols", cols)
            frame = run_case(byte_str, r, c)
            results[case_id] = {
                "bytes": byte_str,
                "rows": r, "cols": c,
                "frame": frame,
            }

        out_path = OUT_DIR / f"{name}.json"
        out_path.write_text(json.dumps({
            "suite": name,
            "rows": rows, "cols": cols,
            "cases": results,
        }, indent=None), encoding="utf-8")
        print(f"  wrote {out_path.relative_to(_ROOT)}  ({len(results)} cases)")
        total += len(results)

    print(f"\nTotal: {total} cases across {len(suites)} suite(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
