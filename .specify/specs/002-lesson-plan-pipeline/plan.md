# Implementation Plan: Lesson Plan Writer Pipeline

**Branch**: `002-lesson-plan-pipeline` | **Date**: 2026-07-06 | **Spec**: `.specify/specs/002-lesson-plan-pipeline/spec.md`

**Input**: Feature specification — Jinja2 → HTML+CSS → WeasyPrint pipeline for producing lesson plan PDFs from structured JSON data, packaged as a global Kilo skill.

## Summary

Replace the Pandoc/Lua/Typst pipeline with a four-stage pipeline: Jinja2 templates + CSS Paged Media → single HTML document → WeasyPrint → intermediate PDF → Ghostscript pdfwrite → print-ready PDF. The Ghostscript concluding step normalises the PDF structure, embeds all fonts, and strips non-standard metadata — preventing Adobe Acrobat's flattening process from shifting or misplacing content. No separate pagination layer — CSS handles all page breaking via `@page`, `break-before`, `break-inside`, `orphans`, and `widows`. Packaged as a global skill at `~/.kilo/skills/jinja-weasy-docs/` for use across projects.

## Technical Context

**Language/Version**: Python 3.12+ (system python3, no uv/pipenv requirement — skill is self-contained)

**Primary Dependencies**: jinja2 >= 3.1, weasyprint >= 62, pydantic >= 2.0, ghostscript >= 10.0, arial (system font)

**Storage**: Filesystem I/O only (JSON in → PDF out)

**Testing**: pytest with WeasyPrint PDF output validation (page count, dimensions, text content)

**Target Platform**: Linux (WSL) — WeasyPrint requires system libraries (libpango, libcairo, libffi). Cross-platform compatibility is a stretch goal.

**Project Type**: CLI script + Jinja2 templates + CSS stylesheets, packaged as a Kilo skill

**Performance Goals**: Single lesson plan PDF in <5s

**Constraints**: Zero Pandoc, zero Lua, zero Typst. No CDN or network dependencies for PDF generation. Logos embedded as data URIs for portability. Ghostscript must be discoverable via `gs` on PATH.

**Scale/Scope**: Single Python render script (~500-700 lines), one HTML base template, one CSS base stylesheet, one lesson-plan template/CSS pair.

## Constitution Check

| Gate | Status | Notes |
|------|--------|-------|
| Simplicity (≤3 projects) | ✅ | Single skill directory |
| Anti-Abstraction (use features directly) | ✅ | Jinja2 and WeasyPrint APIs called directly — no wrapper abstraction |
| Integration-First (contracts before code) | ✅ | Contracts defined in `contracts/` |
| Test-First (Red/Green) | ✅ | All new code test-first |
| Structured-Data-First | ✅ | JSON in → structured Pydantic model → render |
| Pydantic Gate | ✅ | All JSON writes validated before render |
| Kilo Skills Compliance | ✅ | `name: jinja-weasy-docs` matches dir; `scripts/`, `assets/`, `references/` in use; `templates/` and `tests/` as additional dirs; SKILL.md planned for Phase 5 |

## Project Structure

### Documentation (this feature)

```
.specify/specs/002-lesson-plan-pipeline/
├── spec.md              # Feature spec (/speckit.specify)
├── plan.md              # This file (/speckit.plan)
├── research.md          # Library research (/speckit.plan)
├── data-model.md        # Entities and I/O schemas (/speckit.plan)
├── quickstart.md        # Setup + verification (/speckit.plan)
└── contracts/           # Interface contracts (/speckit.plan)
    ├── RENDERER.md
    ├── TEMPLATES.md
    ├── CSS.md
    └── CONTRACTS_TEST.md
```

### Source Code (global skill)

