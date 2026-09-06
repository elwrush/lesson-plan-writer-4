#!/usr/bin/env python3
"""Generate Part C and Part D demo tapes.

Voices (from the private clone library, GET /model?self=true):
  - Intros "Number N."  : Helen_Mirren_v2 (141726a5cc6b426b9eb8be8938d732cf)
  - Demo words (teens)  : teen-girl-conversational (f3aecb70f48a4cccbc5436f920f1cfb2)
                          american_m_teen (c756d1e5dc86432bbfd60f11691d240e)

Pronunciation per the audited answer key:
  PART C (Plural or Not?) — the teen reads:
    1 things ✓ (plural)   2 sibling ✗ (singular)   3 games ✓   4 students ✓
    5 picture ✗ (singular) 6 dinners ✓              7 book ✗ (singular)
    8 plants ✓
  PART D (The Plural Pattern) — syllable clapping: books=1, dogs=1, glasses=2
    (/ɪz/ adds a syllable), friends=1. All plural endings clearly released.

Tape layout:  [Helen] "Number one."  → [teen] word  → short tail; after a demo
word a longer pause so students have time to write.
"""
import os
import subprocess
import sys
from pathlib import Path

import requests

HELEN = "141726a5cc6b426b9eb8be8938d732cf"
TEEN_F = "f3aecb70f48a4cccbc5436f920f1cfb2"
TEEN_M = "c756d1e5dc86432bbfd60f11691d240e"

HERE = Path(__file__).parent
SEG = HERE / "segments"
SEG.mkdir(exist_ok=True)
NUM_WORDS = ["one", "two", "three", "four", "five", "six", "seven", "eight"]

# (number_word, spoken_word, teen_voice)  — spoken word matches the audited key:
# singulars for the ✗ items (2, 5, 7), plurals for the ✓ items.
PART_C = [
    ("one", "things", TEEN_F), ("two", "sibling", TEEN_M),
    ("three", "games", TEEN_F), ("four", "students", TEEN_M),
    ("five", "picture", TEEN_F), ("six", "dinners", TEEN_M),
    ("seven", "book", TEEN_F), ("eight", "plants", TEEN_M),
]
PART_D = [
    ("one", "books", TEEN_F), ("two", "dogs", TEEN_M),
    ("three", "glasses", TEEN_F), ("four", "friends", TEEN_M),
]


def tts(text: str, voice_id: str, out: Path) -> None:
    key = os.environ.get("FISH_API_KEY")
    if not key:
        print("FISH_API_KEY not set (run via zsh -ic)", file=sys.stderr)
        sys.exit(1)
    r = requests.post(
        "https://api.fish.audio/v1/tts",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                 "model": "s2.1-pro-free"},
        json={"text": text, "reference_id": voice_id, "format": "mp3",
              "mp3_bitrate": 128, "latency": "normal"},
        timeout=90, stream=True,
    )
    if r.status_code != 200:
        print(f"TTS error {r.status_code}: {r.text[:200]}", file=sys.stderr)
        sys.exit(1)
    with open(out, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"  [tts] {out.name}  [{text!r}]")


def ensure_clips():
    # Helen "Number N." intros
    for n in NUM_WORDS:
        p = SEG / f"helen-num-{n}.mp3"
        if not p.exists():
            tts(f"Number {n}.", HELEN, p)
    # teen demo words (unique by spoken word) — voice per first occurrence
    needed: list[tuple[str, str]] = list(dict.fromkeys(
        [(w, v) for _, w, v in PART_C] + [(w, v) for _, w, v in PART_D]
    ))
    for word, voice in needed:
        p = SEG / f"teen-{word}.mp3"
        if not p.exists():
            tts(word, voice, p)
    # clean stale clips no longer referenced
    used = {w for _, w, _ in PART_C} | {w for _, w, _ in PART_D}
    for old in SEG.glob("teen-*.mp3"):
        if old.stem.split("-", 1)[1] not in used:
            old.unlink(missing_ok=True)


def stitch(items, out: Path):
    # (clip_path, tail_pad_seconds) — short tail after the intro, longer pause
    # after the demo word so students have time to write their ✓/✗.
    clips = []
    for num, word, _ in items:
        clips.append((SEG / f"helen-num-{num}.mp3", 0.25))
        clips.append((SEG / f"teen-{word}.mp3", 0.75))

    inputs = []
    for c, _ in clips:
        inputs += ["-i", str(c)]

    L = "loudnorm=I=-16:TP=-1.5:LRA=11,aformat=sample_rates=44100:channel_layouts=mono"
    filters = [f"[{i}:a]{L},apad=pad_dur={pad}[p{i}]" for i, (_, pad) in enumerate(clips)]

    filters.append("".join(f"[p{i}]" for i in range(len(clips))) +
                   f"concat=n={len(clips)}:v=0:a=1[out]")

    cmd = ["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(filters),
           "-map", "[out]", "-c:a", "libmp3lame", "-b:a", "128k", str(out)]
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    print(f"Wrote: {out}")


def main():
    print("Generating Part C/D clips...")
    ensure_clips()
    stitch(PART_C, HERE / "Part C - Plural or Not.mp3")
    stitch(PART_D, HERE / "Part D - The Plural Pattern.mp3")


if __name__ == "__main__":
    main()
