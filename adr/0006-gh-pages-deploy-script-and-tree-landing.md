---
title: Centralise gh-pages deploy in a script and build the landing page from the git tree
status: accepted
date: 2026-09-08
deciders: Ed Rush
---

# Centralise gh-pages deploy in a script and build the landing page from the git tree

## Context
The `/git-pages` opencode command deployed slideshows to `gh-pages` on `old-origin`
(elwrush/lesson-plan-writer). Its inline shell had two latent bugs that surfaced on the
Reading M2 deploy:

1. **Landing page built with `os.listdir()` on a SPARSE clone.** The clone used a
   `--filter=blob:none --sparse` cone of `*/index.html`, so only materialised folders
   appeared in the worktree. Presentations whose `index.html` was not materialised were
   silently omitted from the regenerated root `index.html` — it missed `READING_M2` and
   `READING_LESSON_FLUENCY`.
2. **The sparse cone never tracked the ROOT `index.html`.** `*/index.html` matches
   one-level subfolders only, not the repo-root `index.html`. So the regenerated landing
   page was written but `git add -A` did not stage it, and the update silently never
   committed — leaving a stale landing page.

A third pain point: the command's argument parsing misfired on invocation, passing
`name="and"` and a prose string as the source dir.

## Decision
Replace the inline command body with a **single shared implementation,
`scripts/deploy_pages.py`**, and make both the `/git-pages` opencode command and the new
**`just git-pages`** recipe dispatch to it. The script:

- **Enumerates presentations from the git tree** (`git ls-tree` + `git show <blob>`), not
  `os.listdir()` on the worktree — so every presentation `dir/index.html` on `gh-pages`
  appears in the landing page, including the just-deployed one (read from the staging copy
  when it is not yet on the branch).
- Uses a sparse cone that tracks **both** the root `/index.html` and the deployed
  subfolder's full file tree, so neither the landing update nor the deck's asset files are
  silently dropped.
- Keeps **all** gh-pages operations inside an isolated temp `git clone --depth 1` worktree;
  the main working tree/branch is never touched.
- Verifies the pushed files back by **MD5** (deck `index.html` and root landing
  `index.html`) — mandatory, never trust a bare push.
- Detects NEW vs UPDATE automatically and drift-checks (skips when already identical).

`just git-pages "READING M2"` → `scripts/deploy_pages.py "READING M2" "PROJECTS/READING M2/slides"`.

## Consequences

**Good:**
- Landing page is always complete (all presentations listed), fixing both bugs.
- One implementation, so `/git-pages` and `just git-pages` can't drift apart.
- Deterministic args (the garbled `name="and"` failure is gone); `just` supplies the
  folder via `PROJECTS/{name}/slides`.
- Deploy remains additive-safe and MD5-verified.

**Bad / cost:**
- A real push to the live gh-pages site; only run when publishing (same as before, but now
  the recipe makes it easy to invoke quickly).
- The script duplicates some git plumbing that used to live inline.

**Risks / follow-ups:**
- GitHub Pages serves a stale root landing page for a while after a push (edge CDN cache);
  the deck subfolder appears immediately, the landing card lags a few minutes.
- Keep `tests/test_git_pages_safety.py` passing: the command file must not re-introduce
  `git checkout gh-pages`, `git rm -rf .`, `git clean -fd`, and the clone must keep
  `--depth 1` + `-C $worktreeDir`.
- The sparse cone pattern `'/index.html' '*/index.html' {name}/` is the current working
  set; if the branch layout changes, revisit the cone so the root and subfolder assets
  still get staged.
