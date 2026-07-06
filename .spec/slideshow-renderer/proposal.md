## Proposal: slideshow-renderer

## What
A reusable Kilo skill for generating and deploying reveal.js slideshows. The skill packages:
- **Library** (already built): `~/.kilo/skills/slideshow-renderer/lib/slideshow_lib/` — 23 Jinja2 functions wrapping reveal.js data-attributes/HTML patterns
- **SKILL.md**: instructions for the LLM on how to produce slideshows using the library
- **Prompts**: ESL authorial voice guide + best practice principles for Thai A2–B1 slide design
- **Render script**: merges LLM-authored Jinja2 template + data JSON → standalone `index.html`
- **Deploy command** (`.kilo/command/git-pages.md`): pushes rendered slideshows to GitHub Pages via isolated git worktree (ported from LPW-3)

## Pipeline

```
Agent loads skill ──► reads prompts (voice + best practices)
    │
    ▼
Writes slideshow_data.json       Writes slideshow_template.jinja2
  (slide content, metadata)        (structure, calls slideshow_lib)
    │                                      │
    └──────────┬───────────────────────────┘
               ▼
       render.py template.jinja2 data.json
               │
               ▼
        slides/index.html
      (CDN-based reveal.js)
               │
               ▼
       /git-pages {name}
               │
               ▼
        github.io/{repo}/{name}/
```

### Key design decisions
1. **LLM writes both template + data** — every slideshow gets a fresh `.jinja2` tuned to its content, rather than a fixed one-size-fits-all template
2. **Output: single `index.html` with reveal.js loaded from jsDelivr CDN** — zero build step, no vendored reveal.js, deployable as a single file to GitHub Pages
3. **ESL voice enforced at two levels**: prompts (`prompts/esl-voice.md`) define the authorial tone; template structure encodes best practices (text density, color-coded stages, image slots)
4. **Deploy**: git shallow clone of `gh-pages` branch to an isolated temp directory — never touches the main working tree

## Why
- The slideshow library is built and tested but has no pipeline for consuming it — it's a box of functions with no process
- ESL slide design is a specialized skill (font size, text density, color contrast, lexical control) that needs to be captured in prompts so the LLM doesn't guess
- GitHub Pages is the target but there's no repeatable deploy workflow for LPW-4
- LPW-3 has a working `/git-pages` command that can be adapted rather than built from scratch

## Preconditions (already met)
- Library at `~/.kilo/skills/slideshow-renderer/lib/slideshow_lib/` with `setup_jinja(env)` — 23 functions, 100 tests passing
- Library importable via `sys.path.insert(0, expanduser("~/.kilo/skills/slideshow-renderer/lib"))`
- Ruff 0.15.20 installed globally, configured as LSP in `~/.config/kilo/kilo.jsonc`

## Done
- `~/.kilo/skills/slideshow-renderer/SKILL.md` exists with YAML frontmatter (`name: slideshow-renderer`) and instructions covering the full pipeline
- `~/.kilo/skills/slideshow-renderer/prompts/esl-voice.md` exists — captures conversational ESL tone, lexical control (A2–B1), sentence length rules, Mayer's principles
- `~/.kilo/skills/slideshow-renderer/prompts/best-practices.md` exists — slide design rules (font sizes, text density, color-coded stages, image requirements, auto-animate for grammar, speaker notes conventions)
- `~/.kilo/skills/slideshow-renderer/references/slideshow_lib-quickref.md` exists — documents all 23 functions with call signatures and output examples
- `~/.kilo/skills/slideshow-renderer/scripts/render.py` exists — CLI that accepts `template.jinja2` + `data.json` and writes `index.html` with CDN-reveal.js skeleton
- `.kilo/command/git-pages.md` exists — ported from LPW-3, adapted for LPW-4's project layout
- `PROJECTS/TEST/` exists — validation project (Present Perfect for Thai middle schoolers) built end-to-end
- End-to-end flow verified: content.json → template → render → deploy → live URL

## Constraints
- Library code lives at `~/.kilo/skills/slideshow-renderer/lib/` — do not move or duplicate
- Library functions are read-only (already built and tested); the skill scripts consume, not modify them
- Output is single `index.html` with reveal.js from CDN — no local reveal.js vendoring
- All LLM calls use `response_format={"type": "json_object"}` where applicable
- All JSON output validated via Pydantic `model_validate()` before writing
- Deploy command NEVER switches branches in main working tree — uses `git clone --depth 1` to isolated temp directory
- ESL voice prompts must reference research sources (Mayer, Cambridge, CEFR) — not invented
