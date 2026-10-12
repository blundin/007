import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ADR_WRITE_GUARD = Path(__file__).resolve().parent.parent / "adr_write_guard.py"


def run_guard(project: Path, payload: str) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "CLAUDE_PROJECT_DIR": str(project)}
    return subprocess.run(
        [sys.executable, str(ADR_WRITE_GUARD)],
        input=payload,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


def run_for_path(project: Path, file_path: str) -> subprocess.CompletedProcess[str]:
    return run_guard(project, json.dumps({"tool_input": {"file_path": file_path}}))


@pytest.mark.parametrize(
    "file_path",
    [
        "docs/adr/0001-use-postgres.md",
        "docs/adr/sub/0002-nested.md",
    ],
)
def test_allows_markdown_inside_docs_adr(tmp_path: Path, file_path: str) -> None:
    result = run_for_path(tmp_path, str(tmp_path / file_path))

    assert result.returncode == 0, result.stderr


def test_allows_a_relative_path_inside_docs_adr(tmp_path: Path) -> None:
    result = run_for_path(tmp_path, "docs/adr/0001-use-postgres.md")

    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(
    "file_path",
    [
        "src/app.py",
        "docs/specs/AUTH.md",
        "docs/adr",
        "docs/adr/0001-use-postgres.txt",
        "docs/adr/hook.py",
        "docs/adr/0001.md.sh",
        "docs/adr-extra/0001.md",
        "docs/adrs/0001.md",
        "docs/adr/../specs/AUTH.md",
        ".claude/settings.json",
    ],
)
def test_blocks_anything_but_markdown_inside_docs_adr(
    tmp_path: Path, file_path: str
) -> None:
    result = run_for_path(tmp_path, str(tmp_path / file_path))

    assert result.returncode == 2
    assert "adr" in result.stderr


def test_blocks_a_path_outside_the_project(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()

    result = run_for_path(project, str(tmp_path / "docs" / "adr" / "0001.md"))

    assert result.returncode == 2


def test_blocks_a_symlink_that_escapes_docs_adr(tmp_path: Path) -> None:
    (tmp_path / "docs" / "adr").mkdir(parents=True)
    (tmp_path / "src").mkdir()
    (tmp_path / "docs" / "adr" / "link.md").symlink_to(tmp_path / "src" / "app.md")

    result = run_for_path(tmp_path, str(tmp_path / "docs" / "adr" / "link.md"))

    assert result.returncode == 2


@pytest.mark.parametrize(
    "payload",
    [
        "not json",
        "",
        "[]",
        json.dumps({}),
        json.dumps({"tool_input": {}}),
        json.dumps({"tool_input": {"file_path": ""}}),
        json.dumps({"tool_input": {"file_path": 7}}),
        json.dumps({"tool_input": "docs/adr/0001.md"}),
    ],
)
def test_blocks_unreadable_or_incomplete_input(tmp_path: Path, payload: str) -> None:
    result = run_guard(tmp_path, payload)

    assert result.returncode == 2
    assert result.stderr
