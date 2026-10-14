# Framework lessons

Each lesson names its source and, where it led to work, the backlog item.

The lessons below come from the framework's first project. Their sources name files in that repository, not this one.

## Re-examine before re-patching

When a sweep reopens an area that was already patched, decide among four options before writing the next RED batch: build from an allowlist, delegate to a library, narrow the requirement, or accept the risk. Hand-rolled denylist scrubbing of `Location` cost two batches before it was replaced with building from httpx's parsed URL.

Source: `docs/checkpoint-client-core.md`, Lessons.

## Probe prompts must forbid rewriting the command

In the FW-01 hook probe, the test-engineer ran `git -C <path> tag` instead of the `git tag` it was given, which tested a different code path in the hook. Probe prompts should say to run the command exactly as written, with no `-C` and no `cd`.

Source: FW-01 hook probe, 2026-10-02.

## Read the deployed source before theorizing

A v2 401 drew two rounds of guesses about Rock permissions. It was settled only by reading Rock's source at the deployed release tag (18.4.1), which showed that v2 accepts the REST key and that a permission denial is also a 401. Read the source at the deployed tag, and the instance's own `/api/v2/doc`, before proposing a cause. Findings are in `docs/rock-api-notes.md`.

Source: v2 401 investigation, 2026-10-02.

## Probe again after every config change

The human's permission grant had worked, but a probe run before it took effect still showed 401, and that sent the diagnosis back to theory. After any change on the Rock side, rerun the discriminating probe first: without and with the key, v1 against v2, header against `?apikey=`.

Source: v2 401 investigation, 2026-10-02.

## Sandboxed git can half-switch a branch

A sandboxed `git checkout main` couldn't write under `.claude/hooks/` or `.claude/agents/`, so it switched branches but left those files from the old branch behind. A sandboxed `git pull` over SSH failed at the proxy. The main session runs branch switches and pulls outside the sandbox, then checks `git status` and compares any leftover files with the target before resetting.

Source: updating `main` after PR #4, 2026-10-02.

## The project manager pays for itself before the first run

FW-11 acceptance passed on all three runs. Across four planning passes on Querying, the PM raised 7, 9, 3, and then 0 blocking questions, each of which would otherwise have stopped the test-engineer mid-run. It also caught a missing prerequisite, the models spec. Its weaknesses: two "next" runs ordered scopes differently when one choice was open; its "delivered" grep misses spec text added after delivery (the ERR-03 401 hint); and its citations drop escapes, quoting `\u0040x\u002Eorg` as `@x.org`. Set a stopping point: once the remaining questions are single edge cases, record them as run decisions in the plan instead of running another pass.

Source: `docs/checkpoint-query-compiler.md`, Framework. Led to: FW-10 retrospective input.

## Examples bias the setup skill; probes must overrule them

The first `/007-setup` trial ran on a default Rails app, which uses Minitest. The reference's Rails examples assumed RSpec, and four of them were wrong for it. The Stub convention example was harmful: Minitest reports a raised `NotImplementedError` as an Error, so a stub that follows the example makes every valid RED look invalid. The trial also showed that a test run writes to the repo (logs, caches), that the suite may not run at all, and that the draft had no place for findings outside the profile. The skill now says probes overrule examples, uses Minitest for its Rails examples, checks `git status` around every run, runs the existing suite first, and presents findings before questions.

Source: FW-15 trial run on a scratch Rails 8.1 app, 2026-10-12. Led to: FW-15.
