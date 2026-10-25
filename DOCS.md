# Documentation Manifest

Which docs are "living" (must stay current with code) vs "reference" (point-in-time, never need updating). The `/update-docs` slash command uses this manifest to know what to check.

## Living Docs

These track the codebase and must be updated when relevant code changes.

| File | Tracks |
| --- | --- |
| `AGENTS.md` | Project architecture, directory structure, commands, conventions (canonical agent instructions file) |
| `CLAUDE.md` | One-line `@AGENTS.md` import — only update if the import mechanism changes |
| `README.md` | Quick start, setup instructions, feature overview |
| `CHANGELOG.md` | All significant changes, reverse chronological |
| `TODO.md` | Active work items — Now/Next/Later/Ideas/Done |
| `DOCS.md` | This file — update when new living docs are added or removed |
| `.mcp.json` | Active MCP servers — update when MCPs are added/removed for the project |

### When `seo/` is present (site projects only)

| File | Tracks |
| --- | --- |
| `seo/best-practice.md` | Current SEO + AI-optimisation best practice and decisions. Living doc. |
| `seo/strategy.md` | What we are going to do, in priority order. |
| `seo/changelog.md` | Append-only log of SEO-relevant changes shipped to the site. |
| `seo/decisions/log.md` | Append-only decision record. |
| `seo/performance/monthly-log.md` | Append-only running performance log. |

<!-- Add project-specific living docs here, e.g.:
| `docs/architecture/overview.md` | System architecture and deployment |
| `docs/api-reference.md` | API endpoints and response shapes |
-->

## Reference Docs

Written once, not expected to track code changes. Don't check these during `/update-docs`.

- `seo/research/*` — Evergreen research, delta-updated only when the SEO/AEO landscape shifts. Don't sync to code state.
- `seo/baseline/*` — Point-in-time site audits. Frozen after the date in the filename.
- `seo/reports/*` — Periodic deep-dives. Frozen after the date in the filename.

<!-- Add project-specific reference docs here, e.g.:
- `docs/research/` — One-time research and investigation notes
- `docs/design-spec.md` — Original feature design (historical)
-->

## Working Material

Never checked by `/update-docs`.

Gitignored (session artifacts, not committed):

- `_cowork/` — Co-Work session workspace
- `_inbox/` — Temporary file staging

Committed but not tracked by `/update-docs`:

- `audits/archive/` — Completed audits (kept in git history as a durable record)

## Active Audits

The `/update-docs` command should check `audits/*.md` (not `audits/archive/`) to see if any findings were addressed by recent changes, and mark them `[done]` if so.
