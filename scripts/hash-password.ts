/**
 * Password hashing utility for creating pilot credentials.
 * Run with: npx tsx scripts/hash-password.ts
 *
 * Usage:
 *   npx tsx scripts/hash-password.ts
 *   (will prompt for password interactively)
 *
 *   npx tsx scripts/hash-password.ts "mypassword"
 *   (hash a password directly)
 *
 * Output: JSON object with hash and salt to add to PILOT_CREDENTIALS env var.
 */

const PBKDF2_ITERATIONS = 100_000;

function bufferToHex(buffer: ArrayBuffer): string {
  return Array.from(new Uint8Array(buffer))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('');
}

async function hashPassword(password: string): Promise<{ hash: string; salt: string }> {
  const saltBytes = crypto.getRandomValues(new Uint8Array(16));

  const keyMaterial = await crypto.subtle.importKey(
    'raw',
    new TextEncoder().encode(password),
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

async function main() {
  let password = process.argv[2];

  if (!password) {
    const readline = await import('readline');
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
    });

    password = await new Promise<string>((resolve) => {
      rl.question('Enter password to hash: ', (answer) => {
        rl.close();
        resolve(answer);
      });
    });
  }

  if (!password) {
    console.error('No password provided.');
    process.exit(1);
  }

  const { hash, salt } = await hashPassword(password);

  console.log('\n--- Copy these values into your PILOT_CREDENTIALS env var ---\n');
  console.log(JSON.stringify({ passwordHash: hash, salt }, null, 2));
  console.log('\n--- Full credential entry example ---\n');
  console.log(
    JSON.stringify(
      {
        email: 'pilot@example.com',
        name: 'Pilot Name',
        passwordHash: hash,
        salt,
      },
      null,
      2
    )
  );
  console.log(
    '\nIMPORTANT: The "name" field must match EXACTLY what appears in the'
  );
  console.log(
    'Airtable "Pilot name text" field (including spacing and capitalisation).'
  );
}

main().catch(console.error);
