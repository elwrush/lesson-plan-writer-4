#!/usr/bin/env python3
"""
Generate the Nepal flood INTERVIEW audio.
Two voices: Lucy Milligan (podcaster) + Emma McKinley (aid worker).
Announcer: Benedict Cumberbatch clones for "Chunk N" + "Now listen again".

Outputs in this directory:
  interview_chunk{N}.mp3     - raw interview per chunk (played twice in master)
  benedict_announce.mp3      - one-shot announcement clip for each label
  interview-master.mp3       - single file: chunk1..4 each played TWICE
  section{N}.mp3             - the master sliced into 4 sections (ffmpeg)
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import requests

# --- config ---------------------------------------------------------------
MY_DIR = Path(__file__).resolve().parent
OUT = MY_DIR / "dialog"
OUT.mkdir(parents=True, exist_ok=True)

API_KEY = os.environ.get("FISH_API_KEY")
if not API_KEY:
    print("FISH_API_KEY not set", file=sys.stderr)
    sys.exit(1)

LUCY_ID = "141726a5cc6b426b9eb8be8938d732cf"     # Helen_Mirren_v2
EMMA_ID = "3348026252654c05a790528e411b117a"     # Emma_Watson
BENEDICT_ID = "2d3546b7f9424d28ba8d23d90a7bea24"  # Benedict_Cumberbatch

VOICES = {"Lucy Milligan": LUCY_ID, "Emma McKinley": EMMA_ID}
CHARACTERS = [
    {"name": "Lucy Milligan",
     "voice_notes": "British podcaster journalist, professional presenter, clear speech",
     "key_line": "So what actually caused the glacier to collapse?"},
    {"name": "Emma McKinley",
     "voice_notes": "British aid worker, calm and empathetic, measured",
     "key_line": "It was a morning nobody in that region will ever forget."},
]

# --- interview turns (character, stage_direction, line) ------------------
CHUNKS = {
    1: [
        ("Lucy Milligan", None,
         "Welcome back to World Stories. I'm Lucy Milligan, and today we're talking about the terrible floods in Nepal. "
         "I'm joined by Emma McKinley, a British aid worker who has been helping in the affected areas since the very first day. "
         "Emma, thank you so much for coming in. Could you tell us what happened on the 26th of August?"),
        ("Emma McKinley", "softly",
         "Thank you, Lucy. It was a morning nobody in that region will ever forget. I was working in a district called Nuwakot — "
         "that's N-U-W-A-K-O-T. At first, everything was completely quiet and normal. People were having breakfast, and children were "
         "getting ready for school. The sky was clear and blue, and the river was calm. Then, just before ten thirty, we heard this "
         "enormous, deep noise. It sounded a bit like thunder, but there wasn't a single cloud in the sky. We all stopped and looked "
         "at each other, and nobody knew what it was."),
        ("Lucy Milligan", None, "And then what happened?"),
        ("Emma McKinley", None,
         "Then the water came. And I must be clear — it wasn't a normal flood. A normal flood rises slowly, and you have time to move "
         "to higher ground. This was different. It was more like a wall — a solid wall of water, mud, rocks and broken ice, all mixed "
         "together, moving incredibly fast down the valley. It swept everything out of its path in seconds. There was no time to run, "
         "and no time to warn anybody. One minute there was a village, and the next there was just mud and water."),
        ("Lucy Milligan", None, "You mentioned broken ice. Where did that come from?"),
        ("Emma McKinley", None,
         "Later, we learned that part of a glacier had collapsed. A glacier is a huge, slow-moving river of ice that forms high up on the "
         "mountains. This one was on a peak called Langtang Lirung — that's L-A-N-G-T-A-N-G for Langtang, and L-I-R-U-N-G for Lirung. "
         "It sits right on the border with China. When that ice broke away from the mountain, it rushed down the slopes, picked up rocks "
         "and mud on the way, and poured into the Trishuli river — T-R-I-S-H-U-L-I. The water kept travelling for about a hundred "
         "kilometres before it finally slowed down."),
        ("Lucy Milligan", None,
         "So one moment everything was calm, and the next there was a wall of water racing down the river."),
        ("Emma McKinley", None,
         "Exactly. And it moved with incredible speed — for the first twenty-two kilometres, it was travelling at about one hundred and "
         "ninety kilometres an hour. That's faster than a car driving on a motorway. And that is why there was almost nothing anyone could "
         "do. The whole thing — from the mountains to the villages — happened in a matter of minutes."),
    ],
    2: [
        ("Lucy Milligan", None,
         "So what actually caused the glacier to collapse? At first, a lot of people said it was an earthquake, didn't they?"),
        ("Emma McKinley", None,
         "Yes, they did, and it's very easy to see why. When the glacier collapsed and fell, the US Geological Survey recorded it as a "
         "small tremor — about four point four on the Richter scale. So for a day or two, many people believed there had been an earthquake, "
         "and that the earthquake had caused a landslide. That was a very reasonable thing to think, because that kind of massive movement "
         "creates vibrations, and those vibrations are exactly what the instruments pick up."),
        ("Lucy Milligan", None, "But the truth was different, wasn't it?"),
        ("Emma McKinley", None,
         "Yes, it was. After scientists studied the satellite images and went to look at the area itself, they realised the real cause. "
         "It was a glacial collapse. A very large piece of the ice and rock on top of the mountain broke off and fell. It wasn't an "
         "earthquake at all — the earthquake reading we got was the result of the collapse, not the cause of it."),
        ("Lucy Milligan", None, "And why does this happen? Why now, this year?"),
        ("Emma McKinley", None,
         "The main reason is climate change. Our planet is getting warmer, so the glaciers high up in the Himalayas are melting. As they "
         "melt, they get weaker, thinner and more fragile. Sometimes a big piece will break away all at once, without any warning at all. "
         "That is exactly what happened here. It isn't really one sudden event — it's the result of years and years of slow, steady warming."),
        ("Lucy Milligan", None,
         "But surely scientists could see this coming and warn people in advance?"),
        ("Emma McKinley", None,
         "Not really, and that's the terrible, frustrating problem. The Himalayas are enormous, and many of these glaciers are in very "
         "remote places. The weather on that particular day was calm and clear. Scientists know that thousands of glaciers are melting and "
         "getting weaker, but they cannot say which one will be the next to break, or exactly when it will happen. There are too many "
         "mountains, and they change so very slowly — until, suddenly, they change all at once."),
    ],
    3: [
        ("Lucy Milligan", None,
         "And the effects, Emma, were absolutely devastating, weren't they?"),
        ("Emma McKinley", "softly",
         "Yes, they were. Completely devastating. In the first week, more than a thousand people had lost their lives, and thousands more "
         "were still missing. A very sad fact is that many of those who died were women and children. In total, around sixty-five thousand "
         "people were affected by the floods and the mud. That is roughly the same as a small city — suddenly left with nothing, and no idea "
         "what to do next."),
        ("Lucy Milligan", None,
         "That's almost impossible to imagine. And what about the damage to the area itself — to the buildings and the infrastructure?"),
        ("Emma McKinley", None,
         "The flood swept away practically everything in its path. Hundreds of homes were destroyed, along with roads and bridges, so many "
         "whole villages became cut off from the rest of the country. Nineteen schools were destroyed, which means around ten thousand "
         "children lost their classrooms overnight. It also blocked the tunnels of hydroelectric power stations — those are big plants that "
         "use the power of the rivers to make electricity — leaving large parts of the country without power."),
        ("Lucy Milligan", None, "And it wasn't just the villages, was it?"),
        ("Emma McKinley", None,
         "No, not at all. In fact, it destroyed the town of Gyirong — G-Y-I-R-O-N-G — which is a major port and a very important trade "
         "crossing on the border with China. So a key route between the two countries, used by lorries and travellers every day, was simply "
         "wiped out. The total cost of the damage is now thought to be over two hundred billion rupees, which is more than a billion US "
         "dollars. And sadly, I expect that figure will only rise as the rescue continues."),
    ],
    4: [
        ("Lucy Milligan", None,
         "So, given all of that, what is happening now? And is the danger finally over?"),
        ("Emma McKinley", None,
         "I'm afraid the answer is no. Right now, rescue teams are still working as hard as they can to reach people, and there is still a "
         "very serious risk. In one place, for example, two hundred and seventy-nine workers were trapped inside the tunnels of a hydropower "
         "plant, and rescuers had to bring them out one by one, which took a long time. But, to be honest, the biggest worry of all is a new "
         "lake that has formed."),
        ("Lucy Milligan", None, "A new lake? That sounds strange. Where did that come from?"),
        ("Emma McKinley", None,
         "When the glacier collapsed, it left huge amounts of rock, ice and debris blocking the river upstream. That material has created what "
         "we call a barrier lake — really, a natural dam across the river. That lake is still growing, and water is building up behind it day by "
         "day. If that dam of rock and ice breaks, it would send another wall of water down the valley, exactly like before, and it would hit "
         "many of the same villages again. So the danger is definitely not over."),
        ("Lucy Milligan", None,
         "That's frightening. And this risk of flooding — it isn't only in Nepal, is it? I understand many places in Asia face the same danger."),
        ("Emma McKinley", None,
         "That's exactly right, and I think it's the most important point of all. Nepal is not alone. As the planet gets warmer, the risk of "
         "heavy rain and terrible flooding is growing right across Asia. And one of the countries facing a very serious danger is Thailand. "
         "In fact, Thailand is one of the most flood-affected countries in the world. Its coast is very long, and a huge part of Bangkok — "
         "the capital city — sits on very low, flat land, not far above the sea. So when the water comes, there is very little space for it to go."),
        ("Lucy Milligan", None, "And has Thailand already suffered from bad floods?"),
        ("Emma McKinley", None,
         "Yes, sadly. In 2011, there was a terrible flood there. More than eight hundred people lost their lives, and over thirteen million "
         "people were affected. Large parts of the country, including thousands of factories, were covered in water for weeks. And scientists "
         "warn that as the climate changes, these floods will only get worse — there will be more of them, they will be stronger, and they will "
         "happen more often. Some experts believe the number of people affected by flooding in Thailand could double by 2030. So we are not just "
         "talking about one sad event in Nepal. We are talking about a problem that will touch millions of lives across Asia."),
        ("Lucy Milligan", None, "So this is really a climate story, not only a Nepal story."),
        ("Emma McKinley", None,
         "Exactly. And here is the sad truth. Countries like Nepal and Thailand have caused very little of this problem, yet they are among the "
         "first to feel it. They do not have the money, or the strong buildings, to protect themselves. That is why we all need to act — not only "
         "to help them recover, but to stop the planet getting any warmer. If we don't, events like this will happen again and again."),
    ],
}

# --- helpers --------------------------------------------------------------
def tts(text, voice_id, out_path, retries=4):
    payload = json.dumps({
        "text": text,
        "reference_id": voice_id,
        "format": "mp3",
        "mp3_bitrate": 128,
        "latency": "normal",
    })
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(1, retries + 1):
        try:
            r = requests.post(
                "https://api.fish.audio/v1/tts",
                headers={"Authorization": f"Bearer {API_KEY}",
                         "Content-Type": "application/json",
                         "model": "s2.1-pro-free"},
                data=payload, timeout=90, stream=True,
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


def duration(path):
    path = Path(path)
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


def make_silence(dur, name, sr=44100):
    p = OUT / name
    subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i",
                    f"anullsrc=r={sr}:cl=mono", "-t", f"{dur:.2f}",
                    "-c:a", "libmp3lame", "-b:a", "128k", str(p)],
                   capture_output=True, check=True)
    return p


# --- generate interview line files per chunk via skill generator ---------
import re


def clean_line_text(text):
    text = text.strip()
    text = re.sub(r"\([^)]*\)", "", text)
    text = text.replace("...", "\u2014").replace("..", "\u2014")
    return text


def generate_chunk_lines(chunk_num, turns):
    """Generate per-line MP3s for a chunk using Fish TTS directly."""
    chunk_dir = OUT / f"chunk{chunk_num}"
    lines_dir = chunk_dir / "lines"
    lines_dir.mkdir(parents=True, exist_ok=True)

    first = {}
    for i, (char, sd, line) in enumerate(turns):
        # light steering: soft tone for emotional beats
        tag = ""
        if sd and "soft" in sd.lower():
            tag = "[soft tone]"
        elif sd and "long pause" in sd.lower():
            tag = "[calm]"
        elif sd and "interrupt" in sd.lower():
            tag = "[in a hurry tone]"
        text_with_tag = f"{tag} {clean_line_text(line)}".strip()
        lp = lines_dir / f"line_{i:03d}.mp3"
        print(f"  chunk{chunk_num} [{i+1}/{len(turns)}] {char[:14]}...", end=" ")
        ok = tts(text_with_tag, VOICES[char], lp)
        print("OK" if ok else "FAILED")
    return lines_dir, len(turns)


def stitch_chunk(chunk_num, turns, lines_dir, total):
    """Custom stitch with context-aware gaps (44100 mono silence) + re-encode."""
    sil300 = make_silence(0.30, f"c{chunk_num}_s300.mp3")
    sil150 = make_silence(0.15, f"c{chunk_num}_s150.mp3")
    sil500 = make_silence(0.50, f"c{chunk_num}_s500.mp3")

    entries = []
    for i, (char, sd, line) in enumerate(turns):
        entries.append(("file", lines_dir / f"line_{i:03d}.mp3"))
        if i < total - 1:
            nxt_char = turns[i + 1][0]
            sd_lower = (sd or "").lower()
            if "long pause" in sd_lower or "pause" in sd_lower:
                gap = sil500
            elif nxt_char != char:
                gap = sil300
            else:
                gap = sil150
            entries.append(("file", gap))

    concat_txt = OUT / f"chunk{chunk_num}_concat.txt"
    with open(concat_txt, "w") as f:
        for kind, p in entries:
            f.write(f"file '{p.resolve()}'\n")
    out = OUT / f"interview_chunk{chunk_num}.mp3"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_txt),
         "-ar", "44100", "-ac", "1", "-b:a", "128k", str(out)],
        check=True, capture_output=True)
    return out


# --- announce generation --------------------------------------------------
ANNOUNCE_TEXTS = {
    "chunk1": "Chunk one.",
    "chunk2": "Chunk two.",
    "chunk3": "Chunk three.",
    "chunk4": "Chunk four.",
    "again": "Now listen again.",
}


def generate_announcements():
    ann_dir = OUT / "announce"
    ann_dir.mkdir(parents=True, exist_ok=True)
    files = {}
    for key, text in ANNOUNCE_TEXTS.items():
        p = ann_dir / f"{key}.mp3"
        if not p.exists():
            print(f"  announce {key} ...", end=" ")
            ok = tts(text, BENEDICT_ID, p)
            print("OK" if ok else "FAILED")
        files[key] = p
    return files


# --- assemble master ------------------------------------------------------
def assemble_master(chunk_files, ann, lead_in=0.5, lead_out=0.7):
    entries = []
    entries.append(("file", make_silence(lead_in, "m_lead.mp3")))
    for i in range(1, 5):
        entries.append(("file", ann[f"chunk{i}"]))
        entries.append(("file", make_silence(0.9, f"m_afterchunk{i}.mp3")))
        # first play
        entries.append(("file", chunk_files[i - 1]))
        entries.append(("file", make_silence(0.6, f"m_pretul{i}.mp3")))
        # now listen again
        entries.append(("file", ann["again"]))
        entries.append(("file", make_silence(0.9, f"m_afteragain{i}.mp3")))
        # second play
        entries.append(("file", chunk_files[i - 1]))
        if i < 4:
            entries.append(("file", make_silence(1.3, f"m_sep{i}.mp3")))
    entries.append(("file", make_silence(lead_out, "m_out.mp3")))

    # track section boundaries: section N = start of chunkN announce -> start of chunkN+1 announce
    # Recompute a timeline by measuring durations as we go.
    boundaries = {}  # chunk index -> start time (seconds)
    running = 0.0
    # We'll iterate and, when we hit an announce->file for chunkN first time, record running
    # Build list of (type, payload, is_chunkN_announce)
    seq = []
    chunk_seen = {}
    for idx, (kind, p) in enumerate(entries):
        is_chunk_ann = False
        for i in range(1, 5):
            if p == ann[f"chunk{i}"] and i not in chunk_seen:
                chunk_seen[i] = True
                is_chunk_ann = True
                boundaries[i] = running
        seq.append((kind, p, is_chunk_ann))
        running += duration(p)

    concat_txt = OUT / "master_concat.txt"
    with open(concat_txt, "w") as f:
        for kind, p, _ in seq:
            f.write(f"file '{p.resolve()}'\n")
    master = OUT / "interview-master.mp3"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_txt),
         "-ar", "44100", "-ac", "1", "-b:a", "128k", str(master)],
        check=True, capture_output=True)
    return master, boundaries


def slice_sections(master, boundaries):
    """Slice master at recorded boundary times -> section1..4.mp3."""
    total = duration(master)
    order = sorted(boundaries.items())  # [(1,start1),(2,start2),...]
    sections = []
    for idx, (chunk_i, start) in enumerate(order):
        end = order[idx + 1][1] if idx + 1 < len(order) else total
        sec_len = end - start
        out = OUT / f"section{chunk_i}.mp3"
        subprocess.run(
            ["ffmpeg", "-y", "-ss", f"{start:.3f}", "-i", str(master),
             "-t", f"{sec_len:.3f}", "-ar", "44100", "-ac", "1", "-b:a", "128k",
             str(out)],
            check=True, capture_output=True)
        sections.append((chunk_i, out, start, end))
    return sections


# --- main -----------------------------------------------------------------
def main():
    # 1. interview chunks
    chunk_files = []
    for num in sorted(CHUNKS):
        turns = CHUNKS[num]
        print(f"Generating chunk {num} ({len(turns)} turns)...")
        lines_dir, total = generate_chunk_lines(num, turns)
        out = stitch_chunk(num, turns, lines_dir, total)
        chunk_files.append(out)
        print(f"  -> {out} ({duration(out):.1f}s)")

    # 2. announcements
    print("Generating Benedict announcements...")
    ann = generate_announcements()

    # 3. assemble master
    print("Assembling master...")
    master, boundaries = assemble_master(chunk_files, ann)

    # 4. slice
    print("Slicing into 4 sections...")
    sections = slice_sections(master, boundaries)

    print("\n=== DONE ===")
    print(f"Master: {master}  ({duration(master):.1f}s)")
    for chunk_i, p, s, e in sections:
        print(f"  section{chunk_i}: {p}  ({s:.1f}s -> {e:.1f}s, {e-s:.1f}s)")


if __name__ == "__main__":
    main()
