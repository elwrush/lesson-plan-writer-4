#!/usr/bin/env python3
"""Generate speed-dating cue cards for the M2-4A speaking follow-up.

Two sets, no school header, just the cards. Jinja2 + Playwright.

SET A (structured)  — five education topics, each card DUPLICATED (2 copies).
  Each card: topic question + brief context + the revised discussion pattern
  (Open -> Your view -> Respond -> Resolution) + a card-specific bank of target
  language cues (e.g. "I firmly believe ...").

SET B (bare)        — five middle-school-friendly topics, TOPIC ONLY, no structure
  cues, no language cues. Each topic appears twice (the duplicate set), printed
  across TWO pages (page 1 = the five topics, page 2 = the same five duplicated).
"""

from pathlib import Path

from jinja2 import Template
from playwright.sync_api import sync_playwright

PROJ = Path(__file__).parent

# ---------------------------------------------------------------------------
# SET A — structured cue cards (education, middle-school friendly)
# ---------------------------------------------------------------------------

STRUCTURED = [
    {
        "num": 1,
        "title": "Should AI be allowed in classrooms?",
        "context": (
            "Some schools let students use AI to help with homework. "
            "Other schools say students should think for themselves."
        ),
        "opener": "Let's start with a big question: should AI be allowed in the classroom?",
        "lang": [
            "I firmly believe that ...",
            "There's no doubt in my mind that ...",
            "That's a good point, but ...",
            "I see it completely differently.",
            "Could you explain why you think that?",
            "To sum up, we both ...",
        ],
    },
    {
        "num": 2,
        "title": "Would school life be better without smartphones?",
        "context": (
            "Before smartphones, students talked and played at break time. "
            "Now many students just look at their phones all day."
        ),
        "opener": "Imagine a school day with no smartphones. Would it be better or worse?",
        "lang": [
            "If I could turn back time, I would ...",
            "Honestly, I think life was simpler then.",
            "I can see why you'd say that, but ...",
            "What do you mean exactly?",
            "Let me put it another way ...",
            "In the end, I'd say ...",
        ],
    },
    {
        "num": 3,
        "title": "Should students wear school uniforms?",
        "context": (
            "Some schools make students wear uniforms. "
            "Other schools let students wear whatever they like."
        ),
        "opener": "Let's talk about what students wear at school.",
        "lang": [
            "From my point of view, ...",
            "It really depends on the school.",
            "I agree with you up to a point.",
            "Hmm, I'm not so sure.",
            "Can you give me an example?",
            "So, if I understand correctly ...",
        ],
    },
    {
        "num": 4,
        "title": "Is homework really necessary?",
        "context": (
            "Homework helps you practise what you learn. "
            "But too much homework can be stressful and take your free time."
        ),
        "opener": "How much homework is too much? Let's find out.",
        "lang": [
            "I believe it's important to ...",
            "The main reason is that ...",
            "That might be true, however ...",
            "Let's think about it another way.",
            "How would you feel if ... ?",
            "All things considered, ...",
        ],
    },
    {
        "num": 5,
        "title": "Should every student learn to code?",
        "context": (
            "Some people say coding is a skill for the future. "
            "Others say art and music are just as important."
        ),
        "opener": "Should coding be a subject for everyone?",
        "lang": [
            "In my opinion, ...",
            "Some people argue that ...",
            "But on the other hand, ...",
            "What I mean is ...",
            "Do you have any experience with ... ?",
            "At the end of the day, ...",
        ],
    },
]

# ---------------------------------------------------------------------------
# SET B — bare topic cue cards (topic only, no structure, no language cues)
# ---------------------------------------------------------------------------

BARE = [
    {"num": 1, "prompt": "Are video games good for you?"},
    {"num": 2, "prompt": "Should children do chores at home?"},
    {"num": 3, "prompt": "Best friend, or many friends?"},
    {"num": 4, "prompt": "Should students only study subjects they like?"},
    {"num": 5, "prompt": "Should children be allowed to take their phones into their bedrooms at night time?"},
]


# ---------------------------------------------------------------------------
# Jinja2 template
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

  /* ---------- STRUCTURED (Set A): one topic per page, 2 side-by-side cards (pair) ---------- */
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
  }
  .card .lang-box ul {
    list-style: none;
    font-size: 12pt;
    line-height: 1.45;
  }
  .card .lang-box ul li {
    margin-bottom: 0.7mm;
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

  /* ---------- BARE (Set B): 5 per page, single column ---------- */
  .grid-bare {
    display: grid;
    grid-template-rows: repeat(5, 1fr);
    gap: 4mm;
    height: 271mm;
  }
  .bare-card {
    border: 1.2px solid #2c3e50;
    border-radius: 6px;
    padding: 2.5mm 7mm;
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
        <li><strong>Your view:</strong> <em>Give your opinion.</em></li>
        <li><strong>Respond:</strong> <em>Listen, then agree or disagree.</em></li>
        <li><strong>Resolution:</strong> <em>Summarise your discussion together.</em></li>
      </ol>
      <div class="lang-box">
        <div class="label" style="border-top:none;padding-top:0;margin-top:0;margin-bottom:1mm">Language you can use</div>
        <ul>
        {% for l in c.lang %}<li>{{ l }}</li>{% endfor %}
        </ul>
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
      <span class="hint">Talk about this</span>
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


def build_structured_pages(cards, copies=2):
    """One topic per page, with `copies` stacked cards (a matched pair)."""
    pages = []
    for c in cards:
        page_cards = []
        for i in range(1, copies + 1):
            page_cards.append({**c, "dup": f"copy {i}"})
        pages.append({"kind": "structured", "cards": page_cards})
    return pages


def build_bare_pages(cards, copies=2):
    """Page 1 = topics 1..5; page 2 = the same five topics (the duplicate set)."""
    pages = []
    for _ in range(copies):
        pages.append({"kind": "bare", "cards": cards})
    return pages


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
        page.pdf(
            path=str(pdf_path),
            format="A4",
            print_background=True,
            margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
        )
        browser.close()


def flatten(gs, pdf_path, timeout=120):
    import subprocess
    tmp = pdf_path.with_suffix(".tmp.pdf")
    subprocess.run(
        [
            "gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite",
            "-dPDFSETTINGS=/prepress", f"-sOutputFile={tmp}",
            "-dCompatibilityLevel=1.7", str(pdf_path),
        ],
        check=True, timeout=timeout,
    )
    tmp.replace(pdf_path)


def main():
    template = TEMPLATE
    out_dir = PROJ
    render_jobs = [
        ("speaking-followup-setA-structured.pdf", build_structured_pages(STRUCTURED)),
        ("speaking-followup-setB-bare.pdf", build_bare_pages(BARE)),
    ]
    for fname, pages in render_jobs:
        html_path = out_dir / fname.replace(".pdf", ".html")
        pdf_path = out_dir / fname
        render_html(template, pages, html_path)
        render_pdf(html_path, pdf_path)
        flatten("gs", pdf_path)
        print(f"[ok] {pdf_path.name}  ({len(pages)} page(s))")


if __name__ == "__main__":
    main()
