"""Build the joined model-sentence comparison audio.

Structure: [Helen: "Thai English"] [Thai-style recording] [Helen: "Standard
English"] [Benedict native recording], padded with 0.4s gaps and loudness-
normalized at the end (I=-16).
"""

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from generate_partb_audio import tts, trim_to_wav, probe_duration, HELEN_VOICE_ID  # noqa: E402

ASSETS = Path("PROJECTS/PRONUNCIATION NOTICING/slides/assets")
CLIPS = ASSETS / "compare-clips"
OUT = ASSETS / "model-sentence-compare.mp3"
PAD_S = 0.4


def ensure_clip(name: str, text: str, voice_id: str) -> Path:
    raw = CLIPS / f"{name}-raw.mp3"
    wav = CLIPS / f"{name}.wav"
    if not raw.exists():
        print(f"TTS (Helen): {text!r}")
        tts(text, raw, voice_id=voice_id)
    trim_to_wav(raw, wav)
    print(f"  {name:12s} {probe_duration(wav):.2f}s")
    return wav


def src_to_wav(mp3: Path, wav: Path) -> Path:
    if not wav.exists():
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(mp3), "-ar", "44100", "-ac", "2",
             "-c:a", "pcm_s16le", str(wav)],
            capture_output=True, text=True, check=True,
        )
    print(f"  {wav.stem:12s} {probe_duration(wav):.2f}s")
    return wav


def assemble(clip_names: list[str], out: Path) -> None:
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
         "-map", "[out]", "-c:a", "pcm_s16le", str(out)],
        capture_output=True, text=True, check=True,
    )


def main() -> None:
    CLIPS.mkdir(parents=True, exist_ok=True)
    helen_thai = ensure_clip("helen-thai", "Thai English", HELEN_VOICE_ID)
    helen_en = ensure_clip("helen-en", "Standard English", HELEN_VOICE_ID)
    thai = src_to_wav(ASSETS / "thai-style-model.mp3", CLIPS / "thai.wav")
    benedict = src_to_wav(ASSETS / "model-sentence-benedict.mp3", CLIPS / "benedict.wav")

    raw_out = CLIPS / "joined.wav"
    assemble([helen_thai.stem, thai.stem, helen_en.stem, benedict.stem], raw_out)

    subprocess.run(
        ["ffmpeg", "-y", "-i", str(raw_out),
         "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
         "-c:a", "libmp3lame", "-b:a", "128k", str(OUT)],
        capture_output=True, text=True, check=True,
    )
    print(f"Saved: {OUT} ({probe_duration(OUT):.2f}s)")


if __name__ == "__main__":
    main()
