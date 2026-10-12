# FW-12: Agents that check each other

Status: Approved.

## Goal

Close the gaps found when the agents were evaluated as a team. The engineering manager's report is verified, not taken on trust. The reviewer reviews every feature with a fresh context. Decisions reach the agents that need them and are recorded where they can be cited. Design questions get an architect's recommendation before they reach the human, and the architect takes part where structure is actually decided: when a scope sets new structure, when the builders work, and when a review finds design drift.

## Criteria

### Verify the manager (1a)

- **VERIFY-01**: Before treating an engineering-manager report of `DONE` as done, the main session runs `./scripts/check`, runs the Project profile's criterion grep for every ID the report lists as covered, and confirms in `git log` that each batch has a `test(red)` checkpoint before its `feat(green)` checkpoint. HEAD must match the report.
- **VERIFY-02**: Any mismatch goes back to the engineering manager, resumed with the discrepancy. It is not presented to the human as done.

### Decisions reach the agents (2a, 2b, 2c)

- **PLAN-01**: The engineering manager's inputs include the plan path. It reads the plan's quoted criterion text, its known issues, and its `## Decisions` section.
- **PLAN-02**: Each RED dispatch gives the test engineer the exact criterion text quoted in the plan and the decisions that bear on it.
- **PLAN-03**: Every plan ends with a `## Decisions` section. When the human answers a question from the project manager, the engineering manager, or a subagent, the main session appends the question, the answer, and the date, and commits it.
- **PLAN-04**: Triage, the engineering manager, and the project manager cite the plans' `## Decisions` sections. No rule refers to "checkpoint docs" or "rulings" without saying where they are.
- **PLAN-05**: The app developer's definition lists its GREEN inputs, including `docs/code-reviews/known-issues.json` and which findings the batch targets.

### The reviewer in the loop (1b, 1c, 1d)

- **REVIEW-01**: After a verified `DONE`, and before the branch goes to the human as a PR, the main session dispatches `reviewer` on the branch's diff against `main`, with the spec and plan paths.
- **REVIEW-02**: The reviewer returns findings; it doesn't write them. The main session records them with the `review-tracker` skill.
- **REVIEW-03**: Blockers and Majors are triaged against the threat model like sweep findings. Those kept go back to the engineering manager as targets for a new batch. After that run, the reviewer reviews only the new commits. If a Blocker remains after that second review, the main session escalates to the human.
- **REVIEW-04**: The reviewer's severities map to the skill's: Blocker to `high`, Major to `medium`, Minor to `low`, Nit to `info`.

### Independent tests and design questions (1e, 3a)

- **TEST-01**: In conformance mode, the test engineer derives each test from the criterion text and the public signatures, and reads implementation bodies only after its tests are written. Adversarial mode may read the implementation.
- **TEST-02**: At RED, the engineering manager checks each test's assertion against the quoted criterion text and sends back a test that checks a narrower or different reading.
- **DESIGN-01**: A question about structure (module boundaries, patterns, a new abstraction, a dependency choice), as opposed to what the spec requires, goes to `architect` before the human. The main session presents the architect's recommendation with the question. The human decides, and an accepted recommendation becomes an ADR.

### Agent permissions

- **PERM-01**: The engineering manager can dispatch only `test-engineer`, `app-developer`, and `refactorer`. A hook on its `Agent` tool (and the legacy `Task` name) blocks any other type, a missing type, or unreadable input.
- **PERM-02**: Every agent with Bash runs `git_guard.py`, except the engineering manager, which commits checkpoints.
- **PERM-03**: Every agent with a file-writing tool guards all of `Write`, `Edit`, `MultiEdit`, and `NotebookEdit`.
- **PERM-04**: The project manager and reviewer have no file-writing tools, and the project manager has no Bash.
- **PERM-05**: A test checks PERM-01 to PERM-04 against the agent files, so a later edit can't drop a guard unnoticed.
- **PERM-06**: `.claude/settings.json` allows `git worktree` and denies reading `.env` and `.env.*`.

### The architect in the flow

- **ARCH-01**: The project manager's report has a `Design decisions` field. For the chosen scope, it lists each structural decision the scope forces: a new module or boundary, a new external system, persistence, a new dependency, or a change across existing module boundaries. Each has its criterion IDs and the existing ADRs that bear on it, or the field says `none`. The project manager reads `docs/adr/` to fill it in.
- **ARCH-02**: When `Design decisions` isn't `none`, the main session dispatches `architect` in `recommend` mode for each one before presenting the scope, then presents the scope and the recommendations together. Scopes that only add behavior inside existing structure skip this step.
- **ARCH-03**: The architect has two modes. In `recommend` mode it returns options, one recommendation, and a draft ADR as text, and writes nothing. In `record` mode, given the human's decision, it writes the ADR with status `accepted`, recording the option the human chose. It stays the only author of ADRs.
- **ARCH-04**: After the human decides on any architect recommendation, from scope planning, triage, or a review, the main session dispatches the architect in `record` mode. It commits the ADR on the feature branch with the plan update, which lists the ADR under the plan's `## ADRs` and records the decision in `## Decisions`.
- **ARCH-05**: Every plan has an `## ADRs` section listing the ADRs that bear on its scope. The engineering manager passes them to the app developer at GREEN and the refactorer at REFACTOR. The app developer implements within them and stops and reports if a batch can't pass within them. The refactorer counts drift from them as a smell.
- **ARCH-06**: The reviewer marks design-drift findings as `design`. The main session sends them to the architect, not to the engineering manager as RED targets. If the human accepts a structural change, the engineering manager runs a structure-only batch: the refactorer restructures toward the accepted ADR with tests locked. A change that would alter behavior is a spec question instead.
- **ARCH-07**: The engineering manager stops and reports a structural decision the scope's ADRs and the existing structure don't settle. The refactorer reports smells that need a change beyond its scope. Both reach the architect through the main session.

### Closing the flow

- **FLOW-01**: After the review, the main session opens the PR. Its description lists the criteria delivered, the ADRs written, the reviewer's Minors and Nits, and every finding triaged out, with the reason.
- **FLOW-02**: Finding statuses follow triage. A finding sent to a batch stays `open` until the batch lands, then becomes `fixed` with the commit sha. A finding triaged out becomes `wont-fix`, with the reason in its resolution notes. A Minor or Nit left for later becomes `acknowledged`.
- **FLOW-03**: Verifying a `DONE` report expects a `test(red)` before `feat(green)` in every batch except structure-only ones, which have a `refactor` checkpoint and no RED or GREEN.

## Out of scope

From the same evaluation, left for later: refactor-pass cost (4a), resuming the manager in place (4b), cheaper models (4c), the diff check's ignored files (4d), ownership lines between refactorer, reviewer, and architect (3b), and the architect's "ministry systems" phrasing (3c).

## How it's built

Changes to `framework/CLAUDE.md`, the agent definitions, and the `docs/plans/` and `docs/code-reviews/` READMEs. Brian approved the hook and settings changes. The prompt changes have no automated tests; each of those criteria is checked by reading the changed text. PERM-01 to PERM-05 are tested by `test_agent_guard.py` and `test_agent_wiring.py`, and `./scripts/check` must pass.
