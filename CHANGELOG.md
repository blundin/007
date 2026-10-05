# Changelog

Changes to `framework/` that an adopter would notice. Versions are git tags;
`git diff <old>..<new> -- framework/` shows the full change.

## Unreleased

- Added `bin/007 new` and `bin/007 init`, which copy the framework into a
  new or existing repo.
- Moved the framework into `framework/`. Adopters get the same files.
- Stopped shipping `docs/dev-framework/README.md`. The framework's backlog
  and lessons live in 007's own `docs/`.

## Baseline

Extracted from Snakestone at `319e93c`.
