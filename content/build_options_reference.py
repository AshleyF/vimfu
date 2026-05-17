#!/usr/bin/env python3
"""Build a comprehensive option-reference appendix topic JSON.

Self-contained: invokes `nvim --headless` to dump option metadata and
fetches Vim's quickref.txt from the upstream repo. Re-run any time to
regenerate the appendix from the current Neovim / Vim option sets.

Combines:
  - Neovim option metadata from `nvim_get_all_options_info()`.
  - One-line descriptions from Neovim's `quickref.txt` (Q_op section).
  - Vim's `quickref.txt` Q_op section (fetched from vim/vim master).

Emits each option's row tagged with availability:
  N+V  — present in both Neovim and Vim
  N    — Neovim-only (Vim doesn't ship it)
  V    — Vim-only (Neovim removed or never had it)
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "parts" / "99-appendices" / "09-options-reference.json"
VIM_QUICKREF_URL = "https://raw.githubusercontent.com/vim/vim/master/runtime/doc/quickref.txt"


def find_nvim_quickref() -> Path | None:
    """Locate Neovim's runtime quickref.txt next to the nvim binary."""
    nvim = shutil.which("nvim")
    if not nvim:
        return None
    p = Path(nvim).resolve().parent.parent / "share" / "nvim" / "runtime" / "doc" / "quickref.txt"
    return p if p.exists() else None


def dump_nvim_options() -> list[dict]:
    """Run nvim and capture vim.api.nvim_get_all_options_info() as JSON."""
    with tempfile.TemporaryDirectory() as td:
        out_path = Path(td) / "options.json"
        # Lua expression: collect all options, encode as JSON.
        lua = (
            "local o=io.open([[%s]],[[w]]); "
            "local t={}; "
            "for k,v in pairs(vim.api.nvim_get_all_options_info()) do t[#t+1]=v end; "
            "o:write(vim.json.encode(t)); o:close()"
        ) % str(out_path).replace("\\", "\\\\")
        subprocess.run(
            ["nvim", "--headless", "-c", "lua " + lua, "-c", "qa"],
            check=True,
            stderr=subprocess.DEVNULL,
        )
        return json.loads(out_path.read_text(encoding="utf-8"))


def parse_quickref(text: str) -> dict[str, tuple[str, str]]:
    """Return {long_name: (short_name, description)} from quickref Q_op."""
    out: dict[str, tuple[str, str]] = {}
    in_op = False
    for line in text.splitlines():
        if "*Q_op*" in line:
            in_op = True
            continue
        if not in_op:
            continue
        if re.match(r"^\*Q_", line):
            break
        m = re.match(r"^'([a-zA-Z0-9]+)'\s+(?:'([a-zA-Z0-9]+)')?\s*(.*)$", line)
        if not m:
            continue
        name, short, desc = m.group(1), m.group(2) or "", m.group(3).strip()
        if name:
            out[name] = (short, desc)
    return out


def main():
    nvim_quickref_path = find_nvim_quickref()
    if not nvim_quickref_path:
        print("ERROR: nvim not found on PATH. Install Neovim and retry.",
              file=sys.stderr)
        sys.exit(1)
    nvim_text = nvim_quickref_path.read_text(encoding="utf-8", errors="replace")
    print(f"Read Neovim quickref: {nvim_quickref_path}")

    print(f"Fetching Vim quickref from {VIM_QUICKREF_URL} ...")
    with urllib.request.urlopen(VIM_QUICKREF_URL, timeout=30) as r:
        vim_text = r.read().decode("utf-8", errors="replace")

    print("Dumping Neovim options metadata via `nvim --headless` ...")
    nvim_opts = dump_nvim_options()
    print(f"Got {len(nvim_opts)} options from Neovim.")

    nvim_desc = parse_quickref(nvim_text)
    vim_desc = parse_quickref(vim_text)
    nvim_meta = {o["name"]: o for o in nvim_opts}

    all_names = sorted(set(nvim_desc) | set(vim_desc) | set(nvim_meta))
    rows = []
    counts = {"N+V": 0, "N": 0, "V": 0}
    for name in all_names:
        in_n = name in nvim_meta or name in nvim_desc
        in_v = name in vim_desc
        if in_n and in_v:
            avail = "N+V"
        elif in_n:
            avail = "N"
        else:
            avail = "V"
        counts[avail] += 1
        short = ""
        desc = ""
        if name in nvim_desc:
            short, desc = nvim_desc[name]
        if not desc and name in vim_desc:
            short, desc = vim_desc[name]
        if not short and name in nvim_meta:
            short = nvim_meta[name].get("shortname", "") or ""
            if short == name:
                short = ""
        meta = nvim_meta.get(name, {})
        typ = meta.get("type", "")
        scope = meta.get("scope", "")
        type_tok = {"boolean": "bool", "number": "num", "string": "str"}.get(typ, typ)
        rows.append([
            f"`{name}`" + (f" / `{short}`" if short else ""),
            type_tok or "",
            scope or "",
            avail,
            desc.replace("|", "/")[:120],
        ])
    print(f"Totals: {counts}, grand total: {sum(counts.values())}")

    blocks = [
        {"type": "heading", "level": 1, "text": "Complete Options Reference"},
        {
            "type": "prose",
            "text": (
                "Every option known to Neovim and/or Vim, with its short name, "
                "type, scope, and availability. Cross-referenced from "
                "[Setting Options](#ex.set). Use this as a lookup when you "
                "encounter an option name in a config file or plugin and want "
                "to know what it controls and which editor ships it."
            ),
        },
        {
            "type": "prose",
            "text": (
                "**Availability:** *N+V* — both Neovim and Vim. *N* — Neovim "
                "only (Vim doesn't ship it). *V* — Vim only (Neovim removed "
                "or never implemented it). **Scope:** *global*, *win* "
                "(window-local), *buf* (buffer-local). **Type:** *bool*, "
                "*num*, *str*."
            ),
        },
        {
            "type": "prose",
            "text": (
                f"Total: {sum(counts.values())} options "
                f"({counts['N+V']} in both, {counts['N']} Neovim-only, "
                f"{counts['V']} Vim-only). For full documentation of any "
                "option, run `:help '{option}'` in Neovim or Vim."
            ),
        },
        {
            "type": "table",
            "headers": ["Option", "Type", "Scope", "Avail.", "Summary"],
            "rows": rows,
        },
    ]

    topic = {
        "format": "vimfu-content-topic",
        "version": 1,
        "id": "appendix.options-reference",
        "title": "Complete Options Reference",
        "subtitle": f"All {sum(counts.values())} options across Vim and Neovim",
        "part": "appendices",
        "summary": (
            "Comprehensive lookup table of every Neovim and Vim option: name, "
            "short name, type, scope, availability, and a one-line summary."
        ),
        "keys": [],
        "lessons": [],
        "see_also": ["ex.set"],
        "blocks": blocks,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(topic, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    print(f"Wrote {OUT} with {len(rows)} option rows.")


if __name__ == "__main__":
    main()
