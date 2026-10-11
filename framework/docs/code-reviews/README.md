# Code reviews

Findings from every loop run and review session, kept by the `review-tracker` skill (`.claude/skills/review-tracker/SKILL.md`).

- `<timestamp>-<project>-<branch>.json`: one session file per review or feature run, with every finding and its status.
- `known-issues.json`: generated from the session files; only findings that are still `open` or `acknowledged`, highest severity first.

The main session records the engineering manager's `Findings` block here, one session file per feature run, and marks a finding `fixed` with its commit sha when the batch that fixes it lands. GREEN dispatches name this folder's `known-issues.json`, so the app-developer knows which findings are targets.
