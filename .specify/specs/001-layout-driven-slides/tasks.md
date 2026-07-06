---
description: "Task list for 001-layout-driven-slides"
---

# Tasks: Layout-Driven Slides

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/RESOLVER.md, contracts/MACROS.md

**Tests**: All tasks follow Red/Green TDD per constitution. Test tasks written first, confirmed FAIL, then implemented.

**Organization**: Tasks grouped by user story. Foundations must complete before user stories can begin.

## Phase 1: Setup

**Purpose**: Create missing files before any implementation begins.

- [X] T001 Create `macros.jinja2` at `~/.kilo/skills/slideshow-renderer/scripts/macros.jinja2` with macro stubs for all 6 layouts (content, two-column, auto-animate-pair, code, image, raw)

---

## Phase 2: Foundational — Pydantic Models

**Purpose**: Core data models that ALL user stories depend on. Must complete before any user story work.

- [X] T002 [P] Write `LayoutType` enum (`content | two-column | auto-animate-pair | code | image | raw`) with test in `scripts/tests/test_render.py`
- [X] T003 [P] Write `SlideRecord` model with `model_validator` (requires title/body/code unless raw) with test in `scripts/tests/test_render.py`
- [X] T004 [P] Write `ResolvedSlide` model (adds data_id, element_ids, auto_animate, fragment_index) with test in `scripts/tests/test_render.py`
- [X] T005 Write `DeckData` model (title, author, theme, slides list) with test in `scripts/tests/test_render.py`
- [X] T005b Add `markdown_to_html` filter to `slideshow_lib/filters.py` (using Python `markdown` library, `extra` extension) with test in `slideshow_lib/tests/test_filters.py`

**Checkpoint**: All models validated. Ready for user story implementation.

---

## Phase 3: User Story 1 — Emit Structured Data with Layout Enum (P1) 🎯 MVP

**Goal**: LLM produces structured data that validates against the layout enum and Pydantic models. No template code, no raw HTML, no reveal.js attribute names in the output.

**Independent Test**: A JSON deck with all 6 layout types, mixed auto-animate groups, and content-only slides passes Pydantic validation.

### Implementation for US1

- [X] T006 [P] [US1] Write test for deck JSON with all 6 layout types — assert validation succeeds
- [X] T007 [P] [US1] Write test for deck with invalid layout enum — assert validation rejects
- [X] T008 [P] [US1] Write test for deck with empty slide (no title/body/code, not raw) — assert validation rejects

---

## Phase 4: User Story 2 — Named Layout Macros (P1)

**Goal**: Six Jinja2 macros, one per layout type. Each macro produces correct HTML from resolved slide data by calling `slideshow_lib` functions.

**Independent Test**: Feed known resolved data into each macro, verify correct HTML output (data-attributes, structure, content).

### Implementation for US2

- [X] T009 [P] [US2] Write `render_content_slide` macro — test renders correct `<section>` with title/body/notes
- [X] T010 [P] [US2] Write `render_two_column_slide` macro — test body split on `|||` produces left/right columns
- [X] T011a [US2] Write `render_auto_animate_pair` macro structure (template code) — renders multiple `<section data-auto-animate>` elements with shared attributes from the resolved slide group
- [X] T011b [US3] Write test for `render_auto_animate_pair` with resolver output — verify matching data-ids across paired slides (depends on T020)
- [X] T012 [P] [US2] Write `render_code_slide` macro — test renders `<pre><code>` with language class
- [X] T013 [P] [US2] Write `render_image_slide` macro — test renders background image via `slide_bg()`
- [X] T014 [P] [US2] Write `render_raw_slide` macro — test passes body verbatim

**Checkpoint**: All 6 macros produce verified HTML. LLM can select any layout.

---

## Phase 5: User Story 3 — Deterministic Resolver (P2)

**Goal**: `resolve_deck()` assigns all cross-slide attributes before rendering: data-ids, fragment indices, auto-animate grouping.

**Independent Test**: Feed a deck with auto-animate pairs, single slides, and mixed content — resolver output has matching data-ids per group and sequential fragment indices.

### Implementation for US3

- [X] T015 [US3] Write test: resolver assigns matching `data-id` to elements across auto-animate pair
- [X] T016 [US3] Write test: resolver assigns sequential `fragment_index` across entire deck (1..N)
- [X] T017 [US3] Write test: resolver omits `data-auto-animate` for single-slide groups (size 1)
- [X] T018 [US3] Write test: resolver handles groups of size 3+ (all share group_id, sequential element_ids)
- [X] T019 [US3] Write test: resolver handles empty deck (returns as-is, no crash)
- [X] T020 [US3] Implement `resolve_deck()` in `scripts/render.py` — pure function, grouped by id, assigns all cross-slide attrs
- [X] T021 [US3] Integrate resolver into render pipeline — resolver runs before Jinja2 macro dispatch (moved to Phase 6)

---

## Phase 6: Pipeline Integration

**Purpose**: Wire all components together. Update render.py to use resolver + macro dispatch.

- [X] T022 Update `scripts/render.py` to load `macros.jinja2` as default template (relative to script location). The `--template` CLI arg becomes optional — when omitted, default to `macros.jinja2`.
- [X] T023 Update `scripts/render.py` to dispatch each slide to the correct macro based on `layout` field
- [X] T024 Add markdown rendering to content slots (title, body) via `markdown_to_html` filter
- [X] T025 Update existing render tests (test_render_py_exists, test_render_minimal_template, etc.) to work with new pipeline
- [X] T026 Run all tests — confirm existing library tests (113) + new resolver/macro tests (27) all pass

---

## Phase 7: Polish & Cross-Cutting

**Purpose**: Documentation, TEST validation, deploy.

- [X] T027 [P] Update SKILL.md at `~/.kilo/skills/slideshow-renderer/SKILL.md` — instruct LLM to emit structured data only (layout enum + content slots, never template code or HTML)
- [X] T027b [P] Verify SKILL.md prompt contains zero reveal.js attribute names (grep for `data-`, `auto-animate`, `class="fragment"`) — add a quick automated check to tests or a manual review note
- [X] T028 Update PROJECTS/TEST/data.json to use layout-driven format (layout enum, id, step fields)
- [X] T029 Re-render TEST deck, verify locally with Python HTTP server, confirm auto-animate works
- [X] T030 Deploy TEST to GitHub Pages via `/git-pages TEST`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (P1)**: No deps — create stubs file
- **Foundational (P2)**: Depends on Setup — BLOCKS all user stories
- **US1 + US2 (P3-P4)**: Depend on Foundational — can proceed in parallel
- **US3 (P5)**: Depends on Foundational — tightly coupled with US1 (both involve models)
- **Pipeline Integration (P6)**: Depends on P3, P4, P5
- **Polish (P7)**: Depends on P6

### Parallel Opportunities

- T002-T005 (models): All parallel — different model classes, no file conflicts
- T006-T008 (US1 tests): All parallel — standalone data validation
- T009-T014 (US2 macros): T009, T010, T011a, T012, T013, T014 are parallel (independent macro structures). T011b depends on resolver (T020) and lives in Phase 5.
- T015-T021 (US3 resolver): Sequential — tests first, then implementation, then integration
- T022-T026 (pipeline): Sequential — depends on all components being ready
- T027 (SKILL.md): Parallel with T028 — independent files

### MVP Scope

Phase 1 + Phase 2 + Phase 3 (US1: models + validation) = Validates that LLM output conforms to the new schema. Deliverable: Pydantic models with `LayoutType` enum and `SlideRecord` validation.
