#!/usr/bin/env python3
"""
Re-assemble the interview master + sections WITHOUT regenerating any TTS.
Only change: the pause before "Now listen again" -> 5.0s (was 0.6s).

Reads existing: dialog/announce/*.mp3, dialog/interview_chunkN.mp3
Writes:         dialog/interview-master.mp3, dialog/sectionN.mp3
                output/interview-master.mp3, output/sectionN.mp3  (copies)
"""

import subprocess
from pathlib import Path

MY_DIR = Path(__file__).resolve().parent
DLG = MY_DIR / "dialog"
ANN = DLG / "announce"

LEAD_IN = 0.5
LEAD_OUT = 0.7
AFTER_CHUNK_LABEL = 0.9
BEFORE_AGAIN = 5.0   # <-- the requested change
AFTER_AGAIN = 0.9
CHUNK_SEP = 1.3


def duration(path):
    p = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True)
    try:
        return float(p.stdout.strip())
    except ValueError:
        return 0.0


def make_silence(dur, name):
    p = DLG / name
    subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i",
                    f"anullsrc=r=44100:cl=mono", "-t", f"{dur:.2f}",
                    "-c:a", "libmp3lame", "-b:a", "128k", str(p)],
                   capture_output=True, check=True)
    return p


def main():
    chunks = [DLG / f"interview_chunk{i}.mp3" for i in range(1, 5)]
    ann = {k: ANN / f"{k}.mp3" for k in ["chunk1", "chunk2", "chunk3", "chunk4", "again"]}

    entries = []
    entries.append(("file", make_silence(LEAD_IN, "r_lead.mp3")))
    for i in range(1, 5):
        entries.append(("file", ann[f"chunk{i}"]))
        entries.append(("file", make_silence(AFTER_CHUNK_LABEL, f"r_afterchunk{i}.mp3")))
        entries.append(("file", chunks[i - 1]))                                  # 1st play
        entries.append(("file", make_silence(BEFORE_AGAIN, f"r_beforeagain{i}.mp3")))
        entries.append(("file", ann["again"]))
        entries.append(("file", make_silence(AFTER_AGAIN, f"r_afteragain{i}.mp3")))
        entries.append(("file", chunks[i - 1]))                                  # 2nd play
        if i < 4:
            entries.append(("file", make_silence(CHUNK_SEP, f"r_sep{i}.mp3")))
    entries.append(("file", make_silence(LEAD_OUT, "r_out.mp3")))

    # compute boundaries while walking
    boundaries = {}
    running = 0.0
    for (kind, p) in entries:
        for i in range(1, 5):
            if p == ann[f"chunk{i}"] and i not in boundaries:
                boundaries[i] = running
        running += duration(p)

    concat_txt = DLG / "reassemble_concat.txt"
    with open(concat_txt, "w") as f:
        for kind, p in entries:
            f.write(f"file '{p.resolve()}'\n")

    master = DLG / "interview-master.mp3"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_txt),
         "-ar", "44100", "-ac", "1", "-b:a", "128k", str(master)],
        check=True, capture_output=True)
    print(f"Master rebuilt: {master} ({duration(master):.1f}s)")

    # slice
    total = duration(master)
    order = sorted(boundaries.items())
    for idx, (chunk_i, start) in enumerate(order):
        end = order[idx + 1][1] if idx + 1 < len(order) else total
        sec = DLG / f"section{chunk_i}.mp3"
        subprocess.run(
            ["ffmpeg", "-y", "-ss", f"{start:.3f}", "-i", str(master),
             "-t", f"{end - start:.3f}", "-ar", "44100", "-ac", "1",
             "-b:a", "128k", str(sec)],
            check=True, capture_output=True)
        print(f"  section{chunk_i}: {sec} ({start:.1f}s -> {end:.1f}s, {end-start:.1f}s)")

    # copy final tapes up to output/
    for f in ["interview-master.mp3", "section1.mp3", "section2.mp3",
              "section3.mp3", "section4.mp3"]:
        src = DLG / f
        dst = MY_DIR / f
        import shutil
        shutil.copyfile(src, dst)
        print(f"  copied -> {dst}")


if __name__ == "__main__":
    main()
