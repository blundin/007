---
name: 007-setup
description: Customize the 007 framework for this project. Inspects the repo and drafts the Project profile in AGENTS.md, .claude/lanes.json, and the scripts/check, scripts/test, and scripts/lint bodies, showing each value with its evidence for approval before writing. Run again later to check the profile against the repo and propose updates.
disable-model-invocation: true
---

# 007 setup

The framework ships generic. This skill makes it fit this project, through the only places a project customizes it: the Project profile in `AGENTS.md`, `.claude/lanes.json`, and the three scripts. Every agent reads the profile, so a value here changes how they all work.

[`reference.md`](reference.md) has a section for every item: what it controls, how to find the answer in the repo, and examples for a Python library, a Rails app, and a Swift app. Read it before drafting. The examples show the shape of an answer. This repo's files and the probes decide the value, even when an example says otherwise.

## What you may write

Only these, and only after the human approves the exact change:

- The title lines and the `## Project profile` section of `AGENTS.md`
- `.claude/lanes.json`
- `scripts/check`, `scripts/test`, and `scripts/lint`

Never edit agent definitions, hooks, `.claude/settings.json`, `CLAUDE.md`, or specs. They stay stock, so the framework upgrades cleanly. If the project needs something the profile can't express, report it to the human as a finding; don't work around it.

Never commit. The human reviews and commits.

## Which run this is

Read `AGENTS.md`, `.claude/lanes.json`, and the three scripts.

- **First run:** any `<!-- FILL` marker remains, or a script still prints "is not configured". Draft every unfilled item.
- **Drift check:** everything is filled in. Check each value against the repo.

A partly filled profile gets both: draft the unfilled items, check the filled ones.

## First run

1. **Survey.** Read the manifests, the tool configs, the CI workflows and any local CI definition (such as Rails' `bin/ci` and `config/ci.rb`), the directory layout, a few existing tests, and the specs in `docs/specs/`. `reference.md` names the files for each item. The project's own setup is its business; look only for what the framework needs.
2. **Run the existing suite** with the project's own test command, and record the result. If it can't run, say why, and go on: probe with the bare runner, and mark the items that depend on the real run *needs you*, with what you saw.
3. **Probe what reading can't settle.** `Failure versus error` and `Stub convention` need the runner's real output for four cases: an assertion that fails, a file that can't load, an undefined name inside a test body, and a test against a stub. On a first run the scripts aren't written yet, so probe with the command you'll draft for `scripts/test`.
   - Running the runner can write to the repo (logs, caches, a test database). Check `git status` before and after every run, and restore anything a run changed. If that isn't safe, run in a throwaway copy of the repo under `$TMPDIR`.
   - Write probe files under `$TMPDIR` when the runner accepts a path outside the repo. When it doesn't, ask the human before putting probes in the test lane, then delete them.
4. **Draft.** Give a value for the title, the one-line description, and every profile item, and mark each:
   - *found*: name the file and line, or the command and the output, that shows it
   - *needs you*: the question that settles it, with the options you see, and your lean
   Draft `lanes.json` and the three script bodies the same way. Scripts mirror what CI runs. A CI step that needs the network or secrets, or a part of the gate the project has no tool for (often coverage), is a *needs you*, never a silent omission.
5. **Present** the draft as one table of items, then the lanes and scripts, then anything the framework needs that the profile can't express, then the questions. Write nothing yet.
6. **Revise** with the human's answers until they approve.
7. **Write** the approved values. Show the diff. Run `./scripts/check-dev-framework`, then `./scripts/check`, and report both. A failing `./scripts/check` on existing code is information for the human, not something to fix here.

## Drift check

For each filled item, find the answer again as on a first run and compare:

- *matches*: say so in one line
- *drift*: the current value, what the repo shows now, the evidence, and the proposed value
- *can't tell*: why, and what would settle it

Common drift: a runtime dependency added to the manifest but not the profile, a lane path that no longer exists, a test runner or linter that changed, a new external system with no isolation listed, and `Domain notes` naming a file that's gone.

Propose each change as a before and after. Write only the approved ones, then run `./scripts/check-dev-framework`.

## Style

Lead with the table. Keep evidence to a path, a line, or a few lines of output. Ask only what the repo can't answer.
