"""
Upload a VimFu video to YouTube using the curriculum JSON file.

Usage:
    python upload_youtube.py curriculum/shorts/0001_what_is_vim.json
    python upload_youtube.py --schedule 2025-07-20T12:00:00Z curriculum/shorts/*.json
    python upload_youtube.py --public curriculum/shorts/*.json

The lesson JSON contains both the lesson definition and a "youtube"
section with upload settings.  Video and thumbnail files are located
automatically at  shellpilot/videos/{stem}/{stem}.mp4 / .png.

After upload the youtube.videoId and youtube.url fields are written
back into the lesson JSON.

Privacy logic (highest priority first):
    --schedule <future>     private + publishAt (YouTube auto-publishes at the scheduled time)
    --public / --private    explicit override
    (default)               private (from youtube.privacyStatus)
First-time setup:
    1. Go to https://console.cloud.google.com/
    2. Create a project (or use existing)
    3. Enable the "YouTube Data API v3"
    4. Create OAuth 2.0 credentials (Desktop app)
    5. Download the client secret JSON and save as:
           client_secret.json   (in this repo root)
    6. pip install google-auth google-auth-oauthlib google-api-python-client

The first run will open a browser for OAuth consent. After that,
a token is cached in youtube_token.json for reuse.
"""

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
import socket

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google_auth_httplib2 import AuthorizedHttp
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import httplib2

# Force IPv4 — httplib2 tries IPv6 first, which is broken on some networks
_original_getaddrinfo = socket.getaddrinfo
def _ipv4_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    return _original_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
socket.getaddrinfo = _ipv4_getaddrinfo

# OAuth scopes needed for uploading + setting thumbnails
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
]

REPO_ROOT = Path(__file__).parent
CLIENT_SECRET = REPO_ROOT / "client_secret.json"
TOKEN_CACHE = REPO_ROOT / "youtube_token.json"


def get_authenticated_service():
    """Build an authenticated YouTube API client."""
    creds = None

    # Load cached token
    if TOKEN_CACHE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_CACHE), SCOPES)

    # Refresh or re-authorize
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CLIENT_SECRET.exists():
                print(f"ERROR: {CLIENT_SECRET} not found.")
                print("Download OAuth client secret from Google Cloud Console.")
                print("See docstring at top of this file for setup instructions.")
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CLIENT_SECRET), SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save for next time
        TOKEN_CACHE.write_text(creds.to_json())

    # httplib2 with 5-minute timeout for large uploads
    http = AuthorizedHttp(creds, http=httplib2.Http(timeout=300))
    return build("youtube", "v3", http=http)


def upload_video(lesson_path: Path, schedule_dt: datetime = None,
                 privacy_override: str = None):
    """Upload video + thumbnail using the curriculum JSON file.

    Args:
        lesson_path:      Path to the curriculum JSON file.
        schedule_dt:      If a future datetime, publish as public + scheduled.
        privacy_override: "public" or "private" — overrides all other logic.
    """
    meta = json.loads(lesson_path.read_text(encoding="utf-8"))
    yt = meta.get("youtube", {})
    stem = lesson_path.stem

    # Derive video/thumbnail paths from the standard output directory
    videos_dir = REPO_ROOT / "shellpilot" / "videos" / stem
    video_path = videos_dir / f"{stem}.mp4"
    thumb_path = videos_dir / f"{stem}.png"

    if not video_path.exists():
        print(f"ERROR: Video not found: {video_path}")
        sys.exit(1)

    # Determine privacy / scheduling
    scheduled = (
        schedule_dt is not None
        and schedule_dt > datetime.now(timezone.utc)
    )
    if scheduled:
        privacy = "private"
    elif privacy_override:
        privacy = privacy_override
    else:
        privacy = yt.get("privacyStatus", "private")

    print(f"Title:     {meta['title']}")
    print(f"Video:     {video_path.name}")
    print(f"Thumbnail: {thumb_path.name if thumb_path.exists() else '(none)'}")
    print(f"Privacy:   {privacy}")
    if scheduled:
        print(f"Scheduled: {schedule_dt.isoformat()}")
    if meta.get('playlist'):
        print(f"Playlist:  {meta['playlist']}")
    print()

    youtube = get_authenticated_service()

    # --- Upload video ---
    body = {
        "snippet": {
            "title": meta["title"],
            "description": meta.get("description", ""),
            "tags": meta.get("tags", []),
            "categoryId": yt.get("categoryId", "27"),
            "defaultLanguage": yt.get("language", "en"),
        },
        "status": {
            "privacyStatus": privacy,
            "madeForKids": yt.get("madeForKids", False),
            "selfDeclaredMadeForKids": yt.get("madeForKids", False),
        },
    }

    if scheduled:
        body["status"]["publishAt"] = schedule_dt.isoformat()

    media = MediaFileUpload(
        str(video_path),
        mimetype="video/mp4",
        resumable=True,
        chunksize=10 * 1024 * 1024,  # 10 MB chunks
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )

    print("Uploading video...")
    response = None
    retries = 0
    max_retries = 5
    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                pct = int(status.progress() * 100)
                print(f"  {pct}% uploaded")
            retries = 0  # Reset on success
        except Exception as e:
            retries += 1
            if retries > max_retries:
                print(f"ERROR: Upload failed after {max_retries} retries: {e}")
                raise
            wait_time = min(2 ** retries, 60)
            print(f"  Upload error (retry {retries}/{max_retries} in {wait_time}s): {e}")
            import time
            time.sleep(wait_time)

    video_id = response["id"]
    print(f"Upload complete! Video ID: {video_id}")
    print(f"  https://youtube.com/watch?v={video_id}")

    # --- Set thumbnail ---
    if thumb_path.exists():
        print("Setting thumbnail...")
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(str(thumb_path), mimetype="image/png"),
        ).execute()
        print("Thumbnail set!")
    else:
        print("No thumbnail found, skipping.")

    # --- Add to playlist ---
    playlist_name = meta.get("playlist", "")
    if playlist_name:
        print(f"Adding to playlist: {playlist_name}")
        try:
            playlist_id = _find_or_create_playlist(youtube, playlist_name)
            youtube.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": playlist_id,
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": video_id,
                        },
                    }
                },
            ).execute()
            print(f"Added to playlist '{playlist_name}'")
        except Exception as e:
            print(f"Warning: Could not add to playlist: {e}")

    # --- Save video ID back into curriculum JSON ---
    yt["videoId"] = video_id
    yt["url"] = f"https://youtube.com/watch?v={video_id}"
    meta["youtube"] = yt
    lesson_path.write_text(
        json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"Curriculum JSON updated with video ID.")

    return video_id


