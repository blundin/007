# Architecture decision records

One record per significant decision, `docs/adr/NNNN-short-kebab-title.md`, numbered in order. The `architect` agent is the only author, and `adr_write_guard.py` lets it write only Markdown files in this folder. It recommends first, writing nothing; once the human decides, it writes the record as `accepted`. The main session commits it with the plan that lists it under `## ADRs`.

The architect is consulted when a scope forces a structural decision, when the loop raises a design question, and when a review finds design drift. Accepted records bind the app developer and the refactorer, and the reviewer treats a contradiction of one as a Blocker. The format and status rules are in `.claude/agents/architect.md`.

The `architect` and `reviewer` read this folder first. It is the only record of past decisions, so an accepted record changes only by being superseded by a new one.
