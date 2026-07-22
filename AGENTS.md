# LESSON-PLAN-WRITER-4

Data-only repo: lesson shape templates + per-project slide decks, cue cards, and worksheets.  
No Makefile, no build system. Venv has pytest only.

## Remotes

| Remote | URL | Purpose |
|--------|-----|---------|
| `old-origin` | `elwrush/lesson-plan-writer` | gh-pages host. All `/git-pages` go here. |
| `origin` | `elwrush/lesson-plan-writer-4` | Source repo. Never push gh-pages here. |

`/git-pages` deploys to `old-origin`; falls back to `origin`.

## Project layout

```
PROJECTS/{name}/              # Per-lesson directory (15-40 files)
  data.json                   # Slide deck. Load slideshow-renderer skill first.
  lesson.json                 # Source textbook lesson metadata + exercises
  transcript.json             # Audio transcript for listening tasks
  generate_cue_cards.py       # Speed-dating cue cards (self-contained Playwright)
  post-process.py             # Timer + plugin injection (re-run after every render)
  classroom-layout.svg        # Classroom layout diagram for rotation models
  slides/assets/              # splash.jpg, logo.png, blip/BELL.mp3
```

Top-level: `LESSON-SHAPES/shape-{a..g}.json`, `RESEARCH/*.md` (pedagogical references), `tests/test_git_pages_safety.py`.

## Classes

`M3-A`, `M2-4A`, `M2-5A` — three classes. Never invent others.

## HTTP server

- Python `http.server` or `npx http-server -p 8080 --cors -g` on port 8080.
- Re-rendering overwrites `index.html` in-place; **do NOT stop the server**.
- Don't ask about it.

## Slideshow workflow

### Before writing data.json

1. Ask user for splash image. Download/crop to 1920×1080, save to `slides/assets/splash.jpg`.
2. Copy `ASSETS/logo.png` (verify md5: `6b3a32e5`) to `slides/assets/logo.png`.
3. Copy `ASSETS/blip.mp3` + `BELL.mp3` to `slides/assets/`.
4. **Batch all styling decisions**: timer durations, auto-start, yellow highlights, worksheet structure (question count, rule slide count matching Task 2 items). Single question, not iterative.
5. **Read source materials for meaning** (skill Step 1.5). State the narrative in one sentence before writing any JSON. Every slide must trace back to it.
6. **Write a slide blueprint** (see skill Step 3.6): ordered list of slide IDs with one-line descriptions and which existing Design Pattern each slide uses. Tick off each slide as it's written.
7. **Follow the pedagogical arc** (see skill Activity selection table). Stage order is fixed: Recall → Vocab → Strategy → Listening → Controlled → Freer. Don't reorder.

### Writing data.json

