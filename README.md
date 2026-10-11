# 007: The Agentic Deveopment Framework

A Claude Code project template that builds software from specs with a team of agents that check each other's work. A test engineer tries to prove the code fails its spec, a developer writes the minimum code that passes, and a refactorer cleans up with tests locked. Each one is held to its own folder by hooks, and the coordinator verifies every phase before it commits.

It works with any language. Each project fills in three scripts and a short profile, and the loop does the rest.

## How it works

    human ── approves scopes, answers questions, merges PRs
      │
    main session ── plans with the PM, dispatches the EM, records findings
      ├── project-manager      what to build next; cites the spec; read-only
      └── engineering-manager  runs a scope to done; never writes code
            ├── test-engineer  RED: failing tests        (test lane)
            ├── app-developer  GREEN: minimum code       (src lane)
            └── refactorer     REFACTOR: structure only  (src lane)

Every batch goes RED, GREEN, REFACTOR, with a checkpoint commit after each phase and a diff check after every dispatch. The rules are in `CLAUDE.md` (the loop) and `AGENTS.md` (rules for every contributor, plus the Project profile).

## Requirements

- Claude Code
- `python3`, which runs the hooks whatever the project's language
- `uv`, for `./scripts/check-dev-framework` (the hooks' own tests)
- `perl`, for the agents' ASCII check
- `gh`, if you want the main session to open PRs

## Adopting

1. **Copy the framework** with `bin/007`. Install it once by cloning this repo and linking the command onto your `PATH`:

       git clone git@github.com:TheAustinStone/007.git ~/tools/007
       ln -s ~/tools/007/bin/007 ~/.local/bin/007

   Then, for each project:

       007 new myapp    # new directory, git init, copy
       007 init         # into the current repo, from its top level
       007 remove       # take it out again, from the top level

   The clone is the installed version. To pin a release, check out its tag (`git -C ~/tools/007 checkout v0.1.0`); to upgrade, pull or check out a newer tag, and read `CHANGELOG.md` for what changed. `007` refuses to copy while `framework/` has uncommitted changes, since `.007-version` records the commit, not local edits.

   It never overwrites a file. Anything that already exists is skipped and listed. For `CLAUDE.md`, `AGENTS.md`, `.claude/settings.json`, and `.gitignore`, it names the file to merge by hand. It records the 007 commit it copied from in `.007-version`.

   `007 remove` uses that commit to find the framework files. It deletes the ones that still match it, and keeps and lists any you've changed, such as a filled-in `AGENTS.md`. Your clone needs that commit. Any clone of the repo you installed from has it, whatever tag is checked out. Nothing is committed.
2. **Set the lanes.** Edit `.claude/lanes.json` so `src` and `test` list the path prefixes each lane may write, each ending in `/`. A Rails app might use `{"test": ["spec/"], "src": ["app/", "lib/"]}`.
3. **Write the three scripts.** Replace the placeholder bodies:
   - `scripts/check`: the full gate (lint, format, strict types, every test, coverage). Exit 0 only if everything passes. CI should run it too.
   - `scripts/test <paths>`: run the named tests and print each outcome, in a way that tells a failed test from an errored one.
   - `scripts/lint <paths>`: lint, format-check, and type-check the named files.
4. **Fill in the Project profile.** In `AGENTS.md`, replace every `<!-- FILL ... -->` marker (`grep -n FILL AGENTS.md`). Each one has an example from a Python library.
5. **Check the settings.** `.claude/settings.json` puts `git commit` on the `ask` list, so every commit stops and asks first. That's for signed commits whose key has to be unlocked, such as 1Password's SSH agent. If you don't sign commits, move it to `allow`.
6. **Run the framework check.** `./scripts/check-dev-framework` should pass.
7. **Write a spec** in `docs/specs/` with criterion IDs (see its README).
8. **Start a session** and ask what's next. The main session dispatches the project manager, shows you the proposed scope and its questions, and waits for your approval before building anything.

## What's in here

| Path | Contents |
|---|---|
| `framework/` | Everything that lands in a project. `bin/007` copies every tracked file in it, so adding a file here ships it |
| `bin/007` | The copy command |
| `tests/` | The copy command's tests |
| `scripts/check` | 007's single gate: the copy command's checks, then the framework's hook checks |
| `docs/` | 007's own backlog, lessons, decision records, and specs. Never copied |
| `CHANGELOG.md` | What changed in the framework, by version |

Inside `framework/`:

| Path | Contents |
|---|---|
| `CLAUDE.md` | The Adversarial TDD Loop: roles, phases, diff check, triage, done criteria |
| `AGENTS.md` | Rules for every contributor, and the Project profile |
| `.claude/agents/` | The seven agent definitions: the five loop agents, plus `architect` and `reviewer`, which run outside the loop |
| `.claude/hooks/` | `lane_guard.py`, `git_guard.py`, `adr_write_guard.py`, and their tests |
| `.claude/lanes.json` | Lane paths |
| `.claude/settings.json` | Permissions |
| `.claude/skills/review-tracker/` | Records findings in `docs/code-reviews/` |
| `scripts/` | `check`, `test`, `lint` (yours to fill in), and `check-dev-framework` |
| `docs/specs/`, `docs/plans/`, `docs/code-reviews/`, `docs/adr/` | Specs, scope plans, findings, decision records |

## Changing the framework

1. Change files under `framework/` on a branch. Framework changes follow the rules in [`docs/README.md`](docs/README.md).
2. Run `./scripts/check`.
3. Add an entry under `Unreleased` in `CHANGELOG.md` for anything an adopter would notice.
4. To release, move the `Unreleased` entries under a new version heading and tag it (`git tag v0.2.0`). `git diff v0.1.0..v0.2.0 -- framework/` shows adopters exactly what changed.

## Provenance

- Extracted from Snakestone (`TheAustinStone/snakestone`) at `319e93c`, following its spec `docs/dev-framework/specs/FW-08-extract-framework.md`.
- `review-tracker` is vendored from `blundin/code-review-issue-tracker` at `03fc0be` (MIT). If you also have it installed as a personal skill, the two copies share a name. Keep them in sync, or remove one.
- The two projects are separate. A lesson learned in one is applied to the other by hand.
