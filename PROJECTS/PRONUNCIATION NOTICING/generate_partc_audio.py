"""Part C audio: 8 past-tense verbs read by Russell Crowe.

Helen announces each number (1-8). Russell reads each verb once — either with
the -ed ending pronounced (correct) or with the whole ending dropped. Uses a
separate clip directory so the Part B clips are untouched.

Pattern: 1.wanted ✓  2.play ✗  3.stopped ✓  4.need ✗  5.watched ✓
         6.stayed ✓  7.start ✗  8.helped ✓
"""

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from generate_partb_audio import (  # noqa: E402
    CLIPS as PARTB_CLIPS,
    OUT,
    HELEN_VOICE_ID,
    tts,
    trim_to_wav,
    probe_duration,
    PAD_S,
)

RCROWE_VOICE_ID = "0f00fb73c0c94c6182ed994193dd7ce7"
CLIPS = OUT / "partc-clips"

# (past-tense word, dropped respelling or None for correct)
ITEMS = [
    ("wanted", None),
    ("played", "play"),
    ("stopped", None),
    ("needed", "need"),
    ("watched", None),
    ("stayed", None),
    ("started", "start"),
    ("helped", None),
]


def ensure_clip(name: str, text: str, voice_id: str) -> None:
    raw = CLIPS / f"{name}-raw.mp3"
    wav = CLIPS / f"{name}.wav"
    if not raw.exists():
        print(f"TTS: {text!r}")
        tts(text, raw, voice_id=voice_id)
    trim_to_wav(raw, wav)
    print(f"  {name:8s} {probe_duration(wav):.2f}s")


def assemble_single(clip_names: list[str], out: Path) -> None:
    inputs = []
    for name in clip_names:
        inputs += ["-i", str(CLIPS / f"{name}.wav")]
    inputs += ["-f", "lavfi", "-t", str(PAD_S), "-i", "anullsrc=r=44100:cl=stereo"]
    pad_label = len(clip_names)

    filters = [f"[{i}:a]apad=pad_dur={PAD_S}[p{i}]" for i in range(len(clip_names))]
    concat_srcs = []
    for i in range(len(clip_names)):
        concat_srcs.append(f"[p{i}]")
        if i < len(clip_names) - 1:
            concat_srcs.append(f"[{pad_label}:a]")
    filters.append("".join(concat_srcs) + f"concat=n={len(concat_srcs)}:v=0:a=1[out]")
    subprocess.run(
        ["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(filters),
         "-map", "[out]", "-c:a", "libmp3lame", "-b:a", "128k", str(out)],
        capture_output=True, text=True, check=True,
    )


def main() -> None:
    CLIPS.mkdir(parents=True, exist_ok=True)

    for word, dropped in ITEMS:
        ensure_clip(word, word, RCROWE_VOICE_ID)
        if dropped:
            ensure_clip(dropped, dropped, RCROWE_VOICE_ID)

    # Numbers: reuse Helen's 1-5 from Part B, generate 6-8
    for num in range(1, 9):
        dst = CLIPS / f"num{num}.wav"
        if num <= 5:
            src = PARTB_CLIPS / f"num{num}.wav"
            if src.exists():
                import shutil
                shutil.copy2(src, dst)
                continue
        raw = CLIPS / f"num{num}-raw.mp3"
        if not raw.exists():
            print(f"TTS (Helen): 'Number {num}'")
            tts(f"Number {num}", raw, voice_id=HELEN_VOICE_ID)
        trim_to_wav(raw, dst)
        print(f"  num{num:2d}   {probe_duration(dst):.2f}s")

    track = []
    for idx, (word, dropped) in enumerate(ITEMS, start=1):
        track.append(f"num{idx}")
        track.append(dropped or word)
    assemble_single(track, OUT / "partc-audio.mp3")
    print(f"Track: {OUT / 'partc-audio.mp3'}")


if __name__ == "__main__":
    main()
