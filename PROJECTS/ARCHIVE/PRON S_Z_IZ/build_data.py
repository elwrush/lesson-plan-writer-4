#!/usr/bin/env python3
"""Build data.json for the Plural -s (/s/ /z/ /ɪz/) pronunciation-noticing deck (Shape L).

All slide text is authored verbatim below — no sentence is composed from fragments.
This script only wires structure (layout, id, colours, table markup) and dumps JSON.
"""
import json
from pathlib import Path

OUT = Path(__file__).parent / "data.json"

SPLASH = "assets/splash.jpg"
NAVY = "#1a1a2e"
RED = "#c0392b"
GREEN = "#052e0d"
TEAL = "#116466"


def ol(label, text):
    """Answer-table row with a yellow label cell."""
    return (
        f'<tr><td style="padding:8px 12px 8px 0;border-bottom:1px solid #444;'
        f'font-weight:700;color:#ffdd00;white-space:nowrap;vertical-align:top">{label}</td>'
        f'<td style="padding:8px 0;border-bottom:1px solid #444">{text}</td></tr>'
    )


def answer_table(question, answer, explanation, transcript):
    return (
        '<table style="width:100%;border-collapse:collapse">'
        + ol("Question", question) + ol("Answer", answer)
        + ol("Explanation", explanation) + ol("Transcript", transcript)
        + "</table>"
    )


# The condition (step 1) / value (step 2) text for the rule rows — one verbatim pair per row.
# auto-animate matches the value <span> between steps (identical DOM, only span content changes).
RULE_ROWS = [
    ("After a voiceless sound: /p/, /t/, /k/, /f/", "/s/ &mdash; books"),
    ("After a voiced sound: /b/, /d/, /g/, /v/, /l/, /m/, /n/", "/z/ &mdash; dogs"),
    ("After a hiss: /s/, /z/, /&#643;/, /t&#643;/", "/&#618;z/ &mdash; glasses"),
]
RULE_NOTE_V1 = "&nbsp;"
RULE_NOTE_V2 = "/&#618;z/ adds a syllable. Glass = 1. Glasses = 2."


def rule_table(step):
    rows = ""
    for cond, value in RULE_ROWS:
        shown = value if step == 2 else "&nbsp;"
        rows += (
            f'<tr><td style="padding:10px 12px 10px 0;border-bottom:1px solid #444;'
            f'font-size:34px;width:52%">{cond}</td>'
            f'<td style="padding:10px 12px 10px 0;border-bottom:1px solid #444;'
            f'font-size:34px">-s says</td>'
            f'<td style="padding:10px 0;border-bottom:1px solid #444;font-size:34px;'
            f'font-weight:700;color:#ffdd00"><span>{"&nbsp;" if shown == "&nbsp;" else shown}</span></td></tr>'
        )
    note = RULE_NOTE_V1 if step == 1 else RULE_NOTE_V2
    rows += (
        f'<tr><td colspan="3" style="padding:12px 0;font-size:34px;color:#ffffff">'
        f'<span>{note}</span></td></tr>'
    )
    return '<table style="width:100%;border-collapse:collapse">' + rows + "</table>"


# demo-notice model sentence, targets as spans (step1 hidden, step2 underlined)
DEF = "text-decoration:none"
UND = "text-decoration:underline;text-decoration-color:#ffdd00;text-decoration-thickness:3px;text-underline-offset:5px"


def demo_notice_body(style):
    return (
        '<table style="width:100%;border-collapse:collapse">'
        f'<tr><td colspan="2" style="padding:8px 0;border-bottom:1px solid #444">'
        f'I have three <span style="{style}">books</span>,'
        f' two <span style="{style}">dogs</span>,'
        f' and four <span style="{style}">glasses</span>.</td></tr>'
        f'<tr><td colspan="2" style="padding:8px 0;color:#ffdd00;border-bottom:1px solid #444">'
        + ("How many plural sounds?" if style == DEF else "Three. books /s/, dogs /z/, glasses /&#618;z/.")
        + "</td></tr></table>"
    )


