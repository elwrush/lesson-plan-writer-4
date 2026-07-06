# LESSON-PLAN-WRITER-4 Constitution

## Core Principles

### I. Spec-Driven Development
Every feature starts with a spec in `.specify/specs/`. No spec — no code. Specs focus on WHAT and WHY, not HOW.

### II. Structured-Data-First
The LLM emits structured data (Pydantic-validated JSON) with layout enums — never raw HTML or Jinja2 template syntax. Deterministic code (resolvers, macros) handles cross-slide attribute matching.

### III. Layered Pipeline
Three distinct layers with clear responsibility boundaries:
- **LLM layer**: selects layout from enum, fills content slots (markdown inside slots)
- **Resolver layer**: deterministic, assigns data-ids, fragment indices, cross-slide continuity
- **Render layer**: Jinja2 macros consume resolved data, call `slideshow_lib` for HTML generation

### IV. Red-Green TDD
Every code change must follow Red/Green TDD: write tests first, confirm FAIL, implement, confirm PASS. Tests are the gate.

### V. Pydantic Gate for JSON Output
Every JSON write to disk must pass through `BaseModel.model_validate()`. Every LLM call expecting JSON must use `response_format={"type": "json_object"}`.

### VI. Verify Before Done
Before declaring any feature complete, run `/speckit.converge` to detect drift between spec and implementation.

## Pipeline Constraints

- The library at `lib/slideshow_lib/` is read-only — never modified directly during feature implementation
- The resolver must never delegate data-id or fragment-index assignment to the LLM
- Each layout macro must be independently testable against known JSON input
- CDN-based reveal.js (jsDelivr) — no local copy of reveal.js

## Development Workflow

1. `/speckit.constitution` — establish/amend principles (one-time)
2. `/speckit.specify` — create feature spec
3. `/speckit.plan` — implementation plan with tech decisions
4. `/speckit.tasks` — dependency-ordered task list
5. `/speckit.implement` — build with Red/Green TDD
6. `/speckit.converge` — final drift check

### VII. Kilo Skills Compliance

Global skills MUST follow the Kilo Agent Skills format (`/mnt/c/PROJECTS/COMMON/writing-kilo-skills.md`):
- `SKILL.md` placed directly in the skill directory (e.g., `~/.kilo/skills/<name>/SKILL.md`)
- `name` in frontmatter MUST match the parent directory name
- `description` MUST be clear about when to use the skill (how users phrase requests)
- Use defined optional directories: `scripts/`, `references/`, `assets/`
- Additional directories (`templates/`, `tests/`) are permitted as extensions
- Tests are shipped inside the skill, not in a separate repo

## Governance

The constitution supersedes all other practices. Amendments require documenting the rationale and updating affected specs. Violations of layers III, IV, or VII block the PR.

**Version**: 1.1.0 | **Ratified**: 2026-07-06 | **Last Amended**: 2026-07-06
