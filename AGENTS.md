# LESSON-PLAN-WRITER-4

Data-only repo: lesson shape templates + project slideshows. No build system, no Makefile, no lint/typecheck. **Skip** `uv run make validate` — it will fail.

## Remotes

All slides deploy to `old-origin` (`elwrush/lesson-plan-writer`, the canonical slides host). `origin` is `elwrush/lesson-plan-writer-4` (source repo). Never push to `origin`'s gh-pages.

## Layout

- `LESSON-SHAPES/shape-{a..g}.json` — 7 pedagogical models consumed by write-lesson-plan skill
- `PROJECTS/{name}/` — per-lesson material directory:
  - `data.json` — 25-40 slide records for slideshow-renderer
  - `envelope.json` — lesson plan metadata for write-lesson-plan
  - `slides/` — rendered reveal.js output (gitignored)
- `ASSETS/` — logo (`logo.png`, md5: `6b3a32e5`), copied into each project's `slides/assets/`
- `PDF/` — generated lesson plan PDFs (gitignored)
- `scripts/render-pdf.js` — Playwright bridge (used by write-lesson-plan)
- `tests/test_git_pages_safety.py` — safety regressions for git-pages command

## Commands (`.kilo/command/`)

| Command | Use |
|---------|-----|
| `/git-pages [name] [source-dir]` | Deploy/update slides on gh-pages. Always uses `old-origin`. Never switches branches. |

Other commands (`explore`, `propose`, `implement`, `verify`, `project-go`) are generic spec-kit and can be ignored — this repo uses no spec kit.

## Workflow: New slideshow

1. Create `PROJECTS/{name}/slides/assets/`, copy logo from `ASSETS/logo.png`
2. Download images (Wikimedia Commons for historical/public domain, Pixabay for generic) into `slides/assets/`
3. Generate spelling test audio and monolog audio via Inworld TTS-2 (build-a-monolog skill, system voices for speed)
4. Write `data.json` with 25-40 slides (load slideshow-renderer skill for full schema)
5. Run `python3 ~/.kilo/skills/slideshow-renderer/scripts/render.py --data "PROJECTS/{name}/data.json" --output "PROJECTS/{name}/slides/index.html"`
6. Post-process: add `timer-plugin.css`/`.js` links, `TimerPlugin` to plugins array, `data-timer="N"` to task slides (360/300/240s)
7. Validate: `python3 ~/.kilo/skills/slideshow-renderer/scripts/validate_slide_fonts.py "PROJECTS/{name}/data.json"` — catches gray fonts and undersized text
8. Deploy: `/git-pages {name} "PROJECTS/{name}/slides"`

## Workflow: Lesson plan PDF

1. Write `PROJECTS/{name}/envelope.json` with `shape` (must reference existing shape in LESSON-SHAPES/), `metadata` (teacher/date/class/aims/stages/answer key), and `slideshow_url`
2. Run `python3 ~/.kilo/skills/write-lesson-plan/scripts/render.py --template lesson-plan --data "PROJECTS/{name}/envelope.json" -o "PDF/lesson-plan-{date}-{topic}.pdf"`
3. Verify with `pdfinfo` (A4: 595x842 pts), `pdffonts` (fonts embedded)

## Hard-earned slide rules

- **No gray text** on dark backgrounds: only `#fff` or `#ffdd00`. Never `#888`, `#ccc`, `#aaa`, `#ddd`.
- **Min fonts**: headings 44px, body 34px, tables 36px, absolute minimum 28px.
- **Lists must be HTML `<table>`** — markdown fragments produce broken "1." numbering.
- **Timer pill via `data-timer`** on task slides (360s/300s/240s). Added during post-processing, not in data.json body.
- **Model text is a continuous paragraph** — no "Opinion: / Reason:" structural labels in student-facing content.
- **Matching exercises**: `auto-animate-pair` with stable `data-id="o1"`–`oN` on options, `s1`–`sN` on stems.
- **Transcript must match audio verbatim** — every sentence in the TTS prompt must appear on the slide.
- **Audio preview**: use `npx http-server -p 8080 --cors -g` (Python's http.server lacks `Accept-Ranges: bytes`, breaking audio scrubber).

## Testing

- `python3 -m pytest tests/test_git_pages_safety.py -v` — checks git-pages command for forbidden patterns
- `python3 -m pytest ~/.kilo/skills/slideshow-renderer/scripts/tests/ -v` — slideshow skill tests
- `python3 -m pytest ~/.kilo/skills/write-lesson-plan/tests/ -v` — lesson plan skill tests

## Gitignore

`**/slides/`, `PDF/`, `ASSETS/`, `node_modules/`, `.venv/`, `audit-*.md`, `.env` — all output artifacts.

## Shape cross-references

- B depends on A/C
- E → H (receptive skills → new shape H)
- F → J (productive skills → new shape J)

## Before declaring done

Verify source content against slides. Common hallucinations: truncated exercise stems/options, missing "the history of" / "like" / "a lot" type modifiers, wrong CEFR levels on spelling words, US vs UK spelling drift.
