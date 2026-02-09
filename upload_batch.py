"""
Batch upload VimFu videos 002-020 to YouTube, scheduled one per day.

Usage:
    python upload_batch.py
"""

import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Reuse the upload logic from upload_youtube.py
sys.path.insert(0, str(Path(__file__).parent))
from upload_youtube import upload_video

VIDEOS_DIR = Path(__file__).parent / "shellpilot" / "videos"

# Videos 002-020, scheduled starting tomorrow (Feb 9, 2026) at 16:00 UTC
START_DATE = datetime(2026, 2, 9, 16, 0, 0, tzinfo=timezone.utc)

videos = []
for num in range(2, 21):  # 002 through 020
    prefix = f"{num:04d}_"
    matches = sorted(VIDEOS_DIR.glob(f"{prefix}*/{prefix}*.json"))
    if matches:
        videos.append(matches[0])
    else:
        print(f"WARNING: No JSON found for video {num:04d}, skipping.")

print(f"Found {len(videos)} videos to upload.\n")

for i, json_path in enumerate(videos):
    schedule_dt = START_DATE + timedelta(days=i)
    print(f"{'=' * 60}")
    print(f"[{i+1}/{len(videos)}] {json_path.parent.name}")
    print(f"  Scheduled: {schedule_dt.isoformat()}")
    print(f"{'=' * 60}")
    try:
        upload_video(json_path, schedule_dt=schedule_dt)
    except Exception as e:
        print(f"ERROR uploading {json_path.name}: {e}")
        print("Continuing with next video...\n")
        continue
    print()

print("All done!")
