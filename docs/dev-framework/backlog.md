# Framework backlog

Status: `todo`, `doing`, `done`, `dropped`. Newest decisions are recorded in
the item. Done items stay, so the history is visible. Within each section,
order is priority.

IDs continue from Snakestone, where the framework was first built, so
lessons and history trace back to their source.

## Todo

### FW-10 Retrospective after each feature

A fixed step in the done criteria, not a Claude Code hook. After the manager
reports `DONE`, the main session reviews the manager's report, the branch's
commit history, and the checkpoint doc.

- Start from counts in git history, not self-report: batches split, GREEN
  attempts per batch, invalid REDs sent back, lane violations, escalations,
  and sweep rounds to `NO NEW FAILURES`. Track them across features so a
  process change can be shown to help.
- One round of questions to the manager, relayed by the main session, which
  resumes the manager with its run context.
- Output: lessons in `lessons.md`, and at most three proposed backlog items,
  each with its evidence. The human approves each before it becomes `todo`.

### FW-06 Process agent

An agent that works this backlog: records lessons, writes framework specs,
and proposes changes for human approval. Lane: `.claude/agents/`, the loop
rules in `CLAUDE.md`, and `docs/dev-framework/`. Never `.claude/hooks/` or
settings. When it's built, FW-10 dispatches it.

### FW-02 Engineering manager, phase 2: parallel triads

Up to three triads, each in its own git worktree and branch, merged by the
manager after `./scripts/check` passes. Start only after the single-triad
loop has run a feature cleanly in this project.

Known blocker: `lane_guard.py` resolves paths against `$CLAUDE_PROJECT_DIR`
and blocks anything outside it, so a triad writing in a separate worktree
would be blocked or checked against the wrong tree. Hook changes are the
human's to make.
