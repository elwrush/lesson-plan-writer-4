"""generate_transcripts.py — Model interview transcripts (B1 + B2) as A4 PDF.

One A4 page per model interview (Ploy — B1, Elle — B2), formatted as a
readable tapescript: speaker name in bold, line beneath. The transcript
text is parsed from the source markdown dialogs (dialog-b1-ploy.md and
dialog-b2-elle.md) so the PDF can never drift from the authored dialogs.
The markdown sources use the real spellings ("MUIDS", "Mathayom 3") —
never the TTS respellings ("em-yoo-eye-dee-es", "muttiyom") that live in
the dialog JSON used for audio generation.

Usage:
    python3 "PROJECTS/INTERVIEW SPEAKING/generate_transcripts.py"
"""

import html
import re
import subprocess
import sys
from pathlib import Path

OUT_DIR = Path(__file__).parent
PDF_PATH = OUT_DIR / "Interview-Transcripts.pdf"

B1_SOURCE = OUT_DIR / "dialog-b1-ploy.md"
B2_SOURCE = OUT_DIR / "dialog-b2-elle.md"

TURN_RE = re.compile(r"^\*\*([^*]+):\*\*\s*(.+)$")
SETTING_RE = re.compile(r"^\*(.+)\*$")
TITLE_RE = re.compile(r"^###\s+(.+)$")

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
  .doc-title {
    text-align: center;
    margin-bottom: 4mm;
  }
  .doc-title h1 {
    font-size: 18pt;
    color: #1a1a2e;
    letter-spacing: 0.6px;
    text-transform: uppercase;
  }
  .doc-title .tag {
    font-size: 11pt;
    color: #666;
    margin-top: 1mm;
  }
  .interview-heading {
    font-size: 15pt;
    font-weight: 700;
    background: #1a1a2e;
    color: #fff;
    padding: 2mm 4mm;
    margin-bottom: 1.5mm;
    border-left: 4px solid #9b59b6;
  }
  .setting {
    font-size: 11pt;
    font-style: italic;
    color: #666;
    margin-bottom: 4mm;
  }
  .turn {
    page-break-inside: avoid;
    margin-bottom: 2.8mm;
  }
  .speaker {
    font-size: 10pt;
    font-weight: 700;
    color: #1a1a2e;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 0.6mm;
  }
  .line {
    font-size: 12pt;
    line-height: 1.42;
    color: #222;
    border-left: 2px solid #d5dbe8;
    padding-left: 3mm;
  }
  .page-break {
    page-break-before: always;
  }
</style>
</head>
<body>
{document}
</body>
</html>
"""

INTERVIEW_BLOCK = """<h2 class="interview-heading">{title}</h2>
<div class="setting">{setting}</div>
{turns}
"""


def parse_dialog(path: Path) -> dict:
    title, setting, turns = None, None, []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        m = TURN_RE.match(line)
        if m:
            turns.append({"speaker": m.group(1).strip(), "line": m.group(2).strip()})
            continue
        m = TITLE_RE.match(line)
        if m:
            title = m.group(1).strip()
            continue
        m = SETTING_RE.match(line)
        if m:
            setting = m.group(1).strip()
    return {"title": title, "setting": setting, "turns": turns}


def build_turns(turns: list[dict]) -> str:
    blocks = []
    for turn in turns:
        speaker = html.escape(turn["speaker"])
        line = html.escape(turn["line"])
        blocks.append(
            f'<div class="turn">\n'
            f'  <div class="speaker">{speaker}</div>\n'
            f'  <div class="line">{line}</div>\n'
            f'</div>'
        )
    return "\n".join(blocks)


def build_interview(dialog: dict, first: bool) -> str:
    title = html.escape(dialog["title"]) if dialog["title"] else ""
    setting = html.escape(dialog["setting"]) if dialog["setting"] else ""
    turns = build_turns(dialog["turns"])
    block = INTERVIEW_BLOCK.format(title=title, setting=setting, turns=turns)
    if not first:
        block = f'<div class="page-break"></div>\n{block}'
    return block


def build_document() -> str:
    dialogs = [parse_dialog(B1_SOURCE), parse_dialog(B2_SOURCE)]
    parts = [
        '<div class="doc-title">'
        "<h1>Interview Transcripts</h1>"
        '<div class="tag">M2 &middot; M3 &middot; CEFR B1 &middot; Interview Speaking</div>'
        "</div>"
    ]
    for i, dialog in enumerate(dialogs):
        parts.append(build_interview(dialog, first=(i == 0)))
    return "\n".join(parts)


def main() -> None:
    html_path = OUT_DIR / "interview_transcripts.html"
    html_path.write_text(
        HTML_TEMPLATE.replace("{document}", build_document()), encoding="utf-8"
    )
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
