export const prerender = false;

import type { APIRoute } from 'astro';
import { updateSite } from '../../../lib/airtable';

export const PATCH: APIRoute = async ({ params, request, locals }) => {
  const session = (locals as any).session;
  if (!session) {
    return new Response(JSON.stringify({ error: 'Unauthorized' }), {
      status: 401,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  const recordId = params.id;
  if (!recordId) {
    return new Response(JSON.stringify({ error: 'Missing site ID' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  const runtime = (locals as any).runtime;
  const env = {
    AIRTABLE_PAT: runtime?.env?.AIRTABLE_PAT ?? import.meta.env.AIRTABLE_PAT,
    AIRTABLE_BASE_ID: runtime?.env?.AIRTABLE_BASE_ID ?? import.meta.env.AIRTABLE_BASE_ID,
  };

  try {
    const body = await request.json();
    const fields = body.fields;

    if (!fields || typeof fields !== 'object') {
      return new Response(JSON.stringify({ error: 'Missing fields' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    const updated = await updateSite(recordId, fields, session.name, env);

    return new Response(JSON.stringify({ site: updated }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (e: any) {
    console.error('Failed to update site:', e);
    const status = e.message?.includes('Unauthorized') ? 403 : 500;
    return new Response(JSON.stringify({ error: e.message || 'Update failed' }), {
      status,
      headers: { 'Content-Type': 'application/json' },
    });
  }
};
