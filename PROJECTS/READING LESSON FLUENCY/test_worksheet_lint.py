"""Red-green deterministic lint for the two Reciprocal Teaching booklets (B1, B2)."""
import subprocess
from pathlib import Path

PDFS = [
    Path("PROJECTS/READING LESSON FLUENCY/PDF/reading-reciprocal-teaching-B1.pdf"),
    Path("PROJECTS/READING LESSON FLUENCY/PDF/reading-reciprocal-teaching-B2.pdf"),
]


def test_pdfs_exist():
    for path in PDFS:
        assert path.exists(), f"PDF not found at {path}"


def test_pdf_is_a4():
    for path in PDFS:
        r = subprocess.run(["pdfinfo", str(path)], capture_output=True, text=True, check=True)
        # Accept any A4 page size (Chromium may emit 594.96x841.92 or 595.92x842.88).
        assert "A4" in r.stdout or ("595" in r.stdout and "842" in r.stdout), f"Unexpected size: {r.stdout[:200]}"


def test_page_count():
    for path in PDFS:
        r = subprocess.run(["pdfinfo", str(path)], capture_output=True, text=True, check=True)
        count = None
        for line in r.stdout.splitlines():
            if line.strip().startswith("Pages"):
                count = int(line.split(":")[1].strip())
                break
        assert count == 4, f"{path.name}: expected 4 pages, got {count}"


def test_fonts_embedded():
    for path in PDFS:
        r = subprocess.run(["pdffonts", str(path)], capture_output=True, text=True, check=True)
        for line in r.stdout.splitlines()[2:]:
            if not line.strip():
                continue
            flags = [tok for tok in line.split() if tok in ("yes", "no")]
            assert flags and all(f == "yes" for f in flags), f"{path.name}: unembedded font: {line}"
