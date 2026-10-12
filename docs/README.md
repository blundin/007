# 007 docs

This folder tracks 007 as its own project: the framework in `framework/` and the `bin/007` command that installs and removes it. It holds the backlog, lessons, decision records, and specs. Nothing here is copied into projects; what ships is in `framework/`.

## Who does framework work

The main session, with the human, driven by items in [`backlog.md`](backlog.md) and working test-first. The triad builds products, not the framework.

## Files

- [`backlog.md`](backlog.md): framework work items and their status.
- [`lessons.md`](lessons.md): what running the framework has taught us, with the source of each lesson.
- `adr/`: decision records.
- `specs/`: specs for framework changes, written before the change is made.

## Rules

- Framework changes are proposed, then approved by the human before they land.
- `framework/.claude/hooks/` and `framework/.claude/settings.json` change only by the human's hand or with the human's explicit approval.
- Lessons come from evidence: a checkpoint, a manager report, or the human's feedback. Each lesson names its source.
- `./scripts/check` at the repo root runs every gate: `bin/007`'s lint, types, and tests, then the hooks' own `framework/scripts/check-dev-framework`.
- Any change an adopter would notice gets an entry under `Unreleased` in `CHANGELOG.md`.
