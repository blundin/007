# Changelog

Changes to `framework/` and `bin/007` that an adopter would notice. Versions are git tags; `git diff <old>..<new> -- framework/` shows the full change.

## Unreleased

- Added the `architect` agent. It recommends one option and records ADRs in `docs/adr/`. The new `adr_write_guard.py` hook limits it to Markdown files there.
- Added the `reviewer` agent, an independent code reviewer that records findings through the `review-tracker` skill.
- Neither agent is part of the batch loop; the main session dispatches them (see below), or the human does.
- Added `docs/adr/README.md`, and listed `docs/adr/` in the `AGENTS.md` Layout.
- Unwrapped the Markdown files so each paragraph and list item is one line. The wording is unchanged.
- Added `bin/007 remove`. It deletes the framework files that still match the commit in `.007-version` and lists the ones you've changed.
- `bin/007 new` and `init` now refuse to copy while `framework/` has uncommitted changes, so `.007-version` always matches what was copied.
- `bin/007 init` now refuses up front, writing nothing, when a file stands where the framework needs a directory. It used to crash partway through the copy.

- The main session now verifies an engineering manager's `DONE` report before treating it as done: `./scripts/check`, the criterion grep for every covered ID, and a RED-before-GREEN checkpoint for every batch in `git log`.
- The `reviewer` now reviews every feature branch after a verified `DONE` and before the PR. Blockers and Majors go back to the engineering manager as a new batch, followed by one re-review of the new commits.
- The `reviewer` returns findings instead of writing them, with its severities mapped to `review-tracker`'s. The main session records them. It no longer preloads the `review-tracker` skill.
- Each plan in `docs/plans/` ends with a `## Decisions` section recording the human's answers. Triage and the agents cite it in place of the old "checkpoint docs".
- The engineering manager now receives the plan, and each RED dispatch gives the test engineer the exact criterion text and the relevant decisions.
- In conformance mode, the test engineer derives tests from the spec and public signatures before reading the implementation. At RED, the engineering manager checks each assertion against the quoted criterion.
- Design questions go to the `architect` before the human, and an accepted recommendation becomes an ADR.

## v0.1.0 (2026-10-05)

- Added `bin/007 new` and `bin/007 init`, which copy the framework into a new or existing repo.
- Moved the framework into `framework/`. Adopters get the same files.
- Stopped shipping `docs/dev-framework/README.md`. The framework's backlog and lessons live in 007's own `docs/`.

## Baseline

Extracted from the framework's first project at `319e93c`.
