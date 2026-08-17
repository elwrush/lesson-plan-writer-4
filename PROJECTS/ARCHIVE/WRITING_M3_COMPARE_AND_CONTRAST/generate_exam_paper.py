#!/usr/bin/env python3
"""Generate the M3 compare-and-contrast essay exam paper via the shared
write-test-worksheet template (single generic A4 file, no per-student boxes).

Students choose ONE of three essay topics that were NOT used in the lesson or
the cue cards (cinema vs home viewing, paper books vs e-books, online vs mall
shopping), and write a compare-and-contrast essay of at least 200 words using
the four-paragraph shape and linking words taught in the unit. The look-and-feel
(masthead, CSS, section markup) comes from the skill's templates/worksheet.html,
so this script only supplies validated content.
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

OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", str(PROJECT_ROOT / "PDF")))

EXPECTED_TOTAL_PAGES = 1  # single page: task, instructions, and topics

CONTENT = {
    "title": "M3 Writing Examination \u2014 A Compare and Contrast Essay",
    "cefr_tag": "CEFR B1 \u00b7 Writing \u00b7 40 minutes \u00b7 Minimum 200 words",
    "sections": [
        {"type": "heading", "text": "Writing Task"},
        {
            "type": "instructions",
            "text": (
                "<strong>Instructions:</strong> Write a compare and contrast essay. "
                "Choose <strong>ONE</strong> of the three topics below and answer the question at the end.\n"
                '<ol style="margin:0.3em 0 0 0;padding-left:1.3em;">'
                "<li>Read the question twice. Underline the topic and circle both opinions.</li>"
                "<li>Choose the side you agree with. No side is wrong, but you must choose one.</li>"
                "<li>Plan your ideas: list positives and negatives for both sides, then keep "
                "your three strongest points.</li>"
                "<li>Write four paragraphs: an introduction, one paragraph for each side, and a "
                "conclusion that gives your opinion.</li>"
                "<li>Use linking words such as <strong>However</strong>, "
                "<strong>On the other hand</strong>, <strong>Whereas</strong>, and "
                "<strong>In conclusion</strong>.</li>"
                "<li>Write at least <strong>200 words</strong>. Count your words at the end.</li>"
                "</ol>"
            ),
        },
        {"type": "heading", "text": "Choose one topic"},
        {
            "type": "writing_prompt",
            "text": (
                '<ol style="margin:0;padding-left:1.3em;">'
                "<li>Watching a film at the cinema is an exciting night out. Many people love the "
                "big screen and the loud sound, but others say it is cheaper and more comfortable "
                "to watch films at home on a TV or laptop. Which opinion do you agree with the most?</li>"
                "<li>Printed books have existed for hundreds of years, but many people now read "
                "e-books on a phone or tablet. Some readers say paper books feel better in their "
                "hands, while others say e-books are cheaper and easier to carry. Which opinion do "
                "you agree with the most?</li>"
                "<li>Online shopping is growing quickly in Thailand. Many people buy almost "
                "everything on their phone and have it delivered, but others prefer to visit a "
                "shopping mall, see the product, and try it before they pay. Which opinion do you "
                "agree with the most?</li>"
                "</ol>"
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
    parser = argparse.ArgumentParser(
        description="Generate the M3 compare-and-contrast essay exam paper (single generic file)."
    )
    parser.add_argument("--output-dir", default=str(OUTPUT_DIR))
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_pdf = output_dir / "M3-Compare-and-Contrast-Exam-Paper.pdf"

    content = WorksheetContent.model_validate(CONTENT)
    render_worksheet(content, output_pdf)

    pages = count_pdf_pages(output_pdf)
    if pages != EXPECTED_TOTAL_PAGES:
        print(f"LINT FAILURE: expected {EXPECTED_TOTAL_PAGES} pages, got {pages}")
        sys.exit(1)

    print(f"Wrote {output_pdf} ({pages} pages)")


if __name__ == "__main__":
    main()
