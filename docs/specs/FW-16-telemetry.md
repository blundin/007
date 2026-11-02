# FW-16: Local telemetry

Status: Approved 2026-11-02, with the decisions under Decisions.

## Goal

Measure how the loop runs in real projects so that framework changes rest on numbers instead of impressions. Four open items need those numbers: FW-10 (retrospective counts), FW-14 4a (does the refactor pass after every batch pay for itself), FW-14 4c (which agents can run on a cheaper model), and FW-02 (is the single triad clean enough to run in parallel).

Everything stays on the developer's machine. Recording is off until a project turns it on. Each project then records its own events in a gitignored directory, and a reader turns them into a report. Nothing is sent anywhere, and agents never see the metrics, so they can't optimize for them.

## What gets measured

Each metric names the decision it informs and where its data comes from. *Git* means commit history and docs, available today for every project. *Reflog* means the local reflog, which keeps 90 days by default and exists only in the original clone. *Events* means the new event log.

| Metric | Informs | Source |
|---|---|---|
| Batches per scope, criteria per batch | Batch scaling rules | Git |
| Batch splits (resets on a feature branch) | FW-02, batch scaling | Reflog, then events |
| GREEN attempts per batch, invalid REDs sent back | FW-10 | Events (re-dispatches of the same agent within a batch) |
| Lane and git guard denials, by agent and hook | Prompt quality, FW-14 4d | Events |
| Refactor passes that changed nothing | FW-14 4a | Git (missing `refactor` commit) and events (the refactorer ran) |
| Tokens and model by agent, per phase and per scope | FW-14 4a, 4c | Events (captured at SubagentStop) |
| Wall time by agent and phase | Efficiency | Events |
| Main-session tokens per scope | Cost of coordination | Events (captured at Stop) |
| Human wait: time from the main session stopping to the human's next prompt | Human load | Events |
| `./scripts/check` runs and failures | Verification cost | Events |
| Reviewer findings by severity, re-review rounds | Effectiveness of the build loop | `docs/code-reviews/` |
| Escalations and `## Decisions` per scope | Human load, triage quality | `docs/plans/` |
| Escapes: `fix:` commits after merge on files a scope touched | Effectiveness | Git |

## Criteria

### Reader

- **STATS-01**: `framework/scripts/stats` ships with the framework. It is one Python file, standard library only, and reads the repo it runs in: git history, the reflog when present, `docs/plans/`, `docs/code-reviews/`, and `.007/events.jsonl` when present. It prints a per-scope report, and with `--json` it prints the same data as JSON.
- **STATS-02**: The reader works on a project with no event log. Every metric whose source is missing shows as `n/a`, with the reason, rather than zero. With no event log, the reason says telemetry is off and how to turn it on.
- **STATS-03**: The reader identifies scopes from plan files and their branches, and batches from checkpoint commit prefixes (`test(red)`, `feat(green)`, `refactor`, `chore(scaffold)`, `test: pin`).
- **STATS-04**: `bin/007 stats <dir>...` runs the reader from the clone against each named project and adds a cross-project summary. A project installed from an older release, or one without the framework installed, is still read, so the newest reader covers every project.
- **STATS-05**: The reader writes nothing, runs no git command that changes state, and uses no network.

### Event log

