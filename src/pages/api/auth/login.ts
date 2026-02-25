export const prerender = false;

import type { APIRoute } from 'astro';
import {
  authenticatePilot,
  createSessionToken,
  setSessionCookie,
} from '../../../lib/auth';

export const POST: APIRoute = async ({ request, redirect, locals }) => {
  try {
    const runtime = (locals as any).runtime;
    const env = {
      PILOT_CREDENTIALS: runtime?.env?.PILOT_CREDENTIALS ?? import.meta.env.PILOT_CREDENTIALS,
      SESSION_SECRET: runtime?.env?.SESSION_SECRET ?? import.meta.env.SESSION_SECRET,
    };

    if (!env.SESSION_SECRET) {
      return redirect('/login/?error=server');
    }

    const contentType = request.headers.get('content-type') ?? '';
    let email: string | null = null;
    let password: string | null = null;

    if (contentType.includes('application/x-www-form-urlencoded') || contentType.includes('multipart/form-data')) {
      const formData = await request.formData();
      email = formData.get('email') as string | null;
      password = formData.get('password') as string | null;
    } else {
      const body = await request.json();
      email = body.email;
      password = body.password;
    }

    if (!email || !password) {
      return redirect('/login/?error=missing');
    }

    const pilot = await authenticatePilot(email, password, {
      PILOT_CREDENTIALS: env.PILOT_CREDENTIALS,
    });

    if (!pilot) {
      return redirect('/login/?error=invalid');
    }

    const token = await createSessionToken(pilot.email, pilot.name, env.SESSION_SECRET);
    const cookie = setSessionCookie(token);

    return new Response(null, {
      status: 302,
      headers: {
        Location: '/members/',
        'Set-Cookie': cookie,
      },
    });
  } catch (e) {
    console.error('Login error:', e);
    return redirect('/login/?error=server');
  }
};
