# Command: Git Backup

## Usage
`/git-backup`

Stages all changes, generates a categorised commit message, commits to a backup branch (`backup/YYYY-MM-DD-HHMM`), and pushes to origin. All changes are committed — no prompting for individual files.

## Prerequisites
- `gh` CLI authenticated
- Git remote `origin` configured
- Working tree has changes (otherwise stops)

## Safety
**This command pushes to a timestamped backup branch on `origin`.** It does NOT touch `main`. The commit message is presented for confirmation before committing.

## Workflow

### Step 1: Check working tree
```bash
git status
```
If "nothing to commit, working tree clean" — stop.

### Step 2: Run pre-commit checks (optional)
```bash
uv run python -m pytest tests/ -q
```
If tests fail, ask whether to continue or abort.

### Step 3: Stage everything
```bash
git add -A
```

### Step 4: Show staged diff summary
```bash
git diff --cached --stat
```

### Step 5: Build commit message
Categorise changed files from `git diff --cached --name-status` into:
- **Lesson shapes** — `LESSON-SHAPES/`
- **Spec/plans** — `.specify/`
- **Skills/commands** — `.kilo/`
- **Config/docs** — `AGENTS.md`, `README.md`, `*.md` (root)
- **Output** — `PDF/`, `PLANS/`

Subject line: `backup/{timestamp} — {brief description}`

### Step 6: Create backup branch
```bash
timestamp=$(date +%Y-%m-%d-%H%M)
branch="backup/$timestamp"
git checkout -b "$branch"
```

### Step 7: Confirm with user
Display the message. Ask `Commit and push to $branch? (Y/n)`:
- **Y** or empty — commit and push
- **N** — abort, `git reset HEAD .`

### Step 8: Commit and push
```bash
git commit -F /tmp/commit-msg.txt
git push origin "$branch"
```

### Step 9: Return to main
```bash
git checkout main
```

### Step 10: Report
```bash
echo "Pushed to origin/$branch"
```

## Edge cases
- **Nothing to commit** — stop before staging
- **Test failures** — ask user; they can continue or abort
- **Push rejected** — print error; local commit is preserved on the backup branch
- **Custom message** — user can provide their own

## Examples

### Full backup
```
/git-backup
```
Stages, creates backup branch, generates message, confirms, commits, pushes, returns to main.
