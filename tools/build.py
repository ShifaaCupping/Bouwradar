#!/usr/bin/env python3
"""Bouwt alle pagina's van Steenradar uit data/sets.json.

Gebruik:  python3 tools/build.py
Pas SITE_URL aan naar je eigen domein en draai het script opnieuw.
"""
import json, re, html, os, unicodedata
from pathlib import Path

SITE_URL = os.environ.get('SITE_URL', 'https://bouwradar.pages.dev').rstrip('/')
STOP_DATE = '31 december 2026'
ROOT = Path(__file__).resolve().parent.parent

THEME_COLORS = {
    'Star Wars': '#1b2a34', 'Icons': '#582a12', 'Ideas': '#36aebf', 'Technic': '#6c6e68',
    'Harry Potter': '#720e0f', 'Marvel': '#c91a09', 'Architecture': '#a0bcac', 'Art': '#fe8a18',
    'Botanicals': '#4b9f4a', 'Speed Champions': '#f2cd37', 'City': '#0055bf', 'Disney': '#81007b'
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
SITE = json.loads((ROOT / 'data/site.json').read_text())
LEGAL_OK = bool((SITE.get('bedrijfsnaam', '') or SITE.get('eigenaar', '')).strip()) and all(SITE.get(k, '').strip() for k in ('email', 'kvk'))
CONTACT_OK = LEGAL_OK and bool(SITE.get('adres', '').strip())
for s in SETS:
    s['slug'] = f"{s['n']}-{slugify(s['name'])}"

# Productfoto's: vul data/images.json met {"75192": "https://..."} uit je affiliate-productfeed
IMAGES_FILE = ROOT / 'data/images.json'
IMAGES = json.loads(IMAGES_FILE.read_text()) if IMAGES_FILE.exists() else {}
for s in SETS:
    s['img'] = IMAGES.get(s['n'], '')

CHECKED = '15 november 2026'
VERIFY_OK = f'Stopdatum bevestigd door twee onafhankelijke bronnen (<a href="/uitleg/#bronnen">Brick Fanatics en The Brick Observer</a>), gecontroleerd op {CHECKED}. LEGO kan de datum nog aanpassen.'
VERIFY_ONE = f'Stopdatum gemeld door één bron (<a href="/uitleg/#bronnen">Brick Fanatics</a>) en nog niet bevestigd door een tweede bron, gecontroleerd op {CHECKED}.'

def theme_slug(t):
    return slugify(t)

THEMES_ALL = sorted({x['t'] for x in SETS}, key=lambda t: -sum(1 for x in SETS if x['t'] == t))
AVG_PPP = sum(x['p'] / x['pc'] for x in SETS) / len(SETS)

def set_facts(s):
    same = [x for x in SETS if x['t'] == s['t']]
    by_pc = sorted(same, key=lambda x: -x['pc'])
    rank = by_pc.index(s) + 1
    ppp = s['p'] / s['pc']
    t_avg = sum(x['p'] / x['pc'] for x in same) / len(same)
    out = []
    if len(same) > 1:
        if rank == 1:
            out.append(f"Dit is de grootste van de {len(same)} {s['t']}-sets die eind 2026 stoppen.")
        elif rank == len(same):
            out.append(f"Dit is de kleinste van de {len(same)} {s['t']}-sets die eind 2026 stoppen.")
        else:
            out.append(f"Qua aantal stenen staat deze set op plek {rank} van de {len(same)} {s['t']}-sets die eind 2026 stoppen.")
        diff = (ppp - t_avg) / t_avg * 100
        if abs(diff) < 5:
            out.append(f"Met {ppp*100:.1f} cent per steen zit hij rond het gemiddelde van het thema.".replace('.', ',', 1))
        elif diff < 0:
            out.append(f"Met {ppp*100:.1f} cent per steen is hij {abs(diff):.0f}% voordeliger per steen dan gemiddeld in {s['t']}.".replace('.', ',', 1))
        else:
            out.append(f"Met {ppp*100:.1f} cent per steen is hij {diff:.0f}% duurder per steen dan gemiddeld in {s['t']}.".replace('.', ',', 1))
    else:
        out.append(f"Dit is de enige {s['t']}-set op de lijst van sets die eind 2026 stoppen.")
    return ' '.join(out)

def shade(hexc, amt):
    n = int(hexc[1:], 16); r, g, b = n >> 16, (n >> 8) & 255, n & 255
    t = 0 if amt < 0 else 255; p = abs(amt)
    r, g, b = (round((t - c) * p + c) for c in (r, g, b))
    return f'#{r:02x}{g:02x}{b:02x}'

def brick_svg(color, pieces):
    layers = 1 if pieces < 1500 else 2 if pieces < 3000 else 3
    studs = 2 if pieces < 500 else 4
    W = 64 if studs == 2 else 112; x0 = (120 - W) / 2; h = 26; top = 100 - layers * h
    dark, light = shade(color, -0.28), shade(color, 0.22)
    out = '<svg viewBox="0 0 120 104" aria-hidden="true">'
    pitch = W / studs
    for i in range(studs):
        sx = x0 + pitch * i + pitch / 2 - 8
        out += f'<rect x="{sx:g}" y="{top-8}" width="16" height="10" rx="2.5" fill="{color}"/><rect x="{sx:g}" y="{top-8}" width="16" height="3.5" rx="1.75" fill="{light}"/>'
    for l in range(layers):
        y = top + l * h
        out += f'<rect x="{x0:g}" y="{y}" width="{W}" height="{h}" rx="4" fill="{color}"/><rect x="{x0:g}" y="{y+h-5}" width="{W}" height="5" rx="2.5" fill="{dark}"/><rect x="{x0+4:g}" y="{y+3}" width="{W-8}" height="3" rx="1.5" fill="{light}" opacity=".7"/>'
    return out + '</svg>'

def thumb(s, color):
    inner = (f'<img src="{e(s["img"])}" alt="" loading="lazy" decoding="async" referrerpolicy="no-referrer">'
             if s['img'] else brick_svg(color, s['pc']))
    return f'<a class="thumb" href="/sets/{s["slug"]}/" aria-hidden="true" tabindex="-1">{inner}</a>'

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
<meta property="og:site_name" content="Steenradar">
<meta property="og:locale" content="nl_NL">
<meta property="og:image" content="{SITE_URL}/assets/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<meta name="theme-color" content="#d01012">
<link rel="preload" href="/assets/fonts/archivo-latin-wdth-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/style.css">
{extra}</head>
<body>
'''

CUR = ' aria-current="page"'

def topbar(active):
    links = [('sets', '/', 'Alle sets'), ('lijst', '/#mijn-lijst', 'Mijn lijst'), ('meld', '/#meldingen', 'Meldingen'), ('uitleg', '/uitleg/', 'Uitleg')]
    nav = ''.join(f'<a href="{h}"{CUR if k == active else ""}>{t}</a>' for k, h, t in links)
    return f'''<header class="topbar"><div class="wrap">
  <a class="brand" href="/"><span class="brick" aria-hidden="true"></span>Steenradar</a>
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
        p = 'Wij mailen je als de stopdatum van deze set nadert of verandert. Geen spam, altijd afmelden.'
        data = f' data-set="{set_n}"'
    else:
        h2 = 'Krijg een seintje op tijd'
        p = 'Wij mailen je als de stopdatum van een set op je lijst nadert of verandert. Geen spam, altijd afmelden.'
        data = ''
    PRIVACY_LINK = ' (zie de <a href="/privacy/">privacyverklaring</a>)' if LEGAL_OK else ''
    if not LEGAL_OK:
        # Geen aanmeldingen verzamelen zolang de privacyverklaring nog niet online staat
        return f'''<section class="alert" id="meldingen">
    <h2>{h2}</h2>
    <p>Meldingen per e-mail komen binnenkort. Zet je sets alvast met het hartje op je lijst; die blijft bewaard in je browser.</p>
  </section>
'''
    return f'''<section class="alert" id="meldingen">
    <h2>{h2}</h2>
    <p>{p}</p>
    <form id="form"{data} novalidate>
      <input type="email" id="email" placeholder="jouw@email.nl" aria-label="E-mailadres" autocomplete="email" maxlength="254" required>
      <input type="text" id="website" name="website" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
      <button type="submit">Meld mij aan</button>
    </form>
    <label class="consent"><input type="checkbox" id="ok" required> <span>Ik ga akkoord dat Steenradar mijn e-mailadres en mijn lijstje bewaart om mij meldingen te sturen{PRIVACY_LINK}.</span></label>
    <div class="msg" id="msg" role="status"></div>
  </section>
'''

FOOT_THEMES = ''.join(f'<a href="/thema/{slugify(t)}/">LEGO {e(t)}</a>' for t in sorted({x['t'] for x in SETS}))
LEGAL_LINKS = ('<a href="/privacy/">Privacy</a>' if LEGAL_OK else '') + ('<a href="/contact/">Contact</a>' if CONTACT_OK else '')
FOOTER = f'''<footer>
  <div class="wrap">
    <nav aria-label="Voettekst"><a href="/">Alle sets</a><a href="/#meldingen">Meldingen</a><a href="/uitleg/">Uitleg</a><a href="/gids/wanneer-stopt-een-lego-set/">Wanneer stopt een set?</a>{LEGAL_LINKS}</nav>
    <nav class="foot-themes" aria-label="Thema's">{FOOT_THEMES}</nav>
    <p>Prijzen vergelijken op Steenradar is gratis. Als je via een winkellink iets koopt, kunnen wij een kleine commissie krijgen; jij betaalt niets extra. De volgorde van sets en winkels hangt daar niet van af.</p>
    <p>Stopdata en adviesprijzen zijn verwachtingen op basis van openbare bronnen en kunnen veranderen. Controleer altijd de prijs bij de winkel.</p>
    <p>LEGO® is een handelsmerk van de LEGO Group, die deze site niet sponsort, autoriseert of onderschrijft. Steenradar is een onafhankelijke site.</p>
    <p>Steenradar is ook niet van bol of een andere winkel. De winkellinks sturen je door naar de website van die winkel, bijvoorbeeld bol; je bestelt en betaalt daar. Die winkels zijn niet verantwoordelijk voor Steenradar.</p>
  </div>
</footer>
<div class="toast" id="toast" role="status" aria-live="polite"></div>
'''.replace('{{', '{').replace('}}', '}')

AFF = {k: v for k, v in SITE.get('affiliate', {}).items() if not k.startswith('_') and v.strip()}
(ROOT / 'assets/config.js').write_text('// Gegenereerd door tools/build.py uit data/site.json\nwindow.BR_AFF = ' + json.dumps(AFF) + ';\n')

def write(path, content):
    content = content.replace('<script src="/assets/app.js"></script>', '<script src="/assets/config.js"></script>\n<script src="/assets/app.js"></script>')
    p = ROOT / path.lstrip('/')
    if path.endswith('/'):
        p = p / 'index.html'
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)

