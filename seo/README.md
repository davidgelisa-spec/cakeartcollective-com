# SEO Workspace

Working folder for ongoing SEO and AI-search (AEO/GEO) strategy. Treat it as a strategist's notebook: documented, dated, and pickup-able after weeks away.

> **When to keep this folder:** any project where organic search (Google, Bing) or AI-search citation (ChatGPT, Perplexity, Google AI Overviews, etc.) is a meaningful traffic or trust channel. Internal tools, prototypes, and projects without an SEO concern should delete the `seo/` folder during alignment.

## Folder shape

```text
seo/
├── README.md             ← you are here
├── best-practice.md      ← living doc: current best practice + decision log. READ FIRST before any SEO/schema/AI-optimisation work.
├── strategy.md           ← what we're going to do (Now / Next / Later). Convert to strategy/ folder if it grows.
├── changelog.md          ← chronological log of SEO-related changes shipped to the site
├── research/             ← evergreen reference, delta-updated (don't rewrite — append "## Update YYYY-MM-DD" sections)
├── baseline/             ← snapshots of where the site stood at a point in time (date-prefixed audits)
├── performance/
│   └── monthly-log.md    ← append-only running log of GSC + GA4 + Bing trends
├── decisions/
│   └── log.md            ← append-only "we chose X because Y, on date Z"
├── pages/                ← (optional) per-page analysis files (e.g. `pages/poole.md`)
└── reports/              ← (optional) periodic deep-dive reports (date-prefixed)
```

## Picking up after a break

A few-week gap is normal. To get back up to speed:

1. Read `best-practice.md` — the source of truth for current decisions.
2. Read `strategy.md` — what was queued.
3. Skim `performance/monthly-log.md` — what changed since you last looked.
4. Check `decisions/log.md` for any unresolved threads.
5. Run a delta against the most recent file in `research/` — has anything material shifted? If yes, append a new dated section, don't rewrite.

## Conventions

- **Dates everywhere, ISO format** (`YYYY-MM-DD`). Filenames for time-sensitive docs are date-prefixed.
- **Append-only logs.** `performance/monthly-log.md`, `decisions/log.md`, and `changelog.md` grow downward. Don't edit the past — add new entries.
- **Research is evergreen but versioned.** When the landscape shifts (new core update, new AI platform, new measurement signal), add a `## Update YYYY-MM-DD` section at the top of the relevant research doc. Don't replace prior content — strategy is built on it.
- **Strategy lives in `strategy.md`, not in `research/`.** Research is what the world says is true; strategy is what we decide to do about it.
- **Each finding cites a source.** Research notes link out so claims can be re-verified.
- **Best-practice deltas are the canonical decision record.** When a fresh research pass changes a decision, update `best-practice.md` and add a row to `decisions/log.md` — don't bury it in a research file.

## SEO change discipline

Whenever the codebase ships a change with SEO impact (schema, sitemap, robots, meta tags, canonical, redirects, page structure, content), add a single line to `changelog.md`:

```markdown
## YYYY-MM-DD
- [page or scope] — what changed. Why. Linked PR / commit if applicable.
```

The `/update-docs` slash command checks recent diffs for SEO-relevant changes and prompts to update this file.

## Tooling status

Track what's connected for this project:

- **Google Search Console:** [✅ / ❌]
- **Google Analytics 4:** [✅ / ❌] property [`properties/...`]
- **Bing Webmaster Tools:** [✅ / ❌] (important — ChatGPT search uses Bing's index, so Bing is a leading indicator for ChatGPT visibility)
- **Google Business Profile:** [✅ / ❌ / N/A]
- **Cloudflare zone analytics:** [✅ / ❌] (zone id `...`)
- **`cloudflare-worker-mcp`:** [✅ / ❌] (aggregates the above into one MCP — see project root `.mcp.json`)
