#!/usr/bin/env python3
"""gh-pages slideshow deploy — the single implementation behind `just git-pages`
and the `/git-pages` opencode command.

Why this exists (ADR 0006): the old command built the root landing page with
`os.listdir()` on a *sparse* clone, which silently dropped presentations that
were not materialised (it missed READING_M2 and READING_LESSON_FLUENCY), and its
sparse cone `*/index.html` never tracked the ROOT index.html so the landing
update was silently not committed. This script:
  * enumerates presentations from the actual git tree (git ls-tree + git show),
    NOT `os.listdir()` on the worktree
  * uses a sparse cone that includes the root `/index.html` AND the deployed
    subfolder's full file tree
  * keeps every operation inside an isolated temp clone — never touches the main working tree
  * verifies the pushed files back by MD5 (mandatory — never trust a bare push)

Usage:
  python3 scripts/deploy_pages.py "READING M2" "PROJECTS/READING M2/slides"
Flags:
  --dry-run    do everything except commit/push (still builds the landing page)
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]  # repo root
REPO = PROJECT.name
REMOTE_PREFERRED = "old-origin"
REMOTE_FALLBACK = "origin"
GH_HOST = "https://github.com"


# ---------------------------------------------------------------------------
# small git helpers (run in the main repo unless a cwd is given)
# ---------------------------------------------------------------------------
def git(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=False)


def git_ok(args: list[str], cwd: Path) -> bool:
    return git(args, cwd).returncode == 0


def git_out(args: list[str], cwd: Path) -> str:
    r = git(args, cwd)
    return r.stdout if r.returncode == 0 else ""


def remote_for_pages() -> tuple[str, str, str]:
    """Return (pages_remote, owner, repo). Prefer old-origin; fall back to origin."""
    for name in (REMOTE_PREFERRED, REMOTE_FALLBACK):
        url = git_out(["remote", "get-url", name], PROJECT).strip()
        if not url:
            continue
        m = re.search(r"github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?/?$", url)
        if m:
            return name, m.group(1), m.group(2)
    raise SystemExit("ERROR: no GitHub remote (old-origin or origin)")


def gh_authed() -> bool:
    r = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True, check=False)
    return "Logged in" in (r.stdout + r.stderr)


def fetch_pages(remote: str) -> None:
    git(["fetch", remote, "gh-pages"], PROJECT)


def branch_has_dir(ref: str, name: str) -> bool:
    r = git(["ls-tree", "-d", "--name-only", ref], PROJECT)
    return any(d.strip() == name for d in r.stdout.splitlines())


def branch_has_file(ref: str, path: str) -> bool:
    return git_ok(["cat-file", "-e", f"{ref}:{path}"], PROJECT)


def read_branch_file(ref: str, path: str) -> str:
    r = git(["show", f"{ref}:{path}"], PROJECT)
    return r.stdout if r.returncode == 0 else ""


def title_from_html(content: str, fallback: str) -> str:
    m = re.search(r"<title>\s*(.*?)\s*</title>", content, re.DOTALL)
    if m:
        t = m.group(1).strip()
        if t.lower() not in ("slides", "presentation", ""):
            return t
    return fallback


def build_landing(ref: str, local_sub: Path, name: str) -> str:
    """Enumerate presentations from the git tree (authoritative), not os.listdir().

    Every top-level directory that contains an index.html counts as a presentation.
    The NEW/updating subfolder is read from the local staging copy so it appears
    even before the branch has it.
    """
    dirs = [d for d in git_out(["ls-tree", "-d", "--name-only", ref], PROJECT).splitlines()
            if d and not d.startswith(".")]
    presentations: list[tuple[str, str]] = []
    seen: set[str] = set()
    for d in dirs:
        if d in seen or not branch_has_file(ref, f"{d}/index.html"):
            continue
        title = title_from_html(read_branch_file(ref, f"{d}/index.html")[:5000], d)
        presentations.append((d, title))
        seen.add(d)

    # make sure the deployed subfolder is always listed (new deploy)
    if name not in seen:
        local_idx = local_sub / "index.html"
        t = title_from_html(local_idx.read_text(encoding="utf-8", errors="replace")[:5000], name) \
            if local_idx.exists() else name
        presentations.append((name, t))
        seen.add(name)

    presentations.sort(key=lambda x: x[0].lower())
    cards = "\n".join(
        f'<a href="{d}/" class="card"><div class="card-title">{t}</div></a>'
        for d, t in presentations
    )
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8" /><meta name="viewport" content="width=device-width, initial-scale=1.0" /><title>Slides</title><style>*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:system-ui,sans-serif;background:#f0f2f5;min-height:100vh;display:flex;flex-direction:column;align-items:center;padding:60px 20px}}h1{{font-size:2.2em;color:#1a1a2e;margin-bottom:40px}}.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:20px;max-width:960px;width:100%}}.card{{background:white;border-radius:12px;padding:28px 24px;text-decoration:none;color:#333;box-shadow:0 2px 8px rgba(0,0,0,0.08);transition:transform .2s;display:flex;flex-direction:column}}.card:hover{{transform:translateY(-4px);box-shadow:0 8px 24px rgba(0,0,0,0.12)}}.card-title{{font-size:1.15em;font-weight:600;color:#1a1a2e}}footer{{margin-top:50px;font-size:.85em;color:#aaa}}</style></head><body><h1>Slides</h1><div class="grid">
{cards}</div><footer>{len(presentations)} presentations</footer></body></html>"""