# ---------- Overzicht ----------
themes = sorted({s['t'] for s in SETS})
list_data = json.dumps([{k: s[k] for k in ('t', 'n', 'name', 'p', 'pc', 'slug', 'img')} for s in SETS], ensure_ascii=False, separators=(',', ':'))
POP = ['75192','10326','21323','75367','75397','21333','76437','43263','10335','21360']
FEATURED = ''
for n in POP:
    f = next((x for x in SETS if x['n'] == n), None)
    if not f: continue
    col = THEME_COLORS.get(f['t'], '#444')
    ph = f'<img src="{e(f["img"])}" alt="" loading="lazy" referrerpolicy="no-referrer">' if f['img'] else brick_svg(col, f['pc'])
    FEATURED += f'<a class="feat" href="/sets/{f["slug"]}/"><div class="art">{ph}</div><b>{e(f["name"])}</b><span class="sub">{e(f["t"])}, {num(f["pc"])} stenen</span><span class="price">{eur(f["p"])}</span></a>'

counts = sorted(((t, sum(1 for x in SETS if x['t'] == t)) for t in themes), key=lambda x: -x[1])
CHART = ''
for t, c in counts:
    col = THEME_COLORS.get(t, '#444')
    studs = ''.join('<i class="stud"></i>' for _ in range(c))
    CHART += f'<button class="srow" type="button" data-theme="{e(t)}" style="--c:{col}" aria-label="{e(t)}: {c} sets, toon deze sets"><span class="lbl">{e(t)}</span><span class="cnt">{c}</span><span class="studs" aria-hidden="true">{studs}</span></button>'

