# Framework backlog

Status: `todo`, `doing`, `done`, `dropped`. Newest decisions are recorded in the item. Done items stay, so the history is visible. Within each section, order is priority.

IDs continue from the project where the framework was first built, so lessons and history trace back to their source.

## Todo

### FW-12 Agents that check each other

Status: `doing`. From an evaluation of how the agents work as a team: the main session verifies the engineering manager's report, the reviewer reviews every feature before its PR, decisions are recorded in each plan's `## Decisions` and reach the agents that need them, conformance tests are derived from the spec before the implementation is read, the architect recommends structure for scopes that set it and is the only author of ADRs, and every agent's tools are guarded and tested. Spec in [`specs/FW-12-agent-teamwork.md`](specs/FW-12-agent-teamwork.md).

### FW-10 Retrospective after each feature

A fixed step in the done criteria, not a Claude Code hook. After the manager reports `DONE`, the main session reviews the manager's report, the branch's commit history, and the checkpoint doc.

- Start from counts in git history, not self-report: batches split, GREEN attempts per batch, invalid REDs sent back, lane violations, escalations, and sweep rounds to `NO NEW FAILURES`. Track them across features so a process change can be shown to help.
- One round of questions to the manager, relayed by the main session, which resumes the manager with its run context.
- Output: lessons in `lessons.md`, and at most three proposed backlog items, each with its evidence. The human approves each before it becomes `todo`.

### FW-06 Process agent

An agent that works this backlog: records lessons, writes framework specs, and proposes changes for human approval. Lane: `framework/.claude/agents/`, the loop rules in `framework/CLAUDE.md`, and 007's `docs/`. Never `framework/.claude/hooks/` or settings. When it's built, FW-10 dispatches it.

### FW-02 Engineering manager, phase 2: parallel triads

Up to three triads, each in its own git worktree and branch, merged by the manager after `./scripts/check` passes. Start only after the single-triad loop has run a feature cleanly in this project.

Known blocker: `lane_guard.py` resolves paths against `$CLAUDE_PROJECT_DIR` and blocks anything outside it, so a triad writing in a separate worktree would be blocked or checked against the wrong tree. Hook changes are the human's to make.

## Done

### FW-11 007 bootstrap tool

Status: `done`. `bin/007`, a small command like `rails new`: `007 new <dir>`, `007 init`, and `007 remove`. It copies the framework files, never overwrites, records `.007-version`, and prints the setup steps; `remove` deletes the files that still match that version. `new` and `init` shipped in v0.1.0; `remove`, and refusing a dirty checkout or a blocked directory, came in PR #1. Decided in [ADR-001](adr/ADR-001-007-tool.md) (Amendments 2 and 3); spec in [`specs/FW-11-007-tool.md`](specs/FW-11-007-tool.md). Follow-ups are in the spec's "Later, if needed".
