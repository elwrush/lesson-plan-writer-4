## Proposal: TEST — Present Perfect for Thai Middle Schoolers

## What
A validation slideshow that proves the slideshow-renderer pipeline end-to-end. Content: 10-slide reveal.js deck teaching Present Perfect Simple (experience/ever-never) to Thai middle schoolers at A2–B1 level.

## Lesson scope
- **Grammar target**: Present Perfect Simple — "Have you ever...?" / "I have / haven't"
- **Lexical theme**: Real experiences — travel, food, school, hobbies
- **Level**: A2–B1 (Thai middle school, approximately Mattayom 1–3)
- **Slide count**: 10 slides covering warm-up → presentation → controlled practice → freer practice → production
- **CEFR alignment**: B1 Preliminary (PET) vocabulary profile, conversational ESL voice

## Slides structure
| # | Stage | Content |
|---|---|---|
| 1 | Warm-up | Lead-in image + "Have you ever...?" question |
| 2 | Presentation | Form: have/has + past participle |
| 3 | Presentation | Meaning: life experiences (ever/never) |
| 4 | Presentation | Auto-animate: affirmative → negative → question |
| 5 | Controlled practice | Gap-fill: choose have/has + correct participle |
| 6 | Controlled practice | Reorder: sentence scramble |
| 7 | Freer practice | Pair work: ask your partner |
| 8 | Freer practice | Report back: "She has..." / "He hasn't..." |
| 9 | Production | Writing: three true experiences, one lie |
| 10 | Wrap-up | Review + exit ticket |

## Why
- Validate every component of the slideshow-renderer skill: prompts, library, render script, deploy
- Prove the pipeline works with real ESL content before using it for production lesson plans
- Catch any edge cases in the color-coded staging, auto-animate grammar comparison, speaker notes, CDN skeleton

## Done
- `PROJECTS/TEST/data.json` exists with all 10 slides
- `PROJECTS/TEST/template.jinja2` exists using slideshow_lib functions (slide_bg, slide_transition, fragment, auto_animate_pair, notes filter)
- `python render.py template.jinja2 data.json --output slides/index.html` succeeds
- `slides/index.html` is valid HTML with reveal.js from CDN
- `/git-pages TEST PROJECTS/TEST/slides` succeeds
- Live URL loads and all 10 slides display correctly

## Constraints
- Content must follow ESL voice prompts (esl-voice.md, best-practices.md)
- Thai L1 only in speaker notes, never on projected slides
- Images not required for this test (placeholder URLs or omit)
- All text within Cambridge B1 vocabulary profile
