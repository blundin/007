import json
import subprocess
import sys
from pathlib import Path

import pytest

GIT_GUARD = Path(__file__).resolve().parent.parent / "git_guard.py"


def run_guard(command: str) -> subprocess.CompletedProcess[str]:
    payload = json.dumps({"tool_input": {"command": command}})
    return subprocess.run(
        [sys.executable, str(GIT_GUARD)],
        input=payload,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.parametrize(
    "command",
    [
        "git status",
        "git -C /repo status",
        "git -c color.ui=never diff",
        "git --git-dir=/repo/.git log",
        "git --git-dir /repo/.git log",
        "git --work-tree /repo show HEAD",
        "git --no-pager log --oneline",
        "cd /repo && git -C /repo rev-parse HEAD",
        "git stash list",
        "git -C /repo stash list",
    ],
)
def test_allows_read_only_subcommand_after_global_options(command: str) -> None:
    result = run_guard(command)

    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(
    ("command", "subcommand"),
    [
        ("git tag probe", "tag"),
        ("git -C /repo tag probe", "tag"),
        ("git -c user.name=x commit -m x", "commit"),
        ("git --git-dir /repo/.git push", "push"),
        ("git -C status commit -m x", "commit"),
        ("git status && git -C /repo stash", "stash"),
        ("git stash", "stash"),
        ("git stash pop", "stash"),
        ("git stash listx", "stash"),
        ("git stash list&&git stash drop", "stash"),
        ("git stash list ;git push", "push"),
        ("git status ;git push", "push"),
    ],
)
def test_blocks_state_changing_subcommand_and_names_it(
    command: str, subcommand: str
) -> None:
    result = run_guard(command)

    assert result.returncode == 2
    assert f"`git {subcommand}`" in result.stderr
