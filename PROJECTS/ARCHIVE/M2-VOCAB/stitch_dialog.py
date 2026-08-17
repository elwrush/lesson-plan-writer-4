"""
stitch_dialog.py — Per-line MP3 files → single stitched MP3 via ffmpeg.

Builds a concat file with context-aware silence gaps between turns.
Uses ffmpeg concat demuxer for lossless stream copy.

Usage:
    python stitch_dialog.py dialog.json --lines output/dialogs/topic/lines/ --output output/dialogs/topic/output.mp3
"""

import json
import os
import subprocess
import sys
from pathlib import Path


def get_gap_duration(current_turn, next_turn):
    """Determine silence gap between turns based on context."""
    sd = (current_turn.get("stage_direction") or "").lower()
    next_sd = (next_turn.get("stage_direction") or "").lower() if next_turn else ""
    next_char = next_turn.get("character", "") if next_turn else ""
    curr_char = current_turn.get("character", "")

    if "long pause" in sd or "pause" in sd:
        return 500
    if "interrupt" in sd or "interrupt" in next_sd:
        return 50
    # Line ending with -- (em dash or double dash) signals cutoff → quick overlap
    curr_line = (current_turn.get("line") or "").strip()
    if curr_line.endswith("--") or curr_line.endswith("—"):
        return 50
    if next_char == curr_char:
        return 150
    return 300


def generate_silence(duration_ms, filename):
    """Generate a silence MP3 file of given duration."""
    duration_sec = duration_ms / 1000.0
    subprocess.run(
        ["ffmpeg", "-y", "-f", "lavfi", "-i",
         f"anullsrc=r=24000:cl=mono", "-t", str(duration_sec),
         "-c:a", "libmp3lame", "-b:a", "128k", str(filename)],
        capture_output=True,
        check=True,
    )


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    if len(sys.argv) < 2:
        print("Usage: python stitch_dialog.py dialog.json --lines <dir> --output <file>")
        sys.exit(1)

    dialog_path = Path(sys.argv[1])
    if not dialog_path.exists():
        print(f"Dialog file not found: {dialog_path}", file=sys.stderr)
        sys.exit(1)

    dialog = json.loads(dialog_path.read_text(encoding="utf-8"))
    turns = dialog.get("turns", [])

    lines_dir = None
    output_path = None
    args = iter(sys.argv[2:])
    for arg in args:
        if arg == "--lines":
            lines_dir = Path(next(args))
        elif arg == "--output":
            output_path = Path(next(args))
        elif arg == "--output-dir":
            output_path = Path(next(args)) / "stitched.mp3"

    if not lines_dir or not lines_dir.exists():
        print(f"Lines directory not found: {lines_dir}", file=sys.stderr)
        sys.exit(1)
    if not output_path:
        output_path = lines_dir.parent / "stitched.mp3"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Check ffmpeg availability
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ffmpeg not found. Install from https://ffmpeg.org", file=sys.stderr)
        sys.exit(1)

    # Pre-generate silence files
    silence_dir = lines_dir.parent / "silence"
    silence_dir.mkdir(exist_ok=True)

    silence_files = {}
    for ms in [50, 150, 300, 500]:
        sf = silence_dir / f"silence_{ms}ms.mp3"
        if not sf.exists():
            print(f"  Generating silence {ms}ms...")
            generate_silence(ms, sf)
        silence_files[ms] = sf

    # Verify all line files exist before stitching
    missing = []
    for i in range(len(turns)):
        lf = lines_dir / f"line_{i:03d}.mp3"
        if not lf.exists():
            missing.append(f"line_{i:03d}.mp3")
    if missing:
        print(f"ERROR: {len(missing)}/{len(turns)} line files missing:", file=sys.stderr)
        for m in missing:
            print(f"  {m}", file=sys.stderr)
        print("Run generate_lines.py first to create all line files.", file=sys.stderr)
        sys.exit(1)

    # Build concat file
    concat_path = output_path.parent / "concat.txt"
    with open(concat_path, "w", encoding="utf-8") as f:
        for i, turn in enumerate(turns):
            line_file = lines_dir / f"line_{i:03d}.mp3"

            f.write(f"file '{line_file.resolve()}'\n")
            if i > 0:
                f.write("inpoint 0.02\n")  # trim encoder priming gap

            if i < len(turns) - 1:
                gap = get_gap_duration(turn, turns[i + 1])
                sf = silence_files.get(gap, silence_files[300])
                f.write(f"file '{sf.resolve()}'\n")

    # Run ffmpeg concat
    print(f"Stitching {len(turns)} lines -> {output_path}")
    result = subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0",
         "-i", str(concat_path),
         "-c", "copy",
         str(output_path)],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        # Probe duration
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries",
             "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
             str(output_path)],
            capture_output=True, text=True,
        )
        duration = probe.stdout.strip()
        size_kb = output_path.stat().st_size // 1024
        print(f"Done: {output_path} ({duration}s, {size_kb}KB)")
    else:
        print(f"FFmpeg error: {result.stderr[:500]}", file=sys.stderr)
        sys.exit(1)

    # Clean up concat file
    concat_path.unlink(missing_ok=True)
    print(f"Concat temp file cleaned: {concat_path}")


if __name__ == "__main__":
    main()
