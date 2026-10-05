---
name: review-tracker
description: >
  Automatically track code review findings and known issues across sessions.
  PROACTIVE — invoke this skill at the START of any code review, bug investigation,
  or fix session, and keep it running throughout. Trigger phrases include:
  "review", "code review", "find bugs", "audit", "check for issues",
  "fix a bug", "investigate", "look at this code", "what's wrong with".
  Do NOT wait for the user to ask — load and follow this protocol automatically
  whenever review or fix work begins. Silently maintain all files; do not
  announce each write to the user.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
---

# Review Tracker Protocol

Maintain a persistent record of all code review findings and their resolution status. Follow this protocol silently — no user prompts, no per-write announcements. Just keep the files accurate.

## When to invoke

- At the start of any code review, bug investigation, or code-quality session
- Each time you identify a new finding during review work
- Each time a finding is resolved or its status changes
- At natural session boundaries (wrap-up, before a commit summary)

## File layout

All files live under `docs/code-reviews/` in the project root. Create the directory if it does not exist.

```
docs/code-reviews/
  YYYYMMDDHHMMSS-<slug>.json   # one per review session
  known-issues.json            # rolling aggregate of all open/acknowledged findings
```

## Step 1 — Open a review session

At the start of review work, create a timestamped session file.

Get the timestamp and git context with Bash:

```bash
date -u +%Y%m%d%H%M%S
git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown"
git rev-parse --short HEAD 2>/dev/null || echo "unknown"
basename $(git rev-parse --show-toplevel 2>/dev/null) 2>/dev/null || basename $PWD
```

Name the file `<timestamp>-<project>-<branch>.json`, replacing spaces and slashes with hyphens, lowercased. Example: `20260627143052-rangeforge-main.json`.

Initial session file structure:

```json
{
  "review_id": "20260627143052",
  "timestamp": "2026-06-27T14:30:52Z",
  "project": "rangeforge",
  "branch": "main",
  "commit": "9264af1",
  "scope": "brief description of what was reviewed",
  "findings": []
}
```

## Step 2 — Record each finding

As you identify issues during review, append to the `findings` array immediately — do not batch them for the end of the session. Each finding:

```json
{
  "id": "20260627143052-001",
  "severity": "high",
  "category": "bug",
  "file": "RangeForge/Domain/HandCell.swift",
  "line": 42,
  "title": "Force unwrap crashes on nil input",
  "description": "The `!` unwrap on line 42 will crash if `cell` is nil, which can happen when the grid is not yet initialized.",
  "suggestion": "Use guard let or optional chaining instead of force unwrap.",
  "status": "open",
  "resolved_at": null,
  "resolution_notes": null
}
```

ID format: `<review_id>-<three-digit-sequence>`. Sequence resets per session.

Severity values: `high`, `medium`, `low`, `info`

Category values: `bug`, `security`, `performance`, `correctness`, `convention`, `style`

Status values:
- `open` — identified, not yet fixed
- `fixed` — resolved in this or a later session
- `wont-fix` — acknowledged, intentionally not addressed
- `acknowledged` — known, deferred

## Step 3 — Update status when a finding is resolved

When you fix an issue (or the user fixes one you identified), update the finding's record immediately:

```json
{
  "status": "fixed",
  "resolved_at": "2026-06-27T15:10:00Z",
  "resolution_notes": "Replaced force unwrap with guard let; returns early if nil."
}
```

Use Bash for the timestamp: `date -u +%Y-%m-%dT%H:%M:%SZ`

## Step 4 — Maintain known-issues.json

After any write to a session file (new finding or status change), regenerate `known-issues.json` to reflect the current state of all session files.

`known-issues.json` contains only findings with status `open` or `acknowledged` — findings that are `fixed` or `wont-fix` are excluded.

```json
{
  "last_updated": "2026-06-27T15:10:00Z",
  "open_count": 2,
  "issues": [
    {
      "id": "20260627143052-002",
      "review_file": "20260627143052-rangeforge-main.json",
      "severity": "medium",
      "category": "correctness",
      "title": "Combo count wrong for offsuit cells",
      "file": "RangeForge/Domain/HandCell.swift",
      "line": 88,
      "status": "open"
    }
  ]
}
```

Build `known-issues.json` by reading all `*.json` files in `docs/code-reviews/` (excluding `known-issues.json` itself), collecting findings where `status` is `open` or `acknowledged`, and sorting by severity (`high` first, then `medium`, `low`, `info`).

## Transparency rules

- **Do not ask the user** before writing. Just write.
- **Do not narrate each save.** A brief mention at session wrap-up ("Saved 3 findings to docs/code-reviews/") is fine; per-finding announcements are not.
- **Do create the directory silently** if it does not exist: `mkdir -p docs/code-reviews`
- **If docs/ is gitignored or doesn't exist**, create it. These files are intentionally persisted.
- **On session start**, check if a review session file already exists for this session (same timestamp prefix) before creating a new one — resume it if found.
