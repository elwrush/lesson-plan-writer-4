#!/usr/bin/env python3
"""Generate climate-change speaking cards.

SET A (structured, PAIRED)  - 10 topics, each a matched pair (copy 1 / copy 2).
   Appearance: one topic per page, 2 side-by-side cards (as in setA-structured).
   Structure:  YOUR 5-step pattern (Open -> Opinion -> Reason -> Agree/Disagree
   -> Agreement), NOT the reference 4-step Open/View/Respond/Resolution.
   Language:   each card carries function-labelled VARIANT language (a distinct
   pairing per card, never copied verbatim from another card).

SET B (bare)                - 6 single cards (not paired) evoking feelings about
   social responsibility. Appearance: number + prompt + hint (as in setB-bare).
"""

from pathlib import Path

from jinja2 import Template
from playwright.sync_api import sync_playwright

PROJ = Path(__file__).parent

# ---------------------------------------------------------------------------
# LANGUAGE BANKS (10 variants each) -> rotated so every card gets its own pairing
# ---------------------------------------------------------------------------
OV_OPEN = [
    "Let's talk about climate change now.",
    "Shall we talk about what is happening to our planet?",
    "Let's start with a question about the weather.",
    "Should we talk about why the climate is changing?",
    "Let's begin with something we all see every day.",
    "I'd like to talk about the weather and the climate.",
    "What do you think about all these unusual floods?",
    "Let's discuss what we can both do to help.",
    "To start, let's think about our own country.",
    "How do you feel about the way the climate is changing?",
]
OV_OPINION = [
    "In my view, ...",
    "I think ...",
    "If you ask me, ...",
    "I'd say ...",
    "It seems to me that ...",
    "I strongly believe ...",
    "Honestly, I think ...",
    "As far as I'm concerned, ...",
    "My opinion is that ...",
    "I'm fairly sure that ...",
]
OV_REASON = [
    "... because ...",
    "The main reason is that ...",
    "One reason is that ...",
    "... since ...",
    "That's because ...",
    "... because, you see, ...",
    "The reason I say that is ...",
    "I think so because ...",
    "... and that's why ...",
    "... partly because ...",
]
OV_AGREE = [
    "I agree with you.",
    "That's a good point, but ...",
    "I see your point, however ...",
    "I'm not sure I agree.",
    "I partly agree, but ...",
    "I completely agree.",
    "I disagree, because ...",
    "You're right, but ...",
    "I understand your view, yet ...",
    "Hmm, I see it differently.",
]
OV_NEGOTIATE = [
    "So, could we agree that ... ?",
    "Maybe we can both ...",
    "Let's find a middle way.",
    "Would you accept ... ?",
    "Can we compromise and say ... ?",
    "How about we agree that ... ?",
    "Perhaps we can settle on ...",
    "Let's agree on ... then.",
    "Is that a good compromise?",
    "So we both think ..., right?",
]


def variants(bank, i, n=2):
    """Pick `n` variants for card index i, far apart, so each card differs."""
    out = []
    for k in range(n):
        out.append(bank[(i + k * 5) % len(bank)])
    return out


# ---------------------------------------------------------------------------
# SET A - 10 paired structured climate topics (why / effects / what can be done)
# ---------------------------------------------------------------------------
STRUCTURED = [
    {
        "num": 1,
        "title": "Is climate change mainly caused by people?",
        "context": "Most scientists say burning coal, oil and gas is making the world hotter. Some people think it is just a natural cycle.",
        "opener": "Let's talk about why the climate is changing now.",
    },
    {
        "num": 2,
        "title": "Floods and droughts: are they getting worse?",
        "context": "Some countries are having more floods, and others are having longer dry spells. Is climate change really making this happen?",
        "opener": "Shall we talk about all these unusual floods and dry seasons?",
    },
    {
        "num": 3,
        "title": "Can one person really make a difference?",
        "context": "One person recycling or walking to school may seem very small. But everyone doing it together adds up.",
        "opener": "Let's start with what one person can do.",
    },
    {
        "num": 4,
        "title": "Should we stop using petrol and diesel cars?",
        "context": "Cars that use petrol and diesel make a lot of pollution. Electric cars use clean energy, but they can be expensive.",
        "opener": "Should we talk about the cars we use every day?",
    },
    {
        "num": 5,
        "title": "Should governments do more, or is it up to us?",
        "context": "Some say governments and big companies must change the rules. Others say ordinary people also have to change their habits.",
        "opener": "Let's discuss who should act first.",
    },
    {
        "num": 6,
        "title": "Does climate change affect poor countries more?",
        "context": "Countries with less money often have more floods and droughts, and fewer ways to protect themselves.",
        "opener": "What do you think about the flood in Nepal?",
    },
    {
        "num": 7,
        "title": "Should we use more solar and wind energy?",
        "context": "Solar and wind power come from the sun and the air, so they make little pollution. Some say they are not reliable enough yet.",
        "opener": "Let's begin with the energy we all use.",
    },
    {
        "num": 8,
        "title": "Is it fair that some countries pollute more than others?",
        "context": "Rich countries have made most of the pollution, but poor countries often suffer the worst weather.",
        "opener": "Should we talk about who caused the problem?",
    },
    {
        "num": 9,
        "title": "Should schools teach more about climate change?",
        "context": "Students learn about the planet in science and geography. Some say schools should teach even more so young people can act.",
        "opener": "Let's talk about what we learn at school.",
    },
    {
        "num": 10,
        "title": "How will a warmer world change where people live?",
        "context": "If the sea rises and the weather gets hotter, some places may become difficult or impossible to live in.",
        "opener": "Let's discuss where people might move in the future.",
    },
]

