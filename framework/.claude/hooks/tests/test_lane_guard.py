import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

LANE_GUARD = Path(__file__).resolve().parent.parent / "lane_guard.py"

LANES = {"test": ["spec/"], "src": ["lib/", "app/"]}


def write_lanes(project: Path, content: str) -> None:
    (project / ".claude").mkdir(exist_ok=True)
    (project / ".claude" / "lanes.json").write_text(content)


def run_guard(
    project: Path, lane: str, file_path: str
) -> subprocess.CompletedProcess[str]:
    payload = json.dumps({"tool_input": {"file_path": file_path}})
    env = {**os.environ, "CLAUDE_PROJECT_DIR": str(project)}
    return subprocess.run(
        [sys.executable, str(LANE_GUARD), lane],
        input=payload,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


@pytest.mark.parametrize(
    ("lane", "file_path"),
    [
        ("test", "spec/models/user_spec.rb"),
        ("src", "lib/parser.rb"),
        ("src", "app/models/user.rb"),
    ],
)
def test_allows_write_inside_a_lane_read_from_lanes_json(
    tmp_path: Path, lane: str, file_path: str
) -> None:
    write_lanes(tmp_path, json.dumps(LANES))

    result = run_guard(tmp_path, lane, str(tmp_path / file_path))

    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(
    ("lane", "file_path"),
    [
        ("test", "lib/parser.rb"),
        ("src", "spec/models/user_spec.rb"),
        ("src", "tests/test_x.py"),
        ("src", "library/x.rb"),
        ("src", ".claude/lanes.json"),
    ],
)
def test_blocks_write_outside_the_lane(
    tmp_path: Path, lane: str, file_path: str
) -> None:
    write_lanes(tmp_path, json.dumps(LANES))

    result = run_guard(tmp_path, lane, str(tmp_path / file_path))

    assert result.returncode == 2
    assert f"active TDD lane is '{lane}'" in result.stderr


def test_blocks_unknown_lane(tmp_path: Path) -> None:
    write_lanes(tmp_path, json.dumps(LANES))

    result = run_guard(tmp_path, "docs", str(tmp_path / "lib" / "x.rb"))

    assert result.returncode == 2
    assert "unknown TDD lane 'docs'" in result.stderr


def test_blocks_every_write_when_lanes_json_is_missing(tmp_path: Path) -> None:
    result = run_guard(tmp_path, "src", str(tmp_path / "src" / "x.py"))

    assert result.returncode == 2
    assert "lanes.json" in result.stderr


@pytest.mark.parametrize(
    "content",
    [
        "not json",
        "[]",
        '{"src": "lib/"}',
        '{"src": []}',
        '{"src": [""]}',
        '{"src": ["lib"]}',
        '{"src": [3]}',
    ],
)
def test_blocks_every_write_when_lanes_json_is_invalid(
    tmp_path: Path, content: str
) -> None:
    write_lanes(tmp_path, content)

    result = run_guard(tmp_path, "src", str(tmp_path / "lib" / "x.rb"))

    assert result.returncode == 2
    assert "lanes.json" in result.stderr


def test_blocks_write_outside_the_project(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    write_lanes(project, json.dumps(LANES))

    result = run_guard(project, "src", str(tmp_path / "lib" / "x.rb"))

    assert result.returncode == 2
    assert "outside the project" in result.stderr


def test_blocks_relative_path_that_escapes_the_lane(tmp_path: Path) -> None:
    write_lanes(tmp_path, json.dumps(LANES))

    result = run_guard(tmp_path, "src", "lib/../spec/x_spec.rb")

    assert result.returncode == 2


@pytest.mark.parametrize(
    "payload",
    ["not json", "[]", '{"tool_input": []}', '{"tool_input": {"file_path": 1}}'],
)
def test_blocks_input_it_cannot_read(tmp_path: Path, payload: str) -> None:
    write_lanes(tmp_path, json.dumps(LANES))
    env = {**os.environ, "CLAUDE_PROJECT_DIR": str(tmp_path)}

    result = subprocess.run(
        [sys.executable, str(LANE_GUARD), "src"],
        input=payload,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )

    assert result.returncode == 2
    assert "Blocked" in result.stderr
