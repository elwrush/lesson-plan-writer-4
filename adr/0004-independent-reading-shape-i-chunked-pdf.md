---
title: Produce Shape-I reciprocal-teaching leveled texts as one merged PDF
status: accepted
date: 2026-09-08
deciders: Ed Rush
---

# Produce Shape-I reciprocal-teaching leveled texts as one merged PDF

## Context
A reading lesson follows **Shape I (Reciprocal Teaching)**: groups of four rotate
the Predictor / Clarifier / Questioner / Summariser roles while reading a text in
**sections**. For the "Meta $18bn child-safety settlement" article we needed two
leveled versions (B1 emergent, B2 emergent) of one news story, each split into
**four chunks**, each chunk carrying a **headline** so the Predictor can predict
*before* reading that chunk. The `independent-reading-text-generator` skill is
built for a **single, continuous extended-reading text** (34–36 min, one target
line, line numbers, gloss footers) — not for a 4-chunk, 8-minute, two-level
handout. Its default output root also lives under `INDEPENDENT-READING/…`, while
this repo keeps lesson artifacts under `PROJECTS/{name}/`.

## Decision
Drive the per-lesson product with a **project-local `SCRIPTS/produce.py` + a
`SCRIPTS/reading.json` envelope**, and wrap the whole thing behind a new
**`just indread-render`** recipe. Concretely:

- **Target the 8-minute reciprocal pace, not the 36-minute extended pace.**
  Shape I reads each section silently ~1.5–2 min; 4 chunks ≈ 8 min of reading.
  So `minutes=8` → B1 target 920 / cap 1,104, B2 target 960 / cap 1,152. The body
  lands ~990 (B1) and ~1,020 (B2) words — NOT thousands.
- **Render each level separately, then merge into ONE PDF (B1 pages first, then
  B2 pages)**. `render()` emits one `ReadingText` per level; `produce.py` renders
  both and `pymupdf insert_pdf` appends them head-to-tail, preserving each
  section's own masthead, CEFR badge, running head and page numbering.
- **Chunk headlines use the template's `p.section-head` class** — body paragraphs
  are passed as dicts `{"class": "section-head", "text": …}` and interleaved with
  the sanitised body paragraphs. Headlines are excluded from the canonical
  (body-only) word count.
- **Thai currency spell-outs + baht conversions sit in the body** (e.g. $18bn →
  `สิบแปดพันล้านดอลลาร์, about 594 พันล้านบาท`), because middle-school Thai readers
  cannot parse western-script large numerals. These are literal `\u0e00` runs that
  Chromium renders via the installed **Loma** Thai font (font fallback) and that
  the `[a-z]+` word counter ignores, so the count is unaffected.
- **Output goes to `PROJECTS/READING M2/PDF/`** (repo project folder, user
  requirement), not the skill's `INDEPENDENT-READING/…` default.
- The recipe **only runs post-gate**; the simplify → Kimi → human gates stay
  interactive and are **not** wrapped.

## Consequences

**Good:**
- One command (`just indread-render "READING M2"`) reproduces the render → combine
  → verify chain with correct ordering and paths.
- Two leveled versions ship as one printable handout (B1 group, B2 group), with
  predictor-usable chunk headlines and comprehensible Thai magnitude cues.
- The Kimi/human gates remain the single acceptance gate; `produce.py` refuses to
  render until `approved=true`.

**Bad / cost:**
- Output path differs from the skill default, so a future agent must know to read
  `PROJECTS/{name}/PDF/` (documented in AGENTS.md + ADR).
- The count floor forces some padding to hit the band; Kimi flagged a few padded
  sentences, but they're needed to satisfy `[target, cap]`.
- `produce.py` re-renders everything on each run (no incremental rebuild).

**Risks / follow-ups:**
- The combined PDF keeps per-section page numbering (B2 restarts at 1). If a
  single continuous page sequence is wanted, the merge must renumber — not done.
- Thai rendering depends on the **Loma** font being present on the build machine.
- Gloss markers are assigned by the measure pass; any word whose gloss is dropped
  renumbers the survivors — keep gloss words present in the body.
- The `p.section-head` lines increment the JS line-number counter (their number is
  hidden by CSS but still counted), so every-5th markers shift by the number of
  headers — cosmetic only, verify still passes.
