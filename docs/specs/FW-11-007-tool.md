# FW-11: 007, the bootstrap tool

Status: Approved and implemented. `new` and `init` shipped in v0.1.0; BOTH-04, INIT-03, and the REMOVE criteria came in PR #1.

Decision record: [ADR-001](../adr/ADR-001-007-tool.md), as amended (Amendment 2 simplified it to a copy command; Amendment 3 added `remove`).

## Goal

Like `rails new`, but small. A developer can put the framework into a new project or an existing repo with one command, then follow the printed steps to configure it. One more command takes it out again.

    git clone https://github.com/blundin/007.git ~/tools/007

    ~/tools/007/bin/007 new myapp    # new directory, git init, copy the framework
    ~/tools/007/bin/007 init         # copy the framework into the current repo
    ~/tools/007/bin/007 remove       # delete the framework files that are unchanged since install

## What it copies

`bin/007` copies every file git tracks under `framework/` in its own checkout, keeping its path relative to `framework/`. Untracked and ignored files, such as Python caches, are not copied. Nothing outside `framework/` is copied: not `bin/`, `tests/`, the root scripts, or 007's own docs.

`framework/` holds `CLAUDE.md`, `AGENTS.md`, `.gitignore`, `.claude/` (agents, hooks with their tests and configs, the review-tracker skill, `lanes.json`, `settings.json`), `scripts/` (`check`, `test`, `lint`, `check-dev-framework`, copied executable), and the READMEs for `docs/specs/`, `docs/plans/`, `docs/code-reviews/`, and `docs/adr/`.

## Criteria

- **NEW-01**: `007 new <dir>` creates `<dir>`, runs `git init` in it, and copies every framework file. Each file's contents match 007's checkout, and scripts keep their executable bit.
- **NEW-02**: `007 new <dir>` exits non-zero and writes nothing if `<dir>` already exists.
- **INIT-01**: `007 init` copies every framework file into the current directory. It exits non-zero and writes nothing if the current directory is not the top level of a git repo.
- **INIT-02**: `007 init` never overwrites an existing file. It lists every path it skipped. For a skipped `CLAUDE.md`, `AGENTS.md`, `.claude/settings.json`, or `.gitignore`, it says what to add by hand.
- **INIT-03**: `007 init` exits non-zero and writes nothing if a file stands where the framework needs a directory.
- **INIT-04**: `007 init` exits non-zero and writes nothing if `.007-version` already exists, even as a symlink, and says to run `007 remove` first. Installing over an older install would mix two versions that `remove` can't tell apart.
- **BOTH-01**: Both commands write `.007-version`, a single line holding the commit of 007's checkout.
- **BOTH-02**: Both commands end by printing the next steps: run `/007-setup` in Claude Code, or by hand set the lanes, fill in the `FILL` markers, write the three scripts, run `./scripts/check-dev-framework`, and commit.
- **BOTH-03**: Neither command writes outside the target directory, makes a commit, or uses the network.
- **BOTH-04**: Both commands exit non-zero and write nothing if a tracked file under `framework/` in 007's checkout has uncommitted changes, staged or not, so `.007-version` always matches what was copied.
- **REMOVE-01**: `007 remove` deletes every framework file whose contents match the commit in `.007-version`, then `.007-version` itself, then any directory those deletions left empty. It makes no commit.
- **REMOVE-02**: `007 remove` keeps and lists every framework path whose contents differ from that commit, whether the project changed it after install or had its own file there before.
- **REMOVE-03**: `007 remove` exits non-zero and deletes nothing if it isn't run from the top level of a git repo, if `.007-version` is missing or doesn't name a commit 007's checkout has, or if a framework path leads outside the repo.

## Threat model

Trusted developers, running it on their own machines. The tests defend against damage to the target repo: overwriting an existing file, writing or deleting outside the target directory (including through a symlink already in the target), deleting a file the project changed, or a half-finished copy after an error.

## How it's built

- `bin/007`: one Python 3 file, standard library only, as with the hooks.
- Framework work, done by the main session with Brian and test-first with pytest. The triad isn't used.
- Its tests live in `tests/`, outside `framework/`, and run in 007's root gate, `scripts/check`, which is not copied to projects.

## Later, if needed

- An adoption check, if teams get the setup wrong.
- A `/007` skill that fills in the profile.
- Updates. `.007-version` records the starting point, and `remove` already compares against it. Until then, a project upgrades with `remove`, then `init` from the newer release, merging the kept files by hand.
- Removing the untracked caches the hooks' tools leave (`.mypy_cache`, `.ruff_cache`, `__pycache__`). `remove` leaves them, along with the directories that hold them.

## Open questions

None.
