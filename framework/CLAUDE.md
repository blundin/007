@AGENTS.md

# TDD Loop

This loop governs every change in the `src` lane (`.claude/lanes.json`). Changes to docs, specs, CI, or configuration do not use it. It enforces the rules in AGENTS.md through separate subagents and lanes.

## Roles

The main session delegates. It plans each scope with `project-manager` before building it:

1. Dispatch `project-manager` with the spec path and either a requested scope or "next". Dispatch it when the human asks what's next or asks to start a scope; when the engineering manager reports `DONE` and the human has merged its PR (run "next"); and when the human changes a spec or answers one of its open questions.
2. On `BLOCKED`, relay the PM's questions to the human and resume the PM with the answers. Spec changes are the human's to decide: edit a spec only when the human directs it, and show the exact change for approval before writing it. A question about design goes to `architect` first (see Triage).
3. If the PM's `Design decisions` isn't `none`, dispatch `architect` in `recommend` mode for each decision before going further. In either mode, present those recommendations and wait for the human to decide each one. In "next" mode, present the proposed scope, its order rationale, any questions, and the architect's recommendations to the human, and wait for approval. A changed scope goes back to the PM as a requested scope. Never build a proposal without approval.
4. On `READY` (and approval), create the feature branch. For each design decision the human made, dispatch `architect` in `record` mode to write the accepted ADR. Write the plan to `docs/plans/<scope>.md` with `Status: planned`, an `## ADRs` section listing every ADR that bears on the scope (new ones and those the PM named), and a closing `## Decisions` section. Commit the ADRs and the plan together.

Whenever the human answers a question, from the PM, the engineering manager, or a subagent, the main session appends it to that plan's `## Decisions`: the question, the answer, and the date. Answers given while planning go in when the plan is first written; later ones are committed on the feature branch before anyone is resumed. Agents cite these decisions instead of asking again.

To deliver the scope, the main session dispatches `engineering-manager` with the spec path, the scope, and the plan path. When the report says `BLOCKED`, it relays the escalation to the human, records the answer in the plan's `## Decisions`, and re-dispatches the manager with it. A question about design goes to `architect` first (see Triage). The main session does not run the phases itself.

The main session owns each plan doc's status line and keeps it current: `building (<branch>)` when the manager is dispatched, `blocked (<question>)` when it reports `BLOCKED`, back to `building` on resume, and `done (PR #<n>)` when the human merges the PR.

The main session also records the report's `Findings`, and the reviewer's, in `docs/code-reviews/` with the `review-tracker` skill: one session file per feature run, updated in place when the manager is resumed. A finding is marked `fixed`, with its commit sha in the resolution notes, when the batch that fixes it lands.

### Verify a `DONE` report

The manager's report is a claim. Before treating it as done, the main session checks it:

1. `./scripts/check` passes.
2. The Project profile's criterion grep finds a tagged test for every ID under `Criteria covered`, and the scope has no other IDs left.
3. `git log` on the branch shows, for each batch in the report, a `test(red)` checkpoint before its `feat(green)` checkpoint. A structure-only batch has a `refactor` checkpoint instead.
4. HEAD matches the report.

If anything doesn't match, resume the manager with the discrepancy. Never present an unverified report to the human as done.

### Review before the PR

After a verified `DONE`, dispatch `reviewer`. The reviewer's value is that it hasn't seen how the change was built, so its prompt carries exactly three things and nothing else: the commit range (`main..HEAD`, or the new commits on a re-review), the spec path, and the plan path. Never add the manager's report, the triad's reports, your own summary, or why the code was written the way it was. The reviewer runs once per scope, here; don't dispatch it after individual batches or phases.

The reviewer writes nothing, and only its prompt stops it writing through Bash, so run the diff check (below) after it returns. Any change at all is a violation: restore it, discard that review, and dispatch the reviewer again with a notice naming the violation. Two in a row go to the human.

The reviewer returns findings without writing them; record them with the `review-tracker` skill, mapping its severities as `reviewer.md` says.

- Findings the reviewer marks `design` go to `architect`, not to the manager as RED targets; a test can't express a wrong abstraction. Handle them as design questions (see Triage). If the human accepts a structural change, send the manager the accepted ADR and the finding IDs for a structure-only batch.
- Triage every other Blocker and Major against the threat model, as for sweep findings. Send the ones that stand back to the manager as targets for a new batch, with their finding IDs.
- After that run is verified, dispatch the reviewer again on the new commits only. If a Blocker remains, escalate to the human.
- Minors and Nits are recorded as `acknowledged` and listed in the PR description; they don't block it.

