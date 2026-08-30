"""test_worksheet_lint.py — Red-green deterministic checks for the Interview Power worksheet.

Red phase: PDF does not exist yet (test_pdf_exists MUST fail).
Green phase: PDF exists, A4, 3 pages, fonts embedded.
"""

import subprocess
from pathlib import Path

PDF_PATH = Path("PROJECTS/INTERVIEW SPEAKING/Interview-Power-PREP-Worksheet.pdf")
EXPECTED_PAGES = 3


def test_pdf_exists():
    """Red phase: file does not exist yet. Green phase: file exists."""
    assert PDF_PATH.exists(), f"PDF not found at {PDF_PATH}"


def test_pdf_is_a4():
    """A4 dimensions: 595 x 842 pts (allow ±2 pts for rounding)."""
    result = subprocess.run(
        ["pdfinfo", str(PDF_PATH)],
        capture_output=True, text=True, check=True,
    )
    assert "594" in result.stdout and "841" in result.stdout, \
        f"Unexpected page size: {result.stdout}"


def test_page_count():
    """Page count matches the documented expectation for this worksheet."""
    result = subprocess.run(
        ["pdfinfo", str(PDF_PATH)],
        capture_output=True, text=True, check=True,
    )
    count = None
    for line in result.stdout.splitlines():
        if "Pages" in line:
            count = int(line.split(":")[1].strip())
            break
    assert count == EXPECTED_PAGES, f"Expected {EXPECTED_PAGES} pages, got {count}"


def test_fonts_embedded():
    """pdffonts should show every font as 'yes' in the emb column."""
    result = subprocess.run(
        ["pdffonts", str(PDF_PATH)],
        capture_output=True, text=True, check=True,
    )
    rows = result.stdout.splitlines()[2:]
    assert rows, "No fonts listed — check the PDF was rendered"
    for line in rows:
        if not line.strip():
            continue
        emb = line.split()[-4]
        assert emb == "yes", f"Unembedded font: {line}"