```
~/.kilo/skills/jinja-weasy-docs/
├── SKILL.md                          # Usage instructions + workflow
├── assets/
│   ├── act.png                       # ACT logo
│   └── cambridge.png                 # Cambridge logo
├── scripts/
│   └── render.py                     # Main pipeline: Jinja2 → HTML → WeasyPrint → PDF
├── templates/
│   ├── base.html                     # Extendable base layout (doctype, @page, logo block)
│   ├── base.css                      # Shared @page rules, page counters, named pages
│   ├── lesson-plan.html              # Lesson plan template (extends base.html)
│   └── lesson-plan.css               # Lesson plan specific styles
├── references/
│   └── paged-media.md                # CSS Paged Media patterns reference
└── tests/
    ├── test_render.py                # Pipeline tests (page count, dimensions, text presence)
    ├── data/
    │   ├── minimal.json              # Minimal valid lesson data
    │   └── shape-a.json              # Copy of LESSON-SHAPES/shape-a.json for testing
    └── expected/
        └── expected-page-count.txt   # Known-good page counts per test fixture
```

**Structure Decision**: Single skill directory with co-located templates, assets, and tests. No Python package — `render.py` is a standalone CLI script that resolves paths relative to its own location. This keeps the skill self-contained and invocable from any working directory.

## Architecture Overview

```
envelope.json (shape content + document metadata)
    │   {"shape": {...}, "metadata": {teacher, date, ...}}
    ▼
Pydantic validation (InputEnvelope → LessonPlanData)
    │   model_validate() validates envelope
    │   render.py merges shape.stages + metadata into LessonPlanData
    ▼
Jinja2 environment (FileSystemLoader)
    ├── base.html          ← base.css (inline via <style>)
    ├── lesson-plan.html   ← lesson-plan.css (inline via <style>)
    └── data context       ← {lesson, logos (data URIs), css}
    │
    ▼
Single HTML document
    └── <style>: @page rules, page-break classes, table styles
    └── <body>: masthead, metadata, aims, stages table (CSS table)
    │
    ▼
WeasyPrint HTML(string) → PDF
    │   write_pdf()
    ▼
Intermediate PDF (WeasyPrint output)
    │
    ▼
Ghostscript pdfwrite normalisation
    ├── -dPDFSETTINGS=/printer       (300dpi, high-quality)
    ├── -dCompatibilityLevel=1.7     (modern PDF)
    ├── -dEmbedAllFonts=true         (no font substitution)
    ├── -dSubsetFonts=true           (subset without losing glyphs)
    ├── -dDetectDuplicateImages=true (deduplicate logos)
    ├── -dOptimize=true              (linearised for fast rendering)
    └── -sColorConversionStrategy=LeaveColorUnchanged
    │
    ▼
Print-ready PDF (A4, 2 pages, survives Acrobat flattening)
```

### Data flow detail

1. **Input layer**: JSON envelope file loaded and validated against Pydantic `InputEnvelope` model. `render.py` extracts stages from `shape.example_lesson_plan.stages` and merges with `metadata` fields to construct a `LessonPlanData` runtime object.
2. **Render layer**: Jinja2 renders a single HTML document with embedded CSS. CSS uses `@page` for page dimensions/margins, `page-break-before: always` on stage breaks, `string-set` for running headers (future use)
3. **PDF generation layer**: WeasyPrint converts the HTML string to PDF bytes, written to a temp file (the intermediate PDF)
4. **Normalisation layer**: Ghostscript reads the intermediate PDF, applies `pdfwrite` with `/printer` preset, embeds all fonts, deduplicates images, and writes the final print-ready PDF. This eliminates structural quirks that cause Acrobat's flattening to shift content

### Pagination strategy

All pagination is CSS-driven:
- `@page { size: A4; margin: ... }` — page geometry
- `@page:first { @top-center { content: ... } }` — page 1 header band
- `@page { @top-left { content: element(running-header) } }` — running headers on subsequent pages
- `tr { break-inside: avoid }` — keep stage data rows together
- `.stage-section { break-inside: avoid }` — keep stage header + first row together
- Named pages (`@page stages { ... }`) for section-specific page style

