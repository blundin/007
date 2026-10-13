# Changelog

Changes to `framework/` and `bin/007` that an adopter would notice. Versions are git tags; `git diff <old>..<new> -- framework/` shows the full change.

## Unreleased

- `./scripts/check-dev-framework` passes in a project whose Project profile is filled. `test_setup_skill.py` required every profile line to keep its `<!-- FILL` marker, so it failed after `/007-setup` ran; it now checks only the lines still unfilled.

## v1.0.0 (2026-10-12)

The baseline release. Earlier history was folded into this one commit, so `.007-version` files from before it no longer resolve: reinstall those projects from v1.0.0.

- `bin/007 new`, `init`, and `remove`: copy the framework into a new or existing repo, never overwriting a file, and record the commit in `.007-version`; `remove` deletes the files still unchanged since install. `init` refuses a dirty framework checkout, a file where a directory is needed, and a repo where `.007-version` already exists.
- Seven agents. `project-manager` and `architect` plan; `engineering-manager` runs each scope in RED, GREEN, REFACTOR batches with its triad, `test-engineer`, `app-developer`, and `refactorer`; `reviewer` reviews the whole branch once per scope before the PR.
- The main session verifies every `DONE` report, diff-checks every dispatch including the reviewer's, records the human's answers in each plan's `## Decisions`, and takes design questions to the architect, which writes an ADR only after the human decides.
- Hooks: `lane_guard.py`, `git_guard.py`, `adr_write_guard.py`, and `agent_guard.py`, which block anything they can't read. `test_agent_wiring.py` checks every agent's tools against its hooks.
- `/007-setup` drafts the Project profile, lanes, and scripts from the repo for approval, and checks them for drift on later runs. Its reference explains every item, with examples for a Python library, a Rails app, and a Swift app.
- `review-tracker`, vendored, records findings in `docs/code-reviews/`.
