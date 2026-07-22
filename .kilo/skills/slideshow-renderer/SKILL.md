---
name: slideshow-renderer
description: Generate reveal.js slideshows from structured data using Jinja2 macros and a layout-driven resolver pipeline.
license: MIT
compatibility:
  - python3
metadata:
  author: Ed Rush (C·E·L Mathayom / ACT)
---

# Skill: Slideshow Renderer

**Pipeline:** Structured data → Pydantic validation → Resolver (auto-ids) → Jinja2 macros → CDN reveal.js HTML  
**Agent writes:** Structured JSON only — layout enum + HTML content strings. All body content is raw HTML passed verbatim through Jinja2 to reveal.js.  
**Resolver handles:** Auto-animate `data-id` continuity, fragment index sequencing, element matching.  
**Macros handle:** HTML generation per layout type via `slideshow_lib`.

## ⚠️ NON-NEGOTIABLE RULES — Splash & Title Slides

### Splash slide (id: "splash") — image ONLY
The splash slide MUST use `image` layout with `image_url` only. NO `title`, NO `body`.

```json
{"layout": "image", "id": "splash", "step": 1, "image_url": "assets/splash.jpg"}
```

### Title slide (id: "title") — same image + logo + shield
The title slide uses the **same image** as `background_image`. Must include ALL three fields:

```json
{"layout": "content", "id": "title", "step": 1,
 "background_image": "assets/splash.jpg",
 "logo": "assets/logo.png",
 "shield": true,
 "title": "Rhetorical question?",
 "body": "Let's find out."}
```

### Image sourcing
**BEFORE generating** the slideshow, the agent MUST ask the user: *"What image should I use for the splash / title background?"* Create or download the image, save it to `PROJECTS/{project_folder}/slides/assets/`, then reference it in both splash (`image_url`) and title (`background_image`).

| Field | Value | Why |
|-------|-------|-----|
| `background_image` | path to full-bleed image | Background photo for the title slide |
| `logo` | path to logo PNG | Copy `logo.png` from `ASSETS/logo.png`. RGBA with alpha channel. md5: `6b3a32e5`. |
| `shield` | `true` | Wraps title/body in dark semi-transparent boxes for readability on image |

**NEVER** omit `logo` from the title slide. The school logo is required on every title slide. Place it at `PROJECTS/{project_folder}/slides/assets/logo.png`.

The `logo` field is ONLY for the title slide. Do not add it to other slides.

## ⚠️ NON-NEGOTIABLE RULE — Why-This-Is-Important Slide

A **"Why is this lesson important?"** slide MUST follow immediately after the title slide (id: `"importance"`). It frames the lesson value for students.

- Uses `layout: "content"` with `background_color: "#1a1a2e"` (dark navy)
- Title: `"Why is this lesson important?"`
- Body: a `<ul>` with 2–3 bullet points drawn from the deck's content explaining relevance
- No fragments — all bullets visible at once
- NEVER list lesson objectives or grammar terms. Frame in terms of real-world outcomes.

```json
{"layout": "content", "id": "importance", "step": 1,
 "background_color": "#1a1a2e",
 "title": "Why is this lesson important?",
 "body": "<ul><li>The most common mistakes students make when writing are with capitalisation and punctuation.</li><li>These simple lessons will massively improve your writing.</li></ul>"}
```

## ⚠️ NON-NEGOTIABLE RULES — Clickthroughs

- **Expositional and instructional slides** must NEVER have clickthroughs/fragments. All content visible at once.
- **Vocabulary presentation** is EXEMPT from the no-fragments rule. Use the 3-click reveal pattern (see Design Patterns).
- **Bar charts** CAN use auto-animate pairs for anticipation (empty bar → grows to value on click).
- **CEFR band reveals** CAN use fragments to reveal each segment one click at a time.
- **Never** include instructional text like "Click to reveal" — the teacher knows how to use the slides.

## ⚠️ NON-NEGOTIABLE RULES — Font Sizes

Minimum font sizes for classroom projection (1280x720):

| Element | Minimum | Notes |
|---------|---------|-------|
| Headings / class names | 47px | Use 51-55px for prominence |
| Body text | 35px | 37-39px preferred |
| Bar values and labels | 35px | Bar fill text, skill names |
| Axis numbers (0-100) | 35px | No smaller |
| B1/B2 markers | 35px | 4px dashed line, text-shadow for readability |
| Segment counts (CEFR) | 43px | The bold number inside each segment |
| Timer pill time | 43px | Yellow bold in pill shape |

No text below 31px anywhere in the deck. Adjust `font-size` in inline styles or `<style>` blocks accordingly.

## ⚠️ NON-NEGOTIABLE RULES — Class Data

- **Each class on its own slide.** Never combine M3-3A, M3-4A, M3-5A on one slide.
- Grade bars, CEFR bars, and skill bars each get 3 separate slides (one per class).
- CEFR header format: `"M3-3A (19 students)"` followed by question `"How many achieved B1 or B2?"` — then bar segments reveal on click.

## Core Design

**The LLM NEVER writes reveal.js HTML attributes, Jinja2 template code, or raw HTML.** The agent emits a flat JSON array of slide records, each with a `layout` field selecting which Jinja2 macro renders it. The resolver assigns all cross-slide attributes (data-ids, fragment indices, auto-animate grouping) deterministically.

If the existing layouts cannot express the required design, extend the model (add fields to `SlideRecord`/`ResolvedSlide`) and macros (add rendering logic in `macros.jinja2`). Do NOT fall back to writing raw HTML in `data.json`.

Auto-animate bar charts: use `layout: "auto-animate-pair"` with steps 1 (0% width) and 2 (actual width). Add `data-id="bar"` (or `data-id="bl"`/`"br"`/`"bw"` for skill bars) on the inner fill div so reveal.js matches and animates the width change. Include B1 (65%) and B2 (80%) dashed vertical markers with labels.

### What the agent writes

```json
{
  "title": "M3-A Midterm Review",
  "theme": "black",
  "transition": "slide",
  "slides": [
    {"layout": "image", "id": "splash", "step": 1, "image_url": "assets/splash.jpg"},
    {"layout": "content", "id": "title", "step": 1, "background_image": "assets/splash.jpg",
     "logo": "assets/logo.png", "shield": true,
     "title": "How did you go in your exams?",
     "body": "Let's find out.",
     "notes": "Ask students: Why do people study English?"}
  ]
}
```

