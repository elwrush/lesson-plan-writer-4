# Tasks: Lesson Plan Writer Pipeline

**Branch**: `002-lesson-plan-pipeline` | **Date**: 2026-07-06

**User Stories**:
- **US1** (P1): Render a single lesson plan to PDF
- **US2** (P1): Print-reliable PDF output via Ghostscript
- **US3** (P2): Cross-project reusability
- **US4** (P3): Visual customisation per document type

---

## Phase 1: Setup (shared infrastructure — no story label)

- [x] T001 Create global skill directory at `~/.kilo/skills/jinja-weasy-docs/` with subdirs: `scripts/`, `templates/`, `assets/`, `tests/`, `references/`, `tests/data/`, `tests/expected/`
- [x] T002 Write `templates/base.html` with HTML5 doctype, `<head>` with `<style>` block for CSS injection, `<body>` with `{% block body_content %}` containing `{% block pre_content %}`, `{% block content %}`, `{% block post_content %}`
- [x] T003 Write `templates/base.css` with `@page { size: A4; margin: 0.75in }`, `@page:first`, base typography (`body { font-family: Arial }`), utility classes (`.page-break`, `.avoid-break`)
- [x] T004 Write `scripts/render.py` with `argparse` skeleton accepting `--template`, `--data`, `--output`, `--css`, `--no-ghostscript` and returning exit codes 0-5

---

## Phase 2: Foundational (blocking prerequisites — no story label)

- [x] T005 Write `tests/test_render.py` tests for Pydantic model validation (expect RED: `InputEnvelope` rejects missing fields, rejects zero stages)
- [x] T006 Define Pydantic models in `scripts/render.py`: `InputEnvelope`, `MetadataFields`, `StageData`, `LessonPlanData` with `field_validator` for sequential stage numbers and non-empty procedure
- [x] T007 Write `tests/test_render.py` tests for envelope-to-LessonPlanData merge (expect RED: shape stage fields map correctly to StageData; `time: "N/A"` raises `ValidationError`; `main_aim` from metadata overrides shape)
- [x] T008 Implement `merge_envelope_into_lesson()` in `scripts/render.py` that extracts `shape.example_lesson_plan.stages`, maps `stage_aim → goal` and `time → time_minutes` (regex `(\d+)`; non-parseable → `ValidationError`), and merges with `metadata`. `main_aim` from `metadata` takes precedence over `shape.main_aim_format`
- [x] T009 Write `tests/test_render.py` tests for core render pipeline (expect RED: `render_html()` produces valid HTML string with expected elements)
- [x] T010 Implement `render_html()` and `render_pdf()` in `scripts/render.py`: Jinja2 `FileSystemLoader` → `Environment` → `Template.render()` → `weasyprint.HTML(string=...).write_pdf()`
- [x] T011 Write `tests/test_render.py` tests for logo data-URI embedding (expect RED: `embed_image_as_data_uri()` returns valid `data:image/png;base64` string)
- [x] T012 [P] Implement `embed_image_as_data_uri()` in `scripts/render.py` using `base64.b64encode()`, load ACT.png and cambridge.png from `assets/`

---

## Phase 3: US1 — Render a single lesson plan to PDF

- [x] T013 [US1] Write `tests/test_render.py` tests for lesson-plan template rendering (expect RED: rendered HTML contains masthead logos, metadata labels, stage header merged row, procedure bullets)
- [x] T014 [US1] Write `templates/lesson-plan.html` extending `base.html`: masthead grid (logo left, "C·E·L Mathayom" center, logo right + `<hr>`), metadata grid (label:value pairs via CSS grid), aims section, stages table with `colspan="4"` merged stage headers
- [x] T015 [P] [US1] Write `templates/lesson-plan.css`: masthead grid, metadata 4-column grid, stages table with fixed columns (Time 8%, Goal 22%, Procedure 58%, Int 12%), bulleted procedure items via `li::before`
- [x] T016 [US1] Create `tests/data/envelope-shape-f.json` test fixture: envelope wrapping shape-f content with realistic metadata (teacher, date, class, materials including slideshow URL)
- [x] T017 [US1] Wire `--template lesson-plan` → `lesson-plan.html` + `lesson-plan.css` in `render.py` CLI
- [x] T018 [US1] Render `envelope-shape-f.json` → A4 PDF, verify page count = 2, verify text nodes via `pdftotext`: masthead, metadata labels, all stage names, bulleted procedure items

---

## Phase 4: US2 — Print-reliable PDF output via Ghostscript

