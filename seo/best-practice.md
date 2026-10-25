# SEO + AI Optimisation: Current Best Practice & Decisions

**Living document.** Updated when fresh research changes the picture or a decision is made. Read this before any SEO / schema / AI-optimisation work to avoid re-litigating settled choices.

- **Last reviewed:** [YYYY-MM-DD]
- **Last research pass:** [YYYY-MM-DD] ([what was researched])
- **Owner:** [name or "the project — updated by whoever does the next research pass"]

---

## How to use this doc

1. **Before SEO/schema work:** scan the relevant section + the Decision Log below. If the change you're considering has been previously decided on, respect that or revisit deliberately.
2. **After fresh research:** add a dated delta to the relevant section. Don't rewrite — append. The history matters.
3. **After making a decision** (do / don't / defer): add an entry to the Decision Log with date, what, why, and what changed in the codebase.
4. **When external policy changes** (Google, OpenAI, etc.): add a "Change watch" entry with what changed and what we'll do about it.

---

## What we know works for THIS site

[Brief framing: what kind of site, who searches for it, what queries matter, what's the conversion goal. This is what makes the rest of the doc specific rather than generic.]

### SEO fundamentals

<!-- The non-negotiables for this site. Examples:
- Crawlable static HTML — no client-side rendering of content
- Canonical URLs absolute, trailing-slash policy explicit
- Sitemap excludes utility / noindex pages
- Self-hosted fonts, deferred analytics for Core Web Vitals
- Structured logging in place for indexing / sitemap fetches
-->

### Schema strategy

<!-- What schema.org types are used, where, and why. Include a table:
| Schema | Where | Purpose |
| --- | --- | --- |
| WebSite | sitewide | site-name in SERPs |
| Organization / LocalBusiness / etc. | sitewide | trust signals |
-->

### Content & page structure

<!-- What we believe about page length, headings, internal linking, image alt text, FAQ blocks, etc. — specific to THIS project. -->

### AI search (AEO / GEO) strategy

<!-- How we think about being citable in ChatGPT / Perplexity / AI Overviews. Examples:
- Bing Webmaster connected (ChatGPT uses Bing index)
- llms.txt and / or llms-full.txt published
- Author / Organization markup with sameAs links to verifiable sources
- Citations and trust signals over keyword density
-->

---

## Change watch (external)

Things outside our control that we're tracking. Append a row when a new policy / algorithm / platform change matters.

| Date | Source | What changed | Our response |
| --- | --- | --- | --- |
| [YYYY-MM-DD] | [Google / OpenAI / etc.] | [what shifted] | [what we'll do — link to decision log] |

---

## Decision log

Append-only. Each decision: date, what, why, what changed in the code (commit / PR if applicable).

### YYYY-MM-DD — [decision title]

- **Decision:** [do X / don't do X / defer X until Y]
- **Why:** [reasoning, with link to research that informed it]
- **Code impact:** [files / commits affected, or "no code change"]
- **Revisit:** [when, or "once we have N weeks of data"]
