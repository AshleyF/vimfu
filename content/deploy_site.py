#!/usr/bin/env python3
"""Deploy the VimFu website to ``docs/`` for GitHub Pages.

Pipeline:
  1. Re-render all content into ``content/output/html/`` (HTML site,
     redirect map, errata pages).
  2. Build the bundled, minified single-file simulator into
     ``book/output/sim/index.html`` via ``sim/build.py``.
  3. Wipe ``docs/`` (preserving ``CNAME`` if present), then copy the
     entire HTML output there.
  4. Replace ``docs/sim/`` with the bundled single-file simulator.
  5. Drop a ``.nojekyll`` marker so GitHub Pages serves all files
     verbatim (no Jekyll preprocessing of underscore-prefixed paths).

Usage:
    python content/deploy_site.py            # full pipeline
    python content/deploy_site.py --skip-render
    python content/deploy_site.py --skip-sim

GitHub Pages: in repo Settings -> Pages, set "Deploy from a branch",
branch = main, folder = ``/docs``. Commit ``docs/`` to publish.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIR = ROOT / "content"
HTML_OUT = CONTENT_DIR / "output" / "html"
SIM_BUILD_SCRIPT = ROOT / "sim" / "build.py"
SIM_BUNDLED = ROOT / "book" / "output" / "sim" / "index.html"
DOCS_DIR = ROOT / "docs"

# Files inside docs/ we want to keep across re-deploys.
PRESERVE = {"CNAME", ".gitkeep", "vimfu_light.png", "vimfu_dark.png", "icon.png", "cover_thumb.png"}


def run(cmd: list[str], cwd: Path = ROOT) -> None:
    print(f"  $ {' '.join(cmd)}")
    res = subprocess.run(cmd, cwd=str(cwd))
    if res.returncode != 0:
        sys.exit(f"!! Command failed: {' '.join(cmd)}")


def render_content(py: str) -> None:
    print("[1/4] Rendering content -> content/output/html/")
    run([py, str(CONTENT_DIR / "render_redirects.py")])
    run([py, str(CONTENT_DIR / "render_errata.py")])
    run([py, str(CONTENT_DIR / "render_html.py")])


def build_sim(py: str) -> None:
    print("[2/4] Building bundled simulator -> book/output/sim/index.html")
    run([py, str(SIM_BUILD_SCRIPT)])
    if not SIM_BUNDLED.exists():
        sys.exit(f"!! Expected bundled sim at {SIM_BUNDLED} but it's missing.")


def wipe_docs() -> dict[str, bytes]:
    """Save preserved files, wipe docs/, return saved blobs to restore."""
    saved: dict[str, bytes] = {}
    if DOCS_DIR.exists():
        for name in PRESERVE:
            p = DOCS_DIR / name
            if p.is_file():
                saved[name] = p.read_bytes()
        shutil.rmtree(DOCS_DIR)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    return saved


def restore(saved: dict[str, bytes]) -> None:
    for name, data in saved.items():
        (DOCS_DIR / name).write_bytes(data)


def copy_html() -> None:
    print(f"[3/4] Copying {HTML_OUT.relative_to(ROOT)} -> docs/")
    if not HTML_OUT.exists():
        sys.exit(f"!! No HTML output at {HTML_OUT}. Run renders first.")
    # copytree with dirs_exist_ok handles the docs/ already-mkdired case.
    shutil.copytree(HTML_OUT, DOCS_DIR, dirs_exist_ok=True)


def replace_sim() -> None:
    print("[4/4] Replacing docs/sim/ with bundled single-file simulator")
    sim_dir = DOCS_DIR / "sim"
    if sim_dir.exists():
        shutil.rmtree(sim_dir)
    sim_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SIM_BUNDLED, sim_dir / "index.html")
    # README is fine to keep alongside the bundled file.
    src_readme = HTML_OUT / "sim" / "README.md"
    if src_readme.exists():
        shutil.copy2(src_readme, sim_dir / "README.md")


def write_nojekyll() -> None:
    (DOCS_DIR / ".nojekyll").write_text("", encoding="utf-8")


def report() -> None:
    files = list(DOCS_DIR.rglob("*"))
    n_files = sum(1 for f in files if f.is_file())
    total = sum(f.stat().st_size for f in files if f.is_file())
    print()
    print(f"OK  docs/ contains {n_files} files, {total/1_048_576:.2f} MB total.")
    sim_idx = DOCS_DIR / "sim" / "index.html"
    if sim_idx.exists():
        print(f"    sim:    {sim_idx.stat().st_size/1024:.0f} KB (bundled)")
    redirects = DOCS_DIR / "r"
    if redirects.exists():
        n_r = sum(1 for _ in redirects.iterdir() if _.is_dir())
        print(f"    redirs: {n_r} short URLs under /r/")
    print()
    print("Next: commit docs/ and push. GitHub Pages settings ->")
    print("      Deploy from branch  =  main  /  /docs")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--skip-render", action="store_true",
                   help="skip the HTML/redirects/errata render step")
    p.add_argument("--skip-sim", action="store_true",
                   help="skip rebuilding the bundled simulator")
    p.add_argument("--python", default=sys.executable,
                   help="python interpreter to use for sub-builds")
    args = p.parse_args()

    if not args.skip_render:
        render_content(args.python)
    if not args.skip_sim:
        build_sim(args.python)

    saved = wipe_docs()
    copy_html()
    replace_sim()
    restore(saved)
    write_nojekyll()
    report()


if __name__ == "__main__":
    main()
