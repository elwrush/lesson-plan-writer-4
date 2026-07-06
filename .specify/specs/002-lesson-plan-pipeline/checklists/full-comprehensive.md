# Checklist: Lesson Plan Writer Pipeline — Full Comprehensive

**Focus**: Requirement completeness, clarity, consistency, edge case coverage, acceptance criteria quality, non-functional requirements, dependencies and assumptions.

**Source documents**: spec.md, plan.md, tasks.md, data-model.md, contracts/RENDERER.md, contracts/TEMPLATES.md, contracts/CSS.md, research.md

---

## Requirement Completeness

- [x] CHK001 Envelope JSON schema fully specified. data-model.md has input schema with `shape` + `metadata`. Plan.md has InputEnvelope Pydantic model. Spec Q1 confirms envelope wrapper. [Completeness, Spec FR-001, data-model.md §InputEnvelope]
- [x] CHK002 Field mapping documented: `stage_aim → goal`, `time` string → `time_minutes` (regex), `stage_number` preserved. data-model.md §StageData + plan.md §Pydantic models. [Completeness, data-model.md §StageData, plan.md §Pydantic models]
- [x] CHK003 Time format resolved: parsed via regex `(\d+)` from `"5 min"` → `5`. [Completeness, data-model.md §Validation Rules]
- [x] CHK004 CSS column widths documented in contracts/CSS.md: Time 8%, Goal 22%, Procedure 58%, Int 12%. [Completeness, contracts/CSS.md §lesson-plan.css]
- [x] CHK005 Ghostscript error handling: FR-008 covers missing `gs` (warning + passthrough). `normalise_pdf()` raises `CalledProcessError` for other failures (permissions, corrupt input). Version check not needed for v1. [Completeness, spec.md FR-008, contracts/RENDERER.md normalise_pdf]

---

## Requirement Clarity

- [x] CHK006 "Visually matching" defined as text-extraction comparison (same words present, same order, same page count). No pixel diff required. Spec §Assumptions + Q3. Tolerance: same structure, proportional spacing. [Clarity, Spec SC-001, §Clarifications Q3]
- [x] CHK007 Slideshow URL format: plain string in materials array, rendered as a bullet item. data-model.md example shows `"Slideshow URL: https://..."`. Hyperlinked in HTML but plain text in print. [Clarity, Spec FR-004, §Clarifications Q5]
- [x] CHK008 "Survive flattening" verified by text-extraction comparison (content presence and ordering). Position verification not automated — acknowledged limitation in Spec §Resolved. [Clarity, Spec SC-002, §Clarifications Q3]
- [x] CHK009 "Proportional spacing" defined as "same structure, same relative positioning, no content reflow." Not pixel-exact. Different PDF engines produce different inter-word spacing. [Clarity, Spec §Assumptions]
- [x] CHK010 Interaction field: free-text string. Not a controlled vocabulary. Examples: "T-Ss", "Ss-Ss", "S", "T-Ss, S". Documented in data-model.md §StageData. [Clarity, data-model.md §StageData]

---

## Requirement Consistency

- [x] CHK011 FR-009 conditionality resolved: conditional on Ghostscript being available. [Consistency, Spec FR-009]
- [x] CHK012 Metadata labels (FR-004 display text) vs field names (data-model keys): labels are display text, mapped in the Jinja2 template. "Lesson Shape" → `lesson_shape` field — mapping is 1:1 with display-friendly formatting. No separate mapping table needed. [Consistency, Spec FR-004, data-model.md]
- [x] CHK013 `header` HTML content from shape: NOT used in the lesson plan PDF output. Only `example_lesson_plan.stages` and shape metadata are consumed. Header is shape-internal metadata, not rendered. [Consistency, data-model.md]

---

## Acceptance Criteria Quality

- [x] CHK014 US1 Scenario 2 testable via text extraction: `pdftotext` extracts all text including "5 min", stage names, goal text. Verification checks text content, not table positioning. Table structure verified by expected column order. [Measurability, Spec US1]
- [x] CHK015 US2 Scenario 2: acknowledged limitation — text extraction verifies content presence, not pixel position. Position verified indirectly: if all content is present and page count matches, layout is preserved. [Measurability, Spec US2, §Clarifications Q3]
- [x] CHK016 US3 testable without WeasyPrint: `resolve_skill_root()` is a pure `Path(__file__).parent.parent` lookup. Unit testable with mocked file system. [Measurability, Spec US3]

---

## Scenario Coverage

