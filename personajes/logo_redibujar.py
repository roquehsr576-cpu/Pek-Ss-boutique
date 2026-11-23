"""Redraw the Dulce Café badge as a crisp high-resolution PNG (supersampled)."""
import math, sys
from PIL import Image, ImageDraw, ImageFont

FD, OUT = sys.argv[1], sys.argv[2]
SIZE = int(sys.argv[3]) if len(sys.argv) > 3 else 1200
TOP_ARC = sys.argv[4] if len(sys.argv) > 4 else "CAFÉ ARTESANAL Y MUY ESPECIAL"
BAND = sys.argv[5] if len(sys.argv) > 5 else "TANETZE DE ZARAGOZA"
K = 3                      # supersampling
S = SIZE * K
C = S / 2
CREAM = (248, 214, 178)
BROWN = (58, 34, 22)
DARK = (34, 22, 16)
WHITE = (255, 255, 255)

im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
d = ImageDraw.Draw(im)
u = S / 1000  # design units

def circ(r, **kw):
    d.ellipse([C - r, C - r, C + r, C + r], **kw)

circ(480 * u, fill=WHITE)
circ(462 * u, fill=CREAM, outline=BROWN, width=int(16 * u))
circ(430 * u, outline=BROWN, width=int(4 * u))

def arc_text(text, radius, font, center_deg, top=True, fill=BROWN, spacing=1.0):
    """Lay text along a circle; top=True reads left→right over the top."""
    widths = [d.textlength(ch, font=font) * spacing for ch in text]
    total = sum(widths)
    ang = math.radians(center_deg) - (total / radius / 2 if top else -total / radius / 2)
    for ch, w in zip(text, widths):
        step = w / radius
        a = ang + (step / 2 if top else -step / 2)
        x, y = C + radius * math.cos(a), C + radius * math.sin(a)
        g = Image.new("RGBA", (int(w * 2 + 10), int(font.size * 2)), (0, 0, 0, 0))
        ImageDraw.Draw(g).text((g.width / 2, g.height / 2), ch, font=font, fill=fill, anchor="mm")
        rot = -math.degrees(a) - 90 if top else -math.degrees(a) + 90
        g = g.rotate(rot, resample=Image.BICUBIC, expand=True)
        im.alpha_composite(g, (int(x - g.width / 2), int(y - g.height / 2)))
        ang += step if top else -step

small = ImageFont.truetype(f"{FD}/Oswald.ttf", int(30 * u))
small.set_variation_by_axes([600])
arc_text(TOP_ARC, 395 * u, small, -90, top=True, spacing=1.15)
arc_text("CAFÉ DE ALTURA", 395 * u, small, 90, top=False, spacing=1.25)

# three coffee beans
def bean(cx, cy, rx, ry, ang):
    b = Image.new("RGBA", (int(rx * 2.4), int(ry * 2.4)), (0, 0, 0, 0))
    bd = ImageDraw.Draw(b)
    bx, by = b.width / 2, b.height / 2
    bd.ellipse([bx - rx, by - ry, bx + rx, by + ry], fill=(70, 40, 24))
    bd.ellipse([bx - rx * 0.86, by - ry * 0.9, bx + rx * 0.3, by + ry * 0.2], fill=(96, 58, 34))
    pts = [(bx + rx * 0.16 * math.sin(t / 20 * 2 * math.pi), by - ry * 0.9 + ry * 1.8 * t / 20) for t in range(21)]
    bd.line(pts, fill=(28, 16, 10), width=int(rx * 0.16), joint="curve")
    b = b.rotate(ang, resample=Image.BICUBIC, expand=True)
    im.alpha_composite(b, (int(cx - b.width / 2), int(cy - b.height / 2)))
bean(C - 92 * u, C - 255 * u, 52 * u, 78 * u, 28)
bean(C + 92 * u, C - 255 * u, 52 * u, 78 * u, -28)
bean(C, C - 275 * u, 58 * u, 88 * u, 0)

# ribbon with the name
band_top, band_bot = C - 150 * u, C + 95 * u
d.rectangle([C - 520 * u, band_top, C + 520 * u, band_bot], fill=WHITE)
d.rectangle([C - 505 * u, band_top + 14 * u, C + 505 * u, band_bot - 14 * u], fill=CREAM, outline=BROWN, width=int(8 * u))
mid = ImageFont.truetype(f"{FD}/Oswald.ttf", int(50 * u))
mid.set_variation_by_axes([600])
d.text((C, band_top + 70 * u), BAND, font=mid, fill=BROWN, anchor="mm")
d.line([C - 470 * u, band_top + 112 * u, C + 470 * u, band_top + 112 * u], fill=BROWN, width=int(6 * u))
big = ImageFont.truetype(f"{FD}/AlfaSlabOne-Regular.ttf", int(100 * u))
name = "DULCE CAFÉ"
# letter-spaced title
widths = [d.textlength(ch, font=big) for ch in name]
gap = 8 * u
total = sum(widths) + gap * (len(name) - 1)
x = C - total / 2
for ch, w in zip(name, widths):
    d.text((x, band_top + 176 * u), ch, font=big, fill=DARK, anchor="lm")
    x += w + gap
for sx in (-1, 1):
    r = 14 * u
    cx = C + sx * (total / 2 + 44 * u)
    d.ellipse([cx - r, band_top + 176 * u - r, cx + r, band_top + 176 * u + r], fill=DARK)

# cup on a saucer
cy = C + 235 * u
d.ellipse([C - 150 * u, cy + 70 * u, C + 150 * u, cy + 118 * u], fill=WHITE, outline=BROWN, width=int(7 * u))
d.rounded_rectangle([C - 105 * u, cy - 40 * u, C + 105 * u, cy + 92 * u], radius=int(40 * u), fill=WHITE, outline=BROWN, width=int(7 * u))
d.ellipse([C - 105 * u, cy - 62 * u, C + 105 * u, cy - 18 * u], fill=(92, 52, 30), outline=BROWN, width=int(7 * u))
d.arc([C + 85 * u, cy - 20 * u, C + 165 * u, cy + 60 * u], -80, 90, fill=BROWN, width=int(12 * u))
for i, ox in enumerate((-40, 0, 40)):
    pts = [(C + ox * u + 12 * u * math.sin(t / 10 * 2 * math.pi + i), cy - 75 * u - t * 6 * u) for t in range(11)]
    d.line(pts, fill=BROWN + (170,), width=int(7 * u), joint="curve")

im.resize((SIZE, SIZE), Image.LANCZOS).save(OUT)
