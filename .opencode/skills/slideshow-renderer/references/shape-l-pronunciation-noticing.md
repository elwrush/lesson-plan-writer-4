# Shape L — Pronunciation-Noticing Deck (reusable library)

Canonical deck for a noticing-first pronunciation lesson (final-consonant / plural -s).
Reference it instead of reinventing it. Worked examples:

- `PROJECTS/ARCHIVE/PRONUNCIATION NOTICING/data.json` — final /t/, /d/, /Id/
- `PROJECTS/PRON S_Z_IZ/data.json` — plural -s (/s/, /z/, /ɪz/)

## Slide sequence (reuse verbatim as a scaffold)

| # | id | layout | bg | Content |
|---|----|--------|----|---------|
| 1 | `splash` | `image` | image | Splash photo (`image_url` only). Ask the user for the theme image first. |
| 2 | `title` | `content` | image | Same photo + `logo` + `shield:true` + `background_image`. Rhetorical question + tagline. |
| 3 | `importance` | `content` | navy | "Why is this lesson important?" `<ul>` of real-world outcomes (never grammar labels). |
| 4 | `recall` | `content` | navy | Opening question that naturally elicits the feature ("What things do you have?"), with the `Opinion &mdash; Reason &mdash; Evidence` line underneath. |
| 5 | `transition-feature` | `content` | red | Name the feature ("Plural -s: /s/ /z/ /ɪz/"). |
| 6 | `strategy-notice` | `content` | navy | `Do/Why/How` table — Strategy: Notice ("Listen for the last sound of each word"). |
| 7 | `demo-notice` | `auto-animate-pair` | teal | "Try it". Model sentence (every target before a vowel/pause). Step 1 targets in `<span style="text-decoration:none">`, step 2 underline in yellow + count. |
| 8 | `listen-a` | `raw` | navy | Part A comparison track: `<audio controls data-src="assets/model-sentence-compare.mp3">` + "Tap on every final sound." |
| 9 | `answer-a` | `content` | green | 4-row table: how many target sounds (must match the count in the model sentence). |
| 10 | `transition-b`/`-c`/`-f` | `content` | red | "Worksheet, Part X" separators. |
| 11 | `listen-*` | `raw` | navy | Per-part discrimination audio (`<audio ... data-src="assets/partX-audio.mp3">`). |
| 12 | `answer-*` | `content` | green | 4-row table keyed to the AUDITED key (✓/✗ per item). Never guess. |
| 13 | `feature-rules` | `auto-animate-pair` | navy | **The rules presented with auto-animate.** Step 1 = condition column + "-s says" + empty `<span>&nbsp;</span>`; step 2 = the `/s/`, `/z/`, `/ɪz/` values + example word in yellow. |
| 14 | `listen-g` | `raw` | navy | Authentic student recording (e.g. the long `florence2.mp3`). "Tick or cross the numbered words." |
| 15 | `answer-g` | `content` | green | 4-row table with the audited key of the real recording. |
| 16 | `listen-h` | `raw` | navy | Model reading of the paragraph ("the model", not the voice name). |
| 17 | `wrap-up` | `content` | navy | Exit: "Say these with the ending." + recycling note in `notes`. |

## Key rules when writing a Shape L deck

- **Auto-animate the rules.** The `feature-rules` slide uses `auto-animate-pair` with
  DOM-identical tables that only change the value `<span>` content (empty `&nbsp;` →
  `/s/ books` etc.) and yellow-highlight the phonetic value. See "Auto-animate matching rules"
  in `SKILL.md`.
- **Model-sentence salience.** Every target consonant must sit before a vowel or a pause so
  natives audibly release it. Compare: "I have three **books**, two **dogs**, and four
  **glasses**." (released) vs "three books in ..." (reduced). This is a low-level design
  constraint — see the 4 rules in `SKILL.md` and `RESEARCH/pronunciation-noticing.md`.
- **Answer keys are audited, never generated.** The Part B/C/G tick/cross keys come from a
  teacher listening to the recording. Slides must reproduce those exact keys.
- **One `<audio>` element per listen slide** using `data-src` (reveal.js lazy-loads on show),
  `style="width:440px;margin:20px"`. Add `?v=N` to the audio URL only when the file changes
  (browsers cache same-URL mp3s).
- **Voice anonymity.** Slides say "This is the model", "Florence listens", etc. — never the
  celebrity/narrator voice name. Voice identities are teacher-facing only (lesson plan / notes).
