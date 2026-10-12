#!/usr/bin/env python3
"""PreToolUse hook: block git commands that change state inside a loop subagent.

Each loop subagent declares this hook in its frontmatter for the Bash tool.
Git state belongs to the coordinator, whose checkpoint commits the diff check
compares against, so subagents may run only read-only git subcommands.

This is a best-effort text match, not a shell parser. It fails closed on git
invocations it can't read, and the coordinator's HEAD and stash checks remain
the backstop.
"""

import json
import re
import sys

READ_ONLY = {"status", "diff", "log", "show", "ls-files", "grep", "blame", "rev-parse"}

# Subcommands that are read-only only with one action, as in `git stash list`.
READ_ONLY_ACTIONS = {"stash": "list"}

# Global options that take their value as the next word, as in `git -C <path>`.
# Any other option is read as a single word, so an unlisted option that takes a
# separate value makes the value read as the subcommand, which fails closed.
VALUE_OPTIONS = r"(?:-C|-c|--git-dir|--work-tree|--namespace|--config-env)"

# A `git` word at a command boundary or after a path, as in `/usr/bin/git`,
# then any leading options, then the subcommand. The word after it is peeked
# at, not consumed, so a following `;git` still starts its own match.
GIT_INVOCATION = re.compile(
    rf"(?:^|[\s;&|(`$'\"/])git\s+((?:{VALUE_OPTIONS}\s+\S+\s+|-\S+\s+)*)(\S+)"
    r"(?=(?:\s+(\S+))?)"
)


def deny(message: str) -> int:
    print(f"Blocked: {message}", file=sys.stderr)
    return 2


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return deny("unreadable hook input; refusing the command.")

    tool_input = payload.get("tool_input", {}) if isinstance(payload, dict) else None
    command = tool_input.get("command", "") if isinstance(tool_input, dict) else None
    if not isinstance(command, str):
        return deny("no readable command in the tool input; refusing it.")

    for match in GIT_INVOCATION.finditer(command):
        subcommand, action = match.group(2), match.group(3)
        allowed_action = READ_ONLY_ACTIONS.get(subcommand)
        read_only_action = allowed_action is not None and action == allowed_action
        if subcommand not in READ_ONLY and not read_only_action:
            print(
                f"Blocked: `git {subcommand}` is not allowed for loop subagents. "
                f"Only read-only git commands are permitted: "
                f"{', '.join(sorted(READ_ONLY))}. Git state belongs to the "
                "coordinator; report to it if you need a change.",
                file=sys.stderr,
            )
            return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
