# Setup reference

One section per item: what it controls, how to find it, and an example for each of three stacks. The examples show the shape of an answer; take the values from this repo, and let the probes overrule an example. The Rails examples use Minitest, Rails' default; notes say where RSpec differs.

## Project profile

### Language and tools

**Controls:** what every agent assumes about the toolchain, and which commands the scripts call.

**How to find it:** the manifests (`pyproject.toml`, `uv.lock`, `Gemfile`, `.ruby-version`, `Package.swift`, `*.xcodeproj`, `package.json`, `go.mod`, `Cargo.toml`), version files (`.tool-versions`, `mise.toml`), tool configs (`ruff.toml`, `.rubocop.yml`, `.swiftlint.yml`), and what CI runs.

- *Python library:* Python 3.13, uv, ruff (lint and format), mypy strict, pytest.
- *Rails app:* Ruby 3.4, Rails 8, bundler, RuboCop with rubocop-rails-omakase, Minitest through `bin/rails test`. No type checker.
- *Swift app:* Swift 6.2 with strict concurrency, Swift Package Manager, SwiftLint, swift-format, Swift Testing. The compiler is the type checker.

### Fixture path

**Controls:** where the test engineer puts test data. It must sit inside the `test` lane, or the lane guard blocks the write.

**How to find it:** existing fixture or factory directories under the test directory. If there are none, propose one inside the test lane.

- *Python library:* `tests/fixtures/`
- *Rails app:* `test/fixtures/` for YAML fixtures, which `fixtures :all` loads, and `test/fixtures/files/` for uploaded files. With RSpec and FactoryBot, `spec/factories/`.
- *Swift app:* `Tests/AppTests/Fixtures/`, declared as resources of the test target in `Package.swift`.

### Criterion tag

**Controls:** how a test names the spec criterion it verifies. The engineering manager, the project manager, and the main session grep for it to decide what's delivered.

**How to find it:** an existing convention in the tests. Otherwise propose the runner's own metadata, so the tag is data rather than a comment. If the runner has none, start the test's name with the ID. The grep must match one exact ID.

