# Contract Tests

## RENDERER.md Contract Tests

### `test_cli_missing_template`
- **Given**: `--template nonexistent --data test.json -o out.pdf`
- **Expected**: exit code 4, stderr contains "Template not found"

### `test_cli_invalid_json`
- **Given**: `--template lesson-plan --data garbage.json -o out.pdf` (file contains `{invalid json}`)
- **Expected**: exit code 2, stderr contains Pydantic validation error

### `test_cli_single_render`
- **Given**: `--template lesson-plan --data valid.json -o /tmp/test_lp.pdf`
- **Expected**: exit code 0, file `/tmp/test_lp.pdf` exists, is A4 (595.276 × 841.89 pts), >= 1 page

### `test_cli_skip_ghostscript`
- **Given**: `--template lesson-plan --data valid.json -o /tmp/test_nogs.pdf --no-ghostscript`
- **Expected**: exit code 0, `/tmp/test_nogs.pdf` exists, valid PDF, no `gs` process invoked during run

### `test_cli_ghostscript_normalises`
- **Given**: `--template lesson-plan --data valid.json -o /tmp/test_gs.pdf` (default, Ghostscript enabled)
- **Expected**: exit code 0, `/tmp/test_gs.pdf` exists, `pdffonts` shows all fonts embedded (ArialMT, Arial-BoldMT)

### `test_cli_ghostscript_not_found`
- **Given**: `gs` not on PATH, `--template lesson-plan --data valid.json -o /tmp/test_fallback.pdf`
- **Expected**: exit code 0, stderr contains warning about missing `gs`, `/tmp/test_fallback.pdf` is valid but not Ghostscript-processed, `normalise_pdf()` returns False

### `test_time_parsing`
- **Given**: Stage with `"time": "5 min"` in shape data
- **When**: `merge_envelope_into_lesson()` called
- **Then**: StageData.time_minutes = 5

### `test_time_parsing_invalid`
- **Given**: Stage with `"time": "N/A"` in shape data
- **When**: `merge_envelope_into_lesson()` called
- **Then**: ValidationError raised (time not parseable)

## TEMPLATES.md Contract Tests

### `test_template_renders`
- **Given**: Valid LessonPlanData
- **When**: `render_html(template, context)` called
- **Then**: Returns valid HTML string with `<html>`, `<head>`, `<body>`, lesson.topic in title

### `test_masthead_logos`
- **Given**: LessonPlanData with any topic
- **When**: HTML rendered
- **Then**: Contains two `<img>` tags with `src` starting with `data:image/png;base64,`

### `test_metadata_labels`
- **Given**: LessonPlanData with all fields
- **When**: HTML rendered
- **Then**: Contains text nodes "Teacher:", "Date:", "Class:", "Duration:", "CEFR Level:", "Lesson Shape:", "Materials:"

### `test_stage_header_merged`
- **Given**: LessonPlanData with 3 stages
- **When**: HTML rendered
- **Then**: Contains exactly 3 `colspan="4"` elements, one per stage

### `test_procedure_bullets`
- **Given**: Stage with 4 procedure items
- **When**: HTML rendered
- **Then**: Contains 4 `<li>` elements inside the stage's `<ul>`

### `test_subsidiary_aim_optional`
- **Given**: LessonPlanData without subsidiary_aim
- **When**: HTML rendered
- **Then**: "Subsidiary aim:" text does not appear

### `test_materials_list`
- **Given**: LessonPlanData with 2 materials
- **When**: HTML rendered
- **Then**: Both material items appear as text in the materials area

## CSS.md Contract Tests

### `test_page_size_a4`
- **Given**: Any rendered PDF
- **When**: `pdfinfo` run on output
- **Then**: Page size = 595.276 x 841.89 pts (A4)

### `test_multi_page_renders`
- **Given**: Lesson with 6+ stages (long procedure text)
- **When**: Rendered to PDF
- **Then**: PDF has >= 2 pages

### `test_font_arial`
- **Given**: Any rendered PDF
- **When**: `pdffonts` run on output
- **Then**: Lists Arial as embedded font (or ArialMT, Arial-BoldMT variants)

### `test_masthead_layout`
- **Given**: Any rendered PDF
- **When**: Text extracted from page 1 top
- **Then**: Contains "C·E·L Mathayom" centered text

### `test_merged_stage_rows`
- **Given**: Lesson with any stages
- **When**: Text extracted from PDF
- **Then**: Contains "STAGE 1:", "STAGE 2:", etc. as distinct text nodes

### `test_bulleted_procedure`
- **Given**: Stage with procedure items
- **When**: Text extracted from PDF
- **Then**: Procedure text appears with bullet character prefix
