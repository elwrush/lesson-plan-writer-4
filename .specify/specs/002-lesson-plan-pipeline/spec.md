# Feature Specification: Lesson Plan Writer Pipeline

**Feature Branch**: `002-lesson-plan-pipeline`

**Created**: 2026-07-06

**Status**: Draft

**Input**: User described a document production pipeline for generating lesson plan PDFs from structured JSON data. A reference PDF is provided at `KNOWLEDGE BASE/070526-writing-emails-pet-exam-part-1-lesson-plan.pdf` showing the target layout. Ghostscript must be used as a concluding normalisation step to ensure print reliability and prevent content shifting during Adobe Acrobat flattening.

## User Scenarios & Testing

### User Story 1 — Render a single lesson plan to PDF (Priority: P1)

As a lesson plan author, I want to submit lesson data and receive back a professional A4 PDF, so that I can produce ready-to-print lesson plans without manual typesetting.

**Why this priority**: This is the core pipeline. Every other use case depends on it.

**Independent Test**: A known lesson data set (compatible with the existing LESSON-SHAPES format) produces an A4 PDF with the C·E·L Mathayom masthead, metadata table, aims, and stages table. The PDF is 2 pages and matches the reference PDF layout.

**Acceptance Scenarios**:

1. **Given** a lesson data file, **When** processed, **Then** an A4 PDF (595.276 × 841.89 pts) is produced.
2. **Given** a lesson with 4 stages, **When** rendered, **Then** all 4 stages appear in order with correct numbers, times, goals, procedure text, and interaction types.
3. **Given** the reference PDF, **When** a matching lesson is rendered, **Then** the output has: C·E·L Mathayom header band (left logo, center text, right logo), "Lesson Plan" + topic title, metadata table, Lesson Aim section, and Lesson Stages table with merged stage-name rows.

---

### User Story 2 — Print-reliable PDF output (Priority: P1)

As a teacher printing lesson plans, I want the PDF to survive Adobe Acrobat's flattening process without content shifting or reflow, so that the printed output matches what I see on screen.

**Why this priority**: The entire pipeline is worthless if the output clips, shifts, or reflows when sent to a printer. Some PDF viewers and print drivers re-interpret PDF internals, and documents with non-standard structure can break. The output must be normalised to a format that all consumers handle identically.

**Independent Test**: The rendered PDF is passed through a PDF normalisation step and then opened in Adobe Acrobat. No flattening-related content shift occurs. The PDF renders identically in at least two different PDF viewers.

**Acceptance Scenarios**:

1. **Given** a rendered PDF, **When** normalised, **Then** all fonts are embedded, no external font references remain.
2. **Given** a normalised PDF, **When** opened in Adobe Acrobat and flattened (print-to-PDF), **Then** every text element and image is in the same position as in the original — no content clipping or shifting.
3. **Given** a 2-page lesson plan PDF, **When** normalised, **Then** page count is unchanged and all content is preserved.

---

### User Story 3 — Cross-project reusability (Priority: P2)

As a developer, I want to invoke this document generation pipeline from any project directory, so that I don't need per-project setup.

**Why this priority**: The pipeline must serve multiple projects, not just LPW-4.

**Independent Test**: From an empty directory outside any project, a minimal template and data input produce a valid A4 PDF.

**Acceptance Scenarios**:

1. **Given** no project-specific setup, **When** the pipeline is invoked from any directory, **Then** it resolves its own templates and assets correctly.
2. **Given** the pipeline's directory, **When** inspected, **Then** it contains templates, assets, and a SKILL.md with usage instructions.

---

### User Story 4 — Visual customisation per document type (Priority: P3)

As a designer, I want to provide document-specific styling overrides, so that different document types (lesson plans, worksheets, reports) have distinct visual identities.

**Why this priority**: Enables the pipeline to serve multiple document types with minimal code duplication.

**Independent Test**: A custom stylesheet changes the output font family from the default, and the resulting PDF uses the new font.

**Acceptance Scenarios**:

1. **Given** a custom stylesheet, **When** applied, **Then** the PDF uses the custom styles for fonts and spacing.
2. **Given** no custom stylesheet, **When** rendered, **Then** the default styling is used.

---

### Edge Cases

- What happens when a lesson has zero stages? The PDF should render the masthead, metadata, and aims but show a graceful message or empty table with headers where stages would be. Must not crash.
- What happens when procedure text contains Unicode characters (smart quotes, em dashes, accented characters)? Must render without mojibake or substitution errors.
- What happens when a stage has an unusually long procedure? The stage should break naturally across pages, keeping the stage header with its first data row.
- What happens when logo images are missing? The pipeline should warn but still produce a PDF without images.
- What happens when Ghostscript is not installed? The pipeline should produce the intermediate PDF and emit a clear warning that the normalisation step was skipped.
- What happens when input data is invalid? The pipeline must reject with a clear error message before any PDF is written — no partial output.

## Requirements

### Functional Requirements

