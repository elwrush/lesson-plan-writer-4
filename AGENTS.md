# LESSON-PLAN-WRITER-4

Data-only repo: lesson shape templates + per-project slide decks, cue cards, and worksheets.  
No Makefile, no build system. Venv has pytest only.

## Architecture Decision Records (ADRs)

We capture significant architectural decisions as **ADRs**, written at the **project level**.
Each lesson/feature project records its own decisions; for this data-only repo the shared
ADRs live in the repo-root **`adr/`** folder. This is opencode-ready — the instructions below
are loaded when opencode starts, so the agent is always ADR-aware.

- **One ADR per file, one topic each.** A decision never shares a file.
- **Each file under 5KB** — forces clarity and concision.
- **Named `NNNN-topic.md`** (e.g. `0001-fish-audio-single-skill.md`), prefixed with the
  ADR-template frontmatter (`title`, `status`, `date`, `deciders`).
- **Status is one of** `proposed` | `accepted` | `deprecated` | `superseded`. New ADRs open as
  `proposed` and flip to `accepted` once confirmed.
- **Structure:** Context → Decision → Consequences (good / bad / risks). Copy
  `adr/ADR-template.md`.
- **When to write one:** whenever a non-obvious choice is made that future-you (or another
  project) would otherwise have to re-derive — e.g. unifying a tool, choosing an approach with
  real trade-offs, or a hard-won lesson worth recording. Write the ADR at the time of the
  decision, not retroactively.

## Remotes

| Remote | URL | Purpose |
|--------|-----|---------|
| `old-origin` | `elwrush/lesson-plan-writer` | gh-pages host. All `/git-pages` go here. |
| `origin` | `elwrush/lesson-plan-writer-4` | Source repo. Never push gh-pages here. |

`/git-pages` deploys to `old-origin`; falls back to `origin`.

## Tooling

Runs under **opencode** (migrated from KiloCode). Project commands live in
`.opencode/command/*.md`; config is `opencode.json`. Global skills (`slideshow-renderer`,
`write-lesson-plan`, `pixabay-image-search`, etc.) are registered via `skills.paths`
pointing at `~/.agents/skills`.

- **`just`** (command runner) is installed — the repo-root `justfile` holds the
  multi-command workflows. See **Recipes (`just`)** below.
- `/git-pages [name] [source-dir]` (in `.opencode/command/git-pages.md`) is the gh-pages
  deploy command. `source-dir` defaults to `slides/`; quote it if it has spaces. It
  clones gh-pages into an isolated worktree (never touches the main branch), regenerates
  the landing page, and **verifies the pushed file back by MD5** — don't skip that step.
- Slides are gitignored (`**/slides/`); only the gh-pages branch carries them.

## Recipes (`just`)

**`just` is installed and available.** Run `just --list` (or `just help`) to see every
recipe. Use the recipes instead of reconstructing command order — order matters and the
paths are long. Project dirs contain a **space**, so pass `name` as a positional arg
that you quote: `just render "LISTENING M3"`.

| Recipe | What it does |
|--------|--------------|
| `just render "LISTENING M3"` | build → render → post-process → validate fonts (the full dev loop). Only works for projects with a `build_deck.py`. |
| `just validate "LISTENING M3"` | font validation only (gray-color / undersized-text gate). |
| `just test` | `pytest tests/` (gh-pages safety tests). |
| `just serve` | start `http.server` on :8080 in the background — **idempotent**, won't start a second one; never stop it. |

`just render` is a **hard gate** — the final `validate_fonts` step exits non-zero on
gray text (`#aaa`) or undersized fonts. Keep instruction/muted text in a non-gray,
passing color like `#f0f0f0` (not `#aaa`/`#ddd`/`#ccc`).

## Project layout

```
PROJECTS/{name}/              # Per-lesson directory (15-40 files)
  data.json                   # Slide deck. Load slideshow-renderer skill first.
  lesson.json                 # Source textbook lesson metadata + exercises
  transcript.json             # Audio transcript for listening tasks
  build_data.py               # Deck builder: wires structure only, text authored verbatim
  generate_cue_cards.py       # Speed-dating cue cards (self-contained Playwright)
  generate_worksheet.py       # Bespoke worksheet via write-test-worksheet skill
  post-process.py             # Timer + plugin injection (re-run after every render)
  classroom-layout.svg        # Classroom layout diagram for rotation models
  slides/assets/              # splash.jpg, logo.png, blip/BELL.mp3, audio
```