### What the agent NEVER writes

- ❌ `data-*` attributes (data-id, data-auto-animate, data-fragment-index)
- ❌ Jinja2 template syntax (`{% macro %}`, `{{ }}`)
- ❌ HTML tags, CSS, or reveal.js config (except `<span class=\"box-word\">` in HTML content for boxing target words, and `<strong style="color:#ffdd00">` for yellow highlighting of corrected text in auto-animate answer step 2)
- ❌ Fragment indices or auto-animate pairing logic

### Authorial voice

- **Student-facing only** — slides show what students need to see. Teacher instructions, CCQs, and timing go in `notes`.
- **Short imperatives** — "Read each question." "Predict the answer." "Watch the video."
- **No worksheet text** — don't project answer options (A/B/C) or worksheet content. Those are on paper.
- **Conversational "you"/"we"** — not formal textbook English.
- **One concept per slide** — Max 25 body-text words. Max 40 slides total.
- **Page and task numbers always referenced** — every task slide includes the textbook page and task number. Format: "Page 155, Task 1" in the slide heading or body. Students need to know exactly where they are in the book.
- **Box action verbs only** — Use `<span class="box-word">Read</span>` for action words (Read, Predict, Underline, Listen, Watch). Informational scaffolds (Opinion/Reason/Example) get plain `**bold**`, not boxed.

## When to Use

Use this skill when generating reveal.js slideshows for classroom presentation from structured lesson content. The pipeline handles slide layout selection, cross-slide attribute continuity, and CDN-based HTML generation.

## Workflow

### Step 0 — Determine project folder
All output goes under `PROJECTS/{project_folder}/slides/`. The `project_folder` is the name of the directory in `PROJECTS/` containing the lesson materials (e.g. `"JULY 20 M3 VOCAB MOVIES"`). This folder must already exist.

```bash
PROJECT_FOLDER="JULY 20 M3 VOCAB MOVIES"  # ← set this per project
mkdir -p "PROJECTS/${PROJECT_FOLDER}/slides/assets"
```

### Step 1 — Read ESL voice and best-practice prompts
Read `prompts/esl-voice.md` and `prompts/best-practices.md` before writing any content.

### Step 1.5 — Read all source materials for meaning, not just vocabulary
Before writing a single slide, read every source file (lesson.json, transcript.json, worksheets) and understand the narrative. What is the story this lesson tells? What is the central idea? What makes the content compelling?

Common failure modes when this step is skipped:
- **"How does it engage?" → listing techniques instead of the idea.** Close-ups and no-names are HOW it was filmed. The engagement is THAT strangers across 60 countries give the same answers to life's questions — a surprising, moving idea. Derive the concept first, then mention technique as support.
- **Comprehension answers that fragment into nonsense.** "2,000 people. 60 countries." means nothing without a verb. When a task has 2+ comprehension questions, each gets its own answer slide so answers can be full sentences.
- **Paraphrasing the transcript into abstraction.** "Hopes, fears, dreams from around the world" is poetry. "They talk about their hopes, fears, and dreams" is what a student would actually say. Stay concrete.

After reading source materials, state the narrative in one sentence before writing any JSON. Every slide's content must trace back to that narrative.

### Step 2 — Ask for splash image
**BEFORE writing data.json**, ask the user what image to use for the splash/title background. Then find or create it and save to `PROJECTS/{project_folder}/slides/assets/`.

### Step 3 — Copy logo
Before writing data.json, copy the school logo from the master `ASSETS/` directory:
```bash
cp "ASSETS/logo.png" "PROJECTS/${PROJECT_FOLDER}/slides/assets/logo.png"
```
Verify md5: `6b3a32e5a31ddee217875af9f730739e`

### Step 3.5 — Gather all styling and timer requirements upfront
**Before writing data.json**, ask the user about every slide that will need special treatment:
- Which slides need timer pills and what duration?
- Do answer/correction slides need yellow highlighting on the fix?
- Which slides should use red background (transitions, task intros)?
- Any slides that need a different background color or layout?

Batch these into a single pass. Layering them one at a time after rendering causes unnecessary edit→render→post-process cycles.

### Step 3.6 — Write slide blueprint + checklist BEFORE data.json
Plan the full slide sequence before writing any JSON. The blueprint prevents missing slides, structural gaps, and reinvention. Use this format:

```
# Slide blueprint — write in raw HTML — {lesson title}

1. splash — image (splash.jpg only)
2. title — content (logo + shield + background_image)
3. importance — content (navy, <ul> of real-world outcomes)
4. recall-xxx — content (navy, timed pair discussion with data-timer)
5. transition-vocab — content (red, "Let's check your word knowledge")
6. vocab-xxx — content (navy, no title, 3-click reveal: phonemic → box-word → context)
7. vocab-yyy — content (navy, no title, 3-click reveal)
...
11. strategy-xxx — content (navy, Do/Why/How table)
12. demo-xxx — auto-animate-pair (navy, table, matching DOM between steps)
...
20. answer-xxx — content (green, <p> elements — NOT numbered lists)
...
```

**Checklist rules:**
- [ ] Splash: image layout, image_url only, no title/body
- [ ] Title: logo + shield + background_image (all three)
- [ ] Importance: immediately after title, dark navy, <ul>
- [ ] Vocab preceded by red transition: "Let's check your word knowledge"
- [ ] Vocab: raw layout, no title field, no syllable dots in phonemic script, context sentences have clarifying second clause
- [ ] Each strategy followed by a demo (auto-animate-pair table, not real transcript content)
- [ ] Answer slides: one question per slide, four-row table (Question / Answer / Explanation / Transcript)
- [ ] Timed slides: data-timer in post-process.py (use data-id="slide-{id}-1" from resolver)
- [ ] Headers left-aligned: content and auto-animate-pair slides prepend `<style>h2{text-align:left!important;margin-left:0!important;margin-right:0!important}</style>` to body
- [ ] Max 25 body words per content slide, 8-12 words per sentence, one idea per sentence
- [ ] Page and task numbers referenced on every task slide (e.g. "Page 155, Task 1")
- [ ] Color stages: navy (content), red (transitions/tasks), green (answers), purple (freer practice)

