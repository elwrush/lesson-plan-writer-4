#!/usr/bin/env python3
"""generate_audio.py — Generate dictation + podcast interview audio for LISTENING M3.

It's Academic: "Opium, Empire, and the Country That Got Away"

Outputs (copied to slides/assets/):
    questions.mp3    — dictation tape (8 questions, each read twice)
    tape1-4.mp3      — interview sections (each chunk played twice)
    interview-master.mp3 — full interview with announcements

Voices:
    Jack Smith (host)       → scolbert-us-male-celeb (ecd51fc99...)
    Ebony Mills (researcher)→ US-F-teen-1 (c87c0346...)
    Announcer               → Benedict_Cumberbatch (2d3546b7...)
"""

import base64
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import requests


# ── Foreign-name pronunciation (CMU Arpabet phoneme tags) ──────────────
# Canonical module lives in the fish-audio skill. It returns text with
# <|phoneme_start|>...<|phoneme_end|> tags for non-English proper nouns (Siam,
# Mongkut, Chulalongkorn, Lin Zexu, ...) so Fish doesn't misread them.
try:
    sys.path.insert(0, "/home/elwru/.agents/skills/fish-audio/scripts")
    from pronounce import apply_pronunciations  # type: ignore
except ImportError:  # pragma: no cover — fallback: no-op if module missing
    def apply_pronunciations(text: str) -> str:
        return text


# ── Markdown stripping (CRITICAL: Fish TTS reads *all* characters) ────

def strip_markdown(text: str) -> str:
    """Remove markdown formatting so Fish Audio doesn't read it aloud.

    Fish TTS has NO built-in markdown handling. Asterisks, backticks, and
    other formatting characters are read as literal words ("asterisk",
    "hash", etc.). This MUST be called on every text before sending to TTS.

    Reference: AGENTS.md gotcha — "TTS cannot mispronounce"
    """
    # Remove bold/italic markers (order matters: bold before italic)
    text = re.sub(r'\*\*\*(.*?)\*\*\*', r'\1', text)  # ***bold italic***
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)        # **bold**
    text = re.sub(r'\*(.*?)\*', r'\1', text)             # *italic*
    text = re.sub(r'__(.*?)__', r'\1', text)             # __bold__
    text = re.sub(r'_(.*?)_', r'\1', text)               # _italic_
    # Remove code
    text = re.sub(r'`(.*?)`', r'\1', text)               # `code`
    # Remove links — keep text only
    text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', text) # [text](url)
    # Remove images — keep alt text
    text = re.sub(r'!\[([^\]]*)\]\([^)]*\)', r'\1', text) # ![alt](url)
    # Remove headings
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Remove blockquotes
    text = re.sub(r'^>\s*', '', text, flags=re.MULTILINE)
    # Remove horizontal rules
    text = re.sub(r'^[-*_]{3,}\s*$', '', text, flags=re.MULTILINE)
    # Collapse multiple spaces
    text = re.sub(r'  +', ' ', text)
    return text.strip()


# ── RED-GATE: blocks TTS if markdown artifacts remain ─────────────────

# Patterns that MUST NOT reach Fish Audio TTS. Each is tested in order.
# If ANY match, the call is BLOCKED and an error is raised.
MD_ARTIFACT_PATTERNS = [
    (r'\*\*', 'double asterisk (bold marker)'),
    (r'(?<!\w)\*(?!\*)', 'lone asterisk (italic marker)'),
    (r'__(?!_)', 'double underscore (bold marker)'),
    (r'(?<!\w)_(?!_)', 'lone underscore (italic marker)'),
    (r'`', 'backtick (code marker)'),
    (r'!\[', 'image syntax ![alt](url)'),
    (r'(?<!\w)\[([^\]]*)\]\([^)]*\)', 'link syntax [text](url)'),
    (r'^#{1,6}\s', 'heading syntax # Title', re.MULTILINE),
    (r'^>\s', 'blockquote syntax > text', re.MULTILINE),
]