- **FR-001**: System MUST accept structured lesson data and produce an A4 PDF document.
- **FR-002**: Output PDF MUST be 595.276 × 841.89 pts (A4), matching the reference PDF dimensions.
- **FR-003**: Header band MUST display: Cambridge logo (left), "C·E·L Mathayom" text (centered), ACT logo (right), with a horizontal rule below. Must match reference PDF.
- **FR-004**: Metadata section MUST display labeled fields: Teacher, Date, Class, Duration, CEFR Level, Lesson Shape, and Materials (bullet list). Slideshow URL, if provided, appears as an item in the Materials list.
- **FR-005**: Stages section MUST render as a table with 4 columns (Time, Goal, Procedure, Int). Stage name rows MUST span all 4 columns as merged headings.
- **FR-006**: Procedure items MUST render with bullet prefix, matching the reference PDF format.
- **FR-007**: Default font MUST be Arial. Text must be readable at standard print size.
- **FR-008**: Pipeline MUST run PDF normalisation by default. Ghostscript runs automatically. Use `--no-ghostscript` flag to skip. If `gs` is not on PATH, emit a warning and use the intermediate PDF as-is.
- **FR-009**: When Ghostscript normalisation is applied, the output PDF MUST survive Adobe Acrobat flattening (print-to-PDF) without content shifting or reflow. This requirement is conditional on Ghostscript being available.
- **FR-010**: System MUST be invocable from any working directory without project-specific configuration.
- **FR-011**: User-supplied stylesheet MUST be injectable to override default visual styling.
- **FR-012**: Missing logo images MUST produce a warning but not block PDF generation.
- **FR-013**: Invalid input data MUST be rejected with a clear error message before any rendering occurs.

### Key Entities

- **LessonPlanData**: Input data containing the lesson content. Extends the existing LESSON-SHAPES format with document-level metadata (teacher, date, class, duration, CEFR level, shape, materials, aims, stages).
- **StageData**: A single lesson stage within LessonPlanData. Contains stage name, number, time, goal, procedure items (ordered), and interaction type.
- **RenderTemplate**: An HTML document with template markers for data insertion. Defines the document layout (masthead, metadata grid, stages table).
- **StyleDefinition**: Visual styling rules for the document. Default styles are built-in; custom styles override selectively.
- **NormalisedDocument**: The final PDF after normalisation. All fonts embedded, metadata normalised, structurally consistent for reliable printing.

## Success Criteria

### Measurable Outcomes

- **SC-001**: A lesson data file can be converted to a 2-page A4 PDF, visually matching the reference PDF in masthead, metadata, aims, and stages layout.
- **SC-002**: The rendered PDF, after normalisation, shows no content shift when opened in Adobe Acrobat and flattened via print-to-PDF. Verified by text extraction comparison (expected layout preserved).
- **SC-003**: The pipeline can be invoked from any directory and produces valid output without project-specific configuration.
- **SC-004**: All output PDFs pass basic structural validation (open without errors, correct page count, embedded fonts).

## Clarifications

**Q1: Data format — envelope vs modified shapes.** Envelope wrapper. Shape files stay untouched. Input JSON is `{"shape": {...shape-data...}, "metadata": {teacher, date, class_name, ...}}`.

**Q2: Ghostscript default behavior.** Always-on with `--no-ghostscript` to skip. Graceful degradation if `gs` unavailable.

**Q3: Visual match verification.** PDF text extraction comparison. Verify structure via extracted text (expected text nodes, page count, proportions). No pixel comparison.

**Q4: Mail-merge scope.** Out of scope. Single-lesson rendering only.

**Q5: Slideshow URL handling.** Part of `materials` array, not a separate field. Rendered as an additional bullet in the Materials row of the metadata grid.

**Q6: Time format.** Shape files store `time` as string `"5 min"`. Pipeline parses via regex `(\d+)` to integer `time_minutes`. No separate numeric field.

**Q7: FR-009 conditionality.** Conditional on Ghostscript being available. If normalisation is skipped (gs missing or `--no-ghostscript`), the requirement does not apply.

**Q8: Envelope construction.** Manual wrapper via `--data`. The caller constructs `{"shape": {...}, "metadata": {...}}` themselves. No `--shape`/`--metadata` CLI flags.

## Resolved

The above Q6-Q8 items were surfaced by the quality checklist and resolved before implementation:

- **Time format**: Parsed from shape `time` string via regex `(\d+)`. `"5 min"` → `5`. Parse failure → validation error.
- **FR-009 conditionality**: Conditional on Ghostscript being available. If normalisation is skipped, the Acrobat-flattening requirement does not apply.
- **Envelope construction**: Manual wrapper via `--data`. No `--shape`/`--metadata` flags.
- **`main_aim` source**: `metadata.main_aim` takes precedence over `shape.main_aim_format`. The shape field is a template pattern (`[target language]` placeholders); metadata contains the resolved final text.
- **SC-002 limitation**: "No content shift" verification is limited to text extraction comparison (bounding-box positions are not measured). This is an acknowledged design decision — full pixel-level verification requires Adobe Acrobat and is not automated in this pipeline.

Key entities: `MetadataFields` must also include `topic` (lesson topic string, required), `lesson_shape` (shape display name, required).

## Assumptions

- The existing LESSON-SHAPES JSON files remain unchanged. The input is an envelope JSON that embeds the shape data plus separate metadata fields.
- Ghostscript is always-on by default. `--no-ghostscript` to skip.
- The first (and only) implementation target is single-lesson rendering using one existing shape as the test case. Mail-merge is out of scope for this project.
- Arial is available on the target system (universally available on all major OSes). No font bundling needed for v1.
- Visual match to the reference PDF is defined as "same structure and proportional spacing" — exact pixel-level reproduction across different PDF engines is not expected.
