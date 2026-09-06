---
title: Proceed with YouTube auto-captions; defer timed-caption injection
status: accepted
date: 2026-09-06
deciders: Ed Rush
---

# Proceed with YouTube auto-captions; defer timed-caption injection

## Context
ADR 0002 chose YouTube auto-captioning for the 4 podcast tapes. In practice the
4 chunks were uploaded and verified via `captions.list`: chunks 1–3 have an
auto (`asr`, `en`) English caption track, but **chunk 4 never gained one** — even
after a fresh re-upload to a new video ID. Chunk 4 is 360 s (6 min) vs ~190 s for
chunk 3; per YouTube Help, auto-CC consistently skips videos it deems too long or
with "complex" audio, even when the source recording is clean (verified: healthy
loudness, no dead silence).

We do hold the real, correctly-punctuated transcript (`dialog-draft.md`) plus the
Fish-ASR word timings that power the existing `.vtt` files. The obvious "fix" —
upload our own well-punctuated timed captions to the videos — is **not trivial**:
research confirms YouTube **deprecated the `sync` parameter** on `captions.insert`
and `captions.update` on **2024-03-13**, so a plain formatted transcript can no
longer be auto-aligned through the API. Aligning our authored transcript to the
audio requires either re-deriving word timings and mapping punctuation onto ASR
cues, or a manual Creator Studio paste. That is real work with fragile edge cases.

## Decision
For the current lesson, **proceed with YouTube auto-captioning** as-is: keep the
YouTube embeds, keep relying on YouTube's ASR track, and accept that chunk 4 may
ship without a CC track (the class hears it twice; the local `tape4.vtt` + native
`<video>` fallback remains available for that slide if a caption is required).
We deliberately **do not build the timed-caption injection pipeline now**.

The door stays open: if chunk 4's missing CC becomes a blocker, the next step is
to inject **timed** captions (a built-from-`dialog-draft.md` + Fish word-timing
WebVTT, uploaded as a manual track via `captions.insert`), not to re-fight YouTube
ASR. The building blocks (proper transcript, word timings, `youtube.force-ssl`
scope for `captions.*`) are already in place and require no architectural change.

## Consequences
**Good:**
- Lowest effort; zero extra pipeline code; ships the deck now.
- Chunks 1–3 have clean working auto-CC; the CC UX is consistent for those.
- The research finding is captured — future readers won't re-derive the `sync`
  deprecation.

**Bad / cost:**
- Chunk 4 has no CC button on the YouTube embed (inconsistent with 1–3).
- Chunk 4's captions depend on the local `.vtt` fallback, which ADR 0002 was meant
  to retire — so that path is kept alive for one slide.
- Viewer cannot toggle CC on chunk 4 while it plays.

**Risks / follow-ups:**
- **Follow-up (documented, not blocked):** if chunk-4 CC is required, add a
  `--upload-captions` mode that builds a punctuated, timed WebVTT from
  `dialog-draft.md` + Fish ASR timing and uploads it with `captions.insert`
  (needs the `youtube.force-ssl` scope, already added to the skill's `SCOPE`).
- The skill's `--check-cc` should use the `youtube.force-ssl` scope; the earlier
  shortfall (plain `youtube` scope → "insufficient permissions") was the reason
  we could not read captions and is now fixed.
```
