## Tasks

### Phase 1 — Foundation
- [x] T001 **Precondition audit** — confirm library exists at `~/.kilo/skills/slideshow-renderer/lib/slideshow_lib/`, 100 tests pass, `setup_jinja(env)` is importable. Confirm `ruff` LSP is configured globally. Discard old `.spec/slideshow-pipeline/` (superseded by this spec). Report findings before proceeding.

### Phase 2 — Skill
- [x] T002 **Create SKILL.md** — at `~/.kilo/skills/slideshow-renderer/SKILL.md` with YAML frontmatter (`name: slideshow-renderer`, `description:` matching pipeline purpose). Instructions must cover: (a) how to find and read the library quickref, (b) how to load ESL voice prompts before writing content, (c) how to structure a template + data.json pair, (d) how to invoke `render.py`, (e) how to invoke `/git-pages` for deploy. Include a minimal working example.
- [x] T003 **Create prompts/ directory** — two files within the skill directory:
  - `prompts/esl-voice.md`: authorial voice rules — conversational "you"/"we" tone, max 4-5 words/line, 8-12 words/sentence (B1), 32pt+ body, no passive voice, short imperatives, Mayer's Personalization Principle. For each rule, cite the research source.
  - `prompts/best-practices.md`: slide design rules — color-coded staging (orange/blue/green/purple/teal), one concept per slide, heavy image use, auto-animate for grammar comparisons, speaker notes for teacher instructions only, lexical control within Cambridge B1 vocabulary profile, WCAG AA contrast minimum.
- [x] T004 **Create references/slideshow_lib-quickref.md** — documents all 23 functions grouped by reveal.js doc page. Each entry: function signature, example call, example output, enum-validated args. Include import path (`sys.path.insert(0, ...)` + `from slideshow_lib import setup_jinja`). Include the fixed CDN HTML skeleton that every slideshow wraps around.

### Phase 3 — Render script
- [x] T005 **Write scripts/render.py** — CLI script that:
  1. Accepts `template.jinja2` + `data.json` as positional args (or `--template`, `--data`). Optional `--output` (default: `slides/index.html`).
  2. Loads data.json, validates via Pydantic model (slide content structure — title, body, stage color, notes, image_url, etc.).
  3. Creates a Jinja2 `Environment` with `slideshow_lib.setup_jinja(env)`.
  4. Renders template with data, writes `index.html`.
  5. Wraps the rendered output in the fixed CDN skeleton if the template doesn't include `<html>`/`<head>` tags.
  6. Prints output path on success.
  - Tests: red-green pair — minimal template renders, data validation rejects bad input, output file is valid HTML with CDN links.

### Phase 4 — Deploy
- [x] T006 **Port git-pages command to LPW-4** — read `.kilo/command/git-pages.md` from LPW-3. Adapt for LPW-4 layout:
  - Source path: `slides/index.html` (instead of `output/{name}/slides/index.html`)
  - Action: copy `slides/` directory to staging, shallow-clone gh-pages branch, copy into subfolder, regenerate landing page card grid
  - Must match all safety tests: no `git checkout`, no `git rm -rf`, uses `git -C $worktreeDir`, uses `git clone --depth 1`
  - Write safety test at `tests/test_git_pages_safety.py` matching LPW-3's pattern
  - Red: test file created but expected patterns absent. Green: command file written, all safety tests pass.

### Phase 5 — Validation project
- [x] T007 **Create PROJECTS/TEST/.spec/proposal.md + tasks.md** — validation project: Present Perfect for Thai middle schoolers. Proposal defines the lesson content scope (A2–B1, 10 slides, grammar focus on present perfect simple). Tasks cover: research reference materials, write content JSON, write template.jinja2, render, deploy.
- [x] T008 **Build and deploy TEST slideshow end-to-end** — following the skill's own instructions:
  1. Load skill, read ESL voice + best practices prompts
  2. Write `PROJECTS/TEST/data.json` (10 slides covering Present Perfect in ESL context)
  3. Write `PROJECTS/TEST/template.jinja2` (uses slideshow_lib functions for backgrounds, fragments, auto-animate, speaker notes, color-coded stages)
  4. Run `render.py template.jinja2 data.json --output slides/index.html`
  5. Verify output HTML is valid (open in browser, check CDN loads, check slide count)
  6. Run `/git-pages TEST` to deploy
  7. Verify live URL loads

### Phase 6 — Final verification
- [ ] T009 **Final verify** — check all done criteria from proposal are met. Run `/verify` on the spec. No drift between spec and implementation. All tasks marked complete. Prompt sources cited. Library unmodified (read-only consumed).
