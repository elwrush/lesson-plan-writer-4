"""generate_interview_cards.py — 4 MUIDS practice interview question cards per A4 page.

Each card carries one real MUIDS-style interview question, the answer structure
(PREP for opinion questions, a 3-step intro for "Tell me about yourself"),
likely follow-up probes, and language hints. Rendered via Playwright and
flattened with Ghostscript for print reliability; cut along the card borders
and distribute one per student pair.

Usage:
    python3 "PROJECTS/INTERVIEW SPEAKING/generate_interview_cards.py"
"""

import subprocess
import sys
from pathlib import Path

OUT_DIR = Path(__file__).parent
PDF_PATH = OUT_DIR / "interview_cards.pdf"

CARDS = [
    {
        "num": 1,
        "title": "Personal",
        "question": "Tell me about yourself.",
        "structure": [
            ("Who you are", "My name is&hellip; I am 14 years old."),
            ("What you like", "I enjoy&hellip; (sports, music, reading)"),
            ("Your goal", "In the future, I want to&hellip;"),
        ],
        "follow_ups": [
            "What do you do in your free time?",
            "What is your favourite subject?",
        ],
    },
    {
        "num": 2,
        "title": "Why MUIDS?",
        "question": "Why do you want to study at MUIDS?",
        "structure": [
            ("Answer first", "Because of the way they teach. Students learn by doing things, not just reading."),
            ("Example", "For example, science students do real experiments and present them in English."),
            ("For me", "I want to study medicine, so I need strong English and practical skills."),
            ("Close", "So MUIDS is exactly the school I want."),
        ],
        "follow_ups": [
            "What do you know about MUIDS?",
            "Which subjects interest you?",
        ],
    },
    {
        "num": 3,
        "title": "Favourite subject",
        "question": "What is your favourite subject and why?",
        "structure": [
            ("P — Position", "Science, for sure!"),
            ("R — Reason", "I love knowing how things work."),
            ("E — Example", "For example, last term we did an experiment with magnets."),
            ("P — Position", "So yeah, that&rsquo;s why science is my favourite."),
        ],
        "follow_ups": [
            "What do you like most about it?",
            "Which subject do you find difficult?",
        ],
    },
    {
        "num": 4,
        "title": "Opinion",
        "question": "Should mobile phones be banned at school?",
        "structure": [
            ("P — Position", "Hmm, no. I don&rsquo;t think phones should be banned."),
            ("R — Reason", "They&rsquo;re really useful for learning."),
            ("E — Example", "For example, I can look up a word on my phone in seconds."),
            ("P — Position", "So I think they should stay, just not during tests."),
        ],
        "follow_ups": [
            "How much do you use your phone?",
            "What do you use it for?",
            "Do you think phone use is important?",
        ],
    },
    {
        "num": 5,
        "title": "Challenge",
        "question": "What do you do when you face a challenge?",
        "structure": [
            ("S — Situation", "Tell about a hard time. For example, a difficult exam."),
            ("A — Action", "Say what you did. I made a study plan and practiced every day."),
            ("R — Result", "Say what happened. I passed, and I felt proud."),
        ],
        "follow_ups": [
            "What did you learn from it?",
            "Would you do anything differently?",
        ],
    },
    {
        "num": 6,
        "title": "Strengths & weaknesses",
        "question": "What are your strengths and weaknesses?",
        "structure": [
            ("Strength", "I am good at&hellip; (e.g. working in a team)"),
            ("Example", "For example, I help my group in school projects."),
            ("Weakness", "One weakness is&hellip; I worry too much about exams."),
            ("Improving", "I am working on it. I practice deep breathing before tests."),
        ],
        "follow_ups": [
            "How are you improving your weakness?",
            "Who helps you when things are hard?",
        ],
    },
    {
        "num": 7,
        "title": "About MUIDS",
        "question": "What do you know about MUIDS?",
        "structure": [
            ("Facts", "MUIDS is an international high school at Mahidol University."),
            ("Learning", "Students study in English and learn by doing projects and experiments."),
            ("Example", "For example, science students do lab experiments and present their results in English."),
            ("Why it matters", "That&rsquo;s why MUIDS is my first choice."),
        ],
        "follow_ups": [
            "Where is MUIDS?",
            "What subjects can you study there?",
        ],
    },
    {
        "num": 8,
        "title": "Your questions",
        "question": "Do you have any questions for us?",
        "structure": [
            ("About learning", "What is a normal day at MUIDS like?"),
            ("About activities", "What clubs and sports can students join?"),
            ("About support", "How do teachers help new students?"),
        ],
        "follow_ups": [
            "Ask one or two questions. Asking shows you are interested.",
        ],
    },
    {
        "num": 9,
        "title": "Social media",
        "question": "Should social media be banned for teenagers under 16?",
        "structure": [
            ("P — Position", "Hmm, no. I don&rsquo;t think a full ban is the answer."),
            ("R — Reason", "Social media helps us stay in touch and learn new things."),
            ("E — Example", "For example, I follow science pages and chat with my friends."),
            ("P — Position", "So I think age limits and clear rules are better than a ban."),
        ],
        "follow_ups": [
            "How much time do you spend on social media?",
            "What are the dangers of social media?",
            "Do your parents limit your screen time?",
        ],
    },
    {
        "num": 10,
        "title": "Homework",
        "question": "Should homework be banned?",
        "structure": [
            ("P — Position", "Hmm, not completely. Some homework is useful."),
            ("R — Reason", "It helps us practise what we learn in class."),
            ("E — Example", "For example, a little maths homework keeps my skills sharp."),
            ("P — Position", "But I think the amount should be smaller, not banned."),
        ],
        "follow_ups": [
            "How much homework do you get?",
            "What kind of homework do you like?",
            "When is homework a waste of time?",
        ],
    },
]

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  @page {
    size: A4;
    margin: 12mm;
  }
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }
  body {
    font-family: 'Roboto', 'Segoe UI', Arial, sans-serif;
    color: #222;
  }
  .page {
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: 1fr 1fr;
    gap: 4mm;
    height: 273mm;
    page-break-after: always;
  }
  .card {
    border: 1.5px solid #333;
    border-radius: 4px;
    padding: 4mm 5mm;
    display: flex;
    flex-direction: column;
  }
  .card-header {
    font-size: 10pt;
    font-weight: 700;
    color: #1a1a2e;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    border-bottom: 1.5px solid #1a1a2e;
    padding-bottom: 1.5mm;
    margin-bottom: 2mm;
  }
  .num-badge {
    display: inline-block;
    background: #1a1a2e;
    color: #fff;
    width: 5.5mm;
    height: 5.5mm;
    text-align: center;
    line-height: 5.5mm;
    font-size: 9pt;
    border-radius: 2px;
    margin-right: 2mm;
  }
  .question {
    font-size: 16pt;
    font-weight: 700;
    line-height: 1.25;
    background: #eef2f7;
    border-left: 3px solid #1a1a2e;
    padding: 2.5mm 3mm;
    margin-bottom: 2.5mm;
  }
  .section-label {
    font-size: 9pt;
    font-weight: 700;
    color: #666;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 1mm;
  }
  .structure {
    list-style: none;
    font-size: 11pt;
    line-height: 1.35;
    color: #333;
    border-left: 2px solid #9b59b6;
    padding-left: 2.5mm;
    flex: 1;
  }
  .structure li {
    margin-bottom: 1.2mm;
  }
  .structure li strong {
    color: #9b59b6;
    margin-right: 1mm;
  }
  .follow-up {
    margin-top: 2mm;
    font-size: 10.5pt;
    line-height: 1.35;
    color: #444;
    background: #fff8e1;
    border: 1px solid #e0c568;
    border-radius: 3px;
    padding: 1.8mm 2.5mm;
  }
  .follow-up strong {
    color: #7a5c00;
  }