**Activity selection** — the slide sequence follows a pedagogical arc. Don't reorder these stages:

| Stage | Slides | Why |
|-------|--------|-----|
| Recall | recall-xxx | Activate prior knowledge before new input |
| Vocabulary | transition-vocab → vocab-xxx | Pre-teach challenging words before listening |
| Strategies | strategy-xxx → demo-xxx | Teach the skill, demonstrate it, then apply |
| Listening | gist-listen → answer-3a | Scaffold: gist first, answers, then detail |
| Controlled | pair-work → discussion-lang → practice-pairs | Controlled practice with scaffolds |
| Freer | speeddating-video → card → instru → go | Model, show materials, instruct, release |

Vocab slides precede listening. Strategies precede tasks. Within listening: gist → gist answers → detail → detail answers. Within strategies: exposition table → auto-animate demo. Within freer practice: video model → sample card → transition → instructions → timed activity.
- [ ] Max 25 body words per slide, 8-12 words per sentence, one idea per sentence
- [ ] Color stages: navy (content), red (transitions/tasks), green (answers), purple (freer practice)

**Derive from existing patterns** — every slide should map to a documented Design Pattern. Tick off pattern usage as you go. If a slide needs a pattern not yet documented, add it for next time.

Tick each item as the corresponding slide is written. The checklist IS the compile log.

**Also ask about the worksheet structure.** Count the items in each task:
- Task 1: How many questions? How many errors per question?
- Task 2: How many rule items? (The slide rule slides MUST match this count exactly — no extra, no missing)
- Task 3: What's the writing prompt?

The slide deck's rule slides must be numbered (Rule 1, Rule 2, etc.) matching the worksheet item numbers. Do NOT add rule slides that don't correspond to a worksheet item, and do NOT omit a slide for a worksheet item.

### Step 4 — Write data.json
Write `data.json` to `PROJECTS/{project_folder}/data.json` (alongside the `slides/` directory).
Write structured JSON with the `DeckData` schema. The title slide MUST include `logo: "assets/logo.png"`, `shield: true`, and `background_image`. Each slide record supports:

| Field | Type | Used by | Purpose |
|-------|------|---------|---------|
| `layout` | string | all | `content`, `two-column`, `auto-animate-pair`, `code`, `image`, `raw` |
| `id` | string | all | Unique slide identifier |
| `step` | int | all | Sequence position within a group (1-based) |
| `title` | string | content, code, image | Slide heading (HTML) |
| `body` | string | content, two-column, image | Body content (HTML) |
| `notes` | string | all | Speaker notes (teacher instructions only) |
| `background_color` | string | all | CSS hex color (e.g. `#1a1a2e`, `#c0392b`, `#052e0d`) |
| `background_image` | string | all | Relative path for slide background image |
| `fragments` | array | content | HTML strings, each renders as click-to-reveal `<div class="fragment">` |
| `shield` | bool | content | Wraps title/body in shield divs (image-background title slides) |
| `logo` | string | content | Relative path to logo PNG (RGBA with alpha, md5: 6b3a32e5) |
| `cta` | string | content | Call-to-action text rendered in a yellow-bordered box |
| `image_url` | string | image | Background image path |
| `code` | string | code | Source code |
| `language` | string | code | Language for syntax highlighting |

### Step 5 — Copy timer plugin files
If the deck has timed activities, copy timer-plugin files and audio cues to `slides/`. Full plugin code (timer-plugin.js, timer-plugin.css) and documentation are in `references/timer-plugin.md`.

```bash
cp references/timer-plugin.md  # ← contains the full JS + CSS
cp ASSETS/blip.mp3 PROJECTS/${PROJECT_FOLDER}/slides/assets/
cp ASSETS/BELL.mp3 PROJECTS/${PROJECT_FOLDER}/slides/assets/
```

### Step 6 — Write a post-processing script BEFORE rendering
Write `PROJECTS/{project_folder}/post-process.py`. The resolver adds `slide-{id}-1` prefixes to data-ids. Use a template from `templates/post-process.py`. **Render.py wipes timer injections on every re-run** — re-run post-processing after every render.

### Step 7 — Render + post-process
Run render, then immediately run post-processing:
```bash
PROJECT_FOLDER="JULY 20 M3 VOCAB MOVIES"
python ~/.kilo/skills/slideshow-renderer/scripts/render.py \
  --data "PROJECTS/${PROJECT_FOLDER}/data.json" \
  --output "PROJECTS/${PROJECT_FOLDER}/slides/index.html" \
&& python3 "PROJECTS/${PROJECT_FOLDER}/post-process.py"
```

**Do NOT restart the HTTP server** — it reads the file on each request and picks up changes automatically.

### Step 8 — Content integrity check (auto-lint)

After rendering and before deploying, run a **content integrity lint** against all input materials (worksheets, lesson plans, source data). This catches: missing slides, truncated content, answer key mismatches, and hallucinated material.

Additionally, run the deterministic font validator:
```bash
python3 ~/.kilo/skills/slideshow-renderer/scripts/validate_slide_fonts.py \
  "PROJECTS/${PROJECT_FOLDER}/data.json"
python3 -m pytest ~/.kilo/skills/slideshow-renderer/scripts/tests/ -v -q 2>&1 | tail -5
```

```python
REVIEW_PROMPT = """You are a slide quality reviewer. Compare the rendered slideshow
(source HTML) against the input materials listed below. Check:

1. **Completeness**: Is every exercise, question, and answer key from the input
   materials present on a slide?
2. **Fidelity**: Is content from the inputs faithfully reproduced? Check for
   truncated words, missing modifiers ("the history of", "like", "a lot"),
   changed CEFR levels, altered numbers or statistics.
3. **Answer key correctness**: Are all answer keys / correct answers from the
   input materials correctly transferred to the slides?
4. **No hallucinated content**: Does every slide fact have a basis in the input
   materials? Flag any invented statistics, examples, or exercise items.
5. **Slide order**: Does the slide sequence match the pedagogical flow described
   in the lesson plan or worksheet?

Input materials:
{input_materials}

Rate each dimension 1-5 and provide pass/fail (pass requires all >= 3).
If fail, list specific slide IDs with repair actions."""

payload = {
    "model": "deepseek-chat",
    "temperature": 0.1,
    "response_format": {"type": "json_object"},
    "messages": [
        {"role": "system", "content": "You are a slide quality reviewer. Always respond with valid JSON."},
        {"role": "user", "content": REVIEW_PROMPT.format(
            input_materials=", ".join(source_file_paths)
        )},
    ],
}
```

