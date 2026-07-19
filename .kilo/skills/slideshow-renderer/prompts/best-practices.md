# Slide Design Best Practices

## Color-Coded Stages

Use stage-based colours consistently across the deck:

| Stage | CSS class | Hex | Purpose |
|-------|-----------|-----|---------|
| Warm-up / Lead-in | `stage-warmup` | `#f39c12` (orange) | Engagement, context-setting |
| Presentation | `stage-presentation` | `#3498db` (blue) | New language input |
| Controlled Practice | `stage-controlled` | `#2ecc71` (green) | Structured accuracy work |
| Freer Practice | `stage-freer` | `#9b59b6` (purple) | Less structured fluency |
| Production | `stage-production` | `#1abc9c` (teal) | Freer output task |

## One Concept Per Slide

- Never present two grammar points, vocabulary sets, or task types on one slide
- Exception: comparison slides (before/after, correct/incorrect) use auto-animate-pair

## Image Use

- Every content slide should have a supporting image where possible
- Images must be high-resolution, culturally appropriate for Thai students
- No clip art, no low-resolution photos, no watermarked images
- Image backgrounds should use `.shield` div for text readability

## Auto-Animate for Grammar

- Use `auto-animate-pair` for grammar transformations:
  - Word order changes (Subject + verb vs. Subject + have/has + verb)
  - Error → correction pairs
  - Sentence restructuring
- Do NOT use auto-animate for vocabulary (use one-word-per-slide with reveals)

## Font & Readability

- Body text: minimum 32pt on slides (no smaller)
- Headings: 40pt minimum
- High contrast: dark text on light background (WCAG AA minimum)
- No decorative fonts — use system sans-serif

## Speaker Notes

- Speaker notes (`notes` field) are for the teacher only
- Use for: CCQ answers, timing prompts, anticipated student errors, differentiation cues
- Do NOT put student-facing content in notes

## Lexical Control

- All text within Cambridge B1 PET wordlist
- Gloss any B2+ word: "The **consequences** (results) are serious."
- Maximum 25 words per content slide (Mayer's Coherence Principle)

## References

- WCAG 2.1 AA contrast minimum: 4.5:1 (normal text), 3:1 (large text)
- Cambridge English PET vocabulary profile: https://www.cambridgeenglish.org/images/22105-pet-vocabulary-list.pdf