## Component Breakdown

### 1. Pydantic models (`scripts/render.py` — inline or `models.py`)

- **InputEnvelope**: The user-supplied JSON. Contains `shape` (the existing LESSON-SHAPES object) and `metadata` (document-level fields). Validated first; both sub-objects required.
- **MetadataFields**: Document metadata extracted from the envelope. Fields: `teacher`, `date`, `class_name`, `duration_minutes`, `cefr_level`, `lesson_shape`, `materials` (list[str]), `main_aim`, `subsidiary_aim` (optional), `topic`. `materials` may include a slideshow URL as an item.
- **StageData**: Fields: `stage_name`, `stage_number`, `time_minutes`, `goal`, `procedure` (list[str]), `interaction`. Extracted from `shape.example_lesson_plan.stages[].` Mapped from the shape's `stage_aim` → `goal`, `time` (parsed via regex `(\d+)` from string like `"5 min"`) → `time_minutes`, `procedure` → `procedure`.
- **LessonPlanData**: Merged runtime model. Combines `metadata` fields with parsed `stages`. This is the context passed to Jinja2 (as `lesson`). Not user-supplied — constructed internally after validation.
- Validation: at least 1 stage required; stage_number must be sequential; time_minutes > 0

### 2. Render pipeline (`scripts/render.py`)

```
main():
    1. Parse CLI args (--template, --data, --output, --css, --no-ghostscript)
    2. Load JSON data
    3. Validate LessonPlanData → render one HTML → WeasyPrint
       → Ghostscript normalise → final PDF
    4. Write final PDF to output path
```

- `resolve_skill_path()`: Find the skill directory from the script's `__file__` location
- `load_template(name)`: Load Jinja2 template from `templates/`
- `load_css(name)`: Read CSS file content for inline embedding
- `embed_logos()`: Read PNG files from `assets/`, convert to data URIs
- `render_html(template_name, data, css_files)`: Jinja2 render → complete HTML document
- `render_pdf(html_string, output_path)`: WeasyPrint HTML → PDF write
- `normalise_pdf(input_path, output_path)`: Ghostscript pdfwrite post-process
  ```python
  subprocess.run([
      "gs", "-sDEVICE=pdfwrite",
      "-dCompatibilityLevel=1.7",
      "-dPDFSETTINGS=/printer",
      "-dEmbedAllFonts=true",
      "-dSubsetFonts=true",
      "-dDetectDuplicateImages=true",
      "-dOptimize=true",
      "-dNOPAUSE", "-dQUIET", "-dBATCH",
      "-sColorConversionStrategy=LeaveColorUnchanged",
      f"-sOutputFile={output_path}",
      input_path
  ], check=True)
  ```
  If `gs` is not on PATH, emit a warning and copy the intermediate PDF as-is.

### 3. Jinja2 templates

**base.html**: HTML5 doctype, `<html>`, `<head>` with embedded CSS, `<body>` with `{% block content %}`. No assumptions about document structure beyond page geometry.

**lesson-plan.html** (extends base.html): Full lesson plan layout:
- `{% block masthead %}`: Logo band (Cambridge left, title center, ACT right) + horizontal rule
- `{% block metadata %}`: CSS grid with label/value pairs
- `{% block aims %}`: "Lesson Aim" heading + main/subsidiary paragraphs
- `{% block stages %}`: Table with 4 columns, merged stage-name rows, bulleted procedure items

### 4. CSS stylesheets

**base.css**:
- `@page { size: A4; margin: ... }` — standard page setup
- `@page:first { @top-left { content: ... } }` — page 1 header via running elements
- `body { font-family: Arial, sans-serif; font-size: ... }` — base typography
- `.page-break { break-before: page; }` — explicit page break class

