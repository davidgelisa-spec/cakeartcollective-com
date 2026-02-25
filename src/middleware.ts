import { defineMiddleware } from 'astro:middleware';
import { getSessionCookie, verifySessionToken } from './lib/auth';

export const onRequest = defineMiddleware(async (context, next) => {
  const { pathname } = context.url;

  // Only protect /members/ routes and /api/sites/ routes
  const isProtected =
    pathname.startsWith('/members') || pathname.startsWith('/api/sites');

  if (!isProtected) {
    return next();
  }

  const sessionSecret = (context.locals as any).runtime?.env?.SESSION_SECRET
    ?? import.meta.env.SESSION_SECRET;

  if (!sessionSecret) {
    console.error('SESSION_SECRET not configured');
    return context.redirect('/login/');
  }

  const cookieHeader = context.request.headers.get('cookie');
  const token = getSessionCookie(cookieHeader);

  if (!token) {
    return context.redirect('/login/');
  }

  const session = await verifySessionToken(token, sessionSecret);

  if (!session) {
    return context.redirect('/login/');
  }

  // Attach session to locals so pages/API routes can access it
  (context.locals as any).session = session;

  return next();
});
