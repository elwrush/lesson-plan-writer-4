# Feature Specification: Layout-Driven Slides

**Feature Branch**: `001-layout-driven-slides`

**Created**: 2026-07-06

**Status**: Draft

**Input**: Analysis of Jinja2 pipeline tiers — the LLM should never write data-ids, fragment indices, or cross-slide attributes. Instead, it emits structured data with a layout enum, and deterministic code handles cross-slide continuity.

## User Scenarios & Testing

### User Story 1 — Emit structured data with layout enum (Priority: P1)

As a lesson content creator, I want to describe each slide by picking a layout name and filling in content fields, so that I never need to write reveal.js HTML attributes or worry about matching data-ids across auto-animate pairs.

**Why this priority**: This is the core architectural change. Every other improvement depends on the LLM producing structured layout data instead of template code. Without this, cross-slide attribute bugs persist.

**Independent Test**: A deck with two auto-animate slides sharing `id: "grammar-box"` and `step: 1` / `step: 2` can be fed through the pipeline, and the resolver assigns matching data-id attributes to both slides without human intervention.

**Acceptance Scenarios**:

1. **Given** a deck JSON with layout `auto-animate-pair` and two slides sharing `id: "tense-compare"`, **When** the resolver processes it, **Then** both slides receive identical `data-id` values on matching elements and `data-auto-animate` on the `<section>`.
2. **Given** a deck with 5 slides using layout `content`, **When** rendered, **Then** each slide is a standalone `<section>` with no auto-animate attributes.
3. **Given** a slide with layout `two-column`, **When** rendered, **Then** the output contains a left column and right column inside the same `<section>`.

---

### User Story 2 — Named layout macros with content slots (Priority: P1)

As a template author, I want a fixed set of Jinja2 macros (one per layout type) that handle all reveal.js HTML generation by calling `slideshow_lib`, so that the LLM never needs to know about `data-*` attributes, `data-auto-animate` syntax, or fragment class conventions.

**Why this priority**: Moving the LLM away from HTML generation requires well-tested macros that are guaranteed correct. Every layout the LLM can select must have a corresponding macro.

**Independent Test**: Each macro renders correct HTML for at least 3 different content inputs, verified by tests that check for correct data attributes, class names, and element structure.

**Acceptance Scenarios**:

1. **Given** an `auto-animate-pair` macro, **When** invoked with two slides sharing `id` but different content, **Then** the output contains two `<section data-auto-animate>` elements with matching `data-id` on inner elements.
2. **Given** a `content` macro, **When** invoked with title and body markdown, **Then** the output is a single `<section>` with an `<h2>` and `<p>` or rich markdown content.
3. **Given** a `raw` macro, **When** invoked with raw HTML content, **Then** the HTML is inserted verbatim into the output.

---

### User Story 3 — Deterministic resolver for cross-slide continuity (Priority: P2)

As a quality engineer, I want the resolver to assign all data-ids and fragment indices before Jinja2 rendering, so that auto-animate pairs are guaranteed to have matching attributes and no fragment index collisions occur across the deck.

**Why this priority**: Without deterministic cross-slide continuity, manual review of every auto-animate pair is required. This makes the pipeline unreliable for production use.

**Independent Test**: A deck JSON is processed by the resolver in isolation. The output JSON has all data-ids assigned, fragment indices sequential across the deck, and auto-animate attributes only on paired slides.

**Acceptance Scenarios**:

1. **Given** a deck with 3 content slides followed by 2 auto-animate slides, **When** the resolver runs, **Then** the first 3 slides have no `data-auto-animate`, and the last 2 share the same `data-auto-animate-id`.
2. **Given** slides with `fragment_index: 3` and `fragment_index: 5` in the same deck, **When** the resolver runs, **Then** all fragment indices are sequential (1, 2, 3...N) across the entire deck.
3. **Given** a deck with a single slide in an auto-animate group (no pair), **When** the resolver runs, **Then** the slide renders without `data-auto-animate` attributes.

---

### User Story 4 — Raw HTML escape hatch (Priority: P3)

As a power user, I want a `raw` layout type that passes content through unmodified, so that edge cases not covered by the macro set are always possible.

**Why this priority**: Rarely needed, but prevents the macro set from being a hard constraint on creative slide design.

**Independent Test**: A deck with a single `raw` slide renders the content verbatim, with body inserted as-is inside a bare `<section>` wrapper.

**Acceptance Scenarios**:

1. **Given** a slide with `layout: "raw"` and raw HTML content, **When** rendered, **Then** the content is inserted directly into the slide output with no macro processing.
2. **Given** a deck mixing `raw` and standard layout slides, **When** rendered, **Then** the resolver still assigns data-ids to the standard layout slides but does not modify the raw slide.

---

### Edge Cases

