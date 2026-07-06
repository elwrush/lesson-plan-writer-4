# Command: verify

## Usage
/verify {feature-name}

## What it does
Read-only completeness check. Compares proposal + tasks against actual code. Reports drift, missing coverage, unmet done criteria. Does NOT edit files.

## Execution Flow

1. **Explain**: "Running verification for {name}. I'll check spec against code. Nothing will be modified."

2. **Load context**: Read `proposal.md` and `tasks.md` from `.spec/{name}/`

3. **Check each dimension**:
   - Task completion: are all tasks marked `[X]`?
   - Done criteria: is each criterion from the proposal actually met in code?
   - Test coverage: do tests exist and pass?
   - Constraints: are any violated?

4. **Report**:
   ```
   ## Verification: {name}
   - Tasks: N/M complete
   - Done criteria: N/M met
   - Tests: passing/failing/none
   - Drift: [discrepancies]
   - Recommendations: [optional]
   ```

## Constraints
- Strictly read-only — no file modifications
- Report issues with specific file paths
