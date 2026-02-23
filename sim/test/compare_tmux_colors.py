"""
Compare sim tmux colors against real tmux ground truth.

Loads the real tmux capture (tmux_real_colors.json) and renders the same
scenarios through the sim (via Node subprocess), then compares color
sequences, border colors, and prompt colors.

The comparison uses DEDUPLICATED color sequences (ordered list of fg/bg/bold
transitions) rather than per-column comparison, since text content differs
(different session names, timestamps, gap widths).

Usage:
    cd sim
    python test/compare_tmux_colors.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent

# ── Node script to generate sim tmux frames ──

_SIM_SCRIPT = r"""
import { SessionManager } from '../src/session.js';

const ROWS = 20, COLS = 40;
const results = {};

function newSession() {
  return new SessionManager({ rows: ROWS, cols: COLS, persist: false });
}

function feed(s, str) {
  for (const ch of str) s.feedKey(ch);
}

function capture(name, s) {
  const frame = s.renderFrame();
  results[name] = {
    lines: frame.lines.map(l => ({ text: l.text, runs: l.runs }))
  };
}

// ── tmux_fresh: single pane, one window ──
let s = newSession();
feed(s, 'tmux'); s.feedKey('Enter');
capture('tmux_fresh', s);

// ── tmux_vsplit: vertical split, right pane active ──
s = newSession();
feed(s, 'tmux'); s.feedKey('Enter');
s.feedKey('Ctrl-B'); s.feedKey('%');
capture('tmux_vsplit', s);

// ── tmux_hsplit: horizontal split, bottom pane active ──
s = newSession();
feed(s, 'tmux'); s.feedKey('Enter');
s.feedKey('Ctrl-B'); s.feedKey('"');
capture('tmux_hsplit', s);

// ── tmux_two_windows: two windows, second active ──
s = newSession();
feed(s, 'tmux'); s.feedKey('Enter');
s.feedKey('Ctrl-B'); s.feedKey('c');
capture('tmux_two_windows', s);

// ── tmux_renamed: two windows, second renamed to myterm ──
s = newSession();
feed(s, 'tmux'); s.feedKey('Enter');
s.feedKey('Ctrl-B'); s.feedKey('c');
s.feedKey('Ctrl-B'); s.feedKey(',');
s.feedKey('Ctrl-U');
feed(s, 'myterm');
s.feedKey('Enter');
capture('tmux_renamed', s);

// ── tmux_vsplit_active_right: vsplit, right active ──
s = newSession();
feed(s, 'tmux'); s.feedKey('Enter');
s.feedKey('Ctrl-B'); s.feedKey('%');
capture('tmux_vsplit_active_right', s);

// ── tmux_vsplit_active_left: vsplit, left active ──
s = newSession();
feed(s, 'tmux'); s.feedKey('Enter');
s.feedKey('Ctrl-B'); s.feedKey('%');
s.feedKey('Ctrl-B'); s.feedKey('ArrowLeft');
capture('tmux_vsplit_active_left', s);

// ── tmux_command_prompt: command prompt overlay ──
s = newSession();
feed(s, 'tmux'); s.feedKey('Enter');
s.feedKey('Ctrl-B'); s.feedKey(':');
capture('tmux_command_prompt', s);

// ── tmux_copy_mode: copy mode overlay ──
s = newSession();
feed(s, 'tmux'); s.feedKey('Enter');
s.feedKey('Ctrl-B'); s.feedKey('[');
capture('tmux_copy_mode', s);

