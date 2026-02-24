#!/usr/bin/env python3
"""
Build the VimFu simulator for production.

Extracts inline JS from index.html, bundles with esbuild
(tree-shaking + minification), minifies the CSS, and produces
a self-contained HTML file in book/output/sim/.

Usage:
    python sim/build.py
"""

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parent          # sim/
ROOT    = SIM_DIR.parent                            # vimfu/
OUT_DIR = ROOT / "book" / "output" / "sim"

HTML_FILES = ["index.html"]


# ── Helpers ──────────────────────────────────────────────────

def extract_parts(html: str):
    """Split an HTML file into (before_style, css, between, js, after_script)."""
    # CSS: <style> ... </style>
    m_css = re.search(r"<style>(.*?)</style>", html, re.DOTALL)
    if not m_css:
        sys.exit("ERROR: no <style> block found")

    # JS: <script type="module"> ... </script>
    m_js = re.search(
        r'<script type="module">(.*?)</script>', html, re.DOTALL
    )
    if not m_js:
        sys.exit("ERROR: no <script type=\"module\"> block found")

    css = m_css.group(1)
    js  = m_js.group(1)

    before_style   = html[: m_css.start()]
    between        = html[m_css.end() : m_js.start()]
    after_script   = html[m_js.end() :]

    return before_style, css, between, js, after_script


def minify_css(css: str) -> str:
    """Minimal CSS minifier — good enough for inline styles."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)  # comments
    css = re.sub(r"\s+", " ", css)                        # collapse whitespace
    css = re.sub(r"\s*([{}:;,>~+])\s*", r"\1", css)      # trim around symbols
    css = re.sub(r";\s*}", "}", css)                      # drop trailing ;
    return css.strip()


def bundle_js(js_code: str, work_dir: Path) -> str:
    """Write JS to a temp file, bundle + minify with esbuild, return result."""
    entry = work_dir / "_entry.js"
    entry.write_text(js_code, encoding="utf-8")

    npx = "npx.cmd" if sys.platform == "win32" else "npx"
    result = subprocess.run(
        [
            npx, "--yes", "esbuild",
            str(entry),
            "--bundle",
            "--minify",
            "--format=esm",
            "--platform=browser",
            "--target=es2020",
            "--tree-shaking=true",
        ],
        capture_output=True,
        text=True,
        cwd=str(SIM_DIR),
    )
    if result.returncode != 0:
        print("esbuild STDERR:", result.stderr, file=sys.stderr)
        sys.exit(f"esbuild failed (exit {result.returncode})")

    return result.stdout


def build_html(name: str, tmp: Path) -> None:
    """Build one HTML file."""
    src = SIM_DIR / name
    html = src.read_text(encoding="utf-8")

    print(f"  {name}: extracting CSS + JS …")
    before, css, between, js, after = extract_parts(html)

    print(f"  {name}: minifying CSS ({len(css)} → ", end="")
    css_min = minify_css(css)
    print(f"{len(css_min)} bytes)")

    print(f"  {name}: bundling JS with esbuild …")
    js_min = bundle_js(js, tmp)
    print(f"  {name}: JS bundle {len(js_min)} bytes")

    # Reassemble
    out_html = (
        before
        + "<style>" + css_min + "</style>"
        + between
        + '<script type="module">' + js_min + "</script>"
        + after
    )

    dest = OUT_DIR / name
    dest.write_text(out_html, encoding="utf-8")

    orig_size = len(html.encode("utf-8"))
    out_size  = len(out_html.encode("utf-8"))
    print(f"  {name}: {orig_size:,} → {out_size:,} bytes  "
          f"({100 * out_size / orig_size:.0f}%)")


# ── Main ─────────────────────────────────────────────────────

def main():
    print(f"Building VimFu simulator → {OUT_DIR.relative_to(ROOT)}/\n")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp_str:
        tmp = Path(tmp_str)

        # Symlink src/ into the temp dir so esbuild can resolve imports
        # (we write _entry.js there and it does `import … from './src/…'`)
        src_link = tmp / "src"
        # On Windows, use junction (doesn't need admin privileges)
        if sys.platform == "win32":
            subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(src_link), str(SIM_DIR / "src")],
                capture_output=True,
            )
        else:
            src_link.symlink_to(SIM_DIR / "src")

        for name in HTML_FILES:
            build_html(name, tmp)

    print(f"\n✓ Done — output in {OUT_DIR.relative_to(ROOT)}/")

    # List output
    for f in sorted(OUT_DIR.iterdir()):
        if f.is_file():
            size = f.stat().st_size
            print(f"  {f.name:30s} {size:>8,} bytes")


if __name__ == "__main__":
    main()
