# Changelog — [Project Name]

Significant changes to this project, in reverse chronological order.

<!-- Format:
## YYYY-MM-DD
- What changed and why (not just "updated file.ts")
- Link to relevant audit or TODO item if applicable
-->

## 2026-05-04

- Migrated canonical agent instructions to `AGENTS.md`; `CLAUDE.md` is now a one-line `@AGENTS.md` import (cross-tool: Claude Code + Codex + Cursor read the same file).
- Added `seo/` folder template (best-practice doc, strategy, append-only changelog/decisions/performance log, evergreen research) — opt-in for site projects with organic search as a channel.
- Added `brand/` folder placeholder for projects with a defined brand identity.
- Added `.mcp.json` template with documented examples (`context7`, `astro-docs`, `svelte`, `next-devtools`, `chrome-devtools`, `playwright`, `cloudflare-worker-mcp`).
- Updated `ALIGNMENT-PROMPT.md` to add archetype detection (website / app / infra), MCP review, and conditional `seo/` and `brand/` handling.
- Updated `/update-docs` to be aware of `seo/` (prompt for changelog entry on schema/sitemap/meta changes; flag stale `best-practice.md` after 8 weeks).
- Updated `DOCS.md` to list the new living + reference docs.