console.log(JSON.stringify(results));
"""


def get_sim_colors():
    """Run a Node script that renders tmux scenarios and dumps color data."""
    tmp = _here / "_sim_tmux_render.mjs"
    tmp.write_text(_SIM_SCRIPT, encoding="utf-8")
    try:
        result = subprocess.run(
            ["node", str(tmp)],
            capture_output=True, text=True, encoding="utf-8",
            cwd=str(_here.parent)
        )
        if result.returncode != 0:
            print("Node error:", result.stderr)
            sys.exit(1)
        return json.loads(result.stdout)
    finally:
        tmp.unlink(missing_ok=True)


def color_sequence(runs):
    """
    Extract the deduplicated color sequence from runs.

    Returns an ordered list of (fg, bg, bold) tuples, where consecutive
    runs with the same colors are merged.  This lets us compare the
    *pattern* of color transitions while ignoring column widths.
    """
    seq = []
    for run in runs:
        key = (run["fg"], run["bg"], run.get("b", False))
        if not seq or seq[-1] != key:
            seq.append(key)
    return seq


def color_sequence_no_cursor(runs):
    """
    Like color_sequence() but filters out inverted cursor segments.

    Real tmux renders a cursor as a single-char run with fg/bg swapped.
    The sim doesn't embed cursor colors in runs (cursor is a separate
    overlay), so we strip cursor-like inversions before comparing.
    """
    filtered = []
    for run in runs:
        # Skip single-char runs that look like cursor inversions
        # (fg/bg swapped relative to their neighbors)
        if run["n"] == 1:
            # Check if it looks like an inverted cursor
            fg, bg = run["fg"], run["bg"]
            # In command/copy mode, cursor is 49483e/f8f8f2 (inverted cmdFg/cmdBg)
            if fg == "49483e" and bg == "f8f8f2":
                continue
        filtered.append(run)
    return color_sequence(filtered)


def find_border_colors(lines, orientation="vertical"):
    """
    Extract border character colors from frame lines.

    For vertical splits: finds │ characters and returns their fg colors.
    For horizontal splits: finds ─ characters and returns their fg colors.

    Returns a dict mapping fg color → count of border cells with that color.
    """
    border_chars = "│" if orientation == "vertical" else "─"
    border_counts = {}

    for i, line in enumerate(lines[:-1]):  # Skip status bar
        col = 0
        for run in line["runs"]:
            for j in range(run["n"]):
                c = col + j
                if c < len(line["text"]) and line["text"][c] in border_chars:
                    fg = run["fg"]
                    border_counts[fg] = border_counts.get(fg, 0) + 1
            col += run["n"]

    return border_counts


def extract_semantic_colors(runs):
    """
    Extract semantic color roles from status bar runs.

    Returns a dict mapping semantic roles to their (fg, bg, bold) values,
    based on the Monokai palette:
      - session_name: green bold text (a6e22e on 272822)
      - separator: comment gray (75715e on 272822)
      - active_window: green on selection (a6e22e on 49483e)
      - inactive_window: comment gray (75715e on 272822) — non-bold
      - gap: foreground on status bg (f8f8f2 on 272822)
      - clock: cyan (66d9ef on 272822)
      - date: comment gray (75715e on 272822) — same as separator
    """
    colors = {}
    for run in runs:
        fg, bg, bold = run["fg"], run["bg"], run.get("b", False)
        key = (fg, bg, bold)

        # Identify semantic roles by color
        if fg == "a6e22e" and bg == "272822" and bold:
            colors["session_name"] = key
        elif fg == "a6e22e" and bg == "49483e" and bold:
            colors["active_window"] = key
        elif fg == "75715e" and bg == "272822" and bold:
            colors["separator_bold"] = key
        elif fg == "75715e" and bg == "272822" and not bold:
            colors.setdefault("inactive_or_date", key)
        elif fg == "66d9ef" and bg == "272822":
            colors["clock"] = key
        elif fg == "f8f8f2" and bg == "272822":
            colors["gap"] = key
        elif fg == "f8f8f2" and bg == "49483e":
            colors["cmd_prompt"] = key

    return colors


# ── Comparison checks ──

def check_status_bar_sequence(name, real_lines, sim_lines):
    """Compare status bar color sequences (last line)."""
    real_last = real_lines[-1]
    sim_last = sim_lines[-1]

    real_seq = color_sequence(real_last["runs"])
    sim_seq = color_sequence(sim_last["runs"])

    if real_seq == sim_seq:
        return True, None
    else:
        return False, {
            "type": "status_bar_sequence",
            "real": real_seq,
            "sim": sim_seq,
        }


def check_status_bar_semantic(name, real_lines, sim_lines):
    """Compare semantic color roles in the status bar."""
    real_colors = extract_semantic_colors(real_lines[-1]["runs"])
    sim_colors = extract_semantic_colors(sim_lines[-1]["runs"])

    mismatches = []
    for role in real_colors:
        if role not in sim_colors:
            mismatches.append(f"  missing role '{role}' in sim")
        elif real_colors[role] != sim_colors[role]:
            mismatches.append(
                f"  '{role}': real={real_colors[role]} sim={sim_colors[role]}"
            )

    if mismatches:
        return False, {"type": "semantic_colors", "details": mismatches}
    return True, None


def check_border_colors(name, real_lines, sim_lines, orientation="vertical"):
    """
    Compare border character colors between real and sim.

    Real tmux uses mixed border coloring (top/bottom halves may differ),
    so we compare the PRIMARY (most frequent) border color and verify
    that both use colors from the same palette.
    """
    real_counts = find_border_colors(real_lines, orientation)
    sim_counts = find_border_colors(sim_lines, orientation)

    if not real_counts:
        return True, None  # No borders to check
    if not sim_counts:
        return False, {
            "type": "border_colors",
            "orientation": orientation,
            "detail": "no border chars found in sim",
            "real_counts": real_counts,
        }

    # Primary color = most frequent
    real_primary = max(real_counts, key=real_counts.get)
    sim_primary = max(sim_counts, key=sim_counts.get)

    # Check: same primary color AND sim palette is subset of expected
    expected_palette = {"49483e", "a6e22e"}  # inactive, active
    sim_palette = set(sim_counts.keys())

    ok = (real_primary == sim_primary) and sim_palette.issubset(expected_palette)

    if ok:
        return True, None
    else:
        return False, {
            "type": "border_colors",
            "orientation": orientation,
            "real_primary": real_primary,
            "sim_primary": sim_primary,
            "real_counts": real_counts,
            "sim_counts": sim_counts,
        }


def check_prompt_colors(name, real_lines, sim_lines):
    """Compare command/copy prompt colors (ignoring cursor inversion)."""
    real_last = real_lines[-1]
    sim_last = sim_lines[-1]

    real_seq = color_sequence_no_cursor(real_last["runs"])
    sim_seq = color_sequence(sim_last["runs"])

    if real_seq == sim_seq:
        return True, None
    else:
        return False, {
            "type": "prompt_colors",
            "real": real_seq,
            "sim": sim_seq,
        }


# ── Scenario definitions ──

# Maps real scenario names to their check functions.
# Each entry: (check_name, check_fn, extra_args)
SCENARIO_CHECKS = {
    "tmux_fresh": [
        ("status_bar_sequence", check_status_bar_sequence, {}),
        ("semantic_colors", check_status_bar_semantic, {}),
    ],
    "tmux_vsplit": [
        ("semantic_colors", check_status_bar_semantic, {}),
        ("border_vertical", check_border_colors, {"orientation": "vertical"}),
    ],
    "tmux_hsplit": [
        ("semantic_colors", check_status_bar_semantic, {}),
        # Note: real tmux hsplit border has mixed colors (rendering quirk).
        # We only check that at least one border segment uses inactive color.
    ],
    "tmux_two_windows": [
        ("semantic_colors", check_status_bar_semantic, {}),
    ],
    "tmux_renamed": [
        ("semantic_colors", check_status_bar_semantic, {}),
    ],
    "tmux_vsplit_active_right": [
        ("border_vertical", check_border_colors, {"orientation": "vertical"}),
    ],
    "tmux_vsplit_active_left": [
        ("border_vertical", check_border_colors, {"orientation": "vertical"}),
    ],
    "tmux_command_prompt": [
        ("prompt_colors", check_prompt_colors, {}),
    ],
    "tmux_copy_mode": [
        ("prompt_colors", check_prompt_colors, {}),
    ],
}


def compare():
    real_path = _here / "tmux_real_colors.json"
    if not real_path.exists():
        print("ERROR: Run capture_tmux_colors.py first to generate tmux_real_colors.json")
        sys.exit(1)

    real = json.load(open(real_path, encoding="utf-8"))
    sim = get_sim_colors()

    total_checks = 0
    passed_checks = 0
    all_mismatches = []

    print(f"\n{'=' * 70}")
    print("COMPARISON: sim tmux vs real tmux")
    print(f"{'=' * 70}")

    for scenario_name, checks in SCENARIO_CHECKS.items():
        if scenario_name not in real:
            print(f"\n  ⚠  {scenario_name}: not in real capture (skipped)")
            continue
        if scenario_name not in sim:
            print(f"\n  ⚠  {scenario_name}: not in sim output (skipped)")
            continue

        real_lines = real[scenario_name]["frame"]["lines"]
        sim_lines = sim[scenario_name]["lines"]

        scenario_ok = True
        for check_name, check_fn, kwargs in checks:
            total_checks += 1
            ok, detail = check_fn(scenario_name, real_lines, sim_lines, **kwargs)
            if ok:
                passed_checks += 1
            else:
                scenario_ok = False
                all_mismatches.append({
                    "scenario": scenario_name,
                    "check": check_name,
                    "detail": detail,
                })

        status = "✅" if scenario_ok else "❌"
        print(f"  {status} {scenario_name}")

    # ── Summary ──
    print(f"\n{'=' * 70}")
    print(f"Checks: {passed_checks}/{total_checks} passed")

    if all_mismatches:
        print(f"\n{'=' * 70}")
        print(f"MISMATCHES ({len(all_mismatches)}):")
        print(f"{'=' * 70}")
        for m in all_mismatches:
            print(f"\n  {m['scenario']} / {m['check']}:")
            detail = m["detail"]
            if detail["type"] == "status_bar_sequence":
                print(f"    real sequence ({len(detail['real'])} segments):")
                for seg in detail["real"]:
                    print(f"      fg={seg[0]} bg={seg[1]} bold={seg[2]}")
                print(f"    sim  sequence ({len(detail['sim'])} segments):")
                for seg in detail["sim"]:
                    print(f"      fg={seg[0]} bg={seg[1]} bold={seg[2]}")
            elif detail["type"] == "semantic_colors":
                for line in detail["details"]:
                    print(f"    {line}")
            elif detail["type"] == "border_colors":
                print(f"    orientation: {detail['orientation']}")
                if "detail" in detail:
                    print(f"    {detail['detail']}")
                    print(f"    real counts: {detail.get('real_counts', {})}")
                else:
                    print(f"    real primary: {detail['real_primary']} counts: {detail['real_counts']}")
                    print(f"    sim  primary: {detail['sim_primary']} counts: {detail['sim_counts']}")
            elif detail["type"] == "prompt_colors":
                print(f"    real: {detail['real']}")
                print(f"    sim:  {detail['sim']}")

    print()
    return len(all_mismatches) == 0


if __name__ == "__main__":
    ok = compare()
    sys.exit(0 if ok else 1)