</style>
</head>
<body>
{cards}
</body>
</html>
"""

CARD_HTML = """<div class="card">
  <div class="card-header"><span class="num-badge">{num}</span>Interview Question {num} — {title}</div>
  <div class="question">{question}</div>
  <div class="section-label">Answer structure</div>
  <ol class="structure">
    {steps}
  </ol>
  <div class="follow-up"><strong>Follow-up:</strong> {follow_ups}</div>
</div>
"""


def build_card(card: dict) -> str:
    steps = "\n".join(
        f"<li><strong>{label}:</strong> {text}</li>" for label, text in card["structure"]
    )
    follow_ups = " ".join(f"&ldquo;{q}&rdquo;" for q in card["follow_ups"])
    return CARD_HTML.format(
        num=card["num"], title=card["title"], question=card["question"],
        steps=steps, follow_ups=follow_ups,
    )


def build_pages() -> str:
    pages = []
    for i in range(0, len(CARDS), 4):
        chunk = CARDS[i : i + 4]
        cards_html = "\n".join(build_card(card) for card in chunk)
        pages.append(f'<div class="page">\n{cards_html}\n</div>\n')
    return "\n".join(pages)


def main() -> None:
    html_path = OUT_DIR / "interview_cards.html"
    html_path.write_text(HTML_TEMPLATE.replace("{cards}", build_pages()), encoding="utf-8")
    print(f"HTML written to {html_path}")

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Playwright not installed. Install with: pip install playwright && playwright install chromium")
        print(f"Open {html_path} in a browser and print to PDF (A4, background graphics).")
        sys.exit(1)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(html_path.absolute().as_uri())
        page.pdf(path=str(PDF_PATH), format="A4", print_background=True)
        browser.close()
    print(f"PDF written to {PDF_PATH}")

    tmp_pdf = PDF_PATH.with_suffix(".tmp.pdf")
    subprocess.run(
        [
            "gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite",
            "-dPDFSETTINGS=/prepress", f"-sOutputFile={tmp_pdf}",
            "-dCompatibilityLevel=1.7", str(PDF_PATH),
        ],
        check=True, timeout=120,
    )
    tmp_pdf.replace(PDF_PATH)
    print(f"Flattened PDF via Ghostscript: {PDF_PATH}")


if __name__ == "__main__":
    main()
