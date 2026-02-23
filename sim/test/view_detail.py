"""Detailed view of specific scenarios from ground truth."""
import json
d = json.load(open("test/tmux_behavior_ground_truth.json"))

for k in ["vsplit", "hsplit", "three_panes", "close_confirm", "zoomed", "cmd_prompt_empty", "after_resize"]:
    sc = d[k]
    print(f"\n{'='*80}")
    print(f"=== {k} === cursor={sc['cursor']}")
    print(f"{'='*80}")
    for i, line in enumerate(sc["screen"]):
        tag = " <STATUS>" if i == len(sc["screen"]) - 1 else ""
        print(f"  [{i:2d}] {repr(line[:80])}{tag}")
