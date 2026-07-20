---
name: slideshow-renderer
description: Generate reveal.js slideshows from structured data using Jinja2 macros and a layout-driven resolver pipeline.
license: MIT
compatibility:
  - python3
  - pandoc
metadata:
  author: Ed Rush (C·E·L Mathayom / ACT)
---

# Skill: Slideshow Renderer

**Pipeline:** Structured data → Pydantic validation → Resolver (auto-ids) → Jinja2 macros → CDN reveal.js HTML  
**Agent writes:** Structured JSON only — layout enum + content slots. Never writes HTML, template code, or reveal.js attribute names.  
**Resolver handles:** Auto-animate `data-id` continuity, fragment index sequencing, element matching.  
**Macros handle:** HTML generation per layout type via `slideshow_lib`.

## Purpose

Generate classroom-ready reveal.js slideshows from structured JSON data using a Pydantic-validated pipeline with auto-animate resolution and Jinja2 macro rendering. The agent writes only structured data — the pipeline handles all HTML, CSS, and reveal.js configuration.

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
**BEFORE generating** the slideshow, the agent MUST ask the user: *"What image should I use for the splash / title background?"* Create or download the image, save it to `slides/assets/`, then reference it in both splash (`image_url`) and title (`background_image`).

| Field | Value | Why |
|-------|-------|-----|
| `background_image` | path to full-bleed image | Background photo for the title slide |
| `logo` | path to logo PNG | Copy `logo.png` from archived slides assets. RGBA with alpha channel. md5: `6b3a32e5`. |
| `shield` | `true` | Wraps title/body in dark semi-transparent boxes for readability on image |

**NEVER** omit `logo` from the title slide. The school logo is required on every title slide. Place it at `slides/assets/logo.png`.

The `logo` field is ONLY for the title slide. Do not add it to other slides.

## ⚠️ NON-NEGOTIABLE RULES — Clickthroughs

- **Expositional and instructional slides** must NEVER have clickthroughs/fragments. All content visible at once.
- **Bar charts** CAN use auto-animate pairs for anticipation (empty bar → grows to value on click).
- **CEFR band reveals** CAN use fragments to reveal each segment one click at a time.
- **Never** include instructional text like "Click to reveal" — the teacher knows how to use the slides.

## ⚠️ NON-NEGOTIABLE RULES — Font Sizes

Minimum font sizes for classroom projection (1280x720):

| Element | Minimum | Notes |
|---------|---------|-------|
| Headings / class names | 44px | Use 48-52px for prominence |
| Body text | 32px | 34-36px preferred |
| Bar values and labels | 32px | Bar fill text, skill names |
| Axis numbers (0-100) | 32px | No smaller |
| B1/B2 markers | 32px | 4px dashed line, text-shadow for readability |
| Segment counts (CEFR) | 40px | The bold number inside each segment |
| Timer pill time | 40px | Yellow bold in pill shape |

No text below 28px anywhere in the deck. Adjust `font-size` in inline styles or `<style>` blocks accordingly.

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
- ❌ HTML tags, CSS, or reveal.js config (except `<span class=\"box-word\">` inside Markdown content for boxing target words)
- ❌ Fragment indices or auto-animate pairing logic

### Authorial voice

- **Student-facing only** — slides show what students need to see. Teacher instructions, CCQs, and timing go in `notes`.
- **Short imperatives** — "Read each question." "Predict the answer." "Watch the video."
- **No worksheet text** — don't project answer options (A/B/C) or worksheet content. Those are on paper.
- **Conversational "you"/"we"** — not formal textbook English.
- **One concept per slide** — Max 25 body-text words. Max 40 slides total.
- **Box action verbs only** — Use `<span class="box-word">Read</span>` for action words (Read, Predict, Underline, Listen, Watch). Informational scaffolds (Opinion/Reason/Example) get plain `**bold**`, not boxed.

## When to Use

Use this skill when generating reveal.js slideshows for classroom presentation from structured lesson content. The pipeline handles slide layout selection, cross-slide attribute continuity, and CDN-based HTML generation.

## Workflow

### Step 1 — Read ESL voice and best-practice prompts
Read `prompts/esl-voice.md` and `prompts/best-practices.md` before writing any content.

### Step 2 — Ask for splash image
**BEFORE writing data.json**, ask the user what image to use for the splash/title background. Then find or create it and save to `slides/assets/`.