def assert_no_markdown(text: str, context: str = "") -> None:
    """RED-GATE: raise RuntimeError if markdown artifacts are detected.

    This is a HARD GATE, not a warning. If this fires, the TTS call is
    blocked. The caller MUST strip_markdown() before reaching this point.

    Args:
        text: the string about to be sent to Fish Audio TTS.
        context: optional label (e.g. "Jack line 3") for the error message.

    Raises:
        RuntimeError with the specific artifact found and how to fix it.
    """
    for pattern, desc, *rest in MD_ARTIFACT_PATTERNS:
        flags = rest[0] if rest else 0
        if re.search(pattern, text, flags):
            ctx = f" (in {context})" if context else ""
            raise RuntimeError(
                f"RED-GATE BLOCKED{ctx}: markdown artifact detected — {desc}\n"
                f"  Text: {text[:120]!r}...\n"
                f"  Fix:  call strip_markdown() before assert_no_markdown(), "
                f"or remove the {desc} from the source text."
            )

# ── Config ───────────────────────────────────────────────────────────

MY_DIR = Path(__file__).resolve().parent
SLIDES_ASSETS = MY_DIR / "slides" / "assets"
SLIDES_ASSETS.mkdir(parents=True, exist_ok=True)

PIECES_DIR = MY_DIR / "output" / "pieces"
PIECES_DIR.mkdir(parents=True, exist_ok=True)

OUT_DIR = MY_DIR / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)

API_KEY = os.environ.get("FISH_API_KEY")
if not API_KEY:
    print("FISH_API_KEY not set", file=sys.stderr)
    sys.exit(1)

VOICES = {
    "Jack": "ecd51fc992bf4a2d9a4b1d1c7aadcfb8",   # scolbert-us-male-celeb
    "Ebony": "c87c03465e564db9957f25c600895f08",    # US-F-teen-1
}
ANNOUNCER_ID = "2d3546b7f9424d28ba8d23d90a7bea24"   # Benedict_Cumberbatch

# Fish Audio mispronounces numerals unless written as words. Always spell
# numbers out for the label/sentence text sent to TTS.
NUMBER_WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five",
                6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten"}

# ── Dictation questions ──────────────────────────────────────────────

DICT_CHUNKS = {
    1: [
        "What is the key difference between trading with a country and colonising it?",
        "How did the British justify colonisation?",
    ],
    2: [
        "Why was Britain spending so much silver on Chinese tea, silk, and porcelain, and how did the opium trade fix this problem?",
        "What excuse did Britain use to start the First Opium War after Lin Zexu destroyed their opium?",
    ],
    3: [
        "How did the opium trade affect ordinary Chinese families?",
        "What does extraterritoriality mean, and why did it make the Chinese angry?",
    ],
    4: [
        "How did King Mongkut's approach to the British differ from the Chinese emperor's approach?",
        "What strategy did King Chulalongkorn use to keep Thailand independent while giving up forty percent of its territory?",
    ],
}

# Which word the dictation read pauses AFTER, so students have time to write.
# The question is still spoken as ONE complete natural sentence (real prosody);
# ffmpeg inserts a 2s pause at this word's timestamp in post-processing.
# Key = (chunk, question_index 1-based). Value = word the pause lands after
# (must appear verbatim in the question; case-insensitive match).
DICT_SPLITS = {
    (1, 1): "country",          # ... trading with a country | and colonising it?
    (1, 2): "British",          # ... How did the British | justify colonisation?
    (2, 1): "porcelain",        # ... silk, and porcelain, | and how did the opium...
    (2, 2): "War",              # ... the First Opium War | after Lin Zexu...
    (3, 1): "trade",            # ... How did the opium trade | affect ordinary...
    (3, 2): "mean",             # ... What does extraterritoriality mean, | and why...
    (4, 1): "differ",           # ... approach to the British differ | from the Chinese...
    (4, 2): "independent",      # ... keep Thailand independent | while giving up...
}

