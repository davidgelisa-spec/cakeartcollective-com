export const prerender = false;

import type { APIRoute } from 'astro';
import { getSitesForPilot } from '../../../lib/airtable';

export const GET: APIRoute = async ({ locals }) => {
  const session = (locals as any).session;
  if (!session) {
    return new Response(JSON.stringify({ error: 'Unauthorized' }), {
      status: 401,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  const runtime = (locals as any).runtime;
  const env = {
    AIRTABLE_PAT: runtime?.env?.AIRTABLE_PAT ?? import.meta.env.AIRTABLE_PAT,
    AIRTABLE_BASE_ID: runtime?.env?.AIRTABLE_BASE_ID ?? import.meta.env.AIRTABLE_BASE_ID,
  };

  try {
    const sites = await getSitesForPilot(session.name, env);
    return new Response(JSON.stringify({ sites }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (e) {
    console.error('Failed to fetch sites:', e);
    return new Response(JSON.stringify({ error: 'Failed to fetch sites' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
};
