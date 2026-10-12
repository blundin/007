# <!-- FILL: project name -->

<!-- FILL: one line on what this project is. -->
The product spec is in [`docs/specs/`](docs/specs/).

These rules apply to every contributor, human or agent, whatever tool you use.

## Layout

- Source: the `src` lane in [`.claude/lanes.json`](.claude/lanes.json)
- Tests: the `test` lane in `.claude/lanes.json`
- Fixtures: the fixture path in the Project profile below
- Specs: `docs/specs/`
- Plans: `docs/plans/`
- Decision records: `docs/adr/` (written by the `architect` agent)
- Review findings: `docs/code-reviews/` (a session file per review; `known-issues.json` lists what is still open)

## Setup and checks

    ./scripts/check

`./scripts/check` is the single gate: lint, format, strict types, and the full test suite with a coverage threshold. CI runs the same script. `./scripts/test <paths>` runs named tests, and `./scripts/lint <paths>` lints and type-checks named files.

## Specs

- Changes in the `src` lane are driven by acceptance-criterion IDs in a spec, such as `AUTH-03` or `PAGE-06`.
- Specs under `docs/specs/` are written and approved by humans. Edit one only when a human explicitly directs it, and only with their approval of the specific changes.

## Test rules

- Write the test before the code.
- Every test that verifies a spec requirement carries the criterion tag described in the Project profile.
- A new test must first fail for a valid reason: an assertion about the targeted behavior, or the not-implemented signal from a stub (see the Project profile). It must never error at import, collection, or fixture setup.
- Tests never touch a live external system: HTTP services, databases, queues, the real clock, or the filesystem outside the test's own temporary space. Isolate each with the tools in the Project profile's Test isolation.
- Tests that need a live external system are opt-in, run only locally, and are excluded by default.
- Never put real personal data in the repository.

## Code rules

- `./scripts/check` passes in full before any change is done.
- None of the banned suppressions listed in the Project profile.
- No skips or expected-failure markers to hide failures, and no special cases keyed to test input values.
- Never delete or weaken an existing assertion to make code pass.
- A refactor changes structure only. It never changes tests or observable behavior, including the public interface and error messages.
- Runtime dependencies are limited to the list in the Project profile.
- Never read, print, or commit secrets, API keys, or `.env` files.

## Done

A change is done when every criterion ID in scope is referenced by the criterion tag on at least one passing test (check with the profile's grep), and `./scripts/check` passes, including the coverage gate.

## Stop and ask a human when

- A spec is ambiguous or silent about the behavior you need.
- A test appears to contradict the spec.
- A new dependency is needed.

## Commits

- Conventional commits: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`.
- Never commit directly to `main`.

## Project profile

Every agent reads this section. Run `/007-setup` in Claude Code to draft it from the repo; it shows each value and its evidence before writing anything, and explains every item with examples.

- **Language and tools:** <!-- FILL: the language, its version, and the package manager, linter, formatter, type checker, and test runner. See /007-setup. -->
- **Fixture path:** <!-- FILL: where test fixtures live, inside the test lane. See /007-setup. -->
- **Criterion tag:** <!-- FILL: how a test names the criterion it verifies, and the grep that finds it. See /007-setup. -->
- **Stub convention:** <!-- FILL: what a scaffolded body does, so its tests fail rather than error. See /007-setup. -->
- **Failure versus error:** <!-- FILL: how ./scripts/test output tells a failed test from an errored one. See /007-setup. -->
- **Banned suppressions:** <!-- FILL: the language's ways of silencing a check. See /007-setup. -->
- **Public interface:** <!-- FILL: what counts as observable behavior for a refactor. See /007-setup. -->
- **Runtime dependencies:** <!-- FILL: the only runtime dependencies allowed. See /007-setup. -->
- **Test isolation:** <!-- FILL: how tests isolate each external system the project uses, and the property-testing library, if any. See /007-setup. -->
- **Property-testing targets:** <!-- FILL: properties the test-engineer must cover with generated input, or "none". See /007-setup. -->
- **Domain attacks:** <!-- FILL: attack categories specific to this project, or "none". See /007-setup. -->
- **Domain notes:** <!-- FILL: path to verified behavior of external systems, or "none". See /007-setup. -->
- **Threat model:** <!-- FILL: who the adversarial tests defend against, or the spec section that says. See /007-setup. -->
