"""generate_transcript.py — Printable A4 transcript for the Nepal flood interview.

Reads transcript.json (speaker/text turns) and renders a teacher-readable
tapescript PDF. The interview is split into the same four parts used in the
lesson slides (Part 1-4). Speaker names bold, line beneath, one turn per
block, part headings matching the deck.

Usage:
    python3 "PROJECTS/LISTENING M2/generate_transcript.py"
"""

import html
import json
import subprocess
import sys
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent
TRANSCRIPT_JSON = OUT_DIR / "transcript.json"
HTML_PATH = OUT_DIR / "transcript.html"
PDF_PATH = OUT_DIR / "M2-4A-Listening-Transcript.pdf"

# Part boundaries = turn index ranges into the JSON transcript array.
# These match the CHUNKS structure used to build the audio and the deck.
PART_BOUNDARIES = [0, 8, 16, 22, 32]  # Part 1:0-7, 2:8-15, 3:16-21, 4:22-31

DOC_TITLE = "The flood at the China-Nepal border"
DOC_SUBTITLE = "Listening Transcript &middot; M2-4A &middot; World Stories radio interview"

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
    margin-bottom: 6mm;
    border-bottom: 2px solid #1a1a2e;
    padding-bottom: 4mm;
  }
  .doc-title h1 {
    font-size: 19pt;
    color: #1a1a2e;
    letter-spacing: 0.6px;
  }
  .doc-title .tag {
    font-size: 11pt;
    color: #666;
    margin-top: 1.5mm;
  }
  .part-heading {
    font-size: 15pt;
    font-weight: 700;
    background: #1a1a2e;
    color: #fff;
    padding: 2mm 4mm;
    margin-bottom: 3mm;
    border-left: 4px solid #c0392b;
    page-break-after: avoid;
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
</style>
</head>
<body>
{document}
</body>
</html>
"""


def load_turns() -> list[dict]:
    data = json.loads(TRANSCRIPT_JSON.read_text(encoding="utf-8"))
    turns = data if isinstance(data, list) else data.get("transcript", [])
    return turns


def build_part(index: int, turns: list[dict], first: bool) -> str:
    blocks = []
    for turn in turns:
        speaker = html.escape(turn["speaker"].strip())
        line = html.escape(turn["text"].strip())
        blocks.append(
            f'<div class="turn">\n'
            f'  <div class="speaker">{speaker}</div>\n'
            f'  <div class="line">{line}</div>\n'
            f'</div>'
        )
    heading = f"<h2 class=\"part-heading\">Part {index}</h2>"
    return heading + "\n" + "\n".join(blocks)


def build_document(turns: list[dict]) -> str:
    parts = [
        '<div class="doc-title">'
        f"<h1>{DOC_TITLE}</h1>"
        f'<div class="tag">{DOC_SUBTITLE}</div>'
        "</div>"
    ]
    for i in range(len(PART_BOUNDARIES) - 1):
        start = PART_BOUNDARIES[i]
        end = PART_BOUNDARIES[i + 1]
        part_turns = turns[start:end]
        parts.append(build_part(i + 1, part_turns, first=(i == 0)))
    return "\n".join(parts)


def main() -> None:
    turns = load_turns()
    html_str = HTML_TEMPLATE.replace("{document}", build_document(turns))
    HTML_PATH.write_text(html_str, encoding="utf-8")
    print(f"HTML written to {HTML_PATH.name}")

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Playwright not installed.", file=sys.stderr)
        sys.exit(1)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(HTML_PATH.absolute().as_uri())
        page.pdf(path=str(PDF_PATH), format="A4", print_background=True,
                 margin={"top": "12mm", "bottom": "12mm",
                         "left": "12mm", "right": "12mm"})
        browser.close()
    print(f"PDF written to {PDF_PATH.name}")


if __name__ == "__main__":
    main()