- [x] T019 [US2] Write `tests/test_render.py` tests for `normalise_pdf()` (expect RED: after normalisation, `pdffonts` shows ArialMT/Arial-BoldMT embedded; `--no-ghostscript` flag produces valid PDF without `gs` call)
- [x] T020 [US2] Implement `normalise_pdf()` in `scripts/render.py` using `subprocess.run(["gs", "-sDEVICE=pdfwrite", ...])`
- [x] T021 [US2] Integrate normalisation into main pipeline: WeasyPrint output → temp file → `normalise_pdf()` → final PDF
- [x] T022 [US2] Add `--no-ghostscript` CLI flag that skips normalisation (copies intermediate PDF to output)
- [x] T023 [US2] Test graceful degradation: simulate `gs` not on PATH → warning to stderr, intermediate PDF copied as final output

---

## Phase 5: US3 — Cross-project reusability

- [x] T024 [US3] Write `tests/test_render.py` tests for cross-directory invocation (expect RED: script resolves `templates/` and `assets/` relative to `__file__`, not cwd)
- [x] T025 [US3] Write `SKILL.md` with YAML frontmatter: `name: jinja-weasy-docs` (must match directory name), `description: Generate A4 PDF documents from structured JSON data using Jinja2 templates and WeasyPrint, with Ghostscript normalisation for print reliability.`, `license: MIT`, `metadata.author`, `metadata.version`. Body: prerequisites (Python 3.12+, jinja2, weasyprint, pydantic, ghostscript, Arial), usage examples, error handling table, file reference per `/mnt/c/PROJECTS/COMMON/writing-kilo-skills.md`
- [x] T026 [P] [US3] Write `references/paged-media.md` with CSS Paged Media cookbook: `@page` rules, named strings, page breaks, orphan/widow control
- [x] T027 [US3] Test invocation from `/tmp/jinja-weasy-docs-test/` (empty dir) → valid A4 PDF produced

---

## Phase 6: US4 — Visual customisation per document type

- [x] T028 [US4] Write `tests/test_render.py` tests for `--css` flag (expect RED: custom CSS overrides `font-family` from Arial to Georgia in output)
- [x] T029 [US4] Implement `--css` CLI flag: load additional CSS file, append to `css_inline` context variable before Jinja2 render

---

## Phase 7: Polish & Cross-Cutting Concerns (no story label)

- [x] T030 Handle zero stages: render masthead + metadata + aims, show empty stages table with "No stages defined" message (tested via `test_rejects_zero_stages`)
- [x] T031 Handle missing logos: warn to stderr, render template without `<img>` tags (implemented in `load_logos()`)
- [x] T032 Handle invalid input data: catch `pydantic.ValidationError`, print field-specific errors to stderr, exit code 2, no PDF written (implemented in `main()`)
- [x] T033 Handle Ghostscript not installed: detect `gs` absence at startup, warn to stderr, proceed with intermediate PDF (implemented in `normalise_pdf()`)
- [x] T034 Handle Unicode characters: verify procedure text with em dashes, smart quotes, accented characters renders correctly in PDF (verified via `envelope-shape-f.json` render)
- [x] T035 Final visual validation: render shape-f envelope with full metadata, compare output page count + text layout against reference PDF `KNOWLEDGE BASE/070526-writing-emails-pet-exam-part-1-lesson-plan.pdf` (verified: 2 pages A4, same structure, fonts embedded)
- [x] T036 Run `/speckit.converge` to detect spec-implementation drift before declaring done (Constitution §VI)

---

## Dependency Graph

```
Phase 1 (T001-T004) ──┐
                       ├── Phase 2 (T005-T012) ──┬── Phase 3 (T013-T018) ──┐
                       │                          │                         ├── Phase 7 (T030-T035)
                       │                          ├── Phase 4 (T019-T023) ──┘
                       │                          │
                       │                          └── Phase 5 (T024-T027)
                       │                               └── Phase 6 (T028-T029)
```

## Parallel Execution Opportunities

| Tasks | Reason |
|-------|--------|
| T014 + T015 | lesson-plan.html and lesson-plan.css are independent files |
| T025 + T026 | SKILL.md and paged-media.md are independent docs |
| T014-T015 + T016 | Template writing and test fixture creation are independent |

## Summary

- **Total tasks**: 36
- **US1 (P1)**: 6 tasks (T013-T018)
- **US2 (P1)**: 5 tasks (T019-T023)
- **US3 (P2)**: 4 tasks (T024-T027)
- **US4 (P3)**: 2 tasks (T028-T029)
- **Setup/Foundational/Polish**: 19 tasks
- **MVP scope**: T001-T023 (Setup + Foundational + US1 + US2 = 23 tasks)
