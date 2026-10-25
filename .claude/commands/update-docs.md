# Update Docs

Review all living documentation and update anything that has drifted from the current codebase.

## Steps

### 1. Understand what changed

Run `git diff main...HEAD` (or `git diff HEAD~10` if on main) to see recent code changes. Also run `git log --oneline -20` to understand the narrative of recent work.

### 2. Read the documentation manifest

Read `DOCS.md` in the project root. This lists all "living docs" that track the codebase and all "reference docs" that should be left alone.

### 3. Triage — which living docs are affected?

For each living doc in the manifest, assess whether the code changes could affect it. Skip docs where nothing relevant changed. Print your triage:

```text
CHECKING:  AGENTS.md — new route added
CHECKING:  README.md — setup instructions changed
SKIPPING:  docs/api-reference.md — no API changes
...
```

### 4. Read and update affected docs

For each doc you're checking:

1. Read the current file
2. Identify specific sections that are stale, incomplete, or contradicted by the code changes
3. Fix obvious things directly (port numbers, file paths, command examples, new files/routes, removed features)
4. For non-obvious conflicts (architectural intent, phrasing choices, whether something should be documented at all), ask the user before changing

Preserve the existing style and voice of each document. Don't rewrite sections that are still accurate.

Note: `AGENTS.md` is the canonical agent instructions file in this template; `CLAUDE.md` is just a `@AGENTS.md` import. Update AGENTS.md, not CLAUDE.md.

### 5. SEO change check (site projects only)

If a `seo/` folder exists at the project root, additionally:

1. Scan the recent diff for SEO-relevant changes — schema markup, sitemap, robots.txt, meta tags, canonical URLs, redirects, page structure changes, content reshuffles.
2. If any are found, prompt the user to add a dated entry to `seo/changelog.md` summarising what changed and why.
3. Read `seo/best-practice.md`. If the recent code changes contradict any documented best-practice decision (e.g. the doc says "always use X schema" and a commit removed it), surface this and ask whether the doc should be updated or the change reverted.
4. Check `seo/best-practice.md`'s `Last reviewed:` date. If it's more than 8 weeks old, flag it for a fresh research pass — but don't run the pass yourself.

### 6. Update CHANGELOG.md

If there are meaningful changes not yet in the changelog:

1. Read the recent git log
2. Add a new dated entry (## YYYY-MM-DD) at the top
3. Summarise what changed and why — focus on "why", not "what files were edited"
4. Group by theme if there are multiple changes

### 7. Check active audits

Read any files in `audits/` (not `audits/archive/`). If the recent code changes address any audit findings, mark those items as `[done]` with a brief note.

### 8. Summary

Print a summary of what you updated:

```text
Updated:
  - AGENTS.md: added new API endpoint to routes table
  - CHANGELOG.md: added 2026-04-01 entry
  - seo/changelog.md: prompted user — schema change in commit abc1234

No changes needed:
  - README.md, docs/api-reference.md
```

## Rules

- Never modify reference docs or _cowork files
- Never remove content that's still accurate — only add or correct
- Keep AGENTS.md concise — every line competes for attention. If it grows past ~10 KB, suggest splitting subsystems into nested `AGENTS.md` files.
- If unsure whether something should be documented, ask the user
- Don't add speculative documentation about planned features — only document what exists in the code right now
