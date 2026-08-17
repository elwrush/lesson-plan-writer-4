"""
pixabay_download.py - Search Pixabay, download and compress media files.

Usage:
    python scripts/pixabay_download.py --query "Berlin wall" --type image --count 3

Outputs JSON on stdout with file paths and attribution strings.
"""

import argparse
import io
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import requests
from PIL import Image

PROJECT_ROOT = Path(__file__).parent.parent
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "assets"


def get_api_key():
    api_key = os.environ.get("PIXABAY_API_KEY")
    if not api_key:
        print("Error: PIXABAY_API_KEY environment variable not set.", file=sys.stderr)
    return api_key


def search_images(api_key, query, per_page=5):
    per_page = max(per_page, 3)
    url = "https://pixabay.com/api/"
    params = {
        "key": api_key,
        "q": query,
        "image_type": "photo",
        "orientation": "horizontal",
        "safesearch": "true",
        "per_page": per_page,
    }
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        return data.get("hits", [])
    except requests.RequestException as e:
        print(f"Error searching Pixabay images: {e}", file=sys.stderr)
        return []


def search_videos(api_key, query, per_page=5):
    per_page = max(per_page, 3)
    url = "https://pixabay.com/api/videos/"
    params = {
        "key": api_key,
        "q": query,
        "safesearch": "true",
        "per_page": per_page,
    }
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        return data.get("hits", [])
    except requests.RequestException as e:
        print(f"Error searching Pixabay videos: {e}", file=sys.stderr)
        return []


def compress_image(image_url, output_path, pixabay_id, index):
    try:
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        img = Image.open(io.BytesIO(response.content))
        img = img.convert("RGB")

        max_width = 1920
        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.LANCZOS)

        img.save(output_path, "JPEG", quality=80, optimize=True)
        return True
    except Exception as e:
        print(f"Warning: Image compression failed for {pixabay_id}: {e}", file=sys.stderr)
        return False


def compress_video(video_url, output_path):
    try:
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            temp_path = tmp.name

        video_response = requests.get(video_url, timeout=60)
        video_response.raise_for_status()
        with open(temp_path, "wb") as f:
            f.write(video_response.content)

        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            temp_path,
            "-vf",
            "scale=min(1280,iw):min(720,ih):force_original_aspect_ratio=decrease",
            "-c:v",
            "libx264",
            "-crf",
            "28",
            "-preset",
            "fast",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            str(output_path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        os.unlink(temp_path)

        if result.returncode != 0:
            print(f"Warning: ffmpeg failed: {result.stderr}", file=sys.stderr)
            return False
        return True
    except subprocess.TimeoutExpired:
        print("Warning: ffmpeg timed out", file=sys.stderr)
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        return False
    except Exception as e:
        print(f"Warning: Video compression failed: {e}", file=sys.stderr)
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        return False


def get_best_image_url(hit):
    for key in ("largeImageURL", "webformatURL", "previewURL"):
        url = hit.get(key)
        if url:
            return url
    return None


def get_best_video_url(hit):
    videos = hit.get("videos", {})
    for quality in ("large", "medium", "small", "tiny"):
        entry = videos.get(quality)
        if entry and isinstance(entry, dict):
            url = entry.get("url")
            if url:
                return url
    return None


def main():
    parser = argparse.ArgumentParser(description="Search Pixabay, download and compress media.")
    parser.add_argument("--query", required=True, help="Search term")
    parser.add_argument(
        "--type", choices=["image", "video"], default="image", help="Media type (default: image)"
    )
    parser.add_argument(
        "--count", type=int, default=1, help="Number of files to download (default: 1, max: 10)"
    )
    parser.add_argument(
        "--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Output directory (default: assets/)"
    )
    args = parser.parse_args()

    api_key = get_api_key()
    if not api_key:
        print(json.dumps({"files": [], "errors": ["No API key"]}))
        sys.exit(1)

    count = min(max(args.count, 1), 10)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.type == "image":
        hits = search_images(api_key, args.query, per_page=count)
    else:
        hits = search_videos(api_key, args.query, per_page=count)

    if not hits:
        print(json.dumps({"files": [], "errors": [f"No results for '{args.query}'"]}))
        return

    results = []
    errors = []

    for index, hit in enumerate(hits[:count]):
        pixabay_id = hit.get("id", index)
        photographer = hit.get("user", "Unknown")

        if args.type == "image":
            file_url = get_best_image_url(hit)
            ext = ".jpg"
        else:
            file_url = get_best_video_url(hit)
            ext = ".mp4"

        if not file_url:
            errors.append(f"No URL for hit {pixabay_id}")
            continue

        filename = f"pixabay_{pixabay_id}_{index + 1}{ext}"
        output_path = output_dir / filename

        if args.type == "image":
            success = compress_image(file_url, output_path, pixabay_id, index)
        else:
            success = compress_video(file_url, output_path)

        if success:
            size_kb = output_path.stat().st_size / 1024
            print(f"Downloaded: {output_path} ({size_kb:.0f}KB)", file=sys.stderr)
            results.append(
                {
                    "path": str(output_path),
                    "attribution": f"{'Photo' if args.type == 'image' else 'Video'} by {photographer} on Pixabay",
                    "size_kb": round(size_kb, 1),
                }
            )
        else:
            errors.append(f"Failed to process {pixabay_id}")

    output = {"files": results, "errors": errors}
    print(json.dumps(output))


if __name__ == "__main__":
    main()
