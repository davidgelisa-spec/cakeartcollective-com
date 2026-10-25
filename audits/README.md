# Audits

This folder contains audit reports produced by Claude Code or Codex.

## Workflow

1. **Run an audit** — Claude Code or Codex analyses the codebase and produces a report saved here with a date-prefixed filename: `YYYY-MM-DD-description.md`.

2. **Work through findings** — As each finding is addressed, mark it in the audit file:
   - `[done]` — Fixed or implemented
   - `[deferred]` — Acknowledged but intentionally postponed (add reason)
   - `[rejected]` — Reviewed and decided against (add reason)

3. **Archive** — Once an audit is fully resolved or superseded by a newer audit, move it to `archive/`. This keeps the top-level `audits/` folder focused on active work.

## Naming Convention

```
YYYY-MM-DD-description.md
```

Examples:
- `2026-03-28-codex-agent-audit.md`
- `2026-03-16-delta-audit.md`
- `2026-03-07-full-seo-audit.md`

## Archive

The `archive/` subfolder holds completed or superseded audits for reference. No need to delete old audits — just move them out of the active view.