# ── Dialog parsing ───────────────────────────────────────────────────

DIALOG_PATH = MY_DIR / "dialog-draft.md"
SPEAKER_RE = re.compile(r"^\*\*(Jack|Ebony):\*\*\s*(.*)$")
CHUNK_RE = re.compile(r"^\*\*Chunk (\d+)")


def parse_dialog() -> list[list[tuple[str, str]]]:
    """Parse dialog-draft.md into list of chunks, each a list of (speaker, text).

    CRITICAL: All text is run through strip_markdown() before returning.
    Fish Audio TTS reads *all* characters — asterisks become "asterisk",
    underscores become "underscore", etc. This is the #1 source of expensive
    re-generation errors.
    """
    lines = DIALOG_PATH.read_text(encoding="utf-8").splitlines()
    chunks: list[list[tuple[str, str]]] = []
    current: list[tuple[str, str]] = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if CHUNK_RE.match(line):
            if current:
                chunks.append(current)
                current = []
            continue
        m = SPEAKER_RE.match(line)
        if m:
            speaker = m.group(1).strip()
            text = strip_markdown(m.group(2).strip())
            current.append((speaker, text))
    if current:
        chunks.append(current)
    return chunks


# ── TTS ──────────────────────────────────────────────────────────────

def tts(text: str, voice_id: str, out_path: Path, retries: int = 4) -> bool:
    """Generate TTS via Fish Audio API.

    CRITICAL: Text MUST be plain — no markdown, no asterisks, no underscores.
    Pipeline: strip_markdown() → apply_pronunciations() → assert_no_markdown().
    If assert_no_markdown fires, the call is BLOCKED — fix the source text.
    Foreign names (Siam, Mongkut, Chulalongkorn, ...) are tagged with CMU
    Arpabet via apply_pronunciations so Fish doesn't misread them.
    """
    text = strip_markdown(text)
    text = apply_pronunciations(text)
    assert_no_markdown(text, context=f"tts({text[:40]!r})")
    payload = json.dumps({
        "text": text,
        "reference_id": voice_id,
        "format": "mp3",
        "mp3_bitrate": 128,
        "latency": "normal",
    })
    out_path.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(1, retries + 1):
        try:
            r = requests.post(
                "https://api.fish.audio/v1/tts",
                headers={"Authorization": f"Bearer {API_KEY}",
                         "Content-Type": "application/json"},
                data=payload, timeout=120, stream=True,
            )
            if r.status_code == 200:
                with open(out_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                return True
            print(f"  attempt {attempt}: HTTP {r.status_code} {r.text[:120]}", file=sys.stderr)
        except requests.RequestException as e:
            print(f"  attempt {attempt}: {e}", file=sys.stderr)
        time.sleep(2.5)
    return False


def get_duration(path: Path) -> float:
    if not path.exists():
        return 0.0
    p = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True)
    try:
        return float(p.stdout.strip())
    except ValueError:
        return 0.0


def make_silence(dur: float, name: str) -> Path:
    p = PIECES_DIR / name
    subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i",
                    f"anullsrc=r=44100:cl=mono", "-t", f"{dur:.2f}",
                    "-c:a", "libmp3lame", "-b:a", "128k", str(p)],
                   capture_output=True, check=True)
    return p


# ── Streaming TTS with word-level timestamps ─────────────────────────

