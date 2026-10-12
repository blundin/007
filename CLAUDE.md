# Working on 007

This repo is the framework, not a project that uses it. The loop rules that projects follow are in `framework/CLAUDE.md`; they don't apply here.

- `framework/` is what ships. `bin/007` copies every tracked file in it. Anything that shouldn't reach projects lives outside it.
- Framework work is done by the main session with Brian, test-first. The triad isn't used here. The rules are in [`docs/README.md`](docs/README.md).
- `framework/.claude/hooks/` and `framework/.claude/settings.json` change only by Brian's hand or with his explicit approval.
- `./scripts/check` is the single gate. It must pass before any change is done.
- Add a `CHANGELOG.md` entry under `Unreleased` for any change an adopter would notice.
- Don't hard-wrap Markdown. Write each paragraph or list item as one line and use line breaks only for paragraph breaks, as the Markdown spec intends.
