Scan the project for files and content that can be cleaned up. Present findings in two tiers, then wait for user approval before deleting anything.

## Steps

### 1. Scan for cleanup candidates

Check these locations for stale, redundant, or misplaced files:

**Root directory:**
- Date-prefixed files (e.g. `2026-03-31-*.md`) that should have been placed in `_cowork/` or `audits/`
- Any files that don't belong at the project root

**`_cowork/` directory:**
- Files older than 30 days that appear to be one-off investigation notes
- Files whose findings have already been incorporated into `docs/` or code
- Empty or near-empty files
- Duplicate content that also exists in `docs/`

**`_inbox/` directory:**
- Anything still here — this should always be empty when not actively staging files

**`audits/` directory (not archive):**
- Audits where every item is marked `[done]`, `[deferred]`, or `[rejected]` — these should move to `audits/archive/`

**`docs/` directory:**
- Files that document features or systems that no longer exist in the code
- Files with content that has been superseded by newer docs
- Files that duplicate content already in CLAUDE.md or README.md

**Dead code and config:**
- Unused dependencies in package.json (run a quick check)
- Config files for tools no longer used
- Commented-out code blocks longer than 10 lines

### 2. Cross-reference duplicates

Check for content that exists in multiple places. Common patterns:
- `_cowork/` files that were later copied to `docs/` — the _cowork versions can go
- Investigation notes in `_cowork/` whose conclusions are already in `docs/`
- README files that repeat what CLAUDE.md already says

### 3. Present findings in two tiers

**Tier 1 — Safe to delete (high confidence):**
Files that are clearly redundant, empty, misplaced, or fully superseded. For each file, state why it's safe to remove.

```
SAFE TO DELETE:
  _inbox/old-file.xlsx — inbox should be empty
  _cowork/old-notes.md — identical content exists at docs/notes.md
```

**Tier 2 — Probably deletable (review recommended):**
Files that are likely stale but might contain unique information. For each file, summarise what's in it and flag what might be worth preserving before deletion.

```
PROBABLY DELETABLE:
  _cowork/investigation.md — investigation from 2 months ago. Contains edge case notes that may not be documented elsewhere. Worth checking docs/ first.
```

### 4. Present audit archiving separately

```
READY TO ARCHIVE (move to audits/archive/):
  audits/2026-01-20-review.md — all items resolved
```

### 5. Wait for instructions

Do NOT delete or move anything yet. Ask the user:
- "Should I proceed with all Tier 1 deletions?"
- "Which Tier 2 items should I delete?"
- "Should I archive the completed audits?"

Then execute only what's approved.

## Rules

- Never delete anything without explicit user approval
- Never delete `.env`, `.env.local`, or any secrets files — flag them for the user instead
- Never delete `node_modules/`, `dist/`, or build artifacts — those are managed by tooling
- Never delete git history or `.git/` contents
- If a file has unique content worth preserving, mention this in the Tier 2 notes
- For files being deleted from `_cowork/`, check if the content should be preserved in `docs/` first