def tts_with_timestamps(text: str, voice_id: str, out_path: Path,
                        retries: int = 4) -> tuple[Path, list[dict]]:
    """Generate speech + word-level timestamps via the streaming endpoint.

    Calls POST /v1/tts/stream/with-timestamp. Concatenates all audio_base64
    chunks into `out_path`, and returns the global word timeline:
        [{"text": "What", "start": 0.0, "end": 0.32}, ...]
    where start/end are seconds on the FULL audio (chunk_audio_offset_sec
    already added). Timestamps let post-processing place a pause at an exact
    word without fragmenting the sentence.
    """
    text = strip_markdown(text)
    text = apply_pronunciations(text)
    assert_no_markdown(text, context=f"ts({text[:40]!r})")
    for attempt in range(1, retries + 1):
        try:
            resp = requests.post(
                "https://api.fish.audio/v1/tts/stream/with-timestamp",
                headers={"Authorization": f"Bearer {API_KEY}",
                         "Content-Type": "application/json"},
                json={"text": text, "reference_id": voice_id,
                      "format": "wav", "latency": "balanced",
                      "chunk_length": 300, "normalize": True},
                stream=True, timeout=120,
            )
            if resp.status_code != 200:
                print(f"  attempt {attempt}: HTTP {resp.status_code} {resp.text[:120]}", file=sys.stderr)
                time.sleep(2.5)
                continue
            audio = []
            align = {}
            for line in resp.iter_lines(decode_unicode=True):
                if not line or not line.startswith("data: "):
                    continue
                ev = json.loads(line[6:])
                if ev.get("audio_base64"):
                    audio.append(base64.b64decode(ev["audio_base64"]))
                if ev.get("alignment"):
                    align[ev["chunk_seq"]] = {
                        "offset": ev["chunk_audio_offset_sec"],
                        "segments": ev["alignment"]["segments"],
                    }
            if not audio:
                raise RuntimeError("no audio in stream")
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_bytes(b"".join(audio))
            # Build global timeline
            timeline = []
            for cs in sorted(align):
                off = align[cs]["offset"]
                for seg in align[cs]["segments"]:
                    timeline.append({
                        "text": seg["text"],
                        "start": seg["start"] + off,
                        "end": seg["end"] + off,
                    })
            return out_path, timeline
        except Exception as e:
            print(f"  attempt {attempt}: {e}", file=sys.stderr)
            time.sleep(2.5)
    raise RuntimeError(f"tts_with_timestamps failed for: {text[:60]!r}")


def word_pause_time(timeline: list[dict], trigger: str,
                    direction: str = "after", pad: float = 0.12) -> float:
    """Find the timestamp where a pause should be inserted relative to a word.

    trigger: the word to anchor on (case-insensitive, matched against segment
             text, whitespace/punct-trimmed).
    direction:
        "after"  -> pause AFTER the trigger word ends  (split at trigger.end + pad)
        "before" -> pause BEFORE the trigger word (split at trigger.start - pad)
    Returns the split time in seconds on the audio timeline.
    """
    for seg in timeline:
        word = re.sub(r'[^\w\']', '', seg["text"]).lower()
        if word == trigger.lower():
            if direction == "after":
                return max(0.0, seg["end"] + pad)
            return max(0.0, seg["start"] - pad)
    # Trigger not found — no pause (log a warning, keep the sentence whole)
    raise ValueError(f"split word {trigger!r} not found in timeline")


def insert_pause_at(src: Path, dst: Path, split_sec: float,
                    pause_sec: float = 2.0) -> None:
    """Insert `pause_sec` seconds of silence at `split_sec` into `src`.

    Uses ffmpeg filter_complex: split the source at `split_sec`, insert silence,
    and rejoin. Keeps the sentence as ONE recording but adds a clean 2s gap so
    students have time to write.
    """
    sil = make_silence(pause_sec, f"pause_{dst.stem}.mp3")
    cmd = [
        "ffmpeg", "-y",
        "-i", str(src),
        "-i", str(sil),
        "-filter_complex",
        f"[0:a]atrim=0:{split_sec:.3f},asetpts=PTS-STARTPTS[pre];"
        f"[0:a]atrim={split_sec:.3f},asetpts=PTS-STARTPTS[post];"
        f"[pre][1:a][post]concat=n=3:v=0:a=1[out]",
        "-map", "[out]",
        "-ar", "44100", "-ac", "1", "-c:a", "libmp3lame", "-b:a", "128k",
        str(dst),
    ]
    subprocess.run(cmd, check=True, capture_output=True)


