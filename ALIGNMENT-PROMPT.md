# Project Alignment Prompt

Paste this into Claude Code (or Codex) when working inside any project that needs aligning to the standard template.

---

## The Prompt

```text
I'm standardising this project to follow a consistent structure and documentation convention. The canonical template is in `../_project-template/`. Read that entire folder first — every file in it — so you understand the target structure.

Then read `_cowork/project-alignment-audit.md` if one exists for context on what this project currently has and what needs to change. Note that any prior audit may be out of date — properly audit the current project folder rather than relying on it.

Your job is to align this project to the template. The rules are:

1. AUDIT FIRST, PLAN SECOND, EXECUTE LAST
   - Survey what this project already has: documentation files, folder structure, naming conventions, existing content.
   - Identify the project's archetype:
     - **Website / SEO project** — public-facing site with organic search as a traffic channel. Keep `seo/`.
     - **App / tool / backend** — internal app or API. Drop `seo/`. Likely add `scripts/` and `data/` if relevant.
     - **Infra / orchestration hub** — server runbooks, MCP config, deployment notes. Drop most workspace folders; CLAUDE.md/AGENTS.md becomes the runbook.
   - Produce a written plan (save it to `_cowork/alignment-plan.md`) listing every change you intend to make, grouped as MIGRATE, CREATE, or SKIP. Note the chosen archetype at the top.
   - Wait for my approval before making any changes.

2. MERGE AND MIGRATE — NEVER OVERWRITE
   - Existing content always wins. If this project already has a CLAUDE.md, AGENTS.md, README.md, TODO.md, or any documentation, KEEP that content. Expand and restructure it to match the template's format, but preserve everything that's already written.
   - Folders that serve the same purpose as a template folder get RENAMED, not replaced. For example:
     - `co-work/` or `Claude Cowork/` → rename to `_cowork/` (move contents intact)
     - `audit/` → rename to `audits/` (move contents intact, create `archive/` subfolder)
     - `reference/` or `background/` → move contents into `docs/`
     - `00_AI_PROJECT_CONTROL/` → migrate content into AGENTS.md and docs/ as appropriate
     - Any existing `brand-style/`, `brand-guidelines/`, or similar → consolidate into `brand/`
     - Any existing SEO folder (e.g. `_seo/`, `marketing/`, `seo/` with custom shape) → reshape to match `seo/` template structure, preserving all content. Do not delete anything; reorganise.
   - Date-prefixed audit files keep their names. Research docs, investigation notes, and planning files keep their names.
   - If the project has a brief (e.g. `*-brief.md`) or build prompt (e.g. `*-claude-code-prompt.md`), consider whether the content belongs in README.md, AGENTS.md, or docs/. Don't delete the originals until the content is safely migrated.

3. AGENTS.md vs CLAUDE.md
   - The canonical instructions file is `AGENTS.md`. `CLAUDE.md` is a one-line `@AGENTS.md` import so Claude Code reads the same content as Codex/Cursor.
   - If this project currently has only `CLAUDE.md`, MIGRATE its body into `AGENTS.md`, then replace `CLAUDE.md` with the import pointer.
   - If the project has both, keep `AGENTS.md` as canonical and reduce `CLAUDE.md` to the import pointer (preserving any genuinely Claude-specific notes underneath).
   - Add the template's folder conventions, MCP, and logging sections to AGENTS.md if they aren't already there. The existing project-specific instructions are the most valuable part — don't drop them.

4. FILL GAPS WITH THE TEMPLATE
   - Only create template files for things the project genuinely doesn't have.
   - When creating from template, fill in the project-specific details (name, tech stack, description) rather than leaving placeholders.
   - For TODO.md: if the project has existing TODOs scattered in other files, consolidate them into the new TODO.md under the Now/Next/Later/Ideas structure.
   - For .gitignore: merge — keep any project-specific patterns and add any missing standard patterns (especially `_inbox/`, `_cowork/`).
   - For CHANGELOG.md: create a new one. Add a single entry noting "Aligned project structure to standard template" with today's date.

5. SEO FOLDER (conditional)
   - Only include `seo/` if the project archetype is a website with organic search as a meaningful channel.
   - If this is an SEO project, copy the `seo/` template structure, then reshape any pre-existing SEO content into it. Preserve all research, baselines, and decisions.
   - If this is NOT an SEO project, do not create the folder.

6. BRAND FOLDER (conditional)
   - Only include `brand/` if the project has a defined brand identity (client site, branded app, or multi-brand monorepo).
   - Consolidate any existing `brand-style/`, `brand-guidelines/`, palette / logo / voice docs into a single `brand/` folder.
   - For projects with no brand identity (internal tools, prototypes), do not create the folder.

7. MCP CONFIGURATION (`.mcp.json`)
   - Copy the template's `.mcp.json`. Review the `_examples` block and move servers into `mcpServers` that match this project's stack:
     - `context7` for almost any framework-using project
     - Framework MCP (`astro-docs` / `svelte` / `next-devtools`) when relevant
     - `cloudflare-worker-mcp` for any site on a Cloudflare-hosted domain (especially SEO projects — gives GSC / GA4 / Bing / GBP / zone analytics)
     - `chrome-devtools` or `playwright` if live UX / perf inspection will be useful
   - Also actively consider whether a newer MCP has shipped that fits this project's needs. A quick web search for "[framework] MCP server" or "[domain] MCP server" is worth doing during alignment.
   - Never commit real bearer tokens. Use placeholder tokens or load from env.

8. CREATE MISSING FOLDERS
   - `_inbox/`, `_cowork/`, `audits/` (with `archive/`), `docs/` — create any that don't exist.
   - Add `.gitkeep` to empty folders.
   - Copy `audits/README.md` from the template if missing.

9. DON'T TOUCH
   - Source code, config files, package.json, environment files, knowledge bases, build output.
   - Don't restructure the application code — this is documentation and folder alignment only.
   - Don't delete anything. If something is being superseded, note it in the plan and I'll decide.

10. LOGGING SECTION
    - If this project has server-side code (API routes, background processes, etc.), include the Logging & Debugging section from the template in AGENTS.md.
    - If it's a static-only site, skip it.

11. GIT
    - If this project has a git repo, make a single commit at the end with the message: "Align project structure to standard template"
    - If it doesn't have git, don't initialise one.

Start by reading `../_project-template/` and any existing alignment audit, then audit this project, decide the archetype, and produce the plan.
```
