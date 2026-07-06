# Checklist: Layout-Driven Slides — Full Comprehensive

**Focus**: Requirement completeness, clarity, consistency, edge case coverage, acceptance criteria quality, non-functional requirements, dependencies and assumptions.

**Source documents**: spec.md, plan.md, tasks.md, data-model.md, contracts/RESOLVER.md, contracts/MACROS.md, research.md

---

## Requirement Completeness

- [ ] CHK001 Are all 6 layout types (`content`, `two-column`, `auto-animate-pair`, `code`, `image`, `raw`) defined with their rendering behavior? [Completeness, Spec FR-001, data-model.md LayoutType]
- [ ] CHK002 Is the `media` field schema fully specified (supported types: video/audio/iframe, which fields are required vs optional)? [Completeness, Spec §Key Entities, data-model.md SlideRecord]
- [ ] CHK003 Is the `fragment_order` input field's purpose specified relative to the resolver's `fragment_index` output field? (Is it a hint, an override, or ignored?) [Completeness, Spec Edge Cases, data-model.md §Validation Rules]
- [ ] CHK004 Is the markdown rendering engine specified (which filter, what subset of markdown, what happens with unsafe HTML in markdown)? [Completeness, Spec FR-008]
- [ ] CHK005 Is the storage format for slide backgrounds/images specified? (Local path? CDN URL? Embedded base64? Must match reveal.js expectations.) [Completeness, plan.md Technical Context]

---

## Requirement Clarity

- [ ] CHK006 Is "matching data-id" precisely defined? (Must the string be identical byte-for-byte? Same case? Case-insensitive?) [Clarity, Spec FR-003, contracts/RESOLVER.md]
- [ ] CHK007 Is "bypass all macros and resolver attribute assignment" for `raw` layout unambiguous about whether the slide still gets a `data_id`/`fragment_index` from the resolver? [Clarity, Spec FR-009, contracts/RESOLVER.md §Edge Cases]
- [ ] CHK008 Is "sequential fragment index across the entire deck" defined as 1-based or 0-based? [Clarity, Spec FR-004, data-model.md ResolvedSlide]
- [ ] CHK009 Are "sequential `step` values" required to be contiguous (1, 2, 3...) or could they be non-contiguous (1, 3, 7)? [Clarity, Spec FR-002]
- [ ] CHK010 Is the `element_ids` naming convention specified? (What elements get ids? Does every element type get one, or only things inside auto-animate groups?) [Clarity, data-model.md ResolvedSlide, contracts/RESOLVER.md]

---

## Requirement Consistency

