#!/usr/bin/env python3
"""Generate the B1 Compound & Complex Sentences worksheet via the shared
write-test-worksheet worksheet template (single generic 2-page file).

Recall (name the type + construct) flows into Use. No per-student demographic
block — answer sheets are printed separately. The look-and-feel (masthead, CSS,
section markup) comes from the skill's templates/worksheet.html, so this script
only supplies validated content.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

SKILL_ROOT = Path(os.environ.get("SKILL_ROOT", str(Path.home() / ".kilo" / "skills" / "write-test-worksheet")))
sys.path.insert(0, str(SKILL_ROOT / "scripts"))
from render import render_worksheet
from worksheet_content import WorksheetContent

PROJECT_ROOT = Path(os.environ.get("LESSON_PLAN_WRITER_ROOT", "/mnt/c/PROJECTS/LESSON-PLAN-WRITER-4"))

OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", str(PROJECT_ROOT / "PROJECTS" / "AUG 4 M2-4A COMPOUND-COMPLEX")))

PAGES_PER_STUDENT = 2  # Recall A+B flows, then Use — no forced breaks
EXPECTED_TOTAL_PAGES = PAGES_PER_STUDENT

CONTENT = {
    "title": "Writing Compound & Complex Sentences",
    "cefr_tag": "CEFR B1 · Recall · Use",
    "sections": [
        {"type": "heading", "text": "Recall — Part A: Name the sentence type"},
        {
            "type": "instructions",
            "text": (
                "<strong>Instructions:</strong> Label each sentence <strong>CO</strong> (coordinator), "
                "<strong>CA</strong> (conjunctive adverb), <strong>S</strong> (semicolon), or "
                "<strong>CX</strong> (complex). <strong>Circle</strong> the connector that joins the ideas."
            ),
        },
        {
            "type": "task1_sentence",
            "items": [
                {"num": 1, "text": "I wanted pizza, <span class=\"boxed\">but</span> the shop was closed.<span class=\"label-box\"></span>"},
                {"num": 2, "text": "She was exhausted; she could hardly keep her eyes open.<span class=\"label-box\"></span>"},
                {"num": 3, "text": "<span class=\"boxed\">Because</span> it was late, we left.<span class=\"label-box\"></span>"},
                {"num": 4, "text": "He studied hard; <span class=\"boxed\">however</span>, he failed.<span class=\"label-box\"></span>"},
                {"num": 5, "text": "Do you want tea, <span class=\"boxed\">or</span> do you want coffee?<span class=\"label-box\"></span>"},
                {"num": 6, "text": "<span class=\"boxed\">If</span> you practise, you will improve.<span class=\"label-box\"></span>"},
                {"num": 7, "text": "She opened the door; the room was empty.<span class=\"label-box\"></span>"},
                {"num": 8, "text": "I was hungry, <span class=\"boxed\">so</span> I made a sandwich.<span class=\"label-box\"></span>"},
            ],
        },
        {"type": "heading", "text": "Recall — Part B: Construct the sentences"},
        {
            "type": "instructions",
            "text": (
                "<strong>Instructions:</strong> Join the two ideas with the connector in brackets. "
                "<strong>Write the whole new sentence</strong> with correct punctuation."
            ),
        },
        {
            "type": "join_item",
            "items": [
                {"num": 1, "text": "Join with <strong>but</strong>: She was tired. She kept working.", "lines": 1},
                {"num": 2, "text": "Join with <strong>however</strong>: The plan was risky. It worked well.", "lines": 1},
                {"num": 3, "text": "Join with <strong>because</strong>: He was late. He missed the bus.", "lines": 1},
                {"num": 4, "text": "Join with a <strong>semicolon</strong>: The days were hot. The nights were cool.", "lines": 1},
                {"num": 5, "text": "Join with <strong>and</strong>: He likes football. His brother likes basketball.", "lines": 1},
                {"num": 6, "text": "Join with <strong>so</strong>: I was hungry. I made a sandwich.", "lines": 1},
                {"num": 7, "text": "Join with <strong>or</strong>: We can watch a film. We can play a game.", "lines": 1},
                {"num": 8, "text": "Join with <strong>therefore</strong>: She studied all week. She passed the exam.", "lines": 1},
                {"num": 9, "text": "Join with <strong>when</strong>: I get home. I do my homework.", "lines": 1},
                {"num": 10, "text": "Join with <strong>if</strong>: You practise every day. You will improve.", "lines": 1},
            ],
        },
        {"type": "heading", "text": "Use — Write a paragraph"},
        {
            "type": "instructions",
            "text": (
                "<strong>Instructions:</strong> Write a paragraph of <strong>70–80 words</strong> "
                "describing a busy weekend day. Use every sentence type you learned."
            ),
        },
        {
            "type": "writing_prompt",
            "text": (
                "<strong>Include all of the following in your paragraph:</strong>\n"
                '<ul style="margin:0.3em 0 0 0;padding-left:1.2em;">\n'
                "  <li>a compound sentence with a coordinator (<em>and, but, so, or</em>) — with a comma before it</li>\n"
                "  <li>a compound sentence with a conjunctive adverb (<em>however</em> or <em>therefore</em>) — with a semicolon before it</li>\n"
                "  <li>a compound sentence with a semicolon</li>\n"
                "  <li>a complex sentence with an adverb clause (<em>because, when, if</em> or <em>although</em>)</li>\n"
                "</ul>"
            ),
        },
    ],
}


def count_pdf_pages(path: Path) -> int:
    try:
        result = subprocess.run(
            ["pdfinfo", str(path)],
            capture_output=True, text=True, timeout=15
        )
        for line in result.stdout.splitlines():
            if line.startswith("Pages"):
                return int(line.split(":", 1)[1].strip())
    except Exception:
        pass
    return 0


def main():
    parser = argparse.ArgumentParser(description="Generate the B1 Compound & Complex Sentences worksheet (single generic file).")
    parser.add_argument("--output-dir", default=str(OUTPUT_DIR))
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_pdf = output_dir / "Compound-Complex-Sentences-Worksheet-B1.pdf"

    content = WorksheetContent.model_validate(CONTENT)
    render_worksheet(content, output_pdf)

    pages = count_pdf_pages(output_pdf)
    if pages != EXPECTED_TOTAL_PAGES:
        print(f"LINT FAILURE: expected {EXPECTED_TOTAL_PAGES} pages, got {pages}")
        sys.exit(1)

    print(f"Wrote {output_pdf} ({pages} pages)")


if __name__ == "__main__":
    main()
