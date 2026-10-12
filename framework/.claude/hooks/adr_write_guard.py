#!/usr/bin/env python3
"""PreToolUse hook: let the architect write only Markdown files in docs/adr/.

The architect declares this hook in its frontmatter for Write and Edit. Any
other path, a path outside the project, or input that cannot be read blocks
the write.
"""

import json
import os
import sys
from pathlib import Path

ADR_DIR = Path("docs") / "adr"


def deny(message: str) -> int:
    print(f"Blocked: {message}", file=sys.stderr)
    return 2


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return deny("unreadable hook input; refusing the write to docs/adr/.")

    tool_input = payload.get("tool_input") if isinstance(payload, dict) else None
    target = tool_input.get("file_path") if isinstance(tool_input, dict) else None
    if not isinstance(target, str) or not target:
        return deny("no file_path in the tool input; refusing the write to docs/adr/.")

    project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())).resolve()
    target_path = Path(target)
    if not target_path.is_absolute():
        target_path = project_dir / target_path
    target_path = target_path.resolve()

    try:
        relative = target_path.relative_to(project_dir / ADR_DIR)
    except ValueError:
        relative = None

    if relative is None or target_path.suffix != ".md":
        return deny(
            f"the architect may write only .md files under {ADR_DIR.as_posix()}/ "
            f"(got {target}). Return the content as text instead."
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
