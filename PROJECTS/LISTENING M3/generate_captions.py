#!/usr/bin/env python3
"""generate_captions.py — Build WebVTT captions for the It's Academic podcast tapes.

Uses Fish Audio ASR (/v1/asr) to transcribe each tape with word-level timestamps,
then groups words into sentence-level WebVTT cues for the native <video> <track>
caption toggle. Transcribes the DEPLOYED audio (non-destructive — no re-generation).

Outputs to slides/assets/:
    tape1.vtt, tape2.vtt, tape3.vtt, tape4.vtt

Usage:  zsh -ic 'python3 generate_captions.py'
"""

import json
import os
import re
import sys
from pathlib import Path

import requests

PROJ = Path(__file__).resolve().parent
ASSETS = PROJ / "slides" / "assets"

TAPE_IDS = ["tape1", "tape2", "tape3", "tape4"]

# Group words into cues of roughly this many seconds (WebVTT cue length).
TARGET_CUE_SECONDS = 4.0
MIN_CUE_SECONDS = 2.0
MAX_CUE_SECONDS = 7.0
# Words that end a cue (sentence/clause boundaries): ., ? ! , ; : — -
SENTENCE_END = (".", "?", "!", ",", ";", ":", "\u2014", "-")


def api_key() -> str:
    key = os.environ.get("FISH_API_KEY")
    if not key:
        print("FISH_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    return key


def transcribe(path: Path) -> list[dict]:
    """Transcribe an audio file via Fish ASR; return [{start,end,text}, ...]."""
    audio = path.read_bytes()
    r = requests.post(
        "https://api.fish.audio/v1/asr",
        headers={"Authorization": f"Bearer {api_key()}"},
        files={"audio": (path.name, audio, "audio/mpeg")},
        data={"language": "en", "ignore_timestamps": "false"},
        timeout=180,
    )
    if r.status_code != 200:
        raise RuntimeError(f"ASR {r.status_code}: {r.text[:200]}")
    data = r.json()
    return [{"start": s["start"], "end": s["end"], "text": s["text"].strip()}
            for s in data.get("segments", [])]


def format_timestamp(sec: float) -> str:
    """Format seconds -> WebVTT timestamp HH:MM:SS.mmm."""
    ms = int(round(sec * 1000))
    h, rem = divmod(ms, 3600_000)
    m, rem = divmod(rem, 60_000)
    s, msec = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d}.{msec:03d}"


def group_cues(words: list[dict]) -> list[dict]:
    """Group word segments into sentence/clause-level WebVTT cues."""
    cues = []
    i = 0
    while i < len(words):
        start = words[i]["start"]
        parts = [words[i]["text"]]
        end = words[i]["end"]
        j = i + 1
        # Extend until a sentence-end word or target/max length reached
        while j < len(words):
            dur_so_far = words[j]["end"] - start
            cur_text = words[j]["text"]
            # Stop after a sentence/clause boundary if we've hit a minimum
            if (dur_so_far >= MIN_CUE_SECONDS and
                    cur_text.rstrip().endswith(SENTENCE_END)):
                parts.append(cur_text)
                end = words[j]["end"]
                j += 1
                break
            if dur_so_far >= MAX_CUE_SECONDS:
                parts.append(cur_text)
                end = words[j]["end"]
                j += 1
                break
            parts.append(cur_text)
            end = words[j]["end"]
            j += 1
            if dur_so_far >= TARGET_CUE_SECONDS:
                break
        cues.append({"start": start, "end": end, "text": " ".join(parts)})
        i = j
    return cues


def build_vtt(cues: list[dict]) -> str:
    lines = ["WEBVTT", ""]
    for c in cues:
        lines.append(f"{format_timestamp(c['start'])} --> {format_timestamp(c['end'])}")
        lines.append(c["text"])
        lines.append("")
    return "\n".join(lines)


def main():
    for tape_id in TAPE_IDS:
        audio_path = ASSETS / f"{tape_id}.mp3"
        if not audio_path.exists():
            print(f"  SKIP {tape_id}: audio not found", file=sys.stderr)
            continue
        print(f"  {tape_id}: transcribing...", end=" ", flush=True)
        words = transcribe(audio_path)
        cues = group_cues(words)
        vtt = build_vtt(cues)
        out = ASSETS / f"{tape_id}.vtt"
        out.write_text(vtt, encoding="utf-8")
        print(f"{len(cues)} cues -> {out.name}")


if __name__ == "__main__":
    main()
