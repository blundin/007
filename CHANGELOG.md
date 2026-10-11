# Changelog

Changes to `framework/` that an adopter would notice. Versions are git tags; `git diff <old>..<new> -- framework/` shows the full change.

## Unreleased

- Added the `architect` agent. It recommends one option and records ADRs in `docs/adr/`. The new `adr_write_guard.py` hook limits it to Markdown files there.
- Added the `reviewer` agent, an independent code reviewer that records findings through the `review-tracker` skill.
- Neither agent is part of the loop in `CLAUDE.md`; the main session or the human dispatches them.
- Added `docs/adr/README.md`.
- Unwrapped the Markdown files so each paragraph and list item is one line. The wording is unchanged.

## v0.1.0 (2026-10-05)

- Added `bin/007 new` and `bin/007 init`, which copy the framework into a new or existing repo.
- Moved the framework into `framework/`. Adopters get the same files.
- Stopped shipping `docs/dev-framework/README.md`. The framework's backlog and lessons live in 007's own `docs/`.

## Baseline

Extracted from Snakestone at `319e93c`.