The judge output MUST be validated through a Pydantic model:

```python
from pydantic import BaseModel, Field

class SlideIntegrityCheck(BaseModel):
    completeness: int = Field(ge=1, le=5)
    fidelity: int = Field(ge=1, le=5)
    answer_key_correctness: int = Field(ge=1, le=5)
    no_hallucinations: int = Field(ge=1, le=5)
    slide_order: int = Field(ge=1, le=5)
    pass_fail: str
    repair_actions: list[str] = Field(default_factory=list)
```

If `pass_fail` is `"fail"`, apply each `repair_actions` item, re-render, and recheck.

### Step 9 — Deploy (GATED)
**Do NOT proceed without explicit user confirmation.** Deploying to gh-pages overwrites the live site. This step requires a verbal or written OK from the user.

Ask: *"Ready to deploy to GitHub Pages? This will make the slides live at the published URL."*

Only after the user confirms, run:
```bash
/git-pages {name}
```

If the user says no or defers, stop. Do not deploy. The slides are fully functional on the local HTTP server for preview.

## Layout Types

| Layout | Macro | Content fields | Notes |
|--------|-------|---------------|-------|
| `content` | `render_content_slide` | title, body, notes, background_color, background_image, fragments, shield, logo, cta | Standard slide with heading + body. Supports all extended fields. |
| `two-column` | `render_two_column_slide` | body (split on `\|\|\|`) | Left/right column layout |
| `auto-animate-pair` | `render_auto_animate_pair` | title, body (per step) | Grouped by `id`, steps 1..N. Use for bar chart anticipation. |
| `code` | `render_code_slide` | code, language, title | Syntax-highlighted code block |
| `image` | `render_image_slide` | image_url, title, body, fragments | Background image slide. Splash uses this with image_url only, no title/body. |
| `raw` | `render_raw_slide` | body (verbatim) | Passthrough for custom HTML (charts, timer pills, video embeds). |

## Design Patterns

### Splash slide — image only
```json
{"layout": "image", "id": "splash", "step": 1, "image_url": "assets/splash.jpg"}
```

### Title slide with logo + shields
```json
{"layout": "content", "id": "title", "step": 1,
 "background_image": "assets/splash.jpg", "logo": "assets/logo.png",
 "shield": true,
 "title": "How did you go?",
 "body": "Let's find out."}
```

### Why-this-is-important slide — lesson framing
This slide MUST be placed immediately after the title slide (id: `"importance"`). Title is always `"Why is this lesson important?"`. Body is a `<ul>` with 2–3 bullet points that frame the lesson value in student-facing, real-world terms. Never list grammar objectives.

```json
{"layout": "content", "id": "importance", "step": 1,
 "background_color": "#1a1a2e",
 "title": "Why is this lesson important?",
 "body": "<ul><li>The most common mistakes students make when writing are with capitalisation and punctuation.</li><li>These simple lessons will massively improve your writing.</li></ul>"}
```

### Auto-animate error→correction pair with yellow highlight
Use `auto-animate-pair` for before/after answer reveals. Step 1 shows the error (bold). Step 2 shows the correction with the changed character(s) wrapped in `<strong style="color:#ffdd00">`. The yellow color is essential — single-character text changes (i→I, m→M) are nearly invisible without it.

Match both steps' DOM structure by starting the body with the same character type (always raw HTML). The resolver assigns `data-id="el-{id}-body"` to the body div so reveal.js matches and animates the child elements by index.

```json
{"layout": "auto-animate-pair", "id": "answer-1", "step": 1,
 "background_color": "#052e0d",
 "title": "Sentence 1 — Spot the error",
 "body": "**i** think that learning **english** will help me get a better job."},
{"layout": "auto-animate-pair", "id": "answer-1", "step": 2,
 "background_color": "#052e0d",
 "title": "Sentence 1 — Corrected",
 "body": "<strong style=\"color:#ffdd00\">I</strong> think that learning <strong style=\"color:#ffdd00\">E</strong>nglish will help me get a better job."}
```

Only the specific character(s) that changed should be highlighted — not the whole word. This draws the eye to exactly what was fixed:

| Sentence | Error | Yellow highlight in step 2 |
|----------|-------|---------------------------|
| ...a new **Manager**... | Capitalised common noun | **m**anager |
| Chiang Mai **␣**, Thailand | Space before comma | **,** |
| ...difficult **M**ost... | Capital after dependent clause | **, m**ost |
| ...grandfather **␣** who... **Teacher** | Missing appositive commas + capitalised noun | **,** ... old**,** ... **t**eacher |

### Auto-animate bar chart with B1/B2 markers
```json
{"layout": "auto-animate-pair", "id": "grade-3a", "step": 1,
 "background_color": "#1a1a2e",
 "title": "M3-3A",
 "body": "<div style=\"padding:10px 30px\"><div style=\"display:flex;justify-content:space-between;color:#666;font-size:32px;border-bottom:3px solid #555;padding:0 0 5px 0;margin-bottom:8px\"><span>0</span><span>25</span><span>50</span><span>75</span><span>100</span></div><div style=\"position:relative;height:50px;background:rgba(255,255,255,0.05);border-radius:4px\"><div style=\"position:absolute;left:65%;top:-5px;height:calc(100% + 10px);border-left:4px dashed #ffdd00;z-index:2\"><span style=\"position:absolute;top:-38px;left:-18px;color:#ffdd00;font-size:32px;font-weight:900;text-shadow:0 0 10px #000,0 0 10px #000\">B1</span></div><div style=\"position:absolute;left:80%;top:-5px;height:calc(100% + 10px);border-left:4px dashed #2ecc71;z-index:2\"><span style=\"position:absolute;top:-38px;left:-18px;color:#2ecc71;font-size:32px;font-weight:900;text-shadow:0 0 10px #000,0 0 10px #000\">B2</span></div><div data-id=\"bar\" style=\"width:0%;height:100%;background:#3498db;border-radius:4px;display:flex;align-items:center;padding-left:15px;color:#fff;font-size:34px;font-weight:700;transition:all 0.6s ease\"></div></div></div>"},
{"layout": "auto-animate-pair", "id": "grade-3a", "step": 2,
 "background_color": "#1a1a2e",
 "title": "M3-3A &mdash; 77%",
 "body": "<div style=\"padding:10px 30px\"><div style=\"display:flex;justify-content:space-between;color:#666;font-size:32px;border-bottom:3px solid #555;padding:0 0 5px 0;margin-bottom:8px\"><span>0</span><span>25</span><span>50</span><span>75</span><span>100</span></div><div style=\"position:relative;height:50px;background:rgba(255,255,255,0.05);border-radius:4px\"><div style=\"position:absolute;left:65%;top:-5px;height:calc(100% + 10px);border-left:4px dashed #ffdd00;z-index:2\"><span style=\"position:absolute;top:-38px;left:-18px;color:#ffdd00;font-size:32px;font-weight:900;text-shadow:0 0 10px #000,0 0 10px #000\">B1</span></div><div style=\"position:absolute;left:80%;top:-5px;height:calc(100% + 10px);border-left:4px dashed #2ecc71;z-index:2\"><span style=\"position:absolute;top:-38px;left:-18px;color:#2ecc71;font-size:32px;font-weight:900;text-shadow:0 0 10px #000,0 0 10px #000\">B2</span></div><div data-id=\"bar\" style=\"width:77%;height:100%;background:#3498db;border-radius:4px;display:flex;align-items:center;padding-left:15px;color:#fff;font-size:34px;font-weight:700;transition:all 0.6s ease\">77%</div></div></div>"}
```

