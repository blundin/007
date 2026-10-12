# Architecture decision records

One record per significant decision, `docs/adr/NNNN-short-kebab-title.md`, numbered in order. The `architect` agent writes them, and `adr_write_guard.py` lets it write only Markdown files in this folder. The format and status rules are in `.claude/agents/architect.md`.

The `architect` and `reviewer` read this folder first. It is the only record of past decisions, so an accepted record changes only by being superseded by a new one.
