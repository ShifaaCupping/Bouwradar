#!/usr/bin/env python3
"""Bouwt alle pagina's van Bouwradar uit data/sets.json.

Gebruik:  python3 tools/build.py
Pas SITE_URL aan naar je eigen domein en draai het script opnieuw.
"""
import json, re, html, os, unicodedata
from pathlib import Path

SITE_URL = os.environ.get('SITE_URL', 'https://bouwradar.pages.dev').rstrip('/')
STOP_DATE = '31 december 2026'
ROOT = Path(__file__).resolve().parent.parent

THEME_COLORS = {
    'Star Wars': '#1b1b1f', 'Icons': '#7a4b2a', 'Ideas': '#0a7cc1', 'Technic': '#4b4f56',
    'Harry Potter': '#6b2c3e', 'Marvel': '#b0151d', 'Architecture': '#8a8070', 'Art': '#d65a1f',
    'Botanicals': '#2f7d4a', 'Speed Champions': '#c4161c', 'City': '#0f6fb6', 'Disney': '#3a4fb0'
}

def slugify(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    s = s.lower().replace("'", '').replace('&', 'and')
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')

def eur(x):
    return '€ ' + f'{x:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

def num(x):
    return f'{x:,}'.replace(',', '.')

e = html.escape

SETS = json.loads((ROOT / 'data/sets.json').read_text())
for s in SETS:
    s['slug'] = f"{s['n']}-{slugify(s['name'])}"

# Productfoto's: vul data/images.json met {"75192": "https://..."} uit je affiliate-productfeed
IMAGES_FILE = ROOT / 'data/images.json'
IMAGES = json.loads(IMAGES_FILE.read_text()) if IMAGES_FILE.exists() else {}
for s in SETS:
    s['img'] = IMAGES.get(s['n'], '')

def thumb(s, color, link=True):
    inner = (f'<img src="{e(s["img"])}" alt="" loading="lazy" decoding="async" referrerpolicy="no-referrer">'
             if s['img'] else s['n'])
    cls = 'tile has-img' if s['img'] else 'tile'
    style = '' if s['img'] else f' style="background:{color}"'
    if link:
        return f'<a class="{cls}" href="/sets/{s["slug"]}/"{style} aria-hidden="true" tabindex="-1">{inner}</a>'
    return f'<div class="{cls}"{style} aria-hidden="true">{inner}</div>'

ICONS = {
    'sets': '<svg viewBox="0 0 24 24"><rect x="3" y="8" width="18" height="12" rx="2"/><path d="M7 8V5h4v3M13 8V5h4v3"/></svg>',
    'lijst': '<svg viewBox="0 0 24 24"><path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/></svg>',
    'meld': '<svg viewBox="0 0 24 24"><path d="M6 16V11a6 6 0 1 1 12 0v5l2 2H4z"/><path d="M10 21h4"/></svg>',
    'uitleg': '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M9.5 9a2.5 2.5 0 1 1 3.5 2.3c-.6.3-1 .9-1 1.6V14M12 17.5v.01"/></svg>',
}

def head(title, desc, path, extra=''):
    return f'''<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{SITE_URL}{path}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{SITE_URL}{path}">
<meta property="og:type" content="website">
<meta name="theme-color" content="#0d1b2a">
<link rel="stylesheet" href="/assets/style.css">
{extra}</head>
<body>
'''

CUR = ' aria-current="page"'

def topbar(active):
    links = [('sets', '/', 'Alle sets'), ('lijst', '/#mijn-lijst', 'Mijn lijst'), ('meld', '/#meldingen', 'Meldingen'), ('uitleg', '/uitleg/', 'Uitleg')]
    nav = ''.join(f'<a href="{h}"{CUR if k == active else ""}>{t}</a>' for k, h, t in links)
    return f'''<header class="topbar"><div class="wrap">
  <a class="brand" href="/"><span class="brick" aria-hidden="true"></span>Bouwradar</a>
  <nav class="topnav" aria-label="Hoofdmenu">{nav}</nav>
</div></header>
'''

def bottomnav(active):
    links = [('sets', '/', 'Sets'), ('lijst', '/#mijn-lijst', 'Mijn lijst'), ('meld', '/#meldingen', 'Meldingen'), ('uitleg', '/uitleg/', 'Uitleg')]
    items = ''.join(f'<a href="{h}"{CUR if k == active else ""}>{ICONS[k]}<span>{t}</span></a>' for k, h, t in links)
    return f'<nav class="bottomnav" aria-label="Menu">{items}</nav>\n'

def alert_block(set_n=None, set_name=None):
    if set_n:
        h2 = f'Seintje voordat {e(set_name)} verdwijnt'
        p = 'Wij mailen je als deze set bijna uit productie gaat of ergens in de aanbieding is. Geen spam, altijd afmelden.'
        data = f' data-set="{set_n}"'
    else:
        h2 = 'Krijg een seintje op tijd'
        p = 'Wij mailen je als een set op je lijst bijna verdwijnt of ergens in de aanbieding is. Geen spam, altijd afmelden.'
        data = ''
    return f'''<section class="alert" id="meldingen">
    <h2>{h2}</h2>
    <p>{p}</p>
    <form id="form"{data} novalidate>
      <input type="email" id="email" placeholder="jouw@email.nl" aria-label="E-mailadres" autocomplete="email" required>
      <button type="submit">Meld mij aan</button>
    </form>
    <label class="consent"><input type="checkbox" id="ok" required> Ik ga akkoord dat Bouwradar mijn e-mailadres en mijn lijstje bewaart om mij meldingen te sturen.</label>
    <div class="msg" id="msg" role="status"></div>
  </section>
'''

FOOTER = '''<footer>
  <div class="wrap">
    <nav aria-label="Voettekst"><a href="/">Alle sets</a><a href="/#meldingen">Meldingen</a><a href="/uitleg/">Uitleg</a></nav>
    <p>Prijzen vergelijken op Bouwradar is gratis. Als je via een winkellink iets koopt, kunnen wij een kleine commissie krijgen; jij betaalt niets extra. De volgorde van sets en winkels hangt daar niet van af.</p>
    <p>Stopdata en adviesprijzen zijn verwachtingen op basis van openbare bronnen en kunnen veranderen. Controleer altijd de prijs bij de winkel.</p>
    <p>Bouwradar is een onafhankelijke site en is niet verbonden aan, gesponsord door of goedgekeurd door de LEGO Group. LEGO® is een handelsmerk van de LEGO Group.</p>
  </div>
</footer>
<div class="toast" id="toast" role="status" aria-live="polite"></div>
'''

def write(path, content):
    p = ROOT / path.lstrip('/')
    if path.endswith('/'):
        p = p / 'index.html'
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)

