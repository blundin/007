#!/usr/bin/env python3
"""PreToolUse hook: block Write/Edit calls outside the active TDD lane.

Each loop subagent declares this hook in its frontmatter and passes its lane,
`test` or `src`, as the first argument. The paths each lane allows come from
`.claude/lanes.json`, a map of lane name to a list of entries. An entry that
ends in `/` allows everything under that directory; any other entry allows
exactly that one file. Entries are relative to the project, with no `..`.
A missing or invalid lanes file, an unknown lane, or hook input that cannot be
read blocks every write.

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
        if not all(valid_entry(p) for p in prefixes):
            return None
        lanes[name] = tuple(prefixes)
    return lanes


def valid_entry(entry: object) -> bool:
    if not isinstance(entry, str) or not entry or entry.startswith("/"):
        return False
    return ".." not in entry.split("/")


def in_lane(relative: str, entries: tuple[str, ...]) -> bool:
    return any(
        relative.startswith(e) if e.endswith("/") else relative == e for e in entries
    )


def deny(message: str) -> int:
    print(f"Blocked: {message}", file=sys.stderr)
    return 2


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return deny("unreadable hook input; refusing the write.")

    tool_input = payload.get("tool_input", {}) if isinstance(payload, dict) else None
    if not isinstance(tool_input, dict):
        return deny("no readable tool input; refusing the write.")
    target = tool_input.get("file_path") or tool_input.get("notebook_path")
    if not target:
        return 0
    if not isinstance(target, str):
        return deny("the target path is not a string; refusing the write.")

    project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())).resolve()
    lanes = load_lanes(project_dir)
    if lanes is None:
        print(
            f"Blocked: {LANES_FILE} is missing or invalid. It must map each lane "
            'to a list of relative paths: directories ending in "/", or files.',
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

    if not in_lane(relative, allowed):
        print(
            f"Blocked: the active TDD lane is '{lane}', which allows writes only "
            f"to {', '.join(allowed)}. You attempted to write {relative}. "
            "Stay in your lane and report to the coordinator if you need "
            "changes elsewhere.",
            file=sys.stderr,
        )
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
