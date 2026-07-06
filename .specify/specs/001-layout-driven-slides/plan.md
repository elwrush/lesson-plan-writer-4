# Implementation Plan: Layout-Driven Slides

**Branch**: `001-layout-driven-slides` | **Date**: 2026-07-06 | **Spec**: `.specify/specs/001-layout-driven-slides/spec.md`

**Input**: Feature specification — refactor reveal.js pipeline to use layout-enum structured data, deterministic resolver, and Jinja2 macros.

## Summary

Replace the current "LLM writes template code" pipeline with a "LLM emits structured data → resolver assigns cross-slide ids → Jinja2 macros render via slideshow_lib" pipeline. This eliminates the class of bugs where LLMs produce mismatched data-ids, broken auto-animate pairs, or incorrect fragment indices.

## Technical Context

**Language/Version**: Python 3.12+ (uv-managed)

**Primary Dependencies**: jinja2 3.1.x, pydantic 2.x, slideshow_lib (read-only), `markdown` library (for content slot markdown→HTML), reveal.js 6.0.1 (CDN)

**Storage**: None — filesystem I/O only (JSON in → HTML out)

**Testing**: pytest (100 lib + 5 render + 8 git-pages = 113 existing, plus new resolver/macro tests)

**Target Platform**: Static HTML (GitHub Pages)

**Project Type**: Pipeline script + Jinja2 templates

**Performance Goals**: Resolver <1ms for 30-slide deck

**Constraints**: `slideshow_lib/` is read-only; all existing tests must continue to pass; LLM must never touch HTML/attr generation

**Scale/Scope**: Single pipeline script (~200 new lines), 5 layout macros (~150 lines), resolver (~80 lines)

## Constitution Check

| Gate | Status | Notes |
|------|--------|-------|
| Simplicity (≤3 projects) | ✅ | Single script + templates |
| Anti-Abstraction (use features directly) | ✅ | Macros call `slideshow_lib` directly |
| Integration-First (contracts before code) | ✅ | Contracts defined in `contracts/` |
| Test-First (Red/Green) | ✅ | All new code test-first |
| Structured-Data-First | ✅ | Core of this feature |
| Pydantic Gate | ✅ | Already enforced |

## Project Structure

### Documentation (this feature)

```
.specify/specs/001-layout-driven-slides/
├── spec.md              # Feature spec (/speckit.specify)
├── plan.md              # This file (/speckit.plan)
├── research.md          # Tech research (/speckit.plan)
├── data-model.md        # Entities and I/O schemas (/speckit.plan)
├── quickstart.md        # Setup + verification (/speckit.plan)
└── contracts/           # Interface contracts (/speckit.plan)
    ├── RESOLVER.md
    └── MACROS.md
```

### Source Code

```
~/.kilo/skills/slideshow-renderer/
├── SKILL.md                          # Update: prompts for structured-data-only output
├── prompts/
│   ├── esl-voice.md                  # Unchanged
│   └── best-practices.md             # Unchanged
├── references/
│   └── slideshow_lib-quickref.md     # Unchanged (macros hide this from LLM)
└── scripts/
    ├── render.py                     # Update: add resolver + macro dispatch
    ├── macros.jinja2                 # NEW: one macro per layout type
    └── tests/
        └── test_render.py            # Update: resolver tests + macro tests

PROJECTS/TEST/
├── data.json                         # Update: use layout-driven format
└── slides/
    └── index.html                    # Re-rendered output
```

**Structure Decision**: Single pipeline script with co-located macros and tests. The `macros.jinja2` file is loaded by `render.py` via Jinja2's `FileSystemLoader`. No new directories or packages.

## Architecture Overview

```
LLM output (JSON)
    │
    ▼
Pydantic validation (DeckData + SlideRecord)  ─── rejects bad layout enum
    │
    ▼
Resolver (pure function)
    ├── groups slides by id
    ├── assigns auto_animate flags + group_ids
    ├── generates element_ids per group
    └── assigns sequential fragment_index
    │
    ▼
Jinja2 + macros.jinja2
    ├── render_content_slide()
    ├── render_two_column_slide()
    ├── render_auto_animate_pair()
    ├── render_code_slide()
    ├── render_image_slide()
    └── render_raw_slide()
    │  (each macro calls slideshow_lib functions)
    ▼
CDN skeleton wrapper
    │
    ▼
index.html (GitHub Pages-ready)
```

## Component Breakdown

### 1. Resolver (`render.py` — new function `resolve_deck`)
- Pure function: `dict -> dict`
- Groups slides by `id`
- Assigns `auto_animate`, `auto_animate_group_id`, `element_ids`, `data_id`, `fragment_index`
- No mutation of input

### 2. Macro template (`macros.jinja2`)
- 6 macros, one per layout type
- Each macro receives a single resolved slide dict (or group list for auto-animate-pair)
- Calls `slideshow_lib` functions for HTML generation
- Content fields (title, body) rendered as markdown

### 3. Render pipeline (`render.py` — updated `render()`)
- Loads data → validates with Pydantic → runs resolver → loads macros.jinja2 → renders using a dispatch template that selects the right macro → wraps in CDN skeleton
- Content slots (title, body) processed through `markdown_to_html` filter before macro insertion
- Updated `SlideModel` → `SlideRecord` with layout enum

### 4. Skill prompt update (`SKILL.md`)
- Remove instructions about writing Jinja2 templates
- Add instructions: "Emit structured data only — layout enum + content slots"

## Implementation Phases

### Phase 1: Pydantic models + resolver (test-first)
1. Write `SlideRecord` model with `LayoutType` enum (test first)
2. Write `resolve_deck()` function (test first)
3. Tests: auto-animate groups, fragment indices, edge cases

### Phase 2: Macro template (test-first)
1. Write `macros.jinja2` with all 6 macros
2. Test each macro renders correct HTML for known inputs

### Phase 3: Pipeline integration
1. Update `render.py` to use resolver + macro dispatch
2. Update existing render tests to pass with new pipeline
3. Wire up `markdown_to_html` filter for content slot rendering

### Phase 4: SKILL.md + prompts
1. Update SKILL.md to describe structured-data-only output
2. Verify LLM prompt contains zero reveal.js attribute names

### Phase 5: TEST validation
1. Update PROJECTS/TEST/data.json to use layout-driven format
2. Re-render TEST deck
3. View locally, verify auto-animate works
4. Deploy to GitHub Pages

## Complexity Tracking

No constitution violations — this feature reduces complexity by removing the LLM's need to write cross-referential HTML attributes.
