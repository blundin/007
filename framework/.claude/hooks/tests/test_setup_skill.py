import re
from pathlib import Path

import pytest

FRAMEWORK = Path(__file__).resolve().parent.parent.parent.parent
SKILL_DIR = FRAMEWORK / ".claude" / "skills" / "007-setup"
FIELD = re.compile(r"^- \*\*(.+?):\*\*")

# Setup items that live outside the Project profile.
OTHER_ITEMS = ["lanes.json", "scripts/check", "scripts/test", "scripts/lint"]

STACKS = ["Python library", "Rails app", "Swift app"]


def profile_lines() -> list[str]:
    text = (FRAMEWORK / "AGENTS.md").read_text()
    section = text.split("## Project profile", 1)[1]
    return [line for line in section.splitlines() if FIELD.match(line)]


def profile_fields() -> list[str]:
    return [m.group(1) for line in profile_lines() if (m := FIELD.match(line))]


def reference_sections() -> dict[str, str]:
    text = (SKILL_DIR / "reference.md").read_text()
    parts = re.split(r"^### (.+)$", text, flags=re.MULTILINE)
    return {parts[i].strip(): parts[i + 1] for i in range(1, len(parts), 2)}


def frontmatter() -> list[str]:
    lines = (SKILL_DIR / "SKILL.md").read_text().splitlines()
    end = lines.index("---", 1)
    return lines[1:end]


def test_the_profile_has_fields_to_check() -> None:
    assert len(profile_fields()) >= 10


@pytest.mark.parametrize("item", [*profile_fields(), *OTHER_ITEMS])
def test_every_setup_item_has_a_reference_section(item: str) -> None:
    assert item in reference_sections()


@pytest.mark.parametrize("item", [*profile_fields(), *OTHER_ITEMS])
def test_every_reference_section_gives_an_example_for_each_stack(item: str) -> None:
    section = reference_sections().get(item, "")

    for stack in STACKS:
        assert f"*{stack}:*" in section, stack


@pytest.mark.parametrize("line", profile_lines())
def test_profile_fill_comments_point_to_the_skill_without_examples(
    line: str,
) -> None:
    assert "<!-- FILL" in line
    assert "/007-setup" in line
    assert "Example" not in line


def test_the_skill_is_named_and_runs_only_when_invoked() -> None:
    lines = frontmatter()

    assert "name: 007-setup" in lines
    assert "disable-model-invocation: true" in lines