slides = [
    {"layout": "image", "id": "splash", "step": 1, "image_url": SPLASH},

    {"layout": "content", "id": "title", "step": 1,
     "background_image": SPLASH, "logo": "assets/logo.png", "shield": True,
     "title": "Can you hear the -s?",
     "body": "Let's train your ears and your mouth."},

    {"layout": "content", "id": "importance", "step": 1, "background_color": NAVY,
     "title": "Why is this lesson important?",
     "body": "<ul><li>If you drop the -s, your listener can't tell one cat from many cats.</li><li>These three little sounds make your English clear.</li></ul>"},

    {"layout": "content", "id": "recall", "step": 1, "background_color": NAVY,
     "title": "What things do you have?",
     "body": "Tell your partner two things you own.<p style=\"color:#ffdd00;text-align:center;font-size:38px;font-weight:700;margin-top:22px\">Opinion &mdash; Reason &mdash; Evidence</p>",
     "notes": "Elicit 3-4 answers. Note how students say the plural endings. Do not correct yet."},

    {"layout": "content", "id": "transition-feature", "step": 1, "background_color": RED,
     "title": "Plural -s: /s/, /z/, /&#618;z/",
     "body": "The sounds at the end of plural words."},

    {"layout": "content", "id": "strategy-notice", "step": 1, "background_color": NAVY,
     "title": "Strategy: Notice",
     "body": "<table style=\"width:100%;border-collapse:collapse\"><tr><td style=\"padding:8px 12px 8px 0;border-bottom:1px solid #555;font-weight:700;color:#ffdd00;white-space:nowrap;vertical-align:top\">Do</td><td style=\"padding:8px 0;border-bottom:1px solid #555\">Listen for the last sound of each word.</td></tr><tr><td style=\"padding:8px 12px 8px 0;border-bottom:1px solid #555;font-weight:700;color:#ffdd00;white-space:nowrap;vertical-align:top\">Why</td><td style=\"padding:8px 0;border-bottom:1px solid #555\">Dropped -s hides one from many.</td></tr><tr><td style=\"padding:8px 12px 8px 0;font-weight:700;color:#ffdd00;white-space:nowrap;vertical-align:top\">How</td><td style=\"padding:8px 0\">Tap your finger on every plural /s/, /z/, /&#618;z/.</td></tr></table>"},

    {"layout": "auto-animate-pair", "id": "demo-notice", "step": 1, "background_color": TEAL,
     "title": "Try it: Notice", "body": demo_notice_body(DEF)},
    {"layout": "auto-animate-pair", "id": "demo-notice", "step": 2, "background_color": TEAL,
     "title": "Try it: Notice", "body": demo_notice_body(UND)},

    {"layout": "raw", "id": "listen-a", "step": 1, "background_color": NAVY,
     "body": "<p style=\"font-size:40px;margin:8px 0;color:#ffdd00;font-weight:700\">Worksheet, Part A</p><p style=\"font-size:38px;margin:8px 0\">Listen to two recordings. One is Thai English. One is Standard English.</p><p style=\"font-size:38px;margin:8px 0\">Can you hear the difference?</p><p style=\"font-size:36px;margin:16px 0;color:#ffdd00\">I have three books, two dogs, and four glasses.</p><p style=\"font-size:38px;margin:8px 0\">Tap on every plural sound you hear.</p><audio controls data-src=\"assets/model-sentence-compare.mp3\" style=\"width:440px;margin:20px\"></audio>",
     "notes": "The narrator labels Thai English then Standard English. Students tap the three plural words on the printed sentence."},

    {"layout": "content", "id": "answer-a", "step": 1, "background_color": GREEN,
     "title": "Answers: Part A",
     "body": answer_table("How many plural /s/, /z/, /&#618;z/ sounds does the model sentence have?",
                         "Three.",
                         "books /s/ &middot; dogs /z/ &middot; glasses /&#618;z/.",
                         "I have three books, two dogs, and four glasses.")},

    {"layout": "content", "id": "transition-b", "step": 1, "background_color": RED,
     "title": "Worksheet, Part B"},

    {"layout": "raw", "id": "listen-b", "step": 1, "background_color": NAVY,
     "body": "<p style=\"font-size:40px;margin:8px 0;color:#ffdd00;font-weight:700\">Worksheet, Part B</p><p style=\"font-size:38px;margin:8px 0\">You will hear each word twice.</p><p style=\"font-size:38px;margin:8px 0\">Write &#10003; if both have the plural.</p><p style=\"font-size:38px;margin:8px 0\">Write &#10007; if the second one drops it.</p><audio controls data-src=\"assets/partb-audio.mp3\" style=\"width:440px;margin:20px\"></audio>",
     "notes": "Helen announces each number. The second repetition in every pair drops the -s."},

    {"layout": "content", "id": "answer-b", "step": 1, "background_color": GREEN,
     "title": "Answers: Part B",
     "body": answer_table("Which pairs dropped the plural the second time?",
                         "1 &#10007; &middot; 2 &#10003; &middot; 3 &#10007; &middot; 4 &#10007; &middot; 5 &#10003;.",
                         "Books, glasses, and friends lost their plural. Dogs and years matched.",
                         "books/book &#10007; &middot; dogs/dog &#10003; &middot; glasses/glass &#10007; &middot; friends/friend &#10007; &middot; years/year &#10003;.")},

    {"layout": "content", "id": "transition-c", "step": 1, "background_color": RED,
     "title": "Worksheet, Part C"},

    {"layout": "raw", "id": "listen-c", "step": 1, "background_color": NAVY,
     "body": "<p style=\"font-size:40px;margin:8px 0;color:#ffdd00;font-weight:700\">Worksheet, Part C</p><p style=\"font-size:38px;margin:8px 0\">You will hear each word once.</p><p style=\"font-size:38px;margin:8px 0\">Write &#10003; if you hear the plural.</p><p style=\"font-size:38px;margin:8px 0\">Write &#10007; if it is missing.</p><audio controls data-src=\"assets/partc-audio.mp3\" style=\"width:440px;margin:20px\"></audio>",
     "notes": "Helen announces each number. Words 2, 5 and 7 are said as singulars."},

    {"layout": "content", "id": "answer-c", "step": 1, "background_color": GREEN,
     "title": "Answers: Part C",
     "body": answer_table("Which words kept their plural ending?",
                         "1 &#10003; &middot; 2 &#10007; &middot; 3 &#10003; &middot; 4 &#10003; &middot; 5 &#10007; &middot; 6 &#10003; &middot; 7 &#10007; &middot; 8 &#10003;.",
                         "Words 2, 5 and 7 were said as singulars: sibling, picture, book.",
                         "things &#10003; &middot; siblings &#10007; &middot; games &#10003; &middot; students &#10003; &middot; pictures &#10007; &middot; dinners &#10003; &middot; books &#10007; &middot; plants &#10003;.")},

    # The plural rule, presented with auto-animate.
    {"layout": "auto-animate-pair", "id": "feature-rules", "step": 1, "background_color": NAVY,
     "title": "The plural rule", "body": rule_table(1)},
    {"layout": "auto-animate-pair", "id": "feature-rules", "step": 2, "background_color": NAVY,
     "title": "The plural rule", "body": rule_table(2)},

    {"layout": "raw", "id": "feature-d", "step": 1, "background_color": NAVY,
     "body": "<p style=\"font-size:40px;margin:8px 0;color:#ffdd00;font-weight:700\">Worksheet, Part D &mdash; The Plural Pattern</p><p style=\"font-size:38px;margin:8px 0\">Clap the syllables. How many?</p><table style=\"width:100%;border-collapse:collapse;margin-top:16px\"><tr><td style=\"padding:10px 12px 10px 0;border-bottom:1px solid #444;font-size:38px;width:55%\">books</td><td class=\"fragment\" style=\"padding:10px 0;border-bottom:1px solid #444;font-size:38px;color:#ffdd00;font-weight:700\">1 syllable</td></tr><tr><td style=\"padding:10px 12px 10px 0;border-bottom:1px solid #444;font-size:38px\">dogs</td><td class=\"fragment\" style=\"padding:10px 0;border-bottom:1px solid #444;font-size:38px;color:#ffdd00;font-weight:700\">1 syllable</td></tr><tr><td style=\"padding:10px 12px 10px 0;border-bottom:1px solid #444;font-size:38px\">glasses</td><td class=\"fragment\" style=\"padding:10px 0;border-bottom:1px solid #444;font-size:38px;color:#ffdd00;font-weight:700\">2 syllables</td></tr><tr><td style=\"padding:10px 12px 10px 0;border-bottom:1px solid #444;font-size:38px\">friends</td><td class=\"fragment\" style=\"padding:10px 0;border-bottom:1px solid #444;font-size:38px;color:#ffdd00;font-weight:700\">1 syllable</td></tr><tr class=\"fragment\"><td colspan=\"2\" style=\"padding:12px 0;font-size:36px\">Drop the ending and the meaning is lost. Book is one. Books is many.</td></tr></table>"},

    {"layout": "content", "id": "transition-f", "step": 1, "background_color": RED,
     "title": "Worksheet, Part F"},

    {"layout": "content", "id": "game-f", "step": 1, "background_color": RED,
     "title": "Worksheet, Part F &mdash; Catch the Finals Game",
     "body": "<ul><li>Tell your partner two things you own.</li><li>They count every plural /s/, /z/, /&#618;z/.</li><li>One point per sound.</li></ul>",
     "notes": "5-minute timer. Speaker A first, swap after half the time. Dropped plural = do-over."},

    {"layout": "raw", "id": "listen-g", "step": 1, "background_color": NAVY,
     "body": "<p style=\"font-size:40px;margin:8px 0;color:#ffdd00;font-weight:700\">Worksheet, Part G</p><p style=\"font-size:38px;margin:8px 0\">Listen to Florence talk about her life.</p><p style=\"font-size:38px;margin:8px 0\">Tick or cross the numbered words.</p><audio controls data-src=\"assets/florence2.mp3\" style=\"width:440px;margin:20px\"></audio>",
     "notes": "Florence is a past student. The numbered words end with /s/, /z/ or /ɪz/. [0] is the example."},

    {"layout": "content", "id": "answer-g", "step": 1, "background_color": GREEN,
     "title": "Answers: Part G",
     "body": answer_table("Which plural endings did Florence say clearly?",
                         "[0] &#10003; &middot; [1] &#10003; &middot; [2] &#10007; &middot; [3] &#10003; &middot; [4] &#10003; &middot; [5] &#10007; &middot; [6] &#10007; &middot; [7] &#10003; &middot; [8] &#10003; &middot; [9] &#10007;.",
                         "News and books lost their -s. Grammar and plant gained an -s that does not belong.",
                         "[0] years &#10003; (example) &middot; [1] hours &#10003; &middot; [2] news &#10007; &middot; [3] things &#10003; &middot; [4] friends &#10003; &middot; [5] books &#10007; &middot; [6] grammar &#10007; &middot; [7] pictures &#10003; &middot; [8] books &#10003; &middot; [9] plant &#10007;.")},

    {"layout": "raw", "id": "listen-h", "step": 1, "background_color": NAVY,
     "body": "<p style=\"font-size:40px;margin:8px 0;color:#ffdd00;font-weight:700\">Worksheet, Part H</p><p style=\"font-size:38px;margin:8px 0\">This is the model. Listen first.</p><p style=\"font-size:38px;margin:8px 0\">Then read the paragraph to your partner.</p><audio controls data-src=\"assets/model-reading.mp3\" style=\"width:440px;margin:20px\"></audio>",
     "notes": "Student-facing text says 'the model', never the voice name. Pairs read and tick or cross."},

    {"layout": "content", "id": "wrap-up", "step": 1, "background_color": NAVY,
     "title": "You trained your ears today.",
     "body": "Say these with the ending: books, dogs, glasses.",
     "notes": "Recycling: the same plural endings return in the next lesson warm-up."},
]

deck = {
    "title": "Pronunciation Noticing: Plural -s /s/ /z/ /&#618;z/",
    "theme": "black",
    "transition": "slide",
    "slides": slides,
}

OUT.write_text(json.dumps(deck, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Wrote {OUT} with {len(slides)} slides")
