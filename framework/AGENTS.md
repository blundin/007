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
- Review findings: `docs/code-reviews/` (a session file per review;
  `known-issues.json` lists what is still open)

## Setup and checks

    ./scripts/check

`./scripts/check` is the single gate: lint, format, strict types, and the full
test suite with a coverage threshold. CI runs the same script.
`./scripts/test <paths>` runs named tests, and `./scripts/lint <paths>` lints
and type-checks named files.

## Specs

- Changes in the `src` lane are driven by acceptance-criterion IDs in a spec,
  such as `AUTH-03` or `PAGE-06`.
- Specs under `docs/specs/` are written and approved by humans. Don't edit them.

## Test rules

- Write the test before the code.
- Every test that verifies a spec requirement carries the criterion tag
  described in the Project profile.
- A new test must first fail for a valid reason: an assertion about the
  targeted behavior, or the not-implemented signal from a stub (see the
  Project profile). It must never error at import, collection, or fixture
  setup.
- Tests never touch the network. Use the HTTP mocking tool in the Project
  profile.
- Tests that need a live external system are opt-in, run only locally, and
  are excluded by default.
- Never put real personal data in the repository.

## Code rules

- `./scripts/check` passes in full before any change is done.
- None of the banned suppressions listed in the Project profile.
- No skips or expected-failure markers to hide failures, and no special cases
  keyed to test input values.
- Never delete or weaken an existing assertion to make code pass.
- A refactor changes structure only. It never changes tests or observable
  behavior, including the public interface and error messages.
- Runtime dependencies are limited to the list in the Project profile.
- Never read, print, or commit secrets, API keys, or `.env` files.

## Done

A change is done when every criterion ID in scope is referenced by the
criterion tag on at least one passing test (check with the profile's grep),
and `./scripts/check` passes, including the coverage gate.

## Stop and ask a human when

- A spec is ambiguous or silent about the behavior you need.
- A test appears to contradict the spec.
- A new dependency is needed.

## Commits

- Conventional commits: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`.
- Never commit directly to `main`.

## Project profile

Every agent reads this section. Fill in each item; the examples show what a
Python library filled in.

- **Language and tools:** <!-- FILL. Example: Python 3.13, uv, ruff, mypy
  strict, pytest. -->
- **Fixture path:** <!-- FILL. Example: tests/fixtures/ -->
- **Criterion tag:** <!-- FILL: how a test names the criterion it verifies,
  and the grep that finds it. Example: @pytest.mark.spec("AUTH-03"), found
  with grep -rn 'mark.spec("AUTH-03")' tests/ -->
- **Stub convention:** <!-- FILL: what a scaffolded body does, so its tests
  fail rather than error. Example: raise NotImplementedError. -->
- **Failure versus error:** <!-- FILL: how ./scripts/test output shows a
  failed test versus an errored one. Example: pytest -rA prints FAILED for an
  assertion and ERROR for a setup or collection problem. -->
- **Banned suppressions:** <!-- FILL: the language's ways of silencing
  checks. Example: # type: ignore, # pragma: no cover, cast or Any used to
  silence the type checker, bare or broad except. -->
- **Public interface:** <!-- FILL: what counts as observable behavior for a
  refactor. Example: this is a library, so every public name, signature,
  return type, raised exception, and error message. -->
- **Runtime dependencies:** <!-- FILL. Example: httpx and Pydantic only. -->
- **Test isolation:** <!-- FILL: the HTTP mocking tool and the
  property-testing library, if any. Example: respx; Hypothesis. -->
- **Property-testing targets:** <!-- FILL: properties the test-engineer must
  cover with generated input, or "none". Example: no generated string can
  escape its literal in the compiled filter expression. -->
- **Domain attacks:** <!-- FILL: project-specific attack categories for the
  test-engineer, or "none". Example: the upstream API returns 401 with an
  empty body, not 403, for a key that lacks permission. -->
- **Domain notes:** <!-- FILL: path to verified behavior of external
  systems, or "none". Example: docs/upstream-api-notes.md -->
- **Threat model:** <!-- FILL: who the adversarial tests defend against, or
  the spec section that says. Example: docs/specs/PRD.md, Threat model. -->
