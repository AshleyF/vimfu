"""
Capture nvim's actual syntax highlighting colors for demo.py.

Opens the sample Python file in nvim (with default config), captures the
screen at various scroll positions, and writes the per-line color data
to nvim_syntax_colors.json.

This tells us exactly what colors nvim uses for each Python construct,
so we can set our sim theme to match.

Usage:
    cd sim
    python test/capture_nvim_syntax.py
"""

from __future__ import annotations

import json
import sys
import time
import tempfile
from pathlib import Path

# Add shellpilot to path
_here = Path(__file__).resolve().parent
_root = _here.parent.parent  # vimfu/
sys.path.insert(0, str(_root / "shellpilot"))

from shell_pty import ShellPilot
from capture_frames import capture_frame

ROWS = 20
COLS = 80  # wider so we see full lines

# The sample Python content (inline so we don't need Node)
SAMPLE_PYTHON = r'''#!/usr/bin/env python3
"""VimFu demo: Python syntax showcase."""

import os
import sys
from pathlib import Path
from typing import List, Optional

# Constants
MAX_SIZE = 100
PI = 3.14159
HEX = 0xFF
BIN = 0b1010
OCTAL = 0o777
GREETING = "Hello, VimFu!"
RAW = r"no\escapes\here"
FSTR = f"pi is {PI:.2f}"
MULTI = """triple
quoted string"""
EMPTY = None
IS_OK = True
NOPE = False

@property
def greet(name: str) -> str:
    """Return a greeting."""
    return f"Hello, {name}!"

class Animal:
    """Base class for animals."""
    count: int = 0

    def __init__(self, name: str):
        self.name = name
        self._age = 0
        Animal.count += 1

    @staticmethod
    def kingdom() -> str:
        return "Animalia"

    @classmethod
    def from_dict(cls, d: dict):
        return cls(d["name"])

class Dog(Animal):
    """A dog is a good boy."""

    def __init__(self, name: str):
        super().__init__(name)
        self.tricks: List[str] = []

    def learn(self, trick: str):
        if trick not in self.tricks:
            self.tricks.append(trick)

def fibonacci(n: int):
    """Yield Fibonacci numbers."""
    a, b = 0, 1
    while a < n:
        yield a
        a, b = b, a + b

# Lambda and map
square = lambda x: x ** 2
nums = list(range(10))
evens = [x for x in nums
         if x % 2 == 0]

# Exception handling
def divide(a, b):
    try:
        return a / b
    except ZeroDivisionError as e:
        print(f"Error: {e}")
        return None
    except (TypeError, ValueError):
        raise
    finally:
        pass

# Async syntax
async def fetch(url: str):
    async with session.get(url) as r:
        return await r.text()

# Walrus + match
def check(data):
    if (n := len(data)) > 10:
        print(f"Large: {n}")
    match data:
        case []:
            pass
        case [x, *rest]:
            print(x, rest)
        case _:
            pass

# Global / nonlocal
counter = 0
def increment():
    global counter
    counter += 1

# Type hints
Vector = List[float]
def dot(a: Vector, b: Vector):
    assert len(a) == len(b)
    return sum(x*y for x, y in
               zip(a, b))

# Ternary + chained comparison
x = 42
label = "big" if x > 100 else "sm"
in_range = 0 < x < 100

# Unpacking
first, *mid, last = range(5)
a, b = b, a  # swap

# Delete
temp = [1, 2, 3]
del temp[0]

# Entry point
if __name__ == "__main__":
    dog = Dog("Rex")
    dog.learn("sit")
    dog.learn("shake")
    print(dog)
    for n in fibonacci(50):
        if n > 20:
            break
        print(n, end=" ")
    print()
    result = divide(10, 3)
    print(f"Result: {result}")
    # TODO: Add more features
    sys.exit(0)
'''


