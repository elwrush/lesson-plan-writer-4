#!/usr/bin/env python3
"""
generate_interview_audio.py — Nepal flood interview, B1, via Fish multi-speaker.

One Fish Audio TTS call per PART, using the native S2 multi-speaker dialog API:
    text  : "<|speaker:0|>Lucy line<|speaker:1|>Emma line"
    reference_id : [LUCY_ID, EMMA_ID]   (speaker:N indexes this array)

Outputs ONE single-play MP3 per part (NO "listen again", NO doubling):
  output/section{N}.mp3      - the master listen
  slides/assets/tape{N}.mp3  - the copy consumed by the deck + upload script

Neither the tape nor the deck plays Part N twice — the teacher controls any
second listen manually.

Usage:
    python generate_interview_audio.py
"""

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import requests

# Pull the canonical markdown + pronunciation guard pipeline from the fish-audio skill.
SKILL_SCRIPTS = Path.home() / ".agents" / "skills" / "fish-audio" / "scripts"
sys.path.insert(0, str(SKILL_SCRIPTS))
from md_safety import strip_markdown, assert_no_markdown  # noqa: E402
from pronounce import apply_pronunciations                # noqa: E402

# ---------------------------------------------------------------------------
PROJ = Path(__file__).resolve().parent.parent
TRANSCRIPT_JSON = PROJ / "transcript.json"
OUT_DIR = Path(__file__).resolve().parent
DECK_ASSETS = PROJ / "slides" / "assets"

API_KEY = os.environ.get("FISH_API_KEY")
if not API_KEY:
    print("FISH_API_KEY not set", file=sys.stderr)
    sys.exit(1)

# Voice clones (verified to exist as private models)
LUCY_ID = "141726a5cc6b426b9eb8be8938d732cf"    # Helen_Mirren_v2  -> speaker 0
EMMA_ID = "3348026252654c05a790528e411b117a"    # Emma_Watson      -> speaker 1

# Part boundaries = turn index ranges into transcript.json (same as generate_transcript.py)
PART_BOUNDARIES = [0, 8, 16, 22, 32]   # Part 1:0-7, 2:8-15, 3:16-21, 4:22-31

# Fish misreads numerals; spell them out in the SPEECH text only (transcript.json
# keeps the real form, which is what students see printed).
NUMERAL_FIXES = [
    ("on 26 August", "on the twenty-sixth of August"),
    ("In 2011,", "In twenty eleven,"),
    ("by 2030.", "by twenty thirty."),
]


def clean_line(text: str) -> str:
    text = text.strip()
    text = text.replace("...", "\u2014").replace("..", "\u2014")
    return text


def speech_text(text: str) -> str:
    """Apply markdown/pronunciation guard + numeral fixes for TTS."""
    for old, new in NUMERAL_FIXES:
        text = text.replace(old, new)
    text = strip_markdown(text)
    text = apply_pronunciations(text)
    assert_no_markdown(text, context="interview")
    return text


def build_dialog(turns: list[dict]) -> str:
    """Convert a list of {speaker, text} turns into one multi-speaker dialog string."""
    parts = []
    for turn in turns:
        if turn["speaker"].startswith("Lucy"):
            idx = 0
        else:
            idx = 1
        line = clean_line(turn["text"])
        parts.append(f"<|speaker:{idx}|>{line}")
    return " ".join(parts)


def tts_dialog(text: str, out_path: Path, retries: int = 3) -> bool:
    """One multi-speaker Fish TTS call (S2 family). Returns True on success."""
    payload = json.dumps({
        "text": text,
        "reference_id": [LUCY_ID, EMMA_ID],
        "temperature": 0.8,
        "prosody": {"speed": 0.95, "volume": 0, "normalize_loudness": True},
        "chunk_length": 300,
        "normalize": True,
        "format": "mp3",
        "mp3_bitrate": 128,
        "latency": "normal",
        "condition_on_previous_chunks": True,
    })
    out_path.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(1, retries + 1):
        try:
            r = requests.post(
                "https://api.fish.audio/v1/tts",
                headers={"Authorization": f"Bearer {API_KEY}",
                         "Content-Type": "application/json",
                         "model": "s2.1-pro-free"},
                data=payload, timeout=180, stream=True,
            )
            if r.status_code == 200:
                with open(out_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                return True
            print(f"  attempt {attempt}: HTTP {r.status_code} {r.text[:150]}", file=sys.stderr)
        except requests.RequestException as e:
            print(f"  attempt {attempt}: {e}", file=sys.stderr)
        time.sleep(2.5)
    return False


def loudnorm(in_path: Path, out_path: Path) -> Path:
    """Loudness-normalise a section so all 4 parts match (I=-16, TP=-1.5, LRA=11).

    Output is a standard mono 128k mp3 (44.1k or 48k — both fine for YouTube's
    ASR caption engine). Uniform loudness + a < -1.5 dBTP ceiling is what the
    scrubber needs to transcribe cleanly.
    """
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(in_path),
         "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
         "-ac", "1", "-c:a", "libmp3lame", "-b:a", "128k",
         str(out_path)],
        check=True, capture_output=True)
    return out_path


