"""stitch_natural.py — Stitch dialog line MP3s with naturalistic pauses.

Replaces the skill's -c copy stitch (which produced files that ffmpeg decodes
inconsistently) with a re-encoded concat to uniform 44.1kHz mono, and uses
conversation-aware gaps instead of a fixed 300ms turn gap:

    Teacher question -> student answer   600ms  (student processing beat)
    Student answer -> next question      400ms  (teacher moves on)
    Same speaker continuing              250ms  (natural thought flow)

Usage:
    python3 "PROJECTS/INTERVIEW SPEAKING/stitch_natural.py"
"""

import json
import subprocess
from pathlib import Path

BASE = Path(__file__).parent / "assets"
SILENCE_DIR = BASE / "silence"


def silence_path(ms: int) -> Path:
    SILENCE_DIR.mkdir(parents=True, exist_ok=True)
    p = SILENCE_DIR / f"silence_{ms}ms.mp3"
    if not p.exists():
        subprocess.run(
            ["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
             "-t", f"{ms / 1000:.3f}", "-q:a", "9", str(p)],
            check=True, capture_output=True,
        )
    return p


def gap_between(prev: dict, nxt: dict) -> int:
    """Return gap in ms between two consecutive turns."""
    if prev["character"] == nxt["character"]:
        return 250
    if prev["character"].startswith("Teacher"):
        return 600
    return 400


def stitch(dialog_json: Path, lines_dir: Path, out_path: Path) -> None:
    turns = json.loads(dialog_json.read_text(encoding="utf-8"))["turns"]
    concat = out_path.parent / f"concat-{out_path.stem}.txt"

    with open(concat, "w", encoding="utf-8") as f:
        for i, turn in enumerate(turns):
            line_file = lines_dir / f"line_{i:03d}.mp3"
            f.write(f"file '{line_file.resolve()}'\n")
            if i < len(turns) - 1:
                gap = silence_path(gap_between(turn, turns[i + 1]))
                f.write(f"file '{gap.resolve()}'\n")

    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat),
         "-ar", "44100", "-ac", "1", "-b:a", "128k", str(out_path)],
        check=True, capture_output=True,
    )
    concat.unlink(missing_ok=True)
    print(f"Stitched {len(turns)} lines -> {out_path}")


def main() -> None:
    stitch(
        BASE.parent / "dialog-b1.json",
        BASE / "dialog-b1" / "lines",
        BASE / "interview-b1-ploy.mp3",
    )
    stitch(
        BASE.parent / "dialog-b2.json",
        BASE / "dialog-b2" / "lines",
        BASE / "interview-b2-elle.mp3",
    )


if __name__ == "__main__":
    main()
