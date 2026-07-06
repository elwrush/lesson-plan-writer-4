# Quickstart: Lesson Plan Writer Pipeline

## Prerequisites

```bash
# System dependencies (WeasyPrint + Ghostscript)
sudo apt install libpango-1.0-0 libcairo2 libffi8 ghostscript

# Python packages
pip install jinja2 weasyprint pydantic
```

## Skill Setup

The skill lives at `~/.kilo/skills/jinja-weasy-docs/`. It is a global skill — usable from any project directory.

```bash
# Directory structure
~/.kilo/skills/jinja-weasy-docs/
├── SKILL.md
├── assets/
│   ├── act.png
│   └── cambridge.png
├── scripts/
│   └── render.py
├── templates/
│   ├── base.html
│   ├── base.css
│   ├── lesson-plan.html
│   └── lesson-plan.css
├── tests/
│   ├── test_render.py
│   └── data/
└── references/
    └── paged-media.md
```

## Rendering a Lesson Plan

```bash
# The --data file is an envelope JSON containing shape + metadata:
# {"shape": {...}, "metadata": {teacher, date, ...}}
python ~/.kilo/skills/jinja-weasy-docs/scripts/render.py \
    --template lesson-plan \
    --data PLANS/envelope.json \
    -o PLANS/lesson-plan.pdf
```

## Running Tests

```bash
cd ~/.kilo/skills/jinja-weasy-docs
python -m pytest tests/ -v
```

## Verification Scenarios

1. **Single render**: `shape-a.json` → 2-page A4 PDF with masthead, metadata, aims, stages table
2. **Font check**: `pdffonts output.pdf` shows Arial (or ArialMT) embedded
3. **Page size**: `pdfinfo output.pdf` shows 595.276 x 841.89 pts (A4)
4. **Stage count**: PDF text contains all stage names from the input data
5. **Invalid data**: Malformed JSON → exit code 2 + clear error message, no PDF written
6. **Ghostscript skip**: `--no-ghostscript` produces PDF without `gs` call (check no `gs` process in `ps aux`)
7. **Acrobat survival**: Normalised PDF opened in Acrobat → flatten via print-to-PDF → no content shift (visual comparison)

## Common Issues

| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'weasyprint'` | WeasyPrint not installed | `pip install weasyprint` |
| `OSError: cannot load library 'pango-1.0-0'` | Missing system libs | `sudo apt install libpango-1.0-0 libcairo2` |
| PDF has wrong font | Arial not installed | `sudo apt install ttf-mscorefonts-installer` |
| Logos missing in PDF | Data URI embedding failed | Check `assets/act.png` and `assets/cambridge.png` exist |
| Template not found | Wrong --template name | Ensure file exists at `templates/{name}.html` |
| `gs: command not found` | Ghostscript not installed | `sudo apt install ghostscript` |
| Content shifts in Acrobat | Ghostscript step skipped | Use default pipeline (omit `--no-ghostscript`) |