THEMELINKS = ''.join(f'<a href="/thema/{theme_slug(t)}/" style="--c:{THEME_COLORS.get(t, "#444")}"><i></i>{e(t)}<span>{sum(1 for x in SETS if x["t"] == t)}</span></a>' for t in THEMES_ALL)
WEBSITE_LD = '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@type": "WebSite", "name": "Steenradar", "url": SITE_URL + '/', "inLanguage": "nl-NL", "description": "Overzicht van LEGO-sets die uit productie gaan, met prijslinks naar Nederlandse winkels."}, ensure_ascii=False) + '</script>\n'
index = head('Steenradar — LEGO-sets die eind 2026 uit productie gaan',
             f'{len(SETS)} LEGO-sets die naar verwachting op {STOP_DATE} stoppen. Vergelijk prijzen bij Nederlandse winkels en krijg een seintje voordat je set verdwijnt.', '/', WEBSITE_LD)
index += topbar('sets')
index += f'''<section class="hero">
  <div class="wrap">
    <div class="hero-grid">
      <div>
        <h1>{len(SETS)} LEGO-sets stoppen op 31&nbsp;december</h1>
        <p class="lede">Daarna lopen de prijzen bij doorverkopers vaak op. Je hebt nog <b data-days>–</b> dagen om ze voor de gewone prijs te kopen.</p>
        <div class="ctas"><a class="cta primary" href="#alle-sets">Bekijk de sets</a><a class="cta secondary" href="#meldingen">Seintje instellen</a></div>
      </div>
      <div class="studchart">
        <h2>Wat er verdwijnt, per thema</h2>
        <p class="key">Elk nopje is één set. Tik op een thema om die sets te zien.</p>
        {CHART}
      </div>
    </div>
  </div>
</section>

<section class="wrap" aria-label="Uitgelicht">
  <div class="section-head"><h2>Populair bij verzamelaars</h2><p>De grote sets waar het snelst om gevochten wordt.</p></div>
  <div class="rail">{FEATURED}</div>
  <div class="section-head"><h2>Per thema</h2><p>Elk thema heeft een eigen overzicht. Nieuw hier? Lees eerst <a href="/gids/wanneer-stopt-een-lego-set/">wanneer een LEGO-set stopt</a>.</p></div>
  <nav class="themelinks" aria-label="Thema's">{THEMELINKS}</nav>
  <div class="section-head" id="alle-sets"><h2>Alle sets die stoppen</h2><p>Zoek, filter op thema of zet sets op je lijst.</p></div>
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
    <div><b>2. Vergelijk prijzen</b>Bekijk in één tik de prijs bij LEGO.com, bol, Intertoys en Amazon.</div>
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
    title = next(t for t in (f"LEGO {s['n']} {name} stopt eind 2026 | Steenradar", f"LEGO {s['n']} {name} stopt eind 2026", f"LEGO {s['n']} {name}") if len(t) <= 60 or t == f"LEGO {s['n']} {name}")
    desc = f"LEGO {s['n']} {name} stopt naar verwachting op {STOP_DATE}. Adviesprijs {eur(s['p'])}, {num(s['pc'])} stenen. Vergelijk prijzen in NL."
    faq = [
        (f"Wanneer stopt LEGO {s['n']} {name}?", f"Naar verwachting gaat deze set op {STOP_DATE} uit productie. LEGO kan die datum nog veranderen, dus check het regelmatig."),
        (f"Wat is de adviesprijs van LEGO {s['n']}?", f"De adviesprijs is {eur(s['p'])} voor {num(s['pc'])} stenen, ofwel {ppp} cent per steen."),
        (f"Waar koop ik LEGO {s['n']} het goedkoopst?", "Vergelijk de actuele prijs bij LEGO.com, bol, Intertoys en Amazon.nl, of zoek tweedehands op Marktplaats. Wacht je op korting? Meld je aan voor een seintje."),
        ("Wordt een set duurder na de stopdatum?", "Vaak wel: als winkels geen voorraad meer krijgen, stijgen de prijzen bij doorverkopers. Dat is niet gegarandeerd en verschilt per set."),
    ]
    ld = [
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Alle sets", "item": SITE_URL + '/'},
            {"@type": "ListItem", "position": 2, "name": f"{s['t']}", "item": SITE_URL + f"/thema/{theme_slug(s['t'])}/"},
            {"@type": "ListItem", "position": 3, "name": f"LEGO {s['n']} {name}", "item": SITE_URL + path}]},
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
    <nav class="crumbs" aria-label="Kruimelpad"><a href="/">Alle sets</a><span>/</span><a href="/thema/{theme_slug(s['t'])}/">{e(s['t'])}</a></nav>
    <div class="set-hero">
      <div>
        <h1>LEGO {s['n']} {e(name)}</h1>
        <p class="summary">{e(s['t'])}-set met {num(s['pc'])} stenen en een adviesprijs van {eur(s['p'])}. Stopt naar verwachting op {STOP_DATE}.</p>
        <span class="countchip">Nog <b data-days>–</b> dagen</span>
      </div>
      <div class="set-art">{('<img src="' + e(s['img']) + '" alt="LEGO ' + s['n'] + ' ' + e(name) + '" decoding="async" referrerpolicy="no-referrer">') if s['img'] else brick_svg(color, s['pc'])}</div>
    </div>
  </div>
</section>
<main class="wrap">
  <section class="panel" aria-labelledby="pi">
    <h2 id="pi">Prijsinzicht</h2>
    <div class="insight">
      <div><span>Adviesprijs</span><b>{eur(s['p'])}</b></div>
      <div><span>Stenen</span><b>{num(s['pc'])}</b></div>
      <div><span>Prijs per steen</span><b>{ppp} ct</b></div>
      <div><span>Verwachte stopdatum</span><b>31 dec 2026</b></div>
      <div><span>Thema</span><b><a href="/thema/{theme_slug(s['t'])}/">{e(s['t'])}</a></b></div>
      <div><span>Laagste prijs nu</span><b class="note">Vergelijk hieronder</b></div>
    </div>
    <p class="facts">{e(set_facts(s))}</p>
    <p class="datanote">{VERIFY_OK if s.get('v') else VERIFY_ONE} De actuele prijs zie je bij de winkel zelf.</p>
    <button class="favbtn" id="favbtn" data-set="{s['n']}" aria-pressed="false">♡ Zet op mijn lijst</button>
  </section>

  <section class="block">
    <h2>Vergelijk de prijs</h2>
    <p class="datanote" style="margin:-4px 0 12px">Je gaat naar de website van de winkel en bestelt daar.</p>
    <div class="shopgrid" id="shops" data-set="{s['n']}"></div>
  </section>

  {alert_block(s['n'], 'LEGO ' + s['n'])}
'''
    if related:
        page += f'''
  <section class="block">
    <h2>Meer {e(s['t'])}-sets die stoppen</h2>
    <p class="datanote" style="margin:-4px 0 12px"><a href="/thema/{theme_slug(s['t'])}/">Bekijk alle {len(by_theme[s['t']])} {e(s['t'])}-sets</a></p>
    <div class="grid">
'''
        for r in related:
            page += f'''      <article class="card"><div class="top">
        {thumb(r, color)}
        <div class="title"><h3><a href="/sets/{r['slug']}/">{e(r['name'])}</a></h3><p>{num(r['pc'])} stenen, adviesprijs {eur(r['p'])}</p></div>
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
uitleg = head('Hoe werkt Steenradar? | Uitleg', 'Hoe Steenradar werkt: LEGO-sets die uit productie gaan, prijzen vergelijken bij Nederlandse winkels en meldingen.', '/uitleg/')
uitleg += topbar('uitleg') + '''<section class="hero"><div class="wrap">
  <h1>Hoe werkt Steenradar?</h1>
  <p class="lede">Elke LEGO-set heeft een vaste levensduur. Steenradar laat zien welke sets binnenkort stoppen, zodat je ze nog voor de normale prijs kunt kopen.</p>