- **EVENT-01**: `framework/.claude/hooks/telemetry.py` appends one JSON object per line to `.007/events.jsonl` at the project root. Each object carries `v` (schema version, starting at 1), `ts` (UTC ISO 8601), `event`, `session_id`, `branch` (read from `.git/HEAD`, without running git), `agent_id` and `agent_type` (both `null` for the main session), and the event's own fields.
- **EVENT-02**: `.claude/settings.json` registers the hook with `"async": true` on SubagentStart, SubagentStop, PostToolUse, PostToolUseFailure, Stop, and UserPromptSubmit. For PostToolUse and PostToolUseFailure it records only Bash calls that run `./scripts/check`, `./scripts/test`, or `./scripts/lint`, with the script name, duration, and whether it failed.
- **MAIN-01**: The log covers the main session as well as subagents. SubagentStart and SubagentStop already record the main session's dispatches of the project manager, architect, engineering manager, and reviewer. On Stop, the hook records the main session's cumulative tokens by model, read from `transcript_path` the same way as EVENT-03; the reader takes the last value per session. On UserPromptSubmit, it records a `prompt` event with the timestamp only, never the prompt text, so the reader can measure how long each stop waited for the human.
- **EVENT-03**: On SubagentStop, the hook reads the file at `agent_transcript_path` and records the subagent's total input, output, cache-read, and cache-creation tokens by model. If the file is missing or its shape is unknown, it records the stop without tokens and sets `tokens: null`.
- **EVENT-04**: Each guard (`lane_guard.py`, `git_guard.py`, `adr_write_guard.py`, `agent_guard.py`) records a `denied` event when it blocks: the hook name, the agent, the tool, and the repo-relative path or git subcommand. A failure to record never changes the guard's exit code or message.
- **EVENT-05**: The telemetry hook fails open. Any error, including a malformed input or an unwritable directory, exits 0 with no output.
- **EVENT-06**: When the hook creates `.007/`, it writes `.007/.gitignore` containing `*`, so the directory ignores itself and the project's `.gitignore` needs no change.
- **EVENT-07**: Events never contain file contents, prompts, agent messages, command output, or absolute paths. A test feeds each event type an input full of such text and checks that none of it reaches the log.
- **EVENT-08**: Recording is off by default. The hook and the guards record only when the environment has `AGENT007_TELEMETRY=on`. The documented way to turn it on for one project is the `env` block of `.claude/settings.local.json`, which Claude Code keeps out of git, so each developer opts in for themselves. With it unset, or set to anything else, the hook exits 0 at once and writes nothing, and `.007/` is never created.

### The loop uses it

- **RETRO-01**: `CLAUDE.md` adds a step after a merged PR: the main session runs `./scripts/stats` for the scope and gives the human the report. This is the counts half of FW-10; FW-10's question round and lessons stay separate.
- **RETRO-02**: No agent definition mentions telemetry, metrics, or the event log, and no agent is given the report. A test checks the agent files for those words.

### Keeping it wired

- **SETUP-08**: `/007-setup`'s drift check reports when `.claude/settings.json` doesn't register the telemetry hook, and shows the entries to merge. It also says whether recording is on, and how to turn it on, but never turns it on itself. The human decides; an adopter who opts out by leaving the hooks out isn't nagged twice in one run.
- **INIT-01**: When `007 new` or `007 init` skips an existing `.claude/settings.json`, it prints the framework's `hooks` block as JSON ready to paste, and the `settings.local.json` lines that turn recording on. The next-steps text says recording stays off until those lines are added. FW-11's BOTH-02 is updated to match.
- **WIRE-01**: `test_agent_wiring.py`, or a new test beside it, checks that the framework's own `settings.json` registers `telemetry.py` on the four events in EVENT-02.

### Removal

- **REMOVE-01**: `007 remove` leaves `.007/` in place and lists it among what it kept, since the data belongs to the project. FW-11's spec is updated to say so.

## Threat model

Trusted developers on their own repos. The risks are leaking content into a file someone later shares, slowing the loop, and weakening a guard. EVENT-04, EVENT-05, and EVENT-07 cover them. The transcript format is undocumented, so EVENT-03 must degrade rather than fail when it changes.

## How it's built

Test-first, by the main session with Brian, in this order. Each step is its own PR, and `./scripts/check` passes at every step.

1. **This spec and ADR-002.** The ADR records: local only, with no collector; `.007/` as the log location; the self-ignoring directory; the event schema and its version field; transcripts over OpenTelemetry for per-agent cost, because OpenTelemetry labels every custom agent `custom`; and why the guards log their own denials.
2. **Reader over git and docs (STATS-01 to STATS-05).** Fixture repos built in `tmp_path` by the tests. No hook changes, so it can land and be used on existing projects at once.
3. **Event log (EVENT-01, -02, -05 to -08, MAIN-01, WIRE-01).** Touches `settings.json`, so it needs Brian's explicit approval of the diff. First confirm two behaviors on the current Claude Code release and note the version in the ADR: that a hook process sees variables set in `settings.local.json`'s `env` block, and that Stop and UserPromptSubmit inputs carry `transcript_path` and `session_id` as documented.
4. **Guard denials (EVENT-04).** Touches the guards, which also needs Brian's approval. The guards' existing tests must pass unchanged, plus new tests that a logging failure leaves the exit code alone.
5. **Token capture (EVENT-03).** Synthetic transcript fixtures shaped like the current format (assistant records with `message.model` and `message.usage`). Before writing them, confirm the shape against a real subagent transcript and note the Claude Code version in the ADR.
6. **Loop and setup (RETRO-01, RETRO-02, SETUP-08, INIT-01, REMOVE-01).** Then README, CHANGELOG, and the release as v1.1.0.

