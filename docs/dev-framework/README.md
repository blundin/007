# Development framework

This project is built by the Adversarial TDD Loop: the project manager, the
engineering manager and its triad, the lane and git hooks, and the rules in
`CLAUDE.md` and `AGENTS.md`. This folder tracks the framework as its own
project, separate from the product.

## Two kinds of work

| | Product work | Framework work |
|---|---|---|
| Who | `engineering-manager` and its triad | The main session, with the human |
| Lane | the `src` and `test` lanes | `.claude/agents/`, the loop rules in `CLAUDE.md`, this folder |
| Driven by | Criterion IDs in `docs/specs/` | Items in [`backlog.md`](backlog.md) |

## Files

- [`backlog.md`](backlog.md): framework work items and their status.
- [`lessons.md`](lessons.md): what running the framework has taught us, with
  the source of each lesson.
- `specs/`: specs for framework changes, written before the change is made.

## Rules

- Framework changes are proposed, then approved by the human before they land.
- `.claude/hooks/` and `.claude/settings.json` change only by the human's hand.
- Lessons come from evidence: a checkpoint, a manager report, or the human's
  feedback. Each lesson names its source.
- The hooks have their own gate, `./scripts/check-dev-framework`, separate
  from the product's `./scripts/check`.
