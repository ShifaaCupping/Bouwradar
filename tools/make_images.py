#!/usr/bin/env python3
"""Maakt de deelafbeelding (og.png) en het app-icoon. Eenmalig draaien."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT = Path(__file__).resolve().parent.parent
TTF = '/tmp/archivo.ttf'  # uit assets/fonts omgezet met fontTools

def f(size, wght=800, wdth=125):
    ft = ImageFont.truetype(TTF, size); ft.set_variation_by_axes([wght, wdth]); return ft

RED, DARK, YEL, YELD, WHITE = '#d01012', '#a40c0e', '#ffcf00', '#d9ad00', '#ffffff'
STUDS = [('#c91a09', 21), ('#6c6e68', 20), ('#1b2a34', 19), ('#0055bf', 16), ('#720e0f', 11), ('#81007b', 10)]

im = Image.new('RGB', (1200, 630), RED); d = ImageDraw.Draw(im)
d.rectangle([0, 600, 1200, 630], fill=DARK)
# logo
d.rounded_rectangle([72, 78, 132, 116], 6, fill=YEL); d.rounded_rectangle([78, 68, 94, 80], 3, fill=YEL); d.rounded_rectangle([110, 68, 126, 80], 3, fill=YEL)
d.rectangle([72, 110, 132, 116], fill=YELD)
d.text((150, 70), 'Steenradar', font=f(44), fill=WHITE)
d.text((72, 170), '130 LEGO-sets', font=f(84), fill=WHITE)
d.text((72, 262), 'stoppen op 31 december', font=f(64), fill=WHITE)
d.text((72, 360), 'Bekijk ze en vergelijk prijzen bij Nederlandse winkels.', font=f(30, 500, 100), fill='#ffe2df')
# stud chart card
d.rounded_rectangle([72, 430, 1128, 560], 18, fill=WHITE)
y = 452
for i, (c, n) in enumerate(STUDS[:3]):
    x = 100
    for k in range(n):
        d.ellipse([x, y, x + 26, y + 26], fill=c); x += 32
    y += 34
im.save(ROOT / 'assets/og.png', optimize=True)

ic = Image.new('RGB', (180, 180), RED); d = ImageDraw.Draw(ic)
d.rounded_rectangle([30, 62, 150, 126], 10, fill=YEL); d.rounded_rectangle([40, 46, 68, 66], 5, fill=YEL); d.rounded_rectangle([112, 46, 140, 66], 5, fill=YEL)
d.rectangle([30, 114, 150, 126], fill=YELD)
ic.save(ROOT / 'assets/apple-touch-icon.png', optimize=True)
print('ok')
