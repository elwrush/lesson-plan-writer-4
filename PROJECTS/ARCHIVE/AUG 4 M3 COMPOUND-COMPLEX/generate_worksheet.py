#!/usr/bin/env python3
"""Generate the B2 Compound & Complex Sentences worksheet via the shared
write-test-worksheet worksheet template (single generic 2-page file).

Recall (choose the connector + rewrite the pairs) flows into Use. No per-student
demographic block — answer sheets are printed separately. The look-and-feel
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

OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", str(PROJECT_ROOT / "PROJECTS" / "AUG 4 M3 COMPOUND-COMPLEX")))

PAGES_PER_STUDENT = 2  # Recall A+B flows, then Use — no forced breaks
EXPECTED_TOTAL_PAGES = PAGES_PER_STUDENT

CONTENT = {
    "title": "Writing Compound & Complex Sentences",
    "cefr_tag": "CEFR B2 · Recall · Use",
    "sections": [
        {"type": "heading", "text": "Recall — Part A: Choose the connector"},
        {
            "type": "instructions",
            "text": (
                "<strong>Instructions:</strong> Complete each sentence with the best word from the box. "
                "Use each word <strong>once</strong>. Conjunctive adverbs come after a semicolon "
                "<strong>;</strong> and before a comma <strong>,</strong>. <strong>Although</strong> "
                "takes a comma, not a semicolon."
            ),
        },
        {
            "type": "word_bank",
            "words": ["however", "therefore", "moreover", "otherwise", "meanwhile", "although"],
        },
        {
            "type": "gap_sentence",
            "items": [
                {"num": 1, "text": "He missed the deadline; ________, he lost the contract."},
                {"num": 2, "text": "I will start the dinner; ________, you can set the table."},
                {"num": 3, "text": "You must book early; ________, all the rooms will be taken."},
                {"num": 4, "text": "________ the economy improved, unemployment stayed high."},
                {"num": 5, "text": "The hotel was full; ________, we found another place to stay."},
                {"num": 6, "text": "She is a great writer; ________, her novel won a prize."},
            ],
        },
        {"type": "heading", "text": "Recall — Part B: Rewrite the pairs"},
        {
            "type": "instructions",
            "text": (
                "<strong>Instructions:</strong> Rewrite each pair as <strong>one sentence</strong> "
                "using the joining method in brackets. Write the whole new sentence with correct "
                "punctuation."
            ),
        },
        {
            "type": "join_item",
            "items": [
                {"num": 1, "text": "Join with <strong>however</strong>: The plan was risky. It worked well.", "lines": 1},
                {"num": 2, "text": "Join with a <strong>semicolon</strong>: The first half of the film was slow. The second half was thrilling.", "lines": 1},
                {"num": 3, "text": "Join with <strong>although</strong>: The team trained hard. They lost the final.", "lines": 1},
                {"num": 4, "text": "Join with <strong>unless</strong>: You must arrive early. You will not get a seat.", "lines": 1},
                {"num": 5, "text": "Join with <strong>therefore</strong>: The evidence was clear. The jury agreed quickly.", "lines": 1},
                {"num": 6, "text": "Join with <strong>meanwhile</strong>: I prepared the questions. My colleague booked the room.", "lines": 1},
                {"num": 7, "text": "Join with <strong>otherwise</strong>: We must leave now. We will miss the last train.", "lines": 1},
                {"num": 8, "text": "Join with <strong>while</strong>: I cooked dinner. My brother set the table.", "lines": 1},
                {"num": 9, "text": "Join with <strong>when</strong>: The storm ended. Everyone came out of their houses.", "lines": 1},
                {"num": 10, "text": "Join with a <strong>semicolon</strong>: The cafe was packed. Every table was taken.", "lines": 1},
            ],
        },
        {"type": "heading", "text": "Use — Write a paragraph"},
        {
            "type": "instructions",
            "text": (
                "<strong>Instructions:</strong> Write a paragraph of <strong>90–120 words</strong> "
                "giving your opinion. Choose <strong>one</strong> topic and support it with clear reasons."
            ),
        },
        {
            "type": "writing_prompt",
            "text": (
                "<strong>Choose one topic:</strong>\n"
                '<ul style="margin:0.3em 0 0 0;padding-left:1.2em;">\n'
                "  <li>Schools should require students to wear uniforms.</li>\n"
                "  <li>Students should choose their own clothes for school.</li>\n"
                "</ul>"
            ),
        },
        {
            "type": "writing_prompt",
            "text": (
                "<strong>Include all of the following in your paragraph:</strong>\n"
                '<ul style="margin:0.3em 0 0 0;padding-left:1.2em;">\n'
                "  <li>at least 2 compound sentences — one with a semicolon or a conjunctive adverb "
                "(<em>however, therefore, meanwhile</em>)</li>\n"
                "  <li>at least 2 complex sentences with adverb clauses "
                "(<em>because, although, while, unless, when</em>)</li>\n"
                "  <li>a comma before <em>and, but, so</em> or <em>or</em> when they join two main ideas</li>\n"
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
    parser = argparse.ArgumentParser(description="Generate the B2 Compound & Complex Sentences worksheet (single generic file).")
    parser.add_argument("--output-dir", default=str(OUTPUT_DIR))
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_pdf = output_dir / "Compound-Complex-Sentences-Worksheet-B2.pdf"

    content = WorksheetContent.model_validate(CONTENT)
    render_worksheet(content, output_pdf)

    pages = count_pdf_pages(output_pdf)
    if pages != EXPECTED_TOTAL_PAGES:
        print(f"LINT FAILURE: expected {EXPECTED_TOTAL_PAGES} pages, got {pages}")
        sys.exit(1)

    print(f"Wrote {output_pdf} ({pages} pages)")


if __name__ == "__main__":
    main()
