/**
 * Airtable API client for the pilot portal.
 * All calls are server-side only — the PAT is never exposed to the browser.
 *
 * Field names must match the Airtable base EXACTLY (including trailing spaces).
 */

// --- Airtable Field Name Constants ---
// Centralised here so typos are caught in one place

const FIELD = {
  SITE_NAME: 'Site Name',
  ADDRESS: 'Address',
  PILOT: 'Pilot',
  PILOT_NAME_TEXT: 'Pilot name text ',  // trailing space in Airtable
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
  GOOGLE_MAPS_LINK: 'Google Maps link',  // lowercase 'l'
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

// --- Types ---

export interface AirtableSite {
  id: string;
  siteName: string;
  postcode: string;
  omName: string;
  pilotNameText: string;
  approvalStatus: string;
  jobType: string;
  targetVisitDate: string | null;
  schedulingWindow: string | null;
  dateFlown: string | null;
  dataUploaded: string | null;
  hsCompletedDate: string | null;
  ramsLink: string | null;
  weatherForecast: string | null;
  googleMapsLink: string | null;
  latitude: number | null;
  longitude: number | null;
  peakPowerKwp: number | null;
  siteContact1: string | null;
  siteContact2: string | null;
  additionalContacts: string | null;
  holdReason: string | null;
  dateOnHold: string | null;
  notes: string | null;
  hsProcessType: string | null;
  hsProcessNotes: string | null;
}

interface AirtableRecord {
  id: string;
  fields: Record<string, unknown>;
}

interface AirtableListResponse {
  records: AirtableRecord[];
  offset?: string;
}

// --- Status Colours ---

export const STATUS_COLOURS: Record<string, { bg: string; text: string }> = {
  'Awaiting Assignment':  { bg: 'bg-pink-100', text: 'text-pink-800' },
  'Awaiting Assignment ': { bg: 'bg-pink-100', text: 'text-pink-800' },  // trailing space variant
  'RAMS To send':         { bg: 'bg-red-100', text: 'text-red-700' },
  'RAMS Sent':            { bg: 'bg-orange-100', text: 'text-orange-800' },
  'Ready':                { bg: 'bg-yellow-100', text: 'text-yellow-800' },
  'Scheduled':            { bg: 'bg-lime-100', text: 'text-lime-800' },
  'Flown':                { bg: 'bg-green-100', text: 'text-green-800' },
  'Processing':           { bg: 'bg-blue-100', text: 'text-blue-800' },
  'Completed':            { bg: 'bg-gray-100', text: 'text-gray-600' },
  'Hold':                 { bg: 'bg-purple-100', text: 'text-purple-800' },
};

// --- Client ---

const AIRTABLE_API_BASE = 'https://api.airtable.com/v0';

export interface AirtableEnv {
  AIRTABLE_PAT?: string;
  AIRTABLE_BASE_ID?: string;
}

function getConfig(env: AirtableEnv) {
  const pat = env.AIRTABLE_PAT;
  const baseId = env.AIRTABLE_BASE_ID;
  if (!pat || !baseId) {
    throw new Error('Missing AIRTABLE_PAT or AIRTABLE_BASE_ID environment variables');
  }
  return { pat, baseId };
}

// Rate limiter: Airtable allows 5 requests/second per base.
// Simple sequential queue to avoid hitting the limit.
let lastRequestTime = 0;
const MIN_REQUEST_INTERVAL = 220; // ~4.5 req/s to stay safely under 5/s

async function rateLimitedFetch(url: string, options: RequestInit): Promise<Response> {
  const now = Date.now();
  const elapsed = now - lastRequestTime;
  if (elapsed < MIN_REQUEST_INTERVAL) {
    await new Promise((resolve) => setTimeout(resolve, MIN_REQUEST_INTERVAL - elapsed));
  }
  lastRequestTime = Date.now();
  return fetch(url, options);
}

async function airtableFetch(
  env: AirtableEnv,
  table: string,
  path: string = '',
  options: RequestInit = {}
): Promise<Response> {
  const { pat, baseId } = getConfig(env);
  const url = `${AIRTABLE_API_BASE}/${baseId}/${encodeURIComponent(table)}${path}`;

  return rateLimitedFetch(url, {
    ...options,
    headers: {
      Authorization: `Bearer ${pat}`,
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });
}

// --- API Methods ---

/**
 * Fetch all sites assigned to a specific pilot.
 * Excludes completed sites by default.
 */
export async function getSitesForPilot(
  pilotName: string,
  env: AirtableEnv,
  includeCompleted = false
): Promise<AirtableSite[]> {
  const filterParts = [`{${FIELD.PILOT_NAME_TEXT}}='${pilotName}'`];
  if (!includeCompleted) {
    filterParts.push(`{${FIELD.APPROVAL_STATUS}}!='Completed'`);
  }
  const formula = filterParts.length > 1
    ? `AND(${filterParts.join(',')})`
    : filterParts[0];

  const allRecords: AirtableRecord[] = [];
  let offset: string | undefined;

  // Handle pagination
  do {
    const params = new URLSearchParams({
      filterByFormula: formula,
      'sort[0][field]': FIELD.APPROVAL_STATUS,
      'sort[0][direction]': 'asc',
    });
    if (offset) params.set('offset', offset);

    const res = await airtableFetch(env, 'Sites', `?${params.toString()}`);
    if (!res.ok) {
      const error = await res.text();
      throw new Error(`Airtable API error: ${res.status} ${error}`);
    }

    const data: AirtableListResponse = await res.json();
    allRecords.push(...data.records);
    offset = data.offset;
  } while (offset);

  return allRecords.map(mapRecordToSite);
}

/**
 * Update fields on a site record.
 * Only allows updating specific safe fields.
 */
export async function updateSite(
  recordId: string,
  fields: Record<string, unknown>,
  pilotName: string,
  env: AirtableEnv
): Promise<AirtableSite> {
  // Allowlist of fields pilots can update
  const allowedFields = new Set([
    FIELD.APPROVAL_STATUS,
    FIELD.SCHEDULING_WINDOW,
    FIELD.DATE_FLOWN,
    FIELD.DATA_UPLOADED,
    FIELD.HS_COMPLETED_DATE,
  ]);

  const safeFields: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(fields)) {
    if (allowedFields.has(key)) {
      safeFields[key] = value;
    }
  }

  if (Object.keys(safeFields).length === 0) {
    throw new Error('No valid fields to update');
  }

  // Verify the record belongs to this pilot before updating
  const verifyRes = await airtableFetch(env, 'Sites', `/${recordId}`);
  if (!verifyRes.ok) {
    throw new Error(`Site not found: ${recordId}`);
  }
  const existing: AirtableRecord = await verifyRes.json();
  const recordPilot = (existing.fields[FIELD.PILOT_NAME_TEXT] as string)?.trim();
  if (recordPilot !== pilotName) {
    throw new Error('Unauthorized: site does not belong to this pilot');
  }

  // Perform the update
  const res = await airtableFetch(env, 'Sites', `/${recordId}`, {
    method: 'PATCH',
    body: JSON.stringify({ fields: safeFields }),
  });

  if (!res.ok) {
    const error = await res.text();
    throw new Error(`Airtable update error: ${res.status} ${error}`);
  }

  const updated: AirtableRecord = await res.json();
  return mapRecordToSite(updated);
}

// --- Mapping ---

function mapRecordToSite(record: AirtableRecord): AirtableSite {
  const f = record.fields;
  return {
    id: record.id,
    siteName: (f[FIELD.SITE_NAME] as string) ?? '',
    postcode: (f[FIELD.ADDRESS] as string) ?? '',
    omName: ((f[FIELD.OM_NAME] as string[]) ?? [])[0] ?? '',
    pilotNameText: ((f[FIELD.PILOT_NAME_TEXT] as string) ?? '').trim(),
    approvalStatus: ((f[FIELD.APPROVAL_STATUS] as string) ?? '').trim(),
    jobType: (f[FIELD.JOB_TYPE] as string) ?? '',
    targetVisitDate: (f[FIELD.TARGET_VISIT_DATE] as string) ?? null,
    schedulingWindow: (f[FIELD.SCHEDULING_WINDOW] as string) ?? null,
    dateFlown: (f[FIELD.DATE_FLOWN] as string) ?? null,
    dataUploaded: (f[FIELD.DATA_UPLOADED] as string) ?? null,
    hsCompletedDate: (f[FIELD.HS_COMPLETED_DATE] as string) ?? null,
    ramsLink: (f[FIELD.RAMS_LINK] as string) ?? null,
    weatherForecast: (f[FIELD.WEATHER_FORECAST] as string) ?? null,
    googleMapsLink: (f[FIELD.GOOGLE_MAPS_LINK] as string) ?? null,
    latitude: (f[FIELD.LATITUDE] as number) ?? null,
    longitude: (f[FIELD.LONGITUDE] as number) ?? null,
    peakPowerKwp: (f[FIELD.PEAK_POWER_KWP] as number) ?? null,
    siteContact1: (f[FIELD.SITE_CONTACT_1] as string) ?? null,
    siteContact2: (f[FIELD.SITE_CONTACT_2] as string) ?? null,
    additionalContacts: (f[FIELD.ADDITIONAL_CONTACTS] as string) ?? null,
    holdReason: (f[FIELD.HOLD_REASON] as string) ?? null,
    dateOnHold: (f[FIELD.DATE_ON_HOLD] as string) ?? null,
    notes: (f[FIELD.NOTES] as string) ?? null,
    hsProcessType: ((f[FIELD.HS_PROCESS_TYPE] as string[]) ?? [])[0] ?? null,
    hsProcessNotes: ((f[FIELD.HS_PROCESS_NOTES] as string[]) ?? [])[0] ?? null,
  };
}
