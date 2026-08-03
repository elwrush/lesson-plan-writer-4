"""Generate 10 speed dating cue cards, 4 per A4 landscape page, using Playwright.

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
        "opener": "Let's start with a question about food: Should we eat meat?",
        "resolution": [
            "Great, so we both think eating less meat is a good idea!",
            "Hmm, we kind of agree but not completely on this one.",
            "Yikes, we really see this totally differently!",
        ],
    },
    {
        "num": 2,
        "title": "Should there be super-rich people?",
        "context": (
            "A few people have billions of dollars. "
            "Many people have very little money. "
            "Is it fair?"
        ),
        "opener": "I want to discuss money today: Should there be super-rich people?",
        "resolution": [
            "Perfect \u2014 so we agree the gap is way too big.",
            "Yeah, I think we partly agree but not on everything.",
            "Oh man, we are on completely different pages here!",
        ],
    },
    {
        "num": 3,
        "title": "Should students wear school uniforms?",
        "context": (
            "Some schools make students wear uniforms. "
            "Other schools let students wear their own clothes."
        ),
        "opener": "Here's a question about school life: Should students wear school uniforms?",
        "resolution": [
            "Nice, so we both see some good things about uniforms.",
            "Mmm, we are kind of in the middle on this one.",
            "Gosh, we really disagree \u2014 that is interesting!",
        ],
    },
    {
        "num": 4,
        "title": "Is it OK to keep animals in zoos?",
        "context": (
            "Zoos help protect animals. "
            "But animals in zoos cannot live freely."
        ),
        "opener": "Let's talk about animals today: Is it OK to keep animals in zoos?",
        "resolution": [
            "Sweet \u2014 we both think zoos need to do more for animals.",
            "Alright, it sounds like we agree a bit but not fully.",
            "Whoa, we have completely opposite views on this!",
        ],
    },
    {
        "num": 5,
        "title": "Should social media be banned for teens?",
        "context": (
            "Social media can be fun and useful. "
            "But it can also be bad for mental health."
        ),
        "opener": "Here's something to think about: Should social media be banned for teens?",
        "resolution": [
            "Brilliant \u2014 so we all think some rules make sense.",
            "Fair enough, we agree on the problem but not the solution.",
            "Oh dear, we really cannot find common ground here!",
        ],
    },
    {
        "num": 6,
        "title": "City life or countryside life?",
        "context": (
            "Cities have more jobs and things to do. "
            "The countryside is quieter and cleaner."
        ),
        "opener": "Let's compare two lifestyles: City life or countryside life \u2014 which is better?",
        "resolution": [
            "Cool, so we both think each place has good sides.",
            "Okay, I guess we just like different things \u2014 and that is fine.",
            "Wow, we really cannot agree on this at all!",
        ],
    },
    {
        "num": 7,
        "title": "Should everyone learn English?",
        "context": (
            "English helps people communicate worldwide. "
            "But maybe other languages matter more?"
        ),
        "opener": "I have a question about languages: Should everyone learn English?",
        "resolution": [
            "Love it \u2014 so we agree English is super useful.",
            "Kinda, we see this the same way but not quite.",
            "Oh boy, we have really different ideas about this one!",
        ],
    },
    {
        "num": 8,
        "title": "Is university the only path to success?",
        "context": (
            "Many successful people did not go to university. "
            "But some jobs need a degree."
        ),
        "opener": "Let's discuss education and careers: Is university the only path to success?",
        "resolution": [
            "Amazing \u2014 we both agree there are many paths.",
            "Sort of, I think we are close but not on the same page.",
            "Phew, we look at success in completely different ways!",
        ],
    },
    {
        "num": 9,
        "title": "How much homework is enough?",
        "context": (
            "Homework helps you practice. "
            "But too much homework is stressful."
        ),
        "opener": "Here's a question about studying: How much homework is enough?",
        "resolution": [
            "Exactly, so we all agree homework should not be too much.",
            "You know, we cannot quite agree on the right amount.",
            "Hmm, we are really far apart on this issue!",
        ],
    },
    {
        "num": 10,
        "title": "Is technology helping or hurting us?",
        "context": (
            "Technology makes many things easier. "
            "But people spend too much time on screens."
        ),
        "opener": "Let's think about modern life: Is technology helping or hurting us?",
        "resolution": [
            "Right on \u2014 so we see both the good and the bad sides.",
            "I mean, we agree on some things but not others.",
            "Goodness, our opinions could not be more different!",
        ],
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
    page-break-after: always;
    height: 267mm;
  }
  .page:last-child {
    page-break-after: auto;
  }
  .card {
    border: 1.5px solid #333;
    border-radius: 4px;
    padding: 6mm 8mm;
  }
  .card-header {
    font-size: 18pt;
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
    width: 8mm;
    height: 8mm;
    text-align: center;
    line-height: 8mm;
    font-size: 14pt;
    border-radius: 2px;
    margin-right: 3mm;
  }
  .card-subtitle {
    font-size: 14pt;
    color: #555;
    font-weight: 400;
    margin-top: 1mm;
  }
  .section-label {
    font-size: 14pt;
    font-weight: 700;
    color: #666;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-top: 3mm;
    margin-bottom: 1mm;
  }
  .section-label:first-of-type {
    margin-top: 0;
  }
  .context-text {
    font-size: 14pt;
    line-height: 1.5;
    color: #222;
  }
  .structure {
    font-size: 14pt;
    line-height: 1.5;
    color: #333;
    padding-left: 3mm;
    border-left: 2px solid #9b59b6;
    margin-top: 1mm;
    list-style: none;
  }
  .structure li {
    margin-bottom: 1mm;
  }
  .structure li::before {
    content: "\25B8 ";
    color: #9b59b6;
    font-weight: 700;
  }
  .structure .res-options {
    margin-top: 1mm;
    padding-left: 4mm;
    list-style: none;
  }
  .structure .res-options li {
    line-height: 1.4;
    margin-bottom: 0.5mm;
    color: #444;
  }
  .structure .res-options li::before {
    content: "\2022 ";
    color: #8e44ad;
    font-weight: 700;
  }
  .lang-hint {
    font-size: 14pt;
    line-height: 1.45;
    color: #1a1a2e;
    background: #eef2f7;
    border-radius: 3px;
    padding: 2mm 3mm;
    margin-top: 3mm;
  }
  .lang-hint ul {
    margin: 1mm 0 0 0;
    padding-left: 4mm;
    list-style: none;
  }
  .lang-hint ul li {
    font-size: 14pt;
    line-height: 1.45;
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
    <li><strong>Open:</strong> &ldquo;{opener}&rdquo;</li>
    <li><strong>Your view:</strong> State your position. Use <em>I think&hellip; / In my opinion&hellip;</em></li>
    <li><strong>Listen &amp; respond:</strong> <em>I agree because&hellip; / I see it differently. / Why do you think that?</em></li>
    <li><strong>Resolution:</strong> Try to summarise your discussion.
      <ul class="res-options">
        <li>{res0}</li>
        <li>{res1}</li>
        <li>{res2}</li>
      </ul>
    </li>
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


def build_page(card):
    inner = CARD_HTML.format(
        num=card["num"], title=card["title"], context=card["context"],
        opener=card["opener"],
        res0=card["resolution"][0], res1=card["resolution"][1], res2=card["resolution"][2],
    )
    return f'<div class="page">\n{inner}\n</div>\n'


pages_html = ""
for i in range(0, len(CARDS), 1):
    chunk = CARDS[i : i + 1]
    pages_html += build_page(chunk[0])

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

    # Flatten via Ghostscript for print reliability
    import subprocess
    tmp_pdf = pdf_path.with_suffix(".tmp.pdf")
    gs_args = [
        "gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite",
        "-dPDFSETTINGS=/prepress",
        f"-sOutputFile={tmp_pdf}", "-dCompatibilityLevel=1.7",
        str(pdf_path)
    ]
    subprocess.run(gs_args, check=True, timeout=120)
    tmp_pdf.replace(pdf_path)
    print(f"Flattened PDF via Ghostscript: {pdf_path}")
except ImportError:
    print("Playwright not installed. Install with: pip install playwright && playwright install chromium")
    print(f"Open {html_path} in a browser and print to PDF (A4, background graphics).")
