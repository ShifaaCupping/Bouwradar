// Cloudflare Pages Function: POST /api/subscribe
// Vereist een D1-binding met de naam DB (zie README.md).
const MAX_SETS = 200;

export async function onRequestPost({ request, env }) {
  if (!env.DB) return json({ ok: false, error: 'no_db' }, 503);

  const type = request.headers.get('content-type') || '';
  if (!type.includes('application/json')) return json({ ok: false, error: 'bad_type' }, 415);
  const len = Number(request.headers.get('content-length') || 0);
  if (len > 8000) return json({ ok: false, error: 'too_large' }, 413);

  let body;
  try { body = await request.json(); } catch { return json({ ok: false, error: 'bad_json' }, 400); }

  // Honeypot: echte bezoekers zien dit veld niet. Bots vullen het in; doe alsof het lukte.
  if (typeof body.website === 'string' && body.website.trim() !== '') return json({ ok: true });

  if (body.consent !== true) return json({ ok: false, error: 'no_consent' }, 400);

  const email = String(body.email || '').trim().toLowerCase();
  if (email.length > 254 || !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) {
    return json({ ok: false, error: 'invalid_email' }, 400);
  }
  const sets = Array.isArray(body.sets)
    ? [...new Set(body.sets.map(String).filter(s => /^\d{4,6}$/.test(s)))].slice(0, MAX_SETS)
    : [];

  const token = crypto.randomUUID();
  await env.DB.prepare(
    `INSERT INTO subscribers (email, sets, token, consent_at, created_at, updated_at)
     VALUES (?1, ?2, ?3, datetime('now'), datetime('now'), datetime('now'))
     ON CONFLICT(email) DO UPDATE SET
       sets = ?2,
       token = COALESCE(subscribers.token, ?3),
       consent_at = datetime('now'),
       updated_at = datetime('now')`
  ).bind(email, JSON.stringify(sets), token).run();

  return json({ ok: true });
}

export function onRequest() {
  return json({ ok: false, error: 'method_not_allowed' }, 405);
}

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' }
  });
}