Top-level: `LESSON-SHAPES/shape-{a..g,k,l}.json`, `RESEARCH/*.md` (pedagogical references), `tests/test_git_pages_safety.py`.

**Pronunciation lessons (Shape L — see `LESSON-SHAPES/shape-l.json` + `RESEARCH/pronunciation-noticing.md`):**
- Model sentences place every target before a vowel or a pause — never "wanted to", "fight game", "last night" (natives reduce those too).
- Noticing texts use numbered underlined targets: `[0]` = example item, `[1]`–`[n]` = scored. Correct the transcript ONLY in the target feature; leave all other grammar verbatim.
- **Tick/cross answer keys for audio MUST be verified by a teacher listening to the recording** — LLM judges and regex cannot hear dropped consonants. Never guess a key.
- Student-facing slides say "the model", never the celebrity voice name.

## Classes

`M2`, `M3-A`, `M2-4A`, `M2-5A`, `M2A`, `M3A` — never invent others.

## HTTP server

- Python `http.server` or `npx http-server -p 8080 --cors -g` on port 8080.
- If nothing is listening on 8080, start one from the repo root: `python3 -m http.server 8080` (tracked as a background process). The deck URL is `http://localhost:8080/PROJECTS/{name}/slides/index.html`.
- Re-rendering overwrites `index.html` in-place; **do NOT stop the server**.
- Don't ask about it.

## Pixabay image search

Splash/background photos come from Pixabay first. Setup:

- **Script:** `scripts/pixabay_download.py` at the repo root (working copy). The canonical copy lives in the `pixabay-image-search` skill at `~/.agents/skills/pixabay-image-search/scripts/pixabay_download.py`. If either is missing, restore it from git history: `git show $(git log --all --format=%H -- scripts/pixabay_download.py | head -1):scripts/pixabay_download.py > scripts/pixabay_download.py`. It reads the API key from the env var `PIXABAY_API_KEY` and outputs JSON with `path` + `attribution`.
- **API key:** `PIXABAY_API_KEY` is exported in the *interactive* shell environment (injected by the opencode CLI alongside the other API keys — it is NOT in `~/.zshrc` or any rc file). Non-interactive/tool shells do NOT inherit it, so always run the download through an interactive zsh:

```bash
zsh -ic 'python scripts/pixabay_download.py --query "architectural blueprint" --type image --count 3 --output "PROJECTS/{name}/slides/assets/"'
```

  If it errors with "PIXABAY_API_KEY environment variable not set", export it first (export the key from your shell environment) inside the `zsh -ic` invocation.
- **Fallback:** if Pixabay returns nothing usable, use the `search-wikimedia-commons` skill (free, no key) or the `download-image-from-url` skill for a direct URL.
- After download, centre-crop to 16:9 with ImageMagick/Pillow before using as `splash.jpg`.

## Slideshow workflow

### Before writing data.json

1. Ask user for splash image. Download/crop to 16:9 for the reveal canvas (1280×720; a 1920×1080 master is fine), save to `slides/assets/splash.jpg`.
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

**Timers**: write a `post-process.py` per deck. The resolver adds `slide-{id}-1` prefixes to data-ids — `TIMER_DATA` keys MUST be the full resolved form (e.g. `slide-speed-cp-1`, not `speed-cp`). Timer auto-start via `data-timer-autostart="true"`. Re-run post-processing after every render.

## Hard-earned gotchas

**Browser cache.** Do NOT version the timer-plugin.css link (`?v=N`) — reference it plainly and overwrite the file in place. The deck page carries `Cache-Control: no-store` meta tags (injected by post-processing), so the browser always re-fetches the document and its linked CSS. If a change still looks stale, hard refresh (Ctrl+Shift+R).

