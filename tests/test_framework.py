import re
from pathlib import Path

FRAMEWORK = Path(__file__).resolve().parent.parent / "framework"
FIELD = re.compile(r"^- \*\*(.+?):\*\*")


def test_the_shipped_profile_leaves_every_field_for_setup_to_fill() -> None:
    text = (FRAMEWORK / "AGENTS.md").read_text()
    section = text.split("## Project profile", 1)[1]
    lines = [line for line in section.splitlines() if FIELD.match(line)]

    assert len(lines) >= 10
    for line in lines:
        assert "<!-- FILL" in line, line
