# Members Area (Pilot Portal) — Setup & Migration Guide

This document describes how the password-protected pilot portal works so it can be migrated from the Cake Art Collective site to the FutureWise Aerial website.

---

## Overview

The Members Area is a server-rendered section of an Astro site where pilots can log in, view their assigned solar farm sites (pulled from Airtable), and update key fields (scheduling dates, mark sites as flown, confirm data uploaded, etc.). The Airtable PAT is never exposed to the browser — all Airtable calls happen server-side.

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Framework | Astro 5 |
| Hosting | Cloudflare Pages (with SSR) |
| Adapter | `@astrojs/cloudflare` |
| CSS | Tailwind CSS 4 (via `@tailwindcss/vite`) |
| Data source | Airtable REST API |
| Auth | PBKDF2 password hashing + HMAC-SHA256 signed session cookies |
| Runtime | Cloudflare Workers (Web Crypto API — no Node.js crypto) |

---

## File Structure

All files related to the members area:

```
src/
  middleware.ts                    # Auth middleware — protects /members/ and /api/sites/
  lib/
    auth.ts                        # Password hashing, session tokens, cookie helpers
    airtable.ts                    # Airtable API client, field name constants, types
  pages/
    login/index.astro              # Login page (prerender = false)
    members/index.astro            # Pilot dashboard (prerender = false)
    api/
      auth/
        login.ts                   # POST — validate credentials, set session cookie
        logout.ts                  # POST — clear session cookie
      sites/
        [id].ts                    # PATCH — update a site record in Airtable
scripts/
  hash-password.ts                 # CLI tool to generate password hashes for new pilots
```

All pages/routes in the members area have `export const prerender = false;` to enable server-side rendering. The rest of the site stays static.

---

## Environment Variables

Set these in **Cloudflare Pages > Settings > Environment Variables** (for production) and in a `.dev.vars` file locally.

| Variable | Description | Example |
|----------|-------------|---------|
| `PILOT_CREDENTIALS` | JSON array of pilot accounts | See below |
| `SESSION_SECRET` | Random 64-char hex string for signing session cookies | `500186cb6b21...` |
| `AIRTABLE_PAT` | Airtable Personal Access Token (needs `data.records:read` AND `data.records:write` scopes) | `patXXX...` |
| `AIRTABLE_BASE_ID` | Airtable Base ID | `appXXX...` |

### PILOT_CREDENTIALS format

```json
[
  {
    "email": "pilot@example.com",
    "name": "Pilot Name",
    "passwordHash": "5b6dcab008e5a05c...",
    "salt": "efa9c3432b37b7bb..."
  }
]
```

**Critical:** The `name` field must match the Airtable `Pilot name text ` field value **exactly** (including capitalisation). This is how sites are filtered per pilot.

### Generating a SESSION_SECRET

```bash
openssl rand -hex 32
```

---

## Authentication System

### How It Works

1. Pilot visits `/members/` — middleware checks for a valid session cookie
2. No valid cookie → redirected to `/login/`
3. Pilot submits email + password → `POST /api/auth/login/`
4. Server looks up the email in `PILOT_CREDENTIALS`, hashes the submitted password with PBKDF2-SHA256 (100k iterations), compares against stored hash
5. If valid, creates an HMAC-SHA256 signed session token containing `{email, name, exp}`, sets it as an HttpOnly cookie (7-day expiry)
6. Subsequent requests: middleware verifies the cookie signature and expiry, attaches session to `Astro.locals.session`

### Password Hashing (PBKDF2)

- Algorithm: PBKDF2-SHA256
- Iterations: 100,000
- Salt: 16 random bytes (hex-encoded)
- Output: 256-bit derived key (hex-encoded)
- Uses Web Crypto API (works in Cloudflare Workers — no Node.js `crypto` needed)

### Session Tokens

- Format: `base64(JSON payload).hex(HMAC-SHA256 signature)`
- Payload: `{ email, name, exp }` where `exp` is timestamp (7 days from creation)
- Cookie flags: `HttpOnly; Secure; SameSite=Lax; Path=/`

### Middleware (`src/middleware.ts`)

Protects two route prefixes:
- `/members/*` — pilot dashboard
- `/api/sites/*` — Airtable API proxy

All other routes pass through unprotected.

### Adding a New Pilot

1. Generate the password hash:
   ```bash
   npx tsx scripts/hash-password.ts "their-password"
   ```
2. Copy the `passwordHash` and `salt` from the output
3. Add a new entry to the `PILOT_CREDENTIALS` env var:
   ```json
   {"email": "new@pilot.com", "name": "Pilot Name", "passwordHash": "...", "salt": "..."}
   ```