**Timer pill.** The canonical plugin is in the slideshow-renderer skill at `references/timer-plugin.md` (the archive copy under `PROJECTS/ARCHIVE/JULY 20 M3 VOCAB MOVIES/slides/` is OLD — it lacks the `clearInterval` guard in `onStart()` and auto-start support in `loadSlideTimer()`). **NEVER put a static `<div class="timer-pill">` or an inline `.timer-pill{...}` `<style>` rule in a slide body** — the plugin owns that class; an inline style overrides the plugin's `display:none` and forces the pill (▶ start / ↴ reset buttons) to render on every slide. The plugin creates the pill UI automatically; the body must NOT contain a pill. Post-processing must be idempotent (guard every `data-timer` / CSS / script / plugin-array injection) so re-runs after re-renders never duplicate attributes or script tags.

**Timer load order (deck goes blank white + can't navigate).** `TimerPlugin` must be **defined before** `Reveal.initialize()` runs — the `plugins: [..., TimerPlugin]` array is evaluated at init. If `timer-plugin.js` loads at `</body>` (after the init script block), you get `TimerPlugin is not defined`, `Reveal.next is not a function`, and a dead/blank slide that can't be navigated. Inject `timer-plugin.js` **before** the `<script src=".../reveal.js@5.1.0/dist/reveal.js"></script>` tag, never at `</body>`. Verify with Playwright: navigate to a slide and confirm `section.present` resolves and `Reveal.next()` works.

**Timers belong only on speed-dating slides** (`speed-cp`, `speed-fp`) — a 2-minute round pill. Do **NOT** add `data-timer` to tape/video or dictation slides: the user explicitly rejected timer pills on the YouTube-embedded listening pages. When debugging, note the pill is appended to `.reveal` (a sibling of `<section>`), so `document.querySelector('section.present .timer-pill')` is always null — query `.timer-pill` directly.

**Slide layout.** Use `raw` layout with CSS `<style>` blocks and centered tables (`margin:auto`, `max-width`). Don't use `content` layout for anything with HTML. Copy the CSS pattern from the working archive project, not from memory.

**Reveal.js config.** Never inject `margin`, `center`, or `disableLayout` overrides via post-processing. The default config (`width:1280, height:720`) works. Every override tried made the slides worse.

**Gist answers.** "How does it engage?" questions need concept answers (the *idea* that makes it compelling), not technique (close-ups, no names). Split across multiple slides when 25-word limit forces fragmented bullets.

**Vocab context sentences.** Must include a clarifying second clause. "It was a fascinating conversation" is useless. "It was a fascinating conversation. I was so interested by everything she said" allows inference. **Context sentences must be NEUTRAL — never reuse the reading/listening story** (characters, setting, key events). The word comes from the text; the example sentence must NOT ("She ran to the decontamination shower" is a story line, not an example — use "The hospital has a decontamination shower. It cleans dangerous germs off people.").

**Strategy demos.** Use `<span>` not `<strong>` for invisible text-decoration placeholders in step 1 — `<strong>` has default bold that gives the answer away.

**Answer lists.** Use `<p>` tags with hardcoded numbers — NOT Markdown `1.` / `2.` which renders as `<ol>` with gray list markers.

**Font minimums.** No text below 31px. Body 35px, headings 47px, phonemic script 47px.

**Text alignment.** Never add `h2{text-align:left!important}` style blocks or `<div style="text-align:left">` wrappers to slide body content. These override reveal.js's built-in text alignment and break F11 fullscreen scaling — the canvas miscalculates its height and the layout collapses. Let reveal.js handle alignment. Only use `text-align:left` on individual `<td>` cells where needed.

**Pattern reference.** Before writing any slide, study `PROJECTS/ARCHIVE/JULY 20 M3 VOCAB MOVIES/` for the proven table CSS pattern and reveal.js config.

**Slide text is authored verbatim.** Never compose displayed sentences programmatically in a builder script (f-string assembly, joins of clauses) — every string students see must be written out literally by the agent. Grammar errors in a deck are the signature of script-composed text. Demo ("Try it") slides use the teal `#116466` background (distinct from navy strategy slides), and correct-answer positions in demo checkmark tables must vary across demos — never always the first row.

**Generator scripts that share strings** (e.g. a transcript reused by two generators) must guard their render calls under `if __name__ == "__main__":` — otherwise importing them to share a constant triggers a side-effect render and a circular import. Define shared text once in the primary generator and import it.

**LLM-as-judge JSON is unreliable in shape.** deepseek-v4-flash mangles keys (`. __`-prefixed) and occasionally drops fields despite `response_format={"type":"json_object"}`. Normalize keys (`k.lstrip("._")`, `verdict`→`pass_fail`) and retry up to 3× on `model_validate()` failure — but keep Pydantic `model_validate()` as the sole acceptance gate. Never accept unvalidated judge output.

### Render

```bash
python ~/.agents/skills/slideshow-renderer/scripts/render.py \
  --data "PROJECTS/{name}/data.json" \
  --output "PROJECTS/{name}/slides/index.html"
python3 "PROJECTS/{name}/post-process.py"
```

Never stop the HTTP server. Python's `http.server` picks up changed files on each request.

### Validate

```bash
python3 ~/.agents/skills/slideshow-renderer/scripts/validate_slide_fonts.py "PROJECTS/{name}/data.json"
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

- **Banner images get clipped by the shared template.** The skill's `.ws-image img` rule is `max-height:5.5cm; object-fit:cover` — it centre-crops a 16:9 image by ~44%. To show the whole image edge-to-edge, pass `styles_override` (the FULL CSS string with the one rule changed to `width:100%; height:auto`). This replaces the entire stylesheet, so copy the project's working `STYLES` string rather than writing from scratch.
- **Assessment data lives in two Supabase tables.** `speaking_assessment_cambridge` holds grades + `pronunciation_feedback` but its `audio_url` is usually NULL. Speaking audio URLs and comments live in `student_submissions` — columns `url` + `speaking_pron_comment`. Drive URLs are usually **folder** links: download with `gdown --folder <id> -O <dir>`.
- Lint tests assert `EXPECTED_PAGES` — adding/removing sections changes the page count; update the test after a layout shift.

PDFs are gitignored (`PROJECTS/**/*.pdf`).

## Cue cards

Write a `generate_cue_cards.py` per project. Self-contained Playwright script:
- Generates HTML with embedded CSS, renders via Playwright to A4 PDF.
- One card per discussion topic, 4 per A4 page.
- Each card includes: numbered header, context/question, 4-step discussion structure (Open → Your view → Respond → Resolution), dot-pointed language hints (Agree / Disagree / Follow-up).
- Fonts: Roboto (installed via TinyTeX), embedded in PDF.

## Audio / monologs

- Fish Audio TTS. `FISH_API_KEY` is in the environment. `s2.1-pro-free` runs the **same model** as paid `s2.1-pro` — only TTFA/DPA guarantees differ, so the free tier is not a degraded engine.
- Cloned voices are logged in `cloned-voices/readme.md` with reusable voice IDs (e.g. `Patrick_Stewart` `134fbc5b…`, `Benedict_Cumberbatch` `2d3546b7…`, `Helen_Mirren` `6da4ca15…` (number announcer), `RCrowe-adult-Aus-celeb` `0f00fb73…`, `narrator` `f190f246…`, `london-boy` `311190e1…`). Reuse existing IDs; log every new clone.
- **Clone from REAL human audio** (15 s min, 45–60 s ideal) via `POST /api.fish.audio/model` fast mode. Voices cloned from synthetic design audio sound robotic (community-verified) — prefer clean real narration clips (e.g. audiobook excerpts).
- **NEVER apply fades (`afade`)** to generated audio: a fade-out starts before the last phoneme and cuts the final words. Trim trailing silence instead.
- **`silenceremove`'s `stop_periods` is BROKEN on this ffmpeg build** — it cuts into speech (a 10-word sentence trimmed to 1.6s). For edge-trim, detect boundaries with `silencedetect=noise=-40dB:d=0.08`, parse `silence_start`/`silence_end`, and cut with `-ss`/`-to` (leading silence ends at first `silence_end`; trailing starts at last `silence_start`).
- **TTS cannot "mispronounce".** To get a dropped-final-consonant version, feed a homophone respelling: `night`→`nigh`, `fight`→`fie`, `played`→`play`, `wanted`→`want`. Always audition respellings (vowel drift risk: `lahs` can read as `lass`).
- **TTS reads EVERY character — strip markdown before sending.** Fish Audio (and all TTS engines) read `**` as "asterisk asterisk", `#` as "hash", `_` as "underscore", `` ` `` as "backtick", and `[text](url)` as bracket-words. **Every text string MUST pass through `strip_markdown()` before reaching the TTS API.** Add a RED-GATE (`assert_no_markdown()`) that BLOCKS any call containing markdown artifacts — do not warn, raise an error. The `generate_audio.py` in LISTENING M3 has the reference implementation. Cost of getting this wrong: 48 TTS calls × API credits × full regeneration.
- **Generate each TTS sentence as ONE complete call — NEVER split into fragments.** Do NOT regex-split a sentence at commas/"and"/"but" and TTS each fragment separately, then glue with silence. That breaks prosody and creates word-cutoff artifacts (a fragment like "the key difference between trading..." spoken in isolation sounds truncated/robotic). Send the whole sentence to Fish in ONE call and let `chunk_length` handle internal phrasing; reuse the same file for a repeat hearing. Verify with `silencedetect` — speech blocks should be continuous (average 4-6s), not tiny 0.2s fragments. Reference: `generate_dictation()` in LISTENING M3 `generate_audio.py`.
- **Mid-sentence write pause = timestamp + ffmpeg, NOT fragmentation.** To give students time to write in the middle of a dictation sentence, generate the WHOLE sentence via `POST /v1/tts/stream/with-timestamp` (returns concatenated `audio_base64` + `alignment.segments[]` = word-level `{text,start,end}` on the full timeline; add `chunk_audio_offset_sec` for absolute time). Then use ffmpeg `atrim`+`concat` (filter_complex) to splice a 2.0s silence at the split word's `end`+pad. The sentence is recorded naturally ONCE and reused for both hearings. Verify the write pauses exist (16 × ~2.0s gaps for 8 questions × 2 hearings) with `silencedetect`. Reference: `tts_with_timestamps()` / `word_pause_time()` / `insert_pause_at()` in LISTENING M3 `generate_audio.py`.
- **Fish Audio mispronounces numerals — always spell them out.** `"Question 1."` reads as "Question Un"; write `"Question one."` instead. Use a `NUMBER_WORDS` map for any label/instruction text where a number must be spoken.
- **Phoneticise foreign/non-English names with CMU Arpabet tags.** Fish auto-detects language and reads unknown proper nouns how it likes — "Siam" can become "see-am", "Question 1." becomes French "Un". Pin the intended sound with `|<phoneme_start|>ARPABET<|phoneme_end|>` (English uses CMU Arpabet; one word per tag). Pipeline: `strip_markdown()` → `apply_pronunciations()` → `assert_no_markdown()`. Only tag genuinely foreign/ambiguous names (Siam `S AY1 AE2 M`, Mongkut `M AO1 NG K AH0 T`, Chulalongkorn, Nanking, Lin Zexu, Bowring) — never tag already-correct English words (China, Britain, India) or it sounds robotic. Reference: `pronounce.py` + `test_pronunciations.py` (19 GREEN) in the `fish-audio` skill; `apply_pronunciations()` wired into both `tts()` and `tts_with_timestamps()` in LISTENING M3 `generate_audio.py`.
- **Match audio loudness across a deck**: normalize each track with `loudnorm=I=-16:TP=-1.5:LRA=11` (I=-15/LRA=7 for quiet recordings) and verify with `ebur128` — all tracks should land within ~1 LU of each other.
- **Browsers cache mp3s at the same URL** — after re-processing an audio file, add `?v=N` to its `data-src` in data.json or listeners hear the old (quiet) version. (Do NOT version the timer-plugin.css link — see gotchas.)
- Natural prosody for read-along texts: `[long-break]`/`[break]` pause markers between paragraphs, `[emphasis]` on key terms, `temperature=0.8`, `prosody.speed≈0.93`, `chunk_length=300`. Embed the result in the slide body as `<audio controls data-src="assets/{file}.mp3">` (reveal.js lazy-loads `data-src` on show).

## Listening tapes on YouTube (auto-captions)

Classroom listening tapes are hosted on YouTube as unlisted videos so the player's
CC button auto-captions them. Use the **`youtube-audio-developer`** global skill
(`~/.agents/skills/youtube-audio-developer/`) — `scripts/upload.py` builds the mp4
(cover + audio), OAuth-uploads, adds to a playlist, and prints the video ID + embed.

- **Ask the user** for the mp3 path and cover image before uploading — the skill does
  not guess them.
- **Embed** with `?enablejsapi=1` so the deck can pause the player; use the
  `youtube-nocookie.com` host (privacy-enhanced). Add a pause-on-slidechange script
  (postMessage `pauseVideo`) or the audio keeps playing when the student advances.
- **Caption verification needs `youtube.force-ssl` scope**, not plain `youtube` —
  `captions().list` returns `Insufficient Permission` otherwise. The skill's `SCOPE`
  already lists both.
- **Auto-captions lag processing** — `uploadStatus: processed` only means the video is
  playable; the `asr` track can appear minutes-to-hours later, and **longer audio takes
  longer** (a 6-min tape lagged several hours here). If `--check-cc` returns 0 tracks
  for a `processed` video, keep the original and wait/re-check.
- **Never re-upload just because captions aren't ready** — it creates a duplicate video
  and usually fails identically. Re-check `--check-cc` over time first. Delete any
  accidental duplicate via `videos().delete(id=...)`.
- Video IDs are written to `PROJECTS/{name}/youtube/video_ids.json` and wired into
  `build_deck.py`'s `YT_IDS` map. Creditentials (`client_secret.json`, `token.json`)
  live in the skill's `creds/` dir, gitignored — never commit them.

## Lesson plan PDF workflow

Generate lesson plan PDFs via `write-lesson-plan` skill. Always follow these rules:

1. **Teacher is always "Ed Rush"; class time is always 46 minutes.** Both are built into the `write-lesson-plan` renderer defaults — never guess another teacher or duration, and stage times must sum to 46.
2. **Load lesson.json** — extract book name, unit number/title, page numbers for the materials list.
3. **Load transcript.json ONLY for listening lessons** — set `metadata.transcript` to the path. The renderer auto-converts JSON to `<strong>Speaker:</strong> text` format with boldfaced speaker names. Reading lessons (even with an audio read-along main task) must NOT include a transcript.
4. **Main aim = speaking/product, not vocabulary.** The main aim must reflect the lesson's real productive focus (discuss, present, debate, read, listen). Vocabulary is supporting content for a stage, not the main objective.
5. **Lead-in uses splash → title sequence.** Procedure step 1: show splash, let students speculate ("What do you see? Who are these people?"). Step 2: advance to title, confirm the theme.
6. **Materials list:** first item = full textbook details ("Oxford Discover Futures 3, Unit 6 ..., pp. 64–65") or the source article (publication + author) when there is no textbook. Then slideshow, cue cards, audio, worksheet.
7. **Answer keys:** sectioned by exercise (`<strong>Exercise 3 — Gist questions</strong>`), numbered by textbook, full sentences.
8. **No images in the lesson plan** — contextual images go in the slideshow.

```bash
python ~/.agents/skills/write-lesson-plan/scripts/render.py \
  --template lesson-plan \
  --data PROJECTS/{name}/envelope.json
```

**Output location:** lesson plan PDFs go to the repo-root `PDF/` directory (the renderer's default) — never inside `PROJECTS/{name}/`. Do not pass `-o` into a project folder.

Verify: `pdfinfo` confirms A4 (594.96 × 841.92 pts), `pdffonts` confirms embedded fonts.

## Before declaring done

1. Re-run post-processing (render wipes timer injections). Re-run it AFTER every render.
2. Verify slide order matches JSON array.
3. Check source fidelity against worksheets/transcripts.
4. Run `python3 -m pytest tests/ -v`.
5. If the deck has a timer plugin, confirm it loads before `Reveal.initialize()` (blank-white-page guard) and that timers are only on the intended slides.
6. Deploy is GATED — do NOT push gh-pages without explicit user OK. If deploying, `/git-pages` must confirm the remote MD5 matches local.