# ── Interview generation ─────────────────────────────────────────────

ANNOUNCEMENTS = {
    "chunk1": "Chunk one.",
    "chunk2": "Chunk two.",
    "chunk3": "Chunk three.",
    "chunk4": "Chunk four.",
    "again": "Now listen again.",
}


def generate_interview_chunks(chunks: list[list[tuple[str, str]]]) -> list[Path]:
    """Generate per-chunk MP3s (each line as separate TTS, stitched with gaps)."""
    sil300 = make_silence(0.30, "s300.mp3")
    sil150 = make_silence(0.15, "s150.mp3")
    sil500 = make_silence(0.50, "s500.mp3")

    chunk_files = []
    for ci, turns in enumerate(chunks):
        chunk_num = ci + 1
        chunk_dir = PIECES_DIR / f"chunk{chunk_num}"
        lines_dir = chunk_dir / "lines"
        lines_dir.mkdir(parents=True, exist_ok=True)

        print(f"  Generating chunk {chunk_num} ({len(turns)} turns)...")
        for i, (speaker, text) in enumerate(turns):
            lp = lines_dir / f"line_{i:03d}.mp3"
            if not lp.exists():
                print(f"    [{i+1}/{len(turns)}] {speaker}...", end=" ", flush=True)
                ok = tts(text, VOICES[speaker], lp)
                print("OK" if ok else "FAILED")

        # Stitch: gap 300ms between speakers, 150ms same speaker
        entries = []
        for i, (speaker, text) in enumerate(turns):
            entries.append(("file", lines_dir / f"line_{i:03d}.mp3"))
            if i < len(turns) - 1:
                nxt_speaker = turns[i + 1][0]
                gap = sil300 if nxt_speaker != speaker else sil150
                entries.append(("file", gap))

        concat_txt = chunk_dir / "concat.txt"
        with open(concat_txt, "w") as f:
            for kind, p in entries:
                f.write(f"file '{p.resolve()}'\n")
        out = OUT_DIR / f"interview_chunk{chunk_num}.mp3"
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_txt),
             "-ar", "44100", "-ac", "1", "-b:a", "128k", str(out)],
            check=True, capture_output=True)
        chunk_files.append(out)
        print(f"    -> {out.name} ({get_duration(out):.1f}s)")
    return chunk_files


def generate_announcements() -> dict[str, Path]:
    ann_dir = PIECES_DIR / "announce"
    ann_dir.mkdir(parents=True, exist_ok=True)
    files = {}
    for key, text in ANNOUNCEMENTS.items():
        p = ann_dir / f"{key}.mp3"
        if not p.exists():
            print(f"  Announce {key}...", end=" ", flush=True)
            ok = tts(text, ANNOUNCER_ID, p)
            print("OK" if ok else "FAILED")
        files[key] = p
    return files


