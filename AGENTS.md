# LESSON-PLAN-WRITER-4

Data-only repository: pedagogical lesson shape templates consumed by the lesson plan writer pipeline.

## Layout

- `LESSON-SHAPES/shape-{a..g}.json` — 7 JSON files, each defining a lesson shape (pedagogical model) with `name`, `description`, `pedagogical_justification`, `main_aim_format`, and an `example_lesson_plan` containing ordered `stages`.
- `PLANS/` — output directory for generated lesson plans (empty).

## Shape map

| File | Model | Notes |
|------|-------|-------|
| A | Text-based Presentation | Context via text → clarify MFP → practice |
| B | Language Practice | Follow-on from A or C; controlled → freer |
| C | Test-Teach-Test | Diagnostic test → clarify gaps → practice |
| D | Situational Presentation (PPP) | Context → present MFP → controlled → freer |
| E | Receptive Skills | Sub-skills practice (gist/detail). See also Shape H. |
| F | Productive Skills | Preparation → speaking/writing output. See also Shape J. |
| G | Task-Based Learning (TBL) | Task → report → analyze → practice |

## Schema

Every shape JSON has a fixed top-level schema:
- `name`, `description`, `pedagogical_justification` (strings)
- `main_aim_format` (string with template placeholder like `[target language]`)
- `example_lesson_plan.header` (HTML string with `<br>` separators)
- `example_lesson_plan.stages` (array of `{stage, stage_number, stage_aim, procedure, time, interaction}`)

Cross-references exist between shapes (B depends on A/C; E → H; F → J) — preserve these when adding or modifying shapes.

## Pipeline context

This repo is part of the LESSON-PLAN-WRITER family. Shapes are consumed by a separate code pipeline (located outside this repo) that generates lesson plans using these JSON definitions combined with other inputs. Do not add build, test, or runtime config here.

## Workflow commands

4 lightweight spec kit commands in `.kilo/command/`:

| Command | What it does |
|---------|-------------|
| `/explore` | No-stakes brainstorming. Asks questions, reads code, shapes an idea. No files created. |
| `/propose {name}` | Creates `.spec/{name}/proposal.md` (what/why/done/constraints) + `tasks.md` (ordered checklist) in one step. |
| `/implement {name}` | Executes tasks from `.spec/{name}/tasks.md` with red-green TDD. |
| `/verify {name}` | Read-only completeness check. Compares spec + tasks against actual code. No edits. |

These are generic and can be copied to any project.
