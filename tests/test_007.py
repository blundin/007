import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

TOOL = Path(__file__).resolve().parent.parent / "bin" / "007"

GIT_ENV = {
    **os.environ,
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_AUTHOR_NAME": "Test",
    "GIT_AUTHOR_EMAIL": "test@example.com",
    "GIT_COMMITTER_NAME": "Test",
    "GIT_COMMITTER_EMAIL": "test@example.com",
}

FRAMEWORK_FILES = {
    "CLAUDE.md": "@AGENTS.md\nloop rules\n",
    "AGENTS.md": "# <!-- FILL: project name -->\n",
    ".gitignore": "__pycache__/\n",
    ".claude/lanes.json": '{"test": ["tests/"], "src": ["src/"]}\n',
    ".claude/settings.json": '{"permissions": {}}\n',
    ".claude/agents/app-developer.md": "app developer\n",
    ".claude/agents/test-engineer.md": "test engineer\n",
    ".claude/hooks/lane_guard.py": "# lane guard\n",
    ".claude/hooks/ruff.toml": "target-version = 'py312'\n",
    ".claude/hooks/tests/test_lane_guard.py": "# tests\n",
    ".claude/skills/review-tracker/SKILL.md": "review tracker\n",
    "scripts/check": "#!/usr/bin/env bash\nexit 1\n",
    "scripts/test": "#!/usr/bin/env bash\nexit 1\n",
    "scripts/lint": "#!/usr/bin/env bash\nexit 1\n",
    "scripts/check-dev-framework": "#!/usr/bin/env bash\nexit 0\n",
    "docs/specs/README.md": "specs\n",
    "docs/plans/README.md": "plans\n",
    "docs/code-reviews/README.md": "code reviews\n",
    "docs/guides/added-later.md": "a file no list names\n",
}

OUTSIDE_FILES = {
    "README.md": "007 readme\n",
    "CLAUDE.md": "how to work on 007\n",
    "CHANGELOG.md": "changes\n",
    "scripts/check": "#!/usr/bin/env bash\n# 007's own gate\n",
    "tests/test_007.py": "# tool tests\n",
    "docs/README.md": "007 docs\n",
    "docs/backlog.md": "backlog\n",
    "docs/lessons.md": "lessons\n",
    "docs/specs/FW-11-007-tool.md": "spec\n",
    "docs/adr/ADR-001-007-tool.md": "adr\n",
}

SCRIPTS = [
    "scripts/check",
    "scripts/test",
    "scripts/lint",
    "scripts/check-dev-framework",
]

MERGE_BY_HAND = [
    "CLAUDE.md",
    "AGENTS.md",
    ".claude/settings.json",
    ".gitignore",
]


def git(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
        env=GIT_ENV,
    )


def write_files(root: Path, files: dict[str, str]) -> None:
    for relative, content in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)


@pytest.fixture
def checkout(tmp_path: Path) -> Path:
    root = tmp_path / "007"
    write_files(root / "framework", FRAMEWORK_FILES)
    write_files(root, OUTSIDE_FILES)
    for script in SCRIPTS:
        (root / "framework" / script).chmod(0o755)
    (root / "bin").mkdir()
    shutil.copy2(TOOL, root / "bin" / "007")
    git(root, "init", "-q")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "fake 007")
    cache = root / "framework" / ".claude" / "hooks" / "tests" / "__pycache__"
    cache.mkdir()
    (cache / "test_lane_guard.cpython-313.pyc").write_bytes(b"\x00")
    return root


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "existing"
    root.mkdir()
    git(root, "init", "-q")
    (root / "app.py").write_text("print('hi')\n")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "existing")
    return root


def run_007(checkout: Path, cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(checkout / "bin" / "007"), *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
        env=GIT_ENV,
    )


def checkout_commit(checkout: Path) -> str:
    return git(checkout, "rev-parse", "HEAD").stdout.strip()


def all_files(root: Path) -> set[str]:
    return {
        str(path.relative_to(root))
        for path in root.rglob("*")
        if path.is_file() and ".git" not in path.relative_to(root).parts
    }


# NEW-01