**lesson-plan.css**:
- `.masthead` — logo grid, horizontal rule styling
- `.metadata-grid` — CSS grid with 2-column label/value pairs
- `.stages-table` — table layout, column widths, merged row styling
- `.procedure-list` — bullet styling matching reference PDF
- `.stage-section { break-inside: avoid; }` — prevent stages from breaking badly
- `.stage-header { break-after: avoid; }` — keep header with first row

### 5. Tests (`tests/test_render.py`)

- **test_single_render**: Render shape-a to PDF, verify page count = 2, A4 dimensions, text presence (masthead, stage names, aims)

- **test_invalid_json**: Malformed data → Pydantic error → no PDF written
- **test_missing_logo**: Missing logo → warning produced, PDF still renders
- **test_custom_css**: Custom CSS overrides font-family in output
- **test_ghostscript_normalise**: Render + normalise → `pdffonts` shows all fonts embedded, page count unchanged
- **test_ghostscript_skip**: `--no-ghostscript` flag → intermediate PDF written directly, no `gs` call
- **test_ghostscript_not_installed**: `gs` not on PATH → warning emitted, intermediate PDF copied as final output

## Implementation Phases

### Phase 1: Skill skeleton + base template (test-first)
1. Create skill directory structure: `~/.kilo/skills/jinja-weasy-docs/{scripts,templates,assets,tests,references}`
2. Write `base.html` + `base.css` with A4 `@page` rules
3. Write minimal `render.py` that accepts `--template` and `--data`, produces a basic PDF with page geometry verified by test
4. Test: `render.py --template base.html --data '{"title":"test"}' -o /tmp/test.pdf` → valid A4 PDF

### Phase 2: Pydantic models + envelope merge + lesson-plan template (test-first)
1. Define `InputEnvelope`, `MetadataFields`, `StageData`, `LessonPlanData` Pydantic models
2. Implement `merge_envelope_into_lesson()`: extract stages from `shape.example_lesson_plan.stages`, map `stage_aim → goal`, `time` (string) → `time_minutes` (int via regex), merge with `metadata`
3. Write `lesson-plan.html` (extends base.html) with masthead, metadata grid, aims, stages table
4. Write `lesson-plan.css` with all styling matching the reference PDF, `font-family: Arial`
5. Embed logos as data URIs in the Jinja2 context
6. Test: Render shape-a → A4 PDF, verify via `pdffonts` that Arial is used, verify text presence

### Phase 3: Ghostscript normalisation
1. Implement `normalise_pdf()` function using `subprocess.run(["gs", ...])`
2. Integrate into render pipeline: WeasyPrint output → temp file → Ghostscript → final output
3. Add `--no-ghostscript` flag to skip normalisation
4. Handle missing `gs` gracefully (warning + passthrough)
5. Test: `pdffonts` confirms all fonts embedded after normalisation
6. Test: `--no-ghostscript` produces valid PDF without Ghostscript call

### Phase 4: SKILL.md + error handling

1. Write SKILL.md with usage instructions, prerequisites (including Ghostscript), examples
2. Add graceful error handling: missing template, invalid JSON, missing logo, WeasyPrint unavailable, Ghostscript unavailable
3. Write `references/paged-media.md` with CSS Paged Media patterns documentation

### Phase 5: Validation against reference PDF

1. Render shape-f (Productive Skills, matching the reference PDF topic) with full metadata
2. Compare output against reference PDF: page count, masthead position, font, spacing, stage layout
3. Tweak CSS until visual match is achieved
4. Document known differences from reference (font change: Arial vs Roboto, Typst vs WeasyPrint rendering)
5. Note: SC-002 (Acrobat flattening survival) is verified only by text extraction comparison. Pixel-level content-shift detection is not automated.

## Complexity Tracking

No constitution violations — this feature is a clean replacement of a complex pipeline with a simpler one.

**Pre-done gate**: Run `/speckit.converge` before declaring done to detect spec drift per Constitution §VI.
