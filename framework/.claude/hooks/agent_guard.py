#!/usr/bin/env python3
"""PreToolUse hook: let the engineering manager dispatch only its triad.

The engineering manager declares this hook in its frontmatter for the Agent
tool. Claude Code ignores a subagent's `Agent(...)` type list, so without this
it could dispatch an agent that no lane or git hook guards. A missing or
unknown agent type, or input that cannot be read, blocks the dispatch.
"""

import json
import sys

TRIAD = ("test-engineer", "app-developer", "refactorer")


def deny(message: str) -> int:
    print(f"Blocked: {message}", file=sys.stderr)
    return 2


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return deny("unreadable hook input; refusing the dispatch.")

    tool_input = payload.get("tool_input") if isinstance(payload, dict) else None
    agent = tool_input.get("subagent_type") if isinstance(tool_input, dict) else None
    if agent not in TRIAD:
        return deny(
            f"the engineering manager may dispatch only {', '.join(TRIAD)} "
            f"(got {agent!r}). Report to the main session if you need anything else."
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