- [ ] CHK011 Does FR-009 ("raw bypasses all macros and resolver attribute assignment") conflict with the resolver contract that processes ALL slides before rendering? (If the resolver assigns fragment_index to every slide, does raw get one or null?) [Consistency, Spec FR-009 vs FR-010/FR-011]
- [ ] CHK012 Do the success criteria reference existing tests (SC-004: "113 tests") that will become inaccurate as new tests are added? (Should refer to "existing library tests" rather than a hardcoded count.) [Consistency, Spec SC-004]
- [ ] CHK013 Does US4 independent test ("renders the content verbatim, bypassing all layout macros") contradict FR-006 ("each layout type has exactly one rendering component")? (The raw layout HAS a render_raw_slide macro — it just doesn't transform content. The test should say "bypasses content transformation" not "bypasses macros.") [Consistency, Spec US4 vs FR-006]

---

## Acceptance Criteria Quality

- [ ] CHK014 Is US1 Acceptance Scenario 2 ("5 slides with layout content render as standalone sections with no auto-animate") testable without the resolver? (Should this test validate the data model, not the rendered output?) [Measurability, Spec US1]
- [ ] CHK015 Is US3 Acceptance Scenario 2 ("slides with fragment_index: 3 and fragment_index: 5 produce sequential indices 1..N across the deck") specifying that input fragment_order is IGNORED by the resolver? If so, state it explicitly. [Measurability, Spec US3]
- [ ] CHK016 Is SC-001 ("every auto-animate pair has verified matching data-ids") verifiable in automated tests, or does it require manual inspection of rendered HTML? [Measurability, Spec SC-001]

---

## Scenario Coverage

- [ ] CHK017 Is the scenario "deck with only 1 slide" covered? (Minimum viable input — single content slide, no groups.) [Coverage]
- [ ] CHK018 Is the scenario "deck with no `id` values" covered? (Every slide is its own group of size 1.) [Coverage]
- [ ] CHK019 Is the scenario "deck with mixed `layout` types and mixed group sizes" covered? (1 content + 1 auto-animate-pair of size 2 + 1 code + 1 raw + 1 auto-animate-pair of size 3.) [Coverage]
- [ ] CHK020 Is the scenario "notes field contains markdown (bold, italics, links)" covered? Does the notes filter handle markdown or plain text only? [Coverage]

---

## Edge Case Coverage

- [ ] CHK021 Is the edge case "auto-animate group of size 0" covered? (Slides referencing an id that doesn't exist elsewhere.) [Edge case, Spec §Edge Cases]
- [ ] CHK022 Is the edge case "step values out of order" covered? (Steps [2, 1] instead of [1, 2]. Does the resolver sort by step or preserve input order?) [Edge case]
- [ ] CHK023 Is the edge case "empty string in content slots" covered? (title="", body="", code="". Does the macro render an empty element or skip it?) [Edge case, Spec §Edge Cases]
- [ ] CHK024 Is the edge case "raw layout with valid reveal.js HTML using data-attributes" covered? (Does the resolver still skip raw slides, potentially causing mismatched auto-animate chains?) [Edge case, Spec §Edge Cases]
- [ ] CHK025 Is the edge case "special characters in id (spaces, Unicode, hyphens)" covered? (data-id values must be valid HTML attribute values.) [Edge case]
- [ ] CHK026 Is the edge case "deck with no title field" covered? (Is title required or optional in DeckData?) [Edge case, data-model.md DeckData]

---

## Non-Functional Requirements

- [ ] CHK027 Is resolver determinism specified as a requirement? (Given identical input, the resolver MUST produce identical output. SC-002 covers this, but it should be an explicit FR.) [Non-functional, Spec SC-002]
- [ ] CHK028 Is the resolver's input immutability requirement specified? (FR-011 covers "MUST NOT mutate input" — confirmed present.) [Non-functional, Spec FR-011]
- [ ] CHK029 Is the performance requirement for the resolver specified? (research.md estimates <1ms for 30 slides — should this be a bounded requirement?) [Non-functional, research.md]
- [ ] CHK030 Is the LLM output constraint documented in an enforceable way? (SC-003: "zero reveal.js attribute names in LLM prompt." This is a prompt constraint, not a system constraint. Is there a mechanism to enforce it, or is it a guideline?) [Non-functional, Spec SC-003]

---

## Dependencies & Assumptions

- [ ] CHK031 Is the assumption that "slideshow_lib is read-only" documented and is there a process if a bug is found in slideshow_lib during macro testing? [Dependency, Spec §Assumptions]
- [ ] CHK032 Is the assumption that "content inside slots is markdown text" documented with the caveat that raw HTML content (tables, divs) will be escaped by markdown processing? [Dependency, Spec §Assumptions]
- [ ] CHK033 Is the assumption that "markdown processing is via Jinja2 markdown filter" consistent with the research finding that `| markdown` is NOT a built-in Jinja2 filter and requires a custom extension? [Assumption, Spec FR-008, research.md]
- [ ] CHK034 Is the existing TEST deck (Present Perfect) documented as the validation benchmark, and is its expected output specified? (What should the rendered deck look like? How many slides? Which layouts?) [Dependency, Spec §Assumptions]

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
| Dependencies & Assumptions | CHK031–CHK034 | 4 items |
| **Total** | | **34 items** |
