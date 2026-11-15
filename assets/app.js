// Gedeelde code voor alle pagina's van Bouwradar
(function () {
  const END = new Date('2026-12-31T23:59:59+01:00');
  const $ = (s, el = document) => el.querySelector(s);

  const store = {
    get(k, d) { try { const v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch (e) { return d; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }
  };
  const favs = new Set(store.get('br-favs', store.get('sr-favs', [])));
  const saveFavs = () => store.set('br-favs', [...favs]);

  function shopLinks(n) {
    const q = encodeURIComponent('lego ' + n);
    // Vervang deze links door je affiliate-links zodra je bent goedgekeurd.
    return [
      ['LEGO.com', 'https://www.lego.com/nl-nl/search?q=' + n],
      ['bol', 'https://www.bol.com/nl/nl/s/?searchtext=' + q],
      ['Intertoys', 'https://www.intertoys.nl/search?q=' + q],
      ['Amazon.nl', 'https://www.amazon.nl/s?k=' + q],
      ['Tweakers', 'https://tweakers.net/pricewatch/zoeken/?keyword=' + q],
      ['Marktplaats', 'https://www.marktplaats.nl/q/' + q + '/']
    ];
  }

  function daysLeft() { return Math.max(0, Math.ceil((END - new Date()) / 864e5)); }

  let tt;
  function toast(t) {
    const el = $('#toast'); if (!el) return;
    el.textContent = t; el.classList.add('show');
    clearTimeout(tt); tt = setTimeout(() => el.classList.remove('show'), 2600);
  }

  function initCountdowns() {
    document.querySelectorAll('[data-days]').forEach(el => { el.textContent = daysLeft(); });
  }

  function initAlertForm() {
    const form = $('#form'); if (!form) return;
    form.addEventListener('submit', async e => {
      e.preventDefault();
      const email = $('#email').value.trim(), msg = $('#msg');
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { msg.textContent = 'Vul een geldig e-mailadres in.'; return; }
      if (!$('#ok').checked) { msg.textContent = 'Vink eerst het akkoord aan.'; return; }
      const extra = form.dataset.set ? [form.dataset.set] : [];
      const sets = [...new Set([...favs, ...extra])];
      msg.textContent = 'Even geduld…';
      try {
        const r = await fetch('/api/subscribe', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email, sets }) });
        if (!r.ok) throw new Error();
        msg.textContent = sets.length ? 'Top! Je krijgt een seintje over ' + sets.length + (sets.length === 1 ? ' set.' : ' sets.') : 'Top! Je bent aangemeld. Tik op hartjes om je lijst te vullen.';
        form.reset();
      } catch (err) {
        msg.textContent = 'Aanmelden lukt nu niet. Probeer het later opnieuw.';
      }
    });
  }

  function initFavButton() {
    const b = $('#favbtn'); if (!b) return;
    const n = b.dataset.set;
    const paint = () => { const on = favs.has(n); b.setAttribute('aria-pressed', on); b.textContent = on ? '♥ Op mijn lijst' : '♡ Zet op mijn lijst'; };
    b.addEventListener('click', () => {
      if (favs.has(n)) { favs.delete(n); toast('Verwijderd van je lijst'); }
      else { favs.add(n); toast('Op je lijst gezet'); }
      saveFavs(); paint();
    });
    paint();
  }

  window.BR = { $, favs, saveFavs, shopLinks, toast, daysLeft };
  document.addEventListener('DOMContentLoaded', () => { initCountdowns(); initAlertForm(); initFavButton(); });
})();