def assemble_master(chunk_files: list[Path], ann: dict[str, Path]) -> tuple[Path, dict]:
    """Assemble master: each chunk announced + played twice per chunk."""
    entries = []
    entries.append(("file", make_silence(0.5, "m_lead.mp3")))
    boundaries = {}
    running = 0.0
    seen = set()

    for i in range(4):
        chunk_num = i + 1
        entries.append(("file", ann[f"chunk{chunk_num}"]))
        entries.append(("file", make_silence(0.9, f"m_afterchunk{i+1}.mp3")))
        entries.append(("file", chunk_files[i]))
        entries.append(("file", make_silence(0.6, f"m_pretul{i+1}.mp3")))
        entries.append(("file", ann["again"]))
        entries.append(("file", make_silence(0.9, f"m_afteragain{i+1}.mp3")))
        entries.append(("file", chunk_files[i]))
        if i < 3:
            entries.append(("file", make_silence(1.3, f"m_sep{i+1}.mp3")))

    entries.append(("file", make_silence(0.7, "m_out.mp3")))

    # Track boundaries for slicing
    chunk_seen = {}
    concat_entries = []
    for kind, p in entries:
        is_chunk_ann = False
        for i in range(4):
            if p == ann[f"chunk{i+1}"] and i not in chunk_seen:
                chunk_seen[i] = True
                is_chunk_ann = True
                boundaries[i + 1] = running
        concat_entries.append(("file", p))
        running += get_duration(p)

    concat_txt = OUT_DIR / "master_concat.txt"
    with open(concat_txt, "w") as f:
        for kind, p in concat_entries:
            f.write(f"file '{p.resolve()}'\n")
    master = OUT_DIR / "interview-master.mp3"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_txt),
         "-ar", "44100", "-ac", "1", "-b:a", "128k", str(master)],
        check=True, capture_output=True)
    return master, boundaries


def slice_sections(master: Path, boundaries: dict) -> list[Path]:
    total = get_duration(master)
    order = sorted(boundaries.items())
    sections = []
    for idx, (chunk_i, start) in enumerate(order):
        end = order[idx + 1][1] if idx + 1 < len(order) else total
        out = OUT_DIR / f"section{chunk_i}.mp3"
        subprocess.run(
            ["ffmpeg", "-y", "-ss", f"{start:.3f}", "-i", str(master),
             "-t", f"{end - start:.3f}", "-ar", "44100", "-ac", "1", "-b:a", "128k",
             str(out)],
            check=True, capture_output=True)
        sections.append(out)
        print(f"  section{chunk_i}: {out.name} ({end - start:.1f}s)")
    return sections


# ── Dictation questions ──────────────────────────────────────────────

