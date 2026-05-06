"""
Wire ``{"type": "example", "ref": "<id>"}`` blocks into topic JSONs.

For every example file in ``content/examples/*.json``, this script reads
the ``topic`` field (the topic id the example belongs to) and inserts a
matching ``example`` block into that topic's ``blocks`` array, immediately
before the first ``qr`` block (or at the end if none).

Idempotent: existing ``example`` blocks are removed first, then re-added
in the canonical order, so re-running the script always produces the
same result.

Usage:
    python content/wire_examples.py            # apply
    python content/wire_examples.py --dry-run  # preview
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PARTS_DIR = ROOT / "parts"
EXAMPLES_DIR = ROOT / "examples"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    # topic_id -> [example_id, ...]
    topic_to_examples: dict[str, list[str]] = defaultdict(list)
    for p in sorted(EXAMPLES_DIR.glob("*.json")):
        try:
            ex = json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"  ! JSON error in {p.relative_to(ROOT)}: {e}", file=sys.stderr)
            continue
        ex_id = ex.get("id")
        topic_id = ex.get("topic")
        if not ex_id or not topic_id:
            print(f"  ! missing id/topic in {p.name}", file=sys.stderr)
            continue
        topic_to_examples[topic_id].append(ex_id)

    # Index topic files by topic id
    topic_files: dict[str, Path] = {}
    for p in sorted(PARTS_DIR.glob("*/*.json")):
        try:
            t = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if tid := t.get("id"):
            topic_files[tid] = p

    # Wire
    updated = 0
    orphans: list[str] = []
    for topic_id, ex_ids in sorted(topic_to_examples.items()):
        path = topic_files.get(topic_id)
        if path is None:
            orphans.append(topic_id)
            continue
        t = json.loads(path.read_text(encoding="utf-8"))
        blocks = list(t.get("blocks", []))

        # Remove all existing example blocks (clean slate).
        blocks = [b for b in blocks if b.get("type") != "example"]

        # Find insertion point: just before the first 'qr' block.
        insert_at = len(blocks)
        for i, b in enumerate(blocks):
            if b.get("type") == "qr":
                insert_at = i
                break

        new_blocks = [{"type": "example", "ref": eid} for eid in ex_ids]
        blocks[insert_at:insert_at] = new_blocks
        t["blocks"] = blocks

        if not args.dry_run:
            path.write_text(json.dumps(t, indent=2) + "\n", encoding="utf-8")
        updated += 1

    if orphans:
        print("Orphan examples (topic id not found):", file=sys.stderr)
        for o in orphans:
            print(f"  - {o}", file=sys.stderr)

    action = "would update" if args.dry_run else "updated"
    print(f"{action} {updated} topic(s) with example refs")
    print(f"  examples: {sum(len(v) for v in topic_to_examples.values())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
