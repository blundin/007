# Changelog

Changes to `framework/` and `bin/007` that an adopter would notice. Versions are git tags; `git diff <old>..<new> -- framework/` shows the full change.

## Unreleased

- Added the `architect` agent. It recommends one option and records ADRs in `docs/adr/`. The new `adr_write_guard.py` hook limits it to Markdown files there.
- Added the `reviewer` agent, an independent code reviewer that records findings through the `review-tracker` skill.
- Neither agent is part of the loop in `CLAUDE.md`; the main session or the human dispatches them.
- Added `docs/adr/README.md`, and listed `docs/adr/` in the `AGENTS.md` Layout.
- Unwrapped the Markdown files so each paragraph and list item is one line. The wording is unchanged.
- Added `bin/007 remove`. It deletes the framework files that still match the commit in `.007-version` and lists the ones you've changed.
- `bin/007 new` and `init` now refuse to copy while `framework/` has uncommitted changes, so `.007-version` always matches what was copied.
- `bin/007 init` now refuses up front, writing nothing, when a file stands where the framework needs a directory. It used to crash partway through the copy.

## v0.1.0 (2026-10-05)

- Added `bin/007 new` and `bin/007 init`, which copy the framework into a new or existing repo.
- Moved the framework into `framework/`. Adopters get the same files.
- Stopped shipping `docs/dev-framework/README.md`. The framework's backlog and lessons live in 007's own `docs/`.

## Baseline

Extracted from the framework's first project at `319e93c`.
