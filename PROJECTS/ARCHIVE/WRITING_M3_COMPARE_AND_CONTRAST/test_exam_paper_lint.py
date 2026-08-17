"""Red-green deterministic lint for the M3 compare-and-contrast exam paper.

Red phase: the PDF does not exist yet and test_pdf_exists MUST fail.
Green phase: after generate_exam_paper.py runs, every check passes.

Run directly or with pytest:
    python3 -m pytest PROJECTS/WRITING_M3_COMPARE_AND_CONTRAST/test_exam_paper_lint.py -q
"""

import subprocess
from pathlib import Path

PROJECT_DIR = Path(__file__).parent
PDF_PATH = PROJECT_DIR.parent.parent / "PDF" / "M3-Compare-and-Contrast-Exam-Paper.pdf"

EXPECTED_PAGES = 1  # single page: task, instructions, and topics


def pdfinfo() -> dict:
    result = subprocess.run(
        ["pdfinfo", str(PDF_PATH)],
        capture_output=True, text=True, check=True,
    )
    info = {}
    for line in result.stdout.splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            info[key.strip()] = value.strip()
    return info


def test_pdf_exists():
    assert PDF_PATH.exists(), f"PDF not found at {PDF_PATH}"


def test_pdf_is_a4():
    info = pdfinfo()
    assert "594" in info["Page size"], f"Unexpected page size: {info['Page size']}"
    assert "841" in info["Page size"], f"Unexpected page size: {info['Page size']}"


def test_page_count():
    assert int(pdfinfo()["Pages"]) == EXPECTED_PAGES, \
        f"Expected {EXPECTED_PAGES} pages, got {pdfinfo()['Pages']}"


def test_fonts_embedded():
    result = subprocess.run(
        ["pdffonts", str(PDF_PATH)],
        capture_output=True, text=True, check=True,
    )
    lines = [ln for ln in result.stdout.splitlines() if ln.strip()]
    assert len(lines) >= 3, "No font rows found"
    for line in lines[2:]:
        emb = line.split()[-4]
        assert emb == "yes", f"Unembedded font: {line}"