def _find_or_create_playlist(youtube, title: str) -> str:
    """
    Find an existing playlist by title, or create a new one.
    Returns the playlist ID.
    """
    # Search existing playlists
    playlists = youtube.playlists().list(
        part="snippet",
        mine=True,
        maxResults=50,
    ).execute()

    for item in playlists.get("items", []):
        if item["snippet"]["title"] == title:
            return item["id"]

    # Not found — create it
    print(f"  Creating playlist '{title}'...")
    result = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": f"{title} — VimFu tutorial series",
            },
            "status": {
                "privacyStatus": "public",
            },
        },
    ).execute()
    return result["id"]


def main():
    parser = argparse.ArgumentParser(
        description="Upload VimFu videos to YouTube from curriculum JSON files."
    )
    parser.add_argument(
        "lessons", nargs="+", type=Path,
        help="One or more lesson JSON files (e.g. curriculum/shorts/*.json)."
    )
    parser.add_argument(
        "--schedule", "-s", dest="schedule", default=None,
        help="ISO 8601 datetime to schedule publish (e.g. 2025-07-20T12:00:00Z). "
             "If in the future, videos are set to public + scheduled."
    )
    parser.add_argument(
        "--schedule-daily", dest="schedule_daily", action="store_true",
        help="When used with --schedule, increment the date by one day per video. "
             "First video gets the --schedule date, second gets +1 day, etc."
    )
    parser.add_argument(
        "--no-sort", dest="no_sort", action="store_true",
        help="Process files in the order given on the command line, "
             "instead of sorting alphabetically."
    )
    privacy_group = parser.add_mutually_exclusive_group()
    privacy_group.add_argument(
        "--public", dest="privacy", action="store_const", const="public",
        help="Override privacy to public."
    )
    privacy_group.add_argument(
        "--private", dest="privacy", action="store_const", const="private",
        help="Override privacy to private."
    )
    args = parser.parse_args()

    # Parse schedule datetime if provided
    schedule_dt = None
    if args.schedule:
        try:
            schedule_dt = datetime.fromisoformat(args.schedule)
            # Assume UTC if no timezone specified
            if schedule_dt.tzinfo is None:
                schedule_dt = schedule_dt.replace(tzinfo=timezone.utc)
        except ValueError:
            parser.error(f"Invalid datetime: {args.schedule}")

    lessons = args.lessons if args.no_sort else sorted(args.lessons)
    for idx, path in enumerate(lessons):
        if not path.exists():
            print(f"ERROR: {path} not found, skipping.")
            continue
        # Skip lessons that are already uploaded
        data = json.loads(path.read_text(encoding='utf-8'))
        if data.get('youtube', {}).get('videoId'):
            print(f"SKIP: {path.name} (already uploaded: {data['youtube']['videoId']})")
            continue
        # Compute per-video schedule datetime
        video_schedule = None
        if schedule_dt:
            if args.schedule_daily:
                video_schedule = schedule_dt + timedelta(days=idx)
            else:
                video_schedule = schedule_dt
        print(f"{'=' * 60}")
        print(f"Processing: {path.name}")
        print(f"{'=' * 60}")
        upload_video(path, schedule_dt=video_schedule, privacy_override=args.privacy)
        print()


if __name__ == "__main__":
    main()