### Transition slide (red background) — task intro too
Transition slides use red `#c0392b`. Task intro slides (instructions + timer) should also use red — they serve the same role as stage separators.

```json
{"layout": "content", "id": "transition-vocab", "step": 1,
 "background_color": "#c0392b", "title": "Key Vocabulary"}
```

### Vocabulary presentation — 3-click reveal table
Each vocab word gets its own slide. Use `raw` layout with a three-row table. Row 1 (phonemic script) is always visible. Rows 2–3 use `class="fragment"` for click-to-reveal. No `title` field — the phonemic script is the sole initial content.

1. **Visible on entry** — phonemic script only, no syllable dots, left-aligned
2. **Click 1** — English word in `<span class="box-word">`
3. **Click 2** — context sentence with clarifying second clause

The context sentence MUST include a clarifying follow-up. "It was a fascinating conversation" tells the student nothing. "It was a fascinating conversation. I was so interested by everything she said" allows inference. Each context sentence is two clauses — the first uses the word, the second explains what it means through a concrete situation.

```json
{"layout": "raw", "id": "vocab-fascinating", "step": 1,
 "background_color": "#1a1a2e",
 "body": "<table style=\"width:100%;text-align:left;border-collapse:collapse;margin-top:30px\"><tr><td style=\"padding:12px 0;font-size:1.4em\">/ˈfæsɪneɪtɪŋ/</td></tr><tr class=\"fragment\"><td style=\"padding:12px 0\"><span class=\"box-word\">fascinating</span></td></tr><tr class=\"fragment\"><td style=\"padding:12px 0\">It was a <span class=\"box-word\">fascinating</span> conversation. I was so interested by everything she said.</td></tr></table>",
 "notes": "Click 1: show word. Click 2: show context. CCQ: Does fascinating mean boring or very interesting?"}
```

Background: `#1a1a2e`. Precede the section with a red transition slide `"Let's check your word knowledge"`.

### Strategy exposition table
Strategy instruction slides (Predict, Underline, Scan, etc.) MUST use a three-row HTML table with `Do` / `Why` / `How` rows. Each row has a yellow `#ffdd00` label cell and a white content cell separated by a thin `#555` border.

```json
{"layout": "content", "id": "strategy-predict", "step": 1,
 "background_color": "#1a1a2e",
 "title": "Strategy: Predict",
 "body": "<table style=\"width:100%;border-collapse:collapse\"><tr><td style=\"padding:8px 12px 8px 0;border-bottom:1px solid #555;font-weight:700;color:#ffdd00;white-space:nowrap;vertical-align:top\">Do</td><td style=\"padding:8px 0;border-bottom:1px solid #555\">Predict answers before you listen.</td></tr><tr><td style=\"padding:8px 12px 8px 0;border-bottom:1px solid #555;font-weight:700;color:#ffdd00;white-space:nowrap;vertical-align:top\">Why</td><td style=\"padding:8px 0;border-bottom:1px solid #555\">It helps your brain focus.</td></tr><tr><td style=\"padding:8px 12px 8px 0;font-weight:700;color:#ffdd00;white-space:nowrap;vertical-align:top\">How</td><td style=\"padding:8px 0\">Read the question. Think first.</td></tr></table>"}
```

The table removes the need for `<span class=\"box-word\">` instruction verbs — the `Do`/`Why`/`How` structure provides clarity visually. Each cell is under 8 words; no row exceeds the 25-word slide limit.

### Strategy demo — auto-animate table
Each strategy exposition slide MUST be followed by a concrete demonstration using `auto-animate-pair` in a table. The demo uses isolated content (NOT from the actual lesson transcript) to illustrate the strategy without spoiling the task.

**Predict demo** — options with checkmark reveals. Step 1 shows options with empty placeholder spans. Step 2 reveals green `✓` checkmarks only on plausible options. The table structure is identical between steps; only the `<span>` content changes:

```json
{"layout": "auto-animate-pair", "id": "demo-predict", "step": 1, "background_color": "#1a1a2e",
 "title": "Try it: Predict",
 "body": "<table style=\"width:100%;border-collapse:collapse\"><tr><td colspan=\"2\" style=\"padding:8px 0;border-bottom:1px solid #444\">A director became famous. What inspired him?</td></tr><tr><td colspan=\"2\" style=\"padding:8px 0;color:#ffdd00;border-bottom:1px solid #444\">Which predictions make sense?</td></tr><tr><td style=\"padding:8px 12px 8px 0;width:36px;text-align:center;vertical-align:middle;border-bottom:1px solid #444\"><span style=\"display:inline-block;width:24px;text-align:center\">&nbsp;</span></td><td style=\"padding:8px 0;border-bottom:1px solid #444\">A camera from his parents.</td></tr><tr><td style=\"padding:8px 12px 8px 0;width:36px;text-align:center;vertical-align:middle;border-bottom:1px solid #444\"><span style=\"display:inline-block;width:24px;text-align:center\">&nbsp;</span></td><td style=\"padding:8px 0;border-bottom:1px solid #444\">A basketball match.</td></tr><tr><td style=\"padding:8px 12px 8px 0;width:36px;text-align:center;vertical-align:middle;border-bottom:1px solid #444\"><span style=\"display:inline-block;width:24px;text-align:center\">&nbsp;</span></td><td style=\"padding:8px 0;border-bottom:1px solid #444\">A famous actor.</td></tr></table>"}
```

