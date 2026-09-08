---
title: Wrap lesson-plan render + verify in a `just` recipe
status: accepted
date: 2026-09-08
deciders: Ed Rush
---

# Wrap lesson-plan render + verify in a `just` recipe

## Context
Producing the READING M2 lesson-plan PDF (Shape I — Reciprocal Teaching) is a
multi-command workflow: author a bespoke envelope (`{shape, metadata}`), render it
through the `write-lesson-plan` skill, then verify A4 size, embedded fonts, the
class/teacher/aims, and — critically — that a **reading** lesson has **no Transcript
section** and **no contextual images** beyond the two masthead logos. The final
`verify` was done by hand (pdfinfo/pdffonts/pymupdf content checks) each time, so the
gates could be skipped. Without a wrapper, the agent re-derives the envelope path and
the verify sequence every run.

## Decision
Add **`just lesson-plan "READING M2"`**, which (1) renders
`PROJECTS/{name}/lesson-plan-envelope.json` via the skill into the repo-root `PDF/` and
(2) runs a small **`scripts/verify_lesson_plan.py`** gate. The validator:

- recomputes the expected output path exactly as the skill's `make_output_path`
  (`PDF/lesson-plan-{date}-{topic}.pdf`), with a newest-PDF fallback;
- checks A4 (594.96 × 841.92 ±3pt) and ≥1 page;
- checks fonts embedded (pdffonts);
- checks content markers: topic, `class_name`, `teacher`, and the main-aim opening;
- asserts **no Transcript section unless the envelope sets `transcript`** — so a
  reading lesson can never silently carry one;
- asserts no contextual images: page 1 may hold only the two masthead logos, all
  other pages must be image-free.

The **envelope stays hand-authored by the agent** from the lesson shape + source
materials (like `reading.json` for `indread-render`). The recipe wraps only the
deterministic render + verify, so the A4/font/content gates always run and the output
never lands in `PROJECTS/{name}/`.

## Consequences

**Good:**
- One command (`just lesson-plan "READING M2"`) reproduces the render + verify and
  pins output to the mandated repo-root `PDF/`.
- The "no transcript for a reading lesson" and "no contextual images" rules become a
  hard gate instead of a manual check.
- Consistent with `just render` / `just indread-render` / `just git-pages`.

**Bad / cost:**
- The envelope content is not automated — the agent still authors each lesson's aims,
  stages and materials from the shape.
- `verify_lesson_plan.py` replicates the skill's slug logic; if the skill changes its
  output path, the validator's recomputation must be updated (it has a newest-PDF
  fallback as a safety net).

**Risks / follow-ups:**
- The validator treats the two masthead logos (Cambridge + ACT) as the only allowed
  images. Any future contextual image in a lesson-plan template would trip it — which
  is the intended guard.
- Stage times must still sum to `duration_minutes`; the recipe doesn't enforce that
  (the skill validates each stage is positive, not the total).