# ---------------------------------------------------------------------------
# deploy
# ---------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser(description="Deploy a slideshow to gh-pages.")
    ap.add_argument("name", help="subfolder name (spaces -> underscores)")
    ap.add_argument("source_dir", help="path to the slides directory containing index.html")
    ap.add_argument("--dry-run", action="store_true", help="build everything but skip commit+push")
    args = ap.parse_args()

    name = re.sub(r"\s+", "_", args.name.strip()).strip("_")
    source_dir = Path(args.source_dir)
    if not source_dir.is_absolute():
        source_dir = PROJECT / source_dir
    slides_html = source_dir / "index.html"
    if not slides_html.exists():
        raise SystemExit(f"ERROR: no slideshow at {slides_html}")

    pages_remote, owner, repo = remote_for_pages()
    if not gh_authed():
        raise SystemExit("ERROR: gh not authenticated — run 'gh auth login'")

    fetch_pages(pages_remote)
    ref = f"{pages_remote}/gh-pages"
    exists = branch_has_dir(ref, name)
    action = "UPDATE" if exists else "NEW DEPLOY"

    print(f"=== Deploy {name} ===\n  remote:  {pages_remote} ({owner}/{repo})\n"
          f"  source:  {slides_html}\n  action:  {action}")

    # stage a copy of the deck
    staging = Path(tempfile.mkdtemp(prefix="gh-pages-staging-"))
    local_sub = staging / name
    shutil.copytree(source_dir, local_sub)

    # clone gh-pages into an isolated worktree (never touches the main checkout)
    worktree = Path(tempfile.mkdtemp(prefix="gh-pages-worktree-"))
    cloned = git(["clone", "--filter=blob:none", "--sparse", "--branch", "gh-pages",
                  "--single-branch", "--depth", "1",
                  f"https://github.com/{owner}/{repo}.git", str(worktree)], PROJECT)
    if cloned.returncode != 0:
        shutil.rmtree(worktree, ignore_errors=True)
        raise SystemExit(
            "ERROR: gh-pages branch not found on the remote. Create it once, "
            "then re-run (this repo's gh-pages already exists)."
        )
    git(["sparse-checkout", "set", "--no-cone", "/index.html", "*/index.html", f"{name}/"], worktree)

    # drift check: skip if the deployed subfolder already matches
    deployed = worktree / name
    if deployed.exists() and _identical(local_sub, deployed):
        print("  no changes — slides identical to gh-pages. Nothing to deploy.")
        shutil.rmtree(staging, ignore_errors=True)
        shutil.rmtree(worktree, ignore_errors=True)
        return

    # copy the deck in
    shutil.rmtree(deployed, ignore_errors=True)
    shutil.copytree(local_sub, deployed)

    # regenerate the landing page from the git tree (NOT os.listdir on the worktree)
    landing = build_landing(ref, local_sub, name)
    (worktree / "index.html").write_text(landing, encoding="utf-8")
    n = landing.count('class="card"')
    print(f"  landing page: {n} presentations")

    git(["add", "-A"], worktree)
    # completeness gate — abort if the sparse cone dropped any staged file
    missing = [f for f in _all_files(local_sub)
               if not git_ok(["ls-files", "--error-unmatch", f"{name}/{f}"], worktree)]
    if missing:
        raise SystemExit(f"ERROR: sparse cone dropped files: {', '.join(missing[:10])}")

    if args.dry_run:
        print("  --dry-run: would commit+push; skipping.")
        shutil.rmtree(staging, ignore_errors=True)
        shutil.rmtree(worktree, ignore_errors=True)
        return

    if git(["diff", "--cached", "--quiet"], worktree).returncode == 0:
        print("  nothing to commit — deploy cancelled.")
        shutil.rmtree(staging, ignore_errors=True)
        shutil.rmtree(worktree, ignore_errors=True)
        return

    git(["commit", "-m", f"Deploy {name} ({os.popen('date +%d%m%y').read().strip()})"], worktree)
    push = git(["push", "origin", "HEAD:gh-pages"], worktree)
    print("  push:", push.stdout.strip() or push.stderr.strip())

    # MANDATORY verification: fetch back and compare MD5
    fetch_pages(pages_remote)
    ok = True
    landing_path = _write_temp(landing)
    for remote_path, local_file in ((f"{name}/index.html", slides_html),
                                    ("index.html", landing_path)):
        local_md5 = _md5(local_file)
        remote_md5 = _md5_text(read_branch_file(ref, remote_path))
        if local_md5 == remote_md5:
            print(f"  VERIFIED {remote_path} (MD5 {local_md5})")
        else:
            ok = False
            print(f"  ERROR {remote_path}: local {local_md5} != remote {remote_md5}")
    landing_path.unlink(missing_ok=True)

    shutil.rmtree(staging, ignore_errors=True)
    shutil.rmtree(worktree, ignore_errors=True)
    if not ok:
        raise SystemExit("ERROR: deploy verification failed")
    print(f"\nDeployed: {name}\n  https://{owner}.github.io/{repo}/{name}/index.html\n"
          f"  Landing: https://{owner}.github.io/{repo}/")


def _all_files(d: Path) -> list[str]:
    return [str(p.relative_to(d)) for p in d.rglob("*") if p.is_file()]


def _identical(a: Path, b: Path) -> bool:
    files_a = set(_all_files(a))
    files_b = set(_all_files(b))
    if files_a != files_b:
        return False
    for rel in files_a:
        ap, bp = a / rel, b / rel
        if not bp.exists() or ap.read_bytes() != bp.read_bytes():
            return False
    return True


def _md5(p: Path) -> str:
    import hashlib
    return hashlib.md5(p.read_bytes()).hexdigest()


def _md5_text(s: str) -> str:
    import hashlib
    return hashlib.md5(s.encode()).hexdigest()


def _write_temp(s: str) -> Path:
    import tempfile
    f = Path(tempfile.mktemp(suffix=".html"))
    f.write_text(s, encoding="utf-8")
    return f


if __name__ == "__main__":
    main()
