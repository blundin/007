# 007: Adversarial TDD Loop template

A Claude Code project template that builds software from specs with a team of
agents that check each other's work. A test engineer tries to prove the code
fails its spec, a developer writes the minimum code that passes, and a
refactorer cleans up with tests locked. Each one is held to its own folder by
hooks, and the coordinator verifies every phase before it commits.

It works with any language. Each project fills in three scripts and a short
profile, and the loop does the rest.

## How it works

    human ── approves scopes, answers questions, merges PRs
      │
    main session ── plans with the PM, dispatches the EM, records findings
      ├── project-manager      what to build next; cites the spec; read-only
      └── engineering-manager  runs a scope to done; never writes code
            ├── test-engineer  RED: failing tests        (test lane)
            ├── app-developer  GREEN: minimum code       (src lane)
            └── refactorer     REFACTOR: structure only  (src lane)

Every batch goes RED, GREEN, REFACTOR, with a checkpoint commit after each
phase and a diff check after every dispatch. The rules are in `CLAUDE.md`
(the loop) and `AGENTS.md` (rules for every contributor, plus the Project
profile).

## Requirements

- Claude Code
- `python3`, which runs the hooks whatever the project's language
- `uv`, for `./scripts/check-dev-framework` (the hooks' own tests)
- `perl`, for the agents' ASCII check
- `gh`, if you want the main session to open PRs

## Adopting

1. **Copy the template.** On GitHub, use "Use this template". Locally, copy
   the folder and run `git init`.
2. **Set the lanes.** Edit `.claude/lanes.json` so `src` and `test` list the
   path prefixes each lane may write, each ending in `/`. A Rails app might
   use `{"test": ["spec/"], "src": ["app/", "lib/"]}`.
3. **Write the three scripts.** Replace the placeholder bodies:
   - `scripts/check`: the full gate (lint, format, strict types, every test,
     coverage). Exit 0 only if everything passes. CI should run it too.
   - `scripts/test <paths>`: run the named tests and print each outcome, in a
     way that tells a failed test from an errored one.
   - `scripts/lint <paths>`: lint, format-check, and type-check the named
     files.
4. **Fill in the Project profile.** In `AGENTS.md`, replace every
   `<!-- FILL ... -->` marker (`grep -n FILL AGENTS.md`). Each one has an
   example from a Python library.
5. **Check the settings.** `.claude/settings.json` puts `git commit` on the
   `ask` list, so every commit stops and asks first. That's for signed commits
   whose key has to be unlocked, such as 1Password's SSH agent. If you don't
   sign commits, move it to `allow`.
6. **Run the framework check.** `./scripts/check-dev-framework` should pass.
7. **Write a spec** in `docs/specs/` with criterion IDs (see its README).
8. **Start a session** and ask what's next. The main session dispatches the
   project manager, shows you the proposed scope and its questions, and
   waits for your approval before building anything.

## What's in here

| Path | Contents |
|---|---|
| `CLAUDE.md` | The Adversarial TDD Loop: roles, phases, diff check, triage, done criteria |
| `AGENTS.md` | Rules for every contributor, and the Project profile |
| `.claude/agents/` | The five agent definitions |
| `.claude/hooks/` | `lane_guard.py`, `git_guard.py`, and their tests |
| `.claude/lanes.json` | Lane paths |
| `.claude/settings.json` | Permissions |
| `.claude/skills/review-tracker/` | Records findings in `docs/code-reviews/` |
| `scripts/` | `check`, `test`, `lint` (yours to fill in), and `check-dev-framework` |
| `docs/specs/`, `docs/plans/`, `docs/code-reviews/` | Specs, scope plans, findings |
| `docs/dev-framework/` | The framework's own backlog and lessons |

## Provenance

- Extracted from Snakestone (`TheAustinStone/snakestone`) at `319e93c`,
  following its spec `docs/dev-framework/specs/FW-08-extract-framework.md`.
- `review-tracker` is vendored from `blundin/code-review-issue-tracker` at
  `03fc0be` (MIT). If you also have it installed as a personal skill, the
  two copies share a name. Keep them in sync, or remove one.
- The two projects are separate. A lesson learned in one is applied to the
  other by hand.