### Step 3 — Copy logo
Before writing data.json, copy the school logo from archived slides:
```bash
cp "PROJECTS/ARCHIVE/LESSON-PLAN-WRITER-3/output/ARCHIVE/M3-COLUMBUS/slides/assets/logo.png" "slides/assets/logo.png"
```
Verify md5: `6b3a32e5a31ddee217875af9f730739e`

### Step 4 — Write data.json
Write structured JSON with the `DeckData` schema. The title slide MUST include `logo: "assets/logo.png"`, `shield: true`, and `background_image`. Each slide record supports:

| Field | Type | Used by | Purpose |
|-------|------|---------|---------|
| `layout` | string | all | `content`, `two-column`, `auto-animate-pair`, `code`, `image`, `raw` |
| `id` | string | all | Unique slide identifier |
| `step` | int | all | Sequence position within a group (1-based) |
| `title` | string | content, code, image | Slide heading (Markdown) |
| `body` | string | content, two-column, image | Body content (Markdown) |
| `notes` | string | all | Speaker notes (teacher instructions only) |
| `background_color` | string | all | CSS hex color (e.g. `#1a1a2e`, `#c0392b`, `#052e0d`) |
| `background_image` | string | all | Relative path for slide background image |
| `fragments` | array | content | Markdown strings, each renders as click-to-reveal `<div class="fragment">` |
| `shield` | bool | content | Wraps title/body in shield divs (image-background title slides) |
| `logo` | string | content | Relative path to logo PNG (RGBA with alpha, md5: 6b3a32e5) |
| `cta` | string | content | Call-to-action text rendered in a yellow-bordered box |
| `image_url` | string | image | Background image path |
| `code` | string | code | Source code |
| `language` | string | code | Language for syntax highlighting |

### Step 5 — Copy timer plugin (if needed)
If the deck has timed activities, create `slides/timer-plugin.js` and `slides/timer-plugin.css`.

