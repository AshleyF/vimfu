#!/usr/bin/env python
"""Convert clearly-identifiable key references in prose to {key:...} markup.

Operates on raw JSON text so we don't disturb the existing formatting --
arrays stay inline, key order is preserved, etc.

Conservative: only touches patterns we can identify with high confidence as
keys (not arbitrary backtick code spans, which are often option names, regex,
or example text).
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "parts"

# In JSON source, backticks are literal but " is escaped as \".
B = "`"  # literal backtick

# Angle-bracket key notation: `<Esc>`, `<CR>`, `<C-x>`, `<S-Tab>`, `<Leader>`
ANGLE = re.compile(rf"{B}(<[A-Z][A-Za-z0-9-]*>){B}")

# Register notation: `"a`, `"+`, `"-`, `"1`, `""`, ... (the " is JSON-escaped)
REG = re.compile(rf'{B}\\"([A-Za-z0-9_+\-*/=:."#%]){B}')
REG_EMPTY = re.compile(rf'{B}\\"\\"{B}')

# @-notation: `@:`, `@a`, `@@`
AT_KEY = re.compile(rf"{B}@([:@A-Za-z]){B}")

# Modifier-key forms: `Ctrl-X`, `Shift-Tab`, `Alt-Space`, `Meta-X`, `Cmd-X`
MODKEY = re.compile(rf"{B}((?:Ctrl|Shift|Alt|Meta|Cmd)-[A-Za-z0-9]+){B}")

# Bare named keys when alone in backticks
NAMED = re.compile(rf"{B}(Esc|Enter|Tab|Space|Backspace|Delete|Up|Down|Left|Right|Home|End|PageUp|PageDown|Insert){B}")

# Prose: "press X", "pressing X", "hit X", "tap X" with named keys
PRESS_NAMED = re.compile(
    r"\b(press(?:ing|es|ed)?|hit(?:ting|s)?|tap(?:ping|s|ped)?)\s+"
    r"(Enter|Esc|Escape|Tab|Space|Backspace|Delete|Return)\b"
)


def upgrade(text: str) -> str:
    text = ANGLE.sub(lambda m: "{key:" + m.group(1) + "}", text)
    text = REG_EMPTY.sub(r'{key:\"}{key:\"}', text)
    text = REG.sub(lambda m: '{key:\\"}{key:' + m.group(1) + "}", text)
    text = AT_KEY.sub(lambda m: "{key:@}{key:" + m.group(1) + "}", text)
    text = MODKEY.sub(lambda m: "{key:" + m.group(1) + "}", text)
    text = NAMED.sub(lambda m: "{key:" + m.group(1) + "}", text)

    def press_sub(m: re.Match) -> str:
        verb, key = m.group(1), m.group(2)
        if key == "Escape":
            key = "Esc"
        elif key == "Return":
            key = "Enter"
        return f"{verb} {{key:{key}}}"

    text = PRESS_NAMED.sub(press_sub, text)
    return text


def main():
    dry = "--dry-run" in sys.argv
    changed = 0
    for path in sorted(ROOT.glob("**/*.json")):
        original = path.read_text(encoding="utf-8")
        new = upgrade(original)
        if new != original:
            changed += 1
            print(f"  {path.relative_to(ROOT.parent)}")
            if not dry:
                path.write_text(new, encoding="utf-8")
    print(f"\n{changed} files {'would change' if dry else 'updated'}")


if __name__ == "__main__":
    main()

