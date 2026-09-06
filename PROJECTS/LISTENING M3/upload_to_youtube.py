#!/usr/bin/env python3
"""upload_to_youtube.py — Build + upload podcast tapes to YouTube for auto-captions.

For each tape:
  1. Build a .mp4 (cover image + audio) via ffmpeg.
  2. Upload to YouTube via the Data API v3 (OAuth 2.0, resumable videos.insert).
  3. Report the video ID so the slide deck can embed the YouTube player (CC comes
     free from YouTube's own auto-captioning).

OAuth: Google has no service-account path for uploads — this uses an installed-app
flow. The first run opens a browser once for you to approve the youtube.upload
scope; a long-lived refresh_token is saved to token.json. Subsequent runs are
fully automatic (no browser).

Prerequisites:
  - youtube/client_secret.json  (OAuth2 Desktop-app client ID JSON)
  - google-api-python-client, google-auth-oauthlib installed
  - ffmpeg on PATH

Usage:
  zsh -ic 'python3 upload_to_youtube.py'          # upload all 4 tapes
  zsh -ic 'python3 upload_to_youtube.py --tape 1' # upload a single tape
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

PROJ = Path(__file__).resolve().parent
ASSETS = PROJ / "slides" / "assets"
YT_DIR = PROJ / "youtube"
YT_DIR.mkdir(exist_ok=True)
CLIENT_SECRET = YT_DIR / "client_secret.json"
TOKEN_FILE = YT_DIR / "token.json"

# `youtube.upload` only allows videos().insert — playlist create/list/add need the
# broader `youtube` scope. Use full access so we can also manage the playlist.
SCOPE = ["https://www.googleapis.com/auth/youtube"]

# Cover image + per-tape metadata.
# Use the 16:9 crop of the opium-era illustration (from the splash image).
COVER = PROJ / "slides" / "assets" / "splash.jpg"
TAPES = [
    {"id": 1, "title": "It's Academic — Part 1: What is colonisation?",
     "desc": "Jack Smith and Ebony Mills on the It's Academic history podcast. Part 1: what colonisation actually is."},
    {"id": 2, "title": "It's Academic — Part 2: The opium trade as a tool of empire",
     "desc": "Part 2: how Britain used the opium trade as a tool of empire."},
    {"id": 3, "title": "It's Academic — Part 3: The effects of the opium trade on China",
     "desc": "Part 3: the effects of the opium trade on Chinese society."},
    {"id": 4, "title": "It's Academic — Part 4: Britain, Siam, and Thailand",
     "desc": "Part 4: how the British pushed at Siam and why Thailand stayed free."},
]


def build_mp4(tape_id: int, cover: Path, audio: Path, out: Path) -> Path:
    """Loop the cover image over the audio into an mp4 (16:9)."""
    # Scale/crop cover to 1920x1080 (16:9), loop 1 frame, mux audio.
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(cover),
        "-i", str(audio),
        "-c:v", "libx264", "-tune", "stillimage", "-crf", "23",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest", "-pix_fmt", "yuv420p",
        "-vf", "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080",
        str(out),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return out


def get_authenticated_service(scope: list[str]):
    """OAuth2 installed-app flow -> googleapiclient service. Saves token.json."""
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), scope)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET), scope)
            creds = flow.run_local_server(port=0, open_browser=True)
        TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")

    return build("youtube", "v3", credentials=creds)


def upload_video(service, tape_id: int, mp4: Path) -> str:
    """Upload one mp4; return the video ID."""
    from googleapiclient.http import MediaFileUpload

    meta = {t["id"]: t for t in TAPES}[tape_id]
    body = {
        "snippet": {"title": meta["title"], "description": meta["desc"],
                    "categoryId": "27",  # Education
                    "tags": ["It's Academic", "history", "podcast", "B2"],
                    "defaultLanguage": "en"},
        "status": {"privacyStatus": "unlisted", "selfDeclaredMadeForKids": False},
    }
    media = MediaFileUpload(str(mp4), mimetype="video/mp4",
                            chunksize=1024 * 1024 * 8, resumable=True)
    request = service.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"    {status.progress() * 100:.0f}%", flush=True)
    video_id = response["id"]
    print(f"    Uploaded {mp4.name} -> https://youtu.be/{video_id}")
    return video_id


def get_or_create_playlist(service, name: str = "elwrush_class_tapes") -> str:
    """Find the playlist by name, or create it. Returns the playlist ID."""
    # Search existing (up to 50) playlists for a title match.
    resp = service.playlists().list(part="snippet", mine=True, maxResults=50).execute()
    for pl in resp.get("items", []):
        if pl["snippet"]["title"] == name:
            return pl["id"]
    # Not found — create it.
    body = {
        "snippet": {"title": name, "description": "Classroom listening tapes (It's Academic)",
                    "defaultLanguage": "en"},
        "status": {"privacyStatus": "unlisted"},
    }
    created = service.playlists().insert(part="snippet,status", body=body).execute()
    return created["id"]


def add_to_playlist(service, playlist_id: str, video_id: str) -> None:
    """Add a video to the playlist."""
    body = {
        "snippet": {"playlistId": playlist_id, "resourceId": {"kind": "youtube#video", "videoId": video_id}},
    }
    service.playlistItems().insert(part="snippet", body=body).execute()
    print(f"    Added {video_id} to playlist.")


def wait_for_processing(service, video_id: str, timeout=180) -> None:
    """Poll until the video is processed (captions can then appear)."""
    start = time.time()
    while time.time() - start < timeout:
        resp = service.videos().list(part="status,processingDetails", id=video_id).execute()
        items = resp.get("items", [])
        if items:
            proc = items[0].get("processingDetails", {})
            status = items[0].get("status", {}).get("uploadStatus", "")
            if status == "processed":
                print(f"    {video_id} processed.")
                return
        time.sleep(10)
    print(f"    {video_id}: still processing after {timeout}s (captions may take longer).")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tape", type=int, choices=[t["id"] for t in TAPES])
    parser.add_argument("--client-secret", default=str(CLIENT_SECRET))
    args = parser.parse_args()

    if args.client_secret and not Path(args.client_secret).exists():
        print(f"ERROR: client_secret.json not found at {args.client_secret}", file=sys.stderr)
        print("Place the OAuth2 Desktop-app JSON there once, or pass --client-secret PATH.", file=sys.stderr)
        sys.exit(1)

    if not COVER.exists():
        print(f"ERROR: cover image not found: {COVER}", file=sys.stderr)
        sys.exit(1)

    service = get_authenticated_service(SCOPE)

    # Ensure the target playlist exists (elwrush_class_tapes).
    playlist_id = get_or_create_playlist(service, "elwrush_class_tapes")
    print(f"  Playlist: elwrush_class_tapes ({playlist_id})", flush=True)

    tapes = [t for t in TAPES if args.tape is None or t["id"] == args.tape]
    ids = {}
    for t in tapes:
        tape_id = t["id"]
        audio = ASSETS / f"tape{tape_id}.mp3"
        if not audio.exists():
            print(f"  SKIP tape{tape_id}: audio missing", file=sys.stderr)
            continue
        mp4 = YT_DIR / f"tape{tape_id}.mp4"
        if not mp4.exists():
            print(f"  tape{tape_id}: building mp4...", flush=True)
            build_mp4(tape_id, COVER, audio, mp4)
        print(f"  tape{tape_id}: uploading...", flush=True)
        vid = upload_video(service, tape_id, mp4)
        ids[tape_id] = vid
        add_to_playlist(service, playlist_id, vid)
        print(f"  tape{tape_id}: waiting for processing...", flush=True)
        wait_for_processing(service, vid)

    out = YT_DIR / "video_ids.json"
    out.write_text(json.dumps(ids, indent=2), encoding="utf-8")
    print(f"\nVideo IDs -> {out}")
    print(json.dumps(ids, indent=2))


if __name__ == "__main__":
    main()
