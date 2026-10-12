# FW-12: Agents that check each other

Status: Approved.

## Goal

Close the gaps found when the agents were evaluated as a team. The engineering manager's report is verified, not taken on trust. The reviewer reviews every feature with a fresh context. Decisions reach the agents that need them and are recorded where they can be cited. Design questions get an architect's recommendation before they reach the human.

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

## Out of scope

From the same evaluation, left for later: refactor-pass cost (4a), resuming the manager in place (4b), cheaper models (4c), the diff check's ignored files (4d), a `git_guard` hook on the reviewer (4e, a hook change), ownership lines between refactorer, reviewer, and architect (3b), and the architect's "ministry systems" phrasing (3c).

## How it's built

Changes to `framework/CLAUDE.md`, the agent definitions, and the `docs/plans/` and `docs/code-reviews/` READMEs. No hooks or settings change. These are prompts, so there are no automated tests for them; each criterion is checked by reading the changed text, and `./scripts/check` must still pass.
