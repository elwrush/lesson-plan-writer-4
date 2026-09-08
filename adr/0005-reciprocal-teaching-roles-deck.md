---
title: Use canonical Reciprocal-Teaching roles and round structure on Shape-I decks
status: accepted
date: 2026-09-08
deciders: Ed Rush
---

# Use canonical Reciprocal-Teaching roles and round structure on Shape-I decks

## Context
The Reading M2 deck follows **Shape I (Reciprocal Teaching)**: groups of four rotate
the Predictor / Clarifier / Questioner / Summariser roles across the four chunks.
When authoring the "Your four roles" slide from memory, I wrote the Clarifier as "ask
about hard words" (a vocabulary checker) and the Questioner as "Why…?" (a quick
check). Both were wrong. The classroom materials define these roles differently:
the Clarifier fixes **confusions**, and the Questioner asks a **genuine "I wonder…"
question**. The deck had to be corrected after prompting "read the lesson shape."

The four-role pedagogy is subtle and easy to paraphrase incorrectly, because the
shape file's rotation notation (`P→Q→C→S`) and its within-round speaking order
(`Predictor, then Clarifier, Questioner and Summariser`, shape Stage 2) are
**two different things** that look similar.

## Decision
Student-facing Shape-I decks **must derive the four roles and the round timeline
from the canonical classroom source** — the existing Reciprocal-Teaching worksheet
and role cards (`PROJECTS/ARCHIVE/READING LESSON FLUENCY/SCRIPTS/render_rt_worksheet.py`
+ `SCRIPTS/rt_worksheet.html`), plus the prediction audio transcript. Concretely:

- **Predictor** — *before reading*: look at the heading, guess what the section will
  say. Starter: *"The heading says… so I think…"*
- **Clarifier** — *after*: say what was confusing and fix it with the group. Starter:
  *"I didn't understand when it said…"*
- **Questioner** — *after*: ask a genuine "I wonder…" question, not a quick check.
  Starter: *"I wonder… why…"*
- **Summariser** — *after*: say the main idea in one sentence. Starter: *"The main
  point is…"*
- **Round order**: `Predict (only the Predictor speaks) → everyone reads silently →
  Clarify, Question, Summarise in turn → rotate roles for the next chunk.`

The within-round speaking order is **Predict → Clarify → Question → Summarise**
(P, C, Q, S) — the shape's Stage 2 order. The shape's `P→Q→C→S` in the rotation line
is the **rotation mapping** (P→Q, Q→C, C→S, S→P), not the speaking order. Never
conflate them.

## Consequences

**Good:**
- The deck's roles and round match exactly what students see on the worksheet and role
  cards, so the deck and handout agree (no "why is the slide different?" confusion).
- The genuine "I wonder…" vs. quick-check distinction makes the Questioner an inquiry
  role, not a comprehension test; the Clarifier covers all confusion, not just words.

**Bad / cost:**
- Must open the archive worksheet before writing a Shape-I deck — one extra read step
  (the source is under `PROJECTS/ARCHIVE/...`).
- The roles slide is now a 3-column table (role / do / starter) which is denser than a
  2-column version; keep definitions short.

**Risks / follow-ups:**
- Muted starter text must be **non-gray** `#f0f0f0`, not `#ddd`/`#ccc` — the font
  gate (`validate_slide_fonts.py`) fails on gray.
- The role rotation across chunks is still "rotate one position" (shape Stage 3/4);
  the deck reminds groups to rotate per chunk, but the exact P→Q→C→S position mapping
  is teacher-facing, not projected.
- If the worksheet role cards are ever edited, this deck must be re-checked against them.