# ---------- Overzicht ----------
themes = sorted({s['t'] for s in SETS})
list_data = json.dumps([{k: s[k] for k in ('t', 'n', 'name', 'p', 'pc', 'slug', 'img')} for s in SETS], ensure_ascii=False, separators=(',', ':'))
index = head('Bouwradar — LEGO-sets die eind 2026 uit productie gaan',
             f'{len(SETS)} LEGO-sets die naar verwachting op {STOP_DATE} stoppen. Vergelijk prijzen bij Nederlandse winkels en krijg een seintje voordat je set verdwijnt.', '/')
index += topbar('sets')
index += f'''<section class="hero">
  <div class="wrap">
    <h1>Deze LEGO-sets <em>verdwijnen</em> eind 2026</h1>
    <p class="lede">Na de stopdatum wordt een set vaak flink duurder bij doorverkopers. Vergelijk nu de prijzen bij Nederlandse winkels en koop op tijd.</p>
    <div class="herostats">
      <div class="hs hot"><b data-days>–</b><span>dagen tot {STOP_DATE.replace(' 2026','')}</span></div>
      <div class="hs"><b>{len(SETS)}</b><span>sets stoppen</span></div>
      <div class="hs"><b>{len(themes)}</b><span>thema's</span></div>
    </div>
  </div>
</section>

<div class="controls">
  <div class="wrap">
    <div class="row">
      <input class="search" id="q" type="search" placeholder="Zoek een set" aria-label="Zoeken" autocomplete="off">
      <select class="sort" id="sort" aria-label="Sorteren">
        <option value="pop">Populair eerst</option>
        <option value="price-asc">Prijs laag–hoog</option>
        <option value="price-desc">Prijs hoog–laag</option>
        <option value="ppp">Beste prijs per steen</option>
        <option value="pieces">Meeste stenen</option>
      </select>
    </div>
    <div class="chips" id="chips" role="group" aria-label="Filter op thema"></div>
    <div class="meta" id="meta"></div>
  </div>
</div>

<main class="wrap">
  <div class="grid" id="grid"></div>
  <noscript><ul>{''.join(f'<li><a href="/sets/{s["slug"]}/">LEGO {s["n"]} {e(s["name"])}</a></li>' for s in SETS)}</ul></noscript>
  {alert_block()}
  <section class="how">
    <div><b>1. Kies je sets</b>Tik op het hartje bij de sets die je nog wilt hebben.</div>
    <div><b>2. Vergelijk prijzen</b>Bekijk in één tik de prijs bij LEGO, bol, Intertoys, Amazon en Tweakers.</div>
    <div><b>3. Krijg een seintje</b>Meld je aan en wij waarschuwen je voordat je set verdwijnt.</div>
  </section>
</main>
'''
index += FOOTER + bottomnav('sets')
index += f'''<script>window.SETS={list_data};window.THEME_COLORS={json.dumps(THEME_COLORS)};</script>
<script src="/assets/app.js"></script>
<script src="/assets/list.js"></script>
</body>
</html>
'''
write('/', index)

