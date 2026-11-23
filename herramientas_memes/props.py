"""Build abuelita (moka + rebozo) and an unbranded instant-coffee jar. usage: props.py <dir>"""
import sys, math
from PIL import Image, ImageDraw, ImageFilter, ImageChops
D = sys.argv[1]
moka = Image.open(f"{D}/cafetera.png").convert("RGBA")
SS = 4
PAD = 40
W, H = moka.width + 2 * PAD, moka.height + 2 * PAD
big = (W * SS, H * SS)
def P(x, y): return ((x + PAD) * SS, (y + PAD) * SS)
INK = (60, 40, 50, 255)
BASE = (46, 62, 128, 255)      # indigo rebozo
STRIPE = (232, 226, 210, 255)
ROSE = (196, 58, 84, 255)
# outer drape: over the lid and down both sides of the upper chamber
outer = [(-14, 300), (-22, 200), (-10, 110), (20, 60), (70, 28), (145, -8), (215, 26), (262, 80), (282, 150), (286, 230), (292, 305),
         (250, 312), (236, 250), (220, 205), (60, 205), (40, 250), (30, 310)]
mask = Image.new("L", big, 0)
md = ImageDraw.Draw(mask)
md.polygon([P(*p) for p in outer], fill=255)
# face opening
md.ellipse([P(52, 92)[0], P(52, 92)[1], P(232, 212)[0], P(232, 212)[1]], fill=0)
# pattern layer
pat = Image.new("RGBA", big, BASE)
pd = ImageDraw.Draw(pat)
for k in range(-20, 40):
    x0 = k * 22 * SS
    pd.line([(x0, 0), (x0 + H * SS * 0.5, H * SS)], fill=(36, 50, 108, 255), width=6 * SS)
for y in (0.80, 0.86):
    pass
# borders: stripes following the hem near bottom of each side
for yy, col in ((262, STRIPE), (272, ROSE), (282, STRIPE)):
    pd.line([P(-30, yy), P(70, yy)], fill=col, width=5 * SS)
    pd.line([P(220, yy), P(310, yy)], fill=col, width=5 * SS)
# little dots (rebozo de bolita)
for yy in range(0, 340, 18):
    for xx in range(-30, 320, 18):
        if (xx // 18 + yy // 18) % 2 == 0:
            pd.ellipse([P(xx, yy)[0] - 4, P(xx, yy)[1] - 4, P(xx, yy)[0] + 4, P(xx, yy)[1] + 4], fill=(120, 140, 200, 255))
shawl = Image.new("RGBA", big, (0, 0, 0, 0))
shawl.paste(pat, (0, 0), mask)
# outline
edge = mask.filter(ImageFilter.MaxFilter(13)); edge = ImageChops.subtract(edge, mask)
ol = Image.new("RGBA", big, INK); shawl_o = Image.new("RGBA", big, (0, 0, 0, 0)); shawl_o.paste(ol, (0, 0), edge)
shawl_o.alpha_composite(shawl)
# fringe
fd = ImageDraw.Draw(shawl_o)
for x0, x1, y0 in ((-14, 30, 300), (250, 292, 305)):
    for i in range(9):
        x = x0 + (x1 - x0) * i / 8
        fd.line([P(x, y0 + 4), P(x + 2 * math.sin(i), y0 + 30)], fill=BASE, width=3 * SS)
# soft fold lines
fd.arc([*P(60, 40), *P(225, 130)], 200, 340, fill=(30, 42, 92, 255), width=3 * SS)
shawl_o = shawl_o.resize((W, H), Image.LANCZOS)
ab = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ab.alpha_composite(moka, (PAD, PAD))
ab.alpha_composite(shawl_o)
ab.save(f"{D}/abuelita.png")
# jar
JW, JH = 92, 130
j = Image.new("RGBA", (JW * SS, JH * SS), (0, 0, 0, 0))
jd = ImageDraw.Draw(j)
def Q(x, y): return (x * SS, y * SS)
jd.rounded_rectangle([*Q(14, 2), *Q(78, 24)], radius=4 * SS, fill=(150, 30, 30, 255), outline=INK, width=3 * SS)
jd.rounded_rectangle([*Q(4, 22), *Q(88, 126)], radius=16 * SS, fill=(110, 62, 34, 235), outline=INK, width=3 * SS)
jd.rectangle([*Q(4, 58), *Q(88, 98)], fill=(250, 238, 214, 255), outline=INK, width=3 * SS)
jd.line([*Q(16, 70), *Q(76, 70)], fill=(150, 30, 30, 255), width=5 * SS)
jd.line([*Q(22, 84), *Q(70, 84)], fill=(150, 30, 30, 255), width=4 * SS)
jd.line([*Q(14, 34), *Q(14, 50)], fill=(255, 255, 255, 120), width=4 * SS)
j = j.resize((JW, JH), Image.LANCZOS)
j.save(f"{D}/frasco.png")
prev = Image.new("RGBA", (W + 200, H), (248, 196, 149, 255)); prev.alpha_composite(ab); prev.alpha_composite(j, (W + 50, 200))
prev.save(f"{D}/props_prev.png")
