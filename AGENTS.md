# LESSON-PLAN-WRITER-4

Data-only repository: pedagogical lesson shape templates consumed by the lesson plan writer pipeline. No build system, no app code.

## No Makefile — ignore the global `uv run make validate` rule

This repo has no `Makefile`. The global validate command will fail. Skip it here. There is nothing to build or lint at the repo root.

## Layout

- `LESSON-SHAPES/shape-{a..g}.json` — 7 pedagogical models with fixed schema (`name`, `description`, `pedagogical_justification`, `main_aim_format`, `example_lesson_plan.header`, `example_lesson_plan.stages[]`)
- `PROJECTS/{name}/` — per-lesson material directory with `EX-BOOK.json`, audio files, `data.json` (slides), `envelope.json` (lesson plan), and `slides/` (rendered output)
- `ASSETS/` — master logo (`logo.png`, md5: `6b3a32e5`), Cambridge/ACT logos, blip/BELL sounds
- `PDF/` — generated lesson plan PDFs
- `scripts/render-pdf.js` — Playwright bridge for lesson plan PDF rendering

## Shape cross-references

Preserve when adding or modifying shapes:
- B depends on A/C
- E → H (receptive skills → new shape H)
- F → J (productive skills → new shape J)

## Workflows

### Slideshow generation (slideshow-renderer skill)

1. Create `PROJECTS/{name}/slides/assets/` 
2. Copy logo from `ASSETS/logo.png`
3. Write `data.json` with 25-40 slide records (see slideshow-renderer SKILL.md for schema)
4. Run `python3 ~/.kilo/skills/slideshow-renderer/scripts/render.py --data "PROJECTS/{name}/data.json" --output "PROJECTS/{name}/slides/index.html"`
5. Post-process for timer plugin (inject `timer-plugin.js`/`.css`, add `data-timer` attributes, register `TimerPlugin`)
6. Deploy: `/git-pages {name} "PROJECTS/{name}/slides"`

### Lesson plan PDF (write-lesson-plan skill)

1. Write `PROJECTS/{name}/envelope.json` with `shape` (pedagogical model) + `metadata` (teacher/date/class/aims/stages/answer key)
2. Run `python3 ~/.kilo/skills/write-lesson-plan/scripts/render.py --template lesson-plan --data "PROJECTS/{name}/envelope.json" -o "PDF/lesson-plan-{date}-{topic}.pdf"`
3. Verify: `pdfinfo` (should be A4: 595×842 pts), `pdffonts` (fonts embedded)

### Git backup

`/git-backup` — stages all changes, commits to `backup/YYYY-MM-DD-HHMM` branch, pushes. Does NOT touch main.

### Git Pages deploy

`/git-pages [name] [source-dir]` — shallow-clones gh-pages to an isolated temp directory, copies slides, regenerates landing page, commits, pushes, verifies MD5. NEVER switches branches in the main working tree.

## Commands

All in `.kilo/command/`:

| Command | Function |
|---------|----------|
| `/explore` | Brainstorm, read code, no files created |
| `/propose {name}` | Create `.spec/{name}/proposal.md` + `tasks.md` |
| `/implement {name}` | Execute tasks from spec with red-green TDD |
| `/verify {name}` | Read-only spec completeness check |
| `/git-backup` | Backup to timestamped branch |
| `/git-pages` | Deploy slides to gh-pages |

## Slide design rules (hard-earned)

- **No gray text** on dark backgrounds — never `#888`, `#ccc`, `#aaa`, `#ddd`. Only `#fff` (white) or `#ffdd00` (yellow).
- **Minimum font: 28px**. Body text: 32-36px. Tables: 36px. Headings: 44-48px.
- **Lists must be HTML `<table>`** — markdown fragments produce broken "1." numbering.
- **Timer pill required on every task slide** — not just "You have X min" text. Include `data-timer` in post-processing.
- **Transcript must match audio verbatim** — every sentence in the TTS prompt must appear on the slide.
- **Model text is a continuous paragraph** — no "Opinion: / Reason:" structural labels in student-facing content.
- **Matching exercises**: use `auto-animate-pair` with stable `data-id="o1"` through `oN` on options, `s1` through `sN` on stems. No bold on option letters.
- **Run font validator**: `python3 /home/elwru/.kilo/skills/slideshow-renderer/scripts/validate_slide_fonts.py "PROJECTS/{name}/data.json"` — catches gray colors and undersized text.
- **Audio generation**: Inworld TTS API with steering tags (2-3 tags max, no ellipses, no non-verbals, single paragraph). Prebuilt system voices for quick results.

## Testing

- Only test suite: `tests/test_git_pages_safety.py` — scans `.kilo/command/git-pages.md` for forbidden patterns. Run with `python3 -m pytest tests/test_git_pages_safety.py -v`.
- Slideshow skill tests: `python3 -m pytest ~/.kilo/skills/slideshow-renderer/scripts/tests/ -v`
- Lesson plan skill tests: `python3 -m pytest ~/.kilo/skills/write-lesson-plan/tests/ -v`

## Gitignore notes

`**/slides/`, `PDF/`, `ASSETS/`, `node_modules/`, `.venv/`, `audit-*.md`, `.env` are all gitignored. Slides and PDFs are output artifacts, not source code.
