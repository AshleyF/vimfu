/**
 * VimFu Simulator – Sample Files
 *
 * Pre-built demo content for the VFS.
 * Each export is a { filename, content } pair.
 */

// ── Python demo ──────────────────────────────────────────

export const SAMPLE_PYTHON = {
  filename: 'demo.py',
  content: `\
#!/usr/bin/env python3
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
RAW = r"no\\escapes\\here"
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
`,
};

/** All sample files. */
export const SAMPLES = [SAMPLE_PYTHON];
