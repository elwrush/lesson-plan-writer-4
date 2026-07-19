---
description: Deploy or update a single slideshow on gh-pages. Detects whether the subfolder already exists and acts accordingly.
---
# Command: Git Pages

## Usage
`/git-pages [name] [source-dir]`

If `name` is omitted, you will be prompted for one. If `source-dir` is omitted, defaults to `slides/`.

**IMPORTANT: If source-dir contains spaces, you MUST quote it:**
`/git-pages "My Name" "path/with spaces/slides"`

**New deploy** = the subfolder does NOT exist on gh-pages yet. Creates the gh-pages branch if needed.

**Update** = the subfolder ALREADY exists on gh-pages. Overwrites files, regenerates landing page, pushes.

**Do NOT ask the user whether to deploy or update — detect it automatically.**

## What it does
1. Scans `{source-dir}/index.html` for the requested slideshow
2. Warns if not found and stops
3. Detects new deploy vs update by checking gh-pages branch
4. Runs fast lint (ruff)
5. Copies slides to a temp staging directory
6. Shallow clones `gh-pages` branch to an isolated temp directory
7. Drift check — compares staging vs deployed; skips if identical
8. Copies the slideshow into its own subfolder
9. Regenerates the root `index.html` (card grid)
10. Commits from worktree (aborts if nothing changed)
11. Pushes to remote and **verifies by fetching back + MD5 checksum**
12. Removes the worktree — main branch is never touched
13. Prints the URL

**Critical: Step 11 (push verification) is mandatory. Do NOT skip it. The AI must confirm the remote file matches the local source — otherwise the push was hallucinated.**

## Safety
**This command NEVER switches branches in the main working tree.** All gh-pages operations happen inside a `git clone --depth 1` — a separate directory that acts as an independent checkout. If anything fails, the main project directory is completely untouched.

## Regression Guard
A red-green safety test at `tests/test_git_pages_safety.py` (8 tests) scans this command file for forbidden patterns. It FAILS if any of these are re-introduced:
- `git checkout gh-pages` — direct branch switch in the working tree
- `git rm -rf .` — destroys tracked files
- `git clean -fd` — destroys untracked files globally
- Missing `git clone --depth 1` — no worktree isolation
- Missing `git -C $worktreeDir` — worktree isolation not in use

Run: `python -m pytest tests/test_git_pages_safety.py -v`

## Prerequisites
- `gh` CLI installed and authenticated (`gh auth status`)
- A source directory containing `index.html`
- Remote `origin` is a GitHub repo

## Workflow

### Step 0: Detect the target and determine deploy vs update
```bash
name="$1"
shift
source_dir="${*:-slides}"

if [ -z "$name" ]; then
  read -r -p "Enter the subfolder to deploy (e.g. TEST): " name
fi

# Resolve to absolute path so relative paths with spaces work
source_dir="$(realpath -q "$source_dir" 2>/dev/null || echo "$source_dir")"

slides_html="$source_dir/index.html"
if [ ! -f "$slides_html" ]; then
  echo "ERROR: No slideshow found at $slides_html"
  echo "Usage: /git-pages <name> [source-dir]"
  exit 1
fi

# Pre-flight summary
echo "=== Deploy Pre-flight ==="
echo "  Subfolder: $name"
echo "  Source:    $slides_html"

presentations=("$name")

# Detect new deploy vs update
git fetch origin gh-pages 2>/dev/null || true
if git ls-tree --name-only origin/gh-pages 2>/dev/null | grep -q "^${name}$"; then
  echo "  Action:    UPDATE (existing on gh-pages)"
else
  echo "  Action:    NEW DEPLOY (first time on gh-pages)"
fi
```

### Step 1: Check prerequisites
```bash
if ! gh auth status 2>&1 | grep -q "Logged in"; then
  echo "ERROR: gh CLI not authenticated — run 'gh auth login' first"
  exit 1
fi
```

### Step 2: Detect remote
```bash
remote_url=$(git remote get-url origin)
if [[ $remote_url =~ github\.com[:\/](.+)/(.+)\.git ]]; then
  owner="${BASH_REMATCH[1]}"
  repo="${BASH_REMATCH[2]}"
else
  echo "ERROR: Remote origin is not a GitHub repo"
  exit 1
fi
```

### Step 3: Fast lint
```bash
python -m ruff check --fix . 2>/dev/null || true
```

### Step 4: Copy slides to staging temp directory
```bash
staging=$(mktemp -d /tmp/gh-pages-staging-XXXXXX)
for p in "${presentations[@]}"; do
  mkdir -p "$staging/$p"
  cp -r "$source_dir/"* "$staging/$p/"
  echo "  Copied $p to staging"
done
```

### Step 5: Shallow clone gh-pages
```bash
worktreeDir=$(mktemp -d /tmp/gh-pages-worktree-XXXXXX)
if git clone --branch gh-pages --single-branch --depth 1 "https://github.com/$owner/$repo.git" "$worktreeDir" 2>/dev/null; then
  echo "  Cloned existing gh-pages branch"
else
  echo "  gh-pages branch does not exist yet — starting fresh"
  rm -rf "$worktreeDir"
  mkdir -p "$worktreeDir"
  git -C "$worktreeDir" init
  git -C "$worktreeDir" checkout --orphan gh-pages
fi
```

