"""generate_worksheet.py — Smart Glasses listening & discussion worksheet (M2, CEFR B1).

Shape E (Receptive Skills) listening lesson built around the BTN video
"Meta Smart Glasses" (https://www.youtube.com/watch?v=I1BzGOfh4L0).

Structure:
  A. First listen — gist (multiple choice)
  B. Second listen — details (gap sentences)
  C. Second listen — true/false, correct the false ones
  D. Discussion — plan (linear outline) + language support, reach a conclusion

No vocabulary glossing — words are pre-taught in class.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".kilo" / "skills" / "write-test-worksheet" / "scripts"))
from render import render_worksheet

BLANK = '<span style="display:inline-block;border-bottom:1.5pt solid #222;min-width:8em">&nbsp;</span>'
GAP = '<span style="display:inline-block;border-bottom:1.5pt solid #222;min-width:6em">&nbsp;</span>'
TF = '<span class="label-box"></span>'
CORR_LINE = ('<span style="display:block;border-bottom:1.5pt solid #222;'
             'height:1.5em;margin:0.2em 0 0.4em 0;width:100%">&nbsp;</span>')

# Tom's Diner — 5 unique verses only (hums and the repeated final verse excluded).
# Systematic cloze: every 10th word is removed, uniformly spaced through the text.
# Leading/trailing punctuation is preserved around each gap.
import re as _re

LYRIC_LINES = [
    "I am sitting in the morning at the diner on the corner.",
    "I am waiting at the counter for the man to pour the coffee.",
    "And he fills it only halfway, and before I even argue.",
    "He is looking out the window at somebody coming in.",
    '"It is always nice to see you," says the man behind the counter.',
    "To the woman who has come in, she is shaking her umbrella.",
    "And I look the other way as they are kissing their hellos.",
    "And I'm pretending not to see them, and instead I pour the milk.",
    "I open up the paper, there's a story of an actor.",
    "Who had died while he was drinking, it was no one I had heard of.",
    "And I'm turning to the horoscope and looking for the funnies.",
    "When I'm feeling someone watching me, and so I raise my head.",
    "There's a woman on the outside looking inside, does she see me?",
    "No, she does not really see me 'cause she sees her own reflection.",
    "And I'm trying not to notice that she's hitching up her skirt.",
    "And while she's straightening her stockings, her hair has gotten wet.",
    "Oh, this rain, it will continue through the morning as I'm listening.",
    "To the bells of the cathedral, I am thinking of your voice.",
    "And of the midnight picnic once upon a time before the rain began.",
    "And I finish up my coffee, and it's time to catch the train.",
]

_TOKEN_RE = _re.compile(r'^([\'"(\[]*)(.*?)([.,!?;:\'")\]]*)$')


def _build_gapfill(lines, every=10):
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
                lead, core, trail = m.groups() if m else ("", word, "")
                gaps.append(core)
                seg.append(lead + GAP + trail)
            else:
                seg.append(word)
        rows.append(" ".join(seg))
    return "<br>".join(rows), gaps


LYRICS_GAPFILL, LYRICS_GAP_ANSWERS = _build_gapfill(LYRIC_LINES)

content = {
    "title": "Meta Smart Glasses — Listening & Discussion",
    "cefr_tag": "M2 · CEFR B1 · Two listens · Discussion",
    "sections": [
        {"type": "heading", "text": "Entry Ticket — Tom's Diner"},
        {
            "type": "instructions",
            "text": "This song is a story. A woman sits in a diner and watches the "
                    "world go by. We will listen to it <strong>twice</strong>.",
        },
        {
            "type": "instructions",
            "text": "First listen — just enjoy the song. Don't write anything. "
                    "Second listen — complete the gaps with the words you hear.",
        },
        {
            "type": "image",
            "src": "PROJECTS/M2 LISTENING/assets/suzanne_vega.jpg",
            "alt": "Suzanne Vega",
        },
        {
            "type": "writing_prompt",
            "text": LYRICS_GAPFILL,
        },
        {"type": "highlight_bar", "text": "Main Lesson — Meta Smart Glasses"},
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
                        "A. where to buy smart glasses",
                        "B. what smart glasses can do and why some people worry about them",
                        "C. how smart glasses are made",
                        "D. why smart glasses are expensive",
                    ],
                }
            ],
        },
        {"type": "heading", "text": "Second Listen — Details"},
        {"type": "instructions", "text": "Listen again and complete the sentences."},
        {
            "type": "gap_sentence",
            "items": [
                {"num": 1, "text": f"Smart glasses have been around since the early {BLANK}."},
                {"num": 2, "text": f"Ray-Ban and Meta worked together in {BLANK}."},
                {"num": 3, "text": f"The Kmart version costs {BLANK} and sold out last week."},
                {"num": 4, "text": f"The glasses can respond to voice commands, play music, and make {BLANK}."},
                {"num": 5, "text": f"Some glasses use AI to translate foreign {BLANK} instantly."},
                {"num": 6, "text": f"Filming in a bathroom, changeroom, or {BLANK} is illegal."},
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
                {"num": 1, "text": f"{TF} Smart glasses first appeared in 2021. {CORR_LINE}"},
                {"num": 2, "text": f"{TF} The Kmart glasses sold out last week. {CORR_LINE}"},
                {"num": 3, "text": f"{TF} In Australia, filming people in public places is usually allowed. {CORR_LINE}"},
                {"num": 4, "text": f"{TF} You must ask permission before filming on private property. {CORR_LINE}"},
                {"num": 5, "text": f"{TF} Filming someone without their knowledge is always against the law. {CORR_LINE}"},
            ],
        },
        {"type": "heading", "text": "Discuss — Should Smart Glasses Be Banned?"},
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
    ],
}

render_worksheet(content, Path("PROJECTS/M2 LISTENING/Smart-Glasses-Listening-Discussion-Worksheet.pdf"))
print("Worksheet generated")
print("Lyric gap answers:", ", ".join(LYRICS_GAP_ANSWERS))
