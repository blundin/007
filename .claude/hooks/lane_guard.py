#!/usr/bin/env python3
"""PreToolUse hook: block Write/Edit calls outside the active TDD lane.

Each loop subagent declares this hook in its frontmatter and passes its lane,
`test` or `src`, as the first argument. The paths each lane allows come from
`.claude/lanes.json`, a map of lane name to path prefixes that end in `/`.
A missing or invalid lanes file, or an unknown lane, blocks every write.

This guards only file-editing tools. Writes made through Bash are caught by
the coordinator's diff check, which remains the real backstop.
"""

import json
import os
import sys
from pathlib import Path

LANES_FILE = Path(".claude") / "lanes.json"


def load_lanes(project_dir: Path) -> dict[str, tuple[str, ...]] | None:
    try:
        raw = json.loads((project_dir / LANES_FILE).read_text())
    except (OSError, ValueError):
        return None
    if not isinstance(raw, dict):
        return None

    lanes: dict[str, tuple[str, ...]] = {}
    for name, prefixes in raw.items():
        if not isinstance(prefixes, list) or not prefixes:
            return None
        if not all(isinstance(p, str) and p.endswith("/") for p in prefixes):
            return None
        lanes[name] = tuple(prefixes)
    return lanes


def main() -> int:
    payload = json.load(sys.stdin)
    tool_input = payload.get("tool_input", {})
    target = tool_input.get("file_path") or tool_input.get("notebook_path")
    if not target:
        return 0

    project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())).resolve()
    lanes = load_lanes(project_dir)
    if lanes is None:
        print(
            f"Blocked: {LANES_FILE} is missing or invalid. It must map each lane "
            'to a list of path prefixes ending in "/".',
            file=sys.stderr,
        )
        return 2

    lane = sys.argv[1] if len(sys.argv) > 1 else ""
    allowed = lanes.get(lane)
    if allowed is None:
        print(f"Blocked: unknown TDD lane '{lane}'.", file=sys.stderr)
        return 2

    target_path = Path(target)
    if not target_path.is_absolute():
        target_path = project_dir / target_path
    target_path = target_path.resolve()

    try:
        relative = target_path.relative_to(project_dir).as_posix()
    except ValueError:
        print(f"Blocked: {target} is outside the project.", file=sys.stderr)
        return 2

    if not relative.startswith(allowed):
        print(
            f"Blocked: the active TDD lane is '{lane}', which allows writes only "
            f"under {', '.join(allowed)}. You attempted to write {relative}. "
            "Stay in your lane and report to the coordinator if you need "
            "changes elsewhere.",
            file=sys.stderr,
        )
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