def test_new_copies_every_framework_file_with_matching_contents(
    checkout: Path, tmp_path: Path
) -> None:
    result = run_007(checkout, tmp_path, "new", "myapp")

    assert result.returncode == 0, result.stderr
    target = tmp_path / "myapp"
    for relative, content in FRAMEWORK_FILES.items():
        assert (target / relative).read_text() == content, relative


def test_new_initializes_a_git_repo(checkout: Path, tmp_path: Path) -> None:
    run_007(checkout, tmp_path, "new", "myapp")
    assert (tmp_path / "myapp").is_dir()

    result = git(tmp_path / "myapp", "rev-parse", "--show-toplevel")

    assert result.returncode == 0
    assert Path(result.stdout.strip()).resolve() == (tmp_path / "myapp").resolve()


def test_new_keeps_scripts_executable(checkout: Path, tmp_path: Path) -> None:
    run_007(checkout, tmp_path, "new", "myapp")

    for script in SCRIPTS:
        assert os.access(tmp_path / "myapp" / script, os.X_OK), script


def test_new_copies_only_framework_files_and_the_version_file(
    checkout: Path, tmp_path: Path
) -> None:
    run_007(checkout, tmp_path, "new", "myapp")

    assert all_files(tmp_path / "myapp") == {*FRAMEWORK_FILES, ".007-version"}


# NEW-02


def test_new_refuses_an_existing_empty_directory(
    checkout: Path, tmp_path: Path
) -> None:
    (tmp_path / "myapp").mkdir()

    result = run_007(checkout, tmp_path, "new", "myapp")

    assert result.returncode != 0
    assert list((tmp_path / "myapp").iterdir()) == []


def test_new_refuses_an_existing_file(checkout: Path, tmp_path: Path) -> None:
    (tmp_path / "myapp").write_text("not a directory\n")

    result = run_007(checkout, tmp_path, "new", "myapp")

    assert result.returncode != 0
    assert (tmp_path / "myapp").read_text() == "not a directory\n"


# INIT-01


def test_init_copies_every_framework_file_into_the_repo(
    checkout: Path, repo: Path
) -> None:
    result = run_007(checkout, repo, "init")

    assert result.returncode == 0, result.stderr
    for relative, content in FRAMEWORK_FILES.items():
        assert (repo / relative).read_text() == content, relative
    for script in SCRIPTS:
        assert os.access(repo / script, os.X_OK), script


def test_init_refuses_outside_a_git_repo(checkout: Path, tmp_path: Path) -> None:
    plain = tmp_path / "plain"
    plain.mkdir()

    result = run_007(checkout, plain, "init")

    assert result.returncode != 0
    assert list(plain.iterdir()) == []


def test_init_refuses_below_the_top_level_of_a_repo(checkout: Path, repo: Path) -> None:
    sub = repo / "sub"
    sub.mkdir()

    result = run_007(checkout, sub, "init")

    assert result.returncode != 0
    assert list(sub.iterdir()) == []
    assert all_files(repo) == {"app.py"}


# INIT-02


def test_init_never_overwrites_an_existing_file_and_lists_it(
    checkout: Path, repo: Path
) -> None:
    write_files(repo, {"scripts/test": "#!/usr/bin/env bash\nmine\n"})

    result = run_007(checkout, repo, "init")

    assert result.returncode == 0, result.stderr
    assert (repo / "scripts/test").read_text() == "#!/usr/bin/env bash\nmine\n"
    assert "scripts/test" in result.stdout


@pytest.mark.parametrize("relative", MERGE_BY_HAND)
def test_init_says_what_to_merge_by_hand_for_a_skipped_shared_file(
    checkout: Path, repo: Path, relative: str
) -> None:
    write_files(repo, {relative: "the project's own\n"})

    result = run_007(checkout, repo, "init")

    assert (repo / relative).read_text() == "the project's own\n"
    assert str(checkout / "framework" / relative) in result.stdout


def test_init_does_not_overwrite_an_existing_version_file(
    checkout: Path, repo: Path
) -> None:
    write_files(repo, {".007-version": "older\n"})

    result = run_007(checkout, repo, "init")

    assert (repo / ".007-version").read_text() == "older\n"
    assert ".007-version" in result.stdout


# BOTH-01


