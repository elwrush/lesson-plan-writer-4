#!/usr/bin/env python3
"""Stitch the Part A comparison track with ffmpeg.

Sequence:  [Helen] "Thai English."  →  FERN THAI.m4a (real Thai student)  →
           [Helen] "Standard English."  →  [Benedict] model sentence.

Loudness:   every segment is normalised to I=-16 LUFS so the Thai-style student
            recording, the narrator, and the model reading sit at the same level.
Pauses:     0.4 s of silence between segments (natural compare-track pacing).
No fades:   never apply afade (cuts final phonemes); silence pads only.
"""
import subprocess
from pathlib import Path

HERE = Path(__file__).parent
SEG = HERE / "segments"
FERN = HERE.parent / "FERN THAI.m4a"
OUT = HERE / "Part A - Thai vs Standard English.mp3"
PAD_S = 0.4

# order matters: (label, path)
CLIPS = [
    ("narr-thai-english", SEG / "narr-thai-english.mp3"),
    ("fern", FERN),
    ("narr-standard-english", SEG / "narr-standard-english.mp3"),
    ("benedict-model", SEG / "benedict-model.mp3"),
]


def main():
    for label, path in CLIPS:
        if not path.exists():
            print(f"missing input: {path}", flush=True)
            raise SystemExit(1)

    inputs = []
    for _, path in CLIPS:
        inputs += ["-i", str(path)]
    # extra silent source used as the inter-segment pad
    inputs += ["-f", "lavfi", "-t", str(PAD_S), "-i", "anullsrc=r=44100:cl=stereo"]
    pad_label = len(CLIPS)

    L = "loudnorm=I=-16:TP=-1.5:LRA=11,aformat=sample_rates=44100:channel_layouts=mono"
    filters = [f"[{i}:a]{L},apad=pad_dur={PAD_S}[p{i}]" for i in range(len(CLIPS))]

    concat_srcs = []
    for i in range(len(CLIPS)):
        concat_srcs.append(f"[p{i}]")
        if i < len(CLIPS) - 1:
            concat_srcs.append(f"[{pad_label}:a]")
    filters.append(
        "".join(concat_srcs) + f"concat=n={len(concat_srcs)}:v=0:a=1[out]"
    )

    cmd = ["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(filters),
           "-map", "[out]", "-c:a", "libmp3lame", "-b:a", "128k", str(OUT)]
    print(" ".join(cmd))
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    print(f"Wrote: {OUT}")


if __name__ == "__main__":
    main()
