#!/usr/bin/env python
"""Copy the sim runtime into the website output (`output/html/sim/`).

Run after `render_html.py` (or whenever sim sources change) so the website's
"Practice" links resolve to a self-contained copy of the simulator.
"""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
SIM_SRC = REPO / "sim"
OUT = ROOT / "output" / "html" / "sim"

# Files / directories that make up the sim runtime. Everything else (tests,
# node_modules, ground-truth fixtures, design docs) is left behind.
INCLUDES = [
    Path("index.html"),
    Path("README.md"),
    Path("src"),
]


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    copied = 0
    for rel in INCLUDES:
        src = SIM_SRC / rel
        dst = OUT / rel
        if src.is_dir():
            shutil.copytree(src, dst)
            copied += sum(1 for _ in dst.rglob("*") if _.is_file())
        elif src.is_file():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            copied += 1
        else:
            print(f"  warn: {src} not found, skipping")

    print(f"Copied {copied} sim files -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
