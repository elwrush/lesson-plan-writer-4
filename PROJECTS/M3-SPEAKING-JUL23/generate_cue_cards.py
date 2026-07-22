"""Generate 10 speed dating cue cards, 4 per A4 page, using Playwright.

Each card provides:
- The discussion question with brief context
- Suggested discussion structure (opening, arguments, resolution)
- Language hints for each phase
"""

import sys
from pathlib import Path

CARDS = [
    {
        "num": 1,
        "title": "Should we eat meat?",
        "context": (
            "Some people say eating animals is wrong. "
            "Other people say humans need meat to be healthy."
        ),
    },
    {
        "num": 2,
        "title": "Should there be super-rich people?",
        "context": (
            "A few people have billions of dollars. "
            "Many people have very little money. "
            "Is it fair?"
        ),
    },
    {
        "num": 3,
        "title": "Should students wear school uniforms?",
        "context": (
            "Some schools make students wear uniforms. "
            "Other schools let students wear their own clothes."
        ),
    },
    {
        "num": 4,
        "title": "Is it OK to keep animals in zoos?",
        "context": (
            "Zoos help protect animals. "
            "But animals in zoos cannot live freely."
        ),
    },
    {
        "num": 5,
        "title": "Should social media be banned for teens?",
        "context": (
            "Social media can be fun and useful. "
            "But it can also be bad for mental health."
        ),
    },
    {
        "num": 6,
        "title": "City life or countryside life?",
        "context": (
            "Cities have more jobs and things to do. "
            "The countryside is quieter and cleaner."
        ),
    },
    {
        "num": 7,
        "title": "Should everyone learn English?",
        "context": (
            "English helps people communicate worldwide. "
            "But maybe other languages matter more?"
        ),
    },
    {
        "num": 8,
        "title": "Is university the only path to success?",
        "context": (
            "Many successful people did not go to university. "
            "But some jobs need a degree."
        ),
    },
    {
        "num": 9,
        "title": "How much homework is enough?",
        "context": (
            "Homework helps you practice. "
            "But too much homework is stressful."
        ),
    },
    {
        "num": 10,
        "title": "Is technology helping or hurting us?",
        "context": (
            "Technology makes many things easier. "
            "But people spend too much time on screens."
        ),
    },
]

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  @page {
    size: A4;
    margin: 15mm;
  }
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }
  body {
    font-family: 'Roboto', 'Segoe UI', Arial, sans-serif;
    width: 100%;
  }
  .page {
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: 1fr 1fr;
    gap: 10mm;
    page-break-after: always;
    height: 267mm;
    align-content: start;
  }
  .page:last-child {
    page-break-after: auto;
  }
  .card {
    border: 1.5px solid #333;
    border-radius: 4px;
    padding: 8mm 6mm;
    display: flex;
    flex-direction: column;
    page-break-inside: avoid;
  }
  .card-header {
    font-size: 12pt;
    font-weight: 700;
    color: #1a1a2e;
    border-bottom: 2px solid #1a1a2e;
    padding-bottom: 3mm;
    margin-bottom: 3mm;
    line-height: 1.3;
  }
  .card-header .num-badge {
    display: inline-block;
    background: #1a1a2e;
    color: #fff;
    width: 7mm;
    height: 7mm;
    text-align: center;
    line-height: 7mm;
    font-size: 10pt;
    border-radius: 2px;
    margin-right: 3mm;
  }
  .card-subtitle {
    font-size: 8.5pt;
    color: #555;
    font-weight: 400;
    margin-top: 1mm;
  }
  .section-label {
    font-size: 7.5pt;
    font-weight: 700;
    color: #666;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-top: 2.5mm;
    margin-bottom: 0.8mm;
  }
  .section-label:first-of-type {
    margin-top: 0;
  }
  .context-text {
    font-size: 9pt;
    line-height: 1.4;
    color: #222;
  }
  .structure {
    font-size: 8.5pt;
    line-height: 1.4;
    color: #333;
    padding-left: 2mm;
    border-left: 2px solid #9b59b6;
    margin-top: 1mm;
  }
  .structure li {
    margin-bottom: 1mm;
    list-style: none;
  }
  .structure li::before {
    content: "\25B8 ";
    color: #9b59b6;
    font-weight: 700;
  }
  .lang-hint {
    font-size: 8pt;
    line-height: 1.35;
    color: #1a1a2e;
    background: #eef2f7;
    border-radius: 3px;
    padding: 1.5mm 2mm;
    margin-top: 1.5mm;
    flex: 1;
  }
  .lang-hint ul {
    margin: 1mm 0 0 0;
    padding-left: 3mm;
    list-style: none;
  }
  .lang-hint ul li {
    font-size: 8pt;
    line-height: 1.4;
    margin-bottom: 0.5mm;
  }
  .lang-hint ul li::before {
    content: "\2022 ";
    color: #1a1a2e;
    font-weight: 700;
  }
  .lang-hint ul li strong {
    color: #1a1a2e;
  }
</style>
</head>
<body>
{cards}
</body>
</html>
"""

CARD_HTML = r"""<div class="card">
  <div class="card-header">
    <span class="num-badge">{num}</span>M3 Speaking Cue Card
    <div class="card-subtitle">#{num}: {title}</div>
  </div>
  <div class="section-label">The question</div>
  <div class="context-text">{context}</div>
  <div class="section-label">Structure your discussion</div>
  <ol class="structure">
    <li><strong>Open:</strong> &ldquo;We have an interesting question today: {title}?&rdquo;</li>
    <li><strong>Your view:</strong> State your position. Use <em>I think&hellip; / In my opinion&hellip;</em></li>
    <li><strong>Listen &amp; respond:</strong> <em>I agree because&hellip; / I see it differently. / Why do you think that?</em></li>
    <li><strong>Resolution:</strong> Try to agree. <em>We both think&hellip; / We partly agree. / We disagree about&hellip;</em></li>
  </ol>
  <div class="lang-hint">
    <strong>Language hints</strong>
    <ul>
      <li><strong>Agree:</strong> Absolutely. / I think so too. / That&rsquo;s a good point.</li>
      <li><strong>Disagree:</strong> I&rsquo;m not sure. / I see it differently. / Yes, but&hellip;</li>
      <li><strong>Follow-up:</strong> Can you explain? / What makes you say that?</li>
    </ul>
  </div>
</div>"""


def build_page(cards):
    inner = ""
    for c in cards:
        inner += CARD_HTML.format(
            num=c["num"], title=c["title"], context=c["context"]
        )
    return f'<div class="page">\n{inner}\n</div>\n'


pages_html = ""
for i in range(0, len(CARDS), 4):
    chunk = CARDS[i : i + 4]
    pages_html += build_page(chunk)

full_html = HTML_TEMPLATE.replace("{cards}", pages_html)

out_dir = Path(__file__).parent / "cue_cards"
out_dir.mkdir(parents=True, exist_ok=True)
html_path = out_dir / "cue_cards.html"
html_path.write_text(full_html, encoding="utf-8")
print(f"HTML written to {html_path}")

try:
    from playwright.sync_api import sync_playwright

    pdf_path = out_dir / "cue_cards.pdf"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(html_path.absolute().as_uri())
        page.pdf(path=str(pdf_path), format="A4", print_background=True)
        browser.close()
    print(f"PDF written to {pdf_path}")
except ImportError:
    print("Playwright not installed. Install with: pip install playwright && playwright install chromium")
    print(f"Open {html_path} in a browser and print to PDF (A4, background graphics).")
