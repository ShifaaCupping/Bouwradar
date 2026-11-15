#!/usr/bin/env python3
"""Controleert de gebouwde site: interne links, titels, meta descriptions, één H1, geldige JSON-LD, sitemap.
Gebruik: python3 tools/check.py   (exit-code 1 bij fouten)"""
import re, json, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
pages = [p for p in ROOT.rglob('index.html') if '.git' not in p.parts] + [ROOT / '404.html']
errors, warnings = [], []
for p in pages:
    rel = '/' + str(p.relative_to(ROOT)).replace('index.html', '')
    t = p.read_text()
    for href in re.findall(r'href="(/[^"#?]*)', t):
        q = ROOT / href.lstrip('/')
        if href.endswith('/'): q = q / 'index.html'
        if not q.exists(): errors.append(f'{rel}: kapotte link {href}')
    m = re.search(r'<title>(.*?)</title>', t)
    if not m: errors.append(f'{rel}: geen <title>')
    elif len(m.group(1)) > 70: warnings.append(f'{rel}: lange titel ({len(m.group(1))})')
    if not re.search(r'name="description" content=".{50,}"', t): errors.append(f'{rel}: meta description ontbreekt of te kort')
    n = len(re.findall(r'<h1[ >]', t))
    if n != 1: errors.append(f'{rel}: {n} keer <h1>')
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
        try: json.loads(blk)
        except Exception as ex: errors.append(f'{rel}: ongeldige JSON-LD ({ex})')
    if 'fonts.googleapis' in t or 'gstatic' in t: errors.append(f'{rel}: laadt Google Fonts')
sm = (ROOT / 'sitemap.xml').read_text()
for loc in re.findall(r'<loc>https?://[^/]+(/[^<]*)</loc>', sm):
    q = ROOT / loc.lstrip('/'); q = q / 'index.html' if loc.endswith('/') else q
    if not q.exists(): errors.append(f'sitemap: {loc} bestaat niet')
print(f'{len(pages)} pagina\'s gecontroleerd, {len(errors)} fouten, {len(warnings)} waarschuwingen')
for x in errors[:50]: print('FOUT', x)
for x in warnings[:20]: print('LET OP', x)
sys.exit(1 if errors else 0)
