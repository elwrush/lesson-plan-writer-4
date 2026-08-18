"""Generate Patrick Stewart's model reading of the Part H quantum paragraph."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from generate_partb_audio import tts, trim_to_wav, probe_duration  # noqa: E402

PATRICK_VOICE_ID = "134fbc5b934446c5b896b1e07b824e03"
TEXT = (
    "Quantum physics sounds strange. It started as a simple question: scientists wanted answers "
    "about light, so they studied and decided how one particle could act as a wave. They discovered "
    "something amazing. Light exists in two states at once. This idea changed our world. Computers, "
    "phones, and lasers needed this discovery. So remember, when you use your phone, you are using "
    "quantum physics!"
)
CLIPS = Path("PROJECTS/PRONUNCIATION NOTICING/slides/assets/parth-clips")
OUT = Path("PROJECTS/PRONUNCIATION NOTICING/slides/assets/quantum-model.mp3")


def main() -> None:
    CLIPS.mkdir(parents=True, exist_ok=True)
    raw = CLIPS / "quantum-raw.mp3"
    wav = CLIPS / "quantum.wav"
    if not raw.exists():
        print(f"TTS (model): {TEXT[:60]}...")
        tts(TEXT, raw, voice_id=PATRICK_VOICE_ID)
    trim_to_wav(raw, wav)
    duration = probe_duration(wav)
    print(f"trimmed: {duration:.2f}s")

    import subprocess

    subprocess.run(
        ["ffmpeg", "-y", "-i", str(wav), "-c:a", "libmp3lame", "-b:a", "128k", str(OUT)],
        capture_output=True, text=True, check=True,
    )
    print(f"Saved: {OUT}")


if __name__ == "__main__":
    main()
