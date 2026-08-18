"""generate_worksheet.py — Cat's in the Cradle & Leigh Ryswyk listening worksheet (M3, CEFR B2).

Shape E (Receptive Skills) listening lesson built around:
  - Entry ticket: "Cat's in the Cradle" (Harry Chapin) lyric gap-fill.
    Verses 2-4 are gapped (every 10th word); the first chorus is shown,
    later choruses are marked [chorus] so students are not over-assisted.
  - Main lesson: BTN report on Leigh Ryswyk, Australia's first openly gay
    AFL player (gist, details, true/false-correct, discussion).

The answer key is printed on its own final page.
"""

import re as _re
import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".kilo" / "skills" / "write-test-worksheet" / "scripts"))
from render import render_worksheet

GAP = '<span style="display:inline-block;border-bottom:1.5pt solid #222;min-width:6em">&nbsp;</span>'
TF = '<span class="label-box"></span>'
CORR_LINE = ('<span style="display:block;border-bottom:1.5pt solid #222;'
             'height:1.5em;margin:0.2em 0 0.4em 0;width:100%">&nbsp;</span>')

# ── Cat's in the Cradle — verses 2-4 (the sheet starts at verse 2) ────────
V2 = [
    "My son turned ten just the other day",
    "He said, \"Thanks for the ball, Dad, come on let's play",
    'Can you teach me to throw?" I said, "Not today"',
    'I got a lot to do." He said, "That\'s okay"',
    "And he walked away but his smile never dimmed",
    'It said, "I\'m gonna be like him, yeah',
    'You know I\'m gonna be like him"',
]
V3 = [
    "Well, he came from college just the other day",
    "So much like a man I just had to say",
    '"Son, I\'m proud of you, can you sit for a while?"',
    "He shook his head and he said with a smile",
    '"What I\'d really like, Dad, is to borrow the car keys',
    'See you later, can I have them please?"',
]
V4 = [
    "I've long since retired, my son's moved away",
    "I called him up just the other day",
    'I said, "I\'d like to see you if you don\'t mind"',
    'He said, "I\'d love to, Dad, if I can find the time"',
    "You see my new job's a hassle and the kids have the flu",
    "But it's sure nice talking to you, Dad",
    'It\'s been sure nice talking to you"',
    "And as I hung up the phone it occurred to me",
    "He'd grown up just like me",
    "My boy was just like me",
]
CHORUS = [
    "And the cats in the cradle and the silver spoon",
    "Little boy blue and the man on the moon",
    '"When you comin\' home, Dad?"',
    '"I don\'t know when, but we\'ll get together then',
    'You know we\'ll have a good time then"',
]

_TOKEN_RE = _re.compile(r'^([\'"(\[]*)(.*?)([.,!?;:\'")\]]*)$')


def _gap_line(word: str) -> str:
    m = _TOKEN_RE.match(word)
    lead, core, trail = m.groups() if m else ("", word, "")
    return lead + GAP + trail


def _gapfill(lines: list[str], every: int = 10) -> tuple[str, list[str]]:
    """Remove every Nth word. Returns (html, [gap words in order])."""
    rows, gaps = [], []
    idx = 0
    for line in lines:
        parts = line.split(" ")
        seg = []
        for word in parts:
            idx += 1
            if idx % every == 0:
                m = _TOKEN_RE.match(word)
                gaps.append(m.group(2) if m else word)
                seg.append(_gap_line(word))
            else:
                seg.append(word)
        rows.append(" ".join(seg))
    return "<br>".join(rows), gaps


def _gapfill_continuous(verse_lines: list[list[str]], every: int = 10):
    """Remove every Nth word counting continuously across all verse lines.
    Returns (rows_html, [gap words in order])."""
    rows, gaps = [], []
    idx = 0
    for lines in verse_lines:
        for line in lines:
            parts = line.split(" ")
            seg = []
            for word in parts:
                idx += 1
                if idx % every == 0:
                    m = _TOKEN_RE.match(word)
                    gaps.append(m.group(2) if m else word)
                    seg.append(_gap_line(word))
                else:
                    seg.append(word)
            rows.append(" ".join(seg))
    return rows, gaps


ALL_ROWS, LYRICS_GAP_ANSWERS = _gapfill_continuous([V2, CHORUS, V3, V4])
V2_HTML = "<br>".join(ALL_ROWS[: len(V2)])
CHORUS_HTML = "<br>".join(ALL_ROWS[len(V2): len(V2) + len(CHORUS)])
V3_HTML = "<br>".join(ALL_ROWS[len(V2) + len(CHORUS): len(V2) + len(CHORUS) + len(V3)])
V4_HTML = "<br>".join(ALL_ROWS[len(V2) + len(CHORUS) + len(V3):])