Finding statuses follow triage. A finding sent to a batch stays `open` until the batch lands, then becomes `fixed` with its commit sha in the resolution notes. A finding triaged out becomes `wont-fix`, with the reason in its resolution notes.

### Open the PR

When the review is settled, the main session opens the PR. The description lists the criteria delivered, the ADRs written, the reviewer's Minors and Nits, and every finding triaged out with its reason.

### The coordinator

The `engineering-manager` is the coordinator. Throughout this loop, "you" means the coordinator. You do not write or edit files in the `src` or `test` lane yourself. You plan batches, dispatch subagents, verify their work, and commit checkpoints. The subagents work as a triad, one at a time:

- `test-engineer` — writes failing tests (RED). Lane: `test`.
- `app-developer` — scaffolds stubs and writes the minimum passing code (GREEN). Lane: `src`.
- `refactorer` — improves structure without changing behavior (REFACTOR). Lane: `src`.

## Setup

1. Work on a feature branch, never on `main`.
2. Every phase ends in a checkpoint commit, so each diff check compares against the previous phase.
3. Checkpoint commits on a loop feature branch are authorized without asking first. The human reviews the branch as a pull request before it merges. Each `git commit` still raises a permission prompt, so the human can unlock the signing key before it signs. If a commit is denied or fails, retry it once. If it fails again, stop and report `BLOCKED`, naming the phase whose work is uncommitted, and leave that work in the tree.
4. To compare against old behavior, never check old files out into the working tree. Use `git worktree add "$TMPDIR/<name>" <sha>`, compare there, and `git worktree remove` it before the next dispatch.

## Lanes

Each subagent's lane is enforced by hooks in its own definition under `.claude/agents/`, which run only while that subagent is active. They don't restrict you, the coordinator, except the agent guard below.

- `.claude/hooks/lane_guard.py` blocks Write and Edit calls outside the subagent's lane.
- `.claude/hooks/git_guard.py` blocks every git command except read-only ones (`status`, `diff`, `log`, `show`, `ls-files`, `grep`, `blame`, `rev-parse`, and `stash list`). Git state belongs to you.

The `reviewer` runs `git_guard.py` too. Your own `Agent` tool runs `.claude/hooks/agent_guard.py`, which lets you dispatch only the triad: any other agent would work outside every lane.

Neither lane hook can see everything a subagent does through Bash, so the diff check below is the real backstop. Never skip it.

## Diff check (after every dispatch)

Record `git rev-parse HEAD` before dispatching, then run:

    git rev-parse HEAD
    git stash list
    git diff --name-only HEAD
    git ls-files --others --exclude-standard

If HEAD moved or a stash appeared, the subagent changed git state: restore it, then treat it as a lane violation. If any path falls outside the subagent's lane:

1. Restore modified out-of-lane paths with `git restore <path>` and delete untracked out-of-lane files.
2. Re-dispatch the same subagent with a notice naming the violation.
3. After two consecutive violations by the same subagent, stop and escalate to the human.

## Phases per batch

### 0. Plan

