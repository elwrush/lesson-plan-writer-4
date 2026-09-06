#!/usr/bin/env python3
"""Generate Part A comparison-track TTS segments for the Plural-s lesson.

Voices (resolved from the private clone library via GET /model?self=true):
  - Narrator / instructions: Helen_Mirren_v2 (141726a5cc6b426b9eb8be8938d732cf)  [live Helen Mirren]
    NOTE: the readme's Helen_Mirren v1 (6da4ca15...) is DEAD on Fish ("Reference not found").
  - Model English:           Benedict_Cumberbatch (2d3546b7f9424d28ba8d23d90a7bea24) [British RP male]

Part A tape structure (teacher-audited):
  #1 Narrator: "Thai English."
  #2 FERN THAI.m4a  (the real Thai-student recording)
  #3 Narrator: "Standard English."
  #4 Benedict: "I have three books, two dogs, and four glasses."
"""
import os
import sys
from pathlib import Path

import requests

HELEN_MIRREN_V2 = "141726a5cc6b426b9eb8be8938d732cf"
BENEDICT = "2d3546b7f9424d28ba8d23d90a7bea24"

SEG_DIR = Path(__file__).parent / "segments"
SEG_DIR.mkdir(parents=True, exist_ok=True)


def tts(text: str, voice_id: str, out_path: Path) -> None:
    api_key = os.environ.get("FISH_API_KEY")
    if not api_key:
        print("FISH_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    r = requests.post(
        "https://api.fish.audio/v1/tts",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "model": "s2.1-pro-free",
        },
        json={
            "text": text,
            "reference_id": voice_id,
            "format": "mp3",
            "mp3_bitrate": 128,
            "latency": "normal",
        },
        timeout=90,
        stream=True,
    )
    if r.status_code != 200:
        print(f"TTS error {r.status_code}: {r.text[:300]}", file=sys.stderr)
        sys.exit(1)
    with open(out_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"  [tts] {out_path.name}  [{text}]")


def main():
    print("Generating Part A TTS segments...")
    tts("Thai English.", HELEN_MIRREN_V2, SEG_DIR / "narr-thai-english.mp3")
    tts("Standard English.", HELEN_MIRREN_V2, SEG_DIR / "narr-standard-english.mp3")
    tts("I have three books, two dogs, and four glasses.",
        BENEDICT, SEG_DIR / "benedict-model.mp3")
    print("Done.")


if __name__ == "__main__":
    main()
