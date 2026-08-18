"""Generate Part B minimal-pair audio with Benedict's cloned voice.

Each word is synthesized as an individual clip, edge-trimmed, then assembled
into the Part B track (pattern: night✗ fight✓ last✗ wanted✗ played✓) with
0.3s silence between repetitions. Also emits the 'wanted, want' alternative
item so both Thai-error variants can be auditioned.
"""

import os
import re
import subprocess
import sys
from pathlib import Path

import requests

VOICE_ID = "2d3546b7f9424d28ba8d23d90a7bea24"
HELEN_VOICE_ID = "6da4ca158cac4f0e8023a26881b4919d"
CLIPS = Path("PROJECTS/PRONUNCIATION NOTICING/slides/assets/partb-clips")
OUT = Path("PROJECTS/PRONUNCIATION NOTICING/slides/assets")
API_KEY = os.environ.get("FISH_API_KEY")
if not API_KEY:
    print("FISH_API_KEY not set", file=sys.stderr)
    sys.exit(1)

WORDS = {
    "night": "night", "nigh": "nigh",
    "fight": "fight", "fie": "fie",
    "last": "last", "lahs": "lahs",
    "wanted": "wanted", "wonty": "wonty", "want": "want",
    "played": "played", "play": "play",
}

NUMBERS = {1: "Number one", 2: "Number two", 3: "Number three",
           4: "Number four", 5: "Number five"}

# Order for the Part B track: (correct, dropped_or_correct) per item
TRACK = [
    ("night", "nigh"),    # 1 ✗
    ("fight", "fight"),   # 2 ✓
    ("last", "lahs"),     # 3 ✗
    ("wanted", "wonty"),  # 4 ✗
    ("played", "played"), # 5 ✓
]
PAD_S = 0.3


def tts(text: str, out: Path, voice_id: str = VOICE_ID) -> None:
    r = requests.post(
        "https://api.fish.audio/v1/tts",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            "model": "s2.1-pro-free",
        },
        json={"text": text, "reference_id": voice_id,
              "format": "mp3", "mp3_bitrate": 128, "latency": "normal"},
        timeout=60, stream=True,
    )
    if r.status_code != 200:
        print(f"TTS error {r.status_code}: {r.text[:200]}", file=sys.stderr)
        sys.exit(1)
    with open(out, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)


def probe_duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    return float(out)


def silence_boundaries(path: Path, noise_db: str = "-40dB", d: str = "0.08"):
    """Return (start_cut, end_cut) in seconds — first/last non-silence edges."""
    r = subprocess.run(
        ["ffmpeg", "-i", str(path), "-af",
         f"silencedetect=noise={noise_db}:d={d}", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    starts = [float(m) for m in re.findall(r"silence_start: ([\d.]+)", r.stderr)]
    ends = [float(m) for m in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
    dur = probe_duration(path)
    if starts and starts[0] < 0.05 and ends:
        start_cut = max(0.0, ends[0] - 0.03)
    else:
        start_cut = 0.0
    if ends and abs(ends[-1] - dur) < 0.05 and starts:
        end_cut = min(dur, starts[-1] + 0.03)
    else:
        end_cut = dur
    return start_cut, end_cut


def trim_to_wav(raw: Path, wav: Path) -> None:
    start, end = silence_boundaries(raw)
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(raw), "-ss", str(start), "-to", str(end),
         "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", str(wav)],
        capture_output=True, text=True, check=True,
    )


def assemble(items: list[tuple[str, str]], out: Path, with_numbers: bool = False) -> None:
    """Concatenate per-item clips (optional number + correct + dropped) with pads."""
    clips = []
    for idx, (correct, second) in enumerate(items, start=1):
        if with_numbers:
            clips.append(f"num{idx}")
        clips.append(correct)
        clips.append(second)

    inputs = []
    for name in clips:
        inputs += ["-i", str(CLIPS / f"{name}.wav")]
    inputs += ["-f", "lavfi", "-t", str(PAD_S), "-i", "anullsrc=r=44100:cl=stereo"]
    pad_label = len(clips)

    filters = [f"[{i}:a]apad=pad_dur={PAD_S}[p{i}]" for i in range(len(clips))]
    concat_srcs = []
    for i in range(len(clips)):
        concat_srcs.append(f"[p{i}]")
        if i < len(clips) - 1:
            concat_srcs.append(f"[{pad_label}:a]")
    filters.append("".join(concat_srcs) + f"concat=n={len(concat_srcs)}:v=0:a=1[out]")
    subprocess.run(
        ["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(filters),
         "-map", "[out]", "-c:a", "libmp3lame", "-b:a", "128k", str(out)],
        capture_output=True, text=True, check=True,
    )


def main() -> None:
    CLIPS.mkdir(parents=True, exist_ok=True)
    for word, text in WORDS.items():
        raw = CLIPS / f"{word}-raw.mp3"
        wav = CLIPS / f"{word}.wav"
        if not raw.exists():
            print(f"TTS: {text!r}")
            tts(text, raw)
        trim_to_wav(raw, wav)
        print(f"  {word:8s} {probe_duration(wav):.2f}s")

    for num, text in NUMBERS.items():
        raw = CLIPS / f"num{num}-raw.mp3"
        wav = CLIPS / f"num{num}.wav"
        if not raw.exists():
            print(f"TTS (Helen): {text!r}")
            tts(text, raw, voice_id=HELEN_VOICE_ID)
        trim_to_wav(raw, wav)
        print(f"  num{num:2d}   {probe_duration(wav):.2f}s")

    assemble(TRACK, OUT / "partb-audio.mp3", with_numbers=True)
    print(f"Track: {OUT / 'partb-audio.mp3'}")
    assemble([("wanted", "want")], OUT / "partb-item4-alt.mp3")
    print(f"Alt item 4 (want): {OUT / 'partb-item4-alt.mp3'}")


if __name__ == "__main__":
    main()
