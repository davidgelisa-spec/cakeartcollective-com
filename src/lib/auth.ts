/**
 * Authentication utilities for the pilot portal.
 * Uses Web Crypto API (PBKDF2 + HMAC-SHA256) — compatible with Cloudflare Workers.
 */

// --- Types ---

interface PilotCredential {
  email: string;
  name: string;
  passwordHash: string;
  salt: string;
}

interface SessionPayload {
  email: string;
  name: string;
  exp: number;
}

// --- Helpers ---

function hexToBuffer(hex: string): ArrayBuffer {
  const bytes = new Uint8Array(hex.length / 2);
  for (let i = 0; i < hex.length; i += 2) {
    bytes[i / 2] = parseInt(hex.substring(i, i + 2), 16);
  }
  return bytes.buffer;
}

function bufferToHex(buffer: ArrayBuffer): string {
  return Array.from(new Uint8Array(buffer))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('');
}

function encodeText(text: string): Uint8Array {
  return new TextEncoder().encode(text);
}

// --- Password Hashing (PBKDF2-SHA256) ---

const PBKDF2_ITERATIONS = 100_000;

export async function hashPassword(
  password: string,
  salt?: string
): Promise<{ hash: string; salt: string }> {
  const saltBytes = salt
    ? new Uint8Array(hexToBuffer(salt))
    : crypto.getRandomValues(new Uint8Array(16));

  const keyMaterial = await crypto.subtle.importKey(
    'raw',
    encodeText(password),
    'PBKDF2',
    false,
    ['deriveBits']
  );

  const derivedBits = await crypto.subtle.deriveBits(
    {
      name: 'PBKDF2',
      salt: saltBytes,
      iterations: PBKDF2_ITERATIONS,
      hash: 'SHA-256',
    },
    keyMaterial,
    256
  );

  return {
    hash: bufferToHex(derivedBits),
    salt: bufferToHex(saltBytes.buffer),
  };
}

export async function verifyPassword(
  password: string,
  storedHash: string,
  salt: string
): Promise<boolean> {
  const { hash } = await hashPassword(password, salt);
  // Constant-time comparison
  if (hash.length !== storedHash.length) return false;
  let result = 0;
  for (let i = 0; i < hash.length; i++) {
    result |= hash.charCodeAt(i) ^ storedHash.charCodeAt(i);
  }
  return result === 0;
}

// --- Credential Lookup ---

export function getCredentials(env: { PILOT_CREDENTIALS?: string }): PilotCredential[] {
  const raw = env.PILOT_CREDENTIALS;
  if (!raw) return [];
  try {
    return JSON.parse(raw);
  } catch {
    console.error('Failed to parse PILOT_CREDENTIALS');
    return [];
  }
}

export async function authenticatePilot(
  email: string,
  password: string,
  env: { PILOT_CREDENTIALS?: string }
): Promise<PilotCredential | null> {
  const credentials = getCredentials(env);
  const pilot = credentials.find(
    (c) => c.email.toLowerCase() === email.toLowerCase()
  );
  if (!pilot) return null;

  const valid = await verifyPassword(password, pilot.passwordHash, pilot.salt);
  return valid ? pilot : null;
}

// --- Session Tokens (HMAC-SHA256 signed) ---

const SESSION_DURATION_MS = 7 * 24 * 60 * 60 * 1000; // 7 days

async function getSigningKey(secret: string): Promise<CryptoKey> {
  return crypto.subtle.importKey(
    'raw',
    encodeText(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign', 'verify']
  );
}

export async function createSessionToken(
  email: string,
  name: string,
  sessionSecret: string
): Promise<string> {
  const payload: SessionPayload = {
    email,
    name,
    exp: Date.now() + SESSION_DURATION_MS,
  };

  const payloadB64 = btoa(JSON.stringify(payload));
  const key = await getSigningKey(sessionSecret);
  const signature = await crypto.subtle.sign('HMAC', key, encodeText(payloadB64));
  const signatureHex = bufferToHex(signature);

  return `${payloadB64}.${signatureHex}`;
}

export async function verifySessionToken(
  token: string,
  sessionSecret: string
): Promise<SessionPayload | null> {
  const parts = token.split('.');
  if (parts.length !== 2) return null;

  const [payloadB64, signatureHex] = parts;

  try {
    const key = await getSigningKey(sessionSecret);
    const signatureBuffer = hexToBuffer(signatureHex);
    const valid = await crypto.subtle.verify(
      'HMAC',
      key,
      signatureBuffer,
      encodeText(payloadB64)
    );

    if (!valid) return null;

    const payload: SessionPayload = JSON.parse(atob(payloadB64));

    // Check expiry
    if (payload.exp < Date.now()) return null;

    return payload;
  } catch {
    return null;
  }
}

// --- Cookie Helpers ---

export const SESSION_COOKIE_NAME = 'pilot_session';

export function setSessionCookie(token: string): string {
  const maxAge = 7 * 24 * 60 * 60; // 7 days in seconds
  return `${SESSION_COOKIE_NAME}=${token}; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=${maxAge}`;
}

export function clearSessionCookie(): string {
  return `${SESSION_COOKIE_NAME}=; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=0`;
}

export function getSessionCookie(cookieHeader: string | null): string | null {
  if (!cookieHeader) return null;
  const match = cookieHeader
    .split(';')
    .map((c) => c.trim())
    .find((c) => c.startsWith(`${SESSION_COOKIE_NAME}=`));
  return match ? match.substring(SESSION_COOKIE_NAME.length + 1) : null;
}