def generate_dictation() -> Path:
    """Generate questions.mp3 — 8 questions in 4 chunks, each read twice."""
    sil_intro = make_silence(0.6, "d_intro.mp3")
    sil_lab = make_silence(0.9, "d_lab.mp3")
    sil_rep = make_silence(4.0, "d_rep.mp3")
    sil_chunk = make_silence(1.2, "d_chunk.mp3")
    sil_int = make_silence(1.5, "d_int.mp3")
    sil_endq = make_silence(3.0, "d_endq.mp3")
    sil_out = make_silence(0.8, "d_out.mp3")

    intro_text = ("Listen and write down the eight questions you hear. "
                  "You will hear each question twice. Write exactly what you hear.")
    intro_p = PIECES_DIR / "d_intro_line.mp3"
    if not intro_p.exists():
        print("  Dictation intro...", end=" ", flush=True)
        ok = tts(intro_text, ANNOUNCER_ID, intro_p)
        print("OK" if ok else "FAILED")

    entries = [("file", sil_intro), ("file", intro_p), ("file", sil_int)]

    for ci in range(4):
        chunk_num = ci + 1
        q1, q2 = DICT_CHUNKS[chunk_num]

        # Chunk label
        chunk_label = PIECES_DIR / f"d_chunk_{chunk_num}.mp3"
        if not chunk_label.exists():
            print(f"  Dictation chunk {chunk_num} label...", end=" ", flush=True)
            ok = tts(f"Chunk {['one','two','three','four'][ci]}.", ANNOUNCER_ID, chunk_label)
            print("OK" if ok else "FAILED")
        entries.append(("file", chunk_label))
        entries.append(("file", sil_chunk))

        for qi, question in enumerate([q1, q2], 1):
            q_idx = len(DICT_CHUNKS[chunk_num]) * ci + qi
            # CRITICAL: write the number as a WORD, not a digit. Fish Audio
            # mispronounces numerals ("Question 1." reads as "Question Un").
            label_text = f"Question {NUMBER_WORDS[q_idx]}."
            label_p = PIECES_DIR / f"d_qlab_{chunk_num}_{qi}.mp3"
            if not label_p.exists():
                print(f"    Q{q_idx} label...", end=" ", flush=True)
                ok = tts(label_text, ANNOUNCER_ID, label_p)
                print("OK" if ok else "FAILED")

            # Generate the question as ONE complete, continuous natural sentence,
            # capturing Fish's word-level timestamps so we can drop a 2s write
            # pause at the exact split word (DICT_SPLITS) in post-processing.
            # Never fragment the sentence into separate TTS calls.
            raw_file = PIECES_DIR / f"d_q{chunk_num}_{qi}_raw"
            paused_file = PIECES_DIR / f"d_q{chunk_num}_{qi}.mp3"
            if not paused_file.exists():
                print(f"      Q{q_idx} sentence+ts...", end=" ", flush=True)
                raw_path = raw_file.with_suffix(".wav")
                try:
                    raw_path, timeline = tts_with_timestamps(question, ANNOUNCER_ID, raw_path)
                    split_word = DICT_SPLITS.get((chunk_num, qi), "country")
                    split_sec = word_pause_time(timeline, split_word, direction="after")
                    insert_pause_at(raw_path, paused_file, split_sec, pause_sec=2.0)
                    print(f"OK (split after '{split_word}' @ {split_sec:.2f}s)")
                except (RuntimeError, ValueError) as e:
                    print(f"WARNING: {e} — using unpaused sentence", file=sys.stderr)
                    # Fallback: re-encode raw without a pause
                    raw_path = raw_file.with_suffix(".wav")
                    subprocess.run(
                        ["ffmpeg", "-y", "-i", str(raw_path),
                         "-ar", "44100", "-ac", "1", "-c:a", "libmp3lame", "-b:a", "128k",
                         str(paused_file)], check=True, capture_output=True)
                    print("OK (no split)")

            entries.append(("file", label_p))
            entries.append(("file", sil_lab))

            # Hearing 1
            entries.append(("file", paused_file))
            # Pause between hearings
            entries.append(("file", sil_rep))
            # Hearing 2 (same natural sentence, same built-in write pause)
            entries.append(("file", paused_file))

            entries.append(("file", sil_endq))

    entries.append(("file", sil_out))

    concat_txt = OUT_DIR / "questions_concat.txt"
    with open(concat_txt, "w") as f:
        for kind, p in entries:
            f.write(f"file '{p.resolve()}'\n")
    out = OUT_DIR / "questions.mp3"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_txt),
         "-ar", "44100", "-ac", "1", "-b:a", "128k", str(out)],
        check=True, capture_output=True)
    print(f"  Dictation: {out.name} ({get_duration(out):.1f}s)")
    return out


# ── Main ─────────────────────────────────────────────────────────────

def main() -> None:
    chunks = parse_dialog()
    print(f"Parsed {len(chunks)} chunks from dialog-draft.md")

    print("\n=== Interview audio ===")
    chunk_files = generate_interview_chunks(chunks)

    print("\n=== Announcements ===")
    ann = generate_announcements()

    print("\n=== Master assembly ===")
    master, boundaries = assemble_master(chunk_files, ann)
    print(f"Master: {master.name} ({get_duration(master):.1f}s)")

    print("\n=== Slicing ===")
    sections = slice_sections(master, boundaries)

    print("\n=== Dictation questions ===")
    questions = generate_dictation()

    print("\n=== Copying to slides/assets ===")
    for i in range(1, 5):
        src = OUT_DIR / f"section{i}.mp3"
        dst = SLIDES_ASSETS / f"tape{i}.mp3"
        dst.write_bytes(src.read_bytes())
        print(f"  {dst.name}")
    dst = SLIDES_ASSETS / "questions.mp3"
    dst.write_bytes(questions.read_bytes())
    print(f"  {dst.name}")

    print("\n=== DONE ===")


if __name__ == "__main__":
    main()