**timer-plugin.js** — reveal.js plugin that shows a countdown pill on slides with `data-timer="{seconds}"`:
```javascript
(function () {
    var BLIP_SRC = "assets/blip.mp3";
    var BELL_SRC = "assets/BELL.mp3";
    var WARNING_THRESHOLD = 10;

    var pillEl = null, displayEl = null, startBtn = null, pauseBtn = null, resetBtn = null;
    var blipAudio = null, bellAudio = null;
    var totalSeconds = 0, secondsLeft = 0, intervalId = null, finished = false, lastMinute = -1;

    function createPill() {
        if (pillEl) return;
        pillEl = document.createElement("div"); pillEl.className = "timer-pill";
        startBtn = document.createElement("button"); startBtn.className = "timer-pill__btn"; startBtn.innerHTML = "\u25B6"; startBtn.title = "Start timer";
        pauseBtn = document.createElement("button"); pauseBtn.className = "timer-pill__btn timer-pill__btn--hidden"; pauseBtn.innerHTML = "\u23F8"; pauseBtn.title = "Pause timer";
        resetBtn = document.createElement("button"); resetBtn.className = "timer-pill__btn"; resetBtn.innerHTML = "\u21B4"; resetBtn.title = "Reset timer";
        displayEl = document.createElement("span"); displayEl.className = "timer-pill__display";
        [startBtn, pauseBtn, resetBtn, displayEl].forEach(function(el){ pillEl.appendChild(el); });
        document.body.appendChild(pillEl);
        startBtn.addEventListener("click", function(){ playBlip(); onStart(); });
        pauseBtn.addEventListener("click", function(){ playBlip(); onPause(); });
        resetBtn.addEventListener("click", function(){ playBlip(); onReset(); });
    }

    function fmt(s){ var m=Math.floor(s/60); var n=s%60; return (m<10?"0":"")+m+":"+(n<10?"0":"")+n; }

    function showPill(){ pillEl.classList.add("timer-pill--visible"); }
    function hidePill(){ pillEl.classList.remove("timer-pill--visible"); }
    function playBlip(){ if(blipAudio){ blipAudio.currentTime=0; blipAudio.play().catch(function(){}); }}
    function playBell(){ if(bellAudio){ bellAudio.currentTime=0; bellAudio.play().catch(function(){}); }}

    function onStart(){
        if(finished)return; startBtn.classList.add("timer-pill__btn--hidden"); pauseBtn.classList.remove("timer-pill__btn--hidden");
        lastMinute=Math.floor(secondsLeft/60); intervalId=setInterval(tick,1000); tick();
    }

    function onPause(){ clearInterval(intervalId);intervalId=null;startBtn.classList.remove("timer-pill__btn--hidden");pauseBtn.classList.add("timer-pill__btn--hidden");}
    function onReset(){ clearInterval(intervalId);intervalId=null;secondsLeft=totalSeconds;finished=false;lastMinute=Math.floor(secondsLeft/60);startBtn.classList.remove("timer-pill__btn--hidden");pauseBtn.classList.add("timer-pill__btn--hidden");pillEl.classList.remove("timer-pill--warning");pillEl.classList.remove("timer-pill--expired");displayEl.textContent=fmt(secondsLeft);}

    function tick(){
        if(secondsLeft<=0){clearInterval(intervalId);intervalId=null;finished=true;startBtn.classList.add("timer-pill__btn--hidden");pauseBtn.classList.add("timer-pill__btn--hidden");pillEl.classList.add("timer-pill--expired");displayEl.textContent="00:00";playBell();return;}
        secondsLeft--;displayEl.textContent=fmt(secondsLeft);
        if(secondsLeft<=WARNING_THRESHOLD){pillEl.classList.add("timer-pill--warning");playBlip();}
        var cm=Math.floor(secondsLeft/60);if(cm<lastMinute){lastMinute=cm;playBell();}
    }

    function loadSlideTimer(deck){
        hidePill();var slide=deck.getCurrentSlide();if(!slide)return;
        var tv=slide.getAttribute("data-timer");if(!tv)return;
        var p=parseInt(tv,10);if(isNaN(p)||p<=0)return;
        totalSeconds=p;secondsLeft=totalSeconds;finished=false;lastMinute=Math.floor(secondsLeft/60);
        pillEl.classList.remove("timer-pill--warning");pillEl.classList.remove("timer-pill--expired");
        startBtn.classList.remove("timer-pill__btn--hidden");pauseBtn.classList.add("timer-pill__btn--hidden");
        displayEl.textContent=fmt(secondsLeft);showPill();
    }

    window.TimerPlugin = { id: "timer-pill", init: function(deck){
        createPill();
        blipAudio=new Audio(BLIP_SRC);blipAudio.preload="auto";
        bellAudio=new Audio(BELL_SRC);bellAudio.preload="auto";
        deck.on("slidechanged",function(){loadSlideTimer(deck);});
        deck.on("paused",function(){if(intervalId!==null)onPause();});
    }};
})();
```

**timer-plugin.css**:
```css
.timer-pill{display:none;position:fixed;bottom:24px;left:50%;transform:translateX(-50%);z-index:100;background:rgba(0,0,0,0.75);border-radius:28px;padding:8px 18px;box-shadow:0 4px 20px rgba(0,0,0,0.5);align-items:center;gap:12px;font-family:"Courier New",Courier,monospace;user-select:none}
.timer-pill--visible{display:flex}
.timer-pill--warning{background:rgba(180,130,0,0.85)}
.timer-pill--expired{background:rgba(180,40,40,0.85)}
.timer-pill__display{color:#fff;font-size:2em;font-weight:700;min-width:80px;text-align:center;letter-spacing:2px}
.timer-pill__btn{width:36px;height:36px;border-radius:50%;border:2px solid rgba(255,255,255,0.5);background:0 0;color:#fff;font-size:1.1em;cursor:pointer;display:flex;align-items:center;justify-content:center;padding:0;line-height:1}
.timer-pill__btn:hover{border-color:#fff}
.timer-pill__btn--hidden{display:none}
```

Copy `blip.mp3` and `BELL.mp3` from `ASSETS/` to `slides/assets/`. Then in the baseline-test slide body (raw layout), include only the instructions — the timer pill UI is created by the plugin. Do NOT put a static timer display in the body.

### Step 6 — Render
```bash
python ~/.kilo/skills/slideshow-renderer/scripts/render.py --data data.json --output slides/index.html
```

