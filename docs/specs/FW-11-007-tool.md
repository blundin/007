# FW-11: 007, the bootstrap tool

Status: Approved.

Decision record: [ADR-001](../adr/ADR-001-007-tool.md), as amended (simplified to a copy command).

## Goal

Like `rails new`, but small. A developer at Austin Stone can put the framework into a new project or an existing repo with one command, then follow the printed steps to configure it.

    git clone git@github.com:TheAustinStone/007.git ~/tools/007

    ~/tools/007/bin/007 new myapp    # new directory, git init, copy the framework
    ~/tools/007/bin/007 init         # copy the framework into the current repo

## What it copies

`bin/007` copies every file git tracks under `framework/` in its own checkout, keeping its path relative to `framework/`. Untracked and ignored files, such as Python caches, are not copied. Nothing outside `framework/` is copied: not `bin/`, `tests/`, the root scripts, or 007's own docs.

`framework/` holds `CLAUDE.md`, `AGENTS.md`, `.gitignore`, `.claude/` (agents, hooks with their tests and configs, the review-tracker skill, `lanes.json`, `settings.json`), `scripts/` (`check`, `test`, `lint`, `check-dev-framework`, copied executable), and the READMEs for `docs/specs/`, `docs/plans/`, and `docs/code-reviews/`.

## Criteria

- **NEW-01**: `007 new <dir>` creates `<dir>`, runs `git init` in it, and copies every framework file. Each file's contents match 007's checkout, and scripts keep their executable bit.
- **NEW-02**: `007 new <dir>` exits non-zero and writes nothing if `<dir>` already exists.
- **INIT-01**: `007 init` copies every framework file into the current directory. It exits non-zero and writes nothing if the current directory is not the top level of a git repo.
- **INIT-02**: `007 init` never overwrites an existing file. It lists every path it skipped. For a skipped `CLAUDE.md`, `AGENTS.md`, `.claude/settings.json`, or `.gitignore`, it says what to add by hand.
- **BOTH-01**: Both commands write `.007-version`, a single line holding the commit of 007's checkout.
- **BOTH-02**: Both commands end by printing the next steps: set the lanes, fill in the `FILL` markers, write the three scripts, run `./scripts/check-dev-framework`, and commit.
- **BOTH-03**: Neither command writes outside the target directory, makes a commit, or uses the network.

## Threat model

Trusted developers, running it on their own machines. The tests defend against damage to the target repo: overwriting an existing file, writing outside the target directory (including through a symlink already in the target), or a half-finished copy after an error.

## How it's built

- `bin/007`: one Python 3 file, standard library only, as with the hooks.
- Framework work, done by the main session with Brian and test-first with pytest. The triad isn't used.
- Its tests live in `tests/`, outside `framework/`, and run in 007's root gate, `scripts/check`, which is not copied to projects.

## Later, if needed

- An adoption check, if teams get the setup wrong.
- A `/007` skill that fills in the profile.
- Updates. `.007-version` records the starting point.

## Open questions

None. Awaiting Brian's approval.
