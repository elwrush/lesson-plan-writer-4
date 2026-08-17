#!/usr/bin/env python3
"""Red-green deterministic lint for the B2 Compound & Complex Sentences worksheet.

Single generic 2-page worksheet file — no per-student demographic block.
Red phase (before generation): test_pdf_exists MUST fail — the PDF is absent.
Green phase (after generation): all tests pass.
"""

import subprocess
import sys
from pathlib import Path

import pytest

PDF_PATH = Path(__file__).parent / "Compound-Complex-Sentences-Worksheet-B2.pdf"
EXPECTED_PAGES = 2


def test_pdf_exists():
    assert PDF_PATH.exists(), f"PDF not found at {PDF_PATH}"


def test_pdf_is_a4():
    result = subprocess.run(
        ["pdfinfo", str(PDF_PATH)],
        capture_output=True, text=True, check=True,
    )
    assert "594" in result.stdout and "841" in result.stdout, \
        f"Unexpected page size: {result.stdout}"


def test_page_count():
    result = subprocess.run(
        ["pdfinfo", str(PDF_PATH)],
        capture_output=True, text=True, check=True,
    )
    count = None
    for line in result.stdout.splitlines():
        if line.startswith("Pages"):
            count = int(line.split(":")[1].strip())
            break
    assert count == EXPECTED_PAGES, f"Expected {EXPECTED_PAGES} pages, got {count}"


def test_fonts_embedded():
    result = subprocess.run(
        ["pdffonts", str(PDF_PATH)],
        capture_output=True, text=True, check=True,
    )
    for line in result.stdout.splitlines()[2:]:
        if not line.strip():
            continue
        parts = line.split()
        assert parts[-4] == "yes", f"Unembedded font: {line}"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
