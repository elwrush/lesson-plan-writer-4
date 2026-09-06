"""Generate A4 prompt-card books (B1 + B2), 4 cards per page, using Playwright.

20 B1 competition-essay prompts (PET for Schools Task 2 format).
20 B2 compare-contrast prompts.

Output: PROJECTS/FINAL WRITING/B1-Competition-Essay-Prompts.pdf
        PROJECTS/FINAL WRITING/B2-Compare-Contrast-Prompts.pdf
        PROJECTS/FINAL WRITING/B1_PROMPTS.json
        PROJECTS/FINAL WRITING/B2_PROMPTS.json
"""

import json
import subprocess
from pathlib import Path

PROJECT_DIR = Path(__file__).parent

# ── B1 prompts (PET for Schools Task 2 competition essay) ──────────────

B1_PROMPTS = [
    {
        "id": 1,
        "context": "Some students say it is easier to learn today because you can find the answer on the internet. Other students say you learn more when a teacher helps you in class.",
        "topic": "learning with a teacher or learning from the internet",
        "bullets": [
            "what you use the internet for",
            "what you learn from your teacher",
            "which is better for you and why",
        ],
    },
    {
        "id": 2,
        "context": "Some students say school uniforms make everyone equal and save time in the morning. Other students say they should be free to wear their own clothes.",
        "topic": "wearing a school uniform or wearing your own clothes",
        "bullets": [
            "what you like about wearing a uniform",
            "what you like about wearing your own clothes",
            "which you prefer and why",
        ],
    },
    {
        "id": 3,
        "context": "Some students say homework helps them remember what they learned in class. Other students say homework takes too much free time.",
        "topic": "homework \u2014 good or bad for students",
        "bullets": [
            "one good thing about homework",
            "one bad thing about homework",
            "whether homework should be given or not and why",
        ],
    },
    {
        "id": 4,
        "context": "Some students say mobile phones help them learn because they can look up information quickly. Other students say phones are a big distraction in class.",
        "topic": "mobile phones in school \u2014 helpful or distracting",
        "bullets": [
            "one way phones help you learn",
            "one way phones cause problems",
            "whether students should use phones in school and why",
        ],
    },
    {
        "id": 5,
        "context": "Some students say English is the most useful language to learn because it is spoken all over the world. Other students say it is more important to study your own language well first.",
        "topic": "learning English \u2014 the most important subject or not",
        "bullets": [
            "one reason English is useful",
            "one reason other subjects matter more",
            "which you think is the most important and why",
        ],
    },
    {
        "id": 6,
        "context": "Some students say maths is the best subject because it teaches you to think clearly. Other students say science is more useful because it explains the world around us.",
        "topic": "the best subject at school",
        "bullets": [
            "one subject you enjoy and why",
            "one subject you find difficult and why",
            "which subject you think is the most important and why",
        ],
    },
    {
        "id": 7,
        "context": "Some students say school trips are the best way to learn new things. Other students say you learn more in the classroom with a teacher.",
        "topic": "school trips \u2014 fun or useful",
        "bullets": [
            "one school trip you remember",
            "what you learned from it",
            "whether schools should have more trips and why",
        ],
    },
    {
        "id": 8,
        "context": "Some students say reading books helps you learn new words and ideas. Other students say watching videos is easier and more interesting.",
        "topic": "reading books or watching videos \u2014 which helps you learn more",
        "bullets": [
            "one thing you learn from reading",
            "one thing you learn from videos",
            "which you prefer and why",
        ],
    },
    {
        "id": 9,
        "context": "Some students say online friends are just as good as real friends. Other students say you need to meet people face to face to have a real friendship.",
        "topic": "online friends or real friends",
        "bullets": [
            "one good thing about online friends",
            "one good thing about real friends",
            "which type of friend is more important and why",
        ],
    },
    {
        "id": 10,
        "context": "Some students say studying in the morning is best because your brain is fresh. Other students say studying at night is better because it is quiet.",
        "topic": "the best time to study",
        "bullets": [
            "one reason morning study is good",
            "one reason evening study is good",
            "which time you prefer and why",
        ],
    },
    {
        "id": 11,
        "context": "Some students say team sports are better because you learn to work with others. Other students say individual sports are better because you can improve at your own speed.",
        "topic": "team sports or individual sports",
        "bullets": [
            "one good thing about team sports",
            "one good thing about individual sports",
            "which you prefer and why",
        ],
    },
    {
        "id": 12,
        "context": "Some students say living in the city is better because there are more things to do. Other students say the countryside is better because it is quieter and safer.",
        "topic": "living in the city or the countryside",
        "bullets": [
            "one good thing about city life",
            "one good thing about country life",
            "which you prefer and why",
        ],
    },
    {
        "id": 13,
        "context": "Some students say a part-time job teaches teenagers to be responsible. Other students say teenagers should focus on school and not work.",
        "topic": "part-time jobs for teenagers \u2014 a good idea or not",
        "bullets": [
            "one good thing about working as a teenager",
            "one bad thing about working as a teenager",
            "whether teenagers should work and why",
        ],
    },
    {
        "id": 14,
        "context": "Some students say bringing lunch from home is healthier and cheaper. Other students say buying lunch at school is more convenient and tastier.",
        "topic": "bringing lunch from home or buying lunch at school",
        "bullets": [
            "one good thing about bringing lunch",
            "one good thing about buying lunch",
            "which you prefer and why",
        ],
    },
    {
        "id": 15,
        "context": "Some students say making mistakes is the best way to learn. Other students say it is better to get things right the first time.",
        "topic": "learning from mistakes",
        "bullets": [
            "one time you learned from a mistake",
            "what you learned from it",
            "why mistakes can help you learn better",
        ],
    },
    {
        "id": 16,
        "context": "Some students say children should start learning English as early as possible. Other students say it is better to wait until you are older and can understand more.",
        "topic": "the best age to start learning English",
        "bullets": [
            "one advantage of starting young",
            "one advantage of starting later",
            "which age you think is best and why",
        ],
    },
    {
        "id": 17,
        "context": "Some students say having brothers and sisters teaches you to share and cooperate. Other students say sharing with siblings causes arguments and stress.",
        "topic": "sharing with brothers and sisters",
        "bullets": [
            "one good thing about having siblings",
            "one difficult thing about having siblings",
            "whether having siblings is better or worse and why",
        ],
    },
    {
        "id": 18,
        "context": "Some students say video games help you think faster and solve problems. Other students say video games waste time and make you lazy.",
        "topic": "video games \u2014 useful or a waste of time",
        "bullets": [
            "one good thing about playing video games",
            "one bad thing about playing video games",
            "whether video games are useful and why",
        ],
    },
    {
        "id": 19,
        "context": "Some students say cooking is an important life skill that everyone should learn. Other students say it is easy to buy food, so cooking is not necessary.",
        "topic": "learning to cook \u2014 important or not",
        "bullets": [
            "one reason cooking is useful",
            "one reason it is not important",
            "whether students should learn to cook and why",
        ],
    },
    {
        "id": 20,
        "context": "Some students say small classes are better because the teacher can give more attention to each student. Other students say big classes are better because there are more people to work with.",
        "topic": "small classes or big classes",
        "bullets": [
            "one advantage of small classes",
            "one advantage of big classes",
            "which you prefer and why",
        ],
    },
]