# ---------------------------------------------------------------------------
# SET B - 6 bare cards (not paired) evoking feelings about social responsibility
# ---------------------------------------------------------------------------
BARE = [
    {"num": 1, "prompt": "How do you feel when you see litter or plastic in your street?"},
    {"num": 2, "prompt": "Should richer people feel a duty to help poorer people? Why?"},
    {"num": 3, "prompt": "Do you feel responsible for helping families hit by floods?"},
    {"num": 4, "prompt": "Is it fair that some countries pollute more than others? How does that make you feel?"},
    {"num": 5, "prompt": "Would you give up something you enjoy to help the planet?"},
    {"num": 6, "prompt": "Do you believe that your own choices really matter? How do you feel about that?"},
]
BARE_HINT = "How do you feel?"


# ---------------------------------------------------------------------------
# Template
# ---------------------------------------------------------------------------
TEMPLATE = Template(r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  @page { size: A4; margin: 13mm 15mm; }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: 'Roboto', 'Segoe UI', Arial, sans-serif; color: #111; }

  .page { page-break-after: always; }
  .page:last-child { page-break-after: auto; }

  /* ---------- STRUCTURED (Set A): one topic per page, 2 side-by-side cards ---------- */
  .grid-structured {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 6mm;
    align-items: stretch;
  }
  .card {
    border: 1.2px solid #2c3e50;
    border-radius: 6px;
    padding: 7mm 8mm;
    background: #fff;
    break-inside: avoid;
    display: flex;
    flex-direction: column;
    min-height: 240mm;
  }
  .card .badge {
    display: inline-block;
    background: #1a1a2e;
    color: #fff;
    font-size: 12pt;
    font-weight: 700;
    padding: 1.5mm 3mm;
    border-radius: 3px;
    margin-bottom: 3mm;
    align-self: flex-start;
  }
  .card h2 {
    font-size: 19pt;
    font-weight: 700;
    line-height: 1.15;
    margin-bottom: 2.5mm;
  }
  .card .context {
    font-size: 12.5pt;
    line-height: 1.35;
    color: #333;
    margin-bottom: 1mm;
  }
  .card .label {
    font-size: 11pt;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    color: #666;
    margin: 4mm 0 1.5mm 0;
    border-top: 0.8px solid #ddd;
    padding-top: 3mm;
  }
  .card ol.structure {
    list-style: none;
    font-size: 12.5pt;
    line-height: 1.35;
  }
  .card ol.structure li {
    margin-bottom: 1mm;
    padding-left: 4.5mm;
    position: relative;
  }
  .card ol.structure li::before {
    content: "\25B8";
    position: absolute;
    left: 0;
    color: #9b59b6;
    font-weight: 700;
  }
  .card ol.structure li strong { color: #1a1a2e; }
  .card ol.structure li em { color: #333; }
  .card .lang-box {
    background: #eef2f7;
    border-left: 3px solid #1a1a2e;
    border-radius: 3px;
    padding: 3mm 4mm;
    margin-top: 3mm;
    flex: 1;
    font-size: 11.5pt;
  }
  .card .lang-box .lang-func {
    font-size: 10.5pt;
    font-weight: 700;
    color: #9b59b6;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: 2mm;
  }
  .card .lang-box .lang-func:first-child { margin-top: 0; }
  .card .lang-box ul {
    list-style: none;
    line-height: 1.4;
  }
  .card .lang-box ul li {
    margin-bottom: 0.6mm;
    padding-left: 3.5mm;
    position: relative;
  }
  .card .lang-box ul li::before {
    content: "\2022";
    position: absolute;
    left: 0;
    color: #1a1a2e;
    font-weight: 700;
  }

  /* ---------- BARE (Set B): 6 per page, single column ---------- */
  .grid-bare {
    display: grid;
    grid-template-rows: repeat(6, 1fr);
    gap: 4mm;
    height: 271mm;
  }
  .bare-card {
    border: 1.2px solid #2c3e50;
    border-radius: 6px;
    padding: 3mm 7mm;
    display: flex;
    align-items: center;
    gap: 6mm;
    break-inside: avoid;
  }
  .bare-card .num {
    font-size: 13pt;
    font-weight: 700;
    color: #1a1a2e;
    flex: 0 0 auto;
  }
  .bare-card .prompt {
    font-size: 14pt;
    font-weight: 700;
    line-height: 1.2;
    text-align: left;
    flex: 1 1 auto;
  }
  .bare-card .hint {
    font-size: 9pt;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    flex: 0 0 auto;
  }
</style>
</head>
<body>
{% for page in pages %}
<div class="page">
  {% if page.kind == "structured" %}
  <div class="grid-structured">
    {% for c in page.cards %}
    <div class="card">
      <div><span class="badge">Speaking Cue Card {{ c.num }}{% if c.dup %} · {{ c.dup }}{% endif %}</span></div>
      <h2>{{ c.title }}</h2>
      <div class="context">{{ c.context }}</div>
      <div class="label">Structure your discussion</div>
      <ol class="structure">
        <li><strong>Open:</strong> <em>&ldquo;{{ c.opener }}&rdquo;</em></li>
        <li><strong>Opinion:</strong> <em>Give your opinion.</em></li>
        <li><strong>Reason:</strong> <em>Give a reason for your opinion.</em></li>
        <li><strong>Agree / disagree:</strong> <em>Listen, then agree or disagree.</em></li>
        <li><strong>Agreement:</strong> <em>Try to reach a compromise together.</em></li>
      </ol>
      <div class="lang-box">
        <div class="label" style="border-top:none;padding-top:0;margin-top:0;margin-bottom:1mm">Language you can use</div>
        {% for func, items in c.lang %}
        <div class="lang-func">{{ func }}</div>
        <ul>{% for l in items %}<li>{{ l }}</li>{% endfor %}</ul>
        {% endfor %}
      </div>
    </div>
    {% endfor %}
  </div>
  {% else %}
  <div class="grid-bare">
    {% for c in page.cards %}
    <div class="bare-card">
      <span class="num">{{ c.num }}</span>
      <span class="prompt">{{ c.prompt }}</span>
      <span class="hint">{{ c.hint }}</span>
    </div>
    {% endfor %}
  </div>
  {% endif %}
</div>
{% endfor %}
</body>
</html>
""")


# ---------------------------------------------------------------------------
# Builders
# ---------------------------------------------------------------------------
def build_lang(i):
    return [
        ("To open", variants(OV_OPEN, i)),
        ("To give an opinion", variants(OV_OPINION, i)),
        ("To give a reason", variants(OV_REASON, i)),
        ("To agree / disagree", variants(OV_AGREE, i)),
        ("To reach agreement", variants(OV_NEGOTIATE, i)),
    ]


def build_structured_pages(cards, copies=2):
    pages = []
    for idx, c in enumerate(cards):
        page_cards = []
        for i in range(1, copies + 1):
            page_cards.append({
                **c,
                "dup": f"copy {i}",
                "lang": build_lang(idx),
            })
        pages.append({"kind": "structured", "cards": page_cards})
    return pages


def build_bare_pages(cards):
    return [{"kind": "bare", "cards": cards}]


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------
def render_html(template, pages, out_html):
    out_html.write_text(template.render(pages=pages), encoding="utf-8")


def render_pdf(html_path, pdf_path):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(device_scale_factor=1)
        page.goto(html_path.as_uri())
        page.pdf(path=str(pdf_path), format="A4", print_background=True,
                 margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
        browser.close()


def flatten(gs, pdf_path, timeout=120):
    import subprocess
    tmp = pdf_path.with_suffix(".tmp.pdf")
    subprocess.run(
        ["gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite",
         "-dPDFSETTINGS=/prepress", f"-sOutputFile={tmp}",
         "-dCompatibilityLevel=1.7", str(pdf_path)],
        check=True, timeout=timeout,
    )
    tmp.replace(pdf_path)


def main():
    template = TEMPLATE
    jobs = [
        ("speaking-climate-setA-structured.pdf", build_structured_pages(STRUCTURED)),
        ("speaking-climate-setB-bare.pdf", build_bare_pages(BARE)),
    ]
    for fname, pages in jobs:
        html_path = PROJ / fname.replace(".pdf", ".html")
        pdf_path = PROJ / fname
        render_html(template, pages, html_path)
        render_pdf(html_path, pdf_path)
        flatten("gs", pdf_path)
        print(f"[ok] {pdf_path.name}  ({len(pages)} page(s))")


if __name__ == "__main__":
    main()
