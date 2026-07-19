---
name: git-backup
description: Commit and push code-only backup to origin main. Excludes slides (GitHub Pages), binaries, PDFs, and generated files. Codebase-only backup.
license: MIT
---

# Skill: git-backup

## Purpose

Stage all safe changes, generate a descriptive commit message, commit to main, push to origin, then verify the backup succeeded. Code-only — no slides, no binaries, no generated PDFs.

## Rules

- **No force push** (`--force`, `--force-with-lease`) without explicit user approval.
- **Empty commits** are never allowed. If nothing changed, inform the user.
- **No binary or generated files**: Slides go to GitHub Pages, PDFs are outputs, assets are not source code. Exclude via `.gitignore`.
- **Secrets**: Always exclude `.env`, `.env.*`, `*.key`, `*.pem`, `credentials*`.
- **Commit message** follows Conventional Commits: `<type>(<scope>): <description>` then blank line then bullet list.

## Agent workflow

### Step 1 — Health check
```bash
git status --short
git log --oneline -5
git remote -v
```

Exit if clean. Warn if no remote.

### Step 2 — Diff review
```bash
git diff --stat
git diff --stat --staged
```

### Step 3 — Stage safe files
```bash
git add -A
```

### Step 4 — Draft commit message
Format:
```
<type>(<scope>): <subject>

- <file>: <what changed and why>
```

Types: `feat`, `fix`, `refactor`, `chore`, `docs`, `test`.

Present to user with options: `Approve`, `Edit`, `Cancel`.

### Step 5 — Commit & push
```bash
git commit -F /tmp/commit_msg.txt
git push 2>&1 || git push -u origin $(git rev-parse --abbrev-ref HEAD) 2>&1
```

### Step 6 — Verify
```bash
git rev-parse HEAD
git status --short
```

Report: commit hash, branch, files changed, remote status.
