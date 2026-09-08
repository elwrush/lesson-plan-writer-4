---
description: Back up this git repository to a GitHub remote — mirror an existing repo (exact copy, all refs) or publish a fresh working tree (init + commit + push).
---
# Command: GitHub Backup

Back up a git repository to a GitHub remote using the git CLI. Two modes —
**mirror** for an existing repository (exact copy, all refs), **publish** for a
local working tree that is not yet a repo (init + commit + push). Based on
current GitHub docs best practice (`git clone --mirror` + `git push --mirror`
preserves every branch and tag; a fresh local tree is published with
`git push --all --tags`).

## Usage

`/github-backup <owner>/<repo>` — backup the current directory's repo.
`/github-backup <repo> --source /path/to/dir` — backup a specific directory.
`/github-backup <repo> --private` (default) — create as private.
`/github-backup <repo> --public` — create as public.

## Steps

1. **Sanity-check for secrets first.** Grep the working tree for API keys/tokens
   (`.env`, `*_KEY=`, `gho_`, `sk-`, etc.) before anything goes to GitHub. Do
   not push `.env` or other secret-bearing files — confirm they are gitignored.
2. **Filter out binaries.** Never push binary files — no `.exe`, `.dll`, `.so`,
   `.dylib`, `.bin`, `.wasm`, `.class`, `.jar`, images/videos/audio
   (`.png`, `.jpg`, `.mp4`, `.mp3`, …), archives (`.zip`, `.tar`, `.gz`),
   or build artifacts (`.pyc`, `.o`, `.obj`, `.node_modules/`, `build/`,
   `dist/`, `target/`, `WORK/`, `__pycache__/`). Check what would be staged
   first (`git status --porcelain` / `git ls-files`); add anything binary to
   `.gitignore` (append `**/` globs if untracked) and abort with a warning if a
   binary is already tracked — ask the user before `git rm --cached`.
3. **Create the repo** (if it does not exist):
   `gh repo create <repo> --private|--public --source <dir> --remote origin`
4. **Publish a working tree** (not yet a repo):
   - `git init -b main && git add -A && git commit -m "Backup: <date>"`
   - `gh repo create <repo> --private|--public --source . --remote origin --push`
   - This pushes all branches and tags (`--push` does `--all` + `--tags`).
5. **Mirror an existing repo** (full history, exact copy):
   - `git clone --mirror <source-url> backup.git && cd backup.git`
   - `git remote set-url origin <new-repo-url> && git push --mirror origin`
6. **Verify the backup** (never skip):
   - `git remote -v` shows the GitHub remote.
   - `git ls-remote --heads --tags origin | wc -l` — refs count on the remote.
   - `git clone <new-repo-url> /tmp/<repo>-verify` then diff a sample file.
   - Confirm no binary files landed in the remote refs (`git ls-files` on the
     verify clone shows only text/source files).
7. Report the remote URL and confirm to the user that history + tags landed.

Remember the 3-2-1 rule: a single GitHub remote is not a backup on its own —
recommend at least one offsite copy (external drive, another host, or a mirror
tarball).

## Run

Requires `<owner>/<repo>` (the backup target). If the current dir is already a
git repo with remote `origin`, "back up" usually means one of:
- **mirror** the existing repo to a *new* private repo for an offsite copy, or
- the `git-backup` skill (`commit + push` the current uncommitted work to `origin`).

```bash
target="${1:-}"   # e.g. elwrush/lesson-plan-writer-4-backup
mode="${2:-mirror}"  # mirror | publish
vis="${3:-private}"  # private | public
```
