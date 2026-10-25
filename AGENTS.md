# [Project Name]

[One-line project description.]

> **Note on this file:** `AGENTS.md` is the canonical instructions file for AI coding agents (Claude Code, Codex, Cursor, etc.). `CLAUDE.md` in this project is a one-line `@AGENTS.md` import so Claude Code reads the same content without duplication. Edit this file, not CLAUDE.md.

## AI Agent Assignment

**Primary Tool:** Claude Code  
**Role:** Deep engineering, architecture, code development, feature implementation  
**Important:** Do not use ChatGPT for code changes or `/update-docs` on this project. Use `_inbox/` for research handoffs. See [Active Projects Root](../AI-TOOL-ASSIGNMENTS.md) for full assignment details.

## Tech Stack

- **Framework:** [e.g. Astro 5, Next.js, Hono]
- **Language:** [e.g. TypeScript, Python]
- **Styling:** [e.g. Tailwind CSS 4]
- **Deployment:** [e.g. Cloudflare Pages, Vercel]

## Directory Structure

```text
.claude/commands/   ← Claude Code slash commands (e.g. /update-docs)
_inbox/             ← Temporary staging for raw files to be processed by an agent
_cowork/            ← Co-Work workspace: research, planning, analysis
audits/             ← Audit reports (date-prefixed), with archive/ for older reports
docs/               ← Architecture notes, decision records, API references
brand/              ← Brand guidelines, voice, palette, logo assets (optional — delete if N/A)
seo/                ← SEO research, strategy, performance log (optional — site projects only)
src/                ← Source code
```

## Folder Conventions

### `_inbox/`

Temporary drop zone. Files placed here are raw inputs waiting to be processed, renamed, or moved to their permanent location by an agent. Nothing in `_inbox/` is considered part of the project — it's a staging area only. Cleared regularly.

### `_cowork/`

Workspace for Claude Co-Work sessions. Contains research, planning documents, investigation notes, and analysis produced during Co-Work conversations. This folder is for thinking and exploration — not final deliverables.

### `audits/`

Audit reports produced by Claude Code or Codex. Files are named with date prefixes: `YYYY-MM-DD-description.md`. As findings are addressed, items within each audit are marked `[done]`, `[deferred]`, or `[rejected]`. Once an audit is fully resolved or superseded, move it to `audits/archive/`. See `audits/README.md` for the full workflow.

### `docs/`

Architecture decisions, API references, and technical documentation that form part of the project's long-term knowledge. Unlike `_cowork/` (exploratory), `docs/` content is authoritative.

### `brand/` (optional)

Brand guidelines, tone of voice, colour palette, logo assets, and any rules that govern how the brand is presented. Include this folder if the project has a defined brand identity (any client site, branded app, or multi-brand monorepo). Delete it if not applicable.

### `seo/` (optional — site projects only)

SEO research, strategy, performance logs, and decision records. Include this folder for any project that has organic search as a meaningful traffic channel. Delete it for internal tools, prototypes, and projects without an SEO concern. See `seo/README.md` for the conventions and recommended workflow.

## Logging & Debugging

All server-side code, API routes, and background processes should include structured logging that makes debugging possible without reproducing the issue. Follow these conventions:

**Log at decision points, not just failures.** When code takes a branch, calls an external service, or transforms data, log what happened and why. An error log is far more useful when the preceding info logs show the inputs and path that led to it.

**Use consistent log levels:**

- `error` — something failed and needs attention (include the error, the input that caused it, and enough context to trace the request)
- `warn` — something unexpected happened but was handled (e.g. fallback used, retry triggered, missing optional data)
- `info` — significant operations completed (API calls made, state transitions, cache hits/misses)
- `debug` — verbose detail useful during development (full payloads, intermediate values)

**Always include context:** every log line should make sense on its own. Include identifiers (request ID, user session, entity ID) so logs can be correlated. Avoid bare messages like "Error occurred" or "Done".

**External calls:** log before and after every external API call, database query, or LLM invocation. Include the service name, operation, duration, and whether it succeeded. On failure, include the status code and response body (truncated if large).