Step 2 replaces the `&nbsp;` in options 1 and 3 with green `✓` (`color:#2ecc71;font-weight:900`). Option 2 stays `&nbsp;`. The checkmark span has the same `display:inline-block;width:24px` as the empty span so row heights and border positions are pixel-identical.

**Underline demo** — key words get underlined on click. Step 1 wraps target words in `<strong style=\"text-decoration:none\">`. Step 2 changes to `<strong style=\"text-decoration:underline;text-decoration-color:#ffdd00;text-decoration-thickness:2px;text-underline-offset:4px\">`. The `<strong>` tags exist in BOTH steps so auto-animate can match them:

```json
{"layout": "auto-animate-pair", "id": "demo-underline", "step": 1, "background_color": "#1a1a2e",
 "title": "Try it: Underline",
 "body": "<table style=\"width:100%;border-collapse:collapse\"><tr><td colspan=\"2\" style=\"padding:8px 0;border-bottom:1px solid #444\">Read this question.</td></tr><tr><td colspan=\"2\" style=\"padding:8px 0;border-bottom:1px solid #444\"><strong style=\"text-decoration:none\">What</strong> gave the <strong style=\"text-decoration:none\">director</strong> the <strong style=\"text-decoration:none\">idea</strong> for this movie?</td></tr><tr><td colspan=\"2\" style=\"padding:8px 0;color:#ffdd00;border-bottom:1px solid #444\">Which words would you underline?</td></tr></table>"}
```

### Auto-animate matching rules
reveal.js auto-animate matches child elements by index. For a clean animation that only affects the intended element, follow these rules:

1. **Identical DOM structure between steps.** Every `<tr>`, `<td>`, `<span>`, and `<strong>` must appear in the same positions in both step bodies. If an element exists only in step 2, it fades in abruptly rather than animating.

2. **Elements that animate must exist in both steps.** For underline animations: step 1 uses `<span style=\"text-decoration:none\">`, step 2 uses `<span style=\"text-decoration:underline\">`. For checkmark animations: step 1 uses `&nbsp;`, step 2 uses `<span>✓</span>`. The container element (span) is present in both steps.
3. **Use `<span>` not `<strong>` for invisible target placeholders.** `<strong>` has default `font-weight:bold` that visually distinguishes target words even when `text-decoration:none`, giving the answer away before students click. `<span>` has no default styling and is invisible at `text-decoration:none`.

3. **Empty inline-block spans collapse to zero height.** Always put `&nbsp;` inside any `<span style=\"display:inline-block;width:NNpx\">` that might be empty in one step. Without content, the span has no height, shifting the row's line-height and moving border positions between auto-animate steps.

4. **Identical borders on every `<td>` in the table.** Every cell in every row must have the same `border-bottom:1px solid #444`. Partial borders (e.g. only on the text column but not the checkmark column) create visible artifacts at cell junctions. With `border-collapse:collapse`, collapsed borders merge and render as a continuous uniform line only when all adjacent cells share the same style.

5. **Last-row borders are invisible.** Adding `border-bottom` to the last row's cells is harmless — the border renders below the table and is not visible. Keeping it avoids special-case logic.

6. **Edit JSON with `json.load()`/`json.dump()`, not string matching.** When modifying `data.json` body strings that contain HTML with escaped quotes (`\"`), use Python's `json` module to parse, modify the object, and write back. Raw string pattern matching against JSON-escaped content is fragile and frequently produces zero matches.

### B1 adapted error→correction pair (same errors, simpler language)
When adapting a B2 deck for emergent B1 learners, keep every error type from the original. Simplify only the vocabulary and sentence length. The error coverage table must match between versions:

| Original B2 sentence | B1 simplified version | Same error type |
|----------------------|----------------------|-----------------|
| **i** think that learning **english** will help me get a better job. | **i** like to learn **english**. | i→I, english→English |
| My grandfather who is 68 years old still works as a **Teacher**. | My best friend who lives next door works as a **Teacher**. | Appositive commas + lowercase common noun |
| She wanted to attend the conference however she couldn't get time off. | I wanted to go to the party however I was sick. | Semicolon before however + comma after |

Shorter sentence length (8-14 words instead of 14-18), PET wordlist vocabulary, and familiar contexts (school, family, daily life). Never drop an error category just because the level is lower.

### Consolidated task slide with timer pill
Instead of showing individual work-group slides (one per worksheet section), consolidate into a **single timed task slide**. Students work from the paper worksheet; the slide just provides the instruction + countdown.

Use a `content` layout with a timer pill added via post-processing (`data-timer`). No static timer display in the body — the timer-plugin creates the pill UI automatically.

```json
{"layout": "content", "id": "task1-work", "step": 1,
 "background_color": "#1a1a2e",
 "title": "Task 1",
 "body": "Now fix all the errors in questions 1-10.\n\nQuestion 1 has 2 errors."}
```

Post-processing adds `data-timer="480"` to the section element. This replaces 3-4 separate work-group slides with a single slide.

### Answer slide — table format
Use a four-row table on green `#052e0d` background. Each answer gets its own slide. No fragments, no clickthroughs, no word limit.

| Row | Label (yellow `#ffdd00`) | Content |
|-----|--------------------------|---------|
| Question | `Question` | The question text |
| Answer | `Answer` | The correct answer in a complete sentence |
| Explanation | `Explanation` | Why this is the answer — derived from the transcript |
| Transcript | `Transcript` | Verbatim quote from the source material |

