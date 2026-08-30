---
description: Create a feature proposal with spec and implementation tasks in one step. Produces .spec/{name}/proposal.md and .spec/{name}/tasks.md.
---
# Command: propose

## Usage
`/propose {feature-name}` — `$ARGUMENTS` is the feature name.

## What it does
Creates a feature proposal with spec and implementation tasks in one step. Produces two files:
`.spec/{name}/proposal.md` (what/why/done/constraints) and `.spec/{name}/tasks.md` (ordered checklist).

## Execution Flow

1. **Explain**: "Let me create a proposal for {name}. I'll ask a few questions, then generate the spec and tasks together."

2. **Gather context**: Read the project constitution (`.spec/constitution.md` if it exists), AGENTS.md, and relevant existing code.

3. **Ask clarifying questions** (max 3):
   - What are we building? (the WHAT)
   - Why is this needed? (the WHY)
   - How do we know it's done? (the DONE criteria)
   - What must NOT break? (the CONSTRAINTS)

4. **Create artifacts**:
   - Create `.spec/{name}/` directory
   - Write `proposal.md`:
     ```
     ## Proposal: {name}
     ## What
     ## Why
     ## Done
     ## Constraints
     ```
   - Write `tasks.md`:
     ```
     ## Tasks
     - [ ] T001 Setup/Research
     - [ ] T002 Core implementation
     - [ ] T003 Tests
     - [ ] T004 Polish edge cases
     ```

5. **Report**: "Created proposal at .spec/{name}/ with [N] tasks. Ready for /implement?"

## Constraints
- Max 3 clarifying questions
- Tasks must be dependency-ordered
- Keep proposal under one page
