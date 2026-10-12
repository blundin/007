# 007: The Agentic Development Framework

A framework for Claude Code that builds software from specs with a team of seven agents that check each other's work. A project manager turns the spec into ordered scopes, and an architect recommends any structure a scope sets and records the decision as an ADR. An engineering manager runs each scope in test-first batches with a triad: a test engineer tries to prove the code fails its spec, an app developer writes the minimum code that passes, and a refactorer cleans up with tests locked. A reviewer with no stake in the change checks the whole branch before it reaches you as a PR. Hooks hold each agent to what it may write, the engineering manager verifies every phase before it commits, and the main session verifies every report before trusting it. A small command, `bin/007`, puts the framework into a project and takes it out again.

It works with any language. Each project fills in three scripts and a short profile, and the loop does the rest.

## How it works

Each scope goes through four stages. The main session runs them and stops for you where marked.

    PLAN     project-manager      what to build next; cites the spec; read-only
             architect            recommends any structure the scope sets; the only author of ADRs
             ── you approve the scope and decide each design question
    BUILD    engineering-manager  runs the scope in batches; never writes code
               test-engineer      RED: failing tests        (test lane)
               app-developer      GREEN: minimum code       (src lane)
               refactorer         REFACTOR: structure only  (src lane)
             ── the main session verifies the report against the tests and git history
    REVIEW   reviewer             independent review of the whole branch
    PR       ── you review and merge

**Plan.** The project manager proposes a scope and lists every question that blocks it. When a scope sets new structure, such as a module boundary, a dependency, or persistence, the architect recommends a design, and the accepted decision becomes an ADR that the developer and refactorer work within. Your answers are recorded in the plan's `## Decisions`, so no agent asks twice.

**Build.** Every batch goes RED, GREEN, REFACTOR, with a checkpoint commit after each phase and a diff check after every dispatch. The scope ends with an adversarial sweep and a final refactor pass. When the engineering manager reports done, the main session checks the claim before trusting it.

**Review.** The reviewer reads the whole branch with the spec and plan, but none of the builders' reports or reasoning, so its reading is independent. Blockers and Majors go back to the engineering manager as a new batch; design findings go to the architect. Review happens once per scope, not per batch: per-batch review would see only fragments and would put the engineering manager in charge of triaging findings about its own team's work.

The rules are in `CLAUDE.md` (the loop) and `AGENTS.md` (rules for every contributor, plus the Project profile). Review findings are kept in `docs/code-reviews/` by the bundled `review-tracker` skill.

## Requirements