```json
{"layout": "content", "id": "answer-q1", "step": 1,
 "background_color": "#052e0d", "title": "Answers: Detail (1/6)",
 "body": "<table style=\"width:100%;border-collapse:collapse\"><tr><td style=\"padding:8px 12px 8px 0;border-bottom:1px solid #444;font-weight:700;color:#ffdd00;white-space:nowrap;vertical-align:top;width:90px\">Question</td><td style=\"padding:8px 0;border-bottom:1px solid #444\">1. What gave the director the idea?</td></tr><tr><td style=\"padding:8px 12px 8px 0;border-bottom:1px solid #444;font-weight:700;color:#ffdd00;white-space:nowrap;vertical-align:top\">Answer</td><td style=\"padding:8px 0;border-bottom:1px solid #444\">A conversation with a local farmer in Mali.</td></tr><tr><td style=\"padding:8px 12px 8px 0;border-bottom:1px solid #444;font-weight:700;color:#ffdd00;white-space:nowrap;vertical-align:top\">Explanation</td><td style=\"padding:8px 0;border-bottom:1px solid #444\">The farmer told him about his life. The director realized it would make a great movie.</td></tr><tr><td style=\"padding:8px 12px 8px 0;font-weight:700;color:#ffdd00;white-space:nowrap;vertical-align:top\">Transcript</td><td style=\"padding:8px 0\">\u201cHe was talking with a local farmer\u2026\u201d</td></tr></table>"}
```

**One slide per question.** Never pack multiple answers onto one slide — it forces fragmented bullet points under the 25-word limit. With the table format, each slide has room for a complete-sentence answer, pedagogical explanation, and source evidence.

**Engagement/appeal questions**: the `Answer` row states the idea that makes the content compelling (not just the technique). "People everywhere give the same answers" is the engagement. "Close-ups with no names" is technique — it goes in the `Explanation` row as support.

### Timer pill — requires timer-plugin.js + timer-plugin.css
The timer uses a reveal.js plugin. Copy the plugin files from the LPW-3 archive to `slides/`, then add `data-timer="{SECONDS}"` to the section element via post-processing. The body HTML should include the initial display:

```json
{"layout": "raw", "id": "baseline-test", "step": 1,
 "background_color": "#1a1a2e",
 "body": "<style>.timer-pill{display:inline-flex;align-items:center;gap:12px;background:rgba(255,255,255,0.12);border:3px solid #ffdd00;border-radius:40px;padding:12px 28px;margin:20px auto}.timer-pill span{color:#ffdd00;font-size:48px;font-weight:900;letter-spacing:3px;font-variant-numeric:tabular-nums;min-width:100px;text-align:center;font-family:monospace}</style><p style=\"color:#fff;text-align:center;font-size:36px\">Baseline Test</p><div class=\"timer-pill\"><span>&#9202; 15:00</span></div><div class=\"cta-box\"><p>Ready? Start now.</p></div>"}
```

Post-processing adds `data-timer="900"` to the section, injects `timer-plugin.js`/`timer-plugin.css`, and registers `TimerPlugin` in the plugins array. The timer pill UI (start/pause/reset buttons) appears automatically on that slide.

### CEFR distribution (raw with fragment segments)
```json
{"layout": "raw", "id": "cefr-3a", "step": 1,
 "background_color": "#1a1a2e",
 "body": "<style>.cefr-bar{display:flex;height:110px;border-radius:8px;overflow:hidden;width:100%;margin:30px 0}.cefr-bar .seg{display:flex;align-items:center;justify-content:center;color:#fff;font-size:32px;font-weight:700;flex-direction:column;line-height:1.3}.cefr-bar .seg strong{font-size:40px}.seg-a2u{background:#f39c12}.seg-b1l{background:#3498db}.seg-b1u{background:#2ecc71}.seg-b2l{background:#e67e22}.c-label{color:#fff;text-align:center;font-size:52px;font-weight:700}.c-sub{color:#ccc;text-align:center;font-size:38px}</style><h4 class=\"c-label\">M3-3A (19 students)</h4><p class=\"c-sub\">How many achieved <strong>B1</strong> or <strong>B2</strong>?</p><div class=\"cefr-bar\"><div class=\"fragment seg seg-a2u\" style=\"width:16%\">A2+<br><strong>3</strong></div><div class=\"fragment seg seg-b1l\" style=\"width:37%\">B1<br><strong>7</strong></div><div class=\"fragment seg seg-b1u\" style=\"width:37%\">B1+<br><strong>7</strong></div><div class=\"fragment seg seg-b2l\" style=\"width:10%\">B2<br><strong>2</strong></div></div>"}
```

### Matching exercise — auto-animate pair with 2-column grid
Stems on the left, options on the right. Each option has a consistent `data-id` across both steps. In step 1 options are scrambled; step 2 places them in correct positions. Auto-animate slides each option to its matched row.

**Use the helper script** `scripts/matching_exercise.py` to generate matching pairs automatically:

```python
import sys; sys.path.insert(0, "/home/elwru/.kilo/skills/slideshow-renderer/scripts")
from matching_exercise import build_matching_pair

slides += build_matching_pair(
    slide_id="match-ex4",
    title="Match the halves",
    stems=[
        "I thought the movie was a documentary,",
        "The movie deals with real-life issues",
        "This documentary was shot",
    ],
    options=[
        "but it was completely fictional",
        "like homelessness and unemployment",
        "on location in Hawaii",
    ],
    correct_order=[0, 1, 2],  # index of correct option for each stem
    bg_color="#052e0d",
)
```

**Manual approach** (if not using the script):
- Use `auto-animate-pair` layout with two steps
- Every option gets a stable `data-id="o1"`, `o2`, etc. consistent across both steps
- Step 1: options scrambled. Step 2: options in correct matching order
- Stem elements get stable `data-id="s1"`, `s2`, etc.
- CSS: `font-size:32px`, no bold, left-aligned, `white-space:nowrap`
- `data-id` values: `o1`–`oN` for options, `s1`–`sN` for stems

### B2 salary slide — use Thai Baht figures
```json
{"layout": "content", "id": "b2-jobs", "step": 1,
 "background_color": "#1a1a2e",
 "title": "B2 means better jobs &amp; pay",
 "body": "<span style=\"color:#ffdd00\">International companies pay <strong>20–50% more</strong> for roles needing B2 English. Same job at an MNC = <strong>฿15,000–35,000 extra</strong> per month.</span>"}
```

## Color Scheme

