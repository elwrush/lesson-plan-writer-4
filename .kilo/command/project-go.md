# Command: project-go

## Usage
/project-go [description of what you want to do]

## What it does
Entry point for the lightweight spec kit. Reads project state and routes to the right workflow command.

## Execution Flow

1. **Detect state**:
   - Does `.spec/constitution.md` exist? If not, suggest creating one first (write it manually or ask the agent).
   - Scan `.spec/` for existing proposals. List them.
   - Read AGENTS.md for project context.

2. **Ask**: "What would you like to do?"
   - "Explore an idea" → route to `/explore`
   - "Create a proposal for [feature]" → route to `/propose`
   - "Implement [feature]" → route to `/implement`
   - "Verify [feature]" → route to `/verify`

3. **If user provided a description directly**: Route automatically — if it's vague, start with `/explore`; if it's specific, go to `/propose`.

## Constraints
- Read-only — do NOT create or modify any files during state detection
- Route to existing commands; do NOT reimplement their logic
