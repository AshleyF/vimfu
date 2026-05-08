# Building the PDF book

The book is generated from the JSON content in `content/parts/**/*.json` →
LaTeX (`content/render_latex.py`) → PDF (`content/build_pdf.py`).

```
python content/build_pdf.py
```

Output: `content/output/latex/book.pdf`.

## Prerequisites (one-time install)

You need **two** external tools on your `PATH`:

1. **A LaTeX distribution** — gives you `xelatex` / `pdflatex` (and
   ideally `latexmk`).
2. **Inkscape** — used to convert the screenshot and QR-code SVGs to PDF
   so LaTeX can embed them.

### Windows (recommended: MiKTeX + Inkscape via winget)

```powershell
winget install --id MiKTeX.MiKTeX
winget install --id Inkscape.Inkscape
```

Then make sure `inkscape.exe` is on your `PATH`. The default install puts
it at `C:\Program Files\Inkscape\bin\inkscape.exe`. Add that folder to
your user `PATH` via *System Properties → Environment Variables*, or run
this once in PowerShell (admin not required for user-scope):

```powershell
$ink = "C:\Program Files\Inkscape\bin"
[Environment]::SetEnvironmentVariable(
  "Path",
  [Environment]::GetEnvironmentVariable("Path","User") + ";$ink",
  "User")
```

Open a fresh terminal so the new `PATH` takes effect.

**Optional** — install Strawberry Perl if you want to use `latexmk`
(cleaner re-run handling). MiKTeX's `latexmk` wrapper is a Perl script:

```powershell
winget install --id StrawberryPerl.StrawberryPerl
```

Without Perl, `build_pdf.py` automatically falls back to running
`xelatex` twice, which works just as well.

### macOS

```bash
brew install --cask mactex inkscape
```

After install, open a new shell so `xelatex` and `inkscape` are on your
`PATH` (MacTeX puts binaries in `/Library/TeX/texbin`).

### Linux (Debian/Ubuntu)

```bash
sudo apt install texlive-xetex texlive-fonts-extra texlive-latex-extra \
                 latexmk inkscape
```

Other distros: install your equivalent of `texlive-xetex`,
`texlive-latex-extra`, `latexmk`, and `inkscape`.

## How the build works

1. **`render_latex.py`** — reads the JSON content, applies the `book`
   audience filter, and writes:
   - `output/latex/preamble.tex` — packages, colours, custom commands.
   - `output/latex/parts/<part>/<topic>.tex` — one file per topic.
   - `output/latex/parts/<part>/_part.tex` — `\part{}` + `\input`s.
   - `output/latex/book.tex` — master with TOC and every part.
2. **SVG → PDF pre-conversion** — `build_pdf.py` walks
   `output/html/screenshots/*/frame_*.bw.svg` and
   `output/qrcodes/**/*.svg` and runs Inkscape (in `--shell` batch mode)
   to produce `.pdf` siblings. We do this *before* compile so LaTeX uses
   plain `\includegraphics{path/to/file}` (no `.svg` extension), which
   then resolves to the pre-built `.pdf`. This avoids the LaTeX `svg`
   package entirely (it has basename-collision issues when many SVGs
   share the same filename, e.g. `frame_01.bw.svg`).
3. **LaTeX compile** — prefers `latexmk` if `perl` is also available,
   otherwise runs `xelatex` twice (so cross-refs and the TOC resolve).

## CLI options

```
python content/build_pdf.py              # full build
python content/build_pdf.py --no-render  # skip render_latex.py, reuse existing .tex
python content/build_pdf.py --no-svg     # skip Inkscape (use cached .pdf siblings)
```

The SVG conversion is incremental — it only re-runs Inkscape on SVGs
whose `.pdf` is missing or older than the source.

## Troubleshooting

- **"No LaTeX compiler found"** — install MiKTeX/TeX Live/MacTeX (above)
  and open a new terminal so the `PATH` change takes effect.
- **"'inkscape' not on PATH"** — install Inkscape and add its `bin`
  folder to `PATH` (see Windows section above).
- **"Missing character: There is no — in font ec-lmr10"** — the renderer
  already replaces em/en-dashes; if you see this anyway, search
  `output/latex/` for any literal `—` and report it as a bug in
  `render_latex.py` (some path is bypassing `tex_escape`).
- **First-run MiKTeX prompts for missing packages** — let it install on
  the fly. Subsequent builds will be silent.
- **Compile fails partway through with a topic-specific error** — open
  `output/latex/book.log`, search for `! ` (LaTeX errors all start with
  bang). The line number in the error is relative to the originating
  `parts/<part>/<topic>.tex` file, not `book.tex`.
