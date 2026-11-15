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


  // Eigen getekend steentje: hoe groter de set, hoe hoger de stapel
  function shade(hex, amt) {
    const n = parseInt(hex.slice(1), 16);
    let r = n >> 16, g = (n >> 8) & 255, b = n & 255;
    const t = amt < 0 ? 0 : 255, p = Math.abs(amt);
    r = Math.round((t - r) * p + r); g = Math.round((t - g) * p + g); b = Math.round((t - b) * p + b);
    return '#' + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
  }
  function brickSvg(color, pieces) {
    const layers = pieces < 500 ? 1 : pieces < 1500 ? 1 : pieces < 3000 ? 2 : 3;
    const studs = pieces < 500 ? 2 : 4;
    const W = studs === 2 ? 64 : 112, x0 = (120 - W) / 2, h = 26, top = 100 - layers * h;
    const dark = shade(color, -0.28), light = shade(color, 0.22);
    let out = '<svg viewBox="0 0 120 104" aria-hidden="true">';
    const pitch = W / studs;
    for (let i = 0; i < studs; i++) {
      const sx = x0 + pitch * i + pitch / 2 - 8;
      out += `<rect x="${sx}" y="${top - 8}" width="16" height="10" rx="2.5" fill="${color}"/><rect x="${sx}" y="${top - 8}" width="16" height="3.5" rx="1.75" fill="${light}"/>`;
    }
    for (let l = 0; l < layers; l++) {
      const y = top + l * h;
      out += `<rect x="${x0}" y="${y}" width="${W}" height="${h}" rx="4" fill="${color}"/><rect x="${x0}" y="${y + h - 5}" width="${W}" height="5" rx="2.5" fill="${dark}"/><rect x="${x0 + 4}" y="${y + 3}" width="${W - 8}" height="3" rx="1.5" fill="${light}" opacity=".7"/>`;
    }
    return out + '</svg>';
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

  window.BR = { $, favs, saveFavs, shopLinks, toast, daysLeft, brickSvg };
  document.addEventListener('DOMContentLoaded', () => { initCountdowns(); initAlertForm(); initFavButton(); });
})();
