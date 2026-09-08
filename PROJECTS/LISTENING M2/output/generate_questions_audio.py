#!/usr/bin/env python3
"""
Generate the listening comprehension question-set audio (Fish Audio TTS).
Announcer: Benedict_Cumberbatch clone. Pauses inserted via ffmpeg.

Each dictation question is read TWICE. The '//' markers in the source
become 3-second silences inserted by ffmpeg.

Usage:
    python generate_questions_audio.py
"""

import os
import re
import sys
import subprocess
import time
from pathlib import Path

import requests

# RED-GATE: Fish reads every character, so markdown artifacts would be spoken
# verbatim ("asterisk asterisk", "hash", "underscore", brackets). Block the call.
_MD_ARTIFACTS = re.compile(r"\*\*|__|#|\]\(|`|\*")


def assert_no_markdown(text: str, where: str = "text") -> None:
    if _MD_ARTIFACTS.search(text):
        raise SystemExit(
            f"RED-GATE: markdown artifact in {where}: {text!r}"
        )

# ----------------------------------------------------------------------------
# Config
# ----------------------------------------------------------------------------
VOICE_ID = "2d3546b7f9424d28ba8d23d90a7bea24"  # Benedict_Cumberbatch clone
MY_DIR = Path(__file__).resolve().parent
PIECE_DIR = MY_DIR / "pieces"
FINAL = MY_DIR / "questions-audio.mp3"

API_KEY = os.environ.get("FISH_API_KEY")
if not API_KEY:
    print("FISH_API_KEY not set", file=sys.stderr)
    sys.exit(1)

# Timing constants (seconds)
LEAD_IN = 0.6            # silence at very start
GAP_AFTER_LABEL = 0.9    # after "Chunk one." / "Question one."
GAP_BETWEEN_READINGS = 5.0   # between the two hearings of a question
GAP_AFTER_QUESTION = 7.0     # before the next question
GAP_AFTER_CHUNK_LABEL = 1.2
GAP_INTRO_TO_CHUNK = 1.5
LEAD_OUT = 0.8           # silence at very end

# ----------------------------------------------------------------------------
# Speech pieces. Each question is a COMPLETE single sentence (one TTS call).
# Structure per chunk: list of (label, sentence). The sentence is read once by
# TTS and reused for both hearings (ffmpeg doubles it).
# ----------------------------------------------------------------------------
INTRO = (
    "[calm] Listen and write down the eight questions you hear. "
    "You will hear each question twice. Write exactly what you hear."
)

CHUNKS = {
    "one": [
        ("Question one.", "Why does Emma say the flood was not normal?"),
        ("Question two.", "Why was the loud noise so surprising?"),
    ],
    "two": [
        ("Question three.", "Why did many people first think it was an earthquake?"),
        ("Question four.", "Why can't scientists warn people before a glacier breaks?"),
    ],
    "three": [
        ("Question five.", "Give two examples of damage to buildings and roads."),
        ("Question six.", "How many people were affected, and how many children lost their classrooms?"),
    ],
    "four": [
        ("Question seven.", "Why does Emma say the danger is not over?"),
        ("Question eight.", "Why is this a climate story, not only a Nepal story?"),
    ],
}


def tts(text: str, out_path: Path) -> None:
    """Generate one speech piece via Fish Audio TTS."""
    assert_no_markdown(text, where=out_path.stem)
    body = {
        "text": text,
        "reference_id": VOICE_ID,
        "format": "mp3",
        "mp3_bitrate": 128,
        "latency": "normal",
    }
    payload = json.dumps(body)
    # headers split so we can pass the JSON string explicitly
    for attempt in range(1, 5):
        try:
            r = requests.post(
                "https://api.fish.audio/v1/tts",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json",
                    "model": "s2.1-pro-free",
                },
                data=payload,
                timeout=90,
                stream=True,
            )
            if r.status_code == 200:
                out_path.parent.mkdir(parents=True, exist_ok=True)
                with open(out_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                return
            print(f"  attempt {attempt} failed: {r.status_code} {r.text[:150]}",
                  file=sys.stderr)
        except requests.RequestException as e:
            print(f"  attempt {attempt} error: {e}", file=sys.stderr)
        time.sleep(2.5)
    print(f"  !! giving up on: {text[:60]}", file=sys.stderr)
    sys.exit(1)


def make_silence(duration: float, name: str) -> Path:
    """Create a mono mp3 silence of given duration."""
    p = PIECE_DIR / name
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=mono",
        "-t", f"{duration:.2f}",
        "-b:a", "128k", str(p),
    ], capture_output=True, check=True)
    return p


def main() -> None:
    PIECE_DIR.mkdir(parents=True, exist_ok=True)
    piece_map = {}   # id -> Path

    def get_piece(sid: str, text: str) -> Path:
        if sid not in piece_map:
            tts(text, PIECE_DIR / f"{sid}.mp3")
            piece_map[sid] = PIECE_DIR / f"{sid}.mp3"
        return piece_map[sid]

    # silence files (generated once, reused)
    sil = {}
    for name, dur in [("intro", LEAD_IN), ("lab", GAP_AFTER_LABEL),
                      ("rep", GAP_BETWEEN_READINGS), ("endq", GAP_AFTER_QUESTION),
                      ("chunk", GAP_AFTER_CHUNK_LABEL),
                      ("int", GAP_INTRO_TO_CHUNK), ("out", LEAD_OUT)]:
        sil[name] = make_silence(dur, f"s_{name}.mp3")

    # Build ordered list of entries: ('file', path) referenced into concat.
    concat_entries = []
    concat_entries.append(("file", sil["intro"]))

    # Intro announcement
    intro_p = get_piece("intro", INTRO)
    concat_entries.append(("file", intro_p))
    concat_entries.append(("file", sil["int"]))

    chunk_order = ["one", "two", "three", "four"]
    for ci, cname in enumerate(chunk_order):
        # Chunk label
        chunk_p = get_piece(f"chunk_{cname}", f"Chunk {cname}.")
        concat_entries.append(("file", chunk_p))
        concat_entries.append(("file", sil["chunk"]))

        for label_text, sentence in CHUNKS[cname]:
            label_p = get_piece(f"qlab_{len(piece_map)}", label_text)
            concat_entries.append(("file", label_p))
            concat_entries.append(("file", sil["lab"]))

            # ONE complete TTS call, reused for both hearings (ffmpeg doubles it)
            sent_p = get_piece(f"q_{len(piece_map)}", sentence)
            concat_entries.append(("file", sent_p))          # hearing 1
            concat_entries.append(("file", sil["rep"]))      # 5s pause
            concat_entries.append(("file", sent_p))          # hearing 2 (same audio)
            concat_entries.append(("file", sil["endq"]))     # 7s pause

    concat_entries.append(("file", sil["out"]))

    # Write concat list (quote paths with single quotes for ffmpeg safety)
    concat_txt = MY_DIR / "concat.txt"
    with open(concat_txt, "w") as f:
        for kind, p in concat_entries:
            f.write(f"file '{p.as_posix()}'\n")

    # Assemble
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_txt),
        "-ar", "44100", "-ac", "1", "-b:a", "128k",
        str(FINAL),
    ]
    print("Assembling with ffmpeg...")
    subprocess.run(cmd, check=True)
    print(f"DONE: {FINAL}")


import json  # noqa: E402  (used by tts payload)

if __name__ == "__main__":
    main()
