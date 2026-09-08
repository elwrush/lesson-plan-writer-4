"""
test_git_pages_safety.py — Red-Green Test for gh-pages deploy safety.

The single gh-pages deploy implementation moved to `scripts/deploy_pages.py`
(ADR 0006); the `/git-pages` command and `just git-pages` both dispatch to it.
This guard therefore scans the IMPLEMENTATION for the safety guarantees, and
checks the command file only dispatches (never itself runs a destructive git).

Green phase (should PASS):
  - command file exists and dispatches to scripts/deploy_pages.py
  - implementation uses an ISOLATED clone (--depth 1, --single-branch)
  - implementation keeps git ops inside a worktree (never the main checkout)
  - implementation has a drift check + push MD5 verification
  - implementation expands the sparse cone and completeness-checks staged files
  - NO "git checkout" / "git rm -rf" / "git clean -fd" anywhere in the impl
  - a prominent safety guarantee lives in the implementation docstring
"""

from pathlib import Path

COMMAND_FILE = Path(".opencode/command/git-pages.md")
SCRIPT = Path("scripts/deploy_pages.py")


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def _extract_code_blocks(content: str) -> str:
    lines = []
    in_block = False
    for line in content.split("\n"):
        if line.strip().startswith("```bash"):
            in_block = True
            continue
        if line.strip() == "```" and in_block:
            in_block = False
            continue
        if in_block:
            lines.append(line)
    return "\n".join(lines)


# ── command file: exists and only dispatches ────────────────────────────────
def test_command_file_exists():
    assert COMMAND_FILE.exists(), "RED PHASE: command file does not exist yet"


def test_command_dispatches_to_script():
    assert "deploy_pages.py" in _read(COMMAND_FILE), (
        "The /git-pages command must dispatch to scripts/deploy_pages.py (single impl)."
    )


def test_command_has_no_destructive_git():
    code = _extract_code_blocks(_read(COMMAND_FILE))
    for bad in ("git checkout", "git rm -rf", "git clean -fd"):
        assert bad not in code, f"command file must not run '{bad}'"


# ── implementation: isolated clone + worktree ───────────────────────────────
def test_impl_uses_isolated_clone():
    c = _read(SCRIPT)
    assert "clone" in c and "--depth" in c and "--single-branch" in c and "--branch" in c, (
        "Must clone gh-pages into an isolated directory: git clone --depth 1 --single-branch."
    )


def test_impl_keeps_git_in_worktree():
    c = _read(SCRIPT)
    assert "worktree" in c and "cwd=" in c, (
        "All git operations must run inside the isolated worktree cwd (never the main checkout)."
    )


def test_impl_no_direct_branch_switch():
    c = _read(SCRIPT)
    assert "git checkout" not in c, (
        "Found 'git checkout' in the deploy script. Use git clone --depth 1 instead."
    )


def test_impl_no_destructive_git():
    c = _read(SCRIPT)
    for bad in ("git rm -rf", "git rm ", "git clean -fd", "clean -fd"):
        assert bad not in c, f"deploy script must not run '{bad}'"


# ── implementation: drift check + push verification ─────────────────────────
def test_impl_drift_check():
    c = _read(SCRIPT)
    assert "drift" in c and "identical" in c, (
        "Must compare staging vs deployed (drift check) and skip when identical."
    )


def test_impl_push_verification():
    c = _read(SCRIPT)
    assert "md5" in c and "VERIFIED" in c, (
        "Must verify the pushed file back by MD5 before declaring success."
    )


def test_impl_sparse_cone_expands_for_deployed_folder():
    c = _read(SCRIPT)
    assert "sparse-checkout" in c, (
        "Must expand the sparse cone to include the deployed folder so its assets get staged."
    )


def test_impl_staged_completeness_check():
    c = _read(SCRIPT)
    assert "ls-files" in c and "--error-unmatch" in c, (
        "Must verify every staged file is tracked (ls-files --error-unmatch) before commit."
    )


def test_impl_exits_on_failure():
    c = _read(SCRIPT)
    assert "SystemExit" in c or "sys.exit" in c, "Must exit non-zero on failure."


def test_safety_header_present():
    c = _read(SCRIPT)
    assert "never touches the main working tree" in c, (
        "The implementation docstring must state it never touches the main working tree."
    )
