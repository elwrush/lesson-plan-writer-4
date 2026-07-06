# Quickstart: Layout-Driven Slides

## Setup

```bash
# Install the markdown library for content slot rendering
uv add markdown
```

The remaining code adds to the existing pipeline.

The library at `~/.kilo/skills/slideshow-renderer/lib/slideshow_lib/` is read-only. All feature code goes in:

| File | Purpose |
|------|---------|
| `scripts/render.py` | Updated — gains resolver step + macro dispatch |
| `scripts/macros.jinja2` | New — one macro per layout type |
| `scripts/tests/test_render.py` | Updated — resolver tests + macro tests |
| `SKILL.md` | Updated — prompts tell LLM to emit structured data only |

## Running Tests

```bash
# Resolver + macro tests (in scripts/ dir)
cd ~/.kilo/skills/slideshow-renderer/scripts
python -m pytest tests/ -v

# Library tests (unchanged)
cd ~/.kilo/skills/slideshow-renderer/lib
python -m pytest slideshow_lib/tests/ -v

# Git-pages safety tests (in project root)
cd /mnt/c/PROJECTS/LESSON-PLAN-WRITER-4
python -m pytest tests/ -v
```

## Rendering a Test Deck

```bash
cd PROJECTS/TEST
python ~/.kilo/skills/slideshow-renderer/scripts/render.py data.json --output slides/index.html
# Or with inline data: scripts/render.py takes a JSON file
```

## Preview

```bash
cd PROJECTS/TEST/slides
python -m http.server 8080
# Open http://localhost:8080/
```

## Verification Scenarios

1. **LLM produces structured data only**: The template never appears in LLM output. All LLM output is `{layout, id, step, title, body, ...}` JSON.
2. **Cross-slide attributes are correct**: For every auto-animate pair, the resolver assigns matching `data-id` and `auto-animate-group-id`. Verified by test.
3. **Fragment indices are sequential**: Running total across the deck. Verified by test.
4. **Existing tests pass**: All 100 library tests + 5 render tests + 8 git-pages tests continue passing.

## Deploy

```bash
/git-pages TEST
```
