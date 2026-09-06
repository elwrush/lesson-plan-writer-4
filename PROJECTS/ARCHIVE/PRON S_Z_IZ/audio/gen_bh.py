#!/usr/bin/env python3
"""Generate Part B (Same or Different) discrimination tape and Part H model reading.

Voices (private clone library): Helen_Mirren_v2 narrator, teen voices for words,
Benedict_Cumberbatch for the model reading.

PART B key (from the audited answer key → all pairs are ✗): each word is said TWICE —
the first repetition WITH the plural, the second WITHOUT (dropped). Same teen voice
for both repetitions so the only audible change is the -s ending.
  1 books/book ✗  2 dogs/dog ✗  3 glasses/glass ✗  4 friends/friend ✗  5 years/year ✗

PART H: Benedict reads the model-reading paragraph (the "the model" listening text).
"""
import os
import subprocess
import sys
from pathlib import Path

import requests

HELEN = "141726a5cc6b426b9eb8be8938d732cf"   # Helen_Mirren_v2
BENEDICT = "2d3546b7f9424d28ba8d23d90a7bea24"  # Benedict_Cumberbatch
TEEN_F = "f3aecb70f48a4cccbc5436f920f1cfb2"
TEEN_M = "c756d1e5dc86432bbfd60f11691d240e"

HERE = Path(__file__).parent
SEG = HERE / "segments"
SEG.mkdir(exist_ok=True)

# (number_word, plural, singular, voice, matches) — True = both reps match (✓), False = second rep drops (✗)
PART_B = [
    ("one", "books", "book", TEEN_F, False),
    ("two", "dogs", "dog", TEEN_M, True),
    ("three", "glasses", "glass", TEEN_F, False),
    ("four", "friends", "friend", TEEN_M, False),
    ("five", "years", "year", TEEN_F, True),
]

MODEL_READING = (
    "I love my things. I have three books on my desk, two dogs in the garden, "
    "and four glasses in the kitchen. My friends come to my house and we play board "
    "games. My siblings have their own things too. We have plants in every room and "
    "pictures on every wall. I like my house because it is full of things that make me happy."
)


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
        timeout=120, stream=True,
    )
    if r.status_code != 200:
        print(f"TTS error {r.status_code}: {r.text[:200]}", file=sys.stderr)
        sys.exit(1)
    with open(out, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"  [tts] {out.name}  [{text!r}]")


def ensure_b_clips():
    for n in ["one", "two", "three", "four", "five"]:
        p = SEG / f"helen-num-{n}.mp3"
        if not p.exists():
            tts(f"Number {n}.", HELEN, p)
    for _, plural, singular, voice, _ in PART_B:
        pp = SEG / f"teen-{plural}.mp3"
        sp = SEG / f"teen-{singular}.mp3"
        if not pp.exists():
            tts(plural, voice, pp)
        if not sp.exists():
            tts(singular, voice, sp)


def stitch_part_b():
    # clips: (path, tail_pad) — number intro short tail, word then singular, long gap
    clips = []
    for num, plural, singular, _, matches in PART_B:
        clips.append((SEG / f"helen-num-{num}.mp3", 0.2))
        clips.append((SEG / f"teen-{plural}.mp3", 0.25))
        # ✓ = both reps plural (same word); ✗ = second rep drops to singular
        second = SEG / f"teen-{plural}.mp3" if matches else SEG / f"teen-{singular}.mp3"
        clips.append((second, 0.9))
    inputs = []
    for c, _ in clips:
        inputs += ["-i", str(c)]
    L = "loudnorm=I=-16:TP=-1.5:LRA=11,aformat=sample_rates=44100:channel_layouts=mono"
    filters = [f"[{i}:a]{L},apad=pad_dur={pad}[p{i}]" for i, (_, pad) in enumerate(clips)]
    filters.append("".join(f"[p{i}]" for i in range(len(clips))) +
                   f"concat=n={len(clips)}:v=0:a=1[out]")
    out = HERE / "Part B - Same or Different.mp3"
    subprocess.run(["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(filters),
                    "-map", "[out]", "-c:a", "libmp3lame", "-b:a", "128k", str(out)],
                   check=True, capture_output=True, text=True)
    print(f"Wrote: {out}")


def gen_model_reading():
    out = SEG / "model-reading.mp3"
    if not out.exists():
        tts(f"[read clearly, slowly, with a friendly teacher voice] {MODEL_READING}", BENEDICT, out)
    print("Part H segment ready:", out.name)


if __name__ == "__main__":
    print("Generating Part B...")
    ensure_b_clips()
    stitch_part_b()
    print("Generating Part H model reading...")
    gen_model_reading()
