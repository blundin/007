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
- The `architect` now takes part where structure is decided. The project manager's report lists the structural decisions a scope forces, and the architect recommends each one before the scope is approved.
- The `architect` has two modes. In `recommend` it returns a draft and writes nothing; in `record` it writes the ADR as `accepted` after the human decides. It is the only author of ADRs.
- Each plan lists the ADRs that bear on its scope under `## ADRs`. The app developer works within them, and the refactorer counts drift from them as a smell.
- The `reviewer` marks design-drift findings `kind: design`. They go to the architect and, if accepted, to a structure-only refactor batch instead of a RED test.
- The engineering manager and the refactorer report structural decisions beyond their scope, for the architect.
- The main session opens the PR after the review. Finding statuses follow triage: `wont-fix` for triaged out, `acknowledged` for Minors and Nits, `fixed` with the commit sha.
- Added `agent_guard.py`. The engineering manager's `Agent` tool now runs it, so the manager can dispatch only the triad. Claude Code ignores a subagent's `Agent(...)` type list, so before this it could dispatch an agent no hook guards.
- The `reviewer` now runs `git_guard.py` on Bash, so it is held to read-only git.
- The `architect`'s write guard now matches `MultiEdit` and `NotebookEdit` as well as `Write` and `Edit`.
- Added `test_agent_wiring.py`, which checks every agent's tools against its hooks: shell users run the git guard, file writers run a write guard, and dispatchers run the agent guard.
- Renamed the "Adversarial TDD Loop" to the "TDD loop" in `CLAUDE.md` and the agent definitions. Adversarial testing is one mode of the test engineer, not the name of the framework.
- The reviewer's dispatch prompt is now fixed: the commit range, the spec path, and the plan path, never the builders' reports or reasoning. The reviewer doesn't read `docs/code-reviews/` session files, only `known-issues.json`.
- The reviewer now reads the spec and plan and checks spec conformance: unmet criteria, narrower readings, untagged tests, and unrequested behavior.
- `lane_guard.py` and `git_guard.py` now block hook input they can't read. Before, they crashed with exit 1, which Claude Code treats as a non-blocking error, so the call went through.
- `git_guard.py` now catches git run by path, such as `/usr/bin/git commit`.
- `bin/007 init` now refuses, writing nothing, when `.007-version` already exists. Run `007 remove` first; installing over an older version left files that `remove` couldn't account for.
- The main session runs the diff check after the reviewer, and any change it made is a violation.
- The `reviewer` and `architect` are no longer described as "use proactively". The reviewer runs once per scope, after a verified `DONE`. The architect works in `recommend` mode unless told `record`, and writes an ADR only in `record` mode, after the human decides.
- The test engineer's attack categories no longer include HTTP failures, retries, and pagination. They're now the example in the Project profile's `Domain attacks`, so an HTTP client lists them there and other projects don't mark them not applicable on every sweep.
- The architect's default product phase reads "most internal systems" instead of "most internal and ministry systems".
- The placeholder `scripts/check`, `test`, and `lint` point to `AGENTS.md`, Setup and checks, instead of a README section adopters don't have.
- The engineering manager no longer looks for an attribution trailer that nothing gave it.
- Agents may now edit a spec, but only when a human explicitly directs it and approves the specific change. `AGENTS.md`, `CLAUDE.md`, and `docs/specs/README.md` all say so.
- Removed the ASCII-only rule for files the test engineer, app developer, and refactorer write, along with its `perl` check. `perl` is no longer a requirement.
- `.claude/settings.json` now allows `git worktree`, which the loop's Setup step uses, and denies reading `.env` and `.env.*`.

## v0.1.0 (2026-10-05)

- Added `bin/007 new` and `bin/007 init`, which copy the framework into a new or existing repo.
- Moved the framework into `framework/`. Adopters get the same files.
- Stopped shipping `docs/dev-framework/README.md`. The framework's backlog and lessons live in 007's own `docs/`.

## Baseline

Extracted from the framework's first project at `319e93c`.
