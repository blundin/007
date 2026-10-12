# Plans

One plan per scope, `docs/plans/<scope>.md`. The `project-manager` returns the plan as text; the main session writes it here after the human approves the scope, and commits it on the feature branch.

The main session owns each plan's status line:

- `Status: planned` when the plan is written
- `building (<branch>)` when the engineering manager is dispatched
- `blocked (<question>)` when the manager reports `BLOCKED`
- `done (PR #<n>)` when the human merges the PR

Each plan ends with `## Decisions`: every question the human has answered for this scope, from the project manager, the engineering manager, or a subagent, with the answer and the date. The main session appends them, and agents cite them instead of asking again.

The project manager treats any criterion a plan claims as delivered or in flight, whatever its status, and never proposes it again.
