// Overzichtspagina: zoeken, filteren, sorteren en 'Mijn lijst'
(function () {
  const { $, favs, saveFavs, shopLinks, toast, brickSvg } = window.BR;
  const SETS = window.SETS || [];
  const THEME_COLORS = window.THEME_COLORS || {};
  const POP = ['75192','10326','21323','75367','75397','21333','76437','43263','10335','21360','76294','10341','21356','21353','42171','10337','75382','21351','42177'];
  const fmt = n => n.toLocaleString('nl-NL', { style: 'currency', currency: 'EUR' });
  const fmtN = n => n.toLocaleString('nl-NL');
  const state = { q: '', theme: 'Alles', sort: 'pop', onlyFavs: location.hash === '#mijn-lijst' };

  function renderChips() {
    const themes = ['Alles', ...new Set(SETS.map(s => s.t))];
    const el = $('#chips'); el.innerHTML = '';
    const fav = document.createElement('button');
    fav.className = 'chip fav'; fav.textContent = '♥ Mijn lijst'; fav.setAttribute('aria-pressed', state.onlyFavs);
    fav.onclick = () => { state.onlyFavs = !state.onlyFavs; history.replaceState(null, '', state.onlyFavs ? '#mijn-lijst' : location.pathname); renderChips(); render(); };
    el.appendChild(fav);
    themes.forEach(t => {
      const b = document.createElement('button');
      b.className = 'chip'; b.textContent = t; b.setAttribute('aria-pressed', state.theme === t);
      b.onclick = () => { state.theme = t; renderChips(); render(); };
      el.appendChild(b);
    });
  }

  function sorted(list) {
    const by = {
      'price-asc': (a, b) => a.p - b.p,
      'price-desc': (a, b) => b.p - a.p,
      'ppp': (a, b) => a.p / a.pc - b.p / b.pc,
      'pieces': (a, b) => b.pc - a.pc,
      'pop': (a, b) => { const ia = POP.indexOf(a.n), ib = POP.indexOf(b.n); return (ia < 0 ? 999 : ia) - (ib < 0 ? 999 : ib) || b.p - a.p; }
    }[state.sort];
    return [...list].sort(by);
  }

  function metaText(count) {
    return count + (count === 1 ? ' set' : ' sets') + (favs.size ? ' · ' + favs.size + ' op je lijst' : '');
  }

  function render() {
    const q = state.q.trim().toLowerCase();
    const list = sorted(SETS.filter(s =>
      (state.theme === 'Alles' || s.t === state.theme) &&
      (!state.onlyFavs || favs.has(s.n)) &&
      (!q || s.name.toLowerCase().includes(q) || s.n.includes(q) || s.t.toLowerCase().includes(q))
    ));
    $('#meta').textContent = metaText(list.length);
    const grid = $('#grid'); grid.innerHTML = '';
    if (!list.length) {
      grid.innerHTML = '<div class="empty">' + (state.onlyFavs ? 'Je lijst is nog leeg. Tik op het hartje bij een set.' : 'Geen sets gevonden.') + '</div>';
      return;
    }
    const frag = document.createDocumentFragment();
    list.forEach(s => {
      const c = document.createElement('article'); c.className = 'card';
      const color = THEME_COLORS[s.t] || '#444';
      const ppp = (s.p / s.pc * 100).toFixed(1).replace('.', ',');
      const url = '/sets/' + s.slug + '/';
      const thumb = s.img
        ? `<a class="thumb" href="${url}" aria-hidden="true" tabindex="-1"><img src="${s.img}" alt="" loading="lazy" decoding="async" referrerpolicy="no-referrer"></a>`
        : `<a class="thumb" href="${url}" aria-hidden="true" tabindex="-1">${brickSvg(color, s.pc)}</a>`;
      c.innerHTML = `
        <div class="top">
          ${thumb}
          <div class="title"><h3><a href="${url}"></a></h3><p>${s.t}, set ${s.n}</p></div>
          <button class="heart" aria-label="Zet op mijn lijst" aria-pressed="${favs.has(s.n)}">${favs.has(s.n) ? '♥' : '♡'}</button>
        </div>
        <div class="figs">
          <div><span>Adviesprijs</span><b>${fmt(s.p)}</b></div>
          <div><span>Stenen</span><b>${fmtN(s.pc)}</b></div>
          <div><span>Per steen</span><b>${ppp} ct</b></div>
        </div>
        <div class="actions">
          <a class="btn ghost" href="${url}">Prijsinzicht</a>
          <button class="btn compare" aria-expanded="false">Vergelijk prijzen</button>
        </div>
        <div class="shops"></div>`;
      c.querySelector('h3 a').textContent = s.name;
      const shops = c.querySelector('.shops');
      shopLinks(s.n).forEach(([label, href]) => {
        const a = document.createElement('a'); a.className = 'shop'; a.href = href; a.target = '_blank'; a.rel = 'noopener nofollow sponsored'; a.textContent = label;
        shops.appendChild(a);
      });
      const cmp = c.querySelector('.compare');
      cmp.onclick = () => { const o = c.classList.toggle('open'); cmp.setAttribute('aria-expanded', o); cmp.textContent = o ? 'Sluiten' : 'Vergelijk prijzen'; };
      const h = c.querySelector('.heart');
      h.onclick = () => {
        if (favs.has(s.n)) { favs.delete(s.n); toast('Verwijderd van je lijst'); }
        else { favs.add(s.n); toast('Op je lijst gezet. Meld je aan voor een seintje.'); }
        saveFavs();
        h.setAttribute('aria-pressed', favs.has(s.n)); h.textContent = favs.has(s.n) ? '♥' : '♡';
        if (state.onlyFavs) render(); else $('#meta').textContent = metaText(list.length);
      };
      frag.appendChild(c);
    });
    grid.appendChild(frag);
  }

  $('#q').addEventListener('input', e => { state.q = e.target.value; render(); });
  $('#sort').addEventListener('change', e => { state.sort = e.target.value; render(); });
  window.addEventListener('hashchange', () => {
    if (location.hash === '#mijn-lijst') { state.onlyFavs = true; renderChips(); render(); $('#chips').scrollIntoView({ block: 'start' }); }
  });
  document.querySelectorAll('[data-theme]').forEach(b => b.addEventListener('click', () => {
    state.theme = b.dataset.theme; state.onlyFavs = false; renderChips(); render();
    document.getElementById('alle-sets').scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
  }));
  renderChips(); render();
})();
