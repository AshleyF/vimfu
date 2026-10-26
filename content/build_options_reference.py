#!/usr/bin/env python3
"""Build a comprehensive option-reference appendix topic JSON.

Self-contained: asks the local `nvim` and `vim` binaries which options
they can actually set, then pulls one-line descriptions from each
editor's installed quickref.txt. Re-run any time the installed editors
change.

An option is included only when that editor accepts it. Documented
names that this build rejects (compiled-out GUI options, for example)
are left out, so the counts match `:set` on these installs.

Emits each option's row tagged with availability:
  N+V  — present in both Neovim and Vim
  N    — Neovim-only (Vim doesn't ship it)
  V    — Vim-only (Neovim removed or never had it)
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "parts" / "99-appendices" / "09-options-reference.json"


def _runtime_doc(editor: str, flags: list[str]) -> Path | None:
    """Return ``$VIMRUNTIME/doc/quickref.txt`` for a local editor."""
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "runtime.txt"
        script = Path(td) / "runtime.vim"
        script.write_text(
            f"call writefile([$VIMRUNTIME], '{out}')\nqa!\n",
            encoding="utf-8",
        )
        subprocess.run(
            [editor, *flags, "-S", str(script)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        runtime = Path(out.read_text(encoding="utf-8").strip())
    quickref = runtime / "doc" / "quickref.txt"
    return quickref if quickref.exists() else None


def dump_settable_options(editor: str, flags: list[str]) -> set[str]:
    """Option names this editor will actually ``:set``.

    ``getcompletion('', 'option')`` also returns the pseudo-name
    ``all``. Drop it. Names that only appear in the docs, and that
    ``:set`` rejects, never show up here.
    """
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "opts.txt"
        script = Path(td) / "dump.vim"
        script.write_text(
            f"call writefile(getcompletion('', 'option'), '{out}')\nqa!\n",
            encoding="utf-8",
        )
        subprocess.run(
            [editor, *flags, "-S", str(script)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return {
            name.strip()
            for name in out.read_text(encoding="utf-8").splitlines()
            if name.strip() and name.strip() != "all"
        }


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


def unquote_option_names(desc: str) -> str:
    """Turn Vim's ``'incsearch'`` quoting into book backticks.

    The surrounding monospace already names the option. The inner
    single quotes are noise, including inside ``:help {option}``.
    """
    return re.sub(r"'([A-Za-z][A-Za-z0-9_-]*)'", r"`\1`", desc)


def main():
    nvim_flags = ["--headless"]
    vim_flags = ["--clean", "--not-a-term"]

    nvim_quickref_path = _runtime_doc("nvim", nvim_flags)
    vim_quickref_path = _runtime_doc("vim", vim_flags)
    if not nvim_quickref_path or not vim_quickref_path:
        print("ERROR: could not find quickref.txt for nvim and vim.",
              file=sys.stderr)
        sys.exit(1)
    nvim_text = nvim_quickref_path.read_text(encoding="utf-8", errors="replace")
    vim_text = vim_quickref_path.read_text(encoding="utf-8", errors="replace")
    print(f"Read Neovim quickref: {nvim_quickref_path}")
    print(f"Read Vim quickref: {vim_quickref_path}")

    print("Dumping Neovim options metadata via `nvim --headless` ...")
    nvim_opts = dump_nvim_options()
    nvim_names = dump_settable_options("nvim", nvim_flags)
    vim_names = dump_settable_options("vim", vim_flags)
    print(f"Settable options: Neovim {len(nvim_names)}, Vim {len(vim_names)}.")

    nvim_desc = parse_quickref(nvim_text)
    vim_desc = parse_quickref(vim_text)
    nvim_meta = {o["name"]: o for o in nvim_opts}

    all_names = sorted(nvim_names | vim_names)
    rows = []
    counts = {"N+V": 0, "N": 0, "V": 0}
    for name in all_names:
        in_n = name in nvim_names
        in_v = name in vim_names
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
        desc = unquote_option_names(desc.replace("|", "/"))
        if len(desc) > 120:
            desc = desc[:117].rstrip() + "..."
        rows.append([
            f"`{name}`" + (f" / `{short}`" if short else ""),
            type_tok or "",
            scope or "",
            avail,
            desc,
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
                "*Availability:* *N+V* — both Neovim and Vim. *N* — Neovim "
                "only (Vim doesn't ship it). *V* — Vim only (Neovim removed "
                "or never implemented it). *Scope:* *global,* *win* "
                "(window-local), *buf* (buffer-local). *Type:* *bool,* "
                "*num,* *str.*"
            ),
        },
        {
            "type": "prose",
            "text": (
                f"Total: {sum(counts.values())} options "
                f"({counts['N+V']} in both, {counts['N']} Neovim-only, "
                f"{counts['V']} Vim-only). For full documentation of any "
                "option, run `:help {option}` in Neovim or Vim."
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
