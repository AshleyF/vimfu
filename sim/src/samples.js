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
"""Python syntax showcase."""

import os, sys
from pathlib import Path

# Constants
MAX = 100
PI = 3.14159
NAME = "VimFu"
RAW = r"no\\escapes"
FSTR = f"pi={PI:.2f}"
NONE = None
OK = True

def greet(name: str) -> str:
    """Return a greeting."""
    return f"Hello, {name}!"

class Animal:
    """Base animal class."""
    count = 0

    def __init__(self, name):
        self.name = name
        self._age = 0
        Animal.count += 1

    @staticmethod
    def kingdom():
        return "Animalia"

class Dog(Animal):
    """A good boy."""

    def __init__(self, name):
        super().__init__(name)
        self.tricks = []

    def learn(self, trick):
        if trick not in self.tricks:
            self.tricks.append(trick)

def fibonacci(n):
    """Yield Fibonacci numbers."""
    a, b = 0, 1
    while a < n:
        yield a
        a, b = b, a + b

square = lambda x: x ** 2
nums = list(range(10))
evens = [x for x in nums
         if x % 2 == 0]

def divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return None

if __name__ == "__main__":
    dog = Dog("Rex")
    dog.learn("sit")
    dog.learn("shake")
    print(greet(dog.name))
    for n in fibonacci(50):
        if n > 20:
            break
        print(n, end=" ")
    print()
    r = divide(10, 3)
    print(f"Result: {r}")
`,
};

/** All sample files. */
export const SAMPLES = [SAMPLE_PYTHON];
