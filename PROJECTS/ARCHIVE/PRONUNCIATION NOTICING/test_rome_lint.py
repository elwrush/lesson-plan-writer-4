"""Red-green deterministic lint for the Rome Book Review noticing worksheet."""

import subprocess
from pathlib import Path

PDF_PATH = Path("PROJECTS/PRONUNCIATION NOTICING/Rome-Book-Review-Noticing-Worksheet.pdf")
EXPECTED_PAGES = 3


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
        if "Pages" in line:
            count = int(line.split(":")[1].strip())
            break
    assert count == EXPECTED_PAGES, f"Expected {EXPECTED_PAGES} pages, got {count}"


def test_underline_count():
    """27 target words must be underlined in the source HTML."""
    html = Path("PROJECTS/PRONUNCIATION NOTICING/rome-noticing.html").read_text(encoding="utf-8")
    n = html.count("<u>")
    assert n == 23, f"Expected 23 underlined targets, got {n}"


def test_fonts_embedded():
    result = subprocess.run(
        ["pdffonts", str(PDF_PATH)],
        capture_output=True, text=True, check=True,
    )
    for line in result.stdout.splitlines()[2:]:
        if not line.strip():
            continue
        emb = line.split()[-4]
        assert emb == "yes", f"Unembedded font: {line}"