- *Python library:* `@pytest.mark.spec("AUTH-03")`, with `spec` registered under `markers` in the pytest config. Found with `grep -rn 'mark.spec("AUTH-03")' tests/`.
- *Rails app:* Minitest has no metadata, so the name carries it: `test "AUTH-03: rejects an expired token" do`. Found with `grep -rn 'test "AUTH-03:' test/`. With RSpec, use metadata: `it "rejects an expired token", spec: "AUTH-03" do`.
- *Swift app:* the test's display name starts with the ID, `@Test("AUTH-03: rejects an expired token")`. Found with `grep -rn '@Test("AUTH-03' Tests/`.

### Stub convention

**Controls:** what the app developer writes in a scaffolded body, so a new test fails at RED instead of erroring.

**How to find it:** start from the language's not-implemented signal, then probe it: a test against the stub must report as failed, not errored. If the runner reports the signal as an error, the stub returns a value the tests will reject instead.

- *Python library:* `raise NotImplementedError`. pytest reports it as a failure.
- *Rails app:* return `nil`, or another value the tests will reject. Minitest reports any exception, `NotImplementedError` included, as an Error, the same as an undefined name. With RSpec, `raise NotImplementedError` works, since RSpec reports an exception inside an example as a failure.
- *Swift app:* `throw StubError.notImplemented` where the signature throws; otherwise return a value the tests will reject, such as an empty collection or `nil`. Never `fatalError`, which kills the whole test process.

### Failure versus error

**Controls:** how the engineering manager tells a valid RED (an assertion failed) from an invalid one (the test couldn't run).

**How to find it:** run the four probes (an assertion that fails, a file that can't load, an undefined name inside a test body, a stub) with the drafted `scripts/test` command. Record exactly what it prints for each.

- *Python library:* `pytest -rA` prints `FAILED` for an assertion or a stub and `ERROR` for a setup or collection problem. An undefined name inside a test is `FAILED` with a `NameError`, so the valid-RED check reads the exception too.
- *Rails app:* a failure prints a `Failure:` block with `Expected: ... Actual: ...`, and `F` in the progress line. An exception inside a test, such as a `NameError`, prints an `Error:` block and `E`. A file that can't load aborts the run with a backtrace and no summary. With RSpec, failures and exceptions both appear under `Failures:`, and a load problem prints `An error occurred while loading`.
- *Swift app:* a failure prints `Expectation failed:` and the run completes. A missing symbol stops the build with `error: cannot find ... in scope`, and no tests run. A crash prints `exited with unexpected signal`.

### Banned suppressions

**Controls:** the ways of silencing a check that no agent may use to get to green.

**How to find it:** the language's suppression comments and escape hatches, plus any the linter config already forbids.

- *Python library:* `# type: ignore`, `# noqa`, `# pragma: no cover`, `cast` or `Any` used to silence the type checker, and bare or broad `except`.
- *Rails app:* `# rubocop:disable`, `# :nocov:`, `rescue Exception`, and a `rescue` that swallows the error.
- *Swift app:* `// swiftlint:disable`, `try!`, a force unwrap or `as!` used to dodge handling, `@unchecked Sendable`, `nonisolated(unsafe)`, and `@preconcurrency` used to silence the checker.

### Public interface

**Controls:** what the refactorer must not change and the reviewer treats as behavior.

**How to find it:** whether this is a library, an app, or a service, and who depends on it. The README and the spec usually say. With no spec and a boilerplate README, who depends on it is a *needs you*.

- *Python library:* every public name, signature, return type, raised exception, and error message.
- *Rails app:* routes and their parameters, status codes, response bodies and JSON shapes, user-visible text, the database schema, and the effects of jobs and mailers. Internal classes are not part of it.
- *Swift app:* user-visible text and behavior, the persisted data format, and the API of any module other targets import. View internals are not part of it.

### Runtime dependencies

**Controls:** the only dependencies code may use at runtime. Anything else is a new dependency, which stops the loop for the human.

**How to find it:** the manifest's runtime section. Development and test dependencies don't count, and neither do deploy or command-line tools the app never loads (in Rails, gems with `require: false` such as kamal and thruster). Propose the current list as the allow-list.

- *Python library:* httpx and Pydantic only.
- *Rails app:* the gems in the `Gemfile`'s default group.
- *Swift app:* the package dependencies of the app target, or none beyond Apple's frameworks.

### Test isolation

**Controls:** how tests stay off every live external system, and which property-testing library the test engineer uses.

**How to find it:** list the external systems the code touches: grep for HTTP clients, database adapters, queues, the clock, and file access. Then find the isolation tool each one already uses in the tests. A system with no tool is a *needs you*.

- *Python library:* HTTP with respx, the clock with time-machine, files in `tmp_path`. Property testing with Hypothesis.
- *Rails app:* HTTP with WebMock, real connections disabled; the database through transactional tests; the clock with `travel_to`; jobs with the test adapter. No property-testing library.
- *Swift app:* HTTP through a `URLProtocol` stub; the clock as an injected `Clock`; SwiftData in an in-memory container. No property-testing library.

### Property-testing targets

**Controls:** the properties the test engineer must cover with generated input.

**How to find it:** in the spec, look for round trips (parse then format, encode then decode), invariants, and anything that builds strings from input. Use "none" when there's no property-testing library.

- *Python library:* no generated string can escape its literal in the compiled filter expression.
- *Rails app:* none.
- *Swift app:* none. With a library, a candidate is that encoding then decoding any model value returns an equal value.

### Domain attacks

**Controls:** attack categories the test engineer adds to its generic ones in every adversarial batch and sweep.

**How to find it:** the external systems and their known quirks, the threat model, the domain's typical failures, and the project's past bugs and lessons. It grows over time: triage proposes new ones when a sweep or a review finds a project-specific hazard.

- *Python library:* for an HTTP client, HTTP failures (401 versus 403, 404, 400 with error bodies, 429 with and without Retry-After, 5xx, timeouts, malformed JSON, empty bodies, HTML error pages); retries (non-idempotent requests are never retried, others only where the spec says it's safe); pagination (empty results, counts that change mid-iteration, the last page); and the upstream API returning 401 with an empty body, not 403, for a key that lacks permission.
- *Rails app:* another user's record by ID on every member route; mass assignment of protected attributes; a double-submitted form on a non-idempotent action; times that cross the user's and the server's time zones.
- *Swift app:* the app backgrounded mid-operation; no network; a permission denied (location, notifications); the largest Dynamic Type size; data saved by an older schema version.

### Domain notes

**Controls:** where agents read the verified behavior of systems the project doesn't control, instead of guessing.

**How to find it:** an existing notes file in `docs/`. Otherwise "none", and the first verified finding about an external system creates one.

- *Python library:* `docs/upstream-api-notes.md`
- *Rails app:* `docs/payment-gateway-notes.md`, or none.
- *Swift app:* none.

### Threat model

**Controls:** who the adversarial tests defend against. Triage drops findings no real caller could produce.

**How to find it:** the spec's threat model section. If the spec has none, that's a *needs you*: specs are the human's to write.

- *Python library:* `docs/specs/PRD.md`, Threat model. Callers are trusted application code; the upstream server may be misconfigured but not malicious.
- *Rails app:* `docs/specs/PRD.md`, Threat model. Signed-in users trying to reach other users' data, and anonymous traffic on public routes.
- *Swift app:* `docs/specs/PRD.md`, Threat model. One user on their own device; data from the server is untrusted.

## Lanes and scripts

### lanes.json

**Controls:** where each triad agent may write. The test engineer writes only in `test`; the app developer and the refactorer only in `src`.

**How to find it:** where tests and code live. An entry ending in `/` allows a whole directory; any other entry allows exactly one file, for a file the code needs whose directory must stay out, such as a Rails app's `config/routes.rb`. Paths are relative to the repo root, with no `..`. Leave configuration, migrations, CI, and dependency manifests out of both lanes, so a change to them stops the loop for the human.

- *Python library:* `{"test": ["tests/"], "src": ["src/"]}`
- *Rails app:* `{"test": ["test/"], "src": ["app/", "lib/"]}`, or `spec/` for RSpec. Add `"config/routes.rb"` to `src` if batches add routes. The rest of `db/`, `config/`, and `bin/` stays out.
- *Swift app:* `{"test": ["Tests/"], "src": ["Sources/"]}`. An Xcode project might use `{"test": ["MyAppTests/"], "src": ["MyApp/"]}`.

### scripts/check

**Controls:** the single gate: lint, format, strict types, every test, and coverage. GREEN, REFACTOR, and done all require it to pass. CI should run it too.

**How to find it:** what CI runs, in the same order, and any local CI definition. Exit 0 only when everything passes. Pass extra arguments through to the test runner. A CI step that needs the network or secrets, or a missing piece such as a coverage tool, is a *needs you*.

- *Python library:* `uv run ruff check . && uv run ruff format --check . && uv run mypy . && uv run pytest --cov --cov-fail-under=90 "$@"`
- *Rails app:* `bin/rubocop && bin/brakeman --quiet --no-pager --exit-on-warn && bin/rails db:test:prepare test "$@"`, with SimpleCov's `minimum_coverage` in `test/test_helper.rb` if the project adds it.
- *Swift app:* `swiftlint lint --strict && swift format lint --strict --recursive Sources Tests && swift test --enable-code-coverage "$@"`, plus a coverage threshold check if the project has one.

### scripts/test

**Controls:** how agents run named tests and read each outcome. Its output is what `Failure versus error` describes.

**How to find it:** the runner's way to run selected tests with one line per outcome.

- *Python library:* `uv run pytest -rA "$@"`
- *Rails app:* `bin/rails test -v "$@"`, or `bundle exec rspec --format documentation "$@"` for RSpec.
- *Swift app:* `swift test --filter "$1"`. Swift selects tests by name, not path, so say so in `Failure versus error`.

### scripts/lint

**Controls:** how agents lint, format-check, and type-check the files they changed.

**How to find it:** the linter, formatter, and type checker from `Language and tools`, run on the paths given.

- *Python library:* `uv run ruff check "$@" && uv run ruff format --check "$@" && uv run mypy "$@"`
- *Rails app:* `bin/rubocop "$@"`
- *Swift app:* `swiftlint lint --strict "$@" && swift format lint --strict "$@"`. Types are checked by `swift build`.