### Step 7 — Post-process for timer plugin
After rendering, inject timer-plugin files into the HTML:
```bash
python3 -c "
import re
h = open('slides/index.html').read()
h = h.replace('</head>', '  <link rel=\"stylesheet\" href=\"timer-plugin.css\">\n</head>')
h = h.replace('data-id=\"slide-{SLIDE_ID}-1\"', 'data-id=\"slide-{SLIDE_ID}-1\" data-timer=\"{SECONDS}\"')
h = h.replace('<script src=\"https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.js\"></script>', '<script src=\"timer-plugin.js\"></script>\n  <script src=\"https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.js\"></script>')
h = h.replace('plugins: [ RevealNotes, RevealHighlight, RevealSearch, RevealZoom ]', 'plugins: [ RevealNotes, RevealHighlight, RevealSearch, RevealZoom, TimerPlugin ]')
open('slides/index.html','w').write(h)
"
```

### Step 8 — Preview locally (audio scrubber note)
To preview slides locally, use **`http-server`** (Node) — Python's `http.server` does not support `Accept-Ranges: bytes`, which breaks the audio scrubber (seek bar) on `<audio>` elements.

```bash
# ✅ Works — audio scrubber functional
npx http-server -p 8080 --cors -g PROJECTS/{project_folder}/slides

# ❌ Broken — audio scrubber won't seek
python3 -m http.server 8080
```

If `npx http-server` is unavailable, install globally: `npm install -g http-server`.

### Step 9 — Deploy
Use `/git-pages {name}` to push to GitHub Pages from the project subfolder's `slides/` directory.

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

### Transition slide (red background)
```json
{"layout": "content", "id": "transition-vocab", "step": 1,
 "background_color": "#c0392b", "title": "Key Vocabulary"}
```

### Answer slide (green background) — no fragments
```json
{"layout": "content", "id": "test-answers", "step": 1,
 "background_color": "#052e0d",
 "title": "Answers",
 "body": "Let's mark together.\n\n<span class=\"box-word\">Swap</span> books with a partner.\n\nI'll show each answer.\n\n<span class=\"box-word\">Tick</span> correct answers.\n\n<span class=\"box-word\">Correct</span> wrong answers in a different colour."}
```

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
- Do NOT write `fragment_index` — the resolver assigns sequential indices across the deck
- Content is Markdown — use `**bold**`, `*italic*`, `` `code` ``, and `<span class=\"box-word\">` for boxing target words
- Maximum 25 body-text words per content slide
- Maximum 40 slides total
- Use `\n\n` (blank line) for separate paragraphs, not `\n` (soft break)
- **Title slide MUST have `logo`, `shield: true`, `background_image`** — all three required
- Logo file: `slides/assets/logo.png` (md5: `6b3a32e5`)
- Logo color: `#a52d26` (school red)
- Do NOT add `logo` to any slide other than the title slide
- **Minimum font size: 28px everywhere.** Prefer 32px+ for body, 44px+ for headings, 40px+ for timer/numbers.
- **No clickthroughs on expositional or instructional slides.** All content visible at once.
- **Auto-animate only for bar chart anticipation.** Empty bar → full bar on click.
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

**Action:** Ask user for splash image. Read ESL voice + best-practices prompts. Copy school logo from LPW-3 archive to `slides/assets/logo.png`. Fetch grade data from Google Sheet via service account. Plan 30-slide sequence with separate slides per class for each chart type. Use auto-animate pairs for bar charts (step 1 empty, step 2 full), raw layout for CEFR segments with fragments, content layout for exposition (no fragments). Write `data.json`. Run render.py. Deploy via `/git-pages`.

**Output:** `PROJECTS/{project_folder}/slides/index.html` → `https://elwrush.github.io/lesson-plan-writer/{name}/`

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| Render outputs 0 slides | No `slides` array in `data.json` | Check JSON structure |
| Splash slide missing | No `image` layout slide at position 0 | Add `{"layout": "image", "id": "splash", "image_url": "assets/..."}` |
| Title slide missing logo | `logo` field omitted | Add `"logo": "assets/logo.png"` |
| Timer pill visible everywhere | CSS class collision: slide body uses `.timer-pill` (same as plugin class) | Rename slide body class to `.task-timer` |
| Auto-animate not working | `data-id` values don't match between steps | Ensure consistent `data-id` on paired elements |
| Fragments all numbered "1." | Markdown auto-numbering in separate fragment divs | Use raw HTML `<table>` instead of content layout fragments |
| Gray text invisible on projector | Color values like `#888`, `#ccc`, `#aaa` | Use only `#fff` or `#ffdd00` on dark backgrounds |
| Font too small for projection | `font-size` below 28px | Run `validate_slide_fonts.py` before deploying |