4. The `name` must match the `Pilot name text ` field in Airtable exactly
5. Redeploy or update env vars in Cloudflare dashboard

---

## Airtable Integration

### Airtable Table

The portal reads from and writes to a table called **`Sites`** in the Airtable base.

### PAT Scopes Required

The Airtable Personal Access Token needs **both**:
- `data.records:read`
- `data.records:write`

Without the write scope, all PATCH operations return `INVALID_PERMISSIONS_OR_MODEL_NOT_FOUND`.

### Field Name Constants

**Airtable field names are case-sensitive and some have trailing spaces.** All field names are centralised in `src/lib/airtable.ts` in the `FIELD` constant:

```typescript
const FIELD = {
  SITE_NAME: 'Site Name',
  ADDRESS: 'Address',
  PILOT: 'Pilot',
  PILOT_NAME_TEXT: 'Pilot name text ',    // NOTE: trailing space!
  OM: 'O&Ms',
  OM_NAME: 'O&M Name (from O&Ms)',
  OM_CONTACT_EMAIL: 'O&M Contact Email text from O&Ms)',
  PILOT_EMAIL: 'Email Address (from Pilot)',
  APPROVAL_STATUS: 'Approval Status',
  JOB_TYPE: 'Job Type',
  TARGET_VISIT_DATE: 'Target Visit Date',
  SCHEDULING_WINDOW: 'Scheduling Window',
  DATE_FLOWN: 'Flown Date',
  DATA_UPLOADED: 'Data Uploaded',
  HS_COMPLETED_DATE: 'H&S Completed Date',
  RAMS_LINK: 'RAMS Link',
  WEATHER_FORECAST: 'Weather Forecast',
  GOOGLE_MAPS_LINK: 'Google Maps link',   // NOTE: lowercase 'l'
  LATITUDE: 'Latitude',
  LONGITUDE: 'Longitude',
  PEAK_POWER_KWP: 'Peak Power kWp',
  SITE_CONTACT_1: 'Site Contact 1',
  SITE_CONTACT_2: 'Site Contact 2',
  ADDITIONAL_CONTACTS: 'Additional Contacts',
  HOLD_REASON: 'Hold Reason',
  DATE_ON_HOLD: 'Date On Hold',
  IMPORT_BATCH: 'Import Batch',
  NOTES: 'Site Notes',
  HS_PROCESS_TYPE: 'H&S Process Type',
  HS_PROCESS_NOTES: 'H&S Process Notes',
} as const;
```

### Gotchas with Field Names

- `Pilot name text ` has a **trailing space** — if you trim it before querying, the filter won't match
- `Google Maps link` has a lowercase `l` — `Google Maps Link` won't work
- `Flown Date` not `Date Flown` — easy to get wrong
- `Site Notes` not `Notes`
- Airtable returns `UNKNOWN_FIELD_NAME` if the field doesn't exist and `INVALID_VALUE_FOR_COLUMN` if the field exists but the value type is wrong — useful for debugging

### Write Allowlist

Pilots can only update these fields (enforced server-side in `updateSite()`):

- `Approval Status`
- `Scheduling Window`
- `Flown Date`
- `Data Uploaded`
- `H&S Completed Date`

Any other field in the PATCH request body is silently ignored.

### Ownership Verification

Before updating any record, the API verifies that the site's `Pilot name text ` matches the logged-in pilot's name. This prevents pilots from modifying other pilots' sites.

### Rate Limiting

Airtable allows 5 requests/second per base. The client includes a simple rate limiter that spaces requests ~220ms apart.

### Pagination

The `getSitesForPilot()` function handles Airtable's pagination (100 records per page) using the `offset` parameter.

---

## Workflow & Status-Based Editing

Sites move through these statuses (managed by Airtable automations):

```
Awaiting approval → RAMS To send → RAMS Sent → Ready → Scheduled → Flown → Processing → Completed
                                                                                          Hold (any time)
```

Each field is only editable at specific workflow stages:

| Field | Editable When Status Is |
|-------|------------------------|
| Scheduling Window | `Ready` |
| Date Flown | `Scheduled` |
| H&S Completed | `Awaiting approval`, `RAMS To send`, `RAMS Sent`, `Ready`, `Scheduled` |
| Confirm Data Uploaded | `Flown` |

**Important:** Status values are case-sensitive. `Awaiting approval` has a lowercase `a` in "approval".

### Status Colour Badges

Each status has a colour-coded badge on the dashboard:

| Status | Colour |
|--------|--------|
| Awaiting Assignment | Pink |
| RAMS To send | Red |
| RAMS Sent | Orange |
| Ready | Yellow |
| Scheduled | Lime |
| Flown | Green |
| Processing | Blue |
| Completed | Grey |
| Hold | Purple |

---

## Dashboard Features

### Per-site display

- Site name, postcode, approval status badge
- O&M name
- Scheduling Window (date picker when editable)
- Date Flown (date picker when editable)
- H&S Completed (date picker when editable)
- Data Uploaded (confirm button when Flown)
- Peak Power (kWp)
- Hold reason (when on Hold)
- Notes
- Links: Weather, Maps, RAMS

### Inline editing

Date fields use `<input type="date">` that save immediately on change via `fetch()` to `/api/sites/[id]/` (PATCH). A toast notification confirms success or shows errors.

### URL handling

Airtable sometimes stores URLs without the `https://` prefix (e.g. `www.google.com`). The `ensureUrl()` helper prepends `https://` when missing, otherwise the browser treats them as relative paths (e.g. `/members/www.google.com`).

---

## Astro Configuration

### astro.config.mjs

```javascript
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import sitemap from '@astrojs/sitemap';
import cloudflare from '@astrojs/cloudflare';

export default defineConfig({
  site: 'https://your-site.com',
  adapter: cloudflare(),
  vite: {
    plugins: [tailwindcss()],
  },
  integrations: [sitemap()],
  trailingSlash: 'always',
});
```

Key points:
- `adapter: cloudflare()` enables SSR on Cloudflare Pages
- In Astro 5, there is no `output: 'hybrid'` — instead, individual pages opt into SSR with `export const prerender = false;`
- All other pages default to static pre-rendering

### Accessing Environment Variables

Cloudflare Pages makes env vars available through `locals.runtime.env`, not `import.meta.env` (which only works in dev). The pattern used throughout:

```typescript
const runtime = (Astro.locals as any).runtime;
const value = runtime?.env?.MY_VAR ?? import.meta.env.MY_VAR;
```

This works in both local dev (`import.meta.env` via `.dev.vars`) and production (`runtime.env`).

---

## Dependencies

```json
{
  "dependencies": {
    "@astrojs/cloudflare": "^12.6.12",
    "@astrojs/sitemap": "^3.7.0",
    "astro": "^5.17.1"
  },
  "devDependencies": {
    "@tailwindcss/vite": "^4.2.0",
    "sharp": "^0.34.5"
  }
}
```

No additional auth libraries needed — everything uses the Web Crypto API built into Cloudflare Workers.

---

## Local Development

1. Create a `.dev.vars` file in the project root:
   ```
   PILOT_CREDENTIALS=[{"email":"...","name":"...","passwordHash":"...","salt":"..."}]
   SESSION_SECRET=your-secret-here
   AIRTABLE_PAT=patXXX...
   AIRTABLE_BASE_ID=appXXX...
   ```

2. Run the dev server:
   ```bash
   npm run dev
   ```

3. Visit `http://localhost:4321/login/` to test

**Note:** `.dev.vars` should be in `.gitignore` — it contains secrets.

---

## Deploying to Cloudflare Pages

1. Connect your GitHub repo to Cloudflare Pages
2. Build command: `npm run build`
3. Output directory: `dist/`
4. Set all four environment variables in **Settings > Environment Variables**
5. Deploy

The Cloudflare adapter handles the SSR routes automatically — no additional Workers configuration needed.

---

## Migration Checklist

When moving this to the FutureWise Aerial website:

1. Copy these files to the new project:
   - `src/lib/auth.ts`
   - `src/lib/airtable.ts`
   - `src/middleware.ts`
   - `src/pages/login/index.astro`
   - `src/pages/members/index.astro`
   - `src/pages/api/auth/login.ts`
   - `src/pages/api/auth/logout.ts`
   - `src/pages/api/sites/[id].ts`
   - `scripts/hash-password.ts`

2. Install `@astrojs/cloudflare` and add the adapter to `astro.config.mjs`

3. Update the layout import in `login/index.astro` and `members/index.astro` to use the new site's layout

4. Update styling classes to match the new site's design system

5. Set all four environment variables in Cloudflare Pages

6. Verify the Airtable PAT has both `data.records:read` and `data.records:write` scopes

7. Verify field names in `src/lib/airtable.ts` still match your Airtable base (field names can change if someone edits the base)

8. Add `hash-password` script to `package.json`:
   ```json
   "hash-password": "npx tsx scripts/hash-password.ts"
   ```

9. Test login, site display, and write operations before going live