</div></section>
<main class="wrap">
  <section class="how" style="margin-top:20px">
    <div><b>1. Kies je sets</b>Tik op het hartje bij de sets die je nog wilt hebben. Je lijst blijft bewaard op dit apparaat.</div>
    <div><b>2. Vergelijk prijzen</b>Elke set heeft een eigen pagina met prijsinzicht en links naar Nederlandse winkels.</div>
    <div><b>3. Krijg een seintje</b>Meld je aan met je e-mailadres en wij waarschuwen je voordat je set verdwijnt.</div>
  </section>
  <section class="block faq">
    <h2>Veelgestelde vragen</h2>
    <details id="bronnen"><summary>Waar komen de stopdata vandaan?</summary><p>We vergelijken twee onafhankelijke lijsten: <a href="https://www.brickfanatics.com/every-lego-set-retiring-this-year-and-beyond/" rel="nofollow noopener" target="_blank">Brick Fanatics</a> en <a href="https://thebrickobserver.com/every-lego-set-retiring-in-2026/" rel="nofollow noopener" target="_blank">The Brick Observer</a>. Staat een set in allebei, dan noemen we de stopdatum bevestigd. Het blijven verwachtingen: LEGO kan een set eerder of later laten stoppen. Laatst gecontroleerd op 15 november 2026.</p></details>
    <details><summary>Hoe verdient Steenradar geld?</summary><p>Als je via een winkellink iets koopt, kunnen wij een kleine commissie krijgen. Jij betaalt niets extra, en de volgorde van sets en winkels hangt daar niet van af.</p></details>
    <details><summary>Wat doen jullie met mijn e-mailadres?</summary><p>We gebruiken het alleen om je meldingen over je lijstje te sturen. Je kunt je altijd afmelden.</p></details>
    <details><summary>Is Steenradar van LEGO of van een winkel?</summary><p>Nee. Steenradar is een onafhankelijke site en is niet verbonden aan de LEGO Group, bol of een andere winkel. Via de winkellinks ga je naar de website van de winkel en bestel je daar.</p></details>
  </section>