### Step 5a: Drift check — skip deploy if unchanged
```bash
deployed="$worktreeDir/$name"
if [ -d "$deployed" ]; then
  if diff -rq "$staging/$name" "$deployed" >/dev/null 2>&1; then
    echo "  No changes detected — slides are identical to gh-pages. Nothing to deploy."
    rm -rf "$staging" "$worktreeDir"
    exit 0
  else
    echo "  Changes detected — proceeding with deploy."
  fi
else
  echo "  New subfolder — no drift check needed."
fi
```

### Step 6: Copy the current slideshow into the clone
```bash
for p in "${presentations[@]}"; do
  mkdir -p "$worktreeDir/$p"
  cp -r "$staging/$p/"* "$worktreeDir/$p/"
  echo "  Deployed $p"
done
```

### Step 7: Generate/update root landing page
```bash
python3 -c "
import os, re

worktree = os.environ.get('worktreeDir', '$worktreeDir')
# List all subdirectories
slide_dirs = []
for entry in os.listdir(worktree):
    if os.path.isdir(os.path.join(worktree, entry)) and entry != '.git':
        slide_dirs.append(entry)
slide_dirs.sort()

cards = []
for d in slide_dirs:
    idx_path = os.path.join(worktree, d, 'index.html')
    title = d
    if os.path.exists(idx_path):
        with open(idx_path, encoding='utf-8', errors='replace') as f:
            content = f.read()[:5000]
        m = re.search(r'<title>\s*(.*?)\s*</title>', content, re.DOTALL)
        if m:
            t = m.group(1).strip()
            if t.lower() not in ('slides', 'presentation', ''):
                title = t
    cards.append(f'<a href=\"{d}/\" class=\"card\"><div class=\"card-title\">{title}</div></a>')

landing = f'''<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
    <title>Slides</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: system-ui, sans-serif; background: #f0f2f5; min-height: 100vh; display: flex; flex-direction: column; align-items: center; padding: 60px 20px; }}
        h1 {{ font-size: 2.2em; color: #1a1a2e; margin-bottom: 40px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; max-width: 960px; width: 100%; }}
        .card {{ background: white; border-radius: 12px; padding: 28px 24px; text-decoration: none; color: #333; box-shadow: 0 2px 8px rgba(0,0,0,0.08); transition: transform 0.2s; display: flex; flex-direction: column; }}
        .card:hover {{ transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0,0,0,0.12); }}
        .card-title {{ font-size: 1.15em; font-weight: 600; color: #1a1a2e; }}
        footer {{ margin-top: 50px; font-size: 0.85em; color: #aaa; }}
    </style>
</head>
<body>
    <h1>Slides</h1>
    <div class=\"grid\">
        {chr(10).join(cards)}
    </div>
    <footer>{len(slide_dirs)} presentations</footer>
</body>
</html>'''

with open(os.path.join(worktree, 'index.html'), 'w', encoding='utf-8') as f:
    f.write(landing)
print(f'Landing page generated — {len(slide_dirs)} presentations')
"
```

### Step 8: Commit from worktree
```bash
date_str=$(date +%d%m%y)
git -C "$worktreeDir" add -A
if ! git -C "$worktreeDir" diff --cached --quiet; then
  commit_hash=$(git -C "$worktreeDir" commit -m "Deploy $name ($date_str)" | grep -oP '[0-9a-f]{7,}' | head -1)
  echo "  Committed: $commit_hash"
else
  echo "  Nothing to commit — deploy cancelled."
  rm -rf "$staging" "$worktreeDir"
  exit 0
fi
```

### Step 8a: Push and verify
```bash
echo "  Pushing to gh-pages..."
if ! git -C "$worktreeDir" push origin HEAD:gh-pages 2>&1; then
  echo "ERROR: Push failed. Worktree left at $worktreeDir for recovery."
  exit 1
fi
echo "  Push accepted."

# Verify by fetching the deployed file back and comparing checksum
git fetch origin gh-pages 2>/dev/null || true
deployed_content=$(git show origin/gh-pages:"$name/index.html" 2>/dev/null | md5sum | cut -d' ' -f1)
local_content=$(md5sum "$source_dir/index.html" | cut -d' ' -f1)
if [ "$deployed_content" = "$local_content" ]; then
  echo "  VERIFIED: remote file matches local source (MD5: $local_content)"
else
  echo "ERROR: Remote file does NOT match local source!"
  echo "  Local:  $local_content"
  echo "  Remote: $deployed_content"
  echo "  Worktree left at $worktreeDir for investigation."
  exit 1
fi
```

### Step 9: Clean up worktree
```bash
rm -rf "$staging" "$worktreeDir"
echo "Worktree removed. Still on main."
```

### Step 10: Print URL
```bash
echo ""
echo "Deployed: $name"
echo "  https://$owner.github.io/$repo/$name/index.html"
echo ""
echo "Landing page: https://$owner.github.io/$repo/"
```

## Edge cases
- **No argument**: prompts interactively for the subfolder name
- **Not found**: lists error and exits
- **New deploy vs update**: detected automatically in Step 0
- **No changes detected**: drift check (step 5a) compares local slides vs gh-pages; skips commit/push if identical
- **First deploy (gh-pages branch doesn't exist)**: uses `git init --orphan` in isolated temp directory
- **gh not authenticated**: aborts with instruction to run `gh auth login`
- **Push fails**: worktree is left on disk for manual recovery; prints error
- **Landing page**: regenerated each time, listing ALL presentations on gh-pages
