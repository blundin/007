# FW-15: Project setup skill

Status: Approved 2026-10-12.

## Goal

The framework ships generic, and each project makes it its own through the Project profile. The rules and agent definitions keep no assumptions from the first project (a Python HTTP client). A `/007-setup` skill does the customizing: it inspects the repo, drafts the profile, the lanes, and the three scripts, and shows them to the human before writing anything. Run again later, it checks the profile against the repo and proposes updates.

Agent definitions stay stock. Everything project-specific lives in `AGENTS.md`'s Project profile and the docs it points to, so `007 remove` and `init` upgrade the agents cleanly and only `AGENTS.md` is merged by hand.

## Criteria

### Generic rules

- **GEN-01**: `AGENTS.md` and the test engineer say tests never touch a live external system (HTTP services, databases, queues, the clock, the filesystem outside the test's own temp space), and isolate each with the tools the profile names. Neither mentions HTTP as the only kind.
- **GEN-02**: The profile's `Test isolation` field asks how tests isolate each external system the project uses, and which property-testing library it uses, if any.
- **GEN-03**: The test engineer's String hazards category reads as injection into whatever the code builds: queries, shell commands, markup, or expressions.
- **GEN-04**: Each profile item in `AGENTS.md` keeps a one-line FILL comment that says what to fill in, with no example, and points to the skill. The examples move to the skill.
- **GEN-05**: The README says the architect's defaults (monolith first, the pattern table, the testing stance) and the TDD loop are the framework's opinions, which a project may change in its own copy at the cost of a hand merge on upgrade.

### The skill

- **SETUP-01**: `framework/.claude/skills/007-setup/SKILL.md` ships with the framework. The main session runs it when the human invokes `/007-setup`. It isn't auto-invoked.
- **SETUP-02**: For each profile field, and for `lanes.json` and the three scripts, the skill says what the field controls (which agents read it, and what they do with it) and how to find the answer in the repo: which files to read, and which commands to run. For example, run one deliberately failing test and one deliberately broken test to see how `Failure versus error` appears.
- **SETUP-03**: The skill's reference gives an example of every field for three stacks: a Python library, a Rails app, and a Swift app.
- **SETUP-04**: On a first run, the skill drafts every field, `lanes.json`, and the three script bodies. It marks each value *found* (with the file or command output that shows it) or *needs you* (with the question to answer). It writes nothing until the human approves. Then it writes only `AGENTS.md`'s profile and title lines, `.claude/lanes.json`, and the three scripts, and runs `./scripts/check-dev-framework`.
- **SETUP-05**: On a later run, with the profile filled in, the skill compares each field with the repo and reports drift, such as a runtime dependency missing from the profile, a lane path that no longer exists, or a test runner that changed. It proposes each change and writes only approved ones.
- **SETUP-06**: The skill never edits agent definitions, hooks, `settings.json`, `CLAUDE.md`, or specs. A need it can't meet through the profile is reported to the human as one.
- **SETUP-07**: A test checks that every field in the Project profile has a section in the skill's reference, so a new field can't ship without guidance.

### Keeping it current

- **TRIAGE-01**: `CLAUDE.md`'s Triage adds that a hazard specific to this project, found by a sweep, a review, or an escalation, gets a proposed addition to the profile's `Domain attacks` or `Domain notes` for the human to approve.
- **NEXT-01**: `bin/007`'s next steps tell the user to run `/007-setup` in Claude Code first, with the manual steps as the fallback. FW-11's BOTH-02 is updated to match.

## Threat model

Trusted developers on their own repos. The skill must not write before approval, overwrite a field the human filled in without showing the change, or touch files outside SETUP-04's list.

## How it's built

- Test-first where there's code: SETUP-07's coverage test (in `framework/.claude/hooks/tests/`, beside `test_agent_wiring.py`) and NEXT-01's change to the next-steps test. The other criteria are prompt text, checked by reading.
- `./scripts/check` must pass. The CHANGELOG gets an entry under Unreleased.

## Out of scope

- Customizing agent definitions per project. If a project needs it, the human edits its copy by hand and accepts the merge on upgrade.
- Filling in specs or threat models. The skill points to them; humans write them.

## Open questions

None.