Read the spec and list the acceptance-criterion IDs in scope. Group them into batches. A batch is one cohesive requirement group, not a count; the soft cap is 12 tests, and a property-based test counts as one. Run conformance batches (the spec's stated requirements) before adversarial batches (edge cases and attacks).

### 1. Scaffold (only when the test-engineer requests it)

Dispatch `app-developer` in scaffold mode with the signatures the spec declares. Also dispatch it before RED when the path a batch targets already has a fallback that would make a new test fail some other way (a type error, say): the scaffold replaces only that path with a stub. Verify: diff check passes, stubs contain no logic (bodies follow the Project profile's stub convention), and `./scripts/lint` passes on them. Commit: `chore(scaffold): <summary>`.

### 2. RED

Dispatch `test-engineer` with the spec path, the criterion IDs for this batch, the exact criterion text quoted in the plan, any `## Decisions` that bear on them, and the mode (`conformance` or `adversarial`). Verify:

- Diff check passes.
- Each test's assertion checks the behavior its quoted criterion states, not a narrower or different reading. Send back any that doesn't.
- Run the new tests with `./scripts/test <paths>`. Every new test meets the test rules in AGENTS.md: outcome **failed**, not **error** (see the Project profile), for a valid reason. Send invalid tests back.
- `./scripts/lint` passes on the new test code.
- Pins are the one exception to "every new test fails." A pin passes at RED by design because it guards GREEN against over-rejection: an accepted boundary value, or an input that must stay unchanged. The test-engineer labels each pin and names what it guards. Check that each one really is an accept-side guard, and send back any that isn't.

Commit pins first, if any: `test: pin <criterion IDs> guards`. Then commit the failing tests: `test(red): <criterion IDs>`.

### 3. GREEN

Dispatch `app-developer` with the failing test paths, the failure output, the spec, the ADRs listed in the plan, and `docs/code-reviews/known-issues.json`, naming which findings this batch targets and which are already fixed. Verify:

- Diff check passes.
- The diff meets the code rules in AGENTS.md, including a full `./scripts/check`. A passing new test is not enough.

Commit: `feat(green): <criterion IDs>`.

### 4. REFACTOR

Dispatch `refactorer` with the files changed in this batch and the ADRs listed in the plan. Verify:

- Diff check passes, and no file in the `test` lane changed.
- `./scripts/check` passes in full.
- The report accounts for every smell in the catalog with a disposition. Reject a report that says "no refactoring needed" without that accounting, and re-dispatch.
- Any bug the refactorer reports becomes a target for the next RED batch; the refactorer never fixes it directly.

Commit: `refactor: <summary>` (skip the commit if nothing changed, but the report is still required).

### Structure-only batch (design runs only)

When the main session sends an accepted ADR to bring the code in line with, dispatch `refactorer` with the ADR, the finding IDs it resolves, and the files involved. It restructures toward the ADR with tests locked. Verify as for REFACTOR, and also that the change matches the ADR. Commit: `refactor: <ADR number> <summary>`. There is no RED or GREEN: behavior doesn't change. If the ADR can't be met without changing behavior, stop and escalate; that's a spec question.

## Triage (before a finding or question becomes work)

- **Spec questions.** When a subagent raises one, first check the spec and the `## Decisions` sections of the plans in `docs/plans/`. If their text settles it, re-dispatch the subagent with that text quoted. That is citing, not resolving. Escalate only what the text leaves open.
- **Design questions.** A question about structure (module boundaries, a pattern, a new abstraction, a dependency choice), as opposed to what the spec requires, goes to `architect` before the human. Dispatch it in `recommend` mode with the question and the code it touches, then present its recommendation along with the question. The human decides. Then dispatch it in `record` mode with the decision, so it writes the accepted ADR, and commit the ADR with the plan's `## ADRs` and `## Decisions` updated.
- **Adversarial findings.** Before a sweep finding becomes a RED target, judge it against the threat model in the Project profile, using the test-engineer's "Realistic?" answer. A finding no real caller or upstream system could produce is not pursued: report it as `info` with disposition `triaged out` and the reason, so the human sees every one.
- **Project-specific hazards.** When a sweep, a review, or an escalation turns up a hazard specific to this project, such as an upstream system's quirk or a failure mode of its domain, propose adding it to the Project profile's `Domain attacks`, or recording it in the file its `Domain notes` names. The human approves each addition. Later sweeps then try it every time.

## Batch scaling

Large batches are efficient until they aren't. Apply these rules:

- **Split on struggle.** If GREEN fails after two attempts, or the developer reports the batch needs changes across unrelated modules, reset the branch to the commit before this batch's RED checkpoint. Split the batch in half along criterion lines and run each half as its own batch.
- **Shrink after trouble.** If two consecutive batches needed splitting, halve the soft cap.
- **Grow back slowly.** After three consecutive clean batches, the soft cap may double again, up to its original 12.

## Done criteria

A feature is done when the done rules in AGENTS.md hold, and also:

1. A final adversarial sweep by `test-engineer` returns `NO NEW FAILURES` with an attack log. Review the log: every attack category must show what was tried or why it does not apply. Reject a thin log and re-dispatch.
2. A final `refactorer` pass over every file the feature touched is complete.

## Escalate to the human when

Anything in AGENTS.md's "Stop and ask a human" list comes up, or:

- A subagent raises a spec question that triage doesn't settle. Pause the loop and ask; never resolve it yourself.
- A batch needs a structural decision that the plan's ADRs and the existing structure don't settle, such as a new module boundary, or the refactorer reports a smell that needs a change beyond its scope. Report it; the main session takes it to the architect.
- Two consecutive lane violations by the same subagent.
- The feature exceeds 12 batches.
