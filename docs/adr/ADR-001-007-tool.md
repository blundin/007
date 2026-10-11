# ADR-001: `007`, a bootstrap and update tool for the framework

The tool is named **007**, after the template repo. It installs, configures and updates the framework (the Adversarial TDD Loop) in a project.

**Status:** Accepted, then simplified 2026-10-05 (see Amendment 2). Pending Brian's review of this record **Date:** 2026-10-05 **Deciders:** Brian Lundin

## Context

`007` was extracted from the framework's first project at `319e93c`. Today a project adopts it by hand, following the eight steps in `README.md`, and lessons move between projects by hand too (README, Provenance). We want a tool that can:

1. **Bootstrap** a new, empty project into the framework.
2. **Apply** the framework to an existing repo.
3. (Implied) **Update** adopted projects as the framework evolves. Without this, every project drifts from the template.

What the tool has to install falls into four groups:

| Group | Files | Problem |
|---|---|---|
| Fixed | `.claude/agents/*`, `.claude/hooks/*` and their tests, `.claude/skills/review-tracker`, `CLAUDE.md` (loop), `scripts/check-dev-framework`, `docs/*/README.md` | Copy verbatim; update cleanly |
| Filled in per project | `.claude/lanes.json`, the 13 `FILL` items in the AGENTS.md Project profile, `scripts/{check,test,lint}` | Needs judgment about the stack. An existing repo already has these answers in its tooling |
| Merged | `CLAUDE.md`/`AGENTS.md` (if the repo has them), `.claude/settings.json`, `.gitignore` | Existing content must survive |
| Project-owned after install | `docs/dev-framework/backlog.md`, `lessons.md`, specs | Never overwritten |

### Constraints from research (verified 2026-10-05; see Sources)

- **Claude Code plugins can ship** agents, skills, commands, hooks and `bin/`.
- **Plugins cannot ship:**
  - a CLAUDE.md (one at the plugin root is not loaded);
  - project `settings.json` permissions (only `agent` and `subagentStatusLine` are honored);
  - per-agent `hooks:` in agent frontmatter (ignored for plugin agents).
- **Why that matters here:** the lane model depends on per-agent hooks, e.g. `app-developer.md:11` runs `lane_guard.py src` only while that agent is active. Moved into a plugin, the lane guard becomes a plugin-wide hook. It would then have to work out for itself which subagent is calling. [unverified: whether hook input reliably carries the agent type.]
- **Requiring a plugin from a repo:** `.claude/settings.json` can declare it with `extraKnownMarketplaces` and `enabledPlugins`. It is honored only after the user accepts workspace trust. An external-source plugin still needs a manual `claude plugin install` per contributor.
- **Copier:**
  - applies to non-empty existing directories out of the box;
  - keeps answers in `.copier-answers.yml`;
  - `copier update` does a 3-way merge against git-tagged template versions;
  - supports `_skip_if_exists` for files the project owns, `_migrations` tied to versions, and `_tasks`.
- **Copier's costs:** it needs a clean working tree. Conflicts show up as inline markers or `.rej` files.
- **cruft:** has `link` and `update`, but no tag-aware versioning and no migrations.
- **No update path:** GitHub templates, degit/tiged and `/init`.

## Options considered

### Option A: Copier template (deterministic)

Turn `007` into a Copier template. Questions:
- project name;
- stack preset (python-uv, rails, node, other), which selects canned `scripts/*`, lanes and profile text;
- the lane paths;
- whether commits are signed (decides whether `git commit` goes on the `ask` or `allow` list).

Merged files use Jinja conditionals. Project-owned files go under `_skip_if_exists`.

| Dimension | Assessment |
|---|---|
| Complexity | Low to medium. Mostly moving files and adding `copier.yml` |
| Bootstrap | Strong |
| Existing repo | Fair. Overwrite prompts per file. Merging into an existing CLAUDE.md or settings.json is crude |
| Updates | Strong. `copier update` plus migrations, versioned by git tag |
| Profile quality | Weak for anything off-preset. The "other" preset leaves `FILL` markers |
| Familiarity | Python, uv-installable (`uvx copier`) |

**Pros:** deterministic, testable and versioned. It gives a real answer to the update problem. Minimal code. **Cons:**
- It can't look at an existing repo and work out its test runner, coverage setup or failed-vs-error output.
- Each stack preset is something to maintain.
- Conflict markers can end up in agent prompts, where they're easy to miss.

### Option B: Claude Code plugin plus an agentic installer skill

