"""generate_worksheet.py — M2A Vocabulary Levels Test (10 items: 5 B1 + 5 B2).

Entry ticket for the Shape K vocabulary lesson, mirroring the archived
M2-VOCAB / M3-VOCAB levels tests but built from less-accessible Oxford 5000
words (COCA cross-referenced, no overlap with prior test targets).

Reuses the VOCAB-TEST-GENERATOR pipeline machinery (balanced answer positions,
deterministic linting, Kimi v2.5 one-shot validation, Playwright PDF) so the
M2A handout matches the archived tests item-for-item.
"""

import json
import os
import random
import secrets
import sys
from collections import Counter
from pathlib import Path

VOCAB_GEN = Path("/mnt/c/PROJECTS/VOCAB-TEST-GENERATOR")
HERE = Path(__file__).parent.resolve()

sys.path.insert(0, str(VOCAB_GEN))

from src.models import TestPaper, Word
from src.itemgen import assemble_test_items
from src.linting import all_lint_passed, lint_all
from src.rendering import render_pdf

GUIDE_PATH = VOCAB_GEN / ".kilo" / "skills" / "generate-vlt" / "references" / "oneshot-quality-guide.md"
TEMPLATE_DIR = VOCAB_GEN / "templates"
KIMI_MODEL = "kimi-k2.6"
KIMI_URL = "https://api.moonshot.ai/v1"
LETTERS = ["A", "B", "C", "D"]


def load_targets() -> list[Word]:
    with open(HERE / "targets-M2A.json") as f:
        raw = json.load(f)
    return [Word.model_validate(w) for w in raw]


def load_item_specs(targets: list[Word]) -> list[dict]:
    with open(HERE / "items-M2A.json") as f:
        raw = json.load(f)
    specs = []
    for target, item in zip(targets, raw):
        specs.append({
            "target": target,
            "context_sentence": item["context_sentence"],
            "correct_answer": item["correct_answer"],
            "distractors": item["distractors"],
        })
    return specs


def kimi_validate(items, level: str) -> dict | None:
    api_key = os.environ.get("MOONSHOT_API_KEY", "")
    if not api_key:
        print("  WARNING: MOONSHOT_API_KEY not set — validation skipped", file=sys.stderr)
        return None
    guide = GUIDE_PATH.read_text(encoding="utf-8") if GUIDE_PATH.exists() else ""
    item_text = ""
    for it in items:
        correct_letter = LETTERS[it.correct_index]
        item_text += (
            f"Item {it.item_index + 1} [{it.target_word.cefr_level}] "
            f"'{it.target_word.lemma}': \"{it.context_sentence}\"\n"
            f"  A) {it.options[0]}\n  B) {it.options[1]}\n"
            f"  C) {it.options[2]}\n  D) {it.options[3]}\n"
            f"  Correct: {correct_letter}) {it.correct_answer}\n\n"
        )
    prompt = (
        f"{guide}\n\n---\n\n"
        f"Apply the above guide to this {level} vocabulary test:\n\n"
        f"TEST ITEMS:\n{item_text}\n\n"
        "Return valid JSON:\n"
        '{"overall_rating": <1-5>, "verdict": "PASS|FAIL|NEEDS_REVIEW", '
        '"flagged_items": ["Item N [CRITICAL|ADVISORY]: reason", ...]}'
    )
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url=KIMI_URL, timeout=120.0)
        response = client.chat.completions.create(
            model=KIMI_MODEL,
            temperature=0.6,
            max_completion_tokens=4096,
            response_format={"type": "json_object"},
            extra_body={"thinking": {"type": "disabled"}},
            messages=[
                {"role": "system", "content": "You are a vocabulary test validator. Always respond with valid JSON."},
                {"role": "user", "content": prompt},
            ],
        )
        return json.loads(response.choices[0].message.content or "{}")
    except Exception as e:
        print(f"  Validation error: {e}", file=sys.stderr)
        return None


def main() -> None:
    seed = secrets.randbelow(2**31 - 1)
    print(f"Using seed: {seed}", file=sys.stderr)
    rng = random.Random(seed)

    print("[1/5] Loading targets...", file=sys.stderr)
    targets = load_targets()
    specs = load_item_specs(targets)

    print(f"[2/5] Assembling {len(specs)} items...", file=sys.stderr)
    items = assemble_test_items(specs, seed)

    print("[3/5] Linting...", file=sys.stderr)
    reports = lint_all(items)
    all_pass = all_lint_passed(reports)
    for r in reports:
        print(f"  [{'PASS' if r.passed else 'FAIL'}] {r.check}: {r.detail}", file=sys.stderr)
    answers = [LETTERS[it.correct_index] for it in items]
    print(f"  Answer distribution: {dict(sorted(Counter(answers).items()))}", file=sys.stderr)

    print("[4/5] Validating with Kimi v2.5...", file=sys.stderr)
    validation = kimi_validate(items, "M2A")
    if validation:
        verdict = validation.get("verdict", "?")
        print(f"  Overall: {validation.get('overall_rating', '?')}/5  Verdict: {verdict}", file=sys.stderr)
        for issue in validation.get("flagged_items", []):
            print(f"  FLAG: {issue}", file=sys.stderr)
        with open(HERE / "validation-M2A.json", "w") as f:
            json.dump(validation, f, indent=2)
    else:
        print("  WARNING: Validation skipped (API unavailable)", file=sys.stderr)

    paper = TestPaper.model_validate({
        "student_id": "HANDOUT-M2A",
        "student_name": "Class Handout (M2A)",
        "class": "M2A",
        "level": "M2A",
        "seed": seed,
        "items": [it.model_dump() for it in items],
    })

    print("[5/5] Rendering PDF...", file=sys.stderr)
    from datetime import date
    pdf_name = f"M2A-10-{date.today().strftime('%d-%b-%Y')}.pdf"
    pdf_path = HERE / pdf_name
    result = render_pdf(paper, str(pdf_path), str(TEMPLATE_DIR), test_level="M2A")
    print(f"PDF: {result} ({os.path.getsize(result)} bytes)", file=sys.stderr)


if __name__ == "__main__":
    main()