# ---------- Setpagina's ----------
by_theme = {}
for s in SETS:
    by_theme.setdefault(s['t'], []).append(s)

for s in SETS:
    path = f"/sets/{s['slug']}/"
    name = s['name']
    ppp = f"{s['p'] / s['pc'] * 100:.1f}".replace('.', ',')
    title = f"LEGO {s['n']} {name} stopt eind 2026 – prijzen vergelijken | Bouwradar"
    desc = f"LEGO {s['t']} {s['n']} {name} gaat naar verwachting op {STOP_DATE} uit productie. Adviesprijs {eur(s['p'])}, {num(s['pc'])} stenen. Vergelijk prijzen bij bol, Intertoys, LEGO.com en meer."
    faq = [
        (f"Wanneer stopt LEGO {s['n']} {name}?", f"Naar verwachting gaat deze set op {STOP_DATE} uit productie. LEGO kan die datum nog veranderen, dus check het regelmatig."),
        (f"Wat is de adviesprijs van LEGO {s['n']}?", f"De adviesprijs is {eur(s['p'])} voor {num(s['pc'])} stenen, ofwel {ppp} cent per steen."),
        (f"Waar koop ik LEGO {s['n']} het goedkoopst?", "Vergelijk de actuele prijs bij LEGO.com, bol, Intertoys, Amazon.nl en via Tweakers Pricewatch. Wacht je op korting? Meld je aan voor een seintje."),
        ("Wordt een set duurder na de stopdatum?", "Vaak wel: als winkels geen voorraad meer krijgen, stijgen de prijzen bij doorverkopers. Dat is niet gegarandeerd en verschilt per set."),
    ]
    ld = [
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Alle sets", "item": SITE_URL + '/'},
            {"@type": "ListItem", "position": 2, "name": f"LEGO {s['n']} {name}", "item": SITE_URL + path}]},
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}
    ]
    extra = ''.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>\n' for x in ld)
    related = [r for r in by_theme[s['t']] if r['n'] != s['n']]
    related = sorted(related, key=lambda r: -r['p'])[:6]
    color = THEME_COLORS.get(s['t'], '#444')

    page = head(title, desc, path, extra) + topbar('sets')
    page += f'''<section class="hero">
  <div class="wrap">
    <nav class="crumbs" aria-label="Kruimelpad"><a href="/">Alle sets</a><span>›</span>{e(s['t'])}<span>›</span>{s['n']}</nav>
    <h1>LEGO {s['n']} {e(name)}</h1>
    <p class="summary">{e(s['t'])} · adviesprijs {eur(s['p'])} · {num(s['pc'])} stenen · stopt naar verwachting op {STOP_DATE}</p>
    <span class="countchip">Nog <b data-days>–</b> dagen tot de stopdatum</span>
  </div>
</section>
<main class="wrap">
  <section class="panel" aria-labelledby="pi">
    {('<figure class="hero-img"><img src="' + e(s['img']) + '" alt="LEGO ' + s['n'] + ' ' + e(name) + '" decoding="async" referrerpolicy="no-referrer"></figure>') if s['img'] else ''}
    <h2 id="pi">Prijsinzicht</h2>
    <div class="insight">
      <div><span>Adviesprijs</span><b>{eur(s['p'])}</b></div>
      <div><span>Stenen</span><b>{num(s['pc'])}</b></div>
      <div><span>Prijs per steen</span><b>{ppp} ct</b></div>
      <div><span>Verwachte stopdatum</span><b>31 dec 2026</b></div>
      <div><span>Thema</span><b>{e(s['t'])}</b></div>
      <div><span>Laagste prijs nu</span><b class="note">Vergelijk hieronder</b></div>
    </div>
    <p class="datanote">Stopdatum en adviesprijs komen uit openbare bronnen en kunnen veranderen. De actuele prijs zie je bij de winkel zelf.</p>
    <button class="favbtn" id="favbtn" data-set="{s['n']}" aria-pressed="false">♡ Zet op mijn lijst</button>
  </section>

  <section class="block">
    <h2>Vergelijk de prijs</h2>
    <div class="shopgrid" id="shops" data-set="{s['n']}"></div>
  </section>

  {alert_block(s['n'], 'LEGO ' + s['n'])}
'''
    if related:
        page += f'''
  <section class="block">
    <h2>Meer {e(s['t'])}-sets die stoppen</h2>
    <div class="grid">
'''
        for r in related:
            page += f'''      <article class="card"><div class="top">
        {thumb(r, color)}
        <div class="title"><h3><a href="/sets/{r['slug']}/">{e(r['name'])}</a></h3><p>Adviesprijs {eur(r['p'])} · {num(r['pc'])} stenen</p></div>
      </div></article>
'''
        page += '    </div>\n  </section>\n'
    page += '''
  <section class="block faq">
    <h2>Veelgestelde vragen</h2>
'''
    for q, a in faq:
        page += f'    <details><summary>{e(q)}</summary><p>{e(a)}</p></details>\n'
    page += '  </section>\n</main>\n'
    page += FOOTER + bottomnav('sets')
    page += '''<script src="/assets/app.js"></script>
<script>
(function(){var el=document.getElementById('shops');BR.shopLinks(el.dataset.set).forEach(function(x){var a=document.createElement('a');a.className='shop';a.href=x[1];a.target='_blank';a.rel='noopener nofollow sponsored';a.textContent=x[0];el.appendChild(a);});})();
</script>
</body>
</html>
'''
    write(path, page)

