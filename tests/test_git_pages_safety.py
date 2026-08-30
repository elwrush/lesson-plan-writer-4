"""
test_git_pages_safety.py — Red-Green Test for /git-pages Command Safety

Red phase (no command file yet, should FAIL):
    - COMMAND_FILE does not exist

Green phase (should PASS):
    - Contains "git clone --depth 1"
    - Contains "git -C $worktreeDir"
    - Contains "diff -rq" (drift check) in code blocks
    - Contains "md5sum" (push verification) in code blocks
    - Contains NO "git checkout gh-pages" in code blocks
    - Contains NO "git rm -rf" in code blocks
    - Contains NO "git clean -fd" in code blocks
    - Contains "This command NEVER switches branches in the main working tree"
"""

COMMAND_FILE = ".opencode/command/git-pages.md"
RED = "RED PHASE: command file does not exist yet"


def load_command_file():
    with open(COMMAND_FILE, encoding="utf-8") as f:
        return f.read()


def extract_code_blocks(content):
    in_block = False
    lines = []
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


def test_red_phase_would_fail():
    """RED PHASE: command file doesn't exist yet."""
    import pathlib
    assert pathlib.Path(COMMAND_FILE).exists(), RED


def test_uses_isolated_checkout():
    """Must use git clone --depth 1 for isolated gh-pages checkout."""
    content = load_command_file()
    has_shallow_clone = "git clone" in content and "--depth 1" in content
    assert has_shallow_clone, (
        "Must use git clone --depth 1 to check out gh-pages "
        "in an isolated directory."
    )


def test_uses_git_C_flag():
    """Must use 'git -C $worktreeDir' explicitly."""
    content = load_command_file()
    assert "git -C $worktreeDir" in content, (
        "Must use 'git -C $worktreeDir' explicitly."
    )


def test_no_direct_branch_switch():
    """Verify NO 'git checkout gh-pages' in code blocks."""
    code = extract_code_blocks(load_command_file())
    assert "git checkout" not in code, (
        "Found 'git checkout' in a code block. Use git clone --depth 1 instead."
    )


def test_no_git_rm_rf():
    code = extract_code_blocks(load_command_file())
    assert "git rm -rf" not in code, (
        "Found 'git rm -rf' in a code block. Destructive pattern."
    )


def test_no_git_clean_fd():
    code = extract_code_blocks(load_command_file())
    assert "git clean -fd" not in code, (
        "Found 'git clean -fd' in a code block. Destructive pattern."
    )


def test_drift_check_present():
    """Must use 'diff -rq' for drift detection before deploy."""
    code = extract_code_blocks(load_command_file())
    assert "diff -rq" in code, (
        "Missing drift check. Add 'diff -rq' in a code block to compare "
        "staging vs deployed slides before committing."
    )


def test_push_verification_present():
    """Must use 'md5sum' after push to verify remote matches local."""
    code = extract_code_blocks(load_command_file())
    assert "md5sum" in code, (
        "Missing push verification. Add 'md5sum' in a code block to verify "
        "the pushed file matches the local source, preventing hallucinated deploys."
    )


def test_safety_header_present():
    content = load_command_file()
    assert "This command NEVER switches branches in the main working tree" in content, (
        "Must have a prominent safety header."
    )


def test_exit_on_failure():
    content = load_command_file()
    assert "exit 1" in content, (
        "Must exit on failure instead of continuing."
    )


def test_sparse_cone_expands_for_deployed_folder():
    """Sparse clone must include the deployed folder so its assets get staged."""
    content = load_command_file()
    assert "sparse-checkout set" in content, (
        "Step 6 must expand the sparse cone to include the deployed folder. "
        "Without it, git add -A silently skips the folder's assets and the "
        "push ships an index.html with missing media."
    )


def test_staged_completeness_check():
    """Must verify every staged file is tracked before commit."""
    content = load_command_file()
    assert "missing_files" in content and "ls-files" in content, (
        "Before committing, the command must verify every file copied into "
        "the worktree is staged — a sparse-checkout that drops assets must "
        "abort the deploy, not ship a broken deck."
    )