**Sensitive data:** never log API keys, tokens, passwords, or full credit card numbers. Redact or omit.

## MCP Servers

MCP servers extend an AI agent's capabilities (live docs, browser automation, analytics, etc.). They can be configured at three levels:

- **User / Claude.ai level** — connected once via Claude web, available in every session. Most general-purpose MCPs (framework docs, browser tools, calendar / mail / drive, custom analytics aggregators) belong here.
- **Project level** — `.mcp.json` at the repo root. Use only when an MCP needs project-specific scoping (e.g. a Linear/Notion workspace tied to this project), or when collaborators / a fresh environment won't have the user-level MCPs.
- **Tool-specific** — e.g. Codex / Cursor own configs.

This project ships with `.mcp.json` mostly as **documentation**: the `_examples` block lists which MCPs are worth considering for the project's archetype. Leave `mcpServers` empty if your user-level setup already covers them.

**Common MCPs to consider per project type:**

| Project type | Suggested MCPs |
| --- | --- |
| Any project on a real framework | `context7` — up-to-date library/framework docs |
| Astro site | `astro-docs` |
| Svelte / SvelteKit | `svelte` (official) |
| Next.js | `next-devtools` |
| Site on a Cloudflare-hosted domain | A Cloudflare-services aggregator (GSC, GA4, Bing, GBP, zone analytics) — either the official Cloudflare MCP or a custom worker. Prefer OAuth-authenticated workers over inline bearer tokens. |
| Live UX / perf inspection needed | `chrome-devtools` or `playwright` |
| Coordination / client-facing | Google Drive / Gmail / Calendar MCPs |

**When aligning a new project,** review the `.mcp.json` template, decide whether project-scoping any of these is genuinely needed, and consider whether a new MCP has shipped since the template was last updated — search before assuming.

<!-- Project-specific MCP notes here. Examples:
- Why a particular MCP is project-scoped (vs. relying on the user-level setup)
- Auth tokens stored in 1Password / .env (never commit secrets)
- OAuth-authenticated MCPs vs. those needing inline bearer tokens
-->

## Information standards

- Never make information up. Don't state general-knowledge or training-data claims as fact — especially "standard practice" claims (e.g. "most companies do X," "typically," "usually"), and especially on health & safety, compliance, legal, financial/tax, or regulatory questions. These carry no citation and can't be checked against current guidance.
- If a claim isn't sourced from the project's files, a cited document, or a live lookup (web search, WebFetch), say so explicitly and label it as unverified/general knowledge rather than presenting it as confirmed.
- If asked to verify something and no live lookup is available in the session, say that up front rather than answering from memory as if it were checked.
- Don't invent names, email addresses, phone numbers, dates, prices, reference numbers, site details, or quotes. If it isn't known, say it's missing and ask or leave a clear placeholder.
- Reasoning/analysis (e.g. risk-assessment logic) is fine to offer on its own merits — the flag is specifically for unverified factual claims, not for judgement calls.

## Project-Specific Instructions

<!-- Add project-specific instructions here. Examples: -->
<!-- - Build commands: `npm run dev`, `npm run build` -->
<!-- - Test commands: `npm test` -->
<!-- - Key conventions: component naming, file structure rules -->
<!-- - Things to avoid: specific patterns, deprecated approaches -->

## Documentation Maintenance

`DOCS.md` in the project root is the documentation manifest — it lists which docs are "living" (must stay current with code) and which are "reference" (written once, left alone). Run `/update-docs` after significant changes to check all living docs against the current code and update anything that has drifted.

## Nested AGENTS.md / CLAUDE.md Files

Subdirectories may contain their own `AGENTS.md` files with context specific to that area. Use nested files for:

- Complex subsystems that need their own instructions (e.g. `api/AGENTS.md`)
- Areas with different conventions or constraints
- Subdirectories that are worked on semi-independently

**Size discipline:** if the root `AGENTS.md` exceeds ~10 KB, split subsystems out into nested files rather than letting it grow. Every line in this file competes for the agent's attention.

If you also want Claude Code to read the nested file, drop a one-line `CLAUDE.md` next to it containing `@AGENTS.md`.
