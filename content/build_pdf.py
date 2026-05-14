"""
Build content/output/latex/book.pdf from the rendered LaTeX sources.

Usage:
    python content/build_pdf.py             # full build (re-render then compile)
    python content/build_pdf.py --no-render  # skip render_latex.py, just compile

Strategy:
  1. (default) Run ``render_latex.py`` to refresh book.tex / preamble.tex / parts.
  2. Pre-convert every SVG referenced from the LaTeX (screenshots and QR
     codes) into a ``.pdf`` sibling using Inkscape. Then ``\\includegraphics``
     can find each one without needing the LaTeX ``svg`` package (which has
     basename-collision issues when many SVGs share the same filename).
  3. Detect a LaTeX driver in this order:  latexmk+perl → xelatex → pdflatex.
  4. Run the chosen compiler twice (or latexmk once) so cross-refs and TOC
     resolve.
  5. Surface any error log lines so the user can diagnose without sifting
     through the full .log file.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

# This script prints non-ASCII glyphs (→, …, ✓, !) for progress output.
# On a default Windows console (cp1252) those crash with UnicodeEncodeError.
# Force UTF-8 on stdout/stderr so the build doesn't abort before TeX even runs.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parent
LATEX_DIR = ROOT / "output" / "latex"
BOOK_TEX = LATEX_DIR / "book.tex"
SCREENSHOTS_DIR = ROOT / "output" / "html" / "screenshots"
QRCODES_DIR = ROOT / "output" / "qrcodes"


def have(tool: str) -> bool:
    return shutil.which(tool) is not None


def run(cmd: list[str], cwd: Path) -> tuple[int, str]:
    """Run a command and return (returncode, combined_output_tail)."""
    print(f"  $ {' '.join(cmd)}  (in {cwd})")
    proc = subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8",
        errors="replace",
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    tail = "\n".join(out.splitlines()[-40:])
    return proc.returncode, tail


def render() -> int:
    print("[1/3] Re-rendering LaTeX sources…")
    proc = subprocess.run(
        [sys.executable, str(ROOT / "render_latex.py")],
        cwd=ROOT.parent,
    )
    return proc.returncode


def convert_svgs() -> int:
    """Convert every .svg in screenshots/ and qrcodes/ into a .pdf sibling
    using Inkscape (skips when .pdf is newer than .svg)."""
    if not have("inkscape"):
        print("ERROR: 'inkscape' not on PATH. Install Inkscape "
              "(https://inkscape.org) and ensure inkscape.exe is on PATH.",
              file=sys.stderr)
        return 1

    svgs: list[Path] = []
    if SCREENSHOTS_DIR.exists():
        svgs += [p for p in SCREENSHOTS_DIR.rglob("*.svg") if p.name.endswith(".bw.svg")]
    if QRCODES_DIR.exists():
        svgs += list(QRCODES_DIR.rglob("*.svg"))

    if not svgs:
        print("[2/3] No SVGs to convert.")
        return 0

    todo = []
    for s in svgs:
        pdf = s.with_suffix(".pdf")
        if not pdf.exists() or pdf.stat().st_mtime < s.stat().st_mtime:
            todo.append(s)

    if not todo:
        print(f"[2/3] All {len(svgs)} SVG → PDF conversions up to date.")
        return 0

    print(f"[2/3] Converting {len(todo)} of {len(svgs)} SVGs to PDF via Inkscape…")
    # Inkscape supports a shell mode that's much faster than spawning a
    # process per file. Build a script and pipe it in.
    #
    # export-text-to-path:true converts every text element to outline paths
    # before writing the PDF. This eliminates font-embedding warnings from
    # KDP's preflight (the screenshot SVGs use Cascadia/JetBrains-style
    # fallback fonts that Inkscape's PDF exporter can otherwise embed as
    # *unembedded subsets*, which KDP rejects as "fonts not properly
    # embedded"). Converting to paths is the most reliable fix and keeps
    # rendering pixel-identical.
    script_lines = []
    for s in todo:
        pdf = s.with_suffix(".pdf")
        script_lines.append(
            f'file-open:{s};'
            f'export-text-to-path:true;'
            f'export-filename:{pdf};export-do;file-close'
        )
    script = "\n".join(script_lines) + "\nquit\n"

    proc = subprocess.run(
        ["inkscape", "--shell"],
        input=script, capture_output=True, text=True, encoding="utf-8",
        errors="replace",
    )
    failed = [s for s in todo if not s.with_suffix(".pdf").exists()]
    if failed:
        print(f"  ! {len(failed)} SVGs failed to convert; first few:", file=sys.stderr)
        for s in failed[:5]:
            print(f"    - {s}", file=sys.stderr)
        print("  Inkscape stderr tail:", file=sys.stderr)
        print("\n".join((proc.stderr or "").splitlines()[-15:]), file=sys.stderr)
        return 1
    print(f"  ✓ {len(todo)} SVGs converted.")
    return 0


def compile_pdf() -> int:
    if not BOOK_TEX.exists():
        print(f"ERROR: {BOOK_TEX} not found. Run render_latex.py first "
              "(or omit --no-render).", file=sys.stderr)
        return 1

    if have("latexmk") and have("perl"):
        print("[3/3] Compiling with latexmk…")
        rc, tail = run(
            ["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error",
             "-file-line-error", "book.tex"],
            cwd=LATEX_DIR,
        )
        if rc != 0:
            print(tail, file=sys.stderr)
            print(f"\nlatexmk exited {rc}. Full log: {LATEX_DIR}/book.log",
                  file=sys.stderr)
            return rc
        print(f"  ✓ {LATEX_DIR}/book.pdf")
        return 0

    driver = "xelatex" if have("xelatex") else "pdflatex" if have("pdflatex") else None
    if driver is None:
        print("ERROR: No LaTeX compiler found (looked for latexmk+perl, "
              "xelatex, pdflatex). Install TeX Live, MiKTeX, or MacTeX.",
              file=sys.stderr)
        return 2

    print(f"[3/3] Compiling with {driver} (xelatex → makeindex → xelatex × 2)…")
    # 3 compile passes around a makeindex run so imakeidx's index resolves.
    for n in (1, 2, 3):
        rc, tail = run(
            [driver, "-interaction=nonstopmode", "-halt-on-error",
             "-file-line-error", "book.tex"],
            cwd=LATEX_DIR,
        )
        if rc != 0:
            print(tail, file=sys.stderr)
            print(f"\n{driver} (pass {n}) exited {rc}. Full log: {LATEX_DIR}/book.log",
                  file=sys.stderr)
            return rc
        if n == 1 and have("makeindex") and (LATEX_DIR / "book.idx").exists():
            run(["makeindex", "book.idx"], cwd=LATEX_DIR)
    print(f"  ✓ {LATEX_DIR}/book.pdf")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-render", action="store_true",
                    help="Skip render_latex.py; just convert SVGs and compile.")
    ap.add_argument("--no-svg", action="store_true",
                    help="Skip the SVG → PDF conversion step.")
    args = ap.parse_args()

    if not args.no_render:
        rc = render()
        if rc != 0:
            return rc

    if not args.no_svg:
        rc = convert_svgs()
        if rc != 0:
            return rc

    return compile_pdf()


if __name__ == "__main__":
    sys.exit(main())

