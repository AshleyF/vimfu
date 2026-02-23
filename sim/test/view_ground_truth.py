"""Quick view of all captured tmux scenarios."""
import json, sys
d = json.load(open("test/tmux_behavior_ground_truth.json"))
for k, sc in d.items():
    sb = sc["status_bar"].rstrip()
    cur = sc["cursor"]
    # Count non-empty pane lines
    pane_content = [l for l in sc["pane_lines"] if l.strip()]
    print(f"{k:45s} | sb={sb:60s} | cur=({cur['row']:2d},{cur['col']:2d}) | {len(pane_content)} content lines")
