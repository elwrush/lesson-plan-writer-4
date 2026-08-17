"""Generate essay topic cards, 4 per A4 landscape page, using Playwright.

Reads the 10 essay topics verbatim from ESSAY_TOPICS.JSON. Each card shows:
- Numbered header with accent colour and a speech-bubble icon
- The topic context sentences
- The question ("Which opinion do you agree with the most?") in a highlighted box
- An Opinion - Reason - Evidence footer strip

Output: PDF/essay-topic-cards-M3-A.pdf (gh-pages-safe, Ghostscript-flattened).
"""

import json
import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).parent
TOPICS_PATH = PROJECT_DIR / "ESSAY_TOPICS.JSON"
PDF_DIR = Path(__file__).parent.parent.parent / "PDF"
PDF_PATH = PDF_DIR / "essay-topic-cards-M3-A.pdf"

FINAL_QUESTION = "Which opinion do you agree with the most?"

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

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  @page {
    size: A4 landscape;
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
    width: 277mm;
    height: 190mm;
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: 1fr 1fr;
    gap: 6mm;
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
    padding: 4.5mm 5mm;
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
    font-size: 17pt;
    width: 10mm;
    height: 10mm;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    margin-right: 4mm;
    flex-shrink: 0;
  }
  .card-kicker {
    font-size: 12.5pt;
    font-weight: 500;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    opacity: 0.92;
  }
  .icon {
    position: relative;
    width: 9mm;
    height: 9mm;
    flex-shrink: 0;
  }
  .icon-bubble {
    position: absolute;
    top: 0;
    left: 0;
    right: 1.6mm;
    bottom: 1.6mm;
    background: #ffffff;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12.5pt;
    font-weight: 900;
  }
  .icon-tail {
    position: absolute;
    bottom: 0;
    left: 1.6mm;
    width: 0;
    height: 0;
    border-left: 2.4mm solid transparent;
    border-bottom: 2.4mm solid #ffffff;
  }
  .card-body {
    flex: 1;
    padding: 5mm 5.5mm 3mm 5.5mm;
    display: flex;
    flex-direction: column;
  }
  .context-text {
    font-size: 16pt;
    line-height: 1.5;
    color: #222;
  }
  .question-box {
    margin-top: auto;
    border-radius: 0 6px 6px 0;
    padding: 3mm 4mm;
    margin-bottom: 3mm;
  }
  .question-box .question-text {
    font-size: 16.5pt;
    font-weight: 700;
    color: #1a1a2e;
  }
  .card-footer {
    border-top: 1px solid #e3e8ef;
    padding: 2.5mm 5.5mm;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .ore-hint {
    font-size: 11.5pt;
    font-weight: 700;
    color: #8a93a3;
    letter-spacing: 0.6px;
    text-transform: uppercase;
  }
  .ore-hint .sep {
    font-weight: 900;
  }
  .card-page {
    font-size: 11.5pt;
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

CARD_HTML = r"""<div class="card">
  <div class="card-header" style="background:{accent}">
    <div class="card-title">
      <span class="num-badge">{num}</span>
      <span class="card-kicker">Essay Topic</span>
    </div>
    <span class="icon">
      <span class="icon-tail"></span>
      <span class="icon-bubble" style="color:{accent}">?</span>
    </span>
  </div>
  <div class="card-body">
    <div class="context-text">{context}</div>
    <div class="question-box" style="background:{accent_soft};border-left:3px solid {accent}">
      <div class="question-text">{question}</div>
    </div>
  </div>
  <div class="card-footer">
    <span class="ore-hint">Opinion <span class="sep" style="color:{accent}">&mdash;</span> Reason <span class="sep" style="color:{accent}">&mdash;</span> Evidence</span>
    <span class="card-page">Card {num} / {total}</span>
  </div>
</div>
"""


def hex_to_rgba(hex_color: str, alpha: float) -> str:
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"


def main() -> None:
    topics = json.loads(TOPICS_PATH.read_text(encoding="utf-8"))["topics"]
    total = len(topics)

    pages_html = []
    for i in range(0, total, 4):
        chunk = topics[i : i + 4]
        cards = []
        for t in chunk:
            text = t["topic"]
            if text.endswith(FINAL_QUESTION):
                context = text[: -len(FINAL_QUESTION)].rstrip()
                question = FINAL_QUESTION
            else:
                context = text
                question = ""
            accent = PALETTE[(t["id"] - 1) % len(PALETTE)]
            cards.append(
                CARD_HTML.format(
                    num=t["id"],
                    total=total,
                    accent=accent,
                    accent_soft=hex_to_rgba(accent, 0.10),
                    context=context,
                    question=question,
                )
            )
        pages_html.append(
            '<div class="page">' + "".join(cards) + "</div>\n"
        )

    full_html = HTML_TEMPLATE.replace("{pages}", "".join(pages_html))
    html_path = PROJECT_DIR / "topic_cards.html"
    html_path.write_text(full_html, encoding="utf-8")
    print(f"HTML written to {html_path}")

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Playwright not installed. Install with: pip install playwright && playwright install chromium")
        print(f"Open {html_path} in a browser and print to PDF (A4 landscape, background graphics).")
        sys.exit(1)

    PDF_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1400, "height": 1000})
        page.goto(html_path.absolute().as_uri())
        page.pdf(
            path=str(PDF_PATH),
            print_background=True,
            prefer_css_page_size=True,
        )
        browser.close()
    print(f"PDF written to {PDF_PATH}")

    tmp_pdf = PDF_PATH.with_suffix(".tmp.pdf")
    subprocess.run(
        [
            "gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite",
            "-dPDFSETTINGS=/prepress", f"-sOutputFile={tmp_pdf}",
            "-dCompatibilityLevel=1.7", str(PDF_PATH),
        ],
        check=True,
        timeout=120,
    )
    tmp_pdf.replace(PDF_PATH)
    print(f"Flattened PDF via Ghostscript: {PDF_PATH}")


if __name__ == "__main__":
    main()