# ── B2 prompts (compare-contrast) ──────────────────────────────────────

B2_PROMPTS = [
    {
        "id": 1,
        "context": "Repetitive learning has been a feature of Asian education systems for centuries.",
        "definition": "It involves repeating the same information or task again and again until you can remember it and do it without thinking.",
        "topic": "repetitive learning",
    },
    {
        "id": 2,
        "context": "Homework has been a standard part of schooling for generations.",
        "definition": "It involves tasks and exercises that students complete at home after school hours.",
        "topic": "homework",
    },
    {
        "id": 3,
        "context": "Standardised testing has become increasingly common in education systems around the world.",
        "definition": "It involves all students taking the same exam under the same conditions and receiving a score.",
        "topic": "standardised testing",
    },
    {
        "id": 4,
        "context": "School uniforms have been a tradition in many countries for over a century.",
        "definition": "They require students to wear specific clothing chosen by the school rather than their own clothes.",
        "topic": "school uniforms",
    },
    {
        "id": 5,
        "context": "Mobile phones have become a part of daily life for most teenagers.",
        "definition": "They allow students to access information instantly but also offer many distractions.",
        "topic": "mobile phones in the classroom",
    },
    {
        "id": 6,
        "context": "Online learning has grown rapidly since the COVID-19 pandemic.",
        "definition": "It involves attending classes and completing assignments through the internet instead of meeting in a physical classroom.",
        "topic": "online learning",
    },
    {
        "id": 7,
        "context": "Starting foreign language study from primary school has become a policy in many countries.",
        "definition": "It involves teaching children a second language from as young as five or six years old.",
        "topic": "foreign language study from primary school",
    },
    {
        "id": 8,
        "context": "After-school tutoring is widespread in many Asian countries.",
        "definition": "It involves students attending extra classes outside regular school hours to improve their academic performance.",
        "topic": "after-school tutoring",
    },
    {
        "id": 9,
        "context": "Mixed-ability classrooms are used in many education systems to bring students of different levels together.",
        "definition": "They involve placing students of varying academic abilities in the same class rather than separating them by skill level.",
        "topic": "mixed-ability classrooms",
    },
    {
        "id": 10,
        "context": "Handwritten notes remain common in classrooms despite the rise of digital technology.",
        "definition": "They involve students writing by hand during lessons rather than typing on a device.",
        "topic": "handwritten notes",
    },
    {
        "id": 11,
        "context": "Arts and music education has been valued in schools for centuries.",
        "definition": "It involves including creative subjects such as painting, drama, and music as part of the regular school programme.",
        "topic": "arts and music in the curriculum",
    },
    {
        "id": 12,
        "context": "Physical education has been a required subject in most schools for decades.",
        "definition": "It involves students participating in sports, exercise, and fitness activities as part of their school day.",
        "topic": "physical education requirements",
    },
    {
        "id": 13,
        "context": "Peer teaching is a method where students explain concepts to their classmates.",
        "definition": "It involves learners taking on the role of teacher to help others understand a topic.",
        "topic": "peer teaching",
    },
    {
        "id": 14,
        "context": "Textbook-based learning has been the foundation of education for centuries.",
        "definition": "It involves using printed books as the primary resource for delivering lessons and exercises.",
        "topic": "textbook-based learning",
    },
    {
        "id": 15,
        "context": "Project-based learning has gained popularity in recent years as an alternative to traditional teaching.",
        "definition": "It involves students working on extended tasks that combine knowledge from different subjects.",
        "topic": "project-based learning",
    },
    {
        "id": 16,
        "context": "Spaced repetition is a learning technique backed by memory research.",
        "definition": "It involves reviewing material at gradually increasing intervals to strengthen long-term recall.",
        "topic": "spaced repetition",
    },
    {
        "id": 17,
        "context": "Student self-assessment has become more common in modern education.",
        "definition": "It involves learners evaluating their own work and progress rather than relying solely on teacher feedback.",
        "topic": "student self-assessment",
    },
    {
        "id": 18,
        "context": "Year-round schooling is practised in some countries as an alternative to the traditional calendar.",
        "definition": "It involves shorter, more frequent breaks throughout the year instead of one long summer holiday.",
        "topic": "year-round schooling",
    },
    {
        "id": 19,
        "context": "Bilingual education programmes have expanded in many countries as global communication increases.",
        "definition": "They involve teaching students in two languages, often the local language and English, throughout their schooling.",
        "topic": "bilingual education",
    },
    {
        "id": 20,
        "context": "Cram schools, known as juku in Japan and hagwon in South Korea, are widespread across Asia.",
        "definition": "They involve students attending intensive after-school classes specifically designed to prepare for entrance exams.",
        "topic": "cram schools and intensive exam preparation",
    },
]