def capture_at_scroll(shell, scroll_keys: str, label: str) -> dict:
    """Send scroll keys and capture the frame."""
    if scroll_keys:
        for ch in scroll_keys:
            shell.send_keys(ch)
            time.sleep(0.05)
        time.sleep(0.3)

    frame = capture_frame(shell.screen)
    return {
        "label": label,
        "scroll_keys": scroll_keys,
        "cursor": frame["cursor"],
        "lines": frame["lines"][:ROWS - 2],  # text area only
    }


def main():
    # Write sample to temp file
    tmp = Path("demo_capture.py")
    tmp.write_text(SAMPLE_PYTHON.lstrip('\n'), encoding="utf-8")
    print(f"Wrote sample to {tmp}")

    init_vim = (_here / "_nvim_init.vim").resolve()
    shell = ShellPilot(
        shell=f'nvim -u {init_vim} -n -i NONE {tmp.name}',
        rows=ROWS,
        cols=COLS,
    )

    results = {}
    try:
        shell.start()

        # Wait for nvim to render
        deadline = time.time() + 10.0
        while time.time() < deadline:
            text = shell.get_screen_text()
            if '#!/usr/bin/env' in text or 'python3' in text:
                break
            time.sleep(0.1)
        else:
            # Debug: show what's on screen
            screen = shell.get_screen()
            for i, line in enumerate(screen[:5]):
                print(f"  DEBUG line {i}: {repr(line)}")
            raise RuntimeError("nvim didn't render within 10s")
        time.sleep(0.5)

        # Capture top of file
        results["top"] = capture_at_scroll(shell, "", "top of file")

        # Scroll down through the file, capturing at each screenful
        # Use Ctrl-F (page forward)
        results["page2"] = capture_at_scroll(shell, "\x06", "page 2 (Ctrl-F)")
        results["page3"] = capture_at_scroll(shell, "\x06", "page 3 (Ctrl-F)")
        results["page4"] = capture_at_scroll(shell, "\x06", "page 4 (Ctrl-F)")
        results["page5"] = capture_at_scroll(shell, "\x06", "page 5 (Ctrl-F)")
        results["page6"] = capture_at_scroll(shell, "\x06", "page 6 (Ctrl-F)")
        results["page7"] = capture_at_scroll(shell, "\x06", "page 7 (Ctrl-F)")
        results["page8"] = capture_at_scroll(shell, "\x06", "page 8 (Ctrl-F)")

        # Go back to top
        shell.send_keys('g')
        shell.send_keys('g')
        time.sleep(0.3)
        results["back_to_top"] = capture_at_scroll(shell, "", "back to top (gg)")

    finally:
        try:
            shell.send_keys('\x1b:q!\r')
            time.sleep(0.2)
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

    # Write results
    out = _here / "nvim_syntax_colors.json"
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nWrote {out}")

    # Print a summary: for each captured page, show the unique colors seen
    print("\n" + "=" * 70)
    print("COLOR SUMMARY")
    print("=" * 70)

    all_colors = set()
    for page_name, page_data in results.items():
        colors = set()
        for line_data in page_data["lines"]:
            for run in line_data["runs"]:
                colors.add(run["fg"])
                all_colors.add(run["fg"])
        print(f"\n{page_name}: {len(colors)} unique fg colors")
        for c in sorted(colors):
            print(f"  #{c}")

    print(f"\nALL UNIQUE FG COLORS: {len(all_colors)}")
    for c in sorted(all_colors):
        print(f"  #{c}")

    # Print detailed line-by-line for top of file
    print("\n" + "=" * 70)
    print("DETAILED: top of file")
    print("=" * 70)
    for i, line_data in enumerate(results["top"]["lines"]):
        text = line_data["text"].rstrip()
        runs = line_data["runs"]
        print(f"\nLine {i}: {text[:60]}")
        col = 0
        for run in runs:
            snippet = text[col:col + run["n"]] if col < len(text) else ""
            snippet = snippet[:30]
            flags = ""
            if run.get("b"):
                flags += " BOLD"
            print(f"  [{col:3d}-{col + run['n'] - 1:3d}] fg={run['fg']} bg={run['bg']}{flags} '{snippet}'")
            col += run["n"]


if __name__ == "__main__":
    main()
