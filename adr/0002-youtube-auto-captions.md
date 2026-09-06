---
title: Host podcast tapes on YouTube for auto-captions
status: accepted
date: 2026-09-06
deciders: Ed Rush
---

# Host podcast tapes on YouTube for auto-captions

## Context
The lesson's 4 podcast tapes need timed subtitles, toggled on for a second
listening pass. The deck first used the native `<audio>` element, which has NO
caption support. It was replaced with a `<video>` element + pre-generated
WebVTT `.vtt` files (built by transcribing the deployed audio via Fish ASR) plus
a custom caption overlay that fetches/parses the `.vtt` and renders large
high-contrast text below the player.

This works in a fresh Chromium context (verified via Playwright DOM checks), but
the captions did not reliably render for the classroom setup here — the
native `.vtt`/`<track>` path is finicky across environments, and Chrome caches
stale plugin JS unless the reference is versioned. The user requires a solution
that "definitely works" and will be shown in Chrome.

## Decision
Host the 4 tapes on YouTube as unlisted videos in the `elwrush_class_tapes`
playlist, then embed the YouTube `<iframe>` player in the slide deck. Rely on
**YouTube's own auto-captioning** for the CC track (English), toggled by the
built-in YouTube CC button. The tapes are uploaded with a 16:9 cover image
(the opium-era splash) + the tracked audio via ffmpeg → mp4. Upload uses the
YouTube Data API v3 (`videos.insert`, resumable), `categoryId: 27` (Education),
privacy `unlisted`, driven by OAuth 2.0 (installed-app flow; long-lived
refresh token cached in `youtube/token.json`).

## Consequences
**Good:**
- YouTube auto-CC "just works" — no local VTT pipeline, no browser-version
  fragility. Captions appear after processing regardless of local browser.
- Decoupled captions from the local file; the deck just embeds a player URL.
- Unlisted + non-indexed keeps the tapes out of search.

**Bad / cost:**
- Requires internet + the OAuth `client_secret.json`; a one-time browser
  approval is needed on first upload (saved thereafter).
- Upload quota (YouTube API) and processing delay (captions take minutes to
  hours after upload).
- The deck needs the video IDs (from `youtube/video_ids.json`) to build the
  iframe embeds; a local network offline would fail to load the player.
- Removes the ability to edit captions offline.

**Risks / follow-ups:**
- OAuth scope is `https://www.googleapis.com/auth/youtube.upload`; no
  service-account path exists for uploads.
- `client_secret.json` is a secret — never commit it. The token must be
  gitignored.
- The mp4 builder + uploader lives at `PROJECTS/LISTENING M3/upload_to_youtube.py`.
- Supersedes the local `.vtt`/`<video>` approach; the VTT files and caption
  plugin may be removed once the YouTube embed is confirmed.