CHORUS_NOTE = '<div style="text-align:center;margin:0.5em 0;font-style:italic;color:#444">[chorus]</div>'

GAPFILL_HTML = (
    f'<div style="font-size:13pt"><strong>2.</strong> {V2_HTML}</div>'
    f'<div style="font-size:13pt;font-style:italic;margin:0.6em 0 0.4em 0;border-top:1pt solid #bbb;border-bottom:1pt solid #bbb;padding:0.4em 0">'
    f"<strong>Chorus</strong><br>{CHORUS_HTML}</div>"
    f'<div style="font-size:13pt"><strong>3.</strong> {V3_HTML}</div>'
    f"{CHORUS_NOTE}"
    f'<div style="font-size:13pt"><strong>4.</strong> {V4_HTML}</div>'
    f"{CHORUS_NOTE}"
)

content = {
    "title": "Cat's in the Cradle & Leigh Ryswyk — Listening",
    "cefr_tag": "M3 · CEFR B2 · Listening · Discussion",
    "sections": [
        {"type": "heading", "text": "Entry Ticket — Cat's in the Cradle"},
        {
            "type": "instructions",
            "text": "This song tells a story: a father and his son. "
                    "We will listen to it <strong>twice</strong>. "
                    "Listen 1 — just enjoy it. Listen 2 — complete the gaps.",
        },
        {
            "type": "image",
            "src": "PROJECTS/M3 LISTENING/assets/CHAPIN.jpg",
            "alt": "Harry Chapin",
        },
        {"type": "writing_prompt", "text": GAPFILL_HTML},
        {"type": "highlight_bar", "text": "Main Lesson — Leigh Ryswyk"},
        {
            "type": "instructions",
            "text": "We will listen to the video <strong>twice</strong>. "
                    "Listen 1 — just listen. Listen 2 — answer the questions.",
        },
        {"type": "heading", "text": "First Listen — The Big Idea"},
        {"type": "instructions", "text": "Listen once. Tick the main idea of the video."},
        {
            "type": "mcq",
            "items": [
                {
                    "num": 1,
                    "prompt": "The video is mainly about…",
                    "options": [
                        "A. how to become a professional AFL player",
                        "B. the first openly gay AFL player and his decision to come out",
                        "C. how Australian rules football began",
                        "D. famous AFL players from the past",
                    ],
                }
            ],
        },
        {"type": "heading", "text": "Second Listen — Answer the Questions"},
        {
            "type": "instructions",
            "text": "Listen again. Write short answers to the questions "
                    "in your own words.",
        },
        {
            "type": "join_item",
            "items": [
                {
                    "num": 1,
                    "text": "Why was playing for the opposition a turning point for Leigh?",
                    "lines": 2,
                },
                {
                    "num": 2,
                    "text": "Why did Leigh decide to come out publicly, even though he did not want to be the first?",
                    "lines": 2,
                },
                {
                    "num": 3,
                    "text": "What does \"taking the armour off\" tell you about how Leigh felt before he came out?",
                    "lines": 2,
                },
                {
                    "num": 4,
                    "text": "Why does Leigh say the unknown is so scary for young athletes?",
                    "lines": 2,
                },
                {
                    "num": 5,
                    "text": "What does Leigh say needs to change, not just in football but in sport in general?",
                    "lines": 2,
                },
                {
                    "num": 6,
                    "text": "What is Leigh's main message to young athletes who have not come out yet?",
                    "lines": 2,
                },
            ],
        },
        {"type": "heading", "text": "True or False — Correct the False Ones"},
        {
            "type": "instructions",
            "text": "Write <strong>T</strong> or <strong>F</strong> in the box. "
                    "If the sentence is false, correct it on the line.",
        },
        {
            "type": "task1_sentence",
            "items": [
                {"num": 1, "text": f"{TF} Leigh was born in Queensland. {CORR_LINE}"},
                {"num": 2, "text": f"{TF} Leigh was delisted by Brisbane. {CORR_LINE}"},
                {"num": 3, "text": f"{TF} Mitch Brown was the first openly gay player in the AFL. {CORR_LINE}"},
                {"num": 4, "text": f"{TF} Leigh says the media can make it more uncomfortable. {CORR_LINE}"},
                {"num": 5, "text": f"{TF} Leigh thinks athletes must come out publicly. {CORR_LINE}"},
            ],
        },
        {"type": "heading", "text": "Discuss — Should Athletes Have to Come Out Publicly?"},
        {
            "type": "instructions",
            "text": "In a group: give your opinion, agree or disagree, and reach a conclusion. "
                    "Plan first with the outline below.",
        },
        {
            "type": "writing_prompt",
            "text": (
                '<div style="text-align:center;margin:0.4em 0 0.2em 0">'
                "<strong>My opinion:</strong> "
                '<span style="display:inline-block;border-bottom:1.5pt solid #222;min-width:18em">&nbsp;</span></div>'
                '<div style="margin:0.25em 0 0 1.5em"><strong>Idea 1:</strong> '
                '<span style="display:inline-block;border-bottom:1.5pt solid #222;min-width:16em">&nbsp;</span></div>'
                '<div style="margin:0.25em 0 0 1.5em"><strong>Idea 2:</strong> '
                '<span style="display:inline-block;border-bottom:1.5pt solid #222;min-width:16em">&nbsp;</span></div>'
                '<div style="margin:0.25em 0 0 1.5em"><strong>Idea 3:</strong> '
                '<span style="display:inline-block;border-bottom:1.5pt solid #222;min-width:16em">&nbsp;</span></div>'
                '<div style="margin:0.4em 0 0 0"><strong>Our conclusion:</strong> '
                '<span style="display:inline-block;border-bottom:1.5pt solid #222;min-width:16em">&nbsp;</span></div>'
            ),
        },
        {
            "type": "writing_prompt",
            "text": (
                "<strong>Discussion language:</strong>"
                '<table style="width:100%;border-collapse:collapse;margin-top:0.3em">'
                '<tr><th style="text-align:left;padding:0.1em 0.4em;border-bottom:1pt solid #222">Give your opinion</th>'
                '<td style="padding:0.1em 0.4em;border-bottom:1pt solid #999">I think… / In my opinion… / I believe that…</td></tr>'
                '<tr><th style="text-align:left;padding:0.1em 0.4em;border-bottom:1pt solid #222">Agree</th>'
                '<td style="padding:0.1em 0.4em;border-bottom:1pt solid #999">I agree with you because… / That\'s a good point.</td></tr>'
                '<tr><th style="text-align:left;padding:0.1em 0.4em;border-bottom:1pt solid #222">Disagree</th>'
                '<td style="padding:0.1em 0.4em;border-bottom:1pt solid #999">I disagree because… / I see what you mean, but…</td></tr>'
                '<tr><th style="text-align:left;padding:0.1em 0.4em">Reach a conclusion</th>'
                '<td style="padding:0.1em 0.4em">So we agree that… / In conclusion, we think…</td></tr>'
                "</table>"
            ),
        },
        {"type": "page_break"},
        {"type": "heading", "text": "Answer Key"},
        {"type": "heading", "text": "Entry Ticket — Cat's in the Cradle"},
        {
            "type": "gap_sentence",
            "items": [
                {
                    "num": 1,
                    "text": "Gap-fill answers (verses 2-4 and the first chorus, every 10th word): "
                            f"<strong>{', '.join(LYRICS_GAP_ANSWERS)}</strong>.",
                }
            ],
        },
        {"type": "heading", "text": "Main Lesson — Leigh Ryswyk"},
        {
            "type": "gap_sentence",
            "items": [
                {"num": 1, "text": "Gist: <strong>B</strong> — The first openly gay AFL player and his decision to come out."},
                {
                    "num": 2,
                    "text": "1. It was a turning point because he realised he could play well — he was best on ground for the opposition.",
                },
                {
                    "num": 3,
                    "text": "2. He wanted to take the pressure off other people who were afraid — someone had to be the first.",
                },
                {
                    "num": 4,
                    "text": "3. It suggests he was hiding a heavy weight and could finally be himself after coming out.",
                },
                {
                    "num": 5,
                    "text": "4. No active AFL player has done it, so they do not know what to expect — the unknown is scary, and the media and fans add pressure.",
                },
                {
                    "num": 6,
                    "text": "5. Consistent, year-round education about inclusion — not just one pride round once a year — built into workplaces and society.",
                },
                {
                    "num": 7,
                    "text": "6. If you can be yourself, you can still achieve anything; coming out is a personal choice and is not required.",
                },
                {"num": 8, "text": "True or False: 1. <strong>False</strong> — born in Victoria, moved to Queensland at six."},
                {"num": 9, "text": "2. <strong>True</strong>. 3. <strong>False</strong> — he was the first bi man, not the first gay man."},
                {"num": 10, "text": "4. <strong>True</strong>. 5. <strong>False</strong> — it is a personal choice."},
            ],
        },
    ],
}

render_worksheet(content, Path("PROJECTS/M3 LISTENING/Cats-Cradle-Leigh-Ryswyk-Listening-Worksheet.pdf"))
print("Worksheet generated")
print("Lyric gap answers:", ", ".join(LYRICS_GAP_ANSWERS))
