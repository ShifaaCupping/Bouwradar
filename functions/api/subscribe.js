// Cloudflare Pages Function: POST /api/subscribe
// Vereist een D1-binding met de naam DB (zie README.md).
export async function onRequestPost({ request, env }) {
  let body;
  try { body = await request.json(); } catch { return json({ ok: false, error: 'bad_json' }, 400); }

  const email = String(body.email || '').trim().toLowerCase();
  const sets = Array.isArray(body.sets) ? body.sets.filter(s => /^\d{4,6}$/.test(String(s))).slice(0, 200) : [];

  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) || email.length > 254) {
    return json({ ok: false, error: 'invalid_email' }, 400);
  }

  await env.DB.prepare(
    `INSERT INTO subscribers (email, sets, created_at, updated_at)
     VALUES (?1, ?2, datetime('now'), datetime('now'))
     ON CONFLICT(email) DO UPDATE SET sets = ?2, updated_at = datetime('now')`
  ).bind(email, JSON.stringify(sets)).run();

  return json({ ok: true });
}

export function onRequest() {
  return json({ ok: false, error: 'method_not_allowed' }, 405);
}

function json(data, status = 200) {
  return new Response(JSON.stringify(data), { status, headers: { 'Content-Type': 'application/json' } });
}