def verify_scrubber_ready(path: Path) -> None:
    """HARD GATE: assert the final mp3 is a clean mono file under ~-1.5 dBTP.

    YouTube's ASR caption engine ("scrubber") transcribes best from a uniform,
    unclipped mp3. If a section is clipping or encoded oddly, fail loudly here
    rather than let a bad file reach upload and produce garbled captions.
    """
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "stream=codec_name,sample_rate,channels",
         "-of", "default=noprint_wrappers=1", str(path)],
        capture_output=True, text=True).stdout
    codec = re.search(r"codec_name=(\S+)", probe)
    rate = re.search(r"sample_rate=(\d+)", probe)
    ch = re.search(r"channels=(\d+)", probe)
    if not (codec and codec.group(1) == "mp3"):
        raise SystemExit(f"RED-GATE: {path.name} not an mp3:\n{probe}")
    if not (rate and int(rate.group(1)) in (44100, 48000)):
        raise SystemExit(f"RED-GATE: {path.name} sample rate {rate.group(1) if rate else '?'} "
                         f"not ASR-friendly (want 44100 or 48000):\n{probe}")
    if not (ch and int(ch.group(1)) == 1):
        raise SystemExit(f"RED-GATE: {path.name} not mono:\n{probe}")

    vol = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(path), "-af", "volumedetect",
         "-f", "null", "-"],
        capture_output=True, text=True).stderr
    max_v = re.search(r"max_volume:\s*(-?[\d.]+) dB", vol)
    if not max_v:
        raise SystemExit(f"RED-GATE: could not read max_volume for {path.name}")
    if float(max_v.group(1)) > -1.5:   # louder than the TP target => clipping risk
        raise SystemExit(f"RED-GATE: {path.name} peaks at {max_v.group(1)} dB "
                         f"(above -1.5) — clipped, caption quality at risk")


def duration(path: Path) -> float:
    p = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True)
    try:
        return float(p.stdout.strip())
    except ValueError:
        return 0.0


def main():
    data = json.loads(TRANSCRIPT_JSON.read_text(encoding="utf-8"))
    turns = data["transcript"]

    sections = [(turns[PART_BOUNDARIES[i]:PART_BOUNDARIES[i + 1]])
                for i in range(len(PART_BOUNDARIES) - 1)]

    for i, chunk_turns in enumerate(sections, start=1):
        print(f"=== Part {i} ({len(chunk_turns)} turns) ===")
        text = build_dialog(chunk_turns)
        text = speech_text(text)
        raw = OUT_DIR / f"section{i}_raw.mp3"
        print(f"  TTS multi-speaker call ({len(text.split())} words)...")
        if not tts_dialog(text, raw):
            print(f"  !! FAILED Part {i}", file=sys.stderr)
            sys.exit(1)

        # loudnorm + final section file
        section = OUT_DIR / f"section{i}.mp3"
        loudnorm(raw, section)
        raw.unlink(missing_ok=True)
        verify_scrubber_ready(section)
        print(f"  -> section{i}.mp3 ({duration(section):.1f}s, single-play, scrubber-ready)")

        # copy into deck assets (where the upload script reads it)
        deck = DECK_ASSETS / f"tape{i}.mp3"
        deck.write_bytes(section.read_bytes())
        print(f"  -> slides/assets/tape{i}.mp3 ({duration(deck):.1f}s)")

    print("\n=== DONE ===")
    print("Each part is a SINGLE play. No 'listen again', no doubling.")
    print("Teacher controls the second listen manually.")


if __name__ == "__main__":
    main()
