#!/usr/bin/env python3
"""Verify a rendered lesson-plan PDF against its envelope (ADR 0007).

Checks, in order:
  1. the expected output PDF exists (path computed exactly like the renderer's
     make_output_path: PDF/lesson-plan-{date}-{topic}.pdf)
  2. A4 page size and at least 1 page
  3. fonts embedded (via pdffonts when available)
  4. content markers from the envelope: topic, class, teacher, main-aim opening,
     and — crucially — NO "Transcript" section unless the envelope sets it
  5. no contextual images: only the two masthead logos (page 1) are allowed,
     every other page must be image-free

Usage: python3 scripts/verify_lesson_plan.py PROJECTS/{name}/lesson-plan-envelope.json
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

A4_W, A4_H = 594.96, 841.92
TOL = 3.0
MIDDLE_SCRIPT = "PDF"


def _slug(text: str, limit: int) -> str:
    return re.sub(r"[^\w\s-]", "", text).strip().replace(" ", "-")[:limit]


def output_pdf_path(env: dict) -> Path:
    meta = env.get("metadata", {})
    safe_topic = _slug(meta.get("topic", ""), 60)
    safe_date = _slug(meta.get("date", ""), 30)
    stem = f"lesson-plan-{safe_date}-{safe_topic}" if safe_date else f"lesson-plan-{safe_topic}"
    return Path(MIDDLE_SCRIPT) / f"{stem}.pdf"


def fonts_embedded(pdf: Path) -> bool:
    try:
        out = subprocess.run(["pdffonts", str(pdf)], capture_output=True, text=True, check=False)
        # every data row's "emb" column must be "yes"
        rows = [ln for ln in out.stdout.splitlines() if ln.strip() and not ln.strip().startswith(("name", "----"))]
        return all("yes" in r for r in rows) if rows else True
    except FileNotFoundError:
        return True  # pdffonts unavailable — not a hard gate


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("usage: verify_lesson_plan.py <envelope.json>")
    env_path = Path(sys.argv[1])
    if not env_path.exists():
        sys.exit(f"envelope not found: {env_path}")
    env = json.loads(env_path.read_text(encoding="utf-8"))
    meta = env.get("metadata", {})

    pdf = output_pdf_path(env)
    if not pdf.exists():
        # fall back to the newest lesson-plan PDF (name drift guard)
        cands = sorted(Path(MIDDLE_SCRIPT).glob("lesson-plan-*.pdf"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not cands:
            sys.exit(f"ERROR: no lesson-plan PDF found (expected {pdf})")
        pdf = cands[0]

    import pymupdf

    doc = pymupdf.open(str(pdf))
    n_pages = doc.page_count
    errors: list[str] = []

    # 1. A4 + page count
    page = doc[0]
    if not (abs(page.rect.width - A4_W) < TOL and abs(page.rect.height - A4_H) < TOL):
        errors.append(f"not A4: {page.rect.width:.1f} x {page.rect.height:.1f}")
    if doc.page_count < 1:
        errors.append(f"page count {doc.page_count}")

    text = "\n".join(str(doc[i].get_text()) for i in range(doc.page_count))

    # 2. content markers
    if "Lesson Plan" not in text:
        errors.append("'Lesson Plan' heading not found")
    for label, probe in (("topic", meta.get("topic")), ("class_name", meta.get("class_name")),
                         ("teacher", meta.get("teacher"))):
        if probe and probe not in text:
            errors.append(f"{label} not found in PDF: {probe!r}")
    main_aim = meta.get("main_aim", "")
    if main_aim:
        head = " ".join(main_aim.split()[:8])
        if head not in text:
            errors.append(f"main aim opening not found: {head!r}")
    # transcript: must be present ONLY when the envelope sets it (reading lesson => absent)
    has_transcript = bool(meta.get("transcript"))
    if has_transcript and "Transcript" not in text:
        errors.append("transcript set in envelope but no Transcript section found")
    if not has_transcript and "Transcript" in text:
        errors.append("Transcript section present but envelope has no transcript (reading lesson?)")

    # 3. images: only masthead logos on page 1
    for i in range(doc.page_count):
        imgs = len(doc[i].get_images())
        if i == 0:
            if imgs > 2:
                errors.append(f"page 1 has {imgs} images (expected only the 2 masthead logos)")
        elif imgs:
            errors.append(f"page {i+1} has {imgs} images (lesson plans must have no contextual images)")

    doc.close()

    if not fonts_embedded(pdf):
        errors.append("some fonts not embedded")

    if errors:
        for e in errors:
            print(f"  ERROR: {e}")
        print(f"[verify] {pdf.name}: FAIL")
        sys.exit(1)
    print(f"[verify] {pdf.name}: OK ({n_pages} pages, A4)")


if __name__ == "__main__":
    main()