- What happens when an auto-animate group has only 1 slide (no pair)? Resolver should silently omit `data-auto-animate`.
- What happens when an auto-animate group has 3+ slides? Resolver assigns them all the same `data-auto-animate-id`, sequential matching `data-id` per step.
- What happens when an unrecognized layout name is provided? Pydantic validation rejects the deck before resolver runs.
- What happens when content slots are empty? The macro renders an empty element (`<h2></h2>`, `<p></p>`) rather than crashing or omitting the element. The `<section>` wrapper is always emitted.
- What happens when `raw` layout contains broken HTML? No validation — the escape hatch passes content through as-is.
- What happens when fragment indices collide (two slides declare `fragment_index: 1`)? Resolver re-assigns sequential indices, ignoring the input values.

## Requirements

### Functional Requirements

- **FR-001**: Layout MUST be one of a fixed set: `content`, `two-column`, `auto-animate-pair`, `code`, `image`, `raw`. The set is defined once and used consistently across all slides.
- **FR-002**: Each slide MUST declare `layout` and `id` (string). Auto-animate pairs share the same `id` with sequential `step` values.
- **FR-003**: Resolver MUST assign matching `data-id` attributes to all elements sharing the same `id` across steps.
- **FR-004**: Resolver MUST assign fragment indices as sequential 1-based integers across the entire deck, IGNORING any `fragment_order` value in the input. The `fragment_order` field is a rendering hint within a single slide, not an input to the resolver.
- **FR-005**: Resolver MUST set `data-auto-animate` on `<section>` only for slides in multi-step groups (size >= 2).
- **FR-006**: Each layout type MUST have exactly one rendering component. The renderer selects the component based on the slide's layout field.
- **FR-007**: Rendering components MUST use the shared library functions (`slideshow_lib`) for attribute generation — never write raw HTML data-attributes inline.
- **FR-008**: Content slots (title, body, notes) MUST accept markdown text. A `markdown_to_html` filter is added to `slideshow_lib` — it converts markdown to safe HTML using the Python `markdown` library with `extra` extension. (Jinja2 has no built-in markdown filter; this is a custom filter registered via `setup_jinja`.)
- **FR-009**: `raw` layout MUST bypass macro content transformation, passing body content as-is into the slide output. The resolver still assigns `fragment_index` and `data_id` to raw slides for structural consistency (unique DOM ids, sequential indices), but no `data-auto-animate` group attributes or `element_ids` are assigned. The raw macro wraps content in `<section>` only and inserts body verbatim.
- **FR-010**: `render.py` MUST run resolver BEFORE macro rendering, passing resolved data into the template context.
- **FR-011**: Resolver MUST NOT mutate the input Pydantic model — it produces a new resolved data structure.
- **FR-012**: All existing `slideshow_lib` tests (100) and render tests (5) and git-pages tests (8) MUST continue to pass.

### Key Entities

- **SlideRecord**: Input data from LLM. Fields: `layout` (enum), `id` (string, for grouping), `step` (int, sequential within group), `title` (markdown), `body` (markdown), `media` (object, optional), `notes` (markdown, optional), `fragment_order` (int, optional).
- **ResolvedSlide**: Output of resolver. Fields: all SlideRecord fields plus `data_attrs` (dict of assigned data-* attributes), `fragment_index` (int, globally sequential), `element_ids` (dict of element_name → data-id string).
- **LayoutMacro**: Jinja2 `{% macro %}` in the template file. One per layout type. Signature: `{% macro render_content_slide(slide) %}`, `{% macro render_auto_animate_pair(slides) %}`, etc.
- **DeckData**: Top-level container. Fields: `title`, `author`, `theme`, `slides` (list of SlideRecord).

## Success Criteria

### Measurable Outcomes

- **SC-001**: A deck with auto-animate pairs, content slides, and code slides can be produced from a single JSON input, and every auto-animate pair has verified matching data-ids.
- **SC-002**: Resolver assigns all cross-slide attributes deterministically — given the same input, the resolved output is identical across runs.
- **SC-003**: The LLM prompt for slide creation contains exactly zero reveal.js attribute names (no `data-*`, no `data-auto-animate`, no `class="fragment"`).
- **SC-004**: All existing `slideshow_lib` tests (100), render tests, and git-pages safety tests continue to pass, plus new resolver tests and macro tests.
- **SC-005**: A slide deck can be edited by changing only content fields in the JSON — no template modifications needed for content-only changes.

## Assumptions

- The existing `slideshow_lib` functions (23 globals, 2 filters, 100 tests) remain the authoritative source of reveal.js HTML generation — macros call these functions exclusively.
- The LLM output format is Pydantic-validated JSON (per constitution Article V), so malformed layout names or missing content fields are caught before the resolver runs.
- Content inside slots is markdown text — the LLM's strength. No raw HTML inside slots except the `raw` layout type.
- The existing TEST project (Present Perfect slideshow) will be updated to validate the new pipeline end-to-end.