def test_new_writes_the_checkout_commit_to_the_version_file(
    checkout: Path, tmp_path: Path
) -> None:
    run_007(checkout, tmp_path, "new", "myapp")

    version = (tmp_path / "myapp" / ".007-version").read_text()

    assert version == checkout_commit(checkout) + "\n"


def test_init_writes_the_checkout_commit_to_the_version_file(
    checkout: Path, repo: Path
) -> None:
    run_007(checkout, repo, "init")

    assert (repo / ".007-version").read_text() == checkout_commit(checkout) + "\n"


# BOTH-02


@pytest.mark.parametrize("command", ["new", "init"])
def test_prints_the_next_steps(
    checkout: Path, repo: Path, tmp_path: Path, command: str
) -> None:
    if command == "new":
        result = run_007(checkout, tmp_path, "new", "myapp")
    else:
        result = run_007(checkout, repo, "init")

    steps = result.stdout.split("Next steps:")[-1]
    for expected in [
        ".claude/lanes.json",
        "FILL",
        "scripts/check",
        "scripts/test",
        "scripts/lint",
        "./scripts/check-dev-framework",
        "commit",
    ]:
        assert expected in steps, expected


# BOTH-03


def test_new_makes_no_commit(checkout: Path, tmp_path: Path) -> None:
    run_007(checkout, tmp_path, "new", "myapp")
    assert (tmp_path / "myapp" / ".git").is_dir()

    assert git(tmp_path / "myapp", "rev-parse", "HEAD").returncode != 0


def test_init_makes_no_commit(checkout: Path, repo: Path) -> None:
    before = git(repo, "rev-parse", "HEAD").stdout

    run_007(checkout, repo, "init")

    assert git(repo, "rev-parse", "HEAD").stdout == before


def test_init_refuses_a_symlink_that_leads_outside_the_repo(
    checkout: Path, repo: Path, tmp_path: Path
) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    (repo / ".claude").symlink_to(outside)

    result = run_007(checkout, repo, "init")

    assert result.returncode != 0
    assert list(outside.iterdir()) == []
    assert all_files(repo) == {"app.py"}


def test_init_refuses_a_dangling_symlink_that_leads_outside_the_repo(
    checkout: Path, repo: Path, tmp_path: Path
) -> None:
    target = tmp_path / "outside" / "CLAUDE.md"
    (repo / "CLAUDE.md").symlink_to(target)

    result = run_007(checkout, repo, "init")

    assert not target.exists()
    assert "CLAUDE.md" in result.stdout + result.stderr


# BOTH-04


@pytest.mark.parametrize("command", ["new", "init"])
def test_refuses_a_framework_file_with_uncommitted_changes(
    checkout: Path, repo: Path, tmp_path: Path, command: str
) -> None:
    (checkout / "framework" / "AGENTS.md").write_text("an uncommitted edit\n")

    if command == "new":
        result = run_007(checkout, tmp_path, "new", "myapp")
        assert not (tmp_path / "myapp").exists()
    else:
        result = run_007(checkout, repo, "init")
        assert all_files(repo) == {"app.py"}

    assert result.returncode != 0
    assert "uncommitted" in result.stderr


def test_init_refuses_a_staged_framework_file(checkout: Path, repo: Path) -> None:
    write_files(checkout / "framework", {".claude/agents/new.md": "staged\n"})
    git(checkout, "add", "framework/.claude/agents/new.md")

    result = run_007(checkout, repo, "init")

    assert result.returncode != 0
    assert all_files(repo) == {"app.py"}


def test_init_ignores_uncommitted_changes_outside_the_framework(
    checkout: Path, repo: Path
) -> None:
    (checkout / "README.md").write_text("an uncommitted edit\n")
    write_files(checkout / "framework", {"notes.txt": "untracked\n"})

    result = run_007(checkout, repo, "init")

    assert result.returncode == 0, result.stderr
    assert not (repo / "notes.txt").exists()


# INIT-03


def test_init_refuses_a_file_where_a_directory_is_needed(
    checkout: Path, repo: Path
) -> None:
    write_files(repo, {"docs": "notes\n"})

    result = run_007(checkout, repo, "init")

    assert result.returncode != 0
    assert "docs" in result.stderr
    assert "Traceback" not in result.stderr
    assert all_files(repo) == {"app.py", "docs"}
