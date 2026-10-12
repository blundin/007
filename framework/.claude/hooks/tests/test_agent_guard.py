import json
import subprocess
import sys
from pathlib import Path

import pytest

AGENT_GUARD = Path(__file__).resolve().parent.parent / "agent_guard.py"


def run_guard(payload: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(AGENT_GUARD)],
        input=payload,
        capture_output=True,
        text=True,
        check=False,
    )


def dispatch(subagent_type: str | None) -> subprocess.CompletedProcess[str]:
    tool_input: dict[str, str] = {"prompt": "do the batch"}
    if subagent_type is not None:
        tool_input["subagent_type"] = subagent_type
    return run_guard(json.dumps({"tool_name": "Agent", "tool_input": tool_input}))


@pytest.mark.parametrize("agent", ["test-engineer", "app-developer", "refactorer"])
def test_allows_dispatching_the_triad(agent: str) -> None:
    result = dispatch(agent)

    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(
    "agent",
    [
        "general-purpose",
        "Explore",
        "Plan",
        "reviewer",
        "architect",
        "project-manager",
        "engineering-manager",
        "Test-Engineer",
        " test-engineer",
    ],
)
def test_blocks_any_other_agent(agent: str) -> None:
    result = dispatch(agent)

    assert result.returncode == 2
    assert "test-engineer" in result.stderr


def test_blocks_a_dispatch_with_no_agent_type() -> None:
    result = dispatch(None)

    assert result.returncode == 2


@pytest.mark.parametrize("payload", ["", "not json", "[]", '{"tool_input": "x"}'])
def test_blocks_input_it_cannot_read(payload: str) -> None:
    result = run_guard(payload)

    assert result.returncode == 2