# ---------- Uitleg ----------
uitleg = head('Hoe werkt Bouwradar? | Uitleg', 'Hoe Bouwradar werkt: LEGO-sets die uit productie gaan, prijzen vergelijken bij Nederlandse winkels en meldingen.', '/uitleg/')
uitleg += topbar('uitleg') + '''<section class="hero"><div class="wrap">
  <h1>Hoe werkt Bouwradar?</h1>
  <p class="lede">Elke LEGO-set heeft een vaste levensduur. Bouwradar laat zien welke sets binnenkort stoppen, zodat je ze nog voor de normale prijs kunt kopen.</p>
</div></section>
<main class="wrap">
  <section class="how" style="margin-top:20px">
    <div><b>1. Kies je sets</b>Tik op het hartje bij de sets die je nog wilt hebben. Je lijst blijft bewaard op dit apparaat.</div>
    <div><b>2. Vergelijk prijzen</b>Elke set heeft een eigen pagina met prijsinzicht en links naar Nederlandse winkels.</div>
    <div><b>3. Krijg een seintje</b>Meld je aan met je e-mailadres en wij waarschuwen je voordat je set verdwijnt.</div>
  </section>
  <section class="block faq">
    <h2>Veelgestelde vragen</h2>
    <details><summary>Waar komen de stopdata vandaan?</summary><p>Uit openbare lijsten van LEGO-fans en -nieuwssites. Het zijn verwachtingen: LEGO kan een set eerder of later laten stoppen.</p></details>
    <details><summary>Hoe verdient Bouwradar geld?</summary><p>Als je via een winkellink iets koopt, kunnen wij een kleine commissie krijgen. Jij betaalt niets extra, en de volgorde van sets en winkels hangt daar niet van af.</p></details>
    <details><summary>Wat doen jullie met mijn e-mailadres?</summary><p>We gebruiken het alleen om je meldingen over je lijstje te sturen. Je kunt je altijd afmelden.</p></details>
    <details><summary>Is Bouwradar van LEGO?</summary><p>Nee. Bouwradar is een onafhankelijke site en is niet verbonden aan de LEGO Group.</p></details>
  </section>
''' + alert_block() + '</main>\n' + FOOTER + bottomnav('uitleg') + '<script src="/assets/app.js"></script>\n</body>\n</html>\n'
write('/uitleg/', uitleg)

# ---------- Sitemap + robots ----------
urls = ['/', '/uitleg/'] + [f"/sets/{s['slug']}/" for s in SETS]
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
sm += ''.join(f'  <url><loc>{SITE_URL}{u}</loc></url>\n' for u in urls) + '</urlset>\n'
(ROOT / 'sitemap.xml').write_text(sm)
(ROOT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nDisallow: /api/\n\nSitemap: {SITE_URL}/sitemap.xml\n')
print(f'Klaar: {len(urls)} pagina\'s gebouwd voor {SITE_URL}')