- Load the `slideshow-renderer` skill first (defines layout enum, resolver, macros).
- **Max 25 body words per content slide** (Mayer's Coherence Principle).
- **Sentences**: 8–12 words for B1, one idea per sentence, no compounds, no embedded clauses.
- **Voice**: conversational "you"/"we", short imperatives, active voice.
- **Page/task numbers**: every task slide references the textbook page and task number (e.g. "Page 155, Task 1").

**Splash**: `layout: "image"` with `image_url` only — no `title`, no `body`.

**Title**: `logo: "assets/logo.png"` + `shield: true` + `background_image` — all three required.

**Importance**: immediately after title, `background_color: "#1a1a2e"`, `<ul>` of real-world outcomes.

**Vocabulary** — 3-click reveal per word:
- Slide entry: phonemic script only, no syllable dots (e.g. `/ˌdɒkjʊˈmentəri/`)
- Click 1: English word in `<span class="box-word">`
- Click 2: context sentence eliciting meaning (no dictionary definitions)
- No `title` field on vocab slides. Precede section with red transition `"Let's check your word knowledge"`.
- Background: `#1a1a2e`.

**Strategy exposition** — MUST use a `Do` / `Why` / `How` HTML table, not box-word spans:
```json
{"layout": "content", "id": "strategy-predict", "step": 1,
 "background_color": "#1a1a2e", "title": "Strategy: Predict",
 "body": "<table style=\"width:100%;border-collapse:collapse\"><tr><td style=\"padding:8px 12px 8px 0;border-bottom:1px solid #555;font-weight:700;color:#ffdd00;white-space:nowrap;vertical-align:top\">Do</td><td style=\"padding:8px 0;border-bottom:1px solid #555\">Predict answers before you listen.</td></tr><tr><td style=\"padding:8px 12px 8px 0;border-bottom:1px solid #555;font-weight:700;color:#ffdd00;white-space:nowrap;vertical-align:top\">Why</td><td style=\"padding:8px 0;border-bottom:1px solid #555\">It helps your brain focus.</td></tr><tr><td style=\"padding:8px 12px 8px 0;font-weight:700;color:#ffdd00;white-space:nowrap;vertical-align:top\">How</td><td style=\"padding:8px 0\">Read the question. Think first.</td></tr></table>"}
```

**Strategy demo** — each strategy MUST be followed by an `auto-animate-pair` table with a concrete example (not from the actual transcript):

| Demo type | Step 1 | Step 2 | What animates |
|-----------|--------|--------|---------------|
| Predict | options with `&nbsp;` in span | green `✓` on plausible options | span content |
| Underline | `<strong style="text-decoration:none">` | `<strong style="text-decoration:underline;...">` on key words | text-decoration |

**Auto-animate rules when editing data.json directly**:
- DOM structure must be IDENTICAL between steps. Every `<tr>`, `<td>`, `<span>`, `<strong>` in step 2 must also exist in step 1.
- All `<td>` cells in the table must have identical `border-bottom:1px solid #444` (no partial borders — they create visible artifacts at cell junctions, even with `border-collapse:collapse`). Including the last row is harmless.
- Empty inline-block spans collapse to zero height — always put `&nbsp;` inside them.
- **Edit JSON with `json.load()` → modify → `json.dump()`**, never raw string matching. Body strings contain JSON-escaped HTML with `\"` sequences that break string replacement.

**Answer slides**: one question per slide, four-row table (Question / Answer / Explanation / Transcript), green `#052e0d`. No fragments, no word limit. See skill Design Patterns.

**Speed dating sequence**: red transition "Speed Dating!" → video → sample cue card slide → instructions → timed GO slide. The sample card shows the cue card format before students handle them.

**Timers**: write a `post-process.py` per deck. The resolver adds `slide-{id}-1` prefixes to data-ids. Timer auto-start via `data-timer-autostart="true"`. Re-run post-processing after every render.

## Hard-earned gotchas

**Browser cache.** Timer-plugin.css changes won't appear without a cache buster. Add `?v=N` to the CSS link in post-process.py and bump N after every CSS edit. Hard refresh (Ctrl+Shift+R).

**Timer pill.** Don't customize — copy verbatim from `PROJECTS/ARCHIVE/JULY 20 M3 VOCAB MOVIES/slides/timer-plugin.*`. Only legitimate additions: `clearInterval` guard in `onStart()` and auto-start support in `loadSlideTimer()`.

**Slide layout.** Use `raw` layout with CSS `<style>` blocks and centered tables (`margin:auto`, `max-width`). Don't use `content` layout for anything with HTML. Copy the CSS pattern from the working archive project, not from memory.

**Reveal.js config.** Never inject `margin`, `center`, or `disableLayout` overrides via post-processing. The default config (`width:1280, height:720`) works. Every override tried made the slides worse.

**Gist answers.** "How does it engage?" questions need concept answers (the *idea* that makes it compelling), not technique (close-ups, no names). Split across multiple slides when 25-word limit forces fragmented bullets.

**Vocab context sentences.** Must include a clarifying second clause. "It was a fascinating conversation" is useless. "It was a fascinating conversation. I was so interested by everything she said" allows inference.

**Strategy demos.** Use `<span>` not `<strong>` for invisible text-decoration placeholders in step 1 — `<strong>` has default bold that gives the answer away.

**Answer lists.** Use `<p>` tags with hardcoded numbers — NOT Markdown `1.` / `2.` which renders as `<ol>` with gray list markers.

**Font minimums.** No text below 31px. Body 35px, headings 47px, phonemic script 47px.

**Pattern reference.** Before writing any slide, study `PROJECTS/ARCHIVE/JULY 20 M3 VOCAB MOVIES/` for the proven table CSS pattern and reveal.js config.

### Render

```bash
python ~/.kilo/skills/slideshow-renderer/scripts/render.py \
  --data "PROJECTS/{name}/data.json" \
  --output "PROJECTS/{name}/slides/index.html"
python3 "PROJECTS/{name}/post-process.py"
```

Never stop the HTTP server. Python's `http.server` picks up changed files on each request.

### Validate

```bash
python3 ~/.kilo/skills/slideshow-renderer/scripts/validate_slide_fonts.py "PROJECTS/{name}/data.json"
# Manual: check slide order (1,2,3,4 not 1,3,2,4)
# Manual: source fidelity against worksheets (no truncated stems, no spelling drift)
python3 -m pytest tests/ -v
```

## Worksheet PDF workflow

1. Ask user which class. Look up roster via Supabase (`classlists` table; requires `.env` with `SUPABASE_URL` + `SUPABASE_ESL_KEY`).
2. Write `PROJECTS/{name}/generate_worksheet.py`. Model on an existing one.
3. Run: `python3 "PROJECTS/{name}/generate_worksheet.py" --class {CLASS} --output-dir "PROJECTS/{name}"`
4. Verify: `pdfinfo` confirms A4, page count = students × (content pages + padding).
5. Padding rule: `PADDING_MAP = {1:0, 2:0, 3:1, 4:0, 5:3}`.

PDFs are gitignored (`PROJECTS/**/*.pdf`).

## Cue cards

Write a `generate_cue_cards.py` per project. Self-contained Playwright script:
- Generates HTML with embedded CSS, renders via Playwright to A4 PDF.
- One card per discussion topic, 4 per A4 page.
- Each card includes: numbered header, context/question, 4-step discussion structure (Open → Your view → Respond → Resolution), dot-pointed language hints (Agree / Disagree / Follow-up).
- Fonts: Roboto (installed via TinyTeX), embedded in PDF.

## Lesson plan PDF workflow

Generate lesson plan PDFs via `write-lesson-plan` skill. Always follow these rules:

1. **Load lesson.json** — extract book name, unit number/title, page numbers for the materials list.
2. **Read lesson.json exercises** — the answer key numbering must follow the textbook exercise numbers (e.g. Exercise 3 → 3a, 3b; Exercise 4 → 1–6).
3. **Load transcript.json** — set `metadata.transcript` to the path. The renderer auto-converts JSON to `<strong>Speaker:</strong> text` format with boldfaced speaker names.
4. **Main aim = speaking/product, not vocabulary.** The main aim must reflect the lesson's real productive focus (discuss, present, debate). Vocabulary is supporting content for a stage, not the main objective.
5. **Lead-in uses splash → title sequence.** Procedure step 1: show splash, let students speculate ("What do you see? Who are these people?"). Step 2: advance to title, confirm the theme.
6. **Materials list:** first item = full textbook details ("Oxford Discover Futures 3, Unit 6 ..., pp. 64–65"). Then slideshow, cue cards, audio, worksheet.
7. **Answer keys:** sectioned by exercise (`<strong>Exercise 3 — Gist questions</strong>`), numbered by textbook, full sentences.
8. **Transcript included** for any lesson with a listening text.
9. **No images in the lesson plan** — contextual images go in the slideshow.

```bash
python ~/.kilo/skills/write-lesson-plan/scripts/render.py \
  --template lesson-plan \
  --data PROJECTS/{name}/envelope.json
```

Verify: `pdfinfo` confirms A4 (594.96 × 841.92 pts), `pdffonts` confirms embedded fonts.

## Before declaring done

1. Re-run post-processing (render wipes timer injections).
2. Verify slide order matches JSON array.
3. Check source fidelity against worksheets/transcripts.
4. Run `python3 -m pytest tests/ -v`.
5. Deploy is GATED — do NOT push gh-pages without explicit user OK.
