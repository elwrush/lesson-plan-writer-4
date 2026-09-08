---
description: Deploy or update a single slideshow on gh-pages (isolated worktree, MD5-verified). Dispatches to scripts/deploy_pages.py.
---
# Command: Git Pages

## Usage
`/git-pages [name] [source-dir]`

`name` = the subfolder on gh-pages (spaces → underscores). `source-dir` defaults to
`PROJECTS/{name}/slides`. If `name` is omitted you are prompted. Quote paths with spaces:
`/git-pages "Reading M2" "PROJECTS/Reading M2/slides"`.

**New deploy** = subfolder not yet on gh-pages; **Update** = already there. Detect it
automatically — never ask.

## Single implementation
This command is a thin dispatcher to the shared **`scripts/deploy_pages.py`** (the same
code behind the `just git-pages` recipe). It:

1. Detects NEW vs UPDATE by checking the `gh-pages` branch
2. Stages a copy of the deck
3. Sparse-clones `gh-pages` into an **isolated temp worktree** (main branch untouched)
4. Drift-checks (skips if the subfolder already matches)
5. **Builds the landing page from the git tree** (not `os.listdir` on a sparse clone —
   that bug silently dropped presentations)
6. Commits, pushes to `old-origin` (falls back to `origin`), and **verifies the pushed
   files back by MD5** (mandatory — never trust a bare push)
7. Cleans up and prints the URL

## Why a script (ADR 0006)
The previous inline command built the landing page with `os.listdir()` on a **sparse**
clone, which missed presentations that weren't materialised, and its sparse cone
(`*/index.html`) never tracked the ROOT `index.html`, so the landing update silently
never committed. `deploy_pages.py` fixes both and centralises the fragile sequence.

## Run
```bash
orig="${1:-}"
if [ -z "$orig" ]; then read -r -p "Enter subfolder (e.g. TEST): " orig; fi
src="${2:-PROJECTS/$orig/slides}"
python3 scripts/deploy_pages.py "$orig" "$src"
```