''' + alert_block() + '</main>\n' + FOOTER + bottomnav('uitleg') + '<script src="/assets/app.js"></script>\n</body>\n</html>\n'
write('/uitleg/', uitleg)

# ---------- Gids ----------
GUIDE_PATH = '/gids/wanneer-stopt-een-lego-set/'
guide_faq = [
    ("Wanneer gaan LEGO-sets uit productie?", "Meestal in twee rondes per jaar: eind juli en eind december. De meeste sets stoppen op 31 december."),
    ("Hoe lang is een LEGO-set te koop?", "Vaak ongeveer twee tot drie jaar, maar dat verschilt sterk per set en thema. Grote sets voor volwassenen blijven soms langer, kleine sets korter."),
    ("Hoe weet ik of een set bijna stopt?", "Op LEGO.com staat bij sets die bijna verdwijnen het label 'Binnenkort uit handel'. Steenradar zet alle verwachte stopdata per set op een rij."),
    ("Worden sets duurder als ze gestopt zijn?", "Vaak wel, omdat winkels geen nieuwe voorraad meer krijgen en doorverkopers de prijs bepalen. Dat is niet gegarandeerd en verschilt per set."),
]
g_ld = [{"@context": "https://schema.org", "@type": "Article", "headline": "Wanneer stopt een LEGO-set? Zo werkt het", "inLanguage": "nl-NL",
         "datePublished": "2026-11-15", "dateModified": "2026-11-15", "author": {"@type": "Organization", "name": "Steenradar"}},
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in guide_faq]}]
guide = head('Wanneer stopt een LEGO-set? Zo werkt het | Steenradar',
             'Wanneer LEGO-sets uit productie gaan, hoe je het ziet aankomen en hoe je een set nog voor de gewone prijs koopt.',
             GUIDE_PATH, ''.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>\n' for x in g_ld))
top5 = sorted(SETS, key=lambda x: -x['pc'])[:5]
guide += topbar('uitleg') + f'''<section class="hero"><div class="wrap">
  <nav class="crumbs" aria-label="Kruimelpad"><a href="/">Alle sets</a><span>/</span>Gids</nav>
  <h1>Wanneer stopt een LEGO-set?</h1>
  <p class="lede">Elke LEGO-set is maar een paar jaar te koop. Zo werkt het, zo zie je het aankomen en zo koop je een set nog voor de gewone prijs.</p>
