"""
Compare sim syntax colors against nvim ground truth.

Loads the nvim capture (nvim_syntax_colors.json) and renders the same
file through the sim (via Node subprocess), then compares color runs
line by line.

Usage:
    cd sim
    python test/compare_nvim_syntax.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent

def get_sim_colors():
    """Run a Node script that renders demo.py through the sim and dumps color data."""
    js = r"""
import { VimEngine } from '../src/engine.js';
import { Screen } from '../src/screen.js';
import { SAMPLE_PYTHON } from '../src/samples.js';
import '../src/langs/python.js';

const ROWS = 20;
const COLS = 80;

const engine = new VimEngine({ rows: ROWS, cols: COLS });
engine.filename = SAMPLE_PYTHON.filename;
engine.loadFile(SAMPLE_PYTHON.content);

const screen = new Screen(ROWS, COLS, 'nvim_default');

const results = {};
const textRows = ROWS - 2;

function capture(label) {
    const frame = screen.render(engine);
    results[label] = {
        lines: frame.lines.slice(0, textRows).map(l => ({
            text: l.text,
            runs: l.runs
        }))
    };
}

// Same scroll positions as the nvim capture
capture('top');
for (let i = 2; i <= 8; i++) {
    engine.scrollTop = (i - 1) * textRows;
    capture('page' + i);
}
engine.scrollTop = 0;
capture('back_to_top');

console.log(JSON.stringify(results));
"""
    tmp = _here / '_sim_render.mjs'
    tmp.write_text(js, encoding='utf-8')
    try:
        result = subprocess.run(
            ['node', str(tmp)],
            capture_output=True, text=True, cwd=str(_here.parent)
        )
        if result.returncode != 0:
            print("Node error:", result.stderr)
            sys.exit(1)
        return json.loads(result.stdout)
    finally:
        tmp.unlink()


def compare():
    nvim_path = _here / 'nvim_syntax_colors.json'
    if not nvim_path.exists():
        print("ERROR: Run capture_nvim_syntax.py first")
        sys.exit(1)

    nvim = json.load(open(nvim_path))
    sim = get_sim_colors()

    total_lines = 0
    matching_lines = 0
    mismatches = []

    for page_name in nvim:
        if page_name not in sim:
            continue

        nvim_lines = nvim[page_name]['lines']
        sim_lines = sim[page_name]['lines']

        for i in range(min(len(nvim_lines), len(sim_lines))):
            total_lines += 1
            nvim_text = nvim_lines[i]['text']
            sim_text = sim_lines[i]['text']

            if nvim_text != sim_text:
                # Text mismatch (different scroll) - skip
                continue

            # Compare fg color at each column
            nvim_fgs = expand_runs(nvim_lines[i]['runs'], 'fg')
            sim_fgs = expand_runs(sim_lines[i]['runs'], 'fg')

            cols_match = True
            first_diff = None
            for col in range(min(len(nvim_fgs), len(sim_fgs))):
                if nvim_fgs[col] != sim_fgs[col]:
                    cols_match = False
                    if first_diff is None:
                        first_diff = col
                    break

            if cols_match:
                matching_lines += 1
            else:
                text = nvim_text.rstrip()
                if text:  # Skip blank lines
                    snippet = text[first_diff:first_diff + 20]
                    mismatches.append({
                        'page': page_name,
                        'line': i,
                        'col': first_diff,
                        'nvim_fg': nvim_fgs[first_diff],
                        'sim_fg': sim_fgs[first_diff],
                        'snippet': snippet,
                        'text': text,
                    })

    print(f"\n{'='*70}")
    print(f"COMPARISON: sim vs nvim")
    print(f"{'='*70}")
    print(f"Total lines compared: {total_lines}")
    print(f"Matching lines:       {matching_lines}")
    print(f"Mismatched lines:     {len(mismatches)}")

    if mismatches:
        print(f"\n{'='*70}")
        print(f"MISMATCHES (first {min(len(mismatches), 30)}):")
        print(f"{'='*70}")
        for m in mismatches[:30]:
            print(f"\n  {m['page']} line {m['line']}: col {m['col']}")
            print(f"    text:    '{m['text'][:60]}'")
            print(f"    at col:  '{m['snippet']}'")
            print(f"    nvim_fg: {m['nvim_fg']}")
            print(f"    sim_fg:  {m['sim_fg']}")

    return len(mismatches) == 0


def expand_runs(runs, key):
    """Expand runs into per-column array."""
    result = []
    for run in runs:
        result.extend([run[key]] * run['n'])
    return result


if __name__ == '__main__':
    ok = compare()
    sys.exit(0 if ok else 1)
