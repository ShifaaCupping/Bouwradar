// Cloudflare Pages Function: GET /api/unsubscribe?token=...
// Zet in elke e-mail: https://<jouw domein>/api/unsubscribe?token=<token uit de database>
export async function onRequestGet({ request, env }) {
  const token = new URL(request.url).searchParams.get('token') || '';
  let done = false;
  if (env.DB && /^[0-9a-f-]{36}$/i.test(token)) {
    const res = await env.DB.prepare('DELETE FROM subscribers WHERE token = ?1').bind(token).run();
    done = (res.meta && res.meta.changes > 0) || false;
  }
  const title = done ? 'Je bent afgemeld' : 'Afmelden';
  const text = done
    ? 'Je e-mailadres en je lijst zijn verwijderd. Je krijgt geen meldingen meer van Steenradar.'
    : 'Deze afmeldlink is ongeldig of al gebruikt. Krijg je toch nog mails? Stuur dan een bericht naar het adres in de privacyverklaring.';
  return new Response(`<!DOCTYPE html><html lang="nl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex"><title>${title} | Steenradar</title><link rel="stylesheet" href="/assets/style.css"></head><body><header class="topbar"><div class="wrap"><a class="brand" href="/"><span class="brick" aria-hidden="true"></span>Steenradar</a></div></header><section class="hero"><div class="wrap"><h1>${title}</h1><p class="lede">${text}</p><div class="ctas"><a class="cta primary" href="/">Naar Steenradar</a></div></div></section></body></html>`,
    { headers: { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store' } });
}
