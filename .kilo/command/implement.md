# Command: implement

## Usage
/implement {feature-name}

## What it does
Executes tasks from `.spec/{name}/tasks.md`. Follows red-green TDD: write tests first, confirm FAIL, implement, confirm PASS.

## Execution Flow

1. **Explain**: "Starting implementation for {name}. I'll work through each task in order."

2. **Load context**: Read `proposal.md` and `tasks.md` from `.spec/{name}/`

3. **Execute tasks one by one**:
   - Announce: "Starting task [ID]: [description]"
   - Write tests first
   - Confirm tests FAIL (red phase)
   - Implement the code
   - Confirm tests PASS (green phase)
   - Mark task `[X]` in tasks.md

4. **Between tasks**: Pause and ask for input if the next step needs a design decision.

5. **Completion**: "All [N] tasks complete. Ready for /verify?"

## Constraints
- Red-green TDD: every code change has a test that fails first
- Mark each completed task in tasks.md immediately
- Pause for user input on design decisions