</div></section>
<main class="wrap legal">
  <h2>Twee rondes per jaar</h2>
  <p>LEGO haalt sets meestal in twee rondes uit productie: eind juli en eind december. De grootste ronde is op 31 december. Op dit moment staan er {len(SETS)} sets op de lijst voor 31 december 2026, verdeeld over {len(THEMES_ALL)} thema's.</p>
  <h2>Hoe lang is een set te koop?</h2>
  <p>Vaak ongeveer twee tot drie jaar. Sets uit grote licenties zoals Star Wars en Harry Potter wisselen snel, omdat er steeds nieuwe films en series zijn. Grote sets voor volwassenen, zoals de Ultimate Collector Series, blijven soms langer.</p>
  <h2>Zo zie je het aankomen</h2>
  <p>Op LEGO.com krijgen sets die bijna verdwijnen het label "Binnenkort uit handel". Fansites houden lijsten bij met verwachte stopdata; Steenradar vergelijkt twee van die lijsten en zet de uitkomst per set op een rij. Een stopdatum blijft een verwachting: LEGO kan een set eerder of later laten stoppen.</p>
  <h2>Wat gebeurt er met de prijs?</h2>
  <p>Zolang een set in de winkel ligt, zit de prijs rond de adviesprijs, met af en toe korting. Na de stopdatum raken winkelvoorraden op en bepalen doorverkopers de prijs. Bij populaire sets loopt die dan vaak op. Dat is geen garantie: sommige sets blijven lang in de schappen liggen of worden juist afgeprijsd.</p>
  <h2>Zo koop je nog voor de gewone prijs</h2>
  <p>Begin met de sets die je echt wilt hebben en zet ze op je lijst. Vergelijk de prijs bij een paar winkels, want kortingen verschillen per winkel en per week. Rond Black Friday, Sinterklaas en kerst zijn er vaak acties. Wacht niet tot de laatste week van december: populaire sets zijn dan vaak al uitverkocht.</p>
  <h2>De grootste sets die eind 2026 stoppen</h2>
  <p>{'; '.join(f'<a href="/sets/{x["slug"]}/">LEGO {x["n"]} {e(x["name"])}</a> ({num(x["pc"])} stenen)' for x in top5)}.</p>
  <h2>Per thema</h2>
  <nav class="themelinks" aria-label="Thema's">{THEMELINKS}</nav>
  <section class="block faq">
    <h2>Veelgestelde vragen</h2>
    {''.join(f'<details><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in guide_faq)}
  </section>
  <p class="datanote">Laatst bijgewerkt: 15 november 2026.</p>
</main>
''' + FOOTER + bottomnav('uitleg') + '<script src="/assets/app.js"></script>\n</body>\n</html>\n'
write(GUIDE_PATH, guide)

# ---------- Themapagina's ----------
theme_urls = []
for t in THEMES_ALL:
    items = sorted(by_theme[t], key=lambda x: -x['pc'])
    slug = theme_slug(t); path = f'/thema/{slug}/'
    col = THEME_COLORS.get(t, '#444')
    total_pc = sum(x['pc'] for x in items); cheapest = min(items, key=lambda x: x['p']); biggest = items[0]
    n = len(items)
    title = f'LEGO {t}-sets die stoppen in 2026 ({n}) | Steenradar'
    desc = f'{n} LEGO {t}-sets stoppen naar verwachting op {STOP_DATE}, van {eur(cheapest["p"])} tot {eur(max(x["p"] for x in items))}. Bekijk ze en vergelijk prijzen.'
    intro = (f'{n} {t}-sets gaan naar verwachting op {STOP_DATE} uit productie, samen goed voor {num(total_pc)} stenen. '
             f'De grootste is {biggest["name"]} ({num(biggest["pc"])} stenen), de goedkoopste {cheapest["name"]} ({eur(cheapest["p"])}).') if n > 1 else \
            f'Eén {t}-set gaat naar verwachting op {STOP_DATE} uit productie: {biggest["name"]} met {num(biggest["pc"])} stenen.'
    ld = [{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "Alle sets", "item": SITE_URL + '/'},
              {"@type": "ListItem", "position": 2, "name": t, "item": SITE_URL + path}]},
          {"@context": "https://schema.org", "@type": "ItemList", "name": f"LEGO {t}-sets die stoppen in 2026", "itemListElement": [
              {"@type": "ListItem", "position": i + 1, "url": SITE_URL + f"/sets/{x['slug']}/", "name": f"LEGO {x['n']} {x['name']}"} for i, x in enumerate(items)]}]
    extra = ''.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>\n' for x in ld)
    page = head(title, desc, path, extra) + topbar('sets')
    page += f'''<section class="hero"><div class="wrap">
  <nav class="crumbs" aria-label="Kruimelpad"><a href="/">Alle sets</a><span>/</span>{e(t)}</nav>
  <h1>LEGO {e(t)}-sets die stoppen in 2026</h1>
  <p class="lede">{e(intro)}</p>
  <span class="countchip">Nog <b data-days>–</b> dagen tot 31 december</span>
</div></section>
<main class="wrap">
  <div class="grid">
'''
    for x in items:
        ppp = f"{x['p'] / x['pc'] * 100:.1f}".replace('.', ',')
        page += f'''    <article class="card"><div class="top">{thumb(x, col)}<div class="title"><h2 class="cardtitle"><a href="/sets/{x['slug']}/">{e(x['name'])}</a></h2><p>Set {x['n']}</p></div></div>
      <div class="figs"><div><span>Adviesprijs</span><b>{eur(x['p'])}</b></div><div><span>Stenen</span><b>{num(x['pc'])}</b></div><div><span>Per steen</span><b>{ppp} ct</b></div></div>
      <a class="btn ghost" href="/sets/{x['slug']}/">Prijsinzicht en winkels</a></article>
'''
    page += f'''  </div>
  <div class="section-head"><h2>Andere thema's</h2></div>
  <nav class="themelinks" aria-label="Thema's">{''.join(f'<a href="/thema/{theme_slug(o)}/" style="--c:{THEME_COLORS.get(o, "#444")}"><i></i>{e(o)}<span>{len(by_theme[o])}</span></a>' for o in THEMES_ALL if o != t)}</nav>
  {alert_block()}
</main>
''' + FOOTER + bottomnav('sets') + '<script src="/assets/app.js"></script>\n</body>\n</html>\n'
    write(path, page)
    theme_urls.append(path)

# ---------- 404 ----------
notfound = head('Pagina niet gevonden | Steenradar', 'Deze pagina bestaat niet (meer). Bekijk alle LEGO-sets die eind 2026 stoppen of kies een thema.', '/404', '<meta name="robots" content="noindex">\n')
notfound += topbar('') + f'''<section class="hero"><div class="wrap"><h1>Deze pagina bestaat niet</h1>
  <p class="lede">Misschien is de set verplaatst of klopt de link niet. Kies hieronder een thema of ga terug naar het overzicht.</p>
  <div class="ctas"><a class="cta primary" href="/">Naar alle sets</a></div></div></section>
<main class="wrap"><nav class="themelinks" aria-label="Thema's">{THEMELINKS}</nav></main>
''' + FOOTER + bottomnav('') + '<script src="/assets/app.js"></script>\n</body>\n</html>\n'
(ROOT / '404.html').write_text(notfound.replace('<script src="/assets/app.js"></script>', '<script src="/assets/config.js"></script>\n<script src="/assets/app.js"></script>'))

# ---------- Privacy + contact (alleen als data/site.json is ingevuld) ----------
legal_urls = []
if LEGAL_OK:
    bedrijf = SITE.get('bedrijfsnaam', '').strip(); eig = SITE.get('eigenaar', '').strip()
    who = e(f'{bedrijf} ({eig})' if bedrijf and eig else (bedrijf or eig))
    mail = e(SITE['email']); kvk = e(SITE['kvk']); adres = e(SITE.get('adres', ''))
    btw = f'<p><b>Btw-identificatienummer:</b> {e(SITE["btw_id"])}</p>' if SITE.get('btw_id', '').strip() else ''
    privacy = head('Privacyverklaring | Steenradar', 'Welke gegevens Steenradar verwerkt, waarom, en wat je rechten zijn.', '/privacy/')
    privacy += topbar('') + f'''<section class="hero"><div class="wrap"><h1>Privacyverklaring</h1>
  <p class="lede">Steenradar verzamelt zo weinig mogelijk. Hier lees je wat we verwerken, waarom, hoe lang, en wat je rechten zijn.</p>
  <p class="lede" style="font-size:14px;margin-top:-10px">Laatst bijgewerkt: 15 november 2026</p></div></section>
<main class="wrap legal">
  <h2>Wie is verantwoordelijk?</h2>
  <p>Steenradar is een website van {who}, ingeschreven bij de KVK onder nummer {kvk}. Dit bedrijf is verantwoordelijk voor de verwerking van je gegevens. Vragen en verzoeken over privacy stuur je naar <a href="mailto:{mail}">{mail}</a>.</p>

  <h2>Kort gezegd</h2>
  <ul>
    <li>Geen analytische, tracking- of advertentiecookies, en geen profilering.</li>
    <li>De sets op "Mijn lijst" blijven in je eigen browser; wij zien ze niet.</li>
    <li>We bewaren alleen je e-mailadres en sets als je je zelf aanmeldt voor meldingen.</li>
    <li>We verkopen niets door en delen alleen met de dienst die de site draait.</li>
  </ul>

  <h2>Wat we verwerken</h2>
  <p><b>Bezoek aan de site.</b> De site draait bij Cloudflare. Bij elk bezoek verwerkt Cloudflare technische gegevens, zoals je IP-adres en browsergegevens, om de site te leveren en te beveiligen. Grondslag: gerechtvaardigd belang (een werkende, veilige website). Wij gebruiken deze gegevens niet om jou te volgen.</p>
  <p><b>Meldingen per e-mail.</b> Meld je je aan, dan bewaren we je e-mailadres, de setnummers op je lijst, het moment waarop je toestemming gaf en een afmeldcode. Doel: je mailen als de stopdatum van die sets nadert of verandert. Grondslag: je toestemming, die je geeft met het vinkje. Bewaartermijn: tot je je afmeldt. Via de afmeldlink in elke mail worden je gegevens direct verwijderd; via een verzoek per mail binnen 30 dagen.</p>
  <p><b>Mijn lijst.</b> De sets die je met een hartje bewaart, staan alleen in de opslag van je eigen browser (localStorage). Ze worden niet naar ons verstuurd, tenzij je je aanmeldt voor meldingen. Je wist ze door de sitegegevens in je browser te verwijderen.</p>
  <p><b>Contact per e-mail.</b> Mail je ons, dan gebruiken we je naam, e-mailadres en bericht om je te antwoorden. We bewaren dit tot je vraag is afgehandeld en daarna nog maximaal 12 maanden.</p>
  <p><b>Doorklikken naar een winkel.</b> Klik je op een winkellink, bijvoorbeeld naar bol, dan ga je naar de website van die winkel. De winkel of een affiliatenetwerk kan daar cookies plaatsen om te zien dat je via Steenradar kwam; daarvoor geldt hun eigen privacyverklaring. Wij krijgen alleen te zien dat er een aankoop is gedaan en welke commissie daarbij hoort, niet wie jij bent.</p>

  <h2>Diensten die we gebruiken</h2>
  <p><b>Cloudflare</b> host de site, de database met aanmeldingen en de technische afhandeling van bezoeken. Cloudflare verwerkt die gegevens alleen in onze opdracht. Cloudflare is een Amerikaans bedrijf; doorgifte buiten de EU gebeurt op basis van het EU-VS Data Privacy Framework of de standaardcontractbepalingen van de Europese Commissie. We laden geen lettertypes, scripts of advertenties van Google, Meta of andere derden.</p>

  <h2>Beveiliging</h2>
  <p>De site werkt alleen via een versleutelde verbinding (https). De database en de beheeromgeving zijn alleen toegankelijk voor ons en afgeschermd met een eigen account. We bewaren niet meer gegevens dan nodig.</p>

  <h2>Jouw rechten</h2>
  <p>Je hebt het recht op inzage, correctie, verwijdering, beperking van de verwerking, bezwaar en overdraagbaarheid van je gegevens, en je kunt je toestemming altijd intrekken. Stuur je verzoek naar <a href="mailto:{mail}">{mail}</a>; we reageren binnen een maand. Ben je het niet eens met hoe we met je gegevens omgaan, dan kun je een klacht indienen bij de <a href="https://www.autoriteitpersoonsgegevens.nl" rel="noopener" target="_blank">Autoriteit Persoonsgegevens</a>.</p>

  <h2>Wijzigingen</h2>
  <p>Gaan we gegevens anders verwerken, bijvoorbeeld omdat we mails gaan versturen via een maildienst, dan passen we deze verklaring aan. De datum bovenaan laat zien wanneer dat voor het laatst gebeurde.</p>
</main>
''' + FOOTER + bottomnav('') + '<script src="/assets/app.js"></script>\n</body>\n</html>\n'
    write('/privacy/', privacy)
    contact = head('Contact | Steenradar', 'Contactgegevens en bedrijfsgegevens van Steenradar.', '/contact/')
    contact += topbar('') + f'''<section class="hero"><div class="wrap"><h1>Contact</h1>
  <p class="lede">Vraag, foutje in een stopdatum of samenwerking? Mail ons, we reageren meestal binnen twee werkdagen.</p></div></section>
<main class="wrap legal">
  <p><b>E-mail:</b> <a href="mailto:{mail}">{mail}</a></p>
  <p><b>Handelsnaam:</b> Steenradar</p>
  <p><b>Bedrijf:</b> {who}</p>
  <p><b>Adres:</b> {adres}</p>
  <p><b>KVK-nummer:</b> {kvk}</p>
  {btw}
</main>
''' + FOOTER + bottomnav('') + '<script src="/assets/app.js"></script>\n</body>\n</html>\n'
    legal_urls = ['/privacy/']
    if CONTACT_OK:
        write('/contact/', contact)
        legal_urls.append('/contact/')
else:
    print('Let op: data/site.json is nog niet ingevuld, dus privacy- en contactpagina zijn overgeslagen.')
if LEGAL_OK and not CONTACT_OK:
    print('Let op: geen adres in data/site.json, dus de contactpagina is overgeslagen.')

# ---------- Sitemap + robots ----------
urls = ['/', '/uitleg/', GUIDE_PATH] + theme_urls + legal_urls + [f"/sets/{s['slug']}/" for s in SETS]
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
LASTMOD = os.environ.get('LASTMOD', __import__('datetime').date.today().isoformat())
sm += ''.join(f'  <url><loc>{SITE_URL}{u}</loc><lastmod>{LASTMOD}</lastmod></url>\n' for u in urls) + '</urlset>\n'
(ROOT / 'sitemap.xml').write_text(sm)
(ROOT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nDisallow: /api/\n\nSitemap: {SITE_URL}/sitemap.xml\n')
print(f'Klaar: {len(urls)} pagina\'s gebouwd voor {SITE_URL}')