| Slide Type | Background Color | Usage |
|-----------|-----------------|-------|
| Content / Vocab / Strategy | `#1a1a2e` (dark navy) | Regular slides |
| Transition | `#c0392b` (red) | Stage separators, heading only |
| Answer / Gap-fill answers | `#052e0d` (dark green) | Answer reveals |
| Title / Splash | image background | Full-bleed image |
| CTA box border | `#ffdd00` (yellow) | `.cta-box` and `.box-word` borders |
| CTA text | `#ffdd00` (yellow) | `.cta-text` color |
| Highlight text | `#ffdd00` (yellow) | Bold/yellow emphasis |
| B1 marker | `#ffdd00` (yellow) dashed 4px | Threshold line on bar charts |
| B2 marker | `#2ecc71` (green) dashed 4px | Threshold line on bar charts |

## Reveal.js Config (hardcoded in CDN skeleton)

```javascript
Reveal.initialize({
    controls: true, progress: true, history: true,
    width: 1280, height: 720,
    transition: "slide",
    plugins: [ RevealNotes, RevealHighlight, RevealSearch, RevealZoom ]
});
```

- `center: true` is OFF — all sections use `justify-content: flex-start !important` (matches legacy reference).
- `width: 1280, height: 720` — not the default 960x700.

## Constraints

- Do NOT read or edit `slideshow_lib/` files — it is read-only
- Do NOT write raw HTML, CSS, or reveal.js attribute names in data.json
- Do NOT write Jinja2 template code
- Do NOT assign `data-*` attributes — the resolver handles all cross-slide continuity
- Do NOT write `data-fragment-index` — the resolver assigns sequential indices across the deck
- Body content is raw HTML passed verbatim through Jinja2 to reveal.js
- Maximum 25 body-text words per content slide
- Maximum 40 slides total
- Use `<p>` or `<br>` elements for paragraph breaks in HTML bodies
- **Title slide MUST have `logo`, `shield: true`, `background_image`** — all three required
- Logo file: `PROJECTS/{project_folder}/slides/assets/logo.png` (md5: `6b3a32e5`)
- Logo color: `#a52d26` (school red)
- Do NOT add `logo` to any slide other than the title slide
- **Minimum font size: 28px everywhere.** Prefer 32px+ for body, 44px+ for headings, 40px+ for timer/numbers.
- **No clickthroughs on expositional or instructional slides** (except vocabulary 3-click reveal — see Design Patterns). All content visible at once.
- **Auto-animate for bar chart anticipation AND error→correction pairs AND strategy demos.** For before/after answer reveals, use `auto-animate-pair` with each step containing matching body text. See Auto-animate matching rules in Design Patterns for DOM structure requirements.
- **Table borders must be identical on every `<td>`.** Partial borders (on some cells but not others) create visible width/color artifacts at cell junctions. Always include `border-bottom:1px solid #444` on every cell in the table, including the last row (the border renders below the table and is harmless).
- **Empty inline-block spans need `&nbsp;`.** A `<span style=\"display:inline-block;width:24px\">` with no content collapses to zero height, shifting row line-heights and making borders appear to move between auto-animate steps. Always put `&nbsp;` inside placeholder spans.
- **Never stop the HTTP server on re-render.** Python's `http.server` reads files from disk on every request. Re-rendering overwrites `index.html` in-place; the server picks up the new file automatically.
- **B1 adaptation preserves all error types.** A lower CEFR level means simpler vocabulary and shorter sentences, NOT fewer error patterns. If M3 students need appositives, semicolons, and compound-sentence commas, M2 students do too — write simpler examples covering the same grammar.
- **No cryptic abbreviations on slides or worksheets.** Write full words, not single-letter stand-ins. "W/T" is confusing — write "We / The" so students and teachers can parse it without decoding.
- **Verify slide order after any JSON edit.** Changing a title or body does NOT reorder slides. The JSON array order IS the slide order. After renumbering or swapping content, re-read the array from top to bottom to confirm sequence (1, 2, 3, 4 not 1, 3, 2, 4).
- **Never use shell substitution for string manipulation.** `${var//pattern/replacement}` in zsh or bash will corrupt HTML files (reduced to 1 byte) when patterns contain `/`. Use Python `str.replace()` for all post-processing — always.
- **Edit data.json with `json.load()`/`json.dump()`, not raw string matching.** Body strings contain JSON-escaped HTML with `\"` sequences. Raw string replacement frequently fails with zero matches because the escaping doesn't align. Parse the JSON, modify the Python object, and write back with `json.dump(data, indent=2, ensure_ascii=False)`.
- **Each class on its own slide.** Never combine multiple classes in one chart.
- **Never write** "Click to reveal" or similar instructional text on slides.
- B1 threshold at 65%, B2 threshold at 80% on grade bar charts. Use 4px dashed lines with 32px labels and text-shadow.
- Timer pill pattern: `<div class="pill"><span class="pill-icon">&#9202;</span><span class="pill-time">15:00</span></div>` with CSS border-radius:40px.
- CEFR headers: `"M3-3A (N students)"` + `"How many achieved B1 or B2?"`.

## Extending the Pipeline

To add a new feature (e.g. a new layout type or a new field):

1. **Model** (`render.py`): Add field to `SlideRecord` and `ResolvedSlide`
2. **Resolver** (`render.py`): Pass through the field in `resolve_deck()`
3. **Macros** (`macros.jinja2`): Add rendering logic to the relevant macro(s)
4. **CSS** (`render.py`): Add styles to the `CDN_SKELETON` `<style>` block (double braces `{{...}}`)
5. **This file**: Update the schema table and design patterns

## Example

**Request:** Create slides for a midterm review lesson (M3-A, Thai middle schoolers)

**Action:** Ask user for splash image. Read ESL voice + best-practices prompts. Copy school logo from `ASSETS/logo.png` to `PROJECTS/{project_folder}/slides/assets/logo.png`. Fetch grade data from Google Sheet via service account. Plan 30-slide sequence with separate slides per class for each chart type. Use auto-animate pairs for bar charts (step 1 empty, step 2 full), raw layout for CEFR segments with fragments, content layout for exposition (no fragments). Write `PROJECTS/{project_folder}/data.json`. Run render.py. Deploy via `/git-pages`.

**Output:** `PROJECTS/{project_folder}/slides/index.html` → `https://elwrush.github.io/lesson-plan-writer/{name}/`