Publish the framework as a plugin from a personal marketplace.
- **What the plugin carries:** the five agents, review-tracker, the hooks, and an `/007` skill.
- **What the skill does:** it interviews the human (like `/init`'s interview mode). It inspects the repo to detect the language, test runner, linter and existing CLAUDE.md. Then it writes the project-side files the plugin can't carry: CLAUDE.md, the AGENTS.md profile, lanes.json, `scripts/*`, and settings.json with `enabledPlugins`.

| Dimension | Assessment |
|---|---|
| Complexity | Medium to high |
| Bootstrap | Good |
| Existing repo | Strongest. It can read the repo and fill the profile and scripts from what's actually there, and merge prose intelligently |
| Updates | Split. Plugin-shipped parts auto-update by version. Project-side files (the CLAUDE.md loop rules, settings) have no merge story beyond "re-run the skill" |
| Profile quality | High, but not deterministic. Two runs can differ |
| Risk | Per-agent lane hooks don't work in plugin agents, so `lane_guard` has to be redesigned as a plugin-level hook that identifies the active subagent. That breaks the README's model of a self-contained repo |

**Pros:** handles any stack without presets. Installs with one command. It's also the most "Claude-native" option. **Cons:**
- The lane redesign is the core safety mechanism, and it's on a path we haven't verified.
- Updating the loop rules (CLAUDE.md) isn't solved.
- It's harder to test: the installer's output depends on the LLM.
- Contributors need the plugin installed, or the agents vanish.

### Option C: Hybrid. Copier for the structure, an agentic skill for the judgment calls (recommended)

Copier owns every file in the Fixed and Merged groups, and seeds the filled-in files with `FILL` markers, exactly as the template does today. The template also installs a project-local skill, `.claude/skills/007/`, committed with the rest. After `copier copy`, the human starts a session and runs `/007`. The skill:
1. inspects the repo (or asks about the intended stack for a new one);
2. proposes lanes, the 13 profile items and the three scripts, and waits for approval (this matches the "plan before implement" rule);
3. writes them and runs `./scripts/check-dev-framework` and `./scripts/check` to prove the scripts work. It confirms `scripts/test` tells failed from errored by running a deliberately failing and a deliberately erroring sample test, then deleting both.

Updates use `copier update`. The profile, lanes and scripts are `_skip_if_exists`, so updates never touch the judgment work. Because the agents stay in the repo, per-agent lane hooks keep working unchanged.

| Dimension | Assessment |
|---|---|
| Complexity | Medium: `copier.yml` plus one skill |
| Bootstrap | Strong |
| Existing repo | Strong. Copier lays down files, the skill reconciles them with the real tooling |
| Updates | Strong for framework files. Project-owned files are deliberately left alone |
| Profile quality | High, with a verification step that's deterministic |
| Risk | Merging into an existing CLAUDE.md still needs care. Proposal: the template's CLAUDE.md is `@AGENTS.md` + `@.claude/LOOP.md`, so the loop rules live in a file Copier fully owns, and the project's own CLAUDE.md text never conflicts |

**Pros:**
- Each tool does what it's good at.
- Keeps the self-contained repo model and the hooks as they are.
- Updates are versioned.
- The skill can be re-run after a stack change.

**Cons:**
- It's two steps (`uvx copier copy`, then `/007`).
- `copier update` still needs a clean tree, and someone has to resolve conflicts.
- Two things to maintain.

### Option D: Custom Python CLI (`uv tool install 007`, command `007`)

Note: `007` works as a command and a distribution name, but it isn't a valid Python import name, so the package would need an internal module name such as `oh_oh_seven`.

A small purpose-built CLI. Each file carries an ownership class in a manifest (managed / seeded / merged). A lockfile records hashes, so on update the CLI can tell when a managed file has been edited locally and stop instead of overwriting. It also knows how to merge `settings.json` (JSON-aware) and `.gitignore` (line-set union). This is a lighter take on the projen model.

| Dimension | Assessment |
|---|---|
| Complexity | High. We'd be rebuilding what Copier already does |
| Existing repo | Good. Structured merges for JSON beat Copier's text merges |
| Updates | Good, but we'd own every edge case |
| Profile quality | Same as A unless paired with a skill (which brings it back to C) |

**Pros:** full control. JSON-aware settings merges. No templating syntax in the framework files. **Cons:**
- Most code to write and test.
- It reinvents Copier's update engine.
- It goes against the "simplest approach" principle.

## Trade-off analysis

The deciding question is how to split the work: **deterministic file management** (install, update, merge) versus **judgment** (what this repo's test runner and lanes are). A puts everything on the deterministic side and fails on judgment. B puts everything on the judgment side and loses updates, plus the per-agent hook model the framework's safety depends on. D is A done by hand. C uses an established tool for the deterministic part and an agent for the judgment part, and puts its verification step on what matters most: proving `scripts/test` separates failures from errors.

The second deciding factor is the **plugin hook limitation**. Until plugin agents support per-agent hooks, or plugin-level hooks can reliably identify the calling subagent, putting the agents in a plugin weakens the lane guarantee. This counts against B now; it's worth revisiting later.

## Consequences (if C is accepted)

- **Easier:**
  - a new project is two commands;
  - an existing repo gets a profile built from its real tooling;
  - framework fixes reach projects with `copier update` instead of by hand.
- **Harder:**
  - `007` becomes a Copier template, so its own files gain `.jinja` suffixes where templating is needed. Keep this to a handful of files;
  - template releases need git tags.
- **To revisit:**
  - moving agents and skills to a plugin once per-agent hooks work in plugin agents;
  - whether that first project itself should be linked with `copier copy` onto its existing tree;
  - FW-02 (worktrees) interacts with `$CLAUDE_PROJECT_DIR` in the hooks either way.

## Decisions from Brian (2026-10-05)

1. **Audience: Brian and other teams.** The template has to be installable from a shared git remote, with tagged releases and release notes. A team that doesn't sign commits must be able to opt out of the `ask` rule. A plugin marketplace isn't needed for distribution: `uvx copier copy gh:<org>/007 .` is the single entry point.
2. **Updates are a must-have.** That rules out B (no update path for the project-side files) and plain template repos. It leaves A, C or D, and C wins on handling existing repos.
3. **Split CLAUDE.md and keep the multi-agent design.** The template's CLAUDE.md becomes `@AGENTS.md` + `@.claude/LOOP.md`, and Copier fully owns `LOOP.md`. The five agents stay in the repo with their per-agent lane and git hooks, so the design that separates roles is unchanged.

**Decision: Option C**, with the split above. Revisit a plugin only if Claude Code adds per-agent hooks for plugin agents.


## Amendment (2026-10-05): v1 scope

A design review found that most of the risk in Option C sits in the update path: conflict markers in live agent prompts, fork tags confusing Copier's version selection, text merges producing invalid JSON, and Copier `_tasks` needing `--trust`. A review of the `/007` skill found that it adds consistency more than capability, since Claude can already follow the README's Adopting steps. The real risk is a profile that looks right but is wrong. The decision is still Option C, delivered in three releases:

- **v1:** 007 as a Copier template, copy only. Includes the CLAUDE.md split (`@AGENTS.md` + `@.claude/LOOP.md`), the Project profile moved to its own file, and a deterministic `scripts/check-adoption`. It has no Copier tasks. Existing Merged files are kept unchanged, and the check reports what's missing.
- **v1.1:** the `/007` skill, built after watching real adoptions. It runs `check-adoption` rather than re-implementing it.
- **v2:** updates through two layers: 007 upstream, then a team fork via `git merge`, then projects via `copier update`. v1 already writes `.copier-answers.yml`, so v2 needs no migration.

This supersedes the earlier idea of section markers in agent files. Teams may edit core instructions and agents freely, so v2 relies on 3-way merge, not on markers that block edits.

The spec is [`FW-11-007-tool.md`](../specs/FW-11-007-tool.md).

## Amendment 2 (2026-10-05): simplified to a copy command

Each design round added requirements: updates, team forks, merging into existing files, an adoption check, and this repo installing its own template. The audits then kept finding problems in those additions. Brian asked for something like `rails new`, but simple.

**Decision:** a single Python script, `bin/007`, with two commands:
- `new <dir>` creates a directory, runs `git init` and copies the framework;
- `init` copies the framework into the current repo.

It copies a fixed list of paths from its own checkout and never overwrites a file; skipped files are listed. It writes `.007-version` with the commit it copied from, then prints the setup steps.

This replaces Copier (Option C). Option D was rejected because it meant building an update engine. Without updates, a copy script is simpler than Copier. These are dropped for now:
- the CLAUDE.md/LOOP.md split;
- the profile file;
- `check-adoption`;
- the `/007` skill;
- updates;
- the `template/` folder.

`.007-version` keeps updates possible later.

The spec is [`FW-11-007-tool.md`](../specs/FW-11-007-tool.md).

## Sources

- Copier updating: https://copier.readthedocs.io/en/stable/updating/
- Copier FAQ (existing projects): https://copier.readthedocs.io/en/stable/faq/
- Copier configuring: https://copier.readthedocs.io/en/stable/configuring/
- cruft: https://cruft.github.io/cruft/
- Claude Code plugins reference: https://code.claude.com/docs/en/plugins-reference
- Plugin components (CLAUDE.md not loaded, agent hooks ignored): https://code.claude.com/docs/en/plugins/components
- Plugin loading and scopes: https://code.claude.com/docs/en/plugins/loading
- Requiring plugins from a repo: https://code.claude.com/docs/en/plugins/org
- Claude Code memory (AGENTS.md, imports): https://code.claude.com/docs/en/memory
- projen: https://pypi.org/project/projen/
- Nx migrate: https://nx.dev/docs/features/automate-updating-dependencies