- [x] CHK017 Single-stage lesson: valid input (minimum: 1 stage). Render produces 1-page-or-more PDF. Test fixture T016 should include a 1-stage variant. [Coverage]
- [x] CHK018 `subsidiary_aim` omitted: template conditionally renders the paragraph. contracts/TEMPLATES.md contract test covers this. [Coverage]
- [x] CHK019 Empty `materials`: renders the label with no bullets. Template handles via `{% if lesson.materials %}` guard. Added to edge cases in spec and Phase 7 tasks. [Coverage, Spec §Edge Cases]
- [x] CHK020 Long shape name (Shape F): test fixture T016 uses shape-f with the full name string. Reference PDF shows wrapping behavior — CSS `word-wrap: break-word` handles it. [Coverage, T016]

---

## Edge Case Coverage

- [x] CHK021 Non-sequential stage numbers: Pydantic `field_validator` rejects gaps. data-model.md §Validation Rules: "stage_number must be sequential (no gaps)". [Edge case, data-model.md §Validation Rules]
- [x] CHK022 `time_minutes = 0`: rejected by Pydantic (`time_minutes must be > 0`). data-model.md §Validation Rules. [Edge case, data-model.md §Validation Rules]
- [x] CHK023 Empty-string procedure items: stripped before validation. If all items empty → `ValidationError` (procedure must have >= 1 item). Added to T006 implementation. [Edge case]
- [x] CHK024 Both logos missing: FR-012 (warn + continue). T031 implements. Template renders without `<img>` tags. [Edge case, Spec FR-012, T031]
- [x] CHK025 Read-only output path: caught by `OSError` at write time, exit code 4. Standard behavior, documented in contracts/RENDERER.md. [Edge case, contracts/RENDERER.md]
- [x] CHK026 Missing `shape` key: `InputEnvelope` Pydantic model requires `shape: dict`. Missing key → `ValidationError` with field-level message. [Edge case, data-model.md]

---

## Non-Functional Requirements

- [x] CHK027 Cold-start performance: <5s target is for a single run from cold start on WSL. First invocation slower due to module imports; subsequent runs benefit from OS cache. Target is measured from process start to file write. [Non-functional, plan.md]
- [x] CHK028 System library deps documented in quickstart.md: `libpango-1.0-0`, `libcairo2`, `libffi8`, `ghostscript`. Not checked at startup — assumes apt/dnf handles it. [Non-functional, plan.md, quickstart.md]
- [x] CHK029 Ghostscript version: GS 10.0+ recommended per research.md. No runtime version check — GS 9.x flags are compatible with this command set. Version check not needed for v1. [Non-functional, research.md]
- [x] CHK030 PDF quality: SC-004 requires "opens without errors, correct page count, embedded fonts." No PDF/A requirement. For school print use, this is sufficient. [Non-functional, Spec §SC-004]

---

## Dependencies & Assumptions

- [x] CHK031 Shape files unchanged — resolved: manual envelope wrapper via `--data`. [Dependency, Spec §Clarifications Q1]
- [x] CHK032 Arial fallback: CSS specifies `font-family: Arial, Helvetica, sans-serif`. Helvetica and generic sans-serif provide fallback if Arial is missing. On Ubuntu, `ttf-mscorefonts-installer` provides Arial; otherwise system sans-serif is used. Ghostscript embeds whatever font the system provides at render time. [Dependency, research.md, contracts/CSS.md]
- [x] CHK033 `stage` → `stage_name` mapping documented in data-model.md §StageData and plan.md §Pydantic models. Shape uses `"stage"` (string), internal uses `stage_name`. [Dependency, data-model.md]
- [x] CHK034 Known differences from Typst: font (Arial vs Roboto), rendering engine (WeasyPrint vs Typst). Documented as acceptable in plan.md §Phase 5. Outputs have same structure, not pixel-identical. [Dependency, plan.md §Phase 5]
- [x] CHK035 Kilo skills format compliance documented in constitution.md §VII. Plan.md constitution check confirms alignment. T025 ensures SKILL.md frontmatter matches directory name. [Dependency, constitution.md]

---

## Summary

| Category | Items | Status |
|----------|-------|--------|
| Requirement Completeness | CHK001–CHK005 | 5 items |
| Requirement Clarity | CHK006–CHK010 | 5 items |
| Requirement Consistency | CHK011–CHK013 | 3 items |
| Acceptance Criteria Quality | CHK014–CHK016 | 3 items |
| Scenario Coverage | CHK017–CHK020 | 4 items |
| Edge Case Coverage | CHK021–CHK026 | 6 items |
| Non-Functional Requirements | CHK027–CHK030 | 4 items |
| Dependencies & Assumptions | CHK031–CHK035 | 5 items |
| **Total** | | **35 items** |
