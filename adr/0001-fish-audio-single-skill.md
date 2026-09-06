---
title: Consolidate Fish Audio TTS into a single skill
status: accepted
date: 2026-09-06
deciders: Ed Rush
---

# Consolidate Fish Audio TTS into a single skill

## Context
The repo had two Fish Audio skills: `build-a-dialog` (multi-voice) and
`build-a-monolog` (single voice). Both ships the same `design_voices.py`
(byte-identical), the same `/v1/tts` call, the same ffmpeg concat concept, and
the same markdown/pronunciation guards. A monolog is logically just a dialog
with one speaker, and Fish's API even supports true multi-speaker natively
(`reference_id` array + `<|speaker:N|>` tags). The split duplicated the safety
pipeline and let the guards drift out of sync.

## Decision
Replace both with one skill, `fish-audio`, exposing `monolog` and `dialog`
modes. The TTS engine lives in a single module, `scripts/tts.py`, which bakes
in the mandatory guard pipeline (strip markdown → apply pronunciations →
assert_no_markdown) so every call — regardless of mode — is safe by construction.
Shared primitives (`md_safety.py`, `pronounce.py`, `design_voices.py`,
`list_voices.py`, `postprocess.py`) exist exactly once. Dialog-specific
(`parse_dialog.py`, `generate_lines.py`, `stitch_dialog.py`) and monolog
(`generate_monolog.py`) are thin wrappers around the shared engine.

## Consequences
**Good:**
- The safety pipeline is enforced in one place; no mode can bypass it.
- Removed the duplicated `design_voices.py` (was byte-identical) and overlapping
  ffmpeg logic.
- 68 tests green across the unified skill (35 markdown, 19 pronunciation, 14
  pipeline smoke).

**Bad / cost:**
- Broke the old `build-a-dialog` / `build-a-monolog` names; workspace references
  (AGENTS.md, repo `generate_audio.py` import path) had to be updated.
- `audit-skills-compliance.md` reports still mention the old names (historical,
  non-functional).

**Risks / follow-ups:**
- New import path: `/home/elwru/.agents/skills/fish-audio/scripts`. The repo's
  `generate_audio.py` must keep pointing there.
- Any skill referencing the old names must be updated.
- Backup of both old skills kept under `/tmp/opencode/fish-skill-backup/` until
  confirmed unused.