After the release, run three scopes in a real project, then decide FW-14 4a and 4c from the reports and record the decisions in the backlog.

## Moving existing projects over

Projects installed from v1.0.0 can adopt this in three tiers. Each tier stands alone, so a project can stop at any of them.

### Tier 0: baseline, with no change to the project

Run the reader from the 007 clone against the project:

    007 stats ~/code/myproject

This reads git history, the reflog, plans, and review findings for every scope the project has already run. Token and timing metrics show `n/a`. Run this before upgrading anything, so the project has a baseline to compare against once events start.

### Tier 1: upgrade to v1.1.0

There is still no update command, so the upgrade is `remove` and then `init`. This release is the first to change `settings.json`, which `init` never overwrites, so the merge matters this time.

1. Finish or pause the current scope. Upgrade between scopes, never while a feature branch is mid-batch, because the hooks change underneath a running engineering manager.
2. Commit or stash any local work, then update the clone to v1.1.0.
3. In the project, run `007 remove`, then `007 init`. `remove` keeps the files you changed: `AGENTS.md` with its profile, and `settings.json` if you moved `git commit` to `allow`. `init` skips them and lists them, and prints the `hooks` block (INIT-01).
4. Merge the kept files by hand. For `settings.json`, paste the printed `hooks` block in; your `permissions` stay as they are. `CLAUDE.md` gets the RETRO-01 step if you kept your own copy. `AGENTS.md` needs no change.
5. Run `./scripts/check-dev-framework`, then `/007-setup` to check for drift. Its drift check confirms the telemetry hook is registered.
6. Review and commit.
7. To start recording, add `AGENT007_TELEMETRY=on` to the `env` block of `.claude/settings.local.json`, as `init` printed. Until then the hooks run and exit at once.

The first scope recorded after step 7 is the first with events. The report marks earlier scopes `git only`, so a before-and-after comparison never mixes the two sources silently.

### Tier 2: cross-project view

Keep the 007 clone and run `007 stats` against every project at once. Older projects are still read at Tier 0 depth, so you can upgrade them one at a time.

### Opting out and rolling back

To stop recording, remove `AGENT007_TELEMETRY` from `settings.local.json`, or remove the `hooks` block from `settings.json`. To delete the data, delete `.007/`. Neither affects the guards or the loop.

### Projects from before v1.0.0

Their `.007-version` doesn't resolve, so `remove` refuses. Reinstall from v1.1.0 as the v1.0.0 changelog describes, then follow Tier 1 from step 4. Tier 0 works on them without reinstalling.

## Out of scope

- Any network collector, hosted dashboard, or shared aggregation across people. Revisit only if outside adopters appear and ask to opt in.
- An `007 upgrade` command (FW-11's "Updates"). This release makes the manual merge more costly, so it is the obvious next item if Tier 1 proves painful.
- OpenTelemetry export. Anyone who wants it can set Claude Code's own variables; the framework neither requires nor configures it.
- Logging the main session's diff-check outcomes. No hook sees them; re-dispatches in the event log stand in for violations.
- Recording anything about the human's prompts beyond their timestamps.

## Decisions

Brian, 2026-11-02:

1. Is recording on by default or off? Off. A developer turns it on per project with `AGENT007_TELEMETRY=on` (EVENT-08).
2. Does the log cover the main session or only subagents? Both (MAIN-01).
3. Should `007 init` print the `settings.json` hooks block when it skips that file? Yes (INIT-01).

## Open questions

None.