- Claude Code
- `git` and `python3`, for `bin/007` and the hooks, whatever the project's language
- `uv`, for `./scripts/check-dev-framework` (the hooks' own tests)
- `gh`, if you want the main session to open PRs

## Install

`bin/007` runs from a clone of this repo. There's nothing else to install.

**For one project**, clone, copy, and delete the clone. Run `init` from the project's top level:

    git clone https://github.com/blundin/007.git /tmp/007
    /tmp/007/bin/007 init
    rm -rf /tmp/007

To pin a release, run `git -C /tmp/007 checkout v0.1.0` before `init`.

**For many projects**, keep the clone and put its `bin/` on your `PATH`, either by linking the command into a directory already on it or by adding the directory itself:

    git clone https://github.com/blundin/007.git ~/tools/007
    ln -s ~/tools/007/bin/007 ~/.local/bin/007

`~/.local/bin` is on the `PATH` on most Linux systems but not on macOS by default. The kept clone is the installed version: check out a tag to pin a release, and pull or check out a newer tag to upgrade.

Don't clone with `--depth 1`. `007 remove` needs the commit a project was installed from, and a shallow clone lacks older commits.

## Commands

Run each from the top level of a git repo, except `new`, which makes one.

    007 new myapp    # create myapp/, run git init, copy the framework
    007 init         # copy the framework into the current repo
    007 remove       # delete the framework files that are unchanged since install

**`new` and `init`** copy every file git tracks under `framework/`.
- They never overwrite a file. Anything that already exists is skipped and listed. For `CLAUDE.md`, `AGENTS.md`, `.claude/settings.json`, and `.gitignore`, the list names the framework's copy so you can merge it in by hand.
- They write `.007-version`, holding the 007 commit they copied from.
- They refuse to copy while `framework/` in the clone has uncommitted changes, since `.007-version` records the commit, not local edits.
- They refuse, writing nothing, if a file stands where the framework needs a directory.
- They end by printing the setup steps below.

**`remove`** reads the commit in `.007-version` and deletes the framework files that still match that commit. It then deletes `.007-version` and any directories left empty. Files you've changed, such as a filled-in `AGENTS.md`, and files the project had before install are kept and listed. Any clone of this repo has the commit, whatever tag is checked out. It leaves the caches the hooks' tools create (`.mypy_cache`, `.ruff_cache`, `__pycache__`); delete those by hand.

No command commits, uses the network, or writes outside the repo. Review the changes and commit them yourself.

## Configure a project

1. **Set the lanes.** Edit `.claude/lanes.json` so `src` and `test` list the path prefixes each lane may write, each ending in `/`. A Rails app might use `{"test": ["spec/"], "src": ["app/", "lib/"]}`.
2. **Write the three scripts.** Replace the placeholder bodies:
   - `scripts/check`: the full gate (lint, format, strict types, every test, coverage). Exit 0 only if everything passes. CI should run it too.
   - `scripts/test <paths>`: run the named tests and print each outcome, in a way that tells a failed test from an errored one.
   - `scripts/lint <paths>`: lint, format-check, and type-check the named files.
3. **Fill in the Project profile.** In `AGENTS.md`, replace every `<!-- FILL ... -->` marker (`grep -n FILL AGENTS.md`). Each one has an example from a Python library.
4. **Check the settings.** `.claude/settings.json` puts `git commit` on the `ask` list, so every commit stops and asks first. That's for signed commits whose key has to be unlocked, such as 1Password's SSH agent. If you don't sign commits, move it to `allow`.
5. **Run the framework check.** `./scripts/check-dev-framework` should pass.
6. **Write a spec** in `docs/specs/` with criterion IDs (see its README).
7. **Start a session** and ask what's next. The main session dispatches the project manager, shows you the proposed scope and its questions, and waits for your approval before building anything.

## Upgrade a project

There's no update command yet. To move a project to a newer release, remove the old version and install the new one:

    007 remove    # deletes what's unchanged since install; lists what you changed
    007 init      # with the clone at the newer release

The files `remove` kept, such as your filled-in `AGENTS.md`, are skipped by `init`. Merge the newer framework's changes into them by hand. `CHANGELOG.md` says what changed, and `git diff <old>..<new> -- framework/` in the clone shows every line.

## What's in this repo

| Path | Contents |
|---|---|
| `framework/` | Everything that lands in a project. `bin/007` copies every tracked file in it, so adding a file here ships it |
| `bin/007` | The install and remove command: one Python file, standard library only |
| `tests/` | The command's tests |
| `scripts/check` | 007's single gate: the command's checks, then the framework's hook checks |
| `docs/` | 007's own backlog, lessons, decision records, and specs. Never copied |
| `CHANGELOG.md` | What changed for adopters, by version |
| `LICENSE` | MIT |

Inside `framework/`:

| Path | Contents |
|---|---|
| `CLAUDE.md` | The TDD loop: roles, phases, diff check, triage, done criteria |
| `AGENTS.md` | Rules for every contributor, and the Project profile |
| `.gitignore` | Caches and `.env` files |
| `.claude/agents/` | Seven agents: `project-manager` and `architect` (plan), `engineering-manager` and its triad (build), and `reviewer` (review) |
| `.claude/hooks/` | `lane_guard.py`, `git_guard.py`, `adr_write_guard.py`, `agent_guard.py`, their tests (including one that checks every agent's tools are guarded), and the configs for their checks |
| `.claude/lanes.json` | Lane paths |
| `.claude/settings.json` | Permissions, including a deny on reading `.env` files |
| `.claude/skills/review-tracker/` | Records findings in `docs/code-reviews/` |
| `scripts/` | `check`, `test`, `lint` (yours to fill in), and `check-dev-framework` |
| `docs/specs/`, `docs/plans/`, `docs/code-reviews/`, `docs/adr/` | Specs, scope plans, findings, decision records |

## Changing the framework

1. Change files under `framework/` or `bin/007` on a branch, test-first. The rules are in [`docs/README.md`](docs/README.md).
2. Run `./scripts/check`.
3. Add an entry under `Unreleased` in `CHANGELOG.md` for anything an adopter would notice.
4. To release, move the `Unreleased` entries under a new version heading and tag it (`git tag v0.2.0`). `git diff v0.1.0..v0.2.0 -- framework/` shows adopters exactly what changed.

## Provenance

- Extracted from the framework's first project at `319e93c`. That project and this one are separate; a lesson learned in one is applied to the other by hand.
- `review-tracker` is vendored from [`blundin/code-review-issue-tracker`](https://github.com/blundin/code-review-issue-tracker) at `03fc0be` (MIT). If you also have it installed as a personal skill, the two copies share a name. Keep them in sync, or remove one.

## License

MIT. See [`LICENSE`](LICENSE).
