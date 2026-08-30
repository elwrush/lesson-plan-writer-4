"""generate_sentence_strips.py — Sentence cut-up interviews (B1 + B2).

Each A4 page is ONE complete mini-interview published as a table: one sentence
per row, generous row spacing for cutting, dashed cut lines, no instructions.
Interviewer questions and student responses (including the PREP parts inside
each answer) are all unlabeled — students reorder the strips, then practise.

All sentences are brand-new (guitar / weekend-balance topics) — they do not
reuse any of the model interview dialogs.

Usage:
    python3 "PROJECTS/INTERVIEW SPEAKING/generate_sentence_strips.py"
"""

import subprocess
import sys
from pathlib import Path

OUT_DIR = Path(__file__).parent

B1_STRIPS = [
    "Good morning. What do you enjoy doing in your free time?",
    "I really like playing the guitar.",
    "It helps me relax after a long day at school.",
    "For example, I practise for thirty minutes every evening.",
    "So music is my favourite way to unwind.",
    "That's nice. Do you play in a band?",
    "Not yet, but I'd love to.",
    "I think playing with other people is the best way to improve.",
    "For example, my cousin plays with his friends every weekend.",
    "Lovely. Thank you for coming today.",
    "Thank you. Goodbye.",
]

B2_STRIPS = [
    "So, tell me — how do you usually spend your weekends?",
    "That's a good question. Honestly, I try to keep a balance between relaxing and doing something useful.",
    "The main reason is that I think weekends are for recharging, not just for homework.",
    "For example, on Saturday mornings I help my family at our market stall, and in the afternoon I swim.",
    "However, I also spend a couple of hours on Sunday studying, especially English.",
    "So, for me, a good weekend has both fun and a little work.",
    "That sounds well planned. And what's something new you'd like to try?",
    "I'd love to learn scuba diving.",
    "I've watched documentaries about coral reefs, and I find the underwater world fascinating.",
    "For example, a friend of mine started diving last year, and she says it's the most peaceful feeling in the world.",
    "Wonderful. Thank you for coming. We'll be in touch soon.",
    "Thank you very much. It was a pleasure.",
]

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  @page { size: A4; margin: 8mm; }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: 'Roboto', 'Segoe UI', Arial, sans-serif; color: #222; }
  table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0 0.8cm;
    table-layout: fixed;
  }
  td {
    border: 1.5px dashed #888;
    border-radius: 3px;
    text-align: center;
    vertical-align: middle;
    padding: 0.35cm 3mm;
    font-size: 12.5pt;
    line-height: 1.35;
  }
</style>
</head>
<body>
<table>
{rows}
</table>
</body>
</html>
"""


def build_page(strips: list[str]) -> str:
    rows = "\n".join(f"<tr><td>{s}</td></tr>" for s in strips)
    return HTML_TEMPLATE.replace("{rows}", rows)


def render_pdf(page_html: str, pdf_path: Path) -> None:
    tmp_html = OUT_DIR / f"_strip_{pdf_path.stem}.html"
    tmp_html.write_text(page_html, encoding="utf-8")
    with __import__("playwright.sync_api", fromlist=["sync_playwright"]).sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(tmp_html.absolute().as_uri())
        page.pdf(path=str(pdf_path), format="A4", print_background=True)
        browser.close()
    tmp_html.unlink(missing_ok=True)
    print(f"PDF written to {pdf_path}")

    tmp_pdf = pdf_path.with_suffix(".tmp.pdf")
    subprocess.run(
        ["gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite",
         "-dPDFSETTINGS=/prepress", f"-sOutputFile={tmp_pdf}",
         "-dCompatibilityLevel=1.7", str(pdf_path)],
        check=True, timeout=120,
    )
    tmp_pdf.replace(pdf_path)
    print(f"Flattened PDF via Ghostscript: {pdf_path}")


def main() -> None:
    try:
        import playwright  # noqa: F401
    except ImportError:
        print("Playwright not installed. Install with: pip install playwright && playwright install chromium")
        sys.exit(1)

    render_pdf(build_page(B1_STRIPS), OUT_DIR / "Sentence-CutUp-B1.pdf")
    render_pdf(build_page(B2_STRIPS), OUT_DIR / "Sentence-CutUp-B2.pdf")


if __name__ == "__main__":
    main()