# ── Palette (matches existing topic_cards.py) ───────────────────────────

PALETTE = [
    "#1a1a2e",
    "#116466",
    "#2e7d32",
    "#c0392b",
    "#e67e22",
    "#6c3483",
    "#2874a6",
    "#7b241c",
]

# ── HTML template ───────────────────────────────────────────────────────

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  @page {
    size: A4 portrait;
    margin: 10mm;
  }
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }
  body {
    font-family: 'Roboto', 'Segoe UI', Arial, sans-serif;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
  .page {
    width: 190mm;
    height: 277mm;
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: 1fr 1fr;
    gap: 5mm;
    page-break-after: always;
  }
  .page:last-child {
    page-break-after: auto;
  }
  .card {
    border: 1px solid #d5dbe3;
    border-radius: 9px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    background: #ffffff;
    box-shadow: 0 2px 6px rgba(26, 26, 46, 0.10);
  }
  .card-header {
    color: #fff;
    padding: 3.5mm 4mm;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .card-title {
    display: flex;
    align-items: center;
  }
  .num-badge {
    background: #ffdd00;
    color: #1a1a2e;
    font-weight: 900;
    font-size: 14pt;
    width: 8mm;
    height: 8mm;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    margin-right: 3mm;
    flex-shrink: 0;
  }
  .card-kicker {
    font-size: 10pt;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    opacity: 0.92;
  }
  .card-body {
    flex: 1;
    padding: 4mm 4.5mm 3mm 4.5mm;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
  }
  .notice {
    font-size: 9pt;
    color: #888;
    font-style: italic;
    margin-bottom: 2mm;
  }
  .competition-title {
    font-size: 13pt;
    font-weight: 900;
    color: #1a1a2e;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 2.5mm;
    text-align: center;
  }
  .context-text {
    font-size: 10pt;
    line-height: 1.45;
    color: #333;
    margin-bottom: 2.5mm;
  }
  .write-line {
    font-size: 10.5pt;
    font-weight: 700;
    color: #1a1a2e;
    margin-bottom: 2mm;
  }
  .bullets-label {
    font-size: 9.5pt;
    font-weight: 700;
    color: #555;
    margin-bottom: 1mm;
  }
  .bullet {
    font-size: 10pt;
    line-height: 1.4;
    color: #333;
    padding-left: 3mm;
    margin-bottom: 0.8mm;
  }
  .bullet::before {
    content: "\2022  ";
    font-weight: 700;
    color: #1a1a2e;
  }
  .word-count {
    font-size: 8.5pt;
    color: #999;
    font-style: italic;
    margin-top: auto;
    padding-top: 2mm;
  }
  .topic-title {
    font-size: 12pt;
    font-weight: 900;
    color: #1a1a2e;
    margin-bottom: 3mm;
  }
  .b2-context {
    font-size: 10pt;
    line-height: 1.45;
    color: #333;
    margin-bottom: 2mm;
  }
  .b2-definition {
    font-size: 10pt;
    line-height: 1.45;
    color: #333;
    margin-bottom: 2.5mm;
  }
  .b2-instruction {
    font-size: 10.5pt;
    font-weight: 700;
    color: #1a1a2e;
  }
  .card-footer {
    border-top: 1px solid #e3e8ef;
    padding: 2mm 4.5mm;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .level-tag {
    font-size: 8pt;
    font-weight: 700;
    letter-spacing: 0.5px;
  }
  .card-page {
    font-size: 8pt;
    color: #aab2bf;
    font-weight: 500;
  }
</style>
</head>
<body>
{pages}
</body>
</html>
"""

# ── Card HTML builders ──────────────────────────────────────────────────

B1_CARD_HTML = r"""<div class="card">
  <div class="card-header" style="background:{accent}">
    <div class="card-title">
      <span class="num-badge">{num}</span>
      <span class="card-kicker">Essay Competition</span>
    </div>
  </div>
  <div class="card-body">
    <div class="notice">You see this notice in your school magazine.</div>
    <div class="competition-title">ESSAY COMPETITION</div>
    <div class="context-text">{context}</div>
    <div class="write-line">Write an essay for the competition about {topic}.</div>
    <div class="bullets-label">Your essay must include:</div>
{bullets_html}
    <div class="word-count">Write your essay in around 100 words.</div>
  </div>
  <div class="card-footer">
    <span class="level-tag" style="color:{accent}">CEFR B1 &middot; Grade 8</span>
    <span class="card-page">Card {num} / {total}</span>
  </div>
</div>
"""

B2_CARD_HTML = r"""<div class="card">
  <div class="card-header" style="background:{accent}">
    <div class="card-title">
      <span class="num-badge">{num}</span>
      <span class="card-kicker">Compare &amp; Contrast</span>
    </div>
  </div>
  <div class="card-body">
    <div class="topic-title">{topic_title}</div>
    <div class="b2-context">{context}</div>
    <div class="b2-definition">{definition}</div>
    <div class="b2-instruction">Compare and contrast the positive and negative features of {topic}.</div>
  </div>
  <div class="card-footer">
    <span class="level-tag" style="color:{accent}">CEFR B2 &middot; Grade 9</span>
    <span class="card-page">Card {num} / {total}</span>
  </div>
</div>
"""


# ── Page builders ───────────────────────────────────────────────────────

def build_b1_pages(prompts: list) -> str:
    pages = []
    for i in range(0, len(prompts), 4):
        chunk = prompts[i : i + 4]
        cards = []
        for p in chunk:
            accent = PALETTE[(p["id"] - 1) % len(PALETTE)]
            bullets_html = "\n".join(
                f'    <div class="bullet">{b}</div>' for b in p["bullets"]
            )
            cards.append(
                B1_CARD_HTML.format(
                    num=p["id"],
                    total=len(prompts),
                    accent=accent,
                    context=p["context"],
                    topic=p["topic"],
                    bullets_html=bullets_html,
                )
            )
        pages.append('<div class="page">' + "".join(cards) + "</div>\n")
    return "".join(pages)


def build_b2_pages(prompts: list) -> str:
    pages = []
    for i in range(0, len(prompts), 4):
        chunk = prompts[i : i + 4]
        cards = []
        for p in chunk:
            accent = PALETTE[(p["id"] - 1) % len(PALETTE)]
            cards.append(
                B2_CARD_HTML.format(
                    num=p["id"],
                    total=len(prompts),
                    accent=accent,
                    topic_title=p["topic"].title(),
                    context=p["context"],
                    definition=p["definition"],
                    topic=p["topic"],
                )
            )
        pages.append('<div class="page">' + "".join(cards) + "</div>\n")
    return "".join(pages)


# ── Render pipeline ─────────────────────────────────────────────────────

def render_pdf(html_str: str, pdf_path: Path) -> None:
    html_path = pdf_path.with_suffix(".html")
    html_path.write_text(html_str, encoding="utf-8")
    print(f"HTML: {html_path}")

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 800, "height": 1132})
        page.goto(html_path.absolute().as_uri())
        page.pdf(
            path=str(pdf_path),
            print_background=True,
            prefer_css_page_size=True,
        )
        browser.close()
    print(f"PDF: {pdf_path}")

    tmp_pdf = pdf_path.with_suffix(".tmp.pdf")
    subprocess.run(
        [
            "gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite",
            "-dPDFSETTINGS=/prepress", f"-sOutputFile={tmp_pdf}",
            "-dCompatibilityLevel=1.7", str(pdf_path),
        ],
        check=True,
        timeout=120,
    )
    tmp_pdf.replace(pdf_path)
    print(f"Flattened: {pdf_path}")


def verify_pdf(pdf_path: Path) -> None:
    result = subprocess.run(["pdfinfo", str(pdf_path)], capture_output=True, text=True)
    print(f"\n--- {pdf_path.name} ---")
    for line in result.stdout.splitlines():
        if any(k in line for k in ("Pages", "Page size", "Title")):
            print(f"  {line.strip()}")


# ── Main ────────────────────────────────────────────────────────────────

def main() -> None:
    pdf_dir = PROJECT_DIR

    # Save prompts as JSON
    (pdf_dir / "B1_PROMPTS.json").write_text(
        json.dumps(B1_PROMPTS, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (pdf_dir / "B2_PROMPTS.json").write_text(
        json.dumps(B2_PROMPTS, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print("JSON prompts saved.")

    # B1 PDF
    b1_html = HTML_TEMPLATE.replace("{pages}", build_b1_pages(B1_PROMPTS))
    render_pdf(b1_html, pdf_dir / "B1-Competition-Essay-Prompts.pdf")

    # B2 PDF
    b2_html = HTML_TEMPLATE.replace("{pages}", build_b2_pages(B2_PROMPTS))
    render_pdf(b2_html, pdf_dir / "B2-Compare-Contrast-Prompts.pdf")

    # Verify
    verify_pdf(pdf_dir / "B1-Competition-Essay-Prompts.pdf")
    verify_pdf(pdf_dir / "B2-Compare-Contrast-Prompts.pdf")
    print("\nDone.")


if __name__ == "__main__":
    main()
