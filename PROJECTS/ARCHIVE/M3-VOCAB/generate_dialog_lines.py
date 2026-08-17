"""
generate_lines.py — Generate per-line MP3 files via Fish Audio TTS.

Takes dialog JSON + voice ID mapping, engineers steering tags (Fish Audio
bracket syntax), calls Fish Audio API per line, saves MP3 files.

Usage:
    python generate_lines.py dialog.json voices.json --output output/dialogs/topic/
"""

import json
import os
import re
import sys
import time
from pathlib import Path

import requests


# Fish Audio S2 bracket-format emotion/tone tags
STAGE_DIRECTION_TAGS = {
    "laughs": "[chuckling]",
    "laugh": "[chuckling]",
    "skeptical": "[doubtful]",
    "slowly": "[calm]",
    "long pause": "[calm]",
    "pause": "[calm]",
    "interrupting": "[in a hurry tone]",
    "interrupt": "[in a hurry tone]",
    "defensive": "[frustrated]",
    "sharply": "[frustrated]",
    "softly": "[soft tone]",
    "whisper": "[whispering]",
    "excited": "[excited]",
    "excitedly": "[excited]",
    "angry": "[angry]",
    "confused": "[confused]",
    "sarcastic": "[sarcastic]",
    "doubtful": "[doubtful]",
    "happy": "[happy]",
    "confident": "[confident]",
    "chuckling": "[chuckling]",
    "calm": "[calm]",
    "warm": "[happy]",
}

BASELINE_KEYWORDS = {
    "thoughtful": "[thoughtful]",
    "questioning": "[curious]",
    "playful": "[happy]",
    "warm": "[happy]",
    "sharp": "[determined]",
    "defensive": "[frustrated]",
    "soft": "[soft tone]",
    "curious": "[curious]",
    "authoritative": "[confident]",
    "teacher": "[confident]",
    "nervous": "[nervous]",
    "unsure": "[nervous]",
    "enthusiastic": "[excited]",
    "bright": "[excited]",
    "energetic": "[excited]",
}

DEFAULT_BASELINE = "[calm]"


def _lookup_stage_tag(stage_direction: str) -> str | None:
    sd_lower = stage_direction.lower()
    for key, tag in STAGE_DIRECTION_TAGS.items():
        if key in sd_lower:
            return tag
    return None


def _lookup_baseline_tag(voice_notes: str) -> str:
    notes_lower = voice_notes.lower()
    for keyword, tag in BASELINE_KEYWORDS.items():
        if keyword in notes_lower:
            return tag
    return DEFAULT_BASELINE


def _engineer_tag(
    stage_direction: str | None,
    voice_notes: str,
    is_first_line: bool,
) -> str:
    if stage_direction:
        tag = _lookup_stage_tag(stage_direction)
        if tag:
            return tag
    if is_first_line:
        return _lookup_baseline_tag(voice_notes)
    return ""


def _build_character_baselines(characters: list[dict]) -> dict[str, str]:
    baselines = {}
    for char in characters:
        name = char.get("name", "")
        notes = char.get("voice_notes", "")
        baselines[name] = _lookup_baseline_tag(notes)
    return baselines


def clean_line_text(text: str) -> str:
    text = text.strip()
    text = re.sub(r"\([^)]*\)", "", text).strip()
    text = text.replace("...", "\u2014")
    text = text.replace("..", "\u2014")
    return text


def generate_line(voice_id: str, text_with_tag: str, filename: Path, retries: int = 3) -> bool:
    """Generate a single line via Fish Audio TTS API."""
    api_key = os.environ.get("FISH_API_KEY")
    if not api_key:
        print("FISH_API_KEY not set", file=sys.stderr)
        return False

    last_error = None
    for attempt in range(retries):
        try:
            r = requests.post(
                "https://api.fish.audio/v1/tts",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "model": "s2.1-pro-free",
                },
                json={
                    "text": text_with_tag,
                    "reference_id": voice_id,
                    "format": "mp3",
                    "mp3_bitrate": 128,
                    "latency": "normal",
                },
                timeout=30,
            )
            if r.status_code == 200:
                with open(filename, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                return True
            else:
                last_error = f"HTTP {r.status_code}: {r.text[:200]}"
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
        except requests.RequestException as e:
            last_error = str(e)
            if attempt < retries - 1:
                time.sleep(2 ** attempt)

    print(f"  Failed: {filename} \u2014 {last_error}", file=sys.stderr)
    return False


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    if len(sys.argv) < 3:
        print("Usage: python generate_lines.py dialog.json voices.json --output outdir/")
        sys.exit(1)

    dialog_path = Path(sys.argv[1])
    voices_path = Path(sys.argv[2])

    if not dialog_path.exists():
        print(f"Dialog file not found: {dialog_path}", file=sys.stderr)
        sys.exit(1)
    if not voices_path.exists():
        print(f"Voices file not found: {voices_path}", file=sys.stderr)
        sys.exit(1)

    dialog = json.loads(dialog_path.read_text(encoding="utf-8"))
    voices = json.loads(voices_path.read_text(encoding="utf-8"))

    output_dir = None
    args = iter(sys.argv[3:])
    for arg in args:
        if arg in ("--output", "--output-dir"):
            output_dir = Path(next(args))

    if not output_dir:
        output_dir = Path("output/dialogs/unknown/lines")

    output_dir.mkdir(parents=True, exist_ok=True)

    characters = dialog.get("characters", [])
    baselines = _build_character_baselines(characters)
    turns = dialog.get("turns", [])
    total = len(turns)
    success_count = 0

    seen_chars = set()

    print(f"Generating {total} lines...")
    for i, turn in enumerate(turns):
        char = turn["character"]
        voice_id = voices.get(char)

        if not voice_id:
            print(f"  [{i+1}/{total}] No voice ID for {char} \u2014 skipping")
            continue

        is_first_line = char not in seen_chars
        seen_chars.add(char)

        voice_notes = ""
        for c in characters:
            if c.get("name") == char:
                voice_notes = c.get("voice_notes", "")
                break

        tag = _engineer_tag(
            stage_direction=turn.get("stage_direction"),
            voice_notes=voice_notes,
            is_first_line=is_first_line,
        )

        clean_text = clean_line_text(turn["line"])
        if tag:
            text_with_tag = f"{tag} {clean_text}"
        else:
            text_with_tag = clean_text

        filename = output_dir / f"line_{i:03d}.mp3"
        print(f"  [{i+1}/{total}] {char}: {text_with_tag[:50]}...", end=" ")
        if generate_line(voice_id, text_with_tag, filename):
            success_count += 1
            print("OK")
        else:
            print("FAILED")

    print(f"\nGenerated {success_count}/{total} lines in {output_dir}")

    meta = {
        "lines": str(output_dir),
        "total": total,
        "success": success_count,
    }
    with open(output_dir / "generation_meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)


if __name__ == "__main__":
    main()
