import re
from pathlib import Path

import pytest

AGENTS_DIR = Path(__file__).resolve().parent.parent.parent / "agents"

FILE_TOOLS = ["Write", "Edit", "MultiEdit", "NotebookEdit"]

LANES = {"test-engineer": "test", "app-developer": "src", "refactorer": "src"}

# Commits checkpoints, so it can't be held to read-only git.
GIT_WRITERS = {"engineering-manager"}

READ_ONLY_AGENTS = ["project-manager", "reviewer"]


def frontmatter(agent: str) -> list[str]:
    lines = (AGENTS_DIR / f"{agent}.md").read_text().splitlines()
    end = lines.index("---", 1)
    return lines[1:end]


def tools(agent: str) -> set[str]:
    for line in frontmatter(agent):
        if line.startswith("tools:"):
            return {tool.strip() for tool in line.split(":", 1)[1].split(",")}
    return set()


def hooks(agent: str) -> list[tuple[str, list[str]]]:
    entries: list[tuple[str, list[str]]] = []
    for line in frontmatter(agent):
        matcher = re.match(r'\s*- matcher: "(.*)"$', line)
        command = re.match(r"\s*command: (.*)$", line)
        if matcher:
            entries.append((matcher.group(1), []))
        elif command and entries:
            entries[-1][1].append(command.group(1))
    return entries


def commands_for(agent: str, tool: str) -> list[str]:
    return [
        command
        for matcher, commands in hooks(agent)
        if re.fullmatch(matcher, tool)
        for command in commands
    ]


def all_agents() -> list[str]:
    return sorted(path.stem for path in AGENTS_DIR.glob("*.md"))


def agents_with(*names: str) -> list[str]:
    return [agent for agent in all_agents() if tools(agent) & set(names)]


@pytest.mark.parametrize(
    "agent", [a for a in agents_with("Bash") if a not in GIT_WRITERS]
)
def test_every_agent_with_bash_runs_the_git_guard(agent: str) -> None:
    commands = commands_for(agent, "Bash")

    assert any("hooks/git_guard.py" in command for command in commands), agent


@pytest.mark.parametrize("agent", agents_with(*FILE_TOOLS))
@pytest.mark.parametrize("tool", FILE_TOOLS)
def test_every_file_writing_agent_guards_every_file_tool(agent: str, tool: str) -> None:
    commands = commands_for(agent, tool)

    assert any(
        "hooks/lane_guard.py" in command or "hooks/adr_write_guard.py" in command
        for command in commands
    ), f"{agent} does not guard {tool}"


@pytest.mark.parametrize("agent", sorted(LANES))
def test_each_triad_agent_is_held_to_its_own_lane(agent: str) -> None:
    commands = commands_for(agent, "Write")

    assert any(
        command.endswith(f'hooks/lane_guard.py" {LANES[agent]}') for command in commands
    ), agent


@pytest.mark.parametrize("agent", READ_ONLY_AGENTS)
def test_read_only_agents_have_no_file_writing_tools(agent: str) -> None:
    assert not tools(agent) & set(FILE_TOOLS), agent


@pytest.mark.parametrize("agent", agents_with("Agent", "Task"))
def test_every_agent_that_dispatches_runs_the_agent_guard(agent: str) -> None:
    for tool in ["Agent", "Task"]:
        commands = commands_for(agent, tool)

        assert any("hooks/agent_guard.py" in c for c in commands), (agent, tool)


def test_only_the_engineering_manager_dispatches() -> None:
    assert agents_with("Agent", "Task") == ["engineering-manager"]


def test_the_project_manager_has_no_shell() -> None:
    assert "Bash" not in tools("project-manager")


def test_every_agent_is_covered_by_these_checks() -> None:
    assert all_agents() == [
        "app-developer",
        "architect",
        "engineering-manager",
        "project-manager",
        "refactorer",
        "reviewer",
        "test-engineer",
    ]
